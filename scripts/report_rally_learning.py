#!/usr/bin/env python3
"""Summarize retained physical Rally trials without contacting the bench."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

def report(budget_path):
    budget=json.loads(budget_path.read_text());runs=[]
    for record in budget['runs']:
        folder=Path(record['folder']);result=json.loads((folder/'result.json').read_text())
        lateral=[];speeds=[];ages=[];intervals=[];advances=[];frames=0;last=None
        duration=0.;centre_distance=0.;centre_time=0.;centre_target_time=0.
        pass_sides={"left":0,"right":0,"aligned":0}
        with (folder/'telemetry.jsonl').open() as source:
            for line in source:
                sample=json.loads(line);frames+=1
                lateral.append(abs(sample['lateral'])/256);speeds.append(sample['speed'])
                ages.append(sample['wire']['age_ms'])
                if last is not None:
                    dt=((sample['clock']-last['clock'])&0xffffffff)/120
                    duration+=dt
                    intervals.append(dt*1000)
                    advances.append((sample['frame']-last['frame'])&0xffffffff)
                    centre_distance+=dt*abs(last['lateral'])/256
                    centre_time+=dt*(abs(last['lateral'])<=16*256)
                    centre_target_time+=dt*(last['target_lane']==0)
                    for old,new in zip(last['traffic'],sample['traffic']):
                        if 0<old[0]<sample['length']*25 and -sample['length']*25<new[0]<=0:
                            fraction=old[0]/(old[0]-new[0])
                            player_y=last['lateral']+fraction*(sample['lateral']-last['lateral'])
                            opponent_y=old[1]+fraction*(new[1]-old[1])
                            side='left' if player_y<opponent_y else 'right' if player_y>opponent_y else 'aligned'
                            pass_sides[side]+=1
                last=sample
        runs.append({'folder':str(folder),'grip':record['grip'],'seconds':record['seconds'],
                     'steering_step':result.get('steering_step',3),'corner_reserve':result.get('corner_reserve'),
                     'frames':frames,'contacts':result.get('contacts'),
                     'median_observation_interval_ms':statistics.median(intervals) if intervals else None,
                     'p95_observation_interval_ms':sorted(intervals)[min(len(intervals)-1,int(.95*len(intervals)))] if intervals else None,
                     'max_render_updates_between_observations':max(advances,default=None),
                     'grass_samples':result.get('grass'),'kerb_samples':result.get('kerb'),
                     'passes':result.get('passes'),'pass_sides_estimate':pass_sides,'mean_abs_lateral':statistics.mean(lateral) if lateral else None,
                     'mean_speed':statistics.mean(speeds) if speeds else None,
                     'maximum_sample_receipt_age_ms':max(ages,default=None),
                     'mean_abs_lateral_time_weighted':centre_distance/duration if duration else None,
                     'fraction_within_16_world_units_of_centre':centre_time/duration if duration else None,
                     'fraction_targeting_centre':centre_target_time/duration if duration else None,
                     'laps':result.get('laps',[]),'error':result.get('error'),
                     'quit_confirmed':result.get('exit',{}).get('telemetry_stopped',False)
                         or (folder/'recovered-exit.json').exists(),
                     'driver_sha256':(folder/'driver.sha256').read_text().strip(),
                     'telemetry_sha256':hashlib.sha256((folder/'telemetry.jsonl').read_bytes()).hexdigest()})
    groups=[]
    for grip in (200,180,160,140):
        selected=[r for r in runs if r['grip']==grip]
        laps=[l for r in selected for l in r['laps']]
        clean=[l['seconds'] for l in laps if l['clean']]
        groups.append({'grip':grip,'seconds':sum(r['seconds'] for r in selected),
                       'completed_laps':len(laps),'clean_laps':len(clean),
                       'best_clean_lap_seconds':min(clean,default=None),
                       'median_clean_lap_seconds':statistics.median(clean) if clean else None,
                       'contacts':sum(r['contacts'] or 0 for r in selected),
                       'grass_samples':sum(r['grass_samples'] or 0 for r in selected),
                       'passes':sum(r['passes'] or 0 for r in selected)})
    return {'scope':'Physical, instrumented, telemetry-driven manual races; no demo/autosteer. '
                    'Lap crossings interpolate MOS ticks at 120 Hz and have one telemetry interval uncertainty. '
                    'Clean excludes contacts and grass; kerb use is recorded separately. '
                    'Centre occupancy uses left-held samples weighted by MOS-clock intervals; '
                    '16 world units is a reporting band on the 180-unit-wide road. '
                    'Steering step and corner reserve vary between trials and are recorded per run; '
                    'grip groups are not controlled single-variable comparisons. '
                    'Pass sides interpolate relative lateral position at observed longitudinal crossings; '
                    'they are left/right, without inferring inside/outside from a corner label. '
                    'Intervals describe delivered telemetry observations, not physical VDP completion or production FPS. '
                    'These results describe this controller, not a human difficulty threshold.',
            'programme':str(budget_path),'groups':groups,'runs':runs}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('budget',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(json.dumps(report(a.budget),indent=2)+'\n')
