#!/usr/bin/env python3
"""Passive bounded UART acquisition; caller launches the frozen wire fixture.

Reuse AUDIT-005 acquisition/packing checks. The current pinwalk independently
confirmed its four physical channels. No serial observer, reset or board write.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

TASK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK.parents[1] / 'AUDIT-005/scripts'))
from capture_trace import RATE, SAMPLES, discover, inspect, pack_raw, sha

p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output
out.mkdir(parents=True, exist_ok=False)
record = dict(run_id='PORT-008-' + datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ'),
              purpose='pure UART wire selection; no rendering or output observer',
              procedure='WIRE-PROCEDURE.md short invocation',
              acquisition_pass=False, helper_sha256=sha(__file__))
process = None
try:
    connection = discover(out)
    raw = out / 'logic.raw'
    command = ['sigrok-cli', '--loglevel', '2', '--driver', 'fx2lafw:conn=' + connection,
               '--config', f'samplerate={RATE}', '--channels', 'D1,D3,D4,D6',
               '--samples', str(SAMPLES), '--output-format', 'binary', '--output-file', str(raw)]
    record['argv'] = command
    with (out/'sigrok.log').open('wb') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        started = time.monotonic()
        while time.monotonic()-started < 5:
            if process.poll() is not None:
                raise RuntimeError('Acquisition stopped before readiness')
            if raw.exists() and raw.stat().st_size >= 65536:
                break
            time.sleep(.05)
        else:
            raise RuntimeError('No delivered samples within five seconds')
        (out/'ready.json').write_text(json.dumps(dict(delivered_samples=raw.stat().st_size,
            utc=datetime.now(timezone.utc).isoformat()))+'\n')
        print('Samples arriving; launch the staged wire batch now.', flush=True)
        process.wait(timeout=60)
    record['exit_code'] = process.returncode
    record['raw_samples_sha256'] = pack_raw(raw, out/'logic.sr')
    record['acquisition'] = inspect(out/'logic.sr')
    record['acquisition_pass'] = process.returncode == 0 and record['acquisition']['acquisition_pass']
except Exception as error:
    record['error'] = str(error)
finally:
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    record['ended_utc'] = datetime.now(timezone.utc).isoformat()
    (out/'capture-result.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2), flush=True)
raise SystemExit(not record['acquisition_pass'])
