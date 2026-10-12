#!/usr/bin/env python3
"""Verify RGB222 expansion, Native alias ordering and protected span bounds."""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='rgb222-bgr-lut-') as directory:
        binary = Path(directory) / 'check'
        subprocess.run([
            'g++', '-std=c++17', '-O2', '-g',
            *(['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
              if args.sanitize else []),
            '-I' + str(ROOT / 'vdp/video'),
            str(Path(__file__).with_suffix('.cpp')), '-o', str(binary),
        ], check=True)
        subprocess.run([str(binary)], check=True, timeout=30)


if __name__ == '__main__':
    main()
