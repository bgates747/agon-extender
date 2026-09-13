# BENCH-001 telemetry experiment contract

Provisional implementation contract, recorded before code changes on 2026-09-13.
Execution checklist and open work remain in ../BENCH-001.md.

## Ownership and scheduling

Rally calls the existing EMOS gateway (RST 08h API 51h) with namespace `ext`,
provider `telemetry`. The resident Core service copies complete application
snapshots into Core-owned RAM; it retains no application pointer. The existing
EMOS UART1/VBlank vector owners advance bounded asynchronous transmission. No
filesystem operation, dynamic allocation, blocking UART wait or foreground API
call runs in an ISR. This is the TSR role inside resident EMOS, not a separate
RAM loader or a claim of background SD access.

Application operations: one-byte 0 opens, byte 1 followed by a complete snapshot
publishes, one-byte 2 closes. The current v2 snapshot is 140 bytes; historical
v1 snapshots were 84 bytes. All gateway structures/payloads must lie entirely
in ordinary application RAM. Legacy mode, healthy admitted Extender keyboard
transport and an enabled caller are required. Busy transmission returns BUSY;
Rally drops that publication rather than waiting or building a backlog. App
entry/exit and keyboard transport teardown invalidate service admission.
An already queued packet uses Core RAM and may drain after application exit.

The shared UART owner serializes packets: a foreground writer cannot interleave
with a resident packet, nor can resident publication start during a foreground
transaction. UART interrupt work is bounded; CTS blockage disables TX-empty
interrupt demand until a subsequent bounded VBlank kick. A stalled partial
packet faults the owned link rather than appending a fresh packet to its tail.
RX/physical keyboard service keeps priority. Existing receive vectors and
register preservation remain authoritative.

## Private Legacy transport and latest sample

EMOS -> P4 envelope: bytes 23, 0, 0xF5, snapshot length, then the snapshot below
(current v2 length 140; historical v1 length 84). 0xF6 SD and
0xF7 console control remain unchanged. The command is private to the admitted
Extender Legacy parser; it is never sent to the onboard VDP. P4 consumes whole
length-framed records, validates magic/version/length/CRC, and replaces a single
latest-snapshot slot. Bad records cannot partially replace a valid sample.

GET /telemetry/latest returns JSON: online, age_ms, received and payload (hex).
The P4's monotonic receipt age must be below 500 ms to be online. The host checks
run identity, advancing frame/time, receipt age and HTTP observation time before
controlling the car. Duplicate data does not establish fresh game progress.
No network callback reads UART, MOS RAM or the SD filesystem.

## Historical snapshot v1

All multibyte fields are explicitly little-endian, independent of C ABI width.
Signed values use two's complement. The total is 84 bytes.

| Offset | Bytes | Meaning |
| --- | --- | --- |
| 0 | 2 | ASCII RT |
| 2 | 1 | Version 1 |
| 3 | 1 | Flags: running, demo, corner assistance, engine audio (bits 0..3) |
| 4 | 4 | Run identity |
| 8 | 4 | Rendered-update sequence |
| 12 | 4 | MOS raw clock (nominal 120 ticks/s) |
| 16 | 4 | Distance around lap, hundredths of world units |
| 20 | 4 | Speed, current game's integer units |
| 24 | 4 | Lateral displacement, signed Q8 world units |
| 28 | 4 | Lateral velocity, signed Q8 world units/s |
| 32 | 2 | Signed steering in 256-circle units |
| 34 | 2 | Grip percent |
| 36 | 4 | Track length in whole world units |
| 40 | 4 | Local signed tangent cross product, Q12 over 64 world units |
| 44 | 4 | Maximum absolute bend over look-ahead |
| 48 | 1 | Surface: road 0, kerb 1, grass 2 |
| 49 | 1 | Track: oval 0, Fuji 1 |
| 50 | 1 | Game-observed held inputs: left/right/up/down bits 0..3 |
| 51 | 1 | Reserved zero |
| 52 | 4 | Total physics updates in this run |
| 56 | 16 | Eight signed i16 bend samples, 64-world-unit spacing from current position |
| 72 | 2 | Road half width, Q8 world units |
| 74 | 2 | Outer kerb half width, Q8 world units |
| 76 | 2 | Elapsed raw clock ticks at this update, saturating |
| 78 | 1 | Steering step per rendered update (3) |
| 79 | 1 | Reserved zero |
| 80 | 4 | Ordinary reflected CRC32 of bytes 0..79 |

Rally remains in manual race mode with normal grip/surface physics. The host
controller consumes road geometry and motion, computes its own steering/speed
intent, and actuates only ordinary remote key transitions. No game-side demo
controller, position write, steering setter or teleport is used for acceptance.

## Engine sound

Use stock VDP enhanced audio channel 0, sine waveform 3. Frequency increases
monotonically with actual car speed, with a restrained volume and an explicit
mute option for testing. Update frequency only when its quantized value changes;
silence the channel on ordinary exit and errors. Do not synthesize RPM/gearing.
The Author subsequently heard this tone and requested it remain unchanged.
Speakers are now muted; future attention cues use a labelled emulator beep.

## Verification scope

Prove resident transmission progresses while foreground rendering/VDP waits
continue, preserving coherent sample boundaries and existing input. Test stale
samples and physical takeover, bounded queues, CTS stalls and lifecycle reset.
Driving acceptance needs sustained lap progress through bends while remaining
mostly on road, with measured lane error and no built-in demo assistance.
A silent real-board pass precedes the final audible driving launch. Historical
passes are not new-build validation. Exact inputs and rollback accompany each
physical image; applicable human review and commit gates remain separate.

## Snapshot v2 — traffic extension contract

The selected v2 build uses a 140-byte snapshot and a 144-byte UART envelope.
The gateway publish input is 141 bytes including operation 1. Version byte is
2; offsets 0..79 retain v1 meanings. V1 firmware/builds remain preserved evidence;
v2 is an explicit incompatible experiment and all three endpoints change together.

| Offset | Bytes | Meaning |
| --- | --- | --- |
| 80 | 1 | Opponent count, exactly six |
| 81 | 1 | Current overlap mask, bits 0..5 |
| 82 | 1 | Individual car half width, 12 whole world units |
| 83 | 1 | Individual car half length, 16 whole world units |
| 84 | 4 | Cumulative overlap entries, counted per opponent per physics tick |
| 88 | 48 | Six records in stable traffic-array order, eight bytes each |
| 136 | 4 | Reflected CRC32 of bytes 0..135 |

Each traffic record is signed i32 longitudinal distance in hundredths of world
units, signed i16 lane centre in Q8 world units, and u16 speed in game units.
Distance uses the nearest signed lap displacement from the player's contact
station, approximately 68 world units ahead of the camera (8000/118 from the
existing projection). Negative means behind. This is an explicit conservative
arcade contact proxy, not polygon-accurate collision physics: overlap is distance
within 32 world units and lateral separation within 24 world units. Sample every
physics tick to count crossings that a slow render/HTTP observation could miss.
Do not apply bounce, slowdown, damage or position changes. The counter exposes
failed passes even though this game currently lets cars pass through each other.

The host may use all six reported cars, including those outside the drawn range;
this is telemetry-driven driving, not vision. Preserve fixed opponent identity
across lap wrap, choose an unobstructed lateral corridor, and brake if no safe
passing path is available. Actual manual steering is still three ticks per game
frame. No demo controller, state writes or opponent manipulation on hardware.

The normal physical host rejects snapshots/observation gaps at 200 ms. A
separately labelled native-emulator diagnostic uses 350 ms because that UART
model lacks TX-empty interrupt demand. That diagnostic failed driving acceptance
with grass excursions; it is not permission to relax the physical freshness
gate or claim native timing equals hardware.

Physical freshness amendment during the timed grip programme: the earlier
200 ms cutoff caused nuisance stops on a healthy rendered-update stream with
16–22 raw ticks per frame (133–183 ms) plus HTTP/polling variation. Select
300 ms for the current physical trial's receipt/progress checks, while retaining
the 120 ms active HTTP timeout, epoch/CRC/progress checks, no stale-state control,
and automatic quit. Save the last reply on any rejected observation. This
changes the earlier physical limit explicitly; it does not convert the failed
350 ms native-emulator diagnostic into a pass. Cleanup alone uses the ordinary
one-second request bound after active driving stops.

Subsequent HTTP amendment: active requests now have a200ms bound after another
healthy physical run ended on an isolated120ms timeout. The300ms observation
bound still governs control; the host checks age again after obtaining keyboard
status so a slow status reply cannot turn an expired observation into input.
Cleanup retains its separate one-second bound. Mutating keyboard requests are
never blindly retried. This supersedes the120ms request limit in the preceding
historical note, without changing the wire protocol or firmware.

Steering-rate amendment: byte78 reports1,2 or3 angle ticks per held-key rendered
update. The Author requested a physical one-then-two comparison and rejected
three as too aggressive. No payload size, offset, framing or firmware ownership
changes. The host must use the reported step in its real and forecast steering,
including parity changes when step2 clips at±21. Firmware receivers already
transport this byte without imposing the old host-only step3 restriction.

Native integration closeout: HEADLESS-CLOSEOUT.md records the current300ms
controller/game case passing on the explicit mos-agondev TEST-002 UART1
TX-interrupt model. A stationary trace isolates packet assembly from driving:
median134.260ms in the old RX-only model versus2.180ms with TX demand. IIR
priority/status is read-only and UART0/byte clocks remain unchanged. This is
host-socket assembly, not a physical baud or end-to-end latency measurement.
The final fixed drive proves coherent manual snapshots, later guest key
release and normal application exit. Old200/350ms failures remain historical
failures, physical300ms policy stays unchanged, and human review remains open.

## Attended full-game application profile

RALLY-22 R22-11 owns a separate optional full-game producer and host adapter.
It preserves the140-byte v2 framing/CRC and all mandatory reserved bytes, so
current EMOS16/P4 transport requires no change. Flags byte3 upper nibble carries
the game phase0..9; running bit0 is set only during controllable qualifying/race,
and low demo/assist/audio bits retain their meaning. INT32_MIN distance plus
zero lateral/speed denotes an absent opponent slot, including qualifying.
The old bench host rejects these absent records; `scripts/rally_race.py` owns
the explicit full-game parser, phases and active-slot filtering. Actual active
traffic retains slot order and exact Q8 lateral/route speed. Counter84 counts
real game crash starts rather than bench overlap-only observations.

This is an attended Fuji arcade attempt requested after the earlier pause,
not release of Extender video/backlog work or a renewed practice programme.
The parser retains raw wire evidence, reuses the existing bound validation and
PassingDriver, releases controls outside manual phases and on expiry/takeover.
No score writes, firmware updates or direct car-state controls are introduced.
