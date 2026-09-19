# P01h — RLE2 web-frame deployment plan

## Executive summary

Author requested this plan on2026-09-16 after QUAL-004's overwhelmingly successful
static-image comparison. Reuse this existing compression task rather than create
a competing queue. **Execution authorized; contract frozen before implementation.**
Deploy the Author's RLE2 in both directions: P4 encodes optional negotiated
web frames, and P4 decodes uploaded RLE2 assets into bitmap data. Preserve raw output and unchanged graphics semantics. Evaluate
SRLE2 (RLE2 followed by szip) separately after measuring the simpler codec.
The accepted target remains512×384 at30fps; no new60fps promise.

## Naming and source observations

1. `agon-utils/utils/rle/rle2.h` names the format RLE2 and describes RGBA2222
   input. `rle2.c` writes `Cmpr` plus size and `RLE2` version1.0:14 header bytes.
   Singleton tokens use spare high bits; runs3–130 use two bytes; a run of two
   uses two singleton tokens. Payload is bounded by input length; the complete
   file is bounded by input length plus14, not input length alone.
2. `agon-utils/tests/test_images_compression.py::compress_with_srle2` invokes
   `rle2 -c` followed by `szip -b41o3`. SRLE2 is that combined local format,
   not another name for the RLE-only codec or an assumed generic SZIP library.
3. The encoder comment and implementation need careful reconciliation: singleton
   tokens distinguish fully opaque from non-opaque alpha, whereas run literals
   retain the original byte. Do not claim arbitrary four-level alpha round trips.
   Composed visible framebuffer pixels are opaque; explicitly map the captured
   RGB222 colour layout to opaque RGBA2222 and back. Do not reinterpret raw
   framebuffer palette indices as RGBA without proving the mapping.
4. Existing allocation-returning encode/decode functions are reference contracts,
   not permission to allocate/reallocate every frame in the P4 hot path. Preserve
   the Author's attribution and check licensing before copying code.

## Itemized execution plan

1. [x] H01 — Pin source commits/file hashes, licensing and exact wire semantics.
   Inspect encoder, decoder and AGM/Jukebox use, including malformed-input
   behaviour. Produce golden vectors for all64 colours, runs1/2/3/130/131,
   alternating pixels and boundary lengths. Record source defects without
   silently modifying agon-utils or unrelated port logic.
2. [x] H02 — Host round-trip qualification on retained QUAL-004 images plus
   deterministic dense scrolling, sprite-heavy, solid and noise patterns.
   Require byte-exact decoded canonical images. Report raw bytes, payload bytes,
   total framed bytes and compression ratios separately. Validate truncation,
   oversized runs, dimensions, lengths and decoder bounds. Retain reproducible
   seeds and hashes; do not add third-party reference media to tracked files.
3. [x] H03 — Freeze a versioned web protocol extension before implementation.
   P4 and browser negotiate RLE2 capability; old clients retain existing raw
   frames. Define codec ID, dimensions, stride, colour interpretation, frame
   sequence and exact decoded length. Decide explicitly whether the14-byte file
   header is retained or omitted inside the web envelope; never label a variant
   identical to the file format. Reject malformed messages; mode/palette changes
   and reconnects invalidate prior state. Raw fallback when compression offers
   no total-byte saving. Preserve the raw path for256-colour modes.
4. [x] H04 — Implement bounded encoder and browser decoder in the task silo first.
   Encode an immutable snapshot after releasing graphics locks. Preallocate
   capacity from validated mode dimensions, cap queued work and retain existing
   frame ownership until the sender is done. Do not add per-frame malloc/realloc,
   hold graphics locks while encoding/sending, or alter stock rendering commands.
   Instrument snapshot, encode, send and browser decode separately with bounded
   counters. Current raw receiver remains a compatibility control.
5. [x] H05 — Stage and verify a reversible P4 candidate and matching web client.
   Preserve actual installed image/config/startup and record rollback commands.
   Confirm bench ownership and serial-reset consequences. No MOS/mainboard VDP
   changes required. Use /test/nurples and /test/arcade/rally, never production
   replacements; use nurples-repair as the reference. No Golem. Clear mainboard
   status when starting requested hardware-notification work.
6. [ ] H06 — Matched raw versus RLE2 hardware trials with identical scene inputs,
   rendering pace and browser connection. Cap frame sends at30fps. Include idle,
   dense full-frame changes, steady scrolling, busy sprites and incompressible
   data; no dependence on Nurples bezel or game-specific sparse updates. Record
   host wired/Wi-Fi state. Capture decoded images for exact comparison, frame
   sequence/drop counts, achieved cadence and p50/p95/p99 frame intervals.
   Report snapshot/encode/send/decode ms separately, wire bytes/Mbit/s, heap
   low-water, buffer use and rendering slowdown versus output-disabled baseline.
   Use bounded repeat runs; do not infer rendering FPS from network delivery.
7. [ ] H07 — Recovery and compatibility tests: connect/disconnect/takeover, mode
   and palette changes, raw fallback, slow consumer, malformed payloads and
   bounded memory under overload. Reproduce rather than hide QUAL-004's Copper
   restart exception; stop if it invalidates the trial. No unrelated renderer
   fix under this contract. Verify old/raw clients and supported colour modes.
8. [ ] H08 — Report acceptance evidence and deployment decision. Require exact
   images, no new resets/protocol errors, bounded memory and no material native
   rendering regression; quantify headroom instead of promising universal30fps
   on every network. Restore baseline if candidate is not ready. Author visual
   review precedes default enablement/promotion; no experimental remote push.
   Commit discrete owned changes and hardware voice-notify for review.

## Required asset-decompression work — Author amendment

The P4 driver must support **RLE2 decoding as well as encoding**. Asset upload
is a required deliverable, not a deferred optimisation. Keep its tests separate
from web output so gains and failures are attributable.

1. [x] A01 — Alongside H01/H03, inspect stock buffered decompression commands and
   compression-format dispatch before defining any extension. Identify whether
   stock already accepts this exact RLE2 format. Reuse stock contracts where
   available; otherwise explicitly document a capability-gated EDP extension,
   never silently reinterpret an existing VDP command. EMOS owns routing from
   the eZ80 to EDP through the established transport; no direct bypass.
2. [x] A02 — Freeze upload/decode/bitmap lifecycle: eZ80 supplies encoded buffer,
   P4 validates format/version and declared output length, decodes into bounded
   owned storage, and exposes decoded data through the applicable bitmap-create
   command. Specify source/destination buffer IDs, dimensions, pixel format,
   completion ordering, errors, allocation limits and buffer deletion/reuse.
   Do not make clients consume partially decoded data. Allocation for asset
   creation is permitted when checked and bounded; the prohibition on hot-path
   per-frame allocation does not ban asset storage allocation.
3. [x] A03 — Implement P4 decoding using shared pinned RLE2 semantics and golden
   vectors. Test opaque colours and exactly supported transparency separately;
   resolve the singleton/run alpha limitation before claiming RGBA2222 fidelity.
   Reject truncated headers/tokens, run overflow, invalid sizes and unsupported
   versions before out-of-bounds reads/writes. Define behaviour on allocation
   failure without damaging an existing usable bitmap.
4. [ ] A04 — Upload raw and RLE2 forms of identical assets through normal EMOS
   routing. On physical P4, compare decoded bytes and full rendered images after
   bitmap creation, plotting, clipping, scaling and supported sprite use. Compare
   resulting images with stock mainboard receiving equivalent raw assets; do not
   require stock to understand an EDP-only codec extension. Include repeated
   upload/replacement/deletion, transparent cutouts and malformed inputs.
5. [ ] A05 — Report transfer bytes/time, P4 decode milliseconds, peak memory and
   bitmap creation time separately. Preserve protocol synchronization after
   rejected inputs. Include this asset path in H07 recovery and H08 review before
   declaring bidirectional RLE2 deployment complete.

Sequence: freeze A01/A02 with H01/H03; implement A03 alongside H04; qualify A04/A05
with H06/H07. No implementation is started by this planning amendment.

## Deferred follow-on experiments — not part of initial deployment

1. Delta RLE2 needs explicit arithmetic/colour domain, prior-frame identity,
   zero-delta semantics, reconnect/mode/palette keyframes, periodic recovery and
   resynchronisation after a missed frame. Zero difference means unchanged, not
   transparent black in the visible framebuffer. First establish full-frame RLE2.
2. SRLE2 adds the exact AGM entropy stage only after source/license/memory/cost
   review. Compare raw, RLE2 and SRLE2 encode CPU/wall time and wire savings;
   do not assume additional CPU work reduces cache/scheduler contention.
3.256-colour one-byte-per-pixel output remains a long-term goal. Spare-bit64-colour
   coding cannot silently encode a256-colour alphabet. No lossy JPEG/H.264 or
   game-specific redraw workaround is introduced by this plan.

## Authority and status

This revision refines the already frozen P01h compression experiment following
explicit Author request for a deployment plan. The Author now authorizes execution, including a clean-sheet P4 codec implementation
and reversible qualification under the gates below.
QUAL-004 remains open for exception review; its successful static pixels are
reference evidence, not clearance of its unresolved transition failures.

## AGM wire-contract reuse — Author direction and initial archaeology

Author requires reuse of the movie player's existing function contracts unless
recent upstream assignments collide. This supersedes any suggestion to invent
an unrelated EDP command before checking historical compatibility.

Read-only inspection on2026-09-16 found two historical contracts in AgonJukebox:

| Pinned source | Command bytes | Meaning evidenced by caller |
|---|---|---|
| `agm` at `39e800c01826b382a9498e0130e9dbb4e766fad2` (2025-02-15), `src/asm/vdu_buffered_api.inc` | `23,0,160,dstLo,dstHi,65,srcLo,srcHi` | TurboVega decompression |
| Same source, plus `src/asm/agm.inc::pv_cmd_draw` | `23,0,160,dstLo,dstHi,67,srcLo,srcHi` | Custom szip decompression, adjacent to stock command65 |
| Later `origin/agz` at `a8f1075c605a78e573d488dce46d1bfacee8d3a8` (2025-05-10), `src/asm/vdu_buffered_api.inc` and `agm.inc::agm_next_unit` | `23,0,160,dstLo,dstHi,65,srcLo,srcHi` | Generic decompression; same source/destination supported by caller; SRLE2 calls twice to unpack the two layers |

Buffer IDs are16-bit little-endian. The wrapper's trailing padding byte is outside
its transmitted `@end-@cmd` length. The later caller suggests compression-header
dispatch through command65, rather than a separate opcode per codec. That is
caller evidence; locate its matching custom VDP implementation before treating
header dispatch, errors or in-place operation as fully recovered contracts.

Upstream collision check: read-only `git ls-remote` on2026-09-16 returned
`c7ac293d2aa81ddfa693390549bcd909069c8fc3` for AgonPlatform/agon-vdp HEAD/main,
matching the inspected official checkout. `video/agon.h` assigns buffered0x40
compression,0x41 decompression and0x48 bitmap expansion; no0x43 assignment was
found there or in its buffered dispatcher. Thus the earlier67 slot has no observed
collision in this pinned main, but remains historical **szip**, not an RLE2
assignment to repurpose casually. Existing65 must retain stock TurboVega semantics.
Upstream reference: https://github.com/AgonPlatform/agon-vdp/tree/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video

A01/A02 must now recover the later AGM custom-VDP decoder/header dispatch and
inventory relevant upstream release/development assignments again before freezing
implementation. Prefer the later compatible generic contract if confirmed;
retain earlier67 compatibility only as justified by its real format/handler.
Record any actual collision and proposed resolution for review. Do not allocate
new command bytes, or assume that no collision in main rules out all branches.
In-place decode requires retaining source ownership until successful completion.
No firmware or application changes were made during this contract archaeology.

## Clean-sheet implementation authorization — 2026-09-16

Preserve earlier wire contracts where practical, subject to current upstream
collisions. The old custom Xtensa codec is not an official VDP library and its
internal API, layout, algorithms and historical bugs impose no compatibility
requirement. Write the P4 encoder/decoder afresh for its RISC-V target. Historical
code supplies format evidence and comparison vectors, not an implementation to
port. Preserve actual official VDP semantics outside this extension.

Start with bounded portable C/C++ and inspect compiler output and measured P4
cost. Consider P4-specific instructions, alignment and memory placement only
where supported by the actual target/toolchain and evidence. RISC-V alone does
not imply a codec speedup; assembly and speculative cache/DMA changes are not
prerequisites. Keep full-frame encode/decode allocations out of the hot loop.

Execute in discrete evidence-producing chunks, committing completed checkboxes.
First chunk: recover format/dispatch, implement the new bounded codec and host
qualification; freeze asset/web integration contracts. Hardware voice notification
at the chunk's review point. Subsequent integration retains H05–H08's hardware
and default-promotion gates; no experimental push. Do not conflate passing host
codec tests with deployed P4 or browser acceptance.

## One-hour goal amendment — 2026-09-16 22:21:26 UTC

Author now sets a hard one-hour execution limit, ending23:21:26 UTC. Develop,
test and benchmark iteratively rather than only delivering a first implementation.
Reserve final10minutes for rollback/report/voice notification. Prioritise codec
correctness and measured P4 costs, then integration as time permits. Mark unfinished
deployment gates explicitly; no passing host test substitutes for hardware evidence.

## Execution evidence so far

H01–H04 and A01–A03 have candidate implementations/contracts and passing host
checks. `CONTRACT.md` pins historical dispatcher, wire bytes and limitations.
agon-utils is Unlicense; historical personal VDP is MIT. Clean-sheet codec uses
format evidence, not copied legacy implementation. Evidence is under `evidence/`.
Seven routed asset image cases and raw/compressed web static controls pass on
candidate r03; these do not yet complete all A04/A05 or recovery/performance gates.

## One-hour execution review — 2026-09-16

The bounded execution produced iteratively benchmarked clean-sheet codec and
asset/web candidates. See [RESULTS.md](RESULTS.md) and [TABLES.md](TABLES.md).
H06 is partial: a matched 1800-cycle Nurples trial per condition passed, plus
static/incompressible controls; repeated wired trials, Rally and detailed phase
accounting remain open. H07 is partial: malformed assets, raw compatibility,
reconnects and incompressible fallback passed; overload/failure injection and
broad mode/palette coverage remain open. A04 has exact bitmap-transform and
software/hardware-sprite pairs; A05 has codec timings, not full path accounting.
H08 awaits the remaining qualification and Author production-promotion decision.
Unchecked gates are intentionally not represented as complete by this timed run.

## SRLE2 iteration — compile-only authorization

Continue this same task in [srle2/README.md](srle2/README.md): original szip source,
P4 target, historical command65 wrappers. Bench is owned by another agent.
No flash or runtime tests until Author release; RLE2 web wire format unchanged.

## Author decision — 2026-09-19

RLE2 is now the accepted default for browser video output, frozen in
[ADR-0021](../../../../../decisions/ADR-0021-rle2-browser-default.md) and the canonical
browser-video contract. This resolves default-selection approval only; remaining
qualification/promotion gates above are not silently marked complete. Future
client/deployment checks must verify RLE2 remains the default negotiation.
