# SCAN01-S04 — Focused scrolling and software-sprite comparison

## Executive summary

**Author-approved scope: nine workload cases, one video mode, both VDPs.**
The controlled ladder adds partial scrolling, incoming tile rows, then 4/8/16/32
software sprites. A static-background 32-sprite control separates sprite load
from background work. A deterministic derivative of the latest S01-pinned
`nurples-repair` is the final application check. Nurples remains the acceptance
target; passing synthetic workloads alone is insufficient.

This replaces SCAN-001's proposed automatic 22-point resident performance sweep.
Reuse existing measurement, drawing and reporting code; do not resume the broad
BENCH-009 campaign. The Author's earlier mainboard breaking point near 32 sprites
is a hypothesis to test, not a result for these particular assets and positions.

S04 freezes the definition below. **Nothing has been built, deployed or run.**
S05 owns the bounded fixture adaptations and their executable/data identities;
it requires the next Author authorization. The deferred Extender-only scrolling
demo is outside this compatibility suite.

## Fixed workload cases

All cases use **mode 20: 512×384, 64 colors, single-buffered**, selected in
`/autoexec.txt` with `VDU 22 20`. The application must not switch modes, including
on exit. The scrolling field is 256×336 at logical screen (128,48), surrounded by
stationary recognizable sidebars. The P4 retains the accepted centered, unscaled
720p HDMI output. Browser video remains disconnected; browser keyboard traffic
is a separate service.

| ID | Work per application update | Purpose |
|---|---|---|
| SCAN01-T01 | Static scene; ordinary MOS keyboard poll; no game drawing | Timing/command-completion baseline |
| SCAN01-T02 | T01 plus field scrolled downward by one pixel; no tile insertion or sprites | Partial-scroll cost with stationary sidebars |
| SCAN01-T03 | T02 plus incoming terrain through a one-scanline graphics viewport | Nurples' clipped tile insertion cost |
| SCAN01-T04 | T03 plus 4 moving software sprites | First sprite increment |
| SCAN01-T05 | T03 plus 8 moving software sprites | Second sprite increment |
| SCAN01-T06 | T03 plus 16 moving software sprites | Third sprite increment |
| SCAN01-T07 | T03 plus 32 moving software sprites | Suspected high-load breaking point with background work |
| SCAN01-T08 | T01 plus the **same 32 sprites and movement as T07**, over the unchanged initial background | High-load sprite control without scrolling/tile insertion |
| SCAN01-T09 | Deterministic repaired Nurples: ordinary scrolling, tile insertion, actors/projectiles, UI drawing, MOS polling and game pacing | Confirm relevance to actual gameplay |

T07 versus T08 measures the contribution of **scrolling plus strip redraw**, not
scroll alone. T02/T01 and T03/T02 distinguish the two additions, with timing
differences reported as observations rather than assumed additive costs. The
load ladder brackets a breaking point (for example, 16 to 32); it does not establish
that exactly 32 is the maximum, or authorize an automatic sprite-count search.

### Drawing details frozen for T01–T08

W01 — Use the same initial background, palette, origin, field boundaries and
static labels for every case and endpoint. No live FPS text, frame marker,
cursor animation, mouse overlay, audio, Copper, bitmap capture or asset upload
inside measured updates. T02 may eventually scroll its initial pattern away;
keep issuing every scroll command even when exposed pixels are blank. Do not
add periodic full-screen repainting to that case.

W02 — T03–T07 follow repaired Nurples' `tiles_scroll_background`/`tiles_plot`
idiom: one-pixel downward scroll, graphics clip (0,0)…(255,0) relative to the
playing-field origin, the ordinary background strip operation, and sixteen
16×16 tile plots across the 256-pixel width at Y−15…0. Advance the source tile row
every 16 updates. Use a fixed, repeating selection of the pinned game tiles;
freeze its explicit tile IDs/bytes with the S05 payload. Restore the playing-field
viewport before sprite movement. T09 retains the game's actual map and draw order.

W03 — Use familiar 16×16 RGBA2222 game art, reusing the existing familiar-art
loader's ship/seeker/turret/fireball choices where the pinned assets match.
Repeat that four-image sequence as sprite count rises; do not change size,
alpha pattern, paint mode or movement speed between load levels. Disable old
sprites, reset definitions, attach each frame, then explicitly select paint
mode 0 and **`VDU 23,27,20` for every sprite** before enabling the chosen count.
Repeat this explicit software selection after any fixture reset/redefinition;
do not trust inherited hardware-sprite defaults. T09's derivative must do the
same for every game sprite definition, without changing ordinary game assets.

W04 — Freeze update-indexed, integer movement. For sprite index `i` and update
index `u`, use the same prefix of this 32-sprite layout for T04–T08:

```text
x = 128 + 32*(i mod 8) + ((3*u + 5*i + 0xB009) mod 16)
y =  48 + 80*floor(i/8) + ((2*u + 3*i) mod 16)
```

The 16×16 sprites stay inside the field, with no deliberate inter-sprite overlap.
Each update moves every active sprite and issues one refresh after the whole
batch, never a refresh per sprite. Reuse stock software-sprite behavior when
background primitives themselves trigger redraw. T07/T08 sprite-command bytes
must be identical. This known geometry makes a repeatable control; it does not
claim to reconstruct the unspecified earlier 32-sprite experiment.

## Matched endpoints and finite execution

E01 — The eZ80 runs identical executable/assets/workload bytes on mainboard VDP
through EMOS Legacy and P4 VDP through EMOS ExCom. The P4 supplies admitted
keyboard packets in both routes; the broken mainboard keyboard port is not a
prerequisite. Only startup routing, out-of-window run metadata and endpoint
capability records may differ. Mainboard is the stock compatibility/performance
reference; ordinary native HDMI is the P4 regression baseline. Later, compare
the chosen candidate against both. Reconcile installed firmware identity before
timing; the production DevKit bundle is not the experimental P4-PC baseline.

E02 — T01–T08 each perform 60 untimed warm-up updates followed by **600 measured
updates**, nominally 10 seconds. Use the existing nominal 60-Hz MOS-clock deadline
pacing, record late deadlines and never skip a workload update to catch up.
T09 uses the already agreed **3,600 measured gameplay updates** after 120 fixed
untimed warm-up updates. Its ordinary one-vblank wait helper is preserved;
record its finite-poll timing-fault flag. Stop by work count, not elapsed seconds.
A slow endpoint taking longer is a result, not a reason to reduce its workload.

E03 — First run a 120-update smoke using these same cases as needed for readiness.
Then collect one complete nine-case pass on each compared endpoint/variant.
T09 requires three complete matched repetitions. Repeat only the observed
threshold bracket and T07/T08 control pair to three matched repetitions where
needed to support a breaking-point claim; do not automatically repeat an entire
mode/renderer/control matrix. Preserve endpoint order and reverse it for the
second matched repetition where practical. Every retry has a separate run ID.

E04 — A first pass contains 8,400 measured updates: a **nominal 140-second work
floor per endpoint**, excluding warm-up, setup, saving, flashes and collection.
This is arithmetic, not a bench completion estimate. Use the smoke's retained
durations before giving an actual estimate. A five-minute per-case host bound
marks incomplete evidence and requests controlled recovery; it does not reset
Agon automatically. No silent retries after a hang or readiness failure.

E05 — Primary measurements contain no human/host input other than an abort.
All cases still poll the ordinary MOS keyboard interface. Abort makes the run
partial, never a full pass. T09 uses fixed seed/map/initial state, an update-indexed
movement/fire script, invulnerability and disabled joystick/title prompts, as
specified in S05. Simulation state must match across endpoints. Scripted private
key-map substitution is rendering/pacing evidence, not real input-delivery proof.

## What is timed, and what the percentages mean

Reuse PRT1 at /256: nominal 72,000 counts/s, 13.889µs/count and 1,200 counts per
nominal 60-Hz frame interval. Calibrate against the existing MOS-clock control
outside measurement; preserve interrupts, PRT0 and the shared clock selector.
Refuse conflicting PRT1 ownership and restore its prior state on all exits.
A saturated counter is a lower bound/failure, never a wrapped short sample.

| Scope | T01–T08 | T09 |
|---|---|---|
| Submission / active work | Start of loop work through MOS poll and submission of that update's drawing commands | Start of gameplay work through all ordinary update work, immediately before its normal pacing wait |
| Completion | One existing screen-pixel-query fence **after the whole update**, timed through the matching MOS reply | No per-update fence in the primary gameplay run |
| Deliberate pacing | Time after the whole-update fence until the declared MOS-clock deadline | Time in the original game pacing helper |
| Total | Entire measured update, with timing/bookkeeping boundary documented in the S05 source | Same; include record overhead consistently and disclose any unmeasured tail |
| Remaining queued work | Final fence/drain outside the measured window, reported separately | Same; no claim that fast CPU submission means the VDP has caught up |

The existing official pixel-query fence is supported on both VDPs; no new
mainboard firmware hook is required for the primary comparison. It includes
query/reply/dispatch cost and changes natural pipelining. T01 exposes this
overhead; do not subtract it as a guessed constant. The fenced synthetic ladder
measures application-visible completed-update cost. Unfenced T09 measures the
game's normal submission/pacing behavior. Compare endpoints **within the same
case/scope**, not fenced synthetic numbers against unfenced gameplay as though
they were interchangeable.

M01 — Report active work as a percentage of 16.667ms, median and p95. For T01–T08,
show submission and completion budget use separately. Remaining headroom is
`100 − active_budget_percent`; negative means over budget. Active time includes
MOS routing/output blocking and any waits inside game work; it is not pure
eZ80 computation. Preserve raw timer counts and calibration alongside readable
percentages and milliseconds.

M02 — Also report worst active/total interval, achieved updates/s, percentage
over the active budget, missed pacing opportunities, longest consecutive miss
streak, actual pacing wait, saturation/fault counts and final-drain time. Separate
“all required updates completed” from “met the 60-Hz target.” A missed opportunity
is not a deliberately omitted game update or a directly observed dropped HDMI
frame. Show isolated misses separately from sustained overload; do not invent a
universal threshold from one noisy sample.

M03 — For T09, retain update/phase IDs and simulation checkpoints so different
spawn/fire work cannot masquerade as a renderer difference. RAM records store
raw active/wait/total intervals, MOS-clock deltas and flags. Allocate only after
checking code/assets/record-buffer ownership against the module-safe memory map.
Save after timing to `/agents/extender/results`; no SD or serial logging, HTTP
polling, per-primitive callbacks or full-frame capture in measured loops.

M04 — Optional P4 aggregate hooks may observe scroll duration, sprite-absent
time, queue/backpressure, conversion/publication, cache work and DMA cadence.
Read them after the window closes and preserve their existing meanings. These
are P4-only diagnostics, not columns to compare with unavailable mainboard data.
DMA refresh rate is not the rate of fresh coherent game pictures. Do not subtract
timestamps from different processors to infer input latency.

## Small controls and correctness gates

C01 — Reuse the same case IDs for bounded control replays; they are not extra
workloads or an unrestricted cross-product. On T07/T08 and a T09 smoke, compare
the normal instrumented run with timing/marker-disabled operation, and remove
per-update fences from the synthetic pair for a short natural-pacing replay.
Use matched hook-free P4 ordinary/candidate images before attributing a change
to the renderer. Differences are reported, not silently mixed into the primary
timing distribution. Keep the failed direct image to selected diagnostic smokes.
OFF/held-output studies are not automatic additions to this suite.

C02 — Reuse the same scenes for a separate short live-input/visual replay after
timing. Record identified press/release arrival in the real MOS key state and
the update that consumes it; disable private-map substitution for that check.
For deterministic comparison keep input from altering the primary workload.
Retain sprite flicker, stationary-sidebar fidelity and snappy input as independent
acceptance gates. A still image or correct final pixels cannot prove absence of
moving-image flicker. Hold requested visual inspection until the Author replies.

C03 — Validate software-sprite setup, viewport clipping, stream hashes and final
scene/state using existing native/golden helpers outside timing. Explicitly
exercise the full 32-sprite setup in preparation. No fresh hardware-sprite,
double-buffer, alternate-mode, overlap or fill-rate campaign is authorized by
this contract. Existing host correctness checks remain available; propose any
necessary additional physical compatibility checks before widening bench scope.

C04 — Mark capture/probe failures, retain informative evidence, recover and
continue independent cases when readiness is re-established. Recheck affected
cases without the diagnostic before calling them a VDP fault, following the
existing capture-failure protocol. The earlier 32-sprite observation and previous
mainboard diagnostic failures do not justify labeling a new failure “expected.”

## Reuse, identity and remaining implementation work

| Existing source / evidence | Reuse boundary |
|---|---|
| [Frozen r04 contract](../../testing/render-load-contract-r04.md), [application](../../../tests/performance/render_load/benchmark-r04.asm), [generator](../../../tests/performance/render_load/generate.py) | Reuse PRT/fence/stream/provenance idioms and correct per-sprite setup. Existing indefinite cases, counts 1/4/16/64 and frame markers are not this finite nine-case contract; leave frozen bytes unchanged. |
| [Familiar game art](../../../tests/performance/render_load/game_art_visual.py) | Reuse loading/format/source attribution; preserve Nurples assets. No Wolf3D assets or unrelated visual workload needed. |
| [S01 input freeze](S01-BASELINE.md), repaired game `screen.inc`, `tiles.inc`, `sprites.inc`, `timer.inc`, `vdu.inc` | Isolated game derivative plus separately identified synthetic companion. Source hashes must still match, or changed inputs require explicit reconciliation before pairing. |
| [Runner](../../../qualification/render_load.py), [bounded comparison](../../../qualification/rgb888_compare.py), [collector](../../../qualification/render_load_collect.py), [plots](../../../qualification/render_load_plots.py) | Adapt bounded scheduling/schema where needed; do not invoke their old full case lists or label old r04 IDs as T01–T09. Reuse collection and report structure. |
| [Official sprite API](../../../../../agon-docs/docs/vdp/Bitmaps-API.md), [system/pixel query](../../../../../agon-docs/docs/vdp/System-Commands.md) | S01-pinned official docs; per-sprite software selection and one refresh per batch, ordinary MOS-routed query completion. |

S05 must freeze new fixture/build/contract identifiers under the version policy,
exact generated command streams, chosen art/tile IDs and hashes, timing record
schema, source-transform diff and RAM bounds. Those binaries do not exist yet;
S04 does not invent their identities or claim source-to-binary reproducibility.
Maintain support fixtures under `/extender`, the isolated game under
`/test/nurples`, and evidence/startup backups under `/agents/extender` according
to the SD layout. Leave production games unchanged. Preserve and restore startup
byte-for-byte; Author-controlled flashing and normal rollback remain in force.

The final report has a compact side-by-side table: mainboard, ordinary P4 and
chosen candidate; work/headroom percentages first, then timing and faults.
Rank largest regressions first while retaining the nine-case order in a load
curve/table. Name the baseline for `(candidate/baseline − 1) ×100%`. Keep visual
and input outcomes beside the numbers, with unknown/unperformed fields explicit.
No result or hardware acceptance is asserted by this contract.
