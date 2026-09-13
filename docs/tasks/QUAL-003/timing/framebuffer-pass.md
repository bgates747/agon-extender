# Framebuffer-first hardware pass — 2026-09-13

Author authorization: resume hardware video tests with sole Extender ownership;
exclude the previously failed sprite test, and prioritize P4 framebuffer work
with no additional video output. The Author confirms their browser is closed.
This amendment governs the next pass over the earlier browser-connected order.

1. Preserve the original r01 corpus and failed CSV. This bounded variant omits
   BSP30_22 and BSP30_23 (aligned eight/sixteen RGBA8888 hardware sprites), plus
   BSP30_24 which depends on the omitted sixteen-sprite activation. Keep the
   independently resetting BSP30_25. Every retained payload/probe must remain
   byte-identical. Record all three omissions, not just a smaller result count.
2. Use the existing reviewed fixture logic and diagnostic wire contract, with
   a separately identified generated case table and build. There are 61 cases,
   976 intervals across one off and three on pairs. Preserve original source,
   generated corpus, artifact hashes and the builder in the run bundle.
3. Keep P4 browser/WebSocket output disconnected throughout measurement. Check
   retained output counters before and after; no video snapshot/send progress
   should occur. No video or serial-stream observer runs during timed work.
   A sparse read-only SD-status poll may detect the batch returning to sdserve;
   it reads P4 state without UART traffic. Record that observer as measurement
   overhead, and do not confuse it with video output.
   The idle network service remains enabled; this is not a network-disabled build.
4. Current installed P4/EMOS already contain the private graphics diagnostics;
   verify their identities and preserve them. Back up and independently verify
   the actual mainboard VDP flash before temporarily installing the reviewed
   timing application. Restore the actual pre-test application afterward.
5. Mode 20 remains 512x384, 64 colours, single-buffered. External CLI/batch
   setup selects both modes; the fixture never changes them. Mainboard precedes
   P4, one instrumentation-off pair then three enabled pairs. No keyboard or
   browser input during timed intervals. Preserve partial results on failure.
6. With no snapshot demand, P4 hardware-sprite output decoration may record zero
   work. That is a measurement boundary, not proof that visible hardware sprites
   are free. Report primitive/software-sprite work, drain, submit and callback
   times separately; do not call them game FPS or sum nested scopes. Off still
   includes the original hook locks/fences; the earlier interference caveat holds.
7. Collect SD output through the accepted service after fixture return. Validate
   exact sequence/counts against this variant's corpus. Recover ordinary firmware,
   keyboard, CLI and SD operation, then alert the Author on hardware (emulator
   fallback if hardware alert is unavailable). Stop for review before output
   tests, Nurples automation or renderer changes.

## Execution checklist

- [x] Inspect current admission and source; record explicit exclusions and output boundary.
- [x] Build and check the reduced corpus against the unchanged original bytes.
- [x] Preserve actual mainboard firmware and deploy the reviewed diagnostic application.
- [x] Run the paired fixture without video output and collect durable results.
- [x] Analyze completed/failed intervals and output counters; restore and alert.

## Preparation evidence

The generated variant is `graphics-timing-probe-r01-framebuffer-b2026-09-13-18-31-38Z`:
15,552 bytes, SHA256 `e573cddce8d8357431dfd83626d5d16a287bf65c3866ed1664c8e33bd6ac6a85`.
The `framebuffer` variant retains the reviewed r01 application source exactly;
only generated case entries and the build label change. All 61 retained asset
files were read from physical Agon SD and match the original corpus hashes.
Independent framing covers 14,717 commands with no VDU22 mode changes.
The ordinary root startup is preserved; a separate batch owns mode selection,
fixture launch and subsequent SD-service return. Generated binaries/media,
private endpoint scripts and exact deployment evidence live in the ignored
`agents/graphics-timing/framebuffer-pass/` bundle. Historical r01 results and
full corpus remain unchanged. The subsequent outcomes and final completed baseline are recorded below.

Rebuild into a new, ignored output folder after preparing the original r01
corpus with the existing generator:

```sh
.venv/bin/python -B docs/tasks/QUAL-003/timing/scripts/build_framebuffer_variant.py --output agents/graphics-timing/framebuffer-rebuild
```

This builder does not deploy, alter original fixture sources/media, or generate
an emulator profile. It refuses to reuse an existing output fixture directory.

## First rerun outcome and bounded second pass

`GQT002.CSV` records 114 successful intervals, then FR_TIMEOUT (15) at
BSP30_25: four 68x68 hardware sprites, following the omitted BSP30_22–24.
All rows remain repeat0/mainboard/detail0; no P4 case was reached. One probe
mismatch is the existing SHP23 reference disagreement. Both before/after P4
snapshot counts are zero. This is another mainboard stress-fixture failure,
not a P4 performance result or a diagnosed renderer defect.

For the second pass, additionally exclude BSP30_25. It is an independent final
stage, so its removal affects no later bitmap prerequisite; SCROLL resets its
own scene. The remaining 60 cases require 960 intervals. Reuse unchanged,
already-read-back assets and the same diagnostic firmware. Keep the first
partial CSV and source manifest. Use `--omit-large-sprites` with the variant
builder to reproduce this second selection. No rendering implementation change.

Second-pass recovery amendment: use `--continue-batch` as well as
`--omit-large-sprites`. Only the final C return changes to zero so MOS EXEC can
continue to sdserve after a diagnostic failure. The printed outcome, saved
terminal status, callback cleanup and timed code remain unchanged. A zero MOS
exit is explicitly not test acceptance; the strict CSV validator owns that.

During first-pass recovery the keyboard admission epoch advanced around a
supposedly passive mainboard serial open. Treat that access as potentially
resetting, not proven passive. The closed CSV contains a terminal timeout;
service availability is not evidence of a natural batch return. No serial
observer will be used in the second pass. A deliberate Pi reset established
a fresh neutral keyboard admission and ordinary SD startup before restaging.

The Author observed a static green rectangle with a white top stripe during
second-pass execution. This is the retained mainboard final scrolling/clipping
scene, not evidence that the P4 is stalled. Two bounded read-only counter
snapshots showed 386 additional P4 TX replies / 5,232 bytes and zero additional
video snapshots while the mainboard image remained unchanged. These status
reads add small network-observer overhead and are not render timing results.
No browser/video connection or extra drawing was introduced for that check.

## Second rerun outcome and stable baseline selection

The second run records 345 intervals, ending at repeat 1 / mainboard / detail 1,
BSP30_17 (sixteen aligned RGBA2222 hardware sprites), FR_TIMEOUT 15. Its
instrumentation-off mainboard and P4 passes completed. The Author independently
reports scanout errors at stages 16 and 17 (and earlier BSP30/next-scene errors).
A completed callback does not establish clean physical scanout. This observation
also limits interpretation of earlier successfully completed stress stages.

Exclude the entire 25-stage BSP30 population-stress page for the next baseline,
using `--omit-population-page --continue-batch`. The remaining 39 cases require
624 intervals. Preserve all other pages and finite scrolling/clipping cases.
Page-level cleanup keeps dependencies independent. No new firmware or rendering
algorithm is introduced. Retain the 39-case comparison separately from the
61/60-case partial runs and preserve each exact selection. Population stress
and instrumentation interference remain an explicitly open investigation.

## Completed baseline and recovery — 2026-09-13 19:22 UTC

The 39-case run completed all 624 intervals (4 repetitions × 2 destinations ×
39 cases × 2 phases), with eight metrics per interval. The strict existing CSV
validator accepts exact ordering, counts, terminal status and corpus byte counts.
All eight colour-probe differences are the existing SHP23/index1 disagreement:
both destinations return black where the fixture expects white, on every repeat.
There are no new probe differences in this selection. This is a completed
exploratory measurement, not a pass of the omitted population page or a newly
qualified firmware build. Inputs were prepared in a dirty worktree.

The full [comparison](results/framebuffer-first/comparison.md), raw CSV,
analysis, retained corpus and output counters live in
`results/framebuffer-first/`. Selection and exact image/result hashes are in
`selection.json`. The P4 snapshot counter stayed at zero. Sparse HTTP status
observations were retained locally; no browser output or serial-stream capture
ran during timed work. The final CSV was collected from physical SD through
Extender; its SHA256 is
`af876cbffd578434073e7e8ffd33a061763d430d4c4c3ea47d749058525a9693`.

1. Median time inside the P4 primitive scope is lower for the 64-operation
   SCROLL, CLIPROW and COMBINED stages: 2.078/1.951/2.660 ms, versus mainboard
   9.362/6.334/7.102 ms. Their renderer-local elapsed times are respectively
   22.712/50.734/84.950 ms on P4 and 27.964/50.377/84.742 ms on mainboard.
   Faster drawing alone does not deliver proportional whole-stage speedup.
2. Bitmap upload stages expose a separate substantial P4 disadvantage.
   BSP03_01 sends 94,683 bytes, of which 93,788 are asset upload. Median
   elapsed time is 3,165.200 ms on P4 versus 881.983 ms on mainboard, despite
   primitive scope time of 11.518 ms versus 37.607 ms. Raw MOS submission
   ticks rise from 104 to 376; reply ticks remain 2. BSP26_01 similarly sends
   61,406 bytes (60,712 uploaded), with 2,048.142 versus 582.664 ms elapsed
   and 244 versus 68 submission ticks. This locates most of the observed
   difference within submission, potentially including EMOS transport,
   backpressure and concurrent VDP parsing/upload handling. It does not isolate
   one component or prove UART bandwidth alone is responsible.
3. EMPTY still takes about 14–16 ms elapsed. Completion/drain and command
   costs matter, especially for short batches. Do not infer a display refresh
   limit, subtract EMPTY universally, or call these results gameplay FPS.
4. Primitive scopes measure elapsed wall time within their boundaries, not
   exclusive CPU cycles; preemption may be included. Software-sprite scopes
   overlap primitive scopes. Mainboard VGA remains active while P4 output is
   absent, so hardware-sprite scanline work is not an equal-output comparison.
5. The actual pre-test mainboard flash was restored over every affected erase
   sector and independently digest-verified. A deliberate reset re-established
   neutral keyboard admission. Cleanup ran on both display routes; subsequent
   MOS COPY and SD readback confirmed batch return and working SD access.
   Root autoexec is unchanged. P4/EMOS images, game files and wiring are unchanged.
   SD service exited normally to the Legacy CLI. Private detailed restoration
   evidence is in the existing ignored run folders and HARDWARE.local.md.

Revalidate the preserved CSV without hardware:

```sh
.venv/bin/python docs/tasks/QUAL-003/timing/scripts/read_results.py docs/tasks/QUAL-003/timing/results/framebuffer-first/baseline39.csv --corpus docs/tasks/QUAL-003/timing/results/framebuffer-first/baseline39-corpus.json
```

The Author's phone video and five extracted frames remain ignored; findings and
content hash are in [author-video.md](results/framebuffer-first/author-video.md).
No original media has been staged. Population stress, output timing and
Nurples are still unresolved/deferred. Review these results with the Author
before selecting further experiments; no renderer or upstream VDP fixes began.

At 19:24 UTC the host submitted two VDU7 hardware attention cues through the
accepted keyboard path. Admission ended ready, neutral, no held/pending keys;
physical audibility remains for the Author to confirm. Work is paused for review.


## Rendering-only breakdown requested by the Author

[Rendering-only tables](results/framebuffer-first/rendering-only.md) separate
primitive execution and software-sprite redraw scopes from transport/upload
elapsed times. They include side-by-side milliseconds, mainboard-baseline
percentage changes, resident-bitmap amortized costs, and explicit limitations
for hardware sprites and aggregate timing. The Author's immediate assessment
priority is the fidelity and rendering performance of the VDP API port.


## Loading breakdown requested by the Author

[Upload-stage tables](results/framebuffer-first/upload-stages.md) preserve asset
and command byte totals, destination elapsed milliseconds, approximate eZ80
submission milliseconds with raw ticks, percentage changes relative to mainboard
VDP, and completion-reply intervals. They explicitly distinguish these mixed
stage measurements from isolated SD reads, buffer writes and bitmap creation.


The same upload-stage findings now include the Author-requested quick code
audit: the P4 adapter omits stock's bulk UART-read override, while parser delays,
worker priorities, buffering, synchronization and DMA/scanline behavior are
compared explicitly. Bulk-read overhead is a suspect, not a measured root cause.
