# P01g results — network payload ladder

## Executive summary

**The first half-frame rung failed; escalation stopped.** With identical rendering
and independently requested full snapshot composition, 48 KiB payloads passed at
60.045 native refresh completions/s and 21.004 ms p95 spacing.96 KiB payloads produced
**35.981/s, 55.710 ms p95 and terminal pixel-query error15**, while delivering only
**23.817 Mbit/s of payload**. The receiver validated all 2,023 messages; no application
payload corruption was detected. Failed-run timings are diagnostic, not a passing
benchmark. No replicated sharp threshold is established.

The network-disabled repeat immediately before the failure returned to 60.053/s
and 17.053 ms p95. These observations support transmission-related interference
well below the nominal 100 Mbit/s physical link ceiling. They do not prove which
scheduler, lock, cache, TCP-buffer or memory-copy mechanism caused the cliff;
TCP retransmissions/physical wiring were not measured by this experiment.

**Next avenue:** review whether to narrow the 48–96 KiB transaction-size interval,
then apply the frozen P01h AGM/SRLE2 experiment to actual immutable frame captures.
Compression is plausible pressure relief, not a proven cure: even 24/48 KiB output
widens rendering tails, and received message rates are below 60/s. Do not infer
that a 4:1 compressor alone establishes the full output target. No compression,
priority adjustment, Golem, production promotion or push occurred.

## 1. Matched P4 rendering — worst p95 first

Baseline for percentages: first corrected **compose-only** control. Positive p95
change means longer spacing; negative FPS change means slower completion. These
are explicit native RefreshSprites completions after 120 warm-up boundaries, not
physical scanout, browser presentation or individual primitive execution times.

| Condition | Result | Native completions/s | FPS change | Interval p95 ms | p95 change | Worst interval ms |
|---|---|---:|---:|---:|---:|---:|
| 96 KiB payload | **FAILED: query 15** | 35.981 | -40.09% | 55.710 | +221.87% | 78.772 |
| 48 KiB payload | Pass | 60.045 | -0.01% | 21.004 | +21.35% | 29.052 |
| 24 KiB payload | Pass | 60.048 | -0.01% | 20.900 | +20.75% | 25.099 |
| Compose only (baseline) | Pass | 60.054 | +0.00% | 17.308 | +0.00% | 21.273 |
| Output disabled | Pass | 60.053 | -0.00% | 17.116 | -1.11% | 20.944 |
| Compose only (repeat) | Pass | 60.053 | -0.00% | 17.053 | -1.47% | 21.129 |

## 2. Composition and transmission wall times

Same workload and composition algorithm; scheduling can reduce *realized*
composition rate. Mean wall times include waiting/preemption and can overlap;
do not add them and call the sum CPU cost. HTTP send completion is not physical
wire completion or presentation. Receiver byte validation is separate evidence.

| Condition | Compose/s | Mean compose ms | Sends/s | Mean send ms | Payload Mbit/s | Validated messages |
|---|---:|---:|---:|---:|---:|---:|
| 96 KiB payload **FAILED** | 45.660 | 21.329 | 30.285 | 8.443 | 23.817 | 2023 |
| 48 KiB payload | 60.001 | 9.750 | 55.021 | 4.400 | 21.635 | 2199 |
| 24 KiB payload | 60.033 | 8.137 | 54.202 | 1.555 | 10.657 | 2166 |
| Compose only (baseline) | 59.993 | 6.352 | 0.000 | — | 0.000 | 0 |
| Output disabled | 0.000 | — | 0.000 | — | 0.000 | 0 |
| Compose only (repeat) | 60.008 | 6.236 | 0.000 | — | 0.000 | 0 |

Payload rates exclude the 32-byte diagnostic header and WebSocket/TCP/Ethernet
framing. `summary.json` separately records diagnostic-header-plus-payload rate;
that still is not complete Ethernet wire utilization. Networkless cases have no
receiver. All three network receiver counts exactly match marker-window send
counts. CRC32, every payload byte, nonce and consecutive send ID passed.

## 3. Mainboard comparison — shared application measurement

The installed stock mainboard VDP ran the identical r05 SW2400 fixture. It passed
all 2,400 cycles, matching the deterministic state hash. Its paced application loop
measured **59.974 cycles/s**, p95 16.667 ms, maximum 33.333 ms. The corrected P4 off-control
application loop measured **60.000 cycles/s**, p95 16.667 ms, maximum16.667 ms.
These values use the 120 Hz application timer and a terminal fence only. They do
**not** measure individual rendered-frame completion. We did not flash a new
instrumented mainboard VDP or claim this is a fresh native-completion comparison.

Historical instrumented mainboard 59.927native completions/s and 17.063 ms p95 remain
in the prior debrief; they are not silently mixed into the matched P4 percentage
table. No new Rally or hardware-sprite comparison was run here.

## 4. Failure and validity

1. The half-frame run saved 2,400 states and 2,400ordered native completion records,
   with maximum pending refresh count 1. Its state SHA256 matches every passing
   run: `f43eaa27074aaf6916eded49e5f97bb7eb64a79fd0ccc060f1923a9eb3ea3948`.
   Nevertheless, its terminal query failed with code 15. The failure is retained
   in the original binary; it has not been zeroed or relabelled as a pass.
2. Native enqueue-spacing p95 was 56.177 ms versus enqueue-to-completion p95 8.675 ms
   in the failed run. That is consistent with substantial delay before enqueue,
   but percentiles cannot be subtracted to assign a stall budget or identify
   UART arrival versus parser/mutex delay. No new lock tracing was enabled.
3. All output scopes drained: pending 0, invalid 0, no reported compose/send
   failures. Composition fell from roughly 60/s to 45.660/s despite continued
   full-rate requests. That reduction is an outcome, not deliberate lighter work.
4. 144/192 KiB rungs, final control, descending/midpoint repetitions and browser
   comparisons were **not run** because the correctness stop gate fired. The
   observed bracket is a provisional single-run result, not a repeatable limit.

## 5. Method and limitations

1. Same corrected r51 firmware, fixture, assets, priorities, affinity, native
   locks and snapshot algorithm across selected P4 cases. Full independent
   composition requested at logical 60 Hz opportunities; no pending-frame backlog.
2. Wire payload is a preallocated, deterministic PSRAM byte pattern, not the
   newly drawn image. This permits byte-for-byte validation without variable
   P4 checksum/encoder work. Its cache locality differs from changing image
   pixels; infer neither real browser quality nor general image throughput.
3. A wired Pi Python receiver used the existing WebSocket/HTTP transport, one
   credit at a time, no compression and no rendering. Host Wi-Fi was not the
   data receiver. Browser receive-only/presentation comparisons remain unrun.
4. Admission permits one attempt per 16667us bucket. An unavailable credit or
   fresh snapshot can consume an opportunity. Therefore sends/s is an outcome
   of this bounded policy, not an optimized maximum Ethernet benchmark.
5. No sender/receiver hot-loop diagnostics over the test link. Native trace is
   buffered and dumped after the fixture fence. Known periodic USB log writes
   could split marker text; raw logs are preserved privately and the supplied
   normalizer removes only four recognizable log tags before strict validation.
6. Controls/repeats use a warm P4. Capture restarts during setup reset P4 and
   required the documented mainboard/readmission sequence; those setup periods
   were outside selected marker windows. Fixture collection uses unique files
   and nonce verification. Early r50 controls are provisional only and excluded.
7. No direct CPU-residency, lock-hold, packet retransmission or physical display
   measurement was added. This is load-response evidence, not a complete causal
   scheduler audit or proof that wiring cannot contribute.

## 6. Durations, preservation and disposition

Healthy P4 marker windows are approximately 39.96s; the failed half-frame window
lasted 66.798s. Automated reset-to-collection was approximately 120s per run,
including a 100s observation allowance and SD retrieval. Build, setup corrections,
restoration and voice latency are separate. These durations support future
estimates; they are not justification for silently resetting a slow test.

Raw NP04 files, validated summaries, compressed normalized native/output traces,
compressed receiver records and SHA256 hashes are under `evidence/`. Exact source
changes/build identities are in `corrected-candidate.patch` and its manifest.
Machine-private full serial/bench receipts remain under the ignored agent record.

Exact r43 and original startup are restored/read back; input and SD health
verified, SD service exited to Legacy MOS. See `restoration.json`. Hardware
voice receipt follows at closeout. P01h remains
queued for review; no next experiment starts automatically.

[Near-square timing graph](ladder.svg). Lines guide the eye between measured
points; intermediate sizes were not measured. Zero payload means no transmission.
P01h remains the planned next experiment after review; any further G refinement
is a review decision, not a newly imposed prerequisite.
