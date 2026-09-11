from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,yaml
R=Path.cwd();T=R/'docs/tasks/QUAL-003/timing'
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--human',action='store_true');p.add_argument('--native',type=Path,required=True);p.add_argument('--peer-native',type=Path,required=True);p.add_argument('--runtime',type=Path,default=R/'.emulator/graphics-timing/runtime-backpressure');a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);media=out/'sdcard';media.mkdir()
bundle=R/'agents/graphics-timing/emos-draft-a1';manifest=yaml.safe_load((bundle/'build-manifest.yaml').read_text());outputs={i['role']:bundle/i['filename'] for i in manifest['outputs']}
for i in manifest['outputs']:assert hashlib.sha256((bundle/i['filename']).read_bytes()).hexdigest()==i['sha256']
# Populate FAT image from a separate tree; no production media path is opened.
staging=out/'image-files';shutil.copytree(bundle/'emos-sdcard',staging);dest=staging/'extender/gqt';shutil.copytree(T/'fixture/media',dest)
shutil.copy2(T/'fixture/bin/GQTBENCH.bin',dest/'GQTBENCH.BIN')
shutil.copy2(T/'fixture/build/corpus.json',media/'corpus.json')
(staging/'autoexec.txt').write_bytes(b'VDU 22 3\r\nEMOS KEYINPUT extender\r\nVDU 22 20\r\nEMOS EXCOM\r\nVDU 22 20\r\nCD /extender/gqt\r\nLOAD GQTBENCH.BIN\r\nRUN . review\r\n')
mcopy=R/'agents/uart-benchmark/tools/unpacked/usr/bin/mcopy';image=media/'initial.img'
with image.open('wb') as f:f.truncate(64*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
subprocess.run([str(mcopy),'-i',str(image),'-s',*[str(p) for p in staging.iterdir()],'::/'],check=True)
for source,name in [(a.native,'mainboard-native.so'),(a.peer_native,'peer-native.so'),(R/'scripts/console_peer.py','console_peer.py'),(R/'docs/tasks/QUAL-003/timing/scripts/vdu_framer.py','vdu_framer.py'),(R/'docs/tasks/QUAL-003/timing/scripts/timing_peer.py','timing_peer.py')]:shutil.copy2(source,media/name)
subprocess.run(['c++','-std=c++17','-shared','-fPIC','-Wall','-Wextra','-Werror','-I'+str(R/'vdp/video'),str(R/'tests/console_session_peer.cpp'),'-o',str(media/'console-session.so')],check=True)
subprocess.run(['gcc','-shared','-fPIC','-I'+str(Path.home()/'.local/include'),str(R/'docs/tasks/QUAL-003/suite/tests/sdl_review.c'),'-ldl','-o',str(media/'sdl-review.so')],check=True)
maptext=(T/'fixture/bin/GQTBENCH.map').read_text();symbols={n:int(v,16) for v,n in re.findall(r'^\s*(0x[0-9a-f]+)\s+(_graphics_done|_graphics_exit_status)\s*$',maptext,re.M)}
(media/'review.json').write_text(json.dumps(dict(build_id=json.loads((T/'fixture/build/build.json').read_text())['build_id'],human=a.human,done=symbols['_graphics_done'],status=symbols['_graphics_exit_status'],mcopy=str(mcopy)),indent=2)+'\n')
sys.path.insert(0,str(R.parent/'agon-emos/scripts'));from review_boot import make_profile
make_profile(out/'profile',outputs['firmware'],outputs['firmware_map'],media,Path.home()/'Agon/fab-agon-emulator',runtime=a.runtime.resolve(),peer=media/'timing_peer.py',mutable_names=())
print(out/'profile')
