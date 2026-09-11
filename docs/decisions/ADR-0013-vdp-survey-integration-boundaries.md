# ADR-0013 — VDP survey findings and integration boundaries

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-20
- Last amended: 2026-09-10
- Related tasks: SETUP-003, SETUP-004, PORT-002, PORT-003, PORT-005, PORT-007, REMOTE-001, AUDIT-006

## Context

The SETUP-003 source and build surveys show that the official VDP firmware
owns peripheral facilities needed by the stock Agon VDP. These include FabGL's
PS/2 controller and keyboard/mouse paths, low-level ESP32 ULP support, and
other hardware-facing I/O code.

Extender supplements an Agon whose main board and onboard VDP continue to own
their existing physical input and peripheral responsibilities. Backward
compatibility with the official VDP does not require duplicating every stock
VDP hardware implementation on the P4. Blindly compiling all such facilities
would increase the P4 porting surface and preserve dependencies on ESP32-only
hardware that Extender does not use. The first survey build exposed one such
case when `vdp-gl/src/comdrivers/ps2controller.cpp` included the unavailable
ESP32-specific `esp32/ulp.h`.

## Decision

1. Treat the official VDP source survey as both a compatibility inventory and
   a scope-selection exercise. Inclusion in upstream source does not by itself
   require inclusion in Extender firmware.
2. Do not port or build FabGL's PS/2 controller or its physical keyboard and
   mouse implementation for Extender.
3. More generally, exclude upstream hardware-facing I/O facilities when the
   Agon main board or onboard VDP remains responsible for that hardware and
   Extender has no defined use for the implementation.
4. Preserve externally observable VDP protocol and application behavior where
   backward compatibility requires it. Separate that compatibility obligation
   from reuse of the upstream physical driver that originally supplied the
   behavior.
5. Extender-specific input facilities, if introduced, are project-owned. Put
   their interfaces and implementations in the Extender-owned source boundary;
   do not force them through unused FabGL PS/2 or stock peripheral machinery.
6. Use explicit build selection, adapters, or narrow compatibility boundaries
   to omit unused upstream facilities. Do not perform broad source cleanup or
   restructure vendored upstream code merely because part of it is excluded.
7. Record each material omission discovered during SETUP-003 with the upstream
   subsystem, the retained compatibility surface, and the replacement owner or
   reason no replacement is required.
8. Retain pinned ESP32Time `2.0.6` as the initial P4 provider behind the stock
   RTC command and state surface. Keep clock authority, synchronization,
   persistence, and operating-mode policy in a project-owned layer around the
   provider; replace ESP32Time only if qualification demonstrates a material
   limitation.
9. Omit vdp-gl's unused DS3231 translation unit from Extender builds while
   retaining it unchanged inside the complete vendored upstream release. The
   current hardware has no DS3231 and official VDP has no evidenced runtime
   consumer; any future use requires a new project-owned hardware decision.
10. Treat vendored availability and build selection as separate, explicit graph
    properties. Deterministically generate human-readable source-selection and
    tagged-release merge guidance so upstream integration can prioritize the
    selected dependency closure without making unselected changes invisible.
11. Omit vdp-gl's unused MCP23S17 translation unit from Extender builds while
    retaining it unchanged inside the complete vendored upstream release. The
    current hardware has no MCP23S17 and official VDP has no evidenced runtime
    consumer; future GPIO-expander hardware is a project-owned addition.
12. Retain ordinary Arduino and ESP-IDF GPIO direction, read, and write services
    for surviving P4 drivers. This platform-service decision does not retain an
    upstream physical driver, pin assignment, or peripheral extension; those
    remain independently selected through hardware profiles and subsystem
    dispositions.
13. Retain ESP-IDF's P4 SPI master substrate independently of every concrete
    upstream consumer. This does not reverse the MCP23S17 or vdp-gl storage
    omissions; PORT-007 independently selects SDMMC for the DevKit card, and
    future project-owned SPI devices require explicit source selection,
    hardware profiles, and qualification.
14. Retain ESP-IDF's P4 `esp_timer` monotonic-clock and callback lifecycle as a
    shared platform service. Every surviving display, audio, input, scene, or
    utility consumer remains responsible for qualifying its own callback
    latency, jitter, pacing, timeout, and scheduling assumptions.
15. Replace vdp-gl's ESP32/Xtensa-specific CPU/APB clock, APLL/resource,
    FRC-timer, and cycle-counter internals with narrow P4-native implementations
    at the existing upstream seams. Preserve names and call sites wherever
    practical, record the substitution in the compatibility delta and
    dependency graph, and do not use unavoidable architecture work as license
    for unrelated upstream refactoring.
16. Retain the official VDP's header-defined screen facade, including its
    global Canvas/controller ownership, mode selection and fallback, logical
    dimensions and scaling, palette and Copper state, frame counter, completion
    waits, and buffer swaps. Keep its names and source placement recognizable;
    adapt only the narrow concrete-controller binding required by the P4
    display backend rather than create a parallel project-owned display model.
17. Retain vdp-gl `Canvas`, the abstract bitmapped-controller contract, and the
    common primitive, paint, clipping, geometry, glyph, bitmap, sprite, cursor,
    readback, completion, and buffering semantics. Apply narrow P4 adaptations
    where common code directly assumes the old Xtensa VGA-ISR environment,
    including transformed-bitmap coprocessor-state handling; do not redesign
    unrelated common rendering code as part of that adaptation.
18. Replace vdp-gl's concrete VGA2/VGA4/VGA8/VGA16/VGA64 physical-controller
    family with an Extender-owned concrete `BitmappedDisplayController` backed
    by framebuffer production and logical frame progression independent of any
    one output sink. Preserve stock mode dimensions, palette quantization,
    Copper scanline effects, sprite composition, readback, double buffering,
    frame waits and counters, callbacks, and mode failure/fallback behavior as
    closely as practical. The Author clarified on 2026-09-10 that this means
    retaining reusable code exactly as written, including native framebuffer
    formats, row organization and fast paths inside concrete-controller files.
    Replace only portions made unavailable by processor facilities or
    video-output interfaces, such as classic GPIO-matrix, I2S1, DMA descriptor
    and interrupt bindings. Excluding a physical engine does not exclude its
    portable memory/rendering algorithms. A generic replacement controller or
    browser-friendly drawing layout is not itself a requirement. AUDIT-006-D001
    governs review of those earlier implementation choices; output adapters
    consume the image without dictating a less faithful drawing backend.
19. Omit vdp-gl's independently compiled `VGATextController` translation unit
    from Extender builds while retaining it unchanged in the complete vendored
    release. Official VDP text uses Canvas over the retained bitmapped path and
    has no runtime constructor or visible dependency on this separate hardware
    character-cell VGA driver; no stub or replacement is required.
20. Omit vdp-gl's independently compiled `CVBSGenerator` translation unit from
    Extender builds while retaining it unchanged in the complete vendored
    release. Official VDP has no runtime construction or visible dependency on
    this classic-ESP32 DAC/I2S0/DMA composite-video facility, and composite
    video is not a selected Extender output; no stub or replacement is needed.
21. Omit vdp-gl's independently compiled `Scene` translation unit from Extender
    builds while retaining it unchanged in the complete vendored release.
    Official VDP sprite commands use their own state and the retained
    bitmapped-controller path; no Scene object or start call exists at runtime.
    Retain independently required Sprite/display types, but provide no Scene
    stub or replacement unless a future Extender feature deliberately adopts
    that separate scheduler.
22. Retain the official VDP's header-defined audio parser, `PACKET_AUDIO`
    acknowledgements, channel state machines, envelopes, buffer-backed samples,
    playback timing, audio-control task, and VDU 7 behavior. Preserve its names,
    placement, and application-visible behavior; adapt only the direct
    `fabgl::SoundGenerator` binding required to connect it to the selected P4
    synthesis and output service rather than create a parallel audio model.
23. Retain vdp-gl's waveform generators, channel attachment and lifetime rules,
    sample-rate propagation, channel and global volume behavior, and signed
    eight-bit PCM mixer. Narrowly adapt the fused `SoundGenerator` boundary to
    expose mixed samples to an Extender-owned scheduler or sink; do not use that
    seam to redesign unrelated synthesis semantics.
24. Replace vdp-gl's classic-ESP32 DAC, sigma-delta, I2S0-register, legacy-DMA,
    fixed-pin, ISR/timer, VGA/CVBS-selection, and target SDL output machinery
    with an Extender-owned PCM scheduler and sink service. Retain the old source
    in the complete vendored release but omit its physical target paths from the
    P4 build. Network/browser audio is the guaranteed Rev 1 sink; no P4-local
    analog transducer is selected.
25. Preserve logical audio compatibility independently of output delivery. The
    replacement scheduler advances playback at the selected sample rate even
    when a sink is absent, slow, or congested; sink behavior must not block VDU
    processing, delay logical note completion, or change channel status.
    Delivery may drop or resynchronize when necessary. Rev 1 does not guarantee
    the stock analog-output location, analog distortion, or sink latency.
26. Replace direct FabGL physical-input bindings with a processed-event
    adapter. Under ADR-0014's 2026-09-08 amendment, the first source is focused
    browser keyboard input. P4 preserves applicable VDP variables, callbacks,
    control-key/paged-mode behavior and emits stock keyboard packets to EMOS
    over UART. The former aware-application forwarding profile remains later
    scope and retains non-echo behavior for copied events only.
27. Keep physical keyboard, PS/2 scan-code tasks and device control excluded
    from the P4 build while preserving complete vendored sources. Retain stock
    virtual-key/event vocabulary and reuse applicable pure mapping semantics
    for browser input. Physical onboard keyboard ownership does not require
    browser keys to pass through the onboard VDP.
28. Omit vdp-gl's physical mouse device, PS/2 packet decoder, update task,
    queues, acceleration, and direct display-positioning engine from the P4
    build while retaining the complete sources in the vendored release. The
    onboard VDP remains the physical packet-processing owner; application-
    forwarded processed mouse fields feed the EDP injection adapter, which owns
    only EDP-local state and cursor effects.
29. Omit vdp-gl's independently compiled `ICMP.cpp` helper from the P4 build
    while retaining it in the complete vendored release. It has no official VDP
    consumer or visible compatibility surface and binds directly to a local
    Arduino WiFi/raw-lwIP interface. Extender networking is project-owned. The
    optional Rev 1 MOD-WIFI-ESP8266 module is a separate processor reached over
    its dedicated-header host protocol and does not justify selecting this
    P4-local helper.
30. Omit vdp-gl's dormant `FileBrowser` API and implementation from the P4
    build while retaining it in the complete vendored release. No official VDP
    behavior or selected vdp-gl consumer requires it, and Extender does not
    presently select a file-browser interface. Required v1 P4 DevKit SD-card
    support is a separate project-owned capability, deferred beyond the first
    beta; future browser or network file interfaces require their own concrete
    consumers and service decisions. On 2026-09-10 the Author confirmed that
    EMOS must be able to read files from the P4 card. EDP owns the physical
    card/filesystem service; EMOS requests and receives reads through its
    owned Extender transport. PORT-007 owns this consumer's integration.
31. Omit vdp-gl's classic-ESP32 SDSPI/SPIFFS mount, format, capacity, pin,
    host/DMA, global-watchdog, and VGA/WiFi-workaround backend from the P4
    build while retaining it in the complete vendored release. Provide no
    compatibility stub or FabGL-shaped replacement. Implement the required v1
    DevKit microSD capability independently from maintained Olimex/Espressif P4
    SDMMC code, with its own production lifecycle and qualification.

## Rationale

1. The stock main board remains the authority for hardware it already serves;
   duplicating those drivers on Extender adds no useful compatibility.
2. Removing unused hardware implementations reduces architecture-specific
   porting work without weakening the promise to preserve relevant VDP-visible
   behavior.
3. Project ownership of new input paths allows a deliberate P4-native design
   instead of inheriting ESP32 and PS/2 constraints accidentally.
4. Explicitly recording exclusions prevents an omitted source file from being
   mistaken for an incomplete or forgotten port.

## Consequences

1. A successful Extender build will not necessarily compile every translation
   unit supplied by vdp-gl or the official VDP dependency graph.
2. Build manifests and structural inventories must distinguish code available
   in vendored source from code selected into Extender firmware.
3. Compatibility analysis must identify any VDP commands or responses coupled
   to excluded input drivers and decide whether they remain onboard-VDP-only,
   require a stub, or require a project-owned adapter.
4. Future Extender input hardware or network input features require their own
   architecture and qualification decisions.
5. RTC qualification must distinguish the retained clock provider from the
   separately selected authority and synchronization policy.
6. Upstream integration review must use generated build-selection evidence and
   dependency boundaries rather than infer importance from the presence of a
   file in the vendor tree.
7. Work 1.c must validate the SPI, GPIO, interrupt, and link fallout from
   excluding MCP23S17 before the source filter becomes an implementation change.
8. Every retained GPIO consumer must use an explicit target hardware profile
   and receive pin-mux and electrical qualification; no stock pin mapping is
   inherited merely because the portable API survives.
9. Build and dependency records must prevent retention of the SPI platform API
   from being interpreted as retention of all upstream SPI device code.
10. Retaining `esp_timer` establishes an implementation substrate, not proof
    that ESP32-PICO timing behavior carries over to the P4.
11. Architecture substitutions are expected recurring port work. Each must be
    locally bounded, provenance-rich, and traceable to the retained consumer
    that makes it necessary so later tagged-release merges can distinguish
    intentional P4 adaptations from accidental divergence.
12. The retained screen facade becomes the stable upstream-shaped integration
    seam for display work. Replacement physical output code must satisfy that
    seam instead of forcing broad changes through official command-processing
    source.
13. The retained Canvas/common-renderer layer is the behavioral seam beneath
    the facade. Concrete P4 display backends must implement its controller
    contract and preserve observable ordering, completion, refresh, sprite,
    readback, and buffering behavior.
14. Network/browser video and later P4-native local displays consume the same
    logical framebuffer/frame service rather than defining separate VDP
    rendering models. Output-sink pacing must not silently redefine the stock
    frame semantics relied upon by commands and callbacks.
15. Source-selection evidence must keep the omitted hardware text controller
    visible for tagged-release merge review without implying that it belongs in
    the Extender firmware image.
16. The same vendored-versus-selected evidence must keep the unused composite
    generator visible for upstream review without carrying its physical driver
    into the P4 build.
17. Omitting Scene removes an unused task, mutex, collision-callback, and
    parallel sprite-scheduling surface without changing official VDP sprites.
    Future adoption requires an explicit source-selection and concurrency
    decision rather than accidental activation through broad library builds.
18. The official audio runtime becomes the stable upstream-shaped integration
    seam for audio porting. Replacement scheduling or output code must satisfy
    its command, state, timing, sample, callback, and packet contracts instead
    of forcing broad changes through official audio-processing source.
19. The retained vdp-gl mixer is the behavioral seam beneath the official audio
    runtime. Output backends consume its mixed PCM rather than implementing
    independent waveform, attachment, volume, or sample-rate models.
20. Audio qualification must test protocol responses and logical playback
    timing separately from end-to-end browser latency and fidelity. A network
    outage or backpressured client may degrade delivered audio but cannot alter
    the command processor or logical channel state.
21. Optional forwarding to the onboard VDP for local playback is not implied by
    the replacement sink and remains a separate operating-mode decision.
22. The input adapter provides a stable seam between official display-local
    input behavior and whichever event route an operating mode selects. The
    proof-of-concept route validates aware applications only; transparent v1
    routing remains separately unresolved.
23. Source selection must not pull the keyboard task and layout tables back into
    the P4 image merely because shared virtual-key declarations remain visible
    in the complete vendor tree.
24. Shared mouse event/status vocabulary may remain available to the adapter,
    but it must not pull the physical decoder, task, queues, acceleration, or
    display-positioning implementation into the P4 image.
25. The source-selection manifest must keep the dormant ICMP helper visible for
    tagged-release review without compiling it into the P4 image. Native wired
    Ethernet and optional ESP8266 wireless support share project-owned network
    service boundaries rather than inheriting FabGL's unused WiFi helper.
26. Because FileBrowser is fused into otherwise retained `fabutils.cpp`, source
    selection needs a narrow, provenance-rich region boundary rather than
    excluding the whole translation unit. Later tagged imports must verify that
    no newly selected upstream consumer has appeared.
27. The fused physical backend requires the same narrow source-region boundary.
    Its omission must not remove unrelated retained fabutils services, and the
    new P4 storage service must not make automatic formatting, global watchdog
    mutation, or classic-chip bus assumptions accidental product policy.
