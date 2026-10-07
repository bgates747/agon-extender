#!/usr/bin/env python3
"""Separate application completion, conversion and scanout; retain exclusions."""
import argparse,csv,json,math,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests/performance/render_load'))
from generate import cases
from generate import MODES
CATALOG={c['id']:c for c in cases()}
PHASES=('drawing_drain','row_wait','row_compose','rgb888_expand','cache_submit','conversion')
def median(x):return statistics.median(x) if x else None
def percentile(x,p):return sorted(x)[max(0,math.ceil(len(x)*p)-1)] if x else None
def analyse(evidence,out,suite='render-load-contract-r04'):
 out.mkdir(parents=True,exist_ok=True);rows=[];excluded=[];run_notes=[]
 for folder in sorted(evidence.glob('BENCH-009-*')):
  if not (folder/'run.json').exists():continue
  meta=json.loads((folder/'run.json').read_text())
  if meta.get('suite')!=suite:continue # Never mix revisions or qualification pilots.
  if meta.get('outcome')!='pass':
   run_notes.append({k:meta[k] for k in ('run_id','mode','endpoint','variant','pass_number','first','end','outcome','failure','failure_code','bad_frames','short_cases','truncated_cases','early_cli_return') if k in meta})
  if not (folder/'decoded.json').exists():excluded.append({'run':folder.name,'reason':meta.get('failure','missing decoded result')});continue
  result=json.loads((folder/'decoded.json').read_text());windows={};telemetry_invalid=False
  expected=MODES[meta['mode']]
  if (result['mode'],result['tag'],result['width'],result['height'],result['colours'])!=(meta['mode'],meta['tag'],expected[0],expected[1],expected[2]):
   excluded.append({'run':folder.name,'reason':'result mode/tag/geometry/colour mismatch'});continue
  if meta.get('fixture') and result['build_id']!=meta['fixture']['build_id']:
   excluded.append({'run':folder.name,'reason':'fixture build identity mismatch'});continue
  if (folder/'telemetry.json').exists():
   t=json.loads((folder/'telemetry.json').read_text());tagged=[w for w in t['windows'] if w['tag']==meta['tag']];windows={w['id']:w for w in tagged}
   telemetry_invalid=t['overflow'] or t['output']!=meta['variant'] or len(windows)!=len(tagged)
  for c in result['cases']:
   duration=((c['raw_end']-c['raw_start'])&0xffffff)/120
   valid=not c['error'] and not c['truncated'] and c['total_frames']>=64 and not any(f['status'] for f in c['frames']) and duration>0
   w=windows.get(c['id']);scope=CATALOG[c['id']]
   flags=int(scope['timing'] and not meta.get('disable_timing',False))|int(scope['marker'])<<1
   if c['flags']!=flags:valid=False
   if meta['endpoint']=='p4' and (telemetry_invalid or not w or w['end_us']<=w['start_us'] or w['flags']!=c['flags'] or len(w['phases'])!=len(PHASES)):valid=False
   if not valid:
    excluded.append({'run':folder.name,'case':c['id'],'reason':'short/truncated/error/uncorrelated window','frames':c['total_frames']});continue
   row={'run':folder.name,'pass':meta.get('pass_number',0),'mode':meta['mode'],'endpoint':meta['endpoint'],'output':meta['variant'],'case':c['id'],'family':scope['family'],'variant':scope['variant'],'level':scope['level'],'style':scope['style'],'frames':c['total_frames'],'window_seconds':duration,'app_updates_per_second':c['total_frames']/duration,'timing_enabled':bool(c['flags']&1),'disable_timing':meta.get('disable_timing',False),'probe_scope':'PRT1 /256, nominal72000 counts/s; MOS vblank120raw units/s,16.67ms quantisation'}
   if scope['variant']=='hardware':
    row['sprite_composition_scope']=('Mainboard scanline composition is outside the command fence; physical delivery unmeasured' if meta['endpoint']=='mainboard' else 'P4 hardware-sprite RowCompose is suppressed with conversion; pose commands only' if meta['variant'] in ('hold','off') else 'P4 composes hardware sprites in RowCompose during conversion; command fence omits recurring composition')
   if c['flags']&1:
    for name,key in (('submit','submit_counts'),('completion','complete_counts'),('total','total_counts')):
     values=[f[key]/72 for f in c['frames']]
     row[name+'_median_ms']=median(values);row[name+'_p95_ms']=percentile(values,.95);row[name+'_min_ms']=min(values);row[name+'_max_ms']=max(values)
    row['completion_over_16_667_ms_percent']=100*sum(f['complete_counts']>1200 for f in c['frames'])/len(c['frames'])
   if w:
    seconds=(w['end_us']-w['start_us'])/1e6;row['p4_window_seconds']=seconds
    row['conversion_updates_per_second']=w['updates']/seconds;row['dma_scanouts_per_second']=w['scanouts']/seconds
    row['hdmi_submissions']=w['updates']
    row['presentation_outcome']='no completed submission' if meta['variant']=='normal' and not w['updates'] else 'submissions observed' if meta['variant']=='normal' else 'suppressed by selected output control'
    row['output_clock']='software60Hz; no DMA' if meta['variant']=='off' else 'DMA frame-completion proxy'
    row['marker_valid']=w['marker_valid'];row['marker_invalid']=w['marker_invalid'];row['last_template_frame']=w['last_frame']
    for name,phase in zip(PHASES,w['phases']):
     row[name+'_calls']=phase['calls'];row[name+'_wall_sum_ms']=phase['us']/1000;row[name+'_wall_mean_ms']=phase['us']/1000/phase['calls'] if phase['calls'] else None;row[name+'_wall_max_ms']=phase['max_us']/1000 if phase['calls'] else None;row[name+'_boundary_drops']=phase['boundary_drops']
   rows.append(row)
 fields=sorted(set().union(*(r.keys() for r in rows))) if rows else []
 with (out/'cases.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
 (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'excluded.json').write_text(json.dumps(excluded,indent=2)+'\n')
 (out/'run-notes.json').write_text(json.dumps(run_notes,indent=2)+'\n')
 contract=json.loads((ROOT/'tests/performance/render_load/contract-r04.json').read_text())
 coverage=[]
 for output in contract['p4_outputs']:
  modes=contract['modes'] if output=='normal' else contract['output_control_modes']
  endpoints=('mainboard','p4') if output=='normal' else ('p4',)
  for mode in modes:
   for endpoint in endpoints:
    for number in range(1,contract['passes']+1):
     matching=[r for r in rows if (r['output'],r['mode'],r['endpoint'],r['pass'])==(output,mode,endpoint,number) and not r['disable_timing']]
     ids={r['case'] for r in matching};duplicate=sorted(i for i in ids if sum(r['case']==i for r in matching)>1)
     coverage.append(dict(output=output,mode=mode,endpoint=endpoint,pass_number=number,valid_cases=len(ids),expected_cases=len(CATALOG),missing_cases=sorted(set(CATALOG)-ids),duplicate_valid_cases=duplicate,complete=len(ids)==len(CATALOG) and not duplicate))
 (out/'coverage.json').write_text(json.dumps({'suite':suite,'expected_case_executions':len(coverage)*len(CATALOG),'valid_unique_case_executions':sum(r['valid_cases'] for r in coverage),'complete':all(r['complete'] for r in coverage),'groups':coverage},indent=2)+'\n')
 # Preserve duplicate records, but do not silently choose one measurement for
 # a declared pass. Sampling reruns replace short records already excluded above.
 keys={}
 for r in rows:
  if not r['disable_timing']:keys.setdefault((r['output'],r['mode'],r['endpoint'],r['pass'],r['case']),[]).append(r)
 unique=[items[0] for items in keys.values() if len(items)==1]
 groups={}
 for r in unique:
  if r['output']!='normal' or not r['timing_enabled'] or r['disable_timing']:continue
  groups.setdefault((r['mode'],r['case']),{}).setdefault(r['endpoint'],[]).append(r)
 comparisons=[]
 for key,g in groups.items():
  if 'mainboard' not in g or 'p4' not in g:continue
  by_a={r['pass']:r for r in g['mainboard'] if r['pass'] in (1,2,3)};by_b={r['pass']:r for r in g['p4'] if r['pass'] in (1,2,3)}
  paired=sorted(set(by_a)&set(by_b))
  if not paired:continue
  a=[by_a[p] for p in paired];b=[by_b[p] for p in paired];ma=median([x['completion_median_ms'] for x in a]);mb=median([x['completion_median_ms'] for x in b]);ratio=mb/ma if ma else None
  item={k:a[0][k] for k in ('mode','case','family','variant','level','style')};item.update(mainboard_completion_median_ms=ma,p4_completion_median_ms=mb,p4_vs_mainboard_percent=(ratio-1)*100 if ratio else None,mainboard_runs=len(a),p4_runs=len(b),mainboard_app_updates_per_second=median([x['app_updates_per_second'] for x in a]),p4_app_updates_per_second=median([x['app_updates_per_second'] for x in b]),p4_conversion_updates_per_second=median([x['conversion_updates_per_second'] for x in b]),p4_dma_scanouts_per_second=median([x['dma_scanouts_per_second'] for x in b]),mainboard_completion_range_ms=[min(x['completion_median_ms'] for x in a),max(x['completion_median_ms'] for x in a)],p4_completion_range_ms=[min(x['completion_median_ms'] for x in b),max(x['completion_median_ms'] for x in b)],mainboard_p95_ms=median([x['completion_p95_ms'] for x in a]),p4_p95_ms=median([x['completion_p95_ms'] for x in b]))
  item.update(paired_passes=paired,three_pass_complete=len(paired)==3)
  for endpoint,records in (('mainboard',a),('p4',b)):
   item[endpoint+'_completion_over_16_667_ms_percent']=median([x['completion_over_16_667_ms_percent'] for x in records])
   item[endpoint+'_submission_median_ms']=median([x['submit_median_ms'] for x in records])
  comparisons.append(item)
 comparisons.sort(key=lambda r:r['p4_vs_mainboard_percent'] if r['p4_vs_mainboard_percent'] is not None else -1e9,reverse=True)
 (out/'comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
 controls=[];control_groups={}
 for r in unique:
  if r['endpoint']!='p4' or not r['timing_enabled'] or r['disable_timing'] or r['pass'] not in (1,2,3):continue
  control_groups.setdefault((r['mode'],r['case']),{}).setdefault(r['output'],{})[r['pass']]=r
 for key,g in control_groups.items():
  if not all(v in g for v in ('normal','hold','off')):continue
  paired=sorted(set(g['normal'])&set(g['hold'])&set(g['off']))
  if not paired:continue
  item={k:g['normal'][paired[0]][k] for k in ('mode','case','family','variant','level','style')}
  for output in ('normal','hold','off'):
   for metric in ('completion_median_ms','completion_p95_ms','app_updates_per_second','conversion_updates_per_second','dma_scanouts_per_second'):
    item[output+'_'+metric]=median([g[output][p][metric] for p in paired])
  a=item['normal_completion_median_ms'];b=item['hold_completion_median_ms'];c=item['off_completion_median_ms']
  item.update(hold_vs_normal_percent=(b-a)/a*100 if a else None,off_vs_hold_percent=(c-b)/b*100 if b else None,paired_passes=paired,three_pass_complete=len(paired)==3,off_clock='software60Hz; framebuffer memory retained; no DSI DMA')
  controls.append(item)
 controls.sort(key=lambda r:r['normal_completion_median_ms'],reverse=True)
 (out/'output-controls.json').write_text(json.dumps(controls,indent=2)+'\n')
 # Phase means are medians of per-pass window means, not pooled CPU costs.
 # Conversion scopes also close on aborted publication, whereas updates count
 # only accepted framebuffer submissions. Do not call attempts displayed frames.
 phase_groups={}
 for r in unique:
  if r['endpoint']=='p4' and r['timing_enabled'] and r['pass'] in (1,2,3):
   phase_groups.setdefault((r['output'],r['mode'],r['case']),[]).append(r)
 phases=[]
 for key,records in phase_groups.items():
  item={k:records[0][k] for k in ('output','mode','case','family','variant','level','style')}
  item.update(paired_passes=sorted(r['pass'] for r in records),runs=[r['run'] for r in records],three_pass_complete=len(records)==3)
  for phase in PHASES:
   for suffix in ('wall_mean_ms','wall_max_ms','wall_sum_ms','calls','boundary_drops'):
    values=[r[phase+'_'+suffix] for r in records if r[phase+'_'+suffix] is not None]
    item[phase+'_'+suffix]=median(values)
  item['completed_submissions_per_second']=median([r['conversion_updates_per_second'] for r in records])
  item['zero_submission_passes']=[r['pass'] for r in records if not r['hdmi_submissions'] and r['output']=='normal']
  phases.append(item)
 phases.sort(key=lambda r:r['conversion_wall_mean_ms'] if r['conversion_wall_mean_ms'] is not None else -1,reverse=True)
 (out/'phase-summary.json').write_text(json.dumps(phases,indent=2)+'\n')
 zero_submissions=[{k:r[k] for k in ('run','pass','mode','case','family','variant','level','style','frames','window_seconds','p4_window_seconds','conversion_calls','conversion_wall_mean_ms','conversion_boundary_drops','hdmi_submissions','dma_scanouts_per_second')} for r in unique if r['endpoint']=='p4' and r['output']=='normal' and not r['hdmi_submissions']]
 (out/'zero-submissions.json').write_text(json.dumps(zero_submissions,indent=2)+'\n')
 perturbation=[];perturb_groups={}
 for r in unique:
  if r['case'] not in (0,1,90,91,92,93) or r['disable_timing'] or r['pass'] not in (1,2,3):continue
  perturb_groups.setdefault((r['mode'],r['endpoint'],r['output'],r['style']),{}).setdefault(r['case'],{})[r['pass']]=r
 for key,g in perturb_groups.items():
  ids=(0,90,92) if key[3]=='paced' else (1,91,93)
  if not all(i in g for i in ids):continue
  paired=sorted(set.intersection(*(set(g[i]) for i in ids)))
  if not paired:continue
  rates=[median([g[i][p]['app_updates_per_second'] for p in paired]) for i in ids]
  perturbation.append(dict(mode=key[0],endpoint=key[1],output=key[2],style=key[3],ordinary_app_updates_per_second=rates[0],no_marker_no_timing_app_updates_per_second=rates[1],marker_no_timing_app_updates_per_second=rates[2],ordinary_vs_no_marker_no_timing_percent=(rates[0]-rates[1])/rates[1]*100,marker_vs_no_marker_no_timing_percent=(rates[2]-rates[1])/rates[1]*100,paired_passes=paired,three_pass_complete=len(paired)==3))
 perturbation.sort(key=lambda r:r['ordinary_vs_no_marker_no_timing_percent'])
 (out/'instrumentation-controls.json').write_text(json.dumps(perturbation,indent=2)+'\n')
 lines=['# Rendering load results','', 'Worst cases first, ranked by P4/mainboard median completion slowdown. Percent is `(P4−mainboard)/mainboard×100%`. Completion includes routing, transport, drawing and the reply. Application updates and accepted framebuffer submissions are separate from the DMA scanout proxy; none proves physical displayed FPS. Hardware/software sprite labels name the VDP API flag: recurring hardware-sprite composition is outside the command fence. The P4 performs that composition in RowCompose; hold/off suppress it with conversion, so those hardware-sprite controls measure pose-command processing with composition absent. They cannot establish hardware-sprite rendering throughput.','',f'Valid case records: {len(rows)}. Exclusions: {len(excluded)}. Runs with incomplete/failing metadata: {len(run_notes)}. Complete groups: {sum(r["complete"] for r in coverage)}/{len(coverage)}. See coverage.json for every missing case and run-notes.json for run outcomes; valid prior checkpoints remain usable when a later case fails.','', '| Mode / workload / level / style | Mainboard completion ms | P4 completion ms | P4 difference % | Mainboard app updates/s | P4 app updates/s | P4 submissions/s | DMA proxy Hz |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for r in comparisons:
  label=f"{r['mode']} / {r['family']} {r['variant']} / {r['level']} / {r['style']}"
  label+=' ('+str(len(r['paired_passes']))+'/3 paired passes)'
  lines.append('| '+label+' | '+ ' | '.join(f"{r[k]:.3f}" for k in ('mainboard_completion_median_ms','p4_completion_median_ms','p4_vs_mainboard_percent','mainboard_app_updates_per_second','p4_app_updates_per_second','p4_conversion_updates_per_second','p4_dma_scanouts_per_second'))+' |')
 lines += ['', '## Completion tails and budget', '', 'Same slowdown ranking and matching passes as above. p95 and over-budget percentages are medians of per-pass statistics. Ranges span the per-pass completion medians; samples are not pooled. The 16.667ms threshold is 1,200 nominal PRT counts. Double-buffer completion includes ordinary vblank-synchronised swap, so crossing this threshold alone does not establish drawing CPU saturation.', '', '| Mode / case / workload | Mainboard p95 ms | P4 p95 ms | Mainboard median range ms | P4 median range ms | Mainboard over budget % | P4 over budget % |', '|---|---:|---:|---|---|---:|---:|']
 for r in comparisons:
  label=f"{r['mode']} / {r['case']} / {r['family']} {r['variant']} {r['level']} {r['style']}"
  ranges=['–'.join(f'{v:.3f}' for v in r[endpoint+'_completion_range_ms']) for endpoint in ('mainboard','p4')]
  lines.append('| '+label+' | '+f"{r['mainboard_p95_ms']:.3f} | {r['p4_p95_ms']:.3f} | "+' | '.join(ranges)+f" | {r['mainboard_completion_over_16_667_ms_percent']:.3f} | {r['p4_completion_over_16_667_ms_percent']:.3f} |")
 lines += ['', '## P4 presentation phases', '', 'Worst conversion-attempt wall means first; first24 rows shown, all rows retained in phase-summary.json. Each value is the median of per-pass window means. Row wait/composition/expansion are per-row scopes, cache is per-submission, and conversion is per attempt including aborted publication. These scopes have different call counts, overlap and exclude boundary-crossing samples: their means must not be summed as exclusive CPU time. Complete submissions count accepted framebuffer selections, not monitor-observed pictures.', '', '| Output / mode / case | Attempt wall mean ms | Row wait mean ms | Row compose mean ms | RGB888 row expand mean ms | Cache mean ms | Complete submissions/s | Passes |', '|---|---:|---:|---:|---:|---:|---:|---|']
 def shown(value):return '—' if value is None else f'{value:.3f}'
 for r in phases[:24]:
  lines.append(f"| {r['output']} / {r['mode']} / {r['case']} | "+' | '.join(shown(r[k]) for k in ('conversion_wall_mean_ms','row_wait_wall_mean_ms','row_compose_wall_mean_ms','rgb888_expand_wall_mean_ms','cache_submit_wall_mean_ms','completed_submissions_per_second'))+' | '+str(r['paired_passes'])+' |')
 lines += ['', f'Normal-HDMI windows with zero completed submissions: {len(zero_submissions)}; see zero-submissions.json for exact case/run identities. These application measurements can be valid while presentation fails to advance. A 60Hz DMA count can repeatedly scan an older framebuffer. Zero submissions are output failures, not zero application drawing throughput; hook-free controls and independent visual evidence remain separate.', '']
 lines += ['', '## Output controls', '', 'Worst cases first by normal-HDMI completion time. Hold retains scanout; off retains framebuffer memory and uses a software60Hz clock. Percentages are `(hold−normal)/normal×100%` and `(off−hold)/hold×100%` for equal application metrics. Only matching pass numbers are paired; fewer than three pairs are incomplete.', '', '| Mode / workload / level / style | Normal ms | Hold ms | Off ms | Hold vs normal % | Off vs hold % | Paired passes |', '|---|---:|---:|---:|---:|---:|---:|']
 for r in controls:
  label=f"{r['mode']} / {r['family']} {r['variant']} / {r['level']} / {r['style']}"
  lines.append('| '+label+' | '+' | '.join(f"{r[k]:.3f}" for k in ('normal_completion_median_ms','hold_completion_median_ms','off_completion_median_ms','hold_vs_normal_percent','off_vs_hold_percent'))+' | '+str(len(r['paired_passes']))+'/3 |')
 lines += ['', '## Marker and timing controls', '', 'Worst rate difference first. Baseline is the same static workload with no frame marker and no timing probes. Percent is `(variant−baseline)/baseline×100%`; negative values mean fewer application updates/s. Paced rates are capped by deliberate pacing and cannot establish absence of overhead. Disabled probes retain the bounded fence watchdog and the compiled diagnostic carrier.', '', '| Mode / endpoint / output / style | Baseline app updates/s | Marker only app updates/s | Ordinary app updates/s | Marker difference % | Ordinary difference % | Paired passes |', '|---|---:|---:|---:|---:|---:|---:|']
 for r in perturbation:
  label=f"{r['mode']} / {r['endpoint']} / {r['output']} / {r['style']}"
  lines.append('| '+label+' | '+' | '.join(f"{r[k]:.3f}" for k in ('no_marker_no_timing_app_updates_per_second','marker_no_timing_app_updates_per_second','ordinary_app_updates_per_second','marker_vs_no_marker_no_timing_percent','ordinary_vs_no_marker_no_timing_percent'))+' | '+str(len(r['paired_passes']))+'/3 |')
 (out/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'valid_cases':len(rows),'excluded':len(excluded),'comparisons':len(comparisons)}))
def main():
 p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();analyse(a.evidence,a.output)
if __name__=='__main__':main()
