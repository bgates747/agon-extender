; C binding to the existing EMOS gateway. No UART, GPIO or route access.
; AgonDev stack argument -> documented API 0x51 HL pointer, A status -> HL.
        .assume adl=1
        .section .text
        .global _emos_gateway_call
_emos_gateway_call:
        push ix
        ld ix,0
        add ix,sp
        ld hl,(ix+6)
        ld a,051h
        rst.lil 08h
        ld hl,0
        ld l,a
        pop ix
        ret
