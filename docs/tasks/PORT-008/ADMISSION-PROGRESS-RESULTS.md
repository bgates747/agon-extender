# Buffered admission progress — bounded results

The following-offer wait falls from 46–47 ms to 1.6–1.9 ms after a full block.
EMOS local data completion falls from 83.00 to 38.36 ms at 8192 bytes and from 66.96
to 22.36 ms at 4097 bytes. Ordered processing/reply medians remain essentially
unchanged. This fixes admission serialized behind buffered byte updates; it
does not remove the update work itself.

P4 services its existing I/O owner after at most 64 consumed queued bytes,
including availability checks before top-level nonblocking reads. Native payload
ownership and completed staging withhold parser input until physical UART return
and retirement. Nested progress defers console lease transitions and refuses
recursive reads; controller and parallel control traffic remain serviceable.

## Exact comparison

Mode 0/single-buffered, same EMOS/fixture/phase sites, one warm-up plus five measured
samples at each command length. The 11-byte command header is included. The next
seven-byte query and six-byte reverse reply are excluded from the data-completion
endpoint and included in the ordered-reply endpoint. The command is a synchronous
inline buffer SET, not plotting, rendering, bulk file transfer or scanout.

Baseline is source 03e428f3bb87951bd4f296ccb36ef677ef1db617/application 4e2e5348,
retained in [boundary evidence](BOUNDARY-LATENCY-EVIDENCE.json). The fixed matched
source is `dddc10a2a31d993af577be436b5d14f6aee9de15`, build `port-008-stream-r19-b2026-11-02-13-28-51Z`,
1,828,944 bytes, application SHA256
`102014003d771e1c917782e281bdde607da4632d7b255e0c2ba8285bd8c0fd45`.
Maintained changes are commits 005e133d and 226688ba; only console_stream.hpp and
console_hardware.inc differ under vdp/ from the matched baseline. Native graph,
board, compiler, SDK, display, cache, dual-USB and partition checks pass. Neither
boundary observers nor per-lock clocks are compiled in. The P4 application grows by 912 bytes against the matched baseline; EMOS adds
zero bytes. Wire format 4, queue sizes and ordinary protocol are unchanged; no
CRC, substitute checksum or completion exchange is added.

EMOS remains `agon-emos-v0.1.27-b2026-11-02-04-23-34Z`, raw SHA256
`89558bb1aae2ffafe1c916b3ba349e66ba7ebf509f3e5ad856c5b6615b4c722c`,
padded-ROM SHA256
`b0b0ca1a2ed79aa2ca290077787f9d318f55003f2837ae1add44ee6e9014ff3b`.
The unchanged 15698-byte fixture SHA256 is
`604955cfaba60af4f95b4e8a68850fc4bd5722a65db0211688297c07619b2522`.
The full EMOS ROM is independently read back after its sole installation; only
P4 is replaced for the availability correction, with retained ROM provenance.

All tables use five-sample medians in milliseconds and rank by largest baseline
data-completion elapsed first. Change is 100×(fixed/baseline−1); negative is shorter.
Raw warm-ups, every measured row, min/max, exact phases and decoded 8192-byte buffers
remain in [portable evidence](ADMISSION-PROGRESS-EVIDENCE.json).

## Following offer to admission

The P4 recognizes pending offers while older command bytes remain queued. The
following block's payload duration is outside this admission interval.

| Command wire bytes | Following block | Baseline (ms) | Fixed (ms) | Change (%) |
|---:|---|---:|---:|---:|
|8192|4096-byte data block|46.3750|1.5833|-96.59|
|4097|1-byte data tail|46.4861|1.8472|-96.03|
|4096|7-byte query|46.9167|1.7778|-96.21|
|256|7-byte query|3.5972|1.4444|-59.85|

## EMOS local data completion

The historical receipt_prt column ends after EMOS native cleanup and reciprocal
UART return for the command data. It is not a software receipt, separate wire-drain
stamp, parser completion or rendered-frame fence. This phase composition leaves
wire_prt zero. The 14-site record independently retains each last unpark boundary.

| Command wire bytes | Baseline (ms) | Fixed (ms) | Change (%) |
|---:|---:|---:|---:|
|8192|83.0000|38.3611|-53.78|
|4097|66.9583|22.3611|-66.60|
|4096|19.0139|18.9861|-0.15|
|256|3.7361|3.6111|-3.35|

## Ordered command processing and reply

The query reply follows the synchronous update. Earlier data admission lets EMOS return to the eZ80 application sooner. P4
continues its byte-by-byte update/native-guard work.
Remaining processing may move outside recorded transport-block intervals. Do not
add inclusive service/poll/publication scopes again or call that remainder pin
switching. The following endpoint includes processing, query and reverse reply.

| Command wire bytes | Baseline (ms) | Fixed (ms) | Change (%) |
|---:|---:|---:|---:|
|8192|133.3333|133.5556|+0.17|
|4097|83.3472|83.5139|+0.20|
|4096|83.4306|83.3333|-0.12|
|256|16.6528|16.7500|+0.58|

## Physical payload and return scopes

These sum only command-data blocks, excluding the query and reply. They are
software observations around native routines and reciprocal return, not calibrated
wire-edge durations. Control reservation, construction, park/electrical entry,
aggregate admission and outside-block intervals remain separately in evidence.

| Command wire bytes | Baseline (ms) | Fixed (ms) | Change (%) |
|---:|---:|---:|---:|
|8192|31.4028|31.4028|+0.00|
|4097|15.8333|15.8333|+0.00|
|4096|15.6944|15.6944|+0.00|
|256|1.0972|1.0972|+0.00|

Return-to-unpark only:

| Command wire bytes | Baseline (ms) | Fixed (ms) | Change (%) |
|---:|---:|---:|---:|
|8192|0.8056|0.7639|-5.17|
|4097|0.6250|0.7361|+17.78|
|4096|0.4167|0.4028|-3.33|
|256|0.2500|0.2361|-5.56|

## Validation and integration correction

The real-source host regression exercises raw read and availability-driven parser
callers, pending physical ownership, completed-but-unretired staging, exact order,
full queues, bulk/prefix/cache/peek, reset, fault, timeout and callback recursion.
Mutation checks reject both empty-only progress and ungated availability. Existing
split-read/no-idle-sleep, UART/reset, mode lifecycle, queue/backpressure, admission,
coordinator/handover and build-selection checks pass.

The first r18 source passes a bounded 256-byte acquisition, but source review finds
that ungated availability can advertise a byte later withheld by read(). Stock
nonblocking dispatch converts that −1 to VDU 255. R19 corrects this before larger
cases; the final four-case comparison uses only r19. The early acquisition and
its exact identities remain separately retained. See the
[task gotcha](ADMISSION-PROGRESS-R01.md#integration-gotcha-before-larger-cases).

## Acquisitions and required capture-absence control

Six R19 acquisitions retain 36 zero-flag rows. The original 4097-byte acquisition's
repeat 2 dump has 8114 bytes; the separately labeled r02 repeat 2 dump has 8139 bytes.
Both remain failed whole acquisitions, with their original rows/logs/phase data.
After each, one Agon reset and two actual CLI exchanges establish fresh state;
no uncertain RUN is replayed. The final labeled r03 acquisition has six complete
8192-byte dumps. Selection uses the first complete proof for each original repeat
index: 23 original rows plus only 4097 repeat 2 from r03, with its matching phases.
Elapsed time never determines selection. All 24 selected buffers are retained.

The matching control is source d74185ca, application SHA256
`d49d88e54879372db4e1f61252b83f67daf8be5d984f89b0284b285033e29927`.
Only the BUFFERED_DEBUG_INFO read/print body differs from R19, besides build
identity; the literal is absent from the linked application. The same fixture
still issues that command. A control observes the 4097-byte case for 60 seconds.
It completes six zero-flag records with correct phase ordering/conserved descriptor
byte counts, actual CLI handback,
no dump output and no panic. Its timings remain separate; it supplies no actual
buffer-byte or pixel proof. A negative control does not establish the cause of
short USB acquisition. Original 4097 failed before the control build began;
r02 overlaps the lowered-priority Pi build and r03 runs after that build is idle.
Host-load differences are retained rather than assigned a causal explanation.

## Exact restoration and remaining boundaries

The complete incoming 16 MiB P4 flash is restored byte-for-byte, SHA256
`006397a5a8b0f0e47d350e4a63b4f849c4a75635e7f5569a02f2b8a57871f84b`.
The original R25 application is `eb1334276c0c6e5766f718b2aef7984c382931b2a6ae6cb39c0a7ea3332c0645`.
The original full 131072-byte EMOS ROM is restored byte-for-byte, SHA256
`84da2c5ac3cebb1c470bab201f797a936296a6bfc33b6ebdbcf5d1dd3a1d1d79`.
The original bytes cover the largest application erase span, including its tail.
Startup/listener are unchanged; mainboard F060 and wiring are never flashed or
changed. Both mode 0 settings, Legacy, text/visible/flashing cursor controls,
neutral ready input, valid USB controller and actual CLI handback are verified.
All readers/transfers/reset holders are released; no optical pass is claimed.

PRT1 uses nominal 18.432 MHz/div256: 72000 counts/s, 13.8889 microseconds/count. Independent
oscillator calibration is absent; elapsed includes preemption/interrupts and probe
cost. Host preparation/runtime/retrieval durations are retained separately from
PRT endpoints, with durable start/end timestamps for final cases. No HTTP requests
are issued by the host during measured work. USB buffer dumps occur after timing.

This closes only the bounded admission-progress tranche. The byte-work bound is
not a wall-clock deadline; full RX queues still provide intentional backpressure.
Parser/native-lock optimization, P08-D02, warm-reset reliability, games, other
modes and production promotion remain separate. The original wide-mode limits
remain. Pi/bench only; Oryx is not accessed.
