"""Normal routed VDU asset fixtures. Mode selection belongs to autoexec."""
from pathlib import Path
import struct,json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False)
def u(n):return struct.pack('<H',n)
def buf(i,c):return bytes([23,0,160])+u(i)+bytes([c])
def upload(i,data,chunks=None):
 out=buf(i,2)
 for chunk in chunks or [data]:out+=buf(i,0)+u(len(chunk))+chunk
 return out
raw=bytes((0 if (x//8+y//8)%5==0 else 192)|((x//8)&3)|(((y//8)&3)<<2)|((((x+y)//16)&3)<<4) for y in range(64) for x in range(64))
def encode(src):
 out=bytearray(b'Cmpr'+struct.pack('<I',len(src))+b'RLE2\1\0');i=0
 while i<len(src):
  j=i+1
  while j<len(src) and j-i<130 and src[j]==src[i]:j+=1
  n=j-i;v=src[i]
  out.extend([n-3,v] if n>=3 else [128|(v&63)|(64 if v&192==192 else 0)]*n);i=j
 return bytes(out)
packed=encode(raw);bad=bytearray(packed);bad[12]=2
cases={
 'raw':upload(3000,raw),
 'rle':upload(3001,packed)+buf(3000,65)+u(3001),
 'fragmented':upload(3001,packed,[packed[:2],packed[2:13],packed[13:15],packed[15:]])+buf(3000,65)+u(3001),
 'inplace':upload(3000,packed)+buf(3000,65)+u(3000),
 'invalid_version':upload(3000,raw)+upload(3001,bytes(bad))+buf(3000,65)+u(3001),
 'truncated':upload(3000,raw)+upload(3001,packed[:-1])+buf(3000,65)+u(3001),
 'overflow':upload(3000,raw)+upload(3001,b'Cmpr'+struct.pack('<I',1)+b'RLE2\1\0'+b'\x7f\xff')+buf(3000,65)+u(3001),
}
start=bytes([23,0,202,4,26,23,1,0,23,0,192,0,23,27,7,0,23,27,17,17,128,12])
plot=bytes([23,27,32])+u(3000)+bytes([23,27,33])+u(64)+u(64)+bytes([1,23,27,3])+u(80)+u(64)+bytes([23,0,202])
rows=[]
for name,commands in cases.items():
 data=start+commands+plot
 (a.out/(name+'.vdu')).write_bytes(data);(a.out/(name+'.vdu.bar')).write_bytes(b'Q4B1'+len(data).to_bytes(3,'little')+b'\0\0')
 rows.append(dict(name=name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
(a.out/'manifest.json').write_text(json.dumps(dict(raw_bytes=len(raw),encoded_bytes=len(packed),cases=rows),indent=2)+'\n')
(a.out/'expected.rgba2222').write_bytes(raw)
