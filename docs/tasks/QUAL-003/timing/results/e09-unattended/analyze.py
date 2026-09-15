from pathlib import Path
import csv,json,statistics,re,importlib.util,hashlib
r=Path(__file__).resolve().parent;root=Path.cwd();t=root/'docs/tasks/QUAL-003/timing'
spec=importlib.util.spec_from_file_location('results',t/'scripts/read_results.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
corpus=r/'corpus.json';validated=mod.validate(r/'GQT009.CSV',corpus)
(r/'validated.json').write_text(json.dumps(validated,indent=2)+'\n')
text=(r/'GQT009.CSV').read_text();oldtext=(root/'docs/tasks/PORT-008/uart-alignment/results/graphics.csv').read_text()
def rows(s):return list(csv.DictReader(x for x in s.splitlines() if not x.startswith('#')))
new,old=rows(text),rows(oldtext)
def mismatches(s):return sorted(x for x in s.splitlines() if x.startswith('# probe,') and x.endswith('match=0'))
assert mismatches(text)==mismatches(oldtext),'Probe failure signatures changed'
def select(data,name,route,metric,phase='draw'):
 return [x for x in data if x['repeat'] in ('1','2','3') and x['detail']=='1' and x['case']==name and x['route']==str(route) and x['phase']==phase and x['metric']==str(metric)]
records=[]
for case in json.loads(corpus.read_text())['cases']:
 rec={'case':case['name'],'bytes':case['bytes'],'upload_bytes':case['upload_bytes']}
 for label,metric in [('elapsed',1),('primitive',2),('software_sprite',4),('decoration',6)]:
  for data,route,target in [(new,0,'vdp'),(new,1,'edp'),(old,1,'prior_edp')]:
   values=select(data,case['name'],route,metric);assert len(values)==3 and all(x['status']=='0' for x in values)
   samples=[int(x['value'])/1000 for x in values];counts=[int(x['count']) for x in values]
   rec[target+'_'+label]={'median_ms':statistics.median(samples),'min_ms':min(samples),'max_ms':max(samples),'counts':counts}
 records.append(rec)
progress=[]
for line in text.splitlines():
 if line.startswith('# progress,'):
  p=dict(x.split('=',1) for x in line.split(',')[1:]);p['tick']=int(p['tick']);progress.append(p)
assert len(progress)==39*2*4*5
expected=[(str(rep),str(route),case['name'],phase) for rep in range(4) for route in range(2) for case in json.loads(corpus.read_text())['cases'] for phase in ('preload','setup','draw','output','probe')]
assert [(p['rep'],p['route'],p['case'],p['next']) for p in progress]==expected
elapsed=sum((b['tick']-a['tick'])&0xffffff for a,b in zip(progress,progress[1:]))
durations=[]
pre=[p for p in progress if p['next']=='preload']
for a,b in zip(pre,pre[1:]):durations.append(dict(repeat=int(a['rep']),route=int(a['route']),case=a['case'],ticks=(b['tick']-a['tick'])&0xffffff,nominal_seconds=((b['tick']-a['tick'])&0xffffff)/120))
snap=lambda p:next(x for x in json.loads(p.read_text())['phases'] if x['name']=='snapshot')['count']
delta=snap(r/'after-frame-timing.json')-snap(r/'prelaunch-frame-timing.json');assert delta==0
out=dict(intervals=624,probe_mismatches=8,probe_signatures_unchanged=True,snapshot_delta=delta,progress_records=len(progress),clock='low 24-bit MOS clock; 2 ticks/VBLANK, nominal 120 ticks/s in 60Hz mode20',checkpoint_span_ticks=elapsed,checkpoint_span_nominal_seconds=elapsed/120,duration_limit='First preload to last probe checkpoint; excludes last probes/terminal/audio; nominal clock not independently wall-clock calibrated',human_observation='Completed with about 1m30s left on 30m phone timer, started a few minutes after launch; Author estimates somewhat over30m total',case_durations=durations,records=records,endpoint_interval_seconds=sum(int(x['value']) for x in new if x['metric']=='1')/1000000)
(r/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
def val(rec,dev,label):return rec[dev+'_'+label]['median_ms']
def pct(rec,label):
 a,b=val(rec,'vdp',label),val(rec,'edp',label)
 return 100*(b/a-1) if a else None
def table(title,items,label):
 lines=['## '+title,'','VDP is the baseline. Positive difference means EDP took longer. Medians of three enabled repeats; range is min–max. Sorted by EDP minus VDP milliseconds, worst first.','', '| Case | VDP ms (range) | EDP ms (range) | EDP difference | Prior EDP ms |','|---|---:|---:|---:|---:|']
 for rec in sorted(items,key=lambda x:val(x,'edp',label)-val(x,'vdp',label),reverse=True):
  a,b=rec['vdp_'+label],rec['edp_'+label];d=pct(rec,label)
  lines.append(f"| {rec['case']} | {a['median_ms']:.3f} ({a['min_ms']:.3f}–{a['max_ms']:.3f}) | {b['median_ms']:.3f} ({b['min_ms']:.3f}–{b['max_ms']:.3f}) | {d:+.2f}% | {val(rec,'prior_edp',label):.3f} |" if d is not None else f"| {rec['case']} | {a['median_ms']:.3f} | {b['median_ms']:.3f} | n/a | {val(rec,'prior_edp',label):.3f} |")
 return '\n'.join(lines)+'\n'
lines=['# Completed E09 graphics comparison','', 'All 624 intervals validate, all statuses are zero, eight probe differences exactly match the baseline, and P4 snapshot count remains zero. This is an instrumented framebuffer/transport comparison, not production FPS or browser output performance.','']
lines.append(table('Upload-containing stage elapsed', [x for x in records if x['upload_bytes']], 'elapsed'))
lines.append('These include wire arrival, parsing, creation and drawing; they are not isolated upload or SD read times.\n')
lines.append(table('Resident stage elapsed', [x for x in records if not x['upload_bytes']], 'elapsed'))
for label,title in [('primitive','Primitive execution'),('software_sprite','Software sprite processing')]:
 eligible=[x for x in records if x['vdp_'+label]['counts']==x['edp_'+label]['counts']]
 lines.append(table(title+' — matching call counts',eligible,label))
 excluded=[x['case'] for x in records if x not in eligible]
 lines.append('Unequal call-count stages excluded from this ranking: '+(', '.join(excluded) or 'none')+'. Raw totals/counts are retained in analysis.json. These nested scopes overlap and must not be added.\n')
lines.append('## Output observations\n\nMainboard VGA was active; P4 browser output was disabled. Output/scanline decoration is therefore not an apples-to-apples performance ranking. All output interval records remain in the validated data. No display FPS or scanout correctness claim is made.\n')
(r/'comparison.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:out[k] for k in ('intervals','probe_mismatches','snapshot_delta','progress_records','checkpoint_span_nominal_seconds')},indent=2))
for x in sorted(records,key=lambda x:val(x,'edp','elapsed')-val(x,'vdp','elapsed'),reverse=True)[:6]:print(x['case'],val(x,'vdp','elapsed'),val(x,'edp','elapsed'),pct(x,'elapsed'))
for x in records:
 if x['case'] in ('BSP03_01','COMBINED'):print('KEY',x['case'],val(x,'vdp','elapsed'),val(x,'edp','elapsed'),val(x,'prior_edp','elapsed'))
