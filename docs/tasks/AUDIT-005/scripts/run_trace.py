#!/usr/bin/env python3
"""Workstation runner. Private SSH paths/host come from an ignored bench JSON.

Only executes the staged passive analyzer helper and retrieves evidence. The
operator inserts the prepared SD and resets Agon after the explicit cue.
"""
import argparse
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import shlex
import subprocess
import sys
import time
from capture_trace import sha


def condition_settings(cfg):
    condition=cfg.get('browser_condition','connected')
    if condition not in ('connected','disconnected'):
        raise ValueError('Unknown browser condition')
    procedure='uart-path-capture-r02' if condition=='disconnected' else 'uart-path-capture-r01'
    if cfg.get('procedure_identity')=='uart-path-capture-r03':
        if condition!='disconnected' or cfg.get('drawing_policy')!='stock-drain-until-empty-or-suspended':
            raise ValueError('Stock-drain comparison requires the browser-off drain policy')
        if not re.fullmatch(r'uart-excom-console-r08-b\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}Z',cfg.get('p4_build','')):
            raise ValueError('Stock-drain comparison requires the selected r08 build')
        for field in ('p4_factory_sha256','p4_manifest_sha256','p4_deployment_record_sha256'):
            if not re.fullmatch(r'[0-9a-f]{64}',cfg.get(field,'') or ''):
                raise ValueError('Missing verified P4 deployment binding: '+field)
        procedure='uart-path-capture-r03'
    if cfg.get('procedure_identity',procedure)!=procedure:
        raise ValueError('Browser condition and procedure identity disagree')
    return condition,procedure


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bench',type=Path,required=True)
    args=p.parse_args()
    cfg=json.loads(args.bench.read_text())
    condition,procedure=condition_settings(cfg)
    disconnected=condition=='disconnected'
    helper=Path(__file__).with_name('capture_trace.py')
    if sha(helper)!=cfg['capture_helper_sha256']:
        p.error('Capture helper changed since preparation; restage and recheck')
    browser_instruction=('Close all Extender video tabs/windows on every device. Keep Ethernet connected.\n'
                         'Keep those tabs closed until Agon finishes and returns to MOS.\n'
                         if disconnected else 'Connect one browser video client and leave it visible.\n')
    print('Insert the prepared SD. Keep both boards powered and ribbons seated.\n'+browser_instruction+
          'Probes: yellow PC0, gray PC1, orange PC2, purple PC3; common ground.\n'
          'Wait for the reset cue. The P4 will remain running.\n',flush=True)
    try:input('Press Enter after closing all Extender video tabs: ' if disconnected else 'Press Enter when ready: ')
    except (EOFError,KeyboardInterrupt):raise SystemExit('\nCancelled before acquisition.')
    condition_record=dict(procedure=procedure,browser_condition=condition,
                          observation='operator confirmed; server client count not independently observed',
                          operator_confirmed_at=datetime.now(timezone.utc).isoformat(),
                          csv_browser_annotation_override=disconnected)
    if procedure=='uart-path-capture-r03':
        condition_record['browser_off_reference_run']='AUDIT-005-2026-09-10-20-03-35Z'
        condition_record['drawing_policy']=cfg['drawing_policy']
        condition_record['csv_edp_annotation_override']={
            'compiled_build':'uart-excom-console-r07-b2026-09-10-06-31-58Z',
            'measured_build':cfg['p4_build'],
            'factory_sha256':cfg['p4_factory_sha256'],
            'build_manifest_sha256':cfg['p4_manifest_sha256'],
            'deployment_record_sha256':cfg['p4_deployment_record_sha256']}
    if disconnected:
        print('Waiting five seconds after browser closure...',flush=True)
        begin=time.monotonic()
        try:time.sleep(5)
        except KeyboardInterrupt:raise SystemExit('\nCancelled before acquisition.')
        condition_record['settlement_seconds']=time.monotonic()-begin
        condition_record['settled_at']=datetime.now(timezone.utc).isoformat()
        condition_record['connected_reference_run']='AUDIT-005-2026-09-10-19-44-52Z'
    dest=Path(cfg['local_captures']);dest.mkdir(parents=True,exist_ok=True)
    log=dest/('console-'+datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')+'.txt')
    options=cfg['ssh_options'];host=cfg['host'];remote=cfg['remote_stage']
    print('\nArming analyzer...',flush=True)
    remote_sha=subprocess.check_output(['ssh',*options,host,shlex.join(
        ['sha256sum',remote+'/capture_trace.py'])],text=True,timeout=20).split()[0]
    if remote_sha!=cfg['capture_helper_sha256']:
        raise SystemExit('Remote helper changed; do not reset Agon.')
    command=['python3','-u',remote+'/capture_trace.py','--output-parent',remote+'/captures']
    if disconnected:command.append('--browser-disconnected')
    if procedure=='uart-path-capture-r03':command.append('--stock-drain')
    recorded=None
    with log.open('w') as out:
        out.write('Preparation: '+args.bench.read_text()+'\n')
        out.write('Condition: '+json.dumps(condition_record)+'\n');out.flush()
        proc=subprocess.Popen(['ssh',*options,host,shlex.join(command)],stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,text=True)
        try:
            for line in proc.stdout:
                out.write(line);out.flush();print(line,end='',flush=True)
                if line.startswith('Evidence: '):recorded=line.removeprefix('Evidence: ').strip()
            rc=proc.wait(timeout=10)
        except KeyboardInterrupt:
            proc.terminate();proc.wait(timeout=10)
            raise SystemExit('\nInterrupted; remote acquisition has a 60-second bound. Preserve its run folder.')
    if recorded is None or not recorded.startswith(remote+'/captures/AUDIT-005-'):
        raise SystemExit('No complete acquisition receipt; inspect '+str(log))
    copy=subprocess.run(['scp','-q',*options,'-r',host+':'+recorded,str(dest)])
    if copy.returncode:raise SystemExit('Retrieval failed; original remains at '+recorded)
    folder=dest/Path(recorded).name
    subprocess.run(['sha256sum','-c','SHA256SUMS','--status'],cwd=folder,check=True)
    capture=json.loads((folder/'capture-result.json').read_text())
    if capture['procedure']!=procedure:
        raise SystemExit('Recorded procedure differs from requested browser condition')
    condition_record.update(run_id=folder.name,bench_sha256=sha(args.bench),
                            capture_result_sha256=sha(folder/'capture-result.json'),
                            preparation=cfg)
    condition_path=folder/'host-condition.json'
    with condition_path.open('x') as out:json.dump(condition_record,out,indent=2);out.write('\n')
    # Keep the Pi's checksum manifest unchanged; this separate receipt covers
    # the subsequently collected host confirmation and original manifest.
    (folder/'SHA256SUMS.host').write_text(f'{sha(condition_path)}  host-condition.json\n'
                                       f'{sha(folder/"SHA256SUMS")}  SHA256SUMS\n')
    print('Local evidence: '+str(folder),flush=True)
    print('Wait for the Agon result and MOS prompt, then return the SD. No screenshot needed.',flush=True)
    raise SystemExit(rc)


if __name__=='__main__':main()
