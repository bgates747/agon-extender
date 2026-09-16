"""Collect matched ladder scopes; application pacing is not native completion."""
import argparse,json,re,statistics
from pathlib import Path

def load(p):return json.loads(p.read_text()) if p.exists() else None

def summarize(root):
 rows=[]
 tracefile=root/'refresh-final.log'
 if not tracefile.exists():tracefile=root/'refresh.log'
 text=tracefile.read_text(errors='replace') if tracefile.exists() else ''
 for np in sorted(root.glob('*-nonce.txt')):
  name=np.name.removesuffix('-nonce.txt');nonce=np.read_text().strip();h=load(root/(name+'-raw-header.json'));g=load(root/(name+'-game.json'));t=load(root/(name+'-trace.json'));o=load(root/(name+'-output.json'));recv=load(root/name/'result.json')
  if not h:continue
  n=bytes.fromhex(nonce);row={'case':name,'nonce':nonce,'fixture_error':h['error'],'fixture_count':h['count'],'requested_payload_bytes':n[5]*12288 if n[4]==1 else 0,'application':g[0] if g else None,'native':t,'output':o,'receiver':None}
  if t:
   part=text.split('NPTRACE begin '+nonce,1)[1].split('NPTRACE end '+nonce,1)[0]
   raw=[tuple(map(int,v)) for v in re.findall(r'NPTRACE row (\d+) (\d+) (\d+)',part)]
   times=[((raw[i][2]-raw[i-1][2])&0xffffffff)/1000 for i in range(121,len(raw))];ts=sorted(times)
   row['native']['completion_intervals'].update(p50_ms=statistics.median(times),p99_ms=ts[(len(ts)*99+99)//100-1],over_16_67_ms=sum(x>16.67 for x in times),over_33_34_ms=sum(x>33.34 for x in times))
  if o:
   seconds=o['window_seconds'];send=o['phases']['send'];compose=o['phases']['compose'];row.update(approx_nominal_opportunities=seconds*1e6/16667,composition_rate=compose['calls']/seconds,send_rate=send['calls']/seconds,payload_mbit_s=send['calls']*row['requested_payload_bytes']*8/seconds/1e6,protocol_mbit_s=send['units']*8/seconds/1e6)
  if recv:
   row['receiver']={k:v for k,v in recv.items() if k!='rows'};row['receiver']['validated_messages']=len(recv['rows']);row['receiver']['validated_bytes']=sum(x['bytes'] for x in recv['rows'])
  rows.append(row)
 return rows
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(summarize(a.root),indent=2)+'\n')
