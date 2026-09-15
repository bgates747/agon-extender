"""Match nonce-bound wire refresh arrivals to P4 completion trace, offline.

Separate oscillator epochs prevent an absolute ingress-latency claim. Interval
comparisons and offset-normalized delay variation remain directly observable.
Uses the existing independently checked 24MHz/1152000 decoder and channel map.
"""
import argparse,json,re,sys,tempfile,zipfile,statistics
from pathlib import Path
import numpy as np
from analyze import parse
from analyze_refresh_trace import analyze as trace_analyze
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'AUDIT-005/scripts'))
from capture_trace import RATE,metadata,sha
from analyze_trace import decode,high_intervals,gap_metrics,independent_decode,overlap

def stats(values):
 s=sorted(values);return dict(count=len(s),mean_ms=statistics.mean(s),p95_ms=s[(len(s)*95+99)//100-1],max_ms=max(s),min_ms=min(s))
def locate(data,marker):
 matches=[m.start() for m in re.finditer(re.escape(marker),data)]
 assert len(matches)==1,'Missing/duplicate nonce marker'
 return matches[0]
def main():
 p=argparse.ArgumentParser();p.add_argument('capture',type=Path);p.add_argument('--trace',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--nonce',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--inspect-short',action='store_true');a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False)
 provenance=json.loads((a.capture/'capture-result.json').read_text());assert provenance['acquisition_pass'] or a.inspect_short,'Short acquisition requires explicit diagnostic inspection'
 game=parse(a.result,'unfenced-sw',bytes.fromhex(a.nonce),2400);assert game['count']==2400
 log=a.trace.read_text(errors='replace');tr=trace_analyze(log,a.nonce,2400)
 segment=log.split('NPTRACE begin '+a.nonce+' ',1)[1].split('NPTRACE end '+a.nonce,1)[0]
 rows=[tuple(map(int,x)) for x in re.findall(r'NPTRACE row (\d+) (\d+) (\d+)',segment)];assert len(rows)==2400
 with tempfile.TemporaryDirectory(prefix='nurples-wire-') as temp:
  rawpath=Path(temp)/'logic.raw'
  with zipfile.ZipFile(a.capture/'logic.sr') as z:
   names,size=metadata(z);assert size==provenance['acquisition']['samples'];assert size==80*RATE or a.inspect_short
   with rawpath.open('wb') as dst:
    for n in names:
     with z.open(n) as src:
      import shutil;shutil.copyfileobj(src,dst)
  assert sha(rawpath)==provenance['raw_sha256']
  raw=np.memmap(rawpath,dtype=np.uint8,mode='r')
  forward,ferr=decode(raw,1);reverse,rerr=decode(raw,6);data=bytes(f['byte'] for f in forward)
  prefix=bytes([23,0,160,255,255,0,16,0])+b'NPTRACE'
  start=locate(data,prefix+b'1'+bytes.fromhex(a.nonce))+24
  stop=locate(data,prefix+b'0'+bytes.fromhex(a.nonce));assert start<stop
  assert forward[stop+23]['end']<len(raw),'Terminal marker cut off'
  begin=forward[start-1]['end'];end=forward[stop]['start']
  assert not any(begin<=e<end for e in ferr+rerr),'Framing error within nonce-bound game'
  positions=[start+m.start() for m in re.finditer(re.escape(bytes([23,27,15])),data[start:stop])]
  assert len(positions)==2400,'Refresh wire/VDP counts disagree; reject ambiguous matching'
  wire=[forward[i+2]['end']/RATE*1000 for i in positions]
  enqueue=[0.0]
  for prev,row in zip(rows,rows[1:]):enqueue.append(enqueue[-1]+((row[1]-prev[1])&0xffffffff)/1000)
  variation=[e-(w-wire[0]) for e,w in zip(enqueue,wire)];origin=min(variation);variation=[v-origin for v in variation]
  wire_intervals=[wire[i]-wire[i-1] for i in range(121,len(wire))]
  blocked=high_intervals(raw,4);reverse_blocked=high_intervals(raw,3)
  selected=[f for f in forward if f['start']>=begin and f['end']<=end]
  selected_reverse=[f for f in reverse if f['start']>=begin and f['end']<=end]
  record=dict(acquisition_pass=provenance['acquisition_pass'],partial_acquisition_inspection=a.inspect_short,scope='Passive unchanged SW game; wire stop-bit arrivals versus P4 enqueue/completion, not absolute latency or analogue integrity',game=game,completion_trace=tr,wire_refresh_intervals=stats(wire_intervals),offset_normalized_ingress_delay_variation=stats(variation[120:]),clock_limit='Independent clocks/epochs; constant offset removed, oscillator drift not calibrated. Variation is not absolute ingress latency.',forward_bytes=len(selected),reverse_bytes=len(selected_reverse),measured_seconds=(end-begin)/RATE,forward_gaps=gap_metrics(selected,blocked),reverse_gaps=gap_metrics(selected_reverse,reverse_blocked) if len(selected_reverse)>1 else None,p4_withheld_permission_ms=overlap([(begin,end)],blocked)/RATE*1000,ez80_withheld_permission_ms=overlap([(begin,end)],reverse_blocked)/RATE*1000,independent_decode_pass=False)
  (a.output/'preliminary.json').write_text(json.dumps(record,indent=2)+'\n')
  independent_decode(a.capture/'logic.sr',a.output,1,forward,begin,end)
  independent_decode(a.capture/'logic.sr',a.output,6,reverse,begin,end)
  record['independent_decode_pass']=True
  (a.output/'analysis.json').write_text(json.dumps(record,indent=2)+'\n')
  (a.output/'refreshes.csv').write_text('index,wire_stop_ms,enqueue_elapsed_ms,offset_normalized_ingress_variation_ms\n'+''.join(f'{i},{w:.6f},{e:.6f},{v:.6f}\n' for i,(w,e,v) in enumerate(zip(wire,enqueue,variation))))
 print(json.dumps({k:record[k] for k in ('wire_refresh_intervals','offset_normalized_ingress_delay_variation','p4_withheld_permission_ms','independent_decode_pass')},indent=2))
if __name__=='__main__':main()
