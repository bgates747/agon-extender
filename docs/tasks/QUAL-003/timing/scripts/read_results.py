#!/usr/bin/env python3
"""Validate the complete durable case sequence before comparing any timings.

Use --review only for the shortened native functional profile. Native times
are not hardware performance measurements. Partial CSV files remain evidence
but never produce an accepted comparison.
"""
import argparse,csv,json,re,statistics
from collections import defaultdict
from pathlib import Path

def validate(path,corpus,review=False):
    text=path.read_text();lines=text.splitlines()
    terminal=re.fullmatch(r'# terminal,status=(\d+),saved=(\d+),probe_mismatches=(\d+),phase=(\w+)',lines[-1])
    if not terminal:raise ValueError('Missing terminal result: incomplete capture')
    status,saved,mismatches=map(int,terminal.groups()[:3])
    if status:raise ValueError(f'Application failed with status {status}; retain partial results')
    cases=json.loads(corpus.read_text())['cases']
    by_name={case['name']:case for case in cases}
    expected=[(rep,route,int(review or rep!=0),case['name'],phase)
              for rep in range(1 if review else 4) for route in range(2)
              for case in cases for phase in ('draw','output')]
    rows=list(csv.DictReader(s for s in lines if not s.startswith('#')))
    if saved!=len(expected) or len(rows)!=saved*8:raise ValueError('Interval/metric count differs from contract')
    grouped=defaultdict(list)
    for i,key in enumerate(expected):
        block=rows[i*8:(i+1)*8]
        for metric,row in enumerate(block,1):
            actual=(int(row['repeat']),int(row['route']),int(row['detail']),row['case'],row['phase'])
            if actual!=key or int(row['metric'])!=metric or int(row['status']):
                raise ValueError(f'Unexpected, missing or failed record at row {i*8+metric}')
            for field in ('send_ticks','reply_ticks','bytes','upload_bytes'):
                if row[field]!=block[0][field]:raise ValueError('Inconsistent interval metadata')
            if int(row['upload_bytes'])>int(row['bytes']):raise ValueError('Upload count exceeds stage')
            source=by_name[key[3]]
            if int(row['bytes'])!=source['bytes'] or int(row['upload_bytes'])!=source['upload_bytes']:
                raise ValueError('Stage byte counts differ from the identified corpus')
            if not key[2] and 2<=metric<=7 and (int(row['value']) or int(row['count'])):
                raise ValueError('Disabled instrumentation recorded operation durations')
            if metric==8 and int(row['count'])!=256:raise ValueError('Missing timer-overhead control')
            grouped[(key[1],key[2],key[3],key[4],metric)].append((int(row['value']),int(row['count'])))
    probes=[line for line in lines if line.startswith('# probe,')]
    if sum(line.endswith('match=0') for line in probes)!=mismatches:raise ValueError('Probe mismatch count differs')
    return dict(scope='Native functional review only' if review else 'Physical comparison; attach exact image and run identities',
                intervals=saved,probe_mismatches=mismatches,metrics=[
                dict(route=k[0],detail=k[1],case=k[2],phase=k[3],metric=k[4],
                     median_value=statistics.median(v[0] for v in samples),
                     median_count=statistics.median(v[1] for v in samples),samples=len(samples))
                for k,samples in grouped.items()])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv',type=Path)
    p.add_argument('--corpus',type=Path,default=Path(__file__).resolve().parents[1]/'fixture/build/corpus.json')
    p.add_argument('--review',action='store_true');p.add_argument('--output',type=Path)
    a=p.parse_args();result=validate(a.csv,a.corpus,a.review)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(f"Complete: {result['intervals']} intervals; {result['probe_mismatches']} recorded probe differences. {result['scope']}.")
