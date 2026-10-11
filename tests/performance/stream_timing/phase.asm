; PORT-008 PHASE-TIMING-R01. Recorder only: no transport/GPIO writes.
; EMOS's guarded leaf jumps here through the verified B0020 RAM vector.
; Append exactly one eight-byte record under a bounded DI, then restore the
; original AF, BC, DE, HL, IX, IY, SP and IFF. No callbacks or logging here.
        .assume adl=1
        .include "binding.inc"
        .section .text
        .global _phase_record
        .global _phase_probe
_phase_probe:
        call ST_HOOK
        ret
_phase_record:
        push af
        ld a,i
        push af
        di
        push bc
        push de
        push hl
        push ix
        push iy
        ld iy,0
        add iy,sp
        in0 e,(084h)
        in0 d,(085h)
        ld hl,(_phase_count)
        ld a,h
        cp 2
        jr nc,phase_overflow
        inc hl
        ld (_phase_count),hl
        dec hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,_phase_records
        add hl,bc
        ld bc,(iy+21)
        ld (hl),bc
        inc hl
        inc hl
        inc hl
        ld (hl),e
        inc hl
        ld (hl),d
        inc hl
        ld bc,(ST_OFFER+10)
        ld (hl),bc
        jr phase_return
phase_overflow:
        xor a
        ld (ST_ARMED),a
        inc a
        ld (_phase_overflow),a
phase_return:
        pop iy
        pop ix
        pop hl
        pop de
        pop bc
        pop af
        jp po,phase_iff_off
        pop af
        ei
        ret
phase_iff_off:
        pop af
        ret
        .section .bss
        .global _phase_count
        .global _phase_records
        .global _phase_overflow
_phase_count:
        .space 3
_phase_overflow:
        .space 1
_phase_records:
        .space 4096
