# PORT-007 — P4-local HTTP file access

Current scope is full CLI file/directory management, as authorized in the
expansion below. Development source and host checks are complete; physical
qualification and production promotion remain pending. The original minimum
scope below is retained as superseded decision history, not operating guidance.

## Original frozen scope — superseded operation subset

Author authorized implementation on 2026-09-26. Provide a small standard-firmware
service for curl/scripts: status, directory listing, file download and new-file
upload. No GUI, delete, rename, mkdir, overwrite, formatting, EMOS protocol or
MAME integration in this slice. Existing directories are usable; uploads to new
names provide the minimum safe transfer capability. Preserve the selected
production installation until a candidate has been tested and accepted.

Use a separate HTTP server/task on port8080 so storage transfers do not block
the current video/keyboard HTTP task. P4 mounts its own SD with SDMMC/FatFS/VFS;
Agon, UART and sdserve do not participate. Mount on first storage request,
never format on failure. No automatic removal/remount while files are open;
insert before boot and power down before physical removal for this slice.

Use Olimex DevKit example commit26705d36407a07324348927dfd30fbf4ffc1d94c:
SOFTWARE/Demo_Examples/sdmmc. Four-bit SD1, CLK43/CMD44/D0..3=39..42,
LDO4. The existing Rev D1 fixed-function audit in
[requirements](../SETUP-006/SETUP-006.4-wiring-design/electrical-requirements.md)
reserves GPIO39–45 and detect GPIO3; this slice does not drive detect.
No conflict with retained UART/Ethernet/USB/MIPI allocation is identified there.
Board-specific mounting stays separate from filesystem/HTTP adapters for reuse.

N07-01 [x] Implement bounded path validation, streamed JSON listings/downloads,
create-only PUT uploads and explicit HTTP failures. Reject traversal/control
characters/reserved scratch names; write to an exclusive sibling temporary file,
flush/sync/close before rename. Failed uploads leave destination absent; stale
scratch files are reported/retained, not blindly deleted. No durability claim
beyond checked filesystem flush/close; card/controller power loss remains a risk.

N07-02 [x] Validate host filesystem logic against traversal, interrupted uploads,
existing destinations, binary round trips and listing escaping. Compile standard
P4 target. Preserve exact accepted production files and qualify candidate
separately. No physical pass inferred from compilation.

N07-03 [x] Update maintained P4 SD guide with exact curl commands, status/error
behavior, capacity/format caveats, trusted-LAN/no-auth scope and absence of
concurrent MAME image access. Update handbook/build/task status. Freeze results.

Mutating requests require X-Extender-Storage:1 and reject browser Origin headers.
This is intent checking, not authentication. Future MAME/EMOS consumers must
coordinate exclusive writable-image ownership before sharing this mount.
Physical deployment/acceptance follows the normal identified-build and rollback
workflow; no production promotion until tested acceptance.

## Implementation evidence — 2026-09-26

The candidate uses `vdp/video/extender/storage/local/files.hpp` for host-testable
path/upload primitives and `http.cpp` for ESP-IDF mounting and request adapters.
Console FatFS long filenames are enabled on the heap: the original 8.3-only
configuration cannot represent the reserved `.ext-upload` staging suffix.
Failed HTTP requests close their session, including rejected PUT requests whose
body has not been consumed. Uploads require a fixed Content-Length; chunked PUT
is not supported. Other build profiles retain their existing service selection.

Host filesystem tests pass with `-Wall -Wextra -Werror`. They cover binary and
empty uploads, existing destinations, interrupted cleanup, stale scratch-file
preservation, invalid paths and JSON escaping. The console compile validates
SDK integration only; no physical SD mount, network round trip, power-loss
recovery or concurrent video performance is claimed. These remain deployment
qualification checks under the existing contract, not evidence of production
acceptance. The current production bundle remains unchanged.

Current instructions: [P4 SD guide](../../p4-sd.md), including endpoint examples,
error handling and ownership limitations. Build instructions link the host test.

Standard `p4-console` compilation passed with heap-backed long filenames enabled;
generated SDK configuration confirms that selection. Hardware qualification is
still pending and the completed items above describe this bounded development
slice only.

## Author scope expansion — complete CLI file management

The Author supersedes the create-only limitation. HTTP remains the transport;
P4 owns execution on its local card. Implement file replacement, stat, directory
creation (optional parents), file/directory move, file/directory copy, deletion
(optional recursive), recursive listing and recursive name/content search.
Provide a Python CLI for convenient scripting as well as documented curl calls.
No GUI, filesystem formatting, POSIX permissions/symlinks, background indexing,
or concurrent external writers are implied by file management on FAT.

N07-04 [x] Implement shared filesystem operations and HTTP adapters. Replacement
uploads finish staging before changing the existing file; retain a backup through
rename and restore it on a reported installation failure where possible. FAT
replacement is not power-loss atomic. Copies and recursive deletions report
partial completion on failure, without claiming rollback. Reject root mutation,
self/descendant copies/moves and traversal. Bound recursion to 16 levels and
stream file contents/results rather than buffering whole trees. Search supports
case-insensitive basename wildcards and optional case-sensitive literal content.

N07-05 [x] Add a sessionless standard-library Python client covering all methods,
recursive host upload/download, and exact curl documentation. Explain recursive
partial failure, reserved staging names/recovery, fixed-length uploads and LAN
access. Preserve the existing production/physical qualification boundary.

N07-06 [x] Test nested directories, replacement/interruption preservation,
copy/move/delete, recursive search, binary content across chunk boundaries,
root/descendant rejection, depth limits and host CLI against a local HTTP peer.
Compile the standard P4 target and record results without claiming hardware
qualification. Commit the completed source and documentation together.

## Expanded-scope validation

1. Native C++ tests pass with warnings-as-errors and separately with
   AddressSanitizer/UndefinedBehaviorSanitizer: nested create/copy/move/delete,
   depth/root/descendant bounds, replacement/interruption preservation, stale
   backup retention, wildcard matching and content spanning a read boundary.
2. Linux linker fault injection forces the final upload rename to fail; original
   bytes are restored and the upload staging file is cleaned up.
3. Python localhost HTTP tests pass: binary framing/length and escaping,
   recursive host upload/download, all command dispatch options and incomplete
   download preservation. This peer does not implement ESP-IDF firmware.
4. Standard p4-console target compiles with ESP-IDF 5.5.5. Firmware HTTP adapters,
   physical SD operation, interrupted physical writes and video/input coexistence
   still require a separately identified candidate deployment and bench run.

Replacement relies on the inspected ESP-IDF 5.5.5
`components/fatfs/vfs/vfs_fat.c` implementation: `vfs_fat_rename` calls `f_rename`
without POSIX overwrite emulation. The local staging/backup protocol is necessary
for that contract; it is not an upstream patch. No MOS/VDP ABI changes are made.

## Physical qualification procedure — authorized 2026-09-26

N07-07 [ ] Build committed r56 console candidate (registry r114), preserve and
verify installed P4 flash before replacement, verify flash/readback and boot
identity. Keep the approved production selection unchanged until acceptance.
Use current local bench identity/reset configuration. Stop on unexpected
installed firmware rather than assuming the bench still matches production.

N07-08 [ ] Mount without formatting; record capacity/root listing read-only.
Use one newly created `/agents/extender` test subtree only. Test byte-verified
new/replacement transfers, interrupted replacement, nested copy/move/list/search,
conflicts/root guard, recursive delete and final cleanup. Capture durable results.
Check port-80 keyboard/display service coexistence; do not infer gameplay or
all-mode performance from an HTTP health check. Restore input readiness if needed.

The whole-registry validator currently reports a light2-harness-r02 connectivity
hash mismatch in existing hardware records. No hardware design file is changed by
this tranche; do not repair or re-baseline it as part of the SD firmware work.


Physical r56 finding: 1 MiB byte round trip passes, but rejecting an existing
upload destination closed TCP with unread bytes; urllib saw connection reset
rather than HTTP 409. r57 drains bounded fixed-length request data before an
early rejection response. Preserve this failure as informative protocol evidence.
