# Quick replacement-delta correctness result

The experimental candidate passed bounded host and physical-browser correctness
checks, then was rolled back at the Author's request. Subsequent Author playtesting found correct output but worse frame
rate with differencing. Further investigation is deferred; the initial correctness
checks do not establish a gameplay performance improvement.

| Check | Result |
| --- | --- |
| Actual encoder/decoder host vectors | 129 exact frames; 123 delta, six full |
| Changed pixel becomes black | Pass: opaque black distinct from unchanged zero |
| Missing/wrong/truncated reference | Rejected; decoder reference invalidated |
| Sequence gaps/wrap, dimension change, incompressible fallback | Pass |
| Physical static reconstruction | 123 exact frames; 121 delta, two full |
| Periodic full recovery | Observed in physical stream |
| Viewer takeover and reconnect | Both begin with independently decodable full frame |
| Actual browser canvas, delta versus full RLE2 | Exact screenshot pixel match; no page errors |
| ExCom CLI and cursor restoration | Command echo observed; cursor restored |

See [machine-readable live summary](live-result.json), [host test](check.mjs),
[physical stream check](live.mjs), [candidate patch](candidate.patch) and
[build manifest](build.json). Local deployment receipts retain actual incoming
flash, independent candidate verification and USB/Ethernet startup evidence.
Factory SHA256: `e3ff620083c6f94e6dec14b5051a660dbf2007097c1b5619fbd6cd6165b4d461`.

An initial static-image assertion ran before the CLI/cursor state was established;
it was invalid setup, not codec evidence. The reported passing run followed
verified ExCom CLI output and cursor hiding. Final state restores the cursor.
No mainboard firmware, EMOS, game binary or SD startup modification was required.
The automated checks above make no frame-rate claim. Subsequent manual findings
follow.


## Author playtest — 2026-09-21

Correct display in both paths; differencing worsened rather than improved frame
rate. Ranked by the only quantified regression; these are human observations of
browser Presented fps, not renderer/game-loop timing or a controlled benchmark.

| Workload | Full-frame RLE2 baseline | Replacement delta + RLE2 | Difference from baseline |
| --- | --- | --- | --- |
| Mode 0 MOS prompt | 28–30 presented fps | About 15 presented fps | About 46–50% lower; `(delta/full - 1) × 100` |
| Nurples manual gameplay | Correct display; better frame rate | Correct display; worse frame rate | Not quantified |

The experimental implementation added retained transmission history, a delta scratch
buffer and compressed delta storage. P4 reads current and retained pixels, builds
the replacement image, compresses full output and eligible delta output to select
the smaller payload, then copies successfully sent canonical pixels into history.
The browser retains and reconstructs a reference as well. This adds memory traffic
and encoding work; their individual contributions have **not** been measured.
It is not display double-buffering/page flipping, nor evidence that differencing
cannot be useful with a different implementation.

XOR is reversible and also produces zero for unchanged pixels. It remains untested;
changing the pixel operation alone would not eliminate retained history, memory
traffic or dual encoding. No XOR candidate or optimization is authorized by this
record. Author deferred further investigation for available tokens. The initial
`?full=1` comparison used the same experimental image; it was not a rollback.
The later restoration below superseded that comparison setup.


### Subsequent disposition

At Author request, the pre-experiment P4 image was restored and independently
verified. This supersedes the earlier leave-installed/full-override advice.
Previous full-frame browser firmware is installed; refresh the ordinary page.
Further delta investigation remains deferred.
