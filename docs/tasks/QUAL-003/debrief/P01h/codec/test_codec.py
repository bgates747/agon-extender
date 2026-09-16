"""Host correctness/size evidence. Host timings never represent P4 timings."""
import argparse,ctypes as C,hashlib,json,random,struct,time,statistics
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--library',required=True);p.add_argument('--output',required=True);a=p.parse_args()
lib=C.CDLL(str(Path(a.library).resolve()));u=C.POINTER(C.c_ubyte)
lib.encode.argtypes=[u,C.c_size_t,u,C.c_size_t,C.POINTER(C.c_size_t),C.c_int]
lib.decode.argtypes=[u,C.c_size_t,u,C.c_size_t,C.POINTER(C.c_size_t)]
def call(fn,src,cap,*args):
 s=(C.c_ubyte*len(src)).from_buffer_copy(src);d=(C.c_ubyte*(cap+16))();d[cap:]=[0xa5]*16;o=C.c_size_t()
 status=fn(s,len(src),d,cap,C.byref(o),*args)
 assert bytes(d[cap:])==b'\xa5'*16
 return status,bytes(d[:o.value])
def reference_encode(src):
 out=bytearray(b'Cmpr'+struct.pack('<I',len(src))+b'RLE2\1\0');i=0
 while i<len(src):
  v=src[i];j=i+1
  while j<len(src) and j-i<130 and src[j]==v:j+=1
  n=j-i
  if n>=3:out.extend((n-3,v))
  else:out.extend([128|(v&63)|(64 if v&192==192 else 0)]*n)
  i=j
 return bytes(out)
def test(src,opaque=False):
 st,enc=call(lib.encode,src,len(src)+14,int(opaque));assert st==0
 expected=bytes(v|192 for v in src) if opaque else src
 assert enc==reference_encode(expected)
 st,dec=call(lib.decode,enc,len(src));assert st==0 and dec==expected
 assert len(enc)<=len(src)+14
 return enc
checks=0
for alpha in (0,192):
 for c in range(64):
  for n in (0,1,2,3,129,130,131,260,261):test(bytes([alpha|c])*n);checks+=1
rng=random.Random(0x524c4532)
for n in range(512):test(bytes(rng.choice((0,192))|rng.randrange(64) for _ in range(n)));checks+=1
for n in (1,2,3,130):assert call(lib.encode,bytes([64])*n,n+14,0)[0]!=0;checks+=1
# Decoder preserves arbitrary literal alpha in historical run packets.
packet=b'Cmpr'+struct.pack('<I',3)+b'RLE2\1\0'+bytes([0,65]);assert call(lib.decode,packet,3)==(0,b'AAA')
valid=test(bytes([193])*130)
for n in range(len(valid)):assert call(lib.decode,valid[:n],130)[0]!=0;checks+=1
for bad in (valid+b'\xc0',valid[:12]+b'\2\0'+valid[14:],valid[:4]+struct.pack('<I',129)+valid[8:],valid[:4]+struct.pack('<I',131)+valid[8:]):assert call(lib.decode,bad,140)[0]!=0;checks+=1
assert call(lib.decode,valid,129)[0]!=0
# Arbitrary malformed input: bounded decoder must never overwrite guard.
for _ in range(10000):
 n=rng.randrange(100);src=bytes(rng.randrange(256) for _ in range(n))
 if n>=14 and rng.randrange(2):src=b'Cmpr'+struct.pack('<I',rng.randrange(200))+b'RLE2\1\0'+src[14:]
 call(lib.decode,src,200)
rows=[];seen=set()
root=Path('docs/tasks/QUAL-004/evidence')
inputs=[]
for f in sorted(root.rglob('mainboard.png')):
 data=bytes((r//85)|((g//85)<<2)|((b//85)<<4) for r,g,b in Image.open(f).convert('RGB').getdata())
 sha=hashlib.sha256(data).hexdigest()
 if sha in seen:continue
 seen.add(sha);inputs.append((str(f),data))
inputs += [('solid',bytes(196608)),('noise',bytes(rng.randrange(64) for _ in range(196608))),('scroll',bytes((x+y)%64 for y in range(384) for x in range(512))),('sprites',bytes((x//16+y//16)%64 for y in range(384) for x in range(512)))]
for name,data in inputs:
 enc=test(data,True);rows.append(dict(input=name,bytes=len(data),encoded_bytes=len(enc),payload_bytes=len(enc)-14,ratio=len(enc)/len(data),sha256=hashlib.sha256(data).hexdigest()))
Path(a.output).write_text(json.dumps(dict(golden_random_checks=checks,malformed_trials=10000,images=rows,all_pass=True),indent=2)+'\n')
print(json.dumps(dict(checks=checks,malformed=10000,images=len(rows),pass_all=True)))
