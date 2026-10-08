# PORT-008 — Reuse the proved forward parallel transport

## Executive summary

The forward byte clock is already solved and physically demonstrated. PRX-06
used an eZ80 assembly loop and P4 PARLIO DMA, transferring 1,024-byte records at
836.8–838.9 KiB/s in its fastest profile. It checked READY once per block, not
per byte. The clock came directly from eZ80 PD5; 74-series logic did not generate
it. Reuse that mechanism rather than replace payload with software SPI.

The successful prototype used eight data wires plus CLOCK, READY and VALID.
The P4-PC migration specification also includes all eleven signals, and the
Author confirms having followed that specification. The earlier inference from
DevKit r03 that the clock was disconnected was wrong for the PC. Reuse these
reported connections; no pseudo-SPI handshake or reconnection is required just
to provide those signals. Physical parallel qualification and the reverse
protocol remain unperformed; the bench is occupied.

## Retained proof

Sources: [adopted PRX-06 result](../../../hardware/designs/light2-harness-r01/legacy-evidence/prx-06-results.md),
[original result](../../../../agon-extender-legacy/docs/prx-06-results.md),
[retained measurement bundle](../../../../agon-extender-legacy/tests/runs/2026-08-16_005754_prx-06-speed/),
[sender lineage](../../../../agon-extender-legacy/agon/prx06_sender/src/prx06_wire.asm)
and [vendor-derived receiver](../../../../agon-extender-legacy/src/modules/transport/p4_forward_rx.c).
Legacy checkout HEAD at review: `df54cf6a7a23cd40e98076856f68cff0559d1c77`.
Current source paths are evolved lineage, not asserted byte-identical to the
original run's source hashes. The retained fixture-source manifest identifies
those original hashes. Seven retained evidence files were checked against
`SHA256SUMS.local`; raw `logic.sr` was not rehashed or decoded again.

| Evidence | Retained observation | Scope |
|---|---|---|
| Fastest three endpoint samples | 836.8 / 837.5 / 838.9 KiB/s; 1,195 / 1,194 / 1,192 microseconds per 1 KiB record | Sorted slowest first; includes receiver completion/notification overhead, not SD/network/file commit |
| Analyzer follow-up | 876,888.5 falling clock edges/s; exactly 1,024 qualified edges | 856.3 KiB/s wire payload; different timing interval from endpoint measurement |
| Receiver integrity | All22 transactions passed whole-record pattern/sequence/CRC | Full eight-bit endpoint validation |
| Analyzer integrity | D0–D2 had zero mismatches; D3 probe stayed high | Does not establish independent analyzer observation of all eight bits |
| Current UART comparison | 112.5 KiB/s theoretical ceiling at1,152,000 baud,8N1 | Fastest-profile endpoint results are about7.44× that ceiling; not a measured paired file-transfer speedup |

The old prose's approximately0.84MiB/s blends the wire/endpoint distinction.
Use the retained numbers above: endpoint about0.818MiB/s, wire about0.836MiB/s.
Historical records remain unedited. The speed fixture masks interrupts throughout
its wait/send/completion routine; its result does not establish production
keyboard/timer responsiveness. Do not carry that interrupt policy into EMOS
without a separately bounded design and measurement.

## What each original signal did

| Signal | Original endpoint | Actual role | Reuse / change |
|---|---|---|---|
| D0–D7 | PC0–PC7 to eight P4 GPIOs | One byte per sample edge | Keep full width; use current board mapping |
| CLOCK | PD5 / Agon header14 → P4 GPIO14 on DevKit | eZ80 changes data, raises and lowers clock; P4 samples falling edge | Preserve the proved mechanism; current continuity requires confirmation |
| READY_N | PD4 / header13 ← P4 GPIO20 on DevKit | P4 admits a fully armed block and later reports completion | Candidate for negotiated state before/after payload |
| VALID_N | PD7 / header16 → P4 GPIO13 on DevKit | Qualifies payload clock edges | Candidate for software-armed, exact-length receive |

These are original DevKit endpoints. The current
[P4-PC wiring specification](../../../hardware/designs/light2-p4pc-harness-draft/README.md)
and [board profile](../../../vdp/build/boards/p4-pc.json) assign READY toGPIO15,
CLOCK toGPIO14 and VALID toGPIO16, on EXT1 contacts9,8,10 respectively. The
Author confirms wiring that migration specification. The r03 disconnected-line
record refers to the former DevKit and is not current PC wiring evidence.

The useful inner loop is simply RAM byte → PC_DR → PD5 high → PD5 low → next
byte. The driver/configuration lifecycle arms P4 DMA before admitting the block.
Do not substitute a C callback per edge for that measured hot loop and assume
its performance is preserved. Ownership/timeout logic can remain outside it.

## Replacing block handshake wires is plausible

Pinned IDF5.5.5 (`b774170ff46c393eeb5e495ea37936038d3f4f4f`) provides
`parlio_new_rx_soft_delimiter()` and `parlio_rx_soft_delimiter_start_stop()`.
In `components/esp_driver_parlio/src/parlio_rx.c`, soft delimiters select software
start and a strictly positive byte-count EOF, without the external VALID signal.
The [RX API](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/parlio/parlio_rx.html)
describes this facility. This is source-supported feasibility, not a tested
replacement for the current receiver.

EMOS/P4 could agree direction and length during the control phase, release UART
drivers, arm the receiver after pin handover, and transfer exactly that many
clocked bytes. READY would then be a negotiated buffer/ownership state. Keeping
the clock stopped during handshake/mux activity is essential if VALID is removed.
The exact acknowledgement sequence must prove actual DMA readiness, not merely
queued work; this review does not claim that sequence is already complete.

Removing READY/VALID wires is therefore optional research, not necessary for
the selected PC assembly. Prefer the known eleven-signal arrangement for the
first review, with direction/lifecycle decisions owned by EMOS and P4. Software
state still coordinates them; the dedicated signals can communicate it without
a pseudo-SPI preamble. No wiring change is selected.

## Reverse path: reuse the same clock direction first

P4 PARLIO TX supports an external clock and eight data outputs. The
[TX API](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/parlio/parlio_tx.html)
and pinned `parlio_tx.h`/`src/parlio_tx.c` establish the facility; no physical
P4-to-eZ80 parallel result was found in the reviewed records.

A useful candidate keeps EMOS generating PD5 clock pulses in both directions:
for writes, P4 RX DMA samples; for reads, P4 TX DMA advances and EMOS samples
PC_DR into RAM. The slower eZ80 then determines the pace instead of trying to
catch a free-running P4 stream. First/last-byte alignment, external-clock startup,
data-valid delay, stopped-clock behavior, underrun and output release require
small tests. The supported API is not proof of one-byte-per-pulse alignment.

The prior [reverse-UART result](../../../hardware/designs/light2-harness-r01/legacy-evidence/rev-02-results.md)
proved buffered UART handover at115200baud followed by another correct parallel
block; the [reverse driver](../../../../agon-extender-legacy/docs/reverse-uart-driver.md)
provides useful release/neutral/restore structure. Its buffers, lower rate and
UART return are not proof of direct-wire reverse parallel.

## Implementation boundary

Reuse PARLIO, the eight-bit sender mechanism, block admission and existing
integrity fixtures. Reconcile them with current EMOS ownership instead of
resurrecting a frozen standalone application that controls GPIO directly.
The current `emos_parallel.c` binding takes all of Port C and the current P4
parallel target retains buffered-circuit assumptions; both need deliberate
adapters. The superseded `forward_parallel_stream.cpp` is evidence only.

Before a reverse transfer, both UART TX/RTS drivers must be released and eZ80
data pins must be inputs before P4 outputs are enabled. Completion is not
tristate: P4 TX idle data can still be driven after DMA finishes. Recovery must
disable/release the actual GPIO output path before UART is restored. An eZ80
reset during a P4-driven block is especially important: startup must not enable
UART against a still-driven bus. Existing buffers once helped that problem;
RAM flags alone do not solve it. Preserve this as an explicit qualification gate.

Next decision: review the direction/handshake state machine using the already
specified eleven signals, including the reverse-role policy for READY/VALID. Bench remains untouched; no code,
build, flash or physical test is part of this review.
