from pathlib import Path
import json,statistics,argparse
p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);a=p.parse_args();T=Path('docs/tasks/BENCH-005/composed-packing');rows=[];exceptions=[];durations=[]
for run in a.runs:
 for modepath in sorted(run.iterdir()):
  if not modepath.is_dir() or not (modepath/'progress.json').exists():continue
  progress=json.loads((modepath/'progress.json').read_text());m=progress['mode']
  if progress['state']!='pass':continue
  durations.append({'mode':m['mode'],'seconds':progress['end']-progress['start']})
  if (modepath/'restart-exception.json').exists():exceptions.append(dict(mode=m['mode'],kind='P4 restart on transition; one reset retry'))
  for activity in ['static','dense','moving']:
   file=modepath/activity/'samples.json'
   if not file.exists():continue
   trials=json.loads(file.read_text());row={'mode':m,'activity':activity,'status':progress['state'],'trials':[]}
   for trial in trials:
    summary={k:trial[k] for k in ['label','frames','fps','mean_bytes','decode_ms','interval_p95_ms','errors']}
    summary['wire_formats']=sorted(set(s['magic'] for s in trial['samples']))
    if 'before_counters' in trial:
     bc=trial['before_counters'];ac=trial['after_counters']
     summary['timing_valid']=bool(bc['totals_valid'] and ac['totals_valid'] and bc['lost_completions']==ac['lost_completions'] and bc['overlapping_calls']==ac['overlapping_calls'])
     before={v['name']:v for v in trial['before_counters']['phases']};times={}
     for end in trial['after_counters']['phases']:
      start=before[end['name']];n=end['count']-start['count'];times[end['name']]=(end['total_us']-start['total_us'])/n/1000 if n>0 else None
     summary['phase_mean_ms']=times if summary['timing_valid'] else {}
    row['trials'].append(summary)
   if activity!='moving':
    files=[(modepath/activity/(name+'.rgb222')).read_bytes() for name in ['raw','rle2','packed','auto']];row['identical_pixels']=all(x==files[0] for x in files);row['distinct_colours']=len(set(files[0]))
   rows.append(row)
(T/'SUMMARY.json').write_text(json.dumps(dict(rows=rows,exceptions=exceptions,durations=durations),indent=2)+'\n')
lines=['# Composed packing — hardware results','','## Executive summary','','Results are provisional until all requested modes and exceptions are reviewed. Final-colour packing preserves composition; measured performance depends on image entropy. RLE2 is the baseline below, with its size limit corrected for all supported resolutions.','','## Matched browser presentation submissions','','Each trial uses the same candidate, compositor, host and60Hz request cap. These are headless Chromium presentation submissions, not physical display refresh or game simulation fps. Static and dense cases compare decoded images exactly against the same P4 compositor without compression. This qualifies wire preservation, not new stock-mainboard pixel parity. Moving cases measure output during deterministic drawing; images differ in time and are not compared bytewise.','','| Mode | Scene | RLE2 fps | Packed fps | Auto fps | Auto vs RLE2 | RLE2 bytes | Packed bytes | Auto bytes |','|---:|---|---:|---:|---:|---:|---:|---:|---:|']
for row in sorted(rows,key=lambda r:next(x['fps'] for x in r['trials'] if x['label']=='auto')):
 d={t['label']:t for t in row['trials']};base=d['rle2'];auto=d['auto'];pack=d['packed'];pct=(auto['fps']/base['fps']-1)*100 if base['fps'] else 0
 lines.append(f"| {row['mode']['mode']} | {row['activity']} | {base['fps']:.2f} | {pack['fps']:.2f} | {auto['fps']:.2f} | {pct:+.1f}% | {base['mean_bytes']:.0f} | {pack['mean_bytes']:.0f} | {auto['mean_bytes']:.0f} |")
lines+=['','Ranked slowest automatic output first. Percentage is throughput change relative to RLE2-only; positive is faster. Payload bytes include transport frame headers, not TCP/Ethernet overhead. See SUMMARY.json for sample counts, p95 intervals, decoder milliseconds, and snapshot/socket phase milliseconds. Socket phase includes encoding: it is not pure wire time. The timing counter windows include warmup, whereas fps excludes it.','', '## Exceptions', '']
lines += [f"1. Mode {e['mode']}: {e['kind']}." for e in exceptions] or ['None recorded in these run directories.']
(T/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print(len(rows),'mode/scene comparisons,',len(exceptions),'transition exceptions')

# Keep detailed timing separate from throughput: these counters are overlapping
# pipeline phases, not additive pieces of the browser frame interval.
lines += ['', '## Automatic path timing by mode and workload', '',
 'Mean milliseconds per observed operation. Snapshot is composition/copy; socket includes encoding and send API time. Credit-to-ready and ready-to-send are pipeline latency counters, not extra work to add to those means. Counter windows include the one-second warmup. Timing means are withheld if recorder loss or overlap increases during that window; browser throughput remains independently measured. Browser decode is measured after warmup. Sorted by lowest automatic fps first.', '',
 '| Mode | Scene | Samples | Snapshot ms | Socket/encode ms | Credit→ready ms | Ready→send ms | Decode ms | p95 presentation interval ms |',
 '|---:|---|---:|---:|---:|---:|---:|---:|---:|']
for row in sorted(rows,key=lambda r:next(x['fps'] for x in r['trials'] if x['label']=='auto')):
 t=next(t for t in row['trials'] if t['label']=='auto');v=t.get('phase_mean_ms',{})
 def fmt(x):return 'n/a' if x is None else f'{x:.2f}'
 lines.append('| '+ ' | '.join([str(row['mode']['mode']),row['activity'],str(t['frames']),fmt(v.get('snapshot')),fmt(v.get('socket_send')),fmt(v.get('credit_to_ready')),fmt(v.get('ready_to_send')),fmt(t['decode_ms']),fmt(t['interval_p95_ms'])])+' |')
if durations:
 vals=[d['seconds'] for d in durations]
 lines+=['','## Execution time','',f'{len(durations)} completed mode runs: {sum(vals)/60:.1f} minutes accumulated, mean {statistics.mean(vals):.1f} seconds/mode, range {min(vals):.1f}–{max(vals):.1f} seconds. Includes service/startup preparation, reset, observer warmup, measurements and fixture exit; excludes firmware builds, interrupted attempts and final notification. Each non-teletext mode has three workloads × four encoding paths × two measured seconds. Longer repetitions are reported separately.']
(T/'RESULTS.md').write_text('\n'.join(lines)+'\n')
