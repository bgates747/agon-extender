# Shared P4 service boundaries

Extender owns the common implementations; consumers such as detached MAME own
their entry point, workers, device adapters and UI. Pin a committed source tree
and select only the required headers/translation units. This development boundary
has host lifecycle tests and a console compile check, **not detached-runtime or
hardware qualification**. Selected production is unchanged; source checks do not identify the currently
installed peer firmware. Consult the machine-local bench receipt for that.

## Consumer-specific code stays with the consumer

The [repository ownership boundary](../OWNERSHIP.md) is mandatory. Extender owns
reusable services and their generic tests. The TRS-80 project alone owns MAME,
TRS-80 device/guest behavior, its framebuffer and input adapters, and its runtime
composition. Extender must not import those implementations or require that
project to build. Shared APIs may accommodate its needs without encoding
TRS-80 machine semantics. Consumer qualification remains in the consumer's
repository; coordination notes here are not a second implementation tree.

## DevKit Ethernet / DHCP

Include `vdp/video/extender/network/devkit_ethernet.hpp` and add `vdp/video` to the
include path. This header is C++17 and requires Arduino-ESP32's `ETH` and `Network`
components (current build: Arduino 3.3.11 with ESP-IDF 5.5.5). It does not include
VDP, EMOS, HTTP server, USB input, SD or web-asset code. No additional Extender
translation unit is required for this boundary.

`agon::extender::network::DevkitEthernet` provides:

| Method | Contract |
|---|---|
| `start(callback, context)` | Claim the single physical Ethernet owner; register events and begin IP101/RMII with DHCP. True means startup accepted, not an address lease. A second active owner is rejected. Repeating start on the same owner is a no-op. |
| `stop()` | Unregister events and end the owned Ethernet peripheral. Waits for an in-flight callback; queued events from previous registrations are ignored. No-op for an inactive instance. |
| `hasIP()`, `linkUp()` | Current underlying Arduino interface state; meaningful for the active owner |
| `lease()` | Address/netmask/gateway/DNS strings; inspect after GotIp/hasIP, not before startup |

Events: Started, Connected, GotIp, LostIp, Disconnected and Stopped. The callback
signature is `void(void *context, DevkitEthernet::Event) noexcept`. It runs on the
Arduino event task and must only enqueue state/notify a worker. **Do not call
start/stop, block on the owner worker or start/stop HTTP from that callback.**
The caller serializes lifecycle calls on an instance. One object owns the
peripheral; direct external `ETH.begin/end` calls violate this ownership contract.

The consumer initializes Arduino as appropriate for its build before calling
start. An IDF `app_main`/Arduino-component build must establish that initialization
explicitly; this header does not call `initArduino` or create `setup/loop`.
The consumer's worker reacts to current link/address state and owns any server
startup/retry/shutdown. Stop dependent services before stopping the link. The
header does not guarantee DHCP time, start application servers, select routes,
register UI assets, or prescribe reconnect behavior for those servers.

The maintained console now uses this same header from `WiredNetworkService`.
Its existing worker and VDP-specific routes stay there. Detached MAME should
**not** import WiredNetworkService just to initialize Ethernet.

Hardware selection preserves the reviewed Olimex DevKit Rev D1 IP101 settings:
PHY address1, MDC31, MDIO52, PHY power51 and external RMII clock. No static IP is
embedded. This is not a P4-PC board backend. Consult the fixed-function resource
[audit](tasks/SETUP-006/SETUP-006.4-wiring-design/electrical-requirements.md) before
combining hardware services on a different board.

## Storage boundary

The [P4 SD service](p4-sd.md) is independently callable through
`local_sd::startHttp()` after network readiness. Its current lifecycle is
process-long: no stop/unmount API or image lease interface is provided. Starting
Ethernet does not start storage. A detached consumer's server composition must
avoid duplicate port/control-socket assignments and budget lwIP sockets.

The existing HTTP server serializes only its own filesystem requests. Do not
combine it with mounted MAME images, including read-only guest mounts, yet. A filesystem/image ownership
interface must precede that integration; this Ethernet extraction supplies none.
The public header exposes startHttp only; mount state and HTTP task telemetry
are private. Use HTTP status for card readiness, not direct access from another
worker. Raw HID delivery remains separate work. The shared browser transport below
accepts a consumer-owned provider. No complete MAME platform composition is implied by this header.

## Source consumption and checks

Use a detached/pinned checkout; keep the pin/hash receipt in the consuming
project. Do not silently update to mutable Extender HEAD or copy this header into
a separately maintained fork. The TRS-80 owner recorded an Arduino/MAME/Ethernet/SD link pass with unchanged
common source at 2ecd55b8: 13,755,248-byte binary, 924,816 bytes of partition
headroom. This does not establish runtime heap, stack or DHCP behavior. The
consumer owns those measurements and its framework composition.
Common-interface changes require both consumers' review and independent checks.

Linux lifecycle checks:

```sh
g++ -std=c++17 -Wall -Wextra -Werror -pthread \
  -I tests/network/fakes -I vdp/video \
  tests/network/devkit_ethernet_test.cpp -o /tmp/devkit-ethernet-test
/tmp/devkit-ethernet-test
```

Fakes verify pin arguments, exclusive ownership, event mapping, failure/restart,
late callbacks and waiting for an active callback during stop. They do not model
PHY behavior, DHCP, Arduino task scheduling or physical cable reconnection.
Console PlatformIO compilation checks framework integration only. A future
identified firmware build and authorized hardware run remain necessary before
promoting this source change; do not flash a local unversioned compile as r57.

Owning work: [TRS-80 integration](tasks/TRS-80-003.md). The TRS-80 project owns its
SHARE-01 source-consumption/build contract and its MAME adapter implementation.


## HTTP / browser-video transport

Include `vdp/video/extender/network/http_video_service.hpp`. Compile these three
translation units, with `vdp/video` on the include path:

1. `extender/network/http_video_service.cpp`
2. `extender/network/browser_video_service_core.cpp`
3. `extender/network/opaque_message.cpp`

The IDF component dependencies are `esp_http_server`, `esp_timer`, `lwip` and
`log` plus normal C++ runtime support. Enable `CONFIG_HTTPD_WS_SUPPORT` and
`CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT`. Current checks use IDF 5.5.5.
No console, VDP, EMOS, Arduino Ethernet, local SD or embedded console asset
translation units are needed. The optional dispatch-timing define adds its
existing diagnostic dependency; detached consumers leave it disabled.

Construct `network::HttpVideoService` with an `OpaqueMessageProvider&`, then call
`startServer(assets, count, config)` with consumer-owned `web::EmbeddedAsset`
metadata. The server adds GET asset routes and `/video`. It never initializes
Ethernet or SD. The consumer must establish network readiness and serialize
start, stop and periodic `poll()` calls on its own worker. There is no internal
pump thread; a frame credit notifies the console worker through an override,
whereas the base class waits for the consumer's next poll.

Provider, asset table, asset strings/bytes, and the complete service object must
remain alive until `stopServer()` succeeds. Provider acquisition is nonblocking;
leases remain immutable through send completion and receive exactly one release.
Start/stop/poll must not be invoked from HTTP callbacks. Failed stop retains its
server/context and marks the service faulted: retain the object and retry from
its owner. Destruction with a live server aborts rather than allowing callbacks
into a destroyed object. Successful stop permits restart.

The base adapter sends provider segments unchanged (raw EVF1 for the current
TRS-80 pattern provider), with one outstanding `frame` text credit and one viewer.
A replacement viewer closes the previous viewer; old queued work cannot target
its replacement. Failed queue/send/disconnect releases the pending lease. The
shared complete-or-error socket override retains the IDF 5.5.5 positive-short-write
workaround. Finite asset responses request connection close to free HTTP slots.
EVF1 encoding, rendering, pacing and browser UI remain the consumer's responsibility.
The normal Extender console uses this same adapter and retains its existing codec
negotiation/compression, routes and worker through overrides; detached consumers
need not import those facilities.

| Server | Listen port | IDF control port | Client sockets | Internal sockets |
|---|---:|---:|---:|---:|
| Video defaults | 80 | 32768 | 7 | 3 |
| P4 SD service | 8080 | 32769 | 2 | 3 |

Each server needs a distinct listen and control port. IDF's per-server admission
check does **not** reserve enough global sockets for other servers. Both defaults
together require capacity for 15 sockets, plus other live lwIP users. The console's
retained `CONFIG_LWIP_MAX_SOCKETS=10` is not a sufficient worst-case combined budget.
Detached consumers must explicitly raise their framework budget or reduce client
limits and verify concurrent asset/video/SD traffic. This extraction does not
silently change console socket configuration or claim that capacity qualified.

Checks (from repository root):

```sh
bash tests/network/run_http_video.sh
.venv/bin/python tests/video_asset_close_test.py
.venv/bin/pio run -d vdp -e p4-console
.venv/bin/python tests/network/compile_http_video_detached.py
```

The first compiles the actual adapter against HTTP/socket fakes with ASan/UBSan;
legacy takeover/containment test entry points invoke it too. The last compiles a
minimal detached consumer translation unit against actual P4/IDF headers after
the console build; it is not an independent consumer firmware link or runtime
qualification. TRS-80 owns its whole-firmware link and physical integration check.
Extraction evidence: [TRS-80-004](tasks/TRS-80-004.md).
