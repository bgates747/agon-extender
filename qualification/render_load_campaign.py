#!/usr/bin/env python3
"""Run frozen paired passes; preserve faults and continue after known recovery.

Firmware selection remains an explicit outer operation. This controller never
chooses or flashes an image. An optional, exact P4 reset command comes from the
ignored bench configuration. Recovery uses the fixture's existing-result guard;
it never deletes results or repeats an uncertain SD mutation.
"""
import argparse,hashlib,json,subprocess,sys,time,traceback,urllib.request
from pathlib import Path
from render_load import Bench,utc
ROOT=Path(__file__).resolve().parents[1]
HOST_SOURCE_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'tests/performance/render_load'))
from codec import decode

def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def status(b,path):
    with urllib.request.urlopen(b.config['p4']+path,timeout=4) as r:return json.load(r)

def recover(b,out,remote):
    """Preserve telemetry, reset a known bench, prove CLI before SD operations."""
    receipt={'started_utc':utc(),'outcome':'pending'}
    try:
        if (out/'run.json').exists() and json.loads((out/'run.json').read_text()).get('endpoint')=='p4' and b.confirm_p4_fixture_cli(out):
            b.fast_start();receipt.update(outcome='pass',finished_utc=utc(),cli_evidence='rendered benchmark error and MOS prompt',hardware_reset=False);write(out/'recovery.json',receipt);return
        try:write(out/'telemetry-before-recovery.json',status(b,'/diagnostics/render-benchmark'))
        except Exception as e:receipt['telemetry_error']=repr(e)
        if b.sd:
            b.sd.lock.close();b.sd=None
        # A fresh boot invalidates the foreground listener session. Its journal
        # remains evidence; never resume or replay its pending mutations.
        b.state.pop('fast_journal',None);b.save()
        command=b.config.get('p4_reset_command')
        if command:
            with (out/'p4-reset.log').open('w') as f:
                subprocess.run(command,check=True,timeout=30,stdout=f,stderr=subprocess.STDOUT)
            receipt['p4_reset_command']=command
            limit=time.monotonic()+30
            while True:
                try:status(b,'/keyboard/status');break
                except Exception:
                    if time.monotonic()>limit:raise
                    time.sleep(.5)
        b.reset();receipt['hardware_reset']=True;time.sleep(5)
        limit=time.monotonic()+60;escaped=False
        meta=json.loads((out/'run.json').read_text())
        while time.monotonic()<limit:
            s=status(b,'/sd/status')
            if s['online']:break
            eligible,_=b.request('HEAD',remote+'/results.bin',timeout=5)
            if eligible in (200,404):b.fast_start();break
            if eligible!=503:raise RuntimeError(('recovery eligibility',eligible))
            telemetry=status(b,'/diagnostics/render-benchmark')
            active=[w for w in telemetry['windows'] if w['tag']==meta['tag'] and not w['end_us']]
            if not telemetry['open'] and b.confirm_p4_fixture_cli(out):b.fast_start();break
            # Input admission can precede RUN and installation of its callback.
            # An Escape sent then is consumed by startup, so it cannot prove the
            # fixture exited. Require this invocation's measured window first.
            # This recovery wait never changes the scheduled measurement keys.
            if not escaped and active and status(b,'/keyboard/status').get('ready'):
                subprocess.run([sys.executable,str(ROOT/'scripts/keyboard.py'),'--url',b.config['p4'],'--state',str(b.evidence/'keyboard.json'),'key','escape'],check=True,timeout=15,stdout=subprocess.DEVNULL)
                escaped=True;receipt['fresh_fixture_invocation']=True;receipt['escape_window']={'tag':meta['tag'],'case':active[-1]['id'],'sent_utc':utc()}
            time.sleep(1)
        else:raise RuntimeError('recovery did not establish a CLI/listener')
        b.fast_connect();receipt.update(outcome='pass',finished_utc=utc(),escape_sent=escaped)
    except Exception as e:
        receipt.update(outcome='fail',failure=repr(e));write(out/'recovery.json',receipt);raise
    write(out/'recovery.json',receipt)

def mark_exception(b,before,error,suite,number):
    new=set(b.evidence.glob('BENCH-009-*'))-before
    if len(new)!=1:raise RuntimeError('cannot identify failed preparation directory') from error
    out=new.pop();p=out/'run.json'
    if not p.exists():
        write(p,{'suite':suite,'pass_number':number,'outcome':'preparation-fail','failure':repr(error)})
        (out/'exception.txt').write_text(traceback.format_exc())
        raise RuntimeError('preparation failed before a verified invocation; do not replay or reset unknown startup') from error
    m=json.loads(p.read_text())
    m.update(suite=suite,pass_number=number,outcome='fail',failure=repr(error))
    write(p,m);(out/'exception.txt').write_text(traceback.format_exc())
    remote=b.config['results_root']+'/'+out.name
    recover(b,out,remote)
    recovery=json.loads((out/'recovery.json').read_text())
    # A fresh invocation can start after reset if no original checkpoint existed.
    # Its tag is the same saved plan, but it is not the interrupted measurement.
    # Keep those bytes separately; never pair them with pre-reset telemetry.
    recovered_only=recovery.get('fresh_fixture_invocation',False)
    suffix='-recovery-only' if recovered_only else ''
    if recovered_only:m['recovery_started_fresh_fixture']=True
    if b.config.get('defer_result_retrieval',False):
        # Keep bulk failure/checkpoint records on the card under the Author's
        # local-collection contract. Recovery-only bytes must never become the
        # original timed sample even though both invocations use the saved tag.
        m.update(result_retrieval='deferred-sd-mount',sd_results_path=remote+'/results.bin',
                 sd_failure_path=remote+'/failure.bin',recovery_result_suffix=suffix,sd_files={})
        for name in ('results.bin','failure.bin'):
            try:size,attributes=b.fast_connect().stat_entry(remote+'/'+name)
            except Exception as problem:m.setdefault('recovery_stat_errors',{})[name]=repr(problem)
            else:m['sd_files'][name]=dict(bytes=size,attributes=attributes)
        write(p,m);return out
    try:raw=b.fast_read(remote+'/results.bin')
    except Exception as e:m['retrieval_after_recovery_error']=repr(e)
    else:
        (out/('results'+suffix+'.bin')).write_bytes(raw)
        try:write(out/('decoded'+suffix+'.json'),decode(raw))
        except Exception as e:m['decode_after_recovery_error']=repr(e)
    try:(out/('failure'+suffix+'.bin')).write_bytes(b.fast_read(remote+'/failure.bin'))
    except Exception:pass
    # Windows saved before recovery remain attributable only if their tag
    # matches the recorded plan; resetting the P4 must never synthesize them.
    if not recovered_only and not (out/'telemetry.json').exists() and (out/'telemetry-before-recovery.json').exists():
        (out/'telemetry.json').write_bytes((out/'telemetry-before-recovery.json').read_bytes())
    write(p,m);return out

def execute(b,mode,endpoint,variant,number,first,end,interval,suite,disabled=False,control_context=None):
    before=set(b.evidence.glob('BENCH-009-*'))
    try:return b.run(mode,endpoint,first,end,20,max(1100,30+(end-first)*interval+120),variant,interval,disable_timing=disabled,suite=suite,pass_number=number,control_context=control_context)
    except Exception as e:
        print('FAULT '+repr(e),flush=True)
        return mark_exception(b,before,e,suite,number)

def campaign(b,variant,contract,modes,start_pass,end_pass,out,first_case=0,end_case=94,endpoint_override=None):
    if out.exists():raise RuntimeError('Campaign receipt already exists; retain it and choose a fresh path')
    c=json.loads(contract.read_text());suite=c['identity'];receipt={'suite':suite,'variant':variant,'started_utc':utc(),'runs':[],'marked':[],'short':[],'outcome':'running'}
    receipt['host_campaign_sha256']=HOST_SOURCE_SHA256
    receipt['selection']={'first_case':first_case,'end_case':end_case,'endpoint_override':endpoint_override}
    write(out,receipt)
    for number in range(start_pass,end_pass+1):
        for mode in modes:
            endpoints=c['endpoint_order'][number-1] if variant=='normal' else ['p4']
            if endpoint_override:endpoints=[endpoint_override]
            for endpoint in endpoints:
                first=first_case;preparation_failures=0
                while first<end_case:
                    folder=execute(b,mode,endpoint,variant,number,first,end_case,c['automated_case_seconds'],suite)
                    receipt['runs'].append(folder.name)
                    result=json.loads((folder/'decoded.json').read_text()) if (folder/'decoded.json').exists() else {'cases':[]}
                    meta=json.loads((folder/'run.json').read_text());items=result['cases']
                    windows={};telemetry_bad=False
                    if endpoint=='p4':
                        if (folder/'telemetry.json').exists():
                            t=json.loads((folder/'telemetry.json').read_text());tagged=[w for w in t['windows'] if w['tag']==meta['tag']]
                            windows={w['id']:w for w in tagged};telemetry_bad=t['overflow'] or t['output']!=variant or len(windows)!=len(tagged)
                        else:telemetry_bad=True
                    for case in items:
                        ref={'mode':mode,'endpoint':endpoint,'variant':variant,'pass_number':number,'case':case['id'],'run':folder.name}
                        w=windows.get(case['id']);uncorrelated=endpoint=='p4' and (telemetry_bad or not w or w['end_us']<=w['start_us'] or w['flags']!=case['flags'])
                        if case['error'] or case['truncated'] or any(f['status'] for f in case['frames']) or uncorrelated:receipt['marked'].append({**ref,'reason':'error/truncation/uncorrelated telemetry'})
                        elif case['total_frames']<64:receipt['short'].append(ref)
                    if items and items[-1]['id']==end_case-1:break
                    last=items[-1]['id'] if items else first-1
                    failed=last if items and items[-1]['error'] else last+1
                    ref={'mode':mode,'endpoint':endpoint,'variant':variant,'pass_number':number,'case':failed,'run':folder.name}
                    if not any(all(r.get(k)==v for k,v in ref.items()) for r in receipt['marked']):receipt['marked'].append(ref)
                    # An upfront geometry/timer/I/O failure invalidates the mode
                    # preparation, rather than pretending each remaining case ran.
                    failure=(folder/'failure.bin').read_bytes() if (folder/'failure.bin').exists() else b''
                    # A recovered warm-up fence failure belongs to this case.
                    # It does not establish that the next independent family is
                    # unprepared. Only repeated opaque failures count toward the
                    # preparation limit; explicit mode/load/timer failures stop.
                    if not items and not (failure and failure[19]==4):preparation_failures+=1
                    else:preparation_failures=0
                    if (failure and failure[19] in (1,2,3)) or preparation_failures>=3:
                        receipt.setdefault('unperformed',[]).append({**ref,'first':failed+1,'end':end_case,'reason':'upfront preparation failed'})
                        break
                    first=failed+1;write(out,receipt)
                write(out,receipt)
    # Longer windows are sampling corrections; they do not erase the originals.
    for r in receipt['short']:
        f=execute(b,r['mode'],r['endpoint'],variant,r['pass_number'],r['case'],r['case']+1,30,suite)
        receipt.setdefault('longer_runs',[]).append(f.name);write(out,receipt)
    # Omit measurement probes using the same guarded fixture and watchdog.
    # This is a timing-probe control, not removal of every compiled diagnostic.
    seen=set()
    for r in receipt['marked']:
        key=(r['mode'],r['endpoint'],r['case'])
        if key in seen:continue
        seen.add(key)
        origin=json.loads((b.evidence/r['run']/'run.json').read_text())
        # Preserve the failed invocation's preceding setup order and key cadence.
        # A fresh single-case replay would confound removal of probes with history.
        first=origin['first'];interval=origin['case_interval_seconds']
        context=dict(original_run=r['run'],marked_case=r['case'],history_first_case=first,history_end_case=r['case']+1,scope='Timing reads suppressed; bounded watchdog and compiled diagnostic carrier retained',frame_count_limit='Untimed transitions preserved; achieved template repeat counts may differ without probes')
        f=execute(b,r['mode'],r['endpoint'],variant,0,first,r['case']+1,interval,suite,True,context)
        receipt.setdefault('probe_controls',[]).append(f.name);write(out,receipt)
    receipt.update(outcome='finished-with-evidence',finished_utc=utc());write(out,receipt)
    return receipt

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--variant',choices=('normal','hold','off'),required=True);p.add_argument('--contract',type=Path,default=ROOT/'tests/performance/render_load/contract-r04.json');p.add_argument('--modes',type=int,nargs='+');p.add_argument('--start-pass',type=int,default=1);p.add_argument('--end-pass',type=int,default=3);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--first-case',type=int,default=0);p.add_argument('--end-case',type=int,default=94);p.add_argument('--endpoint',choices=('mainboard','p4'));a=p.parse_args()
    c=json.loads(a.contract.read_text());assert 1<=a.start_pass<=a.end_pass<=c['passes']
    modes=a.modes or c['modes' if a.variant=='normal' else 'output_control_modes']
    assert set(modes)<=set(c['modes'])
    assert 0<=a.first_case<a.end_case<=94 and (a.variant=='normal' or a.endpoint in (None,'p4'))
    b=Bench(a.config,a.evidence)
    try:result=campaign(b,a.variant,a.contract,modes,a.start_pass,a.end_pass,a.receipt,a.first_case,a.end_case,a.endpoint)
    except Exception as e:
        if a.receipt.exists():
            receipt=json.loads(a.receipt.read_text())
            receipt.update(outcome='stopped-on-unresolved-recovery',failure=repr(e),finished_utc=utc())
            write(a.receipt,receipt)
        raise
    print(json.dumps(result))
if __name__=='__main__':main()
