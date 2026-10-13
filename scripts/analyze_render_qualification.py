#!/usr/bin/env python3
"""Summarize matched master results without conflating rendering and output."""
import argparse
import csv
import json
from pathlib import Path
import statistics


def reduction(control,candidate):
    return 100*(control-candidate)/control if control else None


def analyze(folder):
    plan=json.loads((folder/'plan.json').read_text())
    completion=json.loads((folder/'summary.json').read_text())
    groups={}
    for job in plan['jobs']:
        path=folder/job['id']
        if not (path/'receipt.json').exists():continue
        receipt=json.loads((path/'receipt.json').read_text())
        if not receipt.get('validated') or not (path/'summary.json').exists():continue
        record=json.loads((path/'summary.json').read_text())
        groups.setdefault((job['mode'],job['case'],job['renderer']),[]).append((receipt,record))
    rows=[]
    for mode,case in sorted({(j['mode'],j['case']) for j in plan['jobs']}):
        a=groups.get((mode,case,'rgb888'),[]);b=groups.get((mode,case,'indexed'),[])
        row=dict(mode=mode,workload=case,valid_rgb_runs=len(a),valid_indexed_runs=len(b),
                 comparable=False,queued_render_reduction_percent=None)
        if len(a)!=3 or len(b)!=3:
            row['limitation']='Requires three validated runs per renderer';rows.append(row);continue
        if sorted(x['trajectory_sha256'] for x,_ in a)!=sorted(x['trajectory_sha256'] for x,_ in b):
            row['limitation']='Deterministic trajectories differ';rows.append(row);continue
        row['comparable']=True
        for name,data in (('rgb',a),('indexed',b)):
            row[name+'_active_p95_budget_percent']=statistics.mean(r['active']['p95_budget_percent'] for _,r in data)
            row[name+'_active_p95_headroom_percent']=100-row[name+'_active_p95_budget_percent']
            row[name+'_updates_per_second']=statistics.mean(r['nominal_updates_per_second'] for _,r in data)
            row[name+'_storage']=' / '.join(sorted({str(x.get('actual_render_storage')) for x,_ in data}))
            row[name+'_render_us_per_update']=None if mode==136 else statistics.mean(
                r['queued_render']['rendering_us']/r['count'] for _,r in data)
        if mode==136:
            row['limitation']='Immediate double-buffer drawing is outside queued-render counters; use eZ80 timing and pacing'
        else:
            row['queued_render_reduction_percent']=reduction(row['rgb_render_us_per_update'],row['indexed_render_us_per_update'])
        rows.append(row)
    rows.sort(key=lambda r:(r['queued_render_reduction_percent'] is None,
                            r['queued_render_reduction_percent'] or 0,r['mode'],r['workload']))
    return dict(state=completion['state'],ranking='Smallest queued-render percentage reduction first; unmeasured rows last',
                scope='Matched within each mode only. Queued rendering excludes UART/parser/pacing/native wait/output. PRT nominal72kHz;1200 counts per60Hz budget. Headroom is eZ80 active-work budget, not P4 CPU utilization.',
                rows=rows)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=analyze(a.run)
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    fields=sorted({k for row in result['rows'] for k in row})
    with (a.output/'comparison.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(result['rows'])
    print('Saved matched comparisons; state:',result['state'])


if __name__=='__main__':main()
