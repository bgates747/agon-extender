#!/usr/bin/env python3
"""Pi-side passive acquisition for uart-path-capture-r01. Never opens P4 serial.

The 30-second untriggered window includes operator reaction and Agon boot.
Readiness requires delivered USB samples, not merely a live sigrok process.
fx2lafw may exit successfully after short acquisition; inspect saved extent.
Private device metadata belongs in the ignored run folder, not tracked evidence.
"""
import argparse
import configparser
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import zipfile

PROCEDURE = 'uart-path-capture-r01'
RATE = 24_000_000
SAMPLES = 720_000_000
CHANNELS = {'probe2': 'D1', 'probe4': 'D3', 'probe5': 'D4', 'probe7': 'D6'}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def discover(folder):
    for attempt in range(2):
        scan = subprocess.check_output(['sigrok-cli', '--scan', '--show'], text=True, timeout=15)
        (folder / f'scan-{attempt}.txt').write_text(scan)
        rows = [line for line in scan.splitlines() if line.startswith('fx2lafw')]
        if rows == ['fx2lafw - Saleae Logic with 8 channels: D0 D1 D2 D3 D4 D5 D6 D7'] and attempt == 0:
            # First scan can load fx2 firmware and cause analyzer re-enumeration.
            time.sleep(2)
            continue
        if len(rows) != 1:
            raise ValueError(f'Expected exactly one known analyzer, found {len(rows)}')
        match = re.fullmatch(r'fx2lafw:conn=(\d+\.\d+) - Saleae Logic \[S/N: Saleae Logic\] '
                             r'with 8 channels: D0 D1 D2 D3 D4 D5 D6 D7', rows[0])
        if not match:
            raise ValueError('Analyzer identity/channel set differs from the procedure')
        return match[1]
    raise ValueError('Analyzer did not finish re-enumerating')


def metadata(archive):
    config = configparser.ConfigParser()
    config.read_string(archive.read('metadata').decode())
    if [x for x in config.sections() if x.startswith('device ')] != ['device 1']:
        raise ValueError('Expected one captured device')
    dev = config['device 1']
    channels = {k: v for k, v in dev.items() if re.fullmatch(r'probe\d+', k)}
    if dev['samplerate'] != '24 MHz' or dev['unitsize'] != '1' or channels != CHANNELS:
        raise ValueError('Unexpected sample rate, packing or physical channel mapping')
    prefix = re.escape(dev['capturefile'])
    names = sorted((x.filename for x in archive.infolist() if re.fullmatch(prefix+r'-\d+', x.filename)),
                   key=lambda n: int(n.rsplit('-', 1)[1]))
    if not names or [int(n.rsplit('-', 1)[1]) for n in names] != list(range(1, len(names)+1)):
        raise ValueError('Missing or nonconsecutive logic chunks')
    return names, sum(archive.getinfo(n).file_size for n in names)


def inspect(path):
    with zipfile.ZipFile(path) as archive:
        names, samples = metadata(archive)
        if archive.testzip() is not None:
            raise ValueError('Capture archive CRC failure')
    return dict(samples=samples, sample_rate_hz=RATE, seconds=samples/RATE,
                expected_samples=SAMPLES, acquisition_pass=samples == SAMPLES, sha256=sha(path))


def pack_raw(raw, destination):
    # libsigrok 0.5.2 output/binary.c passes logic->data unchanged, including
    # original physical bit positions. Defer ZIP compression until acquisition
    # ends so archive work cannot delay servicing USB. Keep the raw hash and
    # verify extraction against it before deleting this temporary raw copy.
    text = ('[global]\nsigrok version=0.5.2\n[device 1]\ncapturefile=logic-1\n'
            'total probes=8\nsamplerate=24 MHz\ntotal analog=0\n'
            'probe2=D1\nprobe4=D3\nprobe5=D4\nprobe7=D6\nunitsize=1\n')
    expected = sha(raw)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        archive.writestr('version', '2')
        archive.writestr('metadata', text)
        archive.write(raw, 'logic-1-1')
    with zipfile.ZipFile(destination) as archive, archive.open('logic-1-1') as source:
        actual = hashlib.file_digest(source, 'sha256').hexdigest()
    if actual != expected: raise ValueError('Packed sample bytes differ from acquisition')
    raw.unlink()
    return expected


def capture(folder, idle_check=False):
    record = dict(procedure=PROCEDURE, run_id=folder.name,
                  started_at=datetime.now(timezone.utc).isoformat(),
                  purpose='passive acquisition check' if idle_check else 'counted-point workload',
                  reset_cue_issued=False, acquisition_pass=False, waveform_verdict='not evaluated',
                  helper_sha256=sha(__file__))
    proc = None
    try:
        connection = discover(folder)
        (folder/'sigrok-version.txt').write_text(subprocess.check_output(
            ['sigrok-cli', '--version'], text=True, stderr=subprocess.STDOUT, timeout=10))
        raw = folder/'logic.raw'
        args = ['sigrok-cli', '--loglevel', '2', '--driver', 'fx2lafw:conn='+connection,
                '--config', f'samplerate={RATE}', '--channels', 'D1,D3,D4,D6',
                '--samples', str(SAMPLES), '--output-format', 'binary', '--output-file', str(raw)]
        record['argv'] = args
        begin = time.monotonic()
        with (folder/'sigrok.log').open('wb') as log:
            proc = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT)
            while time.monotonic()-begin < 5:
                if proc.poll() is not None:
                    raise RuntimeError('Analyzer stopped before readiness')
                if raw.exists() and raw.stat().st_size >= 65536:
                    break
                time.sleep(.05)
            else:
                raise RuntimeError('No delivered samples within five seconds')
            record['ready_seconds_after_start'] = time.monotonic()-begin
            if not idle_check:
                record['reset_cue_issued'] = True
                record['reset_cue_utc'] = datetime.now(timezone.utc).isoformat()
                print('\nReset Agon now. Press and release reset once within five seconds.\n'
                      'Leave keys released. Acquisition ends about 30 seconds from now.\n', flush=True)
            proc.wait(timeout=max(1, 60-(time.monotonic()-begin)))
        record['exit_code'] = proc.returncode
        record['raw_samples_sha256'] = pack_raw(raw, folder/'logic.sr')
        record['acquisition'] = inspect(folder/'logic.sr')
        record['acquisition_pass'] = proc.returncode == 0 and record['acquisition']['acquisition_pass']
    except (Exception, KeyboardInterrupt) as exc:
        record['error'] = str(exc) or type(exc).__name__
        print('Capture stopped: '+record['error'], flush=True)
        if not record['reset_cue_issued']:
            print('Do not reset Agon; no reset cue was issued.', flush=True)
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)
        record['ended_at'] = datetime.now(timezone.utc).isoformat()
        (folder/'capture-result.json').write_text(json.dumps(record, indent=2)+'\n')
        (folder/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(folder.iterdir())
                                                 if p.is_file() and p.name != 'SHA256SUMS'))
    print(('Acquisition passed' if record['acquisition_pass'] else 'Acquisition failed')+
          ': 24 MHz, 720 million samples.', flush=True)
    print('Workload coverage and the saved Agon result require separate validation.', flush=True)
    print('Evidence: '+str(folder), flush=True)
    return 0 if record['acquisition_pass'] and 'error' not in record else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-parent', type=Path, required=True)
    parser.add_argument('--idle-check', action='store_true', help='Same passive capture; no operator reset cue')
    args = parser.parse_args()
    folder = args.output_parent / ('AUDIT-005-'+datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ'))
    folder.mkdir(parents=True, exist_ok=False)
    raise SystemExit(capture(folder, args.idle_check))


if __name__ == '__main__': main()
