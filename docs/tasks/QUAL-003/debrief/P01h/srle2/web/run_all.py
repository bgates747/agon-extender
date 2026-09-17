"""One-command bench-free qualification; every subprocess has a bounded deadline."""
import argparse,datetime,hashlib,json,os,signal,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[6]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--emcc',type=Path,required=True)
p.add_argument('--source-client',type=Path,default=ROOT/'client-source')
p.add_argument('--output',type=Path,required=True)
p.add_argument('--count',type=int,default=20)
p.add_argument('--repeats',type=int,default=2)
a=p.parse_args()
assert 3<=a.count<=300 and 2<=a.repeats<=5
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
started=time.time();deadline=time.monotonic()+1200
record=dict(run='QUAL-003-'+datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d-%H-%M-%SZ'),started_utc=datetime.datetime.now(datetime.UTC).isoformat(),complete=False,steps=[])
def save():
 record['seconds']=time.time()-started
 (out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
def step(name,script,*args):
 command=[str(REPO/'.venv/bin/python'),str(ROOT/script),*map(str,args)]
 begin=time.time();row=dict(name=name,command=command);record['steps'].append(row);save()
 with (out/(name+'.log')).open('w') as log:
  child=subprocess.Popen(command,cwd=REPO,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   code=child.wait(timeout=max(1,deadline-time.monotonic()))
   if code:raise RuntimeError(f'{name}: exit {code}; see {name}.log')
  finally:
   # Kill only descendants in our private process group, including orphaned browsers.
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
 row.update(passed=True,seconds=time.time()-begin);save();print(name,'PASS',flush=True)
try:
 record['source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
 record['task_sources']={str(f.relative_to(ROOT.parent)):hashlib.sha256(f.read_bytes()).hexdigest() for f in ROOT.parent.rglob('*') if f.is_file() and f.suffix in ('.py','.js','.h','.inc') and '__pycache__' not in str(f)}
 step('corpus','corpus.py',out/'corpus')
 step('build','build_decoder.py',out/'decoder','--emcc',a.emcc.resolve())
 step('client','prepare_client.py',a.source_client.resolve(),out/'decoder',out/'client')
 step('native','native_check.py',out/'decoder/codec.so',out/'corpus',out/'native.json')
 step('native-edges','native_edges.py',out/'decoder/codec.so',out/'corpus/reference/szip',out/'native-edges')
 step('edges','edges.py','--corpus',out/'corpus','--client',out/'client','--native-edges',out/'native-edges','--output',out/'edges')
 for n in range(a.repeats):
  step(f'replay{n+1}','replay.py','--corpus',out/'corpus','--client',out/'client','--output',out/f'replay{n+1}','--count',a.count)
 step('report','report.py',out)
 record['complete']=True
except BaseException as e:
 record['error']=str(e);raise
finally:save()
