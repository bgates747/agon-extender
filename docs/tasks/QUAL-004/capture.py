"""Strict decoder for task-local scanout serial records; canonical BBGGRR bytes."""
import hashlib,re

def fnv(data):
 h=2166136261
 for b in data:h=((h^b)*16777619)&0xffffffff
 return h

def decode(raw):
 images=[];pos=0
 while True:
  begin=re.search(rb'Q4BEGIN (\d+) (\d+) (\d+)\n',raw[pos:])
  if not begin:break
  token,w,h=map(int,begin.groups());pos+=begin.end()
  if not (0<w<=1024 and 0<h<=1024):raise ValueError('dimensions')
  pixels=bytearray()
  for y in range(h):
   end=raw.find(b'\n',pos)
   if end<0:raise ValueError('truncated row header')
   match=re.fullmatch(rb'Q4ROW (\d+) (\d+) (\d+) ([0-9a-f]{8})',raw[pos:end])
   if not match:raise ValueError('row header')
   t,row,n=map(int,match.groups()[:3]);hashval=int(match.group(4),16)
   if (t,row,n)!=(token,y,w):raise ValueError('row identity/order')
   pos=end+1;data=raw[pos:pos+w];pos+=w
   if len(data)!=w or any(b>63 for b in data):raise ValueError('pixel payload')
   if fnv(data)!=hashval:raise ValueError('row checksum')
   if raw[pos:pos+1]!=b'\n':raise ValueError('row delimiter')
   pos+=1;pixels.extend(data)
  finish=f'Q4END {token} 1\n'.encode()
  if raw[pos:pos+len(finish)]!=finish:raise ValueError('capture terminal')
  pos+=len(finish)
  images.append(dict(token=token,width=w,height=h,pixels=bytes(pixels),sha256=hashlib.sha256(pixels).hexdigest()))
 return images

def rgb(pixels):
 return bytes(v for b in pixels for v in ((b&3)*85,((b>>2)&3)*85,((b>>4)&3)*85))
