#!/usr/bin/env python3
"""Add timing diagnostics to a preserved P4 build bundle, retaining its backend."""
import argparse
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
if args.output.exists():p.error('output must be a fresh directory')
from pathlib import Path
import subprocess, shutil, os, json, datetime, hashlib
root=Path(__file__).resolve().parents[3]; stage=args.output.resolve(); parent=args.baseline.resolve()
stage.mkdir(parents=True,exist_ok=True)
source=stage/'source/vdp'
if not source.exists(): shutil.copytree(parent/'source/vdp',source,symlinks=True)
for name in ['graphics_timing.hpp','graphics_command.inc','frame_records.hpp']:
 shutil.copy2(root/'vdp/video/extender/diagnostics'/name,source/'video/extender/diagnostics'/name)
config=(parent/'platformio.ini').read_text().replace(str(parent/'build'),str(stage/'build')).replace(str(parent/'sdkconfig'),str(stage/'sdkconfig'))
config += '\n' if not config.endswith('\n') else ''
# The preserved console baseline does not enable private graphics commands.
config=config.replace('\t-D AGON_EXTENDER_VIDEO_POLL_MS=1','\t-D AGON_GRAPHICS_TIMING=1\n\t-D AGON_EXTENDER_VIDEO_POLL_MS=1')
assert '-D AGON_GRAPHICS_TIMING=1' in config
(stage/'platformio.ini').write_text(config);shutil.copy2(parent/'sdkconfig',stage/'sdkconfig')
build='game-timing-probe-r01-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
(stage/'pending-build-id').write_text(build)
with (stage/'build.log').open('w') as log:
 subprocess.run([str(root/'.venv/bin/pio'),'run','-d',str(source),'-c',str(stage/'platformio.ini'),'-e','p4-console'],env=dict(os.environ,AGON_EXTENDER_BUILD_ID=build,AGON_EXTENDER_DSP_LIFETIME_FIX='1'),stdout=log,stderr=subprocess.STDOUT,check=True)
m={'build_id':build,'status':'experimental','parent_build_id':json.loads((parent/'manifest.json').read_text())['build_id'],'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'dirty':True,'outputs':{},'source_delta':{}}
for n in ['firmware.bin','firmware.factory.bin','firmware.elf','bootloader.bin','partitions.bin']:
 shutil.copy2(stage/'build/p4-console'/n,stage/n);d=(stage/n).read_bytes();m['outputs'][n]={'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
assert b'GT1,id,submitted_us,completed_us,drain_us' in (stage/'firmware.bin').read_bytes(), 'Timing command missing from linked image'
for f in source.joinpath('video').rglob('*'):
 if not f.is_file() or f.suffix in ('.orig','.rej'):continue
 rel=f.relative_to(source);p=parent/'source/vdp'/rel
 if not p.exists() or f.read_bytes()!=p.read_bytes():m['source_delta'][str(rel)]=hashlib.sha256(f.read_bytes()).hexdigest()
(stage/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(build, list(m['source_delta']))
