# Parallel block-boundary attribution

The large apparent setup cost is P4 command processing serialized ahead of the
next transport admission. P4 receives a full block, executes an inline update
byte by byte, and services the next UART offer only after its receive queue is
empty or the command ends. Five measured samples show 48.34–52.53 ms in that
command, including 18.92–20.59 ms around 4,086 native-mutex acquisitions. Each
individual acquisition stays below 0.314 ms; there is no single 50 ms lock wait.
This identifies the owner and operation consuming the interval. No transport
fix is included. The complete incoming pair is restored and verified; production is unchanged.

## Frozen workload and measurement

The same mode 0, single-buffered fixture runs four independent ExExt cases, one
warm-up and five measured rows each. Wire lengths 256/4096/4097/8192 include the
11-byte inline buffer-adjustment header. A following seven-byte query provides
an ordered processing reply. EMOS owns routes, offers and Port C handover;
P4 owns native reception, its byte queue, command parsing and replies. No CRC,
substitute checksum or software COMPLETE/ACK is added.

Canonical EMOS source `2fc7b269d57f95ead9ba3a6748852cb84e311186` and builder
`49dc33fee817cb184572351ee71dae7da9a139c4` produce
`agon-emos-v0.1.27-b2026-11-02-04-23-34Z`, 128,881 bytes, 2,191 bytes free.
The raw image SHA256 is
`89558bb1aae2ffafe1c916b3ba349e66ba7ebf509f3e5ad856c5b6615b4c722c`;
padded full-ROM SHA256 is
`b0b0ca1a2ed79aa2ca290077787f9d318f55003f2837ae1add44ee6e9014ff3b`.
The fixture `port-008-phase-timing-r01-b2026-11-02-04-24-47Z` is 15,698 bytes,
SHA256 `604955cfaba60af4f95b4e8a68850fc4bd5722a65db0211688297c07619b2522`.
It is bound to the exact linked ROM/ELF and fourteen actual phase CALL sites.

P4 baseline source `03e428f3bb87951bd4f296ccb36ef677ef1db617` and application
`port-008-stream-r17-b2026-11-02-01-06-24Z` remain the exact preceding matched
composition: 1,828,032 bytes, SHA256
`4e2e5348cc798336d94fa1655b32de61b52a0ce55a86dc3024e01eed49f5a1aa`.
Physical board, display, USB hosts, SDK, compiler, cache component and wiring
are unchanged. Mainboard VDP is not flashed.

## EMOS-side localization

1. In the 4097-byte case, the first 4096-byte native payload takes 15.694 ms.
   Four measured rows then wait 46.35–47.15 ms from the one-byte tail offer to
   admission. The tail's native payload routine takes 0.125–0.139 ms.
2. In the fifth measured row, the tail is admitted in 1.15 ms; the following
   seven-byte query offer instead waits 46.53 ms. A fixed one-byte transfer or
   pin-switch penalty cannot explain that movement.
3. After 256 wire bytes, the following offer takes approximately 3.6 ms instead
   of an initial offer's approximately 1.1 ms. After a full 4 KiB it takes 45–48 ms;
   the 8 KiB command incurs two long intervals. The delay scales with processing
   of preceding data.
4. The entire native payload and the individual admission waits have different
   scopes. Do not label their sum as pin switching, payload throughput or
   rendering completion. The eZ80 timestamps alone cannot identify P4 mutex
   blocking, preemption, parser CPU work or response scheduling individually.

The following are medians of five measured samples, in milliseconds, ranked by
largest aggregate admission wait first. Each cell totals all blocks through the
ordered query/reply, including its seven forward and six reverse bytes. It is
not only the named payload's transfer. Independent column medians need not sum
to the median total.

| Command wire bytes | All offer-to-admission (ms) | All native payload routines (ms) | All park (ms) | All electrical entry (ms) | All reciprocal return to unpark (ms) | Ordered reply total (ms) |
|---:|---:|---:|---:|---:|---:|---:|
|8192|93.2500|31.6667|0.1806|2.5278|1.2917|133.3333|
|4097|49.7778|16.0972|0.1806|2.5000|1.2083|83.3472|
|4096|49.0556|15.9722|0.1250|2.1389|1.0278|83.4306|
|256|5.7500|1.3750|0.1250|1.8889|0.7500|16.6528|

Reservation, packet construction, inclusive service/poll/publication and
outside-block intervals remain separately retained in the phase evidence.
Nested scopes are not added again. Format 4 ends its recorded block at unpark;
remaining cleanup is not replaced by invented zero-duration completion phases.

## P4 observation and implementation limits

The default-off P4 observer confirms the source-level coupling in
`console_stream.hpp::read()`, `console_hardware.inc` and
`vdu_buffered.h::bufferAdjust()`: the parser task also services I/O progress;
its byte read calls that progress function only when the parallel queue is
empty. The inline multi-target/multi-operand update locks/unlocks the native
recursive mutex for each target byte. In this fixture that is a SET operation
with 4,086 operand bytes, not a bulk copy into an input buffer.

After the full block is retired into P4's queue, the parser's update covers the
long gap before recognition of the following offer. Once P4 recognizes a timed
offer, local recognition-to-acceptance takes 0.073–0.200 ms across the measured
groups. That timestamp precedes reply enqueue; it is not a UART wire-completion
timestamp.
In sample 3 the one-byte tail is already admitted before adjustment begins;
the following query waits for the same loop. Both processors' independently
ordered records agree on which block encounters the wait. Their absolute
clocks are never subtracted.

Worst command elapsed first; all values below are P4 local milliseconds. Samples
are the five measured records, excluding the warm-up. Acquisition totals include
observer/preemption and acquisition overhead; the remainder includes byte reads,
updates, unlocks, split-tail service and other elapsed scheduling. Neither is a
count of retired CPU work.

| Sample | Whole adjustment (ms) | Native acquisition total (ms) | Maximum one acquisition (ms) | Previous retirement to next recognition (ms) | Delayed block |
|---:|---:|---:|---:|---:|---|
|2|52.526|20.594|0.284|50.429|One-byte tail|
|4|52.197|20.066|0.294|50.453|One-byte tail|
|5|51.378|19.552|0.313|49.816|One-byte tail|
|1|50.613|18.919|0.215|49.021|One-byte tail|
|3|48.336|19.908|0.250|48.991|Seven-byte query|

Median command elapsed is 51.378 ms; median aggregate acquisition elapsed is
19.908 ms. This does not prove that lock contention alone owns the delay. The
unobserved original P4's 46–47 ms wait and observed P4's 49–50 ms wait are different
instrumented compositions: the observer adds two local clock reads per native
acquisition, task filtering and aggregation. Do not claim exact uninstrumented
lock cost or a performance regression from those raw figures.

Observer source `74006a514c2f03b11744dd741dc3e677df0a6b74` produces
`port-008-stream-r17-b2026-11-02-05-43-40Z`, 1,841,264 bytes, SHA256
`184fb0bf75e2f31b7631a9b2a3c33b9ad1a24beede691a9a849a24c326e4bbd4`.
The native build/graph validation and all unchanged composition checks pass.
Actual locks, byte processing, transport and scheduling remain unchanged.
Records are bounded in PSRAM and fetched after completion and Legacy STOP.

The first observer source `fb867f5f` cannot arm native reception on the first
43-byte CLI packet during three setup-only entries; no timing fixture is invoked
on that image. P4 stays alive with fault-free scanout; Agon-only reset restores
actual CLI. Moving approximately 6 KiB of accidentally internal static records to
PSRAM restores native entry; observed free internal RAM rises from 45,367 to 51,559
bytes. The original receiver's exact allocation-failure stage is not proved.
The repaired composition adds failure-only SDK-stage diagnostics and preserves
successful receiver behavior.

The observed 4097-byte run completes six zero-flag CSV rows. Its warm-up USB dump
contains 8,115 bytes; each of the five measured dumps contains all 8,192 expected
bytes. The session recorder fills 128 offer slots and drops 41 later events during
CLI teardown. The complete required measurement prefix ends at offer index 55;
all six adjustment scopes and all six ordered 4096/1/7/6 block groups are present,
with monotonic sequence/recognition/acceptance/retirement and matching eZ80 phases.
The last retained offer is over 10 seconds after the final adjustment. Therefore
the timed prefix is complete, while the whole-session trace and whole-acquisition
byte-proof pass remain explicitly refused. No missing record or byte is invented.
The raw invalid/dropped fields and short acquisition are preserved.

A host adapter initially refuses this diagnostic JSON because it applies a
controller status response's 4 KiB cap. A bounded 32 KiB HTTP read retrieves the same
frozen records without rerunning the workload. This ordinary retrieval correction
does not erase the separate capture and teardown-capacity limitations.

## Acquisition, controls and clocks

1. Six captured acquisitions retain 36 CSV rows with zero flags. Two original
   byte dumps and one unrelated dump in a labeled repeat are short. They remain
   failed acquisitions, not claims of corrupt parallel payload. First-complete
   integrity-only selection supplies 24 actual 8192-byte proofs:22 original rows
   and two labeled repeats,196,608 actual decoded bytes. No timing-based selection,
   padding or reconstruction supplies missing bytes.
2. Both affected baseline cases, 256/4096, pass a 60-second capture-body-absence
   control with six zero-flag rows and positive CLI, no panic/restart. The exact
   existing no-dump P4 app is
   `4ea314bd679fa90f73d2eaf5542f35710cd0b6248ae1e8d59764221dfe6c0956`.
   These controls neither supply missing bytes nor qualify the new observer.
   The newly marked 4097 observer case requires its own post-campaign control.
   That control removes both USB buffer-dump code and the boundary observer,
   retaining the identical product transport/parser/display implementation;
   its unavoidable diagnostic/binary differences are reported separately.
   With both observations absent, four measured tail offers take 45.597–47.556 ms;
   in the fifth row the tail takes 1.417 ms and the query takes 46.389 ms. The long
   admission wait therefore reproduces without either P4 observer. This does
   not establish which diagnostic caused the short USB acquisition.
   One control setup stops before RUN after the CLI receives `MOS STATUS`
   without its leading `E`. The host adds one second after clearing the screen,
   performs one Agon reset and two actual CLI exchanges, then invokes the first
   actual control RUN. The missing character's underlying cause is unproven;
   no failed workload is replayed.
3. Three planned capture-recovery Agon resets and the observer setup recoveries
   pass actual CLI/read/EXIT without replaying an uncertain RUN. No hardware
   operator action or P4 reset fallback is required for those recoveries.
4. eZ80 PRT1 uses the nominal 18.432 MHz clock divided by 256: 72,000 counts/s,
   13.8889 microseconds per tick. Interrupts and elapsed waiting are included.
   Equivalent cycle conversion is not retired-instruction counting. P4 uses
   local `esp_timer` microseconds, truncated to32 bits; compare local modulo
   differences only. Neither oscillator is independently calibrated and the
   processors' absolute timestamps are not synchronized.
5. Fixture timing excludes Pi preparation, serial byte dumps, retrieval and
   notification. This is not a rendering, scanout, gameplay, full-suite or
   file-transfer speed qualification.

## Restoration and next boundary

The Pi independently reads the complete 16 MiB P4 flash and 128 KiB EMOS ROM and
compares them byte for byte with the retained incoming images. The restoration
writes the original bytes across the largest diagnostic erase span:1,843,200
bytes at 0 x 20000, including the tail beyond the shorter incoming application.

| Restored item | Exact result |
|---|---|
|Complete P4 flash|16,777,216 bytes; SHA256 `006397a5a8b0f0e47d350e4a63b4f849c4a75635e7f5569a02f2b8a57871f84b`|
|P4 application|`indexed-hdmi-r25-b2026-11-01-20-18-04Z`; SHA256 `eb1334276c0c6e5766f718b2aef7984c382931b2a6ae6cb39c0a7ea3332c0645`|
|Complete EMOS ROM|131,072 bytes; `agon-emos-v0.1.27-b2026-10-26-01-06-54Z`; SHA256 `84da2c5ac3cebb1c470bab201f797a936296a6bfc33b6ebdbcf5d1dd3a1d1d79`|
|Startup|Unchanged 108 bytes; SHA256 `9e97ceae5489e1b6330c6a2f207d95c6566c60cac304d65e7aad54b610a5b423`|
|Listener|Unchanged 22,968 bytes; SHA256 `04e7ef596a862b1a6b4f265b6c647e461ef0f65db4851873ac3dd31e4f03f10d`|
|Mainboard VDP|Never flashed; retained F060, no new independent full-flash readback claim|
|Handback|Mainboard/P4 mode 0, Legacy route, text/visible/flashing cursor controls on both displays; actual CLI twice verified; ready neutral input and valid USB controller|

All readers, transfer sessions and independent reset holders are released; the
final device-owner query reports no owner on either serial device. Startup is
never edited and never launches a test. No SD unmount, optical cursor/pixel pass,
wide-mode correction or production promotion is claimed. Incoming R25's known
wide-mode deadline limit remains.

The [portable evidence](BOUNDARY-LATENCY-EVIDENCE.json) retains selected CSV and
phase rows, actual decoded buffers, full P4 timed-prefix records, all acquisition
quality flags, bounded controls, artifact identities and restoration proof.
Original captures, binaries, readbacks and private finite helpers stay in the
ignored local record on Pi; that record is evidence, not a deployment recipe.

The [task contract](BOUNDARY-LATENCY.md) stops this tranche at diagnosis and
restoration. The smallest transport correction to propose next is for the
existing P4 I/O owner to service pending offers at bounded points while the
parser still has queued bytes, admitting only what its existing 8 KiB receive
queue can hold. EMOS continues to authorize every route, offer and pin handover.
That proposal requires reentrancy/ownership checks and a matched comparison;
it is not implemented here. Reusing bulk input operations or reducing per-byte
native guards is a separate parser/display change, not a transport-only fix.
No coarsened locking, separate service task or decision on P08-D02 follows.

## Observation refinement

The P4 collector uses recognition, admitted storage and native-buffer retirement
rather than adding a second trace of every UART enqueue/drain and native phase.
The eZ80 phases already bound the native phases; the P4 records put the long
interval before the offer handler recognizes its packet. No separate P4 UART
wire-completion timing is claimed. This smaller observation suffices for the
identified cause and avoids another diagnostic code cut. Its complete timed
prefix is usable for attribution; its whole-session collector is not qualified
for reuse without addressing post-workload capacity.
