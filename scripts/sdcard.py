#!/usr/bin/env python3
"""Mainboard SD client through the explicitly running Extender SD service.

No device reset, firmware flash, shell command, or automatic game execution.
Keep --state between invocations so an uncertain request can be retried exactly.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import struct
import sys
import time
import urllib.error
import urllib.request
import zlib

HEADER=struct.Struct('<2sBBIIBBH')
NAMES=('ok','bad request','unsupported','busy','stale session','sequence conflict',
       'filesystem error','integrity failure','recovery required')

class RemoteError(RuntimeError):
    def __init__(self,message,*,status=None,detail=b''):
        super().__init__(message);self.status=status;self.detail=detail

def path_payload(path):
    try: data=path.encode('ascii')
    except UnicodeEncodeError as e: raise ValueError('Paths must be ASCII') from e
    if not 1<=len(data)<=120 or not path.startswith('/') or b'\0' in data:
        raise ValueError('Path must be absolute, 1..120 bytes, without NUL')
    return bytes([len(data)])+data

def record(session,seq,op,payload=b''):
    if len(payload)>220: raise ValueError('Payload too large')
    h=HEADER.pack(b'SD',1,1,session,seq,op,0,len(payload))
    return h+struct.pack('<I',zlib.crc32(h+payload))+payload

def response(data,request):
    if not 20<=len(data)<=240: raise RemoteError('Invalid response length')
    magic,version,kind,sid,seq,op,status,n=HEADER.unpack(data[:16])
    if (magic,version,kind)!=(b'SD',1,2) or n!=len(data)-20 or data[4:13]!=request[4:13]:
        raise RemoteError('Response identity/length mismatch')
    if struct.unpack_from('<I',data,16)[0]!=zlib.crc32(data[:16]+data[20:]):
        raise RemoteError('Response CRC mismatch')
    return status,data[20:]

class Client:
    def __init__(self,url,state,timeout=60):
        self.url=url.rstrip('/');self.state_path=Path(state);self.timeout=timeout
        if not self.url.startswith('http://'): raise ValueError('Use the local http:// Extender endpoint')
        self.state_path.parent.mkdir(parents=True,exist_ok=True)
        self.lock=self.state_path.with_name(self.state_path.name+'.lock').open('a')
        try:fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as e:
            self.lock.close();raise RemoteError('Another client owns this state file') from e
        self.state=json.loads(self.state_path.read_text()) if self.state_path.exists() else {
            'url':self.url,'session':secrets.randbelow(0xffffffff)+1,'sequence':0,'boot':None,'pending':None}
        if self.state['url']!=self.url: raise ValueError('State belongs to another endpoint')
    def save(self):
        self.state_path.parent.mkdir(parents=True,exist_ok=True)
        temp=self.state_path.with_name(self.state_path.name+'.tmp')
        with temp.open('w') as f:
            json.dump(self.state,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        temp.replace(self.state_path)
    def status(self):
        with urllib.request.urlopen(self.url+'/sd/status',timeout=3) as r:
            return json.load(r)
    def exchange(self,request):
        deadline=time.monotonic()+self.timeout;last='pending'
        while time.monotonic()<deadline:
            req=urllib.request.Request(self.url+'/sd/rpc',data=request,
                                      headers={'Content-Type':'application/octet-stream'})
            try:
                with urllib.request.urlopen(req,timeout=min(3,max(.1,deadline-time.monotonic()))) as r:
                    code=r.status;data=r.read(241)
            except urllib.error.HTTPError as e:
                code=e.code;data=e.read(241)
            except (OSError,urllib.error.URLError) as e:
                last=str(e);time.sleep(.1);continue
            if code==200:return response(data,request)
            if code not in (202,503):raise RemoteError(f'HTTP {code}; request retained for explicit recovery')
            last=f'HTTP {code}';time.sleep(.04)
        raise TimeoutError(f'Uncertain completion ({last}); keep state and use resume. No offset advanced locally.')
    def resolve(self):
        if not self.state['pending']:raise RemoteError('No uncertain request to resume')
        request=bytes.fromhex(self.state['pending']);status,data=self.exchange(request)
        # Protocol-level sequence failures do not advance the remote sequence.
        # Keep the request for explicit investigation instead of guessing.
        if status in (4,5) or (status==3 and request[12]==1):
            raise RemoteError(NAMES[status]+'; retained pending request')
        if status==0 and request[12]==1:
            if len(data)!=8:raise RemoteError('Malformed HELLO response')
            self.state['boot']=struct.unpack_from('<I',data)[0]
        self.state['sequence']=struct.unpack_from('<I',request,8)[0]
        self.state['pending']=None;self.save()
        if status:raise RemoteError(f'{NAMES[status] if status<len(NAMES) else status}; detail={data.hex()}',status=status,detail=data)
        return data
    def rpc(self,op,payload=b''):
        if self.state['pending']:raise RemoteError('Uncertain earlier request; use resume before another command')
        if self.state['sequence']==0xffffffff:raise RemoteError('Session exhausted; restart service and use a fresh state')
        self.state['pending']=record(self.state['session'],self.state['sequence']+1,op,payload).hex()
        self.save();return self.resolve()
    def connect(self):
        current=self.status()
        if current.get('protocol')!=1:raise RemoteError('Unsupported protocol')
        if self.state['boot'] is not None and current['boot']!=self.state['boot']:
            raise RemoteError('Service restarted; preserve this state, use a new state file, and inspect stage recovery')
        if not current['online']:raise RemoteError('Run sdserve on the Agon first')
        if not self.state['sequence']:
            data=self.rpc(1);boot,chunk,features=struct.unpack('<IHH',data)
            if chunk!=212 or features&15!=15:raise RemoteError('Missing required capabilities')
            self.state['boot']=boot;self.save()
    def download(self,path):
        result=bytearray();offset=0;total=None
        while total is None or offset<total:
            p=self.rpc(4,struct.pack('<IH',offset,216)+path_payload(path))
            if len(p)<4:raise RemoteError('Truncated READ reply')
            size=struct.unpack_from('<I',p)[0]
            if total is not None and size!=total:raise RemoteError('File size changed during download')
            total=size;chunk=p[4:]
            if len(chunk)!=min(216,total-offset):raise RemoteError('Unexpected READ count')
            result.extend(chunk);offset+=len(chunk)
        return bytes(result)
    def directory_capability(self):
        hello=self.rpc(1)
        if len(hello)!=8 or not struct.unpack_from('<H',hello,6)[0]&32:
            raise RemoteError('Directory operations require the development listener capability 0x20')
    @staticmethod
    def operation_path(path):
        path_payload(path)
        if path!='/' and (path.endswith('/') or any(x in ('','.','..') or x.endswith(('.', ' ')) for x in path[1:].split('/'))):
            raise ValueError('Use a normalized absolute path')
        if any(ord(c)<32 or c in ':\\*?"<>|' for c in path):raise ValueError('Invalid path character')
        return path
    def stat_entry(self,path):
        data=self.rpc(2,path_payload(self.operation_path(path)))
        if len(data)!=5:raise RemoteError('Malformed STAT response')
        size,attributes=struct.unpack('<IB',data);return size,attributes
    def entries(self,path):
        self.operation_path(path);cursor=0
        while True:
            data=self.rpc(3,struct.pack('<I',cursor)+path_payload(path))
            if len(data)<5 or data[4] not in (0,1):raise RemoteError('Malformed LIST response')
            next_cursor=struct.unpack_from('<I',data)[0]
            if data[4]:
                if len(data)!=5 or next_cursor!=cursor:raise RemoteError('Malformed LIST end')
                return
            if len(data)<11 or len(data)!=11+data[10] or next_cursor!=cursor+1:
                raise RemoteError('Malformed LIST entry')
            name=data[11:].decode('ascii')
            if not name or '/' in name or name in ('.','..'):raise RemoteError('Unsafe directory entry')
            child=self.operation_path(path.rstrip('/')+'/'+name)
            yield child,struct.unpack_from('<I',data,6)[0],data[5]
            cursor=next_cursor
    def make_directory(self,path,*,parents=False,report=lambda *args:None):
        self.directory_capability();self.operation_path(path)
        paths=['/'+ '/'.join(path[1:].split('/')[:i]) for i in range(1,len(path[1:].split('/'))+1)] if parents else [path]
        for item in paths:
            if parents:
                try:
                    _,attr=self.stat_entry(item)
                except RemoteError as e:
                    if e.status!=6 or e.detail not in (b'\x04',b'\x05'):raise
                else:
                    if not attr&16:raise RemoteError('Parent is not a directory: '+item)
                    continue
            self.rpc(12,path_payload(item));report('mkdir',item)
    def move(self,source,destination):
        self.directory_capability();self.operation_path(source);self.operation_path(destination)
        a=source.encode('ascii');b=destination.encode('ascii')
        descriptor=struct.pack('<BBHHH',6,0,len(a),len(b),0)+a+b
        for offset in range(0,len(descriptor),184):
            piece=descriptor[offset:offset+184];end=offset+len(piece)
            reply=self.rpc(14,struct.pack('<HHI',len(descriptor),offset,zlib.crc32(descriptor))+piece)
            if reply!=struct.pack('<HB',end,int(end==len(descriptor))):raise RemoteError('Unexpected MOVE acknowledgement; inspect both paths')
    def remove(self,path,*,recursive=False,report=lambda *args:None):
        self.directory_capability();self.operation_path(path)
        def walk(current,depth):
            if depth>16:raise ValueError('Directory depth limit (16) exceeded')
            # Ask the engine to enforce its export-root/journal/utility guards
            # BEFORE deleting descendants, not merely at the final rmdir.
            self.rpc(13,b'\x01'+path_payload(current))
            _,attr=self.stat_entry(current)
            if attr&16 and recursive:
                # Restart enumeration after mutation: FAT cursors may move.
                while True:
                    child=next(self.entries(current),None)
                    if child is None:break
                    walk(child[0],depth+1)
            self.rpc(13,b'\x00'+path_payload(current));report('remove',current)
        walk(path,0)
    def copy(self,source,destination,*,recursive=False,replace=False,fast=False,report=lambda *args:None):
        self.directory_capability();self.operation_path(source);self.operation_path(destination)
        a,b=source.lower(),destination.lower()
        if a==b or b.startswith(a.rstrip('/')+'/') or a.startswith(b.rstrip('/')+'/'):
            raise ValueError('Source and destination trees must not overlap')
        def walk(src,dst,depth):
            if depth>16:raise ValueError('Directory depth limit (16) exceeded')
            self.operation_path(dst);_,attr=self.stat_entry(src)
            try:_,target_attr=self.stat_entry(dst);exists=True
            except RemoteError as e:
                if e.status!=6 or e.detail not in (b'\x04',b'\x05'):raise
                exists=False;target_attr=0
            if attr&16:
                if not recursive:raise ValueError('Directory copy requires --recursive')
                if exists:raise RemoteError('Directory merge/replacement is unsupported: '+dst)
                self.rpc(12,path_payload(dst));report('mkdir',dst)
                for child,_,_ in self.entries(src):walk(child,dst+'/'+child.rsplit('/',1)[1],depth+1)
            else:
                if exists and (not replace or target_attr&16):raise RemoteError('Destination exists: '+dst)
                # Host CLI only: same whole-file host-memory behavior as get/put.
                # The P4 native adapter must use its bounded SD spool instead.
                self.upload(dst,self.download(src),True,fast=fast);report('copy',dst)
        walk(source,destination,0)

    def upload(self,path,data,activate=False,*,fast=False):
        encoded=path_payload(path)
        if len(encoded)>113:raise ValueError('Staged target must be at most 112 bytes to allow sibling readback')
        # Re-query mode even for a resumed client state. No BEGIN or file
        # mutation occurs when the requested verification mode mismatches.
        hello=self.rpc(1)
        if len(hello)!=8:raise RemoteError('Malformed HELLO response')
        boot,chunk,features=struct.unpack('<IHH',hello)
        if chunk!=212 or features&15!=15:raise RemoteError('Missing required capabilities')
        if bool(features&16)!=bool(fast):
            raise RemoteError('Upload mode mismatch: use put --fast with sdserve --fast, or normal mode on both')
        tid=secrets.randbelow(0xffffffff)+1;crc=zlib.crc32(data)
        got=self.rpc(5,struct.pack('<III',tid,len(data),crc)+encoded)
        if got!=struct.pack('<II',tid,0):raise RemoteError('Unexpected BEGIN acknowledgement')
        print(f'Transfer {tid}, {len(data)} bytes; '+
              ('fast mode, no whole-file readback' if fast else 'stage only until verified activation'),flush=True)
        for offset in range(0,len(data),212):
            chunk=data[offset:offset+212]
            got=self.rpc(6,struct.pack('<II',tid,offset)+chunk)
            if got!=struct.pack('<II',tid,offset+len(chunk)):raise RemoteError('Unexpected WRITE acknowledgement')
        if self.rpc(7,struct.pack('<I',tid))!=struct.pack('<II',len(data),crc):
            raise RemoteError('Unexpected FINISH identity')
        if not fast:
            stage=self.download(path+'.p17part')
            if stage!=data:raise RemoteError('Independent host stage readback differs')
            print(f'Verified stage SHA256 {hashlib.sha256(data).hexdigest()}',flush=True)
        if activate:
            self.rpc(8,struct.pack('<I',tid))
            if not fast:
                if self.download(path)!=data:raise RemoteError('Activated file readback differs; backup retained')
            print(('Activated without whole-file verification' if fast else 'Activated and read back')+
                  '; previous target retained as .p17bak',flush=True)
        else:print(f'Use activate {tid} or cancel {tid} with this state file',flush=True)
        return tid

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True);p.add_argument('--state',required=True,type=Path)
    p.add_argument('--timeout',type=float,default=60)
    commands=p.add_subparsers(dest='command',required=True)
    for name in ('status','resume','exit'):commands.add_parser(name)
    for name in ('stat','list'):commands.add_parser(name).add_argument('path')
    mkdir=commands.add_parser('mkdir');mkdir.add_argument('path');mkdir.add_argument('--parents',action='store_true')
    remove=commands.add_parser('remove');remove.add_argument('path');remove.add_argument('--recursive',action='store_true')
    move=commands.add_parser('move');move.add_argument('source');move.add_argument('destination')
    copy=commands.add_parser('copy');copy.add_argument('source');copy.add_argument('destination');copy.add_argument('--recursive',action='store_true');copy.add_argument('--replace',action='store_true');copy.add_argument('--fast',action='store_true')
    get=commands.add_parser('get');get.add_argument('path');get.add_argument('output',type=Path)
    put=commands.add_parser('put');put.add_argument('input',type=Path);put.add_argument('path');put.add_argument('--activate',action='store_true');put.add_argument('--fast',action='store_true',help='Skip whole-file readbacks; requires sdserve --fast')
    for name in ('activate','cancel'):commands.add_parser(name).add_argument('transfer',type=int)
    recover=commands.add_parser('recover');recover.add_argument('path')
    recover.add_argument('action',choices=('inspect','restore','abandon','cleanup'),default='inspect',nargs='?')
    a=p.parse_args();client=Client(a.url,a.state,a.timeout)
    if a.command=='status':print(json.dumps(client.status(),indent=2));return
    if a.command=='resume':print('Recovered response:',client.resolve().hex());return
    client.connect()
    report=lambda operation,path:print(json.dumps({'completed':operation,'path':path}),flush=True)
    if a.command=='mkdir':client.make_directory(a.path,parents=a.parents,report=report)
    elif a.command=='remove':client.remove(a.path,recursive=a.recursive,report=report)
    elif a.command=='move':client.move(a.source,a.destination);report('move',a.destination)
    elif a.command=='copy':client.copy(a.source,a.destination,recursive=a.recursive,replace=a.replace,fast=a.fast,report=report)
    elif a.command=='stat':
        print(dict(zip(('size','attributes'),struct.unpack('<IB',client.rpc(2,path_payload(a.path))))))
    elif a.command=='list':
        cursor=0
        while True:
            data=client.rpc(3,struct.pack('<I',cursor)+path_payload(a.path))
            cursor=struct.unpack_from('<I',data)[0]
            if data[4]:break
            print(f'{struct.unpack_from("<I",data,6)[0]:10} {data[11:].decode("ascii")}')
    elif a.command=='get':
        data=client.download(a.path)
        with a.output.open('xb') as f:f.write(data)
        print(f'{len(data)} bytes, SHA256 {hashlib.sha256(data).hexdigest()}')
    elif a.command=='put':client.upload(a.path,a.input.read_bytes(),a.activate,fast=a.fast)
    elif a.command in ('activate','cancel'):client.rpc(8 if a.command=='activate' else 9,struct.pack('<I',a.transfer))
    elif a.command=='exit':client.rpc(11)
    else:
        action=('inspect','restore','abandon','cleanup').index(a.action)
        print('Recovery state:',client.rpc(10,bytes([action])+path_payload(a.path)).hex())

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RemoteError) as error:
        print(f'SD service: {error}',file=sys.stderr);raise SystemExit(1)
