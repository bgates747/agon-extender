#!/usr/bin/env python3
"""Stage one fixed-source HDMI control, collect telemetry, then leave its chart.

Each invocation selects exactly one mode. A subsequent mode requires a separate
invocation after the Author's visual reply. The long render-load campaign stays
paused. Firmware is neither built nor flashed by this supplemental controller.
"""
import argparse, json, statistics, sys, time, urllib.request
from pathlib import Path
from render_load import Bench, digest, utc
from sdcard import RemoteError

PHASES = ('drawing_drain','row_lock_wait','row_read_compose','rgb888_expand','cache_submit','conversion_attempt')

def status(bench,path):
    with urllib.request.urlopen(bench.config['p4']+path,timeout=5) as r:
        return json.load(r)

def write(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')

def summarize(telemetry,mode,height,tag,variant='normal',render_storage='native',render_memory=None):
    assert telemetry['output']==variant and not telemetry['open'] and not telemetry['overflow']
    windows=[w for w in telemetry['windows'] if w['tag']==tag]
    assert [w['id'] for w in windows]==[0,1,2]
    rows=[]
    for w in windows:
        duration=(w['end_us']-w['start_us'])/1e6
        assert 9.5 < duration < 11
        if variant=='normal':assert w['updates'] >= 64
        else:assert w['updates']==0 and w['scanouts']==0 and w['phases'][4]['calls']==0 and w['phases'][5]['calls']>=64
        phases={name:dict(value) for name,value in zip(PHASES,w['phases'])}
        assert len(w['phases'])==6
        # No drawing commands run in these windows. Empty drain calls can run
        # on normal hardware-frame opportunities; report their wall cost too.
        for name,value in phases.items():
            value['mean_call_us']=value['us']/value['calls'] if value['calls'] else None
        normalized={name:(phases[name]['mean_call_us'] or 0)*height/1000 for name in PHASES[1:4]}
        rows.append(dict(id=w['id'],duration_seconds=duration,accepted_submissions=w['updates'],submissions_per_second=w['updates']/duration,scanout_hz=w['scanouts']/duration,conversion_attempts_per_second=phases['conversion_attempt']['calls']/duration,phases=phases,normalized_frame_ms=normalized,cache_submit_mean_ms=phases['cache_submit']['mean_call_us']/1000 if phases['cache_submit']['calls'] else None,conversion_attempt_mean_ms=phases['conversion_attempt']['mean_call_us']/1000))
    ms={p:statistics.median(r['normalized_frame_ms'][p] for r in rows) for p in PHASES[1:4]}
    attempt_ms=statistics.median(r['conversion_attempt_mean_ms'] for r in rows)
    caches=[r['cache_submit_mean_ms'] for r in rows if r['cache_submit_mean_ms'] is not None]
    scope=('Fixed logical VDP image, active HDMI scanout. ' if variant=='normal' else 'Fixed logical VDP image, no DSI/DMA scanout; equal RGB888 allocation and software60Hz opportunities. No panel submission/cache flush; accepted HDMI submissions remain zero. ')
    if render_storage=='rgb888' and render_memory=='panel-direct':
        scope+='RGB-001 draws directly into the HDMI allocation. No full-image row copy or expansion occurs. Preparation includes native exclusion, overlay maintenance and marker sampling; cache submission remains separately measured. '
    elif render_storage=='rgb888':
        scope+='RGB-001 stores RGB888 logical rows. Row-read/compose includes the presentation memcpy and any overlay-row composition; whole-image RGB888 expansion is absent. '
    return dict(mode=mode,variant=variant,render_storage=render_storage,windows=rows,median_normalized_frame_ms=ms,equivalent_phase_frames_per_second={p:1000/v if v else None for p,v in ms.items()},median_cache_submit_ms=statistics.median(caches) if caches else None,median_conversion_attempt_ms=attempt_ms,equivalent_conversion_attempt_frames_per_second=1000/attempt_ms,median_conversion_attempts_per_second=statistics.median(r['conversion_attempts_per_second'] for r in rows),median_submissions_per_second=statistics.median(r['submissions_per_second'] for r in rows),median_scanout_hz=statistics.median(r['scanout_hz'] for r in rows),scope=scope+'RGB888 expansion excludes row preparation/cache/wait; row costs are normalized from mean row wall times, not per-frame distributions. Conversion-attempt scope includes its leading buffer wait and excludes cache submission/trailing reuse wait. Equivalent frames/s is1000 divided by milliseconds for that phase alone, not observed displayed FPS. Phase probes remain enabled; no physical displayed-FPS claim.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--bench-evidence',type=Path,required=True)
    p.add_argument('--build',type=Path,required=True)
    p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--mode',type=int,choices=(20,8,136,21,149),required=True)
    p.add_argument('--variant',choices=('normal','convert-off'),default='normal')
    args=p.parse_args()
    args.evidence.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((args.build/'manifest.json').read_text())
    selected=manifest['modes'][str(args.mode)]
    fixture=args.build/f'mode{args.mode}'/selected['binary']
    assert digest(fixture.read_bytes())==selected['sha256']
    b=Bench(args.config,args.bench_evidence)
    before={path:status(b,path) for path in ('/sd/status','/keyboard/status','/display/status')}
    assert before['/sd/status']['online'] and before['/keyboard/status']['ready'], 'Require positively observed foreground listener before staging'
    assert status(b,'/diagnostics/render-benchmark')['output']==args.variant
    run_id='BENCH-009-'+utc();out=args.evidence/run_id;out.mkdir()
    (out/'controller.py').write_bytes(Path(__file__).read_bytes())
    receipt=dict(run_id=run_id,scope='supplemental-static-conversion',variant=args.variant,mode=args.mode,started_utc=utc(),outcome='preparing',fixture_build_id=manifest['build_id'],fixture=selected,manifest_sha256=digest((args.build/'manifest.json').read_bytes()),host_runner_sha256=digest(Path(__file__).read_bytes()),before=before,p4_installation=json.loads(Path(b.config['installation_record']).read_text()))
    write(out/'run.json',receipt)
    prep=time.monotonic()
    remote='/extender/render-load-static-r01/'+manifest['build_id']
    # The installed foreground listener predates directory capability0x20.
    # Use the maintained finite WebDAV job at a proven CLI to create folders;
    # return to the fast listener before transferring executable bytes.
    client=b.fast_connect()
    try:
        _,attr=client.stat_entry(remote)
        assert attr&16, 'Static build path must be a directory'
    except RemoteError as error:
        if error.status!=6 or error.detail not in (b'\x04',b'\x05'):raise
        try:
            _,attr=client.stat_entry('/extender/render-load-static-r01')
            assert attr&16
            parent_exists=True
        except RemoteError as parent_error:
            if parent_error.status!=6 or parent_error.detail not in (b'\x04',b'\x05'):raise
            parent_exists=False
        b.fast_exit()
        if not parent_exists:b.mkdir('/extender/render-load-static-r01')
        b.mkdir(remote);b.fast_start();client=b.fast_connect()
    # Keep the SD alias below the foreground protocol's120-byte path limit;
    # the parent and retained manifest preserve the immutable build identity.
    target=remote+'/mode'+str(args.mode)+'.bin'
    receipt['deployed_path']=target
    try:
        client.stat_entry(target)
    except Exception as error:
        if not isinstance(error,RemoteError) or error.status!=6 or error.detail not in (b'\x04',b'\x05'):raise
        b.fast_put_new(target,fixture.read_bytes())
    else:
        assert digest(b.fast_read(target))==selected['sha256']
    startup=('SET KEYBOARD 1\nEMOS KEYINPUT extender\nEMOS EXCOM\nVDU 22 '+str(args.mode)+'\nLOAD '+target+'\nRUN .\nEMOS LEGACY\nEMOS sdserve --fast /\n').encode('ascii')
    b.startup(startup);b.fast_exit()
    (out/'startup.txt').write_bytes(startup)
    (out/'reference.svg').write_bytes((args.build/f'mode{args.mode}'/'reference.svg').read_bytes())
    receipt.update(startup_sha256=digest(startup),preparation_seconds=time.monotonic()-prep,outcome='running')
    write(out/'run.json',receipt)
    reset_at=time.monotonic();b.reset()
    print('Static chart mode'+str(args.mode)+' started; collecting three 10-second windows.',flush=True)
    try:
        # Bounded missing-progress guard, not a scheduled reset or retry.
        limit=time.monotonic()+75
        while time.monotonic()<limit:
            telemetry=status(b,'/diagnostics/render-benchmark')
            matched=[w for w in telemetry['windows'] if w['tag']==selected['tag']]
            if len(matched)==3 and all(w['end_us'] for w in matched) and not telemetry['open']:break
            time.sleep(1)
        else:raise RuntimeError('Static control did not close all three windows; leave device state for diagnosis')
        (out/'telemetry.json').write_text(json.dumps(telemetry,indent=2)+'\n')
        display=status(b,'/display/status')
        assert display['mode']==args.mode and display['output']=='hdmi'
        summary=summarize(telemetry,args.mode,display['height'],selected['tag'],args.variant,display.get('render_storage','native'),display.get('render_memory'))
        summary['render_memory']=display.get('render_memory')
        if summary['median_cache_submit_ms'] is not None:
            total=summary['median_conversion_attempt_ms']+summary['median_cache_submit_ms']
            summary.update(preparation_and_cache_ms=total,equivalent_preparation_and_cache_fps=1000/total)
        write(out/'summary.json',summary)
        receipt.update(outcome='measured-awaiting-visual-reply' if args.variant=='normal' else 'measured-scanout-absent',finished_utc=utc(),reset_to_collection_seconds=time.monotonic()-reset_at,display=display,keyboard=status(b,'/keyboard/status'),telemetry_sha256=digest((out/'telemetry.json').read_bytes()),visual_acceptance='pending' if args.variant=='normal' else 'not-applicable-scanout-absent',terminal_state='Static fixture stays active until Escape; no automatic next mode',summary=summary)
        write(out/'run.json',receipt)
        write(args.evidence/'current.json',dict(run=str(out),mode=args.mode,outcome=receipt['outcome']))
        print(json.dumps(dict(run=str(out),summary=summary),indent=2),flush=True)
    except Exception as error:
        receipt.update(outcome='failed-left-for-diagnosis',failure=repr(error));write(out/'run.json',receipt);raise
    finally:
        if b.sd:b.sd.lock.close();b.sd=None

if __name__=='__main__':main()
