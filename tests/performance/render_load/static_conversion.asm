; Supplemental fixed-source HDMI control. Startup owns mode and EMOS routing.
; Draw once, fence, then three ten-second diagnostic windows with no drawing,
; swaps, pixel queries or SD I/O. Keep the chart visible until Escape.
; MOS's raw clock advances by two per vblank: 120 units/s at nominal 60 Hz.
assume adl=1
org 040000h
jp start
align 64
db "MOS",0,1
start:
 push ix
 push iy
 ld a,8
 rst.lil 08h
 ld (sysvars),ix
 ld hl,key_callback
 ld c,0
 ld a,1dh
 rst.lil 08h
 ld c,10h
 ld a,40h
 rst.lil 08h
 ld hl,mode_query
 ld bc,3
 rst.lil 18h
 ld de,360
 call deadline
mode_wait:
 ld ix,(sysvars)
 bit 4,(ix+4)
 jr nz,mode_ready
 call elapsed
 jr c,mode_wait
 jp failed
mode_ready:
 ld a,(ix+27h)
 cp EXPECT_MODE
 jp nz,failed
 ld hl,chart
 ld bc,chart_end-chart
 rst.lil 18h
 ; Query is an untimed fence only, before warm-up and all measurements.
 ld c,4
 ld a,40h
 rst.lil 08h
 ld hl,pixel_query
 ld bc,7
 rst.lil 18h
 ld de,360
 call deadline
fence_wait:
 ld ix,(sysvars)
 bit 2,(ix+4)
 jr nz,fence_ready
 call elapsed
 jr c,fence_wait
 jp failed
fence_ready:
 ld hl,marker_reset
 ld bc,20
 rst.lil 18h
 ld de,600
 call wait_ticks
window_start:
 ld a,1
 ld (marker+13),a
 call send_marker
 ld de,1200
 call wait_ticks
 ld a,2
 ld (marker+13),a
 call send_marker
 ld a,(marker+14)
 inc a
 ld (marker+14),a
 cp 3
 jr c,window_start
 ; Nothing below this point changes the displayed image until Escape exits.
idle:
 halt
 ld a,(escape)
 or a
 jr z,idle
 ld hl,0
 jr finish
failed:
 ld hl,1
finish:
 push hl
 ld hl,0
 ld c,0
 ld a,1dh
 rst.lil 08h
 pop hl
 pop iy
 pop ix
 ret
send_marker:
 ld hl,marker
 ld bc,20
 rst.lil 18h
 ret
deadline:
 ld ix,(sysvars)
 ld hl,(ix+0)
 add hl,de
 ld (due),hl
 ret
elapsed:
 ld ix,(sysvars)
 ld hl,(ix+0)
 ld de,(due)
 or a
 sbc hl,de
 ret
wait_ticks:
 call deadline
wait_loop:
 halt
 call elapsed
 jr c,wait_loop
 ret
key_callback:
 push af
 push hl
 ld hl,3
 add hl,de
 ld a,(hl)
 or a
 jr z,key_return
 ld a,(de)
 cp 27
 jr nz,key_return
 ld a,1
 ld (escape),a
key_return:
 pop hl
 pop af
 ret
sysvars: dl 0
due: dl 0
escape: db 0
mode_query: db 23,0,134
pixel_query: db 23,0,132,0,0,0,0
marker_reset: db 23,0,160,255,255,0,12,0,"B009",1,0,0,0,0,0,0,0
include "chart.inc"
