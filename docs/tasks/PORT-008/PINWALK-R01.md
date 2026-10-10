# PORT-008 — Eight-data-line pinwalk r01

The forward walk matches all eight expected data-wire assignments. No crossed,
stuck or coupled data line is indicated by these digital samples. The reverse
echo is corrupted, including its early waveform; the parallel link remains
unqualified. Keep the data wiring unchanged pending CLOCK/VALID/READY capture.

## Adaptation and scope

1. Author requested a full data-pin walk before moving probes, then explicitly
   required adapting an existing fixture. Reused HW-002's
   [pinwalk fixture](../HW-002/pinwalk/README.md): PC0 through PC7 emit ordinal
   one-through-eight active-low pulses, with all-high idle and a two-half-period
   slot gap. The original fixture and assembly remain unchanged.
2. Adapted that pulse pattern to the existing data-only MOSlet's API51h binding.
   EMOS owns admission, GPIO, clocks, direction changes and UART recovery;
   the MOSlet supplies payload bytes only. Each half-period is 32 repeated bytes.
   Added 128-byte all-low brackets. Total payload:3456 bytes, one forward block
   followed by one same-length P4 echo. No raw application GPIO/register/vector
   access, standalone diagnostic firmware, mode change or firmware flash.
3. All eight analyzer leads remained on the Author-confirmed matching-colored
   data wires, with common ground. CLOCK, VALID and READY were not probed.
   The existing HW-002 analyzer channel map supplies expectations; the capture
   independently checks those expectations rather than assigning channels from
   observed counts after the fact.
4. Installed pair is unchanged from the
   [full EDP data-only comparison](DATA-ONLY-CONTROL-R01.md). That comparison's
   deliberately weaker completion criterion remains; status0 is not integrity
   proof. P4 retains the forward bytes and sends them back. This capture cannot
   distinguish receive/storage corruption from transmit corruption without
   byte-edge evidence or an independent check of P4-retained bytes.

## Results

| Bus bit | Lead | Analyzer channel | Expected pulses | Forward observed |
|---|---|---|---:|---:|
| D0 / PC0 | Yellow | D1 | 1 | 1 |
| D1 / PC1 | Gray | D6 | 2 | 2 |
| D2 / PC2 | Orange | D3 | 3 | 3 |
| D3 / PC3 | Purple | D4 | 4 | 4 |
| D4 / PC4 | Red | D5 | 5 | 5 |
| D5 / PC5 | Blue | D2 | 6 | 6 |
| D6 / PC6 | Brown | D7 | 7 | 7 |
| D7 / PC7 | Green | D0 | 8 | 8 |

1. Forward waveform reproduces the full ordered walk, including all-low brackets.
   Reverse waveform does not reproduce the complete walk. Its later PC4–PC7
   groups reproduce five/six/seven/eight pulses on the expected channels; the
   earlier portion is scrambled. This is not an alternate pin mapping.
2. Agon result: forward3456/status0/guards pass; reverse3456/status0/guards pass,
   first returned mismatch at zero-based offset0. Neither operation was replayed.
3. Acquisition:24MHz ×480million samples,20seconds, all eight physical channels,
   exact length and successful sigrok exit. Sample-clock accuracy is uncalibrated.
   Plateau analysis uses a400-sample/16.67µs minimum; shorter transients remain
   in the retained raw samples. This checks static digital attribution, not
   analogue integrity or exact CLOCK/VALID alignment. It also does not independently prove continuity
   beyond the probe attachment points or reception at the P4 input pads.
4. Capture/invocation/retrieval span:20.87 host wall seconds. Preparation is
   separate. One preparatory Agon reset restored initially unavailable input;
   no reset occurred during the capture and no payload retry followed it.
5. Original38-byte startup read back unchanged; listener exited; input ready and
   neutral, with no held or pending keys. Mainboard VDP and production unchanged.

## Reproduction and evidence

Ignored local evidence: `agents/port008-live-qualification/pinwalk-r01/` contains
the adapted fixture source/binary, manifest and original-source hashes, build
log, staging/readback receipt, exact invocation, complete capture, Agon CSV,
plateaus and analysis. SD files: `/emos/p8walk.bin`,
`/extender/install/p8walk01.txt`, `/agents/extender/results/P8W01.CSV`.
Those result names are consumed; any rerun requires fresh names and a refreshed
bench review. Source identity: `header-pinwalk-native-r01`; timestamp and exact
binary hash are in the manifest. This is experimental evidence, not production.

The capture preserves original channel bit positions in `logic.sr`; extracted
sample SHA256 is
`7d1c2f76e9d11903e30a1b90f6cd572ffd30f80018927312b06ec5055d54a7d2`.
Forward walk bracket window: samples164678511–165120549. Reverse later four
groups:166515614–166780684. Preserve both the intact forward walk and informative
reverse failure before changing probes. Author controls subsequent probe moves.

## Proposed next probe placement — not yet performed

Move three nearby data leads onto CLOCK, VALID_N and READY_N on the same
header, preserving the other five data probes. The Author rejected the earlier
farther-away lead selection; do not reuse it. This exposes data activity
alongside the handshake. Exact connector contacts and proposed channel reassignment
belong in the ignored local bench record. Power off before physically moving
leads. No new acquisition is authorized or started by this proposal.

## Follow-up capture

The [corrected clock/handshake capture](PINWALK-R02.md) uses the same fixture
and unchanged firmware. It confirms exact payload clock counts and isolates
observed return corruption to D7 among the five data bits still probed. Initial
missing-SD setup was resolved by reseating the card, not a firmware change.
