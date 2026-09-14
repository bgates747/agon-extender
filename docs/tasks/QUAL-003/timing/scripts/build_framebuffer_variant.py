#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,datetime
parser=argparse.ArgumentParser(description='Build the documented reduced framebuffer corpus without modifying the original fixture.')
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--omit-large-sprites',action='store_true',help='Also exclude BSP30_25 after its recorded mainboard timeout')
parser.add_argument('--unattended',action='store_true',help='Build the SD-progress and mainboard-status variant; run with unattended')
parser.add_argument('--continue-batch',action='store_true',help='Return to MOS batch after failure; CSV terminal remains authoritative')
parser.add_argument('--omit-population-page',action='store_true',help='Exclude all BSP30 population stress stages for the stable framebuffer baseline')
args=parser.parse_args()
root=Path(__file__).resolve().parents[5];src=root/'docs/tasks/QUAL-003/timing/fixture';out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);dst=out/'fixture'
dst.mkdir();shutil.copytree(src/'src',dst/'src');shutil.copy(src/'Makefile',dst/'Makefile');shutil.copytree(src/'media',dst/'media');shutil.copytree(src/'build',dst/'build')
if args.continue_batch:
 p=dst/'src/main.c';text=p.read_text();old='    return unattended?0:status;\n}\n';assert text.endswith(old);p.write_text(text[:-len(old)]+'    /* Batch continuation only: CSV terminal status determines test success. */\n    return 0;\n}\n')
corpus=json.loads((src/'build/corpus.json').read_text());excluded={'BSP30_22','BSP30_23','BSP30_24'}
if args.omit_large_sprites:excluded.add('BSP30_25')
if args.omit_population_page:excluded.update(c['name'] for c in corpus['cases'] if c['name'].startswith('BSP30_'))
assert len(corpus['cases'])==64
corpus['cases']=[c for c in corpus['cases'] if c['name'] not in excluded];corpus['total']=len(corpus['cases']);corpus['excluded']=sorted(excluded)
assert corpus['total']==64-len(excluded)
for c in corpus['cases']:assert hashlib.sha256((dst/'media'/(c['name']+'.DAT')).read_bytes()).hexdigest()==c['sha256']
for n in excluded:(dst/'media'/(n+'.DAT')).unlink()
header=(src/'build/cases.h').read_text();header='\n'.join(line for line in header.splitlines() if not any('"'+n+'"' in line for n in excluded))+'\n';header=header.replace('#define CASE_COUNT 64',f'#define CASE_COUNT {corpus["total"]}');(dst/'build/cases.h').write_text(header)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ');build_id=('graphics-timing-probe-r02-unattended-b' if args.unattended else 'graphics-timing-probe-r01-framebuffer-b')+stamp
(dst/'build/build_identity.h').write_text('#define GRAPHICS_BUILD_ID "'+build_id+' (experimental reduced corpus)"\n')
(dst/'build/corpus.json').write_text(json.dumps(corpus,indent=2)+'\n')
with (out/'build.log').open('w') as log:subprocess.run(['make','all'],cwd=dst,stdout=log,stderr=subprocess.STDOUT,check=True)
files={str(p.relative_to(dst)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dst.rglob('*') if p.is_file()}
(out/'build.json').write_text(json.dumps(dict(build_id=build_id,source_commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),excluded=sorted(excluded),continue_batch=args.continue_batch,cases=corpus['total'],expected_intervals=corpus['total']*16,files=files),indent=2)+'\n');print(build_id)
