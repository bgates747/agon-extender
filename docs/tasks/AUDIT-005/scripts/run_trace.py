#!/usr/bin/env python3
"""Workstation runner. Private SSH paths/host come from an ignored bench JSON.

Only executes the staged passive analyzer helper and retrieves evidence. The
operator inserts the prepared SD and resets Agon after the explicit cue.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
import subprocess
import sys
from capture_trace import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bench',type=Path,required=True)
    args=p.parse_args()
    cfg=json.loads(args.bench.read_text())
    helper=Path(__file__).with_name('capture_trace.py')
    if sha(helper)!=cfg['capture_helper_sha256']:
        p.error('Capture helper changed since preparation; restage and recheck')
    print('Insert the prepared SD. Keep both boards powered and ribbons seated.\n'
          'Connect one browser video client and leave it visible.\n'
          'Probes: yellow PC0, gray PC1, orange PC2, purple PC3; common ground.\n'
          'Wait for the reset cue. The P4 will remain running.\n',flush=True)
    try:input('Press Enter when ready: ')
    except (EOFError,KeyboardInterrupt):raise SystemExit('\nCancelled before acquisition.')
    dest=Path(cfg['local_captures']);dest.mkdir(parents=True,exist_ok=True)
    log=dest/('console-'+datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')+'.txt')
    options=cfg['ssh_options'];host=cfg['host'];remote=cfg['remote_stage']
    print('\nArming analyzer...',flush=True)
    remote_sha=subprocess.check_output(['ssh',*options,host,shlex.join(
        ['sha256sum',remote+'/capture_trace.py'])],text=True,timeout=20).split()[0]
    if remote_sha!=cfg['capture_helper_sha256']:
        raise SystemExit('Remote helper changed; do not reset Agon.')
    command=['python3','-u',remote+'/capture_trace.py','--output-parent',remote+'/captures']
    recorded=None
    with log.open('w') as out:
        out.write('Preparation: '+args.bench.read_text()+'\n')
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
    print('Local evidence: '+str(folder),flush=True)
    print('Wait for the Agon result and MOS prompt, then return the SD. No screenshot needed.',flush=True)
    raise SystemExit(rc)


if __name__=='__main__':main()
