#!/usr/bin/env python3
"""Compare post-capture renderer serial records with the exact SD CSV."""
import argparse,csv,json,re
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--serial',type=Path,required=True);p.add_argument('csv',type=Path);a=p.parse_args()
groups=[];group=[]
for line in a.serial.read_text(errors='replace').splitlines():
 m=re.search(r'GT1,(\d+),(\d+),(\d+),(\d+)$',line)
 if not m:continue
 row=list(map(int,m.groups()))
 if row[0]==0:
  if group:groups.append(group)
  group=[]
 group.append(row)
if group:groups.append(group)
with a.csv.open() as f:
 rows=list(csv.DictReader(f))
if not rows or any(int(row['source']) not in (0,1) for row in rows):raise SystemExit('No renderer measurement in CSV')
wanted=[[int(r[k]) for k in ['frame','submitted_us','completed_us','drain_us']] for r in rows]
match=[i for i,g in enumerate(groups) if g==wanted]
if not match:raise SystemExit('No exact serial group matches SD records')
print(json.dumps({'rows':len(wanted),'exact_match':True,'matching_groups':match}))
