"""Retain compact evidence and comparison tables; no hardware access."""
import argparse,json,csv,statistics,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--browser',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=True)
paired=json.loads((a.browser/'paired.json').read_text());shutil.copy(a.browser/'paired.json',a.out/'paired.json')
native=json.loads((a.native/'results.json').read_text());web=json.loads((a.browser/'results.json').read_text());selected=json.loads((a.browser/'selected.json').read_text());base=next(r for r in native if r['case']=='retained-sprites' and r['variant']=='rle2')
with (a.out/'native.csv').open('w') as f:
 keys=['case','variant','kind','exact','failure','bytes','encode_ms','original_cli_exact','sha256'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(native)
compact=[{k:v for k,v in r.items() if k!='samples'} for r in web];(a.out/'browser.json').write_text(json.dumps(compact,indent=2)+'\n')
for source,name in [(a.native/'complete.json','native-run.json'),(a.browser/'complete.json','browser-run.json'),(a.browser/'edges.json','edges.json'),(a.browser/'selected.json','selected.json')]:shutil.copy(source,a.out/name)
lines=['# Codec screening tables','', '## Captured 512×384 sprite scene','', 'Sorted by encoded size, largest first. Byte counts include codec headers but exclude the common32-byte EVC1 envelope. RLE2 is the baseline. Encode is native Linux median of20 paired samples (alternating candidate/RLE2 order); decode is browser processing excluding PNG verification/readback. Submission is CPU time issuing WebGL commands, not completed display.','', '| Variant | Bytes | Size vs RLE2 | Linux encode ms | Encode vs paired RLE2 | Browser decode ms | Submit ms |','|---|---:|---:|---:|---:|---:|---:|']
rows=[r for r in native if r['case']=='retained-sprites' and r['variant'] in {v['id'] for v in selected}]
for r in sorted(rows,key=lambda r:r['bytes'],reverse=True):
 timing=next(t for t in paired['rows'] if t['case']==r['case'] and t['variant']==r['variant'])
 b=next(b for b in web if b['phase']=='exact' and b['variant']==r['variant'] and b['cases']==['retained-sprites']);lines.append(f"| {r['variant']} | {r['bytes']} | {(r['bytes']/base['bytes']-1)*100:+.1f}% | {timing['encode_ms']:.3f} | {timing['delta_pct']:+.1f}% | {b['decode_ms']:.3f} | {b['submit_ms']:.3f} |")
lines+=['','## 30 Hz mixed full-size replay','', 'These are pre-encoded loopback frames, not P4/network/application fps. First two samples excluded. Includes synthetic noise and the captured scene. No correctness readback in this pass.','', '| Variant | Submitted fps | FPS vs RLE2 | Decode wall ms | Submit ms |','|---|---:|---:|---:|---:|']
paced=[r for r in web if r['phase']=='paced'];bf=next(r['fps'] for r in paced if r['variant']=='rle2')
for r in sorted(paced,key=lambda r:r['fps']):lines.append(f"| {r['variant']} | {r['fps']:.2f} | {(r['fps']/bf-1)*100:+.1f}% | {r['decode_wall_ms']:.3f} | {r['submit_ms']:.3f} |")
lines+=['','## Native exclusions','', '| Reason | Cases/settings |','|---|---:|']
from collections import Counter
for reason,n in Counter(r['failure'] for r in native if not r['exact']).items():lines.append(f'| {reason} | {n} |')
lines+=['','## Slowest completed native encodes','', '| Case | Variant | Encode ms |','|---|---|---:|']
for r in sorted([r for r in native if r['encode_ms'] is not None],key=lambda r:r['encode_ms'],reverse=True)[:12]:lines.append(f"| {r['case']} | {r['variant']} | {r['encode_ms']:.3f} |")
(a.out.parent/'TABLES.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(native_rows=len(native),exact=sum(r['exact'] for r in native),excluded=sum(not r['exact'] for r in native),browser_rows=len(web),selected=len(selected)),indent=2))
