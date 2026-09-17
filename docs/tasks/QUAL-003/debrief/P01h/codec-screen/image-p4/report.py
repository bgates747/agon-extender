from pathlib import Path
import argparse,json,statistics,collections
p=argparse.ArgumentParser();p.add_argument('private',type=Path);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'evidence';out.mkdir(exist_ok=True);lines=['# Matched physical image-codec tables','','## Game delivery','','Central15-second browser receipt window, ending5 seconds before final receipt.','All runs use clean identical mode20 startup,512×384 source, application cadence60','and30Hz browser request cap. Counters cover whole invocation, a different scope.','','| Phase / codec | Received fps mean (range) | Change vs paired RLE2 | Mean wire bytes/frame | Validate/expand ms | Encode ms | Application cycles/s |','|---|---:|---:|---:|---:|---:|---:|'];summary=[]
for phase in ['jpeg','png']:
 run=a.private/(phase+'-game05');data=json.loads((run/'analysis.json').read_text());(out/(phase+'-game.json')).write_text(json.dumps(data,indent=2));groups=collections.defaultdict(list)
 for name,x in data.items():
  key='RLE2' if name.startswith('rle') else 'JPEG90 RGB888 444' if name.startswith('j') else 'PNG level1' if name.startswith('p1') else 'PNG level3';c=x['codec_counters'];n=c['attempts'];nr=c['rle2_attempts'];groups[key].append(dict(fps=x['browser']['intervals']['effective_fps'],bytes=x['browser']['mean_bytes'],convert_ms=c['convert_us']/n/1000 if n else 0,encode_ms=c['encode_us']/n/1000 if n else c['rle2_us']/nr/1000,cycles=x['application']['intervals']['effective_fps'],failures=c['failures'],magic=x['browser']['magic']))
 base=statistics.mean(x['fps'] for x in groups['RLE2'])
 for name,rows in groups.items():
  avg={k:statistics.mean(x[k] for x in rows) for k in ['fps','bytes','convert_ms','encode_ms','cycles']};fps=[x['fps'] for x in rows];pct=(avg['fps']/base-1)*100
  lines.append(f"| {phase} / {name} | {avg['fps']:.2f} ({min(fps):.2f}–{max(fps):.2f}) | {pct:+.1f}% | {avg['bytes']:,.0f} | {avg['convert_ms']:.3f} | {avg['encode_ms']:.3f} | {avg['cycles']:.2f} |")
  summary.append(dict(phase=phase,codec=name,mean=avg,percent_vs_rle=pct,trials=rows))
(out/'summary.json').write_text(json.dumps(summary,indent=2))
lines+=['','## Static completed scenes','','20 receipts per condition; discard first2; one run per condition. These are','snapshot delivery rates, not changing-game FPS. Encoder counters cover entire','condition; baseline is same-scene RLE2.','','| Scene / codec | Receipt fps | vs RLE2 | Wire bytes/frame | Validate/expand ms | Encode ms |','|---|---:|---:|---:|---:|---:|']
rows=json.loads((a.private/'synthetic01/results.json').read_text());(out/'static.json').write_text(json.dumps(rows,indent=2));base={}
for x in rows:
 f=x['frames'][2:];fps=(len(f)-1)*1000/(f[-1]['ms']-f[0]['ms']);scene=x['scene'];codec=x['codec'];c={k:x['after'][k]-x['before'][k] for k in x['before'] if k!='stack_min_bytes'};n=c['attempts'];nr=c['rle2_attempts'];conv=c['convert_us']/n/1000 if n else 0;enc=c['encode_us']/n/1000 if n else c['rle2_us']/nr/1000
 if codec=='rle2':base[scene]=fps
 lines.append(f"| {scene} / {codec} | {fps:.2f} | {(fps/base[scene]-1)*100:+.1f}% | {statistics.mean(y['bytes'] for y in f):,.0f} | {conv:.3f} | {enc:.3f} |")
(root/'TABLES.md').write_text('\n'.join(lines)+'\n')
