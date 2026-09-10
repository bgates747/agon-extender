; SD application bindings, not firmware replacements. EMOS owns every byte.
; AgonDev C ABI: 3-byte stack slots; IX/IY preserved. No DI, UART or GPIO I/O.
; Counted A status is specific to the pinned EMOS v0.1.12 implementation;
; carry differs by route. Delimiter output cannot expose intermediate failure.
        .assume adl=1
        .section .text
        .global _bench_clock
        .global _bench_count
        .global _bench_bytes
        .global _bench_delimiter

_bench_clock:
        ld hl,3
        add hl,sp
        ld hl,(hl)
        ld hl,(hl)              ; one atomic low-24-bit sysvar read
        ret

_bench_count:
        push ix
        ld ix,0
        add ix,sp
        push iy
        ld hl,(ix+6)
        ld bc,(ix+9)
        rst.lil 18h
        ld hl,0
        ld l,a                  ; both pinned routes return A=0 on success
        pop iy
        pop ix
        ret

_bench_bytes:
        push ix
        ld ix,0
        add ix,sp
        push iy
        ld hl,(ix+6)
        ld b,64
1:      ld a,(hl)
        rst.lil 10h
        jr nc,2f
        inc hl
        djnz 1b
        ld hl,0
        jr 3f
2:      ld hl,1                 ; byte output reports failure only via carry
3:      pop iy
        pop ix
        ret

_bench_delimiter:
        push ix
        ld ix,0
        add ix,sp
        push iy
        ld hl,(ix+6)
        ld bc,0
        ld a,0ffh
        rst.lil 18h
        ld hl,0                 ; no per-byte status in the delimiter ABI
        pop iy
        pop ix
        ret
