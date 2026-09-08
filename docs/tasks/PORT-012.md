# PORT-012 — Prove UART flow control at 1,152,000 baud

Status: active; reviewed candidate preparation. Started: 2026-09-08.

## Scope and accepted decisions

Repeat PORT-011's bounded FLOW/ACK pause, resume and blocked-timeout exchange
at 1,152,000 baud, 8N1 on the seated r03 four-wire harness. EMOS owns UART1
in Legacy; onboard VDP retains ordinary display and clock service. The Author
approved EMOS v0.5.0, uart-flow-probe-r02 and registry r30 on 2026-09-08.
No sustained-load, activation, parallel or electrical redesign work is included.
Keep the passing v0.4.0/r01 images for rollback. Draft review precedes source
freeze, clean candidate builds and authorized deployment.

## Bounded research

1. Official MOS API documentation, `docs/mos/API.md` section 0x15 in the
   read-only agon-docs reference, defines the 24-bit baud field and hardware
   flow flag. Official MOS v3.0.2 at
   `8336409351ee5314e02801a7b72a4f1bb5282519` and VDP v2.16.0 at
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3` remain clean read-only baselines.
   MOS `main.c` selects 1152000 for its onboard VDP UART.
2. EMOS `src/uart.c` already widens the baud multiplication to 32 bits.
   18,432,000 / (16 × 1,152,000) requires divisor 1. Preserve the configured
   linked UART0/UART1 divisor guard; emulator byte delivery does not prove
   physical baud. EMOS INTEG-006 owns the command setting and host assertion.
3. The connected fx2lafw analyzer supports 24 MHz, falling-edge triggers and
   capture ratio. Use 240,000,000 samples (10 seconds), D3 falling trigger,
   1% pretrigger. Confirm positive USB data before the reset cue, since logic
   output may wait for the software trigger. Record actual extent independently
   of exit status; the previous unexplained early USB stop is not fixed.

## Work

1. [x] Set both endpoints to the target baud, expose it in diagnostics and P4
   build provenance, and run actual-code host tests and full build gates.
2. [x] Prepare and launch same-build ordinary/bad-SD and no-peer emulator
   review. Obtain Author validation before committing emulator-coupled changes.
3. [ ] Freeze reviewed candidates, preserve rollback, prepare guarded SD
   installation and combined capture; deploy only under bench authorization.
4. [ ] Run the paired test and retain endpoint results, exact decoded bytes,
   measured baud/pauses and at least five seconds of final quiet waveform.

The current fixture definition is `vdp/fixtures/uart-flow/identity.json`;
PORT-011's r01 definition/evidence remains historical. The design-adjacent
[test sheet](../../hardware/designs/light2-harness-r03/tests/uart-flow-r02.md)
owns the physical procedure. Private bench details remain in HARDWARE.local.md.

## Draft checkpoint — 2026-09-08

EMOS `agon-emos-v0.5.0-b2026-09-08-17-03-35Z` passes the full configured
qualification gate, linked UART divisor/ABI/VDU/parallel checks, runtime
regression and all 68 host tests. Stock/EMOS ordinary and deliberately bad-SD
smoke pass. The CLI no-peer case rejects unheld CTS and returns to the prompt;
the graphical review is prepared for Author validation. Its generic MOS
`Volume timeout` follows the UART diagnostic FR_TIMEOUT, not an SD fault.

P4 `uart-flow-probe-r02-b2026-09-08-17-03-21Z` builds successfully. Sanitized
actual peer-state tests and all 18 UART capture-checker tests pass. Registry
r30 artifact validation passes; repository-wide validation retains the known,
unchanged held-r02 connectivity hash mismatch recorded under PORT-011.

Private combined-capture preparation uses the new trigger/window and positive
USB-transfer readiness. It has not acquired hardware evidence. The mounted
card and passing v0.4.0 image are backed up with verified hashes. No removable
media changes, physical flash/reset, source commit or lifecycle promotion has
occurred. Author graphical review is the next gate.

## Author review and source freeze — 2026-09-08

The Author supplied the v0.5.0 graphical screenshot showing SD/CLOCK PASS,
1152000 baud, bounded `CTS did not release` and final MOS prompt, then
explicitly approved source freeze and candidate/deployment preparation.
Promote lifecycle metadata to candidate, commit reviewed inputs, and build
clean candidates. This no-peer review does not establish physical baud or
flow-control success. Preserve installed v0.4.0/r01 for rollback.

## Candidate preparation — 2026-09-08

Clean EMOS `agon-emos-v0.5.0-b2026-09-08-17-10-00Z` from `0bbd50b` passes all
configured/linked/runtime checks, 68 host tests, ordinary/bad-SD smoke and
bounded no-peer return. Clean P4 r02 from `5116e41` builds and is staged with
verified hashes; stable USB identity matched without flash/reset.

[Installation media](../../hardware/designs/light2-harness-r03/tests/PORT-012-2026-09-08-17-12-29Z/README.md)
are verified and safely unmounted. Working v0.4.0 is preserved on-card and
off-card; older rollback images remain available. The combined capture helper
passes offline full/short/wrong-rate extent checks, with no hardware capture.
Physical Agon installation and explicit P4 flash authorization are pending.
