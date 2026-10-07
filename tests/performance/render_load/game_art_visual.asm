; RGB-001 visual-only game-art review. EMOS/startup owns route and video mode.
; Native RGBA2222 assets; two poses/s, P pauses, Space steps, Escape exits.
; This is not the frozen rendering benchmark and produces no timing results.
; Double-buffered stock software sprites require application background redraw.
assume adl=1
org 040000h
jp start
align 64
db "MOS",0,1
start:
 push ix
 push iy
 ld a,8
 rst.lil 08h
 ld (sysvars),ix
 ld hl,key_callback
 ld c,0
 ld a,1dh
 rst.lil 08h
 ld c,10h
 ld a,40h
 rst.lil 08h
 ld hl,mode_query
 ld bc,3
 rst.lil 18h
 ld de,360
 call deadline
mode_wait:
 ld ix,(sysvars)
 bit 4,(ix+4)
 jr nz,mode_ready
 call elapsed
 jr c,mode_wait
 jp failed
mode_ready:
 ld a,(ix+27h)
 cp EXPECT_MODE
 jp nz,failed
 ld hl,initial
 ld bc,initial_end-initial
 rst.lil 18h
 call draw_pose
 jp nz,failed
 ; This visual-only carrier opens after the first completed drawing fence.
 ; The Pi uses its unique tag as independent runtime readiness evidence.
 ld hl,ready_marker
 ld bc,20
 rst.lil 18h
 ld de,60
 call deadline
idle:
 halt
 ld a,(escape)
 or a
 jp nz,success
 ld a,(pause_key)
 or a
 jr z,check_step
 xor a
 ld (pause_key),a
 ld a,(automatic)
 xor 1
 ld (automatic),a
 ld de,60
 call deadline
check_step:
 ld a,(step_key)
 or a
 jr z,check_clock
 xor a
 ld (step_key),a
 jr advance
check_clock:
 ld a,(automatic)
 or a
 jr z,idle
 call elapsed
 jr c,idle
advance:
 ld a,(pose)
 inc a
 and 15
 ld (pose),a
 call draw_pose
 jp nz,failed
 ld de,60
 call deadline
 jr idle
draw_pose:
 ld hl,0
 ld a,(pose)
 ld l,a
 ld de,0
 add hl,hl
 ld e,a
 add hl,de
 ld de,pose_table
 add hl,de
 ld hl,(hl)
 ld bc,0
 ld c,(hl)
 inc hl
 ld b,(hl)
 inc hl
 rst.lil 18h
 ; Public pixel query fences all Canvas commands, including an explicit swap.
 ld c,4
 ld a,40h
 rst.lil 08h
 ld hl,pixel_query
 ld bc,7
 rst.lil 18h
 ld de,360
 call deadline
fence_wait:
 ld ix,(sysvars)
 bit 2,(ix+4)
 jr nz,fence_ready
 call elapsed
 jr c,fence_wait
 ld a,1
 or a
 ret
fence_ready:
 xor a
 ret
success:
 ld hl,0
 jr finish
failed:
 ld hl,1
finish:
 push hl
 ld a,2
 ld (ready_marker+13),a
 ld hl,ready_marker
 ld bc,20
 rst.lil 18h
 ld hl,0
 ld c,0
 ld a,1dh
 rst.lil 08h
 pop hl
 pop iy
 pop ix
 ret
deadline:
 ld ix,(sysvars)
 ld hl,(ix+0)
 add hl,de
 ld (due),hl
 ret
elapsed:
 ld ix,(sysvars)
 ld hl,(ix+0)
 ld de,(due)
 or a
 sbc hl,de
 ret
key_callback:
 push af
 push hl
 ld hl,3
 add hl,de
 ld a,(hl)
 or a
 jr nz,key_down
 xor a
 ld (held_key),a
 jr key_return
key_down:
 ld a,(de)
 ld hl,held_key
 cp (hl)
 jr z,key_return
 ld (hl),a
 cp 27
 jr z,key_escape
 cp 32
 jr z,key_step
 cp 'p'
 jr z,key_pause
 cp 'P'
 jr nz,key_return
key_pause:
 ld a,1
 ld (pause_key),a
 jr key_return
key_step:
 ld a,1
 ld (step_key),a
 jr key_return
key_escape:
 ld a,1
 ld (escape),a
key_return:
 pop hl
 pop af
 ret
sysvars: dl 0
due: dl 0
automatic: db 1
pose: db 0
held_key: db 0
pause_key: db 0
step_key: db 0
escape: db 0
mode_query: db 23,0,134
pixel_query: db 23,0,132,0,0,0,0
include "scene.inc"
