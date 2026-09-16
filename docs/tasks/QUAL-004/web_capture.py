"""Single-client static EVF1 acquisition, no browser pacing/performance claims."""
import argparse,base64,hashlib,json,os,socket,struct,time
from pathlib import Path
from urllib.parse import urlparse

def exact(s,n):
 data=bytearray()
 while len(data)<n:
  chunk=s.recv(n-len(data))
  if not chunk:raise EOFError('websocket closed')
  data.extend(chunk)
 return bytes(data)
def send(s,data,opcode=1):
 mask=os.urandom(4);n=len(data);assert n<126
 s.sendall(bytes([128|opcode,128|n])+mask+bytes(b^mask[i%4] for i,b in enumerate(data)))
def receive(s):
 result=bytearray()
 while True:
  a,b=exact(s,2);n=b&127
  if n==126:n=struct.unpack('!H',exact(s,2))[0]
  elif n==127:n=struct.unpack('!Q',exact(s,8))[0]
  if n>3000000:raise ValueError('oversize frame')
  if b&128:raise ValueError('masked server')
  data=exact(s,n);op=a&15
  if op==9:send(s,data,10);continue
  if op==8:raise EOFError('server close')
  if op not in (0,2):continue
  result.extend(data)
  if a&128:return bytes(result)
def capture(url,out,count=3):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);u=urlparse(url)
 with socket.create_connection((u.hostname,u.port or 80),timeout=30) as s:
  key=base64.b64encode(os.urandom(16)).decode()
  s.sendall(f'GET /video HTTP/1.1\r\nHost: {u.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
  header=bytearray()
  while not header.endswith(b'\r\n\r\n'):header+=exact(s,1)
  assert b'101 Switching Protocols' in header,header
  accept=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
  assert accept in header
  for i in range(count):
   send(s,b'frame');raw=receive(s);(out/f'{i:02}.evf').write_bytes(raw);time.sleep(.2)
  send(s,struct.pack('!H',1000),8)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',required=True);a=p.parse_args();capture(a.url,a.output)
