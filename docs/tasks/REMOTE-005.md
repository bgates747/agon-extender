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

D01 [ ] Browser trial completed and parked as fallback. Lenovo WebDAV usability trial passed two-way transfers; staged WebDAV is now the proposed implementation direction, pending architecture review.

D02 [x] Accepted scope: bulk loose-file and whole-directory upload/download;
create folders, rename/move, and delete files or nonempty directories in the first
implementation. Deletion is permanent, with confirmation owned by the host file
manager and no Agon recycle bin. Do not promise every client presents a dialog;
P4 executes valid admitted requests, not inferred user intent. Preserve empty
folders and report partial recursive outcomes. D13/D14 govern recovery and
replace/skip behavior. Implementation details remain in the bounded A work items.

D03 [ ] Proposed automatic EMOS-owned foreground servicing at a safe idle CLI point. Reject external requests while a user application runs; allow explicit application-initiated transfers. Current manual Legacy listener remains the implemented behavior until the proposal is approved and qualified.

D04 [ ] Partially settled: expose the whole Agon SD card (root `/`) by default, as accepted 2026-09-27. Do not add a root-selection UI/configuration requirement for the first iteration. Existing path validation and rejection of deleting the filesystem root remain; P4-local staging is not part of this exported namespace. One active transfer job at a time is accepted 2026-09-27; competing clients receive busy rather than being queued. Password-free access is accepted 2026-09-27: no usernames, passwords or accounts in this iteration. Precise client/job identity remains an implementation detail; it is concurrency bookkeeping, not authentication. Multiple HTTP connections from one native client must not automatically be treated as different owners.

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

R05-W03 staged for human review: disposable WebDAV share is available on the
host. Both Linux GVfs byte-transfer suites pass; native GUI acceptance and Finder
remain pending. See [trial results](REMOTE-005/webdav-trial/README.md). No bench
or production changes; host-server results do not qualify the embedded adapter.

## Author feedback — WebDAV trial

2026-09-27: Author confirmed two-way transfers worked in the Lenovo native
file-manager trial. Retain this bounded usability acceptance. Pop!_OS GUI and
Finder checks remain pending; automated GVfs evidence for both Linux hosts is
unchanged. No Agon-backed implementation or production promotion is implied.
Next discussion remains D03 lifecycle, then D04 ownership and upload staging.

## Proposed staged WebDAV architecture — review gate

Author requested a written proposal and development/deployment/test plan, then a
pause. [Proposed ADR](../decisions/ADR-2026-09-27-staged-webdav-admission.md)
records actors, admission, staging and transport boundaries. No implementation
is authorized by this writeup. P4 staging is a proposed simplification of the
WebDAV adapter, not a claim that all filesystem or lifecycle work disappears.

### Remaining bounded design decisions

D11 [x] Accepted 2026-09-27: an admitted external transfer occupies the foreground
CLI until completion, cancellation or failure cleanup. EMOS does not dispatch
another command or user application during that ownership interval. Retain the
selected display mode. Preserve keyboard responsiveness for the defined cancel
mechanism; exact handling of other keystrokes is to be specified without silently
executing commands typed during the transfer afterward.

D06 [x] Author accepted 2026-09-27: external admission only at an empty, idle
CLI prompt; partly typed input means busy and must remain untouched. EMOS admits
one bounded job only when no command executes and no input line is partly typed;
serialize command dispatch with that admission. New input must be preserved or
handled explicitly, never lost or interpreted as transfer data. Trace stock CLI
and application dispatch before selecting hooks. No filesystem work in ISR.

D07 [ ] Partially accepted 2026-09-27: application-initiated transfers are
synchronous; the caller waits for completion or failure and receives a defined
result before resuming. No background completion callbacks. Remaining ABI and
memory model must specify caller-owned buffers and explicit source/destination,
root and direction. Determine whether foreground code can reuse utility routines
without loading a MOSlet over the calling program; do not assume reentrancy or
MOSlet safety. EMOS derives origin from actual execution/call context, not a P4
claim. File transfers only, not unsolicited host access to the application's SD.

D08 [ ] Partially accepted 2026-09-27: P4-local SD staging is required for the
new staged transfer service. Absent/full staging media produces a clear failure;
no alternate transport or RAM-only fallback. Existing explicit CLI transfer tools
remain separate and unchanged. Define staging lifetime/quota and HTTP timing.
Recommend bounded staging
on P4 SD with complete/partial manifests, mainboard boot/admission identity,
cleanup and explicit errors on full/missing media. No unbounded P4 RAM buffering.
P4 should obtain admission before accepting an expensive upload where practical;
otherwise any spool is provisional. Busy rejection never becomes delayed delivery.
Measure native client behavior while mainboard copy proceeds before choosing
lease/HTTP deadlines. Do not acknowledge mainboard success early.

D09 [ ] Author requests Legacy and ExCom transfer support wherever feasible,
without automatic display switching. A02 must investigate removing the current
Legacy-only gateway guard and trace UART framing, ownership and cleanup under
concurrent ExCom display traffic. Both external idle-CLI and application-origin
paths must cover both modes; report a concrete blocker rather than silently
retaining a Legacy-only implementation. One admitted mainboard job
at a time; WebDAV sockets are not equivalent to owners. Define conflicts with CLI
sdcard.py/manual sdserve, keyboard packets, and stale client retry. No pretend locks.

D10 [ ] Define filesystem/export behavior. Recommend new mkdir/rename/unlink
primitives in the EMOSlet, restricted roots, explicit overwrite/recovery rules,
per-entry recursive results and no all-tree atomicity promise. Specify WebDAV
metadata/ETags, temporary sidecars, unsupported properties and range snapshot
lifetime. Keep P4 staging hidden from the exported Agon namespace. Use the SD
layout's reserved transaction concept with a documented P4-local placement;
never reuse a mainboard path by assumption.

D12 [x] Accepted 2026-09-27: Escape on Agon cancels an externally initiated
transfer, returning to CLI after safe cleanup. EMOS does not impose Escape
cancellation on application-origin transfers; the application owns key policy.
The synchronous ABI must not promise application-side event processing while
blocked; any cooperative cancellation mechanism requires explicit ABI design.

D13 [x] Accepted 2026-09-27: preserve existing file-level staged replacement and
recovery. Write/close/verify the stage, preserve the old destination as backup,
activate the stage and confirm success before retiring the backup, following the
existing checked/fast-mode contract. Do not claim unconditional power-loss
atomicity on FAT. Once activation begins, defer cancellation until that sequence
completes or reaches a recoverable error state. Retain recovery evidence rather
than deleting the only good copy. No all-or-nothing directory guarantee in the
first iteration: completed files remain, uncompleted entries are reported, and
cancellation stops further work. Default verification policy remains explicit;
this decision does not silently enable fast mode or weaken existing guarantees.

D14 [x] Accepted 2026-09-27: honor the native file manager's replace/skip
instructions. P4 honors explicit overwrite intent and rejects conflicting
operations without it; no second confirmation on Agon. Preserve staged
replacement/recovery. The adapter must map each WebDAV method's actual
conditional/overwrite semantics correctly (PUT and MOVE/COPY differ); do not
invent an Overwrite-header requirement for ordinary PUT. Verify real-client
request sequences and conditional failures before claiming the UI's choice is
preserved. Skipped items must never be replayed as pending work.

D16 [x] Accepted 2026-09-27: application developers may link a small synchronous
transfer helper into their programs. The helper executes foreground orchestration
with caller-owned memory; resident EMOS retains admission and transport ownership.
Do not load a nested EMOSlet or move the whole transfer engine into ROM. D07's
exact ABI, memory bounds and error/cancellation details remain implementation
contract work. This decision does not authorize direct UART/GPIO access.

### Development, deployment and test work items

R05-A01 [ ] Freeze the Author-reviewed architecture and settle D02–D10 as needed
for the first tranche. Promote accepted ADR/normative text only after review;
record explicitly deferred capabilities. Keep the host sandbox and browser mock
as separate evidence, not P4 acceptance.

R05-A02 [x] Trace stock MOS CLI input/dispatch, execution context, application
entry/exit and MOSlet loading against current EMOS. Include Legacy/ExCom SD
coexistence: current src/emos_sdlink.c explicitly rejects non-Legacy mode; that
guard is observed policy, not proof that removing it is safe. Pin docs/source revisions;
produce the minimal safe-point/admission design and memory map. Prove a request
cannot slip between idle checking and application dispatch. Stop for a bounded
choice if safe auto-dispatch or application calling cannot preserve stock state.

R05-A03 [x] Define admission/control messages, capability negotiation and states:
idle, external job admitted, application running, application-owned transfer,
closing/fault. Include request/boot identity, close/cancel and busy rejection.
EMOS polls/adopts pending intent at safe points; P4 cannot grant itself access.
Tests must distinguish ISR receipt from foreground authorization/execution.
No external-request replay after an application returns to CLI.

R05-A04 [x] Implement/test minimal resident EMOS admission and foreground dispatch
in the project-owned EMOS checkout. Reuse existing gateway and MOS machinery.
Keep filesystem code out of resident ROM where practical; measure ROM/RAM impact.
Test missing utility, partial CLI input, loaded program preservation, keyboard
continuity, app entry/exit, and clean restoration after transfer errors.

R05-A05 [x] Implement/test application-initiated transfer entry points and a tiny
eZ80 caller fixture for both directions. Demonstrate correct caller-memory and
return-state preservation, errors and cancellation. Simultaneous external requests
must be rejected, including while the application is waiting for its own transfer.
Do not fulfill this item by externally typing commands into a running application.

R05-A06 [x] Implement P4 SD spool/manifest layer with bounded buffers, incremental
CRC, quotas and cleanup. Test partial file versus complete snapshot, missing/full
card, reset, stale boot/admission, transfer failure and abandonment. Reuse current
checked UART transfer unchanged where possible; no parallel-link work. Specify
recovery before ever deleting the only confirmed good copy.

R05-A07 [ ] Add required mainboard utility directory operations and client support.
Test root containment, ASCII/path limits, nested/empty directories, collisions,
non-empty removal, overwrite interruption and per-entry recursive outcomes.
Keep current ordinary/fast CLI transfer behavior compatible and test it separately.

R05-A08 [ ] Adapt pinned WebDAV protocol code to the admitted storage interface,
not direct destructive POSIX overwrites. Keep video/input serving independent.
Test PROPFIND/GET/range/PUT/MKCOL/MOVE/COPY/DELETE, truthful locking/ownership,
Finder body handling and negative conditions. WebDAV response success follows
mainboard completion. Resolve D04 exposure policy before device deployment.

R05-A09 [ ] Run host fault tests and emulator eZ80 tests before bench deployment.
Exercise an interleaving matrix: external request at idle/partly typed CLI/app,
app-origin upload/download, duplicate requests, disconnect/reconnect, reset and
external request during an app-origin job. Record distinct expected busy versus
unsupported/offline/error results; verify no delayed rejected work executes.
Measure durations to select justified timeout bounds, not optimize throughput.

R05-A10 [ ] Prepare a separately authorized deployment after bench release: read
current local hardware/fixture constraints, select/version exact P4+EMOS+utility
builds, preserve production rollback and SD files, verify deployed bytes and
input/recovery readiness. Do not flash while TRS-80 owns the bench. Install only
the selected fixture paths; video-mode selection belongs in autoexec if needed.

R05-A11 [ ] Hardware-qualify Legacy and ExCom idle external operations and both application-origin
directions against Agon SD with byte hashes and explicit busy rejection while a
user application runs. Test missing/full staging media, interruption recovery,
concurrent CLI/native client, repeated operations and keyboard/video coexistence.
Record source/destination durability separately; no framebuffer streaming
performance campaign. Restore a known recoverable CLI state after tests.

R05-A12 [ ] Run native file-manager acceptance on Pop!_OS COSMIC Files, Lenovo
Thunar and macOS Finder. Test loose bulk files (>100), directories/empty folders,
selected destinations, collisions, progress/cancel, rename/delete, busy errors and
reconnection. Capture per-client outcomes and hashes, including latency/timeouts
while staging. Human acceptance is distinct from automated GVfs checks.

R05-A13 [ ] On Author acceptance, promote exact tested firmware/utilities and
instructions through the production bundle/version/tag process. Update handbook,
mainboard SD guide, P4 storage guide, wire/API contracts, client instructions and
recovery/cleanup guidance. Retain evidence and rollback; stop temporary host
servers/mounts only after their review purpose ends. Do not claim untested modes,
clients or background access. Commit/publish under applicable authorization.

Execution boundary: proposed plan only. Pause here for Author review before A01
freeze or any source/firmware changes. No new service behavior is implemented.

D15 [x] Accepted 2026-09-27: P4 removes staging after confirmed successful
completion; retain interrupted data only while needed for recovery. For downloads,
serving/range-read lifetime must end safely before cleanup. No permanent mirror
of Agon SD. Do not delete incomplete recovery evidence merely to reclaim space.

## R05-A02 source review authorization — 2026-09-27

Author authorized code review of stock MOS/EMOS safe CLI dispatch, application
caller memory and Legacy/ExCom coexistence. Record feasible hooks, blockers and
minimal changes; no firmware edits or bench operations. Earlier accepted decisions
remain authoritative; the overall proposal is not yet an implementation release.

R05-A02 completed 2026-09-27: [source review](REMOTE-005/ADMISSION-REVIEW.md).
Stock line editor blocks in waitKey; Core policy is not CLI-idle state. Existing
utility loader is suitable only for safe CLI-origin entry; application calls
should use a linked foreground helper plus resident gateway. ExCom needs changes
in both P4 parser/send admission and EMOS guard. No code or bench changes.
D16 now accepts the SDK/resident split; exact A03/A05 contracts remain to be frozen.

## R05-A03 design delivery — 2026-09-27

[Admission contract](REMOTE-005/ADMISSION-CONTRACT.md) defines actors, states,
external/app flows, control framing proposal, retry/reset/cancellation and test
cases. A03 remains unchecked until numeric results, descriptor fragmentation and
capability bootstrap are frozen for implementation. No code or bench changes.
A native client's folder gesture is multiple admitted protocol operations, not
an atomic directory job; client concurrency compatibility remains an explicit test.

## R05-A03 freeze / A04 start — 2026-09-27

Finalized revision-1 controls, safe Legacy-only bootstrap, capability-gated ExCom,
bounded descriptors and finite `/emos/sdjob.bin` dispatch. A03 is complete as a
design. A04 implements the minimal resident boundary; actual staging, filesystem
operations and application SDK remain later items. No physical deployment in this
tranche. Emulator-coupled source remains uncommitted pending Author review.

## R05-A04 implementation — 2026-09-27

Resident boundary implemented in EMOS; [results](REMOTE-005/A04-RESULTS/README.md)
record passing build/linked checks, 112 host tests and five UART-peer emulator
cases. A04 subsequently passed bounded hardware qualification after a cleanup fix;
see [physical results](REMOTE-005/A04-HARDWARE.md). No finite file engine, P4
staging or physical deployment is implied. Source remains uncommitted; production
is unchanged.

## R05-A05 development — 2026-09-27

[Bounded contract](REMOTE-005/A05-CONTRACT.md) owns this tranche. Resident lease
and linked helper are implemented; host checks and eZ80 send/caller return pass.
Both directions now pass on physical EMOS v0.1.21 with a RAM-only diagnostic P4
peer, including caller memory, external-request exclusion and return to CLI.
Normal P4 is restored after qualification. See
[application results](REMOTE-005/A05-RESULTS.md). Real P4 SD staging remains A06;
ExCom transfer support remains downstream. Production selection is unchanged.

## R05-A06 local development — 2026-09-27

Author released the bench to TRS-80 and authorized development only. The bounded
[A06 contract](REMOTE-005/A06-CONTRACT.md) covers staging/recovery storage and local
fault tests. No hardware/network tests, flashing, or production change until cleared.

A06 storage implementation now passes local filesystem/fault tests and P4 object
compilation. [Results](REMOTE-005/A06-RESULTS.md) document the API and integration
boundary. No endpoint instantiates the spool, and no bench operation occurred.
