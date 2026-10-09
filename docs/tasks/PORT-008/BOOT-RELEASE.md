# PORT-008 — Physical boot-release adapter increment

This bench-free increment binds the existing recovery sequencers to actual
GPIO operations. It does not enable the parallel-capable startup composition.
EMOS and P4 must complete reciprocal release before any future boot coordinator
permits shared UART outputs. The Author released the bench; no hardware action,
deployment, production promotion or automatic commit belongs to this increment.

B01 [x] — Add private boot-only physical adapters. EMOS releases all Port C
lanes, isolates UART1 receive, and preloads CLOCK low / VALID high before
enabling its two control outputs. Reuse the existing atomic Port D helpers and
four-byte handover state. P4 releases all eight data outputs, isolates UART
inputs and preloads READY high before enabling that control output. Both
adapters sample actual peer control inputs and publish only completed release.
They return UART restoration permission to the future coordinator; do not
invent a second serializer or use UART timeout as a release acknowledgement.

B02 [x] — Exercise real adapter source through modeled eZ80 registers and
the IDF GPIO boundary, with asymmetric polling, missing peers, one-sided
resets, partial GPIO failures, wrong installation core and premature restore.
Assert output ownership and latch-before-output ordering at every change.
Execute linked EMOS instructions to check actual port writes, ABI and IFF.
Reuse prior sequencer, parking, session/control and build checks.

B03 [x] — Compile both complete targets and retain exact source/artifact
identities. Reuse the maintained EMOS wrappers and ROM ledger; entry headroom
is 592 bytes. Do not relax image guards or add another extraction without review.
P4 compilation must include the adapter source. Keep ordinary startup unchanged.

B04 [x] — Record results and stop. Live earliest-writer gating, boot deadline
and stalled-clock policy, UART restoration/driver installation, fresh identities,
stale-byte quarantine and one-board-reset hardware qualification remain under
the parent integration gate. No success here enables ExExt or native payload.

## Research and boundaries

Official GPIO documentation is `agon-docs/docs/GPIO.md` at
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`; wiring and held recovery levels
remain those in [HANDOVER.md](HANDOVER.md). No official reference was changed.
The reset assembly already writes Port C DDR=FF and alternate functions=0.
The actual F92 defaults used by `init_UART1()` also leave Port C as inputs,
with ALT1=ALT2=0. The earlier control-contract concern about that function
enabling UART was overly broad: **`open_UART1()` is the first EMOS UART mux
enable**. P4 `beginConsole()` explicitly calls `uart_set_pin()` at startup.
The future candidate must gate those real writers, including recovery/error
paths, before activation. Existing UART-only startup remains the installed path.

Boot adapters require exclusive ownership with no live UART/parallel activity;
they are not a substitute for the existing normal packet-draining/parking leaves.
Their caller owns the shared handover state, cancellation, deadlines and the
actual restore completion. A reset cannot promise preservation of that CPU's
RAM queues. Compile/interpreter/SDK-model checks do not establish electrical
timing, physical GPIO levels or bench readiness.

[Results](BOOT-RELEASE-RESULTS.md): 695 paired physical adapter checks and
126 complete-image eZ80 checks pass; both guarded target builds and prior
regressions pass. EMOS uses 130,718 ROM bytes (+238), leaving 354 free;
static RAM is unchanged. No ordinary boot caller or hardware operation.
