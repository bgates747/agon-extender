# First paired hardware UART timing baseline

Collected 2026-09-10 for [AUDIT-005](../AUDIT-005.md). The Author reports both displays completed 48/48. The saved CSV independently validates all 48 rows, expected black/white pixels, mode information, successful final query statuses and Legacy return.

## Evidence and scope

Fixture: `uart-path-benchmark-r03-b2026-09-10-18-21-38Z`. The returned SD executable hash matches the reviewed build. The selected firmware pair remains EMOS `agon-emos-v0.1.12-b2026-09-10-03-50-35Z` and P4 `uart-excom-console-r07-b2026-09-10-06-31-58Z`; no new firmware identity query, flash or reset was performed during collection.

[Original CSV](evidence/paired-hardware-baseline/00000003.CSV), [hashes and numeric summary](evidence/paired-hardware-baseline/collection-and-summary.json), and [validator output](evidence/paired-hardware-baseline/analysis.txt). Collection time is recorded; the unknown hardware run-start time is not invented.

These are three repetitions per case from one exploratory hardware session, not firmware qualification or a statistical population estimate. Every row declares 32,768 output bytes. The fixture checks returned API status and a final pixel, but no analyzer capture yet proves every physical byte or quantifies CTS. The retained delimiter/CLI status limitations still apply. One visible browser client was required by the procedure; continuous client count/visibility was not independently instrumented.

## Measured comparison

Nominal clock conversion is 120 units/s, with two-unit (16.67 ms) resolution. Times below are medians of three repetitions; the linked numeric summary retains all raw values and ranges. Each completion median is calculated independently, not by adding medians.

| Entry / payload | Legacy send (s) | ExCom send (s) | ExCom / Legacy | Completion Legacy / ExCom (s) |
| --- | ---: | ---: | ---: | ---: |
| byte / null | 1.233 | 3.650 | 2.96× | 1.250 / 4.183 |
| byte / points | 1.017 | 4.567 | 4.49× | 1.033 / 5.217 |
| count / null | 1.233 | 3.217 | 2.61× | 1.250 / 3.917 |
| count / points | 1.017 | 4.550 | 4.48× | 1.033 / 5.267 |
| delimiter / null | 1.250 | 3.800 | 3.04× | 1.250 / 4.333 |
| delimiter / points | 1.017 | 4.600 | 4.52× | 1.033 / 5.300 |
| cli-putch / null | 16.183 | 17.967 | 1.11× | 16.183 / 17.967 |
| cli-putch / points | 17.867 | 19.650 | 1.10× | 17.867 / 19.667 |

For byte, counted and delimiter output, ExCom send times are 2.61–4.52× their Legacy medians. Counted point output takes 4.550 s versus 1.017 s; its ExCom completion median is 5.267 s including the tail. Counted null output takes 3.217 s versus 1.233 s. ExCom null sends vary more between repetitions: the counted case ranges from 2.783 to 4.200 s, while counted point sends range from 4.550 to 4.650 s.

CLI rows include resident command parsing and caller scratch copying. Their much longer absolute times and roughly 1.10–1.11× route ratios must not be presented as pure resident `putch` throughput or subtracted to assign an exact per-byte EMOS cost.

## Deadline observations

1. Legacy: zero ordinary MOS wait expirations in either setup or completion.
2. ExCom: all 24 setup queries exceeded the first ordinary MOS wait; setup reply times ranged from 64 to 84 ticks (about 533–700 ms), with a median of 66 ticks (550 ms).
3. ExCom: all 18 measured completion queries in the direct byte/count/delimiter cases exceeded the first ordinary MOS wait. All six CLI completion queries met it.
4. All eventual replies met the benchmark's five-second observation bound. A complete measurement therefore does not mean the ordinary MOS deadline passed. The fixture preserves the earlier timeout status.

## What this establishes and what remains open

The eZ80 stays inside its output calls substantially longer in ExCom. That can delay game execution directly. Those intervals include EMOS work, UART readiness/CTS waits and downstream P4 work that blocks transmission. Browser presentation is not the completion endpoint, although browser-related P4 scheduling can still affect upstream service. This run does not separate those contributors.

Counted and byte point cases converge near the same ExCom send time despite different outer call patterns. The much slower CLI producer leaves little completion tail. These observations make P4 backpressure worth measuring, but they do not by themselves prove that P4 is the dominant bottleneck or dismiss the source-confirmed EMOS overhead.

## Next bounded measurement

Use the already-built `trace count points` invocation and the existing r03 four-wire UART probes. The analyzer should capture eZ80 TX, P4 TX and both flow-control lines through the marker, complete payload and final pixel reply. Compare gaps in eZ80 TX against P4 CTS deassertion, check actual request/reply timing and validate captured payload coverage. Distinguish a sender that is slow while CTS permits transmission from P4 withholding permission. Retain the current firmware and workload. This selects the next case; no physical capture, SD reconfiguration or performance repair is performed by this report.
