#!/usr/bin/env python3
"""Host-native protocol/fixture review, not physical scheduling evidence.

Compile the stock diagnostic VDU source through Fab's userspace library. Its
renderer is a host adaptation; its timestamps never count as hardware results.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,concurrent.futures,hashlib,json,re,shutil,subprocess
T=Path(__file__).resolve().parents[1];ROOT=T.parents[3]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--peer',action='store_true');p.add_argument('--trace',action='store_true',help='Native-only diagnostic request/reply stderr trace');p.add_argument('--fab',type=Path,default=Path.home()/'Agon/fab-agon-emulator');a=p.parse_args()
original=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);fab=a.fab.resolve();gl=out/'gl'
src=out/'source';src.mkdir();shutil.copytree(original/'video',src/'video',ignore=shutil.ignore_patterns('build','*.o','*.a'));shutil.copytree(original/'local-libs/CRC',src/'local-libs/CRC');shutil.copytree(original/'local-libs/ESP32Time',src/'local-libs/ESP32Time')
shutil.copytree(fab/'src/vdp/userspace-vdp-gl/src',gl,ignore=shutil.ignore_patterns('*.o','*.a','.git'))
# Stock v2.16.0 uses unsigned in an out-of-line definition declared size_t.
# They are equal on ESP32, different on this 64-bit host. Match the declaration
# only in the disposable native copy; physical source and behavior untouched.
path=src/'video/ymodem.h';text=path.read_text();old='MOS_YmodemSession::getFilename(unsigned index)'
assert old in text;path.write_text(text.replace(old,'MOS_YmodemSession::getFilename(size_t index)').replace('MOS_YmodemSession::getFilesize(unsigned index)','MOS_YmodemSession::getFilesize(size_t index)'))
# Same guarded instrumentation additions; never port physical ISR code into Fab.
prefix='#ifdef AGON_GRAPHICS_TIMING\n#include "extender/diagnostics/graphics_timing.hpp"\n#else\n#define AGON_GRAPHICS_SCOPE(metric)\n#endif\n'
for file,scopes in {'displaycontroller.cpp':[
 ('void IRAM_ATTR BitmappedDisplayController::execPrimitive(Primitive const & prim, Rect & updateRect, bool insideISR)\n{','Primitive'),
 ('void IRAM_ATTR BitmappedDisplayController::showSprites(Rect & updateRect)\n{','SoftwareSprites')],
 'dispdrivers/vgapalettedcontroller.cpp':[
 ('void IRAM_ATTR VGAPalettedController::drawSpriteScanLine(uint8_t * pixelData, int scanRow, int scanWidth, int viewportHeight) {','ScanlineDecoration')]}.items():
    path=gl/file;s=path.read_text()
    for sig,metric in scopes:
        assert s.count(sig)==1,sig;s=s.replace(sig,sig+'\n  AGON_GRAPHICS_SCOPE('+metric+');')
    s=s.replace('  AGON_GRAPHICS_SCOPE(SoftwareSprites);','agon_graphics_timing::FinishSprites qual_fence_after_sprite_scope;\n  AGON_GRAPHICS_SCOPE(SoftwareSprites);')
    s=s.replace('    case PrimitiveCmd::Flush:\n','    case PrimitiveCmd::GraphicsFence: agon_graphics_timing::reached(uint16_t(prim.ivalue)); break;\n    case PrimitiveCmd::Flush:\n')
    path.write_text(prefix+s)
path=gl/'displaycontroller.h';s=path.read_text();idx=s.index('};',s.index('  Flush,'));path.write_text(s[:idx]+'  GraphicsFence = 126,\n'+s[idx:])
# Fab glue contains relative userspace-vdp-gl includes. Give it one consistent
# disposable include tree, rather than mixing the instrumented and stock enums.
glue=out/'glue';glue.mkdir();(glue/'userspace-vdp-gl').mkdir();(glue/'userspace-vdp-gl/src').symlink_to(gl)
for name in ('rust_glue.cpp','vdp.h','vdp-console8.h'):shutil.copy2(fab/'src/vdp'/name,glue/name)
# Arduino namespace and heap-inspection bindings missing in this Fab adapter.
# Allocated size is used only for VDP's tile-layer debug log; report the host's
# actual malloc extent, never a fabricated size. No physical source is changed.
(out/'compat.hpp').write_text('#pragma once\n#include <algorithm>\n#include <malloc.h>\nusing std::max;\ninline size_t heap_caps_get_allocated_size(void *p) {return malloc_usable_size(p); }\n')
# Copy the current diagnostic header to a separate include overlay. Physical
# input tree is immutable once its image is built.
overlay=out/'include/extender/diagnostics';overlay.mkdir(parents=True)
for name in ('graphics_timing.hpp','graphics_command.inc'):
    shutil.copy2(ROOT/'vdp/video/extender/diagnostics'/name,overlay/name)
    shutil.copy2(ROOT/'vdp/video/extender/diagnostics'/name,src/'video/extender/diagnostics'/name)
if a.trace:
    path=src/'video/extender/diagnostics/graphics_command.inc';s=path.read_text()
    s=s.replace('    using namespace agon_graphics_timing;',
                '    fprintf(stderr,"GQT request op=%d token=%d flags=%d\\n",op,token,flags);\n    using namespace agon_graphics_timing;')
    s=s.replace('        send_packet(0x0C,sizeof packet,packet);',
                '        fprintf(stderr,"GQT reply token=%d metric=%u value=%u count=%u\\n",token,metric,value,count);\n        send_packet(0x0C,sizeof packet,packet);')
    path.write_text(s)
adapter=out/'adapter.cpp';adapter.write_text('#include "Arduino.h"\n#include "vdp-console8.h"\nfabgl::SoundGenerator *getVDPSoundGenerator() { return &*soundGenerator; }\n#include "'+str(src/'video/video.ino')+'"\n')
(out/'yield.hpp').write_text('#pragma once\n#include <thread>\ninline void yield() {std::this_thread::yield();}\n')
make=(gl/'Makefile').read_text();section=make.split('SRCS =',1)[1].split('OBJS =',1)[0]
sources=[gl/s for s in re.findall(r'[\w/-]+\.cpp',section)]
sources += [adapter,glue/'rust_glue.cpp']
sources += [src/'local-libs/CRC/src'/n for n in ('CRC16.cpp','CRC32.cpp','CrcFastReverse.cpp')]
inc=[out/'include',glue,fab/'src',src/'video',gl,gl/'comdrivers',gl/'dispdrivers',gl/'userspace-platform',gl/'userspace-platform/matrix',src/'local-libs/CRC/src',src/'local-libs/ESP32Time']
flags=['-std=c++17','-O2','-fPIC','-fno-gnu-unique','-DUSERSPACE','-DAGON_GRAPHICS_TIMING=1','-DWIFI_TASK_CORE_ID=0','-Werror=return-type']+['-I'+str(p) for p in inc]
if a.peer:flags.append('-DAGON_GRAPHICS_TIMING_PEER=1')
def compile(item):
    i,path=item;obj=out/f'{i:02}.o';cmd=['c++',*flags]
    # Stock's USERSPACE-only hex loader stub has no return. Keep it unchanged;
    # this probe never calls the external-debug loader. Retain a visible warning.
    if path==adapter:cmd+=['-Wno-error=return-type','-include',str(out/'compat.hpp')]
    if path.name.startswith('CRC'):cmd+=['-include',str(out/'yield.hpp')]
    cmd+=['-c',str(path),'-o',str(obj)]
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (out/f'{i:02}.log').write_text(result.stdout)
    if result.returncode:raise RuntimeError(str(path)+'\n'+result.stdout[-1800:])
    return obj
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:objects=list(pool.map(compile,enumerate(sources)))
module=out/'graphics-native.so'
subprocess.run(['c++','-shared','-Wl,-z,defs','-Wl,-Bsymbolic',*[str(x) for x in objects],'-pthread','-o',str(module)],check=True)
identity=json.loads((T/'identity.json').read_text())['source_identity']
(out/'manifest.json').write_text(json.dumps(dict(build_id=identity+datetime.now(timezone.utc).strftime('-b%Y-%m-%d-%H-%M-%SZ'),variant='native-peer' if a.peer else 'native-mainboard',trace=a.trace,scope=__doc__,module_sha256=hashlib.sha256(module.read_bytes()).hexdigest(),sources={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources}),indent=2)+'\n')
print(module)
