# Agon Extender Architecture

This document describes the current accepted architecture. Open questions and
implementation work belong in `TODO.md` and the corresponding tracked files
under `docs/tasks/` rather than here.

## Browser-video default encoding

RLE2 is the accepted default for browser video output. It compresses complete
supported frames; raw compatibility and explicit test overrides remain available.
See [ADR-0021](decisions/ADR-0021-rle2-browser-default.md) and the
[browser-video contract](protocols/browser-video.md). Encoding choice does not
change the separately accepted output pacing policy.

## Web-output cadence

The accepted512×384 web-output contract is30 complete frames/s. Normal test
fixtures must cap snapshot/output admission at30fps, independently of native
rendering and application cadence. See [browser-video contract](protocols/browser-video.md)
and [ADR-0020](decisions/ADR-0020-web-output-30fps.md). This target still needs
representative production/browser qualification; it is not a blanket measured guarantee.

## VDP firmware lineage

Agon Extender's VDP firmware begins as a faithful port of the official Agon VDP
to the ESP32-P4. Full backward compatibility with existing Agon software is a
product requirement.

The port preserves official directory names, filenames, relative source
locations, and recognizable code wherever the target permits. P4-specific
changes should be narrow and explicit so maintainers can compare the port with
upstream and incorporate future official changes without reconstructing
equivalent modules under unrelated names.

## Repository layout

The complete PlatformIO project and VDP firmware live under the repository's
top-level `vdp/` directory. Within that project, `vdp/video/` mirrors the
official VDP source directory.

New Extender capabilities and extended functions live under:

```text
vdp/video/extender/
```

This location is inside the firmware source directory selected by the official
PlatformIO project while retaining a clear ownership boundary. Existing
upstream files remain at their official relative paths. Calls between the
upstream-shaped compatibility port and Extender-owned modules must use narrow,
documented integration points.

The rationale and consequences of this placement are recorded in
[ADR-0001](decisions/ADR-0001-vdp-source-layout.md).

## Change boundaries

The upstream-shaped compatibility port owns stock VDP behavior. The
`video/extender/` subtree owns capabilities that do not exist in the official
firmware.

Target adaptation should follow this preference order:

1. retain upstream code unchanged;
2. isolate board or architecture differences in target-specific support code;
3. use a small conditional or insertion point in an upstream-shaped file when
   isolation is impractical; and
4. replace an upstream implementation only when the P4 target makes the
   original mechanism unavailable.

Every deviation from upstream should remain attributable to a verified target
requirement or an accepted Extender feature.

The official header-defined screen facade remains the display integration
boundary for the port. Preserve its global Canvas/controller ownership, mode
selection and fallback, logical dimensions and scaling, palette and Copper
state, logical frame counter, completion waits, and buffer swaps. P4 display
work may narrowly adapt the concrete controller created behind that facade; it
must not replace the facade with an unrelated project-owned display model.

FabGL `Canvas` and the common bitmapped rendering layer remain the semantic
implementation beneath that facade. Preserve their primitive ordering and
queues, paint and clipping state, geometry, glyph and bitmap operations,
sprites, cursors, readback, completion, and buffering contracts. Direct
assumptions about the old Xtensa VGA-ISR environment may receive narrow P4
adaptations; those changes do not authorize unrelated renderer redesign.

The original VGA2/4/8/16/64 concrete controller family is retained behind a
narrow P4 processor/output binding. It produces native framebuffer state and
logical frame progression independently of any one physical output sink, so
the guaranteed network/browser path and later P4-native local displays consume
one rendering model. Preserve stock mode dimensions, palette quantization,
Copper scanline effects, sprite composition, readback, double buffering, frame
waits and counters, callbacks, and mode failure/fallback behavior as closely as
practical. The old GPIO-matrix, I2S1, DMA-chain, and VSync-ISR engine remains
vendored reference material, not the P4 physical backend.

The video backend preserves stock framebuffer formats, memory organization,
row access, rendering algorithms and fast paths as faithfully as possible.
Reuse upstream code exactly wherever processor facilities and video-output
interfaces permit it, including portable code within the old concrete VGA
classes. Differences require a specific evidenced processor/output dependency;
generic abstractions, browser serialization and an existing project design do
not by themselves justify replacement.

The current generic controller, project pixel codecs and flat logical planes
are implementation choices subject to that rule, not mandatory architecture.
Retain stock native packing, palette/Copper behavior, bitmap save/readback,
sprites, cursors, buffering, completion and mode contracts. Contiguous allocation
may coexist with a logical row-pointer table. Browser and later local-display
adapters produce their required output representation at the output boundary;
they do not require the drawing framebuffer to share that representation.
ADR-0013 and ADR-0015 record the Author's fidelity direction. The accepted
AUDIT-006 comparison selects original depth classes with narrow P4 bindings;
PORT-003 owns implementation. First-pass restoration preserves compilable
upstream behavior unchanged, including suspected bugs; fixes are deferred.
Stock lane ordering and inert sync bytes may remain in native storage, with
normalization confined to the output boundary.

A periodic P4 logical frame clock and frame-service task advance official VDP
time independently of every output sink. P4 preserves queued primitive
execution through the unchanged common controller, logical frame progression
and presentation publication, while maintaining stock's separation between
drawing progress and periodic display progression. Frame counting/output
opportunities must not wait for a continuously replenished drawing queue to
empty. Physical sink callbacks may recycle sink buffers
but do not advance the VDP frame counter or unblock logical swaps.
On a service opportunity, P4 drains queued drawing in FIFO order until empty
or suspended, matching stock VDP's background worker with its timeout disabled.
No fixed primitive-count or elapsed-time cap throttles this drain. Suspension
is checked between primitive executions; immediate flush and double-buffered
drawing/swap contracts remain unchanged.

For the original-controller P4 binding, browser row preparation may wait for
one drawing primitive under PORT-003-R2-D001. Native drawing is excluded only
during one row preparation, and all metadata/lifetime owners share the same
exclusion protocol. This output compromise was accepted with reservation:
stock's reliable 60 Hz cadence remains the reference. The frame-clock path
takes no native-state lock and does not wait for drawing, output preparation,
network delivery or a free snapshot slot. Qualification distinguishes actual
clock jitter from delayed browser presentation. A full queue drain or full
frame copy is not an allowed exclusion boundary.

The retained common renderer preserves pinned upstream bodies for
queue submission, completion waits, background draining, dynamic payloads, and
swap notification. The P4 controller replaces only the unavailable physical
frame executor through existing protected seams. Narrow native-state guards
at execution/lifetime boundaries implement the accepted P4 CPU-reader binding;
they do not change drawing algorithms or add upstream bug fixes. In particular, strict
compatibility retains upstream queue-depth completion behavior even though a
separate A/B research task may evaluate stronger semantics for an upstream
contribution.

Generalized callbacks are a production EDP capability, giving applications a
documented return path for EDP events, results and state information. This
supports meaningful interaction beyond submitting display commands. EMOS
retains transport and application mediation under the EDU service contract.
Render completion and the graphics benchmark are initial use cases within the
broader facility. Rendering completion remains distinct from output-sink
presentation, and the retained stock VDU completion contract still applies.
Pingo's mainboard-tested callback supplies a precedent without prescribing the
general callback mechanism or ABI. See
[ADR-0017](decisions/ADR-0017-generalized-edp-callbacks.md).

One shared output path reuses stock per-depth packed row expansion, palette
tables, Copper traversal and sprite/cursor decoration without changing
logical framebuffer state or readback. Network/browser and later local-display
sinks receive fixed-capacity latest-generation mailboxes through a common
consumer contract. The frame service never invokes sink code; sinks poll from
their own tasks. Slow sinks may drop reported presentation generations; they
must not block rendering, grow an unbounded queue, or redefine logical frame
timing. See
[ADR-0015](decisions/ADR-0015-p4-display-backend-and-frame-service.md).

The separate FabGL `VGATextController` is retained in the complete vendored
vdp-gl source but excluded from Extender builds. Official VDP text remains on
the retained Canvas/bitmapped-controller path, so the unused hardware
character-cell VGA driver receives neither a P4 port nor a compatibility stub.

FabGL `CVBSGenerator` likewise remains in the complete vendored vdp-gl source
but is excluded from Extender builds. Composite video is neither part of the
official VDP runtime nor a selected Extender output, so its classic-ESP32
DAC/I2S0/DMA implementation receives no P4 replacement or stub.

FabGL `Scene` also remains vendored but is excluded from Extender builds.
Official VDP sprites retain their own state and bitmapped-controller path;
shared Sprite/display types survive independently. No Scene task, mutex,
collision callback, or parallel sprite scheduler is selected unless a future
Extender feature adopts it explicitly.

The official header-defined VDP audio runtime remains the audio integration
boundary. Preserve its parser, `PACKET_AUDIO` acknowledgements, channel state,
envelopes, buffer-backed samples, playback timing, audio-control task, and VDU
7 behavior. P4 audio work may narrowly adapt its direct
`fabgl::SoundGenerator` binding to the selected synthesis and output service;
it must not replace the official runtime with a separate audio model.

The vdp-gl waveform and mixer core remains the synthesis layer beneath that
runtime. Preserve waveform generation, channel attachment and lifetime,
sample-rate propagation, channel and global volume behavior, and signed
eight-bit PCM mixing. A narrow P4 adaptation may expose mixed samples to an
Extender-owned scheduler or sink; output backends must not create independent
synthesis semantics.

An Extender-owned PCM scheduler and sink service replaces FabGL's
classic-ESP32 DAC, sigma-delta, I2S0-register, legacy-DMA, fixed-pin, ISR/timer,
and display-mode-selected output machinery. Those physical paths remain in the
complete vendored source but are excluded from the P4 build. Network/browser
audio is the guaranteed Rev 1 sink; Rev 1 does not promise the stock analog
output location or exact analog characteristics.

Logical audio playback runs from the selected sample clock independently of
sink latency, backpressure, or availability. A disconnected or slow browser
must not block VDU processing, delay logical note completion, or alter channel
status; delivery may drop or resynchronize instead. Optional forwarding to the
onboard VDP for local playback remains a separate operating-mode decision.

The dormant vdp-gl `FileBrowser` remains in the complete vendored source but is
excluded from Extender builds. Extender does not presently select a file-browser
API, and required local storage does not imply one. The P4 DevKit microSD card
is a required v1 capability deferred beyond the first beta; its implementation
will follow maintained Olimex/Espressif P4 SDMMC reference code and a
project-owned lifecycle rather than FabGL's classic-ESP32 storage backend.
EDP owns this physical card and its filesystem service. EMOS must be able to
request file reads and receive data from that service through its owned
Extender transport; the P4 card is distinct from the Agon's own SD card.
PORT-007 owns the EMOS interface and storage integration.
Future installed-application, media, network-file, or browser interfaces consume
that storage capability without defining its physical backend.

## Hardware design target

[`light2-harness-r01`](../hardware/designs/light2-harness-r01/README.md) is the
preserved predecessor harness and historical forward-prototype target. It
preserves the physically exercised eight-bit forward-bus pin map, installed-
view routing geometry, series resistance, and control-signal evidence. It is
not the V1 common-UART electrical design and must not be promoted by relabeling
or incremental modification.

[`light2-harness-r02`](../hardware/designs/light2-harness-r02/README.md) is the
frozen controlled-beta candidate and provisional V1 transport core. It uses two
Agon-powered `SN74LVC244AN` forward buffers, one Agon-powered `SN74LV125AN`
UART-return buffer, and one P4-powered `SN74LV125AN` as four low-only isolated
control sinks. It provides one common eZ80 UART1 TX/RX/RTS/CTS circuit for both
exclusive modes and retains one-way `D0..D7`, `CLOCK`, `VALID_N`, and
`READY_N` for Exclusive Extended. Positive 3.3 V rails remain separate and all
cross-board drivers default disabled. R1--R13 are frozen at 220 ohms for this
candidate. See
[ADR-0016](decisions/ADR-0016-v1-transport-electrical-core.md).

This selection does not qualify target-speed UART, reset recovery, Legacy
electrical absence, construction, or Console8 adaptation. HW-001 owns those
remaining design and evidence gates before the topology can become a released
V1 hardware artifact.

R02 is the retained candidate design; its design work, construction, and
validation are on hold by Author direction as of 2026-09-07. Full-circuit
wiring is incomplete and the complete circuit is untested. The following
process description does not authorize resuming work. Its
connectivity model owns the circuit, its maintained physical schematic guides
construction. Signal views isolate functions for tracing/debugging; a separate
wiring order defines cumulative assemblies suitable for powered tests, including
every required input state and shared-bank dependency. The construction plan
uses permanent circuit parts only; any required electrical addition follows
normal successor-revision approval. Tests use production-candidate P4 and EMOS components where
applicable; scoped diagnostic firmware may isolate measurements such as power
and bias. Evidence authenticates the tested stage and candidate code before
eventual release consumption is compared. The complete product firmware and
unrelated mode decisions are not prerequisites for a mode-neutral circuit
measurement. The accepted
[staged process](qualification/staged-circuit-validation.md) defines these
boundaries without changing EMOS ownership or qualifying untested behavior.

## EDU operating modes and application interface

Project terminology distinguishes the **Extended Display Unit (EDU)** exposed
to eZ80 software from the **Extended Display Processor (EDP)** that implements
it on the ESP32-P4. EDU names the command set, API, and logical facility; EDP
names the processor and its firmware. The terms intentionally parallel Agon's
existing VDU and VDP terminology.

Extender-aware programs address the P4 through an explicit, stable, versioned
EDU API owned by EMOS. Synchronous foreground applications may link a client
binding, but that binding invokes EMOS and does not own the transport,
activation, receiver, or lifecycle. Persistent or asynchronous capabilities may
use an explicitly installed resident facility subordinate to EMOS arbitration.

Optional resident facilities do not independently intercept or redirect
`RST.LIL 10h` or `RST.LIL 18h`; the EMOS mode dispatcher alone owns those VDU
paths. Applications must discover and open EDU deliberately through EMOS. EMOS
owns persistent transport state, interrupt-driven reception, queues, client
arbitration, and mode lifecycle. Extend resident EMOS with ordinary compile-time
linking and clear command/service/interrupt boundaries. The current scope
requires no module loader, runtime relocation or restriction to moslet space.
Keep changes small and upstream-reviewable while preserving the EDU contract.
See
[ADR-0014](decisions/ADR-0014-edu-operating-modes-and-service-architecture.md).

In **Exclusive Compatible mode**, the EDP is the sole compatibility display
processor and uses the stock VDP UART transport contract. It owns the
stock-compatible command and response stream while MOS retains canonical VDP
sysvar storage, completion flags, and the mechanism that updates them. The
selected hardware core provides all four eZ80 UART1 signals independently of
the predecessor split-link harness; its exact firmware behavior and physical
qualification remain under HW-001 and PORT-008.

In **Exclusive Extended mode**, the EDP has the same exclusive compatibility
authority and logical MOS/eZ80 integration reach. Commands may use the
eight-bit forward parallel path; response, control, and fallback traffic uses
the same common four-signal UART circuit as Exclusive Compatible during
separately owned UART epochs. Transport enhancement does not weaken the
compatibility ownership model. Exact enhanced reverse capabilities remain
unresolved.

Both exclusive modes may claim compatibility only for the declared normal
application-facing surface; Extender v1 explicitly excludes local printer/USB
serial, console/terminal, ZDI, Intel HEX, YMODEM, updater, and debug facilities
unless a later accepted decision restores them. EMOS's fixed VDU dispatcher and
committed-backend selection are accepted; exact response delivery, parser
integration, activation-carrier and lifecycle implementation, and qualification
remain unresolved.

Author clarification, 2026-09-19: Firmware-update commands and Intel HEX/YMODEM maintenance are supported only
through the stock mainboard path in Legacy mode for now. The operator selects
Legacy through EMOS before invoking them; EMOS does not silently forward these
commands from ExCom to mainboard VDP. EDP does not implement their update or
transfer operations. Project-owned SD service, P4 deployment and ZDI recovery
remain separate capabilities. This scope decision does not assert that upstream
has retired or superseded these utilities. Accidental delivery to EDP still
requires defined rejection/consumption behaviour; empty handlers are not thereby
qualified as safe.

In **Dual mode**, the onboard VDP remains authoritative for VDU and MOS VDP
sysvars while the EDP is addressed through EDU and retains results in an
EDU-owned state domain. Applications and project-owned abstraction layers may
coordinate both processors, but ordinary application VDU is never mirrored:
Legacy and Dual route it only to the onboard VDP, and both exclusive modes
route it only to the EDP. Targeted private input/bootstrap control, recovery
diagnostics, and separately identified qualification traffic are not mirrored
application output. Competing writes to canonical sysvars remain unsupported.

Separately identified qualification traffic may originate in an SD-loaded
application that submits a bounded request to resident EMOS. EMOS validates
and owns the complete transport transaction; the application does not access
Extender registers, UARTs or routing state. The visible-text diagnostic keeps
ordinary VDU on the onboard VDP while P4 executes the submitted text through
retained EDP. Sample contents are independent of both firmware images. This
implements the diagnostic exception in ADR-0014 and does not constitute an
additional operating mode or ordinary-VDU route.

EMOS is one complete backward-compatible replacement for stock MOS, not a
side-by-side companion. It is the only supported software authority for
ordinary VDU routing, Extender transport ownership, and committed mode.
Applications, linked EDU bindings, TSR-like programs, future MOS Modules, and
optional resident services
request those operations through EMOS and do not install independent hooks or
claim UART/GPIO ownership. The proof-of-concept and v1 contract enforce this
across supported software; they do not attempt adversarial isolation from
deliberate eZ80 machine code with unrestricted register and GPIO access. Such
direct manipulation is unsupported caveat emptor. Project hardware and
software still use fail-safe defaults and bounded activation, but make no
non-bricking guarantee for external code that violates this normative contract.

EMOS is also the sole authoritative source of the current formal operating-mode
name. It derives that name only from committed VDU-route and EDP-service state.
EDP/P4 firmware and applications may report their local condition, requested or
pending targets, readiness, transport state, and failures, but may not describe
an uncommitted, failed, or partial combination as Legacy, Dual, Exclusive
Compatible, or Exclusive Extended.

### Mode lifecycle, transition, and recovery

Formal mode is the committed combination of two EMOS-owned logical planes:
ordinary-VDU routing and EDP service. Only these combinations are valid:

| Formal mode | Committed VDU route | Committed EDP service |
|---|---|---|
| Legacy | onboard VDP | inactive |
| Dual | onboard VDP | active |
| Exclusive Compatible | EDP compatible | active |
| Exclusive Extended | EDP extended | active |

An exclusive route with inactive EDP service is invalid. Keyboard-source
selection is independently retained across mode changes under ADR-0014's
2026-09-08 amendment. Keyboard-only P4 activity does not activate the ordinary
EDP/EDU service plane or imply Dual. EMOS alone derives
and names formal mode from the two committed planes; requested, conditionally
pending, failure, and fallback information belongs to lifecycle state rather
than to a fifth formal mode.

Cold boot first reaches fully operational Legacy. Each explicit late
`autoexec.txt` or manual request permits the EMOS coordinator to make at most
one prepare/readiness/commit/recover attempt. EMOS validates every prerequisite
and initializes the complete target before publishing either plane. On a
missing or incompatible prerequisite, EMOS returns or reports a bounded failure
through an available accepted caller or diagnostic path. Any pre-commit failure
restores the current stable mode with routing unchanged and no partial
publication; this routing-coherence guarantee does not depend on preserving the
initiating program or other processor state. A successful presence/version
probe activates EDP and commits Dual; a failed probe leaves Legacy. Exclusive
entry likewise begins in Legacy. Legacy is the mandatory transition hub: EMOS
commits Legacy before attempting a different non-Legacy destination, and no
direct non-Legacy-to-non-Legacy transition is contracted. Live Legacy-to-Dual
and Dual-to-Legacy activation is accepted; an ordinary-VDU route change may
instead use the disruptive transition described below.

Extender v1 uses pull discovery and defines no proactive EDP presence signal.
EMOS selects a reviewed transport/wiring profile, arms the eZ80 receiver, sends
the request, validates the EDP identity, protocol, and capabilities, and alone
commits mode. That handshake establishes protocol readiness; QUAL-002 remains
the authority for electrical and power/reset qualification. EDP asynchronous
traffic requires a negotiated and armed post-activation receiver. P4 reset
revokes that permission, and EMOS quarantines stale traffic.

EMOS uses one fixed set of reset-vector and C-runtime output handlers and one
semantic VDU dispatcher. Each active invocation retains a snapshot of one
committed backend. To change that backend, the EMOS coordinator blocks new
invocations, waits for active calls and owned response work to finish or be
abandoned, reinitializes affected parser state, and commits atomically. The beta
adds no second semantic VDU parser and does not preserve multi-call partial
commands across a disruptive transition.

The first idle-console Legacy↔Exclusive Compatible increment may switch
without rebooting, as accepted in PORT-008-D005. EMOS preserves keyboard
source/layout and presents a fresh destination screen/prompt. It retains
transactional readiness, parser/queue quiescence and bounded failure recovery;
this authorizes neither in-flight application switching nor display-state
preservation or migration. The older disruptive controlled-restart baseline
applies outside this bounded exception and remains an acceptable v1 fallback.
Preserving loaded eZ80 program, data, and resident processor state is an
aspirational v1 target and a firm v2 requirement under MODE-001; preservation
never implies migration of display assets between processors. The exact restart
actor and carrier remain open under SETUP-005 F018. A fixed-backend build still
activates explicitly after Legacy startup, and persisted preferred mode is not
a v1 contract. A pending state carried across reset exists only if a selected
implementation requires it; retained cross-boot circuit breaking remains
conditional under MODE-002. Exact lifecycle-state storage and session/shutdown
APIs remain open in SETUP-005.

A successful explicit activation remains latched system state when the
foreground caller exits or no known callers remain. Normal return to Legacy is
an explicit coordinated EMOS shutdown and may refuse or time out if registered
work cannot quiesce. A separately explicit forced shutdown may invalidate work
after warning.

Reset invalidates the affected component's sessions, parsers, pending work,
readiness, and authority even if RAM bytes or another processor survive;
invalidation does not require erasure. eZ80/MOS and whole-system resets return
through Legacy. P4 reset or detected EDP failure in Dual invalidates EDU work
and causes EMOS to commit Legacy while ordinary VDU continues through the
onboard VDP. In an exclusive mode, EDP or transport failure blocks ordinary
VDU, permits only bounded reinitialization, and then disruptively recovers to
Legacy without claiming preservation of application, display, audio, buffer,
or other EDP-visible state. EMOS recovery may use the onboard VDP for a
best-effort diagnostic only after disclaiming that continuity.

EMOS lifecycle records retain requested, conditionally pending, committed,
failure, and fallback information. Structured failure reporting is advisable
during beta and mandatory for v1. It provides best-effort descriptive display
output plus durable machine-readable consequences and safely obtainable
processor context, never relies solely on a failed component when another
accepted sink survives, and never delays safe recovery. The durable P4-flash
crash-log requirement and provisional `coredump` sink are defined below; exact
record behavior and qualification remain with DIAG-001.

Application entry point and operating-mode destination are separate concerns.
`RST.LIL 10h`, `RST.LIL 18h`, and the corresponding C-runtime output paths are
always conventional VDU calls. EMOS routes them to the onboard VDP in Legacy
and Dual, to the EDP stock-compatible backend in Exclusive Compatible, and to
the EDP enhanced backend in Exclusive Extended. Explicit EDU calls remain a
separate versioned interface with a separate result domain, even in an
exclusive mode where both interfaces reach the EDP.

An EDU-aware application may therefore combine VDU and EDU calls without
creating another operating mode. In Dual this intentionally coordinates two
processors; in either exclusive mode it uses two interfaces to the EDP. An
application may also require Exclusive Extended and use conventional VDU
restart calls as its efficient compatible-output path rather than wrapping
every transfer in an EDU invocation. Such a mode-dependent application must
verify or request Exclusive Extended before issuing output that would be unsafe
or meaningless if routed to the onboard VDP.

Every active Extender mode requires EMOS. In Dual, EMOS keeps ordinary VDU on
the onboard VDP while separately activating and arbitrating EDU access to the
EDP. Stock MOS supports only Legacy: Extender remains inactive, and an unknown
Extender command or API may fail normally. Direct linked-client ownership of
UART1, parallel GPIO, interrupt vectors, or EDP lifecycle under stock MOS is
outside the supported architecture.

Project hardware and firmware apply fail-safe pre-activation design: carrier
hardware keeps P4-to-Agon drivers disabled through hardware defaults rather
than relying only on P4 firmware, and the EDP accepts only a bounded EMOS
activation exchange before exposing ordinary VDU, EDU, update, or persistent
write operations. Supported pre-activation logic patterns or GPIO-direction
changes may be ignored or fail safely without opening another operation. These
rules govern every project-produced design, build,
example, and test. They are not a privilege boundary or warranty for arbitrary
external code that directly manipulates shared GPIO, UART, interrupt, flash, or
routing resources in violation of the EMOS contract; such code may corrupt,
damage, or brick either system. If EDP safely observes unmanaged activity, it
may warn through an Extender-owned display or log only and must not respond over
unactivated Agon-facing wiring.

In **Legacy mode**, the onboard VDP retains ordinary VDU and display behavior,
including maintenance/operator facilities omitted by Extender. Explicitly
selected browser or native USB keyboard input may continue through P4 and EMOS; it is the
accepted exception to older total Extender absence/quiescence requirements.
EMOS retains canonical keyboard state ownership. Other EDP/EDU service remains
inactive. In
Dual mode those facilities may likewise remain available through ordinary VDU
to the onboard VDP; they are not implemented by Extender.

During ExCom, EMOS leaves a static mode/status notice on mainboard VGA and
hides its text cursor with stock VDP commands. Ordinary CLI echo and application
VDU output follow the EDP route. The mainboard VDP keeps scanning out the notice
and generating the retained VBlank clock without periodic EMOS redraws or a
double-buffering requirement. This transition/status output does not mirror
ordinary VDU; Dual retains both displays' active roles.
Initially, returning to Legacy starts a fresh mainboard screen with a visible
cursor and MOS prompt, preserving keyboard source and layout. Clearing the
screen is an initial implementation choice rather than a permanent mode rule.

The formal operating-mode names are **Legacy mode**, **Exclusive Compatible
mode**, **Exclusive Extended mode**, and **Dual mode**. “Compatible” and
“Extended” are accepted short forms in unambiguous operating-mode context, but
“Exclusive” remains part of both official exclusive-mode names.
**ExCom** is accepted conversational shorthand for **Exclusive Compatible**;
the formal name and stable mode identity remain unchanged.

EMOS CLI control uses case-insensitive `EMOS <subcommand>` syntax in both
interactive commands and autoexec. `EMOS EXCOM` and `EMOS LEGACY` request the
named destination mode; `EDU` explicitly addresses Extender functionality while
`VDU` retains ordinary semantics and EMOS-owned routing. The accepted command
contract is in [ADR-0014](decisions/ADR-0014-edu-operating-modes-and-service-architecture.md#cli-and-keyboard-selection--2026-09-08).

`EMOS KEYINPUT mainboard` selects the Agon mainboard keyboard;
`EMOS KEYINPUT extender` selects Extender-connected hardware input, initially a
USB keyboard through the P4 DevKit's native host controller. These are the
immediate input choices. `EMOS KEYINPUT browser` retains its focused-browser
meaning, but browser-input development is deferred until explicitly
reprioritized. PORT-015 records native USB implementation and qualification.
With no source argument, the command reports the selected source.
`SET KEYBOARD n` remains the distinct runtime layout selection with the same
effect across modes. `EMOS LEGACY` preserves the selected keyboard source;
returning display output to the mainboard does not shut down selected browser
or P4 USB keyboard input.
Across boots, `autoexec.txt` alone restores these selections. EMOS starts with
mainboard keyboard input; commands at the interactive prompt change runtime
state without saving a separate state/configuration file. No new nonvolatile
settings store is introduced for this increment.

Extender v1 does not inherit the stock VDP's UART0 `DBGSerial` mapping or local
operator facilities. In either exclusive mode, attempts to invoke those paths
must follow stock VDP command consumption and observable failure behavior as
closely as practical. Strict compatibility modes preserve even undesirable
observable stock behavior; other modes should provide improved deterministic
failure and recovery. The exact strict-mode boundary and command-level
semantics are tracked under SETUP-005-D006.

## Firmware build model

PlatformIO remains the outer project, dependency, build, upload, and monitoring
workflow, preserving the official VDP project's familiar development idioms.
The ESP32-P4 environment combines the Arduino and ESP-IDF frameworks.

Arduino preserves the application-level structure expected by official
`agon-vdp`, including its sketch entry point and Arduino-oriented APIs and
libraries. ESP-IDF supplies the lower-level target configuration and native P4
facilities needed for silicon revision handling, memory, partitions, USB,
Ethernet, multimedia peripherals, and future Extender functions.

The hybrid framework choice must pass a minimal build and physical-board canary
before it becomes the foundation for source adaptation. See
[ADR-0002](decisions/ADR-0002-hybrid-firmware-framework.md).

FreeRTOS supplied by ESP-IDF remains the firmware concurrency substrate.
Extender replaces inherited ESP32-PICO watchdog disabling and core-placement
assumptions with one explicit P4-native policy. Operating modes may change
which tasks run and how they are supervised; strict compatibility governs
externally observable reset and failure behavior rather than requiring obsolete
watchdog internals. Exact task affinity, subscriptions, timeouts, and controlled
resets require subsystem-specific qualification.

Arduino PSRAM and ESP-IDF capability-aware allocation remain the underlying
memory substrate, preserving explicit selection of external, internal,
DMA-capable, and other constrained memory. The compatibility baseline does not
preclude future compile-time performance profiles that exploit P4 resources at
the cost of legacy behavioral fidelity. EDU-aware applications must discover
the active profile's advertised capabilities rather than infer them.

The immediate input goal is selectable Agon-mainboard or Extender-connected
keyboard input. P4 acquires one directly attached USB HID boot keyboard,
translates its events into retained stock VDP keyboard semantics and emits
normal VDP keyboard packets to EMOS over the existing r03 four-signal UART1 link at
1,152,000 baud, 8N1 with RTS/CTS. Keyboard configuration/query traffic uses the
same UART in the Agon-to-P4 direction. No parallel transfer or direct
onboard-VDP/EDP link is required for this capability.

EMOS owns the selected input ingress and stock-compatible packet handling.
P4 sends keyboard events/settings, not MOS memory: EMOS updates its own key
sysvars, event counter, virtual keyboard map and application keyboard hooks
through the stock handling semantics. Ordinary applications continue to use
MOS keyboard APIs, sysvars and the keymap; they do not forward input to P4 or
configure UART1. Browser/P4 session messages are distinct from the stock VDP
wire contract and do not introduce a proprietary UART keyboard envelope.

An explicit `EMOS KEYINPUT extender` command enables native USB input through
P4; `EMOS KEYINPUT mainboard` selects the mainboard VDP's keyboard path. EMOS
admits only the selected keyboard source and continues handling the mainboard
VDP's other communications. Source selection is independent of display mode;
autoexec alone restores the desired selection after reboot. Source changes
release held state before admitting the new source; no dual-keyboard mixing
is selected.

Browser-input development is deferred, not a prerequisite for these choices.
Its retained contract requires P4 to accept input from one controlling browser
session at a time. On focus loss/disconnect P4 releases held keys and stops
that session's keyboard delivery.
Other sessions may view within supported video connection limits. Explicit
takeover revokes the previous owner and releases its held keys before input
from the new owner is admitted; focus alone does not transfer control.

Session admission and revocation precede stock packet delivery. The selected
browser session is a keyboard authority, including normal stock key effects;
focus is a capture condition, not authentication. EMOS retains input-source
selection and canonical-state ownership. EMOS uses interrupt-driven UART1 reception with packet assembly separate from
UART0; the receive streams must not race or splice parser state. The precise session and ingress mechanisms are
owned by SETUP-005, REMOTE-001, PORT-006, PORT-008 and agon-emos INTEG-009.

Physical PS/2 keyboard/mouse acquisition remains on the onboard VDP where
those devices are used. It is not a relay for browser keys. The accepted bench
clock remains the onboard VDP's VBlank/PB1 path. Native USB input uses the
[specified USB keyboard connection](../hardware/designs/light2-harness-r03/README.md#usb-keyboard-addition--2026-09-09).
It does not replace VBlank or itself change ordinary VDU routing. A bounded
qualification session has explicit entry/exit; it does not
claim complete Exclusive Compatible mode; Legacy permits the explicitly
selected keyboard service described above.

For the selected directly attached USB keyboard, P4 receives
USB HID reports through its native host controller, translates them into
ordered processed keyboard events and sends stock keyboard packets through
the same EMOS-owned UART1 session. Explicit `EMOS KEYINPUT extender` selection
controls this path independently of browser focus/network and display mode.
Initial scope is one wired HID boot-protocol keyboard with normal EMOS CLI on
mainboard VGA. USB removal releases held state; it is not browser lease expiry.
No implicit browser/USB mixing or new UART keyboard packet format is selected.

P4's processed-input adapter owns EDP-local keyboard variables, relevant
callbacks, control-key and paged-mode behavior and stock packet generation.
Later Agon-originated EDU event forwarding retains its non-echo rule; browser
keys are original events and must be emitted toward EMOS. Mouse injection and
full mode-specific input composition remain separate scope.

Physical vdp-gl keyboard/mouse drivers, PS/2 controllers, scan-code tasks and
device controls stay vendored but excluded from the P4 build. The browser
adapter reuses stock virtual-key/event vocabulary and applicable pure mapping
semantics without depending on physical PS/2 hardware. Direct USB keyboard
input may use the selected P4 DevKit's existing native host plus the required
USB connector and power assembly. This permission does not restore the omitted
PS/2 engines or select other peripheral expansion.

Extender retains ESP-IDF's OTA image, boot-partition, rollback, and restart
lifecycle as the low-level update substrate. This is independent of the omitted
stock VDP serial updater and does not select an update transport. A project-
owned replacement is warranted only if evidence shows the ESP-IDF facilities
are materially inferior to sound clean-sheet ESP32-P4 practice.

Extender networking is project-owned. The P4 DevKit's native wired Ethernet is
the primary Rev 1 backend; the dedicated-header Olimex MOD-WIFI-ESP8266 is an
optional Rev 1 wireless backend whose P4-to-module protocol and module firmware
must be selected and qualified separately. The dormant vendored vdp-gl ICMP
helper is excluded from the P4 build: it assumes a local Arduino WiFi/raw-lwIP
interface and is not an adapter for a separate ESP8266 network processor.

The initial build pins pioarduino platform release `55.03.311`, which combines
Arduino-ESP32 3.3.11 with ESP-IDF 5.5.5. A moving release alias or development
branch is not an acceptable reproducible baseline. See
[ADR-0003](decisions/ADR-0003-pioarduino-platform-baseline.md).

The Rev-D1 development board's v1.3 ESP32-P4 is represented as the pre-v3
`esp32p4_es` platform variant. SDK configuration explicitly limits compatible
full revisions to 100 through 199, and board qualification reports and checks
the runtime revision. See
[ADR-0004](decisions/ADR-0004-p4-silicon-identity.md).

The primary board environment configures the 16 MB SPI flash for QIO at
80 MHz. This is a qualification candidate until cold-boot, reset, reflash, and
flash-integrity tests pass on the physical board. DIO at 80 MHz is the defined
fallback if QIO proves unreliable. See
[ADR-0005](decisions/ADR-0005-flash-bus-mode.md).

The board definition uses a conservative 512,000-byte internal-RAM link budget
and declares external PSRAM separately. The 32 MB PSRAM operates in hexadecimal
mode at 200 MHz and is intended for explicit bulk allocation; it is not treated
as interchangeable with internal SRAM. Bring-up verifies its capacity and runs
a memory test. See [ADR-0006](decisions/ADR-0006-board-memory-model.md).

The 16 MB flash contains two equal 7 MiB OTA application slots. A candidate
image is written to the inactive slot and must pass an explicit post-boot health
check before it is marked valid; otherwise the bootloader rolls back. There is
no separately maintained factory application. Required NVS, OTA metadata, and
crash diagnostics use the leading data area, and the approximately 1.9 MiB
remainder stays reserved until a durable use is approved. See
[ADR-0007](decisions/ADR-0007-flash-partition-strategy.md).

V1 requires a bounded durable crash-log sink in the P4's onboard flash so
mainboard failure evidence never depends on an optional microSD card. The
dedicated `coredump` partition is the initial candidate and must be validated
for the versioned Extender record, native ESP-IDF crash evidence, integrity,
interrupted writes, and wear limits. P4 microSD may provide richer optional
history or exports. Browser or local video may present a surviving
human-readable report but is not durable by itself. Diagnostic persistence must
never delay safe recovery.

PlatformIO owns hybrid project orchestration. The project begins without
project-authored CMake files; a tracked `CMakeLists.txt` is added only when a
specific build requirement demonstrates that PlatformIO's generated hybrid
structure is insufficient. Any such file must be the smallest boundary needed
and must not reorganize the upstream-compatible `video/` tree. See
[ADR-0008](decisions/ADR-0008-minimal-cmake-boundary.md).

The tracked `scripts/vdp-pio.sh` wrapper locates the repository root, requires
the root `.venv/bin/pio`, selects `vdp/` as the PlatformIO project directory,
and forwards PlatformIO arguments unchanged. It performs no implicit build,
upload, installation, port selection, or environment activation. Direct
PlatformIO invocation remains supported. See
[ADR-0009](decisions/ADR-0009-platformio-wrapper.md).

The primary Rev-D1 pre-v3 board environment configures the CPU at 360 MHz. A
forced 400 MHz candidate repeatedly asserted during clock initialization on the
attached rev 1.3 silicon and is rejected for this hardware profile. See
[ADR-0010](decisions/ADR-0010-cpu-frequency.md).

### Explicit application display preservation

For paired graphics inspection, applications use public mos_oscli to request
`EMOS LEGACY --keep-display` and `EMOS EXCOM --keep-display` at complete
VDU/query boundaries. Mainboard VDP and EDP each retain their own mode, scene
and resources; EMOS changes the committed route and reply authority through
its coordinator without clearing those scenes or drawing a mode notice. USB
source selection and the mainboard clock remain independent. Default console
switch commands keep their fresh-display behavior. ADR-0014 records this
bounded extension; it does not authorize direct application transport access.

## Browser-video encoding and pacing

EDP composes the final pixels on P4. The [browser-video contract](protocols/browser-video.md)
owns presentation transport encoding and pacing: RGB222 saves threefold payload
relative to RGB888, browser WebGL expands colours, and bounded frame credits
control delivery without a fixed 5 fps throttle. Logical VDP time remains
independent of network/browser progress. Hardware qualification of the new
encoding and pacing is tracked in PORT-003.
