; C2 service veneer + inline event adapter. Link with unchanged accounting
; and rxdiag provider sources. Native A-event ABI stays unchanged for WAIT.
; EMOS binds entry+4 only after validating this full8-byte jump-table span.
; CALL-site inline byte is decoded with stack-local storage only. NMI takes
; the FF branch before any shared recorder scratch is touched.
.assume adl=1
.text
.global _agon_cpu_service_entry,_agon_cpu_inline_entry
.extern _agon_neta_service,_agon_cpu_entry,_agon_cpu_record
_agon_cpu_service_entry:
 jp _agon_neta_service
 jp _agon_cpu_inline_entry
_agon_cpu_inline_entry:
 push af
 push hl
 push ix
 ld ix,0
 add ix,sp
 ld hl,(ix+9)                ; caller CALL's return points at inline event
 ld a,(hl)
 inc hl
 ld (ix+9),hl               ; consume exactly one event byte
 pop ix
 pop hl
 cp 0xff
 jr z,inline_poison
 call _agon_cpu_entry        ; unchanged all-register/IFF native A-event ABI
 pop af
 ret
inline_poison:
 ld a,1
 ld (_agon_cpu_record+13),a   ; no shared event/sample scratch, NMI-safe
 pop af
 ret
