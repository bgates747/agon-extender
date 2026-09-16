"""Decode opaque EVF1 and compare every canonical pixel; never resize/crop to pass."""
import argparse,json,struct,hashlib
from pathlib import Path
from PIL import Image
from capture import decode,rgb

def evf(raw):
 if len(raw)<32 or raw[:4]!=b'EVF1':raise ValueError('EVF header')
 version,header,fmt,flags=raw[4:8]
 seq,w,h,stride,size,period,reserved=struct.unpack_from('<IHHIIII',raw,8)
 if version!=1 or header!=32 or fmt not in (1,2) or not flags&1 or flags&~3 or reserved:raise ValueError('EVF flags')
 bpp=1 if fmt==2 else 3
 if not(0<w<=1024 and 0<h<=768) or stride!=w*bpp or size!=stride*h or len(raw)!=32+size:raise ValueError('EVF size')
 data=raw[32:]
 if fmt==2:
  if any(b>63 for b in data):raise ValueError('EVF colour')
  pixels=data
 else:
  if any(b%85 for b in data):raise ValueError('non-Agon RGB colour')
  pixels=bytes((data[i]//85)|((data[i+1]//85)<<2)|((data[i+2]//85)<<4) for i in range(0,len(data),3))
 return dict(width=w,height=h,pixels=pixels,sequence=seq,period=period,sha256=hashlib.sha256(pixels).hexdigest())
def compare(a,b,out):
 if (a['width'],a['height'])!=(b['width'],b['height']):raise ValueError('dimension mismatch')
 w,h=a['width'],a['height'];pa,pb=a['pixels'],b['pixels'];assert len(pa)==len(pb)==w*h
 diff=[i for i,(x,y) in enumerate(zip(pa,pb)) if x!=y]
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 for n,p in [('mainboard',pa),('p4',pb)]:Image.frombytes('RGB',(w,h),rgb(p)).save(out/(n+'.png'))
 mask=bytes(v for x,y in zip(pa,pb) for v in ((255,0,255) if x!=y else (0,0,0)))
 Image.frombytes('RGB',(w,h),mask).save(out/'difference.png')
 record=dict(width=w,height=h,pixels=w*h,mismatches=len(diff),match=not diff,bounds=[min(i%w for i in diff),min(i//w for i in diff),max(i%w for i in diff),max(i//w for i in diff)] if diff else None,mainboard_sha256=hashlib.sha256(pa).hexdigest(),p4_sha256=hashlib.sha256(pb).hexdigest())
 (out/'comparison.json').write_text(json.dumps(record,indent=2)+'\n');return record
