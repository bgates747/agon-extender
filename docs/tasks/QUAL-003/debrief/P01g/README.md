# P01g — Fixed-rendering network payload ladder

## Executive summary

**Review stop: half-frame rung failed terminal query15.** Passing48KiB payloads
retained60.045 native completions/s; failed96KiB produced35.981/s and55.710ms p95
while delivering23.817Mbit/s. Byte validation passed. [Results](RESULTS.md) and
[graph](ladder.svg) distinguish diagnostics from passing benchmarks. Larger
rungs/repeats/browser tests were not run. Exact r43/startup restored; no push.
P01h remains queued after review; no compression implementation has started.

## Frozen contract

1. [x] G01: Freeze this contract and the subsequent P01h contract; preserve W
   evidence, current r43 rollback and startup. Clear mainboard via admitted CLI.
2. [x] G02: Prepare an isolated default-off r45-derived diagnostic candidate.
   Reuse the deterministic r05 SW2400 Nurples fixture (same commands and assets,
   512x384, 60 Hz pacing). No game, Golem, MOS or mainboard VDP source changes.
   Validate protocol/receiver and all bounds on host before physical deployment.
3. [x] G03: Verify candidate write/readback, identity, input and SD. Run output-off
   and full-compose/no-send controls, plus the same fixture on installed stock
   mainboard VDP. Mainboard NP04 application timing is not native P4 completion
   timing; preserve historical instrumented mainboard evidence separately.
4. [ ] G04 (stopped at first correctness failure, 96KiB): Run payload sizes 24576,49152,98304,147456,196608 bytes at 60 nominal
   opportunities/s. Keep full snapshot composition enabled and independently
   demanded at all network rungs. Count coalesced/missed opportunities; never
   describe intended 60 Hz work as realized work. Fixed native drawing and
   snapshot algorithm, priorities, affinity, queue limits and receiver host.
5. [ ] G05 (not run after stop gate): Repeat compose/no-send control between groups and descend through
   the first degrading interval. If integrity passes, refine once at midpoint.
   Repeat informative endpoints through browser receive-only transport; ordinary
   full-frame browser rendering is a separate scope, not a partial-frame viewer.
6. [x] G06: Produce tabular results, uncertainty and next recommendation. Restore
   exact r43/startup, verify keyboard/SD and send standard hardware voice plus
   visible completion banner. Commit granular work; no push, stop for review.

## Isolation and wire contract

Use the existing HTTP/WebSocket transport and one outstanding credit; no new
TCP stack, priority changes, unbounded queue or application-aware optimization.
The wired Pi receiver drains/validates diagnostic payloads without presentation.
A fixed, preallocated deterministic byte pattern may substitute for snapshot
pixels during the ladder to verify every byte without adding variable encoder
or checksum cost on P4. All rungs still perform full original snapshot work.
If used, label this synthetic payload source prominently: its cache/PSRAM access
pattern is not identical to transmitting newly composed pixels. A separate
normal full-frame endpoint preserves the real-image comparison.

Record protocol magic/version, sequence, requested payload size and fixture
nonce; receiver rejects bad lengths, contents, duplicate/out-of-order messages.
Actual sends may skip snapshot generations. Keep intentional omissions distinct
from transport corruption. Preserve installed viewer compatibility when the
experiment is disarmed. Endpoint selection uses the retained fixture nonce;
no production protocol extension. Freeze exact byte format before build.

At fixed full composition, slow networking can still reduce realized composition
through scheduling; measure it rather than normalize it away. Baseline without
network versus constant-work ladder is the causal comparison. A separate
compose-only control is necessary because demand-driven normal output composes
less when the consumer slows down. Keep snapshot storage allocations constant.

## Measures and gates

Record native refresh/s, interval p50/p95/p99/max and counts over16.67/33.34ms;
application NP04 results/state hashes; compose count/wall time; send count/wall
time; actual payload and wire-protocol bytes/s; admission/skip counts where
available; receiver correctness and durations. Lock instrumentation is optional
and separately qualified: do not reintroduce heavy trace overhead merely to fill
a column. State unavailable metrics explicitly. No hot-loop serial logging.

Use at least two controls around a threshold; worsening p95 by >25% or native
rate below58/s marks an investigation threshold, not a product acceptance limit.
Stop immediately for corruption, fixture query error, reset, loss of control,
or materially unrepresentative baseline. Preserve diagnostics, restore and
notify instead of automatically retrying or weakening gates. A performance-only
slowdown is expected ladder evidence and does not itself abort the sequence.
No recovery flash of MOS is planned or necessary for normal execution.

Estimate: roughly 40–60s fixture per healthy rung, longer if slowed; allow about
three minutes observation/staging per rung, approximately30–45min collection
plus build and restoration. Estimates are not automatic reset deadlines.

## Source précis

P01f/A/OWNERSHIP.md and SOURCES.json pin task/lock/SDK ownership; P01f/W/TABLES.md
records rejected priority scope. P02 output-isolation code provides off/discard
and send accounting; r45 archive avoids dormant heavy probes. Retained NPTRACE
is buffered and dumped after the terminal fence. Consult official Agon bitmap
refresh/pixel-query contracts without modifying those read-only checkouts.

Espressif video examples use completed-buffer ownership and compressed streaming;
these are not proof of our raw-frame throughput. P4 Fast Ethernet is100Mbit/s;
512*384*60*8 =94.372Mbit/s payload alone. Keep wire saturation separate from
rendering interference. No assumption that the full rung can sustain60 sends/s.

## Self-assigned harness correction before first network rung

The r50 mainboard/off/compose controls passed, but receiver admission before the
first network reset rejected stale control framing. Inspection found the build
script's stop-hook insertion had not matched its source indentation. The ladder
stayed armed after the compose-only marker. This is an agent-authored diagnostic
lifecycle defect, not evidence of EDP wire corruption or a measured network
threshold. No first network fixture was launched. Correct disarm before normal
output resumes; assert exact patch placement and re-run controls on a new r51
identity. This self-assigned preparation correction does not relax any runtime
correctness gate. Preserve the three r50 controls as provisional only. Also use
the separate variable-payload accounting parser, not P02's fixed-frame validator.

Collection preparation note: the repeated mainboard fixture reached its save,
but COPY could not overwrite a result left by the provisional run. Its fresh
/NPRES.BIN was retrieved and passed nonce/count/state checks. Subsequent targets
use a distinct prefix and must be absent before launch. No fixture timing gate
was relaxed and no stale result was substituted.

Host collection hardening: USB capture reopening resets P4 on this bench; retain
the prescribed startup wait, mainboard reset/readmission and fresh service state
files before timing. During corrected off-control collection, periodic ESP log
writes split the multi-call terminal nonce. Every character and all2400samples
were present. `normalize_trace.py` removes only complete writes from the four
known periodic tags before the unchanged strict trace validator. Retain raw
logs; never synthesize missing characters or suppress unknown fault messages.

## Closeout

Exact r43/startup restoration and SD/input checks passed. Standard British
hardware voice produced a fresh stage6/audio-pass receipt, completion banner
was issued and keyboard left neutral at Legacy MOS. Human hearing unconfirmed.
No active capture/receiver/controller remains. Local commits only; no push.
G04/G05 remain stopped under the correctness gate, not falsely completed.
