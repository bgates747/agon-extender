# Interim ladder observations

The matched corrected controls and first two network rungs pass. Full sequence
and repeats remain in progress; this is not a final threshold or parity claim.

| Condition | Native completions/s | Native interval p95 ms | Compose mean wall ms | Payload Mbit/s |
|---|---:|---:|---:|---:|
| p01g2r-off | 60.053 | 17.116 | — | 0.000 |
| p01g2s-compose | 60.054 | 17.308 | 6.35172723475355 | 0.000 |
| p01g2s-eighth | 60.048 | 20.900 | 8.137016256773656 | 10.657 |
| p01g2s-quarter | 60.045 | 21.004 | 9.750135529608007 | 21.635 |

Payload excludes framing. Wall scopes overlap and include preemption/waits.
Mainboard paced loop is measured separately, not inserted as a native-completion
measurement. No compression trial or new scheduling intervention.
