# Retained card results — offline processing r01

## Executive summary

Offline processing validates 16 predecessor smoke records and 30 selected
mode-20 records against the collected card bytes, frozen fixture plans,
installed-image receipts and retained P4 diagnostic windows. All 46 records
match their recorded identities; their bracketed output-error deltas are zero.
The new corrected-pair campaign has no results. Its newest optimized RGB888
versus indexed comparison therefore remains unmeasured.

The control-file audit finds 562 matching files, 80 missing files and no
mismatches. The missing files are the 40 indexed short-run configurations and
40 associated launchers. No card or bench access occurred during processing.
Stop for Author confirmation of SD-card access before further staging.

## Evidence and validation

The source collection is `RESEARCH-007-2026-10-13-19-19-10Z`: 2,878 files,
42,374,958 bytes, independently verified against source SHA-256 checksums.
Processing rechecks those checksums and retains fresh JSON/CSV summaries under
the collection's ignored `analysis-r01` directory. Exact private paths remain
in the local collection record; no frozen input or result was overwritten.

The maintained SCAN decoder and the frozen r04 analysis helper enforce record
length/order, fixture identity, counts, warm-up, window ID/tag, timer/fault
flags, render schema and trajectory contracts. Finite workloads additionally
retain their exact fence-sample checks. Firmware identities match actual
verified installation receipts and corresponding build manifests. The r04
analyzer's existing fault-path selftest also passes.

| Retained set | Valid records | Coverage | Limit |
|---|---:|---|---|
| Predecessor optimized RGB888 smokes | 16 | Eight workloads in modes 0 and 3; 156 measured updates | Before the HDMI aspect correction; no indexed counterpart |
| Plain RGB888 mode-20 cohort | 24 | Eight workloads, three windows each | Both bitmap-fast and scroll-fast options are off |
| Indexed baseline mode-20 pilot | 3 | Heavy bitmap, partial scroll, software Nurples; one window each | Insufficient independent repeats |
| Indexed scroll-option mode-20 pilot | 3 | Same three workloads; one window each | Insufficient independent repeats |
| Corrected-pair short admissions | 0 | None | All 80 still required |
| New full campaign | 0 | None | All 240 measurements remain unstarted |

All selected firmware builds above use source
`e26c24f743b9b94efa05eac46f2f237689ac3b5b`. The corrected pair uses
`c788b668d64f61431b8de34b72262556d9e4e7b0`; these older records cannot qualify
that pair. The predecessor smoke image is
`rgb-001-r12-b2026-10-13-04-29-52Z` (application SHA-256
`d1cd3a32496881c47b404030aa4d9bea1e71164a2d35c54ff09dc0d8206a0b7d`).
Its mode-3 records retain the old 684×384 carrier. The mode-20 plain RGB image
is `rgb-001-r12-b2026-10-13-04-20-57Z`; the indexed baseline is
`indexed-hdmi-r06-b2026-10-13-04-02-15Z`.

Other historical card datasets and informative failed records remain retained;
they are outside these selected passing counts. In particular, the earlier
diagnostic-ID/fence failure does not become a passing smoke through collection.

## Diagnostic mode-20 comparisons

These values compare the median of three plain RGB888 window means with one
indexed baseline pilot window. They are diagnostic point estimates, with no
repeat-qualified performance gate or claim against the newest optimized RGB888
control. Ranking is smallest percentage reduction first.

| Workload | Plain RGB888, µs/update | Indexed baseline, µs/update | Mean-cost reduction |
|---|---:|---:|---:|
| Software Nurples | 4,140.39 | 1,808.68 | 56.32% |
| Partial scroll | 3,974.50 | 1,711.43 | 56.94% |
| Heavy bitmap | 11,556.00 | 3,249.52 | 71.88% |

Reduction is `100 × (RGB888 − indexed) / RGB888`. Each number measures queued
render execution per fixture update. Native-mutex waiting, eZ80 submission,
UART transport, pacing and HDMI output preparation are separate scopes.
Nurples is unfenced: its window mean does not establish individual render
tails or renderer-completion latency. None of these values proves faster
gameplay, distinct displayed frames, visual stability or input latency.

The single-window indexed scroll-option pilot gives the following point
estimates. Positive reduction means less queued render time with the option;
negative reduction means more. Ranking is smallest reduction first, with the
indexed baseline explicitly serving as the reference.

| Workload | Indexed baseline, µs/update | Scroll option, µs/update | Reduction versus baseline |
|---|---:|---:|---:|
| Software Nurples | 1,808.68 | 1,849.07 | −2.23% |
| Heavy bitmap | 3,249.52 | 3,256.81 | −0.22% |
| Partial scroll | 1,711.43 | 1,693.07 | 1.07% |

These limited observations provide no new justification for enabling the
indexed scroll option. The previously selected indexed baseline remains the
comparison candidate. No frozen selection or historical report was changed.

## Remaining deployment

The audit compares the mixed prepared package with the collected result-tree
files by full length and SHA-256. It verifies file contents, not current access
to a card that the Author has since removed.

| Control files within the copied tree | Count |
|---|---:|
| Matching | 562 |
| Missing indexed smoke configurations | 40 |
| Missing indexed smoke launchers | 40 |
| Mismatched | 0 |

The 101 maintained support/fixture files under `/extender` were outside the
collection. Their previous deployment receipts remain retained; the copied
result tree cannot establish their current on-card contents. The unused full
job result paths remain absent, including the reused predecessor paths.

## Collection workflow consequence

The current master downloads and validates each raw result before accepting
that job's receipt. Fetching the card at the end cannot remove that serial cost
without an explicit deferred-collection phase. That phase is remaining host
runner work, not an implemented capability or a reason to claim readiness.

The host must retain P4 diagnostic windows, firmware identities and fixture
bindings during execution. SD raw files alone cannot reconstruct P4 telemetry.
Deferred receipts must remain unvalidated until the host processes the copied
raw records and checks paired trajectories/repeat counts. The master must show
an awaiting-collection state and withhold its success cue until validation and
the admitted hardware notification are complete. Operator card handling,
fixture execution, retrieval and notification require separate duration records.

The estimated approximately 100 minutes of future serial retrieval and the
4.404-second collection of this different retained dataset are not comparable
speed measurements. The physical collection excludes operator handling.

## Stop boundary

[Multimode preparation](MULTIMODE-QUALIFICATION-R01.md) remains paused. No SD
mount inspection, card write, SSH request, bench command, reset, flash or fixture
invocation occurred during this offline processing. Ask the Author directly in
chat to confirm SD-card access before any subsequent card operation.
