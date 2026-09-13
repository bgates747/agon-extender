#!/usr/bin/env python3
"""One attended full-game attempt. See Rally R22-11; no launch/reset/SD changes.

The separate full-game profile retains the v2 transport, adds phase in flags'
upper nibble and INT32_MIN absent cars. Original bench decoder stays strict.
"""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import struct
import time
import zlib
from rally_drive import Sample, TelemetryError, Freshness, PassingDriver, DriveClient, validate_keyboard

def decode(reply, maximum_age_ms=300):
    if reply.get('online') is not True or not 0 <= reply.get('age_ms',9999) < maximum_age_ms:
        raise TelemetryError('Full-game telemetry offline/stale')
    p=bytearray.fromhex(reply['payload'])
    if len(p)!=140 or zlib.crc32(p[:136])!=struct.unpack_from('<I',p,136)[0]:
        raise TelemetryError('Full-game size/CRC')
    flags=p[3]; phase=flags>>4
    if phase>9 or (flags&1 and phase not in (3,6)) or (phase in (3,6) and flags&6):
        raise TelemetryError('Invalid phase/assistance flags')
    active=[]
    for i in range(6):
        car=struct.unpack_from('<ihH',p,88+i*8)
        if car[0]==-2147483648:
            if car[1:]!=(0,0):raise TelemetryError('Invalid absent car')
            # Reuse the old bounds validator on a benign placeholder, then
            # remove it. Raw evidence below always retains the real payload.
            struct.pack_into('<ihH',p,88+i*8,0,0,0)
        else:
            if phase!=6:raise TelemetryError('Traffic outside race')
            active.append(car)
    # Parsing non-driving phases must not authorize controls. Preserve original
    # flags on the returned sample; the caller explicitly gates driving below.
    p[3]=1|(flags&8)
    struct.pack_into('<I',p,136,zlib.crc32(p[:136]))
    sample=Sample.decode({**reply,'payload':p.hex()},maximum_age_ms)
    return replace(sample,flags=flags,traffic=tuple(active)),phase

def run(url, folder, seconds=300):
    folder=Path(folder);folder.mkdir(exist_ok=False,parents=True)
    client=DriveClient(url,folder/'keyboard.json');fresh=Freshness(.3)
    driver=PassingDriver(.58);held=0;last_phase=None;started=time.monotonic()
    result={'frames':0,'grip':200,'track':'fuji','policy':'arcade','phases':[]}
    try:
        sample,phase=decode(client.http('/telemetry/latest'))
        if sample.track!=1 or sample.grip!=200 or phase not in (2,3):
            raise TelemetryError('Require fresh Fuji qualifier/countdown at grip200')
        run_id=sample.run
        client.open();beat=time.monotonic()
        with (folder/'telemetry.jsonl').open('x',buffering=1) as log:
            while time.monotonic()-started<seconds:
                loop=time.monotonic();reply=client.http('/telemetry/latest')
                sample,phase=decode(reply)
                if sample.run!=run_id or sample.grip!=200:
                    raise TelemetryError('Run or grip changed')
                if fresh.observe(sample,time.monotonic()):
                    status=client.status();validate_keyboard(status,client)
                    if time.monotonic()-loop+reply['age_ms']/1000>=.3:
                        raise TelemetryError('Observation expired before control')
                    if phase!=last_phase:
                        result['phases'].append(phase);last_phase=phase;driver=PassingDriver(.58)
                        print('Game phase',phase,flush=True)
                    detail={};wanted=0
                    if phase in (3,6) and sample.flags&1:
                        wanted,detail=driver(sample,300)
                    if time.monotonic()-loop+reply['age_ms']/1000>=.3:
                        raise TelemetryError('Observation expired during prediction')
                    if not status['pending'] and wanted!=held:
                        usages=(80,79,82,81)
                        events=[(u,0) for i,u in enumerate(usages) if held&(1<<i) and not wanted&(1<<i)]
                        events += [(u,1) for i,u in enumerate(usages) if wanted&(1<<i) and not held&(1<<i)]
                        client.request(2,events);held=wanted;beat=time.monotonic()
                    result['frames']+=1;result['contacts']=sample.contacts
                    log.write(json.dumps({'seconds':loop-started,'phase':phase,**sample.__dict__,
                                          **detail,'requested_keys':held,'wire':reply})+'\n')
                    if phase in (7,8,9):result['terminal_phase']=phase;break
                    if phase in (0,1):raise TelemetryError('Unexpected title/menu')
                if time.monotonic()-beat>=1:client.request(4);beat=time.monotonic()
                time.sleep(max(0,.04-(time.monotonic()-loop)))
            else:raise TelemetryError('Attempt deadline reached')
    except (Exception,KeyboardInterrupt) as failure:
        result['error']=repr(failure)
    finally:
        try:
            client.request_timeout=1
            if client.state.get('pending'):client.recover()
            if client.state.get('active'):result['release']=client.cancel()
        except Exception as failure:result['release_error']=repr(failure)
        client.lock.close()
        result['seconds']=time.monotonic()-started
        (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--seconds',type=float,default=300)
    a=p.parse_args();result=run(a.url,a.output,a.seconds)
    print(json.dumps(result,indent=2));raise SystemExit(1 if 'error' in result or 'release_error' in result else 0)
