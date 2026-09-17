"""Aggregate identical-frame desktop controls; never label them P4 measurements."""
import argparse,json,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args()
runs=[json.loads(f.read_text()) for f in sorted(a.run.glob('replay*/results.json'))]
assert len(runs)>=2
cases={r['case'] for r in runs[0]};rows=[]
for name in cases:
 variants={}
 for codec in ('raw','rle2','srle2'):
  values=[r for run in runs for r in run if r['case']==name and r['codec']==codec]
  assert len(values)==len(runs) and all(r['exact'] for r in values)
  samples=[x for v in values for x in v['samples']['decode'][2:]]
  variants[codec]=dict(message_bytes=values[0]['message_bytes'],samples=len(samples),decode_parse_ms=statistics.mean(x['totalMs']+x['parseMs'] for x in samples),szip_ms=statistics.mean(x['szipMs'] for x in samples),rle_ms=statistics.mean(x['rleMs'] for x in samples),parse_ms=statistics.mean(x['parseMs'] for x in samples),submit_ms=statistics.mean(x for v in values for x in v['samples']['submit'][2:]),receive_interval_ms=statistics.mean(v['receive_interval_ms']['mean'] for v in values),first_decode_ms=[v['samples']['decode'][0]['totalMs'] for v in values])
 rows.append(dict(case=name,variants=variants))
rows.sort(key=lambda r:r['variants']['srle2']['decode_parse_ms'],reverse=True)
(a.run/'comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['# Repeated Linux/browser comparisons','',f'Exact pixels passed on {len(cases)} fixtures × 3 formats × {len(runs)} repetitions. First two frames per run are excluded from steady means. Ranked by worst SRLE2 decode cost.','', '| Fixture | Raw bytes | RLE2 bytes | SRLE2 bytes | SRLE2 vs RLE2 bytes | Raw decode/parse ms | RLE2 decode/parse ms | SRLE2 decode/parse ms |','|---|---:|---:|---:|---:|---:|---:|---:|']
for row in rows:
 v=row['variants'];r,l,s=(v[x] for x in ('raw','rle2','srle2'))
 lines.append(f"| {row['case']} | {r['message_bytes']} | {l['message_bytes']} | {s['message_bytes']} | {(s['message_bytes']/l['message_bytes']-1)*100:+.1f}% | {r['decode_parse_ms']:.3f} | {l['decode_parse_ms']:.3f} | {s['decode_parse_ms']:.3f} |")
lines+=['','## SRLE2 stage detail','','| Fixture | Szip ms | RLE2 expansion ms | Final parse ms | Presenter submission ms | Receive interval ms |','|---|---:|---:|---:|---:|---:|']
for row in rows:
 s=row['variants']['srle2'];lines.append(f"| {row['case']} | {s['szip_ms']:.3f} | {s['rle_ms']:.3f} | {s['parse_ms']:.3f} | {s['submit_ms']:.3f} | {s['receive_interval_ms']:.2f} |")
lines+=['','All timing is headless Chromium on Linux over localhost. It measures neither P4 encode/render/transport cost nor physical display refresh. Frames are credit paced at at most30Hz. GPU palette conversion is part of presenter submission; submission does not wait for GPU completion. Fixed WebAssembly memory reservation is64MiB, not measured live allocation high-water. Original codec invocation allocation budget is12MiB cumulative. First-frame module initialization costs are retained in comparison.json, separately from steady means. Raw and RLE2 use the existing main-thread parser; SRLE2 decoding/expansion runs in a Worker, so scheduler/IPC overhead is not isolated by these inner-operation timings.']
(a.run/'TABLES.md').write_text('\n'.join(lines)+'\n')
