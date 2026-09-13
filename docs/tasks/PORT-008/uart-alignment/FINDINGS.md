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

## U12 — current probe-channel mapping

ROM register readback verified all eight P4 endpoints as inputs before the
Agon walk. Unchanged HW-002 assembly emitted exact pulse counts1through8;
legacy analyzer independently checked the observed mapping. PC0..PC7 map to
D1,D6,D3,D4,D5,D2,D7,D0 respectively. Thus UART forward isD1, returnD6,
Agon RTS/P4 CTS isD3, and P4 RTS/Agon CTS isD4. No wiring moved.

Acquisition limitation: fx2 returned3,038,208 of6,000,000 requested samples
at100kHz,30.38208seconds, despite exit0. This is a partial acquisition, not
a60second pass. Every PC pulse and9.73751seconds of quiet tail were present,
so the observed channel mapping is established; full-duration acquisition is
not claimed. High-speed UART capture must separately meet its exact extent.
P4 flash was untouched; explicit resume restored its installed application.
Exact original startup and its pre-test backup were restored with readback;
the one-shot marker was confirmed consumed. Local captures/ROM/SD journals
retain private evidence; `results/pinwalk-map.json` records public findings.

## U12 — pure UART wire attribution

Full720million samples at24MHz; both independent decoders agree, all65,535
forward bytes and2,048return payload bytes match the PRNG, all257return
records have the expected sequence/completion, all four application rows pass
and recovery0. The oracle rejects eight injected loss/corruption/reorder/
missing-completion/framing variants. No browser, serial observer or rendering.

The following columns partition each P4-wire payload span. Positive permission
means the receiver holds its active-low handshake low. These are elapsed wire
measurements, not sampled CPU instruction timings. Largest total first.

| P4 UART direction | Span ms | Byte occupancy ms | Idle with permission ms | Idle under receiver backpressure ms |
| --- | ---: | ---: | ---: | ---: |
| Agon → P4,65,535bytes | 2099.394 | 568.880 | 1530.514 | 0.000 |
| P4 → Agon,4,626wire bytes | 109.609 | 40.132 | 0.140 | 69.336 |

1. **Forward:** P4 RTS stayed permitting throughout the65,535byte payload;
   zero receiver backpressure. The1,530.514ms idle therefore cannot be assigned
   to P4 receive throttling or rendering. Destination elapsed2,100.970ms agrees
   with the2,099.394ms wire span plus probe/header overhead. Current EMOS still
   runs the layered C per-byte sender identified by AUDIT-005; this is a concrete
   next software lead, not an instruction-level attribution from the sniffer.
2. **Return:**99.80% of inter-byte idle overlaps Agon RTS withholding permission.
   P4 spends only0.140ms idle while permitted across the full reply burst.
   Request-to-final-byte is111.055ms; the P4 enqueue counter is0.596ms and must
   not be presented as completion. Stock's corresponding request-to-reply
   measurement is approximately83.3ms on MOS's coarse timer; UART0 is not on
   these probes, so no invented stock wire-span comparison is made.
3. Neither direction starts a measured byte while its receiver withholds
   permission. Exact decode and no measured framing errors supply no evidence
   for cable corruption here; they do not qualify analogue signal integrity.
4. P4-only tuning cannot remove sender-created forward gaps or Agon-controlled
   reverse pauses. Preserve this result instead of rewriting stock VDP logic.
   U11 will now repeat the paired rendering workload with these UART changes.
   Any EMOS transport work requires a separately bounded stock-reuse contract
   accounting for resident ownership/deadlines and its existing dirty work;
   this finding does not silently extend the current port patch into EMOS.

## U11 first graphics run — retained partial failure

The unchanged39case fixture saved483intervals, then timed out at repeat3,
mainboard/Legacy route0, BSP21_01 draw: status15, submission48rawticks,
reply wait1200rawticks. Seven baseline probe mismatches had been recorded.
P4 snapshot delta0. The application returned to foreground sdserve, its
closed CSV was collected and service exited. This is not a complete paired
graphics result; do not feed it into the full-pass comparison tables.
The exact failing operation is on the mainboard display route, whose firmware
and fixture match the prior completed baseline. No claim of root cause or
EDP regression is made. PLAN.md permits one unchanged retry after an explicit
mainboard reset; no case exclusion, new firmware or timeout change.

## U11 completed retry — loading and rendering stay distinct

The identical retry completed all624intervals, with the same eight SHP23
probe differences as the original baseline and zero P4 snapshots. Full strict
sequence/count/byte metadata validation passed. The prior mainboard timeout
is retained; this retry does not establish that the diagnostic is universally
reliable. No firmware, asset, test case, timeout or renderer was changed.

[Side-by-side graphics tables](results/graphics-comparison.md) show stock VDP,
current EDP and prior EDP, in milliseconds with explicit percentage changes.
Seven of eight upload-heavy stages improve by3.1–3.9%; the smallest is unchanged.
The largest stage falls from3,165.200ms to3,048.353ms on EDP; stock is881.970ms.
Primitive rendering in that scene is11.462ms on EDP versus37.443ms on stock.
The retained renderer's measured scopes remain essentially at prior values;
the transport change does not turn the loading gap into a rendering defect.
Software-sprite comparisons include matching call counts only; unequal
batching totals remain in the adjacent JSON, not a false per-operation table.
