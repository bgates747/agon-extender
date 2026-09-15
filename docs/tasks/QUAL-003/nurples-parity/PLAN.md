# Nurples performance parity goal

## Executive summary

The Author authorizes unattended medium-effort work until Nurples renders as
fast on Extender with a connected streaming web client as on stock mainboard,
or meaningful progress becomes blocked. Stop on demonstrated parity. Necessary
bench flash/reset/SD/keyboard/diagnostic operations are authorized on the existing
wiring; preserve known-good recovery. Commit discrete steps locally; do not push
experimental changes. Voice on hardware for completion or necessary assistance;
spoken emulator fallback only if hardware cannot notify.

This goal supersedes the earlier audit-first sequence for work unrelated to the
Nurples workload. UC02–UC07 remain recorded; pull in only demonstrated blockers.
No Golem or unrelated backlog work. No destructive wiring experiments.

## Measurement contract

Use the same deterministic Nurples workload and assets on both routes in native
mode20 (512x384,64 colours,60Hz,single buffer). Pin original source and an isolated
fixture transformation. Preserve the dirty Nurples dev worktree: benchmark
copies and harness live here, no normal game changes without evidence.
Fix PRNG/input/simulation time so slower rendering cannot reduce the workload.
Record completed work using stock-compatible queue completion/query boundaries,
not submitted commands or browser refresh rate. Measure probe overhead against
unfenced controls; report timing limits. Retain actual frame/state counts and
warmup separately from timed runs. Keep web streaming active on P4, record its
independent delivery rate and errors, and compare with P4 output disabled.

Initial practical parity criterion: repeated matched runs have mean completed
frame time within5% of stock, with p95 no worse than stock plus one120Hz tick;
no increasing command backlog, missing workload, visual corruption or input
regression. Disclose tick quantization and any stricter/weaker conclusion the
data actually supports. Browser delivery is separate: a live stream is required,
but repeated snapshots are never counted as completed game frames. No quality,
resolution, sprite-count or gameplay reduction may be used to claim parity.

## Work checklist

1. [x] N01: Pin current game/assets/bench, inspect timing and deterministic seams;
   freeze a reproducible fixture with durable progress and completion outputs.
2. [ ] N02: Validate fixture workload/oracles, deploy/read back and run paired
   stock/P4 controls plus active web streaming. Retain timings and correctness.
3. [ ] N03: Identify the largest measured P4-specific cost; use bounded probes
   and code comparison to stock. Keep input/transport/render/output separate.
4. [ ] N04: Implement the smallest evidenced correction, commit/build/identify,
   flash/verify and rerun matched checks. Repeat only for unresolved bottlenecks;
   add granular documented experiments when new evidence changes the plan.
5. [ ] N05: Demonstrate repeated parity, restore usable production/CLI and startup,
   preserve results, hardware voice and stop. Human acceptance remains separate.

No completion claim from historical emulator FPS. Notify rather than guess if
an essential measurement/behavior contract needs human disposition. Source
porting remains minimal stock logic; recovery readiness is not a reason to
flash MOS needlessly. Existing r22 and both mainboard firmwares are baseline.

## Author steering and agent-assigned fixture details

Author explicitly selects the dirty `nurples-repair` working tree and generated
assets as the good reference. Preserve them; note bugs without unrelated fixes.
Author permits structured comparable-load stress fixtures and requests hardware
sprites in addition to the game's current software-sprite path. This supersedes
the initial older Nurples checkout selection. No old-checkout fixture was deployed.

AGENT-ASSIGNED (not separately Author-approved): start with a600-boundary pilot,
120-boundary warmup, fixed held-fire input, synthetic two-tick simulation clock,
stock pixel-query completion fence and per-boundary state/timing records. Use
independent SW/HW sprite variants; do not conflate their parity results. Pin
reference source/dirty asset hashes and keep generated copies in ignored storage.
If a query cannot observe scanline sprite decoration, report that limit and use
output captures for visibility; never count that query as hardware scanout proof.

N01: selected repair sources/dirty packed assets pinned in reference.json. Three
fixture variants assemble with ez80asm. A start receipt and fixed-size terminal
result are saved; timed frame records remain in RAM to avoid per-frame SD cost.
Source patching is isolated; reference worktree untouched. N02 validates the
pilot on hardware before it can support conclusions. Archive dirty reference
assets locally; do not rebuild them from older tracked art.

### N02 measurement-path clarification (agent-assigned, not separately Author-approved)

Source review confirms stock `sendScreenPixel` explicitly calls
`waitPlotCompletion(false)`. The downstream `processPrimitives` drains the queue
and calls `showSprites`; `readScreen` alone does neither. Thus the query is a
software-drawing completion boundary, not proof of hardware-sprite scanout.
Reference: official 2.16.0 `video/vdu_sys.h`, `video/agon_screen.h`, and FabGL
`displaycontroller.cpp`; corresponding port paths retain these calls.

The repair AGNB image loader requires RGBA2222, a supported hardware-sprite
format. The isolated HW variant enables the documented test flag and marks
sprites with command19 after normal initialization. Normal game source/assets
remain unchanged. Verify visibility in actual output before crediting the HW
variant; keep software and hardware comparisons separate.

The first pilot remains frozen. Before relying on its unfenced sibling for
probe-overhead conclusions, propagate the final-query failure into the terminal
record and make the analyzer's variant/scope explicit. Those are fixture issues,
not evidence of a VDP defect. Retain the original pilot identity/results.

Installed r22 includes `AGON_GRAPHICS_TIMING=1`. Dormant scopes still enter a
critical section. This is a candidate measurement cost, not yet a diagnosed
bottleneck; do not change firmware on that hypothesis alone.

Probe r02 propagates terminal-query failures and records variant flags in the
generated manifest. SW, HW and unfenced SW assemble successfully. This fixture
revision is agent-assigned under the unattended adjustment authorization; it
does not change or replace the in-flight r01 pilot. The r01 binary hashes remain
in fixture-builds.json; r02 hashes are in fixture-builds-r02.json.

N02 pilot checkpoints (agent-assigned subdivisions of the frozen paired work):

1. [x] N02a: Legacy r01 SW pilot:600 records, no query error, live gameplay/PRNG
   progression; measured60.0 completedFPS. See results/README.md. Full staging
   and both readbacks passed; reuse assets for subsequent runs.
2. [x] N02b: Same r01 SW binary on P4 without output, then with production web
   streaming. Compare state fingerprints before interpreting timing differences.
3. [ ] N02c: Hardware-sprite variant on both routes, with P4 output captures.
   Follow with corrected unfenced controls and repeats needed for conclusions.

### Output-gap investigation — AGENT-ASSIGNED, not separately Author-approved

The first P4 SW run with the production browser connected also completes60FPS,
with the identical600-record state fingerprint. However, browser delivery is
only7.79FPS across the run, about7.66FPS over its last10seconds. A static
receive-only control gives8.93FPS. These are clearly insufficient viewing
performance even though the initial completed-work criterion is satisfied.
Do NOT declare the goal achieved from this pilot. Investigate snapshot/send/
client presentation costs under N03; preserve the separate game-work metric.
Hardware-sprite comparison and heavier/repeated loads remain required.

Start with existing static output and receive-only controls, source review and
host-side network timing if available. Only add/flash bounded snapshot/send
probes if existing evidence cannot isolate the cost. Keep all such additions
agent-assigned, retain r22 rollback, and never change stock drawing semantics
just to make output easier. No EMOS change is currently justified: the P4
no-output and active-output completed-work pilot both match mainboard.

N02b complete: SW600-record fingerprints and measured60FPS match on both P4
controls. N02c hardware pair also completes with the same fingerprint; corrected
unfenced controls, heavier workload validation and repeats remain outstanding.

### N03 bounded output investigation (AGENT-ASSIGNED, not separately Author-approved)

1. [x] N03a: Separate host/network/presentation controls without firmware changes.
   Wired Pi static HW surface:19.93FPS production,28.91FPS receive-only; laptop
   Wi-Fi:about7–9FPS. Do not attribute the whole gap to P4 rendering. Retained
   prior video-throughput research already documents the same host-path effect.
2. [ ] N03b: Build an isolated r23 diagnostic variant of the exact installed r22
   source, enabling only the existing bounded `AGON_EXTENDER_VIDEO_TIMING`
   snapshot/send recorder. Pin source/config/tool/output hashes; preserve r22
   rollback. Flash/verify through the established deployment helper. Collect
   snapshot/send deltas on a static512x384 surface over wired production and
   receive-only clients. Compare observable output rates to the uninstrumented
   controls; do not silently subtract probe cost.
3. [ ] N03c: Use those durations and stock/output contracts to choose one bounded
   correction. The current browser returns credit after RAF presentation; the
   producer then waits for demand at a logical frame boundary before capture,
   and sends the full frame. Serial waits are a hypothesis, not a completed
   diagnosis. Any lookahead/credit experiment must retain bounded storage,
   correct ownership/disconnection/mode-change handling and no starvation of
   parser/network tasks; historical RGB-4 continuous-output starvation remains
   a regression constraint. No drawing-algorithm rewrite is authorized by this
   hypothesis. Freeze the selected change before implementation.

Host packet capture was unavailable without a password; no privilege or wiring
change is needed. Use the existing wired Pi and bounded timing hooks instead.
Do not request the sleeping Author's attention for this optional diagnostic.
