# Performance foundation — offline result r01

The dedicated byte corpus, measurement ordering, timer validator and matched
collector pass their source checks and an independent eZ80 compile/link probe.
They remain separate from the accuracy program. No UART1/parallel speedup has
been measured by this work.

| Check | Result | Boundary |
|---|---|---|
| Host C++ ASan/UBSan | PASS | Corpus bounds, timer wrap and measurement-order models |
| Independent corpus bytes | Four families match | Sink, short VDU, plot batches and buffer clear/write stream |
| Python collector/CLI checks | 9 PASS | Matched pairs, reversed order, tails, identity/refusal, partial files and exclusive report output |
| Measurement boundaries | PASS | Validation/cleanup excluded; uncertain admission or ownership makes no further I/O calls |
| eZ80 corpus/engine link | PASS, 2,988 bytes | Stopped compilation probe only; no physical timing |
| Actual carrier comparison | Not performed | Owner VDU/timer/receiver-completion adapter remains |

1. Source `eced8513f60401f38600acf4d0734e3aa5ae1d67` and
   [structured record](OFFLINE-RESULT-R01.json) bind actual inputs and artifacts.
   Native probe `comms-performance-core-r01-b2026-11-07-03-58-28Z`, SHA256
   `6be5f10091dbaf62576f657057a92e4605145cbfb54b1b81e0d91f047e690ce9`.
2. The measurement engine distinguishes refused, accepted and uncertain submit;
   source release is separate from receiver completion. Its endpoint-local
   intervals do not claim P4 execution timing or CPU utilisation.
3. The collector refuses accuracy journals, failed/incomplete samples, missing
   or duplicate arms, different workload/renderer/configuration/rates, hidden
   batch-size changes, ambiguous wrap and zero/sub-tick intervals. It produces
   separate scope/observer/clock rows with an explicit UART1 baseline. Positive
   and negative arithmetic controls use synthetic samples, not hardware results.
4. The combined finite source/build tranche took6.317 seconds and released
   compiler285 after all owned children joined. The earlier strict-width warning
   was corrected, not suppressed. No device/emulator/firmware operation occurred.

## Remaining integration boundary

Bind actual EMOS-owned ExCom/ExExt VDU/data submission, source release, required
receiver completion and an appropriate timer/batch size. Prove the renderer,
logical corpus, clocks and output requirements match between arms; normal NM
message timing alone cannot answer this task. Preserve exact installation and
rollback before a later finite bench comparison. The accuracy fixture's CRC,
retry, journaling and endurance loop are not part of this benchmark.
