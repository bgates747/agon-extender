"""Build official stock VDP plus bounded scanout tap, in an isolated output tree."""
from pathlib import Path
import argparse,datetime,hashlib,io,json,shutil,subprocess,tarfile
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--all-depths',action='store_true');a=p.parse_args()
stock=Path.home()/'Agon/agon-vdp';gl=stock/'.pio/libdeps/esp32dev/vdp-gl'
def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not git(ROOT,'status','--porcelain'),'Freeze inputs first'
assert not git(stock,'status','--porcelain')
vdp='c7ac293d2aa81ddfa693390549bcd909069c8fc3';fab='ac2dd5986daf496c43ae8e7fe41836274aec54a0'
assert git(stock,'rev-parse','HEAD').decode().strip()==vdp
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);src=out/'source'
def archive(repo,commit,dest):
 dest.mkdir(parents=True)
 with tarfile.open(fileobj=io.BytesIO(git(repo,'archive',commit))) as t:t.extractall(dest,filter='data')
archive(stock,vdp,src);archive(gl,fab,src/'local-libs/vdp-gl')
for name in ('ESP32Time','CRC'):shutil.copytree(stock/'.pio/libdeps/esp32dev'/name,src/'local-libs'/name,ignore=shutil.ignore_patterns('.git','.pio'))
original={str(f.relative_to(src)):sha(f) for f in src.rglob('*') if f.is_file()}
for n in ('scanout_tap.h','capture_command.inc'):shutil.copy2(TASK/n,src/'video'/n)
f=src/'video/vdu_sys.h';s=f.read_text();s='#include "scanout_tap.h"\n'+s
needle='\tswitch (mode) {';pos=s.index(needle,s.index('void VDUStreamProcessor::vdu_sys_video()'))+len(needle)
s=s[:pos]+'\n#include "capture_command.inc"\n'+s[pos:];f.write_text(s)
f=src/'local-libs/vdp-gl/src/dispdrivers/vga64controller.cpp';s=f.read_text();needle='      ctrl->decorateScanLinePixels(dest, scanLine);';assert s.count(needle)==1
s=s.replace(needle,needle+'\n      qual004::tap(dest, scanLine, width);')
f.write_text('#include "scanout_tap.h"\nnamespace qual004 { volatile int requested_row=-1; volatile int ready_width=0; DRAM_ATTR uint8_t row[1024]; }\n'+s)
if a.all_depths:
 for depth in (2,4,8,16):
  f=src/f'local-libs/vdp-gl/src/dispdrivers/vga{depth}controller.cpp';s=f.read_text()
  needle='      ctrl->decorateScanLinePixels(decpix, scanLine);';assert s.count(needle)==1
  s=s.replace(needle,needle+'\n      qual004::tap(decpix, scanLine, width);')
  f.write_text('#include "scanout_tap.h"\n'+s)
f=src/'platformio.ini';s=f.read_text();begin=s.index('lib_deps =');end=s.index('build_unflags',begin)
s=s[:begin]+'lib_deps =\nlib_extra_dirs = local-libs\n'+s[end:];s=s.replace('build_flags =','build_flags =\n    -I video',1);f.write_text(s)
build_id=('mainboard-image-capture-r02' if a.all_depths else 'mainboard-image-capture-r01')+datetime.datetime.now(datetime.timezone.utc).strftime('-b%Y-%m-%d-%H-%M-%SZ')
f=src/'video/version.h';f.write_text(f.read_text().replace('#endif // VERSION_H','#define VERSION_BUILD "'+build_id+' (experimental)"\n#endif // VERSION_H'))
manifest=dict(build_id=build_id,stock_vdp=vdp,stock_gl=fab,contract_commit=git(ROOT,'rev-parse','HEAD').decode().strip(),dirty=False,changed_stock_files=[n for n,h in original.items() if sha(src/n)!=h],files={str(f.relative_to(src)):sha(f) for f in src.rglob('*') if f.is_file()})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with (out/'build.log').open('w') as log:subprocess.run([str(ROOT/'.venv/bin/pio'),'run','-d',str(src),'-e','esp32dev'],stdout=log,stderr=subprocess.STDOUT,check=True)
for n in ('firmware.bin','firmware.elf','bootloader.bin','partitions.bin'):shutil.copy2(src/'.pio/build/esp32dev'/n,out/n)
manifest['outputs']={n:sha(out/n) for n in ('firmware.bin','firmware.elf','bootloader.bin','partitions.bin')};manifest['build_complete']=True
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(build_id)
