#!/usr/bin/env python3
"""BENCH-001: drive an already-running manual Rally using live telemetry.

No firmware/SD/reset or application launch operations. Key transitions use the
existing admitted remote keyboard protocol. A stale run ends this session;
uncertain commands are journalled, never retyped into a newly opened session.
"""
import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import struct
import time
from urllib.request import Request,urlopen
import zlib
from keyboard import Client,KeyboardError

class TelemetryError(RuntimeError): pass

@dataclass(frozen=True)
class Sample:
    run:int; frame:int; clock:int; position:int; speed:int
    lateral:int; velocity:int; steering:int; grip:int; length:int
    bend:int; maximum:int; surface:int; track:int; held:int; physics:int
    bends:tuple; half_width:int; kerb_width:int; elapsed:int; step:int; flags:int
    traffic:tuple; contact_mask:int; contacts:int

    @classmethod
    def decode(cls,reply,maximum_age_ms=200):
        if reply.get('online') is not True or not 0<=reply.get('age_ms',9999)<maximum_age_ms:
            raise TelemetryError('Telemetry is offline or too old')
        try: p=bytes.fromhex(reply['payload'])
        except (KeyError,ValueError,TypeError) as error: raise TelemetryError('Invalid snapshot encoding') from error
        if (len(p)!=140 or p[:3]!=b'RT\x02' or p[51] or p[79]
                or p[80]!=6 or p[81]&0xc0 or p[82:84]!=bytes((12,16))
                or zlib.crc32(p[:136])!=struct.unpack_from('<I',p,136)[0]):
            raise TelemetryError('Invalid snapshot version/size/CRC')
        u32=lambda n:struct.unpack_from('<I',p,n)[0]
        i32=lambda n:struct.unpack_from('<i',p,n)[0]
        u16=lambda n:struct.unpack_from('<H',p,n)[0]
        value=cls(u32(4),u32(8),u32(12),i32(16),i32(20),i32(24),i32(28),
                  struct.unpack_from('<h',p,32)[0],u16(34),u32(36),i32(40),i32(44),
                  p[48],p[49],p[50],u32(52),struct.unpack_from('<8h',p,56),
                  u16(72),u16(74),u16(76),p[78],p[3],
                  tuple(struct.unpack_from('<ihH',p,88+8*i) for i in range(6)),p[81],u32(84))
        if (value.flags&7)!=1: raise TelemetryError('Requires a running manual race without autosteer')
        if not (0<=value.speed<=300 and abs(value.steering)<=21 and 1<=value.step<=3
                and 25<=value.grip<=200 and value.length>0
                and 0<=value.position<value.length*100 and abs(value.lateral)<=150*256
                and value.half_width==90*256 and value.kerb_width==106*256
                and value.surface<=2 and value.track<=1 and value.held<16):
            raise TelemetryError('Snapshot outside the current driving contract')
        if any(abs(d)>value.length*50 or abs(y)>90*256 or not 0<=v<=300
               for d,y,v in value.traffic):
            raise TelemetryError('Invalid traffic bounds')
        return value

class Freshness:
    def __init__(self,maximum_gap=.2): self.last=None;self.at=None;self.maximum_gap=maximum_gap
    def observe(self,sample,now):
        if self.last is not None:
            if sample.run!=self.last.run or sample.track!=self.last.track:
                raise TelemetryError('Rally run changed; no automatic restart')
            advance=(sample.frame-self.last.frame)&0xffffffff
            clock=(sample.clock-self.last.clock)&0xffffffff
            if advance>=0x80000000 or clock>=0x80000000:
                raise TelemetryError('Game state moved backwards')
            if not advance:
                if now-self.at>=self.maximum_gap: raise TelemetryError('Rally frames stopped advancing')
                return False
            if not clock: raise TelemetryError('Frame changed without game clock progress')
            if now-self.at>=self.maximum_gap: raise TelemetryError('Observation gap exceeded configured limit')
        self.last=sample;self.at=now;return True

class LapRecorder:
    """Crossing times interpolated between coherent raw-clock observations.

    Contacts are physics-tick counts; surface durations are sampled estimates.
    Kerb use is reported separately. A clean lap has no contacts or grass;
    road_only additionally excludes kerb samples. Never call these exact
    transponder timings: crossing uncertainty is one telemetry interval.
    """
    def __init__(self):
        self.last=None;self.ticks=0;self.start=0;self.contacts=0
        self.grass=0;self.kerb=0;self.laps=[]
    def observe(self,s):
        old=self.last;self.last=s
        if old is None:self.contacts=s.contacts;return None
        dt=(s.clock-old.clock)&0xffffffff;before=self.ticks;self.ticks+=dt
        grass=dt if s.surface==2 else 0;kerb=dt if s.surface==1 else 0
        self.grass+=grass;self.kerb+=kerb
        if s.position>=old.position:return None
        advance=(s.position-old.position)%(s.length*100)
        at=before+dt*(s.length*100-old.position)/advance
        contacts=(s.contacts-self.contacts)&0xffffffff
        lap={'number':len(self.laps)+1,'seconds':(at-self.start)/120,
             'contacts':contacts,'grass_seconds_estimate':self.grass/120,
             'kerb_seconds_estimate':self.kerb/120,
             'clean':contacts==0 and not self.grass,
             'road_only':contacts==0 and not self.grass and not self.kerb,
             'crossing_interval_ms':dt*1000/120,'grip':s.grip}
        self.laps.append(lap);self.start=at;self.contacts=s.contacts
        self.grass=grass;self.kerb=kerb
        return lap

def speed_limit(s,maximum_speed,reserve=.58):
    limit=s.grip*180*256/100
    worst=max(abs(x) for x in s.bends)
    target=min(maximum_speed,math.sqrt(limit*reserve*1024/max(1,worst)))
    if abs(s.lateral)>76*256:target=min(target,110)
    if s.surface==2:target=min(target,70)
    return target

def intent(s,maximum_speed=300,target_lane=0,reserve=.58):
    """Lateral feedback plus the manual physics' curvature feed-forward.

    Output is a desired held-key mask, never a direct game-state change.
    Look-ahead reserves grip for steering corrections and early braking.
    """
    target=speed_limit(s,maximum_speed,reserve)
    centripetal=s.speed*s.speed*s.bend/1024
    wanted=-1.6*(s.lateral-target_lane*256)+.12*centripetal
    angle=max(-21,min(21,wanted*63/(max(25,s.speed)*512)))
    # Move toward the nearest angle reachable from the current steering value.
    # With step2, clipping at +/-21 changes parity; a zero-based grid is wrong.
    angle=s.steering+round((angle-s.steering)/s.step)*s.step
    angle=max(-21,min(21,angle))
    keys=(1 if s.steering>angle else 2 if s.steering<angle else 0)
    if s.speed<target-4: keys|=4
    elif s.speed>target+4: keys|=8
    return keys,{'target_speed':target,'target_steering':angle,'target_lane':target_lane}

class PassingDriver:
    """Short predictive lane/speed search; observed keys are the only actuator.

    Forecasts use the published bend samples and unchanged Motion equations.
    One rendered update of input delay is included. This is telemetry driving,
    with access to all opponents, not a vision or human reaction-time claim.
    """
    def __init__(self,reserve=.58): self.lane=0;self.last_keys=None;self.reserve=reserve

    @staticmethod
    def forecast(s,lane,target_speed,first_keys=None,next_keys=None):
        y=s.lateral/256;velocity=s.velocity/256;speed=s.speed;steer=s.steering
        progress=0;dt=max(4,min(32,s.elapsed));limit=s.grip*1.8
        opponents=[(d/100,cy/256,cv) for d,cy,cv in s.traffic]
        margin=1000.;unsafe=0
        keys=s.held if first_keys is None else first_keys
        # 1.8 real seconds, 120 raw physics ticks per real second. Lateral
        # integration retains the game's historical /100 scale deliberately.
        for tick in range(216):
            if tick%dt==0:
                if tick==dt and next_keys is not None:
                    keys=next_keys
                elif tick:
                    bend=s.bends[min(7,int(progress//64))]
                    wanted=-1.6*(y-lane)+.12*speed*speed*bend/(1024*256)
                    angle=max(-21,min(21,wanted*63/(max(25,speed)*2)))
                    angle=steer+round((angle-steer)/s.step)*s.step
                    angle=max(-21,min(21,angle))
                    keys=(1 if steer>angle else 2 if steer<angle else 0)
                    keys|=4 if speed<target_speed-4 else 8 if speed>target_speed+4 else 0
                steer=max(-21,min(21,steer+(-s.step if keys&1 else s.step if keys&2 else 0)))
            speed=max(0,min(300,speed+(-4 if keys&8 else 2 if keys&4 else 0)))
            bend=s.bends[min(7,int(progress//64))]
            centr=speed*speed*bend/(1024*256)
            wanted=steer*speed*2/63
            available=max(-limit,min(limit,(wanted-velocity)/.12))
            velocity+=(available-centr)/100
            y+=velocity/100;progress+=speed*.02
            # Replan every observation: an immediate collision must never be
            # traded for fewer overlapping ticks much later in this forecast.
            urgency=(216-tick)**2
            if abs(y)>76:unsafe+=urgency*3
            for d,cy,cv in opponents:
                longitudinal=d+cv*.02*(tick+1)-progress
                if abs(longitudinal)<47:
                    gap=abs(y-cy)-24
                    margin=min(margin,gap)
                    if gap<8:unsafe+=urgency*(4 if gap<0 else 1)
        return unsafe,margin,progress

    def __call__(self,s,maximum_speed=300):
        maximum_speed=speed_limit(s,maximum_speed,self.reserve)
        # Skip the search when nobody can reach our passing zone in its horizon.
        threats=[c for c in s.traffic if -18000<c[0]<95000]
        if not threats:
            self.lane=0;self.last_keys,detail=intent(s,maximum_speed,0,self.reserve)
            return self.last_keys,detail
        best=None
        for speed in sorted(set((maximum_speed,min(maximum_speed,240),min(maximum_speed,180),min(maximum_speed,120),0)),reverse=True):
            for lane in (0,-36,36,-65,65):
                # Stay beside a nearby opponent until it clears the crossing
                # corridor. A future replan may brake, so a predicted pass is
                # insufficient permission to cut back across its lane now.
                crossing = any(abs(d)<14000 and abs(s.lateral-y)>32*256
                    and (s.lateral-y)*(lane*256-y)<32*256*abs(s.lateral-y)
                    for d,y,v in s.traffic)
                command=intent(s,speed,lane,self.reserve)[0]
                immediate=self.forecast(s,lane,speed,command)
                delayed=self.forecast(s,lane,speed,
                                      s.held if self.last_keys is None else self.last_keys,command)
                # The next key-map poll may see this request immediately or
                # after the preceding request. Require both trajectories to be
                # safe; assuming the delay existed caused premature cut-ins.
                unsafe=max(immediate[0],delayed[0]) + (10**12 if crossing else 0)
                margin=min(immediate[1],delayed[1]);progress=min(immediate[2],delayed[2])
                # Safe passing progress outranks centre preference. Among
                # equally progressive paths, return to centre for spectators;
                # its cost exceeds the penalty for leaving a passing lane.
                score=(unsafe, -progress, abs(lane-self.lane)*.35+abs(lane)*2.0)
                if best is None or score<best[0]:best=(score,lane,speed,margin)
        _,self.lane,speed,margin=best
        keys,detail=intent(s,speed,self.lane,self.reserve)
        self.last_keys=keys
        detail.update(predicted_risk=best[0][0],predicted_clearance=margin)
        return keys,detail

class DriveClient(Client):
    """Same protocol/journal, but bounded HTTP observation and no long retry loop."""
    def http(self,path,data=None):
        request=Request(self.url+path,data=data,headers={
            'X-Agon-Keyboard':'1','Content-Type':'application/octet-stream'})
        # Occasional healthy HTTP replies exceed 120 ms on the physical P4.
        # Keep each request below the separate 300 ms observation deadline;
        # do not replay uncertain keyboard mutations here.
        with urlopen(request,timeout=getattr(self,'request_timeout',.2)) as response:return json.load(response)

    def recover(self):
        pending=self.state.get('pending')
        if not pending: raise KeyboardError('No uncertain request to recover')
        data=bytes.fromhex(pending);reply=self.http('/keyboard/rpc',data)
        if (reply['boot'],reply['session'],reply['sequence'])!=struct.unpack_from('<III',data,4):
            raise KeyboardError('Keyboard epoch changed')
        self.state['sequence']=reply['sequence'];self.state['pending']=None;self.save()
        if data[3]!=3 and reply['reason']:raise KeyboardError('Physical takeover or keyboard cancellation')
        return reply

def validate_keyboard(reply,client):
    if ((reply['boot'],reply['session'])!=(client.state['boot'],client.state['session'])
            or reply['reason'] or not reply['ready']):
        raise KeyboardError('Keyboard session ended')

def run(url,state,log,seconds=120,maximum_speed=300,maximum_gap=.3,corner_reserve=.58):
    client=DriveClient(url,state);fresh=Freshness(maximum_gap);held=0
    metrics={'frames':0,'road':0,'kerb':0,'grass':0,'max_lane_error':0,'distance':0,
             'contacts':0,'passes':0,'max_speed':0}
    driver=PassingDriver(corner_reserve);laps=LapRecorder();last_traffic=None;initial_contacts=None
    metrics['corner_reserve']=corner_reserve
    last_position=None;started=time.monotonic();error=None
    try:
        # Require a coherent manual game before asking for keyboard admission.
        sample=Sample.decode(client.http('/telemetry/latest'),maximum_gap*1000);fresh.observe(sample,time.monotonic())
        metrics['steering_step']=sample.step
        client.open();beat=time.monotonic();status=client.status()
        with Path(log).open('x',buffering=1) as output:
            while time.monotonic()-started<seconds:
                loop=time.monotonic()
                received=client.http('/telemetry/latest')
                sample=Sample.decode(received,maximum_gap*1000)
                if fresh.observe(sample,time.monotonic()):
                    status=client.status();validate_keyboard(status,client)
                    if time.monotonic()-loop+received['age_ms']/1000>=maximum_gap:
                        raise TelemetryError('Observation expired during keyboard status lookup')
                    wanted,detail=driver(sample,maximum_speed)
                    # A whole previous transition batch drains before another
                    # is submitted. Releases precede presses; no type-ahead.
                    if not status['pending'] and wanted!=held:
                        usages=(80,79,82,81)
                        events=[(u,0) for i,u in enumerate(usages) if held&(1<<i) and not wanted&(1<<i)]
                        events +=[(u,1) for i,u in enumerate(usages) if wanted&(1<<i) and not held&(1<<i)]
                        client.request(2,events);held=wanted;beat=time.monotonic()
                    metrics['frames']+=1
                    metrics['max_speed']=max(metrics['max_speed'],sample.speed)
                    if initial_contacts is None:initial_contacts=sample.contacts
                    metrics['contacts']=(sample.contacts-initial_contacts)&0xffffffff
                    if last_traffic is not None:
                        metrics['passes']+=sum(0<old[0]<sample.length*25 and -sample.length*25<new[0]<=0
                                              for old,new in zip(last_traffic,sample.traffic))
                    last_traffic=sample.traffic
                    metrics[('road','kerb','grass')[sample.surface]]+=1
                    metrics['max_lane_error']=max(metrics['max_lane_error'],abs(sample.lateral)/256)
                    if last_position is not None:
                        metrics['distance']+=(sample.position-last_position)%(sample.length*100)/100
                    last_position=sample.position
                    lap=laps.observe(sample)
                    output.write(json.dumps({'seconds':loop-started,**sample.__dict__,**detail,
                                             'requested_keys':held,'wire':received,'completed_lap':lap})+'\n')
                if time.monotonic()-beat>=1:
                    client.request(4);beat=time.monotonic()
                # Telemetry arrives much less frequently than this 25 Hz poll.
                # Query keyboard status only for an advancing sample; P4 itself
                # still cancels immediately on physical takeover.
                time.sleep(max(0,.04-(time.monotonic()-loop)))
    except (Exception,KeyboardInterrupt) as failure:
        error=repr(failure)
        if 'received' in locals():metrics['last_reply_on_error']=received
    finally:
        # Retry only the exact uncertain packet, then cancel. If the endpoint
        # is unreachable, stop refreshing its existing five-second lease.
        try:
            # Driving has stopped. Cleanup may use the ordinary bounded CLI
            # timeout so one brief HTTP stall does not also prevent key release.
            client.request_timeout=1
            status=client.status()
            metrics['exit_admission']={k:status[k] for k in ('boot','session','reason','physical_neutral','ready')}
            if client.state.get('pending'):client.recover()
            if client.state.get('active'):client.cancel()
        except Exception as failure:metrics['release_error']=repr(failure)
        client.lock.close()
    metrics['seconds']=time.monotonic()-started
    metrics['laps']=laps.laps
    clean=[lap['seconds'] for lap in laps.laps if lap['clean']]
    metrics['best_clean_lap_seconds']=min(clean) if clean else None
    if error:metrics['error']=error
    Path(str(log)+'.summary.json').write_text(json.dumps(metrics,indent=2)+'\n')
    return metrics

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True);p.add_argument('--state',type=Path,required=True)
    p.add_argument('--log',type=Path,required=True)
    p.add_argument('--seconds',type=float,default=120);p.add_argument('--max-speed',type=int,default=300)
    a=p.parse_args()
    if not 1<=a.seconds<=3600 or not 40<=a.max_speed<=300:p.error('seconds 1..3600, max-speed 40..300')
    result=run(a.url,a.state,a.log,a.seconds,a.max_speed);print(json.dumps(result,indent=2))
    return 1 if result.get('error') or result.get('release_error') else 0

if __name__=='__main__':raise SystemExit(main())
