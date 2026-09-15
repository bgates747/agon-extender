"""Repeat the bounded audit using an explicitly prepared local target command.

The command JSON is an argv array, not shell text. Prepare its include paths and
P4/Arduino definitions for the identified source snapshot as described in README.
Output belongs in an ignored directory. This does not build or flash firmware.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--source-root', type=Path, required=True)
p.add_argument('--command-json', type=Path, required=True)
p.add_argument('--cwd', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
root = a.source_root.resolve()
command = json.loads(a.command_json.read_text())
entry = str(root / 'video/extender/boot/p4_console.cpp')
if command.count(entry) != 1 or '-fsyntax-only' not in command:
    raise SystemExit('Expected one identified console source and syntax-only command')
if any(x in command for x in ('-o', '-c', '-MD', '-MMD', '-MF', '-MT', '-MQ')):
    raise SystemExit('Remove object/dependency-output flags before analysis')
if any(x.startswith('-fdump-') for x in command):
    raise SystemExit('Remove prior dump flags; this script owns dump output')
a.output.mkdir(parents=True, exist_ok=False)
selection = json.loads((root / 'pio/p4-console-source-selection.json').read_text())
units = selection['project_translation_units'] + selection['vendored_translation_units']

def inspect_unit(relative):
    source = root / relative
    log = a.output.resolve() / ('unit-' + relative.replace('/', '_') + '.txt')
    argv = [str(source) if arg == entry else arg for arg in command]
    argv += ['-fdump-tree-original-raw=' + str(log.with_suffix('.raw'))]
    result = subprocess.run(argv, cwd=a.cwd, capture_output=True, text=True)
    log.write_text(result.stdout + result.stderr)
    return dict(file=relative, sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                returncode=result.returncode, log=log.name,
                warnings=result.stderr.count('[-Wfloat-conversion]'))

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(inspect_unit, units))
(a.output / 'units.json').write_text(json.dumps(results, indent=2) + '\n')
print(f'{len(results)} units; {sum(bool(x["returncode"]) for x in results)} failed')
raise SystemExit(any(x['returncode'] for x in results))
