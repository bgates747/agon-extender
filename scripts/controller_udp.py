#!/usr/bin/env python3
"""Candidate Oryx -> P4 UDP controller sender. No eZ80 delivery or firmware install.

120 Hz default; 250 ms health timeout. Runs only when explicitly invoked.
Stops on unplug, SYN_DROPPED, queue overflow, missing ACKs or session loss.
"""
from __future__ import annotations
import argparse
from collections import deque
import json
import math
import secrets
import socket
import struct
import time
import urllib.request
from urllib.parse import urlsplit

from controller_input import Observer, STICKS, TRIGGERS, BUTTONS

HEADER = struct.Struct('<4sBBHQQII')
BASE = struct.Struct('<HHBB')
EDGE = struct.Struct('<IBBH')
OPEN = struct.Struct('<QQHHI')
MAX_EDGES, CAPACITY, MAX_PACKET = 16, 128, 176
DEFAULT_HZ = 120
STATE, ACK, FAULT = 1, 2, 3
RAW8, NATIVE = 1, 2
KEY_INDEX = {code: i for i, code in enumerate(BUTTONS)}


class InputFault(RuntimeError):
    pass


def held_mask(state):
    result = sum(1 << KEY_INDEX[k] for k in state.pressed)
    for code, minus, plus in ((16,11,12),(17,13,14)):
        value = state.values[code]
        if value:
            result |= 1 << (plus if value > 0 else minus)
    return result


def encode(instance, session, sequence, state, edges=(), age_ms=0):
    if not (0 < instance < 2**64 and 0 < session < 2**64 and 0 < sequence < 2**32):
        raise ValueError('Invalid epoch/session/sequence')
    if len(edges) > MAX_EDGES or not 0 <= age_ms <= 50:
        raise ValueError('Packet count or publication age out of range')
    sticks = [state.values[k] for k in STICKS]
    triggers = [state.values[k] for k in TRIGGERS]
    if all(-32768 <= v <= 32767 and (v+32768) % 257 == 0 for v in sticks):
        profile = RAW8
        analog = bytes([(v+32768)//257 for v in sticks] + triggers)
    else:
        profile = NATIVE
        analog = struct.pack('<4h2B', *sticks, *triggers)
    payload = bytearray(BASE.pack(held_mask(state), age_ms, profile, len(edges)) + analog)
    previous = None
    for seq, control, down in edges:
        if not 0 < seq < 2**32 or not 0 <= control < 15 or down not in (0,1):
            raise ValueError('Invalid transition')
        if previous is not None and seq != previous+1:
            raise ValueError('Non-contiguous transitions')
        payload.extend(EDGE.pack(seq, control, down, 0)); previous = seq
    return HEADER.pack(b'AGCP',1,STATE,HEADER.size+len(payload),instance,session,sequence,0)+payload


def decode_ack(data, instance, session):
    if len(data) != 40:
        raise InputFault('Wrong ACK length')
    magic,version,kind,length,epoch,token,seq,reserved = HEADER.unpack_from(data)
    packet,edge = struct.unpack_from('<II',data,32)
    if (magic,version,length,epoch,token,reserved)!=(b'AGCP',1,40,instance,session,0) or packet!=seq or not seq:
        raise InputFault('Wrong ACK identity or framing')
    if kind == FAULT:
        raise InputFault('Receiver invalidated input: reason '+str(edge))
    if kind != ACK:
        raise InputFault('Unexpected controller reply')
    return packet,edge


class Transitions:
    def __init__(self, state):
        self.pending = deque()
        self.next_sequence = 1
        self.hat = held_mask(state) & 0x7800
        self.highest_sent = 0
        self.acknowledged = 0

    def push(self, index, down):
        if len(self.pending) >= CAPACITY or self.next_sequence >= 2**32:
            raise InputFault('Transition queue/sequence exhausted; start a new session')
        self.pending.append((self.next_sequence,index,int(down)))
        self.next_sequence += 1

    def report(self, state):
        # Observer callback runs for every report, even between UI/sender ticks.
        for key, down in state.last_edges:
            self.push(KEY_INDEX[key],down)
        hat = held_mask(state) & 0x7800
        for bit in range(11,15):
            if self.hat & (1<<bit) and not hat & (1<<bit):self.push(bit,False)
        for bit in range(11,15):
            if hat & (1<<bit) and not self.hat & (1<<bit):self.push(bit,True)
        self.hat = hat

    def batch(self):
        result = list(self.pending)[:MAX_EDGES]
        if result:self.highest_sent = max(self.highest_sent,result[-1][0])
        return result

    def ack(self, sequence):
        if sequence > self.highest_sent:
            raise InputFault('ACK claims transitions not sent')
        self.acknowledged = max(self.acknowledged,sequence)
        while self.pending and self.pending[0][0] <= sequence:self.pending.popleft()


def control(base, path, data=None):
    request = urllib.request.Request(base+path, data=data,
                                    headers={'X-Agon-Controller':'1','Content-Type':'application/octet-stream'})
    with urllib.request.urlopen(request, timeout=1.0) as response:
        raw = response.read(4097)
        if len(raw)>4096:raise InputFault('Oversized controller response')
        return json.loads(raw)


def endpoint(url):
    parts=urlsplit(url)
    if parts.scheme!='http' or not parts.hostname or parts.username or parts.password or parts.path not in ('','/') or parts.query or parts.fragment:
        raise ValueError('--url must be an HTTP origin without credentials/path/query')
    address=socket.gethostbyname(parts.hostname)
    return f'http://{address}:{parts.port or 80}',address


def run(url, *, device=None, hz=DEFAULT_HZ, timeout_ms=250, seconds=None, record=None):
    if not math.isfinite(hz) or not 1<=hz<=240 or not 50<=timeout_ms<=2000:
        raise ValueError('Rate must be 1..240 Hz; timeout 50..2000 ms')
    if hz * timeout_ms < 2000:
        raise ValueError('Timeout must allow at least two publication periods')
    if seconds is not None and (not math.isfinite(seconds) or seconds<=0):
        raise ValueError('Duration must be finite and positive')
    base,address=endpoint(url)
    observer=Observer(device)
    udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    session=None;instance=None;queue=None;sent=acks=0;last_ack_packet=0
    started=time.monotonic();failure=None
    try:
        if record:observer.start_recording(record)
        observer.poll()
        if not observer.device:raise InputFault(observer.message)
        source_session=observer.session
        queue=Transitions(observer.state)
        observer.on_frame=queue.report
        def gap():raise InputFault('Linux input overflow: transition history is unknown')
        observer.on_gap=gap
        info=control(base,'/controller/status')
        instance=int(info['instance'],16)
        udp.bind(('0.0.0.0',0))
        udp.connect((address,info['udp_port']))
        udp.setblocking(False)
        body=OPEN.pack(instance,secrets.randbits(64) or 1,udp.getsockname()[1],timeout_ms,0)
        opened=control(base,'/controller/open',body)
        session=int(opened['session'],16)
        last_ack=next_send=time.monotonic()
        end=started+seconds if seconds else math.inf
        print(json.dumps(dict(status='admitted',hz=hz,timeout_ms=timeout_ms,scope='P4 state only; no EMOS/game delivery')),flush=True)
        while time.monotonic()<end:
            observer.poll()
            polled=time.monotonic()
            if not observer.device or observer.session!=source_session:
                raise InputFault('Controller disconnected; run sender again after replug')
            if observer.record_error:raise InputFault('Input recording failed: '+observer.record_error)
            for _ in range(32):
                try:data=udp.recv(256)
                except BlockingIOError:break
                packet,edge=decode_ack(data,instance,session)
                if packet>sent:raise InputFault('ACK claims datagram not sent')
                if packet>last_ack_packet:
                    queue.ack(edge);last_ack_packet=packet;last_ack=time.monotonic();acks+=1
            now=time.monotonic()
            if now-last_ack>=timeout_ms/1000:
                raise InputFault('No fresh receiver ACK within timeout')
            if now>=next_send:
                if sent>=2**32-1:raise InputFault('Datagram sequence exhausted')
                sent+=1
                data=encode(instance,session,sent,observer.state,queue.batch(),min(50,int((now-polled)*1000)))
                if udp.send(data)!=len(data):raise InputFault('Partial UDP send')
                next_send+=1/hz
                if next_send<=now:next_send=now+1/hz
            time.sleep(min(.002,max(0,next_send-time.monotonic())))
    except KeyboardInterrupt:
        pass
    except (OSError,ValueError,InputFault) as error:
        failure=str(error)
    finally:
        udp.close()
        observer.close()
        failure=failure or observer.record_error or None
        if session:
            try:control(base,'/controller/close',struct.pack('<QQ',instance,session))
            except (OSError,ValueError) as error:
                failure=failure or 'Close unconfirmed; receiver timeout required: '+str(error)
    result=dict(sent=sent,acks=acks,pending_edges=len(queue.pending) if queue else 0,
                elapsed_seconds=time.monotonic()-started,error=failure)
    print(json.dumps(result,indent=2),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True)
    p.add_argument('--device')
    p.add_argument('--hz',type=float,default=DEFAULT_HZ)
    p.add_argument('--timeout-ms',type=int,default=250)
    p.add_argument('--seconds',type=float)
    p.add_argument('--record')
    p.add_argument('--status',action='store_true',help='Read P4 status only; do not admit a sender')
    a=p.parse_args()
    try:
        if a.status:
            base,_=endpoint(a.url);print(json.dumps(control(base,'/controller/status'),indent=2));return 0
        result=run(a.url,device=a.device,hz=a.hz,timeout_ms=a.timeout_ms,seconds=a.seconds,record=a.record)
        return 1 if result['error'] else 0
    except (OSError,ValueError,InputFault) as error:p.exit(1,str(error)+'\n')
if __name__=='__main__':raise SystemExit(main())
