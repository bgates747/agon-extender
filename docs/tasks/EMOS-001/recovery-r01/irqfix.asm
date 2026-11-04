; EMOS-001 recovery ONLY: exact r01 ROM binding generated from retained image.
; Eirene RC2 initialized RAM IRQ defaults before clearing their BSS. Restore
; only the dormant UART1 default via official mos_setintvector(14h), so normal
; EMOS keyboard admission can run. No flash, GPIO writes, routing bypass or CRC.
; Removal: remove the temporary boot shim after input works, flash corrected
; r02 through the ordinary updater, then remove this disposable utility.
; This is NOT a general-purpose vector-owner override or production utility.
.assume adl=1
.include "binding.inc"
.text
.global entry
entry:
    jp start
    .org 0x40
    .ascii "MOS"
    .byte 0,1
start:
    push ix
    push iy
    ld hl, ROM_ID_ADDRESS
    ld de, expected_identity
    ld b, IDENTITY_LENGTH
    call compare
    jp nz, refuse
    ld hl, ROM_START_ADDRESS
    ld de, expected_start
    ld b, START_LENGTH
    call compare
    jp nz, refuse
    ld hl, DEFAULT_HANDLER
    ld de, expected_handler
    ld b, HANDLER_LENGTH
    call compare
    jp nz, refuse
    ; A live UART1 or unknown vector owner must never be overwritten.
    in0 a,(0xd3)
    and 0x80
    jp nz, refuse
    in0 a,(0xd1)
    or a
    jp nz, refuse
    ld hl, UART1_SLOT
    ld de, expected_vector
    ld b, 4
    call compare
    jr z, success
    ld hl, UART1_SLOT
    ld b, 4
zero_loop:
    ld a,(hl)
    or a
    jp nz, refuse
    inc hl
    djnz zero_loop
    ld e,0x1a
    ld hl,DEFAULT_HANDLER
    ld a,0x14
    rst.lil 0x08
    ld hl,UART1_SLOT
    ld de,expected_vector
    ld b,4
    call compare
    jr nz,refuse
success:
    ld hl,success_message
    call print
    ld hl,0
    jr done
refuse:
    ld hl,refuse_message
    call print
    ld hl,19
 done:
    pop iy
    pop ix
    ret
; Bytewise comparison, B in1..255, returns Z iff equal. No integrity protocol.
compare:
    ld a,(de)
    cp (hl)
    ret nz
    inc hl
    inc de
    djnz compare
    ret
print:
    ld bc,0
    xor a
    rst.lil 0x18
    ret
success_message:
    .asciz "UART1 default restored in RAM; no flash written.\r\n"
refuse_message:
    .asciz "UART1 repair refused: ROM, owner or UART state mismatch.\r\n"
.include "expected.inc"
