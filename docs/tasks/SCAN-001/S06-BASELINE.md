# SCAN01-S06 — First short hardware baseline

**S06 remains open.** The Author returned the card to Agon and authorized the
next bench step. These are the five agreed short cases on the currently installed
ordinary P4 and mainboard, before diagnostic/direct firmware swaps. No firmware
was flashed and no renderer was changed. The one-subtask gate still applies.

## Comparable results

One run per endpoint, each120 measured updates after60 synthetic/120 game warm-up
updates. Mode20 is selected only by startup. Same executables/assets/configuration
semantics on both routes; only route and unique output filenames differ. Each
case has120 saved rows, no abort, saturation, fence timeout or game fault.
The two Nurples runs have identical update-indexed simulation checkpoints,
input phases, actor/projectile counts, map progression and RNG.

Rows put the only observed pacing failure first, then the primary game target;
remaining controls follow. Rate change=(P4/mainboard−1)×100%. Work is eZ80 active
submission time, **including transport blocking**, as a percentage of a nominal
16.667ms budget. It is not pure CPU work or renderer completion. Units and all
phase statistics are retained in the [machine-readable results](S06-BASELINE.json).

| Case | Mainboard updates/s | Ordinary P4 updates/s | Rate change | Mainboard work median / p95 budget | P4 work median / p95 budget |
|---|---:|---:|---:|---:|---:|
| T07 | 40.22 | 58.06 | +44.4% | 65.0% / 103.0% | 33.0% / 34.9% |
| T09 | 60.00 | 60.00 | +0.0% | 21.2% / 42.6% | 33.5% / 35.2% |
| T03 | 60.00 | 60.00 | +0.0% | 13.1% / 13.3% | 13.8% / 14.0% |
| T08 | 60.00 | 60.00 | +0.0% | 19.2% / 19.2% | 19.3% / 19.7% |
| T01 | 60.00 | 60.00 | +0.0% | 0.0% / 0.0% | 0.0% / 0.0% |

T01 is static/polling; T03 is partial scrolling with incoming tiles; T07 adds32
software sprites; T08 keeps32 software sprites without scrolling; T09 is the
repaired deterministic Nurples smoke. T01/T03/T07/T08 include a pixel-query
completion fence every update; T09 retains ordinary unfenced game pacing.
Do not compare their completion scopes as though all were natural gameplay.

## Findings and limits

F01 — Combining scrolling and32 software sprites exceeds the paced budget on
both endpoints. T07's p95 whole-update completion (including query/reply) uses
178.1% of the budget on mainboard and111.8% on ordinary P4. All120 T07 rows on
each endpoint mark a late deadline. Ordinary P4 sustains58.06updates/s in this
short window versus40.22 on mainboard. Neither meets a perfect60 here.

F02 — Scrolling/tiles alone and32 sprites alone sustain60 on both endpoints.
This supports investigating the combined redraw cost. It does not identify the
specific primitive, queue or scanout ownership stall responsible. No renderer
phase counters were enabled, and no visual flicker acceptance was collected.

F03 — The short Nurples smoke sustains60 on both. Median eZ80 active headroom
is78.8% on mainboard and66.5% on P4; p95 active work uses42.6% versus35.2%.
This mixed distribution is not evidence of a universal speedup or slowdown.
The120-update sample cannot establish longer, busier game performance, fresh
presentation rate, sprite fidelity or responsiveness to live input.

F04 — PRT uses nominal72kHz; rate uses raw MOS clock at nominal120units/s.
Calibration intervals report34839–35677PRT counts over60 raw MOS units; the
initial clock phase and timer/read overhead are not removed. Percentages are
nominal budget estimates, not externally calibrated clock measurements.
Whole-window MOS time includes checkpoint/record overhead excluded from active
PRT work. There are no repeated hardware runs yet, so no repeatability claim.

F05 — The ordinary HDMI build excludes the browser-video WebSocket route.
The host sent no requests or keys during the bounded run wait. Result reads
occurred only after the final foreground listener was online. No screen capture
was used during measurement. These checks do not qualify browser streaming.

## Provenance and continuation

The selected fixture remains the exact [S05 build](S05-FIXTURES.json).
P4 identity follows the retained, verified Author rollback receipt for
`hdmi-001-r03-b2026-10-05-01-47-13Z`, corroborated by HDMI status and the absent
benchmark endpoint. Mainboard stock2.16.0 and EMOS0.1.23 follow retained installed
records; no fresh ROM readback was performed. Do not present these as newly
attested flash hashes. Host runner, exact startup/configurations, readbacks,
request ledger and raw records are retained under `agents/scan001/s06/`.
Card results and startup/configuration backups are under
`/agents/extender/results/scan-r01/s06a`.

The next instrumented native image is
`bench-009-r01-b2026-10-05-23-46-18Z`: all19 manifest artifacts and silicon1.3
image-header compatibility reverified, not flashed. Before interpreting its
phase counters, scope the observation window to the finite measured workload;
existing S05 binaries do not emit the diagnostic window markers. Then compare
the matched direct image and bounded controls. No broad campaign or OFF-output
experiment is authorized by these baseline results.

The retained contract makes firmware flashing Author-controlled. Supply the
verified Pi command at that boundary; do not silently replace that arrangement
with unattended flashing. S06 is incomplete until its remaining mechanism,
direct-path and observer-control evidence is reviewed. S07 has not begun.
