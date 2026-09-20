# Current-build mode transition check — 2026-09-20

The historical stale 320×240 output did not reproduce on the installed key-query
candidate. Ordinary mode changes updated P4 status, actual frame dimensions and
browser canvas. The unmodified historical Nurples fixture also produced 512×384
game output while streaming. A separate, large output-dependent application
slowdown was observed; no firmware correction was attempted.

## Controls

Four CLI changes (8→20→8→20) under continuous production-browser streaming ended
with matching P4 status, frame headers and canvas dimensions. Frames in flight
at the boundary included the preceding size; settled dimensions were correct.
Two no-observer CLI controls also reported the requested modes. No browser page
errors occurred. `cli-control.json` records exact observations. This is not an
exhaustive mode/depth/Copper or concurrent-resource lifetime qualification.

The original cadence60.bin was verified byte-for-byte against its archived
artifact before execution. No production game or fixture binary was modified.
The connected run received 720 512×384 frames, plus title/initial-mode frames;
status reached mode20 about 15 seconds into observation and remained there.
These frame counts include loading and do not measure monitor refresh or
unique rendered frames. Raw browser observations remain in ignored local evidence.

## Unexpected performance finding

Ranking: slowest mean application cycle first. Baseline is output disabled,
same installed firmware and same binary, one run per condition, streaming first.

| Browser streaming | Recorded cycles | Mean application cycle (ms) | Application cycles/s | Mean cycle increase vs baseline |
| --- | ---: | ---: | ---: | ---: |
| On, production client/codec negotiation | 1,800 | 80.174 | 12.473 | +381.0% |
| Off | 1,800 | 16.667 | 60.000 | baseline |

Both terminal telemetry records show zero VDU faults. Timing comes from 1,799
MOS-clock intervals at nominal 120 Hz; these are application-loop rates, not
renderer completion or browser presentation rates. `timing.json` and original
trace/telemetry files retain evidence. This single pair is a strong reason for
follow-up, not a diagnosis of UART, locks, codec, renderer or browser overhead.
Do not compare it as an otherwise-identical trial against an older candidate.

The first 150-second whole-run deadline was insufficient for roughly 144 seconds
of application intervals plus loading/exit. Observer stopped; normal Escape and
CLI recovery were used, without reset. Retrieved evidence contains the full
1,800-cycle record, so the deadline was not proof of a game hang. The subsequent
no-streaming comparison used a 210-second bound justified by the observed total.
It completed normally. No repeated/reset-to-pass tests were performed.

## Disposition and final state

QUAL-003-I006 is not reproduced in this bounded current-build check; retain the
historical failure and do not claim the underlying cause was fixed or identified.
Output-dependent application pacing needs a separate bounded follow-up in this
existing task before optimization. Preserve original algorithms and isolate
production snapshot/encoding/network interference before selecting changes.

No flash, reset, wiring change or autoexec edit. Autoexec was retrieved and
verified byte-identical. Host observer closed; SD service exited; original mode0
restored at an ExCom MOS prompt, keyboard admitted and neutral. Host working
directory returned to root. Test batches and receipts live under /test/mt-*;
no /mystuff game files changed. No hardware/emulator notification.

Author clarification: this output-dependent slowdown is familiar from another
agent's investigation. Reconcile existing findings before proposing further
experiments. Observations and questions for that agent are in
[AGENT-QUESTIONS.md](AGENT-QUESTIONS.md); awaiting its written response.
