# PORT-008 — Runtime release invalidation

EMOS must not reuse a startup UART grant after observing P4 READY low.
This off-bench increment adds latched refusal and uses the existing mainboard
VBlank keyboard owner to stop receive/transmit admission, release held keys,
return input to mainboard, and physically fence the shared pins. Only 123 ROM
bytes remain in the candidate: measure fit first and stop if it exceeds the
unchanged limit. No bench operation, payload activation or automatic commit.

R01 [x] — Implement the smallest EMOS-owned loss boundary in the private
startup candidate. Admission samples P4 READY only for acknowledged UART;
the temporary reciprocal-restore grant remains usable while READY is low.
Once observed, loss must remain latched even if READY rises. The existing
keyboard tick, after its parked-owner exclusion, performs nonblocking fault
cleanup, closes its UART/vector lease, selects mainboard input and repeats
the actual pad fence. Never poll a recovery deadline in an ISR. Ordinary
UART-only composition retains inert hooks. Preserve unrelated mainboard GPIO.

R02 [x] — Compile and account for the complete EMOS candidate before widening
the implementation. Compare against 130,949 ROM bytes / 123 free using the
existing AUDIT-008 accounting tool. Keep all image and writer guards. If the
candidate does not fit, retain the attempted source and exact linker failure,
record the blocking size, and pause before P4 changes or another ROM purge.

R03 [x] — If it fits, execute the actual linked EMOS instructions for loss
during active receive, partial parser state, held-key cleanup, loss first seen
by an admission caller, low/high bounce, repeated ticks and parked-owner
exclusion. Verify denied UART writers and real pad/vector cleanup. Build the
ordinary composition and run affected ownership/profile regressions. Record
source and artifact hashes and pause for review; no hardware claims.

## Research and reuse

The official [MOS UART API](../../../../../agon-docs/docs/mos/API.md) and
[GPIO contract](../../../../../agon-docs/docs/GPIO.md), documentation commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, define the UART interrupt-vector
and GPIO ownership baseline. The maintained EMOS UART/keyboard owner supplies
fault cleanup, parser reset, held-key release, vector release and IRQ preservation;
do not invent another receiver. Reuse the actual fence and linked startup tests
from [BOOT-STARTUP.md](BOOT-STARTUP.md) and the pad sequence in
[BOOT-RELEASE.md](BOOT-RELEASE.md). Keep the ordinary profile explicit.

## Deliberate limits

This is observed-loss invalidation, not complete runtime reset recovery. A
polled READY level cannot prove that every brief reset edge was observed.
EMOS does not automatically reconnect or change committed VDU routing; an
active ExCom display lease may therefore remain unavailable after loss. P4's
runtime queue cancellation, fresh session identities, stale-byte quarantine,
foreground retry, full UART drains and physical asymmetric-reset tests remain
under the parent integration gate. Normal parallel parking must not be mistaken
for peer reset. No supported ExExt payload exists yet.

On a failed ROM gate, R03 remains unexecuted; the retained experiment is not a
deployable candidate. A new extraction or smaller scope needs Author review.

## Result

[Results](RUNTIME-RELEASE-RESULTS.md) record 26 linked startup/runtime cases,
four guard negative controls and existing regressions passing. The complete
candidate adds 32 ROM bytes, leaving 91 free; ordinary composition adds five,
leaving 320 free. No bench operation, P4 change or automatic commit. Pause for
Author review before the next recovery increment.
