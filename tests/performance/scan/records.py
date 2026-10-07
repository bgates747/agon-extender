#!/usr/bin/env python3
"""Decode finite SCAN records. Emulator values are functional evidence only."""
import argparse,csv,json,math,statistics
from pathlib import Path

def u24(b,n):return int.from_bytes(b[n:n+3],'little')
def decode(b):
    if len(b)<128 or b[:8]!=b'SCANR01!' or b[9]!=24:raise ValueError('invalid header')
    count=u24(b,16)
    if not 1<=b[8]<=9 or not 0<=count<=3600 or len(b)!=128+24*count:raise ValueError('truncated/extra/invalid records')
    rows=[]
    for p in range(128,len(b),24):
        a=b[p:p+24]
        r=dict(zip(['update','active','complete','total','mos_delta','state'],[u24(a,n) for n in range(0,18,3)]))
        r.update(zip(['flags','phase','actors','projectiles','map_row','rng'],a[18:]))
        if rows and r['update']!=rows[-1]['update']+1:raise ValueError('missing/reordered update')
        if not 0<=r['active']<=r['complete']<=r['total']<=65535:raise ValueError('timer order/range')
        if r['total']==65535 and not r['flags']&1:raise ValueError('unflagged saturation')
        r['wait']=r['total']-r['complete'];rows.append(r)
    return dict(case=b[8],count=count,expected=u24(b,35),warmup=u24(b,38),controls=b[41],window_tag=u24(b,10),build_id=b[42:128].split(b'\0')[0].decode(),abort=bool(b[34]),window_start=u24(b,19),window_end=u24(b,22),
        calibration_prt=u24(b,25),calibration_mos=u24(b,28),drain=u24(b,31),rows=rows)

def summary(d):
    rows=d['rows'];result={k:v for k,v in d.items() if k!='rows'}
    result['evidence_complete']=d['count']==d['expected'] and not d['abort']
    result['scope']='unfenced game submission/pacing' if d['controls']&1 else 'whole-update pixel-query completion (includes reply overhead)'
    if not rows or d['controls']&2:
        result['timing_disabled']=bool(d['controls']&2)
        return result
    def pctile(v,p):return sorted(v)[max(0,math.ceil(len(v)*p)-1)]
    for name in ['active','complete','total','wait']:
        v=[r[name] for r in rows]
        result[name]={'median_counts':statistics.median(v),'p95_counts':pctile(v,.95),'max_counts':max(v),
            'median_budget_percent':statistics.median(v)/12,'p95_budget_percent':pctile(v,.95)/12,
            'median_ms':statistics.median(v)/72,'over_budget_percent':100*sum(x>1200 for x in v)/len(v)}
    if d['controls']&1:result.pop('complete') # Not renderer completion when no fence was requested.
    result['median_active_headroom_percent']=100-result['active']['median_budget_percent']
    result['fault_rows']=sum(bool(r['flags']&11) for r in rows)
    result['late_rows']=sum(bool(r['flags']&4) for r in rows)
    streak=longest=0
    for r in rows:
        streak=streak+1 if r['total']>1200 or r['mos_delta']>2 else 0
        longest=max(longest,streak)
    result['longest_over_budget_streak']=longest
    ticks=(d['window_end']-d['window_start'])&0xffffff
    result['window_raw_mos_ticks']=ticks
    result['nominal_updates_per_second']=len(rows)*120/ticks if ticks else None
    result['nominal_clock_note']='18.432 MHz /256 PRT; raw MOS nominal120 units/s, observed in steps of2. Not display fps.'
    result['unmeasured_tail_estimate_ms']=(ticks/120-sum(r['total'] for r in rows)/72000)*1000
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--csv',type=Path);a=p.parse_args()
    d=decode(a.input.read_bytes());print(json.dumps(summary(d),indent=2))
    if a.csv:
        with a.csv.open('w') as f:
            w=csv.DictWriter(f,fieldnames=d['rows'][0].keys());w.writeheader();w.writerows(d['rows'])
