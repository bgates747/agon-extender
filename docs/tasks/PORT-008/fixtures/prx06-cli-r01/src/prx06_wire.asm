/* PRX-06 historical sender, CLI launch variant.
 * First-pass exception only; not a supported EMOS transport API.
 * Admission polling extended 16-fold so host can flash/verify the receiver
 * after CLI RUN. Counts are instruction-loop budgets, not calibrated seconds.
 * Byte kernels, seven profiles and completion timeout are unchanged.
 */
        .assume adl=1
        .equ PC_DR,0x9e
        .equ PC_DDR,0x9f
        .equ PC_ALT1,0xa0
        .equ PC_ALT2,0xa1
        .equ PD_DR,0xa2
        .equ PD_DDR,0xa3
        .equ PD_ALT1,0xa4
        .equ PD_ALT2,0xa5
        .equ READY_BIT,0x10
        .equ CLOCK_BIT,0x20
        .equ VALID_BIT,0x80
        .equ KEEP_CTRL,0x4f
        .equ KEEP_CLOCK,0xdf
        .equ KEEP_VALID,0x7f
        .equ OUTPUT_DDR,0x5f
        .section .text
        .global _prx06_enter_idle
        .global _prx06_send

_prx06_enter_idle:
        ld a,0xff
        out0 (PC_DDR),a
        xor a
        out0 (PC_ALT1),a
        out0 (PC_ALT2),a
        in0 a,(PD_ALT1)
        and KEEP_CTRL
        out0 (PD_ALT1),a
        in0 a,(PD_ALT2)
        and KEEP_CTRL
        out0 (PD_ALT2),a
        in0 a,(PD_DR)
        and KEEP_CLOCK
        or VALID_BIT
        ld (_pd_low),a
        or CLOCK_BIT
        ld (_pd_high),a
        ld a,(_pd_low)
        out0 (PD_DR),a
        in0 a,(PD_DDR)
        or READY_BIT | CLOCK_BIT | VALID_BIT
        out0 (PD_DDR),a
        ret

_prx06_send:
        push ix
        ld ix,0
        add ix,sp
        ld hl,(ix+6)
        ld a,(ix+9)
        ld (_profile),a
        call .Lsave_iff
        in0 a,(PD_ALT1)
        and KEEP_CTRL
        out0 (PD_ALT1),a
        in0 a,(PD_ALT2)
        and KEEP_CTRL
        out0 (PD_ALT2),a
        in0 a,(PD_DR)
        and KEEP_CLOCK
        or VALID_BIT
        ld (_pd_low),a
        or CLOCK_BIT
        ld (_pd_high),a
        ld a,(_pd_low)
        out0 (PD_DR),a
        in0 a,(PD_DDR)
        or READY_BIT
        and OUTPUT_DDR
        out0 (PD_DDR),a
        ld a,16
        ld (_admission_rounds),a
        ld a,160
        ld (_wait_windows),a
        ld bc,0
.Lwait_ready:
        ld a,(_pd_high)
        out0 (PD_DR),a
        .rept 16
        nop
        .endr
        ld a,(_pd_low)
        out0 (PD_DR),a
        in0 a,(PD_DR)
        and READY_BIT
        jr z,.Ladmitted
        dec bc
        ld a,b
        or c
        jr nz,.Lwait_ready
        ld a,(_wait_windows)
        dec a
        ld (_wait_windows),a
        ld bc,0
        jr nz,.Lwait_ready
        ld a,(_admission_rounds)
        dec a
        ld (_admission_rounds),a
        jr z,.Ladmission_timeout
        ld a,160
        ld (_wait_windows),a
        ld bc,0
        jr .Lwait_ready
.Ladmission_timeout:
        ld a,1
        jp .Lfinish

.Ladmitted:
        ld a,(hl)
        out0 (PC_DR),a
        xor a
        out0 (PC_DDR),a
        ld a,(_pd_low)
        and KEEP_VALID
        ld e,a
        out0 (PD_DR),a
        ld a,(_pd_high)
        and KEEP_VALID
        ld d,a
        ld a,(_profile)
        or a
        jp z,.Lkernel24
        dec a
        jp z,.Lkernel16
        dec a
        jp z,.Lkernel10
        dec a
        jp z,.Lkernel6
        dec a
        jp z,.Lkernel3
        dec a
        jp z,.Lkernel1
        jp .Lkernel0

        .macro KERNEL name, delay
\name:
        ld c,4
.Louter\@:
        ld b,0
.Lbyte\@:
        ld a,(hl)
        out0 (PC_DR),a
        .rept \delay
        nop
        .endr
        ld a,d
        out0 (PD_DR),a
        .rept \delay
        nop
        .endr
        ld a,e
        out0 (PD_DR),a
        .rept \delay
        nop
        .endr
        inc hl
        djnz .Lbyte\@
        dec c
        jr nz,.Louter\@
        jp .Lrecord_done
        .endm
        KERNEL .Lkernel24,24
        KERNEL .Lkernel16,16
        KERNEL .Lkernel10,10
        KERNEL .Lkernel6,6
        KERNEL .Lkernel3,3
        KERNEL .Lkernel1,1
        KERNEL .Lkernel0,0

.Lrecord_done:
        ld a,e
        or VALID_BIT
        out0 (PD_DR),a
        ld a,32
        ld (_wait_windows),a
        ld bc,0
.Lwait_release:
        ld a,(_pd_high)
        out0 (PD_DR),a
        .rept 16
        nop
        .endr
        ld a,(_pd_low)
        out0 (PD_DR),a
        in0 a,(PD_DR)
        and READY_BIT
        jr nz,.Lok
        dec bc
        ld a,b
        or c
        jr nz,.Lwait_release
        ld a,(_wait_windows)
        dec a
        ld (_wait_windows),a
        ld bc,0
        jr nz,.Lwait_release
        ld a,2
        jr .Lfinish
.Lok:
        xor a
.Lfinish:
        push af
        call _prx06_enter_idle
        call .Lrestore_iff
        pop af
        pop ix
        ret
.Lsave_iff:
        ld a,i
        jp po,.Liff_off
        ld a,1
        jr .Lsave
.Liff_off:
        xor a
.Lsave:
        ld (_saved_iff),a
        di
        ret
.Lrestore_iff:
        ld a,(_saved_iff)
        or a
        ret z
        ei
        ret
        .section .bss
_pd_low: .space 1
_pd_high: .space 1
_profile: .space 1
_saved_iff: .space 1
_wait_windows: .space 1

_admission_rounds: .space 1
