# P01f baseline measurements

All three unchanged-r45 controls passed the r05 deterministic fixture and native completion gates. These are explicit RefreshSprites completion timings, not physical VGA scanout or browser presentation. Mainboard is the retained historical reference, not a new measurement. Positive percentages below mean longer (worse) p95 spacing relative to mainboard.

| Condition | Refresh completions/s | p50 ms | p95 ms | p99 ms | Maximum ms | p95 vs mainboard |
|---|---:|---:|---:|---:|---:|---:|
| Streaming repeat | 60.053 | 16.518 | 29.291 | 33.561 | 37.752 | +71.7% |
| Streaming first | 60.056 | 16.641 | 24.990 | 29.416 | 37.419 | +46.5% |
| Output disabled | 60.053 | 16.668 | 17.052 | 20.776 | 21.090 | -0.1% |
| Mainboard historical | 59.927 | — | 17.063 | — | — | Baseline |

Compared to the same-image output-disabled run, streamed p95 spacing is 46.6% and 71.8% longer. Historical r45 normal was 60.055/s, p95 29.238ms; output-off 60.053/s, p95 17.049ms. The present controls reproduce both the near-60 average and streaming tail. They do not establish pacing parity.

| Full-frame output operation | First streaming | Repeat streaming | Repeat vs first |
|---|---:|---:|---:|
| Compose mean ms | 6.596 | 13.424 | +103.5% |
| Send mean ms | 17.753 | 17.760 | +0.0% |
| Sends/game-window second | 28.226 | 27.232 | -3.5% |

Composition and sending are overlapping wall-time scopes that include waiting/preemption; do not add these means or interpret them as isolated CPU costs. Full frames are 196608 RGB222 bytes plus the 32-byte EVF header. Ordinary WebSocket/TCP/Ethernet overhead is additional. No matched mainboard network operation exists. Output-disabled counted zero composition and send operations.

Snapshot wall time approximately doubled across streamed repeats while mean sending stayed almost unchanged. This does not identify the reason: order, allocations, scheduling and composition timing remain possible contributors. The P4 was not rebooted between controls. The next priority experiment needs matched/repeated controls, not one favorable before/after pair.

| Collection scope | Reset to completed collection, s | Measured marker window, s |
|---|---:|---:|
| p01f-normal1-probe0 | 203.069 | 39.962847 |
| p01f-off2-probe0 | 199.609 | 39.949579 |
| p01f-normal3-probe0 | 199.903 | 39.953196 |

Reset-to-collection includes startup, a fixed 180s observation/wait window and result retrieval; excludes preparation, between-run staging and restoration. Game marker windows are separate. Do not interpret the roughly three-minute collection window as game execution time.

## Browser checks

- p01f-normal1-probe0: 28.346 received frames/s over the full 180.178s observer window, 0 sequence gaps; page errors=[], overflow=False.
- p01f-normal3-probe0: 27.515 received frames/s over the full 180.039s observer window, 0 sequence gaps; page errors=[], overflow=False.

Browser whole-window statistics include mode/setup/terminal screens. They are not game-only rates and do not measure physical display presentation. Game-window sends are reported separately above.

## Validity and retained evidence

Every fixture completed 2400 states, passed its terminal pixel query, and matched state SHA256 f43eaa27074aaf6916eded49e5f97bb7eb64a79fd0ccc060f1923a9eb3ea3948. Each native trace has 2400 ordered completions, maximum pending one, and output accounting has zero pending/invalid operations. First 120 completion records are warmup; p50/p95/p99 are nearest-rank statistics over the remaining 2279 intervals, matching the existing analyzer convention. Framebuffer allocation logs select internal 512x384 in all three controls; this does not prove identical snapshot-pool placement.

evidence/ contains raw NP04 files, sanitized NPTRACE/NPOUT records, decoded summaries, browser summaries and SHA256 manifest. Private full serial/browser/flash logs and images remain under agents/p01f/. No unrelated device identities are published. Archived images and runner identities are in provenance.json; deployment.json records verified installation.

P01e remains failed qualification. Recovery here does not isolate whether its static rings, code layout, scheduling probes or another difference caused the slowdown. No scheduling fix, architecture simplification, new Rally result, hardware-sprite qualification or 60fps browser claim is made.
