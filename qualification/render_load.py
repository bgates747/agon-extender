#!/usr/bin/env python3
"""Frozen render-load-r04 bench runner; explicit operations, no uncertain replay.

Addresses/GPIO mapping are supplied by an ignored local JSON configuration.
External SD jobs run only at admitted CLI; measured applications exclude them.
"""
import argparse, datetime, hashlib, importlib.util, json, subprocess, sys, time
import urllib.error, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HOST_SOURCE_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'tests/performance/render_load'))
from codec import plan,decode
from generate import MODES
sys.path.insert(0,str(ROOT/'scripts'))
from sdcard import Client as SDClient,RemoteError

def digest(b):return hashlib.sha256(b).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
class Bench:
    def __init__(self,config,evidence):
        self.config=json.loads(config.read_text());self.evidence=evidence;evidence.mkdir(parents=True,exist_ok=True)
        self.events=json.loads((evidence/"requests.json").read_text()) if (evidence/"requests.json").exists() else [];self.state_path=evidence/'state.json'
        self.state=json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        self.sd=None
    def fast_connect(self):
        if self.sd is None:
            journal=Path(self.state.get('fast_journal',str(self.evidence/('fast-session-'+utc()+'.json'))))
            self.sd=SDClient(self.config['p4'],journal);self.sd.connect()
            self.state['fast_journal']=str(journal);self.save()
        return self.sd
    def key_command(self,command):
        subprocess.run([sys.executable,str(ROOT/'scripts/keyboard.py'),'--url',self.config['p4'],'--state',str(self.evidence/'keyboard.json'),'type',command,'--enter'],check=True,timeout=15,stdout=subprocess.DEVNULL)
    def fast_start(self):
        # Call only at a CLI established by a completed finite metadata job or
        # the foreground listener's successful EXIT, never a running fixture.
        self.key_command('EMOS LEGACY')
        time.sleep(1)
        self.key_command('EMOS sdserve --fast /')
        # This explicit start creates a new listener incarnation. Retain any
        # old journal as evidence, but never bind its SID/boot to the new one.
        if self.sd:self.sd.lock.close();self.sd=None
        self.state.pop('fast_journal',None);self.save()
        limit=time.monotonic()+10
        while time.monotonic()<limit:
            with urllib.request.urlopen(self.config['p4']+'/sd/status',timeout=3) as r:s=json.load(r)
            if s['online']:return self.fast_connect()
            time.sleep(.2)
        raise RuntimeError('fast listener did not start')
    def fast_exit(self):
        c=self.fast_connect();c.rpc(11);c.lock.close();self.sd=None
        self.state.pop('fast_journal',None);self.save()
        time.sleep(1)
        with urllib.request.urlopen(self.config['p4']+'/sd/status',timeout=3) as r:s=json.load(r)
        if s['online']:raise RuntimeError('foreground listener did not exit')
    def fast_read(self,path):return self.fast_connect().download(path)
    def fast_put_new(self,path,data):
        c=self.fast_connect()
        try:c.stat_entry(path)
        except RemoteError as e:
            if e.status!=6 or e.detail not in (b'\x04',b'\x05'):raise
        else:raise RuntimeError(('target not absent',path))
        t=time.monotonic();c.upload(path,data,True,fast=True);upload=time.monotonic()-t
        t=time.monotonic();got=c.download(path);readback=time.monotonic()-t
        if got!=data:raise RuntimeError(('fast upload readback differs',path))
        self.events.append({'utc':utc(),'operation':'fast-upload','path':path,'bytes':len(data),'sha256':digest(data),'upload_seconds':upload,'single_readback_seconds':readback});self.save()
    def save(self):
        self.state_path.write_text(json.dumps(self.state,indent=2)+'\n')
        (self.evidence/'requests.json').write_text(json.dumps(self.events,indent=2)+'\n')
    def request(self,method,path,data=None,headers=None,timeout=600):
        time.sleep(1.5) # EMOS finite SD job exits before the next admission.
        t=time.monotonic();url=self.config['dav']+path
        try:
            with urllib.request.urlopen(urllib.request.Request(url,data=data,method=method,headers=headers or {}),timeout=timeout) as r:status=r.status;body=r.read()
        except urllib.error.HTTPError as e:status=e.code;body=e.read()
        self.events.append({'utc':utc(),'method':method,'path':path,'status':status,'seconds':time.monotonic()-t,'bytes':len(body),'sha256':digest(body)})
        self.save();return status,body
    def read(self,path):
        s,b=self.request('GET',path)
        if s!=200:raise RuntimeError(('GET',path,s,b[:500]))
        return b
    def absent(self,path):
        s,b=self.request('HEAD',path)
        if s!=404:raise RuntimeError(('target not absent',path,s,b[:500]))
    def put_new(self,path,data):
        self.absent(path);s,b=self.request('PUT',path,data)
        if s not in (200,201,204):raise RuntimeError(('PUT failed; do not replay',path,s,b[:500]))
        if self.read(path)!=data:raise RuntimeError(('readback differs',path))
    def mkdir(self,path):
        s,b=self.request('MKCOL',path)
        if s not in (200,201,204):raise RuntimeError(('MKCOL',path,s,b[:500]))
    def move(self,src,dst):
        self.absent(dst);s,b=self.request('MOVE',src,headers={'Destination':self.config['dav']+dst,'Overwrite':'F'})
        if s not in (200,201,204):raise RuntimeError(('MOVE failed; do not replay',src,dst,s,b[:500]))
    def preserve(self):
        if 'original_sha256' in self.state:return
        b=self.fast_read('/autoexec.txt');(self.evidence/'original-autoexec.txt').write_bytes(b)
        self.state.update(original_sha256=digest(b),current_sha256=digest(b),startup_index=0);self.save()
    def startup(self,b):
        self.preserve()
        if digest(self.fast_read('/autoexec.txt'))!=self.state['current_sha256']:raise RuntimeError('startup changed outside this runner')
        self.fast_exit()
        # A previous closeout flag must not survive a new startup mutation.
        # Restoration is confirmed separately after image/startup verification.
        self.state['restored']=False;self.save()
        old=self.config['results_root']+f"/startup-{self.state['startup_index']:03}.txt"
        self.move('/autoexec.txt',old)
        self.state['startup_index']+=1;self.state['startup_missing']=True;self.save()
        self.fast_start();self.fast_put_new('/autoexec.txt',b)
        self.state['current_sha256']=digest(b);self.state['startup_missing']=False;self.save()
    def reset(self):
        t=time.monotonic()
        subprocess.run([sys.executable,str(ROOT/'scripts/reset_agon.py'),'--config',self.config['reset_config'],'--local'],check=True,timeout=15)
        return time.monotonic()-t
    def confirm_p4_fixture_cli(self,out):
        # A direct startup ExCom switch has no prior Legacy capability grant.
        # Automatic WebDAV then returns503 even at CLI (EMOS5.5-era admission
        # contract). Rendered error/prompt text supplies positive CLI evidence;
        # keyboard readiness or a closed drawing window alone is insufficient.
        for _ in range(30):
            try:
                with urllib.request.urlopen(self.config['p4']+'/screen/text',timeout=4) as r:
                    status=r.status;raw=r.read()
            except urllib.error.HTTPError as e:
                if e.code!=409:raise
            else:
                if status==200:
                    (out/'cli-screen.txt').write_bytes(raw)
                    text=raw.decode('utf-8',errors='replace')
                    return ('Error executing autoexec.txt at line 7' in text and
                            'BENCH-009 ' in text and '*' in text)
            time.sleep(.2)
        return False
    def run(self,mode,endpoint,first,end,wait_seconds,deadline,variant,interval=10,last_key='space',manual=False,disable_timing=False,suite=None,pass_number=0,control_context=None,window_relative=False):
        if window_relative and (endpoint!='p4' or manual or disable_timing):
            raise ValueError('Window-relative timing requires a measured scripted P4 invocation')
        telemetry_required=self.config.get('require_benchmark_telemetry',True)
        if not telemetry_required:
            # Only the separately identified hook-free control may omit windows.
            # Scheduled comparisons still require real correlated P4 telemetry.
            if not (endpoint=='p4' and variant=='normal' and disable_timing and suite=='presentation-no-hook-controls-r04'):
                raise ValueError('Missing P4 windows is permitted only for the identified hook-free presentation control')
            installed=json.loads(Path(self.config['installation_record']).read_text())
            if installed['variant']!='ordinary-hdmi':raise RuntimeError('Hook-free control requires verified ordinary HDMI image')
            try:
                with urllib.request.urlopen(self.config['p4']+'/diagnostics/render-benchmark',timeout=5) as r:r.read()
            except urllib.error.HTTPError as e:
                if e.code!=404:raise
            else:raise RuntimeError('Diagnostic window endpoint remains present in hook-free control')
        stamp=utc();run_id='BENCH-009-'+stamp;out=self.evidence/run_id;out.mkdir()
        remote=self.config['results_root']+'/'+run_id
        prep=time.monotonic();self.fast_exit()
        self.mkdir(remote)
        self.fast_start()
        tag=int.from_bytes(hashlib.sha256(run_id.encode()).digest()[:3],'little')
        p=plan(self.config.get('data_path',self.config['fixture_root']+f'/data{mode}'+self.config.get('data_suffix','.rle')),remote+'/results.bin',mode,MODES[mode],tag,first,end,disable_timing)
        self.fast_put_new(remote+'/plan.bin',p)
        startup=('SET KEYBOARD 1\nEMOS KEYINPUT extender\nEMOS '+('LEGACY' if endpoint=='mainboard' else 'EXCOM')+'\nVDU 22 '+str(mode)+'\nCD '+remote+'\nLOAD '+self.config['fixture_root']+'/'+self.config.get('fixture_name','benchmark-r04.bin')+'\nRUN .\nCD /\nEMOS LEGACY\nEMOS sdserve --fast /\n').encode('ascii')
        self.startup(startup)
        meta={'run_id':run_id,'mode':mode,'endpoint':endpoint,'variant':variant,'first':first,'end':end,'tag':tag,'startup_sha256':digest(startup),'plan_sha256':digest(p),'expected_cases':end-first,'case_interval_seconds':interval,'initial_wait_seconds':wait_seconds,'clock_units':{'prt_hz_nominal':72000,'mos_raw_hz_at_60':120},'outcome':'partial'}
        meta['disable_timing']=disable_timing
        if window_relative:
            meta['key_schedule']='wall clock after observing each correlated open measurement window'
            meta['window_seconds']=interval
        meta['telemetry_required']=telemetry_required
        meta['host_runner_sha256']=HOST_SOURCE_SHA256
        if control_context:meta['control_context']=control_context
        if suite:meta.update(suite=suite,pass_number=pass_number)
        if 'fixture_manifest' in self.config:
            meta['fixture']=json.loads(Path(self.config['fixture_manifest']).read_text())
        current=Path(self.config['installation_record']) if 'installation_record' in self.config else None
        if current and current.exists():meta['p4_installation']=json.loads(current.read_text())
        (out/'run.json').write_text(json.dumps(meta,indent=2)+'\n');(out/'startup.txt').write_bytes(startup);(out/'plan.bin').write_bytes(p)
        self.fast_exit();meta['preparation_seconds']=time.monotonic()-prep
        (out/'run.json').write_text(json.dumps(meta,indent=2)+'\n')
        t=time.monotonic();meta['reset_seconds']=self.reset();print('RUN '+run_id+' '+endpoint+' mode'+str(mode)+' '+variant,flush=True)
        if manual:
            meta['outcome']='interactive';meta['controls']={'next':'Space','exit':'Escape'}
            (out/'run.json').write_text(json.dumps(meta,indent=2)+'\n')
            print('Indefinite visual run: Space advances; Escape exits. No scripted keys scheduled.',flush=True)
            return out
        # No SD transfers during drawing. Read-only eligibility and admitted
        # keyboard requests occur at transitions and are retained in evidence.
        transitions=[]
        for i in range(end-first):
            observed=None
            if window_relative:
                # RGB-001 subset: exclude variable boot/load time from the key
                # schedule. The original fixture and VDU bytes are unchanged.
                # A short measured window still yields >=64 paced frames and
                # avoids filling the fixture's finite sample record allocation.
                opening_limit=time.monotonic()+60
                while time.monotonic()<opening_limit:
                    with urllib.request.urlopen(self.config['p4']+'/diagnostics/render-benchmark',timeout=4) as r:
                        active=json.load(r)
                    match=[w for w in active['windows'] if w['tag']==tag and w['id']==first+i and not w['end_us']]
                    if len(match)==1:
                        observed=time.monotonic();break
                    time.sleep(.2)
                else:raise RuntimeError(('correlated fixture window did not open',run_id,first+i))
                due=observed+interval
            else:due=t+wait_seconds+i*interval
            time.sleep(max(0,due-time.monotonic()))
            # Listener online proves fixture return; never send a stray Space
            # to a completed application's caller/CLI.
            with urllib.request.urlopen(self.config['p4']+'/sd/status',timeout=3) as r:listener=json.load(r)
            if listener['online']:break
            eligible,_=self.request('HEAD',remote+'/results.bin',timeout=5)
            if eligible in (200,404):
                # A finite metadata request was admitted at CLI: RUN returned
                # early and its nonzero exit stopped the remaining autoexec.
                meta['early_cli_return']=True;self.fast_start();break
            if eligible!=503:raise RuntimeError(('unexpected fixture eligibility',eligible))
            if endpoint=='p4' and telemetry_required:
                # ExCom may refuse SD admission even after a fixture error.
                # Check closed tagged windows before sending another key, then
                # require rendered error/prompt evidence to establish CLI.
                with urllib.request.urlopen(self.config['p4']+'/diagnostics/render-benchmark',timeout=4) as r:closed=json.load(r)
                active=[w for w in closed['windows'] if w['tag']==tag]
                if not closed['open'] and all(w['end_us'] for w in active) and self.confirm_p4_fixture_cli(out):
                    meta['early_cli_return']=True;meta['cli_evidence']='rendered benchmark error and MOS prompt'
                    self.fast_start();break
            before=time.monotonic()
            key=last_key if i==end-first-1 else 'space'
            subprocess.run([sys.executable,str(ROOT/'scripts/keyboard.py'),'--url',self.config['p4'],'--state',str(self.evidence/'keyboard.json'),'key',key],check=True,timeout=15,stdout=subprocess.DEVNULL)
            transition={'ordinal':i,'key':key,'scheduled_seconds':due-t,'sent_seconds':before-t,'completed_seconds':time.monotonic()-t}
            if observed is not None:transition['window_observed_seconds']=observed-t
            transitions.append(transition)
            (out/'transitions.json').write_text(json.dumps(transitions,indent=2)+'\n')
            if (i+1)%10==0 or i==end-first-1:
                print('TRANSITIONS '+run_id+' '+str(i+1)+'/'+str(end-first),flush=True)
        limit=t+deadline
        while True:
            with urllib.request.urlopen(self.config['p4']+'/sd/status',timeout=3) as r:listener=json.load(r)
            if listener['online']:break
            eligible,_=self.request('HEAD',remote+'/results.bin',timeout=5)
            if eligible in (200,404):meta['early_cli_return']=True;self.fast_start();break
            if endpoint=='p4' and telemetry_required and eligible==503:
                with urllib.request.urlopen(self.config['p4']+'/diagnostics/render-benchmark',timeout=4) as r:closed=json.load(r)
                active=[w for w in closed['windows'] if w['tag']==tag]
                if not closed['open'] and all(w['end_us'] for w in active) and self.confirm_p4_fixture_cli(out):
                    meta['early_cli_return']=True;meta['cli_evidence']='rendered benchmark error and MOS prompt';self.fast_start();break
            if time.monotonic()>limit:raise RuntimeError(('fixture did not return to foreground listener',run_id))
            time.sleep(2)
        meta['startup_fixture_return_seconds']=time.monotonic()-t
        (out/'run.json').write_text(json.dumps(meta,indent=2)+'\n')
        # Preserve windows before potentially lengthy SD retrieval, so a later
        # retrieval fault cannot erase the already completed measurement.
        if endpoint=='p4' and telemetry_required:
            with urllib.request.urlopen(self.config['p4']+'/diagnostics/render-benchmark',timeout=10) as r:telemetry_bytes=r.read()
            (out/'telemetry.json').write_bytes(telemetry_bytes)
        if self.config.get('defer_result_retrieval',False):
            # Author-selected local-card collection. The resident fixture has
            # returned; inspect only tiny file metadata, retaining its complete
            # samples on SD. Minimum-frame/record validity is established later
            # by the local collector, never inferred from a closed P4 window.
            if endpoint=='p4' and telemetry_required:
                telemetry=json.loads(telemetry_bytes)
                windows=[w for w in telemetry['windows'] if w['tag']==tag]
                meta['telemetry_cases']=len(windows)
                meta['telemetry_closed']=all(w['end_us'] for w in windows)
                if len(windows)!=end-first or not meta['telemetry_closed'] or telemetry['overflow']:
                    raise RuntimeError('Deferred run has incomplete/invalid P4 windows')
            files={}
            for name in ('results.bin','failure.bin'):
                try:size,attributes=self.fast_connect().stat_entry(remote+'/'+name)
                except RemoteError as error:
                    if error.status!=6 or error.detail not in (b'\x04',b'\x05'):raise
                else:files[name]={'bytes':size,'attributes':attributes}
            if not files:raise RuntimeError('Fixture returned without any result/failure file')
            meta.update(outcome='measured-awaiting-local-results',result_retrieval='deferred-sd-mount',
                        sd_results_path=remote+'/results.bin',sd_failure_path=remote+'/failure.bin',
                        sd_files=files,validation_pending='Decode local SD files; require >=64 valid frames and no truncation',
                        finished_utc=utc())
            (out/'run.json').write_text(json.dumps(meta,indent=2)+'\n')
            print('RESULTS RETAINED ON SD '+run_id,flush=True)
            return out
        retrieval=time.monotonic();self.fast_connect()
        try:
            b=self.fast_read(remote+'/results.bin')
        except RemoteError as e:
            try:fb=self.fast_read(remote+'/failure.bin')
            except RemoteError:raise e
            (out/'failure.bin').write_bytes(fb);meta['outcome']='fail';meta['failure']='fixture error receipt'
            (out/'run.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True);return out
        else:
                (out/'results.bin').write_bytes(b);result=decode(b);(out/'decoded.json').write_text(json.dumps(result,indent=2)+'\n')
                if (result['mode'],result['tag'],result['width'],result['height'])!=(mode,tag,MODES[mode][0],MODES[mode][1]):raise RuntimeError('result mode/tag/geometry mismatch')
                ids=[c['id'] for c in result['cases']]
                if ids!=list(range(first,first+len(ids))) or len(ids)>end-first:raise RuntimeError('result case selection/order mismatch')
                if 'fixture' in meta and result['build_id']!=meta['fixture']['build_id']:raise RuntimeError('installed fixture build identity mismatch')
                meta['returned_cases']=len(result['cases']);meta['bad_frames']=sum(f['status']!=0 for c in result['cases'] for f in c['frames']);meta['result_sha256']=digest(b)
                meta['short_cases']=[c['id'] for c in result['cases'] if c['total_frames']<64]
                meta['truncated_cases']=[c['id'] for c in result['cases'] if c['truncated']]
                meta['outcome']='pass' if len(result['cases'])==end-first and not meta['bad_frames'] and not meta['short_cases'] and not meta['truncated_cases'] else 'partial'
                if meta['outcome']!='pass':
                    try:failed=self.fast_read(remote+'/failure.bin')
                    except RemoteError as e:
                        if e.status!=6 or e.detail not in (b'\x04',b'\x05'):raise
                    else:
                        (out/'failure.bin').write_bytes(failed);meta['outcome']='fail';meta['failure_code']=failed[19]
        meta['retrieval_seconds']=time.monotonic()-retrieval
        if endpoint=='p4' and telemetry_required:
            telemetry=json.loads(telemetry_bytes);windows=[w for w in telemetry['windows'] if w['tag']==tag]
            meta['telemetry_cases']=len(windows);meta['telemetry_closed']=all(w['end_us'] for w in windows)
            if len(windows)!=end-first or not meta['telemetry_closed'] or telemetry['overflow']:meta['outcome']='invalid'
        (out/'run.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True);return out
    def restore(self):
        b=(self.evidence/'original-autoexec.txt').read_bytes()
        assert digest(b)==self.state['original_sha256']
        self.startup(b);self.fast_exit();self.reset();self.state['restored']=True;self.save()
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True)
    s=p.add_subparsers(dest='action',required=True)
    s.add_parser('preserve');s.add_parser('restore')
    r=s.add_parser('run');r.add_argument('--mode',type=int,choices=MODES,required=True);r.add_argument('--endpoint',choices=('mainboard','p4'),required=True);r.add_argument('--variant',choices=('normal','hold','off'),default='normal');r.add_argument('--first',type=int,default=0);r.add_argument('--end',type=int,default=94);r.add_argument('--wait',type=float,default=20);r.add_argument('--deadline',type=float,default=1100);r.add_argument('--interval',type=float,default=10);r.add_argument('--last-key',choices=('space','escape'),default='space');r.add_argument('--manual',action='store_true',help='Leave each case running until operator Space/Escape; schedule no automatic keys');r.add_argument('--disable-timing',action='store_true',help='Retain bounded fence watchdog and drawing bytes, suppress measurement probes for recovery controls')
    b=Bench(p.parse_args().config,p.parse_args().evidence);a=p.parse_args()
    if a.action=='run':b.run(a.mode,a.endpoint,a.first,a.end,a.wait,a.deadline,a.variant,a.interval,a.last_key,a.manual,a.disable_timing)
    else:getattr(b,a.action)()
if __name__=='__main__':main()
