# SCAN01-S05 — Built fixtures and mounted-card deployment

**Complete within S05 scope; pause before S06.** The Author authorized building
and deploying directly to the card mounted on their laptop. No P4/mainboard
flash, reset, physical workload or production promotion occurred. The existing
startup is unchanged, and the card remains mounted.

The selected experimental build is
`scan-scroll-suite-r01-b2026-10-06-21-30-09Z`.
The [machine-readable record](S05-FIXTURES.json) freezes all nine executable
hashes, generated streams, asset/input/tool hashes, memory bounds, emulator
identities and validation/deployment facts. Maintained sources and operating
notes are under [tests/performance/scan](../../../tests/performance/scan/README.md).
The [S04 contract](S04-TEST-CONTRACT.md) remains unchanged as historical authority.

## Preparation results

| Check | Outcome | Limit |
|---|---|---|
| Unmodified S01-pinned repaired Nurples rebuild | Byte-identical to the current36439-byte game, SHA256 `63c89d2676f6645631b2240f23002b8b68d45069979a4804ca7d14f34e720088` | No source checkout edits |
| Nine executable builds | Pass; each primary/control uses its case's same binary | Experimental, not production firmware |
| Host stream/record tests | Three tests pass over all256 generated poses; explicit software selection verified for32 sprites | Command semantics, not physical scanout |
| Final-byte emulator smoke | All nine cases save120 measured rows, expected warm-up, no abort/fault | Stock MOS3.0.2/native VDP; no hardware performance claim |
| Full repaired Nurples emulator runs | Two runs each save3600 rows; every recorded simulation checkpoint/phase/count matches | Compact checkpoint, not full RAM identity |
| Natural/no-PRT controls | T07/T08/T09 each save120 rows without faults; T09 trajectories match primary smoke | Hardware observer controls still pending |
| Native pixel checks outside timing | T03 actual partial scroll and incoming tile pixels match for32 updates; T03/T07/T08 sidebars remain unchanged | Still images cannot establish absence of sprite flicker |
| Mounted-card deployment | All65 files hash-readback verified; all91 existing arcade files and startup preserved | No fixture invoked on hardware |

The full game traverses low/high activity: zero through five live enemy/projectile
actors and zero through four player projectiles. Its original256-row map retains
24 rows at the end; no extension, death, prompt or level transition is needed.
The fixed script is neutral64/right+fire64/left+fire64/neutral64, repeating.
Gameplay time is synthetic two raw clock units/update; real elapsed clocks,
ordinary MOS polling and the bounded production vblank helper remain intact.
Every frame attachment explicitly selects software sprites. The derivative's
source diff is retained beside its build, with asserted transformations.

The checkpoint includes player velocity/position, live sprite positions,
simulation clock, map pointer and RNG; actor/projectile counts, map rows and
input phase are also separate fields. Across the two full runs its trajectory
SHA256 is `fe49126ee8b2284d00ef4ed43133ac23bcc0d1a80bd62f46c582bf63b6a69c53`.
These are controlled rendering/pacing workloads; the private key map does not
prove transport input delivery.

## Concrete SD locations

| Content | Card path |
|---|---|
| Synthetic T01–T08 | `/extender/scan-r01/t01` through `/extender/scan-r01/t08` |
| Repaired-game T09 and its copied runtime assets | `/test/nurples/scan-r01` |
| Fresh evidence destinations | `/agents/extender/results/scan-r01` |
| Load-only startup templates | `/extender/scan-r01/autoexec-legacy.txt` and `autoexec-excom.txt` |
| Build manifest and short instructions | `/extender/scan-r01/build-manifest.json`, `README.txt` |

Each case directory has `scan.bin`, `run.cfg`, `smoke.cfg`, `full.cfg`.
T07/T08/T09 additionally carry bounded control plans. `run.cfg` initially selects
120 measured updates; full plans select600 synthetic or3600 game updates.
A later run must select a **fresh result path per endpoint/repetition**. Existing
results cause refusal; no automatic evidence overwrite. Startup templates select
mode20 before loading, but **have not replaced `/autoexec.txt`**. S06 must install
and verify the chosen mode/route startup and bench identities under its own
preflight, then restore original startup at closeout.

## Implementation findings and precise limits

F01 — Reused r04's PRT/fence/deadline idioms and familiar-art format, plus the
existing isolated-game builder and native VDP capture approach. The old r04
files, game checkout, renderer and firmware are unchanged. Synthetic streams
use original game tile IDs0,89,90,91,73,75,57,58,59,129,147,206,207,208,190,192,
and original ship/seeker/turret/fireball images371/339/383/270. Source pixels are
read from the pinned AGNB, not resampled.

F02 — Stock MOS RST18 uses a16-bit BC length even in ADL. The initial >64KiB
asset-stream call was truncated in the emulator; setup now splits into two
bounded calls. The corrected native image and all-case execution checks pass.
This was a fixture preparation bug, not an Extender rendering defect.

F03 — Module-safe memory is checked: repaired-game tables end at `0x04DB8B`,
setup/frame scratch starts at `0x050000`, and3600×24-byte records occupy
`0x080000` through `0x09517F`, below `0x0B0000`. Existing game file-loader scratch
remains its original internal SRAM area. All multibyte harness record/packet
fields accessed with unsuffixed ADL loads/stores are allocated24bits; two-byte
packet fields are emitted by the host or retained game helpers with their
existing padding.

F04 — Interval totals stop after pacing/fault sampling and before compact
checkpoint calculation/record copying. Whole-window MOS elapsed includes that
unmeasured tail. The decoder reports submission/headroom percentages, wait,
misses, saturation/faults and final drain, and omits renderer-completion claims
when the per-update fence is disabled. No emulator speed is presented as a
mainboard/P4 performance result.

F05 — PRT1 is admitted only when unused/disabled with control0 and system-clock
source. Exit restores control0; the reload remains65535 because reading these
addresses returns the counter, not a recoverable prior reload. This refines the
contract's broad “restore state” wording. PRT0, interrupt vectors, shared clock
selector and interrupt enable remain untouched. Saturation is a marked lower
bound; no wrapped short interval is accepted.

F06 — Primary fixtures need no custom mainboard timer firmware. Each synthetic
update has one ordinary screen-pixel query; T09 has none until final drain.
P4-only window instrumentation and physical keyboard-arrival/consumption tests
remain separate S06 preparation, not results claimed by these scripts.

## Retained local evidence and next boundary

Ignored `agents/scan001/s05/build-06` holds the selected source export, assembly
listings, manifests and source-transform diff. `unmodified-rebuild` holds the
matching game reconstruction. `emulator-final` contains the17 validated result
files, decoded summaries and host identities; `native-visual` contains three
images and pixel assertions; `deployment-receipt.json` records the verified
card identity and readbacks. Machine-specific access details stay there and in
the local bench record. The isolated emulator has been stopped.

S06 is next: reconcile installed physical identities, then run the agreed short
mainboard/ordinary-P4 diagnostic comparison. Do not advance to renderer changes,
DMA experiments, broad performance sweeps or production promotion under S05's
completed authorization.
