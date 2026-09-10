; Minimal noninteractive MOS/EMOS program, loaded at the normal user address.
; Video-mode selection belongs to /autoexec.txt before this program runs.
    assume adl=1
    org 0x040000

    jp start
    align 64
    db "MOS"
    db 0                       ; header version
    db 1                       ; ADL executable

; Caller-supplied pixel offsets used by Nurples' fixed-point sprite helpers.
origin_left: equ 0
origin_top: equ 0

start:
    push af
    push bc
    push de
    push ix
    push iy

    call main

    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0                    ; successful return to MOS
    ret

main:
    ld a,4                     ; VDU 4: output at the text cursor
    rst.lil 0x10
    call printInline
    asciz "Hello World!\r\n"
    ret

; Link the entire reusable API set to verify its dependency closure.
    include "../src/asm/api.inc"

app_end:
