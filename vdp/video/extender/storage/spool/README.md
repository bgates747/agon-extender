# P4 transfer spool — development storage API

This is a locally tested storage primitive, not an enabled file service. No
firmware task, HTTP handler or UART capability instantiates it. The next integration
must supply admission, media ownership and endpoint behavior. Bench qualification
is pending. The current manual listener and P4-local file API are unchanged.

## Owner and placement

The P4 foreground transfer worker owns one `spool::Store` for an already provisioned,
private directory on a verified mounted card. Proposed card-relative placement is
`/tmp/extender/spool`; it is independent of the same prefix on the Agon card.
The constructor takes the complete VFS directory and explicit payload-byte quota.
It never mounts media, creates directories, or falls back to RAM. One slot bounds
recovery inventory; old files block the next job until explicitly resolved.

Before enabling this module, the P4 composition must exclude its namespace from
ordinary local-card HTTP access and serialize mount/unmount/card mutations with
this worker. `Store` is not thread-safe, a locking layer, or protection against
an unrelated writer changing its files. Native FAT has no symlinks; host tests use
an isolated temporary directory. This is not a general POSIX sandbox.

## API sequence

1. Construct `Job` with the exact 28-byte admission binding, validated two-path
   descriptor, expected byte count, and optional expected CRC32. `begin` rejects
   an occupied directory, excessive size or invalid identity/descriptor. The limit
   is the smaller of the supplied quota and 2 GiB minus one, preserving signed
   32-bit target seek offsets. Metadata adds at most six 304-byte records; FAT
   allocation overhead and filesystem free space are additional. ENOSPC is a
   retained failure, not permission to exceed the quota or delete recovery data.
2. `append` accepts only consecutive offsets, at most 4096 bytes per call, under
   the same live binding. It incrementally checksums the bytes. Partial writes
   may persist, but any write failure invalidates the live owner; no hidden retry
   or resume follows. `seal` requires the declared length, optional expected CRC,
   sync/close and independent payload readback before writing a complete marker.
3. `read` serves only a sealed/confirmed snapshot under the current live binding.
   Partial data and recovered owners are never served. Each read is at most 4096
   bytes; the caller owns its output buffer. Source/destination files are not
   modified by this layer: it handles only its private payload and records.
4. Before requesting remote activation, call `activationStarted`. Proceed only
   on success. After an exact remote commit acknowledgement, call `confirmed`.
   Do not use local seal/CRC as evidence of remote commit. Missing ACK leaves the
   state uncertain; automatic deletion and restart execution are prohibited.
5. `invalidate`/destruction close handles and retire the volatile owner without
   deleting bytes. `inspect` validates retained records and, for sealed payloads,
   their complete size/CRC. It reports state, never resumes an old grant. Every
   operation receives the full binding; a stale boot/generation/job/grant fails.
6. `discard` means explicit abandonment/release, not a destructor or timeout.
   It refuses uncertain activation. Confirmed jobs can be released; incomplete
   or unused sealed stages can be explicitly abandoned when the owning request
   ends. Cleanup first syncs a retirement record, then removes only fixed owned
   files, retaining retirement proof until last. Interrupted cleanup can finish
   after restart. Unknown files, malformed records and integrity failures block
   automatic cleanup and require inspection/preservation outside this API.

An uncertain job recovered after restart cannot be confirmed using the stale
owner. Future integration must reconcile the remote result under a new valid
control exchange, or retain/export evidence for explicit operator recovery.
This module deliberately supplies no “pretend committed” force-clean API.
No age-based cleanup or deadline is encoded here; the request owner invalidates
its lease on disconnect, reset or expiry and chooses only justified abandonment.

## On-card record layout

All records are 304 bytes, explicit little-endian fields, with no native packing.
Bytes 0..3: `ESP1`;4..31: binding;32..33: descriptor length;34: expected-CRC flag;
35: zero;36..39: expected size;40..43: expected CRC;44..291: zero-padded descriptor;
292..295: CRC32 of preceding 292 bytes;296..299: verified payload CRC;
300..303: CRC32 of preceding 300 bytes. Canonical re-encoding checks padding,
reserved bytes, lengths, identity and both checksums.

`manifest` is immutable and precedes payload creation. `complete` follows verified
payload closure. `inflight` precedes remote activation; `committed` follows its
acknowledgement. `retired` contains the full record, allowing cleanup even after
manifest removal. Marker files are exclusively created, closed and synced; there
is no dependency on POSIX replacement-rename semantics unsupported by FatFS.
A torn marker blocks reuse. These checks detect many failures but do not promise
power-loss atomicity or physical-card persistence based on Linux tests.

## Local verification

From the repository root:

```sh
g++ -std=c++17 -Wall -Wextra -Werror -fsanitize=address,undefined -g \
  -I vdp/video tests/storage/spool_test.cpp -o /tmp/extender-spool-test
/tmp/extender-spool-test
```

Tests use actual temporary files and a small syscall fault seam for ENOSPC, sync
and removal errors. No device or network operations. See the task's
[A06 results](../../../../../docs/tasks/REMOTE-005/A06-RESULTS.md) for exact scope.
