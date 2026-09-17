"""Compile a prepared P4 candidate. Does not flash, connect to bench or run tests."""
from pathlib import Path
import argparse,os,subprocess,json,datetime,hashlib
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--revision',default='r01');a=p.parse_args();
assert __import__('re').fullmatch(r'r[0-9]{2,}',a.revision)
out=a.candidate.resolve()
identity='image-p4-'+a.revision+'-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
with (out/'build.log').open('w') as f:
 status=subprocess.run([str(Path('.venv/bin/pio').resolve()),'run','-d',str(out/'source/vdp'),'-c',str(out/'platformio.ini'),'-e','p4-console'],env=dict(os.environ,AGON_EXTENDER_BUILD_ID=identity,AGON_EXTENDER_DSP_LIFETIME_FIX='1'),stdout=f,stderr=subprocess.STDOUT).returncode
root=Path(__file__).resolve().parent
m=dict(build_id=identity,compile_only=True,tests_run=False,flashed=False,returncode=status,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),inputs={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in root.rglob('*') if f.is_file() and f.suffix in ('.c','.h','.hpp','.inc','.py')},outputs={})
if not status:
 for name in ['firmware.bin','firmware.factory.bin','firmware.elf','partitions.bin']:
  f=out/'build/p4-console'/name;m['outputs'][name]=dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');raise SystemExit(status)
