; Experimental application-RAM observer. No UART/GPIO I/O, C IRQ callback,
; vectors, transport writes, EI/RETI in marker or shared foreground snapshot.
; Marker entry is under DI and preserves all primary/shadow/ADL registers.
; Foreground timer operations sample IFF and restore it independently.
 .assume adl=1
 .section .text
 .global _agon_rxdiag_entry,_agon_rxdiag_claim,_agon_rxdiag_prepare
 .global _agon_rxdiag_publish,_agon_rxdiag_enabled,_agon_rxdiag_ready_sample
 .global _agon_rxdiag_retire,_agon_rxdiag_freeze
 .extern _agon_rxdiag_record,_agon_rxdiag_next_epoch,_agon_rxdiag_ready
_agon_rxdiag_entry:
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
 ld a,b
 ld (remaining),a
 ld a,c
 ld (raw),a
 ld a,d
 ld (pc),a
 ld a,e
 ld (hold),a
 ld (prefix),hl
 ld a,(_agon_rxdiag_record+12)
 bit 1,a
 jp nz,marker_done
 ld a,(event)
 cp 0x40
 jp z,first_fault
 ld a,(armed)
 or a
 jp z,marker_done
 call sample
 ld a,(event)
 cp 0x20
 jr z,first_read_point
 cp 0x21
 jr z,cap_point
 cp 0x22
 jr z,empty_point
 cp 0x80
 jp nc,end_event
 cp 0x20
 jp nc,partial
 cp 0x10
 jp nc,inner_begin
 ; Only begin1..6 reaches this path. Save one outer, tags/depth for nesting.
 or a
 jp z,marker_done
 cp 7
 jp nc,marker_done
 ld a,(active)
 or a
 jr z,outer_begin
 jp inner_begin
first_read_point:
 ld a,(sample_low)
 ld (_agon_rxdiag_record+108),a
 ld a,(sample_high)
 ld (_agon_rxdiag_record+109),a
 ld a,(sample_ctrl)
 ld (_agon_rxdiag_record+110),a
 ld a,1
 ld (_agon_rxdiag_record+111),a
 jp marker_done
cap_point:
 ld hl,_agon_rxdiag_record+100
 call increment32
 jp marker_done
empty_point:
 ld hl,_agon_rxdiag_record+104
 call increment32
 jp marker_done
outer_begin:
 ld a,1
 ld (active),a
 ld hl,_agon_rxdiag_record+56
 ld de,_agon_rxdiag_record+32
 ld bc,24
 ldir                         ; preserve preceding completed span
 ; Do not clear24 bytes on every marked interrupt. Only prior endpoint,
 ; derived-duration and nesting bytes can persist; starts overwrite the rest.
 ld hl,0
 ld (_agon_rxdiag_record+70),hl
 ld (_agon_rxdiag_record+72),hl
 ld (_agon_rxdiag_record+75),hl
 xor a
 ld (_agon_rxdiag_record+67),a
 ld hl,_agon_rxdiag_record+16
 ld de,_agon_rxdiag_record+56
 ld bc,4
 ldir
 ld hl,_agon_rxdiag_record+20
 call increment32
 ld hl,_agon_rxdiag_record+20
 ld de,_agon_rxdiag_record+60
 ld bc,4
 ldir
 ld a,(event)
 ld (_agon_rxdiag_record+64),a
 ld a,3                       ; PRESENT/start sample captured, decoder checks it
 ld (_agon_rxdiag_record+65),a
 ld a,(pc)
 ld (_agon_rxdiag_record+66),a
 ld a,(sample_low)
 ld (_agon_rxdiag_record+68),a
 ld a,(sample_high)
 ld (_agon_rxdiag_record+69),a
 ld a,(sample_ctrl)
 ld (_agon_rxdiag_record+74),a
 jp marker_done
inner_begin:
 ld a,(active)
 or a
 jp z,partial
 ld a,(_agon_rxdiag_record+77)
 cp 8
 jp nc,overflow
 ld de,0
 ld e,a
 ld hl,inner_stack
 add hl,de
 ld a,(event)
 ld (hl),a
 ld (_agon_rxdiag_record+76),a
 ld a,e
 inc a
 ld (_agon_rxdiag_record+77),a
 jp marker_done
end_event:
 ld a,(active)
 or a
 jp z,partial
 ld a,(_agon_rxdiag_record+77)
 or a
 jr z,outer_end
 dec a
 ld de,0
 ld e,a
 ld hl,inner_stack
 add hl,de
 ld a,(event)
 and 0x7f
 cp (hl)
 jp nz,partial
 ld a,e
 ld (_agon_rxdiag_record+77),a
 or a
 jr z,inner_cleared
 dec hl
 ld a,(hl)
inner_cleared:
 ld (_agon_rxdiag_record+76),a
 jp marker_done
outer_end:
 ld a,(event)
 and 0x7f
 ld b,a
 ld a,(_agon_rxdiag_record+64)
 cp b
 jr nz,partial
 ld a,(pc)
 ld (_agon_rxdiag_record+67),a
 ld a,(sample_low)
 ld (_agon_rxdiag_record+70),a
 ld a,(sample_high)
 ld (_agon_rxdiag_record+71),a
 ld a,(sample_ctrl)
 ld (_agon_rxdiag_record+75),a
 ld a,7                       ; endpoint-present only; no duration-valid bit
 ld (_agon_rxdiag_record+65),a
 ; current stays as last complete; active is separate from retained outer tag.
 xor a
 ld (active),a
 jp marker_done
partial:
 ld a,(_agon_rxdiag_record+12)
 or 16
 ld (_agon_rxdiag_record+12),a
 jp marker_done
overflow:
 ld a,(_agon_rxdiag_record+12)
 or 8
 ld (_agon_rxdiag_record+12),a
marker_done_short:
 jp marker_done
first_fault:
 ld a,(active)
 or a
 jr z,fault_raw
 ld a,(_agon_rxdiag_record+65)
 or 16
 ld (_agon_rxdiag_record+65),a
fault_raw:
 ; Raw error survives even while timer disarmed/expired. No extra LSR read.
 ld a,(raw)
 ld (_agon_rxdiag_record+80),a
 ld a,(remaining)
 ld (_agon_rxdiag_record+81),a
 ld a,(pc)
 ld (_agon_rxdiag_record+82),a
 ld a,(hold)
 ld (_agon_rxdiag_record+83),a
 ld hl,(prefix)
 ld de,_agon_rxdiag_record+84
 ld bc,6
 ldir
 ld a,31
 ld (_agon_rxdiag_record+90),a
 ld a,0x40
 ld (_agon_rxdiag_record+95),a
 ld a,(armed)
 or a
 jr z,fault_no_clock
 call sample
 ld a,(sample_low)
 ld (_agon_rxdiag_record+92),a
 ld a,(sample_high)
 ld (_agon_rxdiag_record+93),a
 ld a,(sample_ctrl)
 ld (_agon_rxdiag_record+94),a
 jr freeze_fault
fault_no_clock:
 ld a,(_agon_rxdiag_record+12)
 or 4
 ld (_agon_rxdiag_record+12),a
freeze_fault:
 ld a,(_agon_rxdiag_record+12)
 or 0x82
 ld (_agon_rxdiag_record+12),a
marker_done:
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
sample:
 in0 a,(0x84)
 ld (sample_low),a
 in0 a,(0x85)
 ld (sample_high),a
 in0 a,(0x83)
 ld (sample_ctrl),a
 ret
increment32:
 ld b,4
inc_byte:
 inc (hl)
 ret nz
 inc hl
 djnz inc_byte
 ; HL advanced four bytes after overflow. Saturate the original counter.
 ld b,4
saturate:
 dec hl
 ld (hl),255
 djnz saturate
 ld a,(_agon_rxdiag_record+12)
 or 8
 ld (_agon_rxdiag_record+12),a
 ret
_agon_rxdiag_enabled:
 ld hl,0
 ld a,i
 ret po
 inc hl
 ret
; Each foreground leaf has independent short exclusion; no loop under DI.
guard:
 ld a,i
 di
 ld a,0
 jp po,guard_saved
 inc a
guard_saved:
 ld (iff),a
 ret
leave:
 ld a,(iff)
 or a
 ret z
 ei
 ret
_agon_rxdiag_claim:
 call guard
 ld hl,0
 ld a,(owned)
 or a
 jr nz,leave
 in0 a,(0x83)
 and 0x41
 jr nz,leave
 in0 a,(0x92)
 and 0x0c
 ld (saved_source),a
 ld a,1
 ld (owned),a
 inc hl
 jr leave
_agon_rxdiag_prepare:
 call guard
 ld hl,0
 ld a,(owned)
 or a
 jr z,leave
 ld a,(_agon_rxdiag_record+12)
 bit 1,a
 jr nz,leave
 ld a,(active)
 or a
 jr nz,leave
 xor a
 ld (armed),a
 out0 (0x83),a
 in0 a,(0x92)
 and 0xf3
 out0 (0x92),a
 xor a
 out0 (0x84),a
 out0 (0x85),a
 in0 a,(0x83)
 ld a,0x0f
 out0 (0x83),a
 ld a,(_agon_rxdiag_record+12)
 or 32
 ld (_agon_rxdiag_record+12),a
 inc hl
 jp leave
_agon_rxdiag_ready_sample:
 call guard
 in0 a,(0x84)
 ld (_agon_rxdiag_ready),a
 in0 a,(0x85)
 ld (_agon_rxdiag_ready+1),a
 in0 a,(0x83)
 ld (_agon_rxdiag_ready+2),a
 jp leave
_agon_rxdiag_publish:
 call guard
 ld hl,0
 ld a,(_agon_rxdiag_record+12)
 bit 1,a
 jp nz,leave
 ld a,(owned)
 or a
 jp z,leave
 ld a,(active)
 or a
 jp nz,leave
 in0 a,(0x92)
 and 0x0c
 jp nz,leave
 call sample
 ld a,(sample_ctrl)
 cp 0x0d
 jp nz,leave
 ld a,(sample_low)
 ld b,a
 ld a,(sample_high)
 or b
 jp z,leave
 ld hl,_agon_rxdiag_next_epoch
 ld de,_agon_rxdiag_record+16
 ld bc,4
 ldir
 ld a,1
 ld (armed),a
 ld hl,1
 jp leave
_agon_rxdiag_freeze:
 call guard
 ld a,(_agon_rxdiag_record+12)
 or 2
 ld (_agon_rxdiag_record+12),a
 jp leave
_agon_rxdiag_retire:
 call guard
 ld a,(owned)
 or a
 jp z,leave
 xor a
 ld (armed),a
 ld (owned),a
 out0 (0x83),a
 out0 (0x84),a
 out0 (0x85),a
 in0 a,(0x83)
 in0 a,(0x92)
 and 0xf3
 ld b,a
 ld a,(saved_source)
 or b
 out0 (0x92),a
 jp leave
 .section .bss
owned: .ds 1
armed: .ds 1
active: .ds 1
saved_source: .ds 1
iff: .ds 1
event: .ds 1
remaining: .ds 1
raw: .ds 1
pc: .ds 1
hold: .ds 1
prefix: .ds 3
sample_low: .ds 1
sample_high: .ds 1
sample_ctrl: .ds 1
inner_stack: .ds 8
