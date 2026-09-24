# UPSTREAM-001 — A/B test vdp-gl lifecycle corrections for a possible upstream PR

## State

- Status: Not started — candidate preserved from PORT-003 Phase C correction
- Started: --
- Finished: --

## Intent

Determine whether the lifecycle changes first implemented during PORT-003
Phase C measurably improve vdp-gl without causing regressions. If the evidence
supports them, reduce them to the smallest generally useful change and prepare
an upstream-quality issue or pull request.

This is upstream research, not authority to use corrected behavior in
Extender's strict-compatible firmware. Product adoption requires a separate
compatibility decision after the A/B results are reviewed.

## Preserved candidate

The complete first candidate is preserved in commit
`8aecb0e1a9efb671db2bff56143b11ab7b69aae5` (`PORT-003 Phase C: freeze
logical frame-service candidate`). Its parent,
`89d66c406eb401b33fed8cdc4a5d54aae33a201b`, contains the pristine vendored
vdp-gl baseline before the lifecycle patch.

The principal candidate spans are:

- `vdp/vendor/vdp-gl/src/displaycontroller.h` — virtual completion wait,
  lifecycle hooks, notification deferral, and queued-payload cancellation seam;
- `vdp/vendor/vdp-gl/src/displaycontroller.cpp` — queue lifecycle calls,
  explicit completion calls, deferred swap notification, and queued dynamic
  payload release;
- `vdp/video/extender/display/p4_display_controller.{hpp,cpp}` — the first
  submitted/started/completed sequence implementation and wait policy; and
- `docs/tasks/PORT-003/phase-c/` at that commit — deterministic fixtures,
  retained-controller tests, provenance, and the written candidate contract.

The initial direct consumer-callback design was rejected before `8aecb0e` and
is not part of the preserved candidate. The mailbox design is Extender output
infrastructure, not a proposed vdp-gl correction.

## Questions to answer

1. Does upstream `primitivesExecutionWait()` return while a dequeued primitive
   is still executing on supported stock hardware under reproducible load?
2. If so, does waiting for actual completion improve real applications, or do
   callers depend on the present earlier return?
3. Does changing `SwapBuffers` notification timing improve correctness without
   introducing latency, deadlock, missed notification, or task-ownership
   regressions?
4. Does `enableBackgroundPrimitiveExecution(false)` leave a trailing
   single-buffer `Refresh` in supported upstream configurations, and is that
   harmful or intentional?
5. Are queued dynamic path/matrix payloads leaked or otherwise mishandled by
   an actual supported lifecycle, rather than only by Extender's provisional
   start/stop design?
6. Which findings are independent enough to submit as separate minimal fixes?

## Required method

1. Reproduce each suspected behavior against the unmodified tagged upstream
   baseline on supported stock hardware and in a deterministic host harness
   where the harness does not redefine the behavior being measured.
2. Build an A/B matrix with identical compiler, framework, firmware, hardware,
   workload, and observation points. The sole independent variable is the
   candidate patch under test.
3. Test each proposed correction independently before testing combinations.
   Do not make Extender publication ordering part of a general vdp-gl patch.
4. Cover ordinary single-buffer drawing, double-buffer drawing and swap,
   explicit completion waits, queue saturation, suspension/resumption,
   transformed bitmaps, dynamic paths, task notification ownership, repeated
   lifecycle changes, and shutdown/reconfiguration behavior.
5. Record correctness, deadlock/liveness, notification ordering, memory,
   latency, throughput, and application-visible regressions. Include negative
   controls that should behave identically in both builds.
6. Review current upstream issues and development activity before proposing a
   change. Confirm that a newer tagged release has not already altered the
   relevant code.
7. If results favor a correction, produce the smallest provenance-rich patch,
   focused tests, a plain-language problem statement, reproduction steps, and
   measured before/after evidence suitable for upstream review.

## Gates

- Do not modify the official reference checkouts.
- Do not describe source inspection alone as a reproduced defect.
- Do not combine P4-only frame-service policy, sink mailboxes, or Extender
  publication generations with a general vdp-gl proposal.
- Do not open an upstream issue or pull request without the Author's explicit
  authorization after reviewing the evidence and proposed text.
- Do not restore the corrected semantics to Extender strict compatibility
  merely because the upstream experiment succeeds; upstream acceptance or a
  separate product-mode decision governs that question.

## Completion criteria

1. Every hypothesis has reproducible stock and patched evidence or an explicit
   finding that it could not be reproduced.
2. The A/B matrix includes regressions and negative controls, not only the
   originally failing scenario.
3. Any proposed patch is separated from Extender-only architecture and is
   demonstrably smaller than the preserved Phase C candidate.
4. The Author has accepted the final disposition: abandon, retain as research,
   submit upstream, or promote through a separate Extender decision.

## Firmware bug register cross-reference — 2026-09-20

[FWBUG-007](../firmware-bugs.md#fwbug-007). These stable bug identities supplement the original
finding IDs and evidence. Registration does not authorize repairs or turn
source-only findings into hardware reproductions. Use the same FWBUG ID for
any future dedicated disposal task; current dispositions remain in the register.
