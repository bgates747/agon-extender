# R05-A06 — local staging results

The P4 spool primitive is implemented and passes local filesystem/fault tests
and P4-toolchain object compilation. It is deliberately uninstantiated: no new
HTTP/UART behavior, capability advertisement, device access or flashing occurred.
Mainboard transfers still require the previously documented interfaces. Physical
FAT persistence and integration remain unqualified while TRS-80 owns the bench.

## Implementation and results

Code: `vdp/video/extender/storage/spool/store.hpp`. Its adjacent README is the
maintained development API/record/recovery guide. Tests:
`tests/storage/spool_test.cpp`, compiled with address/undefined-behavior sanitizers,
`-Wall -Wextra -Werror`. Both sanitizer execution and target object compilation pass.

| Check | Local result | Boundary |
|---|---|---|
| Binary snapshots | PASS: 0,1,211,212,213,4096,8193 bytes | Consecutive chunks, independent seal readback, exact exported bytes |
| Partial versus complete | PASS | Partial reads refused; size/CRC required before complete marker |
| Admission binding | PASS | Every changed binding byte rejected; invalidation/restart cannot resume old work |
| Quota/missing storage | PASS | Explicit quota and signed seek-size limit; no directory creation or RAM fallback |
| Storage full | PASS, injected ENOSPC including partial writes | Distinct full result; partial payload and records retained |
| Sync/torn metadata | PASS, injected failures | No success on failure; malformed state blocks reuse/deletion |
| Payload corruption | PASS | Changed, short, extra and missing bytes detected on inspection |
| Remote activation uncertainty | PASS | Persisted before activation; absent ACK prevents discard even after restart |
| Confirmed commit | PASS | Explicit confirmation persists; permits release, not automatic job replay |
| Cleanup interruption | PASS at each of six removals | Retirement proof survives until final deletion; explicit retry can finish |
| Unknown files | PASS | Preserved; staging directory becomes unavailable for new work |
| P4 compiler | PASS, explicit Store template instantiation | Object compilation only, not a linked/deployed firmware |

P4 compiler stack estimates: digest 4128 bytes, inspect 1584 bytes, discard 336
bytes. The recovery call chain can therefore consume roughly 6 KiB before libc/caller
frames; these are per-function static estimates, not a measured task high-water
mark. The eventual worker must budget/check stack explicitly. No whole-file RAM
allocation occurs. Each payload operation uses at most 4096 bytes; records are 304
bytes. A caller-supplied quota bounds payload bytes; fixed metadata and FAT cluster
allocation are additional. No production quota or HTTP timeout is implied.

Local generated logs/objects/hashes are retained under `agents/remote005-spool`.
The initial compile/test sequence took approximately 1.84 seconds of host wall time;
this is build/test duration, not device performance or a transfer-rate result.

## Recovery and integration boundary

1. Single private slot, proposed P4-card path `/tmp/extender/spool`; the caller
   verifies mounted storage and provisions it. No current endpoint reserves or
   exposes that path. Before enabling the worker, reserve it against ordinary
   local-card HTTP mutations and serialize card/mount ownership.
2. Complete staging is not mainboard commit. The worker must journal activation
   before sending it and only record confirmation after an exact matching reply.
   Reset/invalidation retires the live owner, preserves bytes and never queues
   delayed execution. Malformed or uncertain recovery remains blocked rather
   than guessing that a destination was or was not committed.
3. An expired/disconnected request calls invalidate; abandonment is explicit.
   There is no speculative TTL deletion. A recovered uncertain job needs a future
   valid reconciliation exchange or explicit operator preservation/recovery; this
   layer cannot turn a stale grant into a fresh execution permission.
4. ExCom framing, finite mainboard utility, WebDAV mapping, active lease timing,
   namespace integration and real-card/reset testing remain in existing downstream
   work items. The frozen A06 local storage scope is complete; this is not
   end-to-end feature acceptance or a production promotion.
