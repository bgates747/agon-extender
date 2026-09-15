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
2. [x] RX02: Inventory comparable historical evidence and trace current game's
   VDU operations. Prioritize protected HUD clipping/scrolling with alternating
   pages, then near-player span/kerb coordinate clipping and affine traffic.
   Use official docs and retained stock source as semantic baseline.
3. [x] RX03: Prepare minimal deterministic paired reproductions using current
   game's operations and identical inputs. Begin with framebuffer correctness;
   separate browser capture/output from framebuffer/transport timings. Record
   binary/firmware hashes, mode136, input schedule, frame count and clock scope.
   Reuse existing finite graphics infrastructure where it fits; do not run the
   entire matrix first. Fixtures choose modes through startup, not internally.
4. [x] RX04: Run the prioritized tests on Legacy then ExCom. Record pixel/probe
   mismatches and timings side by side in ms, worst first, percentage difference
   (ExCom-Legacy)/Legacy*100. Browser FPS alone is not rendering FPS. Retain
   durable progress/duration and fail state. No inference of throughput parity
   from unlike firmware or workloads.
5. [x] RX05: If a clear provisional defect emerges, preserve reproduction and
   explain stock divergence, evidence and uncertainty. Stop before correction,
   restore usable bench if required and play hardware British voice alert
   (spoken emulator fallback only if hardware unavailable). Otherwise expand
   through the existing relevant suite until a defect emerges or it completes.
6. [ ] RX06: Fix and test the immediate buffered-road conversion problem using
   the smallest compatibility adaptation. Preserve stock signed fixed-point
   semantics, explicit representable ranges and truncation; never rely on a
   compiler flag to define an invalid float-to-unsigned cast. Test finite
   negative/zero/positive values, boundaries, widths and shifts; explicitly
   disposition NaN/infinity/overflow without inventing stock behavior. Rerun
   unchanged r03 against stock mainboard VDP, with clean committed candidates
   and exact firmware hashes. If it does not converge, report and reassess the
   hypothesis before expanding fixes. No Golem or unrelated changes.
7. [ ] RX07: After RX06, search and ENUMERATE ONLY every instance of this
   conversion hazard in code already ported/selected for P4, including retained
   upstream dependencies, adapters, implicit conversions and equivalent helper
   paths. Use the existing dependency/source-selection authority to define the
   audited closure. Record stable finding IDs, file/function/line, source hash,
   upstream origin, source/destination types, range assumptions, risk, stock
   behavior evidence, proposed test and confidence. Separate confirmed issues,
   candidates and reviewed nonissues. Record search methods, exclusions and
   limits; text search alone does not prove exhaustiveness. Make no additional
   conversion corrections during enumeration.
8. [ ] RX08: Present the enumeration to the Author, notify on hardware and STOP.
   Each disposition must identify which findings may be corrected. Silence or
   completion of the search does not authorize bulk edits.
9. [ ] RX09: Only after enumeration review, correct the approved findings in
   discrete commits with minimal platform adaptations and regression tests.
   Keep unapproved findings open. Do not modify official reference checkouts.
10. [ ] RX10: Exercise those corrections deterministically against the pinned
    stock VDP on hardware, with identical input streams, explicit oracles,
    boundary/negative cases and retained failures. Start with each finding's
    regression, then relevant broader graphics cases and current Rally. Keep
    rendering, transport and browser timing separate; report ms and percentage
    differences relative to stock only for comparable measurements. Finish with
    the Author's manual Rally/Nurples review. HUD remains open unless reproduced
    and resolved; linked no-op framing work has its own scope and evidence.
11. [ ] RX11: Promote accepted conversion protections and upstream-update gates
    into existing docs/procedures and docs/dependencies infrastructure. Link
    each adaptation to its upstream location, rationale and executable tests;
    require reconciliation and fresh conversion-site review on upstream import.
    Keep this task's raw evidence in place; do not create competing authorities.

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

## First probe completed

See results/r01/README.md:64/64pixel checks on each path, identical CSVs.
No defect found. Next bounded probe adds direct clipped bitmap drawing and
negative-left road triangles. Keep r01 immutable. No timing conclusion.

## Actionable stop — r03

RX02–RX04 complete for the prioritized tranche: r01 and r02 matched; the current
road-section buffer stream differs at14/80samples, seven left-edge locations on
each page. See FINDINGS.md and results/r03. Stop before fixes or wider tests.
RX05 restoration/voice closes this run; RX06 awaits review. The full HUD issue
and performance comparisons remain open, not waived by this finding.

RX05 complete: original startup restored/read back, older backup preserved,
Legacy MOS prompt, hardware voice command receipt passed. RX06 remains gated
for Author review of the actionable road defect.

## Author sequencing amendment — planning-only turn

The Author selected RX06 immediate repair/test, then RX07 enumeration only,
then the mandatory RX08 review stop, then approved RX09 corrections and RX10
stock-comparison testing. This amendment supersedes the earlier generic RX06
hold for the future work sequence, but **this turn authorizes task-document
changes and the voice notification only**. Do not implement, enumerate source
sites, build, flash or run tests until execution resumes after this stop.
No experimental push without review. Hardware voice at required review stops.

Separately, PORT-003's unimplemented-command consumption tranche owns safe
no-op handlers, with audio obligations retained in PORT-004. Do not mix that
change into the numeric correction candidate. Rally mute/audio A/B and command
framing probes belong to that tranche; the proposed relationship to HUD flicker
remains a hypothesis.
