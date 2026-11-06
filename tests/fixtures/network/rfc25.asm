; Independent fixture bridge for the matched guarded EMOS25 contract.
; Foreground ADL1/MB0/EI; full24-bit args. A0 admits; named refusals publish
; nothing. Preserve IX/IY and A. No raw peripheral access or consumer import.
    .assume adl=1
    .section .text
    .global _netprobe_rfc_submit,_netprobe_rfc_context
_netprobe_rfc_submit:
    push ix
    ld ix,0
    add ix,sp
    push iy
    ld hl,(ix+6)
    ld bc,(ix+9)
    ld de,(ix+12)
    ld (netprobe_rfc_done_address),de
    ld de,netprobe_rfc_callback
    ld a,025h
    rst.lil 08h
    pop iy
    pop ix
    ret
netprobe_rfc_callback:
    ; MOS ISR saves primary HL; store flag only, then ordinary RET to that ISR.
    ; No C, MOS, output, wait or EI here. The source flag was prearmed by C++.
    ld hl,(netprobe_rfc_done_address)
    ld (hl),1
    ret
_netprobe_rfc_context:
    ld a,mb
    or a
    jr nz,netprobe_rfc_bad_context
    ld a,i
    jp po,netprobe_rfc_bad_context
    xor a
    ret
netprobe_rfc_bad_context:
    ld a,32
    ret
    .section .bss
netprobe_rfc_done_address:
    .ds 3
