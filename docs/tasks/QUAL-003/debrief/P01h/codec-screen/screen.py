"""Generate identical-frame codec matrix and original-CLI/native correctness evidence."""
import argparse,ctypes as C,json,time,statistics,subprocess,hashlib,platform,io,itertools,multiprocessing
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--corpus',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=True);start=time.time();root=Path(__file__).resolve().parent
subprocess.run(['c++','-std=c++17','-O2','-shared','-fPIC',str(root/'png.cpp'),'-lz','-o',str(a.out/'png.so')],check=True)
lib=C.CDLL(str(a.build/'codec.so'));fn=lib.bench_szip;fn.argtypes=[C.c_int,C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t,C.POINTER(C.c_size_t),C.c_uint,C.c_uint,C.c_uint];fn.restype=C.c_int
pl=C.CDLL(str(a.out/'png.so'));pl.screen_rle.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];pl.screen_rle.restype=C.c_size_t;pl.screen_unrle.argtypes=pl.screen_rle.argtypes;pl.screen_unrle.restype=C.c_size_t;pl.screen_png.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_int,C.c_int,C.c_int,C.c_void_p,C.c_size_t];pl.screen_png.restype=C.c_size_t
variants=[dict(id='raw',kind='raw'),dict(id='rle2',kind='rle2')];seen=set()
for kind in ['szip','srle2']:
 grids=list(itertools.product([0,3,4,6],[32768,131072,4259840],[1],[False]))+list(itertools.product([0,4],[4259840],[1,2,3,4,8],[False,True]))
 for o,b,r,i in grids:
  key=(kind,o,b,r,i)
  if key in seen:continue
  seen.add(key);variants.append(dict(id=f'{kind}-o{o}-b{b}-r{r}-i{int(i)}',kind=kind,order=o,block=b,record=r,incremental=i))
for level,strategy,filter in itertools.product([1,3],[0,3,2],[0,1,2]):variants.append(dict(id=f'png-l{level}-s{strategy}-f{filter}',kind='png',level=level,strategy=strategy,filter=filter))
(a.out/'variants.json').write_text(json.dumps(variants,indent=2));manifest=json.loads((a.corpus/'manifest.json').read_text());rows=json.loads((a.out/'results.json').read_text()) if (a.out/'results.json').exists() else [];cap=2097152
for case in manifest:
 name=case['name'];raw=(a.corpus/name/'raw.bin').read_bytes();w,h=case['width'],case['height'];assert len(raw)==w*h
 dest=a.out/name;dest.mkdir(exist_ok=True);(dest/'raw.bin').write_bytes(raw);source=C.create_string_buffer(raw);tmp=C.create_string_buffer(cap);out=C.create_string_buffer(cap);decoded=C.create_string_buffer(cap)
 for v in variants:
  if any(r['case']==name and r['variant']==v['id'] for r in rows):continue
  queue=multiprocessing.Queue()
  def evaluate():
   samples=[];failure=None;result=b'';cli_checked=False
   for trial in range(4):
    t=time.perf_counter_ns();kind=v['kind']
    if kind=='raw':C.memmove(out,source,len(raw));n=len(raw)
    elif kind=='rle2':n=pl.screen_rle(source,len(raw),out,cap)
    elif kind=='png':n=pl.screen_png(source,w,h,v['level'],v['strategy'],v['filter'],out,cap)
    else:
     src=source;size=len(raw)
     if kind=='srle2':size=pl.screen_rle(source,len(raw),tmp,cap);src=tmp
     count=C.c_size_t();status=fn(0,src,size,out,cap,C.byref(count),v['order'],v['record']|(128 if v['incremental'] else 0),v['block']);n=count.value
     if status:failure=f'encode status {status}';break
    ms=(time.perf_counter_ns()-t)/1e6
    if not n:failure='encoder returned zero';break
    result=out.raw[:n];samples.append(ms)
   if not failure:
    if kind in ['szip','srle2']:
     count=C.c_size_t();status=fn(1,result,len(result),decoded,cap,C.byref(count),v['order'],v['record']|(128 if v['incremental'] else 0),v['block'])
     if status:failure=f'decode status {status}'
     else:
      data=decoded.raw[:count.value]
      if kind=='srle2':nn=pl.screen_unrle(data,len(data),tmp,cap);data=bytes(x&63 for x in tmp.raw[:nn])
      if data!=raw:failure='native decoded pixels differ'
     # One representative full-size case for each setting against the original CLI.
     if not failure and name=='retained-sprites':
      input_data=raw
      if kind=='srle2':nn=pl.screen_rle(source,len(raw),tmp,cap);input_data=tmp.raw[:nn]
      inp=dest/'cli-input.bin';ref=dest/'cli-output.bin';inp.write_bytes(input_data)
      opt=f'-o{v["order"]}r{v["record"]}'+('i' if v['incremental'] else '')
      if v['block']!=32768:opt+=('b1' if v['block']==131072 else 'b41')
      q=subprocess.run([str((a.build/'reference/szip').resolve()),opt,str(inp.resolve()),str(ref.resolve())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
      if q.returncode or ref.read_bytes()!=result:failure='original CLI mismatch'
      else:cli_checked=True
    elif kind=='png':
     image=Image.open(io.BytesIO(result));rgb=image.convert('RGB').tobytes();expected=bytes(c for x in raw for c in [(x&3)*85,((x>>2)&3)*85,((x>>4)&3)*85]);assert rgb==expected
    elif kind=='rle2':
     nn=pl.screen_unrle(result,len(result),decoded,cap);assert bytes(x&63 for x in decoded.raw[:nn])==raw
    if not failure:(dest/(v['id']+'.bin')).write_bytes(result)
   queue.put(dict(case=name,variant=v['id'],kind=v['kind'],exact=not failure,failure=failure,bytes=len(result),encode_ms=statistics.mean(samples[1:]) if len(samples)>1 else None,samples_ms=samples,original_cli_exact=cli_checked,sha256=hashlib.sha256(result).hexdigest()))
  job=multiprocessing.Process(target=evaluate);job.start();job.join(5)
  if job.is_alive():
   job.terminate();job.join();result=dict(case=name,variant=v['id'],kind=v['kind'],exact=False,failure='screening timeout: four encodes plus verification exceeded 5 seconds',bytes=0,encode_ms=None,samples_ms=[],original_cli_exact=False,sha256=None)
  elif job.exitcode or queue.empty():result=dict(case=name,variant=v['id'],kind=v['kind'],exact=False,failure=f'worker exit {job.exitcode}',bytes=0,encode_ms=None,samples_ms=[],original_cli_exact=False,sha256=None)
  else:result=queue.get()
  queue.close();rows.append(result)
  (a.out/'results.json').write_text(json.dumps(rows,indent=2))
 print(name,len(variants),'variants',sum(x['failure'] is not None for x in rows if x['case']==name),'failures',flush=True)
(a.out/'manifest.json').write_text(json.dumps(manifest,indent=2));(a.out/'complete.json').write_text(json.dumps(dict(seconds=time.time()-start,host=platform.platform(),python=platform.python_version(),variants=len(variants),cases=len(manifest),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()),indent=2))
