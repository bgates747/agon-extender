from pathlib import Path
import subprocess,json,random,struct,playwright
NODE=str(Path(playwright.__file__).parent/"driver/node")
T=Path('docs/tasks/BENCH-005/composed-packing/sixbit');R=Path('agents/sixbit');r=random.Random(817)
(R/'encode.cpp').write_text('#include "packed.hpp"\n#include <cstdio>\n#include <vector>\nint main(){std::vector<uint8_t>s;int c;while((c=getchar())!=EOF)s.push_back(c);std::vector<uint8_t>d(s.size()+64);auto n=packed_frame::encode(s.data(),s.size(),d.data(),d.size(),s.size()+65,true);fwrite(d.data(),1,n,stdout);}\n')
subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-I'+str(T),str(R/'encode.cpp'),'-o',str(R/'encode')],check=True)
(R/'protocol.mjs').write_bytes((R/'web/frame_protocol.js').read_bytes())
(R/'decode.mjs').write_text('import {parseFrame} from "./protocol.mjs";import fs from "node:fs";const b=fs.readFileSync(0);try{const f=parseFrame(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));process.stdout.write(f.pixels);}catch(e){console.error(e.message);process.exit(2);}')
cases=[]
for w,h in [(1,1),(3,5),(320,200),(320,240),(640,240),(640,256),(512,384),(640,480),(640,512),(800,600),(1024,768)]:
 for colours in [1,2,3,4,5,16,17,64]:
  palette=r.sample(range(64),colours);raw=bytes(palette[r.randrange(colours)] for _ in range(w*h))
  encoded=subprocess.run([str(R/'encode')],input=raw,stdout=subprocess.PIPE,check=True).stdout
  actual=len(set(raw));assert bool(encoded),(w,h,colours)
  if not encoded:continue
  head=struct.pack('<4sBBBBIHHIIII',b'EVP1',1,32,2,1,0,w,h,w,w*h,16667,0)
  packet=head+encoded
  result=subprocess.run([NODE,str(R/'decode.mjs')],input=packet,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  assert result.returncode==0 and result.stdout==raw,(w,h,colours,result.stderr)
  cases.append(dict(w=w,h=h,colours=actual,bytes=len(encoded),pixels=len(raw)))
# Force six-bit tails at each non-byte-aligned pixel count.
for n in [17,18,19,20,21]:
 raw=bytes(range(n));encoded=subprocess.run([str(R/'encode')],input=raw,stdout=subprocess.PIPE,check=True).stdout
 assert encoded[0]==6 and len(encoded)==4+(n*6+7)//8
 head=struct.pack('<4sBBBBIHHIIII',b'EVP1',1,32,2,1,0,n,1,n,n,16667,0)
 result=subprocess.run([NODE,str(R/'decode.mjs')],input=head+encoded,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert result.returncode==0 and result.stdout==raw
 cases.append(dict(w=n,h=1,colours=n,bytes=len(encoded),pixels=n))
 for broken in [head+encoded[:-1],head+encoded+b'\0',head+bytes([6,1,0,0])+encoded[4:]]:
  result=subprocess.run([NODE,str(R/'decode.mjs')],input=broken,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert result.returncode==2
 if n%4:
  broken=bytearray(head+encoded);broken[-1]|=1
  result=subprocess.run([NODE,str(R/'decode.mjs')],input=broken,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert result.returncode==2
assert not subprocess.run([str(R/'encode')],input=bytes(range(65)),stdout=subprocess.PIPE,check=True).stdout
# Each malformed packet must be rejected, including out-of-palette indices.
raw=bytes([1,2,3]*5);enc=subprocess.run([str(R/'encode')],input=raw,stdout=subprocess.PIPE,check=True).stdout
head=struct.pack('<4sBBBBIHHIIII',b'EVP1',1,32,2,1,0,3,5,3,15,16667,0);base=head+enc
bad=[base[:-1],base+b'\0']
for offset,value in [(32,3),(33,0),(34,1),(36,64),(37,1),(39,255)]:
 b=bytearray(base);b[offset]=value;bad.append(bytes(b))
for b in bad:
 p=subprocess.run([NODE,str(R/'decode.mjs')],input=b,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert p.returncode==2
(T/'HOST-TESTS.json').write_text(json.dumps(dict(roundtrips=cases,malformed_rejected=len(bad)+19,sixbit=True),indent=2)+'\n')
print(len(cases),'exact C++ to JS roundtrips;',len(bad)+19,'malformed rejected')
