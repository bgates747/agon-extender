"""Legacy application acknowledgement control; cannot compare to ExCom frame timing."""
from pathlib import Path
import queue,concurrent.futures.thread,sys,time,json,urllib.request,argparse,struct
sys.path.insert(0,'agents/qual004');from common import cli,KB
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=True)
def sample():return json.load(urllib.request.urlopen(a.url+'/telemetry/latest',timeout=2))
for i,(kind,busy) in enumerate([('char','idle'),('map','idle'),('char','busy'),('map','busy'),('block','idle')]):
 cli('b005-leg-'+str(i),'EMOS LEGACY --keep-display','LOAD /test/bench005/keylat.bin','RUN . '+kind+' '+busy+' tele')
 k=KB(a.url,a.output/(kind+'-'+busy+'-keyboard.json'));k.open(k.status());rows=[]
 try:
  prev=sample().get('received',0)
  for n in range(20):
   time.sleep(.16+(n*37%170)/1000);start=time.perf_counter();k.request(2,[(4,1)]);http=time.perf_counter();deadline=start+2;polls=0
   while time.perf_counter()<deadline:
    v=sample();end=time.perf_counter();polls+=1
    if v.get('received',0)>prev:
     prev=v['received'];payload=bytes.fromhex(v['payload']);seq=struct.unpack_from('<I',payload,8)[0];assert seq==n+1,(seq,n);break
    time.sleep(.005)
   else:raise RuntimeError('No Legacy application acknowledgement')
   rows.append({'trial':n+1,'http_ms':(http-start)*1000,'ack_observed_ms':(end-start)*1000,'polls':polls,'telemetry_age_ms':v['age_ms'],'payload':v['payload']})
   k.send([(4,0)])
  k.send([(41,1),(41,0)]);k.cancel()
 finally:k.lock.close();(a.output/(kind+'-'+busy+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
 print(kind,busy,len(rows),flush=True)
