# Nurples parity measurements

## Executive summary

**Gameplay parity claims below are invalidated.** The fixture used MOS SAVE
without checking its return value. Stock MOS and installed EMOS open with
`FA_CREATE_NEW`; an existing NPRES.BIN is not replaced. Later COPY commands
therefore reused the first saved pilot. The repeated600-record fingerprints and
60Hz timing comparisons do not establish subsequent game execution/timing.
Retain them as invalid evidence, not performance results. The r03 longer trial
exposed the flaw by returning the old NP01/600-record file.

The first corrected NP04 run verifies its expected nonce, sprite mode, capacity
and size:2,400 fenced P4 SW boundaries,29.57FPS mean,33.333ms p95,50ms maximum,
and13 live sprites maximum. This includes the per-frame completion query;
the repeat matches. Fresh mainboard measures58.76 fencedFPS. Unfenced
boundaries are60.00FPS mainboard versus33.86FPS P4, with matching game state.
The current images predate qualified UART optimizations; a bounded P4-only
comparison is next after HW controls. No parity claim is restored yet.
See verified-sw-controls-r27.json for the fresh paired evidence.

Independent browser/EVF, packet and drained P4 output-recorder measurements
remain valid within their stated scopes. Their output improvements do not prove
game parity. Next: checked fixture I/O, unique per-run nonce and format/variant
validation, then fresh matched runs. This is a benchmark-harness defect, not
an identified MOS/VDP port defect. No firmware API change is warranted.

The historical sections below preserve what was reported and must be read with
this correction.

## Pilot validation

Probe r01 SW binary hash is pinned in ../fixture-builds.json. Source and repair
assets are pinned in ../reference.json. Results: legacy-pilot.json; raw fixed-size
record retained in ignored bench evidence. All600 records show game_playing and
player_alive, with23 distinct PRNG states; this was not an idle menu. Shields
remain64. These compact records validate coarse state progression, not every
sprite, pixel or collision. More demanding loads may still be required.

The measured interval includes game work, query/return and ordinary vblank wait.
Stock's pixel query drains queued primitives and updates software sprites. It
does not prove hardware-sprite scanout. Tick quantization is8.333ms; no finer
instantaneous timing claim is made.

Initial asset/fixture staging with both staging and final readbacks took
**1636.1 seconds (27.27 minutes)**. This is deployment time, not gameplay time.
All files activated and read back successfully. Subsequent runs reuse the pinned
assets; do not repeat the large upload without a reason.

## First matched P4 control (no web output)

| Same r01 SW workload | Mainboard | P4, no web client | P4 elapsed difference |
|---|---:|---:|---:|
| Mean completed frame (ms) | 16.667 | 16.667 | 0.00% |
| Completed frames/s | 60.0 | 60.0 | 0.00% |
| p95 completed frame (ms) | 16.667 | 16.667 | 0.00% |

Both600-record fingerprints match exactly. Every479 post-warmup interval is two
clock ticks on each route. This does not measure spare CPU budget or establish
parity with web streaming/heavier sprite loads. Evidence: no-output-pair.json
and raw NPL1.BIN/NPE1.BIN.

Collector correction: after reset, use a fresh SD client state. The first host
collector reused its pre-reset state and correctly refused the changed service
identity. A fresh client retrieved the completed result without rerunning or
resetting the game. This was not a gameplay/firmware failure.

## Active web pilot: game work matches, viewing does not

The r01 P4 SW pilot with the production web client connected again records600
successful boundaries, the same state fingerprint, and60.0 completedFPS. The
browser remained connected through reset/loading/gameplay/terminal service,
without page errors or socket closure. Raw NPE2.BIN and web-pair.json retained.

| Output observation | Received FPS | Scope |
|---|---:|---|
| Production client, whole pilot observation | 7.79 | Includes loading and terminal surface |
| Production client, last10seconds | 7.66 | Window near gameplay end; not an exact game-only boundary |
| Static terminal surface, receive-only10s | 8.93 | Bypasses presentation, same512x384 RGB222 payload |

No parity success is claimed. Low visible delivery remains material despite
matched game completion. Output and then heavier/repeated workloads require
further work. Headless production observation and EVF captures remain in ignored
bench evidence, with served web assets and observer hashes. The terminal capture
shows Nurples scenery/HUD plus fixture/MOS completion text.

## Hardware-sprite pilot

Both routes complete600 boundaries without query failures. The479 post-warmup
intervals are all16.667ms, and both state fingerprints equal the SW pilot.
Evidence: hardware-sprite-pair.json and NPHL1.BIN/NPHE1.BIN. P4 production
web capture remains connected throughout both runs; its final10second delivery
is7.12FPS. The terminal output shows the expected same scene, plus test/MOS
text. A single terminal image is not a complete animation/scanout oracle.

These HW timestamps are command/drawing boundaries, not measured physical
hardware-sprite scanout; retain this distinction in summaries and comparisons.

## Wired host control, same static HW surface

| Consumer | Laptop Wi-Fi receivedFPS | Wired Pi receivedFPS |
|---|---:|---:|
| Production presentation | 7.12 (last10s of HW run) | 19.93 (static10s) |
| Immediate credit, no presentation | 8.93 (prior SW static surface) | 28.91 (HW static10s) |

The laptop/Pi comparison changes host and network; the left observations are not
identical static HW windows. It nevertheless rules out treating7–9FPS as an
intrinsic P4 drawing rate. The stronger paired Pi control uses the same static
HW surface and10second windows. Exact records/served assets remain in ignored
bench evidence. Both Pi captures report512x384 RGB222, no sequence gaps, and
no observer errors. This still does not achieve60FPS visible output.

## Drained output timings (r24 diagnostic, wired Pi)

| Client | Snapshot mean(ms) | Socket-send mean(ms) | Complete snapshot/send counts | ReceivedFPS |
|---|---:|---:|---:|---:|
| Production | 11.413 | 15.731 | 201/201 | 20.00 |
| Immediate credit | 11.439 | 15.824 | 297/297 | 29.70 |

All pixel/message unit totals match complete512x384 work; no loss/overlap/errors.
These socket times measure acceptance by complete-send calls, not network ACK
or monitor presentation. Credits were gated and the final granted frame drained
before reading counters and closing. This resolves the prior large-surface
incomplete-send accounting gap. Rates reproduce the uninstrumented wired
controls closely. Snapshot and send currently serialize; bounded lookahead is
the next agent-assigned experiment. No optimization success yet.

## First correction: bounded lookahead (r25 diagnostic)

| Wired client | r24 receivedFPS | r25 receivedFPS | FPS change |
|---|---:|---:|---:|
| Production | 20.00 | 24.64 | +23.22% |
| Immediate credit | 29.70 | 32.67 | +10.01% |

Drained accounting passes. In the receive-only window, snapshot time rises to
14.317ms and socket-send wall time to18.070ms while stages overlap. This suggests
shared-resource/scheduling costs limit the benefit; it does not identify their
individual CPU costs. The no-web Nurples HW pilot still completes600 boundaries
at60FPS with the identical state fingerprint. Active wired gameplay and heavier
loads remain required; this is provisional output progress, not goal completion.

Host orchestration needed two routine corrections: wait for actual keyboard
readiness after reset, and wait for a detached job's initial result file to exist.
Both resumed without rerunning/resetting the in-flight game.

## Second correction: packed RGB222 rows (r26 diagnostic)

| Wired client | r25 received FPS | r26 received FPS | FPS change | r26 snapshot mean (ms) | r26 socket mean (ms) |
|---|---:|---:|---:|---:|---:|
| Production | 24.64 | 29.69 | +20.48% | 9.163 | 16.464 |
| Immediate credit | 32.67 | 33.45 | +2.40% | 10.180 | 17.929 |

Complete drained counts are297/297 and335/335 respectively, without recorder
or observer errors. The same no-web hardware-sprite pilot retains60Hz and the
matching state fingerprint. These are static output and no-web game results,
not active wired gameplay qualification. The optimization reduces snapshot cost
but leaves substantial output overhead. See packed-row-comparison.json and
NPHP1.BIN. Build/deploy/game/output pipeline elapsed185.114seconds; this includes
preparation and retrieval, not just gameplay.

## Active wired gameplay (r26)

Both sprite variants retain600 records and60Hz boundaries with identical state
fingerprints. The production browser receives frames before reset and remains
active through terminal service; no socket closure or page error. Whole-window
FPS includes loading and the terminal surface and is not game-only scanout.
See wired-active-r26.json for separate timing scopes and coverage. The two-run
preparation/game/retrieval pipeline took165.231seconds.

## Wired packet timing control

Header-only receive-only capture retains69,785packets, zero kernel drops.
Median payload span17.10ms; median payload-tail to next EVF7.19ms. Browser
credit follows the payload tail by0.80ms, and next EVF follows credit by6.30ms.
These suggest further server-side waiting, rather than attributing the entire
gap to wire capacity. Two-byte WS headers belonging to the next message are
excluded from the preceding payload span; host offload coalesces some packets.
Raw capture is ignored; aggregate evidence is tcp-cycles.json/tcp-analysis-r26.json.
The simultaneous recorder window was rejected for a pre-existing lost completion
count; no firmware-duration conclusion comes from that failed diagnostic window.
Actual ELF confirms a1ms worker wait and packed word accesses. CMake's compile
database omits relevant SCons flags and must not substitute for that inspection.

## Dispatch diagnosis (r27)

| Wired client | Snapshot mean ms | Socket mean ms | Credit to ready mean ms | Ready to send mean ms | Received FPS |
|---|---:|---:|---:|---:|---:|
| Production | 9.247 | 18.940 | 0.589 | 0.105 | 23.79 |
| Immediate credit | 10.171 | 18.022 | 3.905 | 0.219 | 32.15 |

Clean drained accounting passes. HTTP dispatch queue waiting is small; these
results do not justify changing its scheduler. Production delivery varies from
the prior29.69FPS run, so that gain is provisional. The same no-web HW pilot
retains60Hz/state equality. No stock drawing logic changed. See dispatch-r27.json.
Host recorder/optional interval tests pass, including32-bit clock wraparound.

Headless browser screenshot capture on the wired Pi yielded a white canvas,
while the retained EVF pixel payload decodes to the expected Nurples scenery
and terminal text. Do not use that screenshot as visual proof; decoded EVF and
human browser presentation are distinct evidence.

## Unfenced pilot control

Both routes retain60Hz submission/vblank boundaries and the same600-record
state fingerprint without the per-frame query. Corrected terminal fences pass.
See unfenced-r02-pair.json, NPFL2.BIN and NPFE2.BIN. No pacing difference is
observable at this clock granularity; query CPU/transport cost may fit within
vblank slack. These timestamps are explicitly not per-frame drawing completion.
Initial fixture deployment plus the two observation runs took307.460seconds.

## Verified repeated P4 SW runs

NP04 uses distinct expected per-run nonces and checked file operations. Both
2400-record runs pass identity/size/variant/capacity checks and yield the same
state fingerprint. Their fenced means are29.5718 and29.5654FPS, p95 33.333ms,
maximum50ms, with13 live sprites at peak. This establishes repeatability of
this instrumented workload, not mainboard parity or unfenced normal-game FPS.
See verified-two-run-identity.json and NPV4E1.BIN/NPV4E2.BIN. Initial staging plus
the two bounded browser runs took494.767seconds.

## Fresh software-sprite comparison (NP04, r27 P4 / unchanged bench EMOS)

Worst elapsed-time excess first. Every case has2400records, the same state
fingerprint and13 live sprites at peak. P4 production web is connected throughout.

| Boundary | Mainboard mean ms | P4 mean ms | P4 elapsed excess | Mainboard FPS | P4 FPS |
|---|---:|---:|---:|---:|---:|
| Per-frame query/drawing fence | 17.018 | 33.816 | +98.71% | 58.76 | 29.57 |
| Unfenced submission/vblank | 16.667 | 29.530 | +77.18% | 60.00 | 33.86 |

Thus the gap is not solely the completion query. These are fresh nonce-verified
records; do not substitute old pilot data. The running P4/EMOS images predate
the qualified E07P UART changes that were subsequently restored away. A bounded
P4-only comparison will reapply the already-maintained owner/stream alignment
while holding MOS fixed; no new UART algorithm is proposed. HW comparisons
remain in progress. See verified-sw-controls-r27.json.
