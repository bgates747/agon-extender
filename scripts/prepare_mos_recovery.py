#!/usr/bin/env python3
"""Prepare a manifest-bound MOS payload for the maintained P4 programmer."""
import argparse
import hashlib
import json
from pathlib import Path
import zlib

AGENT_SHA = 'ca44786969dc2dd1b0fa51e6b80f530b7241317dc27bf8efac3ca7d56bddee06'


def checked(path, digest, minimum, maximum):
    data = path.read_bytes()
    if not minimum <= len(data) <= maximum:
        raise ValueError(f'{path}: unsupported size {len(data)}')
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f'{path}: SHA-256 mismatch')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mos', type=Path, required=True)
    parser.add_argument('--mos-sha256', required=True)
    parser.add_argument('--flash-agent', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    mos = checked(args.mos, args.mos_sha256, 1, 131072)
    agent = checked(args.flash_agent, AGENT_SHA, 90, 90)
    text = ['// Generated; do not edit or commit.', '#pragma once',
            '#include <cstddef>', '#include <cstdint>',
            'namespace agon_extender::diagnostic::recovery_payload {']
    manifest = {'procedure': 'mos-recovery-r01', 'payloads': {}}
    for role, name, data in [('mos', 'Mos', mos), ('flash_agent', 'FlashAgent', agent)]:
        digest = hashlib.sha256(data).hexdigest()
        crc = zlib.crc32(data)
        array = 'MosImage' if role == 'mos' else name
        text += [f'inline constexpr char k{name}Sha256[] = "{digest}";',
                 f'inline constexpr uint32_t k{name}Crc32 = 0x{crc:08X}U;',
                 f'alignas(4) inline constexpr uint8_t k{array}[] = {{']
        text += [','.join(f'0x{x:02X}' for x in data[n:n+16])+',' for n in range(0,len(data),16)]
        text += ['};', f'inline constexpr size_t k{name}Size = sizeof(k{array});']
        manifest['payloads'][role] = {'bytes': len(data), 'sha256': digest, 'crc32': f'{crc:08x}'}
    text += ['}']
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(text)+'\n')
    args.output.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
