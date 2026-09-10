# Browser-disconnected counted-point findings

Run `AUDIT-005-2026-09-10-20-03-35Z`, procedure `uart-path-capture-r02`.
**Acquisition, waveform, condition record and returned Agon CSV pass. W7
was accepted by the Author on 2026-09-10.** The
[frozen control contract](browser-disconnected-control.md) remains unchanged.

Closing the browser did not materially change this workload's total time.
P4 withholding UART permission remains the dominant observed idle component.
Individual long pauses became much shorter, so this result does not establish
that browser activity is harmless or that every remaining delay has one cause.

## Validated evidence

The analyzer captured all 720 million samples at 24 MHz. Both decoders agree
on the complete 32,768-byte payload, marker and correct black/white pixel
replies. There are no framing errors or byte starts without CTS permission.
Original capture and host integrity manifests pass. The
[analysis](evidence/browser-disconnected-trace/analysis.json),
[collection record](evidence/browser-disconnected-trace/collection.json) and
[comparison](evidence/browser-disconnected-trace/comparison.json) retain exact
values and hashes; full acquisition and decoder output remain in the ignored
bench record.

The [host condition record](evidence/browser-disconnected-trace/host-condition.json)
records operator-confirmed client closure and 5.0004 seconds of settlement
before acquisition. This is not independently observed server client count.
The unchanged executable's compiled CSV annotation still says a connected
client is required. The host record explicitly overrides that expectation for
this control and links the original CSV hash; the CSV is preserved unchanged.
Private host topology is omitted from the tracked condition record.

The returned [00000005.CSV](evidence/browser-disconnected-trace/00000005.CSV)
is the only new result since SD handover. Its build, case, pixel values,
clock arithmetic and successful Legacy return match. The executable, startup
and four prior CSVs retain their hashes. FAT file time is not used as a UTC
run identity. Neither installed firmware image changed. The control helper
was prepared after contract commit `1275b01` with a dirty worktree; this is
exploratory evidence, not firmware qualification.

## Connected versus disconnected

The reference is the completed W6 run
`AUDIT-005-2026-09-10-19-44-52Z`, not the earlier full-suite median. Values
below use wire boundaries. Delta means disconnected minus connected; ratio
means disconnected divided by connected.

| Interval | Connected (s) | Disconnected (s) | Delta (s) | Ratio |
| --- | ---: | ---: | ---: | ---: |
| Payload transmission span | 4.456138 | 4.390836 | -0.065303 | 0.9853 |
| Estimated byte occupancy | 0.284444 | 0.284444 | 0 | 1.0000 |
| Inter-byte idle, P4 withholds permission | 3.407279 | 3.343735 | -0.063545 | 0.9814 |
| Inter-byte idle, P4 permits sending | 0.764414 | 0.762657 | -0.001758 | 0.9977 |
| Longest payload gap | 0.154098 | 0.014203 | -0.139895 | 0.0922 |
| Marker query/reply | 0.124437 | 0.001410 | -0.123027 | 0.0113 |
| Final query/reply | 0.624762 | 0.684048 | +0.059285 | 1.0949 |
| Payload start through final reply | 5.081191 | 5.075174 | -0.006017 | 0.9988 |

Disconnected, CTS-high idle accounts for **76.2% of the payload span and
81.4% of inter-byte idle**, versus 76.5% and 81.7% connected. Total elapsed
time differs by only 6 ms, about 0.12%; one run per condition cannot establish
that small difference as an improvement. The marked reduction in longest
gaps and marker-reply delay suggests browser activity affects the distribution
of waits. It does not isolate snapshot composition, Ethernet, locks or task
scheduling. The short marker reply also does not establish compliance for
every query: both setup and final CSV queries still exceed their first
ordinary MOS wait before eventually completing within the measurement bound.

Agon RTS stays continuously permissive during the disconnected run's
683.953 ms wait for the first final-reply byte. It withholds permission for
only about 47 microseconds while the six-byte reply arrives, effectively the
same as connected. Agon blocking reception does not explain that long wait.

| Same-run interval | Connected clock (s) | Disconnected clock (s) | Clock delta (s) | Disconnected wire (s) | Wire minus clock (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Payload send | 4.450 | 4.383 | -0.067 | 4.391 | 7.5 |
| Completion tail | 0.617 | 0.683 | +0.067 | 0.684 | 1.0 |
| Payload through reply | 5.067 | 5.067 | 0 | 5.075 | 8.5 |

Each disconnected wire/clock difference is within the clock's 16.67 ms
quantum. The software and wire boundaries differ; this agreement is not
precise synchronization. The machine-readable comparison includes unrounded
values, clock ratios and reverse-permission deltas.

## Interpretation and proposed next investigation

The main throughput problem persists without requested browser video.
The remaining targets are P4 receive/parser service and drawing completion,
including waits between those components. The source map identifies the
parser's bounded outer loop and the frame service's bounded primitive drain;
the waveform alone cannot attribute the observed pauses to either one.
CTS-low gaps likewise do not measure pure EMOS CPU overhead.

Recommend one bounded P4 investigation: trace where the retained parser waits
for drawing/queue service and where the UART receive loop yields, then select
minimal internal timing observations that distinguish those waits. Preserve
this browser-off workload as the comparison case. Choose a repair only after
that attribution; no EMOS rewrite, core reassignment, firmware change or
additional capture has been performed or authorized by W7. The Author
requested and subsequently approved the [W8 contract](p4-wait-attribution.md),
authorizing its execution after freezing the findings and contract. The original
collection record retains its earlier pending-review state; the separate
[acceptance record](evidence/browser-disconnected-trace/acceptance.json)
records the subsequent disposition without rewriting run evidence.
