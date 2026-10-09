# PORT-008 LC02 — Software integration checkpoint

## Executive summary

Author resumed the network-change pause. LC02 is complete within its off-bench
software/build scope. Both complete ordinary/private P4 and EMOS builds and
coordinator/linked-instruction checks pass. Private EMOS has **599 ROM bytes
free**. [Results](LIVE-COORDINATOR-LC02-RESULTS.md) and
[portable hashes](LIVE-COORDINATOR-LC02-RESULT.json) are the current evidence.
No flash, reset, SD deployment, device-network request, production change,
commit or push occurred. Pause before a separate physical activation fixture.

LC02-R01 [x] — Review/failure handling, SDK cleanup lifetime, cancellation,
phase timeouts, real clock wrap and console parser/producer/error paths checked.
Normal UART lease changes preserve physical ownership and queued replies.

LC02-R02 [x] — Paired EMOS/P4 coordinator checks and actual complete-image eZ80
startup/native execution pass. IRQ/nested refusals, boot-monitor exclusion,
matched status and refused release/fault fencing are covered.

LC02-R03 [x] — Complete ordinary/private EMOS and P4 builds pass unchanged
ownership and ROM guards. Exact source archives, artifacts, hashes and monotonic
host durations are retained; no additional utility extraction was needed.

LC02-R04 [x] — Parent/component-owner records and build guidance updated.
Author review is the next boundary. A private qualification caller must still
provision P4 storage, negotiate/admit work and consume receipts; no supported
ExExt mode or automatic file transport exists.

[The earlier partial checkpoint](LIVE-COORDINATOR-LC02-CHECKPOINT.json) remains
frozen historical evidence. Its source hashes, 577-byte remainder and initial
22-case count do not describe the final verified composition. No hardware
readiness or throughput claim follows from this software checkpoint.
