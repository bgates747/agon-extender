; SHP-01..24: MOS/EMOS VDU application. Mode 20 is selected by autoexec.
; Optional command-line argument 1..24 displays just that page.
    assume adl=1
    org 0x040000
    jp start
    align 64
    db "MOS",0,1

origin_left: equ 0
origin_top: equ 0
page_count: equ 24

    include "../src/asm/api.inc"

start:
    push af
    push bc
    push de
    push ix
    push iy
    call shapes_main
shapes_review_done:
    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ret

shapes_main:
    call paired_init
    xor a
    ld (selected_page),a
    ld (query_disabled),a
    ld de,results
    ld b,page_count*8
@clear_results:
    ld (de),a
    inc de
    djnz @clear_results
@skip_space:
    ld a,(hl)
    cp ' '
    jr nz,@argument
    inc hl
    jr @skip_space
@argument:
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
    cp 3
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
    asciz "Shapes requires VDU 22 20 before launch.\r\n"
    ld hl,1
    ret
@usage:
    call printInline
    asciz "Usage: shapes [1..24]  (no argument: full tour)\r\n"
    ld hl,1
    ret
@run:
    ld a,(selected_page)
    or a
    jr nz,set_page
    inc a
set_page:
    ld (current_page),a
@page_loop:
    call paired_mainboard
    jp nz,paired_failure
    call render_page
    call paired_edp
    jp nz,paired_failure
    call render_page
page_ready:
    call wait_page
    jp z,escape_exit
    ld a,(selected_page)
    or a
    jr nz,normal_finish
    ld a,(current_page)
    inc a
    cp page_count+1
    jr z,normal_finish
    jp set_page
normal_finish:
    ld hl,finish_commands
    ld bc,finish_commands_end-finish_commands
    rst.lil 0x18
    call printInline
    asciz "Shapes complete. Pixel samples are not a full visual pass.\r\n"
    ld hl,0
    ret
escape_exit:
    ld hl,finish_commands
    ld bc,finish_commands_end-finish_commands
    rst.lil 0x18
    ld hl,clear_commands
    ld bc,clear_commands_end-clear_commands
    rst.lil 0x18
    ld hl,0
    ret

render_page:
    ; Each descriptor has three dl fields and a one-byte probe count.
    ld hl,page_table
    ld de,10
    ld a,(current_page)
    dec a
    jr z,@descriptor
    ld b,a
@find_page:
    add hl,de
    djnz @find_page
@descriptor:
    push hl
    pop iy
    ld hl,(iy+0)       ; ADL24 OK: dl command-stream pointer.
    ld bc,(iy+3)       ; ADL24 OK: dl command-stream length.
    rst.lil 0x18
    ld hl,(iy+6)       ; ADL24 OK: dl probe-stream pointer.
    ld b,(iy+9)
    push hl
    pop iy
    call check_pixels
    ld hl,results
    ld a,(paired_target)
    or a
    jr z,@result_bank
    ld hl,results_edp
@result_bank:
    ld de,4
    ld a,(current_page)
    dec a
    jr z,@record
    ld b,a
@find_result:
    add hl,de
    djnz @find_result
@record:
    call record_results
    ret

; Query records are exactly 10 bytes: VDU header (3), x/y words (4), RGB (3).
; Once a reply times out, stop issuing queries to avoid stale-reply attribution.
check_pixels:
    ld a,b
    ld (probe_total),a
    ld hl,observed_pixels
    ld a,(paired_target)
    or a
    jr z,@pixel_bank
    ld hl,observed_pixels_edp
@pixel_bank:
    ld (observed_cursor),hl ; ADL24 OK: dl pointer into observed_pixels.
    xor a
    ld (probe_passed),a
    ld (probe_failed),a
    ld (probe_timeouts),a
    ld a,(probe_total)
    or a
    jp z,show_results
    ld a,(query_disabled)
    or a
    jp nz,show_results
    MOSCALL mos_sysvars
@next:
    push bc
    res 2,(ix+sysvar_vpd_pflags)
    push iy
    pop hl
    ld bc,7
    rst.lil 0x18
    ; CPU backstop is deliberately bounded even if MOS VBlank time stalls.
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
    jp show_results
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

show_results:
    ld hl,results_caption
    ld bc,results_caption_end-results_caption
    rst.lil 0x18
    ld a,(probe_passed)
    call print_two_digits
    call printInline
    asciz "/"
    ld a,(probe_total)
    call print_two_digits
    call printInline
    asciz " correct, "
    ld a,(probe_failed)
    call print_two_digits
    call printInline
    asciz " wrong"
    ld a,(query_disabled)
    or a
    ret z
    call printInline
    asciz " / timeout; rest skipped"
    ret

record_results:
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

print_two_digits:
    ld b,'0'
@tens:
    cp 10
    jr c,@ones
    sub 10
    inc b
    jr @tens
@ones:
    add a,'0'
    push af
    ld a,b
    rst.lil 0x10
    pop af
    rst.lil 0x10
    ret

; Wait on every page, including isolated-page runs and the final test.
; Return Z for Escape; any other key lets the caller advance or finish.
wait_page:
    ld hl,key_prompt
    ld bc,key_prompt_end-key_prompt
    rst.lil 0x18
    call waitKeypress
    cp 27
    ret

selected_page: db 0
current_page: db 0
query_disabled: db 0
probe_total: db 0
probe_passed: db 0
probe_failed: db 0
probe_timeouts: db 0
observed_cursor: dl 0
; Actual RGB replies for the current page, retained for debugger review.
observed_pixels: blkb 300,0
observed_pixels_edp: blkb 300,0
; Per-page records: total, correct, wrong, timeout. Also readable in debugger.
results: blkb page_count*4,0
results_edp: blkb page_count*4,0

results_caption:
    db 4,17,15,31,2,45
    db "Pixel samples: "
results_caption_end:

key_prompt:
    db 4,17,15,31,2,46
    db "Press a key to continue; ESC clears and exits."
key_prompt_end:

finish_commands:
    db 4,20,26,23,0,0xC0,1,23,23,1,23,1,1
    db 23,0,0xF2,0
    db 31,0,46
finish_commands_end:

clear_commands:
    db 12,23,0,0xCA
clear_commands_end:

    include "../src/asm/paired.inc"
    include "shapes-data.inc"

app_end:
