#!/usr/bin/env python3
"""Validate raw game timing CSV and summarize elapsed scopes without mixing clocks."""
import argparse,csv,json
from pathlib import Path

def summarize(path,prt_divider=16):
    if prt_divider not in (16,64):raise ValueError("Unsupported PRT divider")
    frequency=18432000/prt_divider
    with Path(path).open(newline='') as f:rows=[{k:int(v) for k,v in row.items()} for row in csv.DictReader(f)]
    if len(rows)!=120 or [r['frame'] for r in rows]!=list(range(120)):
        raise ValueError('Expected exactly 120 sequential updates')
    sources={r['source'] for r in rows}
    if len(sources)!=1 or not sources<={0,1,255}:raise ValueError('Inconsistent source')
    for r in rows:
        if not (0<=r['active_prt']<=r['total_prt']<=65535):raise ValueError('PRT count out of bounds')
        if r['overflow']!=int(r['total_prt']==65535):raise ValueError('PRT saturation flag mismatch')
        if r['active_prt']+r['pacing_prt']!=r['total_prt']:raise ValueError('Host intervals do not partition total')
        if r['submitted_us']+r['drain_us']!=r['completed_us']:raise ValueError('Renderer intervals do not partition completion')
    active=sum(r['active_prt'] for r in rows);pace=sum(r['pacing_prt'] for r in rows);total=active+pace
    if not total:raise ValueError('No elapsed clock ticks')
    out={'source':next(iter(sources)),'updates':len(rows),'prt_divider':prt_divider,'prt_counts_per_second_nominal':frequency,
         'clock_resolution_us_nominal':1000000/frequency,
         'overflow_rows':sum(bool(r['overflow']) for r in rows),
         'active_prt':active,'pacing_prt':pace,'total_prt':total,
         'active_ms_per_update':1000*active/frequency/len(rows),'pacing_ms_per_update':1000*pace/frequency/len(rows),
         'active_percent':100*active/total,'updates_per_second':len(rows)*120/rows[0]['run_ticks'] if rows[0]['run_ticks'] else None,
         'active_max_prt_counts':max(r['active_prt'] for r in rows)}
    if out['overflow_rows']:
        for key in ['active_ms_per_update','pacing_ms_per_update','active_percent']:out[key]=None
    if sources!={255}:
        for field in ['submitted_us','completed_us','drain_us']:
            v=sorted(r[field] for r in rows)
            out[field]={'mean':sum(v)/len(v),'p50':v[len(v)//2],'p95':v[(len(v)*95+99)//100-1],'max':v[-1]}
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv',nargs='+',type=Path);p.add_argument('--prt-divider',type=int,choices=[16,64],default=16);a=p.parse_args()
    print(json.dumps({str(f):summarize(f,a.prt_divider) for f in a.csv},indent=2))
