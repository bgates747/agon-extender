#!/usr/bin/env python3
"""Explicit host typing through the Extender's admitted native keyboard source.

State journals retain the exact request across lost HTTP replies. Recovery only
replays that request; it never restarts a command or a session after a reboot.
An emitted event reached the console owner, not necessarily MOS or its caller.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import secrets
import struct
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zlib

KEYS = {'enter':40, 'escape':41, 'backspace':42, 'tab':43, 'space':44,
        'insert':73, 'home':74, 'pageup':75, 'delete':76, 'end':77,
        'pagedown':78, 'right':79, 'left':80, 'down':81, 'up':82,
        'ctrl':224, 'shift':225, 'alt':226, 'gui':227, 'altgr':230}
KEYS.update({f'f{i+1}':58+i for i in range(12)})

def text_events(text, locale, caps=False):
    """Validate the entire string before returning any events. UK=0, US=1."""
    if locale not in (0, 1): raise ValueError('Only UK and US layouts are supported')
    plain = dict(zip('1234567890', range(30,40)))
    plain.update(dict(zip('-=[];\',./', (45,46,47,48,51,52,54,55,56))))
    plain.update({' ':44, '\n':40, '\r':40, '\t':43, '`':53})
    shifted = dict(zip('!@#$%^&*()', range(30,40)))
    shifted.update(dict(zip('_+{}:"<>?', (45,46,47,48,51,52,54,55,56))))
    if locale == 1:
        plain['\\']=49; shifted.update({'|':49, '~':53})
    else:
        plain.update({'#':50, '\\':100})
        shifted.pop('#'); shifted.update({'"':31, '£':32, '@':52, '~':50, '|':100})
        # UK Shift+grave is not the US tilde. Unsupported symbols stay rejected.
    result=[]
    for c in text:
        if c.isascii() and c.isalpha(): usage=4+ord(c.lower())-97; shift=c.isupper()!=caps
        elif c in plain: usage=plain[c]; shift=False
        elif c in shifted: usage=shifted[c]; shift=True
        else: raise ValueError(f'Unsupported character {c!r}; no text submitted')
        if shift: result.append((225,1))
        result.extend(((usage,1),(usage,0)))
        if shift: result.append((225,0))
    return result

def key_usage(name):
    name=name.lower()
    if name in KEYS:return KEYS[name]
    if len(name)==1 and 'a'<=name<='z':return ord(name)-97+4
    if len(name)==1 and name in '1234567890':return 30+'1234567890'.index(name)
    raise ValueError('Unknown key: '+name)

def packet(op, boot, session, sequence, events=()):
    body=bytes(v for pair in events for v in pair)
    if len(body)>192:raise ValueError('Maximum 96 key transitions per request')
    result=bytearray(struct.pack('<2sBBIIIHHI',b'KY',1,op,boot,session,sequence,len(body),0,0)+body)
    struct.pack_into('<I',result,20,zlib.crc32(result))
    return bytes(result)

class KeyboardError(RuntimeError):pass

class Client:
    def __init__(self,url,state):
        self.url=url.rstrip('/');self.path=Path(state)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.lock=self.path.with_suffix(self.path.suffix+'.lock').open('a')
        fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        self.state=json.loads(self.path.read_text()) if self.path.exists() else {}
        if self.state and self.state.get('url')!=self.url:raise KeyboardError('Journal belongs to another endpoint')

    def save(self):
        temp=self.path.with_suffix(self.path.suffix+'.tmp')
        with temp.open('w') as stream:
            stream.write(json.dumps(self.state,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        temp.replace(self.path)

    def http(self,path,data=None):
        request=Request(self.url+path,data=data,headers={'X-Agon-Keyboard':'1','Content-Type':'application/octet-stream'})
        try:
            with urlopen(request,timeout=1) as response:return json.load(response)
        except HTTPError as error:
            with error:detail=error.read().decode(errors='replace')
            raise KeyboardError(f'HTTP {error.code}: {detail}') from error

    def status(self):return self.http('/keyboard/status')

    def recover(self):
        pending=self.state.get('pending')
        if not pending:raise KeyboardError('No uncertain request to recover')
        data=bytes.fromhex(pending);deadline=time.monotonic()+3
        while True:
            try:reply=self.http('/keyboard/rpc',data);break
            except (URLError,TimeoutError,OSError):
                if time.monotonic()>=deadline:raise KeyboardError('Reply uncertain; retain journal and use recover, not retyping')
                time.sleep(.05)
        if (reply['boot'],reply['session'],reply['sequence']) != struct.unpack_from('<III',data,4):
            raise KeyboardError('Session changed; command was not restarted')
        self.state['sequence']=reply['sequence'];self.state['pending']=None;self.save()
        if data[3]!=3 and reply['reason']:raise KeyboardError(f'Automation stopped: reason {reply["reason"]}')
        return reply

    def request(self,op,events=()):
        if self.state.get('pending'):raise KeyboardError('Uncertain request exists; recover it first')
        s=self.state;data=packet(op,s['boot'],s['session'],s['sequence']+1,events)
        self.state['pending']=data.hex();self.save();return self.recover()

    def open(self,observed=None):
        if self.state.get('pending') or self.state.get('active'):raise KeyboardError('Existing session: cancel/recover it explicitly')
        observed=observed or self.status()
        if not observed['ready'] or not observed['physical_neutral']:raise KeyboardError('Keyboard is not admitted and neutral')
        self.state={'url':self.url,'boot':observed['boot'],'session':secrets.randbelow(0xffffffff)+1,
                    'sequence':0,'active':True,'pending':None}
        self.save();return self.request(1)

    def wait(self,held=None):
        deadline=time.monotonic()+8;beat=time.monotonic()+2
        while True:
            s=self.status()
            if (s['boot'],s['session'])!=(self.state['boot'],self.state['session']) or s['reason']:
                raise KeyboardError('Keyboard session ended: '+json.dumps(s))
            if s['pending']==0 and (held is None or s['held']==held):return s
            if time.monotonic()>deadline:raise KeyboardError('Event drain deadline exceeded')
            if time.monotonic()>beat:self.request(4);beat=time.monotonic()+2
            time.sleep(.03)

    def send(self,events):
        for offset in range(0,len(events),96):
            self.request(2,events[offset:offset+96]);self.wait()
        return self.wait()

    def cancel(self):
        result=self.request(3)
        deadline=time.monotonic()+3
        while result['held']:
            if time.monotonic()>deadline:raise KeyboardError('Release not confirmed; retain journal')
            time.sleep(.03);result=self.status()
            if (result['boot'],result['session'])!=(self.state['boot'],self.state['session']):
                raise KeyboardError('Admission changed during release')
        self.state['active']=False;self.save();return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True);p.add_argument('--state',type=Path,required=True)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('status','recover','cancel'):sub.add_parser(name)
    t=sub.add_parser('type');t.add_argument('text');t.add_argument('--enter',action='store_true')
    k=sub.add_parser('key');k.add_argument('keys',nargs='+')
    h=sub.add_parser('hold');h.add_argument('key');h.add_argument('--seconds',type=float,default=1)
    a=p.parse_args();c=Client(a.url,a.state)
    try:
        if a.command in ('status','recover','cancel'):result=getattr(c,a.command)()
        else:
            observed=c.status()
            if a.command=='type':events=text_events(a.text+('\n' if a.enter else ''),observed['locale'],observed['caps'])
            elif a.command=='key':events=[pair for name in a.keys for pair in ((key_usage(name),1),(key_usage(name),0))]
            else:
                if not 0<=a.seconds<=60:raise ValueError('Hold must be 0–60 seconds')
                events=[(key_usage(a.key),1)]
            c.open(observed)
            try:
                result=c.send(events)
                if a.command=='hold':
                    until=time.monotonic()+a.seconds
                    while time.monotonic()<until:time.sleep(max(0,min(1,until-time.monotonic())));c.request(4)
            finally:
                # An uncertain POST must be resolved explicitly; the firmware
                # timeout will release keys even if this process disappears.
                if not c.state.get('pending'):c.cancel()
        print(json.dumps(result,indent=2))
    finally:c.lock.close()

if __name__=='__main__':main()
