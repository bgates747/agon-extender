# Browser file-manager investigation

Initial discovery: 2026-09-27. Research only; no library selected or tested.

## Accepted direction

Browser transfers, bulk loose-file selection with select/deselect all, and
whole-directory operations. The browser should orchestrate the existing P4 HTTP
and EMOSlet service; EMOS retains transport ownership. Lifecycle remains open.
Authoritative checklist: [REMOTE-005](../REMOTE-005.md), R05-B01–B06.

## Initial shortlist

These are upstream README claims, not source-verified feature guarantees.
Repository API license labels are preliminary; inspect actual license texts and
bundled dependencies before reuse. No source has been vendored into the product.

| Candidate / pinned revision | Relevant claims | Initial integration question |
| --- | --- | --- |
| [ESPFMfGK](https://github.com/holgerlembke/ESPFMfGK/tree/ac3b699c35705d34df06ed4a978fb5add4310463) | ESP32 file manager, multiple filesystems, file operations and recursive ZIP download | Attractive embedded UI lead; license API returns NOASSERTION, so actual terms need inspection. Replace local filesystem assumptions with remote service adapter. |
| [esp-fs-webserver](https://github.com/cotestatnt/esp-fs-webserver/tree/502f2f3438f076e70c8563a5f7ec5c36b0feea89) | Embedded file/folder browser and editor; synchronous Arduino WebServer | Apache-2.0 API label; examine frontend separation. Includes unrelated Wi-Fi/OTA facilities; do not import these wholesale. README refers to externally maintained page sources: establish rebuild provenance. |
| [ESP32-File-Server](https://github.com/CyberXcyborg/ESP32-File-Server/tree/63708837464d3d5587761f7584d4e796dc1f30f4) | Folder upload, multiple-file ZIP download, file/folder create/move/copy/rename/delete | MIT API label; closest advertised operations. Verify implementation, dependencies and resource bounds before ranking as a recommendation. |

## Mainboard service gap

The [current wire contract](../../protocols/mainboard-sd.md) exposes listing,
stat, file reads, staged writes/activation, cancellation/recovery and exit.
It does not expose general mkdir, rename, unlink or rmdir commands. A browser
can queue existing file transfers, but uploading a new directory tree and wider
directory management need additional mainboard service operations. Internal
rename/delete used by write recovery are not general client operations.

Current limits include ASCII paths of 120 bytes and staged targets of 112 bytes.
Any reused UI must report these limits instead of promising unrestricted desktop
filesystem semantics. Bulk operations need per-file results; current transaction
handling does not make an entire directory transfer atomic.

## Initial follow-up boundary (superseded by source review below)

Complete R05-B03–B06 before choosing a framework. In particular verify actual
select-all semantics, recursive transfer coverage, empty folders, browser download
permissions/fallbacks, cancellation and memory use. No performance or browser
compatibility tests have yet been performed. D03 is deliberately unanswered.

## Source review and recommendation — 2026-09-27

R05-B03–B05 research completed; no library integration or browser/hardware runtime
qualification performed. Sources downloaded at the three exact revisions above
into ignored research storage; no upstream code executed or product code vendored.

### Candidate disposition

| Candidate | Source-backed result | Recommendation |
| --- | --- | --- |
| ESPFMfGK | LICENSE.md is MIT (resolves API's ambiguous label). Separate filemanager/fm.html, fm.css and fm.js; C++ depends on Arduino WiFi/WebServer/FS. fm.js uploadFile uses a local multipart endpoint and file.name; multi-file scheduling uses uploaddone. ZIP implementation also directly uses FS/WebServer. | Preferred small frontend starting point. Retain attribution, adapt UI/idioms only; replace transport calls with our adapter. Directory selection, detailed errors and cancellation still require work. Do not import backend or optional gzip-js machinery. |
| esp-fs-webserver | LICENSE is Apache-2.0. FSWebServer.cpp handleFileUpload/Create/Delete acts on local FS; editor bundles are generated, README points to an external page-source location. Includes Wi-Fi configuration and OTA outside this task. | Less suitable as reusable editable frontend until page provenance is resolved. No reason to replace our server with its synchronous Arduino server. |
| ESP32-File-Server | LICENSE is MIT. web_ui.h contains toggleSelectAll, recursive scanEntry and an upload queue. ESP32_File_Server.ino uses SD/WebServer, FTP, WebSockets, ArduinoJson and updater facilities. | Useful individual UI idioms, not wholesale framework adoption. Reject its transfer/ZIP implementation as our baseline. |

Specific evidence at the pinned CyberXcyborg revision:

1. toggleSelectAll selects the entire files array, not explicitly the filtered
   visible subset. Our UI must state its selection scope.
2. uploadConcurrency is 3. Our single-sequence remote SD session needs one
   serialized owner; parallel files would contend rather than help.
3. scanEntry queues files only; directories have no independent queue entry.
   Empty directories are therefore lost. Folder picker paths alone cannot repair
   this omission.
4. handleFolderZip collects files in a 16-KiB JSON document; an empty folder gets
   404. streamZipFromJsonArray caps the archive at 100 files and reads data once
   for CRC then again for content. Those limits/extra remote reads are unsuitable
   as inherited behavior for whole-directory transfer.
5. Downloads use response.blob(), holding the resulting archive in host memory.
   Browser code inserts paths into HTML strings; an adaptation should render
   names as text, not adopt those templates unexamined.

Source evidence links: [small UI](https://github.com/holgerlembke/ESPFMfGK/blob/ac3b699c35705d34df06ed4a978fb5add4310463/filemanager/fm.js),
[MIT license](https://github.com/holgerlembke/ESPFMfGK/blob/ac3b699c35705d34df06ed4a978fb5add4310463/LICENSE.md),
[larger UI](https://github.com/CyberXcyborg/ESP32-File-Server/blob/63708837464d3d5587761f7584d4e796dc1f30f4/web_ui.h),
[larger backend](https://github.com/CyberXcyborg/ESP32-File-Server/blob/63708837464d3d5587761f7584d4e796dc1f30f4/ESP32_File_Server.ino),
[editor backend](https://github.com/cotestatnt/esp-fs-webserver/blob/502f2f3438f076e70c8563a5f7ec5c36b0feea89/src/FSWebServer.cpp).

### Size observations, not runtime costs

Locally counted source bytes: ESPFMfGK's three frontend files total 50,582 bytes
(10,657 bytes when concatenated and gzip-compressed for comparison); Cyber's
web_ui.h is 141,753 bytes (33,001 gzip). The latter includes a C++ wrapper, so
these are approximate frontend-source comparisons, not final firmware sizes.
No P4 heap, throughput, compiled size or rendering measurements are claimed.
Third-party dependencies require their own notices if later adopted; choosing
only these plain frontend files avoids importing either full firmware stack.

### Browser behavior and proposed policy

Current Firefox, Chromium and Safari can be targeted with multiple-file inputs
and directory inputs; older browser versions need feature detection. Directory
inputs provide relative paths for files. Empty directories need explicit entry
traversal or an archive import path; a file-only fallback must disclose omission,
not claim a complete directory transfer.

[Directory input documentation](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/webkitdirectory)
and [directory enumeration](https://developer.mozilla.org/en-US/docs/Web/API/FileSystemDirectoryReader/readEntries)
show the relevant APIs. Enumerate until an empty batch, not just once (Chromium
may return 100 entries per batch). This is documentation/source review, not a
claim of passing tests on all three browsers.

Recommend one ZIP download for selected files or directory trees, preserving
relative names and explicit empty-directory entries. Avoid repeated automatic
single-file downloads and their permission prompts. Direct saving into a host
folder is optional future enhancement: [showDirectoryPicker](https://developer.mozilla.org/en-US/docs/Web/API/Window/showDirectoryPicker)
requires a secure context and has limited browser availability, so cannot be our
plain-HTTP cross-browser baseline. ZIP generation should use a reviewed library,
not the candidate's hand-written 100-entry backend. That library selection is
an implementation prerequisite, not completed by this UI review.

Browser upload plan: keep File handles, read bounded slices, compute required
CRC incrementally, and send one transfer at a time. Existing checked protocol
requires CRC before BEGIN_WRITE, so a host-side pre-read may be necessary; do
not silently downgrade verification. Show preparation separately from committed
transfer progress. Stop scheduling on cancel, reconcile any in-flight result,
then use existing cancellation/recovery. An HTTP timeout is not proof of failure.
Do not blindly replay a mutation with a new sequence.

For browser-generated ZIPs, Blob fallback consumes archive-sized host memory.
Propose an explicit size preflight/limit and documented fallback rather than an
unbounded promise. No complete file/tree buffer should live in P4 RAM. Streaming
ZIP export via a new P4 endpoint would avoid browser Blob accumulation, but adds
server coordination and must be selected deliberately; it is not needed for the
first mocked UI proof. Exact limits remain implementation-contract decisions.

Selection proposal: select/deselect all entries in the current directory matching
the visible filter, across loaded pages; show count and bytes, and require full
listing before offering a truthful all-selection. Selecting a directory includes
its subtree, with overlapping selections deduplicated. No silent failed-file
skips: retain per-file outcomes and a retry-failed action after reconciliation.

### Service ownership and API map

| Operation | Existing support / required work | Owner |
| --- | --- | --- |
| Browse/stat | Paginated LIST and STAT already exist | Browser enumerates; P4 relays; EMOSlet reads Agon SD |
| File upload/download | Existing staged write and offset read protocol | Browser serializes RPC, CRC and retry; existing P4 relay; EMOSlet executes |
| mkdir | Add explicit capability-gated operation | EMOSlet invokes stock MOS filesystem API; keep general filesystem work out of resident EMOS |
| Rename/move | Add bounded two-path operation, no implicit overwrite | EMOSlet validates both roots/paths and invokes stock rename |
| Delete file / empty directory | Add explicit unlink operation | EMOSlet enforces allowed root and rejects root deletion |
| Recursive delete / transfer | Enumerate and queue; postorder directory removal; partial outcomes | Browser orchestrates bounded primitives; EMOSlet remains final path authority |
| Copy | Queue READ then staged WRITE; no atomic tree-copy claim | Browser initially; no need for new resident service |
| ZIP import/export | New host/browser archive layer; preserve empty directories | Browser candidate approach; endpoint alternative requires separate choice |

Current implementation references: wired_network_service.cpp sdRpcHandler
serves bounded binary records at /sd/rpc and returns 202 while pending; repeated
identical requests retrieve the result. ../agon-emos/projects/sdserve/src/service.c
owns the filesystem switch. Its internal rename/unlink do not expose general
mutations. P4-local storage/local/http.cpp already has directory/delete/move/copy
routes, but operates on different storage and is not a mainboard API shortcut.
Reuse its validation ideas where applicable, not its local file handles.

Official MOS API documentation reviewed at
f9806bd3cbff6ed5d1c08bef1d51fed11764b86b, docs/mos/API.md:
ffs_unlink 0x97, ffs_rename 0x98 and ffs_mkdir 0x9B provide candidate primitives.
Confirm linked MOS wrapper availability and exact failure behavior in the coding
tranche. Mainboard wire paths remain ASCII, 120 bytes generally/112 staged;
reject traversal, overlong names and unsupported encodings before mutations.
Changing these limits is not implicitly authorized. Negotiate new capabilities;
old listener builds must report unsupported rather than misinterpret requests.

### Proposed implementation sequence — for Author review

R05-P01 [ ] Adapt the small MIT frontend in an isolated host mock: directory
navigation, selection, per-file queue/progress/cancel and offline/busy states.
Use synthetic trees including empty directories and more than 100 entries.
No device traffic or firmware change. Show the UI before building the full service.

R05-P02 [ ] After D02–D05 are settled, add capability-gated EMOSlet directory
primitives and host/client tests. Preserve existing transfer semantics and CLI.
Test root boundaries, missing paths, collisions and non-empty directory errors.

R05-P03 [ ] Connect browser adapter to existing relay; add reviewed ZIP handling
with explicit host-memory bounds and empty-directory behavior. Test interrupted
activation, stale sessions, contention, retries and multi-file partial failure.
Retain machine-readable per-file results. Do not make each file a new session.

R05-P04 [ ] Run emulator/host correctness tests and then separately authorized
bench/browser acceptance, including Firefox, Chromium and Safari where available.
No throughput campaign. Follow production promotion only after acceptance.

D03 remains open. Recommended next decision is lifecycle after Author reviews
this proposed frontend/service split; no convenience launcher has been assumed.
