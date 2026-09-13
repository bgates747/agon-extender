#!/usr/bin/env python3
"""Compare completed, identical graphics cases; keep interval scopes separate."""
import argparse
import csv
import json
from pathlib import Path
import statistics
import sys

TASK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TASK.parents[1]/'QUAL-003/timing/scripts'))
from read_results import validate

p=argparse.ArgumentParser()
p.add_argument('candidate',type=Path)
p.add_argument('--baseline',type=Path,required=True)
p.add_argument('--corpus',type=Path,required=True)
p.add_argument('--before',type=Path,required=True)
p.add_argument('--after',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
new=validate(a.candidate,a.corpus)
old=validate(a.baseline,a.corpus)
assert new['intervals']==old['intervals']==624

def rows(path):
    return list(csv.DictReader(x for x in path.read_text().splitlines() if not x.startswith('#')))

def probe_failures(path):
    # Keep exact failure records: case/route/repeat must not quietly change.
    return [x for x in path.read_text().splitlines() if x.startswith('# probe,') and x.endswith('match=0')]

assert probe_failures(a.candidate)==probe_failures(a.baseline), 'Changed pixel outcomes'
before=json.loads(a.before.read_text())
after=json.loads(a.after.read_text())
snapshot=lambda x:next(p['count'] for p in x['phases'] if p['name']=='snapshot')
assert snapshot(after)-snapshot(before)==0, 'P4 snapshot work occurred'
candidates,baselines=rows(a.candidate),rows(a.baseline)

def median(data,name,route,metric,field='value'):
    selected=[r for r in data if r['case']==name and int(r['route'])==route and
              r['detail']=='1' and r['phase']=='draw' and int(r['metric'])==metric]
    assert len(selected)==3
    return statistics.median(int(r[field]) for r in selected)

records=[]
for case in json.loads(a.corpus.read_text())['cases']:
    r=dict(case=case['name'],bytes=case['bytes'],upload_bytes=case['upload_bytes'])
    for metric,name in ((1,'elapsed'),(2,'primitive'),(4,'software_sprite')):
        for data,route,label in ((candidates,0,'vdp'),(candidates,1,'edp'),(baselines,1,'prior_edp')):
            r[label+'_'+name+'_ms']=median(data,case['name'],route,metric)/1000
            r[label+'_'+name+'_count']=median(data,case['name'],route,metric,'count')
    records.append(r)

lines=['# Graphics workload after stock UART alignment','',
       f"All624intervals complete; {new['probe_mismatches']} unchanged baseline probe mismatches; zero P4 snapshots.",'',
       'Mode20,512×384,64colours,singlebuffered. Medians of three enabled draw',
       'intervals, in milliseconds. Positive percentages mean more time; negative',
       'means less. Each table is sorted by largest current EDP time. Stock VDP',
       'is the main comparison baseline; the final column compares EDP against',
       'its own earlier unchanged-UART run. This is not game FPS or video output.',
       'Mainboard VGA remains active. Instrumentation/fences are not free.','']

def table(title,items,scope,description):
    lines.extend(['## '+title,'',description,'',
                  '| Case | VDP ms | EDP ms | EDP vs VDP | Prior EDP ms | EDP vs prior |',
                  '| --- | ---: | ---: | ---: | ---: | ---: |'])
    for r in sorted(items,key=lambda r:r['edp_'+scope+'_ms'],reverse=True):
        v,e,b=(r[x+'_'+scope+'_ms'] for x in ('vdp','edp','prior_edp'))
        pct=lambda value,base:f'{100*(value/base-1):+.1f}%' if base else 'n/a'
        lines.append(f"| {r['case']} | {v:.3f} | {e:.3f} | {pct(e,v)} | {b:.3f} | {pct(e,b)} |")
    lines.append('')

table('Upload-heavy stage elapsed time',[r for r in records if r['upload_bytes']], 'elapsed',
      'These stages include arriving bytes, command handling, asset creation and\n'
      'their drawing/completion work. They are not isolated bitmap creation or\n'
      'SD loading times. Stage byte counts are retained in the adjacent JSON.')
primitive_names=('BSP03_01','BSP07_02','SHP23','SHP20','BSP07_03','COMBINED','SCROLL','CLIPROW')
primitive=[r for r in records if r['case'] in primitive_names]
assert all(r['vdp_primitive_count']==r['edp_primitive_count'] for r in primitive)
table('Native primitive rendering',primitive,'primitive',
      'Matching primitive counts. Includes state/text work present in each scene;\n'
      'excludes incoming-stream waits. SCROLL,CLIPROW,COMBINED each contain64\n'
      'repeated operations; these rows show the complete batch, not one plot.')
sprites=[r for r in records if r['vdp_software_sprite_count']==r['edp_software_sprite_count'] and
         max(r['vdp_software_sprite_ms'],r['edp_software_sprite_ms'])>=.05]
table('Software sprite processing',sprites,'software_sprite',
      'Matching showSprites call counts; complete scopes include background save\n'
      'and redraw. Rows below0.05ms on both devices are omitted for readability.\n'
      'These scopes overlap native primitive timing: do not add them.')
unequal=[r for r in records if r['vdp_software_sprite_count']!=r['edp_software_sprite_count']]
lines.extend(['Stages with unequal software-sprite call counts are excluded from that',
              'table; draining batches can call showSprites at different frequencies.',
              'Their measured totals and counts remain in the adjacent JSON:',
              ', '.join(r['case'] for r in unequal)+'.',''])
lines.extend(['Hardware-sprite scanline decoration has unequal output demand in this',
              'browser-disconnected test and is intentionally not ranked as a renderer',
              'speed comparison. Primitive durations are instrumented scopes, not',
              'exclusive processor-cycle counts. No renderer was changed in this run.',''])
a.output.write_text('\n'.join(lines))
a.output.with_suffix('.json').write_text(json.dumps(dict(intervals=624,probe_mismatches=new['probe_mismatches'],
    snapshot_delta=0,records=records),indent=2)+'\n')
print('Validated paired graphics comparison written:',a.output)
