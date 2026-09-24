#!/usr/bin/env python3
"""Read-only A08-01 accounting, adapted from INTEG-014 E02's map ledger.
No firmware generation, source modification or deployment. Requires pyelftools.
Input: a completed canonical mos-port build directory. Outputs portable evidence.
"""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
from elftools.elf.elffile import ELFFile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('build', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
b = a.build / 'bin'
with (b / 'MOS.elf').open('rb') as f:
    elf = ELFFile(f)
    sections = {}
    for s in elf.iter_sections():
        if not s['sh_flags'] & 2:
            continue
        sections[s.name] = {'bytes': s['sh_size'], 'vma': s['sh_addr'],
                            'rom': s['sh_type'] != 'SHT_NOBITS'}
    syms = list(elf.get_section_by_name('.symtab').iter_symbols())
    functions = [{'name': s.name, 'address': s['st_value'], 'bytes': s['st_size']}
                 for s in syms if s['st_info']['type'] == 'STT_FUNC' and s['st_size']]
    symbols = {s.name: s['st_value'] for s in syms}
objects = defaultdict(lambda: {'rom': 0, 'ram': 0, 'text': 0, 'rodata': 0,
                               'data': 0, 'bss': 0, 'vectors': 0})
output = pending = None
for line in (b / 'MOS.map').read_text().split('Linker script and memory map', 1)[1].splitlines():
    m = re.match(r'^(\.\S+)\s+0x', line)
    if m:
        output, pending = m[1], None
    if output not in sections:
        continue
    m = re.match(r'^ ([\w.]+)\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+(.+\.o\)?)$', line)
    if not m and pending:
        n = re.match(r'^\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+(.+\.o\)?)$', line)
        if n:
            m = (pending, *n.groups())
    if isinstance(m, re.Match):
        m = m.groups()
    if m:
        sec, addr, size, obj = m
        size = int(size, 16)
        assert not obj.startswith('/'), 'Evidence must not publish local paths'
        entry = objects[obj]
        if sections[output]['rom']:
            entry['rom'] += size
        if sections[output]['vma'] >= 0xbc000:
            entry['ram'] += size
        category = ('text' if output in ('.text', '.startup', '.reset') else
                    'vectors' if output in ('.ivecs', '.ivjmptbl', '.reset_fill') else output[1:])
        entry[category] += size
        pending = None
    else:
        m = re.match(r'^ ([\w.]+)\s*$', line)
        pending = m[1] if m else None
rom = sum(s['bytes'] for s in sections.values() if s['rom'])
ram = sum(s['bytes'] for s in sections.values() if s['vma'] >= 0xbc000)
assert rom == (b / 'MOS.bin').stat().st_size == symbols['__rom_ro_end'] + sections['.data']['bytes']
assert ram == sum(s['ram'] for s in objects.values())
assert sum(f['bytes'] for f in functions if f['name'].startswith('_emos_')) < rom
raw = (b / 'MOS.bin').read_bytes()
identities = sorted(set(x.decode() for x in re.findall(rb'agon-emos-v[\w.]+-b[\dTZ-]+', raw)))
summary = {'rom_capacity_bytes': 131072, 'rom_used_bytes': rom,
           'rom_free_bytes': 131072-rom, 'rom_free_percent': 100*(131072-rom)/131072,
           'static_ram_bytes': ram, 'stack_reserve_bytes': 2048,
           'heap_arena_bytes': 16384-ram-2048,
           'linker_fill_bytes': rom-sum(s['rom'] for s in objects.values()),
           'build_identities': identities,
           'artifacts': {n: {'bytes': (b/n).stat().st_size,
                             'sha256': hashlib.sha256((b/n).read_bytes()).hexdigest()}
                         for n in ('MOS.bin', 'MOS.elf', 'MOS.map')},
           'sections': sections, 'objects': dict(objects)}
(a.output/'BASELINE.json').write_text(json.dumps(summary, indent=2)+'\n')
with (a.output/'OBJECTS.csv').open('w') as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(['object','rom','ram','text','rodata','data','bss','vectors'])
    for name, s in sorted(objects.items(), key=lambda x: (-x[1]['rom'], x[0])):
        w.writerow([name, *s.values()])
with (a.output/'FUNCTIONS.csv').open('w') as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(['symbol', 'address_hex', 'code_bytes'])
    for s in sorted(functions, key=lambda s: (-s['bytes'], s['name'])):
        w.writerow([s['name'], f"0x{s['address']:06x}", s['bytes']])
print(json.dumps({k:v for k,v in summary.items() if not isinstance(v, dict)}, indent=2))
