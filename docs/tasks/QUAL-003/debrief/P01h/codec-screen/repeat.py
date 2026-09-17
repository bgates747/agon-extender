"""Paired host timing confirmation for selected codecs, after browser testing."""
import argparse,ctypes as C,json,time,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--selected',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists()
lib=C.CDLL(str(a.build/'codec.so'));fn=lib.bench_szip;fn.argtypes=[C.c_int,C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t,C.POINTER(C.c_size_t),C.c_uint,C.c_uint,C.c_uint];fn.restype=C.c_int
pl=C.CDLL(str(a.native/'png.so'));pl.screen_rle.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t];pl.screen_rle.restype=C.c_size_t;pl.screen_png.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_int,C.c_int,C.c_int,C.c_void_p,C.c_size_t];pl.screen_png.restype=C.c_size_t
variants=json.loads(a.selected.read_text());rows=[];cap=2097152;out=C.create_string_buffer(cap);tmp=C.create_string_buffer(cap);start=time.time()
for name in ('retained-sprites','sprites1','noise'):
 raw=(a.native/name/'raw.bin').read_bytes();src=C.create_string_buffer(raw)
 def encode(v):
  kind=v['kind']
  if kind=='raw':C.memmove(out,src,len(raw));return len(raw)
  if kind=='rle2':return pl.screen_rle(src,len(raw),out,cap)
  if kind=='png':return pl.screen_png(src,512,384,v['level'],v['strategy'],v['filter'],out,cap)
  source=src;n=len(raw)
  if kind=='srle2':n=pl.screen_rle(src,n,tmp,cap);source=tmp
  count=C.c_size_t();status=fn(0,source,n,out,cap,C.byref(count),v['order'],v['record']|(128 if v['incremental'] else 0),v['block']);assert status==0;return count.value
 for v in variants:
  samples=[];bases=[]
  for i in range(22):
   pair={}
   for label,variant in ([('base',{'kind':'rle2'}),('candidate',v)] if i%2 else [('candidate',v),('base',{'kind':'rle2'})]):
    t=time.perf_counter_ns();n=encode(variant);ms=(time.perf_counter_ns()-t)/1e6;assert n>0;pair[label]=ms
    if label=='candidate':assert out.raw[:n]==(a.native/name/(v['id']+'.bin')).read_bytes()
   if i>=2:samples.append(pair['candidate']);bases.append(pair['base'])
  rows.append(dict(case=name,variant=v['id'],encode_ms=statistics.median(samples),paired_rle2_ms=statistics.median(bases),delta_pct=(statistics.median(samples)/statistics.median(bases)-1)*100,samples_ms=samples,baseline_samples_ms=bases))
  a.out.write_text(json.dumps(dict(seconds=time.time()-start,method='20 paired samples; alternating order; first two warmup pairs excluded; median',rows=rows),indent=2))
print('Paired host confirmation passed',len(rows),'case/settings')
