# EMOS installation confirmed; keyboard-test SD ready

The Author reported “good flash” for candidate
`agon-emos-v0.1.8-b2026-09-09-03-07-18Z`. The returned SD contains the matching
consumed `EMDONE.BIN`, with `EMNEW.BIN` absent. This combines the operator's
installation report with payload verification; no independent flash-memory
readback was performed.

Working v0.1.7 rollback and the older fallback retain their checked hashes.
Existing test files and autoexec were backed up before replacement. The SD now
contains same-build EMBOOT, its check file and candidate observer
`uart-keyboard-probe-r01-b2026-09-09-03-09-38Z`. Exact autoexec and file hashes
are retained here. Mode 3 is selected only in autoexec. The test script contains
no flash command. All copied bytes were verified and the SD safely unmounted.

P4 candidate `uart-keyboard-probe-r01-b2026-09-09-03-01-48Z` and staged helper
hashes still match; stable USB identity passes read-only reinspection. The P4
continues running the preceding counting receiver. Flashing awaits explicit
authorization. The prepared capture launcher remains inactive until that
candidate is installed and verified.

The paired test must still show Agon SD/CLOCK PASS, both detailed P4 KEYBOARD
PASS checks, mainboard input restored and return to MOS. P4 serial stages,
waveform review and two additional Agon-only reset results remain pending.
This record does not qualify physical keyboard delivery or browser input.
