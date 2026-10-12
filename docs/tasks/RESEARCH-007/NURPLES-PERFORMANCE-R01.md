# Nurples rendering gain — eight-hour work contract

## Executive summary

Author-authorized on2026-10-12: recover visual correctness and demonstrate at
least25% less rendering time against the **current RGB888 renderer**, aiming
for50%. Start with static ordinary bitmap plotting and partial vertical scrolling,
then add software and hardware sprites and deterministic repaired Nurples.
The indexed/PPA experiment is an option, not the required winner. Keep current
RGB888 as the control; do not claim success merely by repairing indexed's30Hz
regression to the baseline's60Hz. Bench exclusively belongs to Extender.

The Author permits a negotiated mainboard-only handoff to the6502 agent if
it requests ground-truth testing by mailbox. Handoff occurs only between runs,
with acknowledged CLI/listener state and all collectors closed. Record any
mainboard firmware/startup changes and refresh affected baselines after return;
never share the mainboard concurrently with a rendering measurement.

Time boundary: start2026-10-12T13:16:20Z; stop no later than21:16:20Z (eight hours).
The active goal owns this limit. Finish evidence/restoration within that period.
Proceed unattended within this scope; pause for any required Author answer.

## Fixed boundaries and success metric

1. Preserve EMOS, mainboard VDP, ordinary UART ExCom behavior, input, stock-visible
   drawing/palette/bitmap/sprite semantics and wiring. No ExExt/parallel work.
   No upstream bug fixes or unrelated architecture audit. Upstream references
   remain read-only. P4-specific memory/output implementation may change.
2. Mode20 is512×384×64 on the684×384 widescreen HDMI carrier. Distinguish centred
   4:3 content from full-width logical widescreen content; neither output geometry
   nor a wider workload may silently change between control and candidate.
   Investigate the matching full-width geometry only after512×384 correctness.
3. Primary gain =100×(baseline rendering cost − candidate rendering cost)/baseline
   rendering cost for identical workload, completed rendering scope and units.
   Report median,p95,maximum, late streaks and60Hz budget percentages. Require
   median andp95 gains to satisfy any claimed threshold; retain exceptions.
   Separate eZ80 active submission, UART/reply fences, P4 execution/preparation,
   snapshot, PPA, output-buffer waiting, cache handoff and DMA cadence. Never sum
   nested/concurrent wall scopes as CPU usage. Paced60updates/s is not a speedup.
4. Existing frozen tests and same-state trajectory checks are preferred. Add only
   necessary measurement separation or uncovered static/hardware cases; do not
   expand into a new general benchmarking framework. Identical instrumentation
   must be present in compared builds, with counters outside hot paths where
   practical. If changed hooks invalidate old scopes, redo both controls.
5. No visible sprite/background flicker accepted. Stable frame/strip ownership,
   bounds and scanout progress must hold; timing-only results cannot establish
   visual correctness or human input latency. Preserve Author's observed indexed
   flicker and earlier good visual reference. Do not silently suppress sprites.
6. Full baseline/candidate manifest, source snapshot, compile flags, binaries,
   fixture/config hashes, windows and raw files remain immutable per run.
   Generated build stamps/runs identify each attempt; no production/version tag
   or promotion without the normal tested Author acceptance/version gate.
7. All tests launch by explicit CLI EXEC at acknowledged prompt/listener EXIT.
   Startup contains setup only and selects mode before fixture. No test autorun,
   speculative restart or uncertain replay. On a failed attempt preserve evidence,
   diagnose actual state, recover deliberately and use a new run ID.
8. The Author's broad goal authorizes bounded compile/deploy/measure/fix iterations;
   it supersedes the prior light-thinking stop-after-first-failure experiment.
   It does not authorize proceeding after an explicit stop or unanswered question.
   Do not tie resets to runtime estimates. Preserve user files and saved startup.

## Ordered subtasks

### NP01 [x] Freeze evidence, contract and bench ownership

Commit/push existing owned changes in logical groups, then this contract and
queue/handoff. Confirm no competing bench reservation and retain the existing
listener session, startup/config backups and exact rollback segments. Read the
operation protocols before corresponding hardware actions. Deadline is fixed.

### NP02 [x] Attribute the regression without sprites

Review current indexed and RGB888 paths; separate prior-buffer wait, source row
snapshot/locking, PPA expansion, cache and actual publication. Reuse static colour
chart/bitmap and T03 partial-scroll fixtures. Prove the timing scopes before
changing scheduling. Add bounded diagnostic counters only when existing windows
cannot answer the question. Compile and verify them before flashing.

### NP03 [ ] Improve static bitmap and partial-scroll rendering

Implement the smallest hardware-appropriate remedy: remove redundant work/waits,
use contiguous/row-pointer or efficient block operations where semantics permit,
and retain complete output ownership. Compare same-stream static plotting and
partial scrolling with the current RGB888 control, repeated short windows where
needed. Require independent pixel/guard/controller checks and stable output.
Do not add sprites to hide failure to achieve an elementary gain.

### NP04 [ ] Add software sprites progressively

Reuse T08 static/32-sprite and T07 scrolling/32-sprite controls; use existing lower
counts to locate saturation if necessary. Preserve saved-background and clipping
semantics. Demonstrate median/p95 render cost and compare to RGB888 with identical
hooks. Run the repaired deterministic Nurples trajectory3,600 measured updates
(plus120 warm-up), with matching actor/projectile/map/RNG state. Keep draw cost,
output publications and application pacing separate.

### NP05 [ ] Add hardware sprites and deterministic hardware Nurples

Reuse existing resident case54 and the hardware-sprite Nurples branch/assets.
Start small, graduate to the corresponding busy scene. Measure scanout-overlay
cost separately from background rendering; compare identical sprite populations
and formats against a same-source RGB888 control. Require bounds/rolling counters,
no sprite drop/hidden rows, and retain screenshot/Author observations when available.
Check ordinary input/quit and mode0 outro without broadening into mode work.

### NP06 [ ] Decide512×384 and widescreen outcome

Tabulate worst-casep95 first, including static/scroll, software and hardware
sprites and deterministic Nurples. A25% gain is useful; aim50%. Treat claims as
conditional when output ownership/flicker remains unresolved. Do not claim a
50% gain by comparing the repaired candidate only with the rejected indexed r05.
Confirm matching full-width logical widescreen workload before claiming it.

### NP07 [ ] Other modes — only after the50% sprite gate

Only after at least50% reduction at512×384 and its widescreen counterpart,
including sprites, investigate320×240 and its widescreen equivalent, then other
already implemented native modes in remaining time. Reuse proven carriers; no
monitor-timing hunt or unsupported-mode expansion. Otherwise leave this item
unexecuted and stop by the eight-hour boundary.

### NP08 [ ] Close out, preserve and return usable bench

Retain comparable raw evidence, explicit percentages and limitations in a bounded
results document. Restore saved startup/configs and read back; leave the best
correctly working authorized image with actual CLI/input verification. Revert a
failed candidate to the exact current RGB888 control; no routine full-ROM backup
required. Commit/push owned work in logical groups as it stabilizes. Report actual
achieved gain, what did not work, installed identity, terminal state and remaining
Author visual gate. Do not mark the goal achieved if the performance objective
remains unfulfilled; record a time-limit stop honestly.

## Execution notes

NP01 frozen in73a423de; prior evidence/source commits0ed5f161,bcdc70ce pushed.
Three bounded code/measurement reviews run in parallel; root alone owns bench.
Initial attribution: indexed source snapshots plus prior-buffer waits dominate
its32ms broad scope; PPA expansion about4ms. Static chart is not inherently30Hz.
Current RGB888 control remains the performance baseline. The first optimization
removes per-pixel indirect calls in normal SET bitmap plotting, behind an explicit
comparison option. Render-execution counters will be identical in both builds.
DMA/PPA in-place scroll has no established overlap-safe contract; it is not the
first remedy.

NP02 source review and actual-controller host tests separate lock wait from
queued drawing execution. The new `render` sidecar retains the six existing
phase counters and uses 16 bounded windows (1,856 bytes). It includes stock
primitive execution and final software-sprite drawing, excludes immediate
double-buffer execution and rolling hardware-sprite composition, and reports
window-crossing/overflow explicitly. Execution is wall time with preemption and
nested guards, not exclusive CPU time. Normalize total drawing time by measured
fixture updates; report repeated-window median/p95 separately from individual
eZ80 fenced-frame latency. The existing six phases still cover output work.

NP03 begins with two independent, default-off options: `--bitmap-fast` removes
normal SET bitmap indirect pixel calls, and `--scroll-fast` uses a bounded P4
PIE row-copy kernel adapted from pinned ESP-DL. The latter retains libc for row
edges/small spans/ISRs, preserves stock row order, and performs an actual-P4
alignment/canary self-test before measured execution. No format, transport,
GPIO, DMA ownership or interrupt-priority changes belong to these options.
Control and candidate will share one frozen source revision and instrumentation.

## Research and evidence inputs

1. [Current paired comparison](RESUME-COMPARISON-2026-10-12.md): baseline RGB888
   Nurples60.07background publications/s versus indexed30.14/s; both60 application
   updates/s. Indexed PPA expansion about4ms, broad conversion/preparation scope
   about32ms including prior-buffer waiting and source snapshot. That scope is
   not equivalent to RGB888 panel staging and does not identify the bottleneck.
2. [Pipeline inventory](PIPELINE-INVENTORY.md), [official contracts/source baseline](SOURCE-BASELINE.json)
   and [capability report](CAPABILITY-REPORT.md) bound framebuffer formats,
   bitmap opacity, saved backgrounds, palette ownership and PPA limitations.
3. [Existing integration contract](INTEGRATION-R01.md) and [resumption plan](RESUME-R01.md)
   retain exact frozen fixture identities, raw timing contracts and rollback.
4. [SCAN-001](../SCAN-001.md), [SPRITE-001](../SPRITE-001.md) and
   [HDMI-002](../HDMI-002.md) retain partial-scroll, rolling overlays, known good
   geometry and prior visible behavior. The broader audits remain parked.
5. [Test protocol](../../procedures/test-execution.md), [active bench constraints](../../qualification/bench-constraints.md),
   [serial capture](../../serial-monitor.md), [SD layout](../../sd-layout.md),
   [installation](../../installing.md) and [reset](../../bench-reset.md) govern
   operations. Private devices/reservation/tools remain in ignored local records.

The first physical control identified a diagnostic coverage defect before any
speedup claim: stock pixel-query completion calls `processPrimitives()` in the
parser and bypasses the worker drain. Bitmap case39 completed882updates, but
worker-only counters saw1,048 of the expected14,994 bitmap commands (including
one marker per update). Those initial render totals are explicitly invalid for
whole-workload comparison; fenced PRT results remain separate valid evidence.
A second measurement schema covers both queued worker and queued foreground
execution with identical per-operation lock/wall scopes and exposes foreground
counts. Both variants must be rebuilt and repeated with that schema. It still
excludes immediate double-buffer rendering and hardware scanout composition.

The corrected first RGB888 pair accounts for every measured bitmap command:
case39 reduces queued rendering from2,587 to1,531µs/update (40.8%); case41
from11,561 to7,390µs/update (36.1%). Partial-scroll T03 changes from4,046 to
3,866µs/update (4.4%). These are first-window estimates, not repeated-window
qualification or an accepted Nurples gain. Both variants retain60Hz T03 output;
the candidate's actual-P4 PIE self-test passes all1,024 alignment/canary cases.

NP03 therefore also tests a bounded indexed-output remedy. The P4 output task
may capture all indexed rows and the matching hardware-overlay scene under one
native guard instead of384 separate guards. An explicit default-off
`--indexed-frame-snapshot` option preserves the old indexed path as control.
For this first candidate, prior-output-buffer waiting, target selection,
blocking PPA expansion, cache handoff and scene commit order remain unchanged.
Row descriptors remain authoritative; no assumption of a contiguous source
framebuffer is introduced. PPA and output waits remain outside native exclusion.

Compare this indexed candidate against same-revision RGB888 and indexed
controls. Keep extra full-frame snapshot/PPA cost separate from queued drawing
gains: moving cost into output preparation is not a total pipeline speedup.
Start again with static bitmap cases and T03. A coherent primitive-boundary
snapshot does not establish software-sprite visibility at capture time; examine
completed-drain ownership before graduating to software-sprite acceptance.

The parallel RGB888 alternative keeps three-byte physical rows and uses an
explicit `--bitmap-fast --bitmap-lut` selection: a256-byte internal-SRAM colour
lookup replaces repeated RGB222 channel arithmetic, and bounded four-pixel
Native expansion preserves the one-byte saved-background ABI. Alpha, paint
fallbacks, clipping, alias order, output ownership and palette semantics remain
unchanged. This does not optimize the scrolling copy itself. Sanitized exhaustive
span/alignment/alias checks and actual-controller oracle tests bound correctness;
physical repeated windows determine whether either candidate is worth keeping.

The whole-frame snapshot removes diagnostic scopes as well as lock handoffs.
Compare aggregate row-wait/composition time per attempt, not per-call means;
instrument removal can overstate a small output-preparation benefit. The queued
render sidecar remains identical. An output-only win needs a later probes-off
confirmation before a production performance claim.

While the negotiated mainboard-only lease is active, sprite implementation
preparation occurs in an isolated project-owned worktree; the frozen static
comparison checkout and completed build identities stay unchanged. This is
preparation for NP04/NP05, not permission to skip NP03's physical comparison.

NP05's default-off `--overlay-bgr` experiment composes the existing immutable
hardware-sprite scene directly into physical BGR strips. It preserves binary
alpha, XOR behavior, overlay order, span quantization, scene leases and stock
clipping behavior. Scenes crossing both horizontal edges retain the unchanged
stock painter because that inherited case has a separate bounds defect. No
new DMA client, lock, buffer lifecycle or stock bug fix is introduced. Exact
stock/candidate pixel comparisons and build selection pass offline; scanout
composition timing and physical correctness still need matched runs.

NP04's proposed `--sw-visible-snapshot` requires indexed PPA and a whole-frame
snapshot. While native exclusion is held, the P4 output task declines capture
when active software sprites are in stock's erased state, before changing the
private snapshot. The original completed `showSprites` issues only a coalesced
nonblocking task wake; the output task then acquires native exclusion and
rechecks. The hook cannot capture, wait, acquire foreground exclusion or access
a live controller. Bind at service activation after the old mode has detached;
cancel under native exclusion before joining/deleting the old output task.

Actual-controller concurrency tests cover worker and foreground drains, unchanged
sentinel bytes on refusal, final sprite pixels, outer recursive guards, a full
producer queue and callback cancellation. Their streaming checkpoint is a
deterministic host-only schedule: it establishes an offered visible capture
opportunity, not uncontrolled host/P4 fairness. An indefinitely fed stream that
never completes sprite drawing can retain its prior image. Physical paced
Nurples output and input remain the acceptance gates; no rendering budget or
upstream queue-order change is introduced.

Hardware overlay measurement uses the existing asynchronous strip compositor's
cumulative microseconds, now exposed read-only with refill counts in display
status. No new timer is added to scanout. Capture matched short intervals inside
the active workload; distinguish per-strip mean and frame-equivalent wall from
per-application-update execution. Independently sampled counters can straddle
one strip; maxima are lifetime bounds. Reject resets/faults or unexplained count
regression. Legacy `RowCompose` is output-task framebuffer preparation, never
the asynchronous hardware-sprite overlay scope. Do not sum overlapping copy,
compose and whole-refill wall costs as exclusive processor utilization.
