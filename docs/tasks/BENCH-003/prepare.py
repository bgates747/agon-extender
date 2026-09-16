#!/usr/bin/env python3
"""Build an isolated two-vblank RAM-timestamp derivative; never edit repair source."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert not a.output.exists();a.output.mkdir(parents=True)
src=a.output/'asm';shutil.copytree(a.source/'src/asm',src)
def replace(file,old,new):
 path=src/file;s=path.read_text();assert s.count(old)==1,(file,old);path.write_text(s.replace(old,new))
replace('nurples.asm','    call vdu_vblank\n; poll keyboard','    call vdu_vblank\n    call vdu_vblank\n    call bench_record\n; poll keyboard')
replace('nurples.asm','    include "tables.inc"','    include "bench.inc"\n    include "tables.inc"')
replace('state_game_init.inc','    call choose_joystick','    ; BENCH-003: automated fixture, no GPIO joystick.\n    call player_joystick_disable')
replace('state_game_init.inc','    call vdu_flip \n    call waitKeypress','    call vdu_flip \n    ; BENCH-003: automated start, bypass title key wait.')
replace('state.inc','\ngame_over:\n','\ngame_over:\n    jp game_exit ; BENCH-003: end at game over; never wait unattended.\n')
(src/'bench.inc').write_text('''; BENCH-003: bounded RAM-only post-vblank timestamps, no serial/VDU output.
; Loaded fresh for each run. Table allocation follows this record, preventing overlap.
bench_record:
    push af
    push bc
    push de
    push hl
    push ix
    MOSCALL mos_sysvars
    ld de,(ix+sysvar_time)
    ld hl,(bench_next)
    ld (hl),de
    inc hl
    inc hl
    inc hl
    ld de,(game_state)
    ld (hl),de
    inc hl
    inc hl
    inc hl
    ld (bench_next),hl
    ld hl,(bench_count)
    inc hl
    ld (bench_count),hl
    ld de,1800
    or a
    sbc hl,de
    jp c,@done
    ld a,1
    ld (game_exit_requested),a
@done:
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret
bench_next: dl bench_records
bench_begin:
    db "B003TIME"
bench_count: dl 0
    db 1
bench_records: ds 10800
bench_end:
''')
subprocess.run([str(Path.home()/'.local/bin/ez80asm'),'-l','-s','nurples.asm','cadence.bin'],cwd=src,check=True)
shutil.copy2(src/'cadence.bin',a.output/'cadence.bin');shutil.copy2(src/'nurples.symbols',a.output/'cadence.symbols') if (src/'nurples.symbols').exists() else shutil.copy2(src/'cadence.symbols',a.output/'cadence.symbols')
files={str(f.relative_to(src)):hashlib.sha256(f.read_bytes()).hexdigest() for f in src.glob('*.inc')};files['nurples.asm']=hashlib.sha256((src/'nurples.asm').read_bytes()).hexdigest()
(a.output/'build.json').write_text(json.dumps({'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.source,text=True).strip(),'source_dirty':True,'binary_sha256':hashlib.sha256((a.output/'cadence.bin').read_bytes()).hexdigest(),'inputs':files,'limit':'Diagnostic derivative; same source and assets, not an unmodified production timing claim.'},indent=2)+'\n')
