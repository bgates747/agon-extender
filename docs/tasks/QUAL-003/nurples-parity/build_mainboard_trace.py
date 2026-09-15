"""Exact stock VDP/GL plus the same bounded completion observer used on P4.

Pattern reused from QUAL-003/timing/scripts/build_mainboard.py. No deployment;
reference checkouts are read-only. No retained P4 renderer/transport adaptations.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,io,json,shutil,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
p.add_argument('--stock',type=Path,default=Path.home()/'Agon/agon-vdp');a=p.parse_args()
stock=a.stock.resolve();gl=stock/'.pio/libdeps/esp32dev/vdp-gl';out=a.output.resolve()
def git(where,*args):return subprocess.check_output(['git','-C',str(where),*args])
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert not git(ROOT,'status','--porcelain'), 'Commit bounded inputs before building'
assert not git(stock,'status','--porcelain'), 'Reference must remain clean'
vdp_commit='c7ac293d2aa81ddfa693390549bcd909069c8fc3';gl_commit='ac2dd5986daf496c43ae8e7fe41836274aec54a0'
assert git(stock,'rev-parse','HEAD').decode().strip()==vdp_commit
out.mkdir(parents=True,exist_ok=False);src=out/'source';src.mkdir()
def archive(repo,commit,dest):
 dest.mkdir(parents=True,exist_ok=True)
 with tarfile.open(fileobj=io.BytesIO(git(repo,'archive',commit))) as t:t.extractall(dest,filter='data')
archive(stock,vdp_commit,src);archive(gl,gl_commit,src/'local-libs/vdp-gl')
for name in ('ESP32Time','CRC'):
 shutil.copytree(stock/'.pio/libdeps/esp32dev'/name,src/'local-libs'/name,ignore=shutil.ignore_patterns('.git','.pio'))
original={str(f.relative_to(src)):sha(f) for f in src.rglob('*') if f.is_file()}
diag=src/'video/extender/diagnostics';diag.mkdir(parents=True)
recorder=ROOT/'vdp/video/extender/diagnostics/refresh_trace.hpp';shutil.copy2(recorder,diag/'refresh_trace.hpp')
prefix='#ifdef AGON_EXTENDER_REFRESH_TRACE\n#include "extender/diagnostics/refresh_trace.hpp"\n#endif\n'
f=src/'local-libs/vdp-gl/src/displaycontroller.cpp';s=f.read_text()
needle='void BitmappedDisplayController::addPrimitive(Primitive & primitive)\n{';assert s.count(needle)==1
s=s.replace(needle,needle+'\n#ifdef AGON_EXTENDER_REFRESH_TRACE\n  if (primitive.cmd == PrimitiveCmd::RefreshSprites) agon_refresh_trace::enqueue();\n#endif')
needle='    case PrimitiveCmd::RefreshSprites:\n      hideSprites(updateRect);\n      showSprites(updateRect);';assert s.count(needle)==1
s=s.replace(needle,needle+'\n#ifdef AGON_EXTENDER_REFRESH_TRACE\n      agon_refresh_trace::complete();\n#endif');f.write_text(prefix+s)
f=src/'video/vdu_buffered.h';s=f.read_text();needle='\tif (bufferId == 65535) {\n\t\t// buffer ID';assert s.count(needle)==1
s=s.replace(needle,'\tif (bufferId == 65535) {\n#ifdef AGON_EXTENDER_REFRESH_TRACE\n\t\tagon_refresh_trace::marker(bufferStream->getBuffer(), length);\n#endif\n\t\t// buffer ID');f.write_text(prefix+s)
f=src/'platformio.ini';s=f.read_text();begin=s.index('lib_deps =');end=s.index('build_unflags',begin)
s=s[:begin]+'lib_deps =\nlib_extra_dirs = local-libs\n'+s[end:];s=s.replace('build_flags =','build_flags =\n    -D AGON_EXTENDER_REFRESH_TRACE=1\n    -I video',1);f.write_text(s)
build_id='mainboard-refresh-trace-r01'+datetime.now(timezone.utc).strftime('-b%Y-%m-%d-%H-%M-%SZ')
f=src/'video/version.h';f.write_text(f.read_text().replace('#endif // VERSION_H','#define VERSION_BUILD "'+build_id+' (experimental)"\n#endif // VERSION_H'))
changed={n for n,h in original.items() if sha(src/n)!=h}
assert changed=={'platformio.ini','video/version.h','video/vdu_buffered.h','local-libs/vdp-gl/src/displaycontroller.cpp'},changed
manifest=dict(build_id=build_id,status='experimental',stock_vdp=vdp_commit,stock_gl=gl_commit,contract_commit=git(ROOT,'rev-parse','HEAD').decode().strip(),changed_stock_files=sorted(changed),recorder_sha256=sha(recorder),files={str(f.relative_to(src)):sha(f) for f in src.rglob('*') if f.is_file()})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with (out/'build.log').open('w') as log:
 subprocess.run([str(ROOT/'.venv/bin/pio'),'run','-d',str(src),'-e','esp32dev'],stdout=log,stderr=subprocess.STDOUT,check=True)
assert sha(recorder)==manifest['recorder_sha256']
for name in ('firmware.bin','firmware.elf','bootloader.bin','partitions.bin'):shutil.copy2(src/'.pio/build/esp32dev'/name,out/name)
assert build_id.encode() in (out/'firmware.bin').read_bytes()
assert b'NPTRACE begin' in (out/'firmware.bin').read_bytes()
manifest['outputs']={n:{'bytes':(out/n).stat().st_size,'sha256':sha(out/n)} for n in ('firmware.bin','firmware.elf','bootloader.bin','partitions.bin')};manifest['build_complete']=True
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(build_id+' built; unflashed')
