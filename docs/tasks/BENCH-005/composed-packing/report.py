from pathlib import Path
import json,statistics,argparse
p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);a=p.parse_args();T=Path('docs/tasks/BENCH-005/composed-packing');rows=[];exceptions=[]
for run in a.runs:
 for modepath in sorted(run.iterdir()):
  if not modepath.is_dir() or not (modepath/'progress.json').exists():continue
  progress=json.loads((modepath/'progress.json').read_text());m=progress['mode']
  if (modepath/'restart-exception.json').exists():exceptions.append(dict(mode=m['mode'],kind='P4 restart on transition; one reset retry'))
  for activity in ['static','dense','moving']:
   file=modepath/activity/'samples.json'
   if not file.exists():continue
   trials=json.loads(file.read_text());row={'mode':m,'activity':activity,'status':progress['state'],'trials':[]}
   for trial in trials:
    summary={k:trial[k] for k in ['label','frames','fps','mean_bytes','decode_ms','interval_p95_ms','errors']}
    summary['wire_formats']=sorted(set(s['magic'] for s in trial['samples']))
    if 'before_counters' in trial:
     before={v['name']:v for v in trial['before_counters']['phases']};times={}
     for end in trial['after_counters']['phases']:
      start=before[end['name']];n=end['count']-start['count'];times[end['name']]=(end['total_us']-start['total_us'])/n/1000 if n>0 else None
     summary['phase_mean_ms']=times
    row['trials'].append(summary)
   if activity!='moving':
    files=[(modepath/activity/(name+'.rgb222')).read_bytes() for name in ['raw','rle2','packed','auto']];row['identical_pixels']=all(x==files[0] for x in files);row['distinct_colours']=len(set(files[0]))
   rows.append(row)
(T/'SUMMARY.json').write_text(json.dumps(dict(rows=rows,exceptions=exceptions),indent=2)+'\n')
lines=['# Composed packing — hardware results','','## Executive summary','','Results are provisional until all requested modes and exceptions are reviewed. Final-colour packing preserves composition; measured performance depends on image entropy. RLE2 is the baseline below, with its size limit corrected for all supported resolutions.','','## Matched browser presentation submissions','','Each trial uses the same candidate, compositor, host and60Hz request cap. These are headless Chromium presentation submissions, not physical display refresh or game simulation fps. Static and dense cases compare decoded images exactly. Moving cases measure output during deterministic drawing; images differ in time and are not compared bytewise.','','| Mode | Scene | RLE2 fps | Packed fps | Auto fps | Auto vs RLE2 | RLE2 bytes | Packed bytes | Auto bytes |','|---:|---|---:|---:|---:|---:|---:|---:|---:|']
for row in sorted(rows,key=lambda r:next(x['fps'] for x in r['trials'] if x['label']=='auto')):
 d={t['label']:t for t in row['trials']};base=d['rle2'];auto=d['auto'];pack=d['packed'];pct=(auto['fps']/base['fps']-1)*100 if base['fps'] else 0
 lines.append(f"| {row['mode']['mode']} | {row['activity']} | {base['fps']:.2f} | {pack['fps']:.2f} | {auto['fps']:.2f} | {pct:+.1f}% | {base['mean_bytes']:.0f} | {pack['mean_bytes']:.0f} | {auto['mean_bytes']:.0f} |")
lines+=['','Ranked slowest automatic output first. Percentage is throughput change relative to RLE2-only; positive is faster. Payload bytes include transport frame headers, not TCP/Ethernet overhead. See SUMMARY.json for sample counts, p95 intervals, decoder milliseconds, and snapshot/socket phase milliseconds. Socket phase includes encoding: it is not pure wire time. The timing counter windows include warmup, whereas fps excludes it.','', '## Exceptions', '']
lines += [f"1. Mode {e['mode']}: {e['kind']}." for e in exceptions] or ['None recorded in these run directories.']
(T/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print(len(rows),'mode/scene comparisons,',len(exceptions),'transition exceptions')
