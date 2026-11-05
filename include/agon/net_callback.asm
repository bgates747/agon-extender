; Optional application-owned MOS KBvector router, AgonDev ADL/GNU assembler.
; App defines unsigned agon_net_callback_packet(const uint8_t *packet): return
; 1 to consume NM, 0 to chain, and void(*agon_net_callback_previous)(void).
; OPEN snapshots the previous vector; app installs this through MOS0x1D before
; CONNECT. RELEASE first, then restore previous via MOS0x1D on every exit.
; C helper must not block/call MOS in ISR. Preserve all entry registers; prior
; callback may edit the borrowed keyboard payload before MOS publishes it.
    .assume adl=1
    .text
    .global _agon_net_callback
    .extern _agon_net_callback_packet
    .extern _agon_net_callback_previous
_agon_net_callback:
    push af
    push bc
    push de
    push hl
    push ix
    push iy
    push de
    call _agon_net_callback_packet
    pop de
    ld a,l
    or a
    jr nz,net_app_callback_done
    ld hl,(_agon_net_callback_previous)
    ld bc,0
    or a
    sbc hl,bc
    jr z,net_app_callback_done
    ld bc,net_app_callback_done
    push bc
    jp (hl)
net_app_callback_done:
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret
