#!/usr/bin/env python3
"""Build an isolated repair atop the exact archived installed-source inputs.
No flash. Original archive/config remain immutable. Output is ignored local data.
"""
import argparse,configparser,datetime,hashlib,json,os,shutil,subprocess,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 parent=a.parent.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 original=json.loads((parent/'manifest.json').read_text());tree=out/'source';tree.mkdir()
 with tarfile.open(parent/'source.tar.gz') as tar:tar.extractall(tree,filter='data')
 for name,digest in original['inputs'].items():assert sha(tree/name)==digest,name
 patch=subprocess.check_output(['git','diff','966345e',commit,'--','vdp/video/vdu_buffered.h'],cwd=ROOT)
 patch+=subprocess.check_output(['git','diff','9c38c43',commit,'--','vdp/video/extender/network/wired_network_service.cpp','vdp/video/extender/network/wired_network_service.hpp'],cwd=ROOT)
 assert patch
 subprocess.run(['patch','--dry-run','--batch','-p1'],input=patch,cwd=tree,check=True)
 subprocess.run(['patch','--batch','-p1'],input=patch,cwd=tree,check=True)
 (out/'repair.patch').write_bytes(patch)
 for name in ('vdp/video/extender/port/fixed_conversion.hpp','vdp/pio/p4-console-identity.json'):
  dest=tree/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
 changed={n:sha(tree/n) for n,h in original['inputs'].items() if sha(tree/n)!=h}
 assert set(changed)=={'vdp/video/vdu_buffered.h','vdp/pio/p4-console-identity.json','vdp/video/extender/network/wired_network_service.cpp','vdp/video/extender/network/wired_network_service.hpp'},changed
 # Reuse package/component installations, not older compiler build outputs.
 (tree/'vdp/.pio').mkdir(exist_ok=True)
 (tree/'vdp/.pio/packages').symlink_to(ROOT/'vdp/.pio/packages',target_is_directory=True)
 shutil.copytree(ROOT/'vdp/managed_components',tree/'vdp/managed_components')
 shutil.copy2(ROOT/'vdp/pio/p4-console-dependencies.lock',tree/'vdp/dependencies.lock')
 shutil.copy2(parent/'sdkconfig.videopoll1tcp32k',out/'sdkconfig')
 config=configparser.ConfigParser(interpolation=None);config.optionxform=str;config.read(parent/'platformio.ini')
 config['platformio']['build_dir']=str(out/'build')
 config['env:p4-console']['board_build.esp-idf.sdkconfig_path']=str(out/'sdkconfig')
 with (out/'platformio.ini').open('w') as f:config.write(f)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ');identity='uart-excom-console-r19-b'+stamp
 manifest=dict(build_id=identity,status='draft',patch_commit=commit,parent_build_id=original['build_id'],parent_historical_dirty=original['dirty'],parent_archive_sha256=sha(parent/'source.tar.gz'),changed_parent_inputs=changed,helper_sha256=sha(ROOT/'vdp/video/extender/port/fixed_conversion.hpp'),scope='NET-001 viewer takeover plus RX06 repair atop installed-source parent; no newer UART changes')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 cmd=[str(ROOT/'.venv/bin/pio'),'run','-d',str(tree/'vdp'),'-c',str(out/'platformio.ini'),'-e','p4-console']
 with (out/'build.log').open('w') as f:subprocess.run(cmd,env=dict(os.environ,AGON_EXTENDER_BUILD_ID=identity,AGON_EXTENDER_DSP_LIFETIME_FIX='1'),stdout=f,stderr=subprocess.STDOUT,check=True)
 outputs={}
 for name in ('firmware.bin','firmware.elf','firmware.factory.bin','partitions.bin','bootloader.bin'):
  shutil.copy2(out/'build/p4-console'/name,out/name);outputs[name]=dict(sha256=sha(out/name),bytes=(out/name).stat().st_size)
 assert identity.encode() in (out/'firmware.bin').read_bytes()
 sdk=(out/'build/p4-console/config/sdkconfig.h').read_text();assert '#define CONFIG_LWIP_TCP_SND_BUF_DEFAULT 32768' in sdk
 manifest.update(outputs=outputs,build_complete=True)
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(identity+' built; unflashed',flush=True)
if __name__=='__main__':main()
