# PORT-008 — Bench-free reverse-core results, 2026-10-08

## Executive summary

EMOS can execute the candidate reverse receive sequence, and the paired EDP
core handles transmit completion, explicit pad release and bounded failures.
The maintained C/C++ cores pass paired host tests; the actual linked eZ80
instructions pass CPU-emulator checks. Physical activation remains absent.
UART handover, the native PARLIO binding and first/last-byte timing are still
required before a hardware trial. The occupied bench was not accessed.

## Scope and evidence

| Check | Result | What it establishes |
|---|---|---|
| Paired EMOS C / EDP C++ model | 48 cases pass | Patterned bytes, 1–4096-byte boundaries, edge order, exact buffer limits, reentry, missing peer, deadlines and cleanup failures |
| Linked eZ80 instruction emulator | 38 cases pass | Actual compiled configure/open/read calls and callback ABI; exact bytes, IX/SP/IFF preservation, clock wrap, stopped ticks, fault persistence and invalid lengths |
| Existing EMOS parallel suite | 9 tests pass | Retained forward engine, binding and UART guard checks remain passing |
| Native P4 profile suite | 11 tests pass | Existing native build/profile configuration checks remain passing |
| EMOS wrapper `firmware-check` | Pass | Full link and mandatory baud, keyboard, ABI, console, parallel-route and VDU checks |
| P4 reverse-core RISC-V compilation | Pass | Target compiler accepts the core with warnings as errors, exceptions/RTTI disabled |
| Complete P4-PC console build, browser profile | Pass | Native compile/link plus manifest/action validation; no deployment or HDMI qualification |

The paired test is `tests/parallel_reverse_test.py`; it compiles the maintained
EMOS source, not a copied implementation. The eZ80 test is
`agon-emos/tests/uart_put_cpu/src/bin/parallel_reverse.rs`, using the existing
pinned Fab-family CPU interpreter and the new full EMOS image. It is not a
full-system Fab boot, interrupt-arrival simulation or a UART/PARLIO peripheral
model. No emulator window or hardware attention cue was opened.

Machine-local logs, source receipts, linked EMOS image/map/provenance and target
objects are retained under ignored `agents/port008-reverse/`. Tracked
[REVERSE-CORE-RESULT.json](REVERSE-CORE-RESULT.json) records portable hashes. These are
development artifacts, not production or a deployment bundle.

## Implementation boundaries

1. EMOS adds a private, single-block receive reference to the existing engine.
   Its data bus operation is read-only; caller-owned mux/admission is required.
   The forward sender and active UART/keyboard paths are unchanged. Any failure
   invalidates the whole receive buffer. The added C reference grows the linked
   image from 128,622 to 129,196 bytes (+574); it is not the intended optimized
   assembly hot loop or a promoted production build.
2. EDP adds `P4ParallelEgress` with injectable backend operations. It keeps the
   DMA buffer alive through stop, waits for latched VALID completion and does
   not confuse a task's late completion publication with a short block. It
   attempts pad release even when stop fails and never publishes READY release
   after failed stop/release. Cleanup failure requires retaining the DMA buffer.
3. READY release only establishes the attempted physical release contract.
   The future coordinator must check the matching peer result before reporting
   a valid payload. A timeout also releases pads; sampled bytes alone cannot
   distinguish it from successful completion.
4. No native backend or caller instantiates the P4 core; no EMOS command calls
   the reverse engine. The P4 build profile compiles its source for type/build
   checking. No ExExt feature is enabled, and no readback/throughput result is
   claimed. All existing installed firmware and SD contents remain untouched.

The [contract](BIDIRECTIONAL-DEVELOPMENT.md) maps remaining work to F02c/d.
The Author subsequently authorized a safety commit and push of this development
checkpoint. This overrides the earlier commit hold, not the outstanding runtime
qualification gates; no production promotion or deployment is implied.

The first full P4 build stopped at a registry network restriction. Retrying with
the retained dependency lock and authorized registry access passed; no source
workaround or device access was used.
