#!/usr/bin/env python3
"""Report the separately bounded RGB-001 native/direct subset, without pooling.

This report preserves command completion, presentation and physical DMA cadence
as separate scopes. Marker transitions are sampled source identities, never a
claim that every single-buffer image was complete when physically scanned.
"""
import argparse,csv,datetime,hashlib,json,math,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests/performance/render_load'))
from generate import cases,MODES
from render_load_collect import validate
CATALOG={c['id']:c for c in cases()}
PHASES=('drawing_drain','row_wait','row_compose','rgb888_expand','cache_submit','presentation_attempt')
def median(values):return statistics.median(values) if values else None
def percentile(values,p):return sorted(values)[max(0,math.ceil(len(values)*p)-1)]
def equivalent(ms):return 1000/ms if ms else None
def change(new,old):return (new-old)/old*100 if old else None

def collect(root):
 rows=[];excluded=[]
 for folder in sorted(root.glob('BENCH-009-*')):
  if not (folder/'run.json').exists():continue
  meta=json.loads((folder/'run.json').read_text())
  if meta.get('suite')!='rgb-001-subset-r01':continue
  if meta['outcome']!='pass':
   excluded.append(dict(run=str(folder),reason=meta['outcome']));continue
  raw=(folder/'results.bin').read_bytes();telemetry=json.loads((folder/'telemetry.json').read_text())
  assert hashlib.sha256(raw).hexdigest()==meta['result_sha256'],'Raw result hash differs from validated receipt'
  result,validation=validate(meta,raw,telemetry,(folder/'failure.bin').read_bytes() if (folder/'failure.bin').exists() else None)
  assert validation['outcome']=='pass','Failed or invalid raw records cannot enter the comparison'
  assert result==json.loads((folder/'decoded.json').read_text()),'Decoded records differ from raw checkpoints'
  assert not telemetry['overflow'] and telemetry['output']==meta['variant']
  windows={w['id']:w for w in telemetry['windows'] if w['tag']==meta['tag']}
  renderer=meta['control_context']['renderer']
  for case in result['cases']:
   assert case['total_frames']>=64 and not case['error'] and not case['truncated'] and not any(f['status'] for f in case['frames'])
   w=windows[case['id']];assert w['end_us']>w['start_us'] and w['flags']==case['flags']
   wall=(w['end_us']-w['start_us'])/1e6;raw=((case['raw_end']-case['raw_start'])&0xffffff)/120
   completion=[f['complete_counts']/72 for f in case['frames']]
   scope=CATALOG[case['id']]
   row=dict(mode=meta['mode'],case=case['id'],renderer=renderer,output=meta['variant'],family=scope['family'],workload=scope['variant'],level=scope['level'],style=scope['style'],frames=case['total_frames'],window_seconds=wall,completion_median_ms=median(completion),completion_p95_ms=percentile(completion,.95),completion_equivalent_fps=equivalent(median(completion)),completion_over_16_667_ms_percent=sum(v>1000/60 for v in completion)/len(completion)*100,application_updates_per_second=case['total_frames']/raw,hdmi_submissions_per_second=w['updates']/wall,dma_scanout_hz=w['scanouts']/wall,marker_transitions_per_second=w.get('marker_transitions',0)/wall,marker_repeats_per_second=w.get('marker_repeats',0)/wall,marker_valid=w['marker_valid'],marker_invalid=w['marker_invalid'],run=str(folder))
   row['render_storage']=meta['control_context'].get('render_storage','not-recorded')
   for name,phase in zip(PHASES,w['phases']):
    row[name+'_mean_ms']=phase['us']/phase['calls']/1000 if phase['calls'] else None
    row[name+'_calls']=phase['calls'];row[name+'_boundary_drops']=phase['boundary_drops']
   rows.append(row)
 return rows,excluded

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 assert not a.output.exists(),'Preserve existing reports; select a fresh output directory'
 rows,excluded=collect(a.evidence);a.output.mkdir(parents=True,exist_ok=False)
 keys={}
 for r in rows:
  key=(r['mode'],r['case'],r['renderer'],r['output']);assert key not in keys,'Do not silently pool duplicate matched passes';keys[key]=r
 paired=[]
 for mode,case in sorted({(r['mode'],r['case']) for r in rows}):
  native=keys.get((mode,case,'native','normal'));direct=keys.get((mode,case,'rgb888','normal'))
  if not native or not direct:continue
  item=dict(mode=mode,case=case,family=direct['family'],workload=direct['workload'],level=direct['level'],style=direct['style'],native_completion_ms=native['completion_median_ms'],rgb888_completion_ms=direct['completion_median_ms'],native_completion_equivalent_fps=native['completion_equivalent_fps'],rgb888_completion_equivalent_fps=direct['completion_equivalent_fps'],rgb888_vs_native_completion_percent=change(direct['completion_median_ms'],native['completion_median_ms']))
  for renderer in ('native','rgb888'):
   for output in ('normal','off'):
    r=keys.get((mode,case,renderer,output))
    if r:
     for metric in ('completion_median_ms','completion_equivalent_fps','application_updates_per_second','hdmi_submissions_per_second','dma_scanout_hz','marker_transitions_per_second','marker_repeats_per_second','presentation_attempt_mean_ms'):
      item[renderer+'_'+output+'_'+metric]=r[metric]
  paired.append(item)
 paired.sort(key=lambda r:r['rgb888_completion_ms'],reverse=True)
 result=dict(scope='One matched bounded pass; unchanged r04 VDU templates. CPU/native colour semantics preserved. Each row records copied or panel-direct RGB888 storage from its installed manifest. OFF retains allocations but has no DSI DMA/presentation; software60Hz opportunities. PRT nominal72000counts/s, MOS raw120units/s. Equivalent fps=1000/ms for completion alone. Marker transitions are sampled source identities, not full-frame physical coherence.',ranking='Worst direct-RGB888 median command completion first',rows=rows,comparison=paired,excluded=excluded)
 result.update(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),provenance=[])
 for folder in sorted({r['run'] for r in rows}):
  result['provenance'].append(dict(run=folder,files={name:hashlib.sha256((Path(folder)/name).read_bytes()).hexdigest() for name in ('run.json','results.bin','decoded.json','telemetry.json','startup.txt','plan.bin')}))
 (a.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 if paired:
  fields=sorted({k for r in paired for k in r})
  with (a.output/'comparison.csv').open('w') as f:
   writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(paired)
 print(json.dumps(dict(cases=len(rows),matched_normal_pairs=len(paired),excluded=len(excluded))))

if __name__=='__main__':main()
