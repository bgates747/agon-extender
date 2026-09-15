"""Copy pinned Nurples sources into an isolated benchmark; never edit the game."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--hardware',action='store_true');p.add_argument('--unfenced',action='store_true');p.add_argument('--sustained',action='store_true');a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
files=list(a.source.glob('*.inc'))+[a.source/'nurples.asm']
manifest={}
for f in files:
    manifest[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
    (a.output/f.name).write_bytes(f.read_bytes())
def replace(name,old,new,count=1):
    f=a.output/name;s=f.read_text();assert s.count(old)==count,(name,old,s.count(old));f.write_text(s.replace(old,new))
replace('nurples.asm','main:\n','main:\n    jp bench_start\n')
replace('nurples.asm','    include "tables.inc"','    include "bench.inc"\n    include "tables.inc"')
# Game mode is selected in autoexec. Save/query remains for provenance only.
f=a.output/'state_game_init.inc';s=f.read_text();s=s.replace('    call vdu_set_screen_mode','    ; fixture: mode20 selected by autoexec').replace('    call waitKeypress','    ; fixture: no interactive loading gate').replace('    call vdu_flip','    ; fixture: single-buffered mode20').replace('    call choose_joystick','    call player_joystick_disable');f.write_text(s)
replace('player_input.inc','    MOSCALL    mos_getkbmap','    ld ix,bench_keys ; fixture input instead of MOS map\n;    MOSCALL    mos_getkbmap')
replace('player_input.inc','    in a,(portC)','    ld a,255 ; fixture neutral joystick\n;    in a,(portC)')
replace('player_input.inc','    in a,(portD)','    ld a,255 ; fixture neutral fire pin\n;    in a,(portD)')
f=a.output/'timer.inc';s=f.read_text();s=re.sub(r'ld (hl|de),\(ix\+sysvar_time\)',r'ld \1,(bench_time)',s);f.write_text(s)
replace('vdu.inc','vdu_vblank:', 'vdu_vblank:\n    call bench_boundary')
# End is handled at the boundary, including frames inside death animations.
# Timing routine and real vblank pacing otherwise remain unchanged.
replace('state.inc','\ngame_over:\n','\ngame_over:\n    jp bench_game_over\n')
replace('state.inc','\ngame_victory:\n','\ngame_victory:\n    jp bench_game_victory\n')
bench=(Path(__file__).parent/'verified_bench.inc').read_text()
bench=bench.replace('BENCH_CAPACITY',str(2400 if a.sustained else 600)).replace('BENCH_VARIANT',str(int(not a.unfenced)|(int(a.hardware)<<1)))
bench=bench.replace('bench_hw: db 0','bench_hw: db '+str(int(a.hardware))).replace('bench_fenced: db 1','bench_fenced: db '+str(int(not a.unfenced)))
(a.output/'bench.inc').write_text(bench)
(a.output/'manifest.json').write_text(json.dumps(dict(source_sha256=manifest,fixture='nurples-parity-probe-r04',run_nonce_required=True,sustained=a.sustained,hardware=a.hardware,fenced=not a.unfenced,limits=('2400 boundaries or terminal game state; live-sprite counts; ' if a.sustained else '600 boundaries; ')+'simulated two ticks per boundary, fixed seed and held fire, optional pixel completion query'),indent=2)+'\n')
subprocess.run(['ez80asm','-l','nurples.asm','NPBENCH.bin'],cwd=a.output,check=True)
