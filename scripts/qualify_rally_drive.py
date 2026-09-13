#!/usr/bin/env python3
"""Local physics/codec qualification; no device, network or emulator access."""
import argparse
import ctypes
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile
from rally_drive import Sample,Freshness,TelemetryError,intent

def rejected(fn):
    try:fn()
    except TelemetryError:return
    raise AssertionError('Unsafe state was accepted')

def qualify(root):
    results=[]
    with tempfile.TemporaryDirectory(prefix='bench001-physics-') as directory:
        library=Path(directory)/'motion.so'
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fPIC','-shared',
                        '-I'+str(root/'rally-bench/include'),'-I'+str(root/'rally-production/include'),
                        str(root/'rally-bench/tests/motion_bridge.cpp'),'-o',str(library)],check=True)
        game=ctypes.CDLL(str(library));game.audio_check();game.contacts_check();out=(ctypes.c_ubyte*140)()
        for track in (0,1):
            for ticks in (4,6):
                for delay in (0,1,2):
                    game.begin(track,0);queue=[0]*(delay+1)
                    distance=0;previous=0;maximum=0;grass=0
                    for frame in range(36000//ticks):
                        game.advance(queue.pop(0),ticks,out)
                        packet={'online':True,'age_ms':0,'payload':bytes(out).hex()}
                        sample=Sample.decode(packet);queue.append(intent(sample,180)[0])
                        distance+=(sample.position-previous)%(sample.length*100)/100
                        previous=sample.position;maximum=max(maximum,abs(sample.lateral)/256)
                        grass+=sample.surface==2
                    assert grass==0 and maximum<35 and distance>sample.length
                    results.append(dict(track=('oval','fuji')[track],frame_ticks=ticks,
                                        delayed_frames=delay,simulated_seconds=300,
                                        laps=distance/sample.length,max_lane_error=maximum,grass_frames=grass))
        # These failures are independent of actual HTTP receipt freshness.
        gate=Freshness();assert gate.observe(sample,0);assert not gate.observe(sample,.1)
        rejected(lambda:gate.observe(sample,.201))
        rejected(lambda:gate.observe(replace(sample,run=sample.run+1),.1))
        rejected(lambda:gate.observe(replace(sample,frame=sample.frame-1),.1))
        rejected(lambda:gate.observe(replace(sample,frame=sample.frame+1),.1))
        rejected(lambda:Sample.decode(dict(packet,online=False)))
        rejected(lambda:Sample.decode(dict(packet,age_ms=200)))
        damaged=bytearray(out);damaged[24]^=1
        rejected(lambda:Sample.decode(dict(packet,payload=damaged.hex())))
    return {'scope':'Actual production Motion and snapshot encoder; modeled whole-frame input delay. No UART/HTTP/physical timing claim.',
            'audio':'Stock packet generation, monotonic frequency, unchanged-speed suppression and cleanup passed; silent test.',
            'freshness':'Offline/stale, duplicate progress, backwards/run change and CRC failures rejected.',
            'runs':results}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rally-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=qualify(args.rally_root.resolve())
    with args.output.open('x') as output:json.dump(result,output,indent=2);output.write('\n')
    print('PASS: twelve five-minute physics runs, audio commands and stale-state guards')

if __name__=='__main__':main()
