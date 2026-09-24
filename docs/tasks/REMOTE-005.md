# REMOTE-005 — Human-friendly network access to Agon SD

## Executive summary

Research and Author discussion in progress, requested 2026-09-21. Expose Agon's
mainboard SD through P4 Ethernet using an ordinary host client or browser UI.
Compare browser file management, FTP, SMB and WebDAV before choosing. No protocol,
library, architecture or implementation contract is frozen. No firmware build,
flash, storage mutation or physical test is authorized by this task record.

## Existing foundation and scope

Reuse the accepted [mainboard SD service](../mainboard-sd.md) and its
[PORT-017 record](PORT-017.md). Host software requests operations over Ethernet;
P4 translates them into the existing admitted mainboard-SD transport; EMOS and
the foreground `sdserve` application perform mainboard filesystem operations.
Use the maintained service specification for exact transport and wire contracts;
do not substitute direct GPIO/storage access or bypass EMOS ownership.

The current service requires Legacy mode and runs in the foreground. It does not
provide background SD access while a game runs. A familiar host protocol does
not remove this limitation. P4-local SD storage is a separate future backend,
not the requested first target. Preserve existing transfer staging, verification,
recovery and allowed-root semantics when evaluating an adapter.

## Options and initial research leads

These are upstream claims and preliminary integration assessments, not vetted
libraries or tested compatibility with our P4 candidate/toolchain.

| ID | Host experience | Existing lead | Main integration question |
| --- | --- | --- | --- |
| O01 | Browser directory listing and upload/download | Existing P4 HTTP server and SD RPC; no new external protocol required | UI plus bounded transfers; likely least new machinery, not yet estimated |
| O02 | Standard FTP client | [xreef/SimpleFTPServer](https://github.com/xreef/SimpleFTPServer) supports ESP32 and several filesystem backends | Replace/adapt local filesystem assumptions to remote SD operations; Ethernet/toolchain fit and client command coverage |
| O03 | Network share in Finder or other file manager | [ZiFi ESP32-S3 SMB Server](https://github.com/andrewinsidelazarev/ZiFi-ESP32-S3-Zero/tree/main/SMB%20Server) exposes ZX Evolution storage via its file API | Particularly relevant remote-retrocomputer storage model; audit SMB dialect/authentication, Mac compatibility and portability |
| O04 | HTTP-based network drive | [ErikMeinders ESP-IDF WebDAV](https://github.com/ErikMeinders/webdav) uses esp_http_server and reports Finder read/write support | Expects POSIX/VFS storage; adapter needed; Finder chunked upload/range-read behavior and concurrency semantics |

SMB is the protocol; Samba is one implementation. ZiFi is an embedded SMB server,
not evidence that the Samba package runs on P4. Its documented Windows behavior
must not be presented as verified Finder compatibility. SimpleFTPServer's ESP32
support likewise does not qualify our ESP32-P4 configuration.

The WebDAV lead documents a Finder upload transport shim, no authentication/TLS,
and non-enforcing LOCK/UNLOCK. These affect suitability and integration effort;
do not assume a complete filesystem/locking contract from a mounted-drive UI.
No resource footprint or throughput comparisons have been measured. Pin exact
source revisions and establish licenses before reuse; no upstream source is
vendored by this note.

## Decision register — discuss one at a time

| ID | State | Decision and consequences |
| --- | --- | --- |
| D01 | Open | Primary experience: browser transfers, dedicated transfer client, or Finder-mounted share. Browser minimizes new protocol machinery; mounted share adds compatibility and filesystem semantics. Author preference selects the research direction. |
| D02 | Open | Initial operations: list/download/upload versus rename, delete, mkdir and overwrite. Check each against existing SD-service guarantees before offering it. |
| D03 | Open | Service lifecycle: explicit operator start/stop of sdserve versus a separately scoped convenience launcher. Foreground/Legacy limitation remains unless explicitly redesigned. |
| D04 | Open | Client ownership, authentication, exposed root and serialization; define behavior when service is offline, disconnected or occupied by existing tools. |
| D05 | Open | Select protocol/library and bounded acceptance contract after compatibility, resource and license review. |

## Research work items

R05-01 [x] Record requested mainboard-SD target, existing service limitation,
options and upstream leads.

R05-02 [ ] Review D01 with Author before expanding implementation research.

R05-03 [ ] For shortlisted options, inspect pinned source/API, license and
P4/ESP-IDF/Ethernet fit. Map required filesystem operations, seek/range access,
metadata, file handles and temporary-file replacement to existing SD RPC. Identify
missing semantics without promising unrestricted network-drive behavior.

R05-04 [ ] Settle remaining decisions sequentially; document a bounded contract
and proposed checks: byte-identical round trips, partial-transfer recovery,
interrupted overwrite, offline service, allowed-root enforcement, filenames,
client contention and ordinary keyboard/display responsiveness. No performance
campaign or bench execution before implementation scope is agreed.

R05-05 [ ] Present selected approach and implementation scope for Author approval;
only then freeze the contract and promote accepted architecture decisions through
the normal ADR/specification process.


## Agon community transfer scan — 2026-09-21

1. [envenomator/agon-ymodem](https://github.com/envenomator/agon-ymodem):
   direct match for the listener/terminal-transfer model. Agon utility receives
   into a directory or sends named files through mainboard VDP USB serial;
   host examples include its own utility, lrzsz and Python YMODEM. README reports
   MOS2.2+ and115200/8N1; recursive directory sending remains unfinished.
   Its claim that VDP support is unreleased is stale: official
   [VDP2.16.0 release notes](https://github.com/AgonPlatform/agon-vdp/releases/tag/v2.16.0)
   explicitly include Y-Modem/PR343. No stock deployment needed for this scan.
2. [AgonPlatform/agon-hexload](https://github.com/AgonPlatform/agon-hexload):
   serial Intel HEX receiver primarily for loading executable/data memory;
   optional filename also saves to SD. Host send.py converts binaries to HEX.
   It offers VDP and UART1 routes; neither is permission to repurpose Extender's
   occupied UART or bypass EMOS. This is not a network filesystem.
3. [AgonPlatform/agondev](https://github.com/AgonPlatform/agondev#uploading-programs-version-018):
   `make upload` integrates HEXLOAD; it is a convenient host CLI workflow using
   the same receiver, not another transfer protocol.

Assessment: existing Agon utilities validate the simple foreground receiver
model. YMODEM is relevant for ordinary file exchange, HEXLOAD for development
uploads. Neither establishes Finder mounting or an Ethernet endpoint on P4.
An Extender adaptation would need explicit transport ownership and integration;
current PORT-003 deferral of HEX/YMODEM to Legacy remains unchanged. Compare reuse
against our already-qualified SD RPC before replacing working transfer machinery.
This bounded scan did not establish an Agon-native SMB/WebDAV implementation;
it is not proof that none exists. No firmware or physical tests performed.


## Author direction — MOSlet and YMODEM comparison, 2026-09-21

The minimum desired implementation is conversion of our existing sdserve listener
to a MOSlet. This requirement is accepted; source changes and deployment are not
part of the present feature-comparison step. The choice between extending sdserve
and adapting Jeroen Venema's YMODEM remains open. Author values upstream reuse and
credit and wants any useful additional functionality identified; a YMODEM MOSlet
experiment is a candidate, not yet selected.

R05-06 [ ] Convert sdserve to a MOSlet in a subsequent bounded implementation:
link code/data/heap/stack within the32KiB MOSlet region, preserve caller state and
loaded application memory, verify exits and existing transfer/recovery semantics.
No background execution implied; callers must leave the MOSlet region available.

R05-07 [x] Compare actual YMODEM source and sdserve capabilities, host interfaces,
transport ownership, recovery, missing filesystem operations and MOSlet feasibility.


[Source-backed feature comparison](REMOTE-005/FEATURE-COMPARE.md) completed.
D06 accepted: convert existing sdserve to a MOSlet as minimum implementation.
D07 open: extend sdserve alone, separately test YMODEM as a MOSlet, or reuse
Jeroen's external transfer engine above our storage service. Recommendation is
MOSlet conversion first, optional YMODEM adapter second; Author has not selected
that ordering or an external protocol. No build/flash performed in this review.


## Selected next slice — 2026-09-21

Author selects retaining our listener. Before adding features, review Jeroen's
code/idioms for reuse with attribution and license review. His eZ80 utility uses
C with assembly helpers; VDP is C++, host tooling C/C++. Its VDP component is
necessary because the external USB serial port terminates on that ESP32.
Author now authorizes an isolated MOSlet build and quick bounded checks, not
new features or a broad qualification campaign. Use existing sdserve source,
MOSlet load/heap/stack bounds, small transfer, return/re-entry and application
memory preservation checks. Do not flash processor firmware or alter startup.


[Quick MOSlet build/check](REMOTE-005/MOSLET-CHECK.md): build fits, return and4KiB
application-memory preservation pass, but transfers are blocked by EMOS sdlink's
ordinary-RAM-only buffer contract. Original listener1KiB transfer control passes.
No firmware/startup changes. R05-06 remains incomplete pending narrowly scoped
EMOS admission change; no application-RAM buffer workaround adopted.

## Provisional EMOS follow-up — authorized 2026-09-21

Author subsequently authorized modifying EMOS and testing the MOSlet. This
supersedes the preceding no-firmware-change boundary for this narrow correction.
Admit MOSlet caller memory only for resident ext.sdlink, keep reserved MOS RAM
excluded, preserve the actual installed ROM and startup, and verify firmware
readback before transfer/return/application-sentinel checks. EMOS v0.1.18 is
provisional; P4 and mainboard VDP stay unchanged.

Provisional correction and physical checks now pass; see [MOSlet results](REMOTE-005/MOSLET-CHECK.md#provisional-physical-pass). The earlier admission blocker is resolved. Broader network access research remains open.

ROM simplification and proposed `/emos` CLI utility placement are separately
tracked in [AUDIT-008](AUDIT-008.md), whose refreshed investigation contract
awaits Author review. They do not
expand this task or authorize moving the installed listener.

## SD layout decision and transaction follow-up — 2026-09-21

Author accepted [SD layout](../sd-layout.md), recorded in the
[ADR](../decisions/ADR-2026-09-21-sd-layout.md). Mounted-card cleanup moved 158
identified root artifacts with verified hashes; [manifest](../storage/sd-relocation-2026-09-21.json).
Startup, user assets and executable directories were preserved.

R05-09 [ ] Replace target-adjacent transaction files with reserved `/tmp/extender`
storage. Define unique names and durable destination mapping, legacy transaction
recovery, restart behavior and protected-target checks before implementation.
Do not auto-delete unresolved transactions or add ROM machinery for this change.
This cleanup did not modify the transfer protocol or listener binary.

R05-08 [ ] Improve interactive client session restart handling; ordinary read-only
use should not require manually deleting state journals. Preserve recovery of
uncertain mutations. Author identified this usability problem during Mac listing.

## Authorized fast-transfer tasklet — 2026-09-24 UTC

The Author approved an opt-in listener/client fast path before further general
file-manager work. [Frozen tasklet and checklist](REMOTE-005/FAST-TRANSFER.md)
cover skipping whole-file verification rereads while retaining staged transfer,
recovery and transport admission. Local Linux/emulator work only; bench occupied.
This bounded authorization supersedes the research-only restriction above for
this tasklet alone; it does not select FTP/SMB/WebDAV or authorize deployment.

Fast tasklet now deployed with bounded physical checks passing; see its checked
contract and paired normal/fast timing results. Author accepted the work and authorized commit/push; broader network-access
research is unchanged.
