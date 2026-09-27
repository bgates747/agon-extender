# R05-A08 — admitted WebDAV development contract

Implement the P4-side WebDAV adapter locally, without bench access or enabling a
network endpoint in the installed/default firmware. Reuse the pinned MIT server's
protocol idioms, replacing direct POSIX mutations with an explicit admitted
backend. Production stays unchanged. Runtime admission/card composition and
physical/native-client qualification remain downstream gates, not inferred from
host tests.

A08-01 [x] Record pinned source provenance and the storage/HTTP boundary. Every
mainboard operation requires one backend grant; concurrent requests fail busy,
never queue. OPTIONS is local. No fake LOCK success or invented ETags/timestamps.

A08-02 [x] Implement bounded path/header parsing, PROPFIND depth 0/1, GET/HEAD and
single byte ranges, staged PUT, MKCOL, MOVE, COPY and DELETE. Honor overwrite and
preconditions or explicitly reject unsupported forms before mutation. Failed or
uncertain mainboard completion never returns success. Preserve partial recursive
outcomes and recovery evidence. No destructive replacement fallback.

A08-03 [x] Integrate a bounded request-body reader for ordinary and Finder-style
chunked PUT, including exact expected-length validation, malformed/truncated body
rejection and cancellation. Keep HTTP serving independent of video/input; do not
install upstream socket overrides on the existing video server.

A08-04 [x] Host-test methods, admission/refusal/release, failures, ranges,
conditions, paths, fragmentation and interrupted bodies. Compile adapter with the
P4 toolchain. Update current documentation, record exact local evidence and any
remaining integration boundaries. No emulator changes, hardware/network device
requests, flash, production promotion or native-client acceptance claim.

Frozen 2026-09-27 under the Author's development-only instruction. Backend
interfaces must describe concrete obligations; test doubles are not a deployed
EMOS grant implementation. Keep A08 open where those obligations remain unwired.

Local contract complete; [results](A08-RESULTS.md) distinguish the real file engine
from the simulated READY/transport in tests. A08 overall remains open for its
runtime composition fence. The body adapter uses a separate raw stream, not the
upstream session override. External COPY retains its parent binding in spool
records and changes neither the record layout nor the mainboard file protocol.
