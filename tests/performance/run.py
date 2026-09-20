#!/usr/bin/env python3
"""Run one admitted game-timing batch from a prepared SD service.

Requires exclusive bench ownership and prior preparation/firmware qualification.
Never flashes or resets hardware. Private endpoint and evidence paths are arguments.
"""
from pathlib import Path
import sys,time,datetime,json,re,csv,io,argparse,urllib.request
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'scripts'))
from sdcard import Client,path_payload
from keyboard import Client as KeyboardClient,text_events
from analyze import summarize
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--route',choices=['legacy','excom'],required=True)
p.add_argument('--game',choices=['inv','rally','nur','empty','draw'],required=True)
p.add_argument('--markers',type=int,choices=[0,1],required=True)
p.add_argument('--run-name',required=True,help='Unique ASCII filename stem on SD')
p.add_argument('--symbols',type=Path,help='Exact Nurples build symbols')
p.add_argument('--prt-divider',type=int,choices=[16,64],default=16)
p.add_argument('--rally-binary',default='rtiming.bin')
args=p.parse_args()
if not re.fullmatch('[A-Za-z0-9-]{1,40}',args.run_name):p.error('Invalid run name')
if args.game=='nur' and not args.symbols:p.error('Nurples requires exact --symbols')
route,game,mark=args.route,args.game,args.markers;name=args.run_name
out=args.output;out.mkdir(parents=True,exist_ok=False)
class Control:
 URL=args.url
 def get(self,route):
  with urllib.request.urlopen(self.URL+route,timeout=4) as response:return response.status,response.read().decode()
 def line(self,command):
  c=KeyboardClient(self.URL,out/('cli-'+str(time.time_ns())+'.json'))
  try:
   state=c.status();c.open(state);c.send(text_events(command+'\n',state['locale'],state['caps']));c.cancel()
  finally:c.lock.close()
  time.sleep(.4)
control=Control()
dirs={'inv':'inv','rally':'rally','nur':'nur','empty':'','draw':''};modes={'inv':8,'rally':136,'nur':20,'empty':8,'draw':8};bins={'inv':'inv.bin','rally':args.rally_binary,'nur':'ntiming.bin' if mark else 'ntiming0.bin','empty':'empty.bin','draw':'draw.bin'}
wd='/test/gt'+('/'+dirs[game] if dirs[game] else '')
pre=Client(control.URL,out/'stage.json')
try:
 if not pre.status().get('online'):raise RuntimeError('Start the prepared SD service before invoking this runner')
 pre.connect()
 if game!='nur':
  cfg=wd+'/timing.cfg';current=pre.download(cfg)
  assert current in (b'0',b'1'), 'Unknown timing configuration'
  if current!=str(mark).encode():
   state=pre.rpc(10,b'\x00'+path_payload(cfg));assert state in (b'\x01',b'\x09'),state
   if state==b'\x09':
    backup=pre.download(cfg+'.p17bak');assert backup in (b'0',b'1')
    (out/'prior-config-backup.bin').write_bytes(backup);pre.rpc(10,b'\x03'+path_payload(cfg))
   pre.upload(cfg,str(mark).encode(),True)
 lines=['EMOS '+route,'VDU 22 '+str(modes[game])]
 if game=='nur' and mark:lines+=['CD /test/gt','LOAD probe.bin','RUN']
 lines+=['CD '+wd,'LOAD '+bins[game],'RUN']
 if game=='nur':
  source=args.symbols
  syms={m.group(1):int(m.group(2),16) for m in re.finditer(r'^(\w+) \$([0-9a-fA-F]+)',source.read_text(),re.M)}
  start=syms['gt_data'];size=syms['gt_data_end']-start
  assert size==1448
  lines += [f'SAVE {wd}/{name}.raw &{start:X} &{size:X}']
  if mark:lines+=['LOAD /test/gt/collect.bin','RUN']
 if mark:lines+=['LOAD /test/gt/dump.bin','RUN']
 lines+=['EMOS LEGACY --keep-display','LOAD /extender/sdserve.bin','RUN . /']
 batch=('\r\n'.join(lines)+'\r\n').encode();(out/'batch.txt').write_bytes(batch);pre.upload('/test/gt/'+name+'.txt',batch,True);pre.rpc(11)
finally:pre.lock.close()
(out/'video-before.json').write_text(control.get('/diagnostics/video-timing')[1])
at=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat();control.line('EXEC /test/gt/'+name+'.txt')
c=Client(control.URL,out/'collect.json')
try:
 end=time.monotonic()+180
 while not c.status().get('online'):
  if time.monotonic()>end:raise TimeoutError('Game did not return to SD service within180s')
  time.sleep(1)
 runtime=time.monotonic()-at;(out/'video-after.json').write_text(control.get('/diagnostics/video-timing')[1]);c.connect()
 if game!='nur' or mark:
  raw=c.download(wd+'/'+game+'.csv');(out/'device.csv').write_bytes(raw)
 if game=='nur':
  raw=c.download(wd+'/'+name+'.raw');(out/'raw.bin').write_bytes(raw);assert raw[:8]==b'GT1PRT!!' and len(raw)==1448
  records=[[int.from_bytes(raw[8+i*12+j:11+i*12+j],'little') for j in [0,3,6,9]] for i in range(120)]
  assert all(0<a<=b<=65535 for a,b,_,_ in records),'Incomplete or invalid PRT rows'
  if mark:rows=list(csv.DictReader((out/'device.csv').open()));assert len(rows)==120
  else:rows=[dict(source=255,frame=i,submitted_us=0,completed_us=0,drain_us=0) for i in range(120)]
  for row,(a,b,start,stop) in zip(rows,records):row.update(active_prt=a,logic_prt=0,submit_prt=a,pacing_prt=b-a,total_prt=b,overflow=int(b==65535),mos_ticks=(stop-start)&0xffffff,run_ticks=(records[-1][3]-records[0][2])&0xffffff)
  with (out/'combined.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 else:(out/'combined.csv').write_bytes((out/'device.csv').read_bytes())
 summary=summarize(out/'combined.csv',args.prt_divider);summary.update(game=game,route=route,markers=bool(mark),started=started,fixture_to_service_seconds=runtime,retrieval_finished_seconds=time.monotonic()-at)
 if game=='nur':summary['logic_submission_split']='unavailable; interleaved'
 expected_source=(0 if route=='legacy' else 1) if mark else 255
 assert summary['source']==expected_source,summary
 for phase in ['snapshot','socket_send']:
  before=json.loads((out/'video-before.json').read_text());after=json.loads((out/'video-after.json').read_text())
  assert next(p['count'] for p in before['phases'] if p['name']==phase)==next(p['count'] for p in after['phases'] if p['name']==phase),'Unexpected browser video work'
 summary['browser_video_work']=False
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
finally:c.lock.close()
