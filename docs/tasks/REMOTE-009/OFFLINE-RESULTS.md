# Staged fast file transfer — offline results

The P4 worker, SD staging and explicit host client pass offline tests. HTTP
polling and host journals no longer gate individual UART file records. Native
P4 compilation/action validation passes. Nothing has been deployed or measured
on hardware; the occupied bench remains untouched.

## Structural comparison

For an exact 1,100,000-byte upload, excluding admission/completion control calls:

| Work | Existing fast RPC client | New staged client |
|---|---:|---:|
| Host WRITE transactions, 212B each | 5,189 | 0 |
| Bulk HTTP payload submissions | 0 | 1 |
| Host state saves attributable to WRITE records | 10,378 | 0 |
| Job-boundary host state saves, successful upload | Additional control-operation saves | 3 total |
| Host pending poll gates next UART record | Yes, 40ms between HTTP retries | No |
| UART WRITE records/replies | 5,189 | 5,189, driven locally by P4 |
| Whole-file payload verification downloads | 0 | 0 |

These are code-path counts, not throughput measurements. Status queries and
explicit release do not gate individual UART records. Each new state save
syncs its file/directory at job boundaries. Downloads add a partial-file
ownership journal boundary and sync the completed host output.

## Validation

1. **51 Python-managed checks pass** across paired engine/HTTP, staged client,
   existing SD client/queue/codec and native profile tests. The paired check
   compiles two C++ executables against the actual EMOS sdserve file engine
   and filesystem adapter. Address/undefined-behavior sanitizers run with leak
   detection disabled for the ptrace sandbox.
2. Actual P4 queue/engine tests cover empty, 1/211/212/213B, 65,537B and 1,100,000B
   payloads; exact bidirectional comparisons; complete activation; no payload
   readback on upload; wrong reply identity; transport loss/reset; eZ80
   disk-full/short-write/sync errors; P4 full-output failure; quota rejection.
3. Actual HTTP/worker source runs with fake SDK scheduling/HTTP calls: queue/
   media exclusion, active release refusal, download re-fetch after send
   failure, changed mainboard boot, missing/busy card, interrupted HTTP staging,
   preservation of unknown colliding files, explicit failed discard and input
   validation. The fake does not model RTOS concurrency, UART electrical timing
   or FAT power failure. Native compilation separately checks the real SDK API.
4. Host tests cover bulk upload, job-boundary persistence, empty/binary
   download, lost admission/cleanup replies, no uncertain POST replay, partial
   HTTP retry, crash between output publication and completion journal,
   reset/failure retention and exclusive state ownership.
5. EXIT cache regression passes: listener closing presence preserves the
   completed response for the ordinary HTTP client to collect.
6. Native p4-console/P4-PC/browser compile passes with 38/38 selected source
   compile/archive/link actions validated. Final edited sources are rebuilt
   in the wrapper-generated CMake project and the native validator rerun.
   The new storage unit retains generated board-header provenance. Local
   products are dirty, compile-only **UNVERSIONED-DO-NOT-DEPLOY**, not an
   identified candidate, matched installed HDMI/USB build or production archive.
   The compile-only application is 1,621,216 bytes, SHA-256
   `b9ff4beef951c26a085de0691fe75244f3423862e57418ae7b27e9879f2f72e7`.

## Implementation and remaining boundary

`vdp/video/extender/storage/fast/engine.hpp` owns the network-independent file
loop; `fast/http.cpp` owns SD staging/worker/HTTP lifecycle. `sd_service.hpp`
and `sd_target.hpp` add an exclusive generation-bound claim to the existing
console-owned UART queue. `scripts/sdcard_staged.py` owns job state and bulk
delivery. Ordinary `sdcard.py` is unchanged.

There is no resident EMOS or installed listener change. No processor-link
checksum or verification download is introduced. P4 explicitly frees the stdio
buffer before FreeRTOS task deletion, which does not unwind C++ local objects.
Failed/uncertain jobs retain staging. Discard does not cancel or clean a
mainboard journal; interruption may require stopping/restarting the foreground
listener before normal recovery.

The carrier retains 212/216-byte request/reply records. The SD utility still
opens/seeks/closes the mainboard source for each READ; local task scheduling
also remains. Jukebox's continuous sender is a target for further comparison,
not a measured result or capability of this implementation.

Author bench release must precede matched installation, physical backpressure/
error/coexistence checks and timing comparison. Production, startup, installed
firmware and Wolf3DOrig's transfer are unchanged.
