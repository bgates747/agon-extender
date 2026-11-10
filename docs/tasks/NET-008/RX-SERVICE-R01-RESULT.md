# NET-008 — Receiver correction and corrected modem qualification

The corrected P4 UART appliance passes a full-load, full-minute internal
1152000baud peripheral control. The external P4/ESP8266/Pi5 path passes a full
minute at384000baud, where the prior appliance overran. Higher external rates
produce retained CRC failures without P4 receive-overrun events. The exact cause
among the original receive-service hazards is not individually isolated; the
higher-rate byte loss is also not yet localized to a particular component.

## Changes and source findings

| Setting/path | Previous appliance | Corrected appliance |
|---|---|---|
| Main/RX task priority |1, below TX5|8, above TX5|
| TX task affinity |Unpinned|Core1|
| RX FIFO interrupt threshold |120bytes|32bytes|
| UART interrupt/storage |Default priority, not IRAM-configured|Level2, IRAM ISR/internal driver storage|
| USB reporting while receiving |Synchronous progress and error formatting|Deferred diagnostics; host reports its bounded wait|
| RX software ring |32768bytes|32768bytes, unchanged|
| Integrity/data workload |1024B pattern, CRC32, sequence/counts|Unchanged|

Pinned IDF b774170ff46c393eeb5e495ea37936038d3f4f4f defines128-byte HP UART
FIFOs and defaults the interrupt threshold to120. That leaves only about eight
bytes, approximately0.2ms at3840008N1, for service after the threshold. The driver
also disables normal RX draining if its software ring is full. These explain how
service delay can become a hardware FIFO overrun despite a large software ring;
they do not prove which delay caused the original attempt's first event.

The correction removes avoidable receive-service hazards rather than increasing
the ring or throttling the test producer. Task-level ring/queue observations and
read-call gaps are retained; they are not ISR-latency or true ISR high-water
measurements. Known source behavior and causal hypotheses remain distinguished in
[the source review](RX-SOURCE-R01.md).

## Independent P4 control

The supported IDF internal UART loopback exercises the UART serializer/FIFO,
ISR/ring and concurrent producer/CRC consumer. GPIO47/48 remain inputs, with no
modem-pin routing or test traffic sent to the ESP8266. It does not qualify
external pad electrical behavior, clock tolerance, wiring or RF.

All five reconstructed service profiles passed short384000controls. These are
NOT bit-identical old firmware: compile-time IRAM/internal storage and TX-core
pinning are shared. In particular IDF adds IRAM allocation even when a profile
passes interrupt flags0. The comparison therefore cannot isolate the original
cause or claim that a single profile change fixed it.

The corrected profile then passed1152000short/10/30/60windows. Final results:

| Metric | P4 internal loopback |
|---|---:|
|Nominal baud|1152000bit/s|
|TX/RX complete payload frames|6872/6872|
|Matched payload bytes|7036928|
|TX start-to-drained window|62.033085s|
|RX first-to-last complete frame window|62.023551s|
|Nominal8N1 wire utilization|Approximately100%; required95%minimum|
|UART/CRC/frame/ring/FIFO errors|0|
|Largest observed ring/queue sample|50bytes/33events|

This is actual hardware peripheral evidence, not a software queue simulation.
The UART clock report and nominal timebases were not externally calibrated.

## External modem results

Worst failures first; passing operating points are separate from hardware limits.

| Baud, bit/s | External result | P4 RX error events |
|---:|---|---:|
|1152000|Pi CRC mismatch after16 accepted frames; retained|0|
|576000|Initial short pass, repeated short CRC failure; unqualified|0|
|384000|2/10/30/60s all pass|0|
|230400|Short pass here; prior full-minute operating point|0|
|115200|Short pass|0|

The accepted operating point increases from230400 to384000 nominalbaud, +66.7%.
This compares qualified points in retained runs, not an absolute device limit or
RF-controlled throughput comparison.

Final384000duplex results:

| Direction | Payload bytes | Frames | Receiver window | Payload/window |
|---|---:|---:|---:|---:|
|P4→ESP8266→Pi5|2348032|2293|62.083365s|37820.63B/s|
|Pi5→ESP8266→P4|2371584|2316|62.596361s|37886.93B/s|

Both endpoints' counts agree exactly; CRC/pattern/sequence checks pass, P4 UART,
CRC and frame errors are zero, normal modem cleanup succeeds and UART retires.
Payload/window excludes frame overhead and begins at first completed frame;
TCP buffering/first-frame exclusion prevent treating it as calibrated wire rate.

For each high-rate fault the Pi receives a CRC-invalid P4-origin frame and closes
the connection; the later incomplete P4 incoming frame is a consequence, not
proof of a P4 receive fault. In the576000capture, data initially matches then
skips100expected stream bytes; all224remaining captured bytes match the shifted
expected pattern. The1152000capture has a first apparent500-byte skip followed
by further differences. These locate gaps in the end-to-end byte stream, not the
processor, FIFO or physical wire where loss occurred. No absolute ESP8266 ceiling
is claimed. Both failures were retained and command mode positively reconciled
before deliberate lower-rate qualification; failed high-rate arms were not replayed.

## Identity, cleanup and retained evidence

Frozen contract03aae5cd precedes implementation. Identified source fc061128,
build net008-uart2-rx-service-r02-b2026-11-10-18-33-23Z,243168bytes,
SHA2568e0f2f627d9f74a0e324152ea7d2398a18b12e6e4203519c4eee5cf2de8bd403.
Six qualification-oracle controls and prior native CRC/private-packet/real-TCP
controls pass; strict P4 build45.797host seconds. Compiler and hardware workers
retain their actual parent results, including nonzero failed arms.

Product P4 d9b was restored through the exact changed245760-byte prefix with
independent readback and retained unchanged product suffix. Boot/services/input,
CLI/whole startup+listener read/EXIT, fresh mode0/callback0/backend0, idle worker,
free ports and all owner groups passed. Native VDPdc43, EMOSa25f, startup,
partitions/NVS and ESP8266 firmware remain unchanged. Modem lastassociated baud
384000. No test autorun, persistent modem setting or credential capture occurred.

Lease170 was normally released by the dedicated scheduler after the actual
joined/fresh stopped handback. Primary target access is stopped. The diagnostic
artifact remains retained, not installed; it is not a production promotion.
Ignored evidence is under agents/net008/connect-r02/physical170-* and the
physical170 installation/restoration/fresh-handback records in
agents/net008/bench-test. Raw CRC failures and byte-gap analysis remain available.
