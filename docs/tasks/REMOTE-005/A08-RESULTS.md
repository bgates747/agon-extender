# R05-A08 — local WebDAV adapter results

The HTTP adapter, real wire client and staged file orchestration now pass local
checks against the actual EMOSlet engine. No bench access, flashing, emulator
changes or production selection changes occurred. **A08 remains open:** runtime
admission, media ownership and a dedicated listener/worker must still be wired;
this is not an enabled or native-client-qualified WebDAV endpoint.

## Implemented and verified

| Check | Result | Evidence boundary |
| --- | --- | --- |
| HTTP/protocol and actual spool test | PASS with ASan/UBSan | Methods, conditions, range, XML, busy rejection, body fragmentation, interrupted uploads, retained uncertainty |
| Wire integration test | PASS with ASan/UBSan | HTTP -> P4 wire backend -> actual EMOSlet C engine -> host filesystem adapter |
| P4 target object compile | PASS, all 3 translation units | Real cross compiler, warnings treated as errors; not linked/flashed firmware |
| Existing spool lifecycle/fault suite | PASS with ASan/UBSan | Includes COPY binding refinement; no physical-card claim |

`tests/test_webdav_adapter.py` runs three top-level checks; the two host binaries
contain the scenario assertions. The measured combined host test/target compilation
final run took 8.422 seconds; this is local development duration, not transfer performance.
The C engine came from agon-emos commit `5350759`; generated logs, source hashes
and target object/stack reports are retained in ignored agent evidence.

The real-engine run transfers a 9999-byte binary payload, verifies GET and ranged
GET bytes, creates/moves/copies/deletes directories and files, preserves replaced
bytes as a backup, and refuses another replacement when recovery siblings remain.
It feeds full HTTP requests with fragmented reads/writes and Finder-style chunked
PUT including Expect: 100-continue. Duplicate headers and ambiguous lengths fail
before admission. A deliberately lost activation ACK leaves the actual activated
file intact, retains uncertain P4 state, returns failure and blocks a new upload.
Corrupt replies and remote short writes do not cause hidden retries or success.

Implementation lives in `vdp/video/extender/storage/webdav`. Pin/license and
upstream/RFC references are beside the source. Upstream POSIX truncation and
nominal locks were not imported. The adapter reuses its protocol idioms while
routing all mainboard I/O through the checked wire engine. No EMOS source change
was required. P4 spool validation adds external COPY file stages under the original
parent binding; no new wire opcode or identity substitution was introduced.

## Deliberate limits

1. MOVE replacement and directory-tree replacement return 501 before mutation;
   no destructive delete fallback. File COPY/PUT retain checked backups.
2. PROPFIND supports depth 0/1 and at most 512 children with bounded XML/property
   handling. No synthetic timestamps/ETags or persistent locks. Only wildcard
   If-Match/If-None-Match conditions are supported. Full DAV compliance is not claimed.
3. Recursive work stops at the first failure; a 207 partial response names that
   failure and counts prior completed entries. Mainboard error details do not
   always distinguish a denied operation from a short write/disk-full condition.
4. Fixed-length and Finder expected-length chunked PUT are implemented. Unsupported
   extensions/trailers fail before activation. No socket override is installed on
   the existing video server; a separate raw-stream worker must own this adapter.
5. Target stack estimates show the upload call chain exceeds 8 KiB. The proposed
   dedicated worker starts with a 32-KiB budget, to be measured on hardware. File
   buffers are bounded but metadata strings/vectors still require heap budgeting.

## Remaining A08 integration fence

These are completion conditions for existing A08, not a separate invented task:
connect Channel to the actual console-owned control/file queue, require exact
READY/terminal closure for each job, enforce parent descriptor/subtree scope,
reserve/provision the P4 spool against local-SD APIs and mount changes, and attach
the bounded raw-stream adapter to a dedicated worker/listener. The finite EMOS
utility must process the declared job under that same grant. Keep the endpoint
and capabilities disabled until those implementations and A09 interleaving tests
exist. A10–A12 still own deployment, physical media/reset qualification and human
native-file-manager acceptance after bench release.
