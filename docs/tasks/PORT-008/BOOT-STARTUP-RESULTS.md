# PORT-008 — Candidate startup release results

The private startup composition now gates the actual shared UART writers on
reciprocal pad release. Focused modeled and instruction tests pass, and EMOS
fits its unchanged ROM limit with 123 bytes remaining. Ordinary UART-only
startup remains separately selectable. This is off-bench development evidence,
not permission to deploy, ExExt activation, or production qualification.

## Scope and behavior

1. EMOS calls its private fence from init_UART1, before any UART1 open. After
   stock mainboard startup and interrupt enable, emos_init runs bounded release
   polling. It reuses the existing keyboard deadline, transport claim/release,
   parser/vector ownership and GPIO leaves; no new firmware diagnostic is added.
2. EMOS open_UART1 and uart1_keyboard_unpark refuse mux enable without a startup
   grant. A fresh reciprocal release authorizes the startup-only restore; later
   admission requires acknowledged recovery and READY high. Missing/old P4,
   failed claim, or elapsed/stalled-clock deadline leaves shared pins released
   and mainboard keyboard selected. Expiration never grants UART ownership.
3. P4's explicit --parallel-boot-candidate composition configures UART registers
   during setup without attaching the shared pins. Its existing console task
   installs the UART driver/ISR on the existing owner core, performs physical
   release, and binds UART pins only when the boot adapter requests restore.
   Restore failure or a 2,000 ms phase deadline repeats release. The ordinary
   console parser and keyboard serializer start only after recovery succeeds.
4. Default EMOS selects inert startup hooks. Default P4 does not select the
   candidate definition. P4 candidate selection is restricted to p4-console /
   p4-pc and an UNVERSIONED-DO-NOT-DEPLOY identity. Build validation checks the
   exact compile definition and retained manifests identify the selection.

## Memory

Worst ROM usage first; percentage is extra ROM divided by the prior 130,718-byte
boot-leaf build. All figures are complete linked image accounting, not estimates.

| EMOS composition | ROM bytes | Free of 131,072 bytes | Change from boot leaves | ROM increase | Static RAM bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Private startup candidate | 130,949 | 123 | +231 | 0.177% | 4,063 |
| Ordinary UART-only with inert hooks | 130,747 | 325 | +29 | 0.022% | 4,058 |
| Prior boot leaves | 130,718 | 354 | Baseline | Baseline | 4,058 |

Candidate coordinator RAM increases by five bytes. The existing deadline helper
is shared rather than copied. All ROM, ABI, VDU, route and writer guards remain
mandatory. No further extraction or limit change was needed.

## Validation

1. **706 paired physical-adapter/coordinator cases pass.** Actual P4 startup
   coordinator and pad adapter run against deterministic SDK/register boundaries,
   with the EMOS recovery leaves as the peer. Includes asymmetric polling,
   restore failure, absent/fixed-level peer, clock rollover, wrong-core refusal,
   and the retained reset/GPIO-operation failure cases. Recorded host compile/test
   duration: 2.407 s; not a GPIO speed or physical deadline measurement.
2. **12 linked-eZ80 startup cases pass.** Execute actual candidate instructions,
   actual deadline/frozen-clock fuse, actual keyboard transport claim/release,
   and actual UART enable gate. Cover successful exchange, missing peer with
   moving/frozen clocks, both initial READY levels, direct early open/unpark,
   busy ownership and IRQ-disabled refusal. Stock interrupt vector setup is
   modeled before the foreground hook. No Fab, electrical or bench claim.
3. **Linked guard negative controls pass.** Removing either admission-result
   test from a local ELF copy is rejected. The guard proves denied admission
   skips all hardware writes; it retains exact live boot-leaf caller restrictions.
4. **Existing regressions pass.** Linked eZ80 parking 289 cases, control dispatch
   10, and boot leaves 126; host parallel 9 tests, sender 1 (ordinary/telemetry
   variants), console lifecycle 6, source-profile 6 and P4 profile 12.
5. **Complete target builds.** Candidate and ordinary EMOS pass all maintained
   firmware checks. P4 candidate passes the full native wrapper and a frozen,
   unchanged-source Ninja recheck with the maintained validator. Ordinary P4
   full native verification is recorded in the machine-readable result.

## Gotchas and evidence

1. Adding the admission hook changed AgonDev's failure-return instruction shape:
   OR tests acquire status, then LD A,0xff preserves flags before the rejection
   branch. The linked guard admits only the observed exact epilogue; it does not
   skip arbitrary intervening instructions. Negative tests reject a lost test.
2. The old sender host harness omitted boundary symbols introduced by the prior
   private parallel reservation work. It now supplies fail-on-call boundaries;
   the sender suite cannot silently enter parallel ownership. UART host tests
   link the real inert startup hook unit for the ordinary composition.
3. The initial P4 registry resolution was unavailable; the successful build
   reuses the previous retained dependency lock. An IDF incremental driver later
   remained in its event wait after Ninja had finished and no child remained.
   Only that host process was stopped. Direct Ninja recheck, source-hash equality
   and the maintained validator establish the final candidate check.
4. Exact identities, hashes, logs and preparation snapshots are indexed by
   [BOOT-STARTUP-RESULT.json](BOOT-STARTUP-RESULT.json). Machine-local retained
   evidence is under agents/port008-startup. Prepared source is generated from
   the owning EMOS checkout, never edited to change a test/build outcome.

## Boundary

No hardware reset, flash, serial/network device test, SD write, bench acquisition,
production selection, tag or commit occurred. Changes remain pending review.
The boot handover is private and does not commit ExExt or admit payload/control
capability. Runtime one-board reset coordination, fresh peer identity/stale-byte
quarantine, full UART drains, native block/status binding and physical reset
qualification remain at the parent integration gates. Ordinary firmware behavior
is retained by explicit default composition, not a timed candidate fallback.
