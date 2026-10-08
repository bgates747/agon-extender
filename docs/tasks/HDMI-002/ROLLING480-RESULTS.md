# Rolling scanout at both proven HDMI geometries

The wider rolling renderer reaches approximately 60 images/s in the small
sprite fixture, but **fails the longer Nurples workload**. The diagnostic run
stops presenting after 730 frames (about 12 seconds), records a DSI underrun,
and turns blue. The Author independently reports more than ten seconds of
perfect gameplay followed by a blue screen. This is a rejected experimental
candidate, not a working 60-fps upgrade. Restore the exact r06 image; preserving
the existing game path takes precedence over adding widescreen counterparts.

Later offline follow-up reproduces a premature refill-overlap stop and prepares
an unflashed remedy with first-fault diagnostics. See the
[offline review](OFFLINE480-REVIEW.md). It does not change the failed outcomes
below or establish their initiating cause retroactively.

The bounded HDMI02-F experiment extends the existing three-slot scanline path
to 848×480 while retaining 684×384. No 240-line timing or wider redesign belongs
to this experiment. Production remains unchanged.

## Implementation and memory boundary

The P4 retains three internal DMA slots, each large enough for 848×32 RGB888
pixels. Active width, height, row stride and block count follow the joined panel
lifetime: 12 blocks for 684×384, 15 for 848×480. Scene snapshots carry the active
output stride. Sprite snapshots, ownership checks and late-refill containment
remain in place. No timing change or reduction in color precision is involved.

The larger slots cost 47,232 additional internal bytes. Task stacks for native
drawing/output, HDMI mode switching, wired networking and the two HTTP servers
move to PSRAM using the pinned ESP-IDF 5.5.5 capability APIs. Their combined
nominal stack allocation is 49,152 bytes; actual free heap must be measured.
Priorities, affinities and stack sizes are unchanged. Task controls, interrupt
stacks and DMA storage remain internal. These selected workers do not disable
cache for flash/NVS operations; adding such behavior requires another review.
Capability-created tasks use capability-aware deletion, including worker exit.

Only full-width 64-color mode 96 gains direct RGB888 drawing. Modes 97–99 keep
native indexed composition, so approximately 60 Hz DMA does not promise 60 newly
composed images per second at those depths.

## Host checks

1. Sanitized sprite/scene comparisons pass fixed 848, fixed 684, fixed 512 and
   automatic geometries, including 684 strides inside an 848-sized allocation.
2. Native/direct renderer comparisons pass full-width edge drawing, bounded
   partial scrolling and the hardware overlay at the bottom-right corner.
3. Actual HDMI service scheduling checks pass frame/swap ordering, independent
   clock behavior and joined teardown. The maintained host adapter adds the
   standard FreeRTOS task-entry typedef; target stack placement is a hardware
   question, not evidence supplied by that host model.

One new host probe exposed a retained native `VGA64Controller::swapRows` edge
case: scrolling a region that leaves a one-pixel right sidebar reaches the
unaligned helper with `x1 == x2 == 847`. Its leading and trailing loops overlap
and can swap pixels outside that interval. The direct renderer differs there.
The bounded comparison uses a four-pixel sidebar instead and still tests pixel
847 independently. No upstream or local rasterizer fix was made. This is a
host-observed code discrepancy, not a demonstrated physical mainboard failure;
retain it for separate investigation rather than changing stock behavior here.

## Hardware procedure and evidence

Use the unchanged resident render-load-r04 case 54 first. The retained r03
3,600-update hardware Nurples fixture explicitly rejects modes other than 20.
The new r04 companion first reproduces r03 byte for byte, then changes only
the mode admission check to 96, its error text and build identity. Gameplay,
assets, input, pacing and timing instrumentation are unchanged. Its maintained
builder is [wide_hardware_nurples.py](../../../tests/performance/scan/wide_hardware_nurples.py).
Keep r03 for the mode-20 control. Select mode 96 or mode 20 only in startup;
the ordinary game executable selects its own mode and cannot establish mode-96
performance. Compare deterministic state trajectories and PRT work/headroom
against the retained mode-20 baseline. Keep application, composition and DMA
measurements separate. Restore startup and fixture configuration by full
readback. Preserve ordinary game binaries.

Local build, rollback verification, host logs and subsequent bench evidence
are retained in the ignored `agents/hdmi002/rolling480` silo. Exact r06 rollback
artifacts were verified before candidate deployment. Production selection is
unchanged; this is a bounded development experiment.

## Physical findings

Worst outcomes first; failed game rows are not throughput qualifications.
The baseline is the retained r06 native 848×480 compositor. Small-fixture rates
are observations from short, differently sized windows, not a calibrated speed
comparison. Percentage change is `(candidate / baseline - 1) × 100` for P4
image production only; the signal remains approximately 60 Hz throughout.

| Workload | Retained baseline | Rolling candidate | Disposition |
|---|---|---|---|
| Mode 96, hardware Nurples, r08 | No passing r06 mode-96 Nurples measurement | 730 presentations, then underrun and stopped scanout | Fail; blue screen confirmed by Author |
| Mode 96, hardware Nurples, r07 | No passing r06 mode-96 Nurples measurement | 2,536 presentations, then stopped scanout | Fail; approximately 42 seconds of output, no complete rendering window |
| Mode 96 → native mode 97, r07 | Four native mode checks passed separately on r06 | Following test did not open its measurement window; network/input remained alive | Transition failure retained; cold-start mode 97 subsequently passes |
| Mode 97, 16 sprites, cold start | 14.939 images/s | 13.923 images/s; 60.139 scanouts/s | Short check passes; observed image rate 6.80% lower, insufficient to attribute a regression |
| Mode 96, 16 sprites | 14.894 images/s | 59.964 images/s; 59.964 scanouts/s | Small case passes; observed image rate 302.60% higher, not sustained-game qualification |

The diagnostic r08 run reports one underrun and one contained scanout fault,
with zero late-refill and zero over-budget counts. Maximum measured refill is
1,130 µs against the unchanged 1,600 µs guard; sampled internal free memory is
24,363 bytes. This does **not** prove adequate hardware fetch timing: measured
refill duration and the DSI FIFO's ability to obtain data are different things.
The P4 HTTP service remains responsive after image advancement stops. No CPU
panic or reboot is established by this event.

Pinned ESP-IDF's DPI underrun handler explicitly notes that failure to fetch
pixels can turn the display blue. The generic message mentions external-memory
bandwidth, but these rolling output slots are internal SRAM; do not assume its
generic wording identifies our bottleneck. The read-only diagnostic endpoint
does not expose every abort reason, so the initiating cause and ordering of the
underrun versus the contained fault remain unresolved. Do not weaken the guard
or claim a PSRAM, clock or refill-time cause from this evidence alone.

Both failed game invocations leave 3,600-row SD files, **but their abort flags
are set, their final drain time saturates, and one row records a fault**.
Their P4 measurement windows never close. Row count alone therefore cannot
establish success, and their apparently good median game-work percentages must
not be compared as passing results. The recovered r08 file corroborates the
failure independently of the Author's screen observation.

## Retained identities

1. r07: `rgb-001-r07-b2026-10-07-21-08-34Z`, factory SHA256
   `9d3de8e48733f09d340033612a65a69763a9a9b89f44074a8c50940263defe13`.
2. r08: `rgb-001-r08-b2026-10-07-21-36-29Z`, factory SHA256
   `68af7a18cd22d64ab165dcd5805aaba674b0c0f431a198d29407baa756586a38`.
   Adds read-only rolling counters to `/display/status`; same renderer strategy.
3. Wide game companion: `scan-scroll-suite-r04-b2026-10-07-21-36-29Z`,
   binary SHA256 `f64c75be2481a2ca4b8d444e581a85e5e57eb2f5ccaefcf4df9ab65c164f2b23`.
   Its assembler identity, exact r03 reproduction and mode-only source diff are
   retained with the build manifest. The ordinary installed games are untouched.
4. Exact good rollback: `rgb-001-r06-b2026-10-07-20-23-02Z`, factory SHA256
   `596063a384ab191d8c87827e8ee801f11c26e102d5963b79696b48f0f63b0e7f`.

The ignored evidence silo retains `sprites/evidence`, `cold97-*`,
`game96-v2/partial-result.bin`, and `r08-game96-fresh` (serial/status samples,
correlated timing tag, raw failed game record and decoded summary). All deployed
builds passed independent readback of their four flash segments. An initial
mode-20-only fixture rejection and a guarded existing-result rejection were
setup checks, not game or firmware performance results.

## Existing-mode regression control

After recovering from the blue screen, r08 completes the unchanged r03 hardware
Nurples fixture in mode 20 (512×384 inside 684×384). All 3,600 rows are present,
the abort flag is clear, the final completion check succeeds, and no fault or
late rows occur. Every recorded update/state/phase/actor/projectile/map/RNG
value matches the prior accepted 684-path run. This one controlled run shows
no material regression in the established Nurples path; it is not broad
qualification of all modes or interactive input latency.

The game-work baseline is the retained r04 684×384 memory-remedy run, using the
same r03 fixture. These are eZ80 active-work percentages of one 60-Hz frame,
not P4 composition or HDMI rates. One frame budget is 1,200 nominal PRT counts
at 72 kHz (16⅔ ms). PRT/raw-MOS calibration is retained in both files; no new
precision or oscillator calibration is claimed. Differences below are percentage
points of that frame budget; lower active work leaves more pacing headroom.

| Measurement | Prior 684-path baseline | r08 mode-20 control | Difference |
|---|---:|---:|---:|
| Maximum active work / frame budget | 70.17% | 70.08% | −0.08 points |
| 95th-percentile active work / frame budget | 53.33% | 53.25% | −0.08 points |
| Median active work / frame budget | 43.00% | 42.75% | −0.25 points |
| Median unused active-work budget | 57.00% | 57.25% | +0.25 points |
| Application updates/s, nominal MOS clock | 60.00 | 60.00 | 0.00 |

Median work is 0.58% lower relative to baseline, too small to claim a meaningful
optimization from a single run. The P4 window closes after about 60.058 seconds,
with 3,607 presentations/scanouts and no underrun, invalid-block, sequence,
late-refill or contained-fault counts. Maximum refill is 890 µs; minimum reported
ready lead is 1,145 µs; loaded internal free RAM is 24,403 bytes. The returned
Legacy listener is admitted and exits normally. Evidence is retained in
`game20-v2` and `mode20-comparison.json` beside the failed wider runs.

## Metadata correction

The frozen r07/r08 manifests still describe the r06 automatic scanout in their
human-readable `scanout` summary: 12 rolling blocks at 684×384, full-frame848.
That summary is stale. Their hashed source closures, target compile definitions
and physical logs establish the actual experiment: maximum848 allocation with
12 blocks at684×384 or15 at848×480, both rolling. Preserve the frozen manifests
and image identities; do not silently rewrite evidence. The maintained builder
now records both runtime layouts, the maximum244,224-byte SRAM allocation and
the external worker stacks. All12 metadata/build-selection checks pass after
this correction. It does not change either tested binary, and no further image
is built or flashed for this bookkeeping correction.

## Handback

The exact r06 factory image above is restored, with independent verification of
all four flash segments. A fresh Agon reset verifies Extender keyboard admission;
a successful SD metadata request establishes the idle Legacy CLI. Keyboard state
is neutral with no held or pending keys, the foreground listener is offline with
no pending job, and timing windows are closed. No capture, test, reset or input
automation remains active. The current P4 output is native640×480 in848×480.

Original38-byte startup,128-byte fixture configuration, and both ordinary
Nurples executables pass full SHA256 readback. Their identities and the final
status are retained under `final-readback/verified.json` and `final-status.json`
in the local evidence silo; the exact rollback receipt is in the r06 build's
`installed-2026-10-07-22-06-32Z` directory. Experimental fixtures and failed-run
evidence remain separately under `/test/nurples` and `/agents/extender` on the
Agon card. Source work remains uncommitted; production selection is unchanged.
