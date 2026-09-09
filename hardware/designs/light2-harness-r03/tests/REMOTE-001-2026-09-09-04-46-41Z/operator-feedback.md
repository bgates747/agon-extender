# First physical browser typing — operator feedback

Reported by the Author on 2026-09-09 after the paired deployment recorded in
this directory. This is an operator observation, not another timed capture or
an amendment to the original deployment result.

1. Typed characters appeared in the browser's P4-rendered display.
2. The Author explicitly confirmed that Enter and Backspace worked.
3. There was noticeable latency; no timing measurement was collected.
4. The browser appeared to lose focus while typing. The Author suggested that
   it might be losing its P4 connection. Actual DOM focus loss, capture
   revocation and socket disconnection have not been distinguished; connection
   loss is a hypothesis, not a confirmed cause.
5. Escape/MOS return, the result byte, deliberate blur/reacquisition, repeated
   resets and the timed exit were not confirmed for this physical session.
   Prior emulator results do not fill these hardware evidence gaps.

The Author requested a progress checkpoint and commit before stopping for the
night. This records a working physical typing/editing round trip with unresolved
responsiveness and capture stability, not full qualification. Candidate
identities and registry r41 remain unchanged. No new firmware, reset, capture
or SD operation accompanies this observation.

REMOTE-001 owns the next investigation, with PORT-006 for connection/queue
behavior and PORT-005/EMOS INTEG-009 for input delivery. Measure the path before
changing timeouts, and preserve the distinction between input latency, EMOS
text acknowledgement, P4 presentation and browser presentation.
