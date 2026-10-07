; SCAN01 finite harness, adapted from render_load/benchmark-r04.asm.
; All commands pass through MOS. No mode switch, ISR, UART/GPIO bypass, or
; disk I/O in timed updates. All register-sized memory fields below are DL.
; PRT1 is single-pass /256. Its reload is write-only; ownership requires an
; unused disabled timer. Close restores control=0, not an unknowable reload.
; RAM records: 0x080000..0x095FFF (3600*24 <= 0x16000); no module RAM use.
sc_records: equ 080000h
sc_main:
    ld hl,sc_zero_begin
    ld de,sc_zero_begin+1
    ld bc,sc_zero_end-sc_zero_begin-1
    ld (hl),0
    ldir
    ld hl,sc_config_name
    ld de,sc_config
    ld bc,128
    ld a,1
    rst.lil 08h
    or a
    jp nz,sc_bad_config
    ld hl,(sc_config)
    ld de,0435353h ; SSC
    or a
    sbc hl,de
    jp nz,sc_bad_config
    ld a,(sc_config+3)
    cp sc_case
    jp nz,sc_bad_config
    ld hl,(sc_config+4)
    ld a,h
    or l
    jp z,sc_bad_config
    ld de,3601
    or a
    sbc hl,de
    jp nc,sc_bad_config
    ld hl,(sc_config+7)
    ld de,121
    or a
    sbc hl,de
    jp nc,sc_bad_config
    ld a,(sc_config+127)
    or a
    jp nz,sc_bad_config
    ; Protect retained evidence. This runs outside timing; hardware is single
    ; foreground owner. No create-new claim for directory-backed emulator SD.
    ld hl,sc_config+16
    ld c,1
    ld a,0ah
    rst.lil 08h
    or a
    jp z,sc_new_result
    ld c,a
    ld a,0bh
    rst.lil 08h
    ld hl,sc_existing
    jp sc_print_exit
sc_new_result:
    ld a,8
    rst.lil 08h
    ld (sc_sysvars),ix
    in0 a,(83h)
    and 7fh
    jp nz,sc_timer_busy
    in0 a,(92h)
    and 0ch
    jp nz,sc_timer_busy
    ld a,255
    out0 (84h),a
    out0 (85h),a
    ; Verify startup mode via ordinary VDP reply, never select it here.
    ld c,10h
    ld a,40h
    rst.lil 08h
    ld hl,sc_mode_query
    ld bc,3
    rst.lil 18h
    call sc_timer_begin
sc_mode_wait:
    ld ix,(sc_sysvars)
    bit 4,(ix+4)
    jp nz,sc_mode_ready
    call sc_timer_read
    jp nz,sc_mode_wait
    jp sc_mode_fail
sc_mode_ready:
    ld a,(ix+27h)
    cp 20
    jp nz,sc_mode_fail
    ; Calibrate against 60 raw MOS units outside workload.
    call sc_clock
    ld (sc_t0),hl
    call sc_timer_begin
sc_calibrate:
    call sc_clock
    ld de,(sc_t0)
    or a
    sbc hl,de
    ld (sc_calib_mos),hl
    ld de,60
    or a
    sbc hl,de
    jp nc,sc_calibrated
    call sc_timer_read
    jp nz,sc_calibrate
    jp sc_mode_fail
sc_calibrated:
    call sc_timer_read
    ld (sc_calib_prt),hl
    call sc_timer_stop
    call sc_prepare
    or a
    jp nz,sc_setup_fail
    call sc_timer_begin
    call sc_fence
    jp nz,sc_setup_fail
    call sc_timer_stop
    call sc_clock
    ld (sc_deadline),hl
    ld (sc_window_start),hl
    ld a,(sc_config+10)
    and 2
    ld (sc_no_timing),a
    ld hl,sc_config+4
    ld de,sc_header+35
    ld bc,7
    ldir
    ld hl,sc_identity
    ld de,sc_header+42
    ld bc,sc_identity_end-sc_identity
    ldir
    ld hl,sc_records
    ld (sc_pointer),hl
    ; r02: a fresh pacing epoch starts after warm-up on every control, not
    ; only the marked variant. This removes inherited warm-up deadline debt.
    ld hl,(sc_config+11)
    ld (sc_header+10),hl ; optional 24-bit correlation tag
    ld hl,(sc_config+7)
    ld a,h
    or l
    jp nz,sc_loop
    call sc_measure_begin
    jp nz,sc_finished
sc_loop:
    ; Warm-up uses identical work and pacing. Start measured clock afterward.
    xor a
    ld (sc_flags),a
    call sc_clock
    ld (sc_t0),hl
    call sc_timer_begin
    call sc_work
    ; MOS key-map polling is included; Escape is an abort, never a pass.
    ld a,1eh
    rst.lil 08h
    bit 0,(ix+14) ; virtual Escape=113
    jp z,sc_key_ok
    ld a,1
    ld (sc_abort),a
sc_key_ok:
    call sc_timer_read
    ld (sc_active),hl
    call sc_note_saturation
    ld a,(sc_config+10)
    bit 0,a ; whole-update fence disabled only by an identified control
    call z,sc_fence
    call sc_timer_read
    ld (sc_complete),hl
    call sc_note_saturation
    call sc_wait
    call sc_extra_flags
    call sc_timer_read
    ld (sc_total),hl
    call sc_note_saturation
    call sc_timer_stop
    call sc_clock
    ld de,(sc_t0)
    or a
    sbc hl,de
    ld (sc_delta),hl
    ; Checkpoint calculation and record copy are an explicit unmeasured tail.
    ; Window MOS elapsed includes it. No deceptive total=sum(active+wait) claim.
    call sc_checkpoint
    ld hl,(sc_update)
    ld de,(sc_config+7)
    or a
    sbc hl,de
    jp c,sc_warming
    ld de,(sc_pointer)
    ld hl,sc_row
    ld bc,24
    ldir
    ld (sc_pointer),de
    ld hl,(sc_count)
    inc hl
    ld (sc_count),hl
    ld de,(sc_config+4)
    or a
    sbc hl,de
    jp z,sc_finished
    jp sc_next
sc_warming:
    ld hl,(sc_update)
    inc hl
    ld de,(sc_config+7)
    or a
    sbc hl,de
    jp nz,sc_next
    call sc_measure_begin
    jp nz,sc_finished
sc_next:
    ld hl,(sc_update)
    inc hl
    ld (sc_update),hl
    ld a,(sc_abort)
    or a
    jp z,sc_loop
sc_finished:
    call sc_clock
    ld (sc_window_end),hl
    call sc_timer_begin
    call sc_fence
    call sc_timer_read
    ld (sc_drain),hl
    call sc_timer_stop
    ; Close after the final completion fence: P4 aggregate scope includes
    ; the tail drain, unlike the separately recorded eZ80 workload window.
    call sc_measure_end
    call sc_cleanup
    ; Save one header+RAM record stream after all drawing/timing has ended.
    ld hl,sc_config+16
    ld c,0ah ; write/create always; preflight refused any existing result
    ld a,0ah
    rst.lil 08h
    or a
    jp z,sc_save_fail
    ld (sc_handle),a
    ld c,a
    ld hl,sc_header
    ld de,128
    ld a,1bh
    rst.lil 08h
    ld hl,128
    or a
    sbc hl,de
    jp nz,sc_short_write
    ld a,(sc_handle)
    ld c,a
    ld hl,(sc_count)
    add hl,hl
    add hl,hl
    add hl,hl
    push hl
    pop de
    add hl,hl
    add hl,de ; count*24
    ld (sc_bytes),hl
    ex de,hl
    ld hl,sc_records
    ld a,1bh
    rst.lil 08h
    ld hl,(sc_bytes)
    or a
    sbc hl,de
    jp nz,sc_short_write
    ld a,(sc_handle)
    ld c,a
    ld a,0bh
    rst.lil 08h
    ld hl,sc_done_text
    jp sc_print_exit
sc_mode_fail:
    call sc_timer_stop
    ld hl,sc_mode_text
    jp sc_print_exit
sc_setup_fail:
    call sc_timer_stop
    ld hl,sc_setup_text
    jp sc_print_exit
sc_timer_busy:
    ld hl,sc_timer_text
    jp sc_print_exit
sc_bad_config:
    ld hl,sc_config_text
    jp sc_print_exit
sc_short_write:
    ld a,(sc_handle)
    ld c,a
    ld a,0bh
    rst.lil 08h
sc_save_fail:
    ld hl,sc_save_text
sc_print_exit:
    ld bc,0
    xor a
    rst.lil 18h
    ret
sc_measure_begin:
    ld a,(sc_config+10)
    bit 2,a
    jp z,sc_measure_epoch
    ; No warm-up draw may leak into the aggregate window. Both fences and
    ; carrier traffic are outside per-update PRT samples. The marker's own
    ; post-open fence is included in aggregate wall time, explicitly.
    call sc_timer_begin
    call sc_fence
    push af
    call sc_timer_stop
    pop af
    ret nz
    ld a,1
    ld (sc_window_open),a
    call sc_marker
    call sc_timer_begin
    call sc_fence
    push af
    call sc_timer_stop
    pop af
    ret nz
sc_measure_epoch:
    call sc_clock
    ld (sc_deadline),hl
    ld (sc_window_start),hl
    xor a
    ret
sc_measure_end:
    ld a,(sc_window_open)
    or a
    ret z
    xor a
    ld (sc_window_open),a
    ld a,2
    jp sc_marker
sc_marker:
    ; Official buffer-write to reserved/discarded ID65535. Never CLEAR that
    ; ID (which would clear ALL assets). BENCH-009 diagnostic images observe
    ; this existing 12-byte B009 carrier; stock VDP consumes and discards it.
    ; flags=1 enables phase counters; tag/case bind later HTTP retrieval.
    ld (sc_marker_bytes+13),a
    ld hl,(sc_config+11)
    ld (sc_marker_bytes+17),hl
    ld hl,sc_marker_bytes
    ld bc,20
    rst.lil 18h
    ret
sc_marker_bytes:
    db 23,0,160,255,255,0,12,0,"B009",1,0,sc_case,0,1,0,0,0
sc_note_saturation:
    ret nz
    ld a,(sc_flags)
    or 1
    ld (sc_flags),a
    ret
sc_fence:
    ld c,4
    ld a,40h
    rst.lil 08h
    ld hl,sc_pixel_query
    ld bc,7
    rst.lil 18h
    ld bc,0
sc_fence_wait:
    ld ix,(sc_sysvars)
    bit 2,(ix+4)
    jp nz,sc_fence_ok
    call sc_timer_read
    jp z,sc_fence_timeout
    ld a,(sc_no_timing)
    or a
    jp z,sc_fence_wait
    ; Finite poll budget for no-PRT control, never an infinite diagnostic wait.
    dec bc
    ld a,b
    or c
    jp nz,sc_fence_wait
sc_fence_timeout:
    ld a,(sc_flags)
    or 3
    ld (sc_flags),a
    ld a,1
    ld (sc_abort),a
    or a
    ret
sc_fence_ok:
    xor a
    ret
sc_clock:
    ld ix,(sc_sysvars)
    ld hl,(ix)
    ret
sc_timer_begin:
    ld a,(sc_no_timing)
    or a
    ret nz
    xor a
    out0 (83h),a
    ld a,0fh
    out0 (83h),a
    ret
sc_timer_read:
    ld a,(sc_no_timing)
    or a
    jp z,sc_timer_real
    ld hl,0
    or a ; NZ: disabled measurement is not saturation
    ret
sc_timer_real:
    ld hl,0
    in0 a,(84h)
    ld l,a
    in0 a,(85h)
    ld h,a
    ld a,h
    or l
    push af
    ld de,65535
    ex de,hl
    or a
    sbc hl,de
    pop af
    ret
sc_timer_stop:
    xor a
    out0 (83h),a
    ret
sc_pace:
    ld hl,(sc_deadline)
    inc hl
    inc hl
    ld (sc_deadline),hl
    call sc_clock
    ld de,(sc_deadline)
    or a
    sbc hl,de
    jp m,sc_pace_wait
    jp z,sc_pace_done
    ld a,(sc_flags)
    or 4
    ld (sc_flags),a
    ret
sc_pace_wait:
    call sc_timer_read
    jp z,sc_note_saturation
    call sc_clock
    ld de,(sc_deadline)
    or a
    sbc hl,de
    jp m,sc_pace_wait
sc_pace_done:
    ret
sc_load:
    ld de,050000h
    ld bc,030000h
    ld a,1
    rst.lil 08h
    ret
sc_config_name: asciz "run.cfg"
sc_mode_query: db 23,0,86h
sc_pixel_query: db 23,0,84h,0,0,0,0
sc_existing: asciz "SCAN: result exists; select a fresh run.cfg output.\r\n"
sc_done_text: asciz "SCAN: records saved; check count/flags before acceptance.\r\n"
sc_mode_text: asciz "SCAN: mode 20/VDP reply/clock required.\r\n"
sc_timer_text: asciz "SCAN: PRT1 busy or wrong clock source.\r\n"
sc_config_text: asciz "SCAN: invalid/missing run.cfg.\r\n"
sc_setup_text: asciz "SCAN: setup failed; no timing pass.\r\n"
sc_save_text: asciz "SCAN: result save failed.\r\n"
sc_config: ds 128
sc_header:
    db "SCANR01!",sc_case,24
    ds 6
sc_zero_begin:
sc_count: dl 0 ; header16
sc_window_start: dl 0
sc_window_end: dl 0
sc_calib_prt: dl 0
sc_calib_mos: dl 0
sc_drain: dl 0
sc_abort: db 0 ; header34
    ds 93
sc_sysvars: dl 0
sc_pointer: dl 0
sc_t0: dl 0
sc_deadline: dl 0
sc_no_timing: db 0
sc_window_open: db 0
sc_bytes: dl 0
sc_handle: db 0
sc_row:
sc_update: dl 0 ; offset0 absolute update including warm-up
sc_active: dl 0 ; offset3
sc_complete: dl 0 ; offset6
sc_total: dl 0 ; offset9
sc_delta: dl 0 ; offset12 raw MOS time
sc_state: dl 0 ; offset15 checkpoint hash
sc_flags: db 0 ; offset18: saturated, fence timeout, late, game fault
sc_phase: db 0 ; offset19
sc_actors: db 0 ; offset20
sc_projectiles: db 0 ; offset21
sc_maprow: db 0 ; offset22
sc_rng: db 0 ; offset23
sc_zero_end:

sc_identity:
include "identity.inc"
sc_identity_end:
