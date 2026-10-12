# Transient HDMI display loss — RGB888 control

## Executive summary

The Author observes brief HDMI picture loss and recovery on both the newer
RGB888 r12 control and the exact retained older r11 image. R12 failed during
the mode20 static chart and deterministic Nurples; r11 failed while holding the
same static chart. This fault therefore exists without the indexed/PPA candidate,
which was never installed in this comparison. No root cause or correction is
established. Internal60Hz output counters do not establish monitor image lock.

## Retained identities and observations

| Component or measurement | Recorded identity/result |
|---|---|
| P4 control | rgb-001-r12-b2026-10-12-10-15-57Z |
| P4 app SHA256 | abf8bb9b013b9a2f65e6790230e9a4ff5b6f48936fda000ad192a1ddcd35a284 |
| P4 source |26660db54ca0ff0621cc7822b985092933a636e5 |
| Exact older P4 control |rgb-001-r11-b2026-10-08-01-22-20Z |
| Older P4 app SHA256 |5f1b42a161ec9df13701db3038e06019a27b2880cf608cdcf8eea109670ca13a |
| Older P4 source |8800ca84577410d5b4a9d70fbd830c10624fc326 plus retained dirty-source snapshot; source.tar.gz/source-inputs.json are authoritative |
| EMOS retained throughout |agon-emos-v0.1.24-b2026-10-07-23-11-33Z |
| Mainboard VDP retained throughout |fsim P2 ordinary timing; app SHA25606dcfc3e0d7ddb8bc54eedf45a941330876ac07a74141e105c3dfeba6ba94a18 |
| HDMI carrier |684×384;512×384 logical mode20 centered; nominal60Hz |
| Frozen fixture suite |scan-scroll-suite-r02-b2026-10-06-23-03-19Z |
| Static chart |Three closed windows;1804 DMA completions/30.029358s≈60.07Hz |
| r12 passive observation |50seconds with continuous uptime, no captured panic/reinit, recorded rolling faults/underruns/invalid blocks/sequence errors all zero |
| Author gameplay observation |Nurples looks good while moving; repeated transient off/on, not visual acceptance |

The passive capture is later than the reported dropouts and has no synchronized
human event marker. It does not prove that a visible dropout occurred inside
that50-second window. Zero recorded faults narrow neither a transient outside
the capture nor faults beyond the P4 counters' scope.

## Completed r12 finite records

The foreground listener returned, supplying positive completion evidence before
retrieval. All four saved files pass fixture identity, case/tag, exact expected
record count, warm-up, abort/fault and matching closed P4-window checks. No reset
or application replay was used to obtain them. Nurples contains3,600 measured
updates; each isolated case contains120.

Ranked by95th-percentile measured active eZ80 work, worst first. Frame budget is
16.667ms=1,200 nominal PRT counts; PRT calibration uses18.432MHz/256=72,000
counts/s. Application rate uses nominal120 raw MOS units/s. Neither is a
photometric measurement of visible frames.

| Workload | Active work median (% of60Hz budget) | Active work p95 (%) | Application updates/s | P4 publications/s | P4 DMA completions/s |
|---|---:|---:|---:|---:|---:|
| T09 deterministic repaired Nurples |42.83|53.00|60.00|60.073|60.073|
| T07 partial vertical scroll,32 software sprites |33.75|33.92|60.00|59.692|60.190|
| T08 static background,32 software sprites |19.33|19.33|60.00|59.943|59.943|
| T03 partial vertical scroll, no sprites |13.92|14.00|60.00|59.940|59.940|

The Nurples record is unfenced game submission/pacing: active work includes
ordinary submission/backpressure, but does not establish completed rendering or
sprite visibility. Isolated cases include their recorded completion fence.
These are one-variant results; no indexed speedup, full CPU load, visual pass or
human input-latency claim follows.

## Code comparison and next discrimination

The exact source-input manifests show byte-identical HDMI timing definitions,
vendored LT8912B driver, rolling DPI patch and strip runtime between r11 and r12.
The complete effective SDK configuration, dependency lock and PPA320 scaler
implementation are also byte-identical. R11 already included the PPA320 client
lifecycle in its dirty-source archive; comparing Git commits alone incorrectly
makes that look new in r12. R12 adds the indexed build selection (unselected in
this control) and a DW-GDMA teardown fix, among other non-HDMI changes. A difference
in source is a suspect only if exercised; no change has yet been causally linked
to the observed off/on event. Dynamic CPU power management is disabled in r12.

The pinned Olimex LT8912B driver reads main-bank0xc1 bit7 for hot-plug detection
and0x9c–0x9f for MIPI input checks. Its disabled DDS diagnostic reads the other
bank's0x0c–0x0f. The [Linux LT8912B driver](https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/bridge/lontium-lt8912b.c)
also uses0xc1 bit7 for cable connection. Hot-plug is not monitor image lock.
Its different receiver-settle/DDS settings are not a proven fix for this board.
No bridge register changes have been made.

The exact-r11 static-chart control is complete: after an initial interval with
no observed dropout, the Author reported one brief off/on event. This supersedes
the provisional absence observation; neither control passes visual stability.
Preserve EMOS, mainboard VDP, fixture, startup and monitor. Further isolation
should distinguish a common P4 scanout fault from bridge/link/monitor loss; no
blind timing or bridge-register changes are justified by this comparison.

## Evidence

Local raw evidence is retained under the ignored task workspace:
`agents/research007/resume-r01/dropout-r01` and `bench-r02/baseline`.
The governing bounded steps remain in [the resumption contract](RESUME-R01.md).
The initial wrong-mode chart was a separate corrected host setup mistake; do
not conflate its MOS error text with the later recurring HDMI dropout.


## Older control installed and left for review

The Pi independently verified all four retained r11 segments, preserved NVS,
and released the held Agon reset after P4 initialization. Fresh actual CLI,
listener, startup readback and acknowledged EXIT passed. EMOS and fsim's
mainboard VDP were unchanged; setup-only startup/configs were unchanged.

Explicit CLI EXEC launched the identical mode20 chart. Its three closed windows
contain1,804 DMA completions over30.029439seconds=60.074382Hz. The accompanying
passive P4 capture shows continuous uptime and zero recorded rolling faults,
underruns, invalid blocks or sequence errors. The collector is closed and the
chart remains on screen. The Author first reported no observed blink, then
reported one brief off/on event. No visual pass, root cause or fix is claimed.

The r12 comparison data remain valid as recorded timings but fail the visual
stability gate. Candidate indexed/PPA firmware remains uninstalled. Return to
that experiment only after the control's disposition; do not silently use r11
as the same-source r12 performance baseline.

## R11 dropout reported — follow-up evidence

The held chart sends no drawing commands, swaps, queries or SD operations after
its three measurement windows; its idle loop only waits for Escape. The blank
interval is not an intentional phase of this fixture. After the Author reported
the dropout, the Pi saved a fresh read-only snapshot:46,584 scanouts since mode
initialization and zero rolling faults, underruns, cache/sequence/overlap errors,
with unchanged maximum refill797us. A subsequent bounded passive P4 capture
retains60.069Hz output and zero recorded errors. This is follow-up evidence, not
an exactly synchronized capture of the human-observed event. No reset, input,
firmware edit or startup change occurred during this observation.

[Olimex issue1](https://github.com/OLIMEX/ESP32-P4-PC/issues/1) references
[Espressif commit9d35ba9](https://github.com/espressif/esp-bsp/commit/9d35ba9).
Inspection shows its LT8912B timing change concerns the supplied1280×720 preset
and lane-rate macro, not this project's custom684/848 timings or the driver's
DDS register sequence. It is not a demonstrated correction for this dropout.

Local evidence: `agents/research007/resume-r01/dropout-r01/r11-dropout-observed`.

## Physical display connection confirmed

The Author confirms that the external MIPI LCD ribbon is removed. HDMI is the
only attached display path, so loading from an attached second DSI receiver is
excluded. The Author also reports no further blink since the previous message;
the single earlier r11 event remains a failure observation. The observation
interval has no measured start/end and is not a formal dropout-rate comparison
against r12. No firmware, reset, startup, mode or wiring change follows from
this report.

Further investigation needs evidence that distinguishes uninterrupted P4 DMA
from bridge/link/monitor loss. The existing logs do not contain bridge-state
history, short frame-gap maxima or a synchronized human event marker.

## Read-only observer preparation

The explicitly selected `--hdmi-link-watch` build adds DMA callback gap history
and samples the pinned driver's existing HPD, MIPI-input and DDS registers at
most10Hz in the joined output task. All values are raw; HPD indicates connection,
and no available register has been established as monitor image lock. The nine
byte reads are sequential, not an atomic bridge snapshot. No timing, bridge
register programming, renderer, transport or other component changes are made.

The observer alone uses a20ms I2C transaction timeout; zero in the pinned SDK
means unbounded waiting. This also bounds that diagnostic build's ordinary
bridge initialization transactions. The first failed read stops observation
without a reset or retry. The recorded read duration and USB log overhead are
instrumentation costs, so the image is unsuitable as a performance comparator.
The observer is default-off, mutually excluded from indexed/parallel variants,
and checked against actual compile commands by the native validator. Exact
uninstrumented r11/r12 artifacts remain intact.

## Observer installed — physical result awaiting Author

`rgb-001-r12-b2026-10-12-12-00-47Z` is the installed, explicitly instrumented
RGB888 build; app SHA256
`0452b9680090f6cba60f1a03fc431b983109bca25c1197aaf19d71ce6e2f2396`.
Compile/link/native validation and frozen-source checks pass, as do15 HDMI
selection tests. All indexed/parallel selections are false. Four flash segments
independently verify with NVS retained. Actual CLI/listener/read/EXIT passes.
EMOS, mainboard VDP, startup, fixture and physical connections are unchanged.

Explicit CLI EXEC launches the same mode20 chart, whose three measurement
windows complete. Passive capture runs from12:09:32 to12:11:32UTC and closes
normally. The chart remains active. Measurements below describe instrumented
P4 progress; the Author's visual result remains outstanding.

| Observer measurement | Result |
|---|---:|
| Raw bridge samples |1,031 over119.945s between first/last sample |
| DMA callbacks |7,205;60.069Hz |
| Maximum DMA callback gap since mode initialization |16,781us |
| DMA gaps over25ms |0 |
| HPD changes |0; raw0xfc throughout |
| Bridge-read median / p95 / maximum |1,379 /1,389 /2,216us |
| Captured read failure, panic or error-level output |None |

MIPI raw samples were `a1640502`1,021times, `a1640602`7times and `a1640402`
3times. The final two diagnostic bytes decode as517,518 and516 respectively;
the programmed vertical total is517. The cause/meaning of that variation has
not been established, and these sequential samples are not receiver-lock
evidence. DDS values also vary and remain raw; the vendor's example threshold
is deliberately not applied. Zero counted errors cannot overrule a visual
dropout or establish that this instrumentation fixes anything.

Local installation receipt, raw log, status, windows and trace summary:
`agents/research007/resume-r01/dropout-r01/link-watch-evidence`.

The Author subsequently reports no observed blink on the observer and
authorizes the four-workload uninstrumented RGB888/indexed comparison despite
the unresolved fault. This is permission to collect performance evidence,
not visual acceptance or proof that the observer corrects the dropout.
