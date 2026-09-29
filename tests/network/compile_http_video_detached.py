#!/usr/bin/env python3
"""Compile the detached public interface using a native actual-IDF build."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build-output', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
database = args.build_output / 'build/compile_commands.json'
entry = next(row for row in json.loads(database.read_text())
             if row['file'].endswith('/http_video_service.cpp'))
command = entry.get('arguments') or shlex.split(entry['command'])
command += ['-I' + str(root / 'vdp/video'), '-include', 'sdkconfig.h']
with tempfile.TemporaryDirectory() as temp:
    command[command.index('-o') + 1] = str(Path(temp) / 'consumer.o')
    command[command.index('-c') + 1] = str(root / 'tests/network/http_video_detached_compile.cpp')
    result = subprocess.run(command, cwd=entry['directory'])
    if result.returncode:
        raise SystemExit(result.returncode)
print('PASS: detached consumer compiles against actual ESP-IDF headers/toolchain')
