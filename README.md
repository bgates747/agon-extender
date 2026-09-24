# Agon Extender

Agon Extender adds an ESP32-P4 coprocessor to an Agon computer. Its **Extended
Display Processor (EDP)** runs on an Olimex ESP32-P4-DevKit; **Extender MOS
(EMOS)** runs on the Agon's eZ80. The aim is to extend the machine's display,
input and network capabilities while retaining compatibility with existing
Agon software.

**This project is still very much in its teething stage. The repository is,
frankly, a horrible mess.** Working code sits alongside experiments, superseded
implementations, diagnostic builds and long development records. Features,
interfaces and build instructions are still changing. There is working hardware
and useful code here, but substantial cleanup, compatibility work and testing
remain. Public source availability does not mean a finished product or a
ready-to-install firmware release.

## P4-PC board documentation and examples

Start with the [Olimex ESP32-P4-PC reference library](docs/hardware/esp32-p4-pc/README.md):
manual, schematic, design files, searchable text, example instructions and pinned
provenance. Its index also identifies the complete local upstream software clone.

## Where the actual code lives

Both firmware repositories are public. Start here to find the component you
want to build:

| Component | Source and build entry point |
| --- | --- |
| **EDP / ESP32-P4 firmware** | This repository's [vdp/](vdp/) is the PlatformIO project. [vdp/platformio.ini](vdp/platformio.ini) defines its targets; **`p4-console`** is the current integrated console target. Its entry point is [p4_console.cpp](vdp/video/extender/boot/p4_console.cpp). |
| **Extender-specific P4 implementation** | [vdp/video/extender/](vdp/video/extender/): display, transport, network, input, storage and browser code. The adapted stock VDP code is in [vdp/video/](vdp/video/); retained library sources are in [vdp/vendor/](vdp/vendor/). |
| **EMOS / eZ80 firmware** | Separate [agon-emos repository](https://github.com/bgates747/agon-emos). Maintained firmware is in [src/](https://github.com/bgates747/agon-emos/tree/main/src); its [root Makefile](https://github.com/bgates747/agon-emos/blob/main/Makefile) selects the EMOS build profile. |
| **Agon mainboard SD server** | Maintained in the EMOS development checkout at `projects/sdserve/`, including its source and Makefile. **This directory and the newer EMOS SD gateway have not yet reached public `main`.** See the availability note below. |
| **Host-side SD client** | [scripts/sdcard.py](scripts/sdcard.py) in this repository. It is a Python command-line client for the running mainboard SD service. |
| **Browser display** | [vdp/video/extender/web/](vdp/video/extender/web/): HTML, CSS and JavaScript. These assets are embedded in the P4 firmware; there is no separate npm build. |
| **Small samples to try without our hardware** | [TRS-80 sample bin](docs/tasks/TRS-80-002/bin/README.md): browser demo, SD transport lab and a probe of the upstream TRS-NET server, each with instructions and source. |

## Building the P4 firmware

Use **`p4-console` explicitly**. The default environment in `platformio.ini`
is still `p4-canary`, an earlier bring-up target. Many other named environments
are isolated diagnostics or historical experiments; their presence does not
make them alternative supported firmware configurations.

The current build uses PlatformIO with the Arduino/ESP-IDF hybrid framework.
The repository pins pioarduino `55.03.311` and Arduino-ESP32 `3.3.11`. The
maintainer's Linux build environment uses PlatformIO Core `6.1.19`. From a
POSIX shell with Git and Python 3 available:

```sh
git clone https://github.com/bgates747/agon-extender.git
cd agon-extender
python3 -m venv .venv
.venv/bin/python -m pip install platformio==6.1.19 PyYAML==6.0.3
./scripts/vdp-pio.sh run -e p4-console
```

The [wrapper](scripts/vdp-pio.sh) selects the root `.venv/bin/pio` and runs it
inside `vdp/`. PlatformIO downloads the selected compiler/framework packages;
allow space and time for the first build. Additional documentation/validation
tools have dependencies in [requirements-dev.txt](requirements-dev.txt).
Fresh-machine setup is still rough, and the commands above are the current
compile entry point rather than a complete installation procedure.

Build outputs are under `vdp/.pio/build/p4-console/`, including `firmware.bin`,
`firmware.elf` and `firmware.factory.bin`. An ordinary build without an explicit
build identity carries **`UNVERSIONED-DO-NOT-DEPLOY`**. For an identified bundle
from clean, committed source, use the existing builder with a new output path:

```sh
.venv/bin/python scripts/prepare_console.py --output agents/builds/console-local
```

[prepare_console.py](scripts/prepare_console.py) builds and records binary,
source and dependency identities. It does not flash a board. A successful build
alone does not qualify its firmware for a particular assembly; consult the
[version/build conventions](docs/versions/README.md) and the relevant physical
acceptance record before deployment.

### Which files actually get compiled?

The definitive list for this target is
[p4-console-source-selection.json](vdp/pio/p4-console-source-selection.json).
It names the compiled project/library files, embedded browser assets and
excluded implementations. This matters: several generations of renderer and
transport code coexist in the tree.

[select_sources.py](vdp/pio/select_sources.py) turns that list into the hybrid
build's generated CMake inputs. Edit the maintained source and selection files;
generated `vdp/CMakeLists.txt`, `vdp/video/CMakeLists.txt`, component manifests
and `.pio/` outputs are disposable. Start tracing execution at
[p4_console.cpp](vdp/video/extender/boot/p4_console.cpp), which includes the
retained browser-VDP boot code and
[console transport](vdp/video/extender/transport/console_hardware.inc).

## Building EMOS and the SD application

EMOS is built separately from the P4 firmware. Its current AgonDev build uses
[mos-agondev](https://github.com/bgates747/mos-agondev) for source preparation,
assembly translation and linking, and the
[AgonDev toolchain](https://github.com/AgonPlatform/agondev). The maintained
EMOS source remains in `agon-emos`; generated builder worktrees are disposable.

Start with [mos-agondev/STARTHERE.md](https://github.com/bgates747/mos-agondev/blob/main/STARTHERE.md)
for the toolchain and builder setup, supplying the EMOS checkout to its
`--agon-mos` source option. That builder currently requires Python 3.14 or newer.
EMOS's own Python dependencies are listed in its
[requirements-dev.txt](https://github.com/bgates747/agon-emos/blob/main/requirements-dev.txt).
Once the local paths and Python environments are configured, the EMOS
checkout's own Makefile provides the product build:

```sh
# Run from the agon-emos repository root.
make PYTHON=.venv/bin/python firmware-check
```

The [EMOS Makefile](https://github.com/bgates747/agon-emos/blob/main/Makefile)
defines `MOS_AGONDEV_ROOT`, `MOS_WORKTREE` and `AGONDEV_TOOLCHAIN` overrides.
With its default layout, firmware outputs are in
`../mos-agondev/projects/mos-port/bin/`. For identified builds and automated
qualification, see
[prepare_boot_review.py](https://github.com/bgates747/agon-emos/blob/main/scripts/prepare_boot_review.py);
that workflow also requires a configured Fab emulator.

**SD source availability:** as checked on 13 September 2026, public EMOS
`main` is [e48d431](https://github.com/bgates747/agon-emos/commit/e48d4312907882ee77ab971a3bce956f7a5a8447).
Its declared version is v0.1.13; it does not contain `src/emos_sdlink.c` or
`projects/sdserve/`. The [accepted SD combination](docs/qualification/mainboard-sd/2026-09-13.md)
uses the newer EMOS v0.1.14 and `sdserve` v0.1.0. Those later EMOS commits have
not been pushed to public `main`, so a fresh public clone cannot yet build the
complete mainboard SD service.

When using an EMOS checkout that contains that newer source, the SD server is
an ordinary application built separately. With AgonDev on `PATH`, from that
EMOS repository:

```sh
make -C projects/sdserve
```

This produces `projects/sdserve/bin/sdserve.bin`. In that checkout,
`projects/sdserve/README.md` covers explicit toolchain paths, identified builds
and its EMOS requirements; `scripts/prepare_sdserve.py` creates identified
application bundles.
Use the [mainboard SD operating guide](docs/mainboard-sd.md) for the host client
and service lifecycle. Compiling this application alone does not install the
EMOS gateway or matching P4 firmware it needs.

## What works, and what is still developing

Native USB keyboard input and the ordinary ExCom console remain working
foundations. A separate [host keyboard API](docs/remote-keyboard.md) now passes
bounded physical EMOS input, CLI editing/command execution and SD coexistence
checks in a provisional P4 build. It joins the retained processed-key path,
with paced input, retry protection and physical-keyboard takeover. Attended
review and remaining qualification are recorded under [REMOTE-002](docs/tasks/REMOTE-002.md). Browser input
remains deferred. The [Pi reset circuit](docs/bench-reset.md) is independent of
Extender control. [TODO.md](TODO.md) owns the remaining queue.

Status as of **13 September 2026**. These are scoped development results on the
current bench, not promises of compatibility with every Agon or P4 board.

| Area | Current state |
| --- | --- |
| **UART console and browser video** | Ordinary Exclusive Compatible (ExCom) console, retained VDP rendering and browser presentation work on the current assembly. Graphics performance, compatibility and wider qualification remain active work. |
| **Keyboard** | A directly attached native USB keyboard works through P4 and EMOS. Browser keyboard capture is retired/deferred; the current browser page displays video only. |
| **Agon mainboard SD card** | Foreground `sdserve` supports listing, reads, staged writes, verification and recoverable replacement over Ethernet/P4/EMOS. Ten physical transfer cycles and native-keyboard interruption/restart checks passed for the [recorded builds](docs/qualification/mainboard-sd/2026-09-13.md). The service runs in Legacy mode and at different times from games. |
| **P4 DevKit microSD card** | A separate, planned storage service in [PORT-007](docs/tasks/PORT-007.md). The mainboard SD milestone does not implement P4-card access. |
| **Parallel transport and hardware** | Experimental work exists, but parallel transport and the fuller hardware circuit remain on hold. Current console work uses the UART path; historical throughput figures are not a current product guarantee. |
| **P4/network audio** | Deferred under [PORT-004](docs/tasks/PORT-004.md). Browser video does not imply working streamed audio. |
| **TRS-OS, MicroPython and additional peripherals** | TRS-OS integration is under investigation. MicroPython, MIPI display outputs and optional wireless support remain future work. |

The current physical reference is **Agon Light 2 + Olimex ESP32-P4-DevKit
Rev D1**, using the [r03 UART harness](hardware/designs/light2-harness-r03/README.md)
and its documented USB keyboard addition. The drawing does not yet describe
the complete current assembly, and full electrical/reset qualification remains
unfinished. Read the stated limits before copying wiring or deploying firmware.

EMOS owns the eZ80-side transport, input selection and operating-mode changes.
Applications use its interfaces rather than taking over the active UART/GPIO
resources. The current network services use plain HTTP/WebSocket on a trusted
LAN and have no authentication. The SD endpoint can replace files within the
root selected when `sdserve` starts; the development startup permits the whole
mainboard card. Its file protocol does not provide remote shell execution.

## Finding your way through the rest

1. [TODO.md](TODO.md) is the authoritative unfinished-work list.
2. [Architecture](docs/architecture.md), [component ownership](OWNERSHIP.md)
   and [protocols](docs/protocols/) explain how the firmware pieces fit together.
3. [TRS-OS community guide](docs/tasks/TRS-80-002/COMMUNITY-GUIDE.md) maps the
   Discord discussion to EMOS, EDP, upstream tools and the sample kits.
4. [Task records](docs/tasks/README.md) contain experiments, generators and
   evidence, including useful code that has not yet found a permanent home.
   Check their status and dates: old plans and old test passes describe their
   recorded revisions, not necessarily today's implementation.
5. [Qualification records](docs/qualification/README.md) and
   [publication-readiness findings](docs/public-release-readiness.md) document
   what has been checked and where the setup still falls short.

6. [MOS/VDP firmware bug register](docs/firmware-bugs.md) records reproduction
   conditions, mainboard versus Extender evidence, and fix dispositions.

## License and upstream work

Agon Extender is distributed under **GPL-3.0-only**, except where individual
files or third-party components carry their own compatible license notices.
See [LICENSE](LICENSE) for the full text and [LICENSING.md](LICENSING.md) for
the licensing and attribution policy.

The port builds on the [official Agon VDP](https://github.com/AgonPlatform/agon-vdp)
and FabGL/vdp-gl. Original MIT and GPL-family notices and upstream attribution
remain applicable to their respective sources.
