#!/usr/bin/env python3
"""Isolated UART probe builds. No deployment, runtime-profile or upstream edits."""
import argparse,configparser,hashlib,io,json,os,shutil,subprocess,tarfile
from datetime import datetime,timezone
from pathlib import Path
TASK=Path(__file__).resolve().parents[1];ROOT=TASK.parents[3]
p=argparse.ArgumentParser();p.add_argument('target',choices=['app','mainboard','p4']);p.add_argument('--output',type=Path,required=True);p.add_argument('--p4-baseline',type=Path);p.add_argument('--console-overlay',type=Path);p.add_argument('--hardware-overlay',type=Path);a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd,log,env=None):
 with (out/log).open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
def extract(repo,commit,dest):
 dest.mkdir(parents=True,exist_ok=True)
 with tarfile.open(fileobj=io.BytesIO(git(repo,'archive',commit))) as t:t.extractall(dest,filter='data')
meta={'source_commit':git(ROOT,'rev-parse','HEAD').decode().strip(),'dirty':bool(git(ROOT,'status','--porcelain')),'target':a.target,'status':'experimental','inputs':{}}
if meta['dirty']:raise SystemExit('Commit controlled inputs before building')
stamp=datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ');identity=('uart-excom-console-r17' if a.target=='p4' else 'uart-data-probe-r01')+'-b'+stamp
meta['build_id']=identity
for f in TASK.rglob('*'):
 if f.is_file():meta['inputs'][str(f.relative_to(ROOT))]=sha(f)
if a.target=='app':
 src=out/'fixture';shutil.copytree(TASK/'fixture',src);(src/'build').mkdir();(src/'build/build_identity.h').write_text('#define UART_BUILD_ID "'+identity+' (experimental)"\n')
 run(['make','-C',str(src),'all'],'build.log');artifacts=list((src/'bin').glob('*'))
else:
 if a.target=='mainboard':
  stock=Path.home()/'Agon/agon-vdp';src=out/'source';v='c7ac293d2aa81ddfa693390549bcd909069c8fc3';g='ac2dd5986daf496c43ae8e7fe41836274aec54a0'
  extract(stock,v,src);extract(stock/'.pio/libdeps/esp32dev/vdp-gl',g,src/'local-libs/vdp-gl')
  for name in ('ESP32Time','CRC'):shutil.copytree(stock/'.pio/libdeps/esp32dev'/name,src/'local-libs'/name,ignore=shutil.ignore_patterns('.git','.pio'))
  ini=(src/'platformio.ini').read_text();begin=ini.index('lib_deps =');end=ini.index('build_unflags',begin);ini=ini[:begin]+'lib_deps =\nlib_extra_dirs = local-libs\n'+ini[end:];(src/'platformio.ini').write_text(ini)
  ver=src/'video/version.h';ver.write_text(ver.read_text().replace('#endif // VERSION_H','#define VERSION_BUILD "'+identity+' (experimental)"\n#endif // VERSION_H'))
  meta['stock']={'vdp':v,'vdp-gl':g};envname='esp32dev';env=None
 else:
  assert a.p4_baseline,'--p4-baseline required';base=a.p4_baseline.resolve();old=json.loads((base/'manifest.json').read_text())
  container=out/'source';container.mkdir()
  with tarfile.open(base/'source.tar.gz') as t:t.extractall(container,filter='data')
  for name,h in old['inputs'].items():assert sha(container/name)==h,name
  src=container/'vdp';(src/'.pio').mkdir(exist_ok=True);(src/'.pio/packages').symlink_to(ROOT/'vdp/.pio/packages',target_is_directory=True)
  if not (src/'managed_components').exists():(src/'managed_components').symlink_to(ROOT/'vdp/managed_components',target_is_directory=True)
  c=configparser.ConfigParser(interpolation=None);c.optionxform=str;c.read(base/'platformio.ini');c['platformio']['build_dir']=str(out/'build')
  shutil.copy2(base/'sdkconfig.videopoll1tcp32k',out/'sdkconfig.p4')
  c['env:p4-console']['board_build.esp-idf.sdkconfig_path']=str(out/'sdkconfig.p4')
  with (src/'platformio.ini').open('w') as f:c.write(f)
  if a.console_overlay:
   overlay=a.console_overlay.resolve();shutil.copy2(overlay,src/'video/extender/transport/console_stream.hpp');meta['console_overlay']={'path':str(overlay.relative_to(ROOT)),'sha256':sha(overlay)}
  if a.hardware_overlay:
   overlay=a.hardware_overlay.resolve();shutil.copy2(overlay,src/'video/extender/transport/console_hardware.inc');meta['hardware_overlay']={'path':str(overlay.relative_to(ROOT)),'sha256':sha(overlay)}
  meta['p4_parent']=old['build_id'];envname='p4-console';env=dict(os.environ,AGON_EXTENDER_BUILD_ID=identity,AGON_EXTENDER_DSP_LIFETIME_FIX='1')
 hook=src/'video/uart_data_probe.inc';shutil.copy2(TASK/'uart_probe.inc',hook)
 path=src/'video/vdu_sys.h';s=path.read_text();i=s.index('\tswitch (mode) {',s.index('void VDUStreamProcessor::vdu_sys_video()'))+len('\tswitch (mode) {');path.write_text(s[:i]+'\n#include "uart_data_probe.inc"\n'+s[i:])
 meta['probe_sha256']=sha(hook)
 run([str(ROOT/'.venv/bin/pio'),'run','-d',str(src),'-e',envname],'build.log',env)
 build=(src/'.pio/build'/envname) if a.target=='mainboard' else out/'build'/envname
 artifacts=[build/n for n in ('firmware.bin','firmware.elf','partitions.bin','bootloader.bin')]
 if (build/'firmware.factory.bin').exists():artifacts.append(build/'firmware.factory.bin')
meta['outputs']={}
for f in artifacts:
 if f.is_file():shutil.copy2(f,out/f.name);meta['outputs'][f.name]={'bytes':f.stat().st_size,'sha256':sha(f)}
assert not git(ROOT,'status','--porcelain').strip(),'Maintained worktree changed during build'
(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(identity,flush=True)
