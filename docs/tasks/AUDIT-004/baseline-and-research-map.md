# AUDIT-004 W1 — Baseline and bounded research précis

Recorded 2026-09-07 for [AUDIT-004](../AUDIT-004.md) as the W1 result.
The subsequently authorized [W2 inventory](communication-inventory.md) uses
this same source selection; the task records current execution scope.
This précis establishes source selection and the research boundary. It contains
no communication-path inventory, end-to-end trace, or Extender redesign.

## Selected stock sources

| Repository | Selected identity | Selection evidence |
| --- | --- | --- |
| `agon-mos` | v3.0.2, [`8336409351ee5314e02801a7b72a4f1bb5282519`](https://github.com/AgonPlatform/agon-mos/tree/8336409351ee5314e02801a7b72a4f1bb5282519) | [REPO-001 inventory](../REPO-001/inventory.md) records the release; [prior audit provenance](../../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md) records its full commit. Local and official remote release tags agree; the official release page identifies this as the latest release. |
| `agon-vdp` | v2.16.0, [`c7ac293d2aa81ddfa693390549bcd909069c8fc3`](https://github.com/AgonPlatform/agon-vdp/tree/c7ac293d2aa81ddfa693390549bcd909069c8fc3) | [SETUP-003](../SETUP-003.md) and its [control-build record](../SETUP-003/generated/control-build.yaml) pin the release. Local and official remote release tags agree; the official release page identifies this as the latest release. |
| `agon-docs` | Documentation snapshot; no release tag, [`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`](https://github.com/AgonPlatform/agon-docs/tree/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b) | [Prior transport research](../PORT-008/production-equivalence/README.md) records this documentation commit; the clean local checkout agrees. |

These are existing upstream identities selected for source research, not a new
approved build or qualification baseline. No artifact revision, binary
identity, or current deployed-firmware claim is assigned. After the Author
clarified the reference rule, official remote tags were queried with
`git ls-remote --tags --refs`, and the official latest-release pages resolved
to [MOS v3.0.2](https://github.com/AgonPlatform/agon-mos/releases/tag/v3.0.2)
and [VDP v2.16.0](https://github.com/AgonPlatform/agon-vdp/releases/tag/v2.16.0)
on 2026-09-07. Their tag commits match the selected identities above.
No source fetch or audit-baseline change was needed.

### Current reference state after Author clarification

Both canonical firmware checkouts are clean, detached at the selected latest
release tags. They are read-only stock references. Keep fixes, experiments,
and product development in separate project-owned checkouts. Verify latest
release selection when establishing a new baseline, but keep this audit's
source citations fixed unless a baseline change is explicitly recorded.

The pre-existing MOS work was preserved before restoration: a verified Git
bundle of all refs, the exact uncommitted patch, and a separate reconstructed
working copy with matching file hashes. Recovery details live in the ignored
project-local `agents/reference-recovery/` record. No branch history or local
work was discarded. No filesystem permission change or firmware deployment
was performed; read-only here describes the required reference workflow.

The Author subsequently directed relocation to the existing project-owned MOS
fork. Its `qsort` branch now contains the exact two uncommitted qsort edits;
the identical packet-discard fix was already present in its main ancestry.
The canonical reference's misplaced fix branch and its HEAD reflog references
were removed after verifying the destination. The recovery copy remains
outside the canonical repository; the fork is the working owner.

### Initial W1 discovery and evidence discipline

1. `agon-mos`: branch `fix/vdp-oversize-discard`, HEAD
   `5f67b1ca77eb7a77d3b37cc7b029db51f0d1548e`. Its direct parent is selected
   stock commit `8336409351ee5314e02801a7b72a4f1bb5282519`. The single later
   commit is “Fix oversized VDP packet discard length”; it changes
   `src/vdp_protocol.asm` and adds `tests/test_vdp_protocol_oversize.py`.
   Unstaged edits also exist in `src/mos_api.asm` and `src/mos_api.inc`.
   These were excluded from stock selection and subsequently preserved
   separately before restoring the canonical checkout to v3.0.2.
2. `agon-vdp`: initially clean `main` at the selected v2.16.0 commit; now
   detached at that release tag, still clean.
3. `agon-docs`: clean `main` at the selected snapshot; no tag points at HEAD.
   This is living documentation covering multiple firmware versions, not
   release-matched documentation for the selected MOS/VDP pair.
4. Later source reading must use the recorded commits, for example
   `git show 8336409351ee5314e02801a7b72a4f1bb5282519:src/vdp_protocol.asm`
   in the official MOS repository. The clean release checkout now supplies
   those same objects. Do not switch reference directories to development
   branches or edit their source. Commit-qualified links below remain the
   authority for this audit. Checkout cleanliness does not authenticate ignored
   build products.

The maintained full stock MOS hash resolves the apparent disagreement between
its named release and the patched checkout. No Author choice of a different
stock release is needed for this W1 selection. Older research using `5f67b1ca`
remains evidence about that source, not automatically about v3.0.2.

## Declared configuration and board boundary

The initial board context is **Agon Light 2**, with the onboard VDP processor.
The Extender P4, EMOS, Console8-specific wiring, and alternate firmware forks
are not substitutes for these stock sources. Other variants may be identified
later as explicit scope limits.

1. **MOS:** [README.md](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/README.md) declares ZDS II eZ80Acclaim!
   5.3.5 and describes Light 2 testing. [MOS.zdsproj](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/MOS.zdsproj)
   selects `Release`, processor `eZ80F92`, target `eZ80F92_AGON_Flash`;
   compiler defines are `NDEBUG,_EZ80,_EZ80F92,_EZ80ACCLAIM!`, and the assembler
   define is `_EZ80ACCLAIM!=1`. Debug is a separate configuration.
   [src/version.h](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/version.h) identifies 3.0.2, `Platform`, `Arthur`;
   [src/config.h](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/config.h) has `enable_config=1`.
   [src/equs.inc](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/equs.inc) and [src/uart.h](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/uart.h)
   declare `MASTERCLOCK=18432000`. These files supply no distinct Light 2
   build selector. Board wiring needs its own evidence.
2. **VDP:** [platformio.ini](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/platformio.ini) declares environment/board
   `esp32dev`, `espressif32@6.6.0`, Arduino, QIO flash, 240 MHz CPU, 80 MHz
   flash, `-O2`, `BOARD_HAS_PSRAM`, the ESP32 PSRAM cache workaround, and
   C++17/GNU++17; it removes `-Os` and C++11/GNU++11 flags.
   [video/version.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/version.h) identifies 2.16.0, `Platform`,
   `Bistromathics`. [video/agon.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon.h) owns protocol constants
   and configuration; the optional `VDP_USE_WDT` define is commented out.
3. **VDP dependencies:** the release declares `vdp-gl#all-the-plots`,
   `ESP32Time@^2.0.0`, and `CRC@^1.0.3`. The existing
   [stock control-build evidence](../SETUP-003/evidence/work-3-upstream-control.md)
   resolved vdp-gl `ac2dd5986daf496c43ae8e7fe41836274aec54a0`, ESP32Time 2.0.6,
   CRC 1.0.4, Arduino-ESP32 2.0.14, and Xtensa GCC 8.4.0. Those are inherited
   resolved identities; W1 performed no new resolution or build. Consult a
   dependency only if a later trace reaches behavior it owns, checking its
   identity first.

These are checked-in configuration declarations and explicitly cited historical
build evidence. They do not prove which options produced any currently
installed image. W1 does not need a new firmware build or bench inspection.

## Official-document research map

Read the documentation before following implementation details. Each row is a
bounded research area, not an inventoried communication path.

| Area | Pinned documents | Relevant entry sections and limits |
| --- | --- | --- |
| Platform orientation | [docs/Theory-of-operation.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/Theory-of-operation.md), [docs/VDP.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/VDP.md) | Hardware/VDP responsibilities; “Executing a VDU sequence”. Introductory scope, not a complete protocol contract. |
| Application entry and binary state | [docs/mos/API.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md), [docs/mos/Keyboard.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Keyboard.md) | RST calls, MOS API calls, “VDP protocol, and miscellaneous functions”, “System State Information (SysVars)”, “VDP pflags (vdpflags)”, keyboard access methods. |
| Command families and reverse protocol | [docs/vdp/VDU-Commands.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDU-Commands.md), [docs/vdp/System-Commands.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md) | General poll, VDP Serial Protocol, VDP Protocol events, keyboard packet data, console/terminal modes; follow version notes. |
| Specialized command documentation | [mkdocs.yml](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/mkdocs.yml) | Navigation index for audio, buffered commands, bitmaps, context, fonts, Copper, tile, and VDP variable APIs; follow only relevant family dependencies. |
| Startup, operator and maintenance | [docs/MOS.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/MOS.md), [docs/mos/Star-Commands.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Star-Commands.md), [docs/Updating-Firmware.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/Updating-Firmware.md) | Boot script, Soft Boot, CLI, updater sections and Recovery; verify any claimed recovery contract in selected source. |
| Other application/external interfaces | [docs/mos/API.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md), [docs/mos/C-Functions.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md), [docs/mos/System-Variables.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/System-Variables.md), [docs/mos/Modules.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Modules.md) | UART1, I2C, SD API leads and C calling convention. Named system variables differ from the binary SysVars block. Module proposals must not be mistaken for implemented facilities. |
| Board and processor references | [docs/GPIO.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/GPIO.md), [docs/FAQ.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/FAQ.md), [docs/External-Documentation.md](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/External-Documentation.md) | Light 2 GPIO section and linked header images; manufacturer/user-manual and processor-document leads. Electrical authority still requires exact document verification. |

## Bounded implementation entry map

File existence and the named entry symbols were checked at the selected source
identities. These are starting points for later enumeration/tracing, not
findings about all traffic, active configuration, or protocol completeness.

| Processor/source area | Pinned files | Entry points / purpose of later inspection |
| --- | --- | --- |
| MOS startup | [main.c](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/main.c), [src_startup/cstartup.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/cstartup.asm), [src_startup/init_params_f92.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/init_params_f92.asm) | `main`, `init_interrupts`; startup and initial configuration. |
| MOS UART | [src/uart.c](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/uart.c), [src/uart.h](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/uart.h), [src/serial.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm) | `init_UART0`, `init_UART1`, `UART0_serial_PUTCH`, `UART1_serial_PUTCH`; configuration and byte I/O. |
| MOS interrupts/protocol | [src/interrupts.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/interrupts.asm), [src/vdp_protocol.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/vdp_protocol.asm) | `_uart0_handler`, `_vblank_handler`, `vdp_protocol`, `vdp_protocol_vector`. |
| MOS application/state boundary | [src_startup/vectors16.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/vectors16.asm), [src/mos_api.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm), [src/mos_api.inc](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.inc), [src_startup/globals.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/globals.asm) | RST handlers, `mos_api`, `mos_api_sysvars`, `mos_api_setkbvector`, `mos_api_wait_vdp_flags`. |
| MOS secondary-interface leads | [src/i2c.c](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/i2c.c), [src/spi.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/spi.asm), [src/sd.asm](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/sd.asm), [src_fatfs/diskio.c](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_fatfs/diskio.c), [src/mos.c](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos.c), [src/mos_sysvars.c](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_sysvars.c) | External peripherals and CLI/configuration entry files; follow only in-scope dependencies. |
| VDP configuration/lifecycle | [video/video.ino](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino), [video/agon.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon.h), [video/vdp_protocol.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_protocol.h) | `setup`, `loop`, `setupVDPProtocol`; configuration and startup entry points. |
| VDP stream/protocol | [video/vdu_stream_processor.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h), [video/vdu.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h), [video/vdu_sys.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h) | `VDUStreamProcessor`, `readByte_t`, `send_packet`, `processNext`; dispatch and protocol tracing entry files. |
| VDP secondary-interface leads | [video/agon_ps2.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_ps2.h), [video/agon_audio.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_audio.h), [video/agon_screen.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h), [video/updater.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/updater.h), [video/hexload.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/hexload.h), [video/ymodem.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h), [video/zdi.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/zdi.h) | Peripheral and maintenance entry files; presence of a file alone does not establish active behavior. |

## Existing research and limits

1. [VDP upstream précis](../../architecture/vdp-upstream-precis.md) and
   [SETUP-003](../SETUP-003.md) provide structural and compiler-evidence maps
   for the selected VDP release. Reuse their navigation; do not regenerate
   their tooling merely to begin this audit.
2. [SETUP-004 VDU inventory](../SETUP-004/VDU-inventory.md) supplies command
   discovery leads, but its Extender dispositions are not neutral stock
   findings. Excluded product features remain in the stock audit's scope.
3. [AUDIT-001](../AUDIT-001.md), [AUDIT-003](../AUDIT-003.md), and the
   [prior transport research](../PORT-008/production-equivalence/README.md)
   supply coverage/provenance leads. Recheck stock claims, especially where
   the cited MOS source is patched HEAD `5f67b1ca`.
4. Ignored local `agents/precis/mos-sysvars.md` and `mos-modules.md` provide
   bounded navigation aids. Their MOS source selection is `5f67b1ca`, so their
   conclusions cannot silently become v3.0.2 findings. No private checkout or
   bench locations are copied here.
5. The [earlier circuit proposal's provenance table](../HW-001/v1-uart-parallel-circuit-proposal.md#provenance-and-design-influence)
   records an Olimex AgonLight2 source pin
   `b7f2a21c282813efd8cdf26573eb5126876432a8`, Rev B schematic hash
   `5019caa700d034bd16b720184f291c9768be3dba62734f0569887ee19704953c`, and
   Zilog `PS015317-0120`. These are inherited retrieval leads, not newly
   verified electrical evidence. The hardware hold overrides the proposal's
   historical construction permission.

## Coverage boundary and unresolved evidence

W1 establishes exact source identities, declared configuration, document and
source entry maps, and inherited evidence limits. Communication IDs and
inventory rows are now recorded separately by W2. [W3 endpoint traces](communication-traces.md) now supplement this baseline,
including authenticated board/dependency evidence and remaining limits.
[W4 coverage reconciliation](coverage-review.md) is complete. The [W5 overview](README.md)
presents the result, accepted by the Author on 2026-09-07 within its stated limits.

The task evidence register owns remaining provenance, external-peer, dependency
and validation questions. W4 resolved the manufacturer document identity and
recorded concrete multi-version documentation/source discrepancies. In particular, the pinned official docs have
inconsistent processor links: `docs/External-Documentation.md` labels an
“eZ80F92” specification but targets `ez80/ps0130.pdf`, while `docs/FAQ.md`
targets `ez80acclaim/ps0153.pdf`. No electrical conclusion is drawn from either
link in W1. W4 authenticated the F92/F93 manual at the latter URL and identified
the former as an L92 manual; the [hardware trace](trace-hardware-and-dependencies.md)
records the exact identity and reached peripheral semantics. The older
schematic-byte mismatch remains open. The stock source choice itself is resolved by the recorded release
pins; no communication or hardware requirement is inferred from this map.
