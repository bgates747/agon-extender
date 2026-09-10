# AUDIT-005 W3 — Paired UART pathway benchmark

Prepared 2026-09-10 and accepted through the Author's implementation/deployment
request. See [current usage and validation](README.md). This is the implementation plan
under [AUDIT-005](../AUDIT-005.md), not an executed procedure or a performance
result. The [W1 identities](baseline-and-path-map.md) and
[W2 findings](differences-and-reuse.md) remain the comparison baseline.

## Smallest increment

Build one SD-loaded Agon application, with small assembly wrappers for the
RST interfaces and clock read. It runs the same workloads through EMOS to
mainboard VDP in Legacy and to P4 EDP in ExCom. It records elapsed output-call
time and a subsequent pixel-query reply, then saves results to the Agon SD.
Use the installed EMOS v0.1.12 and P4 console r07 candidates identified in W1.
No resident firmware change, new transport API or flash is required by this
plan. Allocate the fixture/build identity under the versioning policy when
implementation begins; `UPBENCH.BIN` below is its proposed deployment filename.

This measures the complete selected output path, including UART waits and
receiver work that blocks transmission. It does not isolate EMOS CPU time.
Browser presentation, generalized callbacks, new core assignments and the
deferred Nurples controller are outside this increment.

## Cases

Each measured row transmits **32,768 bytes**, organized as 512 repetitions of
the same 64-byte payload. Test all four entry paths with both payloads in
each mode, for three repetitions: **48 measured rows**. Alternate Legacy and
ExCom groups within each repetition. Keep the order and record each ordinal.

| Entry path | Application operation per 64-byte chunk | Interpretation |
| --- | --- | --- |
| `byte` | 64 calls to RST `10h`, each with the next byte in A. | Public single-byte output, including caller-loop cost. |
| `count` | One RST `18h`, HL pointing to data and BC = 64. | Counted output at a fixed 64-byte call size. |
| `delimiter` | One RST `18h`, BC = 0, A = `FFh`; append that delimiter to the source buffer. | Delimited output; the delimiter is not transmitted. |
| `cli-putch` | Execute `VDU <64 decimal byte values>` using `mos_oscli`. | Existing resident C `mos_cmdVDU` → `putch`, including CLI parsing and restoration of its mutable command buffer. |

The fourth row needs an explicit qualification. MOS does not export resident
`putch` through its public C function table. An application's C `putchar`
normally reaches RST `10h`, so it would duplicate the first row rather than
exercise that resident C entry. The existing `VDU` CLI command reaches the
intended code without a new firmware API or a hard-coded ROM call. Prepare
decimal text outside timing; include the per-call scratch-buffer copy in this
row's elapsed time. Do not subtract the first row and call the difference
“putch overhead”: the CLI parser and different callers also contribute.

| Payload | Exact 64-byte chunk | Purpose and final pixel |
| --- | --- | --- |
| `null` | 64 zero bytes, each VDU 0. | Minimal drawing work; target pixel remains black. |
| `points` | Eight records `[25, 69, x, 0, 24, 0, 0, 0]`, for x = 8, 16, …, 64. | Eight absolute foreground point plots, each followed by two VDU 0 bytes; target (64, 24) becomes white. |

Neither payload contains `FFh`. All four entry paths must emit identical
payload bytes; boundary queries and setup are separate traffic. The point
case performs 4,096 plots per row. It is a small drawing workload, not a proxy
for every sprite, bitmap or game operation.

## Setup and invocation

The deployment package contains `/bin/EMBOOT.BIN`,
`/extender/uartbench/UPBENCH.BIN`, an initially writable results directory,
and a manifest identifying both binaries and the selected firmware baseline.
Back up the existing autoexec before an authorized deployment. Proposed
noninteractive `/autoexec.txt`:

```text
VDU 22 3
LOAD /bin/EMBOOT.BIN
RUN
EMOS KEYINPUT extender
VDU 22 0
EMOS EXCOM --keep-display
VDU 22 0
CD /extender/uartbench
LOAD UPBENCH.BIN
RUN
```

Autoexec alone selects video modes: mode 3 for boot smoke, then mode 0 on
each display. Mode 0 gives 640×480, 16 colours and 60 Hz on mainboard VDP.
The fixture must never issue VDU 22. It requests route changes through public
`mos_oscli` commands `emos legacy --keep-display` and
`emos excom --keep-display`, using a fresh mutable command copy each time.
After each switch it checks the command status and obtains fresh mode data;
incorrect route/mode or missing replies abort the comparison.

Before every row, outside timing, the application restores full viewports,
default origin and palette, turns the cursor off, clears the screen, disables
logical coordinate scaling, and selects white foreground on black. It waits
for a fresh pixel reply confirming the cleared target. No other application,
sprite animation or display-query producer runs during a row. The selected
USB keyboard source remains Extender in both modes; the operator leaves keys
released during timing. Keep one visible, connected browser video client
throughout both groups and record that condition. Do not change client count
or background the page between rows.

The application saves progress between rows and returns to Legacy with the
Extender keyboard still selected. Its final mainboard report identifies the
results file and distinguishes complete, failed and incomplete runs. No
keypress is required for setup, measurement, saving or normal completion.

## Timed boundaries

Use MOS's existing clock through the public sysvars pointer. Read its low
24 bits with one ADL load, without disabling interrupts, and calculate
differences modulo 2²⁴. The fixture duration is far below that wrap interval.
The retained mainboard ISR increments the clock by **two per VBlank**. At
60 Hz this is nominally **120 raw units per second**, with one-VBlank
(about 16.67 ms) resolution. Preserve raw values; do not treat each unit as
an accurate 10 ms or claim sub-frame timing from these readings.

1. Finish setup and its reply, prepare data, and record `t0`.
2. Send the 512 chunks through the chosen entry and record `t1` immediately
   after the last output call returns. No printing, SD access, number
   formatting or per-byte timing instrumentation belongs inside this window.
3. Clear the pixel-response flag with `mos_clearvdpflags` (mask `04h`), then
   send `VDU 23,0,132,64,0,24,0` through the common counted-output wrapper.
   Wait with `mos_waitforvdpflags`, recording the first success/timeout status.
   Revision r03 continues observing the same reply on either route until
   600 clock units have elapsed, with a 24-call CPU backstop. It checks the
   deadline between calls and rejects a reply arriving beyond it. This change
   follows the measured 66-tick post-clear ExCom response, versus the first
   stock wait expiring at 30 ticks. Preserve that first timeout separately;
   benchmark completion does not establish ordinary API deadline compliance.
4. Record `t2` on success, then copy the returned pixel sysvars into RAM and
   validate the expected black/white value. Save and print only afterward.

Report `send = t1 − t0`, `tail = t2 − t1` and `complete = t2 − t0`.
Also retain setup/query wait ticks and first statuses. The small common query
observer is part of tail cost on both routes; payload sending is unchanged.
`send` ends when the last call returns, not when the UART's final stop bit
leaves the pin. `tail` includes residual transmission, parsing, drawing,
query/reply traffic, interrupt service and waiter overhead. It is not pure
render time. The reply proves the queried logical drawing boundary, not
delivery of a browser frame or monitor scanout.

Both selected VDP and EDP `sendScreenPixel` implementations call
`waitPlotCompletion()` before reading the pixel and replying. Serially issued
queries with cleared flags avoid accepting a retained completion flag; there
must be no outstanding pixel query from setup. The existing Pingo-specific
callback and a new generalized callback facility are unnecessary here.

At 1,152,000 baud with 8N1, the payload alone has a theoretical wire minimum
of about 284 ms. That makes the mainboard clock useful for an initial coarse
comparison. Report medians and ranges of the three raw measurements, nominal
bytes/second and ExCom/Legacy ratios. Mark intervals below clock resolution
as unresolved; do not invent precision or subtract an assumed fixed overhead.

## Selected-case analyzer capture

The complete suite need not fit in one acquisition. A `trace` invocation of
the same application runs one ExCom row using the identical workload and
saving the same fields. For example, change only autoexec's final line to
`RUN . trace count points`. Implement the full-suite path first; select which
row to capture from its timings rather than scheduling captures of all rows.

Use the existing r03 probes: yellow PC0 (eZ80 TX → P4 RX), gray PC1 (P4 TX →
eZ80 RX), orange PC2 (eZ80 RTS → P4 CTS), purple PC3 (P4 RTS → eZ80 CTS),
and common ground. Their acquisition is **24 MHz, 288,000,000 samples**,
nominally 12 seconds. These probes see UART1 only. They cannot establish
Legacy UART0 wire timing or mainboard VDP CTS occupancy.

The host resolves the known analyzer and arms it before the explicit Agon
reset cue. Allow the usual two-to-three-second boot time. The operator uses
the Agon's reset button with both boards powered and ribbons seated. Do not
open P4 serial just to record this run: that can reset the running receiver.
Machine-specific access details stay in `HARDWARE.local.md`.

The trace starts its row with a completed pixel query at a distinct coordinate
(200, 400), outside timing, and ends with the target query above. Decode both
directions at 1,152,000 baud, 8N1. Require both boundaries, the full known
payload and the final reply inside the actual capture extent before treating
the capture as complete. Compare the decoded payload with the expected bytes.
Measure wire span, framing errors, CTS-high periods and forward-UART idle
intervals in that window. CTS-high overlap identifies receiver backpressure;
it is not an exact measure of eZ80 CPU stall time. Idle with CTS low may
include caller/IRQ work and does not alone identify its cause.

End host acquisition when its requested samples finish, with a bounded wait
for missing progress. This installed P4 image emits no new fixture-specific
PASS: do not reuse a runner condition that waits for one, and do not add a
90-second serial window. The application's saved result and mainboard report
establish completion separately. This acquisition-only procedure therefore
does not claim the serial post-PASS observation used by earlier paired probes.
A short capture invalidates its waveform coverage, not an independently valid
SD timing row. If the selected row exceeds the window, report that limitation
and revise the capture duration before recapture, without shortening only one
mode's benchmark payload.

## Durable results and validity

The application chooses an unused 8.3 CSV filename in its results directory;
it must not overwrite an earlier run. Store measurements in RAM during each
row, then append, sync and close the file between rows. Write a final complete
record only after all 48 rows and the normal return have succeeded. SD failure
must be visible and must not be called a durably recorded pass. On SD return,
the host collects and hashes the CSV with its package manifest and any capture.
An offline file ordinal is not a UTC run identity; the host associates the
file with the actual run record under the versioning policy.

Record firmware/fixture identities, mode dimensions and colours, baud, browser
condition, route, entry, payload, chunk/count/byte totals, repetition/order,
raw timestamps/deltas, output/reply status, pixel RGB/index and row validity.
Keep returned API status distinct from measured physical byte delivery:
W2 found asymmetric counted carry behavior and incomplete partial-write
reporting. Do not impose a shared carry-success convention on both routes or
claim that a final pixel alone validates every repeated payload byte.

Stop on known send, mode, reply or pixel failure; do not record a timeout as
a slow successful row or retry a partially transmitted stream in place.
Attempt the established Legacy return through EMOS and retain the partial
CSV. Stock Legacy output can wait indefinitely for CTS; a between-call
deadline cannot preempt that call. The operator's reset remains recovery for
that case, and a missing final record makes the run incomplete.

## Implementation and review boundary

The Author has authorized implementation and exploratory SD deployment. Necessary checks
are exact payload/caller selection, clock arithmetic and CSV durability,
route/reply failure handling, and no fixture video-mode changes or direct UART
access. Inspect the built wrappers to ensure each case reaches its intended
entry. Use an isolated emulator to review invocation, both route requests,
results and normal return; emulator elapsed times do not qualify hardware
performance. Reuse a controlled peer only as needed for functional review.
The subsequent explicit SD-deployment instruction authorizes this unchanged-
firmware diagnostic after local functional checks. It does not authorize a
commit of emulator-related changes without human review. Collect the paired
hardware baseline before choosing a repair from the W2 findings.

## Bounded research references

The source/document selections remain those in W1; official checkouts were
used read-only. Relevant contracts are:

1. [MOS API][api]: RST output, sysvars, `mos_oscli`, clear/wait VDP flags and
   the C function table; [CLI commands][cli] for `VDU` and `RUN` arguments.
   [Resident MOS CLI][emos-cli] supplies `mos_cmdVDU`'s actual C `putch` calls;
   [resident API table][emos-api] has no exported `putch` entry.
2. [VDU commands][vdu], [PLOT modes][plot], [screen modes][modes] and
   [system commands][system]: null bytes, point plotting, physical coordinates
   and the screen-pixel query.
3. [Stock pixel-query implementation][stock-sys] and
   [retained EDP implementation](../../../vdp/video/vdu_sys.h):
   `sendScreenPixel` waits for plot completion before returning pixel data.
   [Stock clock ISR][clock] and the retained EMOS ISR explain the two-unit
   increment; the API's centisecond label is insufficient for conversion.
4. [Existing paired route wrapper](../QUAL-003/suite/src/asm/paired.inc),
   [bench constraints](../../qualification/bench-constraints.md) and
   [version policy](../../versions/README.md) govern invocation and evidence.

[api]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md
[cli]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Star-Commands.md
[vdu]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDU-Commands.md
[plot]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/PLOT-Commands.md
[modes]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Screen-Modes.md
[system]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md
[emos-cli]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/mos.c
[emos-api]: https://github.com/bgates747/agon-emos/blob/82929c4b3e64c370d1102f46f61e8b600d57d665/src/mos_api.asm
[stock-sys]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h
[clock]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/interrupts.asm
