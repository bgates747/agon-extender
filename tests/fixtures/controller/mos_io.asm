; AgonDev ADL bindings. Ordinary MOS counted output and atomic sysvar read.
; Pinned EMOS counted output returns A=0 on success on both display routes.
; No UART/GPIO access; preserve IX/IY across MOS output.
    .assume adl=1
    .section .text
    .global _bench_clock
    .global _bench_count
_bench_clock:
    ld hl,3
    add hl,sp
    ld hl,(hl)
    ld hl,(hl)
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
    ld l,a
    pop iy
    pop ix
    ret
