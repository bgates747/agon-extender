"""Finite Pi5 TCP peer for Smith's explicitly CRC-authorized NET-008 test.

The data connection is through the real ESP8266. This module has no P4 network,
serial, flash, reset, bench-state mutation or background service on import.
"""
import json,os,socket,struct,threading,time
from pathlib import Path
from modem_bw_protocol import PAYLOAD,UP,DOWN,frame,check,receive,pattern

class Peer:
 def __init__(self,bind,folder,nonce,baud,milliseconds):
  self.folder=Path(folder);self.folder.mkdir(exist_ok=False)
  self.nonce,self.baud,self.ms=nonce,baud,milliseconds
  self.stop=threading.Event();self.finished=threading.Event();self.close_request=threading.Event();self.lock=threading.Lock()
  self.result={'pass':False,'tx_frames':0,'rx_frames':0};self.conn=None
  self.listener=socket.socket();self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);self.listener.bind((bind,0));self.listener.listen(1);self.listener.settimeout(15)
  self.port=self.listener.getsockname()[1]
  self.thread=threading.Thread(target=self.work,name='net008-tcp-peer');self.thread.start()
 def event(self,kind,**fields):
  with self.lock:
   with (self.folder/'events.jsonl').open('a') as f:f.write(json.dumps(dict(event=kind,epoch=time.time(),**fields))+'\n');f.flush()
 def sender(self):
  seq=1;start=time.monotonic();failure=None
  try:
   while not self.stop.is_set() and time.monotonic()-start<self.ms/1000:
    self.conn.sendall(frame(seq,pattern(seq,DOWN)));self.result['tx_frames']=seq;seq+=1
   self.conn.sendall(frame(seq))
  except Exception as e:failure=repr(e);self.stop.set()
  self.result.update(tx_elapsed_seconds=time.monotonic()-start,tx_error=failure,tx_bytes=self.result['tx_frames']*PAYLOAD)
 def work(self):
  sender=None;rx_start=None;rx_last=None;raw=None;failure=None;seq=1
  try:
   self.conn,address=self.listener.accept();self.conn.settimeout(self.ms/1000+20);self.conn.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);self.conn.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,16384)
   hello=receive(self.conn);_,body=check(hello,seq=0)
   if body!=struct.pack('<4I',self.nonce,self.baud,self.ms,PAYLOAD):raise ValueError('Wrong actual P4 hello/configuration')
   self.event('hello',baud=self.baud,milliseconds=self.ms,nonce=self.nonce);self.conn.sendall(frame(0,b'GO'))
   sender=threading.Thread(target=self.sender,name='net008-tcp-tx');sender.start();raw=(self.folder/'received.bin').open('xb');last=time.monotonic()
   while not self.stop.is_set():
    data=receive(self.conn);raw.write(data)
    _,payload=check(data,seq=seq,salt=UP);seq+=1
    if not payload:break
    now=time.monotonic();rx_start=now if rx_start is None else rx_start;rx_last=now;self.result['rx_frames']+=1
    if now-last>=1:
     self.event('progress',elapsed=now-rx_start,tx_frames=self.result['tx_frames'],rx_frames=self.result['rx_frames']);raw.flush();os.fsync(raw.fileno());last=now
   if self.stop.is_set():raise RuntimeError('Peer producer/receiver failure')
  except Exception as e:failure=repr(e);self.stop.set();self.event('failure',error=failure)
  finally:
   if raw:raw.flush();os.fsync(raw.fileno());raw.close()
   if failure and self.conn:
    try:self.conn.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   if sender:
    sender.join(timeout=self.ms/1000+5)
    if sender.is_alive():
     self.stop.set()
     try:self.conn.shutdown(socket.SHUT_RDWR)
     except OSError:pass
     sender.join(timeout=3)
     if sender.is_alive():failure='Sender thread did not join'
   self.result.update(rx_elapsed_seconds=0 if rx_start is None else rx_last-rx_start,rx_bytes=self.result['rx_frames']*PAYLOAD,error=failure)
   self.result['pass']=failure is None and self.result.get('tx_error') is None and self.result['rx_frames']>0
   (self.folder/'result.json').write_text(json.dumps(self.result,indent=2)+'\n');self.finished.set()
   # Keep TCP up until the P4 has completed its guarded escape/close. The
   # operator closes this peer afterward; no guessed app completion or reset.
   self.close_request.wait(timeout=15)
   if self.conn:self.conn.close()
   self.listener.close()
 def close(self):
  self.stop.set();self.close_request.set()
  if not self.finished.is_set():
   if self.conn:
    try:self.conn.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   try:self.listener.shutdown(socket.SHUT_RDWR)
   except OSError:pass
   self.listener.close()
  self.thread.join(timeout=20)
  if self.thread.is_alive():raise RuntimeError('TCP peer did not join')
