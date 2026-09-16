# P02 — composition and transmission isolation

## Executive summary

**The controls reveal two problems to investigate, not a clean network-only
bottleneck.** Normal streaming reproduced the timing tail. Prebuilt full-size
transmission retained a tail without native composition. However, composition-
only changed from near-stock pacing to substantially worse pacing on repeat,
with the same deterministic game states and no network sends. No firmware fix
or core-affinity change is justified yet.

| Condition | Refresh completions/s | Spacing p95 ms |
|---|---:|---:|
| Mainboard historical reference | 59.927 | 17.063 |
| P4 normal web output | 60.055 | 29.238 |
| P4 output disabled | 60.053 | 17.049 |
| P4 composition only, two runs | 60.053 / 52.551 | 17.318 / 45.509 |
| P4 prebuilt transmission, two runs | 60.057 / 60.058 | 25.026 / 21.428 |

Normal composition averaged13.623ms per full frame; discard composition
6.429/13.537ms. Full-frame sends averaged17.702ms normally and17.342/17.082ms
with prebuilt content. These wall-time scopes include waiting/preemption,
not isolated bitmap-plot execution. Game-window sends were27.360/s normally
and28.357/29.184/s prebuilt; approximately60 refresh completions/s is not60
browser frames/s. No matched mainboard snapshot/network operation exists here.

[Comparative tables](TABLES.md) separate completion FPS, spacing milliseconds,
per-frame operation costs and output rates. The historical mainboard p95 is
17.063ms. These are software-sprite fixture results, not new Rally timings or
hardware-sprite qualification. Golem remains excluded.

**First avenue:** resolve discard-repeat variability using matched P4 boot/order
and snapshot-pool placement/lock evidence, then bound HTTP/lwIP/Ethernet task
interference. The priority5 HTTP task performs queued sends; pinning only the
priority3 network worker or lwIP does not isolate the entire path. This is an
agent recommendation for review, not a newly approved experiment.

## Frozen diagnostic choices

These are agent-selected implementation details within approved P02, not new
Author-specified product requirements.

1. A compile-time diagnostic flag enables mode selection using the existing
   NPTRACE nonce: prefix `P02`, then mode0 normal,1 off,2 discard,3 prebuilt,
   followed by four random bytes. Ordinary builds have no selector or altered
   output behavior. The fixture and stock discard-buffer command remain intact.
2. The marker arms the control only for the deterministic game window. Return
   to ordinary mode after terminal accounting. Normal/prebuilt retain production
   browser ownership, takeover, credit and complete-send behavior; no reduced
   payload, receive-only client or browser-local rendering substitute.
3. Discard uses the existing snapshot producer, native rows and normalization,
   plus a local immutable-lease consumer at logical-frame opportunities. No
   frame bytes go to Ethernet. Prebuilt initializes each producer-owned slot
   once per geometry and reuses full-size bytes, bypassing native row work.
   It remains visibly synthetic and never qualifies gameplay or parity.
4. Target opportunity cadence remains nominal60Hz. Browser credit can reduce
   achieved normal/prebuilt rates; local discard may compose more frames.
   Record counts, pixels, bytes and achieved rates explicitly. Unequal work is
   not an apples-to-apples cost comparison. If needed, propose a matched-rate
   follow-up rather than hide the difference or call fewer pixels an improvement.
5. Count admitted composition/prebuilt/send operations and elapsed wall times
   with bounded counters, no timed-window prints/SD. Account operations begun
   in the window and allow a bounded post-terminal drain before dumping. Declare
   failures or unfinished operations instead of silently truncating counts.
6. Reuse r05 SW2400-state fixture and completion recorder;180second wired-Pi
   observer for transmitting controls. Verify hashes, full completion, pixel
   checks, memory placement and post-run SD/native-keyboard health. Preserve
   raw evidence. Run normal/off controls on the same diagnostic image as the
   two isolations. Repeat the discriminating contrast if material.
7. Host-check mode selection, bounded accounting, prebuilt slot initialization
   and lifetime assumptions; compile and verify candidate/rollback before flash.
   Verify normal control still reproduces the relevant behavior before attribution.
8. P02c permits at most one evidence-supported scheduling change. No blanket
   priority changes, resurrection of rejected same-core controls, or restoring
   stock's disabled blanking budget. If controls localize a useful next step,
   stop for review rather than stack speculative changes. No experimental push.

## Execution checklist

1. [x] I01: Implement and host-check default-off controls; freeze candidate source.
2. [x] I02: Build/hash/preserve/deploy/verify candidate and fixture readiness.
3. [x] I03: Run and validate four controls, repeat informative contrast as needed.
4. [x] I04: Interpret per-operation/output and paced completion separately;
   select at most one justified P02c change or stop with a proposed next step.
5. [ ] I05: Restore baseline/startup, verify service/input, commit evidence,
   deliver hardware voice notification and pause.

I01 host checks passed with C++17, warnings-as-errors and pthread support:
invalid selectors, repeated arm rejection, phase accounting, in-flight stop
join, producer-only cache reuse/invalidation, geometry bounds and slot capacity.
The stop dump copies counters under exclusion and prints only after releasing
it. Normal/prebuilt keep the existing network sender and browser protocol.

I02 candidate r45 built successfully; installed r43 was preserved and matched
before writing. Candidate flash was readback verified and boot/native USB
startup identity observed. Original startup and r05 fixture were read back.
P01's full asset readback is reused with no intervening asset writes.

## P02c source inventory — before selecting an affinity change

The selected candidate's `project_description.json` resolves SDK and Arduino to
the project-local `.pio/packages` paths, not an unrelated global installation.
The following is source/configuration evidence, not measured runnable time:

| Owner | Priority | Affinity/configuration evidence |
|---|---:|---|
| Parser |3|Explicit core0 in `video.ino::setup`|
| Drawing |5|Explicit core0 in `stock_p4_service.cpp`|
| Snapshot |2|Explicit core1 in selected experimental configuration|
| Network worker |3|`xTaskCreate`, unpinned|
| HTTP server/send task |5|`HTTPD_DEFAULT_CONFIG`, unpinned; project does not override priority/core|
| lwIP TCP/IP |18|Selected SDK config has NO_AFFINITY|
| Ethernet RX task |15|`ETH_MAC_DEFAULT_CONFIG` flags0; Arduino ETH changes reset timeout/stack but not pin flag|
| EMAC interrupt |Not a task priority|Allocated in MAC creation via `esp_intr_alloc`; setup call path and Arduino core1 configuration suggest core1, not independently observed|

Pinned SDK sources consulted: `components/esp_http_server/include/esp_http_server.h`,
`components/lwip/Kconfig`, `components/esp_eth/include/esp_eth_mac.h`, and
`components/esp_eth/src/mac/esp_eth_mac_esp.c`; selected Arduino
`libraries/Ethernet/src/ETH.cpp`. Distinguish the priority3 network worker from
the priority5 HTTP task that executes queued sends. Moving lwIP alone would
not isolate all these actors. No affinity change is selected by this inventory.

## Run admission failure retained separately

The first prebuilt attempt (`p02-prebuilt4`) saved NP04 count0/error15,
with the expected fresh nonce, and never produced an NPTRACE/NPOUT begin block.
The unchanged r05 fixture calls its pixel-query fence before its start marker;
a failed fence saves that status and terminates. Thus no prebuilt workload
was admitted, and this run supplies no prebuilt timing evidence. The underlying
reason for the initial query failure is not established. Preserve the failed
record; do not label it a prebuilt-renderer failure or discard it as a pass.
An unchanged retry and a second discard control were selected within I03.
No firmware, query timeout, renderer or fixture change was made for the retry.

## Measurement interpretation

1. Refresh completion spacing measures the P4's ordered explicit RefreshSprites
   boundaries, not physical scanout, unique browser pictures or exclusive CPU
   rendering time. Use the microsecond completion trace rather than the coarser
   MOS tick intervals. All admitted runs must match the r05 2400-state hash.
2. Snapshot composition and network-send means include preemption and waits.
   Their wall-time scopes can overlap; adding their means is not a measured
   single-frame critical path. Network units count the 32-byte EVF header plus
   196608 RGB222 bytes; TCP/Ethernet/WebSocket overhead is additional.
3. Composition-only can attain more output opportunities than credit-paced
   network output. That is intentional diagnostic evidence, not equal-output
   work or a production optimization. Normal/discard execute the same native
   composition routine; prebuilt does not establish image correctness.
4. Browser summaries cover the entire 180-second observer window, including
   setup and terminal text. NPOUT counters cover the approximately40-second
   game window. Report both without treating whole-window delivery as pure
   gameplay FPS. Observer closure may generate a final socket-send failure
   after the measured window; distinguish it from admitted NPOUT failures.
5. Mainboard timing is the retained historical stock software-sprite baseline,
   not a newly flashed or remeasured reference. No Rally, Golem or hardware-
   sprite qualification is performed in this tranche.

## Next investigation boundary

1. **Agent recommendation, not a newly approved experiment:** first resolve the
   discard-repeat variance with matched P4 boot/order and snapshot-pool placement
   evidence. Both game framebuffer allocations report internal memory, but that
   does not establish equal pool placement or task/lock timing. Then trace or
   bound HTTP/lwIP/Ethernet work alongside parser admission and composition locks;
   keep parser/draw/snapshot placement unchanged until the cause is localized.
   Start with the selected SDK/source inventory below rather than assuming
   that the priority3 worker performs the full socket send itself.
2. P02c authorizes at most one supported scheduling control. No such change is
   selected in this tranche: source affinity alone is not evidence of which
   runnable task caused a particular stall. A narrowly justified affinity
   control should preserve payload, browser credits and full gameplay work,
   and compare against the normal baseline with repeated completion traces.
3. Reuse P06's existing protocol/delivery audit for sender/API/credit limits;
   do not create a duplicate output-throughput project. The prebuilt control
   does not isolate TCP/IP CPU cost from driver, socket blocking or receiver
   flow control. An approximately28FPS sender result is not a measured raw
   Ethernet ceiling.
4. Full SW/HW streaming parity and human visual validation remain downstream.
   The initial query failure also remains a reliability observation to retain;
   do not silently expand this performance tranche into a MOS recovery task.

## Important contradictory repeat

`p02-discard6` completed all2400 states with the same state hash, zero admitted
network sends and pending refreshes bounded at1, but averaged52.551 completion/s
and p9545.509ms. `p02-discard3` was60.053/s and p9517.318ms. Composition mean
changed from6.429 to13.537ms. Both512×384 game framebuffer allocation records
say internal; this excludes an observed framebuffer PSRAM fallback but not
snapshot-pool placement, timing/locking or persistent run-state differences.

Do not discard this as an outlier or report composition as cleared. It prevents
a clean network-only attribution. The second run's enqueue p9544.339ms is also
bad, whereas enqueue-to-completion p954.123ms is comparatively small. These
are separate distributions, not subtractable estimates of CPU cost. The game
was already delayed before RefreshSprites admission. Mainboard resets do not
establish a fresh P4 boot for each control; the raw logs preserve that distinction.

## Evidence, duration and reproducibility

Six accepted controls completed2400 identical game states and2400 explicit
refreshes each, with at most1 pending refresh and successful terminal fence.
One initial-query failure is retained separately. Run order: normal1, off2,
discard3, failed prebuilt4; prebuilt5, discard6; prebuilt7. A new passive serial
capture initializes the P4 between those three series; mainboard reset alone
between controls does not reset the P4. This is a possible sequencing confounder,
not a proven cause of discard variance.

Raw NP04 state records, microsecond trace blocks, per-phase output blocks,
allocation excerpts, observer summaries and SHA256 inventory are in `results/`.
Private original serial logs and complete browser captures remain under ignored
`agents/p02/`. Recompute with the existing `nurples-parity/analyze.py`,
`analyze_refresh_trace.py`, and this directory's `analyze_output_isolation.py`,
using each result's nonce. Do not run the successful-state analyzer on the
count0/error15 failure and expect it to pass.

Observer windows were180seconds; actual fixture windows were approximately40
seconds, except slow discard6 at45.851seconds. Per-run reset-to-collection
wall durations are in `*-duration.json`; they include observation/retrieval,
not exact gameplay runtime. Allow additional staging and firmware restoration
time when scheduling repetitions. A host cleanup initially reused an old SD
session state; the service rejected it before mutation and cleanup was retried
with fresh state. That bookkeeping issue did not change collected game traces.

No affinity, priority, parser, renderer, MOS or mainboard VDP change was made
between controls. The diagnostic image is not promoted; no experimental push.
