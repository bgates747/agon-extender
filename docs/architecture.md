# Agon Extender Architecture

This document describes the current accepted architecture. Open questions and
implementation work belong in `TODO.md` and the corresponding tracked files
under `docs/tasks/` rather than here.

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

The classic-ESP32 concrete VGA controller family is replaced by an
Extender-owned concrete bitmapped controller. It produces framebuffer state and
logical frame progression independently of any one physical output sink, so
the guaranteed network/browser path and later P4-native local displays consume
one rendering model. Preserve stock mode dimensions, palette quantization,
Copper scanline effects, sprite composition, readback, double buffering, frame
waits and counters, callbacks, and mode failure/fallback behavior as closely as
practical. The old GPIO-matrix, I2S1, DMA-chain, and VSync-ISR engine remains
vendored reference material, not the P4 physical backend.

The replacement is one project-owned `GenericBitmappedDisplayController`
configured with the stock native pixel codecs. The initial compatibility
backend retains packed 2-, 4-, 8-, and 16-color storage and the logical RGB222
contract for 64-color modes; physical VGA sync bits do not belong to P4 logical
storage. The official facade receives only narrow concrete-type,
palette/Copper, frame-counter, and cursor-position binding adaptations.

A periodic P4 logical frame clock and frame-service task advance official VDP
time independently of every output sink. That service owns queued primitive
execution, logical swaps, presentation publication, and explicit completion.
Physical sink callbacks may recycle sink buffers but do not advance the VDP
frame counter or unblock logical swaps.

One central presentation compositor decodes native pixels, applies Copper
palettes by scanline, and adds hardware sprites and cursors without changing
logical framebuffer state or readback. Network/browser and later local-display
sinks receive non-blocking latest-generation notifications through a common
consumer contract. Slow sinks may drop reported presentation generations; they
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
Future installed-application, media, network-file, or browser interfaces consume
that storage capability without defining its physical backend.

## Hardware design target

The authoritative first Agon Light 2 wiring target is
[`light2-harness-r01`](../hardware/designs/light2-harness-r01/README.md). It
adopts the predecessor project's physically exercised eight-bit forward-bus
pin map, installed-view routing geometry, series resistance, and control-signal
biasing. Its tracked YAML profile is the normative pin authority; vendored text
is provenance and supporting evidence, while the inherited SVGs are advisory.

The predecessor's 115,200-baud reverse-UART fixture exercised the same buffered
PC0/PC1 circuit selected as the first physical target for the official legacy
UART contract. The lower rate deliberately prioritized wiring and directional
correctness over speed margin; it does not qualify operation at the required
1,152,000 baud. Complete legacy flow control, target-speed operation,
production isolation, either-order power behavior, final carrier construction,
and Console8 adaptation remain unqualified.

## EDU operating modes and application interface

Project terminology distinguishes the **Extended Display Unit (EDU)** exposed
to eZ80 software from the **Extended Display Processor (EDP)** that implements
it on the ESP32-P4. EDU names the command set, API, and logical facility; EDP
names the processor and its firmware. The terms intentionally parallel Agon's
existing VDU and VDP terminology.

Extender-aware programs address the P4 through an explicit, stable, versioned
EDU API. The API is independent of its eZ80-side implementation: synchronous
foreground operations may use code linked into an application, while
persistent or asynchronous facilities may use an explicitly installed resident
service.

The resident service is optional. Its presence does not intercept or redirect
the stock `RST.LIL 10h` or `RST.LIL 18h` VDU paths, and applications must
discover and open it deliberately. It may own persistent transport state,
interrupt-driven reception, queues, and background work on behalf of clients.
A future official MOS integration may supply another backend without changing
the application-facing EDU contract. See
[ADR-0014](decisions/ADR-0014-edu-operating-modes-and-service-architecture.md).

In **exclusive compatibility mode**, exactly one display processor owns the
stock-compatible command path, responses, completion flags, and canonical MOS
VDP sysvars. EDP-exclusive mode may claim compatibility only for the declared
normal application-facing surface; Extender v1 explicitly excludes local
printer/USB serial, console/terminal, ZDI, Intel HEX, YMODEM, updater, and debug
facilities. Transparent EDP selection remains unresolved until the fixed legacy
VDU restart paths and return traffic can be routed safely.

In **extended cooperative mode**, the onboard VDP remains authoritative for VDU
and MOS VDP sysvars while the EDP is addressed through EDU and retains results
in an EDU-owned state domain. Applications and project-owned abstraction layers
may coordinate both processors, but uncontrolled duplication of a VDU stream or
competing writes to canonical sysvars is unsupported.

Baseline extended cooperative mode supports stock MOS: EDU-aware applications
reach the EDP through linked client code or the optional resident EDU service,
and MOS need not know that Extender exists. An Extender-enabled MOS is required
only by features that need system-wide integration, such as a MOS-based
implementation of transparent legacy VDU routing; it is not a prerequisite for
ordinary cooperative EDU use.

In **legacy mode**, Extender is electrically and logically absent from the Agon
interface even when connected and powered. The onboard VDP owns all stock
behavior, including maintenance/operator facilities omitted by Extender. In
extended cooperative mode those facilities may likewise remain available
through ordinary VDU to the onboard VDP; they are not implemented by Extender.

Extender v1 does not inherit the stock VDP's UART0 `DBGSerial` mapping or local
operator facilities. In EDP-exclusive mode, attempts to invoke those paths must
follow stock VDP command consumption and observable failure behavior as closely
as practical. Strict compatibility modes preserve even undesirable observable
stock behavior; other modes should provide improved deterministic failure and
recovery. The exact strict-mode boundary and command-level semantics are tracked
under SETUP-005-D006.

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

The onboard VDP remains the physical keyboard and mouse owner. Its stock packets
to MOS remain the canonical legacy input path. In the proof of concept, an
EDU-aware eZ80 application reads stock input and explicitly forwards processed
events to an EDP input-injection adapter when it needs display-local behavior
such as paged mode, control keys, mouse cursors, VDP variables, or callbacks.
The adapter updates EDP-local state and does not automatically echo stock input
packets back to the forwarding application. This profile makes no compatibility
claim for untouched applications. A more automatic v1 route and its
single-writer relationship with MOS sysvars remain open under SETUP-005-D007.
V1 adds no P4-owned keyboard, mouse, or other
peripheral hardware beyond facilities already present on the selected P4
DevKit; additional input hardware is post-v1 work.

The vdp-gl physical keyboard device, scan-code conversion task, locale-layout
engine, typematic/LED device control, and compiled layout tables remain in the
complete vendored source but are excluded from the P4 build. The onboard VDP
owns those operations. Extender retains only the stable virtual-key and event
vocabulary required by its processed-event injection adapter.

The vdp-gl physical mouse device, PS/2 packet decoder, task, queues,
acceleration, and direct display-positioning engine likewise remain vendored
but are excluded from the P4 build. The onboard VDP owns physical mouse
processing. Application-forwarded processed mouse fields feed the EDP adapter,
which owns EDP-local state and cursor effects through the retained display
backend.

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
