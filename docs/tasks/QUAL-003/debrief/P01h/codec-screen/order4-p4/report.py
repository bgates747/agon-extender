"""Summarize matched P4 evidence after complete acquisition; no hardware access."""
from pathlib import Path
import json,statistics,argparse
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args();root=Path(__file__).resolve().parent;e=root/'evidence';e.mkdir(exist_ok=True)
game=json.loads((a.run/'game01/analysis.json').read_text());rows=[]
for codec,names in [('RLE2',['rle1','rle2','rle3']),('SRLE2 order3',['srle1','srle2','srle3']),('SRLE2 order4',['o4a','o4b','o4c'])]:
 trials=[]
 for n in names:
  x=game[n];c=x['codec_counters'];trials.append(dict(name=n,application_hz=x['application']['intervals']['effective_fps'],browser_fps=x['browser']['intervals']['effective_fps'],submitted_fps=x['browser']['submission_intervals']['effective_fps'],bytes=x['browser']['mean_bytes'],rle_ms=c['rle2_us']/max(1,c['rle2_attempts'])/1000,entropy_ms=c['srle2_us']/max(1,c['srle2_attempts'])/1000,failures=c['srle2_failures']))
 rows.append(dict(codec=codec,mean={k:statistics.mean(t[k] for t in trials) for k in trials[0] if k!='name'},trials=trials))
(e/'game-summary.json').write_text(json.dumps(rows,indent=2)+'\n');(e/'game-analysis.json').write_text(json.dumps(game,indent=2)+'\n')
lines=['# Matched P4 order4 results','','## Fixed-mode Nurples, three trials each','','Browser central15-second window per trial, excluding startup/completion. Bytes include frame/codec headers. Codec timing counters span the complete invocation, so their scope differs from the central output window. Baseline is RLE2.','','| Codec | App cycles/s | Received fps | vs RLE2 | Submitted fps | Bytes/frame | RLE2 stage ms | Extra szip ms |','|---|---:|---:|---:|---:|---:|---:|---:|']
b=rows[0]['mean']
for x in rows:
 m=x['mean'];lines.append(f"| {x['codec']} | {m['application_hz']:.2f} | {m['browser_fps']:.2f} | {(m['browser_fps']/b['browser_fps']-1)*100:+.1f}% | {m['submitted_fps']:.2f} | {m['bytes']:.0f} | {m['rle_ms']:.3f} | {m['entropy_ms']:.3f} |")
lines+=['','## Exact device encoder RPC','','Input is already RLE2 encoded; this table measures only the additional szip stage. One warmup plus three measured calls; no browser connected.','','| Case | Order3 ms | Order4 ms | Time difference | Order3 bytes | Order4 bytes |','|---|---:|---:|---:|---:|---:|']
r3=json.loads((a.run/'codec3/results.json').read_text());r4=json.loads((a.run/'codec4/results.json').read_text())
for x in sorted([x for x in r3 if x['operation']=='encode'],key=lambda x:x['steady_codec_us'],reverse=True):
 y=next(y for y in r4 if y['case']==x['case'] and y['operation']=='encode4');lines.append(f"| {x['case']} | {x['steady_codec_us']/1000:.3f} | {y['steady_codec_us']/1000:.3f} | {(y['steady_codec_us']/x['steady_codec_us']-1)*100:+.1f}% | {x['output_bytes']} | {y['output_bytes']} |")
for order in [3,4]:(e/f'codec{order}.json').write_bytes((a.run/f'codec{order}/results.json').read_bytes())
s=json.loads((a.run/'synthetic02/results.json').read_text());compact=[];lines+=['','## Static scenes, same512×384 mode','','Twenty receipts per codec; one trial. Excludes first two intervals from receipt rate. Not a game or application-cycle measurement.','','| Scene | Codec | Received fps | Bytes/frame | Extra szip ms |','|---|---|---:|---:|---:|']
for x in s:
 f=x['frames'][2:];fps=(len(f)-1)*1000/(f[-1]['ms']-f[0]['ms']);n=x['after']['srle2_attempts']-x['before']['srle2_attempts'];ms=(x['after']['srle2_us']-x['before']['srle2_us'])/max(1,n)/1000;meanbytes=statistics.mean(f['bytes'] for f in f);lines.append(f"| {x['scene']} | {x['codec']} | {fps:.2f} | {meanbytes:.0f} | {ms:.3f} |");compact.append(dict(scene=x['scene'],codec=x['codec'],fps=fps,bytes=meanbytes,entropy_ms=ms,errors=x['errors']))
(e/'static-summary.json').write_text(json.dumps(compact,indent=2)+'\n');(root/'TABLES.md').write_text('\n'.join(lines)+'\n');print(json.dumps(rows,indent=2))
