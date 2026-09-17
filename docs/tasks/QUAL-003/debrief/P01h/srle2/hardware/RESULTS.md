# SRLE2 physical P4 assessment

## Executive summary

**Keep the tested SRLE2 asset decoder; do not replace RLE2 live streaming with this SRLE2 encoder.** On matched512×384 Nurples trials, SRLE2 delivered 12.66 browser fps versus RLE2's 17.20: **-26.4% lower**, despite 75.0% smaller messages. Both maintained60 application cycles/s. The extra entropy pass costs about21ms per attempted frame in these runs. Smaller packets did not compensate for that cost.

The corrected P4 candidate passed39 original-golden codec controls and six routed full-frame asset checks. Hardware exposed and this task fixed an undersized command-task stack. An output-dependent mode-transition issue remains recorded separately; it invalidated the first game series. Final comparisons use one common test-only fixture with startup-owned mode20, avoiding mode changes during streaming. No EMOS source or mainboard VDP changes were required.

| Output | Trials | Application mean ms / fps | Browser receipt fps | Mean message bytes |
|---|---:|---:|---:|---:|
| Disabled | 1 | 16.667 / 60.00 | — | — |
| Raw | 1 | 16.667 / 60.00 | 7.39 | 196,640 |
| RLE2 | 3 | 16.667 / 60.00 | 17.20 | 23,501 |
| SRLE2 | 3 | 16.667 / 60.00 | 12.66 | 5,879 |

These are P4 variants, not a fresh mainboard comparison. No physical scanout or unique rendered-frame rate is inferred from application ticks or browser submissions.

## Matched game trials

| Pair | RLE2 receipt fps | SRLE2 receipt fps | SRLE2 change vs RLE2 | RLE2 p95 interval ms | SRLE2 p95 interval ms |
|---|---:|---:|---:|---:|---:|
| 1 | 17.60 | 12.95 | -26.5% | 91.6 | 101.7 |
| 2 | 16.48 | 12.67 | -23.1% | 92.1 | 101.7 |
| 3 | 17.53 | 12.36 | -29.5% | 91.4 | 103.7 |

Each run recorded1800 cycles and1799 intervals, all two MOS120Hz ticks (16.667ms), with no VDU fault flags or browser page errors. Output cap remained30Hz. Browser statistics use a central15-second window ending5seconds before final receipt, excluding loading/completion edges. WebGL submission cadence closely followed receipt cadence; it is not monitor scanout. Raw/RLE2/SRLE2 message types were EVF1/EVR1/EVS1 respectively. Three codec trials alternated; disabled/raw each ran once. Host used its current Wi-Fi connection and headless Chromium. Historical24.55fps RLE2 is not substituted for this same-candidate control.

Whole-observation device counters averaged roughly5.86–6.05ms per RLE2 pass and20.88–21.00ms per additional SRLE2 pass. Counter windows include startup/completion frames, unlike the central browser window. They quantify codec cost, not total rendering time, exclusive CPU time or a complete scheduling attribution. No SRLE2 failures were reported by those counters.

## Synthetic controls

| Static scene | RLE2 fps | SRLE2 fps | RLE2 message bytes | SRLE2 message bytes |
|---|---:|---:|---:|---:|
| incompressible | 8.56 | 3.64 | 196,640 | 1,152 |
| raw_sprites | 29.26 | 12.02 | 7,070 | 959 |
| bitmap_raw | 29.22 | 14.01 | 3,301 | 232 |

Twenty receipts per scene/codec, first two excluded. The fixture named `incompressible` is difficult for RLE2 but highly compressible by szip; it is not random entropy noise. Independent seeded-noise RPC controls took about676ms to encode, reinforcing that this encoder cannot be run unconditionally at30Hz. Static tests use real retained browser decoding and normal EMOS-routed drawing, not HTTP-injected pixels.

## Correctness, failure and correction

1. Twelve golden cases × encode/decode/unpack passed exact comparison against the original szip CLI; each ran one warmup and three measured repetitions. Three bounded corruptions were rejected and each was followed by valid recovery. HTTP task minimum reported stack reserve was11,996bytes. Free-heap differences are not peak allocation measurements.
2. Command65 two-layer CmpS→Cmpr→RGBA2222 passed full512×384 comparison for the raw reference, ordinary SRLE2, fragmented source, in-place replacement, wrong version and truncation. Invalid input preserved the existing destination. The checker includes transparent/opaque pixels; this is not exhaustive coverage of arbitrary alpha values or malicious entropy streams.
3. r02 crashed in `processLoop`: original szip `maketable` exceeded its4096-byte stack. Captured serial panic and ELF addresses established the cause; flash coredump storage had failed. r03 increases this task to16384bytes, retaining priority/affinity. HTTP already had16384bytes. All relevant controls passed on r03. No changes to EMOS or stock mainboard VDP.
4. The retained Nurples fixture changes title/game/exit modes. Continuous-output runs stayed at320×240; a sparse capture reached512×384. Original-startup retry reproduced the mismatch. Those timings are excluded. A one-byte test-only RET at the mode setter makes startup the sole mode owner. All final variants use that same derivative; production Nurples is unchanged. This avoids the transition issue and does not claim to fix it.

## Provenance and reproduction

Candidate: `srle2-p4-r03-b2026-09-17-04-05-02Z`, frozen correction commit `f17e943`. Original C codec source and licenses remain retained; wrappers/decoder live in the SRLE2 task silo. `fixed_fixture.py` verifies parent and derivative hashes. Mode20 is selected before fixture/browser startup. The parent is the retained single-vblank repair-based cadence fixture; game logic, addresses, resources and telemetry are unchanged.

`evidence/codec-r03.json`, `assets-r03.json`, `synthetic-r03.json` and compressed `game-r03/` contain the scoped results. Unpack game evidence to a fresh directory and run project-local Python on `hardware/analyze.py DIRECTORY` from repository root. The parser validates1800 cycles, telemetry and512×384 central-window samples. Private controller journals, images, flash receipts and informative failed runs remain under `agents/srle2-hardware/`. Build/run identities and fixture hashes distinguish this from historical tests. This is task-scoped experimental qualification, not a released product or exhaustive decoder-security qualification.

## Disposition

Retain command65 asset support and reusable decoder/tests for review. Do not enable SRLE2 live output by default or spend further time tuning it in this bounded run. RLE2 remains the comparison choice. Original P4 image and original Agon startup are being restored; final restoration/voice receipt will be recorded below. The mounted MOS-test card was never modified. Restored EMOS is unchanged; mainboard VDP remains stock2.16.0. General mode-transition investigation is a separately recorded, unscheduled follow-up.
