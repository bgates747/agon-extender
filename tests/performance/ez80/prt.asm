; PRT1 measurement, derived from timer.inc register definitions.
; Requires unused/disabled PRT1 and system-clock source. PRT0 remains untouched.
; Single-pass /16: nominal 1,152,000 counts/s at 18.432 MHz, saturation after
; 65535 counts (~56.89 ms). No interrupts, shared source selector or vectors changed.
; Low read latches high per eZ80F92 PS0153. Saturation is never treated as wrap.
        .assume adl=1
        .section .text
        .global _gt_prt_init
        .global _gt_prt_begin
        .global _gt_prt_read
        .global _gt_prt_close
_gt_prt_init:
        ld hl,0
        in0 a,(083h)
        and 07fh
        ret nz
        in0 a,(092h)
        and 00ch
        ret nz
        ld a,0ffh
        out0 (084h),a
        out0 (085h),a
        inc hl
        ret
_gt_prt_begin:
        xor a
        out0 (083h),a
        ld a,007h
        out0 (083h),a
        ret
_gt_prt_read:
        ld de,0
        in0 e,(084h)
        in0 d,(085h)
        ld hl,65535
        or a
        sbc hl,de
        ret
_gt_prt_close:
        xor a
        out0 (083h),a
        ret
