# UART alignment précis

## U03 — legacy material reviewed

`agon-extender-legacy` is a read-only reference for this increment. Its
`docs/reverse-uart-audit-summary.md` and `docs/reverse-uart-driver.md` describe
115200-baud, fixed eight-byte POLL/COMMAND/RESPONSE exchanges, switched buffer
ownership, GPIO15/21 output enables and restoration to a forward parallel pipe.
Those are not current 1,152,000-baud stock-compatible full-duplex UART contracts.
The Author recalls an intervening logic buffer; do not infer its exact part
number from that recollection or import historical pins into today's wiring.

| Legacy artifact | Reuse | Do not import |
| --- | --- | --- |
| `tools/run_rev02a_loopback`, `pi_rev02a_loopback` | Immutable run directories, image identity checks, capture hashes and bounded collection | Reset/deploy actions, old endpoint maps and buffer-enable ownership |
| `tools/analyze_rev02a.py`, `analyze_rev02.py` | Independent sample-level UART decoding, exact frame validation, post-exchange checks | 115200 baud, fixed8-byte protocol and historical LA channel constants |
| `tools/analyze_pinwalk.py`, `analyze_header_pinwalk.py`, `pi_pinwalk_capture` | Identify channels from observed pulses, not wire colour guesses | Historical channel-to-pin assignment |
| `tests/runs/2026-08-18_200400_rev-02-ping/rev02-analysis.json` | Prior correctness/ownership evidence | Throughput comparison against current production UART |

The cited ping capture reports PASS at8MHz/6,000,000samples, no overlapping
active enables, 101.375us forward-to-reverse neutral time, 13.875us reverse-to-
forward neutral time, and1024following canary clocks without observed masked
mismatches. These are short exchange/ownership metrics, not sustained useful
bytes per second. No directly comparable sustained UART-rate result was found
in the focused legacy JSON/Markdown/result-text scan. The old probes observed
only selected canary bits; do not upgrade that to an all-byte integrity claim.

Current project's AUDIT-005 `uart-cts-findings.md` is a more relevant electrical
reference: its counted-point trace found3.407s of a4.456s payload wire span
under receiver CTS backpressure, exact observed payload bytes, and no framing
errors. It is an older graphics-loaded P4 image/workload, not this pass's pure
transport baseline. Reuse its decoder and timing attribution techniques only
after verifying current sniffer channels and image identities.

## U04 — stock API and measurement boundaries

Next: complete ordinary stock buffer/return APIs and EMOS receive semantics,
then freeze the pure-data fixture before code or physical tests. The confirmed
bulk-read divergence is already documented in QUAL-003's upload findings.


Stock `Buffered-Commands-API.md` command0 stores arbitrary counted bytes and
command2 clears them. This exercises the actual retained `bufferWrite()` and
`readIntoBuffer()` path without bitmap creation/rendering. Stock buffer dump255
prints to debug serial, not MOS; ordinary echo8A/8B is deliberately ignored by
current stock/EMOS receive integration and ExCom packet admission. It cannot
provide application byte-level readback without new MOS integration. Do not
repurpose these commands or silently change MOS's ignored-echo behavior.

A temporary paired diagnostic is therefore justified for observing pure data:
use the existing private 16-byte 8C callback envelope accepted by installed
EMOS16, with separate probe-only request opcode EE (unassigned in the selected
stock system-command switch). No graphics fences, render hooks, keyboard map
writes or direct eZ80 UART access. The probe requests stock buffer uploads and
checks exact content after the timed interval. A bounded diagnostic return
stream tests the same `send_packet`/Stream/UART path on both destinations.
Its packet efficiency and EMOS ISR costs must be disclosed, not called raw
115,200B/s application payload. It must record stream loss/sequence errors and
retain a bounded sender size instead of silently overflowing current EDP's8KiB
reply staging queue. The exact fixture wire format is frozen under U05.

Forward alignment candidate: implement bulk `ConsoleStream::readBytes` using
the same IDF bulk-read primitive as stock HardwareSerial, honoring setup/peek
bytes, session admission and stock200ms timeout. Do not change parser or bitmap
algorithms. Inherited P4 Stream currently has a1000ms timeout versus stock200ms;
this is a confirmed semantic difference to preserve explicitly in baseline and
align in the candidate. Test timeout/partial/cached-byte behavior on a mocked
UART boundary before hardware.

Return divergence: stock HardwareSerial writes to the IDF UART path; EDP queues
up to8192bytes in ConsoleStream, then the outer loop offers at most128bytes,
waits for wire completion, and returns through its unconditional1ms delay.
A synchronous parser invocation cannot drain its own queued output; a response
larger than the queue fails. The exact throughput effect is unmeasured and the
existing five-second blocked-TX recovery/keyboard packet ordering must survive
any necessary platform adaptation. Do not change EMOS or public reply grammar
merely to improve measured rates. Baseline return tests start at bounded packet
counts, report losses, and stop rather than force repeated overrun.

Official references inspected read-only: stock VDP v2.16.0 `vdp_protocol.h`,
`vdu_stream_processor.h`, `vdu_buffered.h`; `agon-docs/docs/vdp/Buffered-Commands-API.md`
and `System-Commands.md`. Current EMOS `src/emos_console.c` and
`src/vdp_protocol.asm` establish the16-byte diagnostic admission and unchanged
source/magic checks. Temporary fixtures may consume these accepted records;
new production packet types or ISR behavior are not part of the first pass.


### Additional U06 discovery: UART interrupt timeout

Stock Arduino2.0.14 HardwareSerial initializes `_rxTimeout(2)` and applies
`uart_set_rx_timeout` at begin. P4 ConsoleStream installs the IDF5.5.5 driver
and leaves its default RX timeout threshold10. Both configure the high-baud
RX-full threshold120 and flow-control threshold64. Thus an early RTS pause
can be followed by different idle-to-RX-interrupt delays. This is a confirmed
configuration difference, not measured attribution. Freeze a separate change
after the bulk-read comparison if needed to restore the stock timeout2; do
not combine it with the first bulk-read candidate and obscure causality.

## U07 candidate boundary

Added only the bulk `readBytes` overloads and stock200ms Stream timeout. UART
interrupt timeout remains10 for the isolated comparison. Host tests exercise
virtual dispatch, setup/peek ordering, partial reads, driver errors, inactive
lease behavior and once-only RX diagnostic accounting. Build with C++17,
-Wall -Wextra -Werror using tests/stubs and vdp include paths; run stream.cpp
with and without AGON_EXTENDER_FRAME_TIMING. Both pass. Hardware timing and
real IDF timeout behavior still require the candidate run.

The repository version validator currently stops at the preexisting
light2-harness-r02 connectivity integrity mismatch. No hardware definition
changed in this work; record the failure without repairing unrelated wiring
documents. Raw CSV evidence uses CRLF; use core.whitespace=cr-at-eol for diff
checks without altering evidence bytes.

U07 isolated P4 build passed at source bf1232c, uart-excom-console-r17-b2026-09-13-20-38-44Z.
Factory SHA256 d8889fa3e93e237ca3fd290ef5478cee76119b2e5694fad56336104501e10a20.
Comparison against archived measured inputs confirms only the two declared
transport changes plus the unchanged paired probe. No other source overlay.

## U09 implementation decision frozen before editing TX

The actual stock HardwareSerial writer calls IDF uart_write_bytes with TX
software buffering disabled. IDF repeatedly fills available FIFO space while
previous bytes transmit; it does not wait for wire-empty after each128bytes.
The P4 owner adds exactly that empty-FIFO barrier. Its bounded sender is still
necessary for existing five-second CTS-stall cancellation and one-owner packet
ordering: the stock driver call itself has an unbounded semaphore wait.

The smallest next adaptation is to let the existing uart_tx_chars refill FIFO
space while transmission is active. Keep the owner, staging queue, loop delay,
physical CTS, packet order, completion observation and cancellation path. Reset
the blocked-progress timer only when bytes enter the FIFO. No new task, ISR,
protocol, renderer change or arbitrary delay tuning. Before physical use, compile
the maintained console owner unchanged against deterministic UART/USB boundaries
and check exact packet ordering, partial writes, short stalls, long-stall
cancellation/readmission, and final hardware-idle admission. Pure hardware
measurements follow the separately measured RX changes.

The existing8192byte reply staging limit remains a known adapter limitation;
these bounded diagnostics do not qualify arbitrary larger synchronous replies.
Do not silently expand this increment into redesigning the reply subsystem.

U09 pre-change owner tests pass under address/undefined sanitizers. The complete
maintained console_hardware.inc is copied byte-for-byte to a temporary harness;
only driver and USB acquisition boundaries plus the VDU reply producer are fake.
A4626byte sequence crosses staging-ring wrap, exercises FIFO partial writes,
short CTS pause, and a stopped receiver beyond5seconds. Exact output and idle
admission pass; the long stall clears all stale output and accepts a fresh
lease. Run tests/owner.py0 for the old barrier and1 for the planned refill path.
Reported host milliseconds are simulated scheduling checks, not hardware data.
