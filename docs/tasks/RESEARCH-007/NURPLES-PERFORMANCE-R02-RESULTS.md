# Nurples rendering optimization — renewed window results

## Executive summary

The Author renewed eight hours from2026-10-13T00:37:17Z to08:37:17Z under the
existing NP03–NP08 contract. Three fresh RGB888/indexed elementary pairs validate: queued rendering mean
cost falls32–36% for ordinary bitmaps and57% for partial scrolling. Indexed
snapshot/output work increases some completion delays, so this is not yet a
gameplay or full-frame latency win. Software-sprite graduation is underway; no
sprite gain, visual acceptance or production promotion is established. The [first-window partial result](NURPLES-PERFORMANCE-R01-RESULTS.md)
remains unchanged.

## Fresh RGB888 controls

Mode20:512×384×64 single-buffered, centered on the684×384 HDMI carrier. No browser
video subscriber. Rendering includes worker and foreground queued execution,
excluding native-mutex wait and asynchronous hardware overlays. Each measurement
below is a whole-window arithmetic mean per completed fixture update. The table
orders the worst baseline cost first. One60Hz interval is16,667µs.

| Workload | Three control means, µs/update | Median, µs/update | Median60Hz budget |
|---|---:|---:|---:|
|64 ordinary bitmap plots + marker|11431.97 /11449.97 /11439.75|11439.75|68.64%|
|Partial vertical scroll, no sprites|4074.85 /3809.38 /3669.65|3809.38|22.86%|
|16 ordinary bitmap plots + marker|2555.20 /2556.46 /2553.31|2555.20|15.33%|

All raw files, closed/nonoverflowed schema2 windows and exact bitmap-call coverage
validate. Scroll variability remains visible rather than selecting the slowest
control. Per-update PRT latency percentiles include eZ80 submission, UART and
completion replies; they are separate from these P4 rendering means. Repeated-
window percentiles are percentiles of means, not individual-frame rendering tails.

## Comparison identity and operational boundary

1. Same-source pair-r04: clean `a167e43ebe3a8ba2f51e000cf17a43a68443e273`, common
   SDK/compiler/configuration closure at360MHz CPU/200MHz PSRAM/80MHz flash.
   Control `rgb-001-r12-b2026-10-12-15-43-40Z`, application SHA256
   `f93fc0e0be48e0299eb29dbb196edb4afa6b66ce12ec9192abdb49e1ea675ccb`.
2. Candidate selections are default-off indexed whole-frame/SW-visible snapshots
   and direct-BGR hardware overlays. Exact flags and bytes come from frozen build
   manifests and independently verified installation receipts, not fixture labels.
3. EMOS pre-parallel v0.1.24, incoming fsimP2 mainboard VDP and wiring remain
   unchanged. Four P4 flash segments are independently verified with NVS preserved;
   actual CLI/listener/read/EXIT checks follow each installation.
4. Original38-byte keyboard-only startup and original four SCANconfigs were restored
   at the first-window closeout. This window preserves them and stages a verified
   63-byte setup-only startup selecting ExCom/mode20. Tests launch only by explicit
   CLI EXEC, after acknowledged foreground-listener EXIT.
5. Raw evidence, fixture/config/source hashes, manifests and single-session journals
   remain in the ignored local campaign record identified by the bench guide.
   Elementary runs use frozen bench-r05 labels rgb/rgb2/rgb3 and fresh result paths.
6. Current work is experimental. The earlier intermittent HDMI dropout and rejected
   indexed sprite flicker remain open until separately tested. Counter correctness
   cannot establish visible stability, physical monitor FPS or human input latency.

## Elementary indexed comparison

Each variant has three independent windows with identical source/SDK/fixture
contracts. Positive gain is100×(RGB888 − indexed)/RGB888. Ranking is lowest gain
first; all times below exclude native-mutex wait and HDMI preparation.

| Workload | RGB888 median window mean, µs/update | Indexed median window mean, µs/update | Median mean-cost reduction | Repeated-windowp95 reduction | Indexed median60Hz budget |
|---|---:|---:|---:|---:|---:|
|16 ordinary bitmap plots + marker|2555.20|1748.22|31.58%|31.35%|10.49%|
|64 ordinary bitmap plots + marker|11439.75|7273.27|36.42%|36.35%|43.64%|
|Partial vertical scroll, no sprites|3809.38|1637.41|57.02%|58.24%|9.82%|

These percentiles describe three **window means**, not individual-frame renderer
tails. Actual per-update PRT completion remains independently available: it
includes eZ80 submission, UART/query/reply and rendering completion. One60Hz
budget is1200 nominalPRTcounts. Worst repeated per-updatep95 first:

| Workload | RGB888 completionp95 range, PRTcounts | Indexed completionp95 range, PRTcounts | RGB888 / indexed worstp95 budget |
|---|---:|---:|---:|
|64 bitmap plots + marker|1719–1726|1904–1905|143.83% /158.75%|
|Partial scroll|734–747|625–889|62.25% /74.08%|
|16 bitmap plots + marker|462–465|704–704|38.75% /58.67%|

The indexed renderer does less work per pixel, but its output task copies the
whole indexed background under native exclusion and then expands it with PPA.
Rendering's native-wait cost rises:64-plot windows average about5.13–5.20ms/update
versus0.58ms in RGB888. Indexed publications remain59.34–60.04/s across these
windows, and DMA remains59.97–60.33/s; these are submissions/scanout cycles, not
proof of distinct visible images or flicker-free output. Broad output phases
remain separate, potentially overlapping wall scopes.

All18 raw case files validate, with closed/nonoverflowed schema2 windows, zero
primary render-boundary drops, matching finite trajectory and exact bitmap calls.
This establishes an elementary rendering-mean gain and permits the contracted
software-sprite tests. It does not satisfy the full50% sprite/widescreen gate or
individual-frame render-tail requirement. Current candidate application SHA256
`0a339344516f1fe8c4d8d9e05caa49037502900954fe19b7aa06aafb62d769dd`;
its default-off indexed/SW-visible snapshot flags preserve complete-background
ownership while avoiding the prior row-by-row snapshot's30Hz publication result.
