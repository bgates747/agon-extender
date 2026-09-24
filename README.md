# Agon Extender

Agon Extender adds an ESP32-P4 coprocessor to an Agon computer. **Extended
Display Processor (EDP)** runs on P4; **Extender MOS (EMOS)** replaces MOS on the
eZ80 and owns display routing, keyboard admission and Extender transports.

This is a working development project, not a general ready-to-install release.
The tree includes retained experiments and diagnostic targets. A source checkout,
a successful compile and a deployed/qualified combination are different things.

## Start here

1. **Using an existing installation:** [operator and external-agent entry point](docs/using-extender.md).
2. **Transferring files:** [mainboard SD guide](docs/mainboard-sd.md), including the
   foreground `EMOS sdserve` EMOSlet and paired `--fast` option.
3. **Building:** [component build guide](docs/building.md). Select `p4-console`
   explicitly; PlatformIO's default target is a historical bring-up target.
   The base target does not yet reconstruct all deployed candidate overlays.
4. **Unfinished work:** [TODO](TODO.md). Task records preserve dated evidence;
   they are not automatically current operating instructions.

## Capabilities and limits

Current documentation review: **24 September 2026**. Results apply to the
recorded builds and bench, not every Agon/P4 combination.

| Capability | Current status and authority |
|---|---|
| Legacy / Exclusive Compatible (ExCom) display routing | EMOS selects mainboard VDP or EDP. Retained VDP rendering and browser output work; compatibility and performance limits remain. [Architecture](docs/architecture.md), [bug register](docs/firmware-bugs.md). |
| Physical, browser and agent keyboard input | P4 USB input, explicit browser capture and paced host automation are implemented. All require EMOS to have admitted Extender input. Physical input takes priority; browser capture overrides automation. [Keyboard guide](docs/remote-keyboard.md). |
| Browser video and observation | P4 serves the page and final rendered pixels, with full-frame RLE2 by default. Browser output can slow gameplay; presented fps is not application-loop or native-rendering throughput. [Video contract](docs/protocols/browser-video.md). |
| Agon mainboard SD | Foreground `EMOS sdserve [--fast] /` supports listing, reads and recoverable staged replacement. Normal mode verifies whole files; fast mode omits those verification passes. EMOSlet installation and latest scoped physical checks: [operating guide](docs/mainboard-sd.md). It does not run alongside a game. |
| Remote reset | An optional Pi-hosted bridge pulses the Agon's reset circuit; the browser button uses that bridge. This is not P4-native reset or power cycling. [Reset guide](docs/bench-reset.md). |
| Future / deferred | P4-local SD: [PORT-007](docs/tasks/PORT-007.md). Audio: [PORT-004](docs/tasks/PORT-004.md). Parallel transport, MicroPython and physical video outputs remain separate work; see [TODO](TODO.md). |

Network services use plain HTTP/WebSocket on a trusted LAN, without
authentication. The SD root passed to `sdserve` bounds access; `/` exposes the
whole mainboard card. The SD wire API does not execute programs. Agent keyboard
control can issue MOS commands only after its input path is already admitted.

The current physical reference is **Agon Light 2 + Olimex ESP32-P4-DevKit Rev D1**.
The [r03 UART harness](hardware/designs/light2-harness-r03/README.md) and its
USB addition are not a complete qualification of every as-built circuit.
The planned **ESP32-P4-PC** has a separate [reference library](docs/hardware/esp32-p4-pc/README.md)
with manuals, schematics, provenance and upstream example-clone instructions.
Do not treat the planned board as the installed DevKit.

## Source ownership and further reading

| Component / subject | Entry point |
|---|---|
| Integrated P4 console | [vdp/platformio.ini](vdp/platformio.ini), [p4_console.cpp](vdp/video/extender/boot/p4_console.cpp), [source selection](vdp/pio/p4-console-source-selection.json) |
| EDP / adapted VDP | [vdp/video/extender](vdp/video/extender/), [vdp/video](vdp/video/), [retained libraries](vdp/vendor/) |
| EMOS and SD listener | [agon-emos](https://github.com/bgates747/agon-emos), including `src/` and `projects/sdserve/` |
| Host SD client | [scripts/sdcard.py](scripts/sdcard.py) |
| Embedded browser assets | [web component](vdp/video/extender/web/README.md); no separate npm build |
| Design and responsibility | [architecture](docs/architecture.md), [ownership](OWNERSHIP.md), [protocols](docs/protocols/) |
| Qualification and known faults | [qualification index](docs/qualification/README.md), [firmware bugs](docs/firmware-bugs.md), [publication review](docs/public-release-readiness.md) |
| Evidence and research | [task conventions](docs/tasks/README.md), [TRS-OS community guide](docs/tasks/TRS-80-002/COMMUNITY-GUIDE.md), [hardware-free samples](docs/tasks/TRS-80-002/bin/README.md) |

## License and upstream work

Agon Extender is distributed under **GPL-3.0-only**, except where individual
files or third-party components carry their own compatible license notices.
See [LICENSE](LICENSE) for the full text and [LICENSING.md](LICENSING.md) for
the licensing and attribution policy.

The port builds on the [official Agon VDP](https://github.com/AgonPlatform/agon-vdp)
and FabGL/vdp-gl. Original MIT and GPL-family notices and upstream attribution
remain applicable to their respective sources.
