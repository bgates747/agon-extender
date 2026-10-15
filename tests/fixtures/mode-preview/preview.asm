; HDMI-004 interactive visual review: explicit Author exception permits mode
; changes here. Every VDU byte uses MOS routing; EMOS owns console activation.
; Streams through 4096 bytes of RAM; never loads a full raster into eZ80 RAM.
assume adl=1
org 040000h
jp start
align 64
db "MOS",0,1
start:
 push ix
 push iy
 ld hl,excom
 ld a,10h
 rst.lil 08h
 or a
 jp nz,exit
menu:
 ld hl,menu_vdu
 ld bc,menu_end-menu_vdu
 rst.lil 18h
 xor a
 ld (number),a
 ld (digits),a
input:
 xor a
 rst.lil 08h
 cp 27
 jp z,exit
 cp 13
 jr z,select
 cp '0'
 jr c,input
 cp '9'+1
 jr nc,input
 ld b,a
 ld a,(digits)
 cp 3
 jr nc,input
 inc a
 ld (digits),a
 ld a,b
 push af
 rst.lil 10h
 pop af
 sub '0'
 ld c,a
 ld a,(number)
 ld hl,0
 ld l,a
 ld de,0
 ld e,a
 add hl,hl
 add hl,hl
 add hl,de
 add hl,hl
 ld de,0
 ld e,c
 add hl,de
 ld a,h
 or a
 jr nz,bad
 ld a,l
 ld (number),a
 jr input
select:
 ld a,(digits)
 or a
 jr z,input
 ld a,(number)
 ld hl,entries
 ld b,ENTRY_COUNT
search:
 cp (hl)
 jr z,found
 ld de,4
 add hl,de
 djnz search
bad:
 ld hl,bad_message
 call print
 xor a
 rst.lil 08h
 jp menu
found:
 inc hl
 ld hl,(hl)
 ld c,1
 ld a,0ah
 rst.lil 08h
 or a
 jr z,bad
 ld (handle),a
stream:
 ld a,(handle)
 ld c,a
 ld hl,chunk
 ld de,4096
 ld a,1ah
 rst.lil 08h
 ld a,d
 or e
 jr z,closed
 push de
 pop bc
 ld hl,chunk
 rst.lil 18h
 jr stream
closed:
 ld a,(handle)
 ld c,a
 ld a,0bh
 rst.lil 08h
 ; Escape alone returns to the menu; ignore Tab and other app-switch input.
preview_key:
 xor a
 rst.lil 08h
 cp 27
 jr nz,preview_key
 jp menu
exit:
 ld hl,cleanup
 ld bc,cleanup_end-cleanup
 rst.lil 18h
 ld hl,legacy
 ld a,10h
 rst.lil 08h
 pop iy
 pop ix
 ld hl,0
 ret
print:
 ld a,(hl)
 or a
 ret z
 rst.lil 10h
 inc hl
 jr print
excom: db "EMOS EXCOM --keep-display",0
legacy: db "EMOS LEGACY --keep-display",0
bad_message: db 13,10,"Unknown mode or missing asset. Press a key.",13,10,0
number: db 0
digits: db 0
handle: db 0
cleanup: db 22,0,23,1,1,12
cleanup_end:
include "generated.inc"
chunk: ds 4096
