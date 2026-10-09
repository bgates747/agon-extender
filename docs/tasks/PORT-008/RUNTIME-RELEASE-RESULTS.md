# PORT-008 — Runtime release invalidation results

EMOS now latches an observed loss of P4 READY and uses its existing keyboard
interrupt owner to invalidate the receiver, release remote held keys, close
the UART/vector lease and fence the shared pads. Focused linked-instruction
tests pass. The candidate fits with 91 ROM bytes remaining. This closes only
the observed-loss boundary, not automatic recovery or physical qualification.

## Behavior

1. Candidate UART admission invalidates the acknowledged grant when READY is
   sampled low. A subsequent high READY cannot restore that grant. The temporary
   reciprocal-release grant still permits the authorized startup restore while
   P4 READY is low. The grant is volatile because ISR and foreground now share it.
2. The existing mainboard VBlank keyboard tick excludes normal parallel parking
   before calling the private candidate hook. The hook reuses actual keyboard
   fault/parser/SD-mailbox cleanup, stock callback/keymap release, UART close and
   pad fencing. It also handles a receiver that was already faulted. No ISR wait,
   new diagnostic, timer policy or public API is added.
3. EMOS selects mainboard input after cleanup; the next stock key packet is
   accepted. The hook releases only its owned UART interrupt vector. Subsequent
   ticks do not repeat cleanup, and denied writers cannot reenable UART pads.
4. Ordinary UART-only firmware selects the actual inert hook. P4 source,
   production selection, installed firmware and bench ownership are unchanged.

## Memory

Worst ROM use first. Percentage is the increment divided by each composition's
previous ROM use. These are complete guarded linked images, not estimates.

| EMOS composition | ROM bytes | Free of 131,072 bytes | Prior ROM bytes | Increase | ROM increase | Static RAM bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Private startup/runtime candidate | 130,981 | 91 | 130,949 | +32 | 0.024% | 4,063 |
| Ordinary UART-only / inert hooks | 130,752 | 320 | 130,747 | +5 | 0.004% | 4,058 |

The final candidate includes the already-faulted receiver correction and
volatile grant. The earlier 38-byte measurement is superseded by this final
32-byte increment. No ROM guard or source ownership boundary was relaxed.

## Validation

1. **26 linked eZ80 startup/runtime cases pass.** Twelve retained startup cases
   and fourteen runtime cases execute the actual candidate instructions.
   Runtime cases cover all three keyboard sources, an existing receiver fault,
   loss first observed by UART admission versus the tick, READY bounce, partial
   parser state, real held-key callbacks/keymap cleanup, owned-vector closure,
   repeated ticks, denied late transmission, mainboard input, temporary restore
   and parked-owner exclusion. GPIO, IX/SP and IFF checks are retained. No
   modeled peripheral boundary is a hardware speed or electrical measurement.
2. **The previous candidate fails the new regression control.** Running the
   same linked suite against the preserved startup-only image fails because
   READY returning high revives its lost grant. The final image passes.
3. **Four linked guard negative controls pass.** Removed UART admission tests,
   removed runtime hook and an unauthorized second hook caller are rejected.
   The final guard also passes against the preserved ordinary composition.
4. **Existing regressions pass.** Ordinary linked parking 289 cases, control
   10 and boot leaves 126; keyboard host receiver in both ordinary/telemetry
   variants, console host adapter, parallel host nine tests, source profile six
   tests, and 706 retained paired startup-adapter cases.
5. **Complete target builds pass.** Both EMOS compositions pass all maintained
   firmware, ABI, VDU, keyboard and writer checks. Final candidate source equals
   its retained preparation snapshot; test-only revisions have a separate
   snapshot. The instruction suite records its own host-monotonic duration;
   artifact identities and log hashes are indexed in
   [RUNTIME-RELEASE-RESULT.json](RUNTIME-RELEASE-RESULT.json).

## Evidence and limits

Machine-local evidence is retained under agents/port008-runtime-release. The
initial builder lacked its runtime-check default worktree link; setting that
local link fixed preparation. Host regressions initially selected the wrong
prepared tree or enabled unsupported LeakSanitizer; explicit owner/worktree
selection and ASan/UBSan with leak detection disabled pass. The keyboard harness
now links the real inert startup hook instead of omitting its new boundary.
These setup failures do not establish firmware defects.

No reset, flash, serial/network device test, SD operation, bench claim, P4 change,
production promotion or commit occurred. READY sampling cannot guarantee every
brief reset edge is observed. Existing admitted UART traffic is stopped by the
keyboard tick; this is not instantaneous physical quiescence or a completed
packet drain. An active ExCom display route is not automatically recovered.
P4 runtime queue cancellation, a held reset/release protocol, fresh identity and
stale-byte quarantine, foreground reconnect, full UART drains, native payload
binding and asymmetric-reset hardware qualification remain open. Pause here.
