# SETUP-004 — Determine upstream I/O driver disposition

## State

- Status: Complete — all subsystem dispositions accepted or explicitly deferred
- Started: 2026-08-20 20:52 EDT
- Finished: 2026-08-22 06:55 EDT

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

## Work 1.b execution record

The deterministic extraction classified 145 scoped RTC and peripheral-driver
evidence items: 141 belong to four candidates and four are explicitly delegated
to Work 1.c's low-level I2C review. No item is ambiguous or unclassified. The
[coverage audit](SETUP-004/generated/work-1b/coverage.yaml) passes without
errors or warnings, and the provisional records are included in the generated
[disposition matrix](SETUP-004/disposition-matrix.md).

Targeted source review established these bounded facts:

- official VDP `v2.16.0` implements its application-visible RTC service with a
  global `ESP32Time` object backed by ESP-IDF/Newlib system time;
- `VDU 23,0,&87`, the six-byte `PACKET_RTC` payload and eight-octet wire frame,
  RTC-backed VDP variables, and packet callbacks form one protocol surface
  independent of the concrete clock provider;
- MOS `v3.0.2` receives stock VDP packets on UART0, copies the six RTC payload
  octets into MOS-owned sysvars at offset `0x1A`, and sets completion-flag bit
  5; the adopted Extender return path is eZ80 UART1, which stock MOS does not
  feed to that parser;
- vdp-gl's DS3231 and MCP23S17 drivers are independently selected translation
  units but have no evidenced official-VDP runtime consumer; and
- generic vdp-gl `TSI2C` implementation details remain assigned to Work 1.c.

No firmware, source selection, or build configuration changed during this
survey.

### Work 1.b question register

Resolve these questions one at a time. A question is disposed only when its
answer is recorded as **Accepted**, **Deferred** to a named task or decision, or
**Rejected** with a replacement disposition. Work 1.b cannot close until all
four candidate dispositions and the clock-policy dependency are explicitly
disposed.

#### W1B-Q01 — RTC protocol surface

- **Status:** Accepted — Retain with mode-qualified ownership (2026-08-22)
- **Candidate:** `rtc-protocol-surface`
- **Question:** Retain stock `VDU 23,0,&87`, the six-byte packed RTC payload and
  eight-octet wire framing, RTC-backed VDP variables, and packet callbacks as
  an **EDP-exclusive compatibility contract**, without claiming that Extender
  owns or may directly write canonical MOS sysvars?
- **Recommendation:** **Retain with a strict ownership qualification.** In
  legacy and stock-MOS cooperative modes, the onboard VDP remains the sole
  producer of canonical RTC sysvar updates. An EDU RTC operation returns data
  through EDU-owned application/service state. In EDP-exclusive mode, stock
  sysvar compatibility is available only if an Extender-enabled MOS explicitly
  routes the UART1 response through a MOS-owned parser and performs the write.
- **Alternatives/tradeoffs:** Omission drops RTC from the EDP-exclusive legacy
  promise. Emitting the frame blindly over UART1 does not update stock MOS and
  must not be represented as compatibility. Direct application or resident
  service writes into MOS sysvars would violate ownership and are rejected.
- **Downstream effect:** `SETUP-005-D003` must decide whether the project ships
  and maintains the required MOS route; without it, full RTC compatibility is
  impossible in EDP-exclusive mode. `SETUP-005-D008` separately defines clock
  authority and synchronization.
- **Disposition:** **Retain.** Strict EDP-exclusive compatibility preserves the
  stock command, six-byte payload, eight-octet frame, VDP-variable behavior,
  callbacks, and—through a selected MOS-owned route—canonical sysvar effects
  with as much fidelity as practical. This strict-mode requirement is
  sufficient to retain the code and contract. Cooperative-mode RTC behavior
  remains under `SETUP-005-D003` and `SETUP-005-D008`; its unresolved details
  do not weaken or defer the retention decision.

#### W1B-Q02 — ESP32Time provider

- **Status:** Accepted — Retain (2026-08-22)
- **Candidate:** `rtc-esp32time-provider`
- **Question:** Retain the pinned ESP32Time provider as the initial P4 clock
  implementation behind the stock RTC protocol surface?
- **Recommendation:** **Retain.** It is a thin upstream-compatible layer over
  normal ESP-IDF/Newlib system time and avoids needless source divergence. A
  project-owned policy layer may wrap it later without changing its callers.
- **Alternatives/tradeoffs:** Immediate replacement adds porting and merge work
  without an evidenced deficiency; omission requires a source-compatible
  replacement before RTC code can compile.
- **Downstream effect:** Work 1.g must qualify any network-time facility.
  Accuracy, reset persistence, timezone behavior, and synchronization policy
  remain unresolved under `SETUP-005-D008`.
- **Disposition:** **Retain.** Use pinned ESP32Time `2.0.6` as the initial P4
  clock provider. Preserve its upstream-facing API and place any future
  authority, synchronization, persistence, or mode policy in a project-owned
  wrapper. Replace the provider only if qualification establishes a material
  limitation.

#### W1B-Q02.a — Clock authority and synchronization policy

- **Status:** Deferred to `SETUP-005-D008` (2026-08-22)
- **Question:** Defer selection of the authoritative clock and the rules for
  MOS, onboard-VDP, EDP, and network synchronization to `SETUP-005-D008`?
- **Recommendation:** **Defer.** The policy is mode- and routing-sensitive but
  does not prevent retaining either the protocol surface or initial provider.
- **Alternatives/tradeoffs:** Selecting policy during this driver survey would
  pre-empt unresolved response routing and cooperative-mode ownership; leaving
  it unnamed would conceal a material implementation dependency.
- **Downstream effect:** RTC implementation and qualification may proceed only
  after `SETUP-005-D008` defines authority, synchronization, conflicts, and
  capability/status behavior.
- **Disposition:** **Defer.** `SETUP-005-D008` is the authoritative home for
  clock authority, mode-specific read/set routing, synchronization, persistence,
  timezone, conflict, failure, and capability/status policy. The deferral does
  not block the accepted RTC-surface or ESP32Time retention decisions.

#### W1B-Q03 — vdp-gl DS3231 driver

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `peripheral-vdp-gl-ds3231`
- **Question:** Omit vdp-gl's independently compiled DS3231 hardware-RTC driver
  from the Extender build?
- **Recommendation:** **Omit.** Official VDP uses ESP32Time instead, neither the
  stock nor current Extender v1 hardware contains a DS3231, and no official-VDP
  runtime consumer was found.
- **Alternatives/tradeoffs:** Retention adds unused driver and I2C coupling;
  stubbing or replacement preserves no required interface. Future DS3231
  support would be a separately owned hardware feature.
- **Downstream effect:** The future port must exclude `DS3231.cpp` while
  preserving any umbrella declarations needed by otherwise retained vdp-gl
  code. Work 1.c validates the I2C/source-filter fallout.
- **Disposition:** **Omit from the Extender build; retain unchanged in the
  complete vendored vdp-gl release.** Exclude `DS3231.cpp` through
  project-owned source selection. Preserve upstream declarations unless build
  qualification proves a narrow change necessary. Work 1.c validates the I2C
  and link fallout; PORT-002 makes the vendored-versus-selected distinction and
  its upstream-merge significance explicit in the dependency graph.

#### W1B-Q04 — vdp-gl MCP23S17 driver

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `peripheral-vdp-gl-mcp23s17`
- **Question:** Omit vdp-gl's independently compiled MCP23S17 SPI GPIO-expander
  driver from the Extender build?
- **Recommendation:** **Omit.** No current stock or Extender v1 hardware uses
  the device and no official-VDP runtime consumer was found.
- **Alternatives/tradeoffs:** Retention adds unused SPI/GPIO and interrupt
  coupling; stubbing or replacement preserves no required interface. A future
  expander would be a project-owned hardware feature selected deliberately.
- **Downstream effect:** The future port must exclude `MCP23S17.cpp` while
  preserving any umbrella declarations needed elsewhere. Work 1.c validates
  the source-filter and low-level peripheral fallout.
- **Disposition:** **Omit from the Extender build; retain unchanged in the
  complete vendored vdp-gl release.** Exclude `MCP23S17.cpp` through
  project-owned source selection. Preserve upstream declarations unless build
  qualification proves a narrow change necessary. Work 1.c validates SPI,
  GPIO, interrupt, and link fallout; PORT-002 records the file as
  vendored-but-excluded and preserves its merge-review significance.

Work 1.b is complete. All four candidate dispositions completed Author review;
the distinct clock-authority policy was explicitly deferred to
`SETUP-005-D008`. The refreshed audit passes with no errors, warnings,
ambiguous evidence, or unclassified evidence.

## Work 1.c execution record

The deterministic extraction classified 703 scoped low-level transport and
peripheral items: 507 belong to ten candidates and 196 are explicitly delegated
to their display, audio, concrete-interrupt, RTC, or storage owners. No item is
ambiguous or unclassified. The
[coverage audit](SETUP-004/generated/work-1c/coverage.yaml) passes without
errors or warnings, and the provisional records are included in the generated
[disposition matrix](SETUP-004/disposition-matrix.md).

Six candidate dispositions follow decisions already accepted during Work 1.a,
Work 1.b, and ADR-0013/0014:

- **Replace** the stock UART hardware binding with the accepted Extender
  transport while preserving required Stream and strict wire contracts.
- **Omit** terminal-mode ADC extensions, vdp-gl TSI2C, ESP32 ULP/RTC-domain PS/2
  support, and the ZDI direct-register GPIO helper.
- **Retain** the source-compatible pinned-core interrupt-allocation helper only
  for concrete drivers retained by later work.

The P4 framework supplies portable GPIO, SPI, `esp_timer`, IPC, UART, ADC, I2C,
and interrupt APIs. Availability does not retain an upstream consumer or pin
assignment. Conversely, the ESP32/Xtensa clock and cycle-counter utility is not
a portable implementation: the P4 is RISC-V and direct preprocessing already
fails at the absent `soc/frc_timer_reg.h` header.

No firmware, source selection, or build configuration changed during this
survey.

### Work 1.c question register

Resolve these remaining questions one at a time. Existing accepted decisions
are not reopened. Work 1.c closes only after W1C-Q01–Q04 are explicitly
disposed and the generated audit is refreshed.

#### W1C-Q01 — Portable GPIO services

- **Status:** Accepted — Retain (2026-08-22)
- **Candidate:** `peripheral-portable-gpio-services`
- **Question:** Retain ordinary Arduino/ESP-IDF GPIO direction, read, and write
  services for surviving P4 drivers while rejecting inherited pin assignments
  and omitted consumers?
- **Recommendation:** **Retain.** These are normal P4 platform services needed
  by project-owned transport and surviving display/peripheral code. Retention
  does not select terminal GPIO extensions, MCP23S17, ZDI, stock VGA pins, or
  any other concrete physical driver.
- **Alternatives/tradeoffs:** Replacing standard P4 GPIO APIs adds an
  unnecessary abstraction; omission prevents retained hardware code from
  configuring pins. Unqualified retention could accidentally preserve stock
  pin mappings, so mappings remain explicit hardware-profile data.
- **Downstream effect:** Work 1.d, 1.e, and 1.h qualify their concrete consumers;
  pin-mux and electrical conflicts remain hardware-profile qualification.
- **Disposition:** **Retain.** Preserve ordinary Arduino/ESP-IDF GPIO
  direction, read, and write services for surviving P4 drivers. Concrete pin
  assignments, electrical behavior, pin multiplexing, and source selection
  remain owned by explicit hardware profiles and subsystem decisions; this
  does not retain any omitted upstream consumer.

#### W1C-Q02 — SPI platform services

- **Status:** Accepted — Retain (2026-08-22)
- **Candidate:** `peripheral-spi-services`
- **Question:** Retain ESP-IDF's P4 SPI master substrate independently of the
  upstream device and storage code that may use it?
- **Recommendation:** **Retain.** The MCP23S17 consumer remains omitted; Work
  1.h separately decides whether upstream FileBrowser SD-card behavior
  survives. Keeping the standard platform API does not compile or activate
  either consumer.
- **Alternatives/tradeoffs:** Omission prematurely removes possible P4 SD and
  project-owned expansion support; replacement reinvents a normal ESP-IDF
  service. Retaining inherited devices would wrongly conflate API availability
  with source selection.
- **Downstream effect:** Work 1.h owns SD host, pins, DMA, mounting, and
  filesystem behavior; PORT-002 records each consumer's build selection.
- **Disposition:** **Retain.** Preserve ESP-IDF's P4 SPI master substrate while
  selecting every concrete consumer independently. MCP23S17 remains omitted;
  Work 1.h owns the upstream FileBrowser/SD decision, and future project-owned
  devices require their own hardware profile and qualification.

#### W1C-Q03 — ESP-IDF high-resolution timer

- **Status:** Accepted — Retain (2026-08-22)
- **Candidate:** `timing-idf-high-resolution-service`
- **Question:** Retain `esp_timer` monotonic reads and callback lifecycle for
  surviving utility, display, scene, input, and audio code?
- **Recommendation:** **Retain.** ESP-IDF 5.5.5 supplies the same portable API
  on P4. Each surviving subsystem must still qualify callback latency, jitter,
  and timing assumptions.
- **Alternatives/tradeoffs:** Replacing a standard service adds divergence;
  omission breaks shared timeout/profiling code even if physical mouse and
  audio drivers are excluded.
- **Downstream effect:** Work 1.d–1.f determine concrete consumers and their
  timing qualification.
- **Disposition:** **Retain.** Use ESP-IDF's P4 `esp_timer` monotonic clock and
  callback lifecycle for surviving consumers. Display, audio, input, scene, and
  utility code retain independent obligations to qualify callback latency,
  jitter, pacing, timeout, and scheduling assumptions.

#### W1C-Q04 — CPU clock and cycle-counter utilities

- **Status:** Accepted — Replace as proposed (2026-08-22)
- **Candidate:** `architecture-cpu-clock-and-cycle-counter`
- **Question:** Replace vdp-gl's ESP32/Xtensa clock, APLL, FRC-timer, and cycle-
  counter assumptions with narrow P4-native implementations at the existing
  upstream seams?
- **Recommendation:** **Replace.** Direct retention already fails at an absent
  ESP32 SoC header and cannot be trusted across the Xtensa-to-RISC-V change.
  Omission would break shared timing utilities used by any surviving display or
  audio path.
- **Alternatives/tradeoffs:** Broad vdp-gl refactoring would increase upstream
  merge burden; narrow adapters preserve names and call sites. Exact semantics
  need only match the consumers that Work 1.d and 1.e retain.
- **Downstream effect:** Display/audio surveys establish required frequency,
  resolution, wrap, and latency behavior before implementation and testing.
- **Disposition:** **Replace.** Preserve existing upstream names and call sites
  while supplying narrow P4-native clock, APLL/resource, timer, and cycle-count
  implementations for the consumers retained by Work 1.d and 1.e. Record every
  unavoidable architecture substitution in the dependency graph and local
  compatibility delta; do not broaden it into unrelated vdp-gl refactoring.

Work 1.c is complete. All ten candidate dispositions are accepted, either
directly during this review or through prior accepted architecture. The
refreshed audit passes with no errors, warnings, ambiguous evidence, or
unclassified evidence.

## Work 1.d execution record

The deterministic extraction classified 1,002 scoped display items: 1,000
belong to six candidates and two are explicitly delegated to the updater and
physical-input owners. No item is ambiguous or unclassified. The
[coverage audit](SETUP-004/generated/work-1d/coverage.yaml) passes without
errors or warnings, and all six provisional records appear in the generated
[disposition matrix](SETUP-004/disposition-matrix.md).

The survey found a real semantic/physical split, but not a clean source-file
split:

- `Canvas` and common `BitmappedDisplayController` code own most drawing,
  queue, paint, clipping, geometry, bitmap, sprite, cursor, readback, and
  buffer-swap semantics.
- The five concrete VGA controller classes mix useful stock pixel formats,
  palettes, Copper scanline effects, sprite composition, and frame semantics
  with classic-ESP32 GPIO-matrix, I2S1, DMA-descriptor, and VSync-ISR code.
- Even the common renderer has one direct Xtensa dependency: transformed
  bitmaps executed inside the ISR save and restore coprocessor state with
  `xthal_*` calls. It therefore needs a narrow P4 adaptation even if retained.
- `VGATextController`, `CVBSGenerator`, and `Scene` are compiled only because
  upstream selects the broad vdp-gl source tree. No official VDP v2.16.0
  runtime constructor or application-visible path reaches them.

The P4 target supplies native RGB-LCD and MIPI-DSI facilities. Those are
possible later physical sinks, but the guaranteed initial video sink remains
the network/browser path. This survey therefore treats logical frame
progression, completion, callbacks, Copper effects, and double buffering as
display contracts rather than assuming that physical VGA VSync remains their
only clock.

No firmware, source selection, or build configuration changed during this
survey.

### Work 1.d question register

Resolve these questions one at a time. Work 1.d closes only after W1D-Q01–Q06
are explicitly disposed and the deterministic audit and projections are
refreshed.

#### W1D-Q01 — Official VDP screen facade

- **Status:** Accepted — Retain (2026-08-22)
- **Candidate:** `display-vdp-screen-facade`
- **Question:** Retain the official header-defined screen facade—its global
  Canvas/controller ownership, mode and fallback behavior, dimensions,
  scaling, palettes, Copper lists, frame counter, completion waits, and buffer
  swaps—while narrowly adapting its concrete controller construction for P4?
- **Recommendation:** **Retain.** The accepted VDU surface depends pervasively
  on these names and behaviors, and preserving the upstream source shape is the
  lowest-drift route for future tagged-release updates.
- **Alternatives/tradeoffs:** Replacing the facade creates a second VDP display
  model and broad upstream divergence; omitting it removes nearly all visible
  output. Retaining its stock concrete VGA type literally is impossible, so
  retention expressly permits the narrow binding adaptation decided in Q03.
- **Downstream effect:** Q02 and Q03 must provide compatible Canvas and
  controller seams. `SETUP-005-D002` later qualifies facade ownership across
  operating-mode transitions.
- **Disposition:** **Retain.** Preserve the official screen-facade names,
  placement, global ownership model, mode/fallback behavior, dimensions,
  scaling, palette and Copper state, logical frame counter, completion waits,
  and buffer swaps. Permit only the narrow concrete-controller binding changes
  required by the accepted P4 backend disposition; do not replace the facade
  with a parallel project-owned display model.

#### W1D-Q02 — Canvas and common bitmapped rendering

- **Status:** Accepted — Retain with narrow P4 adaptation (2026-08-22)
- **Candidate:** `display-canvas-common-rendering`
- **Question:** Retain FabGL Canvas and common bitmapped rendering semantics,
  subject to narrow P4 changes where common code assumes execution inside an
  Xtensa VGA ISR?
- **Recommendation:** **Retain.** This is the mature semantic layer beneath the
  accepted text, plot, bitmap, sprite, font, transform, readback, and buffering
  commands. It is the best available seam for avoiding a wholesale graphics
  rewrite.
- **Alternatives/tradeoffs:** Full replacement offers architectural purity but
  sacrifices tested behavior and greatly increases compatibility and
  upstream-merge risk. Literal retention fails on the transformed-bitmap
  `xthal_*` ISR path and would preserve an output-specific scheduling model.
- **Downstream effect:** Q03's replacement backend must implement the abstract
  controller contract and provide task/frame scheduling that preserves visible
  ordering, completion, and refresh semantics.
- **Disposition:** **Retain with narrow P4 adaptation.** Preserve Canvas, the
  abstract bitmapped-controller contract, primitive ordering and queues, paint
  and clipping state, generic geometry, glyph and bitmap operations, sprites,
  cursors, readback, completion, and buffer semantics. Replace only direct
  architecture assumptions such as Xtensa coprocessor-state handling inside
  the old VGA ISR; do not use those adaptations to redesign unrelated common
  rendering code.

#### W1D-Q03 — Concrete VGA controller family

- **Status:** Accepted — Replace (2026-08-22)
- **Candidate:** `display-vga-concrete-controller-family`
- **Question:** Replace the five concrete ESP32 VGA controllers with an
  Extender-owned framebuffer and logical-frame backend, preserving their
  application-visible behavior and reusing separable rendering algorithms
  where practical?
- **Recommendation:** **Replace.** Their physical engine depends on classic
  ESP32 GPIO-matrix/I2S1/DMA/ISR behavior and cannot serve network/browser or
  P4-native local sinks. The replacement must preserve stock mode dimensions,
  palette quantization, Copper scanline effects, sprite composition, readback,
  double buffering, frame progression, waits, callbacks, and failure/fallback
  behavior as closely as practical.
- **Alternatives/tradeoffs:** Porting the old physical VGA engine has no
  selected hardware destination and retains severe architecture coupling;
  omitting the family without replacement breaks all output. Refactoring the
  vendored classes into clean renderer and scanout layers might salvage more
  code but would be broad upstream surgery. A project-owned backend can instead
  preserve the facade and use old algorithms as a behavioral reference.
- **Downstream effect:** Acceptance creates follow-on implementation and
  qualification work for the backend, frame service, network sink, and later
  MIPI sinks. `PORT-002` must distinguish the vendored old controllers from
  whichever sources are actually selected.
- **Disposition:** **Replace.** Provide an Extender-owned concrete
  `BitmappedDisplayController` implementation with framebuffer production and
  logical frame progression independent of any one output sink. Preserve stock
  mode dimensions, palette quantization, Copper scanline effects, sprite
  composition, readback, double buffering, frame waits and counters,
  callbacks, and mode failure/fallback behavior as closely as practical. Reuse
  separable upstream algorithms where that reduces risk, but do not retain the
  classic-ESP32 GPIO-matrix, I2S1, DMA-chain, or VSync-ISR physical engine.

#### W1D-Q04 — Hardware VGA text controller

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `display-vga-text-controller`
- **Question:** Omit `VGATextController` from the Extender build while retaining
  it unchanged in the complete vendored vdp-gl release?
- **Recommendation:** **Omit from build.** Official VDP text uses Canvas over a
  bitmapped controller; no runtime reference reaches this separate hardware
  character-cell VGA implementation.
- **Alternatives/tradeoffs:** Retention ports a second ESP32 I2S1 VGA engine
  with no compatibility benefit. Replacement or stubbing preserves no selected
  interface.
- **Downstream effect:** Source-filter its independent translation unit and let
  `PORT-002` preserve its vendored-but-unselected status and merge relevance.
- **Disposition:** **Omit from the Extender build; retain unchanged in the
  complete vendored vdp-gl release.** Source-filter `vgatextcontroller.cpp` and
  verify that no retained runtime constructor or link edge appears. No stub or
  replacement is required; official VDP text remains implemented through the
  retained Canvas and bitmapped-controller path. `PORT-002` records its
  vendored-but-unselected status and continuing merge visibility.

#### W1D-Q05 — Composite-video generator

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `display-composite-video-generator`
- **Question:** Omit `CVBSGenerator` from the Extender build while retaining it
  unchanged in the complete vendored vdp-gl release?
- **Recommendation:** **Omit from build.** Official VDP never constructs it,
  Extender has selected no composite-video output, and the code is a classic
  ESP32 DAC/I2S0/DMA implementation unrelated to the guaranteed browser path
  or planned MIPI-DSI path.
- **Alternatives/tradeoffs:** Retention spends porting and qualification effort
  on an unused output; replacement invents an unrequested product feature;
  stubbing preserves no runtime surface.
- **Downstream effect:** Source-filter its independent translation unit and
  record it as vendored-but-unselected in `PORT-002`.
- **Disposition:** **Omit from the Extender build; retain unchanged in the
  complete vendored vdp-gl release.** Source-filter `cvbsgenerator.cpp` and
  verify that no retained constructor, callback registration, or link edge
  appears. No stub or replacement is required because composite video is not
  part of the official VDP runtime or the selected Extender output design.
  `PORT-002` preserves its vendored-but-unselected status and merge visibility.

#### W1D-Q06 — FabGL Scene helper

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `display-fabgl-scene-helper`
- **Question:** Omit FabGL `Scene` from the Extender build while retaining it
  unchanged in the complete vendored vdp-gl release?
- **Recommendation:** **Omit from build.** Official VDP sprite commands use
  their own state and `BitmappedDisplayController`; no `Scene` object or start
  call exists in the runtime. Its separate task, mutex, collision callback, and
  sprite scheduler are dead code for the selected firmware.
- **Alternatives/tradeoffs:** Retention is likely source-portable but adds an
  unused concurrency subsystem and can mislead future maintainers about the
  actual sprite path. Shared Sprite/display types remain independently
  retained, so omission does not remove stock sprites.
- **Downstream effect:** Source-filter `scene.cpp` and record the file as
  vendored-but-unselected in `PORT-002`; re-audit before any future Extender
  feature deliberately adopts Scene.
- **Disposition:** **Omit from the Extender build; retain unchanged in the
  complete vendored vdp-gl release.** Source-filter `scene.cpp` while retaining
  the independently required Sprite and display-controller types. No stub or
  replacement is required. `PORT-002` records its vendored-but-unselected
  status; any future feature that deliberately adopts Scene must reopen source
  selection and concurrency qualification.

Work 1.d is complete. All six candidate dispositions completed Author review.
The refreshed audit passes with no errors, warnings, ambiguous evidence, or
unclassified evidence. `PORT-003` owns implementation and qualification of the
accepted replacement display backend; `PORT-002` owns the build-selection and
upstream-merge representation. No firmware, source selection, or build
configuration changed during this survey.

## Work 1.e execution record

The deterministic extraction classified 458 scoped audio items into three
candidates with no ambiguity or unclassified evidence. The
[coverage audit](SETUP-004/generated/work-1e/coverage.yaml) passes without
errors or warnings, and the candidates appear in the generated
[disposition matrix](SETUP-004/disposition-matrix.md).

The source has a usable semantic boundary but not a clean file boundary:

- official VDP header-defined code owns the complete `VDU 23,0,&85` command
  surface, `PACKET_AUDIO` acknowledgements, channel state machines, envelopes,
  buffer-backed samples, and the one-millisecond audio control task;
- vdp-gl owns portable waveform generation, channel attachment, volume, and
  signed eight-bit PCM mixing; and
- the same vdp-gl `soundgen.cpp` and `soundgen.h` also embed classic-ESP32
  I2S0-register, built-in-DAC, legacy-DMA, sigma-delta, timer, ISR, fixed-pin,
  and VGA/CVBS output-selection code.

ESP32-P4 supports modern I2S and SDM peripherals but not the classic ESP32
built-in DAC used by the upstream backend. More importantly, Rev 1 selects no
local P4 audio transducer: its guaranteed EDP-generated audio destination is
the network/browser path. Therefore the whole `soundgen.cpp` translation unit
cannot simply be source-filtered. The retained waveform/mixer behavior needs a
narrow PCM production seam, while the old physical methods and their headers
must be conditioned out or replaced on the P4 path. Optional forwarding to the
onboard VDP remains separately unresolved as `SETUP-005-D005` and does not
alter this analysis.

No firmware, source selection, or build configuration changed during this
survey.

### Work 1.e question register

Resolve these questions one at a time. Work 1.e closes only after W1E-Q01–Q03
are explicitly disposed and the deterministic audit and projections are
refreshed.

#### W1E-Q01 — Official VDP audio runtime

- **Status:** Accepted — Retain (2026-08-22)
- **Candidate:** `audio-vdp-command-and-channel-runtime`
- **Question:** Retain the official header-defined audio parser, status-packet,
  channel, envelope, sample, playback-timing, and audio-control-task runtime,
  adapting only its direct `fabgl::SoundGenerator` binding?
- **Recommendation:** **Retain.** The accepted VDU inventory keeps every audio
  command, and this code owns their application-visible state, success/failure
  results, `PACKET_AUDIO` acknowledgements, VDU 7 behavior, and buffer-backed
  samples. Preserving it also minimizes tagged-upstream merge divergence.
- **Alternatives/tradeoffs:** Replacement would rewrite the complete mature
  audio service and create a second behavior model; omission contradicts the
  accepted command surface. Literal retention without an output seam cannot
  compile or run correctly because it constructs the fused upstream hardware
  backend.
- **Downstream effect:** Q02 must preserve the waveform/mixer contract used by
  `AudioChannel`. `SETUP-005-D005` independently decides whether any mode also
  forwards audio commands to the onboard VDP.
- **Disposition:** **Retain.** Preserve the official parser, status packets,
  channel state, envelopes, samples, playback timing, audio-control task, and
  VDU 7 behavior. Permit only the bounded `fabgl::SoundGenerator` binding
  adaptation required by Q02 and Q03; do not replace the official audio model.

#### W1E-Q02 — Waveform and PCM mixer core

- **Status:** Accepted — Retain with narrow P4 adaptation (2026-08-22)
- **Candidate:** `audio-waveform-and-mixer-core`
- **Question:** Retain vdp-gl's waveform generators, channel attachment and
  lifetime rules, sample-rate propagation, volume behavior, and signed
  eight-bit PCM mixer, with a narrow adaptation that exposes mixed samples to
  an Extender-owned scheduler/sink?
- **Recommendation:** **Retain with narrow P4 adaptation.** These are the
  mature synthesis semantics beneath the accepted commands. The natural seam
  is `SoundGenerator::getSample()`, presently private and consumed only by the
  stock DAC ISR, sigma-delta timer, or host SDL callback.
- **Alternatives/tradeoffs:** Replacing the mixer permits a cleaner design but
  adds major compatibility and qualification burden; literal retention keeps
  incompatible physical members and callbacks fused into the class; omission
  forces a complete synthesis rewrite.
- **Downstream effect:** Q03 supplies sample scheduling and delivery. PCM
  format conversion, buffering, and network transport are implementation and
  Work 1.g concerns, not reasons to alter waveform semantics now.
- **Disposition:** **Retain with narrow P4 adaptation.** Preserve waveform
  generation, channel attachment and lifetime, sample-rate propagation,
  volume behavior, and signed eight-bit PCM mixing. Create only the bounded
  PCM pull/sink seam needed by an Extender-owned scheduler; do not redesign the
  synthesis model.

#### W1E-Q03 — Physical output and sample scheduler

- **Status:** Accepted — Replace as specified (2026-08-22)
- **Candidate:** `audio-classic-esp32-physical-output`
- **Question:** Replace FabGL's classic-ESP32 DAC/sigma-delta output and sample
  scheduler with an Extender-owned PCM scheduler/sink service, omitting the old
  physical methods from the P4 build path and making network/browser delivery
  the guaranteed Rev 1 sink?
- **Recommendation:** **Replace.** The old code directly programs classic
  ESP32 I2S0, built-in DAC, legacy DMA descriptors, fixed pins, and a
  display-mode-dependent output choice. None matches the P4 target or selected
  Rev 1 hardware, while output scheduling and audible delivery remain required
  behavior.
- **Alternatives/tradeoffs:** Porting to P4 SDM or I2S would invent an
  unselected local-audio feature; omitting all scheduling leaves retained
  synthesis with no consumer; stubbing would acknowledge commands without
  producing promised browser audio.
- **Downstream effect:** Work 1.g must qualify network transport, buffering,
  backpressure, latency, and browser delivery. `SETUP-005-D005` may later add
  onboard-VDP forwarding but does not restore or require the stock P4-local
  backend.
- **Disposition:** **Replace as specified.** Preserve no old DAC, sigma-delta,
  fixed-pin, DMA, ISR, display-mode-selection, or SDL target path in the P4
  build; retain the vendored source for upstream comparison and expose the Q02
  mixer through a project-owned scheduler/sink seam. The scheduler must advance
  logical playback at the selected sample rate independently of sink latency,
  backpressure, or availability: a disconnected or slow browser must not block
  VDU processing, delay logical note completion, or change channel status.
  Output may drop or resynchronize when delivery cannot keep pace. Rev 1
  guarantees software/protocol compatibility and network/browser audio, not
  stock analog-output location or exact analog characteristics.

Work 1.e is complete. All three candidate dispositions completed Author
review. The refreshed audit passes with no errors, warnings, ambiguity, or
unclassified evidence. `PORT-004` owns implementation and qualification of the
accepted PCM scheduler and initial network/browser sink; `PORT-002` owns the
vendored-versus-selected representation. Optional onboard-VDP audio forwarding
remains open under `SETUP-005-D005`. No firmware, source selection, or build
configuration changed during this survey.

## Work 1.f execution record

The deterministic extraction classified 521 scoped keyboard/mouse items into
four candidates with no ambiguity or unclassified evidence. The
[coverage audit](SETUP-004/generated/work-1f/coverage.yaml) passes without
errors or warnings, and all candidates appear in the generated
[disposition matrix](SETUP-004/disposition-matrix.md).

The source confirms that physical PS/2 acquisition and compatibility-visible
input behavior are conceptually separable but heavily coupled in code:

- `agon_ps2.h`, `vdu_sys.h`, and `vdu_stream_processor.h` combine command
  parsing, VDP variables, packets, callbacks, control-key and paged-mode
  behavior, mouse cursor state, and custom cursor bitmaps with direct global
  FabGL `Keyboard`, `Mouse`, and `PS2Controller` calls;
- vdp-gl `keyboard.cpp` and `kbdlayouts.cpp` reset a physical device, translate
  scan codes, own locale tables, maintain key state and LEDs, and run a
  conversion task;
- vdp-gl `mouse.cpp` decodes physical packets, runs a mouse task, applies
  acceleration, owns absolute-position queues, and can update the display
  controller directly; and
- `ps2controller.cpp` is the already-excluded classic-ESP32 ULP/RTC-GPIO/SENS
  physical backend that caused the P4 preprocessing failure.

The proof of concept leaves scan-code and mouse-packet processing with the
onboard VDP. An EDU-aware eZ80 application reads that stock input and explicitly
forwards the processed events to Extender when it needs EDP-local control-key,
paged-mode, logical-position, callback, or cursor behavior. The proposed seam
is therefore a project-owned input-injection adapter, not a P4 port of the
physical device engines and not yet a transparent compatibility route. A v1
implementation may deliver more automatic routing; that remains open under
`SETUP-005-D007`. V1 will not add its own keyboard, mouse, or other peripheral
hardware beyond facilities already present on the selected P4 DevKit.

No firmware, source selection, or build configuration changed during this
survey.

### Work 1.f question register

Resolve W1F-Q01–Q03 one at a time. The physical PS/2 controller disposition is
already accepted by ADR-0013 and Work 1.c. Work 1.f closes only after the three
remaining questions are explicitly disposed and the deterministic audit and
projections are refreshed.

#### W1F-Q01 — Official input compatibility integration

- **Status:** Accepted — Replace as revised (2026-08-22)
- **Candidate:** `input-official-compatibility-integration`
- **Question:** Replace the direct FabGL keyboard/mouse bindings inside the
  official integration with a project-owned processed-event injection adapter,
  initially fed explicitly by EDU-aware eZ80 applications, while preserving the
  official packets, callbacks, VDP variables, control-key and paged-mode
  behavior, logical mouse state, and cursor effects when events are supplied?
- **Recommendation:** **Replace.** The proof of concept needs an explicit EDU
  input-injection path, not transparent routing. Literal retention starts the
  excluded physical PS/2 stack and cannot consume application-forwarded events.
  A narrow adapter preserves useful official behavior and source shape while
  changing the event source beneath it. Injected events should update EDP-local
  input variables, callbacks, control-key/paged-mode logic, mouse position, and
  cursor effects, but should not automatically emit `PACKET_KEYCODE` or
  `PACKET_MOUSE` back to the eZ80 that just forwarded them; later compatibility
  profiles may enable packet emission through an explicit routing policy.
- **Alternatives/tradeoffs:** Retaining the bindings contradicts accepted
  hardware ownership and fails on P4; omission breaks legacy-visible behavior;
  a broad rewrite creates unnecessary divergence. Aware-application forwarding
  is sufficient for the proof of concept; any more automatic v1 route remains
  a separate `SETUP-005-D007` decision. Automatic packet echo risks duplicate
  input or a forwarding loop.
- **Downstream effect:** Q02 and Q03 may exclude the physical keyboard and mouse
  engines only after this adapter satisfies their official consumers. Display
  cursor rendering remains owned by Work 1.d.
- **Disposition:** **Replace** the direct device-object bindings with
  a narrow processed-event injection adapter. The proof-of-concept source is an
  EDU-aware application that reads stock VDP input and forwards it explicitly.
  Preserve official event, packet, callback, state, control-key, paged-mode, and
  cursor semantics for later profiles, but update only EDP-local state and
  behavior by default in the proof of concept; do not echo injected input or
  presume transparent routing.

#### W1F-Q02 — Keyboard device and layout engine

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `input-vdp-gl-keyboard-and-layout`
- **Question:** Omit vdp-gl's physical keyboard device, scan-code conversion
  task, layout engine, typematic/LED device control, and compiled locale tables
  from the P4 build, while retaining only stable virtual-key/event vocabulary
  needed by the Q01 adapter?
- **Recommendation:** **Omit from build; retain in the vendor tree.** The
  onboard VDP already produces processed key events and owns physical locale,
  repeat, LED, and key-state behavior. Extender should route the corresponding
  commands rather than decode the same keyboard independently.
- **Alternatives/tradeoffs:** Retention duplicates physical state and tasks and
  still depends on the omitted controller; replacement is unnecessary unless a
  future P4-owned input feature is selected. Shared type declarations may
  remain without selecting the implementation translation units.
- **Downstream effect:** `SETUP-005-D007` must define locale, repeat, LED, and
  check-key routing and event delivery. `PORT-002` records the implementation as
  vendored but excluded.
- **Disposition:** **Omit from the P4 build; retain unchanged in the
  vendor tree**, preserving only shared type/wire vocabulary required by the
  compatibility adapter.

#### W1F-Q03 — Mouse device and positioning engine

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `input-vdp-gl-mouse-device`
- **Question:** Omit vdp-gl's physical mouse device, packet decoder, task,
  queues, acceleration, and direct display-positioning engine from the P4
  build, with processed onboard-VDP mouse fields and EDP-local cursor effects
  handled by the Q01 adapter?
- **Recommendation:** **Omit from build; retain in the vendor tree.** The
  onboard VDP already performs device negotiation, packet decoding, sampling,
  scaling, and acceleration. Repeating those stages on processed data would be
  incorrect as well as unnecessary.
- **Alternatives/tradeoffs:** Retention duplicates physical processing and
  depends on the omitted controller; replacement as a physical engine invents
  unselected P4 mouse hardware. Logical position, packets, callbacks, command
  consumption, and cursor rendering are preserved through Q01 and Work 1.d.
- **Downstream effect:** `SETUP-005-D007` must define mouse-command forwarding,
  event ordering, coordinate synchronization, and mode behavior. `PORT-002`
  records the implementation as vendored but excluded.
- **Disposition:** **Omit from the P4 build; retain unchanged in the
  vendor tree**, replacing its official consumers with the processed-event and
  logical-state adapter from Q01.

Work 1.f is complete. All four candidate dispositions are accepted, including
the physical PS/2 controller omission inherited from ADR-0013 and Work 1.c. The
refreshed audit passes with no errors, warnings, ambiguity, or unclassified
evidence. `PORT-005` owns implementation and qualification of the
proof-of-concept processed-input injection adapter; `PORT-002` owns the
vendored-versus-selected representation. Any more automatic v1 route remains
open under `SETUP-005-D007`. No firmware, source selection, or build
configuration changed during this survey.

## Work 1.g execution record

The deterministic extraction currently classifies 353 scoped network,
updater, and transfer evidence items: 311 belong to two candidates and 42 are
explicitly delegated to already-decided updater/runtime boundaries. No item is
ambiguous or unclassified. Targeted source review confirms that official VDP
v2.16.0 contains no active network service: its top-level `WiFi.h` include is
unused, while vdp-gl's independently compiled ICMP helper has no VDP consumer.
Ethernet initialization, browser media delivery, and a network update service
are therefore project-owned work rather than upstream code dispositions.

The stock updater is not reopened here. Work 1.a already accepted retention of
the ESP-IDF OTA/restart primitives and omission of the defective stock serial
updater transaction. Likewise, ADR-0014 already accepts omission of the coupled
Intel HEX/YMODEM UART maintenance subsystem; `SETUP-005-D006` retains the
unresolved mode-specific parser and failure behavior.

### Work 1.g question register

#### W1G-Q01 — Dormant vdp-gl ICMP helper

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `network-vdp-gl-icmp-helper`
- **Question:** Omit vdp-gl's independently compiled, otherwise unreferenced
  `ICMP.cpp` helper from the P4 build while retaining its source unchanged in
  the pinned vendor tree?
- **Recommendation:** **Omit from build; retain vendor source.** It exposes no
  official VDP behavior, has no inbound runtime consumer, and binds hostname
  lookup directly to Arduino `WiFiGenericClass` although Extender Rev 1 uses
  wired Ethernet. A future ping diagnostic should use the project-owned network
  abstraction rather than make this dormant helper part of the port contract.
- **Alternatives/tradeoffs:** Retaining it carries unused WiFi/raw-lwIP coupling
  and future qualification burden. Replacing it now invents an unrequested
  diagnostic feature. Defer would leave a known, independently removable
  translation unit in the selected build without an unresolved product need.
- **Downstream effect:** `PORT-002` records the source exclusion and future
  tagged vdp-gl imports re-audit inbound references. `PORT-003` and `PORT-004`
  must not depend on this helper for browser video or audio.
- **Disposition:** **Omit from the P4 build; retain unchanged in the vendor
  tree.** The optional Rev 1 MOD-WIFI-ESP8266 add-on remains a required network
  backend consideration, but it is a separate processor reached through the
  dedicated-header host protocol. It does not expose the P4-local
  `WiFiGenericClass`/raw-lwIP environment assumed by this helper.

Work 1.g is complete. Both candidate dispositions are accepted: the dormant
vdp-gl ICMP translation unit is vendored but excluded, and the stock Intel
HEX/YMODEM maintenance subsystem inherits ADR-0014's omission. Work 1.a's
accepted OTA/restart substrate and stock-updater omission remain unchanged.
`PORT-006` owns the project network foundation, wired-Ethernet service, optional
MOD-WIFI-ESP8266 backend, and network update-service implementation; `PORT-002`
owns source-selection representation. No firmware, source selection, or build
configuration changed during this survey.

## Work 1.h execution record

The deterministic extraction currently classifies 139 scoped storage and
filesystem evidence items into two candidates with no exclusions, ambiguity,
or unclassified evidence. Official VDP v2.16.0 has no storage startup, VDU
command, response packet, callback, or runtime consumer. The only upstream
facility is vdp-gl `FileBrowser`, compiled incidentally inside `fabutils.cpp`.

The source boundary is fused: `fabutils.cpp` also supplies retained timing,
geometry, container, memory, and display utilities, so the translation unit
cannot be excluded. Its dormant FileBrowser region combines generic POSIX-like
operations with SPIFFS-specific directory simulation, two hard-coded drive
types, old SDSPI mounting, classic-chip pin overrides, a fixed host/DMA policy,
FAT formatting, and an ESP-IDF 4-era watchdog call that is incompatible with
the selected ESP-IDF 5.5.5 API.

Extender nevertheless requires the P4 DevKit microSD card as a v1 project
capability, deferred beyond the first beta. This requirement does not imply a
file browser. Olimex publishes a board-specific ESP-IDF SDMMC example derived
from Espressif's maintained P4 example; that current, proven P4 lineage is the
implementation baseline rather than vdp-gl's classic-ESP32 backend. The Agon
main board and MOS remain sole owners of the Agon card, which Extender can
access only through a later filesystem RPC service. Network protocols consume
storage services but do not define their local filesystem implementation.

### Work 1.h question register

#### W1H-Q01 — Upstream FileBrowser API and generic operations

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `storage-vdp-gl-filebrowser-api`
- **Question:** Omit the unused vdp-gl `FileBrowser` API and implementation,
  retaining the complete upstream source for provenance but excluding its
  bounded FileBrowser region from the P4 build?
- **Recommendation:** **Omit.** Extender does not presently require a file
  browser, and no stock VDP behavior or selected vdp-gl consumer requires this
  class. Adopting it would unnecessarily freeze raw-allocation, weak-error,
  SPIFFS-directory, two-drive, and global-mount assumptions into our
  architecture. The required v1 P4-card capability is a separate concern and
  does not require a replacement FileBrowser API.
- **Alternatives/tradeoffs:** Retain and adapt saves a modest amount of code but
  creates a permanent upstream-shaped storage contract with no compatibility
  benefit. Deferral preserves an unnecessary coupling and prevents clean
  separation of the fused physical backend.
- **Disposition:** **Omit from build; retain in vendor tree.** No replacement
  browser or generic file-service API is selected. A later feature may define
  one when concrete consumers justify it.
- **Downstream effect:** W1H-Q02 can dispose the physical backend without
  preserving FileBrowser signatures. `PORT-002` must represent a region-level
  exclusion inside retained `fabutils.cpp`; v1 P4-card implementation receives
  separate follow-on work.

#### W1H-Q02 — Classic ESP32 mount and format backend

- **Status:** Accepted — Omit from build; retain in vendor tree (2026-08-22)
- **Candidate:** `storage-vdp-gl-esp32-mount-format-backends`
- **Question:** Omit the classic ESP32 SDSPI/SPIFFS backend from the P4 build
  and implement the required v1 DevKit-card capability separately from current
  proven Olimex/Espressif P4 SDMMC code?
- **Recommendation:** **Omit from build; retain in the vendor tree.** Olimex
  already publishes a DevKit-specific ESP-IDF SDMMC demo using the maintained
  P4 stack, four-line bus configuration, internal-LDO setup, FAT/VFS mounting,
  and POSIX file operations. The old backend is neither a faithful board
  description nor a safe storage policy, and calling it a replacement seam
  would unnecessarily couple the new feature to dormant FabGL code.
- **Alternatives/tradeoffs:** Adapting the old backend saves little and carries
  classic-chip pin, SDSPI host/DMA, watchdog, workaround, and automatic-format
  assumptions. Deferral leaves a known incompatible region in the selected
  source boundary. Selecting the proven P4 path still requires production
  lifecycle design and hardware qualification.
- **Disposition:** **Omit from build; retain in vendor tree.** Implement no
  compatibility stub or FabGL-shaped replacement. `PORT-007` owns the separate
  v1 P4 DevKit microSD capability.
- **Downstream effect:** A follow-on storage task must determine exact card
  wiring and power configuration from the Olimex design, mount lifecycle,
  namespaces, concurrency, hot removal, write durability, capacity reporting,
  and explicitly authorized formatting. `PORT-007` targets v1 after the first
  beta; no file browser is implied. `PORT-002` records the old backend as
  vendored but excluded.

Work 1.h is complete. Both dormant vdp-gl storage regions are accepted as
**Omit from build; retain in vendor tree**. The passing inventory remains 139
scoped items in two candidates with no errors, warnings, ambiguity, or
unclassified evidence. `PORT-007` owns the independent v1 P4 DevKit microSD
implementation; no firmware, source selection, or build configuration changed
during this survey.

## Review gate

Stop after producing and explaining the provisional disposition matrix. Do not
alter source selection, add stubs, or modify VDP/vdp-gl code until the Author
has reviewed the affected subsystem group.
