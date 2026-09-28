    assume adl=1
    org 0x040000
    jp start
    align 64
    db "MOS",0,1
start:
    push ix
    push iy
    ld hl,commands
    ld bc,commands_end-commands
    rst.lil 0x18
wait_key:
    xor a
    rst.lil 0x08
    cp 27
    jr nz,wait_key
    pop iy
    pop ix
    ld hl,0
    ret
commands:
    incbin "grid.vdu"
commands_end:
