# Focused scrolling fixtures

Experimental SCAN-001 S05/S06 implementation of the
[nine-case contract](../../../docs/tasks/SCAN-001/S04-TEST-CONTRACT.md).
Production Nurples and the frozen render-load-r04 harness remain unchanged.

## Build and ownership

`build.py` requires explicit `--source` (nurples-repair), `--assets` (its pinned
AGNB/font directory), `--pin` (S01 source manifest), `--assembler` and fresh
`--output` paths. It checks the source snapshot, exports/patches the game in the
output directory, retains the diff, and builds all nine executables. Generated
files and game assets belong in the build archive, not Git. The build manifest
pins exact streams, binaries, tool and source hashes. S05's local receipts live
under ignored `agents/scan001/s05`; its tracked results identify the selected
build. Stock MOS/VDP and the game checkout are read-only references.

## SD and invocation

The retained S05 deployment uses the following paths. Current r02 build output
and the explicitly mapped S06 companion executables are described below.

1. T01–T08 reside at `/extender/scan-r01/t01` through `t08`.
2. T09 resides at `/test/nurples/scan-r01`, with only its own copied runtime
   assets. Every directory contains `scan.bin`, `run.cfg`, `smoke.cfg` and
   `full.cfg`. The installed `run.cfg` initially selects a 120-update smoke.
3. Results go to `/agents/extender/results/scan-r01`. A result which already
   exists is protected: the fixture refuses that invocation. Give every new
   endpoint, repetition or control a fresh output path in `run.cfg`.
4. Startup templates select `EMOS KEYINPUT extender`, the EMOS route and
   `VDU 22 20`, then load T01 **without running it**. They are templates only;
   S05 deployment leaves the existing `/autoexec.txt` unchanged. Back up and
   restore startup byte-for-byte when a later bench run installs a template.
5. After authorized mode/route preflight, `CD` to one fixture directory,
   `LOAD scan.bin`, then `RUN`. No fixture changes display mode or EMOS route.
   Escape in the ordinary MOS key map aborts; partial records are not a pass.
   Load before every run, even though the common harness resets its own state.
6. `natural.cfg` disables per-update fences for short T07/T08 controls;
   `no-timing.cfg` disables PRT reads/writes inside updates. T09 already omits
   per-update fences, so its natural control repeats that scope. Controls remain
   separate results. No renderer hooks are required by these executables.

`config()` in `build.py` creates the exact 128-byte plan; callers select an
explicit result filename. Fields: `SSC`, case u8, measured count u24, warm-up
count u24, flags u8 at10 (bit0 no fence, bit1 no PRT, bit2 window markers),
optional correlation tag u24 at11, two reserved bytes,
NUL-terminated absolute result path at16. Counts are bounded by3600/120.
The host creates the result's parent directory before invocation. Output-path
reservation is a single-foreground-owner preflight, not a claim of atomic
create-new semantics on the directory-backed emulator filesystem.

## Measurement and records

`runner.inc` reuses r04's PRT1 /256, raw MOS deadline and whole-update pixel-query
idioms. `synthetic.asm` feeds frozen 256-update command cycles. Setup streams
exceed64KiB, so MOS RST18 calls are split below its16-bit BC length limit.
T01–T08 use60 warm-up updates and600 measured updates; T09 uses120+3600.

The common24-byte row is: six u24 fields (absolute update, active, completion
boundary, total, MOS delta, compact state hash), then six u8 fields (flags,
script phase, live enemies/projectiles, live player projectiles, map rows
remaining, 8-bit RNG). Flag bits0/1/2/3 mean saturation/fence timeout/late
deadline/game fault. PRT counts are nominal72,000/s;1200 counts is one60Hz budget.
The total ends after pacing/fault sampling, before checkpoint hashing and RAM
copy. Whole-window MOS elapsed includes that tail. Neither is a physical
scanout/presented-frame measurement. T09's completion-boundary timestamp does
**not** establish renderer completion; its final drain is separate.

A128-byte header stores magic `SCANR01!`, case/row size, optional tag at10,
count at16, start/end
raw MOS clock at19/22, PRT/MOS calibration at25/28, drain counts at31, abort
at34, requested count/warm-up/flags at35/38/41 and build identity at42. File writes
are checked for short writes and the handle closed after all timing ends.
`records.py FILE [--csv OUTPUT]` validates length/order/timer ranges and produces
raw rows and budget percentages. Require expected count, no abort/faults and
matched identities/state before pairing measurements. Emulator timings are
functional evidence only.

PRT1 ownership requires disabled control0 and system-clock source; no PRT0,
interrupt, shared source selector or vector is changed. Exit stops PRT1 and
restores control0. Its write-only reload cannot be recovered from a counter
read: the unused timer retains reload65535. This is the precise restoration
limit, also present in the older harness; do not claim arbitrary timer-state
save/restore. The fixture refuses an occupied timer.

## Deterministic game adaptation

The repaired game starts directly, centered, invulnerable, joystick disabled.
Its256-row map covers3720 updates without extension. Seed0x50 and the ordinary
map/assets remain fixed. Gameplay timestamp advances by two synthetic MOS units
per update; real MOS/PRT clocks and the original bounded vblank helper are intact.
Each256-update input cycle is neutral64, right/fire64, left/fire64, neutral64.
The ordinary MOS keyboard poll remains before substitution of a private map;
this proves rendering/pacing, not delivery of physical/browser input.

Every frame attachment explicitly establishes paint0/software sprite mode.
The compact checkpoint hashes player position/velocity, all live sprite
positions, simulation clock, map pointer and RNG; live actor/projectile counts,
map rows remaining and input phase are also retained. It is not a full-RAM
cryptographic digest. Real-input delivery and moving-image review remain later
bench checks. No audio or new rendering firmware is introduced.

## Local validation

Run `python -m unittest discover -s tests/performance/scan -v` in the project
venv. Use the canonical isolated emulator launcher, stock MOS3.0.2 and selected
native VDP; never point an emulator at the physical card. The pixel checker
reuses `scripts/console_peer.py` and reads native framebuffer pixels **outside**
measurements. It checks actual shifted rows, transparent incoming tile pixels
and stationary sidebars with0/32 sprites; still images cannot prove flicker-free
physical scanout. Preserve emulator firmware hashes with the run receipts.

## r02 diagnostic windows (SCAN01-S06)

S05 r01 builds/deployments remain immutable. Current builder emits r02 into
`scan-r02` directories. The bounded S06 bench may instead deploy the r02 binary
as `window-r02.bin` beside existing r01 assets, after verifying asset/stream
identity; that explicit mapping belongs in the deployment receipt. `scan.bin`
is preserved. No firmware or normal game is modified by this fixture change.

Flag bit2 enables the existing BENCH-009 discarded-buffer marker carrier.
A nonzero u24 tag at config11 is required and copied to header10. Case ID and
tag correlate one retained P4 aggregate window with one result file. Mainboard
stock VDP consumes/discards the same official buffer-write bytes, without new
mainboard firmware. See official `Buffered-Commands-API.md`, command0, reserved
buffer65535; never use CLEAR65535, which would remove the game assets.

After warm-up, marked runs drain before opening, send OPEN, and acknowledge it
with a pixel query. All r02 variants start a fresh synthetic pacing deadline
at the measurement boundary, avoiding deadline debt from warm-up. Per-update
drawing/PRT records are unchanged. At the end, the ordinary final drain is
recorded separately before CLOSE; cleanup and SD output occur afterward. P4
aggregate wall time therefore includes the opening acknowledgement, untimed
record/checkpoint tails, final drain and closing-carrier transit. It excludes
loading/setup/warm-up. It must not be called identical to the eZ80 PRT sum.

No per-frame picture marker is added. Existing `marker_invalid`/`last_frame`
fields in firmware telemetry are consequently inapplicable, not pixel failures.
DMA counts are signal cadence; `updates` counts publication submissions, not
proof of fresh coherent pictures or absence of sprite flicker. Phase scopes
are nested/concurrent wall time, cannot be added as CPU percentages, and may
discard scopes crossing a window boundary. The existing hooks do not directly
measure sprite-hidden duration or individual scroll primitive time.

Marked, unmarked, natural and no-PRT controls use the same r02 bytes. Historical
r01 comparisons remain separately identified because its pacing epoch differed.
