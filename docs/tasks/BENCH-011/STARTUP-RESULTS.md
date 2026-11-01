# Bounded remote startup diagnosis

All four planned startup attempts passed on the Olimex bench. The Console8
first-failure/second-success symptom did not reproduce here. Extender restored
the original mainboard flash byte for byte and verified normal CLI handback;
P4, EMOS and startup were not written. FSIM independently verified the separate raw evidence, mode sequences, pool
checkpoints and temporary installation comparison. These runs do not establish a Console8 fix or explain FPS.

## Results

| Cohort | First invocation | Second RUN without reload/reset |
|---|---|---|
| Unchanged baseline | Mode entry and clean exit; 1,762 physics ticks, error 0 | Mode entry and clean exit; 1,762 physics ticks, error 0 |
| Separate instrumented executable | Mode entry and finite clean exit; 180 ticks, error 0 | Mode entry and finite clean exit; 180 ticks, error 0 |

The first baseline followed installation boot. One deliberate Agon/mainboard
reset separated the completed baseline cohort from the diagnostic cohort;
actual CLI proof preceded the diagnostic LOAD. Neither pair contained a reset
or reload between its first and second RUN. Each attempt's terminal, summary,
renderer state and raw printer capture were archived before another invocation.
Diagnostic files `p066001.log` and `p066002.log` independently retain both runs.

Both diagnostic traces receive mode 0 at 640×480/16 colours, mode 136 at
320×240/64 colours, then restored mode 0. Entry admission, query verification,
ordered fences and settling succeed. Native error, unsafe state, cleanup error
and log-write failure are absent. This is observed technical execution; no
optical review is claimed.

## Memory observations

The following values precede selection of mode 136. Units are bytes. The raw
u16 samples and all other checkpoints remain in the
[portable evidence](STARTUP-RESULTS.json). Combined words were sampled
sequentially; they are not atomic snapshots. Capability pools overlap and must
not be added together.

| Pre-mode observation | First diagnostic | Second diagnostic |
|---|---:|---:|
| Executable free / largest | 27,740 / 14,324 | 27,740 / 14,324 |
| Internal 8-bit free / largest | 58,256 / 36,852 | 58,072 / 25,588 |
| PSRAM free / largest | 2,831,815 / 1,933,300 | 2,831,807 / 1,933,300 |
| Historical task-stack minimum | 2,136 | 1,364 |

The smaller largest internal block in the second run is an observed layout
difference, not proof of a leak or the Console8 failure's cause. Historical
stack minima are not current stack headroom. Every pool query reports success
and native error 0.

## Identity and restoration

1. The seven-file baseline and separate 177,054-byte diagnostic executable were
   uploaded through the maintained checksum-free fast2 listener and explicitly
   downloaded for host comparison. Six identical config/assets were reused for
   the diagnostic. The original `flight.bin` remained intact; no `verify.tst`
   changed baseline behaviour. An interrupted host READ was reconciled from its
   saved request without repeating the activated upload.
2. Actual incoming 4 MiB flash SHA256
   `42b165d7ecd0c6c0dab836178baa052ce6216f9c70c6d8c7d307d6c1a0ad05af`
   matches the prior F060 installation. Its partition table matches the supplied
   runtime layout; existing valid OTA sequence 1 selects app0. Boot metadata was
   read and interpreted on the host, never rewritten.
3. The temporary rows-r1 application SHA256
   `8d980025f891484cf7e6cc5f2992cf517cb80e0123ff7de712ae8d7f2dc1c807`
   was written only at app0, offset 0x10000. Full readback verified exact app
   bytes and unchanged bytes outside application erase sectors. No bootloader,
   partition, NVS, OTA, other app bank, P4 or EMOS write was requested.
4. Exact retained application sectors restored F060 after the tests. The full
   subsequent 4 MiB readback equals the incoming backup byte for byte. Two
   listener/startup-read/EXIT exchanges prove actual restored CLI operation;
   108-byte load-only startup remains unchanged. Text/cursor/flashing controls
   were submitted at that verified prompt. No optical cursor pass is claimed.
5. Final bench state is Legacy with idle foreground service, admitted neutral
   input and valid USB controller. P4 remains the incoming R25 image, mode 0 with
   advancing fault-free native scanout; its unrelated mode 96 defect remains.
   No capture, test, transfer, reset hold or pending replay remains owned here.

## Timing limits and handoff

Whole host fixture durations were 97.212/94.976 seconds for baseline and
57.839/55.575 seconds for diagnostic. These include input, startup, flight,
instrumentation and log retrieval. They are not precisely bounded presentation
intervals and must not be converted to comparative FPS. Source MOS ticks are
nominally 120 Hz without independent calibration; USB receive timestamps are
not synchronized source-event timestamps. Diagnostic printing/query overhead
is separate from an uninstrumented performance control.

FSIM independently audited all four attempts and the temporary installation
readbacks. FSIM owns later successful-run stage-cost instrumentation. No such performance executable was supplied or run here.
Console8 hardware/stock-MOS results and Olimex/EMOS results remain distinct.
The isolated SD fixtures remain available for future explicitly selected use;
their loadable renderer requires rows-r1. The mainboard now runs F060 and
does not support those loadable fixtures. Production selection and the deferred HDMI investigation are unchanged.
