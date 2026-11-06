#!/usr/bin/env python3
"""One finite four-session peer for the separately selected repeated fixture."""
import argparse
import datetime
import json
from pathlib import Path
import socket
import struct
import time

SIZES=(0,1,2,17,63,64,65,75,79,127,128)
SESSIONS=4
ROUNDS=4

def payload(session,index,size):
    seed=session*ROUNDS*len(SIZES)+index
    pattern=(session+index//len(SIZES))%4
    if pattern==0:return bytes((j*37+seed)&255 for j in range(size))
    if pattern==1:return bytes((~(j*37+seed))&255 for j in range(size))
    if pattern==2:return bytes(255 if (j+seed)%2 else 0 for j in range(size))
    return bytes(1<<((j+seed)%8) for j in range(size))

def serve(server,output,*,seconds=150,progress=5,registration=30):
    """Original whole deadline plus bounded reads; no retry after any failure."""
    start=time.monotonic();deadline=start+seconds
    report=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                records=[],closed_sessions=0,passed=False,clock='host monotonic')
    def timeout(peer,limit=progress):
        left=deadline-time.monotonic()
        if left<=0:raise TimeoutError('Original whole peer deadline')
        peer.settimeout(min(limit,left))
    def exact(peer,n):
        data=bytearray()
        while len(data)<n:
            timeout(peer);chunk=peer.recv(n-len(data))
            if not chunk:raise RuntimeError('Peer closed mid-record')
            data.extend(chunk)
        return bytes(data)
    try:
        for session in range(SESSIONS):
            # Initial CLI delivery/mode settling precedes CONNECT. This is a
            # registration allowance inside the original whole deadline, never
            # a reset of that deadline or a retry after a failed accept.
            timeout(server,registration if session==0 else progress)
            peer,_=server.accept()
            with peer:
                for index in range(ROUNDS*len(SIZES)):
                    size=SIZES[index%len(SIZES)]
                    if struct.unpack('<I',exact(peer,4))[0]!=size:
                        raise RuntimeError('Unexpected record length')
                    data=exact(peer,size)
                    if data!=payload(session,index,size):raise RuntimeError('Unexpected record bytes')
                    timeout(peer);peer.sendall(struct.pack('<I',size)+data)
                    report['records'].append(dict(session=session,index=index,bytes=size))
                timeout(peer)
                if peer.recv(1):raise RuntimeError('Unexpected extra record')
            report['closed_sessions']+=1
        report['passed']=True
    except BaseException as exc:
        report['first_error']=repr(exc)
        raise
    finally:
        report.update(ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      duration_ns=int((time.monotonic()-start)*1e9))
        (output/'run.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    import os
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE,(1024*1024,1024*1024))
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bind',required=True);p.add_argument('--port',required=True,type=int)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    with socket.socket() as server:
        server.bind((a.bind,a.port));server.listen(1)
        (a.output/'ready.json').write_text(json.dumps(dict(pid=os.getpid(),port=server.getsockname()[1],sessions=4,records=176,initial_registration_seconds=30,progress_seconds=5,deadline_monotonic=time.monotonic()+150))+'\n')
        report=serve(server,a.output)
    print(json.dumps(dict(passed=report['passed'],records=len(report['records']),closed_sessions=report['closed_sessions'])))
if __name__=='__main__':main()
