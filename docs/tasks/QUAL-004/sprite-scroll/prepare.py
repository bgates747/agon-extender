"""Deterministic accumulated sprite/scroll history, with background-only oracle.
Mode20 selected by startup. All resources remain live until capture completes.
No timing claim, random inputs, Copper, hardware sprites or game modifications.
"""
from pathlib import Path
import struct,json,hashlib,gzip
R=Path(__file__).resolve().parent
W,H=512,384;b=bytearray();bg=bytearray(W*H);cases=[]
def emit(*v):b.extend(v)
def words(*v):b.extend(struct.pack('<'+'H'*len(v),*(x&65535 for x in v)))
def fence():emit(23,0,202)
def select(n):emit(23,27,4,n)
def move(n,x,y):select(n);emit(23,27,13);words(x,y)
def viewport(top,bottom):emit(24);words(32,bottom,287,top)
def bitmap(n,pixels,w=16,h=16):
 emit(23,27,0,n,23,27,1);words(w,h)
 for p in pixels:
  if p is None:emit(0,0,0,0)
  else:emit((p&3)*85,((p>>2)&3)*85,((p>>4)&3)*85,255)
def checkpoint(name,description):
 fence();raw=bytes(b);bar=b'Q4B1'+len(raw).to_bytes(3,'little')+b'\0\0'
 (R/(name+'.vdu')).write_bytes(raw);(R/(name+'.vdu.bar')).write_bytes(bar)
 cases.append(dict(name=name,file=name+'.vdu',mode=20,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),barrier_sha256=hashlib.sha256(bar).hexdigest(),description=description))
emit(23,27,7,0,23,27,15);fence();emit(23,27,17,4,26,20,23,1,0,23,0,192,0,17,128,12,18,0,128)
# Four exact primary/grey strips, no copied renderer logic.
for i in range(16):
 c=(1,2,4,7)[i%4];packed=(2,8,32,42)[i%4];x=32+i*16
 emit(18,0,c,25,4);words(x,32);emit(25,101);words(x+15,223)
 for y in range(32,224):bg[y*W+x:y*W+x+16]=bytes([packed])*16
fence()
bitmap(0,[3 if x==y or x+y==15 or 5<=x<=10 else None for y in range(16) for x in range(16)])
bitmap(1,[15 if x==y or x+y==15 or 5<=x<=10 else None for y in range(16) for x in range(16)])
bitmap(2,[60 if x in (0,15) or y in (0,15) or (x+y)%5==0 else None for y in range(16) for x in range(16)])
strip=[63 if (x+y)%2==0 else 48 for y in range(8) for x in range(16)];bitmap(3,strip,16,8)
for n,frames in [(0,(0,1)),(1,(2,))]:
 select(n);emit(23,27,5)
 for f in frames:emit(23,27,6,f)
 emit(23,27,18,0,23,27,20,23,27,11)
move(0,80,80);move(1,160,100);emit(23,27,7,2,23,27,15);checkpoint('SS_INITIAL','Two separated transparent software sprites on striped background')
def step(i,x0,y0,x1,y1):
 viewport(32,223);emit(23,7,2,3,1);fence()
 # Explicit top/bottom pixel rows: only first row of an 8-row bitmap may land.
 viewport(223,223);emit(23,27,0,3)
 for x in range(32,288,16):emit(25,237);words(x,223)
 fence();emit(26)
 for y in range(32,223):bg[y*W+32:y*W+288]=bg[(y+1)*W+32:(y+1)*W+288]
 bg[223*W+32:223*W+288]=bytes(strip[:16])*16
 move(0,x0,y0);select(0);emit(23,27,10,i%2);move(1,x1,y1);emit(23,27,15);fence()
for i in range(1,5):step(i,80+i*8,80+i*4,160-i*10,100-i)
checkpoint('SS_OVERLAP','Four scroll/refill/frame/move updates ending in sprite overlap')
for i,pos in enumerate(((200,120,208,124),(280,216,284,219),(400,260,408,268),(-7,60,507,379)),5):step(i,*pos)
checkpoint('SS_EDGES','Eight updates; sprites partially outside opposite screen edges')
for n in (0,1):select(n);emit(23,27,12)
emit(23,27,15);checkpoint('SS_HIDDEN','Both sprites hidden; complete background must be restored')
(R/'hidden-background.bin.gz').write_bytes(gzip.compress(bytes(bg),mtime=0))
(R/'manifest.json').write_text(json.dumps({'identity':'sprite-scroll-probe-r01','surface':[W,H],'cases':cases,'hidden_oracle_sha256':hashlib.sha256(bg).hexdigest()},indent=2)+'\n')
