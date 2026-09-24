# BENCH-008 — Ad hoc AGM-style frame differencing

## Executive summary

Status: initial experiment complete; further investigation deferred by Author on
2026-09-21. Output was correct, but presented frame rate worsened at the Mode 0
MOS prompt and in manual Nurples comparison. Author subsequently requested rollback to the pre-experiment firmware. No further implementation or tests scheduled.

Original scope: quick correctness-checked P4/browser experiment followed by
manual Nurples/game playtesting. Encode unchanged pixels as transparent zero and
changed pixels as opaque new RGBA2222 colors, then RLE2. Neither XOR nor arithmetic
subtraction. No TurboVega, detailed timing campaign, renderer changes or game edits.

B08-01 [x] Record contract and historical reuse: AgonJukebox agz a8f1075,
tests/rle2_histogram.py::compute_diff_frame and compare_compressions_movie3.py
use compare-and-replace. RLE2 preserves zero-alpha versus opaque black.

B08-02 [x] Implement an isolated candidate derived from the installed key-query
build. P4 stores the last successfully transmitted canonical RGB222 frame per
video connection. Explicit delta negotiation; other clients keep full frames.
New connection/takeover, missing reference, dimensions/format/period change,
send failure and periodic recovery require full output. Use full output whenever
delta RLE2 is no smaller. A skipped renderer frame is allowed: the reference is
the last sent frame, not the previous generated frame. Include its sequence in
each delta; browser rejects mismatched references and closes for reconnect.

B08-03 [x] Quickly verify exact reconstruction, unchanged areas, changed-to-black,
sequence gaps/wrap, reconnect/takeover, dimension changes and full fallback.
Keep input, request pacing, renderer scheduling and ordinary full-frame support
unchanged. Decoder references are private per connection and updated only after
complete validation. Sending references advance only after successful full sends.

B08-04 [x] Build, preserve installed P4 image, flash and independently verify.
Check live first-full/subsequent-delta reconstruction and reconnection, input/CLI
readiness. Preserve mainboard firmware/EMOS/SD startup. Leave manual game comparison
to Author; no unattended performance campaign, emulator cue or automatic game run.

B08-05 [x] Report concrete playtest instructions and rollback identity. This is
an experiment, not replacement of accepted production protocol or reassessment
of old performance results. Revisit comparisons only after Author feedback.

Standing identity approval: frame-delta-probe-r01, registry r98. Candidate sources
and build overlays stay isolated from unrelated working-tree changes. Normal
browser requests delta by default in this candidate; ?full=1 page override uses
plain full-frame RLE2 for manual A/B. Wire extension EVD1 keeps the32-byte header;
reserved word holds base sequence, payload is ordinary RLE2 RGBA2222 replacement
pixels. Full EVF1/EVR1 keeps reserved zero. Full recovery at least every120 sends;
all decoding reconstructs canonical final RGB222, not browser VDP semantics.

Quick host checks:129exact reconstructed frames,123deltas/six full frames,
including periodic full recovery and rejection of missing/wrong/truncated
references. P4 build passed. Physical connection/takeover checks subsequently passed.


## Physical result and manual handover

Candidate frame-delta-probe-r01-b2026-09-21-03-36-19Z is flashed and independently
verified. [Quick correctness results](BENCH-008/RESULTS.md) pass. Mainboard VDP,
EMOS and SD startup are unchanged. ExCom CLI responds; cursor restored; all agent
video observers closed. Author subsequently confirmed correct output in both paths and worse frame rate
with differencing; see the results below.

Refresh the browser page to load the candidate JavaScript. Default page negotiates
replacement deltas; append `?full=1` to the page URL for full-frame RLE2 comparison.
Each new connection starts with a full frame. Run the ordinary game unchanged.
Rollback image is the preserved key-query-probe-r01-b2026-09-20-02-08-44Z candidate;
private deployment receipts identify the exact saved bytes and restore procedure.


## Deferred investigation

B08-06 [ ] Deferred until Author resumes: isolate added P4 comparison, full-plus-
delta compression, reference-copy and browser reconstruction costs before choosing
an optimization. XOR is a valid alternative representation, not a demonstrated
speed fix. Retained transmission history is additional buffering, not a display
page-flip mode. Do not start a profiling campaign or alter installed firmware
under this deferral. [Manual findings](BENCH-008/RESULTS.md#author-playtest--2026-09-21)
retain the observed regression and distinguish suspects from measured causes.


## Rollback — 2026-09-21

Author requested restoration after the regression. Actual saved pre-experiment P4
flash prefix was restored and independently verified; boot identified
key-query-probe-r01-b2026-09-20-02-08-44Z and native USB startup passed. Served
browser JavaScript no longer contains the delta decoder. One normal Agon reset
re-admits keyboard input through unchanged startup. Reload the ordinary browser
URL; `?full=1` is no longer needed. No EMOS/mainboard VDP flash or SD edit.
