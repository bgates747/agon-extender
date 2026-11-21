"""Run the corrected stock pilot and advance only after each window validates."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


def windows():
    yield 20, 'R', 1
    for mode in (20, 8, 0, 3, 136):
        for case in 'CRDB':
            for repetition in (1, 2, 3):
                if (mode, case, repetition) != (20, 'R', 1):
                    yield mode, case, repetition


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binding', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('previous', type=Path)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    previous = args.previous
    with (args.output / 'completed.jsonl').open('x') as log:
        for index, (mode, case, repetition) in enumerate(windows()):
            out = args.output / f'{index+1:02d}-m{mode}-{case}{repetition}'
            cmd = [sys.executable, str(Path(__file__).with_name('legacy_pilot.py')),
                   str(args.binding), str(out), '--previous', str(previous),
                   '--mode', str(mode), '--case', case]
            if index == 0:
                cmd.append('--pilot')
            print('Starting', out.name, flush=True)
            subprocess.run(cmd, check=True)
            result = json.loads((out / 'result.json').read_bytes())
            log.write(json.dumps(dict(epoch=time.time(), window=out.name, result=result)) + '\n')
            log.flush()
            previous = out / 'after.csv'


if __name__ == '__main__':
    main()
