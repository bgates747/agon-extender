# W9 — Stock drawing-drain comparison

Run `AUDIT-005-2026-09-10-21-40-16Z`, procedure `uart-path-capture-r03`.
**Acquisition, exact payload, saved result and timing checks pass.** The Author
accepted these findings and authorized W10 on 2026-09-10; the separate W9
post-run keyboard observation remains unconfirmed. The
[accepted contract](stock-queue-drain.md) authorizes this single comparison;
no further capture, firmware change or game test was performed.

Removing P4's 64-primitive drawing limit reduced this workload's elapsed time
from **5.075174 s to 1.097135 s: 4.63 times faster, or 78.4% less time**.
The approximately 60 Hz transmission pauses disappeared. This controlled
change corroborates AUDIT-005-F006: the departed drawing limit was the dominant
cause of this counted-point slowdown. It does not establish that all remaining
delays, setup timeouts or browser/game latency share that cause.

## Evidence and provenance

1. The analyzer acquired 720 million samples at 24 MHz. The complete marker,
   32,768-byte payload and correct black/white pixel replies match with two
   independent decoders. There are no framing errors, payload byte starts
   while P4 withholds CTS permission, or final-reply starts while Agon
   withholds permission. [Analysis](evidence/stock-drain-trace/analysis.json)
   and [collection](evidence/stock-drain-trace/collection.json) retain hashes
   and checks; original capture/decoder records remain in the local bundle.
2. P4 ran `uart-excom-console-r08-b2026-09-10-21-23-43Z` from clean `b9d4ff6`.
   The [deployment receipt](evidence/stock-drain-local/deployment.json) binds
   the independently verified image and observed startup to the
   [host condition](evidence/stock-drain-trace/host-condition.json). The
   operator confirmed all video clients closed, followed by five seconds of
   settlement. No independent server client-count observation is claimed.
3. EMOS and the SD executable/startup were unchanged. The only new result is
   [00000006.CSV](evidence/stock-drain-trace/00000006.CSV); case, pixel values,
   timestamp arithmetic and successful Legacy return pass. All five prior
   CSVs retain their hashes. Raw CSV annotations still name the old P4 image
   and connected browser expectation; the host record explicitly overrides
   both, without rewriting the original CSV. FAT time is not the run identity.
4. The Author reports Agon PASS. The CSV independently records successful
   Legacy return. Post-run USB keyboard responsiveness is a separate requested
   observation, not inferred from a successful drawing result.

## Comparison with the accepted browser-off reference

Both runs use the same EMOS, counted-point workload, baud rate and acquisition
mechanics. P4 drawing draining is the selected production change; common
renderer, UART/parser/input/network code, core placement and dependencies are
unchanged. Reference: [W7](browser-disconnected-findings.md), run
`AUDIT-005-2026-09-10-20-03-35Z`. Unrounded values and deltas are in the
[comparison record](evidence/stock-drain-trace/comparison.json).

| Interval | Before (s) | Stock drain (s) |
| --- | ---: | ---: |
| Payload transmission span | 4.390836 | 1.094046 |
| Estimated byte occupancy | 0.284444 | 0.284444 |
| Inter-byte idle, P4 withholds permission | 3.343735 | 0.044065 |
| Inter-byte idle, P4 permits sending | 0.762657 | 0.765537 |
| Payload end through final reply | 0.684338 | 0.003089 |
| Payload start through final reply | 5.075174 | 1.097135 |
| Final query through reply | 0.684048 | 0.002799 |
| Longest payload gap | 0.014203 | 0.000110 |

P4-imposed idle drops by **98.7%**. The old trace had 249 payload gaps longer
than 1 ms, with transmission resuming every 16.669 ms on average and about
102 bytes between resumptions. The new trace has **zero** gaps over 1 ms;
its longest is approximately 110 microseconds. The predicted signature of
the removed frame-count limit is absent.

Agon remains continuously permissive during the 2.704 ms wait for the first
final-reply byte. Its permission pauses during the six-byte reply total only
47 microseconds, matching the previous behavior. The remaining CTS-permitted
payload idle is nearly unchanged at 0.766 s; this is not a direct measurement
of EMOS CPU cost and is insufficient to select another code repair.

| Same-run interval | Agon clock (s) | Wire (s) | Wire minus clock (ms) |
| --- | ---: | ---: | ---: |
| Send | 1.083333 | 1.094046 | 10.713 |
| Tail | 0 | 0.003089 | 3.089 |
| Total | 1.083333 | 1.097135 | 13.802 |

All differences fit one 16.67 ms clock quantum. Zero saved tail ticks means
the tail fits within that clock interval, not instantaneous completion.
The earlier three Legacy counted-point totals were all 124 ticks (1.033 s),
versus 130 ticks (1.083 s) here. That historical comparison puts this result
near the prior stock throughput, but is not a fresh paired or variance study.

## Remaining issue and next recommendation

The final measured pixel query now succeeds on the first ordinary MOS wait.
The **setup** pixel query still records first status 15 and 66 ticks (0.550 s)
before eventual success, as before. Setup precedes the trace marker and is
excluded from the workload timings above. This correction therefore does not
resolve every ordinary-query timeout; preserve that distinct observation.

Recommend rerunning the **existing 48-case paired suite**, with the browser
connected and this exact P4 image, before the Author's planned Nurples
playtest. That checks whether the improvement extends across output paths and
payloads while video is active. It also retains separate setup/completion
timeout observations. This is a recommendation for review, not an armed run.

The Author subsequently authorized this recommendation; the
[W10 contract](stock-drain-full-suite.md) records the bounded follow-up.
The [acceptance record](evidence/stock-drain-trace/acceptance.json) preserves
this disposition separately from the original collection-time review state.

The point-workload bottleneck improved as measured above. The subsequent
[W10 suite and playtest](stock-drain-suite-findings.md) retain uneven gains,
ordinary-query stalls and a reported Nurples regression. Keep the
[core-affinity review](../PORT-003.md#deferred-core-affinity-review) deferred
deferred pending the next reviewed investigation. If the broader slowdown is resolved, its review
waits for optimization after implementation is substantially complete, as
the Author directed. Do not infer a need for core changes from this result.
