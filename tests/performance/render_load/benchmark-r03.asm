; render-load-r03: one application for both VDP endpoints. ADL fields are 24-bit.
; No mode/routing changes, UART access or per-frame disk I/O. PRT1 saturates.
assume adl=1
org 040000h
jp start
align 64
db "MOS",0,1
PLAN: equ 042000h
PAYLOAD: equ 070000h
RESULT: equ 043000h
PACKED: equ 080000h
FILTERED: equ 090000h
; Module-safe Agon user RAM ends at0x0B0000. Records occupy0x044000
; through0x06FFF7 (15,018 records), then0x080000 through0x0AFFFF
; (16,384 records). The second region reuses PACKED/FILTERED only AFTER
; a whole case is restored atPAYLOAD, and is saved BEFORE the next preload.
FRAMES: equ 044000h
SECOND_FRAMES: equ 080000h
FIRST_CAPACITY: equ 15018
RECORD_CAPACITY: equ 31402
start:
 push ix
 push iy
 ld hl,plan_name
 ld de,PLAN
 ld bc,256
 ld a,1
 rst.lil 08h
 or a
 jp nz,load_error
 ld hl,PLAN
 ld de,plan_magic
 ld b,4
check_magic:
 ld a,(de)
 cp (hl)
 jp nz,load_error
 inc hl
 inc de
 djnz check_magic
 ld a,1
 ld (plan_valid),a
 ; Never overwrite checkpointed evidence if recovery reboots the same startup.
 ; A fresh host run supplies a fresh directory; an existing result returns to
 ; CLI without touching that file or its earlier failure receipt.
 ld hl,PLAN+107
 ld c,1
 ld a,0ah
 rst.lil 08h
 or a
 jr z,result_absent
 ld c,a
 ld a,0bh
 rst.lil 08h
 ld a,6
 ld (exit_status),a
 ld hl,msg_existing
 ld bc,0
 xor a
 rst.lil 18h
 jp done
result_absent:
 ld a,8
 rst.lil 08h
 ld (sysvars),ix
 ld c,0
 ld hl,key_callback
 ld a,1dh
 rst.lil 08h
 ld a,1
 ld (callback_installed),a
 ; PRT1 must be unused and on system clock. Do not alter the source selector.
 in0 a,(83h)
 and 7fh
 jp nz,timer_error
 in0 a,(92h)
 and 0ch
 jp nz,timer_error
 ld a,1
 ld (timer_owned),a
 ld a,255
 out0 (84h),a
 out0 (85h),a
 ; Verify observed mode and geometry after an ordinary mode query.
 ld c,10h
 ld a,40h
 rst.lil 08h
 ld hl,mode_query
 ld bc,3
 rst.lil 18h
 call timer_begin
mode_wait:
 ld ix,(sysvars)
 bit 4,(ix+4)
 jr nz,mode_ready
 call timer_read
 jr nz,mode_wait
 jp mode_error
mode_ready:
 ld a,(PLAN+235)
 cp (ix+27h)
 jp nz,mode_error
 ld a,(PLAN+236)
 cp (ix+0fh)
 jp nz,mode_error
 ld a,(PLAN+237)
 cp (ix+10h)
 jp nz,mode_error
 ld a,(PLAN+238)
 cp (ix+11h)
 jp nz,mode_error
 ld a,(PLAN+239)
 cp (ix+12h)
 jp nz,mode_error
 ld a,(PLAN+240)
 cp (ix+15h)
 jp nz,mode_error
 call timer_begin
 call timer_read
 ld a,l
 ld (header+20),a
 ld a,h
 ld (header+21),a
 call timer_stop
 ; Calibrate PRT against 60 raw MOS units (~0.5 s) outside every case.
 call raw_clock
 ld (calib_start),hl
 call timer_begin
calib_wait:
 call raw_clock
 ld de,(calib_start)
 or a
 sbc hl,de
 ld (calib_raw),hl
 ld de,60
 or a
 sbc hl,de
 jr nc,calib_done
 call timer_read
 jp z,timer_error
 jr calib_wait
calib_done:
 call timer_read
 ld a,l
 ld (header+100),a
 ld a,h
 ld (header+101),a
 ld hl,(calib_raw)
 ld (header+102),hl
 call timer_stop
 ld hl,PLAN+11
 ld c,1
 ld a,0ah
 rst.lil 08h
 or a
 jp z,load_error
 ld (input_handle),a
 ; Read the stream header and assets before cases. Host verifies entire file hash.
 ld hl,PAYLOAD
 ld de,13
 call read_block
 jp nz,io_error
 ld a,(PAYLOAD+2)
 cp 'X'
 jr z,stream_packed
 cp 'D'
 jp nz,load_error
 xor a
 jr stream_kind_ready
stream_packed:
 ld a,1
stream_kind_ready:
 ld (packed_stream),a
 ld a,(PAYLOAD+4)
 ld hl,PLAN+235
 cp (hl)
 jp nz,mode_error
 ld hl,0
 ld a,(PAYLOAD+11)
 ld l,a
 ld a,(PAYLOAD+12)
 ld h,a
 ld (decoded_len),hl
 ex de,hl
 ld hl,PAYLOAD
 ld a,(packed_stream)
 or a
 jr z,read_assets_raw
 call read_packed
 jr assets_ready
read_assets_raw:
 call read_block
assets_ready:
 jp nz,io_error
 ld bc,(decoded_len)
 ld hl,PAYLOAD
 rst.lil 18h
 ; Persist the build identity and observed geometry in a fixed result header.
 ld hl,PLAN+235
 ld de,header+5
 ld bc,6
 ldir
 ld hl,PLAN+4
 ld de,header+12
 ld bc,3
 ldir
 call raw_clock
 ld (header+16),hl
 ld hl,PLAN+107
 ld de,header
 ld bc,128
 ld a,2
 rst.lil 08h
 or a
 jp nz,io_error
 call timer_begin
 xor a
 call send_marker
 call fence_only
 jp nz,fence_error
case_next:
 ld hl,length_word
 ld de,2
 call read_block
 jp nz,io_error
 ld hl,0
 ld a,(length_word)
 ld l,a
 ld a,(length_word+1)
 ld h,a
 ld a,h
 or l
 jp z,done
 ld (decoded_len),hl
 ex de,hl
 ld hl,PAYLOAD
 ld a,(packed_stream)
 or a
 jr z,read_case_raw
 ld hl,FILTERED
 ex de,hl
 ld bc,78
 or a
 sbc hl,bc
 jp c,io_error
 ex de,hl
 ld a,6
 ld (header+105),a
 call read_packed
 jp nz,io_error
 ld a,7
 ld (header+105),a
 call unfilter_case
 jr case_loaded
read_case_raw:
 call read_block
case_loaded:
 jp nz,io_error
 ; case ID selection, preserving the frozen payload bytes.
 ld hl,0
 ld a,(PAYLOAD)
 ld l,a
 ld a,(PAYLOAD+1)
 ld h,a
 ld (case_id),hl
 ld de,0
 ld a,(PLAN+7)
 ld e,a
 ld a,(PLAN+8)
 ld d,a
 or a
 sbc hl,de
 jp c,case_next
 ld hl,(case_id)
 ld de,0
 ld a,(PLAN+9)
 ld e,a
 ld a,(PLAN+10)
 ld d,a
 or a
 sbc hl,de
 jp nc,case_next
 ld a,(PAYLOAD+2)
 ld (paced),a
 ld a,(PAYLOAD+3)
 ld hl,PLAN+241
 bit 0,(hl)
 jr z,timing_selection_ready
 and 0feh
timing_selection_ready:
 ld (flags),a
 ld hl,0
 ld (submit_ticks),hl
 ld (complete_ticks),hl
 ld (total_ticks),hl
 ld hl,0
 ld a,(PAYLOAD+4)
 ld l,a
 ld a,(PAYLOAD+5)
 ld h,a
 ld (setup_len),hl
 ld bc,(setup_len)
 ld hl,PAYLOAD+6
 rst.lil 18h
 ld de,(setup_len)
 ld hl,PAYLOAD+6
 add hl,de
 ld (frame_ptr),hl
 ld (frames_begin),hl
 call show_label
 xor a
 ld (frame_index),a
 ; Eight warm-up frames including the same completion fence, outside the window.
warm_loop:
 call execute_frame
 jp nz,fence_error
 ld a,(frame_index)
 inc a
 ld (frame_index),a
 cp 8
 jr nz,warm_loop
 ; Clear case result, copy header, then open P4 window with identical carrier bytes.
 ld hl,RESULT
 ld (hl),0
 ld de,RESULT+1
 ld bc,23
 ldir
 ld hl,case_magic
 ld de,RESULT
 ld bc,4
 ldir
 ld hl,(case_id)
 ld a,l
 ld (RESULT+4),a
 ld a,h
 ld (RESULT+5),a
 ld a,(paced)
 ld (RESULT+6),a
 ld a,(flags)
 ld (RESULT+7),a
 call timer_begin
 ld a,1
 call send_marker
 call fence_only
 jp nz,fence_error
 call raw_clock
 ld (RESULT+8),hl
 ld (deadline),hl
 ld hl,FRAMES
 ld (result_ptr),hl
 ld hl,0
 ld (frame_count),hl
 ld (sample_count),hl
 xor a
 ld (samples_truncated),a
measure_loop:
 call raw_clock
 ld (frame_start),hl
 call timer_begin
 call send_frame
 ld a,(flags)
 bit 0,a
 jr z,no_submit_probe
 call timer_read
 ld (submit_ticks),hl
no_submit_probe:
 call fence_only
 ld a,0
 jr z,fence_ok
 inc a
fence_ok:
 ld (frame_status),a
 ld a,(flags)
 bit 0,a
 jr z,no_complete_probe
 call timer_read
 ld (complete_ticks),hl
 jr nz,no_complete_probe
 ld a,2
 ld (frame_status),a
no_complete_probe:
 ld a,(paced)
 or a
 jr z,pacing_done
 ld hl,(deadline)
 inc hl
 inc hl
 ld (deadline),hl
pacing_wait:
 push hl
 call raw_clock
 ex de,hl
 pop hl
 push hl
 ex de,hl
 or a
 sbc hl,de
 pop hl
 jr nc,pacing_done
 push hl
 call timer_read
 pop hl
 jr nz,pacing_wait
 ld a,2
 ld (frame_status),a
pacing_done:
 ld a,(flags)
 bit 0,a
 jr z,no_total_probe
 call timer_read
 ld (total_ticks),hl
 jr nz,no_total_probe
 ld a,2
 ld (frame_status),a
no_total_probe:
 call timer_stop
 call raw_clock
 ld de,(frame_start)
 or a
 sbc hl,de
 ld (raw_delta),hl
 ld hl,(sample_count)
 ld de,RECORD_CAPACITY
 or a
 sbc hl,de
 jr nz,record_frame
 ld a,1
 ld (samples_truncated),a
 jr frame_recorded
record_frame:
 ld ix,(result_ptr)
 ld a,(frame_index)
 ld (ix+0),a
 ld a,(frame_status)
 ld (ix+1),a
 ld hl,(submit_ticks)
 ld (ix+2),l
 ld (ix+3),h
 ld hl,(complete_ticks)
 ld (ix+4),l
 ld (ix+5),h
 ld hl,(total_ticks)
 ld (ix+6),l
 ld (ix+7),h
 ld hl,(raw_delta)
 ld (ix+8),hl
 ld hl,(result_ptr)
 ld de,12
 add hl,de
 ld (result_ptr),hl
 ld hl,(sample_count)
 inc hl
 ld (sample_count),hl
 ld de,FIRST_CAPACITY
 or a
 sbc hl,de
 jr nz,frame_recorded
 ld hl,SECOND_FRAMES
 ld (result_ptr),hl
frame_recorded:
 ld hl,(frame_count)
 inc hl
 ld (frame_count),hl
 ld a,(frame_index)
 inc a
 cp 40
 jr nz,frame_cycle_ready
 xor a
 ld hl,(frames_begin)
 ld (frame_ptr),hl
frame_cycle_ready:
 ld (frame_index),a
 ld a,(frame_status)
 or a
 jr z,frame_valid
 ld (RESULT+22),a
 ld a,1
 ld (pending_key),a
frame_valid:
 ld a,(pending_key)
 or a
 jp z,measure_loop
 ld (RESULT+20),a
 xor a
 ld (pending_key),a
 call raw_clock
 ld (RESULT+11),hl
 ld hl,(frame_count)
 ld (RESULT+14),hl
 ld hl,(sample_count)
 ld (RESULT+17),hl
 ld a,(samples_truncated)
 ld (RESULT+21),a
 call timer_begin
 ld a,2
 call send_marker
 call fence_only
 jp nz,fence_error
 ; Durable per-case checkpoint outside all measured frames.
 ld hl,PLAN+107
 ld c,32h
 ld a,0ah
 rst.lil 08h
 or a
 jp z,io_error
 ld c,a
 ld (output_handle),a
 ld hl,RESULT
 ld de,24
 ld a,1bh
 rst.lil 08h
 ld hl,24
 or a
 sbc hl,de
 push af
 ld a,(output_handle)
 ld c,a
 ld hl,(sample_count)
 ld de,FIRST_CAPACITY
 or a
 sbc hl,de
 jr nc,save_two_regions
 ld de,(sample_count)
 ld hl,FRAMES
 call write_samples
 jr save_samples_checked
save_two_regions:
 ld (remaining_samples),hl
 ld hl,FRAMES
 ld de,FIRST_CAPACITY
 call write_samples
 jr nz,save_samples_checked
 ld hl,SECOND_FRAMES
 ld de,(remaining_samples)
 call write_samples
save_samples_checked:
 jr z,samples_written
 pop af
 jp io_error
samples_written:
 ld a,(output_handle)
 ld c,a
 ld a,0bh
 rst.lil 08h
 pop af
 jp nz,io_error
 ld a,(RESULT+22)
 or a
 jp nz,fence_error
 ld a,(RESULT+20)
 cp 2
 jp z,done
 jp case_next
write_samples:
 ld a,d
 or e
 ret z
 push hl
 ld hl,0
 ld b,12
sample_byte_count:
 add hl,de
 djnz sample_byte_count
 ld (sample_bytes),hl
 ex de,hl
 pop hl
 ld a,(output_handle)
 ld c,a
 ld a,1bh
 rst.lil 08h
 ld hl,(sample_bytes)
 or a
 sbc hl,de
 ret
send_frame:
 ld hl,(frame_ptr)
 ld bc,0
 ld c,(hl)
 inc hl
 ld b,(hl)
 inc hl
 push hl
 push bc
 add hl,bc
 ld (frame_ptr),hl
 pop bc
 pop hl
 ; The frozen no-marker static control has zero drawing bytes. RST18 with
 ; BC=0 means a NUL-terminated string, not counted zero-byte output. Skip it
 ; explicitly so the final empty template cannot read beyond its payload.
 ld a,b
 or c
 ret z
 rst.lil 18h
 ret
execute_frame:
 call timer_begin
 call send_frame
 call fence_only
 ret
fence_only:
 ld c,4
 ld a,40h
 rst.lil 08h
 ld hl,pixel_query
 ld bc,7
 rst.lil 18h
fence_wait:
 ld ix,(sysvars)
 bit 2,(ix+4)
 jr nz,fence_received
 call timer_read
 jr nz,fence_wait
 ld a,1
 or a
 ret
fence_received:
 xor a
 ret
raw_clock:
 ld ix,(sysvars)
 ld hl,(ix+0)
 ret
send_marker:
 ld (marker+13),a
 ld hl,(case_id)
 ld a,l
 ld (marker+14),a
 ld a,h
 ld (marker+15),a
 ld a,(flags)
 ld (marker+16),a
 ld hl,PLAN+4
 ld de,marker+17
 ld bc,3
 ldir
 ld hl,marker
 ld bc,20
 rst.lil 18h
 ret
read_block:
 ld (last_read),de
 ld a,(input_handle)
 ld c,a
 ld a,1ah
 rst.lil 08h
 push hl
 ld hl,(last_read)
 or a
 sbc hl,de
 pop hl
 ret
; Packing reduces untimed SD preparation only. Each complete case is restored
; byte-for-byte before any VDU setup/warm-up/window/timer interval. B9X1 uses
; byte-run tokens over column/delta-filtered equal-length frames; B9D1 stays
; supported for independently qualified pilot data. Both buffers are <=64 KiB.
read_packed:
 ld (unpack_dest),hl
 push hl
 add hl,de
 ld (unpack_end),hl
 pop hl
 ld hl,length_word
 ld de,2
 call read_block
 ret nz
 ld de,0
 ld a,(length_word)
 ld e,a
 ld a,(length_word+1)
 ld d,a
 ld a,d
 or e
 jr z,unpack_bad
 ld hl,PACKED
 push hl
 add hl,de
 ld (packed_end),hl
 pop hl
 call read_block
 ret nz
 ld hl,PACKED
 ld de,(unpack_dest)
unpack_next:
 push hl
 ld bc,(packed_end)
 or a
 sbc hl,bc
 pop hl
 jr z,unpack_finished
 jp nc,unpack_bad
 ld a,(hl)
 inc hl
 ld bc,0
 bit 7,a
 jr nz,unpack_repeat
 ld c,a
 inc bc
 call unpack_input_bound
 jr c,unpack_bad
 call unpack_output_bound
 jr c,unpack_bad
 ldir
 jr unpack_next
unpack_repeat:
 and 127
 ld c,a
 inc bc
 inc bc
 inc bc
 call unpack_output_bound
 jr c,unpack_bad
 push bc
 ld bc,1
 call unpack_input_bound
 pop bc
 jr c,unpack_bad
 ld a,(hl)
 inc hl
unpack_repeat_loop:
 ld (de),a
 inc de
 dec bc
 push af
 ld a,b
 or c
 jr z,unpack_repeat_done
 pop af
 jr unpack_repeat_loop
unpack_repeat_done:
 pop af
 jr unpack_next
unpack_finished:
 ld hl,(unpack_end)
 or a
 sbc hl,de
 ret
unpack_bad:
 ld a,1
 or a
 ret
unpack_input_bound:
 push hl
 push de
 ex de,hl
 ld hl,(packed_end)
 or a
 sbc hl,de
 or a
 sbc hl,bc
 pop de
 pop hl
 ret
unpack_output_bound:
 push hl
 ld hl,(unpack_end)
 or a
 sbc hl,de
 or a
 sbc hl,bc
 pop hl
 ret
unfilter_case:
 ld hl,(decoded_len)
 ld (header+106),hl
 ld hl,(unpack_end)
 ld (header+109),hl
 ld hl,0
 ld a,(FILTERED+4)
 ld l,a
 ld a,(FILTERED+5)
 ld h,a
 ld bc,6
 add hl,bc
 ld bc,(decoded_len)
 ; The prefix must leave at least two bytes for a frame length.
 push hl
 inc hl
 inc hl
 or a
 sbc hl,bc
 pop hl
 ld a,8
 ld (header+105),a
 jr nc,unpack_bad
 push hl
 pop bc
 ld hl,FILTERED
 ld de,PAYLOAD
 ldir
 ld (column_dest),de
 ld bc,0
 ld c,(hl)
 inc hl
 ld b,(hl)
 inc hl
 ld (frame_length),bc
 push hl
 inc bc
 inc bc
 ld (frame_stride),bc
 push de
 pop ix
 ld b,40
unfilter_lengths:
 ld de,(frame_length)
 ld (ix+0),e
 ld (ix+1),d
 ld de,(frame_stride)
 add ix,de
 djnz unfilter_lengths
 push ix
 pop hl
 ld de,PAYLOAD
 or a
 sbc hl,de
 ld de,(decoded_len)
 or a
 sbc hl,de
 pop hl
 ld a,9
 ld (header+105),a
 jp nz,unpack_bad
 ld bc,(frame_length)
 ld a,b
 or c
 ; Empty drawing templates are valid controls. Their forty length words
 ; have already been restored; there are no delta columns to expand.
 jr z,unfilter_finished
unfilter_column:
 push bc
 ld ix,(column_dest)
 inc ix
 inc ix
 ld de,(frame_stride)
 ld b,40
 xor a
unfilter_frame:
 add a,(hl)
 inc hl
 ld (ix+0),a
 add ix,de
 djnz unfilter_frame
 ld ix,(column_dest)
 inc ix
 ld (column_dest),ix
 pop bc
 dec bc
 ld a,b
 or c
 jr nz,unfilter_column
unfilter_finished:
 ld de,(unpack_end)
 ld (header+112),hl
 or a
 sbc hl,de
 ret
timer_begin:
 xor a
 out0 (83h),a
 ld a,0fh
 out0 (83h),a
 ret
timer_read:
 ld hl,0
 in0 a,(84h)
 ld l,a
 in0 a,(85h)
 ld h,a
 ; Z means saturation (remaining=0). Preserve Z through elapsed conversion.
 ld a,h
 or l
 push af
 ld de,65535
 ex de,hl
 or a
 sbc hl,de
 pop af
 ret
timer_stop:
 xor a
 out0 (83h),a
 ret
mode_error:
 ld a,1
 ld hl,msg_mode
 jr error
load_error:
 ld a,2
 ld hl,msg_load
 jr error
timer_error:
 ld a,3
 ld hl,msg_timer
 jr error
fence_error:
 ld a,4
 ld hl,msg_fence
 jr error
io_error:
 ld a,5
 ld hl,msg_io
error:
 ld (exit_status),a
 ld bc,0
 xor a
 rst.lil 18h
 ld a,(plan_valid)
 or a
 jp z,done
 ld a,(exit_status)
 ; Save a separate failure receipt; never replace completed case checkpoints.
 ld (header+19),a
 ld hl,PLAN+107
 ld b,128
find_failure_name:
 ld a,(hl)
 or a
 jr z,failure_name_ready
 inc hl
 djnz find_failure_name
 jp done
failure_name_ready:
 ld de,-11
 add hl,de
 push hl
 ex de,hl
 ld hl,failure_name
 ld bc,12
 ldir
 pop hl
 ld de,header
 ld bc,128
 ld a,2
 rst.lil 08h
done:
 ld a,(callback_installed)
 or a
 jr z,callback_cleared
 ld hl,0
 ld c,0
 ld a,1dh
 rst.lil 08h
callback_cleared:
 ld a,(timer_owned)
 or a
 call nz,timer_stop
 ld a,(input_handle)
 or a
 jr z,no_input
 ld c,a
 ld a,0bh
 rst.lil 08h
no_input:
 pop iy
 pop ix
 ld hl,0
 ld a,(exit_status)
 ld l,a
 ret
failure_name: db "failure.bin",0
plan_name: db "plan.bin",0
plan_magic: db "B9P1"
case_magic: db "B9C2"
mode_query: db 23,0,86h
pixel_query: db 23,0,84h,0,0,0,0
marker: db 23,0,160,255,255,0,12,0,"B009",1,0,0,0,0,0,0,0
msg_mode: db "BENCH-009 wrong mode",13,10,0
msg_load: db "BENCH-009 load failed",13,10,0
msg_timer: db "BENCH-009 PRT1 unavailable",13,10,0
msg_fence: db "BENCH-009 fence failed",13,10,0
msg_io: db "BENCH-009 SD failed",13,10,0
msg_existing: db "BENCH-009 result exists; retained",13,10,0
header: db "B9R2",2
 ds 17
 include "identity.inc"
calib_start: dl 0
calib_raw: dl 0
sysvars: dl 0
case_id: dl 0
setup_len: dl 0
last_read: dl 0
frame_ptr: dl 0
result_ptr: dl 0
submit_ticks: dl 0
complete_ticks: dl 0
total_ticks: dl 0
raw_delta: dl 0
frame_start: dl 0
deadline: dl 0
length_word: dw 0
decoded_len: dl 0
packed_end: dl 0
unpack_dest: dl 0
unpack_end: dl 0
column_dest: dl 0
frame_length: dl 0
frame_stride: dl 0
packed_stream: db 0
frame_index: db 0
paced: db 0
flags: db 0
frame_status: db 0
input_handle: db 0
output_handle: db 0
exit_status: db 0

frames_begin: dl 0
frame_count: dl 0
sample_count: dl 0
sample_bytes: dl 0
samples_truncated: db 0
pending_key: db 0
held_key: db 0
callback_installed: db 0
plan_valid: db 0
timer_owned: db 0

; Public MOS keyboard callback: DE points to ASCII, modifiers, virtual key,
; down/up. Latch the press so a quick scripted press/release is never missed.
; No I/O in this ISR. A held key advances once; Escape takes priority.
key_callback:
 push af
 push hl
 ld hl,3
 add hl,de
 ld a,(hl)
 or a
 jr nz,key_down
 xor a
 ld (held_key),a
 jr key_return
key_down:
 ld a,(de)
 cp 32
 jr z,key_relevant
 cp 27
 jr nz,key_return
key_relevant:
 ld hl,held_key
 cp (hl)
 jr z,key_return
 ld (hl),a
 cp 27
 jr nz,key_next
 ld a,2
 ld (pending_key),a
 jr key_return
key_next:
 ld a,(pending_key)
 cp 2
 jr z,key_return
 ld a,1
 ld (pending_key),a
key_return:
 pop hl
 pop af
 ret
show_label:
 ld hl,label_position
 ld bc,4
 rst.lil 18h
 ld hl,(case_id)
 ld de,0
 add hl,hl
 ld de,(case_id)
 add hl,de
 ld de,label_table
 add hl,de
 ld hl,(hl)
 ld bc,0
 xor a
 rst.lil 18h
 ld hl,0
 ld a,(PLAN+236)
 ld l,a
 ld a,(PLAN+237)
 ld h,a
 srl h
 rr l
 srl h
 rr l
 srl h
 rr l
 dec hl
 ld a,l
 ld (text_viewport+3),a
 ld hl,0
 ld a,(PLAN+238)
 ld l,a
 ld a,(PLAN+239)
 ld h,a
 srl h
 rr l
 srl h
 rr l
 srl h
 rr l
 dec hl
 ld a,l
 ld (text_viewport+2),a
 ld hl,text_viewport
 ld bc,5
 rst.lil 18h
 ret
label_position: db 26,31,4,0
text_viewport: db 28,0,0,0,1
 include "labels.inc"

remaining_samples: dl 0
