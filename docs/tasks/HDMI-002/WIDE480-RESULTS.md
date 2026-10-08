# Full-width 848×480 logical modes — 2026-10-07

## Result and scope

The experimental automatic-HDMI build exposes the entire proven 848×480 carrier
for drawing. Stock mode IDs and the centered 384-line Nurples path are unchanged.
Modes 96–99 are provisional Extender-only, single-buffer IDs for 64, 16, 4 and
2 colors. Their native compositor remains distinct from the faster direct
RGB888/rolling path used by Nurples. This is a geometry/API extension, not a
60-rendered-fps performance claim. The Author confirms the pattern looks good.

## Identity and implementation

P4 build **rgb-001-r06-b2026-10-07-20-23-02Z**, factory SHA256
`596063a384ab191d8c87827e8ee801f11c26e102d5963b79696b48f0f63b0e7f`.
Compilation and native build validation pass; flash readback independently
verified all four segments. The exact prior r05 rollback artifacts were also
hash-verified before deployment. Neither EMOS nor the game binaries changed.

The mode dispatch adds four entries only when `AGON_EXTENDER_HDMI_AUTO` is
selected. EMOS routes ordinary VDU22 to P4; existing controller initialization,
mode metadata, palette and sprite routines handle the new geometry. No upstream
reference checkout changes, new DB aliases, clock changes, scaling or direct
RGB888 geometry expansion. The physical signal remains 34.285714 MHz,
1104×517 totals, approximately 60.069438 Hz. The 848×480 aspect is 0.625% narrower
than exact 16:9; it is the already accepted practical widescreen carrier.

## Bounded checks

The existing host HDMI geometry/buffer-ownership test passes in AUTO selection.
The unchanged **render-load-r04-b2026-10-05-05-58-59Z** executable, SHA256
`55f4bb13eb561ac1f3fda98c6ed8b18d479ec0f34d3ddc601b9784935c0b571d`, runs
case54 (sixteen paced hardware sprites) with four new parameter files. Each
mode is selected in temporary `/autoexec.txt`, never by the fixture. Host evidence
requires matching mode/color/output geometry, complete fixture records, valid
markers and a closed correlated P4 timing window. These checks establish
execution, not pixel-perfect monitor output or broad gameplay performance.

All four checks pass: no bad/truncated fixture records, no invalid image
markers, matching 848×480 output and logical geometry, and closed windows.
Ranked by slowest P4 image production; these are brief same-fixture observations,
not a newly calibrated comparative benchmark. The five-second host hold starts
after observing the open window; setup/observation/input latency extends the
actual measured window below.

| Mode/colors | Application updates | P4 images/s | DMA scanouts/s | Window |
|---|---:|---:|---:|---:|
| 96 / 64 | 580 | 14.894 | 60.094 | 9.668 s |
| 97 / 16 | 470 | 14.939 | 60.139 | 7.832 s |
| 98 / 4 | 448 | 15.411 | 60.035 | 7.462 s |
| 99 / 2 | 488 | 15.735 | 60.113 | 8.135 s |

The approximately 60 Hz physical cadence is independent of the approximately
15 images/s native full-frame compositor. This tranche does not optimize the
480-line renderer or qualify gameplay/input latency. Run identities:

- Mode 96: `BENCH-009-2026-10-07-20-37-27Z`.
- Mode 97: `BENCH-009-2026-10-07-20-39-03Z`.
- Mode 98: `BENCH-009-2026-10-07-20-40-36Z`.
- Mode 99: `BENCH-009-2026-10-07-20-42-01Z`.


## Visual article and handback

**hdmi-wide-mode-r01-b2026-10-07-20-27-23Z**, binary SHA256
`e70d686807c9ec2e79a1df384a5fe1055b7175b847de3a1cbfff03f35cc493a0`, reuses
the ordinary LCD color-bar MOS wrapper and stock VDU drawing operations.
Its maintained source is [the full-width fixture](../../../tests/fixtures/hdmi-wide-mode/README.md).
It draws an outer white border, eight labeled color bars, a circle and square,
and dashed guides marking the former centered 640-pixel viewport. The side
areas are drawable; there are no reserved pillarboxes in mode96.

Local build/flash/fixture/run evidence is retained under the ignored
`agents/hdmi002/wide480` silo. Maintained support files go under
`/extender/hdmi-wide-mode-r01`; parameter files, results and startup backups go
under `/agents/extender/results/hdmi02-wide480`. Original 38-byte startup was restored and fully read back before handback
(SHA256 `7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`).
The documented `EMOS EXCOM --keep-display` then retained mode96; reloading and
running the pattern required no extra mode command. The program waits for
Escape; keyboard input is admitted/neutral, the SD listener is offline, timing
windows are closed and passive USB capture has stopped. No host automation
remains. The Author accepts the visible geometry. Canonical qualification and an agreed
production version remain separate promotion dependencies. Production selection remains unchanged: this
bounded experiment does not complete canonical qualification or choose a release
version. The 240-line carrier and wider rolling renderer remain outside scope.
