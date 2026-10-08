; HDMI02-W: reuse lcd-color-bars' ordinary MOS executable wrapper.
; Startup, not this program, selects the video mode and EMOS display route.
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
    ld hl,finish
    ld bc,finish_end-finish
    rst.lil 0x18
    pop iy
    pop ix
    ld hl,0
    ret
commands:
    incbin "pattern.vdu"
commands_end:
finish:
    db 17,128,17,7,23,1,1,31,0,57,13,10
finish_end:
