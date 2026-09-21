# Packed bitmap expansion — passed within scope

## Executive summary

PACK1, PACK2 and PACK4 pass on mainboard VDP and Extender: **589,824 pixels,
zero differences**, and zero independent expected-image mismatches on either
endpoint. Six mainboard captures were repeatable; each P4 case had two distinct
identical frame generations. No renderer repair was needed. BM02 is complete;
BM03 remains deferred. Cumulative paired coverage is77scenes /14,410,752pixels.

| Case | Mapping | Mainboard repeat/oracle | Extender repeat/oracle | Paired mismatches |
|---|---|---|---|---|
| 1 bit/pixel | Inline | Pass / 0 | Pass / 0 | 0 /196,608 |
| 2 bits/pixel | Buffer | Pass / 0 | Pass / 0 | 0 /196,608 |
| 4 bits/pixel | Inline | Pass / 0 | Pass / 0 | 0 /196,608 |

34×34 source patterns use byte-aligned rows, including partial final bytes in
1/2bpp. Index zero leaves the white backdrop visible. Command72 expands indices;
explicit RGBA2222 bitmap creation follows. Full512×384 mode20 surfaces compare
without cropping, masks, tolerance or scaling. Mode selection belongs to startup.

## Evidence and provenance

[Mainboard](evidence/capture/results.json), [Extender](evidence/extender/results.json),
[provenance](evidence/provenance.json), [file hashes](evidence/SHA256.json),
[restoration](evidence/final.json). Retained evidence contains raw serial captures,
compressed browser wire frames, decoded pixels, PNGs and difference images.
Inputs are packed-expansion-probe-r02 at110fc061; the wider workspace was dirty
with unrelated work. No firmware was rebuilt; this is bounded comparison evidence,
not a new qualified/released product identity. Existing mainboard-image-capture-r02
was temporarily installed; actual flash was backed up and independently verified.
P4/EMOS were unchanged. See the shared [diagnostic provenance](../ARTIFACTS.json).

Mainboard run `QUAL-004-2026-09-21-02-44-53Z` took258.15host seconds;
Extender run `QUAL-004-2026-09-21-02-49-49Z` took113.25host seconds.
These acquisition/recovery wall-clock durations exclude fixture preparation,
flashing and final restoration; they are neither frame rates nor rendering times.
Host clock was not independently calibrated. No voice notification was required.

## Invalid initial setup and correction

r01 omitted source/map clears when extracting the older suite. Agon reset resets
mainboard VDP but does not guarantee fresh P4 buffers. Stock buffer command0
appends blocks, and command72 requires a single-block mapping buffer. Later P4
cases therefore consumed retained state: PACK2 repeated PACK1; PACK4 also differed.
This was a fixture-isolation mistake, not a demonstrated firmware defect or
capture crash. r02 reinstated explicit clears from the original suite; both
endpoints were rerun. Initial run identities and discrepancy counts remain in
[the contract](CONTRACT.md); their raw local evidence is retained for traceability
but is not counted as valid parity evidence. No failure-triggered uninstrumented
control was needed for the corrected, passing suite.

## Restoration and remaining limits

Incoming mainboard flash sectors and95-byte startup were restored and verified.
Legacy mode20 MOS is responsive, q4draw is loaded but not running, keyboard is
neutral, SD service is closed and no capture observers remain. Production games
were untouched. Test files remain under /test/qual004.

This does not establish every bit depth/mapping/packing combination or performance.
The repository-wide version validator still reports a pre-existing light2-harness-r02
connectivity hash mismatch. The changed artifact registry itself validates; no
wiring file was changed as part of this work.
