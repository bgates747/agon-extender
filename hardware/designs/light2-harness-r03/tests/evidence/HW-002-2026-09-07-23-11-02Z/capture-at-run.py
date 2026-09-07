#!/usr/bin/env python3
"""Run the Pi capture from the workstation; preserve raw evidence and decode PC0-PC7."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[3]
MAP = [('PC0', 'D1', 1), ('PC1', 'D6', 2), ('PC2', 'D3', 3), ('PC3', 'D4', 4),
       ('PC4', 'D5', 5), ('PC5', 'D2', 6), ('PC6', 'D7', 7), ('PC7', 'D0', 8)]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check Pi/analyzer without capturing')
    parser.add_argument('--config', type=Path, default=REPOSITORY / 'agents/bench/hw002-pinwalk.json')
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    opts = ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', '-o', 'IdentitiesOnly=yes',
            '-o', 'UserKnownHostsFile=' + cfg['known_hosts'], '-i', cfg['key']]
    ssh = ['ssh', *opts, cfg['target']]
    remote_root = cfg['capture_root']
    helper = remote_root + '/capture-on-pi.sh'
    subprocess.run(ssh + ['mkdir -p -- ' + shlex.quote(remote_root)], check=True)
    subprocess.run(['scp', '-q', *opts, str(ROOT / 'capture-on-pi.sh'),
                    cfg['target'] + ':' + helper], check=True)
    if args.check:
        subprocess.run(ssh + ['bash ' + shlex.quote(helper) + ' /unused check'], check=True)
        print('PASS: Pi reachable and one analyzer found; no capture or reset performed.')
        return 0
    run_id = datetime.now(timezone.utc).strftime('HW-002-%Y-%m-%d-%H-%M-%SZ')
    local = REPOSITORY / 'agents/evidence' / run_id
    local.mkdir(parents=True, exist_ok=False)
    remote = remote_root + '/' + run_id
    print('Use the prepared SD card. P4 connections must be released inputs before the Agon drives them.', flush=True)
    command = 'bash ' + shlex.quote(helper) + ' ' + shlex.quote(remote)
    result = subprocess.run(ssh + [command])
    # Fetch the entire unique run directory even after capture failure.
    fetched = subprocess.run(['scp', '-q', '-r', *opts, cfg['target'] + ':' + remote + '/.', str(local)])
    if fetched.returncode:
        print('Capture/retrieval incomplete; inspect Pi output. Local directory:', local)
        return 1
    subprocess.run(['sha256sum', '--check', '--strict', 'SHA256SUMS'], cwd=local, check=True)
    (local / 'run-parameters.json').write_text(json.dumps({
        'run_id': run_id, 'status': 'diagnostic', 'operator_reports_stock_mos_vdp': True,
        'displayed_versions': None, 'samplerate_hz': 100000, 'samples': 6000000,
        'expectations': MAP, 'probe_position': None,
    }, indent=2) + '\n')
    manifest = ROOT / 'bin/build-manifest.yaml'
    if manifest.exists():
        (local / 'prepared-build.yaml').write_bytes(manifest.read_bytes())
    provenance = [ROOT / 'capture.py', ROOT / 'capture-on-pi.sh', Path(cfg['analyzer']),
                  Path(cfg['analyzer']).with_name('analyze_la_capture.py')]
    (local / 'tool-hashes.json').write_text(json.dumps(
        {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in provenance}, indent=2) + '\n')
    print('Evidence:', local, flush=True)
    if result.returncode:
        print('Capture failed; raw output retained.')
        return result.returncode
    # A pulse-count match in a truncated capture is not a complete run.
    sys.path.insert(0, str(Path(cfg['analyzer']).parent))
    from analyze_la_capture import load_capture
    rate, samples, probes = load_capture(local / 'logic.sr')
    if rate != 100000 or len(samples) != 6000000 or set(probes) != {f'D{i}' for i in range(8)}:
        print('FAIL: capture rate, length, or channel set differs from the procedure.')
        return 1
    analyze = [sys.executable, cfg['analyzer'], str(local / 'logic.sr'),
               '--output', str(local / 'pinwalk-analysis.json')]
    for signal, channel, count in MAP:
        analyze += ['--expect', f'{signal}:{channel}:{count}']
    return subprocess.run(analyze).returncode

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print('FAIL:', error, file=sys.stderr)
        raise SystemExit(1)
