#!/usr/bin/env python3
"""Build and identify the stopped NET-009 P4 Ethernet peer."""

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDF = ROOT / 'agents/build001/native-tools/esp-idf'
IDF_COMMIT = 'b774170ff46c393eeb5e495ea37936038d3f4f4f'
PROJECT = ROOT / 'vdp/fixtures/net009_ethernet'
INPUTS = (
    PROJECT, ROOT / 'vdp/fixtures/esp8266_uart/main/bw_codec.h',
    ROOT / 'vdp/partitions.csv', ROOT / 'vdp/build/boards/p4-pc.json',
    Path(__file__).resolve(), ROOT / 'scripts/net009_p4_peer.py',
    ROOT / 'scripts/net009_pi_uart.py', ROOT / 'scripts/modem_bw_protocol.py',
    ROOT / 'scripts/modem_bw_peer.py', ROOT / 'scripts/modem_join.py',
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_commit(directory):
    return subprocess.check_output(['git', '-C', directory, 'rev-parse', 'HEAD'],
                                   text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--tools-path', required=True, type=Path)
    parser.add_argument('--python-env', required=True, type=Path)
    args = parser.parse_args()
    paths = [str(path.relative_to(ROOT)) for path in INPUTS]
    if subprocess.check_output(['git', 'status', '--porcelain', '--', *paths], cwd=ROOT):
        raise SystemExit('Commit the selected build inputs first')
    if get_commit(IDF) != IDF_COMMIT:
        raise SystemExit('Unexpected ESP-IDF commit')
    source = get_commit(ROOT)
    files = sorted(path for entry in INPUTS
                   for path in (entry.rglob('*') if entry.is_dir() else [entry])
                   if path.is_file())
    pins = {str(path.relative_to(ROOT)): sha(path) for path in files}
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    config = out / 'sdkconfig'
    config.write_text((PROJECT / 'sdkconfig.defaults').read_text() +
                      '\nCONFIG_PARTITION_TABLE_CUSTOM=y\n' +
                      f'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="{ROOT / "vdp/partitions.csv"}"\n')
    tools, python = args.tools_path.resolve(), args.python_env.resolve()
    env = dict(os.environ, IDF_PATH=str(IDF), IDF_TOOLS_PATH=str(tools),
               IDF_PYTHON_ENV_PATH=str(python), ESP_IDF_VERSION='5.5',
               IDF_COMPONENT_MANAGER='0',
               ESP_ROM_ELF_DIR=str(next(tools.glob('tools/esp-rom-elfs/*'))))
    env['PATH'] = os.pathsep.join([str(python / 'bin'), *map(str, tools.glob('tools/**/bin')),
                                  env['PATH']])
    argv = [str(python / 'bin/python'), str(IDF / 'tools/idf.py'), '-C', str(PROJECT),
            '-B', str(out / 'build'), '-DIDF_TARGET=esp32p4', f'-DSDKCONFIG={config}',
            f'-DNET009_SOURCE_COMMIT={source}', 'build']
    (out / 'command.json').write_text(json.dumps(argv, indent=2) + '\n')
    with (out / 'build.log').open('x') as log:
        subprocess.run(argv, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
    layout = json.loads((out / 'build/flasher_args.json').read_text())
    if layout['app']['offset'] != '0x20000' or any(sha(ROOT / p) != h for p, h in pins.items()):
        raise SystemExit('Build configuration or source inputs changed')
    app = out / 'build' / layout['app']['file']
    manifest = dict(source_commit=source, idf_commit=IDF_COMMIT, source_inputs=pins,
                    board='Olimex ESP32-P4-PC Rev C', start_required=True,
                    app=dict(path=str(app), offset=layout['app']['offset'],
                             bytes=app.stat().st_size, sha256=sha(app)),
                    sdkconfig_sha256=sha(config))
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
