# sdserve versus Agon YMODEM — source comparison

## Executive summary

Retain and convert sdserve to a MOSlet as the accepted minimum. YMODEM offers
standard host-client interoperability and multi-file batch transfer, but does not
replace sdserve's directory/range-read/recoverable-write service. Prefer considering
Jeroen's protocol implementation as an additional P4-facing transfer adapter above
our storage service, rather than discarding that service. This is a recommendation,
not a selected architecture or authorization to code/flash.

## Sources and confidence

Read-only inspection on2026-09-21; no build or test of YMODEM performed.

1. [Agon YMODEM main.c](https://github.com/envenomator/agon-ymodem/blob/cd4b0ff350a8ae28078beea0d1b79652c6c235a3/src/agon/src/main.c),
   [serial.asm](https://github.com/envenomator/agon-ymodem/blob/cd4b0ff350a8ae28078beea0d1b79652c6c235a3/src/agon/src/serial.asm)
   and [Makefile](https://github.com/envenomator/agon-ymodem/blob/cd4b0ff350a8ae28078beea0d1b79652c6c235a3/src/agon/Makefile).
2. Official clean VDPv2.16.0 at c7ac293d2aa81ddfa693390549bcd909069c8fc3:
   [ymodem.h](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/ymodem.h).
   Relevant functions: MOS_YmodemSession readFiles/writeFiles/addFile, serialRx_byte_t,
   CRC/block and retry handlers. This component is part of the functionality,
   not merely a transparent serial cable.
3. sdserve source in project-owned agon-emos commit26ba8776bc147e262cd45dc808d5869740b1396e:
   projects/sdserve/src/{main.c,service.c,sd_wire.h,emos_gateway.asm}, Makefile,
   README and current build map. Authoritative shared contracts:
   [operation guide](../../mainboard-sd.md), [wire protocol](../../protocols/mainboard-sd.md).
4. [Official executable layout](https://agonplatform.github.io/agon-docs/mos/Executables/):
   MOSlet region starts0x0B0000 and provides32KiB. Our local map reports binary18974
   bytes and code/static data through0x45326 from0x40000:21286bytes before heap/stack.
   These are current local build observations, not proof that a relocated build fits.

## Feature comparison

| Capability | Our sdserve + maintained host client | Agon YMODEM utility + stock VDP component |
| --- | --- | --- |
| Host interface | Project Python CLI over P4 HTTP/SD RPC | Standard YMODEM clients and provided host tooling over VDP USB serial |
| Transfer directions | Upload and download | Upload and download |
| Multiple files | Host can orchestrate individual requests; no wire batch operation | Explicit named-file batch send and repeated received files |
| Directory discovery | LIST with cursor; STAT size/attributes | No remote directory-query operation found |
| Partial reads | Explicit offset/count READ | Sequential whole-file transfer |
| Writes | Sequential staged whole-file upload; not random in-place writes | Receiver opens final destination with FA_CREATE_ALWAYS |
| Integrity | Record CRC32/session/sequence; final size+CRC readback, host byte comparison | YMODEM block CRC16 and ACK/retry on external link; CRC32 checks between VDP and eZ80 |
| Overwrite/recovery | Part/meta/backup journal, explicit finish/activate/recover; not FAT power-loss atomic | Direct replacement; abort/error cleanup; no comparable retained old-file/stage journal found |
| Duplicate requests | Same request/sequence returns cached reply; stale requests rejected | Protocol block sequencing/retries; not general filesystem RPC idempotency |
| Root/path policy | Explicit allowed root, bounded printable paths, reserved running-service/journal names | Receiver directory argument; no equivalent confined-root validation in inspected receive path |
| mkdir/delete/rename as client operations | Not exposed as general operations; internal rename/delete only for transfer recovery | Not exposed as general operations |
| Memory strategy | Small bounded eZ80 records,212byte write chunks; host Python upload currently holds file bytes | eZ80 uses1KiB transfer buffer; VDP session allocates whole files in PSRAM before forwarding |
| Service execution | Foreground; existing Legacy/ext.sdlink admission, no direct UART ownership | Foreground; VDU23,28 selects VDP transfer; assembly receives via virtual keyboard sysvars |
| Standard mounted network drive | No | No |
| MOSlet today | No; ordinary0x40000 build | No; ordinary agondev defaults |

YMODEM's larger blocks are not a demonstrated throughput improvement over our
transport. External USB serial, internal UART, Ethernet and existing SD-link records
have different costs. Do not infer speed from block size or nominal baud alone.
Our protocol also lacks the timestamp, arbitrary write and locking semantics a
full mounted-share client may expect. Prior discussion of rename/delete described
possible adapter operations, not features already exposed by sdserve.

## Adaptation and MOSlet implications

1. **sdserve MOSlet:** assign RAM_START0xB0000 and bounded RAM_SIZE, then verify
   linker layout, runtime heap/stack high water, CRT register/stack restoration,
   EMOS gateway buffers and cleanup. Preserve an application-region sentinel
   across start/transfer/exit and test the real loaded-application workflow.
   Relocation must not silently retain the ordinary build's0xB0000 stack/heap
   ceiling. The initial footprint leaves roughly11.2KiB, not a guaranteed margin.
2. **YMODEM MOSlet:** plausible but not built or sized. Its1KiB automatic buffer,
   roughly4KiB debug globals, libraries and stack need a linked map. Neither
   MOSlet status nor relocation changes its virtual-keyboard transport dependency.
3. **Reuse as-is on mainboard:** native USB serial and stock VDP YMODEM support
   are the existing route. This is useful interoperability, not P4 Ethernet access.
4. **Adapt YMODEM to Extender:** either port its VDP-side session machinery and
   review keyboard/routing interaction, or reuse the external protocol engine on
   P4 and map file operations onto ext.sdlink/sdserve. The latter keeps EMOS
   ownership and current storage recovery. It would require a raw network/serial
   endpoint and compatible host-client setup; YMODEM alone does not provide FTP
   or Finder mounting. Current Legacy-only command deferrals remain authoritative
   until explicitly revised; do not feed transfer bytes as ordinary human keys.
5. **Review before reuse:** eZ80 getbyte/getblock spin awaiting keycount changes;
   outer VDP timeouts do not establish bounded eZ80 recovery. Receive code trusts
   peer lengths before copying and does not visibly check every filesystem result.
   These are source-review concerns, not reproduced defects; scope any hardening
   separately and preserve Jeroen's provenance/license rather than silently
   rewriting upstream behavior. Review whole-file PSRAM demand on P4 as well.

## Recommendation for the next decision

First make the existing listener a MOSlet without changing its wire/storage
semantics. Keep YMODEM as a serious optional interoperability front end, crediting
and reusing Jeroen's work where it fits. If the Author prioritizes Finder mounting,
SMB/WebDAV still require their own adapters; YMODEM is not a substitute for them.
No implementation begins as part of this comparison.
