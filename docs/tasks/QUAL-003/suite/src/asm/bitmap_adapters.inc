; Application-neutral additions missing from the preserved Nurples snapshot.
; All serialized words use exact byte stores; MOS RST 18 owns transmission.
ext_sprite_hardware:
    ld hl,@cmd
    ld bc,3
    rst.lil 0x18
    ret
@cmd: db 23,27,19

ext_sprite_software:
    ld hl,@cmd
    ld bc,3
    rst.lil 0x18
    ret
@cmd: db 23,27,20

ext_sprite_replace8:
    ld (@arg),a
    ld hl,@cmd
    ld bc,4
    rst.lil 0x18
    ret
@cmd: db 23,27,21
@arg: db 0

ext_sprite_replace16:
    ld a,l
    ld (@arg),a
    ld a,h
    ld (@arg+1),a
    ld hl,@cmd
    ld bc,5
    rst.lil 0x18
    ret
@cmd: db 23,27,0x35
@arg: dw 0
