# REMOTE-005 — Human-friendly network access to Agon SD

## Executive summary

Author selected browser transfers on 2026-09-27. Investigate embedded-oriented
file-manager reuse, select/deselect all for bulk loose-file transfers, and whole
directory operations before selecting a library or implementation contract.
D03 service lifecycle discussion waits for this investigation. Separately authorized
MOSlet admission, `/emos` migration and paired fast-transfer work have since
been implemented and physically checked; use the [current SD guide](../mainboard-sd.md)
and the [fast-transfer record](REMOTE-005/FAST-TRANSFER.md). The original
research scope below does not itself authorize further hardware operations.

## Existing foundation and scope

Reuse the accepted [mainboard SD service](../mainboard-sd.md) and its
[PORT-017 record](PORT-017.md). Host software requests operations over Ethernet;
P4 translates them into the existing admitted mainboard-SD transport; EMOS and
the foreground `sdserve` application perform mainboard filesystem operations.
Use the maintained service specification for exact transport and wire contracts;
do not substitute direct GPIO/storage access or bypass EMOS ownership.

The current service requires Legacy mode and runs in the foreground. It does not
provide background SD access while a game runs. A familiar host protocol does
not remove this limitation. P4-local SD storage is a separate backend,
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

## Decisions — settle one at a time

D01 [x] Accepted 2026-09-27: browser transfers. Prefer adapting an existing framework, especially an embedded-oriented one, after investigation. FTP/SMB/WebDAV are retained alternatives, not current implementation targets.

D02 [ ] Partially settled: select/deselect all for bulk transfers of loose files and whole-directory operations are required. Investigate uploads/downloads preserving hierarchy, empty directories, create/rename/move/delete, overwrite conflicts and partial failure. Exact initial operation set and destructive-operation behavior remain to be settled from findings.

D03 [ ] Deferred until browser investigation is presented. Service lifecycle: explicit operator start/stop of sdserve versus a separately scoped convenience launcher. Foreground/Legacy limitation remains unless explicitly redesigned.

D04 [ ] Client ownership, authentication, exposed root and serialization; define behavior when service is offline, disconnected or occupied by existing tools.

D05 [ ] Select protocol/library and bounded acceptance contract after compatibility, resource and license review.

## Research work items

R05-01 [x] Record requested mainboard-SD target, existing service limitation,
options and upstream leads.

R05-02 [x] Review D01 with Author before expanding implementation research.

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

## Qualification procedure refresh

R05-10 [ ] Refresh the retained mainboard SD qualification procedure before its
next execution; owns [AUDIT-009 F020](AUDIT-009/FINDINGS.md). Prepare a bounded
implementation/validation contract and new procedure identity first.

1. The operator selects exact component builds from the production authority
   or an explicitly identified candidate; preserve the original r01 evidence.
2. The operator establishes Legacy mode, prior Extender input admission and
   checked-mode `EMOS sdserve /`. The host keyboard observer must instruct this
   EMOSlet restart after Escape, not `RUN . /` of an ordinary application.
3. The host controller must preserve active EXEC/autoexec files and unknown
   transaction state. Reconcile test targets and retained evidence with the
   current SD layout; do not relocate live sibling journals into `/tmp/extender`.
4. Replace the obsolete reset-circuit prohibition with the maintained reset
   guide's explicit authorization/evidence boundary. No automatic reset or
   serial opening becomes part of transfer recovery.
5. Keep checked-transfer qualification distinct from fast-mode evidence,
   physical keyboard observations distinct from injected packets, and physical
   recovery distinct from host fault injection. Validate refreshed instructions
   and tools before declaring the procedure ready; respect emulator review gates
   if a refreshed test changes an emulator setup.

The documentation audit neither edits r01/scripts nor authorizes this test run.

## Browser investigation — 2026-09-27

Research only; no product implementation, vendoring, deployment or bench use.
Findings: [browser reuse investigation](REMOTE-005/BROWSER-RESEARCH.md).

R05-B01 [x] Record D01 and the accepted portion of D02; leave D03 open.

R05-B02 [x] Identify embedded-oriented candidates and pin initial review revisions;
compare advertised bulk/directory support and identify existing SD API gaps.

R05-B03 [x] Inspect shortlisted source and actual licenses/dependencies. Separate
reusable browser assets from local-filesystem/server assumptions; estimate asset
sizes and P4 adapter work without claiming unmeasured runtime costs. Prefer a
frontend adapter to replacing our HTTP service or adding unrelated Wi-Fi/OTA code.

R05-B04 [x] Assess Firefox/Chromium/Safari folder upload/download mechanisms,
empty-directory preservation, ZIP versus direct downloads, bounded host/P4 memory,
serialized RPC transfers, progress/cancellation/retry, filename/path limits and
per-file outcomes. Define what select-all includes when filtering or paging.

R05-B05 [x] Map each proposed operation to current EMOSlet/P4/host ownership;
identify required mainboard API additions, reuse P4-local SD idioms where sound,
and preserve staging/recovery and root restrictions. Do not silently substitute
P4-local storage for Agon SD or presume background mainboard access.

R05-B06 [x] Present a recommended reuse approach, gaps and bounded implementation
proposal. Then return to D02/D03 with evidence; do not decide lifecycle in advance.

Browser investigation delivered 2026-09-27: B03–B05 are source/documentation
review, not runtime qualification. B06 proposal is presented in BROWSER-RESEARCH;
implementation items R05-P01–P04 are proposals awaiting Author review. Preferred
approach is selective MIT frontend reuse, existing relay and serialized browser
orchestration, with additional EMOSlet directory primitives. D03 remains open.

## R05-P01 execution contract — accepted 2026-09-27

Author authorized the proposed isolated browser mock. Adapt the small embedded
frontend's layout/interaction concepts with retained MIT provenance; keep all
mock assets under REMOTE-005. Demonstrate folder navigation, filtered bulk
selection, recursive queue expansion (including empty directories and >100
entries), sequential progress, cancellation/retry, and offline/busy states.
Use synthetic content only. File inputs may inspect names/sizes but must not
read or transfer user file contents. No P4/Agon calls, service lifecycle change,
firmware build or deployment. Validate in a local browser with synthetic cases;
provide an accessible preview for Author review. Runtime browser coverage must
be stated precisely. D02–D05 and backend implementation remain separate gates.

R05-P01 delivered: [browser mock](REMOTE-005/browser-mock/README.md). Synthetic
navigation, selection, directory queue and interruption controls pass local
Chromium checks; Author usability review pending. No backend or bench changes.

## Author review — browser mock parked, 2026-09-27

Author found the mock visually suitable but browser transfers clunky. Preserve
R05-P01 code as a fallback for further investigation if other approaches fail.
Do not proceed to browser backend implementation. D01's browser-first trial is
complete; final interface selection is reopened. D02 bulk/directory requirements
remain. D03 remains unanswered. Next suggested investigation is WebDAV for native
host file-manager access; suggestion alone does not authorize implementation.

## WebDAV investigation — 2026-09-27

Author authorized investigation including Pop!_OS, Lenovo and macOS after
preserving outstanding work. [WebDAV findings](REMOTE-005/WEBDAV-RESEARCH.md)
record completed W01/W02, actual Linux client inventory, pinned standard-MIT
ESP-IDF server review and the mainboard CRC/staging mismatch. W03 proposes a
host-only native-file-manager usability trial; W04 remains conditional. D03 and
D04 are still open. No device or native-client transfer qualification yet.

## R05-W03 execution authorization — 2026-09-27

Author authorized the host-only WebDAV usability control. Serve generated files
only from an isolated temporary directory, with an isolated server environment.
Exercise native Linux GVfs clients on Pop!_OS and Lenovo for nested/empty folders,
128 files, bidirectional byte checks, rename and sandbox deletion. Open the share
on Lenovo for human interaction review. Mac/Finder remains pending if unavailable.
No Agon/P4 endpoints or storage involved; no firmware changes. This validates a
host reference server/client interaction, not the embedded candidate.
