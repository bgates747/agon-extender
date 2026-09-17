"""Build pinned Linux encoder and create raw/RLE2/SRLE2 golden fixtures."""
from pathlib import Path
import argparse,hashlib,json,random,shutil,struct,subprocess
p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];out=a.output;out.mkdir(exist_ok=False);src=out/'reference';shutil.copytree(root/'vendor',src)
files=['szip.c','rangecod.c','qsmodel.c','bitmodel.c','sz_mod4.c','sz_srt.c','reorder.c']
# Original CLI remains unmodified; sz_unsrt(NULL) writes decoded output itself.
subprocess.run(['cc','-O2','-DGCC',*files,'-o','szip'],cwd=src,check=True)
def rle(data):
 b=bytearray(b'Cmpr'+struct.pack('<I',len(data))+b'RLE2\1\0');i=0
 while i<len(data):
  j=i+1
  while j<len(data) and j-i<130 and data[j]==data[i]:j+=1
  n=j-i
  if n>=3:b.extend((n-3,data[i]|192))
  else:b.extend([data[i]|192]*n)
  i=j
 return bytes(b)
rng=random.Random(0x53524c32);cases=[('colours',64,1,bytes(range(64))),('tiny',1,1,b'\x15')]
w,h=512,384
cases += [('solid',w,h,bytes([21])*(w*h)),('stripes',w,h,bytes((x//16)%64 for y in range(h) for x in range(w))),('noise',w,h,bytes(rng.randrange(64) for _ in range(w*h)))]
for phase in range(3):
 cases.append((f'scroll{phase}',w,h,bytes(((x+phase)//8+y//8)%64 for y in range(h) for x in range(w))))
 cases.append((f'sprites{phase}',w,h,bytes((63 if ((x-phase*5)%73<16 and y%47<16) else (x//32+y//32)%8) for y in range(h) for x in range(w))))
# Retained task-owned synthetic bitmap/sprite scene from physical validation.
import gzip
f=root.parent/'evidence/raw_sprites-r06.evf.gz'
if f.exists():cases.append(('retained-sprites',w,h,gzip.decompress(f.read_bytes())[32:]))
manifest=[]
for name,w,h,raw in cases:
 assert len(raw)==w*h and max(raw)<64
 d=out/name;d.mkdir();(d/'raw.bin').write_bytes(raw);(d/'rle2.bin').write_bytes(rle(raw))
 subprocess.run([str((src/'szip').resolve()),'-b41o3',str((d/'rle2.bin').resolve()),str((d/'srle2.bin').resolve())],check=True,timeout=20,stdout=subprocess.DEVNULL,stderr=(d/'encoder.log').open('w'))
 subprocess.run([str((src/'szip').resolve()),'-d',str((d/'srle2.bin').resolve()),str((d/'decoded-rle2.bin').resolve())],check=True,timeout=20,stdout=subprocess.DEVNULL,stderr=(d/'decoder.log').open('w'))
 assert (d/'decoded-rle2.bin').read_bytes()==(d/'rle2.bin').read_bytes(),name
 manifest.append(dict(name=name,width=w,height=h,stride=w,format=2,source=('retained P01h task-owned raw_sprites-r06.evf.gz' if name=='retained-sprites' else 'corpus.py deterministic synthetic generator'),seed='0x53524c32',files={n:dict(bytes=(d/(n+'.bin')).stat().st_size,sha256=hashlib.sha256((d/(n+'.bin')).read_bytes()).hexdigest()) for n in ('raw','rle2','srle2')}))
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(name,'golden PASS',flush=True)
