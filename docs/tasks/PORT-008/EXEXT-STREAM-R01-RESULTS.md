# Ordinary ExExt — bounded results

**Disposition: failed performance experiment; restore the verified pre-goal UART
pair.** Ordinary ExExt VDU/reply routing and finite endpoint checks work, but
the measured adapter is unsuitable for normal use: Nurples reaches14.55updates/s
versus earlier ExCom60, and Lode Runner takes34.233s versus Legacy6.383s for
fixed emulated CPU work. Warm-reset admission is unreliable. Passing finite
checks do not establish playability, acceptable latency or production readiness.
The Author reports a major regression. Retain this evidence and the compiled,
uninstalled split-upload candidate; stop candidate installation. Production
selection remains unchanged. [Work contract](EXEXT-STREAM-R01.md) owns the
remaining investigation and qualification.

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


## Finite Rally UART controls

Same existing120update deterministic attract fixture, mode136, host-only
PRT markers (source255); all120ordered rows save with no timer overflow.
Road assets and binary are byte-readback verified on first deployment and
reused unchanged for ExCom; prior result is retained under the owned test
directory before invocation. Mainboard fsim VDP remains unchanged. Worst
median active work first; these are application measurements, not HDMI FPS.

|Route|Updates/s|Median active|60Hz budget used|p95active|Median submission|
|---|---:|---:|---:|---:|---:|
|ExCom|8.30|116.457ms|698.74%|176.458ms|64.512ms|
|Legacy|10.14|98.314ms|589.89%|127.934ms|53.884ms|

ExCom median active is18.45% above Legacy (Legacy baseline). This instrumented
fixture is not a60Hz pacing target; do not compare it to prior interactive FPS
without matching source/build/workload. The ExCom screen observer fails to
recognize completion on the graphical/custom-font display. Subsequent normal
CLI return/listener retrieves the fresh complete CSV **without any reset**,
then restores/readback-checks original startup. Treat that as durable finite
execution evidence, not a transport hang or interactive keyboard acceptance.


## Internal DMA physical controls and post-failure observation

All four installed stream-r13 segments verify. With EMOS-r07 unchanged, T01
and T03 each save 120 valid rows with no abort or invalid flags. T01 reaches
15.82 updates/s and T03 15.45; median query completion is 50.069/50.188 ms.
These fenced measurements include the request/return schedule and are not
raw parallel bandwidth. Original startup and both configurations are restored
and verified before the next invocation.

The separate unfenced T09 attempt produces no timing file. After its observer
deadline, intrusive USB-JTAG captures show the P4 process task actively polling
UART control, not blocked inside the renderer or PARLIO driver. Its ordinary
stream is active, receive and return queues empty, handover in UART, no pending
block, and no recorded transport failure. Retained stream bytes contain the
game's `AGNB image load failed: 02`, the fixture's setup-failure message and
MOS prompt text. Error 02 is the AGNB loader's FatFS-read error wrapper. The
actual FatFS status and failing offset have not yet been captured. This attempt
is a **setup failure, not a completed gameplay benchmark**. A zero allocation
failure count does not establish byte integrity.

The debugger resumes and detaches; OpenOCD closes without a firmware change or
requested reset. These halted observations are never timing evidence. A paired
reset and then verified stream-r10 rollback initially fail input admission.
After P4 initialization completes, one ordinary Agon-only reset restores input.
The Legacy listener finds no T09 file and restores/readback-checks the original
38-byte startup and T09 configuration. The boot-ordering failure remains open;
HTTP availability alone is insufficient proof that the P4 console owner is ready.

Local evidence indexes: focused-r04/exext-154654 and exext-155007, debug-r13
and debug-r13-state, bench-r14 installation/restoration, and after-r13-reset-r17.


## EMOS byte-append installation and first finite ExExt game

The complete 128 KiB installed EMOS-r08 ROM matches the retained image padded
with erased flash; SHA256
`a6fbd92d0587605eef9d57c00fe8ca86372d39bea7a4ddc248e673dc4f0e08bf`.
Original startup and stable neutral input verify. Stream-r13 is independently
reinstalled and all four segments verify; mainboard fsim VDP is unchanged.

Aginvadors mode 8 completes 120 ordered records on ExExt at 14.29 updates/s,
versus the preceding UART controls' 51.06. That is a 72.03% lower update rate
with Legacy as baseline; the EMOS/P4 builds also differ, so this is an observed
route/build comparison, not an isolated wire-bandwidth measurement. Seventy-two
records report fine-timer saturation; do not use their clipped PRT totals as
exact durations. The overall rate uses the full-run MOS clock. Fresh result
and original startup restoration/readback both pass. Local run index:
`games-r01/inv-exext-161420`. This is finite execution, not playability acceptance.

A fresh original T09 on this pair again returns to a freshly observed MOS
prompt with no completion marker. The host observer stops without resetting
the Agon; normal listener entry fails, requiring deliberate recovery. The
separate diagnostic will resolve the wrapped read-error status before a remedy.


## Nurples SD isolation and checked chip-select scheduling

1. A separately named, byte-verified diagnostic derivative changes only the
   existing loader error display. It reports **FRESULT01 / FR_DISK_ERR** at
   file offset **0x0487FC**, SP0x0BFF63. The frozen gameplay fixture and source
   remain untouched. This is a setup failure, not a completed timing run.
2. Stock MOSv3.0.2 owns active-low SD chip select PB4 and a100ms response-token
   deadline. Synchronous ExExt service in VBlank can preempt that foreground
   transaction. The bounded remedy defers physical ExExt work while PB4 is low;
   already-received packet publication and stock clock ticks continue. No stock
   SD timeout, parser or renderer is changed. Hardware causality remains a gate.
3. The initial compiled guard was rejected by the actual linked-eZ80 test:
   AgonDev exposed PB_DR as a numeric address, so the expression was constant.
   That image was **not flashed**. The reusable MOS builder now maps PB_DR0x9A
   through its existing volatile I/O facade and checks actual IN0 generation.
4. Corrected EMOS build `agon-emos-v0.1.24-b2026-10-11-16-39-51Z` is130,967bytes,
   with105bytes free. Image SHA256
   `b02c2f9f277dcd49d702d69d18d4b7a2f8cbb08457bbe942ec2f4b08693fc48a`.
   Real linked VBlank tests pass SD-selected deferral/resumption, nested and
   non-nested IRQ, ordered down/up callbacks, primary/alternate registers,
   IX/IY/SP/IFF. Host owner tests also preserve already-buffered publication
   while SD is selected. Physical installation and frozen T09 repeat follow.
5. Stream-r14 adds a one-time USB marker after boot pad fencing. All four flash
   segments verify, and the installer observes that marker before releasing
   held Agon reset. This **does not close reset qualification**: initial admission
   still fails and a later ordinary Agon-only reset recovers. Original startup
   and T09 config are restored/readback checked before the EMOS installation.


## SD-selected deferral — physical frozen Nurples pass

The corrected EMOS image independently matches a complete 128 KiB ROM readback
(SHA256 `431e27eb36679c53273e4a8a39e68eb5fde1dad34747932d5ab9b23cf1525d45`).
With stream-r14 and the same frozen unfenced T09 fixture, setup completes and
all 120 measured updates save, with zero fault/late rows or abort. Original
startup and configuration are restored/readback checked. This supports the
ExExt ISR/SD scheduling cause; it does not qualify every SD workload.

| Route/control | Application updates/s | Median active submission | Median whole update | Median pacing interval |
|---|---:|---:|---:|---:|
| ExExt, SD-selected deferral | 13.33 | 2.722 ms (16.33% of 60 Hz budget) | 67.035 ms | 63.819 ms |
| Earlier ExCom control | 60.00 | 5.778 ms (34.67%) | 16.549 ms | 10.757 ms |

ExExt application rate is 77.78% below the earlier ExCom control. Firmware
identities differ; this is not an isolated wire-bandwidth comparison. The
pacing interval includes preempting synchronous ExExt ISR work and therefore
must not be called spare CPU time. Scanout remains about 60 Hz. Finite gameplay
completion does not establish interactive playability or absence of flicker.


## Rally and paired-clock kernel checkpoint

Rally ExExt saves 120 ordered records and returns to an admitted MOS CLI.
Normal CLI collection retrieves the fresh result without a reset or replay;
the graphics screen sampler cannot read its completion text. Observed application
rate is 2.092 updates/s versus earlier ExCom 8.304 and Legacy 10.141. **117 rows
saturate the PRT counter**; clipped active/logic totals are not precise durations
or spare CPU percentages. These are finite execution results, not playability.

The paired-clock EMOS kernel passes 124 actual-linked byte/edge/register/ISR
interleaving cases and ten actual-ELF profile/mutation controls. For a4096-byte
payload with interrupts initially enabled, counted eZ80 instructions fall from
148,488 to103,080 forward (−30.58%) and148,052 to102,820 reverse (−30.55%).
These are instruction counts, not physical elapsed times. No renderer changes.
The new image is130,968bytes (104 free), build
`agon-emos-v0.1.24-b2026-10-11-16-52-19Z`, source
`2b75451b37402bfc0eb5fee8cd22fd8b8f3fd4ea`, image SHA256
`25196ce7b88a1e2f05ba3445f43d625623759ba304b51e58f9443c0b564677ca`.
Complete installed ROM readback matches SHA256
`e44c60b60359f64cc3a48a4559ce7ab4090fff0a7b742e4d4fd70adb517b6578`.
Startup is restored/readback checked, input ready/neutral. Physical comparison
uses the existing unmarked empty-loop control before frozen Nurples repetition.


## Paired-clock physical comparison and empty-loop isolation

P4 remains `port-008-stream-r14-b2026-10-11-16-29-33Z`; EMOS is the independently
ROM-verified `agon-emos-v0.1.24-b2026-10-11-16-52-19Z`. No mainboard VDP,
renderer, wiring or application pacing change. Browser video is disconnected.

Worst application rate first. Empty controls have120updates and no PRT overflow;
Nurples has120warm-up plus120measured updates and no fault/late/abort. Rate
uses nominal120MOS clock units/s; precise counters assume18.432MHz/256.

| Workload/route | Application updates/s | Median whole update | Median active work/submission | Comparison |
|---|---:|---:|---:|---|
| Nurples ExExt, preceding SD-corrected EMOS |13.33|67.035ms|2.722ms|Baseline for kernel comparison |
| Nurples ExExt, paired-clock EMOS |14.55|50.215ms|2.708ms|+9.09% rate; −25.09% median whole duration |
| Empty ExExt, paired-clock EMOS |59.02|16.646ms|0.00694ms|−1.64% rate vs matched Legacy empty control |
| Empty Legacy, same pair |60.00|16.625ms|0.00694ms|Empty-control baseline |
| Earlier Nurples ExCom |60.00|16.549ms|5.778ms|Latest ExExt rate remains75.76% lower; builds differ |

The paired kernel's31% instruction reduction is not a31% physical speedup.
Nurples's ExExt median pacing interval is47.750ms and includes preempting
synchronous transport ISR work; it is not spare CPU. Its95th-percentile active
interval is79.403ms (476.42% of a60Hz budget), so the small median does not
establish ample headroom. Empty ExExt whole-update p95 is20.448ms versus
Legacy16.628ms. The empty fixture issues no VDU during its measured window;
its result rejects a blanket claim that idle POLL alone lowers every loop to15Hz.

Raw ignored run indices: `focused-r04/exext-170750`,
`games-r01/empty-legacy-170333`, `games-r01/empty-exext-170525`.
Each original startup/configuration is restored and byte-readback verified.
Finite completion does not establish interactive playability or visual quality.


## Apple IIe Lode Runner — matched finite endpoint controls

P4stream-r14/EMOSpaired-clock image, browser disconnected, mode136 selected only
by startup. The existing consumer fixture executes524,288emulated instructions,
scripted Return and one real read-only DOS sector read; all256 final monochrome
pixel samples and disk/CPU endpoint checks pass on both routes. Exact assets
and executable are reused without alteration between runs.

| Measure | ExExt | Legacy/mainboard custom VDP | ExExt change vs Legacy |
|---|---:|---:|---:|
| Measured MOS-clock interval |4108ticks =34.233s|766ticks =6.383s|+436.29% elapsed time |
| Paced presentations during that interval |336|215|Adaptive work differs; not a fixed frame-count comparison |
| Derived paced presentations/s |9.81|33.68|−70.86%; not physical display FPS |
| Final sampled pixels matching |256/256|256/256|Same final pixel oracle |
| DOS reads/errors |1/0|1/0|Both pass |

The executed instruction budget matches but the real-time adaptive presenter
submits different frame counts. This is an end-to-end consumer comparison,
not isolated renderer or bus bandwidth. The raw16-bit flip-wait accumulator
has no overflow attribution; retain it as evidence, not precise headroom.
Host setup/waits/collection are excluded from the MOS-clock intervals. Raw runs:
`games-r01/loderunner-exext-171252` and `games-r01/loderunner-legacy-172052`.
Original startup is restored/readback checked, input ready/neutral after each.

## Split-upload progress control — candidate not yet installed

Execute the maintained P4 `ConsoleStream::readBytes` method with modeled
byte arrivals/ownership/clock boundaries. Its old unconditional sleep incurs
three ticks across three pending-handshake progress calls; the negative control
fails the no-sleep assertion. The candidate preserves exact split byte order,
idle waits, timeout and fault exit while promptly reentering pending blocks.
Four existing actual reset/parser tests and17queue/receipt cases also pass.
Normal full-HDMI stream-r15 compiles and validates, but remains uninstalled.
Its physical Nurples comparison is deferred after the regression report; this
source finding alone establishes neither the dominant bottleneck nor a speedup.


## Choplifter preparation admission failure

All isolated Choplifter assets verify byte-for-byte, but the startup reset on
P4stream-r14/EMOSpaired-clock does not regain keyboard admission. Two later
Agon-only resets also fail. No CD/LOAD/RUN is sent by that failed preparation;
there is no gameplay or performance result from it. A fresh paired reset,
without reflashing either board, restores stable input. The verified fixture
then receives its first explicit invocation through the resumed-once wrapper.
This is informative EX06 evidence: later Agon reset is not a guaranteed recovery,
and the boot-fence marker does not close reset qualification. Original startup
restoration remains mandatory when that finite invocation finishes.


## Choplifter — finite ExExt completion, no speedup claim

The first actual invocation after paired admission recovery completes both
existing native-core variants. Each executes4,194,304emulated instructions from
the retained maximum-difficulty state. All native endpoints pass;
`PERF015 status=0 log_failed=0`. The P4/EMOS pair is stream-r14/paired-clock r11,
browser disconnected, mode136 selected in startup. The earlier failed reset
attempts never invoked the application.

| Existing consumer variant | Raw MOS ticks | Nominal elapsed at120units/s | Display calls |
|---|---:|---:|---:|
| Baseline core |33134|276.117s|2718|
| Candidate core |32024|266.867s|2645|

These are separate emulator-core variants, not UART/parallel transport variants.
Adaptive presentation counts differ. Do not infer isolated graphics bandwidth,
HDMI FPS, interactive response or a matched UART speed ratio from this run.
The raw result is retained below; exact executable SHA256 is
`9c4915582788ccfe6851e242795958898513a715a698eb4965a929f8496e63e7`.

```text
PERF015 baseline=388ef52 candidate=3bad6f2 cumulative=1 difficulty=3 helicopter_collision_immune=1; TIME units=raw MOS ticks; variant 0=baseline 1=candidate
BEGIN choplifter-max 1 0 0
TIME choplifter-max 1 0 0 33134 2718
BEGIN choplifter-max 1 0 1
TIME choplifter-max 1 0 1 32024 2645
PASS: PERF014 all native endpoints
PERF015 status=0 log_failed=0
```

The host collector initially counts the header's `TIME units` as a third data
record and fails its post-collection assertion. It has already saved the raw
result, restored the original startup with byte readback and closed the listener.
Record-line validation confirms exactly two BEGIN and two numeric TIME records;
no rerun or reset is used to repair that metadata. This is a collector defect,
not a fixture or firmware failure.


## Regression decision — no ordinary-use acceptance

The Author's regression report agrees with the saved measurements. Functional
completion alone is insufficient. The current ordinary parallel adapter is not
accepted for gameplay or unattended ordinary use. The compiled stream-r15
split-upload change remains uninstalled; a plausible scheduling improvement
is not permission to leave the slower, reset-sensitive pair on the bench.

Application-rate comparisons, largest relative reduction first. Rates are
application updates/s, **not display FPS**; UART controls and ExExt candidates
use different component builds, so these establish end-to-end regression and
do not isolate one source change. Rally's117 and Aginvadors's72 overflowing
fine-timer rows cannot support precise PRT-duration/headroom comparisons.

| Workload | ExExt updates/s | Retained UART control updates/s | Rate change vs UART |
|---|---:|---:|---:|
| Nurples T09 |14.55|60.00 ExCom|−75.76%|
| Rally finite timing loop |2.09|8.30 ExCom|−74.81%|
| Aginvadors finite timing loop |14.29|51.06 ExCom|−72.02%|

Lode Runner's separate fixed-CPU-work comparison takes436.29%longer in ExExt;
its adaptive frame counts differ and its elapsed-time metric is not ranked
against these application-rate reductions. Choplifter only has the completed
ExExt pair above; no matched UART claim is made. Idle empty-loop controls stay
near60updates/s, so this is a loaded-workload regression. Root cause and the
benefit of the uninstalled candidate remain unproved. The required safe handback
is the exact pre-goal UART pair, independently verified, with the original
startup and mainboard consumer VDP preserved.


## Verified pre-goal UART rollback and Nurples control

After the Author reports the regression, EMOS is flashed once to its preserved
`agon-emos-v0.1.24-b2026-10-10-01-48-39Z` image, SHA256
`55aafe657987754bd6dcda0d2747d145702da9d995e90d9409e8509ccd41c343`.
Its complete128KiB ROM readback matches
`69d7b11ac1fa6fcd48cc3770356c3b8806d8f308c345bd670075a7eb21b613dd`.
The matching P4 `port-008-data-r20-b2026-10-11-09-07-32Z` is restored with
all four flash segments independently verified; app SHA256
`01cbd53255fbbae4760bc2ba64fc0f987cb9ef828b397d17a7cd7a64b9322771`.
Keyboard admission returns after the matched P4 restoration. The intervening
old-EMOS/new-P4 pair does not regain admission; it is not a supported pair.
No mainboard VDP, wiring, user application or selected production change.

The same frozen software-sprite Nurples T09 workload, mode20, completes120warm-up
and120measured updates on ExCom after rollback. Browser video is disconnected.
No workload, pacing, sprite or renderer modification is made for this control.

| Measure | Restored UART ExCom | Experimental ExExt | Scope |
|---|---:|---:|---|
| Application updates/s |60.00|14.55|ExExt75.76%below restored UART; same frozen workload, different firmware pairs |
| Median whole update |16.549ms|50.215ms|Unfenced submission/pacing, not renderer completion |
| Median active interval |5.653ms (33.92%of60Hz budget)|2.708ms|ExExt pacing includes preempting transport; its small active median is not headroom |
| Active interval p95 |6.056ms (36.33%of60Hz budget)|79.403ms (476.42%)|No overflow in either Nurples run |
| Valid measured updates / fault rows |120/0|120/0|Finite completion; not interactive Author acceptance |

The startup preparation's early epoch-stability assertion races a later input
admission during autoexec. Input then settles without another reset. The
maintained runner's CD/LOAD echo checks, fresh completion and saved result all
pass; the invocation is not replayed. Original startup and T09configuration
are byte-readback restored after completion. Raw rollback receipts and control
remain in the ignored local evidence index, not a new production bundle.


A subsequent cached-input control on the restored pair fails readiness while
sending its first CD command, before LOAD/RUN. It is not an input-fixture pass.
This demonstrates that warm-reset/admission unreliability is also observable
with the preserved pre-goal pair; attribution exclusively to the new ExExt
code is unsupported. No uncertain application invocation is replayed. Restore
normal startup and admitted neutral CLI input before releasing the bench.


Final handback: paired reset recovers the restored pair; the original38byte
startup is byte-readback restored, the listener is closed and reset is released.
Normal Legacy CLI accepts an ECHO command and input stays ready/neutral for
five seconds, held0/pending0. No fixture, collector, debugger or flash remains
active. Bench reservation is released. This is a usable handback, not broad
warm-reset qualification or a successful cached-input fixture run.
