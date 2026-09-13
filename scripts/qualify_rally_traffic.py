#!/usr/bin/env python3
"""Local actual-Motion traffic qualification; no device access."""
import argparse
import ctypes
import json
from pathlib import Path
import subprocess
import time
from rally_drive import Sample,PassingDriver

def qualify(root,out,reserve=.58,grip=200,step=3):
    out.mkdir(parents=True)
    library=out/'motion.so'
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fPIC','-shared',
                    '-I'+str(root/'rally-bench/include'),'-I'+str(root/'rally-production/include'),
                    str(root/'rally-bench/tests/motion_bridge.cpp'),'-o',str(library)],check=True)
    game=ctypes.CDLL(str(library.resolve()));packet=(ctypes.c_ubyte*140)()
    results=[]
    for name,track,ticks,delay,blocked in [('oval',0,12,0,False),('fuji',1,12,0,False),
                                         ('delayed',0,16,1,False),('blocked',0,12,0,True),
                                         ('slow',0,22,0,False),('uneven',0,20,0,False)]:
        game.begin(track,0);game.set_grip(grip);game.set_step(step);driver=PassingDriver(reserve);queue=[0]*(delay+1)
        if blocked:
            for i in range(3):game.set_car(i,150,(i-1)*45,140)
        stats={'case':name,'grip':grip,'steering_step':step,'corner_reserve':reserve,'frames':0,'contacts':0,'grass':0,'passes':0,'top_speed':0,'max_decision_ms':0}
        previous=None
        with (out/(name+'.jsonl')).open('x') as log:
            for frame in range(7200//ticks):
                elapsed=(16,20,22,18)[frame%4] if name=='uneven' else ticks
                game.advance(queue.pop(0),elapsed,packet)
                sample=Sample.decode(dict(online=True,age_ms=0,payload=bytes(packet).hex()))
                start=time.monotonic();keys,detail=driver(sample);elapsed=time.monotonic()-start
                queue.append(keys);stats['max_decision_ms']=max(stats['max_decision_ms'],elapsed*1000)
                stats['frames']+=1;stats['contacts']=sample.contacts;stats['grass']+=sample.surface==2
                stats['top_speed']=max(stats['top_speed'],sample.speed)
                if previous:
                    stats['passes']+=sum(0<a[0]<sample.length*25 and -sample.length*25<b[0]<=0
                                         for a,b in zip(previous.traffic,sample.traffic))
                previous=sample
                log.write(json.dumps({**sample.__dict__,**detail,'requested_keys':keys})+'\n')
        print(json.dumps(stats),flush=True);results.append(stats)
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    assert all(r['contacts']==0 and r['grass']==0 for r in results),results
    assert results[0]['passes']>3 and results[0]['top_speed']>=280
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rally-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--reserve',type=float,default=.58);p.add_argument('--grip',type=int,default=200)
    p.add_argument('--step',type=int,choices=(1,2,3),default=3)
    a=p.parse_args();qualify(a.rally_root.resolve(),a.output,a.reserve,a.grip,a.step)
