# Forward communication performance — physical r01 result

Eight-bit parallel improves the larger tested ordinary VDU transfers on the matched diagnostic pair. At 8192 stream bytes, sender drain falls from 81.139 to 24.069 ms, a 70.34% reduction and 3.371× the UART1 command-stream rate. UART1 wins the 256-byte case. The 4097-byte pair remains unqualified because its parallel USB byte dumps are incomplete.

This run uses one identical configured 360 MHz P4 build for both carriers. The current 240 MHz networking/application pair was restored afterward; its performance was not measured here.

## Measured scopes

Rows rank by longest UART1 sender-drain baseline first. Each qualified cell has one retained warm-up plus five measured samples. All numbers below are medians; the structured record includes every selected raw count, minimum, maximum and nearest-rank p95 (with five samples, that p95 is the maximum). UART1 is the baseline; time saved is `100 × (UART1 − parallel) / UART1`.

| Command-stream bytes | UART1 sender drain, ms | Parallel sender drain, ms | Parallel / UART1 rate | Drain time saved | UART1 ordered reply, ms | Parallel ordered reply, ms |
|---:|---:|---:|---:|---:|---:|---:|
| 8192 | 81.139 | 24.069 | 3.371× | +70.34% | 163.542 | 116.861 |
| 4096 | 36.917 | 11.528 | 3.202× | +68.77% | 81.792 | 66.792 |
| 256 | 2.333 | 2.556 | 0.913× | -9.52% | 6.528 | 16.639 |
| 4097 | Unmatched UART data retained | No complete paired acquisition | — | — | — | — |

| Stream bytes | UART1 command-stream bytes/s | Parallel command-stream bytes/s | UART1 application submission, ms | Parallel application submission, ms | Parallel local completion, ms |
|---:|---:|---:|---:|---:|---:|
| 8192 | 100963 | 340349 | 81.125 | 24.819 | 24.847 |
| 4096 | 110953 | 355316 | 36.903 | 12.306 | 12.333 |
| 256 | 109714 | 100174 | 2.319 | 0.083 | 3.083 |

1. The eZ80 sends ordinary buffer-update VDU commands through EMOS-owned UART1 ExCom or eight-bit ExExt wiring to the same P4 renderer. Stream length includes the eleven-byte header; useful uploaded data is N − 11. Rates are whole command-stream bytes divided by sender-drain time, including existing handovers, not isolated electrical bandwidth.
2. Submission ends when the existing source call returns. Sender drain is the software-observed last-byte boundary. Parallel local completion includes native cleanup and reciprocal UART return; the historical CSV name `receipt_prt` does not represent a software ACK. These are intervals from a common start, not phases to add together.
3. The ordered fence adds synchronous receiver work and a seven-byte query/six-byte reply. Its gain is smaller than sender-drain gain: 8192-byte ordered time falls 28.54%. It is neither reverse bulk throughput nor display presentation. At 256 bytes, ordered time is worse with parallel; fixed transaction costs matter. These sizes locate a useful large-transfer regime, not an exact crossover threshold.
4. EMOS still supplies the parallel byte clocks. Early submission return in the tiny case does not establish autonomous transmission or useful CPU headroom. No renderer FPS, game performance or current networking-carrier speed claim follows.

## Completeness and acquisition failures

The eight original invocations produced 48 timing rows. The original P4096 and P4097 applications completed six zero-flag rows and returned to an actual CLI, but one USB dump in each lacked bytes. Those whole acquisitions were rejected, retained and excluded from performance. No missing byte was padded or inferred from the ordered query.

The standing capture-failure procedure was applied through a published amendment before further dispatch. Independent cases continued after supported recovery. Both affected cases then passed separate bounded 60-second controls with the P4 debug-dump routine absent. These controls have no complete byte proof and supply no performance values. Their passes do not prove that the dump routine caused the loss.

After restoring and independently verifying the exact capture P4 build, one labelled fresh acquisition per affected case was allowed. P4096-r02 supplied all six complete dumps and is the declared P4096 source. P4097-r02 remained incomplete; no further attempt occurred. Original failed acquisitions and new namespaces remain separate.

| Rejected acquisition | Six dump byte counts, in original repeat order | Disposition |
|---|---|---|
| P4096 original | 8192, 8150, 8192, 8192, 8192, 8192 | Retained failure; separately labelled r02 qualifies |
| P4097 original | 8192, 8140, 8192, 8192, 8192, 8192 | Retained failure |
| P4097 r02 | 8192, 8152, 8192, 8192, 8192, 8192 | Unresolved; no paired performance value |

Ten acquisitions contain 60 raw timing rows, with three invalid acquisitions. The three selected paired size sets cover 36 complete receiver buffers, 294912 verified bytes and 30 measured samples after excluding six declared warm-ups. Every byte of each 8192-byte poisoned/updated receiver buffer matches its expected value outside timing. All timing flags were zero; this does not erase the capture failures or establish error-free endurance. No partial-acquisition stitching or elapsed-time selection was used.

## Identity, clocks and validation

1. P4 `port-008-stream-r19-b2026-11-02-13-28-51Z`, source `dddc10a2a31d993af577be436b5d14f6aee9de15`, app SHA256 `102014003d771e1c917782e281bdde607da4632d7b255e0c2ba8285bd8c0fd45`; configured 360 MHz. Both measured arms use this exact image. Capture-absence control source `d74185caa47107b52bb2633eb9d27291f5f98c1e`, app SHA256 `d49d88e54879372db4e1f61252b83f67daf8be5d984f89b0284b285033e29927`, retains that configuration with the dump routine absent.
2. Optimized EMOS `agon-emos-v0.1.27-b2026-11-02-16-22-52Z`, source `08301e6`, full-ROM SHA256 `b4e07568aa6ba25b1e7b872d97e81942343ca935f633543a9f0f6924563ded28`. Exact-bound 13386-byte MOSlet `port-008-stream-timing-r01-b2026-11-02-16-32-30Z`, SHA256 `a0599d231f0da370f6773a934a3870800d16ae0b64e1491573f68bf677e6f417`.
3. PRT1 /256 gives nominal 72000 counts/s at nominal eZ80 18.432 MHz, 13.8889 microseconds/count. Single-pass range and ordering checks pass; MOS coarse units are 1/120 second. No independent oscillator calibration or cross-processor timestamp subtraction. Interrupt/preemption and software observation costs remain included.
4. Fifteen retained validator checks and artifact rehash passed under compiler 286, released before target preparation. Offline report validation independently recomputed selected medians/rates, checked all 60 receipt/CSV rows and timer order/bounds, and rehashed all 30 acquisition files. The first local analyzer attempt passed string CSV fields to an integer helper and produced no report; numeric conversion was corrected offline without target activity.
5. Setup, route/mode changes, allocation/poison, dumps, byte checking and SD I/O are outside measured intervals. Reinitialization history differs for the labelled acquisitions; five samples are not a population-tail estimate. No new sensors, software CRC protocol, emulator or mixed-carrier accuracy soak was used.

## Restoration and handback

Generation 70 ran from 2026-11-07T04:20:31UTC to clean release at 04:57:51UTC. The full incoming 131072-byte EMOS ROM and 1830912-byte touched P4 span were independently read back equal after restoration. Only an unresolved additional 65536-byte P4 tail required new preservation; the known retained prefix was reused. Bootloader, partition table, OTA/NVS and the mainboard VDP image were not written.

Returned P4 app SHA256 `d9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e`, full EMOS SHA256 `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca`; mainboard profile 8 app `5d65797e53a70db8716cc3bc31dc936e431aea975ffad8efb76d5d7e8c1e3d07` unchanged. Final mode 0/callback zero/Legacy 0, whole normal startup/listener, actual CLI/cursor, neutral input, offline listener, idle worker, free ports and joined actors passed; SD remains mounted. The isolated old diagnostic listener alias is retained separately and never replaces or autoruns the canonical listener.

Two host compatibility mismatches were reconciled without application replay: the old control P4 lacks the newer `/sd/fast` endpoint, and the restored current display status lacks old `rolling` diagnostics. The former was corrected before control installation; the latter required fresh truthful final state/release collection after successful restoration readbacks. Absent fields were not invented as zero counters.

The next prepared MechAgon reservation received normal fresh generation 71 and a stopped sole-operator handoff after release. No firmware promotion, blocked Wolf endpoint decision or broader benchmark completion follows.

The [structured result](PHYSICAL-R01-RESULT.json) preserves selected raw counts, ranges, acquisition hashes and installation identities. Large captures, operation freezes, control receipts and full restoration/release evidence remain in the ignored local run directory named there. The [physical plan](PHYSICAL-R01.md) and [fixture source](../../../tests/performance/stream_timing/README.md) retain the explicit measurement contract. Reverse bulk, useful CPU progress, the remaining live corpus and application-matched performance remain outstanding; [COMMS-001](../COMMS-001.md) stays a separate accuracy/endurance task.
