# Matched UART / parallel timing fixture

Experimental MOSlet and offline validator for
[PORT-008 stream timing](../../../docs/tasks/PORT-008/STREAM-TIMING-R01.md).
Compiled/model checks are available; physical execution and timing are pending.
This is not a production utility or permission to acquire an occupied bench.

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

## Later bench procedure

1. Obtain bench release, then follow the local hardware/fixture constraints.
   Preserve the selected working UART pair, mainboard fsim VDP and startup.
   Install/verify the timing EMOS image with the exact retained P4 stream-r14
   partner specified in the task; neither Git HEAD nor the uninstalled r15
   candidate substitutes for that partner. Keep browser video disconnected.
2. Deploy only this fixture to `/test/extender/stream-timing/r01` through the
   maintained SD transfer path. Do not populate `/bin`, modify games, or start
   tests from autoexec. Autoexec selects the agreed video mode before the fixture
   is invoked; the program contains no mode switch.
3. Start a bounded P4 USB log collector using the current stable device identity
   and no reset-producing line-control changes. Begin collection before each
   explicit invocation. Buffer command &80 logs each byte with an ESP_LOGI prefix;
   these large dumps occur outside timing and must be retained completely.
   The fixture allows up to 120 nominal seconds for each dump's ordered reply;
   ordinary measured replies retain their four-second fault bound. Neither is
   an advance runtime estimate or permission for an automatic board reset.
4. At a verified CLI, select `EMOS EXCOM` or `EMOS EXEXT`, change to the isolated
   test directory, and load the MOSlet at its linked address:

   ```text
   LOAD stream.bin B0000
   RUN B0000 excom uart0256.csv 256
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
   before CSV saving, not just timed sending.
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
