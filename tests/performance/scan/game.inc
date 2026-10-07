; SCAN01-T09 adapter: current repaired Nurples, unchanged assets/map/drawing.
; Simulation clock advances by two raw ticks/update; MOS/PRT clocks stay real.
; Private keys replace only the map consumed by player_input, AFTER MOS polling.
sc_case: equ 9
sc_prepare:
    call telemetry_init
    call runtime_process_init
    ld hl,0
    ld (timestamp_now),hl
    ld (timestamp_old),hl
    ld (timestamp_chg),hl
    call game_init
    ld hl,(game_state)
    ld de,game_playing
    or a
    sbc hl,de
    ld a,h
    or l
    ret
sc_work:
    call sc_script
    call timestamp_tick
    call do_game
    call telemetry_tick
    ret
sc_wait:
    jp vdu_vblank
sc_extra_flags:
    ld hl,(game_state)
    ld de,game_playing
    or a
    sbc hl,de
    jp nz,sc_game_fault
    ld a,(game_exit_requested)
    or a
    jp nz,sc_game_fault
    ld a,(vdu_timing_fault_flags)
    ld b,a
    ld a,(timer_fault_flags)
    or b
    ld b,a
    ld a,(game_fault_flags)
    or b
    ld b,a
    ld a,(sprite_fault_flags)
    or b
    ld b,a
    ld a,(tile_fault_flags)
    or b
    ret z
sc_game_fault:
    ld a,(sc_flags)
    or 8
    ld (sc_flags),a
    ret
sc_cleanup:
    jp original_main_end
sc_sim_tick:
    ld hl,(timestamp_now)
    ld (timestamp_old),hl
    inc hl
    inc hl
    ld (timestamp_now),hl
    ld hl,2
    ld (timestamp_chg),hl
    ret
sc_script:
    ld hl,sc_keys
    ld de,sc_keys+1
    ld bc,15
    ld (hl),0
    ldir
    ; Each 256-update phase: neutral64, right/fire64, left/fire64, neutral64.
    ; Horizontal excursion is clamped by original player movement rules.
    ld a,(sc_update)
    rlca
    rlca
    and 3
    ld (sc_phase),a
    cp 1
    jp z,sc_right
    cp 2
    ret nz
    ld a,2
    ld (sc_keys+3),a
    jp sc_fire
sc_right:
    ld a,2
    ld (sc_keys+15),a
sc_fire:
    ld a,4
    ld (sc_keys+12),a
    ret
sc_force_software:
    push af
    push bc
    push hl
    ld hl,sc_sw_packet
    ld bc,7
    rst.lil 18h
    pop hl
    pop bc
    pop af
    ret
sc_sw_packet: db 23,27,18,0,23,27,20
sc_keys: ds 16
sc_checkpoint:
    ; Compact 16-bit hash of player position/velocity + simulation/map/RNG.
    ; Hashing is outside each interval, in measured whole-window elapsed.
    ld de,0
    ; Compact checkpoint excludes scratch bytes and pointers in free records.
    ; Hash player velocity, live sprite positions, map progress and RNG; retain
    ; independent live actor/projectile counts below. Not a proof of all RAM.
    ld hl,player_begin+sprite_x
    ld bc,12
    call sc_hash
    ld hl,timestamp_now
    ld bc,9
    call sc_hash
    ld hl,tiles_row_defs
    ld bc,3
    call sc_hash
    ld hl,r_seed
    ld bc,1
    call sc_hash
    ld hl,seed1
    ld bc,6
    call sc_hash
    ld ix,table_base
    ld b,table_num_records
sc_hash_actor:
    bit sprite_alive,(ix+sprite_collisions)
    jp z,sc_hash_actor_next
    push bc
    lea hl,ix+sprite_x
    ld bc,6
    call sc_hash
    pop bc
sc_hash_actor_next:
    push de
    ld de,table_record_size
    add ix,de
    pop de
    djnz sc_hash_actor
    ld (sc_state),de
    ld a,(tiles_row)
    ld (sc_maprow),a
    ld a,(r_seed)
    ld (sc_rng),a
    ld ix,enemy_sprites_begin
    ld b,[enemy_sprites_end-enemy_sprites_begin]/table_record_size
    call sc_count_actors
    ld (sc_actors),a
    ld ix,player_lasers_begin
    ld b,player_lasers_max
    call sc_count_actors
    ld (sc_projectiles),a
    ret
sc_hash:
    ; Fletcher-like rotating XOR is a checkpoint, not an integrity digest.
    ld a,d
    rlca
    xor e
    ld d,e
    xor (hl)
    ld e,a
    inc hl
    dec bc
    ld a,b
    or c
    jp nz,sc_hash
    ret
sc_count_actors:
    ld c,0
sc_count_loop:
    bit sprite_alive,(ix+sprite_collisions)
    jp z,sc_count_next
    inc c
sc_count_next:
    ld de,table_record_size
    add ix,de
    djnz sc_count_loop
    ld a,c
    ret
include "runner.inc"
