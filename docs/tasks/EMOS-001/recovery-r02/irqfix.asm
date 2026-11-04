; EMOS-001 recovery ONLY: exact r01 ROM binding generated from retained image.
; Eirene RC2 initialized RAM IRQ defaults before clearing their BSS. Restore
; only the dormant UART1 default via official mos_setintvector(14h), so normal
; EMOS keyboard admission can run. No flash, GPIO writes, routing bypass or CRC.
; Removal: remove the temporary boot shim after input works, flash corrected
; r02 through the ordinary updater, then remove this disposable utility.
; Recovery r02 also restarts the failed EMOS startup handshake via its own
; exact-ROM fence/connect entry points. They retain ownership/admission checks.
; This controlled boot-recovery call is an exception to those private hooks'
; application-use prohibition: it is NOT an application API, exported service,
; consumer example or general UART override. Remove with this temporary shim.
; No application, callback or normal product utility may reuse this binary.
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
    ; Refuse an active owner; startup recovery is allowed only while dormant.
    ld a,(UART1_OWNED)
    or a
    jp nz,refuse
    ld a,(KEY_SOURCE)
    or a
    jp nz,refuse
    ld a,(CONSOLE_OWNED)
    or a
    jp nz,refuse
    ld hl,BOOT_START_ADDRESS
    ld de,expected_boot_start
    ld b,BOOT_START_LENGTH
    call compare
    jp nz,refuse
    ld hl,BOOT_CONNECT_ADDRESS
    ld de,expected_boot_connect
    ld b,BOOT_CONNECT_LENGTH
    call compare
    jp nz,refuse
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
    ; The earlier firmware boot failed its connection before OBEY ran. Merely
    ; repairing the vector cannot reopen its deliberate grant0 fence. Ask the
    ; resident EMOS startup owner to execute its normal physical handshake.
    ; No direct grant writes or transport access is added here.
    call BOOT_START_ADDRESS
    call BOOT_CONNECT_ADDRESS
    call BOOT_ALLOWED_ADDRESS
    cp 2
    jr nz,refuse
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
    .asciz "UART1 default and EMOS startup connection restored; no flash written.\r\n"
refuse_message:
    .asciz "UART1 repair refused: ROM, owner or UART state mismatch.\r\n"
.include "expected.inc"
