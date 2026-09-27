#!/usr/bin/env python3
"""Compile the detached public interface using an existing actual-IDF build.
Not a separate firmware link or runtime test; run pio p4-console first.
"""
import json
from pathlib import Path
import shlex
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
database = root / 'vdp/.pio/build/p4-console/compile_commands.json'
entry = next(row for row in json.loads(database.read_text())
             if row['file'].endswith('/http_video_service.cpp'))
args = shlex.split(entry['command'])
args += ['-I' + str(root / 'vdp/video'),
         '-I' + str(root / 'vdp/.pio/packages/framework-espidf/components/esp_http_server/include'),
         '-I' + str(root / 'vdp/.pio/packages/framework-espidf/components/http_parser'),
         '-include', 'sdkconfig.h']
with tempfile.TemporaryDirectory() as temp:
    args[args.index('-o') + 1] = str(Path(temp) / 'consumer.o')
    args[args.index('-c') + 1] = str(root / 'tests/network/http_video_detached_compile.cpp')
    result = subprocess.run(args, cwd=entry['directory'])
    if result.returncode:
        raise SystemExit(result.returncode)
print('PASS: detached consumer compiles against actual ESP-IDF headers/toolchain')
