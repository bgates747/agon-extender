from pathlib import Path
import subprocess,random,struct,json,playwright
T=Path('docs/tasks/BENCH-005/composed-packing/pair-rle');R=Path('agents/pair-rle');NODE=str(Path(playwright.__file__).parent/'driver/node')
(R/'encode.cpp').write_text('#include "pair.hpp"\n#include <cstdio>\n#include <vector>\nint main(){std::vector<uint8_t>s;int c;while((c=getchar())!=EOF)s.push_back(c);std::vector<uint8_t>d(s.size()+1);auto n=pair_rle::encode(s.data(),s.size(),d.data(),d.size(),s.size()+1);fwrite(d.data(),1,n,stdout);}\n')
subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-I'+str(T),str(R/'encode.cpp'),'-o',str(R/'encode')],check=True)
(R/'protocol.mjs').write_bytes((R/'web/frame_protocol.js').read_bytes())
(R/'decode.mjs').write_text('import {parseFrame} from "./protocol.mjs";import fs from "node:fs";let b=fs.readFileSync(0);try{let f=parseFrame(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));process.stdout.write(f.pixels);}catch(e){process.exit(2);}')
def encode(raw):return subprocess.run([str(R/'encode')],input=raw,stdout=subprocess.PIPE,check=True).stdout
def head(w,h):return struct.pack('<4sBBBBIHHIIII',b'EVQ1',1,32,2,1,0,w,h,w,w*h,16667,0)
def decode(b):return subprocess.run([NODE,str(R/'decode.mjs')],input=b,stdout=subprocess.PIPE)
rng=random.Random(817);cases=[]
for w,h in [(1,1),(3,1),(17,1),(18,1),(19,1),(20,1),(31,1),(32,1),(33,1),(34,1),(65,1),(320,200),(320,240),(512,384),(640,480),(1024,768)]:
 n=w*h
 patterns={'flat':bytes([37])*n,'pairs':bytes([3,60])*(n//2)+bytes([3])*(n%2),'random':bytes(rng.randrange(64) for _ in range(n)),'odd_runs':bytes((i//3)%64 for i in range(n))}
 for name,raw in patterns.items():
  enc=encode(raw);assert enc and len(enc)<=n;res=decode(head(w,h)+enc);assert res.returncode==0 and res.stdout==raw
  cases.append(dict(w=w,h=h,pattern=name,raw=n,encoded=len(enc)))
raw=bytes([x for i in range(32) for x in (i,i^63)]);assert len(encode(raw))==len(raw)
for raw in [b'\x40',b'\0\xff',bytes(range(65))]:assert not encode(raw)
bad=[head(2,1)+b'\0',head(2,1)+b'\0\x10',head(2,1)+b'\0\0\0',head(1,1)+b'\x40',head(3,1)+b'\0\0',head(3,1)+b'\0\0\x40',head(3,1)+b'\0\0\0\0',head(2,1)+b'\0\x90']
for b in bad:assert decode(b).returncode==2
(T/'HOST-TESTS.json').write_text(json.dumps({'roundtrips':cases,'malformed_rejected':len(bad),'nonexpansion':True,'worst_case_exact':True},indent=2)+'\n')
print(len(cases),'exact round trips;',len(bad),'malformed packets rejected; nonexpansion verified')
