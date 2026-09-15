# Rally Legacy/ExCom comparison — r01

## Executive summary

Author authorized a diagnosis-first comparison of current Rally on Legacy and
ExCom, with Golem explicitly excluded. Start with the most informative cases;
stop at the first clear provisional defect for human review rather than fixing
it silently. After reviewed fixes, iterate toward comparable or better ExCom
performance and full relevant-suite coverage. Manual Rally and Nurples review
remains the Author's acceptance gate. No improvement is yet claimed.

## Scope and baseline

1. Current AgonArcade main game is rally-game, commit 9e75196770ec14bf6826f27237f08c99176d6840,
   default grip200. Production binary SHA256
   4be88dd1c8efbb6f7cddbdce1b98ee8805572f47550cda5d8c0ef3207189395b,
   171080bytes, deployed with independent readback. Golem is out of scope.
2. Author reports ExCom HUD flickering then disappearing except speed, and
   distorted left kerbs/stripes near the player. Nurples stalls with sprite
   population/spawn. Both are visually correct and smooth in Legacy. Nurples
   is a subsequent manual cross-check, not this first fixture.
3. Preserve current firmware identities and startup before any change. Current
   bench has restored pre-E09 images, not the E07P optimized candidates.
   Do not attribute E09 optimized timing to the installed images.
4. Earlier video-throughput results measure browser delivery and earlier builds;
   E09 measures curated primitives/transport, not current Rally frame rate.
   Admit historical comparisons only after matching build, input, mode, work,
   timing scope and output settings. Otherwise create paired current baselines.
5. EMOS owns routing. Use stock VDP semantics: port, do not redesign or repair
   upstream behavior opportunistically. Keep production game/rollback intact.

## Execution checklist

1. [x] RX01: Add detached deployment execution with durable command log,
   start/end time, terminal success/failure and exact invocation. Existing SD
   client owns staging, independent readbacks and recovery journals. No host
   polling during transfers; later human follow-up reads local evidence.
   Interrupted/uncertain results must not be labelled success or blindly retried.
2. [ ] RX02: Inventory comparable historical evidence and trace current game's
   VDU operations. Prioritize protected HUD clipping/scrolling with alternating
   pages, then near-player span/kerb coordinate clipping and affine traffic.
   Use official docs and retained stock source as semantic baseline.
3. [ ] RX03: Prepare minimal deterministic paired reproductions using current
   game's operations and identical inputs. Begin with framebuffer correctness;
   separate browser capture/output from framebuffer/transport timings. Record
   binary/firmware hashes, mode136, input schedule, frame count and clock scope.
   Reuse existing finite graphics infrastructure where it fits; do not run the
   entire matrix first. Fixtures choose modes through startup, not internally.
4. [ ] RX04: Run the prioritized tests on Legacy then ExCom. Record pixel/probe
   mismatches and timings side by side in ms, worst first, percentage difference
   (ExCom-Legacy)/Legacy*100. Browser FPS alone is not rendering FPS. Retain
   durable progress/duration and fail state. No inference of throughput parity
   from unlike firmware or workloads.
5. [ ] RX05: If a clear provisional defect emerges, preserve reproduction and
   explain stock divergence, evidence and uncertainty. Stop before correction,
   restore usable bench if required and play hardware British voice alert
   (spoken emulator fallback only if hardware unavailable). Otherwise expand
   through the existing relevant suite until a defect emerges or it completes.
6. [ ] RX06: After Author review, implement minimal fixes in discrete commits,
   repeat failed cases then broaden relevant suite; preserve regression evidence.
   End with Author's manual Rally/Nurples review. No experimental push without
   review. This item is gated, not automatically released by diagnosis.

## Execution policy

Commit this contract before implementation or hardware tests. Update checkboxes
and findings as completed work warrants, with discrete rollback commits. Existing
TODO remains authoritative; this is its bounded task detail. No emulator test
changes committed before required human validation. Host-only job tests require
no firmware or hardware. Deployment jobs report into their own durable files and
return control immediately; agent does not repeatedly inspect progress. A later
turn may inspect results when the Author asks. Preparation is not deployment
success. Test staging means all required firmware/fixtures are installed and
verified. Alerts distinguish notification from test evidence.

## References

- ../timing/results/e09-unattended/README.md — latest isolated graphics result.
- ../../PORT-003/video-throughput/README.md — earlier browser/game experiments.
- ../../../../mainboard-sd.md — SD service and recovery contracts.
- AgonArcade rally-game/README.md and docs/specifications/rally-full-game.md.
- Official agon-docs/docs/vdp/VDU-Commands.md, VDU23,7 graphics-viewport scroll;
  current game hud.hpp and drawScenery use protected viewports and page caching.

## RX01 evidence

Detached worker host checks returned success/0 and failure/7, with terminal
JSON and monotonic duration, without bench access. SD verified upload semantics
are unchanged. Physical detached deployment remains to be exercised.

## Author amendment — unattended iterations

The Author explicitly permits and recommends monitoring deployment jobs when
they are prerequisites within unattended development/testing iterations. Keep
durable detached jobs; the no-monitoring policy remains for transfers handed
back for later human follow-up, not this newly authorized continuous run. Push
existing changes, confirm installation, then proceed. The Author closed the
browser and granted exclusive P4 web-socket access. Hardware voice at actionable
findings or intervention. This amendment changes no diagnosis/fix review gate.
