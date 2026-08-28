# PORT-003 Phase F boot closure

Generated from `boot-closure.yaml` by `scripts/render-boot-closure.py`; do not edit.

## Claim boundary

1. The image is the retained official VDP parser and lifecycle with bounded P4 bindings, not a demonstration parser.
2. Phase F qualifies display and browser presentation only; an included command body is not thereby qualified.
3. PORT-008 replaces the disconnected Stream with physical parallel ingress without changing parser ownership.

## Lifecycle

| ID | Disposition | Actor | Phase F operation | Failure rule |
|---|---|---|---|---|
| `setup-presentation-storage` | add | P4 setup task | Allocate the fixed presentation snapshot pool before the display controller can publish. | Report over USB diagnostics and continue retained display execution without browser frames. |
| `setup-watchdogs` | replace-binding | P4 setup task | Preserve the official no-IDLE-watchdog intent and 400-millisecond delay through ESP-IDF's hook-aware reconfiguration path; leave the official non-P4 calls unchanged. | Report over USB diagnostics and stop P4 startup rather than continue with stale IDLE hooks or silently change watchdog policy. |
| `setup-debug` | replace-binding | P4 setup task | Use the DevKit USB diagnostics path without assigning stock UART0 GPIO 3 and GPIO 1. | Diagnostic failure cannot disable retained VDP execution. |
| `setup-display` | retain-adapted | P4 setup task | Preserve call order and official mode fallback through the accepted P4 screen facade. | Preserve official mode failure/fallback; snapshot publication remains independently optional. |
| `setup-ingress` | replace-binding | P4 setup task | Construct the unchanged processor on a disconnected project-owned Arduino Stream for Gate F. | Reads remain empty; writes are discarded and counted; no fabricated startup or response byte exists. |
| `setup-process-task` | retain-profiled | P4 setup task | Preserve the official process task, stack size, priority, and selected core unless P4 evidence forces a reviewed profile change. | Task creation failure is reported and makes Gate F fail. |
| `setup-audio` | defer-binding | P4 setup task | Do not initialize or link the classic physical SoundGenerator; select the PORT-004 logical scheduler when available. | Phase F exposes no audio qualification and may not make an audio command reachable through physical ingress. |
| `setup-boot-screen` | retain | P4 setup task | Render the official version banner through the retained parser after processor construction. | A missing browser does not alter boot-screen rendering or logical state. |
| `setup-network` | add | PORT-006 P4 network service | Start onboard Ethernet, DHCP, HTTP, and the video WebSocket after retained display startup. | Report link or service failure over USB diagnostics; do not stop parser or logical frame service. |
| `loop-idle` | retain | Arduino loop task | Preserve the official idle loop; network work runs in its owning ESP-IDF tasks. | none |
| `process-input-acquisition` | replace-binding | P4 process task | Bind to the PORT-005 processed-event seam; the Phase F adapter owns no physical device and yields no events. | No physical PS/2 source, input task, or fabricated event may enter the image. |
| `process-startup-handshake` | retain | P4 process task | Preserve General Poll parsing and the initialised gate; disconnected Gate F ingress waits indefinitely without blocking display or network tasks. | Do not synthesize General Poll or mark the EDP initialized. |
| `process-terminal` | omit-adapter | P4 process task | Keep normal parser dispatch active and make the accepted unsupported terminal/console path explicit without constructing FabGL Terminal. | Exact application-visible handling remains outside Gate F and must not be described as compatible. |
| `process-vdu` | retain | P4 process task | Preserve the official parser call and byte vocabulary after startup initialization. | Parser or command-semantic rewrites are a Phase F stop condition. |

## Subsystem closure

| ID | Disposition | Owner | Phase F binding | Later owner |
|---|---|---|---|---|
| `official-parser` | retain | agon-vdp | Compile the official header-defined command closure; use only bounded target guards/adapters named below. | — |
| `contexts-buffers-and-screen` | retain-adapted | agon-vdp plus PORT-003 | Preserve official state and behavior over the already accepted P4 facade and logical controller. | — |
| `rtc` | retain | agon-vdp | Retain ESP32Time and the official RTC packet/state surface; Gate F does not qualify return delivery or clock authority. | operating-mode qualification |
| `transport` | replace-binding | PORT-008 | A disconnected Stream proves boot closure and counts discarded writes; it supplies no bytes. | PORT-008 parallel ingress and later reverse UART |
| `input` | replace-binding | PORT-005 | Compile a no-device processed-input seam sufficient for parser linkage and display-local cursor state; acquire no hardware input. | PORT-005 |
| `audio` | defer-binding | PORT-004 | Keep vendored parser/runtime source visible but do not select classic physical soundgen or claim audio behavior in Gate F. | PORT-004 logical scheduler and network sink |
| `updater` | omit | none in Extender v1 | Exclude ESP OTA command handling from the selected parser build under the accepted maintenance carveout. | PORT-006 owns project network update independently |
| `transfers` | omit | none in Extender v1 | Exclude Intel HEX and YMODEM maintenance handlers; do not retain their UART0 or PSRAM behavior accidentally. | — |
| `terminal-console-zdi` | omit | none in Extender v1 | Exclude Terminal construction, ZDI GPIO access, printer capture, and console forwarding under the accepted maintenance carveout. | — |
| `debug-diagnostics` | replace-binding | P4 platform and PORT-006 | Preserve disabled official debug calls while routing mandatory Extender link/lease/failure diagnostics through USB without stock UART pin assignments. | DIAG-001 for durable crash records |
| `wifi` | omit | PORT-006 if later selected | Remove the unused upstream WiFi include; wired Ethernet only. | optional MOD-WIFI-ESP8266 work outside Phase F |

## Nonclaims

1. No audio behavior or output.
2. No keyboard or mouse acquisition, forwarding, or packet behavior.
3. No updater, terminal, console, printer, ZDI, Intel HEX, or YMODEM compatibility.
4. No parallel ingress, reverse UART, General Poll exchange, EMOS mode transition, or sysvar qualification.
5. No physical hardware or deployment qualification.
