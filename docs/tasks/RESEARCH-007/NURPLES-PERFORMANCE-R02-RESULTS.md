# Nurples rendering optimization — renewed window results

## Executive summary

The Author renewed eight hours from2026-10-13T00:37:17Z to08:37:17Z under the
existing NP03–NP08 contract. Three fresh RGB888/indexed elementary pairs validate: queued rendering mean
cost falls32–36% for ordinary bitmaps and57% for partial scrolling. Indexed
snapshot/output work increases some completion delays, so this is not yet a
gameplay or full-frame latency win. Three repeated software-sprite pairs now show
52.52% less queued rendering work in deterministic repaired Nurples and52.74%
less with32 sprites over the scrolling background. Three hardware-sprite pairs
show41.58% less queued drawing in repaired Nurples, but greater snapshot/native
waiting and rolling-copy cost. Visual acceptance and production promotion remain
unestablished. The [first-window partial result](NURPLES-PERFORMANCE-R01-RESULTS.md)
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

## Software sprites and repaired Nurples

Three windows per variant use the same source, SDK, mode, binaries, assets,
command stream and deterministic state trajectory as the elementary comparison.
Positive reduction means100×(current RGB888 − indexed)/current RGB888. Ranking
is lowest rendering reduction first. Each cost is a whole-window arithmetic
mean per completed application update; the median/p95 columns compare the three
window means rather than individual-frame tails.

| Workload | RGB888 median, µs/update | Indexed median, µs/update | Median reduction | Repeated-windowp95 reduction | RGB888 / indexed rendering share of60Hz budget |
|---|---:|---:|---:|---:|---:|
|32 moving software sprites; static background|1940.91|1235.51|36.34%|37.07%|11.65% /7.41%|
|Repaired Nurples;3600 measured updates|4121.34|1956.66|52.52%|52.32%|24.73% /11.74%|
|32 software sprites + partial scroll +17 bitmaps|6444.03|3045.44|52.74%|51.73%|38.66% /18.27%|

These are rendering-work savings, not an assertion of that much spare CPU or
faster displayed frames. The P4 output task has additional work:

| Nurples scope | RGB888 | Indexed | Meaning |
|---|---:|---:|---|
|Queued rendering, median µs/application update|4121.34|1956.66|Worker + foreground execution; excludes native wait and rolling overlays|
|Drawing's native-mutex wait, median µs/update|345.51|683.66|Separate drawing delay; rises despite less execution work|
|Output snapshot, median µs/update|Different row/scanout path|4292.79|Indexed full-frame snapshot preparation under native exclusion|
|Blocking expansion, median µs/update|No indexed expansion|4061.06|Helper/driver cache work, PPA wait and post-invalidation; overlapping output scope|
|Background publications/s, median|60.06|58.77|Panel submissions; neither distinct visible FPS nor a flicker test|
|Application updates/s|60|60|Both retain the fixture's pacing; matching state trajectory|

All18 software run records validate. The finite fixtures retain120 measured
updates each: both sprite cases execute exactly120 refreshes; the scrolling case
adds120 scrolls and2040 bitmap plots. Each Nurples run retains3600 measured plus
120 warm-up updates,3600 scrolls and69172 bitmap plots, with the same actor,
projectile, map and RNG trajectory hash. Windows match both case ID and unique
tag, with zero primary rendering-boundary drops. All36 elementary/software
records remain separate and complete; no rerun overwrites prior results.

Completion latency is not uniformly better. Pooled finite-fixture PRTp95 rises
from539 to621counts with sprites alone, and1360 to1605counts with scrolling and
sprites. At nominal72000counts/s, one60Hz interval is1200counts. Nurples's active
PRTp95 is636 versus637counts, but its controls5 configuration is **unfenced**:
this measures application work/submission before pacing, not finished rendering.
No individual-update render-onlyp95 or maximum is available from schema2.

This completes the measurement portion of software graduation with an explicit
Nurples rendering-mean gain. NP03/NP04 acceptance checkboxes remain open for
strict render-tail and visual validation; the whole50% sprite/full-width gate is
not satisfied. Hardware overlays, full-width logical widescreen, visible flicker
and human input response remain separate gates. No other mode or production
promotion follows from these data.

## Hardware sprites and repaired hardware Nurples

Three RGB888/direct-BGR indexed pairs retain the same source/SDK and fixture
identities as the preceding cohorts. The candidate application SHA256 is
`a2f0967c999d8ebd449e86fe5c80a5adcbfd90f2785c02b204611d63477754f1`.
Case54 refreshes16 hardware sprites over a static background and performs one
marker bitmap per update; its queued cost therefore excludes the actual sprite
overlay. Hardware Nurples retains3600 measured updates,3600 scrolls,69172 bitmap
plots and the same deterministic trajectory as software Nurples.

| Workload | RGB888 median window mean, µs/update | Indexed median window mean, µs/update | Median reduction | Repeated-windowp95 reduction | RGB888 / indexed rendering share of60Hz budget |
|---|---:|---:|---:|---:|---:|
|Static16 hardware sprites; marker and refresh only|43.29|79.03|−82.56%|−80.24%|0.26% /0.47%|
|Repaired hardware Nurples;3600 updates|3822.55|2233.31|41.58%|41.53%|22.94% /13.40%|

The tiny static queued cost worsens in absolute terms by36µs/update. Asynchronous
sprite composition is measured separately using two matching active display
samples five seconds apart. The Nurples bracket covers an early five-second
slice, not all later busy scenes. Ranking below puts the worse whole-refill
regression first; positive reduction means lower cost.

| Active rolling scope | RGB888 median, µs | Indexed median, µs | Reduction |
|---|---:|---:|---:|
|Nurples whole refill, per32-line strip|293.93|408.46|−38.97%|
|Static16 whole refill, per32-line strip|387.99|410.68|−5.85%|
|Nurples overlay composition, per384-line frame equivalent|310.14|185.78|40.10%|
|Static16 overlay composition, per384-line frame equivalent|1628.63|700.66|56.98%|

The combined indexed/snapshot/direct-BGR candidate reduces measured composition,
but this comparison does not isolate the painter's contribution. Rolling copy becomes more
expensive: Nurples252.16→368.64µs/strip, static238.88→336.54µs/strip. Whole-refill,
copy and composition are overlapping wall scopes and must not be summed. All
twelve active brackets (six per workload) retain approximately60 carrier frames/s and zero rolling
fault/late/underrun/cache/overlap/sequence counters. Those counters do not prove
physical flicker-free output or distinct visible frames.

Hardware Nurples native-mutex wait rises346.71→4476.56µs/update. Its indexed
snapshot averages3918.24µs/update; blocking expansion is about4226.57µs/update.
Broad conversion has one boundary drop per candidate, and expansion has one in
two of the three candidates, so those broad scopes remain descriptive and do
not qualify a complete output-cost comparison. Primary queued-render windows
are closed, nonoverflowed and have zero boundary drops. Median background
publication rates are60.07/s RGB888 and59.89/s indexed.

These data meet25% for hardware Nurples's repeated rendering means, not50%,
and do not satisfy individual-frame tails, visual/input or full-width gates.
The Author's earlier “looks very good” observation described the RGB888 control;
it is not acceptance of this indexed candidate. The next bounded pilots isolate
cache-once and the existing inline bitmap painter before a larger cohort.

The RGB888 reference in this report is the original all-experimental-flags-off
renderer explicitly selected by the renewal contract. A previous RGB fast
candidate has separate elementary evidence and remained installed at first-window
closeout. None of the gains above proves a win against that prior optimization;
the final fresh cohort should include it as a separate same-source comparator.

## Narrow cache-once pilot — not selected

One fresh window per variant/workload uses identical clean source
`e00f556903759ce89c1c44901d75c1c15b210d8d`, SDK and frozen workloads. Only the
guarded output helper cache-once selection changes. All six records validate;
no repeated-window or individual-frame threshold claim follows from this pilot.
Worst observed rendering change first; positive reduction means lower cost.

| Workload | Cache-off queued rendering, µs/update | Cache-once queued rendering, µs/update | Observed reduction | Helper pre-C2M off / once, µs/update |
|---|---:|---:|---:|---:|
|Partial scroll|1614.08|1735.89|−7.55%|17.38 /0.00|
|64 bitmap plots + marker|7124.29|7278.26|−2.16%|30.63 /0.00|
|Repaired software Nurples|1935.18|1959.74|−1.27%|36.31 /19.33|

The actual helper clean is tens of microseconds, not the roughly4ms broad
blocking expansion. Nurples still performs required helper cleans after target
eligibility is revoked, so cache-once does not imply zero calls there. Required
PPA-driver/input/post-DMA/panel/rolling cache maintenance remains unchanged.
The pilot supplies no useful rendering gain and does not justify further repeats
or enabling this flag in the final candidate. Small differences are observations,
not proof of a statistically reliable regression. The separate bitmap-fast
pilot uses cache-once on both prebuilt members only to isolate its bitmap flag;
that does not select cache-once for the final matched cohort.


## Narrow indexed bitmap pilot — retained for final comparison

One fresh control/candidate window per workload uses identical clean source
`5444b8f345fc79439a382411c780dda7bd427397`, SDK and frozen fixtures. Both images
select indexed whole-frame/SW-visible snapshots and cache-once; the existing
inline bitmap SET painter is their sole option difference. Cache-once remains
unselected for the final cohort. All six records, exact bitmap call coverage,
installed manifests and repaired Nurples trajectory validate. Lowest observed
gain first; positive reduction means less queued drawing wall time.

| Workload | Inline painter off, µs/update | Inline painter on, µs/update | Observed reduction |
|---|---:|---:|---:|
|Repaired software Nurples|1937.03|1805.68|6.78%|
|Partial vertical scroll with bitmap row|1731.20|1596.88|7.76%|
|64 bitmap plots + marker|7280.97|3253.15|55.32%|

Nurples's bitmap component falls310.34→239.38µs/update; its final software-sprite
component falls120.48→87.60µs/update. Scrolling remains the largest component at
1196.05µs/update. Its background publication stays58.88→58.90/s and application
pacing stays60updates/s. The finite64-plot PRT completionp95 improves1906→1576
counts, still including submission, UART/query/reply and native/output waiting.
One60Hz budget is1200 nominalPRTcounts.

These single-window observations justify retaining the inline painter for the
final repeated matched-source comparison. They do not qualify a repeatedp95,
individual-render tail, visual/input pass or overall50% Nurples improvement.
The next combined builds include bounded exact samples at existing completion
queries and a separately selected proven-PIE indexed snapshot row copy. Compare
that copy with and without its selector before choosing it. Preserve original
RGB888 and previous RGB fast as separate same-source references. Unrelated
output-phase drops remain visible without invalidating otherwise exact queued
render samples; output and drawing still require separate conclusions.


## Narrow snapshot PIE pilot — not selected

One pair on clean matched source
`832fb5bce0e7c2375aab80cddde5adc7891fee56` changes only indexed snapshot PIE;
inline bitmaps/direct-BGR/SW-visible snapshots are selected and cache-once is off
in both. All six records validate. The candidate boot retains the actual P4
1,280-case alignment/byte/canary PASS. The new finite render samples have exact
expected counts, zero errors and closed/quiescent ownership. Unfenced Nurples
remains aggregate-only. Worst observed mean change first; positive means less time.

| Workload | Scalar / PIE queued mean, µs/update | Observed mean reduction | Scalar / PIE exact renderp95, µs/update | Scalar / PIE snapshot, µs/update |
|---|---:|---:|---:|---:|
|Partial scroll|1582.51 /1693.64|−7.02%|1669 /2528|3873.30 /3794.65|
|64 bitmap plots + marker|3248.07 /3259.71|−0.36%|3595 /3582|4057.91 /4071.77|
|Repaired software Nurples|1804.42 /1782.61|1.21%|unavailable /unavailable|4310.65 /4292.64|

Static snapshot cost per attempt is3503.41→3491.89µs, effectively unchanged;
Nurples publications stay58.87→58.86/s. Removing the large ordinary helper stack
frame and using the proven vector kernel did not supply a useful snapshot gain.
This single pair does not prove a repeatable regression or a memory-bandwidth
root cause. Leave snapshot PIE off in the next candidate. Keep the default-off
prototype and evidence rather than change ownership or cache policy speculatively.

The next bounded matched-source pilot uses the same existing kernel explicitly
for256-byte indexed partial-scroll spans. Host/controller/sprite/bounds tests,
twelve P4 object checks and independent review pass on sourcee26c24f7; complete
builds and actual target execution remain pending. It preserves stock scroll
traversal, filling, sprite erasure, row descriptors and horizontal scrolling.
No new task, video mode, transport or upstream correction is introduced.
