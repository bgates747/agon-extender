# Curated graphics timing experiment

Reviewed candidate implementation of the [frozen contract](../benchmark-contract.md).
[Protocol and measurement boundaries](protocol.md) govern interpretation.
Temporary firmware is required on all three processors; these files do not
authorize skipping the emulator-review, clean-build or actual-backup gates.

## Contents and preparation

1. `scripts/prepare_corpus.py` derives the 64 selected cases from the existing
   vendored suite, retaining stage prerequisites, quiet stages and asset bytes.
2. `scripts/build_fixture.py` stamps and builds `fixture/bin/GQTBENCH.bin` and
   `fixture/media/*.DAT`. The build manifest and exact corpus are under
   `fixture/build/`. The application owns no UART, GPIO or video-mode setup.
3. `scripts/build_mainboard.py --output PATH` exports the exact stock VDP and
   vdp-gl commits and builds a classic ESP32 image with the private hooks.
   `scripts/prepare_console.py --output PATH` at repository root prepares the
   corresponding P4 candidate. EMOS is built through its own repository wrapper.
4. `scripts/build_native.py --source MAINBOARD/source --output PATH` builds
   the native mainboard adaptation; add `--peer` for the EDP functional peer.
   The optional `--trace` writes native diagnostic requests/replies to stderr;
   it is never a physical performance build.
5. Use mos-agondev's maintained `prepare_uart_peer.py` to build the current
   runtime with host-socket CTS backpressure. `prepare_timing_review.py`
   accepts explicit native modules, runtime and output directory. It creates
   a verified profile with a raw FAT SD image, independent of physical media.
   Run the profile's local `./fab-agon-emulator`; `--human` at preparation
   enables the labelled visual review. The default is headless and silent.

Run Python through the repository interpreter with `-B`. Builders never write
the official references or physical media. Source edits after a build require
fresh qualification; draft outputs are not clean candidate evidence.

## Physical execution, after review and candidate preparation

1. Record exact candidate and installed identities/hashes. Preserve the
   accepted ordinary EMOS/P4 bundles. Establish the mainboard's stable serial
   identity, read its actual flash and verify the saved bytes **before** any
   mainboard write. A reconstructed stock build does not replace that backup.
   Use the canonical deployment workflow and machine-local bench record.
2. Deploy the reviewed diagnostic images. Install only `GQTBENCH.BIN` and
   all generated `.DAT` files into `/extender/gqt` on Agon SD. Preserve existing
   results and the prior autoexec. No test requires the broken mainboard
   keyboard for setup or recovery.
3. Autoexec selects input and mode 20 on both renderers, then runs the test:

   ```text
   EMOS KEYINPUT extender
   VDU 22 20
   EMOS EXCOM
   VDU 22 20
   EMOS LEGACY --keep-display
   CD /extender/gqt
   LOAD GQTBENCH.BIN
   RUN
   ```

   An admission/setup error stops before the workload. For manual launch,
   omit the last two lines and use the accepted Extender USB keyboard to
   issue them after setup. Do not pass the emulator-only `review` argument.
4. Keep one browser video client visible, leave all keys released during
   measurement, and retain the same connection state for both routes. Run
   one entire instrumentation-off pair, then three on pairs automatically.
   Each pair runs all mainboard cases before EDP; no per-case keypress occurs.
   Fixed output windows alone total about eight and a half minutes; drawing,
   transfer, setup and durable writes add time. Each firmware fence and
   receive wait is bounded at ten seconds. A failure saves an incomplete
   terminal result and returns; it must not be relabelled a pass.
5. The application closes each completed record on Agon SD and creates
   `GQT001.CSV`, then the next unused numbered file on later invocations.
   The terminal summary names the file. Wait for the MOS prompt, return the
   card to the host, and copy/hash the complete result alongside image/corpus
   identities and host observations. No screenshot is required for collection.
6. Run `scripts/read_results.py RESULT.CSV --output SUMMARY.json` to validate
   the complete 1024-interval sequence before interpreting timings. Record
   pixel-probe disagreements separately from timing completion. Native
   shortened results require `--review` and cannot establish device speed.
7. Restore the preserved ordinary mainboard/P4/EMOS images through the same
   deployment workflow, then verify USB input and Legacy/ExCom operation.
   Review the measurements before making any performance change. Automated
   Nurples and typing-latency work remain deferred.

The experiment records renderer CPU and completion timing, not physical VGA
or browser presentation latency. Browser sequence/refresh observations remain
separate. The restored P4 publication path and stock mainboard cadence are
unchanged by this experiment.
