"""Exact original-CLI/P4 controls; save each result before advancing."""
import argparse,hashlib,json,time,urllib.request,urllib.error,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--corpus',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--trials',type=int,default=3);a=p.parse_args();a.output.mkdir(exist_ok=False)
assert a.url.startswith('http://') and 1<=a.trials<=9
start=time.time();rows=[]
def call(op,data):
 req=urllib.request.Request(a.url+'/diagnostics/srle2?op='+op,data=data,headers={'Content-Type':'application/octet-stream'})
 began=time.perf_counter()
 try:
  with urllib.request.urlopen(req,timeout=30) as r:return r.status,r.read(),dict(r.headers),1000*(time.perf_counter()-began)
 except urllib.error.HTTPError as r:return r.code,r.read(),dict(r.headers),1000*(time.perf_counter()-began)
def save():
 (a.output/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
try:
 for case in json.loads((a.corpus/'manifest.json').read_text()):
  d=a.corpus/case['name'];rle=(d/'rle2.bin').read_bytes();packed=(d/'srle2.bin').read_bytes();raw=(d/'raw.bin').read_bytes()
  for op,data,expected in [('encode',rle,packed),('decode',packed,rle),('unpack',packed,bytes(x|192 for x in raw))]:
   samples=[]
   for trial in range(a.trials+1):
    status,result,headers,wall=call(op,data)
    if status!=200 or result!=expected:
     (a.output/'mismatch.bin').write_bytes(result);raise RuntimeError(f'{case["name"]}/{op}: HTTP{status}, exact={result==expected}, {headers}')
    samples.append(dict(codec_us=int(headers['X-Codec-Us']),http_ms=wall,stack_min_bytes=int(headers['X-Stack-Min-Bytes']),psram_before=int(headers['X-Psram-Free-Before']),psram_after=int(headers['X-Psram-Free-After'])))
   rows.append(dict(case=case['name'],operation=op,exact=True,input_bytes=len(data),output_bytes=len(expected),output_sha256=hashlib.sha256(expected).hexdigest(),samples=samples,steady_codec_us=statistics.mean(x['codec_us'] for x in samples[1:])));save();print(case['name'],op,'PASS',flush=True)
 # These bounded corruptions already rejected natively and in the isolated Worker.
 valid=(a.corpus/'colours/srle2.bin').read_bytes();negative={'truncated':valid[:-1],'short':b'CmpS'}
 b=bytearray(valid);b[13]=0x7f;negative['wrong-version']=bytes(b)
 for name,data in negative.items():
  status,result,headers,wall=call('decode',data);assert status==400,(name,status)
  status,result,_,_=call('decode',valid);assert status==200 and result==(a.corpus/'colours/rle2.bin').read_bytes()
  rows.append(dict(case=name,operation='reject-and-recover',exact=True));save();print(name,'PASS',flush=True)
 (a.output/'complete.json').write_text(json.dumps(dict(complete=True,seconds=time.time()-start,rows=len(rows),trials=a.trials))+'\n')
except BaseException as e:
 (a.output/'failure.json').write_text(json.dumps(dict(error=str(e),seconds=time.time()-start))+'\n');raise
