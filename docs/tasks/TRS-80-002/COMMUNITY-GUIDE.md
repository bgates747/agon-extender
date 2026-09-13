# Agon Extender: pointers for the TRS-OS discussion

[Agon Extender](https://github.com/bgates747/agon-extender) is now public.
It is an experimental ESP32-P4 companion for Agon, with working browser video,
USB keyboard input and a newly qualified, narrowly scoped mainboard-SD service.
TRS-OS integration is at the investigation stage. Here are the useful places
to start, whether you want to borrow an idea or work towards interoperability.

The firmware is split between two repositories:

1. **EDP (Extended Display Processor)** runs on the ESP32-P4 and lives in this
   public [agon-extender repository](https://github.com/bgates747/agon-extender/tree/main/vdp).
   The firmware project is `vdp/`; start in
   [vdp/video/extender/](../../../vdp/video/extender/) for Extender-specific
   display, transport, network, input and storage code. EDP is not a separate
   repository.
2. **EMOS (Extender MOS)** runs on the Agon's eZ80 and lives in
   [bgates747/agon-emos](https://github.com/bgates747/agon-emos).
   **It is now public**, alongside EDP. It owns the EMOS APIs, UART gateway
   and foreground SD application. Start with its
   [README](https://github.com/bgates747/agon-emos/blob/main/README.md),
   [SD gateway](https://github.com/bgates747/agon-emos/blob/main/src/emos_sdlink.c)
   and [sdserve guide](https://github.com/bgates747/agon-emos/blob/main/projects/sdserve/README.md).
   The host sample kits below can also be tried without installing EMOS.

| Discussion topic | Where to look |
| --- | --- |
| TRS-OS loaders, TRS-NET, NHACP/nabud, DriveWire/FujiNet and TNFS | [TRS-80-001](../TRS-80-001.md) compares roles and links the upstream tools. The [TRS-NET source map](../TRS-80-001/trs-net-source-notes.md) identifies Daniel's host server, guest network utilities and UART routines. The [repository inventory](../TRS-80-001/reference-repositories.json) pins collected sources; no protocol has been selected yet. |
| Moving files without repeatedly removing the Agon's SD card | [Operating guide](../../mainboard-sd.md), [wire contract](../../protocols/mainboard-sd.md) and [host client](../../../scripts/sdcard.py). This accesses the **Agon mainboard SD card** through P4 Ethernet, EMOS and foreground `sdserve`. It is bleeding-edge work, with exact builds and limits in the [13 September acceptance record](../../qualification/mainboard-sd/2026-09-13.md). |
| Bounded packets, lost acknowledgements and recoverable writes | [C record codec](../../../vdp/video/extender/storage/sd_wire.h), [C++ request queue](../../../vdp/video/extender/storage/sd_service.hpp) and the wire contract above. The client saves uncertain requests before sending and retries identical bytes. CRC detects corruption; it does not authenticate callers. |
| Browser display and a possible future guest console | [Browser assets](../../../vdp/video/extender/web/) and [EVF1 pixel protocol](../../protocols/browser-video.md). P4 renders; the browser presents final pixels. The current page is video-only: it is not an ANSI/VT100 terminal and does not capture a keyboard. |
| What happens when TRS-OS takes over the machine? | [ExCom/UART contract](../../protocols/excom-console.md), [component ownership](../../../OWNERSHIP.md) and TRS-80-001. The loader changes memory/interrupt ownership; the EMOS foreground SD service cannot simply be assumed to survive. UART and terminal handover need an explicit design. |

The **P4 DevKit microSD card** is separate, with its service still planned in
[PORT-007](../PORT-007.md). Guest RAM disks and host-backed virtual disks are
different storage owners again. The existing HTTP file service does not speak
TRS-NET, NHACP or DriveWire. Real Extender network services currently assume a
trusted LAN and have no authentication.

For a quick look without our hardware, the [sample bin](bin/README.md) contains
a probe of Daniel's unmodified TRS-NET server, a local browser demo and an
Extender transport lab. The probe uses a caller-supplied upstream archive and
temporary generated data; the other kits use our actual production sources.
They are small source kits, not board images; each includes instructions,
licenses and file hashes. These are experimental source samples, with the
validation scope recorded alongside them.

The aim is to reuse community tools and collaborate across independently owned
projects. Loader/terminal handover and the first compatible disk path are the
questions to settle before promising a supported TRS-OS configuration.
