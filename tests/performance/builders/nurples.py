#!/usr/bin/env python3
"""Build isolated game timing derivative; source checkout is never modified."""
import argparse
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--no-markers',action='store_true',help='Build pacing-only PRT control')
args=parser.parse_args()
if args.output.exists():parser.error('output must be a fresh directory')
args.output.parent.mkdir(parents=True,exist_ok=True)
from pathlib import Path
import shutil,subprocess
r=Path(__file__).resolve().parents[3];orig=args.source.resolve();out=args.output.resolve();out.mkdir(exist_ok=True)
shutil.copytree(orig/'src/asm',out/'asm',dirs_exist_ok=True)
s=(out/'asm/nurples.asm').read_text()
s=s.replace('main_loop:\n','    call game_init\n    ld hl,(game_state)\n    ld de,game_playing\n    or a\n    sbc hl,de\n    jp nz,main_end\n    call gt_reset\n    jp c,main_end\nmain_loop:\n    call gt_begin\n',1)
s=s.replace('    call vdu_vblank\n','    call gt_submit\n    call vdu_vblank\n    call gt_end\n    jp c,main_end\n',1)
# Keep loop bookkeeping/keyboard polling inside active time, before pacing.
start=s.index('; poll keyboard for escape keypress',s.index('main_loop:'))
end=s.index('; escape not pressed so loop',start)
tail=s[start:end];s=s[:start]+s[end:];s=s.replace('    call gt_submit\n',tail+'    call gt_submit\n',1)
s=s.replace('    call vdu_set_screen_mode','    ; Startup/CLI owns video mode')
s=s.replace('main_end:\n','main_end:\n    call gt_prt_close\n')
s=s.replace('; --- MAIN PROGRAM FILE ---','    include "gt.inc"\n; --- MAIN PROGRAM FILE ---')
(out/'asm/nurples.asm').write_text(s)
p=out/'asm/state_game_init.inc';s=p.read_text().replace('    call vdu_set_screen_mode','    ; Startup owns mode20').replace('    call choose_joystick','    call player_joystick_disable').replace('    call waitKeypress','    ; Noninteractive benchmark')
p.write_text(s)
p=out/'asm/player_state.inc';p.write_text(p.read_text().replace('ld bc,0*256','ld bc,sprite_right*128').replace('ld de,sprite_bottom*256','ld de,sprite_bottom*128'))
p=out/'asm/player_shields.inc';s=p.read_text().replace('update_shields:\n','update_shields:\n    ld a,64\n    ld (player_shields),a\n    or a\n    ret\n; Test-only invulnerability; production damage code retained below.\n');p.write_text(s)
# Preserve MOS map polling but use an all-released private input map.
p=out/'asm/player_input.inc';s=p.read_text().replace('MOSCALL    mos_getkbmap ;ix = pointer to MOS virtual keys table','MOSCALL    mos_getkbmap ; retain ordinary polling\n    ld ix,gt_keys ; deterministic no human control during capture');p.write_text(s)
(out/'asm/gt.inc').write_text('''; RAM-only loop records. Marker commands use admitted MOS output.
gt_keys: ds 16
gt_packet: db 23,0,0efh,5,0,0,0
gt_count: dl 0
gt_pointer: dl gt_rows
gt_t0: dl 0
gt_t1: dl 0
gt_data: db "GT1PRT!!"
gt_rows: ds 1440
gt_data_end:
gt_send:
    ld hl,gt_packet
    ld bc,7
    rst.lil 18h
    ret
gt_reset:
    call gt_prt_init
    ld a,l
    or a
    scf
    ret z
    ld a,5
    ld (gt_packet+3),a
    call gt_send
    or a
    ret
gt_begin:
    MOSCALL mos_sysvars
    ld hl,(ix+sysvar_time)
    ld (gt_t0),hl
    call gt_prt_begin
    ld hl,(gt_count)
    ld (gt_packet+4),hl
    ld a,6
    ld (gt_packet+3),a
    jp gt_send
gt_submit:
    ld a,7
    ld (gt_packet+3),a
    call gt_send
    call gt_prt_read
    ld (gt_t1),hl
    ret
gt_end:
    call gt_prt_read
    push hl
    MOSCALL mos_sysvars
    ld de,(ix+sysvar_time)
    ld hl,(gt_pointer)
    ld bc,(gt_t1)
    ld (hl),bc
    inc hl
    inc hl
    inc hl
    pop bc
    ld (hl),bc
    inc hl
    inc hl
    inc hl
    ld bc,(gt_t0)
    ld (hl),bc
    inc hl
    inc hl
    inc hl
    ld (hl),de
    inc hl
    inc hl
    inc hl
    ld (gt_pointer),hl
    ld hl,(gt_count)
    inc hl
    ld (gt_count),hl
    ld de,120
    or a
    sbc hl,de
    ccf
    ret
''')
prt=(r/'tests/performance/ez80/prt.asm').read_text()
prt='\n'.join(x for x in prt.splitlines() if not x.strip().startswith(('.section','.global','.assume'))).replace('_gt_prt','gt_prt')
with (out/'asm/gt.inc').open('a') as f:f.write('\n'+prt+'\n')
if args.no_markers:
 p=out/'asm/gt.inc';p.write_text(p.read_text().replace('gt_send:\n','gt_send:\n    ret ; Pacing-only control: suppress renderer markers\n'))
subprocess.run(['ez80asm','-s','nurples.asm','../ntiming.bin'],cwd=out/'asm',check=True)

from provenance import record
record(args.source,args.output,markers=not args.no_markers)
