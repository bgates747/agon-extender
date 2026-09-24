# Olimex ESP32-P4-PC reference library

Local, provenance-recorded copies of Olimex's board documentation are stored
here so research does not require rediscovering web links. The official upstream
repository is also cloned separately for complete software examples and design
sources. This is reference material, not Extender firmware or board qualification.

## Start here

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
This snapshot describes the upstream Rev.B files, not an assertion about the
revision of a board received by the Author.

Olimex states documentation CC BY-SA4.0, hardware CERN-OHL-S2.0 and software MIT;
retain upstream notices and individual dependency licenses. Imported originals
have not been edited. Extracts only change representation; attribution and
applicable document terms remain. Website documents retain their own notices.

To refresh deliberately: fetch/review upstream changes, select a commit, replace
copies from that revision, refresh website sources and text derivatives, and
update/verify provenance hashes. Do not silently mix changing upstream files
into this pinned snapshot. Board integration remains in
[P4PC-001](../../tasks/P4PC-001.md).
