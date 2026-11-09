"""NET-008 P4/Pi5 test-only wire codec; CRC is directly authorized by Smith."""
import struct,zlib
HEADER=struct.Struct('<4sIII')
PAYLOAD=1024
UP=0x13579bdf
DOWN=0x2468ace0

def pattern(seq,salt,n=PAYLOAD):
 x=((seq*0x9e3779b9)&0xffffffff)^salt;out=bytearray()
 for _ in range(n):
  x^=(x<<13)&0xffffffff;x^=x>>17;x^=(x<<5)&0xffffffff
  b=x>>24;out.append(0x2c if b==0x2b else b)
 return bytes(out)

def frame(seq,data=b''):
 if len(data)>PAYLOAD:raise ValueError('Oversized frame')
 h=struct.pack('<4sII',b'N8BW',seq,len(data));return h+struct.pack('<I',zlib.crc32(data,zlib.crc32(h)))+data

def check(raw,seq=None,salt=None):
 if len(raw)<HEADER.size:raise ValueError('Truncated header')
 magic,actual,n,crc=HEADER.unpack_from(raw)
 if magic!=b'N8BW' or n>PAYLOAD or len(raw)!=16+n:raise ValueError('Framing/length error')
 if seq is not None and actual!=seq:raise ValueError('Sequence error')
 if zlib.crc32(raw[16:],zlib.crc32(raw[:12]))!=crc:raise ValueError('CRC mismatch')
 if salt is not None and n and raw[16:]!=pattern(actual,salt,n):raise ValueError('Payload pattern mismatch')
 return actual,raw[16:]

def receive(sock):
 def exact(n):
  out=bytearray()
  while len(out)<n:
   b=sock.recv(n-len(out))
   if not b:raise EOFError('TCP closed/truncated frame')
   out+=b
  return bytes(out)
 h=exact(16);magic,seq,n,crc=HEADER.unpack(h)
 if magic!=b'N8BW' or n>PAYLOAD:raise ValueError('Invalid frame header')
 return h+exact(n)
