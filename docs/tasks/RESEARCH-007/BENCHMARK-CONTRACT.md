# Indexed expansion benchmark — executable preparation

## Executive summary

The Author requires a complete executable test of whether PPA indexed expansion
beats the old CPU RGB222-to-RGB888 expansion. The earlier compile-only example
did not answer or prepare the performance question sufficiently. Prepare and
verify a flashable, self-running benchmark plus durable capture/analysis tools.
Bench access remains unavailable: no flashing, serial/device/network access,
reset, SD/startup change or product integration in this tranche.

## Frozen comparison

1. The P4 CPU baseline calls the maintained `expandSignalRowToHdmi` implementation
   unchanged. Its RGB222 signal bytes use `x ^ 2` lane order and `00BBGGRR`,
   including ignored sync bits. Freeze its two header dependencies by hash.
2. A CPU linear-input control uses the same channel-expansion helper. PPA BLEND
   uses linear L8 input and a256-entry palette repeating the exact64 RGB222
   colours. A fourth path reorders legacy signal bytes before PPA submission;
   its total includes that cost. Distinguish a changed storage layout from a
   drop-in conversion replacement. Reuse the already reviewed CLUT backport.
3. Six cases: 320×32 and512×32 strips to SRAM and PSRAM, then320×240 and512×384
   full images to PSRAM. Each path gets four warmups and32 retained samples;
   alternate method order. Source is PSRAM. Use identical deterministic content,
   input-cache conditions and independently verified B,G,R output per case.
4. Measure source reorder, CPU conversion or blocking PPA call, necessary output
   publication, and complete elapsed time separately. PPA call time includes
   driver cache work, queuing and completion wait. Timers exclude source creation,
   correctness checks, result storage and serial printing. Do not call elapsed
   CPU clock cycles CPU-busy time. This standalone benchmark has no HDMI/DMA
   scanout or concurrent game load and cannot establish gameplay performance.
5. Preserve guard/input correctness checks, explicit error outcomes and build
   identity. Store raw timing records durably on P4 NVS after measurement and
   emit machine-readable serial records. The host collector writes the raw
   transcript and normalized JSON/CSV; the analyzer presents side-by-side median,
   p95 and worst times plus signed percentage improvement over the old CPU path.
   State strip guard/frame-budget context without claiming a60Hz qualification.
6. Produce application ELF/BIN, bootloader, partition image, verified offset-zero
   factory image, flash-segment manifest, source/config/tool hashes and an exact
   future deployment/capture recipe. No installation occurs now. Reuse maintained
   bench identity/reset procedures when later execution is authorized; keep Agon
   held reset while this standalone firmware lacks the ordinary transport service.

## Bounded work

### R07-B01 [x] Freeze baseline, executable contract and identities

Commit/push existing owned dirt, this contract and task/TODO updates. Pin the old
CPU conversion source and selected CLUT backport. Register a separate experimental
benchmark lineage; leave the r05 compile-only article and evidence immutable.

### R07-B02 [x] Implement the complete benchmark and offline host tools

Write all four paths, six cases, finite timing/correctness execution, durable NVS
results and serial records. Prepare capture/analysis and explicit deployment
instructions. Preserve stock colour mapping; no renderer or public API changes.

### R07-B03 [x] Compile and validate the deployment payload

Cross-compile/link actual benchmark/API calls; verify header dependencies, image
silicon range, flash segments/factory bytes, source/tool hashes and exact config.
Test host parsing and numerical analysis with labelled synthetic serial data,
including missing/error records. Do not mistake synthetic data for P4 results.

### R07-B04 [x] Package, report and stop before bench access

Retain the generated package and one local evidence index. Update task, dated log
and handoff, commit/push owned work, report what is prepared and what still needs
physical execution. Do not claim hardware correctness, measurements, installed
readiness or production promotion. The Author's existing no-flash boundary holds.

### R07-B05 [x] Physical execution — completed 2026-10-11

Only after Author releases the bench: sign it out, identify the current installed
pair, hold Agon reset using the admitted executor, install/verify the standalone
P4 image, capture the finite run and validate every case. Restore the selected
ordinary P4 image and normal keyboard readiness before handback. Report measured
conversion results separately from absent HDMI/gameplay measurements. This step
is not executed or authorized by the current preparation tranche.

## Preparation outcome — 2026-10-11

R07-B01–B04 completed: [preparation results](PREPARATION-RESULTS.md),
[build/hash evidence](BENCHMARK-EVIDENCE.json) and
[executable recipe](benchmark/README.md). Native build and offline tests pass;
no physical execution or deployment. R07-B05 remains bench-gated.

## Hardware authorization — 2026-10-11

The Author releases the bench and directs commit, push and execution. Execute
R07-B05 with the already built benchmark, retain the exact ordinary installed
P4 restoration payload, preserve EMOS/mainboard VDP/SD/startup/wiring, and restore
ordinary readiness afterward. Stop before deeper debugging if hardware checks
fail; the Author will raise the thinking level if necessary.

## Physical outcome — 2026-10-11

All768 measured records and firmware pixel/source/guard checks pass in one
fresh14.439231s run. [Physical results](PHYSICAL-RESULTS.md) and
[evidence](PHYSICAL-EVIDENCE.json) record timings and exact ordinary P4
restoration with admitted CLI input/neutral readiness. Bench released; no product
integration or additional campaign. The earlier preparation-only boundary is
historical; the Author explicitly authorized this completed R07-B05 execution.
