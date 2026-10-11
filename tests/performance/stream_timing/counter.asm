; Raw resident timestamp -> elapsed PRT ticks, zero-extended before subtraction.
; Application RAM read only; EMOS owns the timestamp and transport operations.
        .assume adl=1
        .include "binding.inc"
        .section .text
        .global _st_wire_read
        .global _st_flush
; ZDS resident C returns its byte status in A and may clobber IY. AgonDev
; expects HL and preserved IX/IY. Keep this ABI bridge in the MOSlet, not ROM.
_st_flush:
        push ix
        push iy
        ld hl,0
        push hl                 ; count = 0
        push hl                 ; pointer = NULL
        call ST_FLUSH
        pop de
        pop de
        ld hl,0
        ld l,a
        pop iy
        pop ix
        ret
_st_wire_read:
        ld de,0
        ld a,(ST_LAST_RAW)
        ld e,a
        ld a,(ST_LAST_RAW+1)
        ld d,a
        ld hl,65535
        or a
        sbc hl,de
        ret
