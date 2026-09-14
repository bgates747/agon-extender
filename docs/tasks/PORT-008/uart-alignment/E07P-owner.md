# E07P owner scheduling — bounded stock-alignment comparison

## Executive summary

The current P4 console owner sleeps one millisecond on every pass, including
passes that have just queued a reply. Official VDP 2.16.0's hardware process
loop does not. This is a concrete divergence worth measuring after the already
frozen EMOS comparisons. Keep the UART, parser, keyboard, SD, admission and
cancellation behavior intact. This remains under the Author's unattended parity
authorization and EMOS INTEG-014 E07P; no experimental push.

## Read-only baseline and precise hypothesis

1. Official read-only VDP tag v2.16.0, commit
   c7ac293d2aa81ddfa693390549bcd909069c8fc3: `video/video.ino`, `processLoop`.
   The stock hardware loop continuously calls `processor->processNext()`;
   its occasional delay belongs only to the USERSPACE build.
2. Maintained `vdp/video/extender/transport/console_hardware.inc` ends its owner
   loop with unconditional `delay(1)`. SHA256
   59529e79291d6b2c79e1423d6d976c97038876efda499e6ad094c85762ae940a
   exactly matches the frozen installed diagnostic P4 owner overlay.
3. Both stock and retained P4 create the process task on core0 at priority3.
   The existing P4 watchdog adapter already preserves stock's disabled IDLE-task
   watchdog policy. Do not change priorities, affinity or watchdog configuration.
4. The observed small-transfer elapsed excess is roughly1.4–2.2ms in RX02.
   Queued READY versus stock blocking READY is one known scope difference;
   the sleep is a causal hypothesis, not a measured attribution yet.
5. Existing owner host tests advance virtual time only in `delay()`. They would
   hang if production delay disappeared. Fix this modeling limitation first:
   model independent clock/UART progress at a small deterministic quantum on
   time observation, retaining real simulated delays as additional elapsed time.
   These tests prove behavior, never physical performance.

## Ordered contract

1. [x] **O01 — Freeze and prepare independent-time owner tests.** Preserve the
   old passing test output. Use a10µs deterministic observation quantum and the
   existing100-byte/ms virtual line rate; `delay(n)` adds its real n milliseconds.
   Run current owner and existing deliberate control variants. Preserve exact
   ring-wrap output, CTS stalls, five-second cancellation, fresh admission,
   parser/reply ordering and no stale tail. No firmware change in this step.
2. [x] **O02 — Minimal stock-shaped candidate.** After the isolated EMOS
   TX03/TX04/RX03 comparisons, remove only the unconditional owner `delay(1)`.
   Retain the whole owner loop and every guard, timestamp, queue, deadline and
   service call. Do not invent a new scheduler, transport, parser or wire rule.
   Run owner/stream and relevant service host tests, then build from the frozen
   original P4 baseline with only the maintained owner overlay changed.
3. [x] **O03 — Physical comparison.** Hold the selected EMOS ROM, mainboard VDP
   and app05/batch fixtures fixed. Preserve current P4 prefix before deploying;
   verify exact flashed bytes, native admission and SD/CLI readiness. Measure
   all random lengths, both directions, exact/mixed controls and independent
   wire timing with no browser output. Observe ordinary service responsiveness
   and long idle stability so a throughput gain does not hide starvation.
4. [ ] **O04 — Disposition.** Retain only demonstrated improvement with correct
   required services. Restore the old P4 image if behavior regresses; record any
   necessary platform adaptation before trying it. Update EMOS E07P results and
   the PORT-008 record. Final qualification and original bench restoration stay
   under the parent's P07/P08 gates; hardware voice only at the final checkpoint
   or a physical-assistance blocker.

Each completed step/disposition receives a separate local commit. All source
and firmware manifests remain reproducible; never edit generated build input
silently. The existing current owner is retained until O02's ordering gate.


## O01 host-model checkpoint

The old owner test passed before editing. The revised independent10µs clock
and100-byte/ms virtual UART pass all four scenarios with ASan/UBSan. Two explicit
private-copy controls also pass their expected outcomes: disabling partial-FIFO
refill produces zero refills, while allowing the next blocking parser command
before queued replies drain produces a401ms intra-packet gap. The maintained
owner retains refill and serial-reply ordering, with a1ms maximum virtual gap.
These are synthetic behavioral observations, not physical throughput results.
All12 scenarios preserve exact output, bounded CTS cancellation and fresh lease
admission. Production owner bytes remain unchanged; O02's ordering gate remains.


## Ordering checkpoint after RX03

RX03 completed its isolated wire/batch comparison and was rejected: fewer idle
instructions did not produce a demonstrated throughput gain. TX04 remains the
retained EMOS baseline. O02 source preparation is now released. EMOS RX04 removes
only redundant assembly-to-C argument marshaling relative to TX04 and can be
prepared independently; O03 physical deployment waits for that candidate's
selection, then holds its exact ROM fixed throughout the P4 comparison.


## O02 source freeze before the build

The candidate removes only the unconditional owner sleep and explains its stock
reference beside the loop. All twelve owner/control scenarios pass with ASan
and UBSan, as do the stream cases in both counter-enabled and ordinary forms.
Five service tests pass for console admission, remote input, SD lifecycle and
telemetry; the USB keyboard checks also execute in that host invocation.
No other production source changed. The clean-input P4 build follows; O02 stays
unchecked until its artifact and exact overlay provenance are verified. O03
still waits for the new EMOS receiver's isolated disposition.


## O02 artifact checkpoint

Clean source3a0f05e built identity15:14:56Z. The factory image is1578288 bytes,
SHA256 `368ff0a00e798f598964471656608d8a944a24cc062434c918e71cda203f91c5`.
The app is1447216 bytes, SHA256
`fbbc4500cbb6ce5d0aae9c906367d9fa723ab18e9fe13849c29ce570d71c9a72`.
An exhaustive comparison of the two prepared video trees finds exactly one
changed file: `extender/transport/console_hardware.inc`. The stream overlay,
probe, partition table and bootloader remain unchanged. The build manifest
and source-difference receipt are preserved in ignored E07P/p4-owner01.
No physical deployment yet; O03 still waits for RX04 disposition.


## O03 physical evidence

The factory image read back exactly and its native USB host startup was observed.
Fresh EMOS admission and SD recovered with the selected RX04 ROM unchanged.
All376 original full/mixed/wire cases and12 matched-batch rows passed exact
bytes and recovery; independent wire decoding passed with zero snapshots.
Four large-forward samples give P4 median588.147ms (588.113–588.186), mainboard
589.595ms (589.550–589.710). Return wire remains85.957ms; request-to-first-byte
fell1.397→0.749ms. Matched return remains slower:87.500 versus85.417ms (+2.44%).
The endpoint scopes remain distinct; the reverse target is not passed.

A257-byte SD upload/independent readback passed, root autoexec was unchanged,
and more than120 seconds of subsequent idle preserved the same ready/neutral
keyboard boot and online SD admission with zero browser snapshots. This is
a bounded service/idle observation, not a long-term stability guarantee.
Raw data, flash prefix/boot receipts and idle snapshots remain under ignored
E07P; paired evidence is in agon-emos E07P-results/owner01.json and epob1.
