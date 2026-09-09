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

## Morning follow-up — 2026-09-09

These are additional Author observations and supplied screenshots, not a timed
capture or a repeat of the deployment run.

1. The Author typed `abcdefg` slowly. The browser then reported keyboard
   unavailable/released while video remained connected (sequence 1747,
   received/presented 322, zero gaps).
2. Approximately one or two minutes later, the Author observed video
   disconnection (sequence 1882, received/presented 457, zero gaps). Another
   135 video frames therefore arrived after the keyboard closure.
3. Reconnecting and recapturing restores typing. The Author reports that Agon
   remains undisturbed and continues functioning while Escape is not pressed.
   This does not establish the Escape/MOS-return outcome.
4. The Author reports that the preceding P4 firmware maintained its browser
   connection indefinitely. No comparative timed capture accompanies this report.

Source inspection associates the first screenshot's exact keyboard message with
the keyboard WebSocket close handler, rather than the ordinary blur handler.
The close initiator and cause remain unknown. Slow input provides no evidence
of UART saturation. Shared HTTP-task video transmission, newly shortened socket
timeouts and keyboard acknowledgement/lease deadlines require correlated
measurement. Existing browser tests use a simulated WebSocket and do not
exercise simultaneous physical video transmission and keyboard servicing.
