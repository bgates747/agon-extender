# UART alignment précis

## U03 — legacy material reviewed

`agon-extender-legacy` is a read-only reference for this increment. Its
`docs/reverse-uart-audit-summary.md` and `docs/reverse-uart-driver.md` describe
115200-baud, fixed eight-byte POLL/COMMAND/RESPONSE exchanges, switched buffer
ownership, GPIO15/21 output enables and restoration to a forward parallel pipe.
Those are not current 1,152,000-baud stock-compatible full-duplex UART contracts.
The Author recalls an intervening logic buffer; do not infer its exact part
number from that recollection or import historical pins into today's wiring.

| Legacy artifact | Reuse | Do not import |
| --- | --- | --- |
| `tools/run_rev02a_loopback`, `pi_rev02a_loopback` | Immutable run directories, image identity checks, capture hashes and bounded collection | Reset/deploy actions, old endpoint maps and buffer-enable ownership |
| `tools/analyze_rev02a.py`, `analyze_rev02.py` | Independent sample-level UART decoding, exact frame validation, post-exchange checks | 115200 baud, fixed8-byte protocol and historical LA channel constants |
| `tools/analyze_pinwalk.py`, `analyze_header_pinwalk.py`, `pi_pinwalk_capture` | Identify channels from observed pulses, not wire colour guesses | Historical channel-to-pin assignment |
| `tests/runs/2026-08-18_200400_rev-02-ping/rev02-analysis.json` | Prior correctness/ownership evidence | Throughput comparison against current production UART |

The cited ping capture reports PASS at8MHz/6,000,000samples, no overlapping
active enables, 101.375us forward-to-reverse neutral time, 13.875us reverse-to-
forward neutral time, and1024following canary clocks without observed masked
mismatches. These are short exchange/ownership metrics, not sustained useful
bytes per second. No directly comparable sustained UART-rate result was found
in the focused legacy JSON/Markdown/result-text scan. The old probes observed
only selected canary bits; do not upgrade that to an all-byte integrity claim.

Current project's AUDIT-005 `uart-cts-findings.md` is a more relevant electrical
reference: its counted-point trace found3.407s of a4.456s payload wire span
under receiver CTS backpressure, exact observed payload bytes, and no framing
errors. It is an older graphics-loaded P4 image/workload, not this pass's pure
transport baseline. Reuse its decoder and timing attribution techniques only
after verifying current sniffer channels and image identities.

## U04 — current cursor

Next: complete ordinary stock buffer/return APIs and EMOS receive semantics,
then freeze the pure-data fixture before code or physical tests. The confirmed
bulk-read divergence is already documented in QUAL-003's upload findings.
