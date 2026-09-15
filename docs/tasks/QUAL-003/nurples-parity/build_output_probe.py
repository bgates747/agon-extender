"""Isolate the installed r22 source; enable only existing output timing scopes.

No deployment. Parent input/output tree is read-only. This is an agent-assigned
Nurples diagnostic variant, not a production or qualified firmware revision.
"""
import argparse,configparser,datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=Path.cwd();parent=a.parent.resolve();out=a.output.resolve()
 assert not subprocess.check_output(['git','status','--porcelain'],text=True)
 meta=json.loads((parent/'manifest.json').read_text());assert meta['build_id']=='uart-excom-console-r22-b2026-09-15-07-01-47Z'
 assert sha(parent/'firmware.bin')=='ccb96bf7e2e9de172732118d5ee93c01d2f6c4ae4b3b953a98881c58c622cdd7'
 out.mkdir(parents=True,exist_ok=False)
 source=parent/'source';tree=out/'source'
 shutil.copytree(source,tree,ignore=shutil.ignore_patterns('.pio','managed_components','__pycache__'))
 pinned={str(f.relative_to(source)):sha(f) for f in source.rglob('*') if f.is_file() and '.pio' not in f.parts and 'managed_components' not in f.parts and '__pycache__' not in f.parts}
 assert all(sha(tree/n)==h for n,h in pinned.items())
 identity_file=tree/'vdp/pio/p4-console-identity.json';record=json.loads(identity_file.read_text());record.update(source_identity='uart-excom-console-r23',status='draft',note='Agent-assigned Nurples output timing only; exact installed r22 drawing and transport retained.')
 identity_file.write_text(json.dumps(record,indent=2)+'\n')
 (tree/'vdp/.pio').mkdir();(tree/'vdp/.pio/packages').symlink_to(root/'vdp/.pio/packages',target_is_directory=True)
 shutil.copytree(source/'vdp/managed_components',tree/'vdp/managed_components')
 shutil.copy2(parent/'sdkconfig',out/'sdkconfig')
 cfg=configparser.ConfigParser(interpolation=None);cfg.optionxform=str;cfg.read(parent/'platformio.ini')
 cfg['platformio']['build_dir']=str(out/'build');cfg['env:p4-console']['board_build.esp-idf.sdkconfig_path']=str(out/'sdkconfig')
 assert 'AGON_EXTENDER_VIDEO_TIMING' not in cfg['env:p4-console']['build_flags']
 cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_VIDEO_TIMING=1'
 with (out/'platformio.ini').open('w') as f:cfg.write(f)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ');identity='uart-excom-console-r23-b'+stamp
 manifest={'build_id':identity,'status':'draft','parent_build_id':meta['build_id'],'parent_app_sha256':sha(parent/'firmware.bin'),'contract_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'parent_source_sha256':pinned,'source_change':'identity only','configuration_change':'enable existing AGON_EXTENDER_VIDEO_TIMING=1','scope':'snapshot/send timing; no VDP algorithm or MOS changes'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 cmd=[str(root/'.venv/bin/pio'),'run','-d',str(tree/'vdp'),'-c',str(out/'platformio.ini'),'-e','p4-console']
 with (out/'build.log').open('w') as log:subprocess.run(cmd,env=dict(os.environ,AGON_EXTENDER_BUILD_ID=identity,AGON_EXTENDER_DSP_LIFETIME_FIX='1'),stdout=log,stderr=subprocess.STDOUT,check=True)
 assert all(sha(source/n)==h for n,h in pinned.items())
 assert all(sha(tree/n)==h for n,h in pinned.items() if n!='vdp/pio/p4-console-identity.json')
 outputs={}
 for n in ('firmware.bin','firmware.elf','firmware.factory.bin','partitions.bin','bootloader.bin'):
  shutil.copy2(out/'build/p4-console'/n,out/n);outputs[n]={'bytes':(out/n).stat().st_size,'sha256':sha(out/n)}
 assert identity.encode() in (out/'firmware.bin').read_bytes()
 assert sha(out/'partitions.bin')==sha(parent/'partitions.bin')
 manifest.update(outputs=outputs,build_complete=True);(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(identity+' built; unflashed',flush=True)
if __name__=='__main__':main()
