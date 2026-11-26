# RESEARCH-009 — Transport feasibility findings

**Qualify isolated, shared-bus SPI first.** The historical SPI problem is
real, but a chip-select-gated MISO and a bus owner that restores the SD
configuration addressed it on the Agon-to-WROOM link. The P4 replacement
is feasible on paper and still needs proof in both directions. I²C is a
credible low-pin-count control link. At the stock EMOS I²C settings it is
roughly as fast on the wire as the existing staged UART is end to end, so
it is a poor first choice for bulk staging. Continue capturing the PARLIO
failure so a replacement can be tested against the failure it is meant to fix.

Frozen execution contract `d6ae3f75bc8af341a73a42ec11a101c7c80359ca`.
[Task](../RESEARCH-009.md)

## What each option buys

| Link | Best grounded bulk rate and scope | 1.10 MB example | Main reliability dependency | Disposition |
| --- | --- | --- | --- | --- |
| I²C with current EMOS API | 24.82 kB/s wire-only at 230.4 kHz with 32-byte transactions and one address byte per transaction | 44.31 s minimum per direction before SD, starts/stops, stretch or framing | Shared bus/address ownership, buffering, pull-ups, stuck-line and F92 erratum recovery | Control candidate; defer bulk |
| Ordinary staged UART | 25.44 kB/s PUT, 25.24 kB/s GET, measured earlier checksum-free optimized path | 43.24 s PUT, 43.57 s GET, measured earlier path | Existing CTS, framing, worker and SD path; no parallel pad switching | Keep as comparison and fallback |
| I²C with a faster qualified divider | 39.72 kB/s wire-only at 368.64 kHz with the same 32-byte assumption | 27.69 s minimum before the same costs | Same as above, plus new divider, timing/CPU and rise-time qualification | Consider only if the control use justifies it |
| Production PARLIO | 82.9 kB/s PUT, 34.9 kB/s GET, measured Pi-side staged transfer | 13.27 s PUT, 31.56 s GET, measured | Port C UART/parallel handover, READY/CLOCK/VALID, eZ80 and P4 completion, SD and host deadlines | Keep capture open |
| Isolated shared SPI | 384 kB/s wire at 3.072 MHz; 192 kB/s ideal shared-wire file ceiling for two passes at that clock | 5.73 s ideal shared-wire minimum. An older SD→WROOM benchmark sustained about 122 kB/s, equivalent to about 9.0 s at that rate | Exclusive eZ80 bus use, isolated MISO, distinct selects, P4 DMA readiness, bounded fault recovery | First bulk prototype |

Decimal kB/s and MB throughout this table. Time examples use 1,100,000
logical bytes. Rows are ordered by descending PUT time or lower bound.
That ordering mixes measurement and theoretical limits for orientation only.
The PUT/GET baseline is the P4 staging endpoint measured
through the Pi client including its retained host transfer stages. Rates
are not Gigabit Ethernet throughput, total test-suite duration or eZ80 CPU
capacity. The preceding UART runs used earlier builds, so the numbers are a
comparison of observed workflows. Relative to those UART elapsed times,
PARLIO was 69.3% shorter on PUT and 27.6% shorter on GET. The SPI historical
run used a WROOM and sequential Agon SD reads. It is evidence of an achievable
same-bus design, not a P4 performance claim or a write measurement. See
[PARLIO and UART evidence](PARLIO.md), [SPI evidence](SPI.md), and
[I²C evidence](I2C.md).

### Performance and costs worth measuring

- An 18.432 MHz eZ80 master uses a minimum SPI divisor of 3. Eight raw
  clocks at 3.072 MHz give a 48-cycle eZ80 byte budget before register
  polling, copying and scheduling. The stock SD driver already polls SPI
  a byte at a time. An interrupt per byte at the raw maximum is not a
  credible way to recover meaningful CPU time. Use short polled bursts,
  P4 DMA and explicit safe points. Measure eZ80 time in the SPI and FatFS
  path separately, and confirm that ordinary UART0 and keyboard handling
  still meet their latency budget. With a 1.536 MHz P4-link starting clock
  and 3.072 MHz SD, the two ideal serial passes cap the file rate at
  128 kB/s (8.59 s for 1.10 MB) before software and SD media delays.
- The bulk link carries the file and the eZ80 must also move the data
  between FatFS and the card. Shared SPI serializes those passes by
  construction. At 512 B there are 2,149 link bursts in the 1.10 MB case.
  An extra 100 µs per burst costs about 0.21 s, and 1 ms per burst costs
  about 2.15 s. Measure P4 arm, eZ80 wait/transfer, SD operation, UART
  completion and host overhead as separate intervals. Compare larger
  batches only after proving bounded eZ80 latency and memory fit.
- I²C clocks nine bits per payload byte with ACK and adds addressing.
  `rate = f_scl * 32 / (9 * 33)` is an optimistic ceiling using the
  current API's maximum payload. At 230.4 kHz the bit budget projects
  about 720 eZ80 cycles per byte event before control overhead. This
  can leave time between interrupts but does not make the synchronous
  MOS call asynchronous. Clock stretching or unarmed application buffers
  lowers effective throughput. At 400 kHz even an infinitely long
  transaction caps out at 44.44 kB/s before SD and idle time. At 230.4 kHz
  the measured production PARLIO PUT rate is about 3.34 times the I²C
  wire ceiling. The 3.072 MHz isolated SPI physics permits bulk parity
  or improvement, but a common host-path performance claim requires
  measured PUT and GET.
- The selected EMOS ROM has about 1,150 bytes of linked headroom. The
  26,127-byte listener has 3,388 bytes below its documented 32 KiB
  region after the code and tracked static occupancy. That remainder is
  the existing allowance for stack and heap. Start with one
  transport candidate and one existing reusable buffer. Measure ROM,
  RAM, stack depth and P4 DMA-capable memory against the exact baseline
  maps. Avoid duplicating full payload buffers on eZ80 and assigning a
  permanent simultaneous set of SPI, PARLIO and I²C resident drivers
  before size and boot-path review.

## Why SPI can coexist with the SD card

The previous failure had separate electrical and software causes. An ESP
on the shared MISO path interfered with SD even when it was not the intended
target. Separately, an early sender left the SPI controller and clock
configuration changed when it called FatFS. A separate chip select by
itself addresses neither issue. The historical WROOM work used gated MISO
and restored the SPI settings around each burst. It then had to fix a
separate READY-before-DMA-arm race under network work. The historical
coexistence evidence has value because it tested ordinary SD reads between
SPI bursts. It does not establish that today's P4 link has the same timing
or performance. [Historical owner evidence](SPI.md)

For the first fixture, the eZ80 remains the sole SPI clock and chip-select
controller. P4 operates as a queued SPI device. The eZ80 SD driver continues
to own PB4 and card transactions. EMOS arbitrates temporary ownership for
a P4 block at a quiescent boundary, snapshots and restores the SPI settings,
and never calls FatFS while P4 CS is active. A P4 clock-controller design
would put a second output owner on the card bus and require physical
multiplexing and a more invasive role change. The eZ80 has one hardware
SPI controller, so a second native port is unavailable. A software SPI
on separate GPIO avoids sharing but reintroduces CPU timing and lacks a
current candidate throughput case. [SPI alternatives](SPI.md)

### Candidate connectors

| Link | AgonLight2 host | Olimex ESP32-P4-PC endpoint | Condition |
| --- | --- | --- | --- |
| SPI clock | UEXT 9, PB3 | EXT1 8, GPIO14 | Disconnect the previous PD5 CLOCK wire before repurposing the P4 pin |
| SPI MOSI | UEXT 8, PB7 | EXT1 16, GPIO33 | Disconnect the previous PC5 data wire |
| SPI MISO | UEXT 7, PB6 | EXT1 15, GPIO32 | Hardware isolation between P4 and shared MISO. Verify external-power sense link absent and disconnect the previous PC4 data wire |
| SPI select, active low | GPIO header 26, PB5 | EXT1 10, GPIO16 | Idle high. Disconnect the previous PD7 VALID wire. PB4 remains the SD select |
| SPI READY, active low | GPIO header 13, PD4 | EXT1 9, GPIO15 | Retain existing conductor, assert only once the P4 DMA descriptor is armed, release on abort or retirement |
| I²C clock and data | UEXT 5 SCL, UEXT 6 SDA | UEXT 5 GPIO23 SCL, UEXT 6 GPIO22 SDA | P4 HP I²C port separate from onboard codec/HDMI GPIO7/8. Confirm board pull-up and power domains |
| Ground | GPIO 33 or UEXT 2 as appropriate | EXT1 3 or UEXT 2 as appropriate | Common reference. Each board keeps its own supply |

These are schematic and board-profile assignments, not continuity
measurements. The SPI proposal reuses P4 pins from the PARLIO link, so
firmware selection alone cannot restore PARLIO after changing those wires.
Use a removable adapter or explicitly reversible harness. Keep PC0–PC3
UART/flow control intact. Agon UEXT 10 is PC2, already part of the UART
flow-control route. It is unsuitable for P4 SPI select in this design.
Also keep the eZ80's PB2 native SS high for SPI controller mode. Use
fail-safe, power-off isolation for inter-board paths that would otherwise
inject current into an unpowered device. On MISO the gate must remain
inactive when P4 is unpowered, reset or deselected. A series resistor can
damp an edge but does not make MISO high impedance. Verify each line, idle
pull direction and safely disconnected PARLIO drivers before first power.

For I²C, make EMOS the sole SCL controller for Extender transactions and
allocate a conflict-checked target address, after an inventory of external
UEXT devices. P4 owns its I²C target buffers. Prequeue each exact response
or receive buffer before advertising readiness on the existing independent
UART. Do not stretch the bus across an SD operation or use a P4 controller
on SDA/SCL for normal transfer. Check rise times and isolated power-off
behavior. The F92 idle-clock erratum means a generic nine-clock bus-clear
assumption is unsafe. The stuck-bus test must prove a device-specific
bounded recovery path and preserve existing MOS I²C users. [I²C constraints](I2C.md)

## Failure attribution and replacement boundary

Production PARLIO has completed mixed-size traffic in both directions.
It has also stalled after successful files. The retained 177-byte PUT and
the later Earth 541,408-byte PUT show a worker timeout or terminal
transport error before recorded payload progress. The counters on those
failures are unavailable, so the records do not identify the exact pad,
DMA, SD or UART handover event. The later Earth retry received a recovery
disposition from the SD transaction layer. Successful UART continuation
shows those files could finish through a different carrier after
reconciliation. It does not settle whether the original failure began on
the data wires or at control/ownership. [Incident comparison](PARLIO.md)

A new SPI link removes Port C pin-direction switches and the need to park
the shared UART for every PARLIO payload. It still uses the Pi client, P4
worker and spool, UART control correlation, EMOS listener, SD
transaction activation and recovery boundaries. It replaces three timed
handshake lines and a shared bidirectional data byte with explicit CS,
fixed data directions and a correlated readiness signal. It introduces
a new shared resource with the mainboard SD card. Retain strict carrier
selection, preserve the failed transaction and never silently move a
partly completed transfer to a different carrier. Ordinary no-CRC transfer
policy still applies. The host prototype checks the ownership and exact
transaction-length logic independently of driver wiring. [Candidate and host checks](candidate/README.md)

Scope the first replacement to staged SD traffic. The separate ExExt
command-stream benchmark reached 340.35 kB/s of eZ80 sender drain at 8,192 B.
Meeting that with one-bit SPI at 3.072 MHz would require nearly 89% of its raw
clock budget before adding admission or response work. Screen rendering or
game frame times cannot be inferred from either rate. An application that
streams from SD and sends to P4 adds the two passes over the shared SPI
shifter. VDU, application network messages and any background services
would each need separately scoped migration, performance and IRQ scheduling
checks. [Command-stream control](../PORT-008/TRANSFER-RATE-COMPARISON-RESULTS.md)

## Smallest useful qualification sequence

1. **Prove electrical isolation and stock SD first.** Use a reversible
   harness and a test-owned card directory. Bind the two board revisions,
   verified pin assignments, chip-select and power isolation circuit,
   accepted ROM/P4/listener versions and exact rollback. Capture PB4 SD CS,
   PB5 P4 CS, MISO at both sides of the gate, SCK, READY and reset. Run
   ordinary SD init, directory, file read/write and keyboard tests with
   the P4 disconnected, off, booting, idle and under load. Refuse any
   interaction with card initialization or evidence of two active drivers.
   Use the current bench operation and startup contract.
2. **Prove one in-memory transfer per direction.** Keep production UART
   control untouched. Start below the existing SD SCK. Exercise 1, 3, 4,
   177, 511 and 512 logical bytes plus a 513-byte two-block case. Test exact
   clocking, odd word padding, stale READY, partial transactions and delayed P4 queue service.
   Verify captured test patterns end to end and unchanged SD operation
   immediately after every transfer. The controller must release CS and
   restore SD settings even if the P4 disappears. The P4 must retire
   its descriptor before accepting a new owner. Only hosted qualification
   uses known data comparison.
3. **Pair the bulk and reliability checks.** Run back-to-back PUT and GET
   on the same card and production-equivalent software. Compare strict
   PARLIO, ordinary staged UART and candidate SPI with identical payload,
   packet boundaries where possible, HTTP client, storage destination
   policy and entry conditions. Include empty, 1, 177, 511/512/513,
   4,097, 65,537, 541,408 and 1,100,000-byte cases and the seven-file
   sequence. Alternate run order and include both warm and cold entry.
   Report first-attempt successes, failures, mixed-sequence successes,
   p50/p95 elapsed times and maximum eZ80 exclusion time per direction,
   along with results after any authorized recovery. Preserve stage, SD
   commit, hardware release and network timing boundaries.
4. **Soak and inject isolated faults before considering promotion.** Start
   with at least 100 completed mixed-size sequences across distinct boot
   sessions in each direction, with USB keyboard and P4 Ethernet work
   concurrent. Qualify separate resets of either endpoint and simultaneous
   reset, delayed arm, lost UART result, incomplete payload and SD write
   error. Preserve the original fault before reset or replay. A useful
   candidate has zero lost/incorrect data in known-data qualification, no
   SD or startup regression, bounded fault cleanup and a reproducible
   time-to-recovery advantage or reliability improvement over paired
   PARLIO. No failure in 100 independent sequences would still be
   consistent with a roughly 3% one-sided 95% upper failure bound.
   Report clustering by boot/session instead of treating repeated blocks
   as independent. Set throughput and rate targets after the paired
   pilot and before any larger trial.
5. **Restore and verify.** Operators restore the recorded production
   wiring and image trio, prove Legacy CLI, keyboard and two-way PARLIO
   with scratch data, close device handles and check in. Any I²C
   control-only experiment should first prove open-drain power behavior,
   preserved addresses, prearmed TX/RX and timeout recovery at 57.6 or
   115.2 kHz before moving up to 230.4 kHz. A faster divider and bulk
   experiment are separate decisions.

## Evidence status

The two pin designs, estimates and failure analysis are offline findings.
The C admission model passed warning-clean C11 host builds and
AddressSanitizer/UndefinedBehaviorSanitizer execution over 1,024
size/direction pairs, with short/long clock, stale state and abort controls.
There is no selected firmware, bench action, soldered harness, target build
or claim that either option is physically qualified. The [production
selector](../../../production/current.yaml) remains the operating authority.
