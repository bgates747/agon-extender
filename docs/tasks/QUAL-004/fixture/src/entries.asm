.assume adl=1
.section .text
.global _bench_count
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

