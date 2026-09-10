# Frame timing measurement contract

Console r09 adds observation to r08; it changes no queue-draining, logical
tick, task placement, UART, input, rendering or browser-credit rule. The
`AGON_EXTENDER_FRAME_TIMING` component definition and recorder translation
unit belong only to the selected diagnostic console. Other compositions have
empty scopes and no endpoint. Remove that selection after this investigation.

## Observed boundaries

| Phase | P4 owner and interval | Context / progress |
|---|---|---|
| frame | LogicalFrameService's call to executeFrameWork | pending ticks at entry, including current; units = executed primitives |
| queue | P4DisplayController's existing drain loop | units = executed primitives |
| sprites | P4DisplayController's showSprites call | all sprite work in that call |
| snapshot | successful snapshot claim through composition and finish | width × height; unrequested/skipped compositions excluded |
| suspend | caller's wait after increasing suspension depth | observed depth at entry |
| parser | runConsole's admitted/preactivation parser batch | 1 = admitted ExCom, 0 = preactivation; units = actual ConsoleStream UART bytes consumed |
| tx_enqueue | runConsole's existing UART FIFO submission | software reply depth at entry; units = bytes accepted by UART |
| tx_complete | successful existing nonblocking UART TX-completion check | completed batch count; duration of this marker is not wire time |

Frame, queue, sprites and snapshot are nested. Suspension may overlap frame
work and the parser. Do not add their times. Counts do not claim completion of
an entire application command. Pixel-read/immediate drawing may occur inside
the parser outside the frame task. TX bytes include keyboard/control replies;
this recorder does not decode them or prove eZ80 execution. Parser byte counting
adds one owner-local increment per successful UART read; cached bytes are not
counted twice. Synthetic setup bytes and the preactivation control recognizer's
direct reads are excluded. Completed batches and received bytes distinguish an
idle parser from admitted Agon traffic without per-byte timestamps/atomics.

P4 monotonic microseconds are recorded modulo 2^32. Unsigned interval arithmetic
supports wrap for intervals below 71 minutes; the host session is limited to
five minutes. A restart must be distinguished from wrap by continuity of counts
and the deployment receipt; do not splice resets into one timing comparison.

Each phase retains count, sum, maximum, last duration, maximum start/context,
units and a live start/generation/context. The 32-entry shared history retains
completed events at least 20 ms long, with explicit overwrite count. A long
operation remains visible while active even before history receives it.

Writers use fixed memory and try a lock only once. Lost completion records and
overlapping calls of one phase are counted. A dropped aggregate never leaves
the phase falsely active. The HTTP copy also tries once: `totals_valid=false`
makes aggregates/history unusable for that sample. Individual live records have
a `consistent` flag; ignore inconsistent observations. These observations are
not an atomic snapshot of every task at exactly one instant.

## HTTP and host recording

Read-only `GET /diagnostics/frame-timing` uses the existing HTTP task. It copies
fixed records briefly, then allocates/formats JSON outside the measured paths.
Timestamp and atomic overhead, short copy contention and HTTP polling are
perturbations. No allocation, network, storage or serial logging is added to
frame/parser hot paths. No additional worker or core affinity is introduced.

The task-owned `scripts/record.py` uses an ignored local configuration binding
the endpoint to the exact verified image, build manifest and deployment receipt.
It reuses one HTTP connection, waits one second after each result and allows
two seconds per socket operation. No catch-up burst occurs after a stall.
Raw JSON, host request times/durations, failures and operator markers are saved
to JSONL as they arrive; closed files receive SHA-256 hashes. Markers are human
observations and can be delayed by the operator and an in-progress request.

An HTTP failure can mean the HTTP worker or network is blocked. It does not
establish a frame-task or eZ80 hang. If HTTP recovers, maxima and live phases
provide additional evidence; overwritten history and dropped records remain
explicit limitations. Browser display continuity, Escape response and game
recovery are separate operator observations.

## Manual reproduction

1. Agent verifies and deploys the identified diagnostic P4 image, closes serial,
   backs up autoexec and prepares Extender keyboard plus the Nurples directory.
   EMOS, the game binary and assets retain their previous hashes.
2. Operator keeps the browser video connected and starts the prepared host
   recorder. After its recording cue, reset Agon, enter ExCom, load/run the
   existing Nurples executable and decline joystick input.
3. Operator plays normally. On a hang, press Enter in the host recorder to mark
   it; optionally type a short note first. Observe whether the game recovers
   and whether Escape still exits normally. Do not reset P4 during recording.
4. Type `q` and Enter in the host recorder after the observation; it also ends
   after five minutes. Report the saved path and observations. No screenshot,
   analyzer capture or SD-card return is required by this measurement.
5. Agent interprets the evidence and stops with one supported next action.
