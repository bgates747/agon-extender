; AgonDev ADL bindings. Ordinary MOS counted output and atomic sysvar read.
; Pinned EMOS counted output returns A=0 on success on both display routes.
; No UART/GPIO access; preserve IX/IY across MOS output.
    .assume adl=1
    .section .text
    .global _bench_clock
    .global _bench_count
    .global _controller_gateway_available
    .global _controller_gateway_call
    .include "src/emos_api.inc"
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
_controller_gateway_available:
    push ix
    push iy
    ld b,EMOS_FUNCTION_GATEWAY
    ld c,0
    ld a,MOS_GETFUNCTION
    rst.lil 08h
    or a
    ld hl,0
    jr nz,1f
    inc hl
1:  pop iy
    pop ix
    ret
_controller_gateway_call:
    push ix
    ld ix,0
    add ix,sp
    push iy
    ld hl,(ix+6)
    ld a,EMOS_GATEWAY
    rst.lil 08h
    ld hl,0
    ld l,a
    pop iy
    pop ix
    ret
