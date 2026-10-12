# Executable indexed-expansion comparison

## Executive summary

This standalone P4 firmware directly compares the exact old CPU RGB222 expansion
with PPA indexed expansion, verifies every output pixel, saves all timing samples
to dedicated NVS, and emits a machine-readable result. The host tool validates
the complete result and writes raw serial, JSON, CSV and a side-by-side report.
The first bounded physical run now passes all768 measured samples and firmware
correctness checks; see [physical results](../PHYSICAL-RESULTS.md). Ordinary P4
firmware was restored and the bench released. The recipe below is reusable
evidence, not authorization to repeat deployment.

The [frozen contract](../BENCHMARK-CONTRACT.md) owns scope. This is a conversion
benchmark, not new product firmware: it supplies no HDMI, keyboard, networking,
Agon transport or SD service. Agon must remain held reset throughout standalone
P4 execution, under the maintained bench/reset procedure. Do not run this while
another project owns the bench. Read project `HARDWARE.local.md` and the current
installed-component records before later deployment/restoration.

## Measurements and interpretation

| Method | Input layout | Timed work |
|---|---|---|
| cpu_signal | Existing byte order `x ^ 2` | Unchanged maintained `expandSignalRowToHdmi`, then output publication |
| cpu_linear | Linear | Same channel-expansion helper, then output publication |
| ppa_linear | Linear | Blocking PPA BLEND indexed expansion, including driver cache work/completion |
| reorder_ppa | Existing byte order `x ^ 2` | CPU reorder to linear staging plus the same blocking PPA operation |

Six workloads cover 320×32 and 512×32 strips into SRAM and PSRAM, plus 320×240
and 512×384 full images into PSRAM. Strip sources include 32 preceding rows to
exercise a nonzero crop. All sources/staging/transparent alpha masks are PSRAM.
Four warmups and 32 samples per method/case produce 768 measured records. Method
order rotates each round. Source content covers all 256 byte values; the CLUT
repeats the exact RGB222 colours because the CPU ignores the top two signal bits.
RGB888 memory order is B,G,R. This is not the unrelated public VDU colour encoding.

Input generation, poisoning, verification, serial output and flash storage are
outside each measured interval. The selected source rows are freshly CPU-written
before each method. The CPU baseline includes its required DMA publication; PPA
includes input-cache flushing and output invalidation performed by the driver.
Full-source physical integrity and output guards are checked after every call.
PPA BLEND still reads a second, zero-alpha input; that memory traffic is included.
Linear PPA measures the opportunity with different storage; reorder + PPA measures
the cost of retaining existing storage. Neither alone proves game performance.

`esp_timer_get_time` supplies microseconds. The configured CPU is 360 MHz, PSRAM
200 MHz, CPU task pinned to core0, power management disabled. Cycle counts are
elapsed core cycles, including blocking/preemption, not CPU-busy time. Reports
rank worst PPA-to-old-CPU p95 ratios first and define signed improvements. Strip
guard (1,600 µs) and frame budget (16,666.7 µs) percentages are contextual only.

## Build and offline checks

Run from the repository root with its selected `.venv`:

```bash
.venv/bin/python docs/tasks/RESEARCH-007/benchmark/test_offline.py
.venv/bin/python docs/tasks/RESEARCH-007/benchmark/build.py \
  --output agents/research007/benchmark-r01/build-r01 \
  --tools-path agents/p4pc-demo/tools \
  --python-env agents/p4pc-demo/python-env
```

The native overrides above apply to the present ignored local tool installation;
use the machine's documented native tools on other hosts. The builder requires
committed input files and a fresh output path. It pins the old CPU headers and
partition baseline, verifies the unchanged IDF5.5.5 source inputs, and reuses the
six-file upstream CLUT backport from the frozen r05 example. Driver/header copies
are generated under the output directory; the base SDK is never modified.

The output contains application BIN/ELF/map, bootloader, partition table, offset
manifest, merged factory image, exact source archive, sdkconfig, build log and
`flash-package.tar.gz`. The builder checks actual frequency/cache/console choices,
P4 v1.3 image acceptance, segment non-overlap, and each segment's exact bytes in
the merged image. Hashes and build duration are in `manifest.json`. The retained
build/evidence index is [PREPARATION-RESULTS.md](../PREPARATION-RESULTS.md).

## Later bench execution — not authorized by preparation

1. After Author handover, reserve the bench and identify the exact installed
   ordinary P4 image/segments for restoration. Read the canonical reset protocol
   in `HARDWARE.local.md`; hold Agon reset before replacing its P4 peer. No eZ80
   fixture, SD deployment or startup edit is needed.
2. Verify the P4 stable USB path and its expected serial identity using the
   maintained `udevadm`/stable-device procedure. Set local `P4_PORT` to that
   verified path. Use `P4_ESPTOOL` from the local native tool environment and
   `BENCH_BUILD` for the generated directory. Do not select by enumeration order.
3. Write **only** the segments listed in `manifest.json`/`build/flasher_args.json`.
   On P4 these are bootloader at0x2000, partition table at0x8000 and application
   at0x20000. The exact manifest is authoritative if offsets differ. For this
   verified layout the commands are:

```bash
"$P4_ESPTOOL" --chip esp32p4 --port "$P4_PORT" --baud 460800 \
  --before usb_reset --after no_reset write_flash \
  --flash_mode keep --flash_freq keep --flash_size keep \
  0x2000 "$BENCH_BUILD/build/bootloader/bootloader.bin" \
  0x8000 "$BENCH_BUILD/build/partition_table/partition-table.bin" \
  0x20000 "$BENCH_BUILD/build/ppa_clut_benchmark.bin"
"$P4_ESPTOOL" --chip esp32p4 --port "$P4_PORT" \
  --before no_reset --after hard_reset verify_flash \
  0x2000 "$BENCH_BUILD/build/bootloader/bootloader.bin" \
  0x8000 "$BENCH_BUILD/build/partition_table/partition-table.bin" \
  0x20000 "$BENCH_BUILD/build/ppa_clut_benchmark.bin"
.venv/bin/python docs/tasks/RESEARCH-007/benchmark/results.py \
  --port "$P4_PORT" --build-id "$BENCH_ID" --output "$BENCH_RUN"
```

`BENCH_ID` is `manifest.json`'s build_id. `BENCH_RUN` is a fresh ignored evidence
directory with a task/timestamp run identity. Verify and record payload hashes
before writing. Preserve flash/verify logs with the result. The capture tool opens
without toggling reset lines. Its explicit 180-second capture deadline never
resets/restarts the board or claims a runtime estimate. USB renumeration may delay
attachment; the durable dump below recovers results if the first stream is missed.

**Do not write the merged factory image as one span on this bench.** Its padding
covers ordinary NVS. Segment-only writing preserves ordinary NVS at0x9000–0xEFFF.
The benchmark writes only its own 64 KiB NVS partition at0xE20000, within the
hash-pinned ordinary product table's unused reserved tail. It never initializes
or erases default NVS. Restoring the ordinary partition table makes this scratch
result area reserved again; no user partition needs to be erased.

4. The P4 automatically runs once after a four-second attach grace. After all
   checks pass, it commits 768 samples to `bench_nvs` and prints `BENCH_STORED`,
   the complete batch and `BENCH_DONE`. At idle, send `d` to replay the saved result
   or `r` for another finite run. If a collector attaches after completion:

```bash
.venv/bin/python docs/tasks/RESEARCH-007/benchmark/results.py \
  --port "$P4_PORT" --dump --build-id "$BENCH_ID" --output "$BENCH_RUN"
```

Saved replay is explicitly labelled `stored`, never a fresh run. One saved dataset
per build is retained; each successful rerun replaces it. A boot starts a fresh
run, so do not reset just to collect. Any firmware failure/missing/duplicate row,
wrong build or arithmetic inconsistency fails host validation and retains raw
evidence. Results are valid only after the host reports all768 samples validated.

5. Restore and independently verify the exact ordinary P4 segments/table under
   the same Agon reset hold. Wait for ordinary P4 pin-release readiness before
   releasing Agon. Confirm ordinary CLI/keyboard/service readiness and hand back
   the bench. Do not substitute this standalone test for production selection or
   reuse the regular flash worker, which expects ordinary USB keyboard readiness.
6. Retain the raw output and side-by-side report. A measured conversion advantage
   would justify discussion of integration; it does not authorize it.

For re-analysis without hardware, pass `--input SERIAL_LOG` instead of `--port`.
Offline unit-test data are synthetic and must never be filed as P4 measurements.
