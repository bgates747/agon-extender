# Ordinary ExExt — bounded results

Ordinary parallel VDU/reply routing now passes two focused physical fixtures.
Three warm resets pass on the earlier held-prefix pair, but later resets into
ExExt fail admission and require paired recovery. Cached keyboard input now
passes physically; larger sprite-stream traffic faults before completion. Full
transition/gameplay qualification remains incomplete. Production remains unchanged.
[Work contract](EXEXT-STREAM-R01.md) owns the remaining implementation/tests.

## Firmware and physical scope

| Pair | P4 build | EMOS build | Installed verification |
|---|---|---|---|
| Earlier held-prefix comparison | `port-008-stream-r04-b2026-10-11-12-24-35Z` | `agon-emos-v0.1.24-b2026-10-11-12-31-04Z` | All four P4 segments; complete128KiB EMOS ROM |
| IRQ teardown/cached-input comparison | `port-008-stream-r06-b2026-10-11-13-07-17Z` | `agon-emos-v0.1.24-b2026-10-11-12-47-24Z` | All four P4 segments; same verified EMOS image |
| Latency/partial-return comparison | `port-008-stream-r05-b2026-10-11-12-47-10Z` | `agon-emos-v0.1.24-b2026-10-11-12-47-24Z` | All four P4 segments; complete128KiB EMOS ROM |

All use P4-PC, normal full HDMI, existing renderer, no private payload probe,
and the unchanged eleven-signal resistor harness. Mainboard VDP is the preceding
consumer's custom build, **not official stock**. Browser video is disconnected.
Exact private receipts/raw results are retained in the ignored run silo.

## Focused physical results

Worst completion latency first; ranking is the newer pair's median whole-update
pixel-query completion. Each accepted run has120ordered rows, no fault/abort.
PRT nominal18.432MHz/256 gives72,000counts/s; one60Hz budget is1,200counts.
MOS nominal120clock units/s advances in steps of2. These calibrated assumptions
are not a precision wall-clock or HDMI-FPS measurement.

| Fixture | Earlier pair median completion (ms) | Newer pair median completion (ms) | Newer / earlier change | Newer application updates/s | Newer median active submission (ms) |
|---|---:|---:|---:|---:|---:|
| T03 single-scanline clipped tile upload | Not run: CLI invocation failed | 50.056 | Not comparable | 16.438 | 0.069 |
| T01 static tiny pixel query | 67.000 | 50.042 | −25.31% latency | 16.628 | 0.000 |

T01's newer median completion is300.25% of one60Hz budget. This includes
batching, handover, parser/query and reverse-reply scheduling; it is not raw
parallel bandwidth or a renderer-only duration. HDMI scanout remains about
60.07Hz. Application cycle rate, framebuffer submission and scanout are separate.

## Correctness/recovery boundaries

| Check | Evidence/result | Limit |
|---|---|---|
| Agon-only warm reset | Three consecutive stable ready/neutral admissions on stream-r04/EMOS-r06; first automatic post-FLASH startup also succeeds | Reset during payload/power loss not established |
| Partial returned VDP packet |4,096 actual EMOS-owner boundary/body/STOP cases pass, including257-byte packets | Host transport leaves are modeled |
| Keyboard ISR/callback ABI | Actual linked eZ80 VBlank, nested/non-nested delivery, primary/alternate/IX/IY/SP/IFF pass | Does not alone prove physical idle/game input |
| P4 native coordinator |319 ordinary/diagnostic paired cases pass;754 actual boot-pad cases separate | Not an electrical performance measurement |
| Cached-map physical input | Five seconds with no hot-loop MOS/VDU calls: six exact a/Shift/B down/up callbacks and six matching cached-map changes on stream-r06/EMOS-r07 | Bounded idle-input proof, not gameplay responsiveness |
| HDMI mode transition | Captured shared-IRQ load fault at DW-GDMA status0x50081030; original startup restored after recovery | [FWBUG-015](../../firmware-bugs.md) source-derived teardown remedy passes host negative/positive controls; first previously crashing transition and input run pass; broader repeat pending |

The earlier T03 invocation lost its leading RUN character. A stale completion
message was rejected by missing durable evidence. The revised runner clears
prior completion and verifies preparation/errors/result identity; the newer
T03 pass has its own complete saved record.

## Larger-stream and reset failures — subsequent control

1. Stream-r06/EMOS-r07 passes the five-second cached-input fixture. MOS cached
   key-map bit positions are stock BBC physical-key mappings (a65, b100,
   Shift3), not FabGL virtual-key indices. Exact packets and map sequence match.
2. Preparing T07/T08/T09 succeeds, but the following Agon-only reset does not
   restore readiness. A second Agon-only reset also fails. P4 stays running
   with clean60Hz HDMI counters; paired P4/Agon reset recovers without reflashing.
   Earlier original-startup warm-reset passes do not establish this case.
3. T07 then starts once and faults before a result: normal USB log reports
   native completion failure, native result5. T08/T09 are not invoked. No saved
   rows or sprite/gameplay pass claimed. A fresh paired reset recovers. Original
   startup and all three configs are restored and verified; bench released.
4. Extend only the existing failed-leaf USB message with direction, admitted
   length, completed bytes/callback flags and current control levels. No private
   probe, successful per-byte instrumentation or EMOS diagnostic ROM growth.
   These facts distinguish callback rejection, TX backend failure and timeout
   before choosing a remedy; do not infer new electrical corruption.


## Finite RX descriptor isolation — stream-r07

1. The Legacy five-second cached-input control saves six exact callbacks and
   cached-map changes, matching the ExExt input control. The ExCom control does
   not launch: after its reset, screen sampling remains stale and the expected
   preparation command is absent. It is not an ExCom pass.
2. All four stream-r07 P4 segments independently verify. Its first T07 invocation
   fails forward RX: requested591bytes, completion1, received576bytes,
   callback-fault0. No T07 result, T08 or T09 run is claimed. Paired reset
   recovers; original startup/config are restored and readback checked.
3. Pinned PARLIO RX accounts one descriptor per DONE callback. Its body/tail
   descriptors can complete before one interrupt is served. A source-derived
   negative reproduces591→576; the bounded derivative passes16 actual-callback
   controls, including split/coalesced completions, short/stale events, cache
   visibility and unchanged infinite RX. This supports an accounting cause,
   not a conclusion of electrical corruption or a physical remedy pass.
4. [FWBUG-016](../../firmware-bugs.md) records the isolated driver change. The
   full-HDMI candidate must now compile, independently verify after installation
   and repeat T07 before expanding to T08/T09/games. Existing warm-reset
   limitations remain open; paired recovery is a separate operation.


## Stream-r08 physical receive correction and remaining game failure

Normal full-HDMI `port-008-stream-r08-b2026-10-11-13-48-07Z`, source
`b73a5d9d856c5d8afa9870d2f16e37dafeded478`, app SHA256
`e1eb1daed0019c30bc25218c2217707e39dd64a76a94b1b4bdd4e82158e8f917`,
independently verifies all four segments. EMOS-r07 and mainboard fsim VDP are
unchanged. Results below rank slowest observed application rate first;
completion includes pixel-query transport and is not display FPS.

| Existing case | Saved records | Whole-update completion median | Application updates/s | Status |
|---|---:|---:|---:|---|
| T07:32 software sprites |120/120|67.00ms|9.96|No abort/packet fault; formerly missing RX tail now completes |
| T08:scrolling plus32 software sprites |120/120|50.06ms|14.75|Fresh completion observed; file retrieved after recovery; no abort/packet fault |
| T09:short deterministic Nurples, unfenced |No result file|Unmeasured|Unmeasured|No completion; input/listener does not answer; intentionally recovered, no automatic replay |

The screen sampler's transient409 on a display-context change stops the first
T09 observer; bounded resumed observation still finds no completion. Recovery
collection confirms no T09 file, so this is not a hidden pass. P4 keeps clean
60.07Hz HDMI counters and emits no native transport failure/panic. Agon-only
reset does not restore keyboard admission. The paired helper's fixed four-second
P4-start delay also fails; one subsequent Agon reset with P4 fully initialized
recovers. Startup and T08/T09 configs are restored/readback checked. Require
actual P4 HTTP initialization before releasing Agon in future paired helpers;
this setup correction does not itself close the warm-reset failure.

Stream-r09 freezes only the separately tested poll-snapshot ordering correction.
Its full build passes; physical T01/T03 comparison and a fresh T09 attempt must
follow before judging that change or proceeding to longer gameplay.

## Stream-r09 — no query gain; actual game allocation failure

All four stream-r09 segments independently verify; EMOS-r07/mainboard VDP
remain unchanged. Each tiny-query case saves120valid rows. Ranking is by
slowest stream-r09 whole-update rate; these are fenced application cycles,
not HDMI frames or raw parallel throughput.

| Case | r05 median | r09 median | Median latency difference vs r05 | r09 updates/s |
|---|---:|---:|---:|---:|
|T01|50.0417ms|50.0486ms|+0.014%|15.79|
|T03|50.0556ms|50.0625ms|+0.014%|16.44|

Fresh T09 stops at loading image3/350; no result file exists after recovery.
The USB log now captures `gdma_new_link_list: no mem for link list items`, then
PARLIO RX creation failure and native-arm failure for3456bytes (completion0,
received0). This is a concrete transport resource failure, not evidence of
electrical corruption or slow HDMI. Internal free-memory reporting includes
regions that do not satisfy DMA capabilities; it is not a DMA allocation proof.
The HTTP-initialized paired-reset helper recovers stable input, and original
startup/T09config are restored/readback checked. Warm-reset coverage remains
separate. The poll-ordering experiment is reverted; cache-aligned PSRAM payload
placement is the next bounded candidate.

## Matched ExCom Nurples control and byte-append CPU check

Fresh unfenced T09 on the retained full-HDMI stream-r09/EMOS-r07 UART-only
ExCom route saves120/120ordered rows after120warm-up updates:60.00updates/s,
median active work5.78ms (34.67% of a60Hz budget), p95active6.10ms (36.58%).
No abort/game/packet flags. This validates the same fixture/assets that stop
during ExExt image upload; it is not hardware-input or full-game acceptance.
Original startup/config restore is independently read back.

The explicit ExExt PSRAM candidate `port-008-stream-r10-b2026-10-11-14-25-13Z`
uses source `ad3c8e93436134e632a1e9110038a136cac375ef`, app SHA256
`efd317086df87e7b4d07af0f50d415cc5a7bf8715039290104f56d173278acfc`.
Actual native tests pass78 PSRAM payload/failure cases and213 retained internal
payload cases; coordinator and queue tests pass. Physical Nurples remains the
next gate. No source changes are made to the pinned SDK checkout.

Separately, EMOS byte-only RAM appends avoid the general memcpy path while
preserving interrupt exclusion, boundary flushing and public byte ABI. Actual
linked eZ80 instruction counts below exclude physical transfers and public
PUTCH save/restore; no bytes/s inference is justified.

|1000byte append method|Prior instructions|Candidate instructions|Difference vs prior|
|---|---:|---:|---:|
|1000single-byte calls|165000|72000|−56.36%|
|One counted call|1145|1145|0%|

The wrapper-built EMOS candidate is130960bytes (112free), source
`62928801038f8ca16ca8299714899adb2574c72a`, build
`agon-emos-v0.1.24-b2026-10-11-14-27-50Z`, image SHA256
`30e527b5d5efc3c43a30a7d295c1d7c0df52356ca80c43fec19d6b99723f0341`.
Actual linked primary/alternate registers, stack, IFF, nested VBlank and bundled
key publication checks pass. Hardware installation/performance are pending.

The first Aginvadors ExCom setup stops before RUN because its40column display
wraps the LOAD echo. The observer now permits only whitespace/explicit unknown
edge-cell substitutions; original startup is restored. No game failure or pass
is attributed to this unexecuted setup.

## Stream-r10 physical allocation repeat

All four installed segments verify. T09 again stops loading image3/350, now
with339bytes requested: SDK reports no memory for GDMA link-list items before
native completion (done0/bytes0). PSRAM payload placement alone is insufficient;
this is not a game pass or electrical corruption evidence. Paired reset recovers
stable input; original startup/config restore is readback checked. The bench is
released for bounded ExExt driver-resource reuse with a stable callback owner.


## Stream-r12 retained resources — unresolved physical repeat

Source47d230e779be459087756cac4f06347e84796367 builds full HDMI stream-r12,
app SHA256 `3607a08b85ccdfa1dae5f8c11e3db43ab806a52bccab3fbeea7e3cd865316ca4`.
All four segments verify. T09 no longer logs the prior GDMA allocation failure,
but saves no result and does not respond to normal CLI/listener recovery. HDMI
scanout remains60.07Hz with no reported native failure, panic or rolling faults.
Those counters do not establish payload integrity or successful game execution.
Paired and Agon-only reset attempts fail keyboard admission. Verified rollback
to stream-r10 restores input; Legacy listener confirms the T09 result is absent.
Original38byte startup and T09config are restored/readback checked. EMOS-r07
and mainboard fsim VDP remain unchanged. Bench released for offline isolation.

## Finite Aginvadors UART controls

Same finite120update fixture and assets;120ordered CSV rows per route, source255,
no flags or timer overflow. Rank by larger median active time. Percentages use
a16.6667ms60Hz budget; active excludes pacing. Both routes use EMOS-r07 and
full-HDMI stream-r10, mainboard fsim VDP unchanged. Not a stock VDP comparison.

|Route|Updates/s|Median active|60Hz budget used|p95active|Median submission|Median pacing|
|---|---:|---:|---:|---:|---:|---:|
|ExCom|51.06|14.631ms|87.78%|20.345ms|8.773ms|3.131ms|
|Legacy|51.06|14.216ms|85.30%|18.316ms|8.130ms|4.388ms|

ExCom median active is2.92% above Legacy (Legacy baseline). Original startup
restoration/readback passes after both. This is finite timing evidence, not
interactive acceptance or a60updates/s claim. First Rally control omitted
external road assets; runner corrected to include both tracks and restore
startup even if result retrieval fails. No Rally runtime pass/failure inferred.


## Stream-r13 internal retained DMA candidate

Source `c27a927db8a40f62dabe6f46030bad9b553ea07c` builds
`port-008-stream-r13-b2026-10-11-15-31-39Z`, app1781360bytes, SHA256
`1abba98a93a775a2ba629b12a2d33cc1b699592c2a44a62ad5e7455c35de4268`.
Full normal-HDMI build/validation passes. Host sanitizer checks pass246native
ExExt payload/retention/failure cases,24reused coordinator transfers and reset
cleanup, retained213native/319coordinator cases, and paired native controls.
Real P4 translation unit also compiles. The4KiB payload now uses the qualified
internal DMA allocation; resource reuse is unchanged. Physical gates follow.
