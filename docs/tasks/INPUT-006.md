# INPUT-006 — F310 controller packets through the Console8 gameport

Research whether an external USB-host adapter can deliver full Logitech F310
state to an application on Console8 through gameport A, using public MOS APIs
and the eZ80's hardware UART1 RX
function on the existing Up signal. The aim is an externally plugged adapter
without a Console8 motherboard modification, while retaining proportional
sticks, separate triggers and buttons.

## State, authority and boundaries

On 2026-11-08 Smith requested: “write up a task for this, research only at this
point, and record the conversation thus far. i'll be back”. This record and the
[conversation record](INPUT-006/CONVERSATION-2026-11-08.md) capture that scope.
State: research task recorded; initial datasheet/schematic findings below;
feasibility review incomplete. No implementation or hardware qualification.

Extender owns this research and any proposed reusable adapter/transport design.
Smith subsequently emphasized the strict project guideline: **no MOS or VDP
hacks**. Research targets a standalone external adapter and application-linked
driver using supported public MOS facilities, without adding controller-specific
MOS/VDP hooks, private firmware offsets or runtime firmware patches. Official
references remain read-only. Applications such as FSIM would consume the reusable
application library; app-specific control mappings remain with their owners.
Possible removal of existing resident controller code is an accounting/reuse
question here, not authorization to change or remove installed firmware.

1. Authorized now: documentation, schematic/datasheet and existing-source
   research; report findings and bounded alternatives to Smith.
2. Not selected: code changes, firmware builds, emulator work, bench reservation,
   device access, wiring, reset, flashing, fixture staging, application execution,
   new protocol deployment, production selection or downstream game changes.
3. No automatic continuation into implementation after a favorable paper result.
   Smith selects any later prototype and its hardware/firmware scope.
4. Preserve existing UART1 users, GPIO ownership, ordinary joystick behavior,
   EMOS transport/routing rules and normal startup. Availability of a pin or
   peripheral does not establish that the installed software leaves it free.

## Continuing discussion — reuse and simpler delivery

1. **Extender prototype already has the link.** The confirmed P4-PC harness
   carries P4 GPIO18 TX to eZ80 PC1/RX, PC0/TX back to P4 GPIO17 RX, common
   ground and UART flow-control lines. PD4/PD5/PD7 are also reported connected
   for parallel handshakes, but the proposed receive-only UART does not need
   Port D. This is the existing Light2/P4-PC harness, not a claim that Console8
   gameport filters/cabling have been qualified. See the
   [reported harness mapping](../../hardware/designs/light2-p4pc-harness-draft/README.md)
   and [current hardware architecture](../architecture.md#hardware-design-and-active-evidence).
   No wiring change or prototype execution has been selected.
2. **Much of the code exists.** P4 already decodes F310 USB/XInput reports and
   represents normalized state. EMOS has hardware-UART-backed controller
   transport; application interpretation is also implemented in the newer
   application library. Reuse unchanged pieces first, while separating software
   results from the physically reviewed older combination. Existing Extender
   UART ownership/admission does not imply a free standalone serial channel.
3. **Existing bidirectionality is protocol policy.** Mainboard requests poll
   P4, acknowledge accepted button-transition sequences, correlate replies to
   a caller/query and close the session. P4 does not need these messages to
   read the USB controller. The existing CI/CIS2 exchange is therefore not an
   unchanged drop-in for gameport-A-only reception. Its dependence on Extender
   keyboard admission and Legacy/ExCom must not become a standalone requirement
   without justification.
4. **Avoid carrying over unnecessary machinery.** Smith called the existing
   polling/acknowledgement/session approach “building an ERP again”. The leading
   simple candidate is periodic full-state reports from the adapter, possibly
   carrying cumulative button-press counters to preserve taps between reads,
   without a mainboard-to-adapter return channel. This is a research proposal,
   not an agreed wire format. Examine counter wrap, source restart, missed
   reports, disconnect neutralization and resynchronization without recreating
   the session/ACK service by default. Counters would not preserve complete
   event ordering or durations; report those limits.
5. **Public APIs and resident footprint.** Smith identified an opportunity to
   free EMOS bytes under the no-hacks constraint. Investigate whether supported
   UART open/close and interrupt-vector facilities suffice for an application
   driver; byte reception uses hardware UART, not GPIO bit-banging. Public
   `mos_ugetc` is documented as blocking while UART1 is open; do not assume it
   supplies a nonblocking ring buffer or that a public vector API alone resolves
   ISR access/lifecycle. Identify any missing supported facility plainly.
6. **Prior measured extraction is a baseline, not a saving claimed here.**
   [INPUT-005 offline results](INPUT-005/RESULTS.md) measured 991 ROM bytes and
   29 static RAM bytes recovered by moving interpretation into an application
   include. Its remaining controller object was 1,208 ROM/102 RAM bytes, and
   complete controller composition cost 1,306 ROM bytes above its comparable
   ordinary build. Those numbers apply to its exact historical build/source,
   not a measured current-image saving or proof that all bytes are removable.
   Inventory actual consumers, shared transport/parser hooks and compatibility
   before recommending further removal. No firmware editing/build/removal now.

## Initial research précis

These findings concern the published Console8 Rev 2.0 schematic and eZ80F92
pin functions. They do not identify Smith's physical board revision or prove
operation through its cable/filter network.

| Finding | Evidence and implication |
|---|---|
| Gameports connect to eZ80 GPIO | Heber manual printed pp. 13 and 16, schematic sheets 2/5 and 5/5. Six signals per connector; Port C holds directions and Port D holds buttons. |
| Gameport circuits do not contain level shifters | Sheet 2/5 shows 3.3 V pull-ups, series resistors, ferrite filtering, shunt capacitors and ESD protection. The keyboard/mouse level shifters are separate circuits on sheet 4/5. Do not treat the gameport as 5 V logic or as a powered USB socket. |
| GPIO pins support interrupt operation | Zilog GPIO chapter: port pins can be vectored interrupt sources. This makes a GPIO packet transport conceivable; no useful rate/CPU-cost claim is established. |
| UART1 RX is PC1 | PC1 is gameport A Up, DE-9 pin 1, and expansion-header pin 15. A one-way adapter-to-eZ80 UART link is therefore a wiring-level candidate using only connector A. |
| UART1 TX is PC0 | PC0 is gameport B Up, DE-9 pin 1, and expansion-header pin 18. Bidirectional hardware UART needs access to both nets, unlike the proposed receive-only connector-A route. |
| Header duplicates gameport GPIO | The expansion header exposes all twelve signals; header and gameport access are shared ownership of the same CPU nets. The gameport adds its filter path. |
| Existing MOS documentation describes UART1 support | Official API documents open/close/read/write and UART1 interrupt vector 0x1A. Actual stock/EMOS pin setup, ownership, buffering and installed compatibility still require review. |

### Connector-to-header map

Directions are from the controller's perspective; UART RX/TX are from the
eZ80's perspective. Header numbers are EXP1 schematic pin numbers, not a cable
orientation or wiring instruction.

| Function | A GPIO | A EXP1 pin | B GPIO | B EXP1 pin |
|---|---|---|---|---|
| Up | PC1 / UART1 RX | 15 | PC0 / UART1 TX | 18 |
| Down | PC3 | 13 | PC2 | 16 |
| Left | PC5 | 11 | PC4 | 14 |
| Right | PC7 | 9 | PC6 | 12 |
| Button 1 | PD5 | 19 | PD4 | 22 |
| Button 2 | PD7 | 17 | PD6 | 20 |

### Source references and baseline

1. [Heber Console8 user manual, issue 2, 2024-01-23](https://heber.co.uk/wp-content/uploads/2024/01/Heber_Agon_Console8_user_manual-2.pdf):
   section 5.1 and schematic sheets 1/5, 2/5 and 5/5; published schematics
   labelled Rev 2.0, 2023-07-12. Download examined during the conversation:
   SHA-256 `44da31c513ea1a7050b492871e63ddad4a49461bac339ab9a2b502272dc610da`.
2. [Zilog eZ80F92/F93 product specification](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf):
   pin description PC1/RxD1 and PC0/TxD1; GPIO, interrupt and UART chapters.
   A revision-pinned complete review remains part of research; do not infer
   timing or mux guarantees from search excerpts alone.
3. Official Agon documentation reviewed at commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`: `mos/API.md` UART1 operations
   and interrupt-vector contract, `mos/C-Functions.md`, `GPIO.md`, and the
   Console8 description in `index.md`. This is an observed checkout commit,
   not a newly verified official release tag. Establish tagged source baselines
   before relying on MOS implementation details.
4. [Current controller guide](../controller-input.md),
   [direct F310 work](INPUT-003.md), and
   [application-owned controller API work](INPUT-005.md): reuse research for
   F310 XInput decoding, state semantics, validity and source ownership. Existing
   physical P4 acceptance is not qualification of the proposed gameport link.
   Also review [application API](../controller-api.md),
   [existing request/reply carrier](../protocols/controller-emos.md) and
   [measured extraction](INPUT-005/RESULTS.md) for actual ownership, current
   development-versus-installed limits and existing resident costs.
5. [Espressif USB host support](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/usb_host.html):
   S2/S3/P4 have USB OTG host support. A classic ESP32-WROOM-32 has no native
   USB host/hub; a USB programming connector does not supply that function.
   Identify the actual spare module and board before selecting adapter hardware.

## Research work and completion gates

1. **I06-R01 — Electrical path.** Extender traces all connector pins, ground,
   unused contacts and EXP1 duplicates from the exact schematic. Determine
   adapter logic/interface options, idle levels, output contention protection,
   external power requirements, and filter/cable effects on plausible UART
   rates. Separate calculations from measurements. No live probing selected.
2. **I06-R02 — UART1 and GPIO mux.** Review revision-pinned Zilog documentation
   and read-only official MOS references, then project-owned EMOS source.
   Determine whether receive-only UART1 can leave PC0 and the remaining pins
   as GPIO; whether existing initialization changes whole-port settings; what
   happens at boot, close and reset; and whether ordinary gameport B can
   coexist. Do not repeat the conversational claim that two ordinary joysticks
   must become impossible without resolving these distinctions.
3. **I06-R03 — Existing ownership.** Identify Console8 UART1/modem/expansion and
   Extender transport consumers. Explain which combinations conflict and how
   the application could use supported MOS facilities to acquire/release the
   peripheral, preserve pin/interrupt settings and handle competing owners.
   Do not add a controller-specific resident gateway to solve this by default.
   No supported bypass of EMOS routing or private transport state is proposed.
4. **I06-R04 — Adapter feasibility.** Compare reusing the P4 Extender's working
   F310 host input with a smaller S3-class USB-host board and a classic WROOM
   plus external host interface. Identify USB host power and XInput support;
   distinguish a hub, host controller and USB-to-serial programming bridge.
   No purchase, build or hardware selection is authorized by this comparison.
5. **I06-R05 — State and receive costs.** Propose a minimal receive-only framing
   concept, full controller state representation, bounded resynchronization,
   sequence/source identity, disconnect/stale-input neutralization, buffering
   and ISR/application ownership. Estimate serial utilization and CPU costs
   with explicit assumptions, not measured claims. No added CRC/checksum is
   selected; preserve the project's processor-communication cost instruction.
   Begin with periodic state and cumulative press counters, not inherited
   request/ACK/lease machinery. Determine the public API and documented hardware
   interface needed for an application-owned bounded receive buffer/ISR and
   its safe close/unload behavior; report unsupported requirements instead of
   silently patching MOS/VDP or borrowing private resident state.
6. **I06-R06 — Multiple controllers.** Distinguish two passive joysticks, one
   smart adapter plus a passive joystick, and one USB-host adapter multiplexing
   two USB controllers. Controller IDs are a candidate, not an agreed protocol.
   Establish USB hardware/software capacity and mux restrictions before claims.
7. **I06-R07 — Recommendation.** Return an actor-explicit feasibility report,
   unresolved questions, likely resource costs, and the smallest later prototype
   proposal. Record source revisions and evidence limits. Stop at research;
   hardware and implementation need Smith's subsequent selection.
8. **I06-R08 — EMOS byte-recovery opportunity.** Inventory controller-specific
   resident code, RAM, shared hooks, exact source/configuration and all callers.
   Compare the historical INPUT-005 accounting with the relevant current source
   without building or modifying it. Identify what could be removed if the
   reusable application driver replaces the resident service, what remains for
   existing users and what cannot yet be quantified. Separate resident savings
   from application/adapter costs. Return a bounded future removal proposal;
   do not remove support or claim installed savings in this research task.

## Decision register

| ID | State | Question / current direction |
|---|---|---|
| I06-D01 | Research direction selected | Investigate UART1 RX through gameport A, preserving an external plug-in adapter. GPIO bit-banging is background comparison, not the selected implementation. |
| I06-D02 | Open | Which adapter board/USB-host hardware should a later prototype use? Extender reuse is plausible; the spare WROOM identity and host capability are unverified. |
| I06-D03 | Open | Can receive-only UART1 preserve ordinary gameport B and other GPIO users under actual MOS initialization? |
| I06-D04 | Open | What MOS/application contract and UART1 ownership policy fit stock Console8 and project-owned EMOS without conflicts? |
| I06-D05 | Open | What signalling rate, framing, power arrangement and multi-controller policy should a later prototype test? |
| I06-D06 | Existing project constraint reaffirmed by Smith | No MOS/VDP hacks. Target supported public MOS facilities and an application-linked driver; no new controller-specific firmware requirement selected. |
| I06-D07 | Simple candidate for research | Periodic one-way full state, with cumulative press counters considered for short taps. Request/ACK/session machinery is not a default requirement; exact format remains open. |
| I06-D08 | Open | Which controller-specific EMOS bytes can be recovered without breaking existing users, and what is the exact supported source/build accounting? No removal authorized. |

These are research directions and unresolved design questions, not accepted
architecture. No normative protocol, firmware version or deployment is created.
