#!/usr/bin/env python3
"""RGB-001 bounded subset of the frozen r04 fixture; never select/flash firmware.

Use only after each renderer's static-chart visual gates. Retain one matched
pass per mode/case for each selected renderer/output; stop on unresolved faults.
The original fixture/VDU templates stay unchanged. Wall-clock keys close each
window five seconds after the host observes its correlated start. At60Hz this
allows about300 paced frames, with a required minimum64. This shorter subset
schedule is separately identified and does not rewrite the long r04 contract.
"""
import argparse,json,sys,time,urllib.request
from pathlib import Path
from render_load import Bench,utc,digest
from render_load_campaign import mark_exception

SELECTION={20:(0,1,7,9,15,23,39,41,46),8:(0,1,7,9,15,23,39,41,46),136:(0,9,41,46)}

def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def status(b,path):
    with urllib.request.urlopen(b.config['p4']+path,timeout=5) as r:return json.load(r)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True);p.add_argument('--renderer',choices=('native','rgb888'),required=True)
    p.add_argument('--output',choices=('normal','off'),required=True)
    p.add_argument('--modes',nargs='+',type=int,default=[20,8,136])
    p.add_argument('--defer-retrieval',action='store_true',help='Keep result bytes on SD for local-card collection; validate them later')
    p.add_argument('--resume-from',type=Path,help='Reuse prior passing or deferred invocations from this same installed renderer/output')
    p.add_argument('--skip-recorded-failures',action='store_true',help='Continue independent cases after the referenced failure has a passing recovery receipt; keep it marked')
    a=p.parse_args()
    assert not a.receipt.exists(),'Preserve an existing subset receipt; no uncertain replay'
    assert set(a.modes)<=set(SELECTION)
    b=Bench(a.config,a.evidence)
    b.config['defer_result_retrieval']=a.defer_retrieval
    assert status(b,'/sd/status')['online'] and status(b,'/keyboard/status')['ready']
    assert status(b,'/diagnostics/render-benchmark')['output']==a.output
    installed=json.loads(Path(b.config['installation_record']).read_text())
    assert installed['renderer']==a.renderer and installed['variant']==a.output
    storage=json.loads(Path(installed['manifest']).read_text())['display_inputs'].get('render_storage','native')
    selection={m:list(SELECTION[m]) for m in a.modes};carried=[];marked=[]
    assert not a.skip_recorded_failures or a.resume_from
    if a.resume_from:
        prior=json.loads(a.resume_from.read_text())
        assert prior['installation']==installed and prior['renderer']==a.renderer and prior['output']==a.output
        for ref in prior['runs']:
            accepted=ref['outcome'] in ('pass','measured-awaiting-local-results')
            if ref['outcome']=='fail' and a.skip_recorded_failures:
                recovery=json.loads((Path(ref['run'])/'recovery.json').read_text())
                assert recovery['outcome']=='pass','Never continue after unresolved recovery'
                accepted=True;marked.append(ref)
            if accepted and ref['mode'] in selection:
                selection[ref['mode']]=[c for c in selection[ref['mode']] if not ref['first']<=c<ref['end']]
                carried.append(ref)
    receipt=dict(started_utc=utc(),outcome='running',selection={m:SELECTION[m] for m in a.modes},renderer=a.renderer,output=a.output,pass_number=1,window_seconds=5,minimum_frames=64,installation=installed,host_source_sha256=digest(Path(__file__).read_bytes()),runs=[],limitations='One bounded pass; unchanged r04 fixture/template bytes, separately identified shorter wall-clock schedule. Marker transitions are sampled source identities, not proof of tear-free physical delivery.')
    receipt.update(selection=selection,result_retrieval='deferred-sd-mount' if a.defer_retrieval else 'foreground-uart',resume_from=str(a.resume_from) if a.resume_from else None,carried_runs=carried,marked=marked)
    write(a.receipt,receipt)
    try:
        for mode in a.modes:
            # Combine adjacent0/1 only; avoid running any unselected workload.
            groups=[]
            for case in selection[mode]:
                if groups and groups[-1][1]==case:groups[-1]=(groups[-1][0],case+1)
                else:groups.append((case,case+1))
            for first,end in groups:
                before=set(a.evidence.glob('BENCH-009-*'))
                try:
                    folder=b.run(mode,'p4',first,end,20,180,a.output,5,suite='rgb-001-subset-r01',pass_number=1,window_relative=True,control_context=dict(renderer=a.renderer,render_storage=storage,scope='matched existing VDU templates; five seconds per open window'))
                except Exception as error:
                    folder=mark_exception(b,before,error,'rgb-001-subset-r01',1)
                meta=json.loads((folder/'run.json').read_text())
                receipt['runs'].append(dict(mode=mode,first=first,end=end,run=str(folder),outcome=meta['outcome']))
                write(a.receipt,receipt)
                if meta['outcome'] not in ('pass','measured-awaiting-local-results'):
                    # mark_exception completes recovery or raises. Returned
                    # failed/partial data likewise leaves the foreground listener
                    # active. Keep failures marked and continue independent cases.
                    assert status(b,'/sd/status')['online'] and status(b,'/keyboard/status')['ready']
                    receipt['marked'].append(receipt['runs'][-1]);write(a.receipt,receipt)
        terminal='completed-awaiting-local-results' if a.defer_retrieval else 'completed'
        if receipt['marked']:terminal='completed-with-marked-cases-awaiting-local-results' if a.defer_retrieval else 'completed-with-marked-cases'
        receipt.update(outcome=terminal,finished_utc=utc());write(a.receipt,receipt)
    except Exception as error:
        receipt.update(outcome='stopped-left-for-diagnosis',failure=repr(error),finished_utc=utc());write(a.receipt,receipt);raise
    finally:
        if b.sd:b.sd.lock.close();b.sd=None
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
