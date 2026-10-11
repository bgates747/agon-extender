# Olimex ESP32-P4-PC reference library

Local, provenance-recorded copies of Olimex's board documentation are stored
here so research does not require rediscovering web links. The official upstream
repository is also cloned separately for complete software examples and design
sources. This is reference material, not Extender firmware or board qualification.

## Start here

## Current Rev C authority — 2026-10-02

The Author confirms receipt of an **Olimex ESP32-P4-PC Rev C**, replacing the
DevKit as the project target. The authoritative manufacturer reference is the
[official Olimex repository](https://github.com/OLIMEX/ESP32-P4-PC), with the
local read-only checkout verified at commit
`04032d68e5c727870f9d40beb9e37b7ab3a66916`.
Use its `HARDWARE/ESP32-P4-PC-Rev.C/` schematic, design and BOM,
`HARDWARE/Hardware-revision-changes.txt`, and `DOCUMENTS/` manual for Rev C
research. The machine-local checkout location is recorded in
`agents/p4pc-reference/LOCAL.md`.

The vendored files and `PROVENANCE.json` below remain the historical Rev B
snapshot at `89a7b96e2ec4c3f28b55d768dfda3ba8a86846bd`; their hashes and
provenance have not been relabelled as Rev C. They are not the current board's
documentation authority. Receipt does not establish integration or qualification.
The Pi 5 now hosts development and the P4-PC bench; standalone P4-PC tests
precede Agon reconnection. Current topology and remaining identity/wiring
verification boundaries are recorded in `HARDWARE.local.md`.

## Rev C shared GPIO/SD supply

GPIO39–48 use VDDPST_5, which the Rev C PCB connects to ESP_LDO_VO4.
Transport D7/GPIO46 therefore needs LDO4 even when no P4-local SD card is used.
The maintained P4-PC console initializes and retains a fixed 3.3V supply before
console GPIO setup. SDMMC uses four data lines at its default 20MHz/3.3V and
cannot acquire an adjustable owner, switch the shared bank to 1.8V or turn it
off after mount failure. DevKit transport D7/GPIO9 uses a different I/O bank;
its existing SD-only supply lifecycle remains unchanged.

The manufacturer PCB source at the Rev C commit above and Espressif's
[chip v1.3 datasheet](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_datasheet_en.html)
establish the connection. The [direction-isolation results](../../tasks/PORT-008/DIRECTION-ISOLATION-R01.md)
record the independently compared physical transfers and current qualification
boundary. This correction does not establish successful P4-PC SD mounting.

## Retained Rev B snapshot

| Resource | Local copy |
|---|---|
| User manual | [PDF](upstream/DOCUMENTS/ESP32-P4-PC-user-manual.pdf) · [searchable text](text/ESP32-P4-PC-user-manual.txt) · [editable upstream original](upstream/DOCUMENTS/ESP32-P4-PC-user-manual.odt) |
| Rev.B schematic | [PDF](upstream/HARDWARE/ESP32-P4-PC-Rev.B/ESP32-P4-PC_Rev_B.pdf) · [searchable text](text/ESP32-P4-PC_Rev_B.txt) |
| Hardware design and BOM | [Rev.B directory](upstream/HARDWARE/ESP32-P4-PC-Rev.B/) |
| Board photographs | [Documents directory](upstream/DOCUMENTS/) |
| ESP-IDF production test instructions | [README](upstream/SOFTWARE/ESP-IDF/p4_production_test/README.md) |
| Arduino MIPI display demo instructions | [README](upstream/SOFTWARE/Arduino/ESP32-P4-PC-MIPI-LCD-Arduino/README.md) |
| EU conformity declaration | [PDF](website/EU-DOC-ESP32-P4-PC.pdf) |
| UKCA declaration | [PDF](website/UKCA-ESP32-P4-PC.pdf) |
| Product-page snapshot | [Archived HTML](website/product-page.html); external page assets were not mirrored |
| Exact origins, licenses and hashes | [PROVENANCE.json](PROVENANCE.json) · [upstream licensing statement](upstream/README.md#licensee) |

[HDMI driver research](HDMI-DRIVERS.md) identifies the existing Espressif driver
and Olimex production-test integration.

## Complete software and hardware repository

[Official OLIMEX/ESP32-P4-PC repository](https://github.com/OLIMEX/ESP32-P4-PC),
pinned documentation snapshot:
`89a7b96e2ec4c3f28b55d768dfda3ba8a86846bd`.

A clean reference clone has been installed on the Linux development host. Its
clickable local checkout/examples links are in the ignored
`agents/p4pc-reference/LOCAL.md`, and HARDWARE.local.md points there. Absolute
machine paths intentionally stay out of tracked documentation. In the standard
Agon workspace layout the checkout is the `ESP32-P4-PC` sibling of `mystuff`.

Full source includes ESP-IDF production tests, Arduino examples, vendored BSP
code, KiCad files and 3D component models. Upstream examples are references;
do not infer compatibility with this project's pinned toolchain or flash them
onto the working bench merely because they are present. Keep the upstream
checkout clean; experiments belong in project-owned working directories.

## Provenance and scope

Unmodified board files are copied under `upstream/`, preserving original paths.
Included: all upstream DOCUMENTS, board hardware files except the bulky generic
3D package library, and board-specific software documentation. Full dependency
and other-board documentation remains in the complete clone rather than being
presented here as P4-PC documentation. Product HTML and the two directly linked
regulatory PDFs are stored under `website/` with retrieval metadata.

`text/` contains marked pdftotext derivatives for searching. Consult original
PDFs for pinouts, electrical diagrams and visual layout. Each original and
extract has a SHA-256 record; upstream files also have commit-pinned source URLs.
This snapshot describes the upstream Rev.B files; the received board is Rev C.

Olimex states documentation CC BY-SA4.0, hardware CERN-OHL-S2.0 and software MIT;
retain upstream notices and individual dependency licenses. Imported originals
have not been edited. Extracts only change representation; attribution and
applicable document terms remain. Website documents retain their own notices.

To refresh deliberately: fetch/review upstream changes, select a commit, replace
copies from that revision, refresh website sources and text derivatives, and
update/verify provenance hashes. Do not silently mix changing upstream files
into this pinned snapshot. Board integration remains in
[P4PC-001](../../tasks/P4PC-001.md).
