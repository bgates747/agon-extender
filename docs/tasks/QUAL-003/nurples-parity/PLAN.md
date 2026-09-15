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
