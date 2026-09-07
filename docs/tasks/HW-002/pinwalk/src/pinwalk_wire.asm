/* Standalone, low-rate eZ80 header pinwalk. */
        .assume adl=1
        .equ PB_DR,0x9a
        .equ PB_DDR,0x9b
        .equ PB_ALT1,0x9c
        .equ PB_ALT2,0x9d
        .equ PC_DR,0x9e
        .equ PC_DDR,0x9f
        .equ PC_ALT1,0xa0
        .equ PC_ALT2,0xa1
        .equ PD_DR,0xa2
        .equ PD_DDR,0xa3
        .equ PD_ALT1,0xa4
        .equ PD_ALT2,0xa5
        .equ PB5_BIT,0x20
        .equ HALF_DELAY_OUTER,92

        .section .text
        .global _pinwalk_gpio_run
        .global _pinwalk_release

/* Leave the direct header GPIO as inputs. Dedicated CLK/I2C/SPI are untouched. */
_pinwalk_release:
        ld a,0xff
        out0 (PC_DDR),a
        xor a
        out0 (PC_ALT1),a
        out0 (PC_ALT2),a
        in0 a,(PD_DDR)
        or 0xf0
        out0 (PD_DDR),a
        in0 a,(PD_ALT1)
        and 0x0f
        out0 (PD_ALT1),a
        in0 a,(PD_ALT2)
        and 0x0f
        out0 (PD_ALT2),a
        in0 a,(PB_DDR)
        or PB5_BIT
        out0 (PB_DDR),a
        in0 a,(PB_ALT1)
        and 0xdf
        out0 (PB_ALT1),a
        in0 a,(PB_ALT2)
        and 0xdf
        out0 (PB_ALT2),a
        ret

_pinwalk_gpio_run:
        call .Lsave_iff
        in0 a,(PB_DR)
        ld (_saved_pb_dr),a
        in0 a,(PB_DDR)
        ld (_saved_pb_ddr),a
        in0 a,(PB_ALT1)
        ld (_saved_pb_alt1),a
        in0 a,(PB_ALT2)
        ld (_saved_pb_alt2),a
        in0 a,(PC_DR)
        ld (_saved_pc_dr),a
        in0 a,(PC_DDR)
        ld (_saved_pc_ddr),a
        in0 a,(PC_ALT1)
        ld (_saved_pc_alt1),a
        in0 a,(PC_ALT2)
        ld (_saved_pc_alt2),a
        in0 a,(PD_DR)
        ld (_saved_pd_dr),a
        in0 a,(PD_DDR)
        ld (_saved_pd_ddr),a
        in0 a,(PD_ALT1)
        ld (_saved_pd_alt1),a
        in0 a,(PD_ALT2)
        ld (_saved_pd_alt2),a

        xor a
        out0 (PC_ALT1),a
        out0 (PC_ALT2),a
        in0 a,(PD_ALT1)
        and 0x0f
        out0 (PD_ALT1),a
        in0 a,(PD_ALT2)
        and 0x0f
        out0 (PD_ALT2),a
        in0 a,(PB_ALT1)
        and 0xdf
        out0 (PB_ALT1),a
        in0 a,(PB_ALT2)
        and 0xdf
        out0 (PB_ALT2),a

        ld b,1
        ld c,1
.Lpc_loop:
        ld a,c
        call .Lwalk_pc
        inc b
        sla c
        jr nz,.Lpc_loop

        ld b,9
        ld c,0x10
.Lpd_loop:
        ld a,c
        call .Lwalk_pd
        inc b
        sla c
        jr nz,.Lpd_loop

        ld b,13
        ld a,PB5_BIT
        call .Lwalk_pb

        ld a,(_saved_pb_dr)
        out0 (PB_DR),a
        ld a,(_saved_pb_alt1)
        out0 (PB_ALT1),a
        ld a,(_saved_pb_alt2)
        out0 (PB_ALT2),a
        ld a,(_saved_pb_ddr)
        out0 (PB_DDR),a
        ld a,(_saved_pc_dr)
        out0 (PC_DR),a
        ld a,(_saved_pc_alt1)
        out0 (PC_ALT1),a
        ld a,(_saved_pc_alt2)
        out0 (PC_ALT2),a
        ld a,(_saved_pc_ddr)
        out0 (PC_DDR),a
        ld a,(_saved_pd_dr)
        out0 (PD_DR),a
        ld a,(_saved_pd_alt1)
        out0 (PD_ALT1),a
        ld a,(_saved_pd_alt2)
        out0 (PD_ALT2),a
        ld a,(_saved_pd_ddr)
        out0 (PD_DDR),a
        call .Lrestore_iff
        ret

/* A=one-hot mask, B=ordinal pulse count. DDR zero means output. */
.Lwalk_pc:
        ld d,a
        in0 a,(PC_DR)
        or d
        out0 (PC_DR),a
        in0 a,(PC_DDR)
        ld e,a
        ld a,d
        cpl
        and e
        out0 (PC_DDR),a
        call .Lpulses_pc
        in0 a,(PC_DDR)
        or d
        out0 (PC_DDR),a
        call .Lslot_gap
        ret
.Lpulses_pc:
        push bc
        ld c,b
.Lpc_pulse:
        in0 a,(PC_DR)
        xor d
        out0 (PC_DR),a
        call .Lhalf_delay
        in0 a,(PC_DR)
        xor d
        out0 (PC_DR),a
        call .Lhalf_delay
        dec c
        jr nz,.Lpc_pulse
        pop bc
        ret

.Lwalk_pd:
        ld d,a
        in0 a,(PD_DR)
        or d
        out0 (PD_DR),a
        in0 a,(PD_DDR)
        ld e,a
        ld a,d
        cpl
        and e
        out0 (PD_DDR),a
        push bc
        ld c,b
.Lpd_pulse:
        in0 a,(PD_DR)
        xor d
        out0 (PD_DR),a
        call .Lhalf_delay
        in0 a,(PD_DR)
        xor d
        out0 (PD_DR),a
        call .Lhalf_delay
        dec c
        jr nz,.Lpd_pulse
        pop bc
        in0 a,(PD_DDR)
        or d
        out0 (PD_DDR),a
        call .Lslot_gap
        ret

.Lwalk_pb:
        ld d,a
        in0 a,(PB_DR)
        or d
        out0 (PB_DR),a
        in0 a,(PB_DDR)
        ld e,a
        ld a,d
        cpl
        and e
        out0 (PB_DDR),a
        push bc
        ld c,b
.Lpb_pulse:
        in0 a,(PB_DR)
        xor d
        out0 (PB_DR),a
        call .Lhalf_delay
        in0 a,(PB_DR)
        xor d
        out0 (PB_DR),a
        call .Lhalf_delay
        dec c
        jr nz,.Lpb_pulse
        pop bc
        in0 a,(PB_DDR)
        or d
        out0 (PB_DDR),a
        call .Lslot_gap
        ret

.Lslot_gap:
        call .Lhalf_delay
        call .Lhalf_delay
        ret
.Lhalf_delay:
        push bc
        ld b,HALF_DELAY_OUTER
.Ldelay_outer:
        ld c,255
.Ldelay_inner:
        dec c
        jr nz,.Ldelay_inner
        djnz .Ldelay_outer
        pop bc
        ret

.Lsave_iff:
        ld a,i
        jp po,.Liff_off
        ld a,1
        jr .Liff_saved
.Liff_off:
        xor a
.Liff_saved:
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
_saved_iff: .space 1
_saved_pb_dr: .space 1
_saved_pb_ddr: .space 1
_saved_pb_alt1: .space 1
_saved_pb_alt2: .space 1
_saved_pc_dr: .space 1
_saved_pc_ddr: .space 1
_saved_pc_alt1: .space 1
_saved_pc_alt2: .space 1
_saved_pd_dr: .space 1
_saved_pd_ddr: .space 1
_saved_pd_alt1: .space 1
_saved_pd_alt2: .space 1
