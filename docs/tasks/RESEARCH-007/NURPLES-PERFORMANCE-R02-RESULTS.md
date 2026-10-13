# Nurples rendering optimization — renewed window results

## Executive summary

The Author renewed eight hours from2026-10-13T00:37:17Z to08:37:17Z under the
existing NP03–NP08 contract. Three fresh RGB888 elementary controls validate;
indexed comparison is in progress. No sprite gain, visual acceptance or production
promotion is established. The [first-window partial result](NURPLES-PERFORMANCE-R01-RESULTS.md)
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
