# Shared P4 service boundaries

Extender owns the common implementations; consumers such as detached MAME own
their entry point, workers, device adapters and UI. Pin a committed source tree
and select only the required headers/translation units. This development boundary
has host lifecycle tests and a console compile check, **not detached-runtime or
hardware qualification**. Selected production and installed r57 are unchanged.

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
combine it with writable mounted MAME images yet. A filesystem/image ownership
interface must precede that integration; this Ethernet extraction supplies none.
Raw HID delivery and shared browser-provider interfaces also remain separate
work. No complete MAME platform composition is implied by this header.

## Source consumption and checks

Use a detached/pinned checkout; keep the pin/hash receipt in the consuming
project. Do not silently update to mutable Extender HEAD or copy this header into
a separately maintained fork. The TRS-80 owner evaluates Arduino component
closure, flash size and heap use before deciding its final framework composition.
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
