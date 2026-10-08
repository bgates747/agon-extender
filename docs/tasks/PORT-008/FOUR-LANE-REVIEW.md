# PORT-008 — Four-lane bidirectional transport review

## Superseded recommendation — Author clarification

This review answered the wrong payload question. The Author intends eight-bit
payload on all Port C lanes; the four spare lanes are for handshaking while
UART is active. The two-bit SPI payload recommendation below is withdrawn, not
an accepted implementation plan. Source findings remain research evidence.
See [the corrected scope](EIGHT-BIT-HANDSHAKE.md) and PORT-008 P08-F01.

## Original executive summary

The four spare Port C lanes can plausibly carry a two-bit, bidirectional,
clocked link while TX/RX/RTS/CTS remain available. Prefer investigating the
P4's existing SPI Slave HD peripheral and DMA driver over inventing per-symbol
software handshaking. EMOS would generate the clock through GPIO and initiate
every transaction; the P4 would receive or return data under that clock.
This is a source-backed recommendation, not compiled or hardware-tested firmware.
No bench access, deployment or pin driving occurred in this review (2026-10-08).
Implementation selection remains P08-F-D02 in the parent task.

## Findings and sources

| Finding | Evidence / consequence |
|---|---|
| PC0–PC3 already carry the four UART signals | Keep their mux, direction, output latch and interrupt handling intact |
| PC4–PC7 are individually configurable GPIOs, with UART modem alternate functions | They are not the eZ80 hardware SPI pins; EMOS needs a GPIO transfer loop |
| P4-PC routes PC4–PC7 to GPIO32/33/36/46 | Use the current board profile, not the old DevKit map |
| SPI Slave HD supports P4, TX/RX DMA and 64 shared register bytes | Reuse its buffer preparation and clocked transfer mechanisms |
| Dual-data commands exist in the pinned P4 HAL | Two payload bits per clock fit alongside clock and chip select |
| Old EMOS parallel entry/release writes all of Port C | Reusing that binding would disable the UART; replace the binding rather than merely changing pin constants |
| Old P4 parallel binding needs extra clock/valid/ready and buffer-enable pins | Its hardware assumptions do not match the proposed four-lane link |

Reviewed references, in documentation-first order:

1. Official [Agon GPIO documentation](../../../../../agon-docs/docs/GPIO.md),
   checkout `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.
2. Zilog [eZ80F92/F93 specification](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf),
   locally retained PS015317-0120: PC4–PC7 pin descriptions, printed pp16–17;
   GPIO modes/registers, pp39–45. Local PDF SHA256
   `9d64cfd5e75e50b009028f75ec6a2377ee1cf3721443715d32a78a0d920a71ba`.
   Reset selects GPIO input; reads of Px_DR report actual pin levels, not a
   saved output latch. Maintain an output shadow for owned bits.
3. [P4-PC profile](../../../vdp/build/boards/p4-pc.json) and
   [BOARD-001](../BOARD-001.md). The profile is a mapping, not continuity proof.
   GPIO32's board sensing connection must remain disconnected as documented.
4. [ESP-IDF SPI Slave HD guide](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/spi_slave_hd.html)
   and [wire protocol](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/protocols/esp_spi_slave_protocol.html).
   Local pinned IDF5.5.5 commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`
   corroborates these in `docs/en/api-reference/protocols/esp_spi_slave_protocol.rst`,
   `components/esp_driver_spi/include/driver/spi_slave_hd.h`,
   `components/hal/esp32p4/include/hal/spi_ll.h` and
   `components/soc/esp32p4/include/soc/soc_caps.h`. Its checkout was clean.
5. Pinned IDF's `parlio_rx.h`, `parlio_tx.h` and `src/parlio_rx.c`: bus widths
   are powers of two; a three-data-wire plan is not a direct three-bit PARLIO
   configuration. External-clock TX exists, but its startup/edge relationship
   would require qualification. SPI already defines that relationship.
6. Owned EMOS source at `cf10f0b1848346bc5d04056e4663bbbc166b2480`:
   [SPI SD implementation](../../../../agon-emos/src/spi.asm),
   [UART ownership](../../../../agon-emos/src/uart.c),
   [old parallel binding](../../../../agon-emos/src/emos_parallel.c) and
   [atomic helpers](../../../../agon-emos/src/emos_parallel_io.asm).
   P4 [old parallel configuration](../../../vdp/video/extender/transport/p4_parallel_target_config.hpp)
   likewise belongs to a different transport. No component source was edited.

## Candidate comparison

| Candidate within four spare lanes | Benefit | Cost / disposition |
|---|---|---|
| Two shared data + EMOS clock + EMOS select; P4 SPI Slave HD | Existing DMA, framing and direction protocol; EMOS controls pace in both directions | Recommended first candidate; eZ80 software clock and electrical turnaround still need proof |
| Two shared data + request + acknowledge; both CPUs service symbols | Explicit receiver backpressure, easy to single-step | P4 scheduling/per-symbol work can dominate; reserve as a diagnostic alternative |
| Two data + clock + delimiter; P4 PARLIO | Existing forward receiver experience and hardware buffering | Reverse external-clock launch/first-symbol control is additional work; second choice |
| Conventional one-bit SPI: MOSI/MISO/clock/select | Fixed data directions reduce turnaround complexity | Eight clocks per byte; useful initial control with the same four wires |
| Four payload lanes, timing inferred from UART or delays | Nominally wider | No per-symbol sampling signal; not selected |

SPI here does not mean moving or sharing the Agon's SD SPI wires. PC4–PC7 stay
where they are. EMOS implements the controller waveform through those GPIOs;
P4 GPIO-matrix routing connects the existing wires to a general-purpose SPI
slave peripheral. This is two-bit parallel payload, not restoration of the old
eight-bit PARLIO link. Board resource allocation must be checked for the exact
compiled composition before reserving a SPI host or DMA channel.

## Proposed lane allocation — not a wiring instruction

| Agon lane | Current P4-PC GPIO / EXT1 contact | Candidate role | Driver |
|---|---|---|---|
| PC0–PC3 | GPIO17–20 / contacts11–14 | Existing UART TX/RX/RTS/CTS | Existing ownership unchanged |
| PC4 | GPIO32 / contact15 | IO0 | EMOS command/write phases; P4 read-data phase |
| PC5 | GPIO33 / contact16 | IO1 | Depends on single/dual phase; otherwise released |
| PC6 | GPIO36 / contact17 | Select, active low | EMOS only; inactive high |
| PC7 | GPIO46 / contact18 | Clock | EMOS only; polarity chosen with supported SPI mode |

GPIO36 is a P4 strapping pin. The
[P4 datasheet](https://documentation.espressif.com/esp32-p4_datasheet_en.html)
lists it as don't-care for normal flash boot with GPIO35 high, but relevant to
download boot and some ROM-log settings. Thus it is not automatically unusable,
nor is reset safety proven. Review the actual silicon/board/reset path before
driving it. Making it inactive-high select is a proposal, not a guarantee that
a reset in an active transaction is harmless. Pull resistors and series
resistors do not supply powered-off isolation.

## Proposed handshake

1. EMOS admits a transfer only in an explicitly negotiated ExExt session,
   identifying direction, byte count and a session/job sequence over the existing
   framed UART control path. Allocate protocol IDs only after checking the current
   parser and capability contract; do not inject ad hoc bytes into VDU traffic.
2. P4 firmware reserves the complete bounded DMA buffer and prepares the channel.
   It reports READY only when the descriptor is actually loaded, not merely queued.
   UART remains able to carry keyboard and control packets.
3. EMOS selects the P4 and sends the peripheral's command/address phases. For a
   read, EMOS releases both data drivers before the prescribed turnaround/dummy
   phase. P4 hardware then drives data; EMOS clocks and samples it. For a write,
   P4 remains the receiver. Do not use guessed delays in place of protocol edges.
4. EMOS clocks only the admitted length. DMA handles P4 data movement without a
   firmware acknowledgement per symbol. EMOS may pause its clock for interrupts;
   that behavior and timeout limits need validation. No long DI section, per-bit
   allocation, or dependency on an RTOS task running at every clock edge.
5. EMOS deasserts select and sends the driver's required segment-completion
   command. WRDMA uses WR_DONE; RDDMA uses CMD8. P4 completion status and the
   byte-count/integrity check establish success. A select edge or SPI completion
   alone does not establish a successful file write or durable SD commit.
6. A timeout or reset invalidates the operation. EMOS stops the clock and releases
   select/data; P4 cancels its DMA and releases output ownership before rearming.
   A stale READY or a local timeout cannot authorize a new direction. Reconcile
   session identity and outstanding completion over UART; never replay uncertain
   filesystem writes automatically.

Each processor still owns local RAM state. The peripheral's small remotely
readable register bank is a useful optional status latch, not shared general RAM
and not a substitute for EMOS admission. Use existing UART framing first rather
than introduce a second control protocol unnecessarily. Multi-byte status must
have a coherent publication rule if the register bank is later used.

## Performance and correctness gates

UART at 1,152,000 baud, 8N1 has a raw ceiling of 115,200 payload bytes/s before
protocol costs. Two-bit payload needs four clocks per byte: it must exceed
460,800 clocks/s just to beat that ceiling before its own overhead. At the
Agon's nominal18.432MHz, that corresponds to160 CPU clocks per byte, or40 per
two-bit symbol, for the *entire* transfer loop. These are arithmetic budgets,
not throughput predictions; GPIO accesses, packing, flash waits, interrupts,
control messages, checksums and SD costs all consume time.

Use a short assembly hot loop in owned EMOS code if justified by instruction
counts. Reuse the existing SD SPI loop's coding idioms, not its PB pin binding.
Protect only register ownership updates; preserve PC0–PC3 output state with an
audited shadow/atomic update shared with software RTS, rather than writing a
sampled input value back across the port. Audit initialization, close and recovery
paths too: coexistence is a change from the old exclusive Port C lease.

Later tests should start with single-bit register read/write, then dual register
transfers, bounded DMA in both directions, alternating directions with delayed
interrupts, reset/abort recovery and finally end-to-end file transfers. Check odd
lengths and alignment: the driver requires RX buffer lengths divisible by four;
padding must not become file data. Check simultaneous UART keyboard/flow control.
Compare link-only and SD end-to-end rates separately against the same UART
workload. A slower new transport is not an optimization merely because it is
called parallel. No speed, reset-safety or full ExExt compatibility claim is yet made.
