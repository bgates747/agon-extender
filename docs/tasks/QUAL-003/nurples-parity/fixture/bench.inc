; nurples-parity-probe-r01. Fixture-only hooks, never normal gameplay.
bench_active: db 0
bench_sp: dl 0
bench_time: dl 0
bench_count: dl 0
bench_failed: db 0
bench_fenced: db 1
bench_hw: db 0
bench_hwflag: db 23,0,248,2,0,1,0
bench_hwcmd: db 23,27,4
bench_hwid: db 0
    db 23,27,19
bench_pointer: dl bench_records
bench_keys: ds 16
bench_query: db 23,0,132,0,0,0,0
bench_name: asciz "/NPRES.BIN"
bench_progress_name: asciz "/NPPROG.BIN"
bench_progress:
    db "NP01"
    dl 0
bench_progress_end:

bench_start:
    ld (bench_sp),sp
    call telemetry_init
    call runtime_process_init
    ld a,20
    ld (original_screen_mode),a
    call game_init
    ld a,(game_exit_requested)
    or a
    jp nz,bench_finish
    ld a,(bench_hw)
    or a
    call nz,bench_hardware
    ld a,1
    ld (bench_active),a
    ld a,4
    ld (bench_keys+12),a ; held fire; no steering/joystick
    ld hl,0
    ld (bench_time),hl
    ld (timestamp_now),hl
    ld (timestamp_old),hl
    ld a,$50
    ld (r_seed),a
    ld hl,bench_progress_name
    ld de,bench_progress
    ld bc,bench_progress_end-bench_progress
    MOSCALL mos_save
    jp main_loop

bench_boundary:
    push af
    push bc
    push de
    push hl
    push ix
    push iy
    ld a,(bench_active)
    or a
    jp z,bench_return
    ld a,(bench_fenced)
    or a
    jr z,bench_record
    call bench_fence
bench_record:
    MOSCALL mos_sysvars
    ld hl,(ix+sysvar_time)
    ld ix,(bench_pointer)
    ld (ix+0),hl
    ld a,(r_seed)
    ld (ix+3),a
    ld a,(player_shields)
    ld (ix+4),a
    ld hl,(player_state)
    ld (ix+5),hl
    ld hl,(game_state)
    ld (ix+8),hl
    ld de,11
    add ix,de
    ld (bench_pointer),ix
    ld hl,(bench_count)
    inc hl
    ld (bench_count),hl
    ld bc,600
    or a
    sbc hl,bc
    jp z,bench_finish
    ld hl,(bench_time)
    inc hl
    inc hl
    ld (bench_time),hl
bench_return:
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret

bench_hardware:
    ld hl,bench_hwflag
    ld bc,7
    rst.lil $18
    ld b,0
@loop:
    push bc
    ld hl,bench_hwcmd
    ld bc,7
    rst.lil $18
    ld hl,bench_hwid
    inc (hl)
    pop bc
    djnz @loop
    ret

bench_fence:
    ld c,4
    MOSCALL $40
    ld hl,bench_query
    ld bc,7
    rst.lil $18
    ld c,4
    MOSCALL $41
    or a
    ret z
    ld (bench_failed),a
    jp bench_finish

bench_finish:
    ld sp,(bench_sp)
    xor a
    ld (bench_active),a
    ; Final fence also drains unfenced control before its result is saved.
    ld c,4
    MOSCALL $40
    ld hl,bench_query
    ld bc,7
    rst.lil $18
    ld c,4
    MOSCALL $41
    ld hl,(bench_count)
    ld (bench_header_count),hl
    ld a,(bench_failed)
    ld (bench_header_failed),a
    ld hl,bench_name
    ld de,bench_header
    ld bc,bench_records_end-bench_header
    MOSCALL mos_save
    ld hl,(bench_count)
    ld (bench_progress+4),hl
    ld hl,bench_progress_name
    ld de,bench_progress
    ld bc,bench_progress_end-bench_progress
    MOSCALL mos_save
    call printInline
    asciz "\r\nNurples benchmark ended; results saved.\r\n"
    ret

bench_header:
    db "NP01"
bench_header_count: dl 0
bench_header_failed: db 0
bench_records: ds 600*11
bench_records_end:
