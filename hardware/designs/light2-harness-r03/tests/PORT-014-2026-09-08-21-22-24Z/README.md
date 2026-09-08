# Paced SD counting sample — PASS

The SD-loaded C application sent its clear/banner and decimal 1..10 through
EMOS's resident text gateway. P4 executed all 11 transactions through retained
EDP and returned their actual General Poll replies. The Author supplied a
browser screenshot showing `EMOS TO EDP: UART TEXT` and 1..10 on separate
lines, then confirmed SD/CLOCK and sample PASS with MOS return on the captured
run and two additional Agon-only resets.

The original trace and serial hashes verify. The frozen serial checker passes
all 11 ordered transactions. Offline raw-sample decoding and the independent
sigrok 8N1 decoder agree on exactly 136 forward and 33 return bytes at 1152000
baud. Each character has valid framing and active-low CTS permission. The
analyzer saved all 288 million samples at 24 MHz (12 seconds). All four signals
are quiet for the final 6.287879 seconds and end high;
P4 serial monitoring is clean for 6.008467 seconds after the
last counting PASS. No acquisition or quiet-tail exception is required.

The ten number transactions begin about 0.44–0.56 seconds apart after the first
banner-to-number interval. The application's accepted 250 ms pause is additive
to EMOS/P4 completion and scheduling; this is not a 250 ms throughput promise.
Repeated runs are Author observations, not additional captured waveforms.
The screenshot is retained in the Author's conversation; the tracked record
preserves its observed content without copying browser/account chrome.

`run.yaml` records the three exact clean candidate builds, checks and hashes.
`logic.sr` is the unchanged original acquisition; `uart-decoder.txt` contains
the independent byte annotations and `measurements.json` contains transaction
boundaries. `serial-excerpt.txt` retains text-fixture diagnostics; the original
serial log, command lines and offline review helper stay in the private bundle.

This completes PORT-014 and its EMOS implementation task INTEG-008 for the
bounded diagnostic. The r01/r02 results keep their original limitations; r03
supersedes their outstanding repeat-test work without relabelling those runs.
Artifact registry identities/status remain unchanged. Ordinary MOS VDU and
clock remain onboard; this does not activate Exclusive Compatible mode.
