# P01 — matched output comparison

## Executive summary

**The long timing tail is associated with active P4 web output in this matched
software-sprite fixture.** With output off, two runs closely match historical
mainboard completion p95; with output on, both are materially worse, although
one meets the existing tolerance gate. Mean completion remains approximately60Hz
throughout. This is pacing interference, not evidence that the drawing workload
cannot average60completions/s. All four runs completed the same2400 states and
refresh commands, with matching state hashes and terminal checks.

Worst completion-p95 cases first; the stock baseline is historical, not rerun.
Percentage =100×(run p95 / stock p95−1); positive means worse tail latency.

| Run | Completion FPS | Mean interval ms | p95 ms | Max ms | p95 vs stock | Enqueue p95 ms |
|---|---:|---:|---:|---:|---:|---:|
| p01-on1 | 60.059 | 16.650 | 28.879 | 37.651 | +69.25% | 27.0 |
| p01-on4 | 60.058 | 16.651 | 24.890 | 37.304 | +45.87% | 22.936 |
| stock_historical | 59.927 | 16.687 | 17.063 | 31.816 | +0.00% | not in retained summary |
| p01-off2 | 60.054 | 16.652 | 16.981 | 21.156 | -0.48% | 17.312 |
| p01-off3 | 60.051 | 16.652 | 16.949 | 20.931 | -0.67% | 17.301 |

**Recommended next action: P02a/b's existing composition-discard versus prebuilt
network-stream controls**, preserving the same workload and output accounting.
These can distinguish snapshot CPU/memory/locking cost from network scheduling
without adding a broad parser probe. This sequencing recommendation follows
P01 evidence; it does not authorize or execute P02. P01c/d remain deferred,
unexecuted, if those controls fail to localize the cause. No immediate firmware
fix is established. Golem remains excluded.

## What was measured

1. Archived r43, byte-verified after preserving installed r44; same candidate
   throughout. No new firmware build, renderer change, MOS change or mainboard
   VDP flash. r44 native-acquisition instrumentation is absent.
2. Existing r05 unfenced software-sprite fixture,2400 states,120 warmup boundaries,
   2279 measured intervals. A nonce binds every result and completion trace.
   Source/assets/fixture identities are in [provenance.json](provenance.json).
3. Run order on/off/off/on. Each condition gets a180second observation/wait
   window, with no periodic HTTP/SD diagnostic polling during game timing.
   The USB handle is opened before controlled resets and stays open; trace
   dumps occur after the terminal fence. This removes historical host polling
   equally from both new conditions, so they are the strongest causal comparison.
4. Actual mode20 game allocation is512×384,196608bytes, internal for all runs.
   Default640×480 preparation mode uses PSRAM fallback. Do not conflate them.
5. Drawing opportunities4/logical frame; parser core0 priority3, drawing core0
   priority5, output core1 priority2. These are candidate configuration/source
   identities, not a new scheduler trace or task-time attribution.
6. The mainboard reference remains the earlier matched refresh trace, with
   stock VDP and qualified EMOS provenance retained. No fresh mainboard flash
   readback or timing run was performed. Thus this is not final parity certification.

## Output observations

- p01-on1: 27.988 received FPS across the full180.18second browser window; 5044 frames, 0 sequence gaps, no page errors or connection closures.
- p01-on4: 28.664 received FPS across the full180.16second browser window; 5166 frames, 0 sequence gaps, no page errors or connection closures.

These browser rates include preparation and terminal surfaces; they are not
pure gameplay FPS or proof of distinct image changes/physical presentation.
Both output-off runs held every output recorder phase count unchanged. They
are diagnostic controls, not qualifying streaming passes. Their counter records
are retained beside this report. No browser-local pattern benchmark was run.

## Interpretation and limits

1. On→off completion p95 improves from28.879 to16.981ms; the reversed pair is
   off16.949 versus on24.890ms. The return of the tail supports output-related
   interference, while variation between on runs shows why one passing run
   was insufficient in earlier experiments. It does not identify a specific
   task, lock, copy or network API as the cause.
2. Enqueue p95 changes with output too: on27.000/22.936ms versus off17.312/17.301ms.
   The divergence is already present before refresh enqueue. A delay solely
   between enqueue and drawing completion cannot explain it. Do not subtract
   unrelated percentiles to estimate exclusive CPU costs.
3. The existing tolerance is mean≤1.05×stock and p95≤stock+8.333ms. On1 fails;
   on4 meets this numerical SW gate. The required repeated streaming SW/HW
   qualification has not passed; no HW-sprite runs or new Rally runs occurred.
4. P4 output encompasses row composition, copying, native exclusion, network
   work and receiving-client flow control. This experiment toggles that whole
   path. It does not show that Ethernet bandwidth or the workstation's Wi-Fi is
   the culprit. Both production observers ran on the wired Pi. Its receiver
   link reported1000Mbps; that is not the P4's negotiated link rate.
5. No P01c diagnostic was added, so parser active versus runnable/blocked time,
   reply admission and individual lock costs remain unmeasured. P02 is the
   narrower next discrimination; retain P01c/d for any residual ambiguity.
6. Snapshot/swap coherence raised in P00 remains an untested, separate
   double-buffer correctness risk. This single-buffer fixture does not settle it.

## Validation and evidence

All four2400-state hashes equal
`f43eaa27074aaf6916eded49e5f97bb7eb64a79fd0ccc060f1923a9eb3ea3948`.
All refresh traces contain exactly2400 submitted/completed operations, maximum
pending1 and no recorder invalid flag. Retained NP04 result files have fresh
nonces, full counts and zero failure status. Normal keyboard readiness and SD
access passed after each run.

[comparison.json](comparison.json) contains the paired summaries and historical
baseline; `refresh.txt` contains only the four nonce-tagged trace blocks, without
private boot/network details. `P01R1.BIN` through `P01R4.BIN` are fixture result
records, not executable images or artwork. [evidence-sha256.json](evidence-sha256.json)
records their hashes. Existing `nurples-parity/analyze.py` and
`analyze_refresh_trace.py` reproduce state and timing summaries. Browser raw
headers, screenshots, full serial captures, deployment readback and controller
scripts remain in ignored `agents/p01/`.

## Preparation and duration

Asset readback initially ran slowly from the workstation. Its outstanding read
was retained and resolved on the wired Pi, where all assets were re-read and
matched; the latter took415.93seconds. This is preparation overhead, not a
controlled Wi-Fi experiment. No asset or startup mutation occurred in that
interruption. Capture was restarted before measured runs to preserve its
bounded collection lifetime.

Each run deliberately waits180seconds before collection. `*-duration.json`
records reset-to-collection/validation elapsed time, which includes this wait
and SD transfer; it is not exact game runtime. The trace's first-to-last
completion span is approximately40seconds. Plan future repetitions as3minutes
observation plus setup/retrieval, not40seconds total.

The1ms p95 contrast threshold used to select reverse-order repeats was an
agent-selected diagnostic criterion under the approved material-contrast
instruction, not an Author-specified acceptance threshold or significance test.

## End state and review boundary

Original89-byte startup was restored and read back only after exiting the
child batch and starting SD directly. SD then exited to Legacy MOS; input is
ready and neutral. P4 remains on verified r43; r44 rollback is preserved.
Mainboard VDP/EMOS are unchanged. No push. Hardware review notification is
recorded separately when delivered. P01a/b complete; P01c/d deferred, not passed.
