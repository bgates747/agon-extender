# PARLIO and UART comparison baseline

The selected Olimex v0.3.0 stack has verified byte-for-byte parallel transfers
through 1.1 MB in both directions. The recent 541,408-byte EARTH PUT stopped
after transaction creation and before confirmed payload completion. A later
UART recovery uploaded that file and three additional inputs. This confirms a
useful recovery route. The timed-out transaction does not isolate the shared
GPIO handover, P4 DMA, UART completion or Agon media as the cause. A replacement
carrier should remove the handover risk and make these states distinguishable
without sacrificing normal MOS access.

## Exact production reference

The [selector](../../../production/current.yaml) binds the
[Olimex v0.3.0 manifest](../../../production/bundles/olimex-parlio-v0.3.0/bundle.yaml)
and the [current VDPlet v0.1.3-alpha companion](../../../production/companions/olimex-mainboard-vdplet-v0.1.3-alpha.yaml).
The companion is the ESP32 on the Agon mainboard. File payload travels between
the eZ80 and the Extender ESP32-P4. The display companion is not the SD data
peer. Its version still belongs in comparative run evidence because workload
and restart state can differ.

| Component | Selected build | Source commit | Selected binary SHA-256 |
| --- | --- | --- | --- |
| P4 app, 1,768,624 B | `port-008-upload-r05-b2026-11-18-03-43-16Z` | `be1d94329e55cc5e4243adbcdad73e3c530f9053` | `539dc7176f079bc6c298c48352b7e94c54db654fb6fdbb9c42897370fb19834b` |
| EMOS ROM, 131,072 B padded | `agon-emos-eirene-r06-b2026-11-18-02-44-46Z` | `abefa2f943eb3089c08d85bf39e48ebb4938f4bd` | `9b90b5d94ec6888d85ef1fa1acf23a82b2e0eb1f179b75f549863fbd72343673` |
| Agon SD listener, 26,127 B | `sdserve-v0.4.0-b2026-11-18-02-44-55Z` | `b949b7505f121b58623a94b31bb9b53a75b7819f` | `98492acc7dcd29e484ef76c69026e8801375738c33c617ba61a94d8481151f08` |

The exact selected EMOS binary also appears in the [r02 build record](../PORT-008/PRODUCTION-SD-PARALLEL-R02.md).
That record reports 129,922 unpadded ROM bytes, 1,150 free, and 3,388 bytes
available for listener heap and stack within its 32 KiB region. Budget new
resident instructions against the code actually removed. Budget listener
buffers and stack separately.

## How the file moves

1. Pi5 starts `EMOS sdserve --fast --parallel /` at an admitted Legacy MOS
   prompt. The Pi staged client POSTs the PUT bytes to P4 or an empty GET
   request. P4 manages a private local-card spool, binds boot/job IDs and
   reserves the console-owned UART request service. For PUT, P4 syncs the
   HTTP body to its card before starting mainboard I/O. For GET, P4 serves
   HTTP from a finished, synced snapshot. Parallel-required staging and
   collection demand matching capabilities on both processors. P4 retains
   a failed job for inspection, and a still-running worker can outlive a Pi
   stage timeout. [Staged protocol and lifecycle](../../protocols/mainboard-sd-staged.md)
2. For a nonempty PUT, P4 loads the complete spool into PSRAM before BEGIN.
   The listener creates its `.p17meta` and `.p17part` through Agon's FatFS.
   P4 sends UART operation 15, `SD_PARALLEL_WRITE` (transfer ID and size).
   EMOS parks UART1 and owns pad direction and the eZ80 clock/VALID.
   P4 drives eight shared Port C wires by externally clocked PARLIO DMA and
   drives READY. EMOS receives the block in up to 512-byte slices. The
   listener pauses clocks for each FatFS write. P4 requires the declared
   clock count and one VALID interval. It retires DMA and restores UART
   jointly with EMOS. The UART reply then confirms final offset. FINISH
   syncs/closes the partial file, and ACTIVATE replaces the live name under
   the existing transaction rules. [P4 staged engine](https://github.com/bgates747/agon-extender/blob/be1d94329e55cc5e4243adbcdad73e3c530f9053/vdp/video/extender/storage/fast/engine.hpp)
   · [EMOS private gateway](https://github.com/bgates747/agon-emos/blob/abefa2f943eb3089c08d85bf39e48ebb4938f4bd/src/emos_sdlink.c)
   · [Listener transactions](https://github.com/bgates747/agon-emos/blob/b949b7505f121b58623a94b31bb9b53a75b7819f/projects/sdserve/src/service.c)
3. For a nonempty GET, P4 STATs the file and requests at most 512 bytes at a
   time via UART operation 16, `SD_PARALLEL_READ` (job ID, offset, total, count
   and path). The listener reads the exact range into its buffer before EMOS
   parks UART1. The eZ80 drives data and clocks. P4 checks DMA receive length,
   clocks and VALID, both processors release the shared pins and restore UART,
   then P4 checks the correlated reply before appending the block to its spool.
   There is one handover in each 512-byte block. Count/identity checks and
   filesystem results are required even in checksum-free mode. Zero-byte
   operations use UART control messages only. [Staged protocol](../../protocols/mainboard-sd-staged.md)
   · [Physical handover contract](../PORT-008/HANDOVER.md)
4. Ordinary UART fast mode uses the same mainboard transaction and existing
   UART1 control carrier, with major-2 blocks of up to 212 PUT or 216 GET
   bytes. The direct recovery client makes an HTTP RPC per record. The
   P4-staged worker can instead issue local queue RPCs and stream a single
   HTTP body in each direction. Neither fast workflow routinely checksums
   or rereads uploaded contents. The Pi host tooling records elapsed time
   and first failure. P4 owns its spool, EMOS owns UART1/transport, and
   the listener owns Agon card files. [Host staged client](../../../scripts/sdcard_staged.py)
   · [Host direct client](../../../scripts/sdcard.py)

The device-to-device UART control path is the eZ80's UART1 on its Extender
connection. Agon UART0 to the native VDP, the USB programmer, application
network messages, VDU streaming, and P4-local file management follow their
own contracts. A new bulk SD carrier does not automatically migrate those
services. [Current service boundaries](../../mainboard-sd.md)

## Available measured rates

Decimal kB/s = 1,100 kB divided by host elapsed seconds in the table. Rows use
1,100,000 useful file bytes. Compare GET and PUT separately. Rows within each
direction are ordered by descending host time. Production PARLIO and prior UART
measurements are operational references from different dated campaigns. The
staged UART rate is a better planning comparison than the per-RPC rate.
The data does not supply a matched current-production UART/PARLIO A/B.

| Direction | Carrier and scope | Host s | Host kB/s | P4 worker s |
| --- | --- | ---: | ---: | ---: |
| GET | Historical checksum-free UART direct HTTP/RPC | 507.445 | 2.17 | — |
| GET | Historical staged UART with reopen-per-read control | 250.920 | 4.38 | 249.277 |
| GET | Historical staged UART with sequential-reader candidate | 43.573 | 25.24 | 42.100 |
| GET | Production PARLIO r03 | 31.556 | 34.86 | 30.084 |
| PUT | Historical checksum-free UART direct HTTP/RPC | 283.396 | 3.88 | — |
| PUT | Historical staged UART priority-4 worker | 43.240 | 25.44 | 40.814 |
| PUT | Production PARLIO r03 | 13.266 | 82.92 | 10.801 |

Sources are [r03 qualification](../PORT-008/PRODUCTION-SD-PARALLEL-R03-RESULT.md),
[direct fast baseline](../REMOTE-009/BASELINE-R01.md),
[priority comparison](../REMOTE-009/STAGED-RESULTS.md) and
[sequential reader comparison](../REMOTE-009/DOWNLOAD-RESULTS.md).
r03 covered 0, 1, 511, 512, 513, 4,097, 65,537 and 1,100,000 B with separate
qualification comparisons. The large GET took 2,149 parallel blocks. The
large PUT captured exactly 1,100,000 clocks and one VALID interval. The
~14.0 ms mean GET worker elapsed per block is whole-worker time divided by
the count, including queue, handover, FatFS and spool work. It is useful for
sizing admission overhead experiments, rather than a calibrated P4 or eZ80
CPU cost. UART1 at 1,152,000 baud 8N1 has a raw 115.2 kB/s ceiling per
direction before any framing, request/reply gaps or filesystem time. A
historical 8,192-byte eZ80-to-P4 *command stream* measured 340.35 kB/s
PARLIO and 100.60 kB/s UART sender drain. That benchmark excludes complete
file service and reverse transport. [Forward-rate comparison](../PORT-008/TRANSFER-RATE-COMPARISON-RESULTS.md)

The recent EARTH-001 stage's first eight successful PARLIO PUT receipts total
3,015,392 B in 50.920 s of **summed per-file host elapsed** (59.22 kB/s).
This excludes job startup, interfile gaps, recovery and the failed ninth
transfer. The successful control copy of `game.agnb` took 8.830 s for
541,408 B, while the following aligned copy of the same size later blocked.
The four UART recovery successes total 994,096 B, with per-file activation
receipts and no instrumented comparable whole-call rate. The two 32-byte
game reports are result retrieval proof, not a reverse speed measurement.

## Failure boundaries

| Incident | First proved boundary | What the record leaves open |
| --- | --- | --- |
| EARTH-001 November 26, 541,408-byte aligned `game.agnb` PUT after eight successes | Pi's 300 s stage supervisor expired while the started PUT remained on P4. The original P4 job and boot persisted, and the later original job ended phase 5, error 2, two accepted replies (HELLO and BEGIN), 0 confirmed payload bytes, filesystem status 0, no counters, and 402.165 s of worker time. Source puts the next exchange at operation 15. | Whether EMOS received operation 15, whether any clocks ran, whether Agon SD stalled while CLOCK paused, or whether UART return failed. The production upload exchange cap is 610 s and the observed earlier terminal time cannot by itself identify what ended the exchange. |
| EARTH-001 immediate second PARLIO attempt for the same target | New job on the same P4 boot ended error 4, remote status 8, 0 bytes and two records. Operation count includes the matched failure reply. This localizes the new refusal to BEGIN. The listener inspected state `06` (partial file and metadata). The operator cleared that transaction with explicit authorization, then got four UART activation receipts without touching the eight completed files. | This is a filesystem transaction recovery gate, rather than evidence of a second payload failure or of a card hardware fault. Removing PARLIO would not remove this gate. |
| BENCH-024 November 20, 177-byte PUT at position seven | Pi timed out at 300 s. Same P4 job/EMOS startup later returned error 2 at 611.964 s worker time, HELLO and BEGIN accepted, 0 bytes confirmed and no terminal pin counts. The source's 610 s exchange cap is consistent with the record. | Missing operation 15 receipt or missing reply after a possible payload. The exact 177-byte file passed alone and seventh. Later 10 × 7 controls passed without recovery with fresh SD paths/listeners and production VDPlet. Those 70 transfers do not establish a general failure probability. |
| PORT-008 r02 and earlier consumer captures | r02 lost listener admission on a 511-byte PUT and a 65,537-byte GET after 18 confirmed blocks (9,216 B). The corrected P4 boot-watcher race reproduces in the host model and r03 passed the selected campaign. Earlier cases saw extra VALID edges or wrong CLOCK totals with actual counters, prompting the fixed VALID filter. | Exact pin causes of the r02 field failures, later MP008 edge-count anomaly and later zero-count-completion stalls remain open. These are distinguishable from an uploader ROM sync error, app exit panic or success with wrong file contents. |

The EARTH timing and job evidence is retained in the Nurples EARTH-001 local
`bench-vl1` record. See `stage/blocked.json`,
`stage/stage-file-08.json`, `retry-file-08/prior-status.json`,
`uart-file-08/terminal.json`, `uart-file-08/inspect.json`, the four
activation receipts, and the paired result recovery record. The later aligned
app exit panic occurred after staging and produced a distinct VDP serial
capture. Both reports were collected and the original crash remains recorded.
For the comparable prior records, see the [open stall item](../PORT-008/PARLIO-UPLOAD-STALL.md),
[November controls](../BENCH-024.md), [r02 campaign](../PORT-008/PRODUCTION-SD-PARALLEL-R02.md),
[extra-VALID repair](../PORT-008/UPLOAD-REPAIR-R01.md) and the
[bench failure audit](../BENCH-022/FINDINGS.md). The source paths for the
ordering and timeout are [P4 staged engine](https://github.com/bgates747/agon-extender/blob/be1d94329e55cc5e4243adbcdad73e3c530f9053/vdp/video/extender/storage/fast/engine.hpp)
and [P4 queue bridge](https://github.com/bgates747/agon-extender/blob/be1d94329e55cc5e4243adbcdad73e3c530f9053/vdp/video/extender/storage/fast/http.cpp).
There is no demonstrated silent corruption among the retained reported
failures. Exact byte comparison remains appropriate in controlled
qualification.

## Consequences for the serial candidates

A dedicated payload bus can eliminate the Port C UART parking and reciprocal
pad release, PARLIO DMA/filter lifecycle and extra CLOCK/VALID checks. Where
UART remains the control channel, a new payload bus still inherits console
queue admission, stale session/boot handling, control replies and deadlines.
Any design still inherits P4 staging and resource pressure, Agon card
ownership/FatFS errors, transaction cleanup and power-loss semantics. Keeping
the same 512-byte read RPC loop may preserve much of the fixed per-block
delay. Test larger bounded windows separately from carrier selection, preserving
SD service responsiveness and both endpoints' memory limits.

When a run fails, obtain contemporaneous boot/job IDs, producer/consumer
stages, hardware transaction counters, Agon listener/keyboard status and
both deadlines before resetting. A retained or retrievable snapshot requires
known completed bytes. Missing proof should have an explicit terminal result.
For a future A/B, preserve the same fixture, file sizes and order, SD media,
firmware outside the transport delta, startup, and load. Measure actual
host, worker and bus intervals separately. Include no-P4 boot and injected
peer-loss cases, observe both storage transaction states, and preserve the
UART compatibility path when its endpoint remains available.
