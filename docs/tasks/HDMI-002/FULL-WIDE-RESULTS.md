# Full684-wide rolling integration — 2026-10-07

## Executive summary

The reviewed684×384 HDMI timing now runs in full Extender firmware: Ethernet,
P4 SD, EMOS input and the existing one/16-hardware-sprite fixtures pass their
bounded checks. Marked deterministic Nurples fails around the warm-up/measurement boundary and P4 restarts.
A saved core identifies destruction of a timing-marker BufferStream's invalid
mutex, not an interrupt-stack crash. The marker-disabled control completes all
3600 updates at nominal60/s, with zero timing faults and median57% active-work
headroom. Author reports fantastic, flicker-free gameplay with slight tearing
one-third down the picture. However, internal free RAM falls to83bytes, HTTP
accepts fail, and P4 crashes clearing game buffers at exit. This is a rendering
success with a memory/stability blocker, not a qualified firmware or promotion.
Exact full848 rollback and original startup/configuration are restored.

The logical512×384 image remains unscaled at(86,0). Twelve32-row DMA blocks
reuse three internal SRAM slots totaling196992bytes; the1600µs abort, stock
sprite scanline painter, accepted copy-scroll renderer, timing tuple and bridge
component remain unchanged. EMOS, normal games/assets and selected production
are unchanged. [The task contract](../HDMI-002.md) owns the next gate.

## Handback correction and continuation

After the recorded restoration, the Author reports that the old848 image is
non-working for hardware-sprite Nurples. Its successful service recovery must
not be presented as successful gameplay. The next work continues the684 rolling
candidate, with allocation-failure diagnosis before a bounded placement remedy.
That continuation is now recorded in [memory remedy results](MEMORY-RESULTS.md):
the latest684 image passes the marked workload and ordinary game entry/exit,
and remains installed for Author review. The failed-build measurements below
are preserved historical evidence, not current installed-state instructions.
Original timing/core evidence below remains unchanged. Do not infer which image
is installed from this historical result; consult the local installed receipt.

## Results, failures first

| Check |684-wide rolling candidate|Disposition|
|---|---|---|
| Marked Nurples3600, original attempt | Blue then black after first enemy fireball; P4 restarts; aborted header,0 measured rows | Fail; no useful game timing |
| Same marked fixture, deliberate repeat | P4 restarts; saved core resolves invalid mutex in BufferStream destruction | Fail; diagnosis retained |
| Marker-disabled Nurples3600 exit/services | Internal free RAM83bytes; HTTP accepts fail; invalid mutex while clearing buffers | Fail; same class of crash without markers |
| Marker-disabled Nurples3600 workload |3600 clean updates at nominal60/s; median active43%,p95 active53.25% of budget | Workload/timing pass; not a clean-exit or service pass |
| Case54,16 hardware sprites |402 clean updates, nominal60/s; p95 command completion3.333ms,20.0% of60Hz budget | Bounded pass |
| Case50,one hardware sprite |403 clean updates, nominal60/s; p95 command completion0.917ms,5.5% of60Hz budget | Bounded pass |
| Idle output | Approximately60 DMA frames/s; about58KiB internal free after startup | Progress evidence only |
| Normal services | Ethernet, mounted P4 SD and fresh EMOS input admission; agent commands operate the foreground listener | Bounded pass; no separate physical-keypress trial |
| Host/build |11 build-option tests;684-wide real renderer; ASan/UBSan scene checks at848/512/684; compiled C/C++ geometry and negative-definition guard | Pass; not physical picture evidence |

These small fixtures use16×16 sprite art and are not equivalent to the game's
larger overlapping sprites and scrolling. PRT uses nominal72000counts/s and raw
MOS units120/s. A60Hz budget is16.667ms; percentages above are interval/16.667ms.
Completion is the eZ80 submission-to-reply interval, not full scanout composition.
No calibrated optical refresh or mainboard comparison was performed here.

| Scanout observation | One sprite |16 sprites |
|---|---:|---:|
| Maximum observed complete strip refill |846µs|1106µs|
| Maximum observed DMA-copy interval |803µs|828µs|
| Maximum observed CPU composition |66µs|813µs|
| Minimum observed ready lead |1164µs|955µs|
| Invalid/underrun/sequence/late/overlap/fault counters |0|0|

Counters are cumulative captures, not reset per-case isolated distributions.
Independent maxima must not be added. Sprite work moved into scanout callbacks;
reduced task preparation does not mean the work disappeared. Clean counters do
not substitute for the Author's visible-picture review.

The marker-disabled control sustains six consecutive10.005-second output
windows at60.068–60.071 updates/s and matching DMA cadence. Maximum retained
strip refill903µs, DMA-copy interval858µs, composition280µs and minimum ready
lead1131µs; all recorded scanout-error counters remain zero. These are observed
intervals, not promises about more heavily populated scenes. Its3600 state,
phase, actor/projectile, map and RNG checkpoints match the retained848-wide
software-sprite run exactly. Maximum retained enemies5 and player projectiles4;
this is not a32-sprite gameplay population proof.

The actual saved eZ80 result is86528bytes, abort=false, fault_rows=0, late_rows=0;
no update exceeds the nominal60Hz budget. Median active work7.167ms (43% of a
16.667ms budget),95th percentile8.875ms (53.25%), maximum11.847ms (71.08%).
Median active-work headroom is57%; this is not an arithmetic-average statistic.
P4 aggregate markers are disabled and no corresponding phase-window comparison
is available. The final fence drains in44 nominal PRT counts before cleanup.
See [portable measured result](FULL-WIDE-RESULT.json).

## Failure evidence and diagnosis

The exact full candidate is `rgb-001-r04-b2026-10-07-13-47-13Z`, factory SHA256
`83f8f1bc1fe086ddc53bcd32c4658ed5c47954ed9e8525beda274b1f05dfeaa2`.
All four flash segments were independently verified. The frozen hardware game
companion is `scan-scroll-suite-r03-b2026-10-07-06-32-42Z`,38728bytes,
SHA256 `0999e9f99e8b580823f1398c38275d49788add1da4675f2bf2afbcc1a28583da`.
It reproduces the repaired-game r02 fixture before changing only hardware-sprite
admission/type and fixture identity. See [integration](../SPRITE-001/INTEGRATION.md).

The original and repeated marked runs use distinct tags740228/148265 and fresh
SD result directories. Each recovered128-byte header reports case9,expected3600,
warm-up120,abort=true,count0 and saturated final fence65535. These files were
retrieved during recovery. No recovery sample is a performance result, and no
in-memory P4 window survived the restart.

The repeated firmware's61440-byte core partition has SHA256
`f34cc54dd349bb8f3cafb1f685a7380123f539528993328f52b45bde8218bbc8`.
Decoding with its exact application ELF identifies:

1. Task `processLoop`, explicitly not interrupt context; used/free stack1008/3080.
2. `VDUStreamProcessor::bufferWrite`, bufferID65535, destroys a
   `shared_ptr<BufferStream>` control block.
3. `pthread_mutex_destroy` dereferences mutex handle0x48000014 and tries to take
   semaphore0x15541865, outside valid data RAM.
4. The carrier is the fixture's B009 aggregate timing marker. Source:
   [`bufferWrite`](../../../vdp/video/vdu_buffered.h), with marker generation in
   the retained scan fixture's `runner.inc`. Markers occur around the measured
   window after warm-up; the first fireball is a visual correlation, not a proven
   projectile-rendering cause.

The marked core alone did not demonstrate allocation failure. Pinned
IDF5.5.5 `pthread_mutex_init` can fail allocating its FreeRTOS semaphore, while
this compiler's libstdc++ mutex initialization wrapper ignores the returned
error. An uninitialized handle is therefore plausible; corruption/lifetime
errors have not been excluded by that core. Do not patch stock VDP, libstdc++, or the pinned SDK
on this evidence alone. The current renderer/DMA paths are also not exonerated.

The initial serial capture missed the panic. Its subsequent factory rollback
overwrote the core partition. The repeat's separately spawned capture child did
not survive its parent execution session, so it also yields no serial transcript;
its core was preserved before reflashing. Future capture orchestration must wait
for the child, close the serial descriptor, and preserve the core before recovery.
This recording failure does not invalidate the independently saved core.

The marker-disabled control provides independent evidence: its retained95-second
serial capture records internal free RAM falling from57699 to83bytes during
loading, then staying at83 throughout the measured game. PSRAM still has about
28.8MB free. HTTP connection accepts fail while rendering continues. This
demonstrates internal-memory exhaustion, not exhaustion of PSRAM or flash.
The exact failing allocation call remains to be captured.

Its second saved core has SHA256
`acc6303e6ba55e51c2505b68f838f39e4b0c19271af8f127b7a513e8c2123775`.
The same invalid mutex/semaphore values occur in `processLoop`, now under
`bufferClear`/`buffers.clear()` destroying ordinary BufferStream objects. This
matches the game fixture's cleanup after3600 updates and rules out removing
timing markers as a sufficient remedy. No ISR crash or strip deadline miss is
observed. Exact allocation/lifetime causality still needs targeted proof;
recovering internal headroom is the next remedy boundary. Keep the existing
renderer and timing, and avoid an upstream mutex/destructor workaround.

## Evidence and restoration

Ignored local evidence is under `agents/sprite001/integration/wide684`, with
build/flash artifacts in the adjacent exact build directory. Small runs:
`BENCH-009-2026-10-07-14-00-55Z` and `BENCH-009-2026-10-07-14-03-04Z`.
Agon results are under `/agents/extender/results/spr01-w684-small`,
`spr01-w684-game`, `spr01-w684-game-r2` and `spr01-w684-game-um`. Source snapshots, byte manifests,
PRT records, raw core, decoded stack and restoration receipts are retained.

All three attempts were followed by exact full848 rollback, segment
readback, byte-verified original38-byte startup and original128-byte fixture
configuration restoration, then a normal Agon reset and admitted neutral input.
A recovery boot can encounter the retained result and exit without overwriting
it; it is excluded from measurements. Ordinary software/hardware game binaries
and assets remain untouched. The marker-disabled result was already present and
its recovery boot did not rerun the measurement or send Escape. Its3600 records
therefore belong to the original candidate run; recovery is not their source.
Final read-only checks confirm admitted neutral input, no held/pending keys,
mounted P4 SD, offline idle Agon listener and no open diagnostic windows.
Machine-local installed state is in `HARDWARE.local.md`, not inferred from an
earlier receipt. No active fixture/capture/reset/transfer remains. No commit,
push, production promotion,240-line timing trial or ordinary manual game launch
was performed in this tranche.
