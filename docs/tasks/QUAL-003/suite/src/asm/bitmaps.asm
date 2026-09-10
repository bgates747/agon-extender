; BSP-01..32: staged MOS/EMOS bitmap and sprite library demonstrations.
    assume adl=1
    org 0x040000
    jp start
    align 64
    db "MOS",0,1

origin_left: equ 0
origin_top: equ 0
page_count: equ 32
    include "../src/asm/api.inc"
    include "../src/asm/bitmap_adapters.inc"

start:
    push af
    push bc
    push de
    push ix
    push iy
    call bitmaps_main
bitmaps_review_done:
    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ret

bitmaps_main:
    call paired_init
    xor a
    ld (selected_page),a
    ld (query_disabled),a
    ld (load_error),a
@spaces:
    ld a,(hl)
    cp ' '
    jr nz,@arg
    inc hl
    jr @spaces
@arg:
    or a
    jr z,@mode
    ld c,0
@digit:
    ld a,(hl)
    cp '0'
    jr c,@number_done
    cp '9'+1
    jr nc,@number_done
    sub '0'
    ld e,a
    ld a,c
    cp 4
    jr nc,@usage
    add a,a
    ld d,a
    add a,a
    add a,a
    add a,d
    add a,e
    cp page_count+1
    jr nc,@usage
    ld c,a
    inc hl
    jr @digit
@number_done:
    ld a,c
    or a
    jr z,@usage
    ld (selected_page),a
@trailing:
    ld a,(hl)
    inc hl
    cp ' '
    jr z,@trailing
    or a
    jr nz,@usage
@mode:
    MOSCALL mos_sysvars
    ld a,(ix+sysvar_scrMode)
    cp 20
    jr z,@run
    call printInline
    asciz "Bitmaps requires VDU 22 20 before launch.\r\n"
    ld hl,1
    ret
@usage:
    call printInline
    asciz "Usage: bitmaps [1..32]  (no argument: full tour)\r\n"
    ld hl,1
    ret
@run:
    ld a,(selected_page)
    or a
    jr nz,set_page
    inc a
set_page:
    ld (current_page),a
    call paired_mainboard
    jp nz,paired_failure
    call clean_resources
    ld a,12
    rst.lil 0x10
    call paired_edp
    jp nz,paired_failure
    call clean_resources
    ld a,12
    rst.lil 0x10
    ld hl,page_table
    ld de,4
    ld a,(current_page)
    dec a
    jr z,@descriptor
    ld b,a
@find:
    add hl,de
    djnz @find
@descriptor:
    push hl
    pop iy
    ld hl,(iy+0) ; ADL24 OK: page descriptor dl stage-table pointer.
    ld (stage_cursor),hl ; ADL24 OK: dl pointer.
    ld a,(iy+3)
    ld (stage_total),a
    ld a,1
    ld (current_stage),a
stage_loop:
    call paired_mainboard
    jp nz,paired_failure
    call render_stage
    jp nz,asset_error
    call record_pair_results
    call paired_edp
    jp nz,paired_failure
    call render_stage
    jp nz,asset_error
    call record_pair_results
stage_ready:
    ; No drawing here: the deferred-update stages must remain untouched.
    call waitKeypress
    cp 27
    jp z,escape_exit
    ld a,(paired_stage_index)
    inc a
    ld (paired_stage_index),a
    ld a,(current_stage)
    ld b,a
    ld a,(stage_total)
    cp b
    jr z,@page_finished
    ld a,b
    inc a
    ld (current_stage),a
    ld hl,(stage_cursor) ; ADL24 OK: dl descriptor pointer.
    ld de,7
    add hl,de
    ld (stage_cursor),hl ; ADL24 OK: dl pointer.
    jp stage_loop
@page_finished:
    ld a,(selected_page)
    or a
    jp nz,normal_finish
    ld a,(current_page)
    inc a
    cp page_count+1
    jp nz,set_page
normal_finish:
    call finish
    jp nz,paired_failure
    call printInline
    asciz "Bitmaps complete. See recorded rendering observations.\r\n"
    ld hl,0
    ret
escape_exit:
    call finish
    jp nz,paired_failure
    ld hl,clear_commands
    ld bc,clear_commands_end-clear_commands
    rst.lil 0x18
    ld hl,0
    ret

render_stage:
    ld iy,(stage_cursor) ; ADL24 OK: dl stage descriptor pointer.
    ld hl,(iy+3) ; ADL24 OK: dl probe-table pointer.
    ld (stage_probes),hl ; ADL24 OK: dl pointer.
    ld a,(iy+6)
    ld (probe_total),a
    ld iy,(iy+0) ; ADL24 OK: dl stage-program pointer.
    call execute_program
    ld a,(load_error)
    or a
    ret nz
    call settle_transport
    call check_pixels
    xor a
    ret

record_pair_results:
    ld hl,0
    ld a,(paired_stage_index)
    ld l,a
    add hl,hl
    add hl,hl
    ld de,results
    ld a,(paired_target)
    or a
    jr z,@bank
    ld de,results_edp
@bank:
    add hl,de
    ld a,(probe_total)
    ld (hl),a
    inc hl
    ld a,(probe_passed)
    ld (hl),a
    inc hl
    ld a,(probe_failed)
    ld (hl),a
    inc hl
    ld a,(probe_timeouts)
    ld (hl),a
    ret

; VM records: 0 end; 1 word length + raw bytes;
; 2 byte call-ID/A + three dl BC/DE/HL; 3 byte asset-ID + word buffer + mode.
execute_program:
@next:
    ld a,(iy+0)
    inc iy
    or a
    ret z
    cp 1
    jr z,@raw
    cp 2
    jr z,@call
    cp 3
    jr z,@load
    ld a,3
    ld (load_error),a
    ret
@raw:
    ld bc,0
    ld c,(iy+0)
    ld b,(iy+1)
    lea iy,iy+2
    push iy
    pop hl
    add iy,bc
    push iy
    rst.lil 0x18
    pop iy
    jr @next
@call:
    ld hl,bitmap_calls
    ld de,3
    ld a,(iy+0)
    or a
    jr z,@target
    ld b,a
@call_find:
    add hl,de
    djnz @call_find
@target:
    ld ix,(hl) ; ADL24 OK: dl function-pointer table entry.
    ld a,(iy+1)
    ld bc,(iy+2) ; ADL24 OK: VM dl BC argument.
    ld de,(iy+5) ; ADL24 OK: VM dl DE argument.
    ld hl,(iy+8) ; ADL24 OK: VM dl HL argument.
    lea iy,iy+11
    push iy
    call call_ix
    pop iy
    jr @next
@load:
    ld a,(iy+0)
    ld hl,0
    ld l,(iy+1)
    ld h,(iy+2)
    ld (load_buffer),hl ; ADL24 OK: zero-extended ID in dl storage.
    push af
    ld a,(iy+3)
    ld (load_mode),a
    pop af
    lea iy,iy+4
    push iy
    call load_asset
    pop iy
    ld a,(load_error)
    or a
    ret nz
    jp @next
call_ix:
    jp (ix)

; Let MOS interrupts drain the final UART bytes before a review breakpoint.
; No VDU/drawing is emitted: preserves the deferred software-update fixture.
; Three MOS clock changes are only a transport settle, never stage progression.
settle_transport:
    MOSCALL mos_sysvars
    ld a,(ix+sysvar_time)
    ld b,a
    ld c,3
    ld de,0x200000
@wait:
    ld a,(ix+sysvar_time)
    cp b
    jr z,@backstop
    ld b,a
    dec c
    ret z
@backstop:
    dec de
    ld hl,0
    or a
    sbc hl,de
    jr nz,@wait
    ret

; File descriptor: dl path,length; dw width,height; db format (11 bytes).
; Read expected length+1 before sending anything; exact size includes EOF check.
; Maximum generated asset is <32768 bytes; staging is owned by this executable.
load_asset:
    ld hl,asset_table
    ld de,11
    or a
    jr z,@descriptor
    ld b,a
@find:
    add hl,de
    djnz @find
@descriptor:
    push hl
    pop iy
    ld (asset_cursor),iy ; ADL24 OK: dl descriptor pointer, survives MOS fread.
    ld hl,(iy+0) ; ADL24 OK: dl filename pointer.
    ld (error_path),hl ; ADL24 OK: dl filename pointer.
    ld de,(iy+3) ; ADL24 OK: dl expected byte count.
    ld (asset_length),de ; ADL24 OK: dl byte count.
    ld c,fa_read
    MOSCALL mos_fopen
    or a
    jp z,@open_failed
    ld c,a
    ld (asset_handle),a
    ld hl,asset_staging
    ld de,(asset_length) ; ADL24 OK: dl byte count.
    inc de
    MOSCALL mos_fread
    ld hl,(asset_length) ; ADL24 OK: dl expected byte count.
    or a
    sbc hl,de
    push af
    ld a,(asset_handle)
    ld c,a
    MOSCALL mos_fclose
    pop af
    jp nz,@size_failed
    ld hl,(load_buffer) ; ADL24 OK: dl zero-extended ID.
    call vdu_clear_buffer
    ld a,(load_mode)
    cp 2
    jp z,@legacy
    ld de,asset_staging
    ld (upload_cursor),de ; ADL24 OK: dl data pointer.
    ld hl,(asset_length) ; ADL24 OK: dl remaining bytes.
    ld (upload_remaining),hl ; ADL24 OK: dl count.
@upload:
    ld bc,(upload_remaining) ; ADL24 OK: dl count, upper byte zero.
    ld a,(load_mode)
    cp 1
    jr nz,@send
    ld hl,1024
    or a
    sbc hl,bc
    jr nc,@send
    ld bc,1024
@send:
    push bc
    ld hl,(load_buffer) ; ADL24 OK: dl zero-extended ID.
    ld de,(upload_cursor) ; ADL24 OK: dl staging pointer.
    call vdu_load_buffer
    pop de
    ld hl,(upload_cursor) ; ADL24 OK: dl pointer.
    add hl,de
    ld (upload_cursor),hl ; ADL24 OK: dl pointer.
    ld hl,(upload_remaining) ; ADL24 OK: dl count.
    or a
    sbc hl,de
    ld (upload_remaining),hl ; ADL24 OK: dl count.
    jr nz,@upload
    ld hl,(load_buffer) ; ADL24 OK: dl ID.
    call vdu_consolidate_buffer
    ld a,(load_mode)
    cp 3
    ret z
    ld hl,(load_buffer) ; ADL24 OK: dl ID.
    call vdu_buff_select
    ld iy,(asset_cursor) ; ADL24 OK: dl descriptor pointer.
    ld bc,0
    ld c,(iy+6)
    ld b,(iy+7)
    ld de,0
    ld e,(iy+8)
    ld d,(iy+9)
    ld a,(iy+10)
    jp vdu_bmp_create
@legacy:
    ld hl,(load_buffer) ; ADL24 OK: dl ID.
    call vdu_buff_select
    ld iy,(asset_cursor) ; ADL24 OK: dl descriptor pointer.
    ld a,(iy+6)
    ld (legacy_dimensions),a
    ld a,(iy+7)
    ld (legacy_dimensions+1),a
    ld a,(iy+8)
    ld (legacy_dimensions+2),a
    ld a,(iy+9)
    ld (legacy_dimensions+3),a
    ld hl,legacy_command
    ld bc,7
    rst.lil 0x18
    ld hl,asset_staging
    ld bc,(asset_length) ; ADL24 OK: dl exact raw RGBA8888 byte count.
    rst.lil 0x18
    ret
@open_failed:
    ld a,1
    ld (load_error),a
    ret
@size_failed:
    ld a,2
    ld (load_error),a
    ret

asset_error:
    call clean_resources
    call printInline
    db 12,17,15,31,2,2
    asciz "BITMAP ASSET ERROR - no incomplete payload was sent."
    call printInline
    db 31,2,5
    asciz "Missing/unreadable file or unexpected byte count:"
    call printInline
    db 31,2,7,0
    ld hl,(error_path) ; ADL24 OK: dl filename pointer.
    ld bc,0
    xor a
    rst.lil 0x18
    call printInline
    db 31,2,11
    asciz "Restore assets and retry. Any key exits; ESC clears."
asset_error_ready:
    call waitKeypress
    push af
    call finish
    jr z,@cleaned
    pop af
    jp paired_failure
@cleaned:
    pop af
    cp 27
    jr nz,@return
    ld hl,clear_commands
    ld bc,clear_commands_end-clear_commands
    rst.lil 0x18
@return:
    ld hl,1
    ret

check_pixels:
    xor a
    ld (probe_passed),a
    ld (probe_failed),a
    ld (probe_timeouts),a
    ld a,(probe_total)
    or a
    ret z ; no flush or text output for quiet deferred-update observations
    ld hl,flush_commands
    ld bc,3
    rst.lil 0x18
    ld a,(query_disabled)
    or a
    ret nz
    ld hl,observed_pixels
    ld a,(paired_target)
    or a
    jr z,@pixel_bank
    ld hl,observed_pixels_edp
@pixel_bank:
    ld (observed_cursor),hl ; ADL24 OK: dl observation pointer.
    ld iy,(stage_probes) ; ADL24 OK: dl probe pointer.
    ld a,(probe_total)
    ld b,a
    MOSCALL mos_sysvars
@next:
    push bc
    res 2,(ix+sysvar_vpd_pflags)
    push iy
    pop hl
    ld bc,7
    rst.lil 0x18
    ld de,0x200000
@wait:
    bit 2,(ix+sysvar_vpd_pflags)
    jr nz,@reply
    dec de
    ld hl,0
    or a
    sbc hl,de
    jr nz,@wait
    ld a,1
    ld (query_disabled),a
    ld (probe_timeouts),a
    pop bc
    ret
@reply:
    ld hl,(observed_cursor) ; ADL24 OK: dl observation pointer.
    ld a,(ix+sysvar_scrpixel)
    ld (hl),a
    inc hl
    ld a,(ix+sysvar_scrpixel+1)
    ld (hl),a
    inc hl
    ld a,(ix+sysvar_scrpixel+2)
    ld (hl),a
    inc hl
    ld (observed_cursor),hl ; ADL24 OK: dl observation pointer.
    ld a,(ix+sysvar_scrpixel)
    cp (iy+7)
    jr nz,@fail
    ld a,(ix+sysvar_scrpixel+1)
    cp (iy+8)
    jr nz,@fail
    ld a,(ix+sysvar_scrpixel+2)
    cp (iy+9)
    jr nz,@fail
    ld a,(probe_passed)
    inc a
    ld (probe_passed),a
    jr @advance
@fail:
    ld a,(probe_failed)
    inc a
    ld (probe_failed),a
@advance:
    lea iy,iy+10
    pop bc
    djnz @next
    ret

clean_resources:
    ld hl,cleanup_commands
    ld bc,cleanup_commands_end-cleanup_commands
    rst.lil 0x18
    ret
finish:
    call paired_mainboard
    ret nz
    call finish_one
    call paired_edp
    ret nz
    call finish_one
    xor a
    ret
finish_one:
    call clean_resources
    ld hl,finish_commands
    ld bc,finish_commands_end-finish_commands
    rst.lil 0x18
    ret

selected_page: db 0
current_page: db 0
current_stage: db 0
stage_total: db 0
stage_cursor: dl 0
stage_probes: dl 0
query_disabled: db 0
probe_total: db 0
probe_passed: db 0
probe_failed: db 0
probe_timeouts: db 0
observed_cursor: dl 0
observed_pixels: blkb 300,0
observed_pixels_edp: blkb 300,0
results: blkb 123*4,0
results_edp: blkb 123*4,0
load_error: db 0
load_mode: db 0
asset_handle: db 0
load_buffer: dl 0
asset_cursor: dl 0
asset_length: dl 0
error_path: dl 0
upload_cursor: dl 0
upload_remaining: dl 0
legacy_command: db 23,27,1
legacy_dimensions: blkb 4,0
flush_commands: db 23,0,0xca
finish_commands: db 4,20,26,23,0,0xc0,1,23,1,1,31,0,46
finish_commands_end:
clear_commands: db 12,23,0,0xca
clear_commands_end:

    include "../src/asm/paired.inc"
    include "bitmaps-data.inc"
; Deliberately part of the executable memory extent: no inherited fixed address.
asset_staging: blkb 32768,0
app_end:
