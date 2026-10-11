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
