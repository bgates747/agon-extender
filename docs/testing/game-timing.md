# Paired game timing package

## Executive summary

Reusable diagnostic support for mainboard VDP and P4 EDP. Scoped controls and
paired game captures passed; see the [retained results](../tasks/BENCH-007/RESULTS.md)
for limits and the unresolved mainboard sequential-run panic. Artifact status
remains experimental; this is not general production qualification. Shared
recorder source is vdp/video/extender/diagnostics/frame_records.hpp.
The source is integrated into diagnostic builds only; game clients use EMOS-owned
VDU routing and the established private QTG reply envelope.

## Batch operations

Retain existing EF operations1–4 unchanged. Extend the diagnostic seven-byte
request `23,0,EF,op,id_lo,id_hi,detail` with:

| Op | Action |
| --- | --- |
|5|Drain preceding work once, reset bounded capture; acknowledge capability/capacity outside timing|
|6|Begin drawing interval for sequential update ID; previous end/reset owns fence|
|7|End submission and wait for normal-worker fence; save elapsed/completion/drain|
|8|Read stopped record ID, detail selects metric1 submission,2 completion,3 drain|
|9|Stop and acknowledge record count; reject an incomplete active interval|
|10|Dump stopped records through diagnostic serial output after capture|

No replies on successful6/7: avoid per-frame reverse-UART traffic. Errors latch
and surface at stop; clients must bound the overall workload and check stop.
Record capacity240, no overwrite. Read replies retain QTG/A1/16-byte format,
source/token ownership and existing EMOS callback admission. Values use local
ESP microseconds. No cross-processor subtraction. Start/end fence overhead is
measured separately by empty controls and retained in the reported interval;
never subtracted as if constant.

Reset and each preceding end pass the ordinary worker fence. Begin timestamps
without a second fence; clients place no unrelated drawing between intervals.
Submitted time ends when the parser handles the end command; completion ends when
its fence reports prior primitives/software sprites complete. These are elapsed
wall times, not exclusive drawing CPU usage or physical scanout. The additional
barriers can perturb natural pipelining; instrumented and pacing-only controls
must be compared explicitly.

## eZ80 active time

Record active work and deliberate pacing with an otherwise-unused PRT1.
Single-pass /16 at nominal18.432MHz gives1,152,000 counts/s, about0.868us/count.
Read low byte then latched high byte. Keep interrupts enabled; no new ISR.
PRT0, used by MOS and AgonDev delay, remains untouched. Refuse an already-active
PRT1 or non-system source. Do not change the shared timer source selector.

Reload65535 once per iteration. A saturated counter marks the row overflow;
never unwrap it into an apparently short measurement. MOS raw ticks provide a
coarse duration cross-check. Disable PRT1 on exit. Timer read/control overhead
remains in measurements and is qualified with an immediate-read control.

AgonDev delay uses PRT0; its clock() returns raw MOS ticks despite the library
header's100 CLOCKS_PER_SEC declaration. Do not infer game cadence from that
constant. Vblank, delay and saturation controls precede performance acceptance.

## Reuse boundary after the EMOSlet migration

The retained `tests/performance/run.py` still ends its batch by loading the
ordinary `/extender/sdserve.bin` fallback. That is deliberate recorded behavior,
not a claim that it invokes `/emos/sdserve.bin`. The runner also assumes normal
checked uploads; do not start it against a `--fast` listener. Both layouts and
session handling are described in the [SD guide](../mainboard-sd.md).

Before another run, refresh and review its generated batch against current
[bench constraints](../qualification/bench-constraints.md) and
[SD layout](../sd-layout.md). In particular, it currently selects a video mode
inside its generated EXEC batch; the standing fixture rule requires mode
selection in `/autoexec.txt`, before invocation. This documentation audit does
not alter a frozen runner or authorize that exception. BENCH-007 owns its next
procedure refresh. Preserve old evidence and do not rerun old command sequences
as though documentation review qualified a new deployment.

## Building and running

1. `tests/performance/builders/aginvadors.py`, `rally.py`, and `nurples.py`
   accept `--source` and a fresh `--output` directory. Supply the current
   Aginvadors Agon target directory, Rally repository root, or Nurples repair
   repository root respectively. They copy source before instrumentation.
2. `tests/performance/builders/mainboard.py` exports the pinned stock VDP/GL
   commits into a fresh `--output`; `--stock` identifies the read-only reference.
   P4 uses the same diagnostic headers in its existing normal-worker build.
   Firmware installation uses the maintained machine-local bench authority,
   preserving and independently verifying actual installed flash first.
3. C test derivatives read `timing.cfg` once, outside capture: ASCII `0`
   disables renderer markers and `1` enables them. Both cases use the identical
   game binary and PRT reads. Missing or invalid configuration refuses capture.
   Normal production Aginvadors contains none of this instrumentation.
4. Select mode through MOS CLI/startup before invocation:8 for Aginvadors,
   136 for Rally,20 for Nurples. Place runtime data in the isolated test
   directory. Do not run these derivatives on unprepared production directories.
5. C variants write120 rows after capture. Nurples stores120 raw active/total PRT
   records and MOS timestamps in RAM; save the symbol-delimited range before
   loading the common post-run collector. Symbol addresses belong to the exact
   compiled binary. Never reuse addresses from another build.
6. `tests/performance/analyze.py` validates sequential rows and interval
   partitions, reports elapsed work/wait and renderer percentiles separately,
   and flags saturated rows. Device identity255 means the no-marker control;
   its renderer fields are placeholders, not zero rendering cost. MOS run ticks
   measure whole capture duration; summed PRT intervals exclude small inter-loop
   instrumentation bookkeeping. Never call elapsed active time exclusive CPU.
7. `serial_capture.py` is a bounded console reader, opened before admission,
   never during a game or another reader/flash operation. Post-capture operation10
   uses stock `force_debug_log`; UART/USB identity and reset behavior belong to
   machine-local bench configuration. Serial lines are renderer timing records,
   not browser presentation timestamps.

## Source and precision notes

PRT register definitions follow the current Nurples `timer.inc` and Zilog
[eZ80F92 product specification](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf),
Programmable Reload Timers. The new reader uses the hardware counter rather than
that file's centisecond interrupt accumulator. Mainboard/EDP graphics timing
continues to use their existing diagnostic fence and `esp_timer_get_time`.

## Collection and wider timer range

`tests/performance/builders/controls.py --output DIR` builds the protocol,
empty/drawing, PRT precision, capability, collector and serial-dump applications.
`--prt-divider 64` builds the wider-range precision control. The Rally builder
also accepts `--prt-divider 64`; its generated assembly selects /64 before any
measurement. This gives nominal288,000 counts/s,3.472us/count and227.55ms range.
Other fixtures default to /16. Always retain the selected divisor beside raw
counts and pass the same value to the analyzer; never mix raw counts across them.

The reusable `tests/performance/run.py` accepts `--url`, `--output`, `--route`,
`--game`, `--markers`, and a unique `--run-name`. It requires an already-running
SD service and exclusive bench ownership. It does not flash or reset boards.
For Nurples supply the exact binary's `--symbols`; for the wider Rally build
supply `--rally-binary rtime64.bin --prt-divider 64`. Prepared files belong under
/test/gt, with game directories inv/rally/nur and common helpers at /test/gt.
CLI batches select the mode outside the applications and return to the SD service.
The operator must prepare firmware, runtime assets and the admitted keyboard path
before invoking it. No browser observer should request video during this baseline.

Each batch and Nurples raw dump uses a unique name. SD service staging verifies
both staged and activated contents. Known timing configuration backups contain
only0/1 and are preserved locally before cleanup; unfamiliar recovery states stop
collection. MOS SAVE will not overwrite an existing raw file. An interrupted run
must preserve its live RAM before another application is loaded if recovery is
possible; never substitute stale CSV or RAM records for the failed run.

## Repeatable host checks

Run the Python analyzer checks with the project virtual environment:
`.venv/bin/python -m unittest discover -s tests/performance/host -p 'test_*.py'`.
Compile `tests/performance/host/recorder.cpp` with C++17, AddressSanitizer and
UndefinedBehaviorSanitizer, adding `vdp/video/extender/diagnostics` to includes.
`verify_serial.py --serial CAPTURE CSV` requires an exact120-record dump match.
A serial dump confirms retrieved renderer values; it does not validate physical
scanout or prove that the diagnostic fence leaves natural scheduling unchanged.
