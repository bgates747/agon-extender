# P01g — Fixed-rendering network payload ladder

## Executive summary

Author-authorized on 2026-09-16: freeze and execute this experiment, then restore
and hardware-voice notify. No compression or scheduling remedy is implemented.
Measure where increased network bytes disturb otherwise identical rendering.
P01f W rejected priority boosting; this experiment changes load, not priorities.

## Frozen contract

1. [ ] G01: Freeze this contract and the subsequent P01h contract; preserve W
   evidence, current r43 rollback and startup. Clear mainboard via admitted CLI.
2. [ ] G02: Prepare an isolated default-off r45-derived diagnostic candidate.
   Reuse the deterministic r05 SW2400 Nurples fixture (same commands and assets,
   512x384, 60 Hz pacing). No game, Golem, MOS or mainboard VDP source changes.
   Validate protocol/receiver and all bounds on host before physical deployment.
3. [ ] G03: Verify candidate write/readback, identity, input and SD. Run output-off
   and full-compose/no-send controls, plus the same fixture on installed stock
   mainboard VDP. Mainboard NP04 application timing is not native P4 completion
   timing; preserve historical instrumented mainboard evidence separately.
4. [ ] G04: Run payload sizes 24576,49152,98304,147456,196608 bytes at 60 nominal
   opportunities/s. Keep full snapshot composition enabled and independently
   demanded at all network rungs. Count coalesced/missed opportunities; never
   describe intended 60 Hz work as realized work. Fixed native drawing and
   snapshot algorithm, priorities, affinity, queue limits and receiver host.
5. [ ] G05: Repeat compose/no-send control between groups and descend through
   the first degrading interval. If integrity passes, refine once at midpoint.
   Repeat informative endpoints through browser receive-only transport; ordinary
   full-frame browser rendering is a separate scope, not a partial-frame viewer.
6. [ ] G06: Produce tabular results, uncertainty and next recommendation. Restore
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
