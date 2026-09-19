# BENCH-005 — Keyboard-to-visible-response investigation

## Executive summary

**The web client's explicit 30 fps request cap contributes materially to visible latency.**
A bespoke 320×240 app measured 76.1 ms median from host injection start to browser
display submission in the idle-character baseline, versus 42.1 ms with only that
client delay removed: approximately **45% lower**. This is a small controlled
sample, not proof of physical keyboard latency, monitor latency or sustained
60 fps gameplay. The installed UI and firmware were not modified.

**The proposed idle-screen explanation was not supported.** Busy-screen medians
were slightly worse (79–80 ms) than idle (71–76 ms). Blocking MOS input, polled
character state and keymap results were close; no large character-path penalty
was demonstrated. The original interactive console editor itself was not timed.

All **120 ExCom taps** produced the expected marker. The attempted Legacy app
acknowledgement control could not run: EMOS returned 27, provider not found. The
fixture's return 2 explains the Author's "Internal error" observation; it was not
an SD-service failure. Therefore there is **no paired Legacy/ExCom application
receipt comparison**, and no legitimate numerical split between MOS input,
rendering and transport delays in these results.

First avenues: (1) consider mode-dependent browser pacing, with a matched
repeat before any production change; (2) add an explicitly qualified application
receipt channel for both routes if further input-path isolation is needed;
(3) measure actual MOS console editing separately. Do not optimize the keyboard
path solely on these end-to-end numbers.

## Measured ExCom results

Milliseconds; nearest-rank p95. Worst median first among the baseline conditions.
"Presented" means the instrumented client returned from its WebGL submission,
not monitor light output. HTTP column includes host journal/request overhead and
is **not** application acknowledgement. Each condition has 20 taps.

| Input / screen / observer | n | HTTP median | Decoded median | Presented median | Presented p95 | Presented max | Max clock alignment ± bound |
|---|---:|---:|---:|---:|---:|---:|---:|
| map / busy / 30 fps cap | 20 | 24.3 | 68.7 | 80.4 | 95.8 | 99.5 | 0.9 |
| char / busy / 30 fps cap | 20 | 29.2 | 72.4 | 79.1 | 94.2 | 95.3 | 2.8 |
| char / idle / 30 fps cap | 20 | 26.5 | 64.3 | 76.1 | 84.8 | 95.9 | 2.3 |
| block / idle / 30 fps cap | 20 | 23.9 | 62.4 | 73.2 | 87.2 | 96.3 | 1.8 |
| map / idle / 30 fps cap | 20 | 25.7 | 65.5 | 71.0 | 84.9 | 85.4 | 2.0 |
| char / idle / uncapped control | 20 | 27.2 | 36.2 | 42.1 | 47.0 | 50.7 | 2.4 |

## Method and provenance

1. [Frozen contract](../BENCH-005.md), [fixture source](fixture/src/main.c),
   [observer](observe.py), and attempted [Legacy control](legacy.py).
2. Build `make -C docs/tasks/BENCH-005/fixture`. Run `keylat.bin` through MOS with
   `RUN . char idle`, `map idle`, `char busy`, `map busy`, or `block idle`.
   `char` polls MOS event count/down/ASCII; it is not the blocking API. `block`
   uses `getch()`. `map` tests A's rising held-state edge. Escape exits.
3. Mode 8 selected for both routes by temporary autoexec before the test. Fixture
   does not set mode. Busy activity changes a separate rectangle at MOS-clock
   transitions; it is a light synthetic graphics load, not Rally or Aginvadors.
4. Every A press flips a 96×96 patch black/white and increments a displayed
   counter. Trials alternate expected patch values, so an unchanged old frame
   cannot count as a response. Hold until response, then release; no timed
   short taps, no overlap and no repeat intended. Intertrial spacing varies.
5. Chromium headless, installed RLE2-capable client, instrumented only in host
   response interception. Timestamps at decoded-frame acceptance and WebGL
   submission. Instrumentation reads one decoded pixel; no screenshot/OCR in
   the measurement loop. Software renderer is a host condition, not the Author's
   actual browser/monitor. Current client source is preserved in evidence.
6. Inject through existing host keyboard API; it intentionally rejects browser
   Origin requests. Align browser monotonic time to bracketed host timestamps
   before every tap, retaining half-roundtrip bounds. These are alignment bounds,
   not the total accuracy of network/OS scheduling. Host injection includes
   durable request journaling. Physical keyboard USB polling is bypassed.
7. Installed `app.js` has `lastCreditAt+1000/30` regardless of resolution.
   The control intercept changes only that delay to zero; close the observer to
   remove it. The 30 fps baseline uses fixture r01; uncapped uses r03, whose
   changes only affect the unused Legacy telemetry branch. Render/input code is
   otherwise identical. Build hashes are in deployment manifests.
8. P4 retained fullscreen r02; mainboard firmware unchanged. No hardware flash.
   These results do not retroactively establish the FPS of the Author's gameplay.

## Raw evidence and reproduction

[30 fps trials](evidence/excom-30fps.json), [uncapped trials](evidence/excom-uncapped.json),
[Legacy admission status](evidence/legacy-telemetry-open.txt), and deployment
manifests alongside this report. Private journals/addresses/control logs remain
in ignored `agents/bench005`. Reproduction requires the current bench's admitted
CLI helpers and a fresh output directory; inspect startup before invoking.

Use the project `.venv/bin/python observe.py --url <P4> --output <new-directory>`
from repository root (full task-relative script path), with optional `--uncapped`.
Scripts depend on existing local `agents/qual004/common.py` bench helpers and
Playwright Chromium. They are research harnesses, not a portable product CLI.

The raw tick count is never converted using CLOCKS_PER_SEC=100. Latency authority
is host/browser monotonic time. Frame statistics do not claim render-completion
or physical scanout timing.

## Legacy failure and limitations

The installed EMOS could not resolve `ext/telemetry`; open returned 27. A diagnostic
revision wrote that status to SD. P4 `/telemetry/latest` remained received=0.
No acknowledgement sample was accepted. The fixture originally returned 2 without
explanation, which MOS maps to "Internal error"; the Author saw that before
sdserve. This was poor diagnostic reporting in the new fixture, not evidence
that sdserve or the board had failed. No inference of pure input latency follows
from HTTP event admission or queue drain.

A matched cross-route app-receipt channel remains follow-up instrumentation.
Firmware was deliberately left intact for this bounded investigation, as allowed
by K03's unavailable-measurement branch. No per-stage latency attribution, USB
polling measurement, exhaustive network-tail study, or physical display latency
is claimed. The uncapped control is sequential, not randomized/counterbalanced;
a larger paired repeat should precede an optimization decision.

## Text readback

Author requested screen visibility during this work. `textread` uses stock
VDU 23,0,&83 per cell, checks the response flag with a bounded timeout, captures
before file output, and saves dimensions, cursor and recognized rows to SD.
It neither changes mode nor clears the screen. The helper's own LOAD/RUN commands
still appear on the screen. Recognition depends on current font and colour;
unknown characters are marked `?`. It is not a true backing-store dump and cannot
observe a hung program which cannot launch it. No claim of concurrent universal
screen access is made.

Build `make -C docs/tasks/BENCH-005/textread`; at a prompt:
`LOAD /test/bench005/textread.bin` then `RUN . /test/bench005/screen.txt`.
Retrieve via the existing SD service. Readback validation and restoration receipt
are recorded below on completion.

### Text-readback validation result

Both physical routes returned 1,200 cell replies with **zero timeouts** and the
expected marker text. [Legacy text](evidence/legacy-screen.txt) includes the actual
`Internal error` line; [ExCom text](evidence/excom-screen.txt) includes its marker.
Each had exactly 69 unknowns: 30 right-edge cells plus 40 bottom cells minus the
shared corner. Official VDP `video/context/fonts.h::getScreenChar(Point)` uses
`p.X >= canvasW-fontWidth || p.Y >= canvasH-fontHeight`, excluding those boundary
cells. This matches the observed geometry; no upstream behavior was changed.
The header cursor is the **cached MOS cursor report**, not a fresh cursor query,
and can be stale. Interior readback passed; full-grid and current-cursor coverage
are explicitly incomplete. Non-ASCII/control glyphs and graphics remain outside
this smoke's validation.

## Closeout

Temporary startup restored and independently read back. Observers closed, injected
keys released, Legacy CLI restored; firmware never changed. Test binaries remain
under `/test/bench005`. Hardware voice receipt is recorded in `notification.json`.
No production frame-rate policy change has been deployed. Follow-up app receipt
instrumentation and MOS-console latency measurement remain open research work,
not falsely passed tests.
