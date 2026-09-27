# Native file-manager access via WebDAV

Research date: 2026-09-27. Author authorized investigation after committing
outstanding work. No firmware changes, bench requests, network share mounts,
package installs or file-transfer tests performed in this tranche.

## Recommendation

WebDAV is worth a disposable native-file-manager usability trial before porting
anything onto P4. It can present a browsable remote directory in the ordinary
host file manager, with host-selected destinations and recursive transfers.
Keep the browser mock as fallback. Do not adopt the server unchanged: its direct
filesystem writes and nominal locks differ materially from our SD contract.

## Actual client inventory

| Host | Observed client / backend | Evidence boundary |
| --- | --- | --- |
| Pop!_OS | Installed COSMIC Files 1.8.0 build ending 089ad2b; running cosmic-files process. GVfs and gvfs-backends 1.54.4; GIO 2.80.0; dav/davs mount definition and gvfsd-dav installed. | Local read-only package/process inspection. Not a WebDAV mount or GUI transfer pass. |
| Linux Lite / Lenovo | Running Thunar, package 4.18.8; GVfs and gvfs-backends 1.54.4; GIO 2.80.0. | Read-only SSH inspection. Not a WebDAV mount or GUI transfer pass. |
| macOS | Finder's native WebDAV client is documented by Apple. | Documentation only; no current Mac connection or version inspection performed. |

Both Linux hosts share the same installed GVfs version. Their GUIs differ, so
common protocol/backend does not establish identical prompts, recursive-copy,
replacement or error behavior. No Nautilus assumption is needed.

[System76 network-drive guide](https://support.system76.com/support/map-a-network-drive/)
lists dav/davs access; [COSMIC Files upstream](https://github.com/pop-os/cosmic-files)
is the client source. [Apple's guide](https://support.apple.com/guide/mac-help/mchlp1546/mac)
documents Finder Connect to Server. Use explicit server URLs for initial tests,
not network-discovery icons. Discovery is independent of transfer correctness.

## Embedded server reviewed

[ErikMeinders/webdav](https://github.com/ErikMeinders/webdav/tree/8ab2375018047b3c943a3195ffd7948a990b654a),
revision 8ab2375018047b3c943a3195ffd7948a990b654a. Complete LICENSE inspected:
standard MIT text, no trailing organization exclusion. Source retained only in
ignored research storage. No code vendored or executed. Requires ESP-IDF >=5.0.

| Source | Finding | Integration consequence |
| --- | --- | --- |
| include/esp_webdav.h, src/esp_webdav.c | Component starts and owns an esp_http_server; root_path is a POSIX/VFS mount, not a filesystem callbacks interface. | No direct remote-SD adapter slot. Refactor handlers around an explicit storage adapter or supply a substantially more involved VFS implementation. Prefer explicit adapter for staged remote writes. Avoid replacing the existing video/input HTTP server. |
| src/esp_webdav.c, PUT handler | fopen(path,"wb") truncates existing target before receiving content; failure unlinks target. | Must replace with our staged write/activate/recovery semantics. Do not call this safe overwrite for mainboard SD. |
| src/esp_webdav_copy_move.c | MOVE with overwrite removes destination before rename; COPY similarly uses direct files. | Must specify collision/recovery behavior rather than inherit destructive replacement sequences. |
| src/esp_webdav_propfind.c | Streams XML listing via POSIX enumeration, supports depth traversal. | Adapt paginated remote LIST/STAT; bound recursion/work and disable unrestricted depth initially. Review metadata the mainboard API does not provide. |
| src/esp_webdav.c and src/esp_webdav_macos_put.c | Byte-range GET and receive override for Finder chunked PUT with expected length. | Useful compatibility code to reuse after pinned IDF build tests. Shim is server/socket-sensitive; keep isolated from video endpoints. Upstream Mac pass claims are not our validation. |
| LOCK/UNLOCK handlers | Issues lock tokens without an enforcing lock table. | Cannot infer exclusion of CLI or second client. D04 must settle ownership; truthful lock/If behavior needs a bounded contract. |

Server defaults include seven sockets, 4-KiB I/O buffers and 8-KiB task stack.
These are configured defaults, not measured P4 memory costs. It has no built-in
authentication/TLS. Treat D04's exposure/ownership choices as unresolved, not a
reason to add an unrelated security project or assume public access is acceptable.

## The upload impedance mismatch

Our mainboard BEGIN_WRITE carries expected length and CRC before any data,
including fast-mode requests. Ordinary WebDAV PUT supplies bytes and length (or
chunked framing), not that checksum. Therefore an adapter cannot simply forward
the stream into the current checked transaction unchanged.

Options for a later contract:

1. P4 stages the complete upload to its local SD, computes CRC, then relays the
   existing transaction to mainboard. Bounded RAM; requires local SD availability,
   staging quota/cleanup and extra disk work. Use the reserved transaction area
   only after specifying ownership; do not treat current P4-SD candidate as
   accepted production automatically. Return success only after mainboard commit.
2. Extend the EMOSlet transaction protocol to accept a checksum at finish and
   preserve meaningful recoverable metadata. Avoid local staging, but changes
   the integrity/recovery contract; must be explicitly scoped and qualified.
3. Require a special host client to precompute CRC. Defeats the immediate native
   file-manager objective; not recommended for this trial.

No option selected. A host-only usability server avoids deciding this prematurely.
Long uploads also need a measured client-timeout budget before promising success:
P4 upload completion is not mainboard activation completion.

## Operations and ownership

WebDAV adds a client protocol; it does not remove foreground sdserve's Legacy
limitation or EMOS transport ownership. P4 would translate WebDAV requests into
one serialized mainboard session. MKCOL, rename/move and unlink/rmdir still need
new EMOSlet operations, as found in BROWSER-RESEARCH. Ordinary GET/range requests
map to offset READ. Directory recursion can live in P4 adapter orchestration;
EMOSlet remains final allowed-root/path authority. Byte/ASCII path limits, invalid
names and unavailable service must become explicit errors, not silent truncation.

Native clients may open parallel connections, issue metadata reads and create
sidecar/temporary files. Serialize backend work without assuming one socket
means one user. Coordinate with the CLI session owner; do not silently take over.
Real locking, synthetic metadata, ETags, overwrite and cleanup are implementation
questions, not proven compatible merely because a directory can be listed.

## Bounded next proposal — not yet executed

R05-W01 [x] Inspect Pop!_OS and Lenovo clients and review official Mac support.

R05-W02 [x] Pin embedded candidate and review license, server ownership,
filesystem assumptions, Finder handling and existing-transaction compatibility.

R05-W03 [ ] Host a temporary WebDAV sandbox serving only generated sample files.
Use a maintained host server as a usability control, not as evidence that the
embedded component works. Run both Linux GUIs plus GIO checks for list, upload,
download, 128 loose files, empty/nested folders, rename and deletion within the
sandbox. Compare content hashes. Include a separate Finder pass when available.
No mainboard/P4 access. User reviews whether native interaction is preferable.

R05-W04 [ ] If usability is accepted, settle D03 lifecycle and D04 ownership,
select upload staging strategy and freeze a separate P4/EMOSlet implementation
contract. Start with read-only listing/range reads, then staged writes and directory
mutations. Retain rollback and existing CLI behavior; bench qualification follows
separate authorization. Do not advertise locking or recovery guarantees that
have not been implemented and tested.

## Results boundary

This is feasibility/source research and client inventory only. No WebDAV client
has yet transferred files in this project. Main risk is integration semantics,
not lack of a shared Linux protocol. Recommended next work is W03's cheap
usability control, before choosing a server port, SD staging scheme or lifecycle.

## W03 execution update — 2026-09-27

[Host control results](webdav-trial/README.md): both Linux GVfs clients mounted
and passed 129-file bidirectional hash checks, nested/empty directories,
rename/overwrite/deletion. Both native GUIs were asked to open the share. Human
usability acceptance and Finder remain pending, so W03 is not marked fully
complete. Unix metadata-preserving copy hit EOPNOTSUPP; byte-copy tests pass.
No embedded candidate or Agon/P4 testing is implied.
