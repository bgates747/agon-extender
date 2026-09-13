# UART alignment findings

## U06 — pure-data baseline

All336cases completed, exact byte counts/patterns matched, and application
Legacy return succeeded. Both destinations used the same frozen probe/app;
no bitmap creation/drawing. Raw results and identities are adjacent.
Forward figures are destination-clock medians across four patterns and three
repetitions. Positive percentage means EDP takes more time. Bytes/s uses
payload bytes divided by the same destination interval (no overhead subtraction).

| Payload bytes | VDP ms | EDP ms | Time change | VDP bytes/s | EDP bytes/s |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,535 | 589.410 | 2178.151 | +269.5% | 111,187 | 30,087 |
| 32,768 | 295.101 | 1090.270 | +269.5% | 111,040 | 30,055 |
| 4,096 | 37.300 | 138.364 | +270.9% | 109,811 | 29,603 |
| 257 | 2.812 | 10.932 | +288.8% | 91,394 | 23,508 |
| 0 | 0.441 | 1.884 | +327.7% | 0 | 0 |

Return time uses eZ80 request-to-final-reply ticks converted at nominal120ticks/s,
with16.7ms quantum. Destination return `elapsed_us` is enqueue time and excludes
EDP queued draining, so it must not be compared as wire-transfer completion.
Each packet carries8test bytes in an18byte envelope; final completion adds18bytes.

| Test payload bytes | Total reply wire bytes | VDP ms (approx.) | EDP ms (approx.) | Time change |
| ---: | ---: | ---: | ---: | ---: |
| 2,048 | 4,626 | 83.3 | 150.0 | +80.0% |
| 512 | 1,170 | 33.3 | 33.3 | coarse timer |
| 64 | 162 | 0.0 | 0.0 | coarse timer |
| 8 | 36 | 0.0 | 0.0 | coarse timer |

Initial smoke had32correct transfers but used the CLI-only Legacy transition
from an application. Existing EMOS correctly rejected it31; external batch
recovered SD. The corrected full run uses documented --keep-display and has
recovery0. This fixture mistake was corrected without firmware transport changes.
Pure data already reproduces the large forward gap. There is no evidence here
that bitmap rendering is necessary to cause it. No wiring fault is established.

## U08 — bulk read and stock stream timeout

All336cases pass with exact data and recovery0. Only bulk read plus200ms
Stream timeout changed. The large-payload result is effectively unchanged:

|65535byte forward scope|Stock VDP ms|EDP ms|EDP time change vs VDP|
|---|---:|---:|---:|
|Original adapter|589.410|2178.151|+269.5%|
|Bulk-read adapter|589.423|2178.119|+269.5%|

Return256packets remains10ticks stock and18ticks EDP. The missing override is
a stock API difference, but this measurement does **not** establish it as the
throughput bottleneck. Retain the faithful bulk primitive and continue to the
separate RX interrupt timeout experiment. No wiring fault inferred.

## U08a — stock RX idle interrupt timeout

Again336/336exact cases and recovery0. The65535byte forward interval is
589.385ms stock and2101.073ms EDP.
The RX idle timeout2 change reduces EDP elapsed by3.5% versus the bulk-only
candidate, while leaving it256.5% slower than stock. It does not close the
large-payload gap.
It restores stock configuration; neither RX candidate established the cause.
Return256packets remains10versus18ticks. Next is the frozen FIFO-refill change.

## U10 — combined candidate, separate-direction matrix

All336cases pass, exact bytes/order and recovery0. The256packet return burst
drops from18to14MOS ticks (about150.0to116.7ms), a22.2% time reduction. Stock
remains10ticks/about83.3ms: EDP is still40% slower at this coarse resolution.
No throughput parity claim. Forward large-payload remains near the RX2 result.
The simultaneous-traffic extension is next, followed by pure-data wire attribution.

## U10 mixed-traffic failure and U10a ordering diagnosis

UDT006 preserves24rows: all9mainboard trials pass, then EDP257/4096byte trials
pass. The first EDP65535byte trial fails after32MOS ticks (~267ms), retaining
only240of2048return bytes. Terminal status2 and Legacy recovery35; this is
a failure. SD was recovered after reset, not a natural completed batch.

The maintained-owner host test reproduces a400ms gap **inside an18byte reply**
when a400ms next-command read begins with software output pending. EMOS's
existing partial-packet deadline is about250ms. The source ordering and physical
failure timing agree; test the minimal stock ordering restoration next. Do not
change EMOS's deadline. Failed CSV and exact candidate identities remain here.
A subsequent P4 serial-open reset limits its late boot log to recovery evidence;
it cannot identify the original failure. No serial observers in further runs.

U10a ordering candidate passes all36mixed rows with exact forward bytes and
all2048return bytes in every trial; natural Legacy/SD recovery0. Mainboard
remains unchanged. The host model's induced partial-reply gap falls400ms→1ms;
physical EDP65535byte mixed trials now finish in about2207ms instead of aborting
at~267ms. This confirms the adapter ordering defect within this tested scope.
Stock's reply-before-next-command ordering is restored; EMOS remains unchanged.
The full original336case regression is still required before this step closes.

## U10/U10a — separate regression after ordering restoration

All336 original separate-transfer cases pass, with exact bytes and recovery0;
combined with the36mixed rows, the ordering candidate passes both frozen
matrices. No rendering, EMOS change, browser or serial observer.

| Largest transfer | VDP ms | EDP ms | Time change (VDP baseline) |
| --- | ---: | ---: | ---: |
| forward: 65,535 payload bytes | 589.424 | 2101.057 | +256.5% |
| reverse: 2,048 payload bytes | 83.333 | 116.667 | +40.0% |

Return timing remains quantized to16.7ms. Source/build identity and raw
CRLF bytes are retained beside `order-full-analysis.json`. The forward gap
remains: U12 will distinguish permission-to-send idle from P4 backpressure.
