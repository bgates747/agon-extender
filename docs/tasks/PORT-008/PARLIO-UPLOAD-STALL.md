# PORT-008-014 — Intermittent PARLIO upload stall

**Open. Extender owns diagnosis of the Pi5 → P4 → EMOS/SD upload.** On
November 20, 2026, a 177-byte SD upload stalled during preparation for an
Agon Flash test. The USB flash had passed. The stall preceded invocation of
Agon Flash. Later upload-only controls passed. Capture the next failure on
the existing bench before changing its state.

## What the evidence establishes

| Observation | Evidence and limit |
| --- | --- |
| The seventh upload stalled | The same listener had completed six PARLIO uploads, including both firmware images and 175-, 101- and 77-byte command files. The Pi's client timed out after 300 s waiting for `write-production.txt` (177 bytes). The upload used the v0.3.0 P4, EMOS and listener with mainboard VDPlet receiver A. [Original run](../BENCH-024.md) |
| The P4 later reported a terminal transport error | The saved pre-reset observation shows the same P4 job and listener boot as at submission. The P4 reported failed phase 5, transport error 2, two accepted control replies, zero confirmed payload bytes, no remote filesystem error and no retained CLOCK or VALID counts. The listener was online at this later observation. The P4 worker elapsed time was 611.964 s. The two replies establish HELLO and BEGIN. The failing boundary is the subsequent `SD_PARALLEL_WRITE` exchange. The elapsed time is consistent with the P4's 610 s request deadline. [P4 transfer worker](../../../vdp/video/extender/storage/fast/http.cpp) · [SD request engine](../../../vdp/video/extender/storage/fast/engine.hpp) |
| The failure did not recur in the controls | The exact 177-byte file passed alone and seventh in the same order. A further ten seven-file sequences passed all 70 uploads without a recovery reset. Those controls used a restarted bench, production VDPlet and fresh SD paths. Passing receipts show completion and exact clock counts. The failure rate and the influence of entry state remain unknown. [Upload controls and series](../BENCH-024.md) |
| Earlier PARLIO failures provide comparisons | November 17 qualification lost listener admission on a 511-byte PUT and a 65,537-byte GET. Arcade MP008 reported unexpected VALID edges on a separate upload. Those records have distinct signatures. The cause of the 177-byte stall remains open. [First two-way campaign](PRODUCTION-SD-PARALLEL-R02.md) · [Bench audit](../BENCH-022/FINDINGS.md) |

The Pi reached the P4 and the P4 reached the EMOS listener before the stall.
The status fields cannot tell whether EMOS received the parallel-write
request, whether the endpoints exchanged payload clocks, or whether the UART
completion reply or its handover was lost. The P4 copies its physical
counters into the staged result at return, so unavailable counts do not
establish that the wires were idle.

## Capture on the next failure

1. **Preserve the failed attempt under the operator's current reservation.**
   Stop new transfers. Copy the Pi runner output, parent/child receipts, job
   manifest, failed file's original staged-client journal and the preceding
   successful transfer receipts to the run evidence. Record the failed
   file size, direction, position, source identity, SD target, firmware
   identities, last restart and host timeout. Use the journal's P4 boot and
   job ID to correlate every later observation.
2. **Take the first read-only snapshot immediately.** Save the raw response
   or HTTP error and a UTC timestamp for each of these P4 endpoints. Capture
   these before a reset, listener EXIT, input command, discard, release or
   another upload.

   | GET | What to save |
   | --- | --- |
   | `/sd/fast` | P4 boot, job ID, phase, confirmed bytes, size, record count, transport/remote/filesystem status, worker timing, and all parallel outcome and CLOCK/VALID fields. |
   | `/sd/status` | EMOS listener boot, protocol, online and pending status as reported by the P4. |
   | `/keyboard/status` | EMOS input boot/epoch, readiness, neutrality, held or pending state, and reason as reported by the P4. |
   | `/telemetry/latest` | Raw cached EMOS telemetry, receive count and age when this endpoint is available. |

3. **Capture the same job at its terminal result if it is still pending.**
   A Pi timeout can occur while the P4 worker is still within its deadline.
   If the operator is authorized to keep observing, take a second GET
   snapshot at terminal state or at the P4 deadline. Keep both snapshots
   with their timestamps. If ownership, boot or job ID changes, record
   that transition. Leave the P4 spool and any mainboard target,
   `.p17part`, `.p17meta` and `.p17bak` files in place. When the worker has
   released its queue and inspection is authorized, record the presence
   and sizes of those files before any recovery changes them. [Staged transfer protocol](../../protocols/mainboard-sd-staged.md)
4. **Record physical evidence if an approved capture is already running.**
   Retain the time window from the UART `SD_PARALLEL_WRITE` request through
   EMOS CLOCK/VALID and P4 READY handover, payload clocks, UART restoration
   and any completion reply. Correlate it to the failed job and a successful
   one in the same setup. With no capture available, record that gap. Any
   added instrumentation or wiring belongs in a separately reviewed test.
   [Shared-pin handover](HANDOVER.md)

Extender will use the first failure record to place the stop before or
during payload, during the SD write, or during the return to UART. If the
available fields cannot separate those cases, Extender will report the
missing observation before proposing a targeted test. The ordinary bench
stop and custody rules apply. Routine transfers stay checksum-free.
