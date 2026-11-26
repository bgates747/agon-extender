# I²C alternative for Olimex AgonLight2 and Extender P4

I²C can connect the eZ80 and P4 through dedicated header pins and avoid
sharing the microSD SPI signals or turning UART1 pins around. It is a
credible low-rate control link. A bulk-transfer replacement is a poor
fit at the existing MOS settings. The wire alone takes at least 44.3 s
for a 1.10 MB file at the fastest existing setting, even without
application framing or firmware stalls. The eZ80 also has an I²C
silicon lockup erratum. Qualification would need to prove bounded
recovery as well as throughput.

## Pin assignment and electrical design

Use the native eZ80 I²C controller and configure the ESP32-P4 **HP I²C1**
as a target. This preserves the P4's HP I²C0 use on GPIO7/GPIO8 for its
onboard display-control bus. The separately routed UEXT GPIO22/GPIO23
are outside the production EXT1 UART1/PARLIO assignments.
The official PCB files establish these candidate connections, and the
installed assembly still needs continuity and rail checks before a
physical test. [P4-PC reference and hardware revision](../../hardware/esp32-p4-pc/README.md) ·
[P4 HDMI I²C use at production source](https://github.com/bgates747/agon-extender/blob/be1d94329e55cc5e4243adbcdad73e3c530f9053/vdp/video/extender/display/hdmi_output.cpp) ·
[Current harness assignment](../../../hardware/designs/light2-p4pc-harness-draft/README.md)

| Signal | AgonLight2 Rev B | ESP32-P4-PC Rev C | Ownership |
| --- | --- | --- | --- |
| SCL | UEXT1 pin 5, GPIO1 pin 30, eZ80 U1 pin 99 | UEXT1 pin 5, GPIO23 | eZ80 clocks. P4 may hold low for bounded target stretch. Both use open drain. |
| SDA | UEXT1 pin 6, GPIO1 pin 29, eZ80 U1 pin 98 | UEXT1 pin 6, GPIO22 | The transmitter or acknowledging receiver pulls low during its assigned phase. |
| Ground | UEXT1 pin 2 | UEXT1 pin 2 | Maintain common ground. Keep UEXT1 pin 1 supply rails separate. |

AgonLight2 Rev B ties UEXT SDA/SCL to GPIO1 and ACCESS_BUS1 as well. P4
Rev C ties its GPIO22/GPIO23 to UEXT and the local pull-ups, with a
separate GPIO7/GPIO8 I²C net. GPIO22/GPIO23 belong to VDD_IO_0, outside
the LDO4-dependent bank used by current PARLIO GPIO46. Connect only the
two I²C signals and ground between board sides of the link. A fully wired
UEXT cable would include power, UART and SPI. Keep any existing I²C
consumer on the Agon side accounted for and assign the P4 a fixed
unreserved 7-bit address after checking attached-device identities.
[AgonLight2 Rev B schematic](https://github.com/OLIMEX/AgonLight2/blob/b7f2a21c282813efd8cdf26573eb5126876432a8/HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.pdf) ·
[AgonLight2 Rev B PCB](https://github.com/OLIMEX/AgonLight2/blob/b7f2a21c282813efd8cdf26573eb5126876432a8/HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.kicad_pcb) ·
[P4-PC Rev C schematic](https://github.com/OLIMEX/ESP32-P4-PC/blob/04032d68e5c727870f9d40beb9e37b7ab3a66916/HARDWARE/ESP32-P4-PC-Rev.C/ESP32-P4-PC_Rev_C.pdf) ·
[P4 I/O bank table](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/schematic-checklist-esp32p4.html)

Both boards specify 2.2 kΩ pull-ups to their local 3.3 V rail on each
line, Agon R39/R40 and P4 R92/R93. A direct connection gives about 1.1 kΩ
effective only with both rails at 3.3 V. At a 0.4 V low level that draws
about 2.64 mA per asserted line before additional peripherals. Extra
pull-ups could exceed the 3 mA standard design point. Direct wiring also
lets a powered rail feed an unpowered rail through the far-side pull-up
or the pin clamps. A high-impedance GPIO mode alone leaves that resistor
path intact. For independent power and fault isolation, use a normally
isolated link with a two-sided open-drain buffer or switch specified for
partial power-down. Each side retains its local pull-ups. A part such as
TI TCA9517A can be evaluated against its supply-order, side voltage
offset, timing and enable constraints. The gate should enable only
with nominal rails and an idle bus. Define how the controller-side
segment is isolated when the P4 pins remain low. Validate leakage, actual
low level, and edge timing in both power orders. Do not add pull-ups
before measuring the assembled bus. At Fast-mode's 300 ns rise-time limit,
`tr = 0.8473 × Rp × Cbus` gives a first-order limit of about 161 pF per
isolated 2.2 kΩ segment. This is an RC estimate, with other electrical
limits and buffer delay still applicable.
[NXP UM10204, Rev. 7, Sections 6–7](https://www.nxp.com/docs/en/user-guide/UM10204.pdf) ·
[TI TCA9517A data sheet](https://www.ti.com/lit/ds/symlink/tca9517a.pdf)

## Device roles and implementation

**EMOS remains the only controller of this link.** The eZ80F92 has dedicated
SDA/SCL and a byte-oriented I²C block. Zilog exposes data and status at
`I2C_DR` and `I2C_SR`, with `I2C_CTL.IFLG` signalling each protocol stage.
The hardware supports controller and target modes, repeated START, and
Standard- and Fast-mode operation. Production EMOS r06 already implements
controller read/write on the standard MOS API. The driver caps a transaction
at 32 data bytes, waits synchronously while the interrupt progresses the
transfer, uses Timer0 for nominal 2 s waits, and uses global message state.
Its repeated-START status table entry `10h` is invalid and target states
are unimplemented. Adapting the controller role preserves the public API.
Making the P4 controller instead would require a new eZ80 target-mode
driver, arbitrating the existing controller API on the same physical bus,
and addressing the same clock-lock erratum. There is no speed advantage
with the roles reversed. Candidate traffic should run while the foreground
SD listener owns the transport, or at an explicitly tested EMOS safe
point. Serialize public MOS I²C calls and candidate use, reserve the timer
during transactions, preserve unrelated power-gate bits, and restore the
existing rate/configuration on release. Keep raw-register overrides out of
the supported application path.
[Zilog PS015317-0120, I²C chapter](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf) ·
[Public MOS API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md) ·
[Production EMOS I²C source](https://github.com/bgates747/agon-emos/blob/abefa2f943eb3089c08d85bf39e48ebb4938f4bd/src/i2c.c) ·
[Production IRQ dispatch](https://github.com/bgates747/agon-emos/blob/abefa2f943eb3089c08d85bf39e48ebb4938f4bd/src/interrupts.asm)

**The P4 manages bounded memory frames and credits.** In ESP-IDF 5.5.5
at `b774170ff46c393eeb5e495ea37936038d3f4f4f`, HP I²C supports target
mode and has 32-byte FIFOs. LP I²C is unsupported for the target driver.
Build with `CONFIG_I2C_ENABLE_SLAVE_DRIVER_VERSION_2=y` and internal
pull-ups disabled. In target driver v2 the ISR moves bytes through
hardware and software buffers, notifies a worker through
`on_receive` and `on_request`, and explicitly enables clock stretch.
Address-match/read servicing, TX-empty and RX-full handling differ.
The address-match path calls the request callback and defers clearing
stretch until the task-side write path. Treat this as a short bounded
service window with response bytes already available in P4 RAM. Keep
on-wire readiness separate from completing a P4 file or network operation.
The driver's TX submission exposes a write count, so require the exact
count before advertising a complete response. The RX ISR pulls FIFO data
before attempting to enqueue it in the software ring. A full ring is
therefore a real loss case even if wire-level ACKs were seen. Require
capacity, length and sequence checks at the protocol boundary. Start with
frames no larger than 30 total bytes, using bounded software rings and
an explicit test around FIFO boundaries. The v5.5.5 driver uses FIFO mode,
compatible with avoiding Espressif I2C-308's non-FIFO repeated-read fault
on several silicon revisions, including v1.3. Verify repeated reads and
partial transactions on the actual fitted silicon.
[Espressif v5.5 programming guide](https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32p4/api-reference/peripherals/i2c.html) ·
[P4 capabilities](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/soc/esp32p4/include/soc/soc_caps.h) ·
[ESP-IDF 5.5.5 target v2 driver](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_driver_i2c/i2c_slave_v2.c) ·
[P4 erratum I2C-308](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32p4/03-errata-description/shared/i2c-fail-in-multiple-reads-operation.html)

For a two-way trial, retain UART1 for admission, capability, job/epoch,
direction, offsets, credits and completion. This preserves a monitorable
control path and avoids changing the shared port's pin directions to use
I²C. On a PUT the P4 prepares a frame in local RAM before granting credit.
EMOS initiates a read of a known length, validates its job and offset
through the associated control state, and writes to its existing SD
transaction. On a GET the P4 offers receive capacity and EMOS reads the
SD card between transactions, then initiates bounded writes to the P4
target. The P4 checks the expected length/offset and accepts the frame
within its admitted session before advancing progress. Use one outstanding
frame first, distinct START/STOP operations, and fixed-size metadata or
window credits carried on UART1. Advance reported file progress only at
the existing confirmed service boundary. I²C ACK is a byte-level response,
and cannot prove that the P4 queued the frame or that FatFS completed an
operation. Avoid filesystem, network and render work in I²C callbacks.
Exercise packet tails and partial read/NACK, cancellation, duplicate
offset, lost epoch and ring-full failure. The eZ80 ISR/driver, small shared
scratch state and timeout path need a linked ROM/RAM delta and front-end
latency check before any production adoption. P4 v2 allocates distinct RX
ring, RX scratch, TX ring and synchronization state, so also measure
internal-memory cost and worker scheduling margin on the matched build.

## Recovery constraints

Zilog erratum 4 says an isolated SCL pulse at idle with SDA high may lock
the I²C block even with `I2C_CTL.ENAB` clear. A software `I2C_SRR` reset
alone does not clear that fault. The production driver already gates the
block with `CLK_PPD1` before enabling it. Qualify that sequence, keeping
the block clock-gated while inactive when compatible with existing MOS
use. Zilog lists an externally generated STOP after SCL is released,
or whole-system reset, as recovery options. A generic nine-clock bus
clear addresses SDA held low, and is not an unconditional recovery for
this erratum. For an admitted, isolated trial, snapshot SCL/SDA and both
controller/target states before recovery. If SCL stays low, isolate the
Extender side and require a bounded recovery or supervised reset of the
holding device. If SDA stays low while SCL releases, qualify recovery
clocks and a STOP specifically with the F92 block gated as needed and
with ownership of any other devices on the bus. For the F92 internal
lock with lines high, qualify the external STOP or fall back to a
supervised Agon reset. The existing EMOS timeout helper resets the block
and its byte count but does not explicitly clear `i2c_role`. A candidate
needs to release its software state, buffers and timers as well as reset
the peripheral. Leave the P4 I²C link disabled or isolated on failed
admission. Preserve normal Legacy startup, UART operation, and microSD
with the P4 absent or off. Record bounds for stuck-line recovery and
reject persistent stretches without rebooting repeatedly or silently
changing carrier.
[Zilog UP004909-0910, erratum 4](https://www.zilog.com/docs/ez80acclaim/up0049.pdf) ·
[NXP UM10204, bus clear](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)

## Transfer ceiling, both directions

The board oscillator is 18.432 MHz. The Zilog divider yields
`fSCL = 18.432 MHz / (10 × (M + 1) × 2^N)`. The existing MOS rate IDs
select 57.6, 115.2 and 230.4 kHz with `M=1` and `N=4,3,2`. For the
last two the corresponding sample clocks are 2.304 and 4.608 MHz.
The fastest nominal divider-derived candidate below 400 kHz is **368.64
kHz**, `M=4,N=0` or `CCR=0x20`. Its 18.432 MHz sample clock exceeds
Zilog's 4 MHz Fast-mode sampling recommendation. The divider alone does
not establish Fast-mode operation. A physical trace must meet the SCL
low/high minima of 1.3 µs/0.6 µs, 300 ns maximum rise time, and the
data and ACK setup requirements with the actual buffer and harness.
400 kHz is the devices' Fast-mode ceiling. The production MOS rate
reaches 230.4 kHz through its public API.
Each data byte uses nine clocks including ACK/NACK. A read has the same
payload clock count as a write at a given SCL clock. Sustained software
throughput can differ by direction.
[AgonLight2 Rev B oscillator](https://github.com/OLIMEX/AgonLight2/blob/b7f2a21c282813efd8cdf26573eb5126876432a8/HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.pdf) ·
[Zilog divider and sampling, pp. 160–161](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf) ·
[NXP UM10204, Fast-mode timing](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)

| Controller setting | Continuous 9-clock data ceiling (kB/s) | 32 data bytes + 1 address ceiling (kB/s) | 1.10 MB time floor at 32 data bytes (s) | eZ80 cycles per 9 clocks |
| --- | ---: | ---: | ---: | ---: |
| MOS 57.6 kHz | 6.40 | 6.21 | 177.3 | 2,880 |
| MOS 115.2 kHz | 12.80 | 12.41 | 88.6 | 1,440 |
| MOS 230.4 kHz | 25.60 | 24.82 | 44.3 | 720 |
| Candidate 368.64 kHz | 40.96 | 39.72 | 27.7 | 450 |
| Nominal 400 kHz ceiling | 44.44 | 43.10 | 25.5 | 415 |

Rates are decimal kB/s. These are calculations with one address byte per
transaction. START/STOP/setup, bus-free time, clock stretching, frame
metadata, firmware scheduling, Ethernet and SD are excluded. As an
illustrative cost case, 24 payload bytes plus six frame bytes and one
address byte allow at most **19.82 kB/s** at 230.4 kHz, or **31.71 kB/s**
at 368.64 kHz. A 1.10 MB file would take at least 55.5 s or 34.7 s,
respectively, each way, before other costs. Production PARLIO's measured
1.10 MB writer and reader take 13.3 s and 31.6 s end to end, respectively.
Thus at the existing MOS rate even the optimistic I²C floor exceeds both
measured times. The candidate divider could approach the measured PARLIO
GET time only without meaningful overhead. At 368.64 kHz, the controller
must keep up with about 41,000 byte events/s to reach the raw rate.
The existing byte ISR and synchronously waiting caller consume that
budget even while the P4 is faster. Measure operation latency and CPU
busy time under the real SD and input workloads.
[Production PARLIO reference](../PORT-008/PRODUCTION-SD-PARALLEL-R03-RESULT.md)

## Discriminating qualification sequence

- Prove exact pins, local pull-ups, rail isolation, idle high, start/stop
  edges and acceptable rise time. Exercise either power order, unplugged
  P4, and powered-on or restarting P4 with Agon booting independently.
- Demonstrate clean write and read using one small known RAM-only frame,
  separate START/STOP, at 57.6 kHz and then 230.4 kHz. Exercise repeated
  transactions, successively crossing the FIFO watermark, 30, 31 and 32
  bytes, final-byte NACK, RX ring full, partial TX queue, and delayed
  request processing. A later divider experiment needs measured SCL
  high/low periods and stretch bounds at both endpoints.
- Inject a restart in each direction and test idle glitch and stuck-line
  recovery through controlled isolation. Capture first-fault clock/data,
  stretch cause, I²C status, UART control sequence, queue/epoch and SD
  progress before restarting. Confirm rejected/cancelled frames do not
  activate a staged file. Retain Legacy CLI and keyboard behavior.
- If the link is still useful, compare identical mixed-size jobs including
  a 1.10 MB PUT and GET, report aggregate time and worst-case recovery on
  the same files, and test an installed Agon-side I²C peripheral at its
  own supported rate if coexistence is required.

Recommend retaining I²C as a possible small-control/messages link. To
justify replacing PARLIO bulk with I²C, a test would have to show enough
real-work reliability and recovery benefit to outweigh the measured and
calculated throughput gap, with the F92 erratum accounted for. This is an
offline, source-based assessment. No hardware, firmware image or wiring
was changed.
