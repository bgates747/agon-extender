#!/usr/bin/env python3
"""Explicit host adapters for the focused rendering qualification master.

Machine identity, frozen session/installer helpers and manifests are supplied
by ignored local configuration and pinned by the master plan. Tests never run
from startup. Session uncertainty stops input; no automatic retry or replay.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import statistics
import math

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests/performance/scan'),str(ROOT/'scripts')]
from records import decode, summary
from window_results import analyse
from run_render_qualification import banner, MODES, CASES
from sdcard import path_payload


def sha(data): return hashlib.sha256(data).hexdigest()
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.new');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)
def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def mode_startup(mode):
    # P4 mode selection belongs in startup, but startup must finish in Legacy.
    # EMOS temporarily routes VDU22 to P4, then closes that display lease.
    return ('SET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\nEMOS LEGACY\r\n'
            'EMOS EXCOM\r\nVDU 22 '+str(mode)+'\r\nEMOS LEGACY --keep-display\r\n').encode()
def directory_closure(files):
    paths=set()
    for entry in files:
        path=Path(entry['remote']).parent
        while str(path) not in ('/agents/extender/results','/extender','/'):
            paths.add(str(path));path=path.parent
    return sorted(paths,key=lambda p:(p.count('/'),p))
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def validate_records(plan,job,raw,windows,initial_display,display):
    """Pure shared validation for serial and later physical-card collection."""
    stable=('mode','width','height','colors','double_buffered','output_width','output_height')
    if not display.get('available') or any(display.get(k)!=initial_display.get(k) for k in stable):
        raise RuntimeError('Display geometry/output changed during workload')
    d=decode(raw)
    if d['case']!=job['case_number'] or d['window_tag']!=job['tag'] or d['count']!=job['frames'] or d['abort'] or d['warmup']!=job['warmup'] or d['build_id']!=plan['fixture_build']:
        raise RuntimeError('Record identity/count/abort mismatch')
    if any(r['flags']&11 for r in d['rows']):raise RuntimeError('Timer/fence/game fault in records')
    calibration=d['calibration_prt']/d['calibration_mos'] if d['calibration_mos'] else 0
    if not 510<=calibration<=690:
        raise RuntimeError('PRT/raw-MOS calibration outside the declared 72k/120Hz tolerance')
    diagnostic_id=job.get('diagnostic_id',job['case_number'])
    hits=[w for w in windows['windows'] if w['id']==diagnostic_id and w['tag']==job['tag']]
    if windows['open'] or windows['overflow'] or windows.get('render_overflow') or len(hits)!=1:
        raise RuntimeError('Missing/overflow/open diagnostic sidecar')
    window=hits[0]
    if window['end_us']<=window['start_us'] or window['render']['boundary_drops']:
        raise RuntimeError('Unclosed or dropped render window')
    if not job['game'] and job['mode']!=136:
        fences=window.get('render_fences',{})
        if (fences.get('count')!=job['frames']+2 or fences.get('pending_requests')!=0 or
            fences.get('errors')!=0 or not fences.get('samples_complete')):
            raise RuntimeError('Finite render fence samples incomplete or not N+2')
    faults=('faults','late','over_budget','underruns','invalid_blocks','sequence_errors','cache_errors','overlap')
    before_rolling=initial_display.get('rolling',{});after_rolling=display.get('rolling',{})
    output_errors={k:after_rolling.get(k,0)-before_rolling.get(k,0) for k in faults}
    if any(v!=0 for v in output_errors.values()):
        raise RuntimeError('HDMI rolling output errors: '+str(output_errors))
    s=analyse(raw,window,diagnostic_id=diagnostic_id)
    s['queued_render']=window['render']
    if not job['game'] and job['mode']!=136:
        cumulative=window['render_fences']['cumulative_render_us']
        if len(cumulative)!=job['frames']+2 or any(b<a for a,b in zip(cumulative,cumulative[1:])):
            raise RuntimeError('Finite cumulative rendering samples are missing or reversed')
        samples=[b-a for a,b in zip(cumulative,cumulative[1:-1])]
        if len(samples)!=job['frames']:raise RuntimeError('Wrong finite update sample count')
        s['finite_render_samples_us']=dict(median=statistics.median(samples),
            p95=sorted(samples)[math.ceil(.95*len(samples))-1],maximum=max(samples),
            count=len(samples),seed_us=cumulative[0],tail_us=cumulative[-1]-cumulative[-2])
    s['rolling_output_errors']=output_errors
    s['queued_render_scope']='Not instrumented for immediate double-buffer drawing' if job['mode']==136 else 'Queued execution wall, excludes parser/UART/pacing/output and native wait'
    return s


class Adapter:
    def __init__(self,path):
        self.path=path.resolve();self.c=json.loads(self.path.read_text())
        self.local=Path(self.c['local']);self.package=Path(self.c.get('package',self.local/'package'))
        self.p=json.loads((self.package/'plan.json').read_text())
        self.m=module(Path(self.c['session_module']),'render_mode_session')
        self.b=self.m.bench(Path(self.c['session_config']))
        self.state_path=self.local/'adapter-state.json'
        self.state=json.loads(self.state_path.read_text()) if self.state_path.exists() else {}

    def close(self): self.b.close_host()
    def save(self): dump(self.state_path,self.state)
    def checked(self): self.m.online(self.b.config);self.m.neutral(self.b.config)

    def admit(self,evidence,confirmed_cli=False):
        """Reuse an idle listener or start one from the operator-confirmed CLI."""
        self.m.neutral(self.b.config)
        status=self.m.get(self.b.config,'/sd/status')
        if status['pending']:raise RuntimeError('SD operation pending; preserve session and stop')
        if status['online']:
            self.b.fast_connect()
        else:
            if not confirmed_cli:raise RuntimeError('Offline listener requires operator-confirmed CLI')
            journal=self.b.state.get('fast_journal')
            if journal:
                prior=json.loads(Path(journal).read_text())
                if prior['pending']:raise RuntimeError('Uncertain SD request; preserve journal and stop')
            # A stopped listener invalidates its session. Preserve that journal;
            # bind the authority only after a fresh startup read and positive EXIT.
            self.b.key_command('EMOS LEGACY');time.sleep(1)
            self.b.key_command('EMOS sdserve --fast /')
            self.m.wait_listener(self.b.config,15)
            c=self.m.SDClient(self.b.config['p4'],evidence/'admission-session.json')
            try:
                c.connect();startup=c.download('/autoexec.txt')
                if any(line.strip().upper().startswith(('LOAD ','RUN','EXEC ')) for line in startup.decode().splitlines()):
                    raise RuntimeError('Startup launches an application; stop admission')
                c.rpc(11)
            finally:c.lock.close()
            if self.m.get(self.b.config,'/sd/status')['online']:
                raise RuntimeError('Admission EXIT did not return CLI')
            self.b.state.pop('fast_journal',None)
            self.b.state['np01_acknowledged_exit']=utc()
            self.b.state['current_sha256']=sha(startup);self.b.save()
            self.b.fast_start()
        self.checked()
        self.b.fast_read('/autoexec.txt')
        dump(evidence/'admission.json',dict(validated=True,bench_idle=True,
             listener_online=True,neutral_input=True,verified_utc=utc()))

    def replace_startup(self,desired,backup,local_backup):
        """Keep the old startup present until listener transaction activation.

        The inherited MOS RENAME recipe removed autoexec before re-admitting
        the listener. A lost handback then left reset without input bootstrap.
        Use the listener's existing staged replacement and retained backup;
        uncertain activation still stops with its exact journal preserved.
        """
        old=self.b.fast_read('/autoexec.txt')
        if old==desired:return
        if local_backup.exists() and local_backup.read_bytes()!=old:
            raise RuntimeError('Prior startup evidence differs')
        local_backup.write_bytes(old)
        self.m.new_file(self.b,backup,old)
        if self.b.fast_read(backup)!=old:raise RuntimeError('Startup archive readback differs')
        for suffix in ('.p17part','.p17meta','.p17bak'):
            if not self.m.absent(self.b,'/autoexec.txt'+suffix):
                raise RuntimeError('Startup recovery sibling exists; preserve and inspect')
        c=self.b.fast_connect()
        c.upload('/autoexec.txt',desired,True,fast=True)
        if self.b.fast_read('/autoexec.txt')!=desired:
            raise RuntimeError('Activated startup readback differs; backup retained')
        if self.b.fast_read('/autoexec.txt.p17bak')!=old:
            raise RuntimeError('Startup transaction backup differs; preserve recovery files')
        c.rpc(10,b'\x03'+path_payload('/autoexec.txt'))

    def stage(self,finish=False):
        self.checked()
        if self.state.get('staged'):raise RuntimeError('Already staged; no replay')
        # Stage only this frozen campaign. The existing listener's directory
        # RPC is unavailable, so one admitted MOS batch makes fresh directories.
        for e in self.p['files']:
            raw=(self.package/e['local']).read_bytes()
            if sha(raw)!=e['sha256']:raise RuntimeError('Changed prepared payload')
        verification=self.local/'resident-assets-verified.json'
        if verification.exists():
            retained=json.loads(verification.read_text())
            if retained.get('assets')!=self.p['resident_assets'] or not retained.get('verified'):
                raise RuntimeError('Retained asset verification does not match this package')
        else:
            for e in self.p['resident_assets']:
                if sha(self.b.fast_read(e['path']))!=e['sha256']:raise RuntimeError('Resident game asset differs')
            dump(verification,dict(verified=True,assets=self.p['resident_assets'],verified_utc=utc(),
                                   scope='Full on-card reads; root retains exclusive bench ownership'))
        self.m.ensure_dir(self.b,self.p['remote'])
        directories=directory_closure(self.p['files'])
        # Existing support parents are deliberately not recreated by this batch.
        if not finish:
            lines=[]
            for d in directories:
                if self.m.absent(self.b,d):lines.append('MKDIR '+d)
                elif not self.b.fast_connect().stat_entry(d)[1]&16:raise RuntimeError('Parent path is a file')
            lines+=['CD /','EMOS sdserve --fast /']
            batch=self.p['remote']+'/mkdir-'+dt.datetime.now(dt.timezone.utc).strftime('%H%M%S')+'.txt'
            raw=('\r\n'.join(lines)+'\r\n').encode()
            self.m.new_file(self.b,batch,raw)
            if self.b.fast_read(batch)!=raw:raise RuntimeError('Directory batch readback differs')
            dump(self.local/'directory-batch.json',dict(command='EXEC '+batch,directories=directories,invocation_utc=utc()))
            self.b.fast_exit();self.b.key_command('EXEC '+batch)
            self.m.wait_listener(self.b.config,300)
        # --finish-stage is a separate explicit operation: observe the actual
        # admitted listener and every completed directory, without replaying
        # a batch whose earlier observation window elapsed.
        for d in directories:
            if not self.b.fast_connect().stat_entry(d)[1]&16:raise RuntimeError('Directory batch incomplete')
        for index,e in enumerate(self.p['files']):
            raw=(self.package/e['local']).read_bytes()
            self.m.new_file(self.b,e['remote'],raw)
            if sha(self.b.fast_read(e['remote']))!=e['sha256']:raise RuntimeError('Staged readback differs')
            if index%25==0:print('Verified payload',index+1,'/',len(self.p['files']),flush=True)
        self.state['original_startup_sha256']=sha(self.b.fast_read('/autoexec.txt'))
        (self.local/'original-autoexec.txt').write_bytes(self.b.fast_read('/autoexec.txt'))
        self.state.update(staged=True,staged_utc=utc(),plan_sha256=sha((self.package/'plan.json').read_bytes()))
        self.save()

    def select_renderer(self,renderer):
        label=self.c['renderers'][renderer]['label']
        installer=Path(self.c['installer'])
        if self.state.get('renderer')==renderer:
            record=json.loads(Path(self.c['installed_record']).read_text())
            if record['application_sha256']!=self.state['app_sha256']:raise RuntimeError('Installed firmware changed')
            return
        # The reviewed installer itself validates clean source, manifests,
        # non-NVS segments, independent readback and actual CLI/read/EXIT.
        self.b.fast_exit();self.b.key_command('VDU 12');self.b.fast_start()
        self.close()
        runid='mq-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+label
        subprocess.run([sys.executable,str(installer),label,'--run-id',runid],cwd=ROOT,check=True)
        record=json.loads(Path(self.c['installed_record']).read_text())
        identity=json.loads(Path(record['identity']).read_text())
        if identity['app_sha256']!=self.c['renderers'][renderer]['app_sha256']:
            raise RuntimeError('Installer returned a different selected image')
        self.b=self.m.bench(Path(self.c['session_config']));self.b.fast_start()
        self.state.update(renderer=renderer,app_sha256=identity['app_sha256'],identity=str(record['identity']))
        self.state.pop('selected_mode',None);self.save()

    def mode(self,mode,evidence):
        self.checked()
        display=self.m.get(self.b.config,'/display/status')
        startup=self.b.fast_read('/autoexec.txt')
        desired=mode_startup(mode)
        if display.get('available') and display['mode']==mode and startup==desired:
            self.state['selected_mode']=mode;self.save();return
        if any(s.strip().upper().startswith(('LOAD ','RUN','EXEC ')) for s in startup.decode().splitlines()):
            raise RuntimeError('Startup would launch an application')
        backup=self.p['remote']+'/startup-'+dt.datetime.now(dt.timezone.utc).strftime('%H%M%S')+'.txt'
        self.replace_startup(desired,backup,evidence/'prior-startup.txt')
        if self.b.fast_read('/autoexec.txt')!=desired:raise RuntimeError('Mode startup readback differs')
        self.b.state['current_sha256']=sha(desired);self.b.save()
        self.b.fast_exit()
        with (evidence/'mode-reset.log').open('x') as f:
            subprocess.run([sys.executable,str(ROOT/'scripts/reset_agon.py'),'--config',self.c['reset_config'],
                            '--local','--verify-url',self.b.config['p4']],stdout=f,stderr=subprocess.STDOUT,check=True)
        self.b.fast_start()
        if self.b.fast_read('/autoexec.txt')!=desired:raise RuntimeError('Post-boot CLI/read proof differs')
        actual=self.m.get(self.b.config,'/display/status');w,h,c,db=self.p['geometries'][str(mode)]
        if not actual.get('available') or tuple(actual[k] for k in ('mode','width','height','colors','double_buffered'))!=(mode,w,h,c,db):
            raise RuntimeError('Post-boot display geometry mismatch')
        dump(evidence/'mode-display.json',actual)
        self.state['selected_mode']=mode;self.save()

    def run(self,job_id,receipt,evidence):
        if not self.state.get('staged'):raise RuntimeError('Campaign not staged')
        if self.state.get('plan_sha256')!=sha((self.package/'plan.json').read_bytes()):
            raise RuntimeError('Staging receipt belongs to a different package')
        job=next(j for j in self.p['jobs'] if j['id']==job_id)
        if receipt.exists():raise RuntimeError('Receipt already exists; no replay')
        self.select_renderer(job['renderer']);self.mode(job['mode'],evidence);self.checked()
        if not self.m.absent(self.b,job['result']):raise RuntimeError('Result already exists; no replay')
        expected=(self.package/job['config_local']).read_bytes()
        if self.b.fast_read(job['config_remote'])!=expected:raise RuntimeError('Job config readback differs')
        before=self.m.get(self.b.config,'/diagnostics/render-benchmark')
        if before['open']:raise RuntimeError('Previous render window unresolved')
        initial_display=self.m.get(self.b.config,'/display/status')
        dump(evidence/'before-display.json',initial_display)
        self.b.fast_exit();started=time.monotonic()
        dump(evidence/'invocation.json',dict(job=job,invoked_utc=utc(),identity=self.state['identity']))
        self.b.key_command('EXEC '+job['command_remote'])
        # A missing handback preserves the application; never reset/replay.
        self.m.wait_listener(self.b.config,240 if job['game'] else 90)
        windows=self.m.get(self.b.config,'/diagnostics/render-benchmark')
        display=self.m.get(self.b.config,'/display/status')
        dump(evidence/'windows.json',windows);dump(evidence/'after-display.json',display)
        result={k:job[k] for k in ('id','renderer','mode','case','repeat')}
        result.update(bench_idle=True,safe_to_continue=True,validated=False,ended_utc=utc(),
                      execution_seconds=time.monotonic()-started,identity=self.state['identity'])
        if self.c.get('collection')=='physical-card' and not job.get('smoke'):
            # The host retains every transient P4 sidecar before the next job.
            # CLI handback proves execution returned, not raw-data validity.
            result.update(collection_pending=True,result_remote=job['result'],
                          sidecar_sha256={name:sha((evidence/name).read_bytes()) for name in
                              ('invocation.json','windows.json','before-display.json','after-display.json')},
                          actual_render_storage=display.get('render_storage'),
                          output_geometry=[display.get('output_width'),display.get('output_height')])
            dump(receipt,result)
            return 0
        try:
            raw=self.b.fast_read(job['result']);(evidence/'records.bin').write_bytes(raw)
            s=validate_records(self.p,job,raw,windows,initial_display,display)
            dump(evidence/'summary.json',s)
            result.update(validated=True,raw_sha256=sha(raw),trajectory_sha256=s['trajectory_sha256'],
                          actual_render_storage=display.get('render_storage'),
                          output_geometry=[display.get('output_width'),display.get('output_height')])
        except Exception as error:
            result['error']=str(error)
        dump(receipt,result)
        return 0 if result['validated'] else 1

    def park(self,evidence):
        """Restore ordinary boot and acknowledge EXIT before operator card removal."""
        self.checked()
        original=(self.local/'original-autoexec.txt').read_bytes()
        backup=self.p['remote']+'/collection-startup-'+dt.datetime.now(dt.timezone.utc).strftime('%H%M%S%f')+'.txt'
        self.replace_startup(original,backup,evidence/'prior-startup.txt')
        if self.b.fast_read('/autoexec.txt')!=original:raise RuntimeError('Collection startup restoration failed')
        self.b.state['current_sha256']=sha(original);self.b.save()
        self.b.fast_exit();self.m.neutral(self.b.config)
        dump(evidence/'collection-handback.json',dict(verified_utc=utc(),original_startup_restored=True,
             listener_exited=True,bench_idle=True,raw_validation_pending=True,success_displayed=False))

    def notify(self,success,evidence):
        self.checked()
        original=(self.local/'original-autoexec.txt').read_bytes()
        backup=self.p['remote']+'/final-startup.txt'
        self.replace_startup(original,backup,evidence/'prior-startup.txt')
        if self.b.fast_read('/autoexec.txt')!=original:raise RuntimeError('Final startup restoration failed')
        self.b.state['current_sha256']=sha(original);self.b.save()
        target=self.p['remote']+('/success.txt' if success else '/errors.txt')
        # Draw the cue into both banks. The pixel-based text reader may inspect
        # the current drawing bank, while HDMI presents the other bank.
        # One CLI batch supplies positive listener handback after both draws;
        # no guessed delay is used as proof of command completion.
        batch=self.p['remote']+'/final-notice.txt'
        raw=('EMOS EXCOM --keep-display\r\nVDU 23 1 0\r\nVDU 20\r\nVDU 19 1 48 0 0 0\r\n'
             'VDU 19 2 12 0 0 0\r\nVDU 19 7 63 0 0 0\r\nEXEC '+target+'\r\nEXEC '+target+
             '\r\nEMOS LEGACY --keep-display\r\nEMOS sdserve --fast /\r\n').encode()
        self.m.new_file(self.b,batch,raw)
        self.b.fast_exit();self.b.key_command('EXEC '+batch)
        self.m.wait_listener(self.b.config,60)
        with (evidence/'screen-text.txt').open('x') as f:
            subprocess.run([sys.executable,str(ROOT/'scripts/screen_text.py'),'--url',self.b.config['p4']],stdout=f,check=True)
        expected='ALL TESTS COMPLETE SUCCESS' if success else 'TESTS COMPLETE WITH ERRORS'
        if expected not in (evidence/'screen-text.txt').read_text():raise RuntimeError('Final banner text not verified')
        self.b.fast_exit();self.m.neutral(self.b.config)
        dump(evidence/'notification.json',dict(success=success,message=expected,original_startup_restored=True,
                                             screen_text_verified=True,actual_CLI_handback=True,finished_utc=utc()))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True)
    sub=p.add_subparsers(dest='action',required=True);q=sub.add_parser('stage');q.add_argument('--finish-stage',action='store_true')
    q=sub.add_parser('run');q.add_argument('--id',required=True);q.add_argument('--receipt',type=Path,required=True);q.add_argument('--evidence',type=Path,required=True)
    q=sub.add_parser('notify');q.add_argument('--status',choices=('success','errors'),required=True);q.add_argument('--evidence',type=Path,required=True)
    q=sub.add_parser('park');q.add_argument('--evidence',type=Path,required=True)
    q=sub.add_parser('admit');q.add_argument('--evidence',type=Path,required=True);q.add_argument('--confirmed-cli',action='store_true')
    a=p.parse_args();adapter=Adapter(a.config)
    try:
        if a.action=='stage':adapter.stage(a.finish_stage);return 0
        if a.action=='run':return adapter.run(a.id,a.receipt,a.evidence)
        a.evidence.mkdir(parents=True,exist_ok=False)
        if a.action=='admit':adapter.admit(a.evidence,a.confirmed_cli)
        elif a.action=='park':adapter.park(a.evidence)
        else:adapter.notify(a.status=='success',a.evidence)
        return 0
    finally:adapter.close()


if __name__=='__main__':raise SystemExit(main())
