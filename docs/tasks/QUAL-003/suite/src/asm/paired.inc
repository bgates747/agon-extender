; QUAL-003: applications request EMOS routing through public mos_oscli only.
; The command parser can mutate its buffer: copy a fresh command every time.
; Caller-owned VDU packets must be complete before changing their destination.
; Autoexec, never this fixture, selects video mode 20 on both displays.
paired_init:
    push hl
    ld hl,paired_identity
    ld bc,paired_identity_end-paired_identity
    rst.lil 0x18
    xor a
    ld (paired_disabled),a
    ld (paired_disabled+1),a
    ld (paired_stage_index),a
    inc a
    ld (paired_target),a       ; startup is explicitly ExCom
    pop hl
    ret

paired_mainboard:
    ld hl,paired_legacy_command
    ld bc,paired_legacy_end-paired_legacy_command
    xor a
    jr paired_switch
paired_edp:
    ld hl,paired_excom_command
    ld bc,paired_excom_end-paired_excom_command
    ld a,1
paired_switch:
    ld (paired_requested),a
    push bc
    push de
    push ix
    push iy
    push hl
    ld hl,paired_disabled
    ld de,0
    ld a,(paired_target)
    ld e,a
    add hl,de
    ld a,(query_disabled)
    ld (hl),a
    pop hl
    ld de,paired_command_buffer
    ldir
    ld hl,paired_command_buffer
    MOSCALL mos_oscli
    or a
    jr nz,paired_switch_done
    ld a,(paired_requested)
    ld (paired_target),a
    ld hl,paired_disabled
    ld de,0
    ld e,a
    add hl,de
    ld a,(hl)
    ld (query_disabled),a
    ; Mainboard mode notification is asynchronous. Ask the selected authority
    ; and wait before using dimensions/font metrics or executing the next page.
    MOSCALL mos_sysvars
    res 4,(ix+sysvar_vpd_pflags)
    ld hl,paired_mode_query
    ld bc,3
    rst.lil 0x18
    ld de,0x200000
paired_mode_wait:
    bit 4,(ix+sysvar_vpd_pflags)
    jr nz,paired_mode_reply
    dec de
    ld hl,0
    or a
    sbc hl,de
    jr nz,paired_mode_wait
    ld a,1
    jr paired_switch_done
paired_mode_reply:
    ld a,(ix+sysvar_scrMode)
    cp 20
    ld a,0
    jr z,paired_switch_done
    inc a
paired_switch_done:
    ld (paired_status),a
    pop iy
    pop ix
    pop de
    pop bc
    or a
    ret

paired_failure:
    ld hl,paired_error_setup
    ld bc,paired_error_setup_end-paired_error_setup
    rst.lil 0x18
    call printInline
    asciz "Comparison stopped: EMOS route or mode-info failure.\r\n"
    ld hl,1
    ret

paired_legacy_command: asciz "emos legacy --keep-display"
paired_legacy_end:
paired_excom_command: asciz "emos excom --keep-display"
paired_excom_end:
paired_mode_query: db 23,0,0x86
paired_error_setup: db 4,26,17,15,13,10
paired_error_setup_end:
paired_command_buffer: blkb 32,0
paired_target: db 1
paired_requested: db 0
paired_disabled: db 0,0
paired_status: db 0
paired_stage_index: db 0

    include "paired-identity.inc"
