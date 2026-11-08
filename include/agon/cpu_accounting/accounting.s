; MGCPU001/schema1. Bounded native recorder; existing rxdiag owns one PRT1.
; No vectors/UART/GPIO/C calls. DI callers serialize shared scratch. NMI uses
; separate entry at+4, writing ONLY poison (never shares recorder scratch).
.assume adl=1
.text
.global _agon_cpu_entry,_agon_cpu_foreground
.global _agon_cpu_start_native,_agon_cpu_stop_native
.extern _agon_cpu_record
_agon_cpu_entry:
 jp marker
 jp poison
poison:
 push af
 ld a,1
 ld (_agon_cpu_record+13),a
 pop af
 ret
; Independent foreground IFF save; interrupt between LD A,I and DI retains
; incoming IFF by the ordinary MOS convention. No loop in exclusion.
_agon_cpu_start_native:
 push af
 ld a,0x60
 call _agon_cpu_foreground
 pop af
 ret
_agon_cpu_stop_native:
 push af
 ld a,0x70
 call _agon_cpu_foreground
 pop af
 ret
_agon_cpu_foreground:
 push af
 push bc
 ld b,a
 ld a,i
 di
 push af
 ld a,b
 call _agon_cpu_entry
 pop af
 jp po,foreground_disabled
 pop bc
 pop af
 ei
 ret
foreground_disabled:
 pop bc
 pop af
 ret
marker:
 push af
 push bc
 push de
 push hl
 push ix
 push iy
 ex af,af'
 push af
 exx
 push bc
 push de
 push hl
 exx
 ex af,af'
 ld (event),a
 ld a,(_agon_cpu_record+13)
 or a
 jp nz,done
 ld a,(event)
 cp 0x60
 jp z,start
 ld a,(_agon_cpu_record+14)
 or a
 jp z,done
 call sample
 jp c,clock_bad
 ; Charge previous end->this start to its exclusive instrumented class.
 ld de,(last)
 ex de,hl
 or a
 sbc hl,de
 jp c,clock_bad
 push hl
 ld a,(_agon_cpu_record+24)
 call total_for_class
 pop de
 call add_count
 jp c,overflow
 ; If interrupted class IRQ, also subdivide that same time by vector; NEVER
 ; add subdivisions to the exclusive total again in the decoder.
 ld a,(_agon_cpu_record+24)
 cp 2
 jp nz,state_change
 ld a,(_agon_cpu_record+26)
 dec a
 add a,a
 ld e,a
 ld d,0
 ld hl,_agon_cpu_record+42
 add hl,de
 ld de,(delta)
 call add_count
 jp c,overflow
state_change:
 ld a,(event)
 cp 1
 jp c,context_bad
 cp 4
 jp c,irq_enter
 cp 4
 jp z,gate_enter
 cp 6
 jp z,halt_enter
 cp 7
 jp z,finish
 cp 0x20
 jp z,callback_enter
 cp 0x21
 jp z,callback_exit
 cp 0x30
 jp z,wait_enter
 cp 0x31
 jp z,wait_exit
 cp 0x70
 jp z,stop
 cp 0x81
 jp c,context_bad
 cp 0x84
 jp c,irq_exit
 cp 0x84
 jp z,gate_exit
 cp 0x86
 jp z,halt_return
context_bad:
 ld a,0x14
 jp invalid
clock_bad:
 ld a,0x0c
 jp invalid
overflow:
 ld a,0x24
invalid:
 ld b,a
 ld a,(_agon_cpu_record+12)
 or b
 ld (_agon_cpu_record+12),a
 xor a
 ld (_agon_cpu_record+14),a
 jp done
start:
 ld a,(_agon_cpu_record+15)
 or a
 jp nz,context_bad
 call sample
 jp c,clock_bad
 push af
 ld a,l
 ld (_agon_cpu_record+20),a
 ld a,h
 ld (_agon_cpu_record+21),a
 pop af
 ld (_agon_cpu_record+58),a
 ld (first),hl
 ld a,1
 ld (_agon_cpu_record+14),a
 jp finish
irq_enter:
 ld a,(_agon_cpu_record+26)
 or a
 jp nz,context_bad
 ld a,(_agon_cpu_record+24)
 cp 3
 jp nz,resume
 xor a                       ; first IRQ ends logical taken-HALT interval
resume:
 ld (_agon_cpu_record+25),a
 ld a,(event)
 ld (_agon_cpu_record+26),a
 dec a
 add a,a
 ld e,a
 ld d,0
 ld hl,_agon_cpu_record+48
 add hl,de
 ld de,1
 call add_count
 jp c,overflow
 ld a,2
 jp class_set
irq_exit:
 ld a,(event)
 and 0x7f
 ld b,a
 ld a,(_agon_cpu_record+26)
 cp b
 jp nz,context_bad
 xor a
 ld (_agon_cpu_record+26),a
 ld a,(_agon_cpu_record+25)
 jp class_set
gate_enter:
 ld a,(_agon_cpu_record+24)
 or a
 jp nz,context_bad
 ld a,1
 jp class_set
gate_exit:
 ld a,(_agon_cpu_record+24)
 cp 1
 jp nz,context_bad
 xor a
 jp class_set
halt_enter:
 ld a,(_agon_cpu_record+24)
 or a
 jp nz,context_bad
 ld a,3
 jp class_set
halt_return:
 ; Real IRQ exit already restored foreground; without one, HALT isn't proved.
 ld a,(_agon_cpu_record+24)
 or a
 jp nz,context_bad
 jp finish
class_set:
 ld (_agon_cpu_record+24),a
 jp finish
callback_enter:
 ld a,(_agon_cpu_record+62)
 cp 4
 jp nc,context_bad
 inc a
 ld (_agon_cpu_record+62),a
 ld b,a
 ld a,(_agon_cpu_record+63)
 cp b
 jp nc,finish
 ld a,b
 ld (_agon_cpu_record+63),a
 jp finish
callback_exit:
 ld a,(_agon_cpu_record+62)
 or a
 jp z,context_bad
 dec a
 ld (_agon_cpu_record+62),a
 jp finish
wait_enter:
 ld a,(_agon_cpu_record+27)
 or a
 jp nz,context_bad
 inc a
 ld (_agon_cpu_record+27),a
 jp finish
wait_exit:
 ld a,(_agon_cpu_record+27)
 dec a
 jp nz,context_bad
 ld (_agon_cpu_record+27),a
 jp finish
stop:
 ld a,(_agon_cpu_record+24)
 or a
 jp nz,context_bad
 ld a,(_agon_cpu_record+62)
 ld b,a
 ld a,(_agon_cpu_record+27)
 or b
 jp nz,context_bad
 ld a,1
 ld (_agon_cpu_record+15),a
 xor a
 ld (_agon_cpu_record+14),a
finish:
 ; Every marker has separately captured internal observer work. Prefix register
 ; saves and suffix restores are NOT captured: PARTIAL_BOUNDARIES is mandatory.
 ld hl,(current)
 ld (before),hl
 call sample
 jp c,clock_bad
 ld (_agon_cpu_record+59),a
 ld (last),hl
 push af
 ld a,l
 ld (_agon_cpu_record+22),a
 ld a,h
 ld (_agon_cpu_record+23),a
 pop af
 ex de,hl
 ld hl,(before)
 or a
 sbc hl,de
 jp c,clock_bad
 ex de,hl
 ld hl,_agon_cpu_record+40
 call add_count
 jp c,overflow
 ld de,1
 ld hl,_agon_cpu_record+54
 call add_count
 jp c,overflow
 ld a,(_agon_cpu_record+15)
 or a
 jp z,done
 ld hl,(last)
 push af
 ld a,l
 ld (_agon_cpu_record+60),a
 ld a,h
 ld (_agon_cpu_record+61),a
 pop af
 jp done
; Sample same single-pass provider; invalid ctrl/source/zero/increase/limit
; never wraps. first=0 means initial sample. These are timer reads ONLY.
sample:
 ld hl,0
 in0 l,(0x84)
 in0 h,(0x85)
 in0 a,(0x83)
 cp 0x0d
 jp nz,bad_sample
 ld (_agon_cpu_record+57),a
 in0 a,(0x92)
 and 0x0c
 jp nz,bad_sample
 ld a,l
 or h
 jp z,bad_sample
 ld (current),hl
 ld de,(first)
 ld a,d
 or e
 jp z,sample_ok
 ex de,hl
 or a
 sbc hl,de
 jp c,bad_sample
 ld de,54001
 or a
 sbc hl,de
 jp nc,bad_sample
 ld hl,(current)
sample_ok:
 ld a,0x0d
 or a
 ret
bad_sample:
 scf
 ret
; HL points to LE16 counter; DE delta. All totals <=54000 by window contract,
; but overflow remains checked and never wraps into an accepted snapshot.
add_count:
 ld (delta),de
 ld e,(hl)
 inc hl
 ld d,(hl)
 push hl
 ld hl,(delta)
 add hl,de
 ld (sum),hl
 ex de,hl
 pop hl
 ld a,(sum+2)
 or a
 jp nz,add_overflow
 ld (hl),d
 dec hl
 ld (hl),e
 or a
 ret
add_overflow:
 ld (hl),255
 dec hl
 ld (hl),255
 scf
 ret
; Class0..4 -> total offset32,34,36,38,40.
total_for_class:
 add a,a
 ld e,a
 ld d,0
 ld hl,_agon_cpu_record+32
 add hl,de
 ret
done:
 ex af,af'
 exx
 pop hl
 pop de
 pop bc
 exx
 pop af
 ex af,af'
 pop iy
 pop ix
 pop hl
 pop de
 pop bc
 pop af
 ret
.bss
event: .ds 1
first: .ds 3
last: .ds 3
current: .ds 3
before: .ds 3
delta: .ds 3
sum: .ds 3
