# GPIO ownership, reserve, and eZ80 passthrough discussion

## State

- Status: Beta boundary accepted; v1 architecture and pin budget unresolved
- Prompt: SETUP-006.4 Q001 review
- Scope: GPIO budget, user expansion, mode-dependent ownership, and possible
  replication of eZ80 expansion pins consumed by Exclusive Extended transport

This document preserves the reasoning that interrupted disposition of Q001. It
is neither an ADR nor authority to allocate a pin, add switching hardware,
change a compatibility claim, or revise the beta circuit.

## Why Q001 was paused

Q001 proposes dedicating P4 GPIO16/EXT1-17 to return-UART transmission while
leaving P4 GPIO12 permanently assigned to parallel D1 input. This removes P4
pin-direction and peripheral-mux turnaround, separates the two P4 electrical
roles, and modestly simplifies circuit topology without reducing the number of
buffer channels.

The Author withheld approval pending a complete GPIO budget. Consuming GPIO16
cannot be judged only against the immediate transport: the product must retain
room for planned or plausible facilities and for user-owned connections.

## Present eZ80 transport consumption

Exclusive Extended currently requires eleven eZ80 GPIOs and eleven matching
P4 transport endpoints:

1. `PC0` through `PC7`: eight forward parallel data bits.
2. `PD4`: `READY_N`.
3. `PD5`: `CLOCK`.
4. `PD7`: `VALID_N`.

The proposed but unselected `UART_ALLOW_N` return-pacing signal would consume
`PD6` and raise the eZ80 total to twelve. Return UART reuses eZ80 `PC1`; it does
not consume another eZ80 pin.

The P4 also needs controls that do not have matching eZ80 conductors. The
current candidate uses GPIO15 for `FWD_OE_N` and GPIO21 for `REV_ENABLE`.
Q001 would add dedicated GPIO16 return TX, and `UART_ALLOW_N` would provisionally
add GPIO17. The resulting P4 allocation is fourteen GPIOs without pacing or
fifteen with it.

## Future and user-reserve pressure

1. The planned optional MOD-WIFI-ESP8266 integration is expected to require
   two P4 UART GPIOs, presently associated with pUEXT GPIO37/GPIO38. Power and
   ground do not count as GPIOs. The exact dedicated-header contract remains
   to be frozen.
2. A conventional full-duplex SPI link requires four GPIO signals: `SCLK`,
   `MOSI`, `MISO`, and `CS`. Common ground is an additional conductor but not a
   GPIO. A practical direct onboard-VDP/EDP link may also need an interrupt or
   ready line, making five reserved GPIOs prudent; a dedicated reset would make
   six. LINK-001 owns that post-v1 aspiration and has not selected SPI.
3. The current P4 review identifies GPIO6, GPIO18, GPIO19, and GPIO46 through
   GPIO48 as uncommitted exposed candidates. The pUEXT SPI pins GPIO4, GPIO5,
   GPIO53, and GPIO54 may appear attractive for a future SPI link, but they
   cannot be counted twice until the complete Wi-Fi header/module connection
   proves those pins remain electrically and mechanically available.
4. The Author requires useful P4 GPIO access for consumer extensions. A
   preliminary recommendation is to preserve six exposed GPIOs for users, with
   four as a possible hard minimum. No reserve count is accepted yet.
5. Optional-feature pins may be documented as user-reclaimable when their
   module is absent, but this is not equivalent to maintaining a permanently
   uncommitted user reserve. Profiles, headers, firmware, and user guidance
   would need to make every conflict explicit.

## Compatibility boundary exposed by the pin count

EMOS can route MOS and VDU services, but it cannot transparently virtualize an
unaware assembly program's direct reads and writes to eZ80 GPIO registers.
While Exclusive Extended owns Port C and `PD4`/`PD5`/`PD7`, an application
which independently expects those pins cannot remain hardware-compatible.
Application activity and Extender transport activity are electrically
indistinguishable at those pins.

The resulting candidate interpretation is:

1. **Legacy:** Extender remains logically and electrically absent; ordinary
   mainboard GPIO behavior is preserved.
2. **Exclusive Compatible:** Extender uses the stock UART transport. GPIOs
   claimed only by the extended parallel transport can potentially remain
   available to user hardware.
3. **Exclusive Extended:** the parallel transport owns its eleven eZ80 pins.
   VDU/application compatibility does not imply compatibility for software
   directly owning those GPIOs.
4. **Dual:** any active extended parallel transport has the same GPIO
   ownership conflict. No transparent simultaneous reuse is presently known.

This mode-scoped GPIO carve-out has not yet been promoted into the normative
compatibility contract.

## Public Agon GPIO-use survey (2026-08-25)

### Method and limits

The survey searched GitHub repositories and general web sources for Agon
software, hardware, examples, and discussions involving the exposed eZ80 GPIO,
UEXT, UART1, SPI, I2C, joysticks, interrupts, LEDs, displays, sensors, and direct
port-register access. Candidate repositories were then inspected locally at
the following commits:

1. `AgonPlatform/agondev` at `b67ab2444a63267a42193f204889d466765d8dd2`.
2. `Kayto/AgonLight_GPIO` at `a1897a6deadca545d92a1915a5d519d2f6834cb9`.
3. `tomm/vga-ez80` at `000f67f14fa80147dd32cf68be5b7656050fd6b0`.
4. `richardturnnidge/lessons` at
   `3cb69781f37a25d3ff7da6e31cd59a7ee4dc19b5`.
5. `S0urceror/AgonElectronOS` at
   `fce95087857d6f3192d0371e1c4275fa2da52406`.
6. `nihirash/Agon-MOS-Tools` at
   `617a465eb1fa4259548db0bb267820173f37d449`.
7. `AgonPlatform/agon-flash` at
   `e670b5bd910dfe372c29aa9e896e6c24cc8530ec`.
8. `TurBoss/plato-agon` at
   `f531337cbe8613398dea7c2b488d1962ff5a2fd0`.
9. `xianpinder/AgonChuckieEgg` at
   `01830f3c4c9ebe46d5d2933cf87fa2628046e447`.
10. `OLIMEX/AgonLight-WPC` at
    `83e23488d8912b2fdb1c109ef186ad356b722925`.

This is a representative public-code survey, not an exhaustive census.
GitHub code search does not reliably expose binaries, SD-card distributions,
unindexed BASIC source, private repositories, forum attachments, or Discord
discussions. Absence from this inventory is therefore not evidence that a pin
or peripheral is unused.

### Platform contract and intended uses

The [official Agon GPIO documentation](https://agonplatform.github.io/agon-docs/GPIO/)
describes UEXT as a second physical connection to signals already present on
the main I/O bus, not as an independent set of ports. Its worked example uses
a Nunchuck on UEXT and a joystick on the I/O connector simultaneously. The
[Olimex Agon Light 2 product page](https://www.olimex.com/Products/Retro-Computers/AgonLight2/open-source-hardware)
advertises the exposed connections for digital input/output, SPI, I2C, UART,
sensors, relays, and home automation, and links a broad UEXT module ecosystem.
These uses are part of the board's advertised expansion model rather than
accidental access to undocumented pads.

The maintained [Agondev GPIO interface and examples](https://github.com/AgonPlatform/agondev/tree/master/release/examples/gpio)
make direct GPIO a first-class application pattern. `gpio_blink` drives `PC0`,
`gpio_knightrider` drives all of `PC0` through `PC7`, and
[`agon/gpio.h`](https://github.com/AgonPlatform/agondev/blob/master/release/include/agon/gpio.h)
publishes identifiers for each Port C and Port D pin. The official MOS GPIO API
also permits input, output, open-drain, open-source, alternate-function,
edge-sensitive, and dual-edge interrupt configurations. An Extender design
therefore cannot assume that these contacts carry only slow, direction-fixed
digital signals.

The [Zilog eZ80F92 product specification](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf)
defines UART1 as `PC0/TxD1`, `PC1/RxD1`, `PC2/RTS1`, and `PC3/CTS1`. The
[published Agon Light 2 header pinout](https://github.com/AgonPlatform/agon-docs/blob/main/docs/images/iopinsAL2.png)
places those functions respectively on GPIO connector pins 17 through 20, and
the [Olimex Agon Light 2 manual](https://github.com/OLIMEX/AgonLight2/blob/main/DOCUMENTATION/AgonLight2-user-manual.pdf)
routes UEXT UART pins 3 and 4 to `PC0` and `PC1`. Official MOS agrees:
`open_UART1()` places `PC0` and `PC1` in alternate-function mode and optionally
reads `PC3` as CTS.

This review exposed an unrelated but material documentation defect in the
accepted Fritzing scaffold. CA-2026-08-25-001 traced it to the first pristine-
project generator commit and corrected the current source and derived files.
The current scaffold assigns `PC0/TXD1`, `PC1/RXD1`, `PC2/RTS1`, and
`PC3/CTS1` to header pins 17 through 20 respectively; pins 13 and 14 remain
`PD4` and `PD5`. The CA preserves the defective assignments and originating
commit as historical evidence without leaving them in current pin-function
authorities.

### Observed applications and experiments

| Source | eZ80 interface used | Application-visible behavior | Extender consequence |
|---|---|---|---|
| [`Kayto/AgonLight_GPIO`](https://github.com/Kayto/AgonLight_GPIO) | All of Port C for eight LEDs and single-digit seven-segment output; Port C plus two Port D pins for a proposed multiplexed display; Port C for RGB LED and buttons | Static and patterned output, multiplexing, crude software PWM, and polled input from BBC BASIC | The beta transport occupies the principal whole-byte hobbyist output port. Saving register state cannot preserve external LED state, PWM waveform, multiplex timing, or button events while pins are repurposed. |
| [`tomm/vga-ez80`](https://github.com/tomm/vga-ez80) | `PC0`–`PC7` as RGB332 pixel data, `PD6` as VSYNC, and `PD7` as HSYNC; [`gpiovideo.asm`](https://github.com/tomm/vga-ez80/blob/main/gpiovideo.asm) also configures `PD5` for audio | Cycle-counted direct VGA scanout at about 6.14 MHz; the interrupt implementation leaves less than 6% eZ80 time to the application and explicitly manages timing jitter | This overlaps nine of the present eleven transport pins, or ten when its `PD5` audio output is active. Proposed `PD6/UART_ALLOW_N` would add another conflict. It cannot coexist with even brief transport leases: a disconnection or delayed replay destroys the electrical waveform. |
| [Agondev joystick support](https://github.com/AgonPlatform/agondev/blob/master/release/include/agon/joystick.h) and [joystick example](https://github.com/AgonPlatform/agondev/tree/master/release/examples/joysticktest) | The implementation reads the complete `PC_DR` and `PD_DR` registers; its standard two-joystick mapping uses `PC0`–`PC7` for directions and `PD4`–`PD7` for buttons | Frame-polled press, hold, and release state for two physical joysticks | The mapping consumes every currently selected transport pin and would also consume proposed `PD6/UART_ALLOW_N`. Slow polling may survive pauses only when the physical joystick remains observable; the beta circuit provides no such path. |
| [NCoT Agon joystick interface](https://ncot.uk/projects/agon-light-joystick-interface/) | Physical joystick connected to exposed GPIO and read through Agondev's joystick API; the [earlier test](https://ncot.uk/projects/agon-light-joystick-test-1/) demonstrates direct port input | Maintains previous and current state to distinguish press, hold, and release | This is a concrete application of the standard Port C/Port D mapping, not merely a library facility. Missing a transition changes application behavior even if final levels are restored. |
| [`richardturnnidge/lessons`](https://github.com/richardturnnidge/lessons) | `gpio_interrupt_rotary_01.asm` configures Port C interrupt inputs and reads/acknowledges `PC_DR`; `joystick_interrupts_mode_6a.asm` installs per-pin Port C and `PD5`/`PD7` interrupt handlers | Rotary-state decoding and asynchronous joystick edge/level handling | EMOS cannot make interrupt-driven direct GPIO transparent by pausing an application and restoring registers. An event recorder would need to preserve interrupt semantics, ordering, timing, and overflow behavior. |
| [`S0urceror/AgonElectronOS`](https://github.com/S0urceror/AgonElectronOS/blob/main/src/joystick.asm) | Direct reads of `PC_DR` and `PD_DR` using the same two-joystick allocation | Operating-system-level joystick input | The pin allocation exists outside stock MOS and can bypass any EMOS service-level ownership policy. |
| [`xianpinder/AgonChuckieEgg`](https://github.com/xianpinder/AgonChuckieEgg/blob/main/input.asm) | Direct `PC_DR` and `PD_DR` reads for joystick input; startup probes Port C before enabling joystick handling | A released retail-style game detects the adapter and reads directions and fire buttons without an EMOS GPIO API | Extender loading or transport activity can alter both gameplay input and the program's initial determination that a joystick is present. This is stronger compatibility evidence than a demonstration alone. |
| [`nihirash/Agon-MOS-Tools`](https://github.com/nihirash/Agon-MOS-Tools/tree/main/esp8266) | ESP8266 on eZ80 UART1 through MOS `mos_uopen`, `mos_ugetc`, and `mos_uputc`, configured for 115200 8N1 without flow control | Network management, ESP firmware update and testing, and the Snail Gopher client | UART1 uses `PC0/TxD1` and `PC1/RxD1`, which are also selected as Extender `D0`/`D1`. Use through a MOS API does not remove the physical conflict. EMOS could reject or serialize ownership, but cannot let both independent serial and parallel roles drive the same contacts simultaneously. |
| [`TurBoss/plato-agon`](https://github.com/TurBoss/plato-agon/blob/master/src/uart.asm) | Directly configures Port C alternate functions and UART1 registers rather than asking MOS to own the session | PLATO network-terminal communication over UART1 | This confirms that real applications may bypass MOS UART ownership entirely. EMOS can define and enforce supported calls, but cannot transparently serialize direct UART register access against Extender transport. |
| [Agondev I2C ADC1115](https://github.com/AgonPlatform/agondev/tree/master/release/examples/i2c_ADC1115) and [Nunchuck](https://github.com/AgonPlatform/agondev/tree/master/release/examples/nunchuck) examples | Exposed eZ80 I2C bus through MOS calls or direct helper code | External analog conversion and game-controller input | These do not presently overlap the selected Port C/Port D transport nets. They demonstrate that unclaimed bus pins are useful application interfaces and must remain accessible rather than being treated as spare Extender capacity. |

Additional public code-search results include joystick-related material in
[`OLIMEX/AgonLight-WPC`](https://github.com/OLIMEX/AgonLight-WPC) and UART-related
Agon projects such as
[`AgonPlatform/agon-hexload`](https://github.com/AgonPlatform/agon-hexload) and
[`nihirash/ZINC`](https://github.com/nihirash/ZINC). `AgonPlatform/agon-flash`
also contains a compile-time debug path that drives Port C, although that is a
developer instrumentation option rather than a normal user contract. These
results establish additional interest but were not counted as independent
pin-contract evidence without the same source-level behavioral review.

The bounded search found concrete external I2C examples but no comparably
specific public application using the exposed SPI pins, nor source for an Agon
relay or home-automation installation. This is a search result, not a design
permission: the official hardware explicitly advertises SPI, sensors, and
relays, and private, binary-only, forum, or unindexed projects remain invisible
to this method.

The [StarDot GPIO discussion](https://stardot.org.uk/forums/viewtopic.php?t=28429)
also records users connecting the GPIO header to breadboards and controlling it
from BASIC. It is useful corroboration of the intended hobbyist workflow, but
the source repositories above provide stronger evidence for actual electrical
and timing behavior.

### Compatibility classes inferred from the evidence

The observed uses divide into three materially different classes:

1. **Static or slowly polled signals.** LEDs, buttons, and some simple devices
   might tolerate an EMOS-controlled pause. They still require a circuit that
   preserves output levels and observes user-side inputs; software register
   restoration alone is insufficient.
2. **Event- or waveform-sensitive signals.** GPIO interrupts, rotary encoders,
   PWM, multiplexed displays, and many serial or synchronous peripherals lose
   meaning when edges are omitted, delayed, reordered, or replayed at a
   different rate. A finite event queue cannot generally reproduce the
   original electrical contract.
3. **Continuous or cycle-counted ownership.** Direct VGA and similar protocols
   require uninterrupted pins with tightly bounded timing. They are
   fundamentally mutually exclusive with Extender transport use of the same
   contacts, irrespective of mux sophistication.

These are engineering inferences from the cited implementations. They do not
select a v1 circuit. They do establish that the accepted beta carve-out affects
known software and hardware, not merely hypothetical GPIO consumers.

### Consequences for the remaining design decisions

1. Exposing spare P4 GPIO benefits new Extender-aware hardware but does not
   restore compatibility for existing software that addresses eZ80 Port C or
   Port D registers and fixed header contacts.
2. A v1 passthrough/mux could materially improve compatibility for static and
   some slowly polled uses. It cannot support uninterrupted VGA, independent
   UART traffic, or arbitrary edge-sensitive peripherals during an active
   transport lease.
3. Legacy and Exclusive Compatible can preserve direct-GPIO use only if the
   Extender carrier is electrically passive enough in those modes. Input
   capacitance, leakage, buffer state, power order, and connector topology must
   be bench-qualified before making that claim.
4. Every eZ80 expansion signal not consumed by the beta transport should remain
   physically accessible. UEXT must not be counted as independent capacity
   where it merely duplicates the same eZ80 signals.
5. The eleven transport contacts should provisionally be treated as restricted
   transport/test contacts in Exclusive Extended and Dual, not advertised as
   simultaneously usable general-purpose passthrough. Whether the beta carrier
   exposes them at a replicated header or only at labeled test points remains
   a deliberate hardware decision.
6. The beta compatibility statement must explicitly exclude direct ownership
   of transport GPIO while Exclusive Extended or Dual transport is active.
   Broader VDU/MOS compatibility does not imply electrical GPIO compatibility.

## Mode-dependent eZ80 passthrough concept

The Author proposed exposing consumed eZ80 pins on the Extender board through
mode-controlled multiplexing so they could, when available, behave for user
hardware like the corresponding contacts on the Agon expansion header.

A conceptual channel is:

```text
                         +-- protected Extender transport path --> P4
eZ80 expansion pin -- mux|
                         +-- replicated user expansion contact
```

Applied to all eleven claimed pins, a bank of bidirectional switches could
select the Extender transport or a replicated user header. This provides
temporal reuse by mode; it cannot provide simultaneous transparent use while
the parallel transport is active.

The plausible mode behavior is:

| Mode | Extended-transport branch | Replicated user branch |
|---|---|---|
| Legacy | isolated | connected by hardware default |
| Exclusive Compatible | isolated for parallel-only pins | connected, subject to the separate stock-UART pins |
| Exclusive Extended | connected | isolated |
| Dual | connected whenever extended transport is active | isolated for every transport-owned pin |

This truth table is a discussion candidate, not an accepted circuit contract.

## EMOS transaction-scoped leasing refinement

The mode-level truth table is unnecessarily coarse for normal VDU/EDU traffic.
EMOS is both the normative transport authority and the eZ80 software executing
the system call. While an application is blocked inside an EMOS dispatcher,
EMOS could lease the shared GPIOs to the Extender transport for only the
duration of one bounded transaction:

1. EMOS reads and saves the eZ80 GPIO data, direction, alternate-function, and
   interrupt configuration that it is able to preserve.
2. EMOS quiesces relevant eZ80 interrupt activity and commands the external
   switching circuit to isolate the replicated user contacts.
3. EMOS configures and operates the eZ80-side Extender transport while EDP/P4
   operates the matching P4-side transport endpoints.
4. EMOS and EDP complete or abort every forward and return ownership epoch.
5. EMOS disables the transport, restores the saved eZ80 GPIO configuration,
   reconnects the replicated user contacts, and returns to the application.

Mode would authorize whether a lease may occur; the transaction state would
determine when it actually occurs. This could preserve software-visible GPIO
configuration for unaware applications that invoke ordinary EMOS services. It
would not protect code that bypasses EMOS and accesses the transport while a
lease is active.

Software state restoration is not electrical transparency. External hardware
continues operating while the eZ80 application is blocked. During a lease it
may observe a temporary disconnection, miss an output transition, generate
input transitions that the eZ80 never sees, or depend on timing that the added
latency and jitter violate.

## User-side state and event retention

The Author proposed accumulating user-side input activity while direct
passthrough is unavailable and delivering it after the transport lease ends.
The general term is **input-event capture and buffering**. A design preserving
an ordered sequence would use an **edge-capture event FIFO** or **timestamped
event queue**. Simpler circuits preserve less information:

1. A level latch or sample-and-hold preserves only the latest logic level.
2. A sticky edge latch records that at least one rising or falling edge
   occurred, but not how many times or in what order relative to other pins.
3. A per-pin event counter preserves the number of selected edges, but not
   their cross-pin order or original timing.
4. A timestamped FIFO records pin identity, edge polarity, order, and relative
   time until its finite storage fills.

The existing P4 transport GPIOs cannot perform this capture. During a lease
they are electrically connected to and occupied by eZ80-to-P4 transport
signals, while the user-side branch is isolated. The P4 could participate only
if the circuit gives it a second observation path: dedicated P4 GPIOs, an
external GPIO/event-capture peripheral, or a CPLD/FPGA that buffers events and
later presents them to the P4 or EMOS. Dedicated P4 observation pins would
substantially worsen the GPIO budget that prompted this discussion.

Candidate implementation classes are:

1. **Passive switch plus output-hold and input latches.** Hold the last eZ80
   output levels toward external hardware and latch selected external input
   events during a lease. This is relatively small but cannot preserve a
   general ordered event stream.
2. **GPIO expander or small companion MCU.** Keep the device connected to the
   user-side contacts and use interrupt flags, counters, or firmware queues.
   Its interrupt-capture semantics, queue bounds, latency, startup behavior,
   and independent failure modes would become part of the compatibility
   contract.
3. **CPLD/FPGA input concentrator and mux.** Combine break-before-make
   switching, output holding, direction control, edge capture, counters, and a
   FIFO in deterministic logic. This is the most capable approach and the
   closest to a purpose-built GPIO virtualization device, but adds design,
   programming, supply, routing, qualification, and component-lifecycle cost.
4. **P4 capture through separate pins or a serial capture peripheral.** Let
   EDP/P4 drain captured records over SPI or I2C. This can centralize policy in
   P4 firmware but still requires independent hardware on the user side; the
   shared transport pins alone cannot observe both branches.
5. **No event virtualization.** Guarantee passthrough only when no transport
   lease is active and document time-sensitive external GPIO as incompatible
   with transaction-scoped reuse. This is the simplest and most electrically
   honest beta or v1 boundary.

Capturing events does not by itself determine how to deliver them. Physically
replaying queued edges after reconnection changes their timing, compresses or
delays the stream, and may contend with a still-active external source.
Delivering records through an EMOS API is safer but helps only aware software;
it does not reproduce direct GPIO reads or hardware interrupts expected by an
unaware application. A useful design therefore needs an explicit per-signal
contract—level preservation, sticky event, count, ordered/timestamped events,
or unsupported—rather than a blanket promise to queue arbitrary GPIO input.

Output continuity is a related but separate requirement. If external hardware
must continue seeing the eZ80's pre-lease output levels, the circuit needs an
output-hold latch on the user side. EMOS can read the eZ80 direction and output
registers before a cooperative lease, but the hardware must apply that state
without glitches and must prevent contention from a misconfigured external
driver.

## Circuit and qualification consequences

The raw channel count is manageable, but the safety and qualification surface
is substantial:

1. Use direction-neutral switching because applications may reconfigure eZ80
   GPIO direction directly.
2. Power passthrough control from an appropriate Agon domain so the replicated
   user path can default active when the P4 is absent, off, booting, or failed.
3. Guarantee hardware break-before-make behavior and a safe default without
   depending only on P4 initialization.
4. Prevent user hardware, transport drivers, or either powered board from
   back-powering or contending with another branch during every power/reset
   and transition order.
5. Bound switch on-resistance, capacitance, leakage, edge degradation, and
   timing changes before claiming that replicated contacts behave like the
   original header.
6. Define which processor and firmware authorize and actuate selection. EMOS
   must remain the normative mode authority; any P4-controlled switch must
   implement only an EMOS-authorized committed state and fail toward the
   legacy/user path where electrically feasible.
7. Define what happens when external hardware remains connected during a mode
   request, including whether EMOS refuses the transition, warns the operator,
   or relies on a documented user contract.
8. Add continuity, passive, powered-off, either-order-power, contention,
   transition, timing, and fault tests for every selected branch and mode.
9. Replicate and label the physical header without implying that switch-added
   electrical characteristics are literally identical to a bare mainboard
   contact.

This feature would increase IC count and routing, but its largest cost is the
mode, safety, and qualification matrix rather than the number of switch gates.

## Accepted beta direction

The Author accepted the following first-beta scoping rule on 2026-08-25:

1. Trade availability of the eleven eZ80 transport GPIOs for circuit
   simplicity while the Exclusive Extended transport is active.
2. Do not put passthrough multiplexing, event capture, signal replay, output
   holding, or GPIO virtualization on the first beta carrier.
3. Treat direct use of those transport-owned GPIOs during Exclusive Extended
   or Dual operation as an explicit beta compatibility carve-out. EMOS may
   save and restore software-visible GPIO configuration, but beta makes no
   electrical-transparency promise.
4. Keep v1 multiplexing under active design consideration so a later carrier
   can narrow this carve-out and make the product's backward-compatibility
   claim materially stronger. Preserve clear net roles and consider routing,
   board area, and replicated-header placement when reviewing beta layout, but
   do not add speculative footprints or components without an accepted v1
   circuit.
5. Keep the P4 user-GPIO reserve problem separate: reclaiming eZ80 expansion
   pins would not return any P4 GPIO consumed by Extender features.
6. Expose genuinely uncommitted P4 GPIOs for beta experimentation only after
   the complete pin budget is accepted.

This accepts a beta scope, not a v1 passthrough architecture. Transaction-
scoped leasing and event retention remain candidate mechanisms for later
evaluation.

## Questions requiring disposition

1. What permanently uncommitted P4 GPIO reserve must v1 expose to users: six,
   four, or another number?
2. Which pins are reserved for MOD-WIFI-ESP8266, and does its realized header
   leave the pUEXT SPI quartet independently usable?
3. How many pins must LINK-001 reserve now for a possible VDP/EDP link: four
   for SPI, five including handshake, six including reset, or none before
   architecture selection?
4. Does the completed budget permit Q001's dedicated GPIO16 return TX while
   retaining the accepted user reserve and contingency margin?
5. Is the replicated eZ80 header a hard v1 requirement or a post-v1 feature?
6. Which eZ80 contacts should be replicated: only the eleven extended-
   transport pins, all otherwise accessible expansion GPIOs, or the complete
   physical expansion-header interface?
7. What exact mode truth table and hardware-failure default govern the
   passthrough switches?
8. What exact v1 user/operator contract governs attached external circuitry
   during a transaction-scoped lease?
9. If v1 implements passthrough, must it preserve only steady input/output
   levels, sticky edge occurrence, edge counts, or an ordered timestamped
   event stream during an EMOS transport lease?
10. If v1 captures events, are they physically replayed, exposed only through
    an aware EMOS API, converted into delayed eZ80 interrupts, or handled by
    another mechanism?
11. Does v1 require transaction-scoped GPIO virtualization, or does the direct-
    GPIO compatibility carve-out remain after beta?
12. Does the beta carrier expose transport-owned eZ80 signals only as labeled
    test points, or also on a replicated connector whose restrictions are
    conspicuously documented?
13. Which known public GPIO applications become explicit qualification
    fixtures for Legacy and Exclusive Compatible electrical-passivity claims:
    static Port C output, standard joystick polling, UART1, interrupts, or a
    selected subset?
14. Resolved by CA-2026-08-25-001: the canonical scaffold and every current
    derivative now use `PC0/TxD1`, `PC1/RxD1`, `PC2/RTS1`, and `PC3/CTS1` on
    Agon Light 2 header pins 17 through 20 respectively. The CA's regenerated
    and electrical evidence passes and awaits commit review.
