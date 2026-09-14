#!/usr/bin/env python3
"""Check the separately frozen E07P reverse batch scope, never enqueue time."""
import argparse,csv,json,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('csv',type=Path);p.add_argument('--transfers',type=int,choices=[16,31,128],default=16);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
transfers=a.transfers;useful=transfers*2048
lines=a.csv.read_text().splitlines();rows=list(csv.DictReader(l for l in lines if not l.startswith('#')))
assert len(rows)==12 and lines[-1]=='# terminal,status=0,saved=12,recovery=0'
seen=set();samples={0:[],1:[]}
for r in rows:
 key=(int(r['repeat']),int(r['route']));assert key not in seen and key[0] in range(6) and key[1] in (0,1);seen.add(key)
 assert r['direction']=='reverse-batch' and r['pattern']=='3' and r['length']=='256'
 assert r['expected_bytes']==r['actual_bytes']==str(useful) and r['errors']==r['status']=='0'
 assert r['send_ticks']==r['elapsed_us']=='0'
 ticks=int(r['reply_ticks']);assert ticks>0 and ticks%2==0
 samples[key[1]].append(ticks*1000/120/transfers)
uncertainty=1000/60/transfers
summary={'scope':f'{transfers} repeated 256-packet end-to-end returns; includes equal request/arming/mailbox-copy work, excludes verification/SD/output',
 'rows':12,'exact_useful_bytes':12*useful,'clock_units_per_vblank':2,'vblank_hz':60,'transfers_per_interval':transfers,
 'per_transfer_uncertainty_ms':uncertainty,'routes':{}}
for route,v in samples.items():
 m=statistics.median(v);summary['routes'][str(route)]={'samples_ms':v,'median_ms':m,'min_ms':min(v),'max_ms':max(v),'median_lower_ms':m-uncertainty,'median_upper_ms':m+uncertainty}
b=summary['routes']['0'];c=summary['routes']['1'];summary['elapsed_difference_percent']=(c['median_ms']/b['median_ms']-1)*100
summary['conservative_parity_pass']=c['median_upper_ms']<=b['median_lower_ms']
a.output.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
