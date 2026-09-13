#!/usr/bin/env python3
"""Validate durable UART results before comparing any timing; no hardware I/O."""
import argparse,csv,json,re,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('csv',type=Path);mode=p.add_mutually_exclusive_group();mode.add_argument('--smoke',action='store_true');mode.add_argument('--duplex',action='store_true');mode.add_argument('--wire',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
lines=a.csv.read_text().splitlines();rows=list(csv.DictReader(l for l in lines if not l.startswith('#')))
end=re.fullmatch(r'# terminal,status=(\d+),saved=(\d+),recovery=(\d+)',lines[-1]);errors=[]
if not end:errors.append('Missing terminal record')
else:
 status,saved,recovery=map(int,end.groups())
 if saved!=len(rows):errors.append('Saved count differs')
 if status or recovery:errors.append(f'Terminal status={status}, recovery={recovery}')
lengths=[0,257,65535] if a.smoke else [0,1,63,64,65,255,256,257,4095,4096,4097,32768,65535]
expected=[]
if a.wire:
 for direction,n in (('forward',65535),('reverse',256)):
  for route in range(2):expected.append((direction,route,0,3,n))
elif a.duplex:
 for route in range(2):
  for repeat in range(3):
   for n in (257,4096,65535):expected.extend([('duplex-forward',route,repeat,3,n),('duplex-reverse',route,repeat,3,256)])
else:
 for direction in ('forward','reverse'):
  for route in range(2):
   for repeat in range(1 if a.smoke else 3):
    for pattern in (range(4) if direction=='forward' else [3]):
     for n in (lengths if direction=='forward' else [1,8,64,256]):expected.append((direction,route,repeat,pattern,n))
if len(rows)!=len(expected):errors.append(f'Expected {len(expected)} rows; got {len(rows)}')
for i,r in enumerate(rows):
 key=(r['direction'],int(r['route']),int(r['repeat']),int(r['pattern']),int(r['length']))
 if i>=len(expected) or key!=expected[i]:errors.append(f'Unexpected sequence at row{i}')
 n=key[-1]*(8 if key[0] in ('reverse','duplex-reverse') else 1)
 if int(r['expected_bytes'])!=n or int(r['actual_bytes'])!=n or int(r['errors']) or int(r['status']):errors.append(f'Integrity/status failure at row{i}')
summary={'complete':not errors,'rows':len(rows),'errors':errors,'comparison':[]}
if not errors:
 for direction in (('duplex-forward','duplex-reverse') if a.duplex else ('forward','reverse')):
  for n in (([65535] if a.wire else ([257,4096,65535] if a.duplex else lengths)) if direction.endswith('forward') else ([256] if a.duplex or a.wire else [1,8,64,256])):
   entry={'direction':direction,'length':n}
   for route,label in ((0,'vdp'),(1,'edp')):
    r=[r for r in rows if r['direction']==direction and int(r['route'])==route and int(r['length'])==n]
    entry[label]={k:statistics.median(int(v[k]) for v in r) for k in ('send_ticks','reply_ticks','elapsed_us')}
   summary['comparison'].append(entry)
if a.output:a.output.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
raise SystemExit(bool(errors))
