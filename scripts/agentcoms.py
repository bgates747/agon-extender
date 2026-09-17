#!/usr/bin/env python3
"""Linux-hosted immutable agent mailbox. JSON stdin/stdout; SSH is the transport.
No model invocation, shell execution, hardware control or session-store access.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

DEFAULT = Path(__file__).resolve().parents[2] / 'agon-dev-env/cross-agent/agentcoms'
NAME = re.compile(r'[a-z][a-z0-9-]{0,63}\Z')

def name(value):
    if not isinstance(value, str) or not NAME.fullmatch(value):
        raise ValueError('Names must be lowercase letters/digits/hyphens, starting with a letter')
    return value

def atomic(path, data):
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
        d = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(d)
        finally: os.close(d)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

@contextmanager
def locked(root):
    root.mkdir(parents=True, exist_ok=True)
    (root / 'messages').mkdir(exist_ok=True)
    with (root / '.lock').open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield

def records(root):
    result = []
    for p in sorted((root / 'messages').glob('*.md')):
        pre, header, body = p.read_text().split('---\n', 2)
        if pre: raise ValueError('Malformed message: '+p.name)
        item = {}
        for line in header.splitlines():
            key, value = line.split(': ', 1)
            item[key] = json.loads(value)
        item['body'] = body.removeprefix('\n')
        result.append(item)
    return result

def send(root, req):
    allowed = {'author','recipient','request_id','thread_id','branch','in_reply_to','body'}
    if set(req)-allowed: raise ValueError('Unknown fields')
    for k in ('author','recipient','request_id','thread_id'):
        name(req[k])
    req = dict(req)
    req.setdefault('branch','main'); name(req['branch'])
    req.setdefault('in_reply_to',None)
    if not isinstance(req['body'],str) or not req['body'].strip():
        raise ValueError('Nonempty text body required')
    if len(req['body'].encode()) > 65536: raise ValueError('Body exceeds 64 KiB')
    fingerprint = hashlib.sha256(json.dumps(req,sort_keys=True).encode()).hexdigest()
    with locked(root):
        rows = records(root)
        for row in rows:
            if (row['author'],row['request_id']) == (req['author'],req['request_id']):
                if row['fingerprint'] != fingerprint: raise ValueError('Conflicting retry')
                return {'message_id':row['message_id'],'duplicate':True}
        if req['in_reply_to'] is not None:
            parents = [r for r in rows if r['message_id']==req['in_reply_to']]
            if not parents or parents[0]['thread_id']!=req['thread_id']:
                raise ValueError('Reply parent missing or thread mismatch')
        now = datetime.now(ZoneInfo('America/New_York'))
        mid = now.strftime('%Y-%m-%d_%H-%M-%S')+'_'+req['author']+'_'+req['request_id']
        item = dict(req, message_id=mid, created=now.isoformat(),status='published',fingerprint=fingerprint)
        body = item.pop('body')
        text = '---\n'+''.join(k+': '+json.dumps(v)+'\n' for k,v in item.items())+'---\n\n'+body
        path = root/'messages'/(mid+'.md')
        if path.exists(): raise ValueError('Message filename collision')
        atomic(path,text)
        return {'message_id':mid,'duplicate':False}

def read(root, recipient, include_acked=False):
    name(recipient)
    with locked(root):
        p=root/('ack-'+recipient+'.json')
        acks=json.loads(p.read_text()) if p.exists() else []
        return [r for r in records(root) if r['recipient']==recipient and
                (include_acked or r['message_id'] not in acks)]

def ack(root, recipient, ids):
    name(recipient)
    with locked(root):
        valid={r['message_id'] for r in records(root) if r['recipient']==recipient}
        if not set(ids)<=valid: raise ValueError('Unknown message or wrong recipient')
        p=root/('ack-'+recipient+'.json')
        old=set(json.loads(p.read_text())) if p.exists() else set()
        atomic(p,json.dumps(sorted(old|set(ids)))+'\n')
    return {'acknowledged':ids}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=DEFAULT)
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('send',help='Read one JSON request from stdin')
    for cmd in ('read','wait','ack'):
        q=sub.add_parser(cmd);q.add_argument('--recipient',required=True)
        if cmd=='read': q.add_argument('--all',action='store_true')
        if cmd=='wait': q.add_argument('--seconds',type=int,default=50,choices=range(1,61),metavar='1..60')
        if cmd=='ack': q.add_argument('ids',nargs='+')
    args=p.parse_args()
    if args.cmd=='send':
        data=sys.stdin.buffer.read(100001)
        if len(data)>100000: raise ValueError('Request too large')
        output=send(args.root,json.loads(data))
    elif args.cmd=='ack': output=ack(args.root,args.recipient,args.ids)
    else:
        deadline=time.monotonic()+(args.seconds if args.cmd=='wait' else 0)
        while True:
            output=read(args.root,args.recipient,getattr(args,'all',False))
            if output or time.monotonic()>=deadline: break
            time.sleep(min(1,max(0,deadline-time.monotonic())))
    print(json.dumps(output,ensure_ascii=False))

if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr);sys.exit(1)
