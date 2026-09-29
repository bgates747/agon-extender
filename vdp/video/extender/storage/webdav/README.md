# Admitted mainboard WebDAV adapter — development only

The portable HTTP adapter and wire backend are locally tested against the real
EMOSlet C file engine and P4 spool. The maintained native `p4-console` profile
explicitly enables the finite Legacy/negotiated-ExCom runtime on
port 8081; physical/native-client acceptance remains separate. The current manual listener, video server and
production bundle are unchanged. Native-client and physical qualification remain.

## Composition boundary

1. `serveConnection` handles one raw HTTP/1.1 request then closes. `Stream` must
   belong to a dedicated transfer worker with bounded socket read/write deadlines.
   It retains header read-ahead and decodes Finder-style chunked PUT without
   modifying `esp_http_server` or touching the existing video/input connection.
   `runtime.cpp` supplies that dedicated acceptor/worker when explicitly enabled.
2. `Adapter` translates HTTP semantics and rejects concurrent calls immediately.
   Its atomic guard is additional bookkeeping, not EMOS permission. Local OPTIONS
   requires no grant; every mainboard-backed request requires `Backend::begin`.
3. `WireBackend` obtains the full binding through `Channel::enter`, then emits
   checked file records and validates every reply's session/sequence/opcode/CRC.
   `Channel` must implement the actual POLL/OFFER/DECIDE/descriptor/READY lifecycle
   through the existing console-owner queue; it must check the immutable operation
   and full live binding on every exchange, and wait for terminal closure in leave.
   It must serialize against the manual listener and application-owned jobs.
   No direct UART writer, fresh mutation retry or delayed job queue is permitted.
4. The composition must reserve the supplied P4 spool directory against local-card
   HTTP operations and mount changes. It supplies an explicit quota and verified
   mounted directory. The runtime creates its private spool directory under the
   card lease without formatting; there is no RAM fallback.
5. The finite utility/control peer and transport/media owners are not provided by
   a test Channel. Do not enable an endpoint until these are implemented and
   qualified. Both Legacy/ExCom deployment gates remain in the parent task.

## Behavior and limits

| Method | Implemented local behavior |
| --- | --- |
| OPTIONS | Allow list and [capability URI](../../../../../docs/protocols/staged-webdav.md); no DAV class or persistent lock advertisement |
| PROPFIND | Depth 0/1, at most 512 children; bounded allprop/propname/explicit prop XML subset; unknown properties receive 404 propstat |
| GET / HEAD | Verified P4 SD snapshot for GET; exact length; single open/closed/suffix byte ranges; HEAD has no body |
| PUT | Fixed Content-Length or chunked with X-Expected-Entity-Length; complete local stage before checked EMOSlet transfer/activation |
| MKCOL | One directory, parent must exist, no request body |
| MOVE | Same configured origin, disjoint paths, absent destination only |
| COPY | File replacement uses checked staging/backups; absent directory tree may be copied recursively or depth 0; no directory merge/replacement |
| DELETE | Root/utility/journal preflight, recursive depth at most 16, stops on first error |

Each request owns one job. Recursive operations report the failing path and count
of completed entries in a 207 response when partially completed; later entries
are not run. There is no tree atomicity. GET releases mainboard ownership before
sending the completed local snapshot. Mainboard checked upload verifies stage,
independently reads it back, activates, then independently checks the activated
file's length/CRC. Existing `.p17bak` siblings remain; repeated overwrites can
require explicit recovery cleanup, exactly as with the checked CLI workflow.

Ordinary PUT replaces an existing file unless a supported precondition forbids
it. COPY/MOVE default Overwrite to T; F rejects a collision with 412. Unsupported
replacement operations return 501 before mutation. If-Match/If-None-Match support
only `*`; other entity tags, date conditions, DAV If and If-Range are rejected
rather than guessed. No ETag or timestamp is fabricated from file size. No LOCK
or UNLOCK success is invented. These limitations prevent a DAV compliance claim.

Paths are normalized absolute ASCII, at most 120 bytes; staged upload/copy targets
are at most 112 bytes to allow the existing sibling readback. Encoded separators,
traversal, control characters and invalid FAT characters are rejected. Destination
absolute URLs must match the configured origin exactly; alternate host aliases
are not silently accepted. PROPFIND rejects unlimited depth and overlarge listings
before starting the 207 response; larger-directory pagination is not implemented.

The XML subset excludes DTD, entities, comments, CDATA, include and property
values. HTTP headers are limited to 4096 bytes/32 fields, PROPFIND body to 4096
bytes/24 requested properties. Duplicate headers are rejected. Chunk extensions
and trailers are unsupported and fail before remote activation. Conflicting
Content-Length and Transfer-Encoding fail. `100 Continue` is emitted only when
an admitted body is first read. One-request close semantics avoid reusing chunk
parser state or interpreting excess body bytes as another operation.

Local seal is not commit. `stagedPut` persists the activation marker before remote
activation; an absent or invalid reply retains evidence and returns failure.
Startup/retry never consumes retained spool files as permission to execute.
Malformed uploads before remote transfer may explicitly abandon their local stage.
Other failed stages remain for deliberate recovery. Remote FatFS denied/short-write
errors share an existing wire detail and cannot always be classified as disk-full;
the adapter does not claim otherwise.

## Memory and validation

No entire file is held in RAM. Data buffers are at most 4096 bytes and wire chunks
212/216 bytes. Listing metadata is bounded to 513 entries; strings/maps/vectors
still consume heap and must be budgeted. Target compiler stack estimates include
5120 bytes for Adapter::handle, 4160 for stagedPut, 4128 for spool digest and 1280
for serveConnection. Their nested upload path exceeds an 8-KiB HTTP task stack.
A dedicated worker needs a conservative stack budget (32 KiB initial development
candidate), followed by target high-water measurement; no runtime task exists yet.

Run `python -m unittest discover -s tests -p test_webdav_adapter.py -v` using the
project venv. Set `AGON_P4_CXX` to the P4 cross compiler for target object checks.
The real-engine test uses sibling agon-emos (or AGON_EMOS_ROOT); its POSIX test
adapter is not FAT power-loss evidence. Tests use memory streams/temp files, no
network listener, emulator or device. Source attribution is in PROVENANCE.md.
