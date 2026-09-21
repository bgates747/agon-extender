# Official stock control — no crash observed

## Executive summary

Published stock VDP v2.16.0 did **not** reproduce the sprite panic in this one
control. The unchanged SS_INITIAL scene/player ran without the optional capture
request; a30-second post-invocation observation contained no panic. Escape was
followed by successful ordinary CLI commands starting the SD service. This
narrows the evidence: the earlier physical failure occurred with diagnostic
firmware, and must not yet be labelled a diagnostic-independent stock defect.

## Evidence and limits

1. [Run](evidence/result.json): QUAL-004-2026-09-21-00-45-53Z. Host elapsed38.33s
includes command injection; observation was30s. This is not a rendering benchmark.
2. [Installation](evidence/installed.json): exact published application SHA256
b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f matched retained
release metadata, was flashed and independently verified. Incoming bootloader,
partitions and application already matched the published release; app0 selection
was preserved. No local build, row tap or private capture handler was installed.
3. [Input hashes](evidence/staged.json): SD player, SS_INITIAL and sidecar read
back identical to the prior attempt. Invocation omitted only the capture token.
Mode20 was selected in autoexec. This control configured only mainboard video;
the preceding paired procedure had also initialized P4 mode20 before returning
to Legacy. It is therefore not a fully identical startup-history experiment.
4. [Serial](evidence/mainboard.serial.gz) contains the startup watchdog-removal
warning, but no Guru Meditation/panic. [Clean exit](evidence/clean-exit.json)
records Escape and subsequent SD-service admission. No mainboard screenshot or
pixel capture was taken, so visible scene correctness is not asserted.
5. [Final state](evidence/final-state.json) and [prompt](evidence/final-prompt.png):
original startup restored/read back, keyboard neutral, SD offline and observers
closed. Stock application is also the original incoming application. P4/EMOS
unchanged. Actual full flash backup retained privately.

One negative run cannot exclude an intermittent stock defect. Diagnostic
instrumentation, binary layout/timing and startup history remain possible
contributors. Sprite qualification remains blocked; no renderer fix or added
passing-image coverage follows from this control. See
[FWBUG-002](../../../../firmware-bugs.md#fwbug-002).

## Subsequent Author visual control

The [manual review](VISUAL-REVIEW.md#author-observation--accepted-visual-control)
confirmed the expected striped background and red/cyan software sprites, stable
with no apparent scanout disruption. This is a stock visual pass for SS_INITIAL,
not exact pixel qualification or proof of the diagnostic failure's cause.
