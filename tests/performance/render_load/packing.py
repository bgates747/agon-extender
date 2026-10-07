"""Independent LZ4 block packing for untimed SD preload. No external dependency."""
import struct

def rle(data):
 """Bounded literal/repeated-byte tokens, independently decoded on the eZ80."""
 out=bytearray();i=0
 while i<len(data):
  n=1
  while i+n<len(data) and n<130 and data[i+n]==data[i]:n+=1
  if n>=3:out.extend((128+n-3,data[i]));i+=n;continue
  start=i;i+=n
  while i<len(data) and i-start<128:
   if i+2<len(data) and data[i]==data[i+1]==data[i+2]:break
   i+=1
  out.append(i-start-1);out+=data[start:i]
 return bytes(out)

def unrle(data):
 out=bytearray();i=0
 while i<len(data):
  token=data[i];i+=1
  if token&128:
   if i==len(data):raise ValueError('truncated repeat')
   out.extend(bytes([data[i]])*((token&127)+3));i+=1
  else:
   n=token+1
   if i+n>len(data):raise ValueError('truncated literal')
   out.extend(data[i:i+n]);i+=n
 return bytes(out)

def filter_case(raw):
 j=6+int.from_bytes(raw[4:6],'little');head=raw[:j];frames=[]
 for _ in range(40):
  n=int.from_bytes(raw[j:j+2],'little');j+=2;frames.append(raw[j:j+n]);j+=n
 if j!=len(raw) or len(set(map(len,frames)))!=1:raise ValueError('unequal frame lengths')
 n=len(frames[0]);planes=bytearray()
 for col in range(n):
  prev=0
  for f in range(40):v=frames[f][col];planes.append((v-prev)&255);prev=v
 return head+struct.pack('<H',n)+planes

def unfilter_case(data):
 j=6+int.from_bytes(data[4:6],'little');head=data[:j];n=int.from_bytes(data[j:j+2],'little');j+=2
 if len(data)!=j+40*n:raise ValueError('invalid plane length')
 frames=[bytearray(n) for _ in range(40)]
 for col in range(n):
  value=0
  for f in range(40):value=(value+data[j])&255;j+=1;frames[f][col]=value
 return head+b''.join(struct.pack('<H',n)+f for f in frames)

def pack_rle_stream(data):
 a=int.from_bytes(data[11:13],'little');asset=data[13:13+a];p=rle(asset)
 assert unrle(p)==asset
 out=bytearray(b'B9X1'+data[4:13]+struct.pack('<H',len(p))+p);i=13+a
 while True:
  n=int.from_bytes(data[i:i+2],'little');i+=2
  if not n:out+=b'\0\0';break
  raw=data[i:i+n];i+=n;filtered=filter_case(raw);p=rle(filtered)
  assert unfilter_case(unrle(p))==raw and len(filtered)==n-78
  if len(p)>65535:raise ValueError('packed block too long')
  out+=struct.pack('<HH',n,len(p))+p
 assert i==len(data)
 return bytes(out)

def unpack_rle_stream(data):
 a,p=struct.unpack_from('<HH',data,11);i=15
 asset=unrle(data[i:i+p]);i+=p
 if len(asset)!=a:raise ValueError('asset size')
 out=bytearray(b'B9D1'+data[4:13]+asset)
 while True:
  n=int.from_bytes(data[i:i+2],'little');i+=2
  if not n:out+=b'\0\0';break
  p=int.from_bytes(data[i:i+2],'little');i+=2
  raw=unfilter_case(unrle(data[i:i+p]));i+=p
  if len(raw)!=n:raise ValueError('case size')
  out+=struct.pack('<H',n)+raw
 if i!=len(data):raise ValueError('trailing data')
 return bytes(out)

def compress(data):
 out=bytearray();table={};anchor=0;i=0
 def extra(n):
  while n>=255:out.append(255);n-=255
  out.append(n)
 while i+4<=len(data):
  key=data[i:i+4];prev=table.get(key);table[key]=i
  if prev is None or i-prev>65535:i+=1;continue
  n=4
  while i+n<len(data) and data[prev+n]==data[i+n]:n+=1
  lit=i-anchor;out.append(min(lit,15)<<4|min(n-4,15))
  if lit>=15:extra(lit-15)
  out.extend(data[anchor:i]);out.extend(struct.pack('<H',i-prev))
  if n-4>=15:extra(n-19)
  for j in range(i+1,i+n):
   if j+4<=len(data):table[data[j:j+4]]=j
  i+=n;anchor=i
 # LZ4 permits a final literal-only sequence, including an empty one.
 lit=len(data)-anchor;out.append(min(lit,15)<<4)
 if lit>=15:extra(lit-15)
 out.extend(data[anchor:]);return bytes(out)

def decompress(data):
 out=bytearray();i=0
 def length(n):
  nonlocal i
  if n==15:
   while True:
    b=data[i];i+=1;n+=b
    if b!=255:break
  return n
 while i<len(data):
  token=data[i];i+=1;n=length(token>>4);out.extend(data[i:i+n]);i+=n
  if i==len(data):break
  offset=int.from_bytes(data[i:i+2],'little');i+=2
  if not offset or offset>len(out):raise ValueError('invalid offset')
  n=length(token&15)+4
  for _ in range(n):out.append(out[-offset])
 return bytes(out)

def pack_stream(data):
 # Preserve all decoded case bytes and asset bytes; SHA identity is unchanged.
 a=int.from_bytes(data[11:13],'little');asset=data[13:13+a];packed=compress(asset)
 out=data[:4]+data[4:11]+struct.pack('<HH',a,len(packed))+packed
 i=13+a
 while True:
  n=int.from_bytes(data[i:i+2],'little');i+=2
  if not n:out+=b'\0\0';break
  raw=data[i:i+n];i+=n;p=compress(raw);assert decompress(p)==raw
  out+=struct.pack('<HH',n,len(p))+p
 assert i==len(data)
 return b'B9Z1'+out[4:]
