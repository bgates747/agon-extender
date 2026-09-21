"""Reuse suite packed bytes; oracle computes source pattern, not VDP expansion.
Mode is owned by autoexec. No sprites, transforms, resource mutation or scaling.
"""
from pathlib import Path
import struct,json,hashlib,gzip
R=Path(__file__).resolve().parent
assets=R.parents[1]/'QUAL-003/suite/tgt/assets/bitmaps'
def w(*n):return struct.pack('<'+'H'*len(n),*n)
def buf(n,op,data=b''):return bytes((23,0,160))+w(n)+bytes((op,))+data
cases=[]
for bits in (1,2,4):
 source=(assets/f'packed{bits}.packed').read_bytes()
 # Decode retained source independently to validate its documented pattern.
 stride=(34*bits+7)//8
 assert len(source)==stride*34
 for y in range(34):
  for x in range(34):
   assert (source[y*stride+x*bits//8]>>(8-bits-(x*bits%8)))&((1<<bits)-1)==(x//4+y//4)%(1<<bits)
 mapping=bytes(0 if i==0 else 192|((i*7)&63) for i in range(1<<bits))
 b=bytearray((23,27,7,0,23,27,15,23,0,202,23,27,17,4,26,20,23,1,0,23,0,192,0,17,128,12))
 # White background exposes index-zero transparency (stock default white=42).
 b+=bytes((18,0,7,25,4))+w(64,64)+bytes((25,101))+w(97,97)+bytes((23,0,202))
 for ident,data in ((61030,source),(61040,mapping)):
  b+=buf(ident,0,w(len(data))+data)
 b+=buf(61034,72,bytes((bits|8|(16 if bits==2 else 0),))+w(61030,34)+(w(61040) if bits==2 else mapping))
 b+=bytes((23,27,32))+w(61034)+bytes((23,27,33))+w(34,34)+bytes((1,23,27,3))+w(64,64)+bytes((23,0,202))
 name=f'PACK{bits}';raw=bytes(b);bar=b'Q4B1'+len(raw).to_bytes(3,'little')+b'\0\0'
 oracle=bytearray(512*384)
 for y in range(34):
  for x in range(34):
   idx=(x//4+y//4)%(1<<bits)
   oracle[(64+y)*512+64+x]=42 if idx==0 else (idx*7)&63
 for suffix,data in (('.vdu',raw),('.vdu.bar',bar),('.oracle.gz',gzip.compress(bytes(oracle),mtime=0))):
  (R/(name+suffix)).write_bytes(data)
 cases.append(dict(name=name,bits=bits,mapping='buffer' if bits==2 else 'inline',source_sha256=hashlib.sha256(source).hexdigest(),sha256=hashlib.sha256(raw).hexdigest(),oracle_sha256=hashlib.sha256(oracle).hexdigest()))
(R/'manifest.json').write_text(json.dumps(dict(identity='packed-expansion-probe-r01',mode=20,surface=[512,384],cases=cases),indent=2)+'\n')
