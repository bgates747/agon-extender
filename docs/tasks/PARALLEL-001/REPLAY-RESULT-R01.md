# Real-module parallel replay — first strict VALID failure

The small guarded graphics control passed on bench59, but the next real-module
replay failed after two native frame returns. P4 completed the requested118bytes
and DMA, then rejected three VALID edges against the unchanged strict-two
requirement. The fault is preserved; working UART operation was fully restored
and bench60 released before Wolf's fresh admission. This narrows the failing
workload without establishing an electrical cause or qualifying parallel use.

## Actual observations

| Witness | Actual result | Meaning / limit |
|---|---|---|
| Selected workload | One24-turn deterministic real-client/module replay | No game, second attempt, extra echo or filter case |
| P4 reverse transfer | requested118B, DMA done1, bytes118, VALID1, edges3, result5 | Complete bytes/DMA do not satisfy strict edge proof |
| P4 completion | native completion phase12, pending1, session3 | First informative failure retained |
| Host | Two intents, then connection closed | No24-turn completion claim |
| Native RAM | Two decisions and two FRAME returns | Failure occurred after successful frame returns; not first-frame deadlock |
| First application error | SUBMIT132, POLL, query16/clientquery15, pending0, BUSY/retries0 | Query16 is not equated with FRAME2 merely from length |
| Renderer RAM | No current borrowed/pending batch; rendering idle | Does not prove transport cleanup succeeded |
| Native cleanup | phase2, close0, cleanup/end uncompleted | Original CLI remained unknown until recovery |

The exact-map decoder verified native/object/map/code witnesses. Full65536B
application RAM at040000 was saved **before any subsequent LOAD**, SHA256
`a5d8401f10a90ac070fbe4b2dfb7fcd65c39f2a4a3dcca2ac2b10ced9b76be2e`.
Both endpoint captures, original150s observation, transaction journals and
first-fault bytes remain in the ignored owner/consumer evidence records.

## Exact EMOS first-fault interpretation

Matched EMOS source `71552879cb7e60f656ecbbc5c964ddd0e40fa416`,
`src/emos_keyboard_io.asm`, defines the private16-byte record. The immutable
first sample is `0103000003000060fb03aa5802000004`:

| Field | Value | Source interpretation |
|---|---|---|
| Reason |1| Deadline |
| Original / remaining |3B /3B| Zero control-prefix transmit progress |
| Already-read UART1 LSR |0x60| Clean sample; THRE and TEMT set |
| Already-read Port C |0xfb| PC3 active-low peer CTS is high: blocked |
| Sample-valid mask |3| Both status samples are present |
| Elapsed |600 MOS ticks| Nominal5seconds at120Hz; no added calibration claim |
| Remaining no-progress fuse |0x040000| Clock deadline, not fuse exhaustion |

The source tests **PC3**, not PC2. PC2 controls the opposite-direction peer
stop signal. No additional acknowledging UART read or live probe was performed
to interpret this saved sample. P4's earlier strict VALID rejection and later
blocked control transmission are correlated observations; the origin of the
extra counted edge remains unresolved.

## Recovery and restoration

1. MechAgon let the original150s observation expire, joined every runner/host/
   passive-reader actor, then explicitly returned sole operation to Extender.
   No uncertain test or transfer was replayed.
2. The standing Agon-only recovery failed input readiness. One paired P4 reset
   observed the exact build and released boot pads, but an HTTP observer timed
   out before issuing the paired Agon reset. The failed observer is preserved.
3. A separately source-frozen bounded continuation reconciled that already
   initialized P4 read-only, recorded fresh healthy display observation, and
   completed only the missing Agon reset. It does not relabel the original
   observer as passing or repeat P4 reset. Actual CLI and RAM preservation
   followed before LOAD or firmware installation.
4. Extender restored full131072B UART EMOSa25f and independently compared its
   complete ROM. Extender restored and independently compared the entire
   maximum1765376B touched P4 application span, including retained suffix:
   SHA256 `629aab118e03e7b42b3235d7eed633b6103931273d524f097ef446e92fc3d17f`.
   UART P4d9bcb boot/input/actual CLI passed separately. Bootloader, partitions,
   NVS and current mainboard5d657/profile8 were not replaced.
5. Selected postgetter confirmed exact original feature absence and ordered
   callback/buffer retirement. Fresh mode0/callback0/Legacy0, unchanged whole
   startup/listener, CLI/cursor, neutral input, offline listener, idle worker,
   free USB ports and joined actors passed. SD remains mounted.
6. Actual60 clean release: `2026-11-06T21:33:53.589941+00:00`. Wolf's normal
   fresh61 admission followed, with155 frozen comparison inputs and sole Wolf
   operation. Its fill comparison retains the qualified ordinary carrier.

## Next discriminator and remaining goal

The [fixed VALID-filter comparison](VALID-FILTER-COMPARISON-R01.md) changes only
the published P4 VALID input filter against this same24-turn corpus and strict
proof. It requires a new immutable consumer/owner kit and fresh FIFO admission
behind Wolf. It is not a second test under60 or a claimed electrical repair.

The [independent176-record repeated matrix](REPEAT-MATRIX-R01.md) has checked
host/native builds; physical repeatability is still pending. An agreed Wolf
eight-bit endpoint and actual matched Wolf integration also remain necessary.
The persistent goal is active; no production promotion or general speed claim
follows from either isolated control or this informative failure.
