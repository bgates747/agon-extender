# AUDIT-010 coverage ledger

## Executive summary

This ledger froze the complete review map before conclusions were drawn. Its
stable `A10-COVnnn` rows partition the pre-LCD product by owning actor and
resource/transition boundary. Every row was queued for A10-03 architecture and
resource tracing, A10-04 applicable automation, and A10-05 manual review unless
its disposition explicitly narrows it. The original table cells preserve that
pre-review state; A10-06's final crosswalk at the end now links stable
`AUDIT-010-Fnnn` and existing FWBUG identities without renumbering coverage.

## Disposition vocabulary

- `Exhaustive` — review all project-owned behavior and selected integration
  assumptions in the named boundary.
- `Selected-vendor` — exhaustively review local changes, configuration,
  wrappers and assumptions; enter untouched internals only when an active call
  path or demonstrated behavior requires it.
- `Reference` — use to judge a contract, not as an audit target.
- `Deferred delta` — preserve evidence but exclude code from this baseline.
- `Historical comparison` — consume already accepted evidence only; no new
  history inspection without the task's explicit Author gate.

## Firmware and service coverage

| Coverage ID | Actor; files / symbols | Function and state/resources | Callers → consumers | Prior evidence / contract | Automated checks | Manual checks | Disposition / findings |
|---|---|---|---|---|---|---|---|
| A10-COV001 | P4 Arduino/IDF boot actor; `p4_console.cpp`, `video.ino`, generated build identity | Initializes serial transport, retained VDP lifecycle and Extender services; owns boot ordering and persistent singleton construction | IDF/Arduino `app_main` → EMOS UART peer, display and network services | BUILD-001 boot/equivalence; ADR-0023 | Native warnings, linked-action proof, LLVM/Cppcheck | Initialization order, partial-start rollback, service coexistence, published identity | Exhaustive; findings: none yet |
| A10-COV002 | P4 UART console transport; `console_hardware.inc`, selected parser path included by boot TU | Receives ordinary VDU bytes and sends control/input/telemetry records over UART1 with RTS/CTS; owns parser-facing stream and transport state | EMOS VDU route ↔ retained VDP parser and EMOS keyboard/admission | ExCom protocol; BUILD-001 hardware results | Compile/selection checks; local policy rules for bypasses | Framing, ownership handoff, timeout/fault recovery, direct-writer search | Exhaustive; none yet |
| A10-COV003 | P4 retained VDP mode/runtime coordinator; `stock_runtime_controller.*`, `stock_p4_service.*`, `stock_native_access.*`, `screen_facade_adapter.*` | Selects controller/mode, resets drawing state, serializes native/foreground access, exposes logical mode and presentation boundary | VDU mode command and renderer → display, snapshot, browser status, EMOS-observed behavior | Official `Screen-Modes.md`; architecture mode lifecycle; inherited Nurples failure | LLVM/Cppcheck; mode lifecycle host tests | Allocation transaction, fallback order, stale state, lock scope, teardown and retry | Exhaustive; none yet |
| A10-COV004 | P4/vdp-gl paletted controllers; selected `vga{2,4,8,16,64}controller.cpp`, `vgapalettedcontroller.cpp`, `vgabasecontroller.cpp` | Allocates line pointer tables, palettes, signal maps, DMA rows/pools, queues and primitive task; implements resolution/reallocation | Runtime coordinator → canvas/drawing, snapshot producer | Official mode sizes/fallback; AUDIT-007 retained findings; BUILD-001 selected graph | LLVM/Cppcheck and allocation-pair inventory | Capability/contiguous-memory budgets, task/queue lifetime, partial allocation cleanup, fallback semantics | Selected-vendor; none yet |
| A10-COV005 | P4 retained drawing core; selected `canvas.cpp`, `displaycontroller.cpp`, `fabfonts.cpp`, `codepages.cpp`, `stock_render_utils.cpp`, `stock_scanline.cpp`, cursor adapter | Owns canvas state, sprites/bitmaps, saved backgrounds, fonts, paint primitives, scanline/Copper-visible composition and temporary pools | VDU parser/buffer commands → framebuffer and presentation boundary | Official VDU and buffered-command docs; PORT-003; AUDIT-007 boundary | LLVM/Cppcheck; existing host graphics/sanitizer harness inventory | Bitmap/sprite ownership, realloc failure, clipping, buffer lifecycle, scanout-time effects | Selected-vendor; none yet |
| A10-COV006 | P4 presentation snapshot pool; `presentation_snapshot_pool.*` | Owns bounded PSRAM slots, generation/lease state, mutex/atomics and producer/consumer admission | Display presentation boundary → browser provider and diagnostics | Browser protocol ownership; BUILD-001 analysis smoke | LLVM/Cppcheck; snapshot host tests/sanitizers | Slot sizes, allocation timing, lease abandonment, contention, teardown, truth of metrics | Exhaustive; none yet |
| A10-COV007 | P4 browser frame provider/codecs; `browser_video_provider.*`, codec/network headers reached by selected TUs | Validates snapshot shape and constructs EVF1/EVR1/EVP1/EVQ1 frames; owns active lease/header/compression view | Snapshot pool → HTTP WebSocket sender → browser | Browser-video protocol; 48-vector native browser check | LLVM/Cppcheck; codec vectors; host sanitizers | Scratch bounds, failed encoding fallback, lease completion/abandonment, generation pacing | Exhaustive; none yet |
| A10-COV008 | P4 HTTP video/session actor; `http_video_service.*`, `browser_video_service_core.*`, `opaque_message.*` | Owns WebSocket session state, credits, queued sends, close callbacks and in-flight opaque segments | Wired HTTP server/browser request → browser client | Browser-video pacing/error contract | LLVM/Cppcheck; browser tests; detached consumer compile | Callback lifetime, queued-work races, close/error transaction, one-viewer ownership | Exhaustive; none yet |
| A10-COV009 | P4 wired network service; `wired_network_service.*` | Owns Ethernet/DHCP worker, primary HTTP server/routes and persistent PSRAM compression scratch (786,432 + 589,828 + 786,446 bytes) | Boot actor → browser video, keyboard, telemetry, SD diagnostics/clients | Shared-P4 services; browser and keyboard guides; HTTP hardware checks | LLVM/Cppcheck; route/codec host checks | Startup rollback, scratch allocation policy/lifetime, task stack, route registration failure, service coexistence | Exhaustive; none yet |
| A10-COV010 | P4 remote/USB keyboard integration compiled through boot TU and wired HTTP routes | Owns physical/browser/agent arbitration, held-key cleanup, admitted outbound records and observable readiness | USB HID/browser/host client → EMOS keyboard owner → MOS/application | Keyboard guide; official MOS keyboard contract; BUILD-001 input checks | Native compile; keyboard host tests; local owner-only rules | Source priority, lock transitions, disconnect cleanup, queue/timeout/fault behavior | Exhaustive; none yet |
| A10-COV011 | P4 local-SD HTTP actor; `storage/local/http.cpp` and included storage helpers | Owns port-8080 HTTP server, FatFS file handles, upload staging, mount/card leases and request buffers | P4 SD clients → P4-local card | P4-SD guide; shared service storage boundary | LLVM/Cppcheck; filesystem host tests | Mount/unmount transaction, file/handle cleanup, concurrent request bounds, mutation recovery | Exhaustive for selected service; none yet |
| A10-COV012 | P4 staged WebDAV runtime; `storage/webdav/{runtime,connection,adapter,wire_backend}.*` | Owns port-8081 acceptor/worker, socket, parser vectors/arrays, spool/card lease, finite EMOS binding and file transaction state | Native file manager/WebDAV client → P4 runtime → EMOS `sdjob` → mainboard FatFS | Mainboard-SD protocol/guide; REMOTE-005 qualification | LLVM/Cppcheck; WebDAV adapter/wire host tests | Worker/socket/file lifetimes, bounds, cancellation, spool reservation, terminal closure, failure truth | Exhaustive; none yet |
| A10-COV013 | P4 embedded browser assets; `embedded_assets.cpp`, five embedded web files and generated IDF embedding | Serves immutable UI/parser/presenter/input assets; build optionally substitutes private reset URL in generated output | HTTP server → browser DOM/WebGL/client input | Browser asset README/protocol; native embedded-byte test | Browser harness, asset hashes, JS tests, Ruff/Semgrep where applicable | Source/generated correspondence, client error visibility, no hidden runtime authority | Exhaustive integration; none yet |
| A10-COV014 | EMOS mode coordinator; pinned `src/emos.c`, `emos_console.*`, console assembly boundary | Owns Legacy/ExCom mode transaction, VDU route, adapter prepare/ready/commit/recover, retained-display publication | CLI/application mode request → P4 console adapter or onboard VDP → MOS/application/user | Architecture; ExCom protocol; official VDU routing semantics | AgonDev warnings/link checks; C static tools where consumable | Complete transaction, rollback, public result mapping, retained state and re-entry | Exhaustive; none yet |
| A10-COV015 | EMOS admission/lease actor; `emos_admission.*` | Owns HELLO/POLL/DECIDE/RUNNING state, sequence/grant/link identities, deadlines and finite utility dispatch | Idle CLI/application context ↔ P4 control peer → `sdjob` | Mainboard-SD admission contract; REMOTE-005 | EMOS host/unit checks; Ruff/mypy for peer tools | State-machine completeness, wrap/exhaustion, mode/key changes, terminal closure | Exhaustive; none yet |
| A10-COV016 | EMOS keyboard/UART actor; `emos_keyboard.*`, `emos_keyboard_io.asm`, `uart.*` and ISR glue | Owns UART1, RX parser (246-byte layout), async TX, physical key state/modifiers, transport claim and fault recovery | P4 key/control records and onboard keyboard → MOS key APIs/applications | Keyboard guide; official keyboard/API docs; hardware input checks | AgonDev checks and EMOS tests; assembly review | IRQ/foreground synchronization, parser timeout, held-key cleanup, ownership transitions, error observability | Exhaustive; none yet |
| A10-COV017 | EMOS SD/telemetry gateways; `emos_sdlink.*`, `emos_telemetry.*` | Owns Core-RAM mailboxes, application/negotiated binding, request/reply readiness and telemetry publication | `sdserve`/`sdjob`/application gateway → P4 WebDAV/host clients; game → P4 diagnostics | Mainboard-SD wire contract; telemetry contract/evidence | EMOS unit/link checks; protocol host tests | Buffer/address validation, lock duration, dual reply ordering, reset/leave behavior | Exhaustive; none yet |
| A10-COV018 | Foreground `sdserve`; pinned `projects/sdserve` and shared `lib/sdapp` | Owns foreground session, FatFS handles, checked/fast upload state, recovery siblings, cached reply and path buffers | Host `sdcard.py` through P4/EMOS gateway → mainboard SD | Mainboard-SD protocol/guide; accepted checked/fast runs | AgonDev build; service host tests/sanitizers | File transaction durability, handle cleanup, duplicate/retry semantics, fast-mode truth | Exhaustive; none yet |
| A10-COV019 | Negotiated `sdjob`; pinned `projects/sdjob` plus shared SD engine | Owns finite descriptor, session, transfer path/state and recovery closure during a granted application job | P4 staged WebDAV → EMOS admission → mainboard SD | REMOTE-005 application transfer evidence; mainboard-SD protocol | AgonDev build; job/peer host tests | Grant validation, descriptor/path bounds, cancellation/terminal transaction, no retry of mutation | Exhaustive; none yet |
| A10-COV020 | AgonDev EMOS build integration; `port/mos-agondev.mk`, builder `projects/mos-port` selection/translation/runtime/link tools | Selects EMOS additions, transforms ZDS assembly, compiles/links image and records provenance | EMOS source profile → MOS image → hardware/production candidate | EMOS ownership docs; builder verification contracts | Fresh build/provenance validators; Python lint/type pass | Exact closure, scoped flags, generated-source ownership, workaround/removal conditions | Exhaustive integration; none yet |

## Build, host, fixture and reference coverage

| Coverage ID | Actor; files / symbols | Function and state/resources | Callers → consumers | Prior evidence / contract | Automated checks | Manual checks | Disposition / findings |
|---|---|---|---|---|---|---|---|
| A10-COV021 | Native P4 build authority; `build_p4.py`, `validate_p4_build.py`, `prepare_p4_clang_database.py`, `p4-profiles.json`, SDK/partition/lock inputs | Selects three buildable profiles, generates CMake, locks tools/dependencies, emits/validates artifacts and analysis database | Developer/audit → IDF/CMake/Ninja → P4 artifacts/analyzers | ADR-0023; BUILD-001; `BASELINE.md` | Unit tests, clean build, graph validator, manifest/hash checks | Stale-input prevention, dirty/identity policy, generated-file lifecycle, profile isolation | Exhaustive; none yet |
| A10-COV022 | Native profile branches | `p4-console` is exhaustive target; `p4-mos-recovery` and `p4-port008-nonrelease-qualification` are separately maintained recovery/diagnostic compositions | Operator/task → distinct firmware consumers | BUILD-001 inventory/design | Manifest uniqueness/forbidden-source tests; build checks | Confirm no diagnostic/recovery source or definition contaminates console | Exhaustive selection boundary; non-console runtime behavior outside audit |
| A10-COV023 | Historical hybrid build files; `vdp/platformio.ini`, `vdp/pio/*`, gated `vdp-pio.sh` and historical performance adapter | Reproduces identified pre-cutover evidence only | Explicit acknowledged historical invocation → r61 comparison | BUILD-001 rollback decision | Fail-closed wrapper test/review | Ensure routine docs/automation do not call it; no new history | Historical comparison; none yet |
| A10-COV024 | Maintained operator clients; `sdcard.py`, `keyboard.py`, `screen_text.py`, `p4sd.py`, reset and recovery clients | Issue bounded network/input/reset/recovery requests and retain receipts/journals | Operator/automation → P4/EMOS services → files/input/observations | Scripts index and current operating guides | Ruff/mypy staged by module; existing unit tests | Receipt truth, timeouts, partial I/O, safe paths, no inferred authority | Exhaustive active clients; none yet |
| A10-COV025 | Maintained automation/build/package tools; `bench_job.py`, native builders/validators, version/hardware validators, `reproduce_sd_components.py`, production verifier; r02 packager frozen | Runs detached jobs, produces identities/evidence, reconstructs accepted components and validates bundles | Developer/agent → build/test records → reviewer/operator | Build/version guides; production selection; notification contract | Python/shell tools and tests; policy rules | Failure propagation, subprocess/timeout cleanup, path/receipt validation, production-vs-development separation | Exhaustive maintained tools; none yet |
| A10-COV026 | Active validation fixtures/harnesses; native browser/codec, mode lifecycle, storage/WebDAV, keyboard, build graph, SD engine/job and notification tests | Deterministic host or eZ80 stimuli and result assertions; may substitute platform services | Test runner/operator → selected code → evidence | BUILD-001 validation and current task contracts | Inventory exact executed tests in A10-04; sanitizers where faithful | Detect test-only transformations, weak oracles, hidden modes/assets, false equivalence | Exhaustive active tests; none yet |
| A10-COV027 | LCD fixtures and implementation evidence; `tests/fixtures/lcd-color-bars`, `lcd-mode20-grid`, LCD-001 preserved source/receipts | Post-audit visual geometry/color/resource regression only | Later LCD redeployment → panel/browser/operator | LCD-001; A10-P01 supersession | No baseline source scan beyond exclusion checks | Preserve identities and required later regressions; do not infer baseline behavior from panel | Deferred delta; none yet |
| A10-COV028 | Retained historical fixture/helper families indexed in `scripts/README.md`, including visible-text, old UART/keyboard and game runners | Evidence replay or future bounded task input, not active audit execution | Owning historical task only → retained evidence | Scripts index and task records | Exclude explicitly from broad tool counts or label results historical | Promote only a demonstrated active dependency; do not revive silently | Outside exhaustive runtime; review only if current caller found |
| A10-COV029 | Official Agon documentation and tagged official MOS/VDP source | Defines mode, VDU, buffered command, keyboard, MOS API and system-variable semantics | Audit judgment → finding disposition | A10-ID04–ID06 | Link/existence checks only | Consult docs first; source only for insufficient/material detail; keep read-only | Reference; no findings assigned to upstream here |
| A10-COV030 | Production and installed comparisons | v0.1.0/r02, installed native candidate, exact hybrid r61 and their retained receipts | Bounded regression/resource comparison → audit interpretation | A10-ID08–ID11 | Existing hashes/receipts only | Never treat installed, production or Git HEAD identity as interchangeable | Historical/installed comparison; no exhaustive second audit |
| A10-COV031 | Compiled EMOS parallel facilities; pinned `emos_parallel.*`, `emos_parallel_engine.*`, `emos_parallel_io.asm`; fixed backend excluded from ordinary profile | Retains negotiation/data-plane state and hardware-facing assembly even though the accepted pre-LCD console uses UART ExCom | EMOS command/profile branches → PORT-008 consumers when selected | PORT-008 and EMOS profile selection; ordinary UART hardware baseline | AgonDev selection/link checks and EMOS parallel harnesses | Prove inactive-path isolation, retained state/resource cost, owner boundaries and no UART interference | Exhaustive compiled branch; none yet |
| A10-COV032 | Complete EMOS/MOS base image; pinned stock-shaped C/assembly selected by AgonDev (`mos*`, file/editor/sysvars, clock/timer, SD/FatFS, keyboard, interrupts, serial/SPI/I²C/RTC, startup and runtime) | Supplies CLI, application loading, MOS APIs, mainboard VDP/UART0, FatFS, interrupts, allocator/runtime and all base state into which Extender hooks are linked | User/application/hardware interrupts → EMOS additions and ordinary MOS consumers | Official MOS docs/source; EMOS lineage; AgonDev source profiles | AgonDev build/provenance/link checks; applicable EMOS tests and host static tools | Review Extender modifications/hooks and cross-boundary lifecycle exhaustively; use unchanged upstream internals as reference unless active interaction is material | Exhaustive project-owned EMOS integration; selected upstream boundary; none yet |
| A10-COV033 | P4 retained VDU parser and header-implemented subsystems textually compiled through `p4_console.cpp` → `p4_browser_vdp.cpp` → `video.ino`; `vdu_stream_processor.h`, `vdu*.h`, `buffers.h`, `buffer_stream.h`, `context.h`, `sprites.h`, screen/teletext/font/palette/compression and P4 compatibility headers | Owns parser command state/timeouts, buffer maps/streams/callbacks, contexts/stacks, bitmaps/sprites/tile layers, palette, VDU queries, audio-command state/stubs and event queue; much of this code has no separate translation unit | UART stream processor → drawing/controller/storage in-memory buffers → eZ80 queries and applications | Official VDU/buffer/audio contracts; PORT-003 and retained upstream boundary | The boot TU's actual compiler action; Clang/Cppcheck; parser/buffer/context/audio host tests and sanitizers | Command completeness, allocation/reference cycles, callback cleanup, mode-reset interaction, unsupported-hardware truth, parser timeout/recovery | Exhaustive selected textual closure; none yet |
| A10-COV034 | ESP-IDF/Arduino managed-component boundary; exact versions in `p4-profiles.json` and native `dependencies.lock`, including Arduino-ESP32, USB HID, Ethernet/HTTP/FatFS and transitive managed components | Supplies lifecycle, FreeRTOS, heap capabilities, networking, USB, filesystem and codec APIs/tasks linked into the image | Project wrappers/services → managed components/ESP-IDF → P4 hardware | ADR-0023; BUILD-001 dependency/config comparison; official ESP-IDF/component contracts when material | Lock/hash checks, compiler diagnostics, OSV inventory, linked-symbol/action inventory | Review project API assumptions, configuration, callbacks and resource ownership; do not line-audit untouched component internals absent an active path/finding | Selected third-party integration; none yet |
| A10-COV035 | P4 hardware/build configuration; `p4-console.sdkconfig`, `partitions.csv`, native CMake and profile definitions | Selects CPU/flash/PSRAM, heap/task/network/USB/filesystem facilities, partition sizes and compile-time feature coexistence | Native builder → ESP-IDF/components → every P4 service | Board/memory ADRs; BUILD-001 configuration ledger | Effective-config/hash comparison, build warnings, OSV/manifest checks | Identify resource-affecting options, disabled/unused features, partition/runtime mismatch and feature-combination assumptions | Exhaustive project configuration; none yet |

## Generated-code and state inventory

| Generated ID | Producer → output | Authority and audit treatment |
|---|---|---|
| A10-GEN01 | `build_p4.py` → fresh project/component CMake, build identity header, optional private embedded page | Disposable generated state. Manifest/profile and wrapper are authoritative; verify source substitution and reject hand edits. |
| A10-GEN02 | ESP-IDF/CMake/Ninja → dependency lock, sdkconfig, compile database, Ninja graph, ELF/map/segments/factory image | Canonical only as one validated build-output set. The compile database is eligible only after linked-graph validation. |
| A10-GEN03 | ESP-IDF embedding → browser asset objects/symbols | Compare source or generated private page bytes with the linked application; do not audit generated assembly as independent logic. |
| A10-GEN04 | EMOS profile plus AgonDev builder → prepared MOS worktree and translated GNU assembly | Source profile and pinned EMOS tree own selection; translator/provenance records must account for every generated input. |
| A10-GEN05 | AgonDev compiler/linker/runtime builder → objects, runtime archive, MOS ELF/map/bin/hex | Review actual selected/link actions and scoped workarounds; generated products are evidence, not editable source. |
| A10-GEN06 | Fixture generators → checked-in `.asm`, `.vdu` and `.bin` assets | Compare generator/source/binary identities when a fixture is active. LCD fixtures remain deferred and are not baseline mode owners. |

## Exact selected-source closure

The following mapping prevents a broad subsystem label from silently omitting a
linked P4 translation unit. It is derived from the frozen `p4-console` profile;
BUILD-001 proved that each entry contributes exactly one object to the linked
application archive.

| Coverage row | Exact selected P4 translation units |
|---|---|
| A10-COV001 | `video/extender/boot/p4_console.cpp`; `video/extender/port/p4_task_watchdog.cpp`; `vendor/ESP32Time/ESP32Time.cpp` |
| A10-COV003 | `video/extender/display/screen_facade_adapter.cpp`; `stock_native_access.cpp`; `stock_p4_service.cpp`; `stock_runtime_controller.cpp` |
| A10-COV004 | `vendor/vdp-gl/src/dispdrivers/vga2controller.cpp`; `vga4controller.cpp`; `vga8controller.cpp`; `vga16controller.cpp`; `vga64controller.cpp`; `vgabasecontroller.cpp`; `vgapalettedcontroller.cpp` |
| A10-COV005 | `video/extender/display/cursor_position_adapter.cpp`; `stock_scanline.cpp`; `video/extender/port/stock_render_utils.cpp`; `vendor/vdp-gl/src/canvas.cpp`; `codepages.cpp`; `displaycontroller.cpp`; `fabfonts.cpp` |
| A10-COV006 | `video/extender/display/presentation_snapshot_pool.cpp` |
| A10-COV007 | `video/extender/web/browser_video_provider.cpp` |
| A10-COV008 | `video/extender/network/browser_video_service_core.cpp`; `opaque_message.cpp`; `http_video_service.cpp` |
| A10-COV009 | `video/extender/network/wired_network_service.cpp` |
| A10-COV011 | `video/extender/storage/local/http.cpp` |
| A10-COV012 | `video/extender/storage/webdav/adapter.cpp`; `wire_backend.cpp`; `connection.cpp`; `runtime.cpp` |
| A10-COV013 | `video/extender/web/embedded_assets.cpp` |

The console transport and integrated keyboard implementation in A10-COV002 and
A10-COV010 are included textually by the selected boot translation unit rather
than separately compiled objects. Their headers/includes remain first-class
manual and policy-review inputs. A10-COV033 likewise covers the substantial
header-implemented VDU/parser closure compiled inside that boot object; counting
only `.cpp` actions would understate the audited source.

The frozen ordinary EMOS build adds ten Extender C units and three Extender
assembly units through `port/mos-agondev.mk`: admission, telemetry, SD link,
console, keyboard, UART flow/probe, mode coordinator, parallel facade/engine,
and console/keyboard/parallel I/O assembly. AgonDev combines them with its
explicit base list of 15 C units, 15 assembly units, FatFS, startup, allocator
and runtime archive. A10-COV014–A10-COV020 plus A10-COV031–A10-COV032 cover that
complete selected image; `sdserve` and `sdjob` are separate foreground images
under A10-COV018–A10-COV019.

## Active test and fixture inventory

| Test group | Current inputs and coverage rows | A10 treatment |
|---|---|---|
| Native build/selection | `native_p4_build_test.py`, `usb_source_selection_test.py`, build/graph validators | A10-COV021–COV023; execute as target-authority controls. |
| Mode, parser and retained drawing | `console_mode_lifecycle_test.py`, `mode_status_test.cpp`, `dsp_matrix_lifetime_test.*`, `fixed_conversion_test.cpp`, `video_takeover_test.py`, `video_asset_close_test.py` | A10-COV003–COV006 and COV033; first verify that each harness still selects the frozen code and documents substitutions. |
| Browser/video/network | `browser_bundle_test.py`, `browser_*` UI/C++/Python tests, `network/http_video_service_test.cpp`, detached compile and DevKit Ethernet host test | A10-COV006–COV010 and COV013; distinguish parser/codec checks from target task/socket behavior. |
| Keyboard/input | `browser_keyboard*`, `processed_keyboard*`, `remote_keyboard*`, `keyboard_hardware*`, `usb_boot_keyboard*`, `key_query_test.py` | A10-COV010 and COV016; classify hardware-named host seams versus physical results. |
| Storage/admission | `storage/*_test.cpp`, `sd_service_test.cpp`, `sd_peer.cpp`, `sd_keyboard_packets.cpp` plus pinned EMOS admission/SD-link/SD-app/SD-service/job suites | A10-COV011–COV012 and COV015–COV019; run only current-source, deterministic host cases in A10-04. |
| EMOS integration | Pinned `tests/test_emos_*`, UART/general-poll/ABI/VDU/profile checks and AgonDev firmware/provenance validators | A10-COV014–COV020, COV031–COV032; inventory compiled harness substitutions before crediting coverage. |
| Automation/receipts | `bench_job_test.py`, capture-analysis tests, installation/package/version validators | A10-COV024–COV026; do not import or execute hardware controllers as generic unit modules. |
| Physical eZ80 fixtures | mode-0 color bars and mode-20 static grid retained by LCD-001/BUILD-001; manual Nurples executable is external retained evidence | No A10-02/A10-04 physical execution. Bars/grid are post-audit LCD regressions under A10-COV027; Nurples is a bounded installed/hybrid comparison under A10-COV030. |
| Historical fixture families | visible-text, earlier UART/keyboard, Rally/game/performance helpers indexed as retained in `scripts/README.md` | A10-COV028 exclusion unless a current caller or finding demonstrates relevance. |

## Finding register

No findings were opened during A10-02; the original disposition cells above
preserve that pre-review freeze. A10-06 completed the findings set in
[FINDINGS.md](FINDINGS.md). The final crosswalk below is now authoritative for
review status without rewriting the frozen source-coverage description.

## A10-06 final coverage crosswalk

| Coverage ID | Final review disposition and findings |
|---|---|
| `A10-COV001` | Complete. `AUDIT-010-F002` mandatory browser resources and `AUDIT-010-F005` product-profile drift apply. Boot fail-stop paths otherwise remain explicit. |
| `A10-COV002` | Complete; no new finding. UART framing, sole-writer ownership, admission and fault containment remain coherent. |
| `A10-COV003` | Complete. `AUDIT-010-F001` mode transaction, `AUDIT-010-F002` display/snapshot coupling and `AUDIT-010-F012` parallel display ownership apply. |
| `A10-COV004` | Complete. `AUDIT-010-F001`, `AUDIT-010-F011`, `AUDIT-010-F012` and existing `FWBUG-001` apply. |
| `A10-COV005` | Complete. `AUDIT-010-F006`, `AUDIT-010-F008`, `AUDIT-010-F011`, `AUDIT-010-F012`, `FWBUG-001`, `FWBUG-007` and `FWBUG-012` apply. |
| `A10-COV006` | Complete. Slot ownership is bounded; mandatory eager lifetime is `AUDIT-010-F002`. |
| `A10-COV007` | Complete. Codec bounds and lease release are coherent; maximum persistent allocation policy is `AUDIT-010-F002`. |
| `A10-COV008` | Complete. Callback/one-viewer ownership is coherent; socket composition is `AUDIT-010-F004`. |
| `A10-COV009` | Complete. `AUDIT-010-F002`, `AUDIT-010-F003` and `AUDIT-010-F004` apply. |
| `A10-COV010` | Complete. Runtime input arbitration is coherent; repeated checksum implementation is `AUDIT-010-F013`. The frozen standalone USB diagnostic remains disposed, not a finding. |
| `A10-COV011` | Complete. File/lease lifecycle is coherent; global socket composition is `AUDIT-010-F004`. |
| `A10-COV012` | Complete. WebDAV partial startup is `AUDIT-010-F003`; global socket composition is `AUDIT-010-F004`; repeated SD checksum implementation contributes to `AUDIT-010-F013`. |
| `A10-COV013` | Complete; no finding. Embedded asset identity and browser error/status paths are accounted for. |
| `A10-COV014` | Complete; no finding. EMOS prepare/commit/recover and truthful committed-route publication remain coherent. |
| `A10-COV015` | Complete; no finding. Admission generations, deadlines, terminal proof and fail-closed exhaustion remain coherent. |
| `A10-COV016` | Complete; no finding. Keyboard/UART1 transitions and held-key cleanup remain coherent; documented silent-idle peer loss remains an accepted hardware limit. |
| `A10-COV017` | Complete. Gateway/mailbox ownership is coherent; repeated checksum primitive is `AUDIT-010-F013`. |
| `A10-COV018` | Complete. Transfer transaction behavior is coherent; implicit shared path policy is `AUDIT-010-F014`. |
| `A10-COV019` | Complete. Finite job/admission behavior is coherent; implicit shared path policy is `AUDIT-010-F014`. |
| `A10-COV020` | Complete; no finding. AgonDev selection, translation, link and provenance are identity-validated. |
| `A10-COV021` | Complete. Native graph authority remains sound; `AUDIT-010-F005` and `AUDIT-010-F012` apply to selected/maintained profile ownership. |
| `A10-COV022` | Complete. Profile isolation passes; `AUDIT-010-F005` and `AUDIT-010-F012` govern retained profile/qualification boundaries. Retired ZDI and frozen USB predecessors remain disposed, not findings. |
| `A10-COV023` | Complete. Historical gates are sound; stale maintained invocation is `AUDIT-010-F010`. |
| `A10-COV024` | Complete; no new client finding. Recovery implementation duplication is owned by `A10-COV021`/`022`, not attributed to client wrappers. |
| `A10-COV025` | Complete; no finding. Maintained automation propagates failure and separates production/development identities. |
| `A10-COV026` | Complete. Dynamic effect gap `AUDIT-010-F008`, browser oracle `AUDIT-010-F009` and shape validation `AUDIT-010-F011` apply. |
| `A10-COV027` | Deferred LCD delta. Post-audit redeployment must regress `AUDIT-010-F001`, `AUDIT-010-F002` and `AUDIT-010-F008`; no LCD-baseline finding is assigned. |
| `A10-COV028` | Complete exclusion. Historical helpers remain outside active runtime; exact helper/fixture duplicates are disposed in A10-05a rather than promoted to findings. |
| `A10-COV029` | Complete reference use; no finding assigned to read-only official authorities. Inherited origins are recorded in finding lineage. |
| `A10-COV030` | Complete bounded comparison. Retained mode20 behavior is consistent evidence for `AUDIT-010-F001` but not proof of its cause. |
| `A10-COV031` | Complete; no finding. Compiled EMOS parallel facilities remain isolated from the ordinary UART profile. |
| `A10-COV032` | Complete. Existing `FWBUG-008`, `FWBUG-009` and `FWBUG-010` apply; no duplicate A10 IDs were created. |
| `A10-COV033` | Complete. `AUDIT-010-F006`, `AUDIT-010-F007`, `FWBUG-006`, `FWBUG-007` and `FWBUG-012` apply. |
| `A10-COV034` | Complete selected-component integration. `AUDIT-010-F004` applies; incomplete OSV ecosystem coverage remains an explicit audit limit, not a clean result. |
| `A10-COV035` | Complete. `AUDIT-010-F004` socket limits and `AUDIT-010-F005` feature-definition composition apply. |
