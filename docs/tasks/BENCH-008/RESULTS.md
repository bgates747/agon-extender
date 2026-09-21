# Quick replacement-delta correctness result

The candidate passed bounded host and physical-browser correctness checks and is
installed for Author playtesting. These checks establish reconstruction and
connection recovery, not a gameplay performance improvement.

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
No frame-rate conclusion is drawn; Author compares games manually next.
