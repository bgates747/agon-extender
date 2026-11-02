# Matched UART / parallel timing fixture

Experimental MOSlet and offline validator for
[PORT-008 stream timing](../../../docs/tasks/PORT-008/STREAM-TIMING-R01.md).
The original matched physical comparison is complete; phase attribution below is a separate diagnostic tranche.
This is not a production utility or permission to acquire an occupied bench.

The [current resumption contract](../../../docs/tasks/PORT-008/RESUMPTION.md)
supersedes the historical deployment steps below. New builds require a fresh
mode0 reply from the selected P4 route before acquisition, identify that case
visibly and restore a flashing text cursor on handled exit. They do not change
mode. The Pi runner owns earlier route/mode state, explicit preselection,
confirmation, at least one second of settling and final restoration. Startup
is read-only; never follow the historical autoexec instruction below. Rebuild
against the exact new timing ELF/ROM; old P4 partners and private addresses are
not a current deployment recipe. Use maintained `/extender` support and
`/agents/extender/results` output paths under the current SD layout.
The historical CSV column `receipt_prt` remains for analysis compatibility;
format4 measures native cleanup and reciprocal UART return there, without a
software COMPLETE/ACK exchange. Do not describe it as a measured serial receipt.

## Four-arm transfer-rate comparison

The [current comparison task](../../../docs/tasks/PORT-008/TRANSFER-RATE-COMPARISON.md)
reuses this unchanged fixture with two exact EMOS timing images and one fixed P4
application. U0/P0 select UART/parallel on the baseline EMOS image; U1/P1 use
the optimized image. Build a fresh exact-ROM-bound fixture for each image using
the existing builder. No new MOS API, wire command or per-byte probe is needed.

`compare_rates.py` validates all 96 rows and all 96 complete 8192-byte receiver
buffer dumps before reporting measured stream/useful-upload bytes per second,
separate submission/drain/local-completion/ordered-reply times, ranges and
baseline-relative differences. It refuses phase-only zero-wire timestamps and
mixed P4/configuration identities. It reads retained files only and never
accesses the bench:

```sh
.venv/bin/python tests/performance/stream_timing/compare_rates.py \
  --campaign PATH_TO_CAMPAIGN_JSON --output FRESH_ANALYSIS_DIRECTORY
```

The campaign JSON has `schema: 1`, `direction: "ez80-to-p4"`,
`parallel_format: 4`, and an `arms` object with exactly U0, P0, U1, P1. Each
arm supplies `route` (`excom` or `exext`), `emos_sha256`, `fixture_sha256`,
`p4_sha256`, `environment_sha256`, and ordered `results`/`captures` path arrays
relative to the campaign file. Hashes bind the exact artifacts and fixed
environment record; verified installation receipts remain separate evidence.
U0/P0 must share EMOS/fixture identities, as must U1/P1. Both EMOS images must
differ, while P4 and environment identities remain constant. CSV/dump arrays
cover lengths 256/4096/4097/8192 in that order, retaining original repeat indices.
Partial acquisition selection remains an explicit, integrity-only upstream step;
the analyzer never selects samples by elapsed time.

Run the existing host checks plus the new four-arm controls with
`-m unittest discover -s tests/performance/stream_timing -p 'test*.py' -v`.
Synthetic host cases test arithmetic/refusals; they are not performance results.
The report ranks largest P0 drain time first, then largest stream length on ties.
Analysis start/end and host duration are retained separately from fixture runtime.
The small reverse query is not a reverse bulk-rate measurement.

The [2026-11-02 physical comparison](../../../docs/tasks/PORT-008/TRANSFER-RATE-COMPARISON-RESULTS.md)
uses this analyzer unchanged: 96 full-buffer-proved rows, a fixed admission-corrected
P4 and old/optimized exact-ROM fixtures. At 8192 bytes optimized parallel is 3.383×
matched UART and 54.13% faster than baseline parallel; UART still wins 256 bytes.
Acquisition failures, matching no-dump controls, timing scopes and exact incoming
restoration are retained separately. This is forward throughput evidence only.

## Build and correctness checks

1. Build EMOS through its ordinary repository wrapper with the explicit
   `port/exext-stream-timing.mk` profile. Preserve the ELF, image, map, complete
   build provenance and mandatory link-check output. No generic build edits.
2. Build the fixture in a fresh ignored directory:

   ```sh
   .venv/bin/python tests/performance/stream_timing/build.py \
     --toolchain PATH_TO_AGONDEV \
     --emos-elf PATH_TO_EXACT_MOS_ELF \
     --emos-bin PATH_TO_MATCHING_MOS_BIN \
     --output FRESH_BUILD_DIRECTORY
   ```

3. The builder verifies ELF/image correspondence and generates private symbol
   bindings plus a full padded-ROM fingerprint. The MOSlet refuses a mismatched
   ROM or route before invoking those bindings. This fingerprint is an accident
   guard, not a cryptographic authorization boundary. Host verification still
   compares the complete installed ROM with its retained SHA256.
4. Run host interpretation checks with:

   ```sh
   .venv/bin/python -m unittest discover \
     -s tests/performance/stream_timing -p test_contract.py -v
   ```

5. EMOS's retained `parallel_native`, `exext_output`, `exext_irq` and
   `stream_timing` linked CPU tests cover actual compiled hooks and owners.
   They model I/O and do not measure physical transfer speed.
6. Run the actual MOSlet/resident ABI bridge check using the generated symbol
   maps and the same pinned CPU model:

   ```sh
   cargo run --manifest-path tests/performance/stream_timing/Cargo.toml \
     --bin abi-check -- EXACT_EMOS_ARTIFACT_DIRECTORY FIXTURE_BUILD_DIRECTORY
   ```

   The fixture's assembly bridge preserves IX/IY and converts ZDS C's A return
   to AgonDev's HL return. Calling that private C symbol through an ordinary
   AgonDev function pointer is incorrect even when its stack arguments match.

## Historical bench procedure — do not execute

1. Obtain bench release, then follow the local hardware/fixture constraints.
   Preserve the selected working UART pair, mainboard fsim VDP and startup.
   Install/verify the timing EMOS image with the exact retained P4 stream-r14
   partner specified in the task; neither Git HEAD nor the uninstalled r15
   candidate substitutes for that partner. Keep browser video disconnected.
2. Deploy only this fixture to `/test/extender/stream-timing/r01` through the
   maintained SD transfer path. Do not populate `/bin`, modify games, or start
   tests from autoexec. The historical autoexec preselection instruction is
   superseded: the Pi runner must preselect the mode, confirm it and wait at
   least one second before explicit fixture invocation; startup is read-only.
3. Start a bounded P4 USB log collector using the current stable device identity
   and no reset-producing line-control changes. Begin collection before each
   explicit invocation. Buffer command &80 logs each byte with an ESP_LOGI prefix;
   these large dumps occur outside timing and must be retained completely.
   The fixture allows up to 7200 MOS units for each dump's ordered reply;
   ordinary measured replies retain their 240-MOS-unit fault bound. At the
   measured 60 Hz VBlank cadence these are about 60 seconds and two seconds,
   respectively: stock MOS increments its coarse clock by two per VBlank.
   The initial preparation described them incorrectly as 120/four seconds;
   the frozen fixture's constants and measured intervals are unchanged. Neither is
   an advance runtime estimate or permission for an automatic board reset.
4. At a verified CLI, select `EMOS EXCOM` or `EMOS EXEXT`, change to the isolated
   test directory, and load the MOSlet at its linked address:

   ```text
   LOAD stream.bin &B0000
   RUN &B0000 excom uart0256.csv 256
   ```

   Use `exext` for the parallel case. Run lengths 256, 4096, 4097 and 8192;
   alternate route order between lengths. Each invocation produces six rows:
   one retained warm-up and five comparison samples. Give each CSV and USB log
   a distinct path and verify completion/CLI before the next invocation. An
   omitted length runs all four sequentially, useful for a smoke but not the
   primary alternated-order campaign.
5. Retrieve the CSVs after execution through the maintained Legacy listener.
   The fixture's completion text means acquisition finished, not byte validation.
   Run `analyze.py --help`; pass each route's four CSVs and four USB logs in
   ascending payload-length order. The validator requires all 24 rows per route,
   correct timer scope, and all 8192 poisoned/updated buffer bytes after every
   sample. It writes a fresh JSON result and side-by-side Markdown tables.
   Large serial dumps have occasionally lost bytes despite zero fixture flags,
   including with a dedicated reader and host tmpfs. Reject incomplete samples;
   do not pad missing bytes or assume a query proves data integrity. The
   [physical run record](../../../docs/tasks/PORT-008/STREAM-TIMING-R01-RESULTS.md)
   documents completed-case repeats and integrity-only sample selection with
   original row/chunk provenance. Preserve raw captures before assembling inputs.
6. Restore the exact working UART pair/startup, verify CLI/input, close collectors
   and release the bench. Do not promote or leave this diagnostic pair installed
   without explicit Author acceptance.

## Interpretation and limits

1. Payload: stock buffered command 5/&C2 updates preallocated buffer &E100 using
   inline binary operands. The eleven-byte header is included in the four exact
   stream lengths. Buffer allocation, poisoning, debug dumps and CSV writes are
   outside each timed sample. EDP still executes normal per-byte buffer updates;
   backpressure from that processing remains part of observed sending time.
2. PRT1 /256 gives nominal 72,000 ticks/s, 256 equivalent CPU clock cycles/tick,
   and 0.9102 seconds of single-pass range. Overflow invalidates a sample. Read
   overhead, empty-drain overhead and a VBlank/MOS-clock cross-check are retained;
   they are not subtracted as if constant. `run_ticks` includes setup and dumps
   before CSV saving, not just timed sending. MOS clock units increment by two
   per VBlank; retain the raw units and measured calibration rather than
   assuming either centiseconds or one unit per VBlank.
3. Physical drain is observed in software. Parallel snapshots after the final
   rising edge and loop-exit bookkeeping; UART polls shift-register-empty.
   Interrupt preemption and observation overhead can delay either observation.
   These values are not exact edge-to-edge logic-analyzer measurements.
4. The seven-byte pixel query confirms ordered processing of synchronous buffer
   operations. Its reverse traffic is included only in the reply endpoint. It
   does not measure rendering completion or HDMI frame rate.
5. The native assembly body is shared. The ordinary profile assembles the timer
   probe out; its complete ROM matches the preceding stream implementation
   except for its build-identity string. The timing composition adds 80 ROM bytes.

## Phase attribution composition

[Approved contract](../../../docs/tasks/PORT-008/PHASE-TIMING-R01.md) owns this
bounded investigation. Build the EMOS `port/exext-phase-timing.mk` profile, then
use the existing builder with `--phase --emos-objects RETAINED_C_OBJECT_DIRECTORY`.
Retain `emos_exext.o` and `emos_parallel_coordinator.o` beside the exact ELF/image.
The builder verifies sixteen original relocations against final CALL bytes and
records their return-PC names in `phase-sites.json`. The MOSlet uses the same
CLI arguments/lengths, requires ExExt and additionally saves `results.csv.phases.csv`.
The original `wire_prt` column is zero: this composition does not measure M02.

The sole RAM recorder has 512 eight-byte records. Its private &B0020 jump vector
occupies verified zero header padding; the builder patches only those four bytes
and hashes the final deployed binary. Reset-zero EMOS arming and full ROM
fingerprint/binding prevent accidental ordinary invocation; they are not a
security boundary. Only PRT1 is read by the recorder; EMOS owns every GPIO,
control exchange, payload and returned packet. Normal builds erase these calls.
Results/formatting and probe code remain in MOSlet RAM. The profile is temporary.

Run `cargo run --manifest-path tests/performance/stream_timing/Cargo.toml
--bin phase-check -- EXACT_EMOS_DIRECTORY FIXTURE_DIRECTORY` for actual linked
ROM-gate/RAM-handler preservation, disabled path, latch order and overflow checks.
Host checks are `python -m unittest discover -s tests/performance/stream_timing
-p 'test*.py' -v`. These model correctness and offline interpretation, not physical
clocks. `phase_analyze.py` requires conserved forward bytes including the seven-byte
query, matched phase scopes and unsaturated monotonic samples. Inclusive VBlank
service and publication overlap block intervals; never add them to phase totals.

Use the same per-sample full-buffer USB proof and integrity-only repeat selection
as the original comparison. Record both phase/endpoint CSV hashes and original
repeat indices together. Stop and discuss results before transport changes.

The [completed phase results](../../../docs/tasks/PORT-008/PHASE-TIMING-R01-RESULTS.md)
measure the preceding CRC-bearing experimental transport. Author now requires
no CRC in ExExt; these frozen bytes are evidence, not the final protocol design.
The read-only `crc-check` CPU-model binary calls that retained ROM's `_console_crc`
leaf with four fourteen-byte reference inputs and counts decoded instructions.
It adds no CRC to firmware and supplies no physical CRC timing:

```sh
cargo run --offline --manifest-path tests/performance/stream_timing/Cargo.toml \
  --bin crc-check -- EXACT_EMOS_ARTIFACT_DIRECTORY
```
