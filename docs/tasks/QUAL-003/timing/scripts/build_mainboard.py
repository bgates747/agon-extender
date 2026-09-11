#!/usr/bin/env python3
"""Build a temporary classic ESP32 image from exact stock releases.

Only three measurement scopes and the private command are injected. Official
checkouts remain read-only. No upstream bug fixes or rendering replacements.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,io,json,shutil,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[5];TIMING=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
p.add_argument('--stock',type=Path,default=Path.home()/'Agon/agon-vdp');a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);src=out/'source';src.mkdir()
stock=a.stock.resolve();gl=stock/'.pio/libdeps/esp32dev/vdp-gl'
def git(where,*args):return subprocess.check_output(['git','-C',str(where),*args])
identity=json.loads((TIMING/'identity.json').read_text())
provenance=dict(commit=git(ROOT,'rev-parse','HEAD').decode().strip(),dirty=bool(git(ROOT,'status','--porcelain')))
if identity['status']!='draft' and provenance['dirty']:
    raise SystemExit('Candidate mainboard builds require clean committed inputs')
def archive(repo,commit,dest):
    dest.mkdir(parents=True,exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(git(repo,'archive',commit))) as t:t.extractall(dest,filter='data')
vdp_commit='c7ac293d2aa81ddfa693390549bcd909069c8fc3';gl_commit='ac2dd5986daf496c43ae8e7fe41836274aec54a0'
archive(stock,vdp_commit,src);archive(gl,gl_commit,src/'local-libs/vdp-gl')
for name in ('ESP32Time','CRC'):
    shutil.copytree(stock/'.pio/libdeps/esp32dev'/name,src/'local-libs'/name,ignore=shutil.ignore_patterns('.git','.pio'))
diagnostic=src/'video/extender/diagnostics';diagnostic.mkdir(parents=True)
for name in ('graphics_timing.hpp','graphics_command.inc'):
    shutil.copy2(ROOT/'vdp/video/extender/diagnostics'/name,diagnostic/name)
prefix='#ifdef AGON_GRAPHICS_TIMING\n#include "extender/diagnostics/graphics_timing.hpp"\n#else\n#define AGON_GRAPHICS_SCOPE(metric)\n#endif\n'
for name,scopes in {
 'displaycontroller.cpp':[
 ('void IRAM_ATTR BitmappedDisplayController::execPrimitive(Primitive const & prim, Rect & updateRect, bool insideISR)\n{','Primitive'),
 ('void IRAM_ATTR BitmappedDisplayController::showSprites(Rect & updateRect)\n{','SoftwareSprites')],
 'dispdrivers/vgapalettedcontroller.cpp':[
 ('void IRAM_ATTR VGAPalettedController::drawSpriteScanLine(uint8_t * pixelData, int scanRow, int scanWidth, int viewportHeight) {','ScanlineDecoration')]
}.items():
    path=src/'local-libs/vdp-gl/src'/name;s=path.read_text()
    for signature,metric in scopes:
        assert s.count(signature)==1
        s=s.replace(signature,signature+'\n  AGON_GRAPHICS_SCOPE('+metric+');')
    path.write_text(prefix+s)
# Explicit fence extension: retain all stock opcode values and normal worker policy.
path=src/'local-libs/vdp-gl/src/displaycontroller.h';s=path.read_text()
idx=s.index('};',s.index('  Flush,'));s=s[:idx]+'#ifdef AGON_GRAPHICS_TIMING\n  GraphicsFence = 126,\n#endif\n'+s[idx:];path.write_text(s)
path=src/'local-libs/vdp-gl/src/displaycontroller.cpp';s=path.read_text()
s=s.replace('  AGON_GRAPHICS_SCOPE(SoftwareSprites);','#ifdef AGON_GRAPHICS_TIMING\n  agon_graphics_timing::FinishSprites qual_fence_after_sprite_scope;\n#endif\n  AGON_GRAPHICS_SCOPE(SoftwareSprites);')
s=s.replace('    case PrimitiveCmd::Flush:\n','#ifdef AGON_GRAPHICS_TIMING\n    case PrimitiveCmd::GraphicsFence:\n      agon_graphics_timing::reached(uint16_t(prim.ivalue));\n      break;\n#endif\n    case PrimitiveCmd::Flush:\n')
path.write_text(s)
path=src/'video/vdu_sys.h';s=path.read_text();idx=s.index('\tswitch (mode) {',s.index('void VDUStreamProcessor::vdu_sys_video()'))+len('\tswitch (mode) {')
s=s[:idx]+'\n#ifdef AGON_GRAPHICS_TIMING\n#include "extender/diagnostics/graphics_command.inc"\n#endif'+s[idx:]
path.write_text(prefix+s)
# Keep the stock platform/toolchain options, pin dependency source locally.
ini=(src/'platformio.ini').read_text();begin=ini.index('lib_deps =');end=ini.index('build_unflags',begin)
ini=ini[:begin]+'lib_deps =\nlib_extra_dirs = local-libs\n'+ini[end:]
ini=ini.replace('build_flags =','build_flags =\n    -D AGON_GRAPHICS_TIMING=1\n    -I video',1)
(src/'platformio.ini').write_text(ini)
build_id=identity['source_identity']+datetime.now(timezone.utc).strftime('-b%Y-%m-%d-%H-%M-%SZ')
(out/'build-id.txt').write_text(build_id+'\n')
version=src/'video/version.h';version.write_text(version.read_text().replace('#endif // VERSION_H','#define VERSION_BUILD "'+build_id+' ('+identity['status']+')"\n#endif // VERSION_H'))
files={str(f.relative_to(src)):hashlib.sha256(f.read_bytes()).hexdigest() for f in src.rglob('*') if f.is_file()}
(out/'sources.json').write_text(json.dumps(dict(stock_vdp=vdp_commit,stock_gl=gl_commit,build_id=build_id,variant='mainboard',status=identity['status'],provenance=provenance,files=files),indent=2)+'\n')
with (out/'build.log').open('w') as log:
    result=subprocess.run([str(ROOT/'.venv/bin/pio'),'run','-d',str(src),'-e','esp32dev'],stdout=log,stderr=subprocess.STDOUT)
if result.returncode:raise SystemExit('Mainboard build failed; see '+str(out/'build.log'))
if provenance!=dict(commit=git(ROOT,'rev-parse','HEAD').decode().strip(),dirty=bool(git(ROOT,'status','--porcelain'))):
    raise SystemExit('Source changed during mainboard build; no candidate frozen')
for name in ('firmware.bin','firmware.elf','bootloader.bin','partitions.bin'):
    shutil.copy2(src/'.pio/build/esp32dev'/name,out/name)
(out/'outputs.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.glob('*') if f.suffix in ('.bin','.elf')},indent=2)+'\n')
print(build_id+' mainboard image built; not deployed')
