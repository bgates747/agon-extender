# PORT-007 — P4-local HTTP file access

## Summary and frozen scope

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

N07-04 [ ] Implement shared filesystem operations and HTTP adapters. Replacement
uploads finish staging before changing the existing file; retain a backup through
rename and restore it on a reported installation failure where possible. FAT
replacement is not power-loss atomic. Copies and recursive deletions report
partial completion on failure, without claiming rollback. Reject root mutation,
self/descendant copies/moves and traversal. Bound recursion to 16 levels and
stream file contents/results rather than buffering whole trees. Search supports
case-insensitive basename wildcards and optional case-sensitive literal content.

N07-05 [ ] Add a sessionless standard-library Python client covering all methods,
recursive host upload/download, and exact curl documentation. Explain recursive
partial failure, reserved staging names/recovery, fixed-length uploads and LAN
access. Preserve the existing production/physical qualification boundary.

N07-06 [ ] Test nested directories, replacement/interruption preservation,
copy/move/delete, recursive search, binary content across chunk boundaries,
root/descendant rejection, depth limits and host CLI against a local HTTP peer.
Compile the standard P4 target and record results without claiming hardware
qualification. Commit the completed source and documentation together.
