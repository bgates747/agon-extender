#!/usr/bin/env python3
"""Wired HTTP collector. No board mutations; exact payload validation per frame."""
import argparse,http.client,json,struct,time,hashlib
from pathlib import Path
W,H=512,384

def reference(phase):
    p=bytearray(((x>>2)^(y>>2)^phase)&63 for y in range(H) for x in range(W))
    for i in range(16):
        x=(phase*7+i*29)%(W-24); y=(phase*3+i*19)%(H-24)
        for dy in range(24):p[(y+dy)*W+x:(y+dy)*W+x+24]=bytes([(i*3+phase)&63])*24
    return bytes(p)

def exact(response,n):
    b=bytearray()
    while len(b)<n:
        c=response.read(n-len(b))
        if not c:raise EOFError(f'truncated record {len(b)}/{n}')
        b.extend(c)
    return bytes(b)

def run(host,mode,fps,frames,out):
    expected=[reference(i) for i in range(64)]
    connection=http.client.HTTPConnection(host,timeout=90)
    samples=[]; report={'mode':mode,'target':fps,'requested':frames,'state':'starting'}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    def persist():out.write_text(json.dumps(report,indent=2)+'\n')
    persist();begin=time.monotonic_ns()
    try:
        connection.request('GET',f'/run?mode={mode}&fps={fps}&frames={frames}')
        resp=connection.getresponse()
        if resp.status!=200:raise RuntimeError(f'HTTP {resp.status}: {resp.read()!r}')
        previous=-1;validation=0
        while True:
            magic,seq,size,render,lo,hi=struct.unpack('<6I',exact(resp,24))
            if magic==0x314a3352:
                assert size<=2048
                report['device']=json.loads(exact(resp,size));break
            assert magic==0x31463352 and size==W*H and previous<seq<frames
            payload=exact(resp,size);now=time.monotonic_ns()
            v=time.monotonic_ns();assert payload==expected[seq&63],f'pixel mismatch {seq}'
            validation+=time.monotonic_ns()-v
            samples.append({'seq':seq,'host_ns':now-begin,'done_us':lo+(hi<<32),'render_us':render})
            previous=seq
        assert resp.read()==b'', 'trailing bytes'
        d=report['device'];assert d['sent']==len(samples) and d['send_error']==0
        assert d['produced']+d['dropped']==frames
        if mode=='render':assert not samples
        else:assert d['produced']==len(samples)
        duration=d['elapsed_us']/1e6
        report.update(state='complete',pixel_validation='pass',samples=samples,
            validation_ms=validation/1e6,host_elapsed_s=(time.monotonic_ns()-begin)/1e9,
            device_window_fps=len(samples)/duration,device_window_payload_mbps=len(samples)*W*H*8/duration/1e6)
        persist();print(json.dumps({k:v for k,v in report.items() if k!='samples'}),flush=True)
    except BaseException as e:
        report.update(state='failed',error=repr(e),samples=samples);persist();raise
    finally:connection.close()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--host',required=True);p.add_argument('--mode',choices=['render','send','combined'],required=True);p.add_argument('--fps',type=int,required=True);p.add_argument('--frames',type=int,default=600);p.add_argument('--out',required=True);a=p.parse_args();run(a.host,a.mode,a.fps,a.frames,a.out)
