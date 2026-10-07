assume adl=1
org 040000h
jp start
align 64
db "MOS",0,1
include "case.inc"
start:
    push ix
    push iy
    call sc_main
    pop iy
    pop ix
    ld hl,0
    ret
sc_prepare:
    ld hl,setup_name
    call sc_load
    ret nz
    ld hl,050000h
    ; Stock MOS RST18 tests BC's low word. Split the >64KiB asset stream;
    ; BCU does not make one counted transmission longer than 65,535 bytes.
    ld bc,60000
    rst.lil 18h
    ld hl,050000h+60000
    ld bc,setup_size-60000
    rst.lil 18h
    ld hl,frames_name
    call sc_load
    ret
sc_work:
    ld a,(sc_update)
    ld hl,frame_table
    ld de,0
    ld e,a
    add hl,de
    add hl,de
    add hl,de
    ld hl,(hl)
    ; ADL24 OK: frame prefix is an actual 24-bit byte count.
    ld bc,(hl)
    inc hl
    inc hl
    inc hl
    ld a,b
    or c
    ret z
    rst.lil 18h
    ret
sc_wait:
    jp sc_pace
sc_checkpoint:
    ld hl,(sc_update)
    ld (sc_state),hl ; stream is frozen; absolute update identifies scene
    ret
sc_extra_flags:
    ret
sc_cleanup:
    ld hl,cleanup
    ld bc,cleanup_end-cleanup
    rst.lil 18h
    ret
setup_name: asciz "setup.bin"
frames_name: asciz "frames.bin"
cleanup: db 23,27,7,0,23,27,17,26,4,17,63,17,128,23,1,1
cleanup_end:
include "runner.inc"
include "frames.inc"
