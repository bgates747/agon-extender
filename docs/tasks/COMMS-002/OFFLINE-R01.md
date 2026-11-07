# Carrier benchmark — first implementation tranche r01

Implement a dedicated benchmark data/corpus/analysis foundation, separate from
the accuracy engine, without bench access or invented speed measurements.

1. Implement deterministic transfer-sink, short/mid VDU and buffer-upload byte
   workloads from the official command definitions. Generate identical logical
   bytes for each carrier; expose required setup/cleanup and completion witnesses.
2. Implement a portable timer-interval validator using explicit endpoint, clock
   identity, nominal rate, width and wrap policy. Reject ambiguous intervals.
3. Implement a strict host collector/analyser for matched UART/parallel samples.
   Bind pair, workload/renderer/configuration and timer identities; preserve
   errors and incomplete cohorts instead of producing a successful speedup.
4. Report separate scopes, baseline units, median/tails/worst cases and paired
   changes. Missing CPU or receiver execution fields stay unavailable. Do not
   add overlapped scope durations or infer utilisation from wall time.
5. Compile a stopped eZ80 core self-check and run host tests for actual corpus
   bytes, timer rollover, zero/sub-tick intervals, unmatched pairs, bad identity,
   failed/missing samples and correct positive/negative percentage arithmetic.
6. Use the same normal serial Pi compilation tranche and guards as
   [accuracy offline r01](../COMMS-001/OFFLINE-R01.md), with independent binaries,
   source tests and result records. No emulator/bench/firmware or speed test on Pi.

This delivers reusable source and compilation evidence, not a hardware benchmark.
The later executable must bind the actual EMOS-owned ExCom/ExExt VDU stream and
receiver completion. Network-message timing alone does not meet this task.
