# P4-staged fast mainboard file transfers

The development P4 worker removes HTTP request/reply turnaround and host journal
writes from the mainboard's per-record transfer loop. It stages complete files
on the P4 card in both directions. Existing EMOS/sdserve major2 UART records
remain the base carrier. The optional matched parallel-upload trial below
replaces only upload payload movement. Bounded hardware results exist; neither
that trial nor the staged interface selects a new complete production release.

## Ownership and requirements

1. The host explicitly starts one job. EMOS must already have admitted the
   foreground checksum-free `sdserve --fast` listener in Legacy mode. No test,
   startup rewrite, mode switch, keyboard injection or reset starts a job.
2. P4 reserves its physical card through the existing nonblocking MediaLease.
   It uses private `/tmp/extender/spool/fast-BOOT-ID.data` and `.state` files;
   local HTTP/file-manager services cannot expose that private directory.
   Maximum declared file size is 32MiB; actual media-full errors remain errors.
3. HTTP upload receives/syncs/closes the P4 file before P4 starts mainboard I/O.
   For download, P4 completes/syncs/closes the snapshot before serving HTTP.
   The P4 worker uses 8KiB stdio buffering to coalesce small UART records into
   P4 SD operations. Only the existing console task transmits UART bytes.
4. A generation-bound worker claim excludes ordinary `/sd/rpc` requests.
   EMOS boot/protocol changes, listener closure and transport loss invalidate
   the claim. A stale worker cannot release or submit through a later claim.
   Failure cancels any unsent pending queue item; it does not replay a job.
5. The installed SD utility retains target-adjacent journals/backup semantics
   and its write/sync/close error checks. The base UART staging integration adds
   no resident EMOS bytes; the optional parallel pair below has its own matched
   gateway. Neither adds CRCs, substitute checksums, whole-file verification
   reads or a supported raw UART bypass.

## Optional parallel upload payload

The [trial manifest](../mainboard-sd-parallel-trial.json) pins the matched P4,
EMOS and private foreground MOSlet. Explicit `--fast --parallel` selection
advertises HELLO capability0x80. After HTTP/P4-SD staging, P4 allocates and
loads one complete PSRAM source before admitting the payload. P4 then sends
SD operation15 with little-endian transfer-ID32 and declared-size32; the utility
requires the existing unfinished BEGIN at offset0 with the same nonzero size.
The successful reply returns transfer-ID32 and final-offset32. Existing FINISH
and ACTIVATE follow only after successful physical and file-service results.

EMOS owns UART parking, shared Port C pins and reciprocal restoration. P4 drives
eight data lines through externally clocked PARLIO loop DMA; eZ80 owns CLOCK
and holds VALID active across the payload. The utility writes at most512 bytes
per FatFS slice while CLOCK is paused. There is no per-slice or per-byte UART
acknowledgement. P4 requires exact declared CLOCK count and one VALID interval
(two edges), then stops DMA and releases data pads before freeing the source.
Whole-file PSRAM capacity is required; source preparation/admission failure
never silently switches carriers or replays a request. Empty files retain their
existing control-only path. Downloads remain UART.

The original upload trial filters CLOCK. The consumer-repair trial also filters
VALID using the pinned SDK's fixed two-IO_MUX-sample hardware filter; strict
counts and rejection of sustained extra pulses remain. Filtering does not
establish the electrical origin of the observed extra edges.

Optional HTTP status fields preserve `parallel_prepare_us` (P4 monotonic source
loading/allocation), `parallel_active_ms` (armed receive including SD pauses),
`parallel_handover_ms` (remaining physical coordination), `parallel_phase` and
`parallel_outcome`. Retained signed `parallel_clock_count` and
`parallel_valid_count` report the actual proof samples; -1 means unavailable.
These are not calibrated wire rates. The original ten-file comparison and the
[consumer repair record](../tasks/PORT-008/UPLOAD-REPAIR-R01.md) bound evidence.

## HTTP contract, interface version 1

Use the ordinary P4 HTTP origin. `GET /sd/fast` returns JSON with `protocol:1`,
P4 service `boot`, job `id`, `phase`, `bytes`, `size`, `records`, `error`,
`remote_status`, `filesystem`, `stage_us` and `mainboard_us`.

| Phase | Meaning |
|---|---|
| 0 | Idle |
| 1 | Receiving/saving HTTP staging file |
| 2 | Staged, worker scheduled |
| 3 | P4 worker transferring through admitted EMOS listener |
| 4 | Complete, including required sync/close and optional activation |
| 5 | Failed; local stage and any mainboard journal remain for inspection |

1. `POST /sd/fast`: headers `X-Extender-Job` (nonzero eight lowercase hex
   digits), `X-Extender-Boot` (same encoding, current P4 service boot),
   `X-Extender-Operation` (`put`/`get`) and `X-Extender-Path` (absolute ASCII
   mainboard path, at most112 bytes for put/120 for get). For put, the body is
   exactly the file and `X-Extender-Activate: 1` is required. This job completes
   one replacement; stage-only transactions retain the existing RPC client.
   For get, the body must be empty and activation omitted. Admission returns
   202 plus JSON; an existing retained job returns 409. No duplicate POST is
   automatically replayed or treated as a new transfer.
2. `GET /sd/fast/data`: completed-download snapshot, with matching job/boot
   headers. HTTP can be repeated against the same completed P4 file after a
   network interruption without executing another mainboard transfer.
3. `DELETE /sd/fast`: matching job/boot headers release a completed spool.
   Failed jobs additionally require `X-Extender-Discard: 1`. Active jobs cannot
   be deleted. This removes only files created by this job; it never cleans
   mainboard journals or automatically scans/deletes earlier-boot spools.
4. Mutating requests reject browser Origin headers. Busy/missing local media
   or an unavailable matching listener returns 503; malformed admission 400.
   Errors after staging begins retain a failed job instead of implying success.

Job error values: 0 none, 1 invalid plan, 2 transport/uncertain completion,
3 protocol/identity error,4 remote service error,5 local staging error,
6 file exceeds quota. `remote_status` uses the existing SD protocol status;
`filesystem` reports its FatFS error where provided.

## Timing, durability and recovery

`stage_us` covers initial local staging, including upload HTTP receipt and its
file flush/sync/close. `mainboard_us` covers worker file open, queue admission,
   local UART request/reply/file loop and final local close/sync. Both use P4
esp_timer monotonic microseconds with no independent oscillator calibration.
Job-boundary metadata writes, scheduling and HTTP download delivery are not
included in those two counters. Host results separately record monotonic HTTP
upload/download seconds and wall-clock total job elapsed seconds; a clock
adjustment can affect the latter. These are distinct scopes, not CPU cycles.

The host durably records its job before POST and confirmed delivery before
DELETE. `resume` only observes this job and optionally retrieves its completed
P4 snapshot; it never resubmits a file operation. Loss of P4 boot/job identity
requires deliberate inspection of retained P4 files and mainboard journals.
P4 writes metadata at job boundaries, not per UART record. Completion metadata
failure is a failed job even if remote activation may already have succeeded;
inspect the destination before deciding any new action.

No power-atomic FAT replacement or byte-integrity proof is claimed. Exact
counts and filesystem results do not detect equal-length content corruption.
Only explicit discard removes a failed P4 spool. Existing mainboard recovery
tools remain available after the worker relinquishes its queue claim.

The old RPC tool remains supported separately; it cannot interleave with an
active worker. Remaining212/216-byte UART replies and local task scheduling
still impose costs. The accepted sequential-reader utility removes the earlier
per-READ open/seek/close cycle; its identities are in the current SD guide. The implementation and
bounded hardware comparison are tracked in [REMOTE-009](../tasks/REMOTE-009.md).
The [measured result](../tasks/REMOTE-009/STAGED-RESULTS.md) passes Legacy files
through1.1MB and error/CLI handback with a priority4 worker. Production remains
unchanged; this does not qualify every mode, failure or power-loss boundary.
