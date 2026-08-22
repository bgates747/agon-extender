# SETUP-004 — Determine upstream I/O driver disposition

## State

- Status: In progress — Work 1.a complete; Work 1.b next
- Started: 2026-08-20 20:52 EDT
- Finished: --

## Intent

Review the official VDP and vdp-gl hardware-facing I/O facilities and decide
which Extender must retain, replace, stub, omit, or defer. Reduce unnecessary
ESP32-PICO-to-P4 porting while preserving the externally observable behavior
required for VDP backward compatibility.

Begin from the documented VDU interface rather than implementation internals.
The Author will review each command or command family in
[`SETUP-004/VDU-inventory.md`](SETUP-004/VDU-inventory.md) and state which
observable behavior Extender promises to preserve. Driver disposition follows
from that product-level compatibility boundary.

This is a survey and disposition task. It does not implement driver removals,
replacement drivers, compatibility adapters, or build-selection changes.

## Authority and inputs

- [ADR-0013 — VDP survey findings and integration boundaries](../decisions/ADR-0013-vdp-survey-integration-boundaries.md)
- [SETUP-003 — official VDP structural inventory](SETUP-003.md)
- [SETUP-003 generated compiler and include evidence](SETUP-003/generated/)
- [Light 2 harness r01 first design target](../../hardware/designs/light2-harness-r01/README.md)
- Official VDP release `v2.16.0` at
  `c7ac293d2aa81ddfa693390549bcd909069c8fc3`
- vdp-gl tag `all-the-plots` at
  `ac2dd5986daf496c43ae8e7fe41836274aec54a0`

## Required dispositions

Assign exactly one provisional disposition to every material hardware-facing
subsystem:

- **Retain:** required substantially as implemented, subject to P4 adaptation.
- **Replace:** behavior is required but implementation becomes project-owned.
- **Stub:** an interface must remain, but no physical implementation is needed.
- **Omit:** neither implementation nor compatibility surface is required in the
  Extender image.
- **Defer:** evidence is insufficient; record the exact unresolved dependency
  or product decision.

Provisional dispositions become accepted architecture only after Author
review. Any accepted decision with broad or durable consequences receives an
ADR or an amendment to ADR-0013.

## Work

1. Derive a candidate inventory from compiler evidence, source includes,
   PlatformIO library selection, and targeted source searches. At minimum
   review:
   - **1.a** Arduino, ESP-IDF, and FreeRTOS hardware abstractions used by those
     areas;
   - **1.b** RTC and peripheral-device drivers;
   - **1.c** UART, GPIO, ADC, I2C, SPI, timers, interrupts, and ULP facilities;
   - **1.d** FabGL VGA, composite-video, display-controller, and canvas drivers;
   - **1.e** sound generators and physical audio output;
   - **1.f** PS/2 keyboard and mouse controllers;
   - **1.g** network, updater, and transfer facilities;
   - **1.h** storage and filesystem interfaces.

   For each candidate, record:
   - owning project and source files;
   - selected translation units and header-defined implementation;
   - direct hardware and architecture dependencies;
   - startup, task, interrupt, callback, and global-state connections;
   - VDP commands, responses, status packets, or application-visible
     behavior;
   - present physical owner: main board, onboard VDP, Extender, or none;
   - proposed disposition and rationale; and
   - dependencies on other disposition decisions.

   Trace each proposed omission far enough to identify compile/link fallout.
   Distinguish removing an independently selected translation unit from
   severing a header-defined or global-state dependency inside the effective
   VDP translation unit.
2. Identify facilities that are not needed physically but whose protocol
   surface must remain for backward compatibility. Recommend a project-owned
   adapter, inert stub, explicit unsupported response, or continued delegation
   to the onboard VDP as appropriate.
3. Produce a compact review matrix grouped by subsystem. Keep unresolved
   decisions here rather than in an ADR.
4. Present the matrix to the Author in manageable groups and record accepted
   dispositions. Create follow-on implementation tasks only after review.

## Initial accepted boundary

Per ADR-0013, FabGL PS/2 controller and physical keyboard/mouse support will
not be ported or built for Extender. Existing input responsibilities remain
with the Agon main board and onboard VDP. Any future Extender input facility is
project-owned. The survey must still trace protocol and compile-time coupling
before assigning the precise **Omit**, **Stub**, or **Replace** mechanics.

Retain keyboard and mouse command parsing and externally visible protocol state
needed by exclusive compatibility mode, while leaving cooperative-mode routing
unresolved. This retained surface does not reverse the physical-driver boundary:
upstream PS/2 acquisition remains excluded, and couplings such as sprite command
`&40` calling mouse-owned cursor code require a project-owned adapter or
delegation boundary.

Retain the complete buffered-callback facility unconditionally. Commands 80 and
81 modify EDP-local registration state, while callback execution can alter or
suppress later protocol packets. Exclusive compatibility mode requires those
indirect MOS-visible effects to match the official VDP behavior.

The Extender application interface is a stable, explicit EDU API with both
directly linked and optional resident-service implementations. The resident
service does not intercept stock VDU restart paths. See
[ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md).

### Known diagnostic-output constraint

Official VDP `v2.16.0` implements buffered command 128 with
`force_debug_log()` through `DBGSerial`, which is stock UART0 on ESP32 pins 3
and 1. It reports the stream count, prints transform matrices in readable form,
or emits the entire first buffer stream as hexadecimal. It sends no VDP protocol
packet and modifies no MOS sysvar.

The P4 port must bind this command to an explicit EDP diagnostic console or log
sink rather than inherit the upstream UART mapping. Because output is
synchronous and unbounded by command semantics, large buffers can stall VDU
processing and may expose task-latency or watchdog problems. Preserve that
behavioral warning during implementation and qualification.

## Outputs

- A machine-readable driver/subsystem inventory under
  `docs/tasks/SETUP-004/generated/`.
- A concise review matrix under `docs/tasks/SETUP-004/`.
- Task-local reproducible extractors under `docs/tasks/SETUP-004/scripts/` if
  SETUP-003 evidence is insufficient.
- Follow-on implementation tasks and accepted ADR updates after review.

## Work 1.a execution record

The deterministic extraction classified 764 scoped evidence items: 719 belong
to 13 framework/runtime candidates and 45 are explicitly assigned to later
Work 1 boundaries. No item is ambiguous or unclassified. The passing
[coverage audit](SETUP-004/generated/work-1a/coverage.yaml) and generated
[disposition matrix](SETUP-004/disposition-matrix.md) record the completed
Author review. Every candidate has an accepted disposition; explicitly deferred
design and qualification details remain in their named follow-on work.

### Work 1.a Author review

- **Accepted — `framework-unused-wifi-include`: Omit.** Official VDP v2.16.0
  includes `WiFi.h` but has no WiFi API consumer or runtime activation. Remove
  the include from the Extender source; no adapter or stub is required.
- **Upstream contribution opportunity:** test removal of the same include in an
  otherwise untouched v2.16.0 checkout using the exact upstream build. If that
  proves no accidental transitive-header dependency, propose the one-line
  cleanup upstream. This is not required for the Extender port and does not
  authorize changing the official checkout or opening a PR.

### Work 1.a question register

These questions were resolved one at a time. Each answer is recorded as
**Accepted**, **Deferred** to a named task or decision, or **Rejected** with a
replacement disposition. Work 1.a closed after every question was disposed and
the generated audit and projections were refreshed.

#### W1A-Q01 — Arduino core types and utilities

- **Status:** Accepted — Retain (2026-08-21)
- **Candidate:** `framework-arduino-core-types`
- **Question:** Retain the Arduino source-level contracts used by vendored
  agon-vdp, vdp-gl, ESP32Time, and CRC code, including `Arduino.h`, `String`,
  and `map()`?
- **Recommendation:** **Retain.** They are available under the accepted hybrid
  framework and avoiding them would require unnecessary upstream-source
  surgery.
- **Alternatives/tradeoffs:** Replace with standard C++ or project-owned
  equivalents, increasing divergence and future upstream-merge work; omission
  would fail compilation.
- **Downstream effect:** Individual hardware APIs remain subject to their own
  disposition; this accepts only the shared source compatibility layer.
- **Disposition:** **Retain.** Preserve the shared Arduino source-compatibility
  layer; hardware-facing APIs remain independently reviewable.

#### W1A-Q02 — Arduino sketch lifecycle

- **Status:** Accepted — Retain (2026-08-21)
- **Candidate:** `framework-arduino-sketch-lifecycle`
- **Question:** Retain Arduino `setup()`/`loop()` lifecycle idioms and upstream
  startup shape on P4?
- **Recommendation:** **Retain.** The hybrid-framework decision and physical
  canary already qualify this lifecycle, and preserving it minimizes upstream
  structural divergence.
- **Alternatives/tradeoffs:** Replace it with a pure ESP-IDF `app_main`, gaining
  direct lifecycle control at the cost of needless porting and merge burden;
  omission removes firmware startup.
- **Downstream effect:** The contents and ordering of `setup()` remain subject
  to display, transport, audio, and input dispositions.
- **Disposition:** **Retain.** Preserve upstream `setup()`/`loop()` structure;
  adapt startup contents only as owning subsystem decisions require.

#### W1A-Q03 — Arduino Stream/Print contract

- **Status:** Accepted — Retain (2026-08-21)
- **Candidate:** `framework-arduino-stream-contract`
- **Question:** Retain the abstract Arduino `Stream`/`Print` byte-stream
  interface as the compatibility seam used by VDP command processing and
  internal buffer streams?
- **Recommendation:** **Retain.** It separates parser behavior from physical
  transport and allows Extender-owned transports to replace stock UART without
  rewriting the parser family.
- **Alternatives/tradeoffs:** A project-owned stream abstraction could reduce
  Arduino coupling but would touch pervasive upstream interfaces; omission is
  compile-incompatible.
- **Downstream effect:** This does not retain `Serial2`, UART pin mappings, or
  stock duplex behavior; those are W1A-Q05 and later peripheral decisions.
- **Disposition:** **Retain.** Preserve the abstract byte-stream seam without
  retaining stock `Serial2`, pin assignments, or duplex behavior.

#### W1A-Q04 — Arduino timing services

- **Status:** Accepted — Retain (2026-08-21)
- **Candidate:** `framework-arduino-timing`
- **Question:** Retain portable Arduino `millis()`, `micros()`, `delay()`, and
  `delayMicroseconds()` calls where their owning subsystem survives?
- **Recommendation:** **Retain**, subject to subsystem-specific timing
  qualification. The accepted target framework supplies them and replacing
  every call adds divergence without an identified benefit.
- **Alternatives/tradeoffs:** Replace globally with ESP-IDF timing APIs for
  finer control, at the cost of broad source changes; omission breaks timing,
  timeout, and pacing behavior.
- **Downstream effect:** Low-level drivers may still require targeted timing
  replacement after Work 1.c–1.f determines their disposition.
- **Disposition:** **Retain.** Preserve portable Arduino timing calls where the
  owning subsystem survives, subject to later driver-level qualification.

#### W1A-Q05 — Concrete serial bindings

- **Status:** Accepted with explicit follow-on work 2026-08-22
- **Candidates:** `framework-primary-vdp-serial-binding` and
  `framework-debug-serial-binding`
- **Question:** Replace the stock `Serial2`/`VDPSerial` and UART0 `DBGSerial`
  bindings while preserving the stream-facing protocol and diagnostic
  behavior that remains required?
- **Recommendation:** **Replace.** Rev 1 separates high-speed forward command
  transport, UART return traffic, and diagnostics; stock pin and duplex
  assumptions cannot represent that architecture.
- **Alternatives/tradeoffs:** Retaining stock bindings conflicts with Extender
  wiring and transport ownership; omission would break protocol consumers and
  diagnostic command behavior; stubbing would lose required return traffic.
- **Downstream effect:** Exact replacements depend on Work 1.c transport/GPIO
  review, Work 1.g transfer/update review, and SETUP-005's unresolved routing
  mechanism between onboard VDP and EDP.
- **Disposition:** Replacement direction accepted, but the candidate remains
  pending until W1A-Q05.a–e are explicitly disposed.

##### W1A-Q05.a — Default legacy path

- **Status:** Accepted (2026-08-21)
- **Decision:** Unaware legacy applications default to the regular UART path.
  Extender-aware software may select other transports through mechanisms
  defined elsewhere.

##### W1A-Q05.b — Exact legacy UART contract

- **Status:** Accepted (2026-08-21)
- **Question:** Must Extender's legacy UART-facing mode preserve all
  host-observable official VDP v2.16.0 serial behavior: 1,152,000 baud, 8N1,
  RTS flow control in the default mode, optional CTS/RTS full-duplex switching,
  command byte-stream semantics, return-packet encoding, and timeout behavior?
- **Recommendation:** **Yes**, except physical ESP32 pin numbers, buffer sizes,
  and internal driver implementation are not contractual. This gives untouched
  MOS and legacy applications the same wire protocol while permitting P4-owned
  internals.
- **Alternatives/tradeoffs:** Preserving only command bytes but changing flow
  control or duplex behavior could break MOS versions or timing-sensitive
  software; preserving stock pins and buffers would confuse compatibility with
  obsolete implementation detail.
- **Disposition:** **Preserve exactly at the host-visible boundary.** Preserve
  1,152,000 baud, 8N1, default RTS flow control, optional CTS/RTS full-duplex
  switching, command and return-packet encodings, and observable timeout
  behavior. Internal buffers and driver implementation are not contractual.

##### W1A-Q05.b.1 — Pin-configuration policy

- **Status:** Accepted (2026-08-21)
- **Source finding:** Official VDP v2.16.0 centralizes the protocol UART values
  as `UART_TX`, `UART_RX`, `UART_RTS`, and `UART_CTS` in `video/agon.h`, and
  `video/vdp_protocol.h` consumes those names. The separate debug UART is an
  exception: `video/video.ino` hardcodes RX GPIO 3 and TX GPIO 1 in
  `DBGSerial.begin()`.
- **Question:** Preserve upstream names and initialization shape, but place P4
  pin values in a visible, tracked compile-time board profile, while giving
  project-owned extensions their own configuration namespace?
- **Recommendation:** **Yes.** Keep upstream identifiers and source locations
  wherever the P4 permits. Do not promise the stock ESP32-PICO GPIO numbers on
  different silicon; select P4 pins from the qualified wiring profile. Replace
  the hardcoded debug pins with named profile values as a prominently recorded
  mandatory port deviation. Treat pins as build/hardware configuration, not a
  runtime end-user setting.
- **Alternatives/tradeoffs:** Reusing stock GPIO numbers merely because the
  numbers match may conflict with P4 board functions; scattering new literals
  repeats the upstream debug-pin defect; runtime configurability adds startup
  and recovery complexity without a present use case.
- **Disposition:** Preserve upstream UART macro names and initialization shape;
  supply P4 values through a visible tracked compile-time board profile. Keep
  Extender-only pins in a project namespace. Replace hardcoded debug GPIO 3/1
  with named profile values as a documented mandatory port deviation. Runtime
  pin configuration is not presently required.

##### W1A-Q05.c — VDP/EDP endpoint routing

- **Status:** Deferred to `SETUP-005-D003` (2026-08-21)
- **Question:** Dispose the mechanism that routes a legacy UART stream to the
  onboard VDP or EDP by explicitly deferring it to `SETUP-005-D003`?
- **Recommendation:** **Defer to SETUP-005-D003.** Q05 must constrain routing to
  preserve the accepted default and wire contract, but choosing interception,
  MOS integration, resident service, or another mechanism belongs to the EDU
  operating-mode task.
- **Disposition:** Implementation mechanism unknown and explicitly deferred.
  The target contract is binding: unaware legacy applications default to
  regular UART, and endpoint routing must preserve the exact legacy contract.

##### W1A-Q05.d — Extender transport implementation

- **Status:** Disposed — baseline accepted; validation deferred to
  `SETUP-004.1.c` (2026-08-22)
- **Source finding:** The predecessor project contains a physically exercised
  eight-bit forward bus, stable Light 2/P4 pin map, electrical conditioning,
  and bounded PC0/PC1 UART evidence. These have been adopted as
  [`light2-harness-r01`](../../hardware/designs/light2-harness-r01/README.md).
  The profile is now the authoritative first design target. The UART fixture
  deliberately ran at 115,200 baud to prove wiring and direction before speed;
  it is the candidate physical path for the 1,152,000-baud legacy contract, not
  a separate product channel.
- **Question:** With the mature forward design adopted, dispose the remaining
  official-UART and integration choices by assigning validation
  to `SETUP-004.1.c`, followed by separately created implementation work?
- **Recommendation:** **Use `light2-harness-r01` as Work 1.c's default baseline,
  then create implementation work afterward.** Work 1.c should validate pin
  conflicts, P4 peripheral routing, 1,152,000-baud electrical margin, complete
  legacy flow-control behavior, and coexistence with retained board facilities.
  Departure from the proved map requires evidence and a new harness revision.
- **Alternatives/tradeoffs:**
  - Treat the predecessor's 115,200-baud pass as complete qualification. This
    would confuse wiring correctness with proof of ten-times-faster operation
    and complete legacy flow-control behavior.
  - Redesign all pins from scratch. This discards physically exercised geometry
    and performance evidence without an identified conflict.
  - Implement the imported map without Work 1.c validation. This risks target-
    speed failure or collision with pin mux and later retained P4 facilities.
  - Implement transport inside Work 1.c. This conflates survey/disposition with
    source modification and violates SETUP-004's review boundary.
- **Disposition:** The `light2-harness-r01` forward map and electrical baseline
  are accepted as the authoritative first design target, including its buffered
  PC0/PC1 legacy-UART candidate path. Work 1.c must qualify 1,152,000-baud
  operation, complete legacy flow control, pin mux, and parallel-bus coexistence;
  it then creates separate implementation work. Departure from the baseline
  requires evidence and a new harness revision.

##### W1A-Q05.e — Existing DBGSerial consumers

- **Status:** Accepted 2026-08-22; exact mode-specific behavior deferred to
  `SETUP-005-D006`
- **Question:** Dispose the consumers currently collapsed onto upstream
  `DBGSerial` by deferring console, printer, diagnostic, and ZDI transport
  ownership to `SETUP-004.1.c`, and HEX/YMODEM/updater transfer ownership to
  `SETUP-004.1.g`, with no implicit global UART0 binding retained?
- **Recommendation:** Superseded by Author decision.
- **Disposition:** Extender v1 does not support printer/USB serial,
  console/terminal, ZDI, Intel HEX, YMODEM, updater, or local-debug facilities.
  In legacy mode Extender is electrically and logically absent and the onboard
  VDP retains stock behavior. In cooperative mode ordinary VDU may still reach
  those onboard-VDP facilities. EDP-exclusive handling is mode-contract
  dependent: strict compatibility preserves stock-observable behavior, while
  non-strict operation should fail deterministically and recover cleanly.

##### W1A-Q05.e.1 — Exact unsupported-command semantics

- **Status:** Deferred — accepted 2026-08-22
- **Question:** Explicitly defer command-by-command no-op, rejection, status,
  timeout, and parser recovery behavior to `SETUP-005-D006`?
- **Recommendation:** **Defer to SETUP-005-D006.** The v1 omission and mode
  boundary are accepted here; exact behavior requires command framing and MOS
  compatibility analysis. The task must ensure unsupported commands cannot
  block on absent USB/UART hardware or leave the EDP parser in a loader,
  terminal, console, updater, or debug-output state.
- **Disposition:** Defer the command-by-command analysis to `SETUP-005-D006`.
  Mirror current stock VDP command framing, consumption, parser recovery, and
  externally observable failure behavior as closely as practical. Stock
  behavior observed by the Author includes silent failure, garbage screen
  output with continued operation, hardware reset, and—at the severe end—an
  ESP32 Guru Meditation. Strict compatibility modes preserve observable stock
  behavior even when that permits a reset, crash, corrupted output, or other
  undesirable result. Modes not promising strict compatibility should improve
  this behavior through deterministic failure, parser recovery, and useful
  diagnostics. `SETUP-005-D006` must define the mode-specific boundary rather
  than imposing one universal safe-failure policy.

##### W1A-Q05.f — Split mixed serial candidate

- **Status:** Accepted 2026-08-22
- **Question:** Split the present combined mechanical candidate so primary
  `VDPSerial` transport is **Replace**, while the `DBGSerial` binding is
  **Omit** and its retained command parsers receive the safe unsupported
  handling owned by `SETUP-005-D006`?
- **Recommendation:** **Yes.** One candidate may not carry mixed dispositions.
  Regenerate Work 1.a after splitting scope, mechanical evidence, reviewed
  records, and fallout analysis; do not reinterpret the accepted decisions.
- **Disposition:** Split the candidate as proposed. Primary `VDPSerial` is
  **Replace** while preserving the accepted wire contract; `DBGSerial` is
  **Omit**, with affected command behavior owned by `SETUP-005-D006`. This is
  the initial source-survey boundary and may be revised if deeper review exposes
  an inseparable dependency or a narrower defensible split.

#### W1A-Q06 — FreeRTOS concurrency

- **Status:** Accepted 2026-08-22
- **Candidate:** `framework-freertos-concurrency`
- **Question:** Retain FreeRTOS tasks, queues, semaphores, timers, and task
  notifications as the firmware concurrency substrate?
- **Recommendation:** **Retain.** ESP-IDF supplies FreeRTOS on P4, upstream uses
  it pervasively, and the qualified framework profile already fixes the
  required tick rate.
- **Alternatives/tradeoffs:** Replacing it would amount to rewriting the
  scheduler-facing architecture; omission is compile- and runtime-incompatible.
- **Downstream effect:** Particular tasks and queues disappear when their
  owning display, audio, or input subsystem is omitted; retention does not
  preserve every upstream worker.
- **Disposition:** **Retain.** Use the FreeRTOS implementation supplied by the
  selected ESP-IDF/P4 environment. Preserve upstream concurrency architecture
  initially; qualify and adapt task topology, affinity, priority, stack sizing,
  timing, and synchronization where P4 behavior or retained subsystem ownership
  requires it. This does not require implementing or vendoring FreeRTOS.

#### W1A-Q07 — Watchdog and core-control policy

- **Status:** Accepted 2026-08-22
- **Candidate:** `framework-watchdog-and-core-control`
- **Question:** Replace inherited watchdog disabling, obsolete watchdog setup,
  and ESP32-era core-placement assumptions with an explicit P4 policy?
- **Recommendation:** **Replace.** Preserve supervision and scheduling intent,
  but do not inherit global watchdog disabling or the source-incompatible
  ESP-IDF 4-era `esp_task_wdt_init()` call.
- **Alternatives/tradeoffs:** Retaining unchanged code fails against ESP-IDF
  5.5.5 and preserves unqualified policy; omission risks unexplained resets or
  hangs; deferral blocks serious runtime qualification.
- **Downstream effect:** Final subscriptions, timeouts, and affinity depend on
  retained display/audio workers from Work 1.d and 1.e.
- **Disposition:** **Replace.** Define one P4-native internal watchdog and
  core-placement policy, with activation and workload tuned by operating mode.
  Legacy mode requires only supervision of whatever dormant housekeeping
  remains active. EDP-exclusive and cooperative modes use explicit P4 task
  supervision and measured placement rather than inherited ESP32-PICO global
  watchdog disabling. Compatibility governs externally observable behavior,
  not obsolete watchdog internals: a strict mode may intentionally produce a
  stock-compatible reset or failure where required, while non-strict operation
  should recover and diagnose faults. Exact subscriptions, timeouts, affinity,
  and controlled-reset cases remain later subsystem qualification work.

#### W1A-Q08 — PSRAM and capability heap

- **Status:** Accepted 2026-08-22
- **Candidate:** `framework-psram-and-capability-heap`
- **Question:** Retain Arduino PSRAM and ESP-IDF capability-heap APIs as the
  allocation substrate for large buffers and DMA-constrained objects?
- **Recommendation:** **Retain.** The P4 profile physically qualifies 32 MiB
  PSRAM, and upstream data structures depend heavily on capability-aware
  allocation.
- **Alternatives/tradeoffs:** A project-owned allocator wrapper may be useful
  later but cannot eliminate the underlying ESP-IDF capabilities; omission
  causes compilation failures or severe internal-memory pressure.
- **Downstream effect:** Allocation policy and DMA placement require later
  subsystem qualification; retained APIs do not guarantee unchanged allocation
  sizes or lifetimes.
- **Disposition:** **Retain.** Preserve Arduino PSRAM and ESP-IDF
  capability-aware allocation as the underlying memory substrate. Extender may
  add project-owned allocation helpers, but must continue distinguishing
  external, internal, DMA-capable, and other constrained memory. Later design
  should consider compile-time firmware profiles that exploit P4 memory and
  performance more aggressively at the cost of strict backward-behavior
  fidelity. Such profiles are not the compatibility baseline; EDU-aware
  applications must query advertised capabilities so they can deliberately use
  the active hardware limits.

##### W1A-Q08.a — Performance-oriented build profiles

- **Status:** Deferred
- **Question:** Define compile-time profiles, their compatibility guarantees,
  and the EDU capability-discovery contract for P4-native performance choices.
- **Disposition:** Preserve as follow-on architecture work. SETUP-004.1.a only
  establishes that retained capability-aware allocation can support both a
  compatibility baseline and future performance-oriented builds.

#### W1A-Q09 — Interrupt and critical-section services

- **Status:** Accepted 2026-08-22
- **Candidate:** `framework-idf-interrupt-and-critical-services`
- **Question:** Retain portable ESP-IDF interrupt allocation, ISR notification,
  critical-section, and IRAM-placement mechanisms for surviving drivers?
- **Recommendation:** **Retain** the abstractions, while replacing
  ESP32-specific registers, sources, and peripheral assumptions in their owning
  Work 1 items.
- **Alternatives/tradeoffs:** A wholesale wrapper would add another abstraction
  without removing ESP-IDF underneath; omission prevents surviving hardware
  drivers from functioning.
- **Downstream effect:** Work 1.c–1.f decides which concrete ISR paths remain;
  this decision does not retain PS/2, VGA, or stock audio hardware.
- **Disposition:** **Retain** the portable ESP-IDF interrupt, ISR handoff,
  critical-section, and IRAM-placement mechanisms for surviving and new P4
  drivers. Do not infer retention of any concrete upstream physical driver:
  ESP32-specific sources, registers, and peripheral assumptions remain subject
  to their owning Work 1 reviews. In particular, Extender v1 does not initially
  own the physical PS/2 keyboard or mouse drivers; their input ownership and
  event routing are tracked separately under `SETUP-005-D007`.

#### W1A-Q10 — OTA and restart services

- **Status:** Split for review 2026-08-22
- **Question:** The reusable ESP-IDF primitives and stock serial updater carry
  different ownership and dispositions; review them separately.
- **Disposition:** Split into W1A-Q10.a and W1A-Q10.b.

##### W1A-Q10.a — ESP-IDF OTA and restart primitives

- **Status:** Accepted 2026-08-22
- **Candidate:** `framework-idf-ota-and-restart-primitives`
- **Question:** Retain ESP-IDF's flash-update, boot-partition, image-lifecycle,
  rollback, and restart primitives for the eventual Extender update service?
- **Recommendation:** **Retain.** ADR-0007 already selects dual OTA slots and
  requires ESP-IDF image-validity and rollback integration. Retention does not
  select a network protocol, expose an updater command, or preserve the stock
  transaction.
- **Alternatives/tradeoffs:** Omission requires replacing ESP-IDF's flash and
  boot lifecycle ourselves. Deferral leaves the accepted partition strategy
  without its intended implementation substrate.
- **Downstream effect:** Work 1.g must still design authorization, transport,
  validation, rollback, power-loss recovery, and user-visible status.
- **Disposition:** **Retain.** Use ESP-IDF's proven OTA image, partition,
  rollback, and restart lifecycle as the Extender update substrate to the extent
  that it remains adequate and is not materially worse than normal clean-sheet
  ESP32-P4 practice. Do not invent a project-owned replacement without concrete
  evidence of a material deficiency. Work 1.g still owns the update service,
  transport, authorization, recovery, and qualification design.

##### W1A-Q10.b — Stock VDP serial updater

- **Status:** Accepted 2026-08-22
- **Candidate:** `framework-stock-serial-updater`
- **Question:** Omit the stock `VDP_UPDATER` serial command path from Extender
  v1 while retaining mode-specific parser behavior?
- **Recommendation:** **Omit.** This follows the accepted maintenance-facility
  carveout and avoids inheriting stock stream/display assumptions and a
  defective OTA transaction.
- **Disposition:** **Omit.** Legacy and applicable cooperative operation leave
  the facility to the onboard VDP. Extender does not perform the stock serial
  update transaction. `SETUP-005-D006` defines how strict and non-strict
  EDP-exclusive modes consume and respond to attempted commands.

The complete scan includes Arduino core types and utilities among 13 current
candidates. Direct `Arduino.h`, `String`, and `map()` dependencies span
`agon-vdp`, vdp-gl, ESP32Time, and CRC and must remain available to the vendored
source. Exact installed Arduino-ESP32 3.3.11 and ESP-IDF 5.5.5 headers were
hashed and reviewed for the target-side contracts cited by the evidence.

Two porting hazards require prominent preservation:

- vdp-gl's `FileBrowser::format()` uses the ESP-IDF 4-era
  `esp_task_wdt_init(45, false)` form. ESP-IDF 5.5.5 requires an
  `esp_task_wdt_config_t` pointer, so unchanged source is incompatible and the
  inherited watchdog/core policy is provisionally **Replace**.
- official agon-vdp `v2.16.0` begins and writes an OTA transaction in
  `video/updater.h::receiveFirmware()` but calls neither `esp_ota_end()` nor
  `esp_ota_abort()`. This inherited upstream defect is recorded with its
  provenance, required local remedy, and removal condition. The defective stock
  serial updater is **Omit**; reusable ESP-IDF OTA/restart primitives remain an
  independent **Retain** proposal for Author review.

The mechanical graph slices retain 1,482 conservative unresolved relationship
IDs and 75 explicit continuations into later survey boundaries. These are not
missing scope assignments: they preserve PORT-001's lexical uncertainty and
prevent broad reverse slices from asserting false absence. Reviewed behavioral
claims remain bounded by targeted source inspection. No firmware, source
selection, or build configuration changed during Work 1.a.

## Review gate

Stop after producing and explaining the provisional disposition matrix. Do not
alter source selection, add stubs, or modify VDP/vdp-gl code until the Author
has reviewed the affected subsystem group.
