; Raw resident timestamp -> elapsed PRT ticks, zero-extended before subtraction.
; Application RAM read only; EMOS owns the timestamp and transport operations.
        .assume adl=1
        .include "binding.inc"
        .section .text
        .global _st_wire_read
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
