#!/usr/bin/env python3
"""Summarize S06 records/aggregate windows; never infer displayed game FPS."""
import argparse,hashlib,json
from pathlib import Path
from records import decode,summary
PHASES=('drain','row_wait','row_compose','expand','cache','conversion')

def analyse(raw,window=None):
    d=decode(raw);s=summary(d)
    ticks=(d['window_end']-d['window_start'])&0xffffff
    s['nominal_updates_per_second']=d['count']*120/ticks if ticks else None
    s['fault_rows']=sum(bool(r['flags']&11) for r in d['rows'])
    s['raw_sha256']=hashlib.sha256(raw).hexdigest()
    keys=('update','state','phase','actors','projectiles','map_row','rng')
    state=[[r[k] for k in keys] for r in d['rows']]
    s['trajectory_sha256']=hashlib.sha256(json.dumps(state,separators=(',',':')).encode()).hexdigest()
    s['activity']={name:{'min':min((r[name] for r in d['rows']),default=None),'max':max((r[name] for r in d['rows']),default=None)} for name in ('actors','projectiles')}
    # Stable interpretable groups; not claimed to count all sprites on screen.
    s['actor_groups']=[]
    for lo,hi in ((0,0),(1,2),(3,255)):
        rows=[r for r in d['rows'] if lo<=r['actors']<=hi]
        if not rows:continue
        group={'actor_min':lo,'actor_max':hi,'rows':len(rows)}
        sub=summary(dict(d,rows=rows,count=len(rows),expected=len(rows)))
        if not d['controls']&2:
            group.update(active=sub['active'],total=sub['total'],fault_rows=sub['fault_rows'])
        # Groups can be disjoint; do not treat their whole-run endpoints as a group duration.
        s['actor_groups'].append(group)
    if window is not None:
        if window['tag']!=d['window_tag'] or window['id']!=d['case'] or not d['controls']&4:
            raise ValueError('window/result identity mismatch')
        span=window['end_us']-window['start_us']
        if span<=0:raise ValueError('open/invalid window')
        s['p4']={'duration_us':span,'scanouts_per_second':window['scanouts']*1e6/span,'submissions_per_second':window['updates']*1e6/span,'phases':{}}
        for name,c in zip(PHASES,window['phases']):
            s['p4']['phases'][name]={**c,'mean_us':c['us']/c['calls'] if c['calls'] else None}
        s['p4']['scope_note']='Opening acknowledgement through final drain/close; nested/concurrent wall scopes, not CPU utilization. No frame-marker or sprite-visibility claim.'
    return s

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    meta=json.loads((a.run/'run.json').read_text());windows=json.loads((a.run/'windows.json').read_text())
    assert not windows['open'] and not windows['overflow']
    out={'run':meta,'cases':[]}
    for case in meta['cases']:
        raw=(a.run/f't{case:02}.bin').read_bytes();d=decode(raw)
        candidates=[w for w in windows['windows'] if w['tag']==d['window_tag'] and w['id']==case]
        expected=meta['endpoint']=='p4' and d['controls']&4 and meta.get('telemetry_required',True)
        assert len(candidates)==int(bool(expected))
        out['cases'].append(analyse(raw,candidates[0] if expected else None))
    data=json.dumps(out,indent=2)+'\n'
    if a.output:a.output.write_text(data)
    else:print(data,end='')
