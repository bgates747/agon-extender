#!/usr/bin/env python3
"""Offline preparation for the five-mode rendering master; no device imports."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests/performance/scan'),str(ROOT/'scripts')]
import multimode
from run_render_qualification import banner


def sha(data):return hashlib.sha256(data).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')


def prepare(config,fixtures,campaign):
    c=json.loads(config.read_text());local=Path(c['local']);out=Path(c.get('package',local/'package'))
    out.mkdir(parents=True,exist_ok=False)
    fm=json.loads((fixtures/'manifest.json').read_text())
    remote='/agents/extender/results/'+campaign
    if not campaign.startswith('rq-') or any(x not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for x in campaign):
        raise ValueError('Use a fresh rq- lowercase campaign ID')
    p=dict(campaign=campaign,remote=remote,fixture_build=fm['build_id'],
           geometries={str(k):list(v) for k,v in multimode.MODES.items()},files=[],jobs=[],resident_assets=[])
    def add(name,destination,data):
        path=out/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        p['files'].append(dict(local=name,remote=destination,sha256=sha(data),bytes=len(data)))
    for e in fm['files']:
        raw=(fixtures/'sdcard'/e['path']).read_bytes()
        if sha(raw)!=e['sha256']:raise ValueError('Frozen fixture artifact changed')
        add('fixtures/'+e['path'],'/'+e['path'],raw)
    for name in ('game.agnb','ui.agnb','fonts/Lat38-VGA8_8x8.font'):
        path=Path(c['asset_source'])/name
        p['resident_assets'].append(dict(path='/test/nurples/scan-r01/'+name,sha256=sha(path.read_bytes())))
    for name,good in (('success',True),('errors',False)):
        add(name+'.txt',remote+'/'+name+'.txt',banner(good))
    jobs=[]
    for renderer in ('rgb888','indexed'):
        for mode in multimode.MODES:
            for repeat in (0,1,2,3):
                for case,name in multimode.NAMES.items():
                    ident=f'{renderer}-m{mode}-c{case}-r{repeat}'
                    folder=remote+'/'+ident
                    geometry=next(e for e in fm['cases'] if e['mode']==mode and e['case']==case)
                    game=geometry['game'];smoke=repeat==0
                    frames=(30 if game else 3) if smoke else (3600 if game else 120)
                    warmup=0 if smoke else (120 if game else 60)
                    result=folder+'/records.bin'
                    tag=int.from_bytes(hashlib.sha256((campaign+'/'+ident).encode()).digest()[:3],'little') or 1
                    data=multimode.old.config(case,frames,warmup,result,fence_off=game,extra_flags=4,window_tag=tag)
                    add(ident+'/run.cfg',folder+'/run.cfg',data)
                    binary=geometry.get('sd_binary',geometry['sd_dir']+'/fixture.bin')
                    # One explicit host EXEC owns directory setup and launch.
                    # Keyboard delivery of a separate CD cannot establish
                    # completion of that command before the next command.
                    lines=['EMOS EXCOM --keep-display','CD '+folder,'LOAD '+binary,
                           'RUN','CD /','EMOS LEGACY','EMOS sdserve --fast /']
                    add(ident+'/run.txt',folder+'/run.txt',('\r\n'.join(lines)+'\r\n').encode())
                    job=dict(id=ident,renderer=renderer,mode=mode,case=name,case_number=case,
                             repeat=repeat,frames=frames,warmup=warmup,tag=tag,result=result,
                             game=game,smoke=smoke,config_local=ident+'/run.cfg',
                             config_remote=folder+'/run.cfg',command_remote=folder+'/run.txt',
                             diagnostic_id=geometry['diagnostic_id'],
                             limits=geometry['limits'])
                    p['jobs'].append(job)
                    if not smoke:
                        jobs.append({k:job[k] for k in ('id','renderer','mode','case','repeat')}|
                                    dict(qualified_geometry=False,command=[sys.executable,str(ROOT/'qualification/render_modes.py'),
                                         '--config',str(config.resolve()),'run','--id',ident,
                                         '--receipt','{receipt}','--evidence','{evidence}']))
    dump(out/'plan.json',p)
    inputs={str(path.resolve()):sha(path.read_bytes()) for path in
            [config, fixtures/'manifest.json',out/'plan.json',ROOT/'qualification/render_modes.py',
             ROOT/'scripts/run_render_qualification.py',Path(c['session_module']),Path(c['installer'])]}
    for r in c['renderers'].values():
        mp=Path(r['manifest']);inputs[str(mp)]=sha(mp.read_bytes())
    master=dict(schema=1,ready=False,cwd=str(ROOT),renderers=['rgb888','indexed'],
                bench_lock=str(local/'bench.lock'),inputs=inputs,jobs=jobs,
                notification={name:[sys.executable,str(ROOT/'qualification/render_modes.py'),
                              '--config',str(config.resolve()),'notify','--status',name,
                              '--evidence',str(local/('final-notification-'+name))]
                              for name in ('success','errors')})
    dump(local/'master-plan.pending.json',master)
    print('Offline prepared',len(jobs),'full jobs plus80 smoke jobs;',len(p['files']),'payloads')


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--config',type=Path,required=True);a.add_argument('--fixtures',type=Path,required=True)
    a.add_argument('--campaign',required=True);x=a.parse_args();prepare(x.config,x.fixtures,x.campaign)
