# Host controller viewer

The Linux viewer displays an F310 in XInput mode and records its native input
without sending anything to P4 or Agon. It is the first host-only tranche of
[INPUT-001](../tasks/INPUT-001.md); The Author accepted the host viewer and recorded full control exercise and
physical reconnect. Network and target delivery are not implemented.

## Run on the desktop host

Use the staged review directory recorded in the ignored local task receipt, or
run from a checkout with its project Python environment and Tk support:

```bash
.venv/bin/python scripts/controller_view.py --record-dir agents/input001/captures
```

No pip dependencies are needed. Python must provide Tkinter; Linux evdev device
read permission and the host's normal graphical session are required. The reader
currently supports Linux 64-bit x86/ARM input-event layouts. It opens the device
read-only, never grabs exclusive ownership, changes no driver calibration and
writes no rumble commands. Existing gamepad applications can continue reading
it, but the operator should avoid running a game that reacts to review input.

The observer searches stable joystick links and verifies vendor/product and
required axes/buttons. It refuses ambiguous multiple F310s. For explicit
selection, use `--device /dev/input/by-id/DEVICE-event-joystick` from that host's
current enumeration; do not hard-code an event number. DirectInput mode waits
with an XInput-mode explanation. Replugging reconnects automatically; each
connection gets a new session, fresh counters and no inherited calibration.

## Read and review

1. Both stick crosshairs show native-range movement. Trigger bars are separate;
   the D-pad and all eleven XInput buttons have labelled indicators. Button
   bracket counts are observed press edges, not redraw counts. The last four
   transitions appear at the bottom; a fast press/release can count even when
   it occurs between screen updates. A button held when observation starts is
   shown held but is not counted as a new press.
2. The table shows native values, proposed eight-bit values, preview centre,
   observed minimum/maximum, distinct values and smallest step/GCD. A centred
   stick previews near 128; a released trigger previews 0. No application dead
   zone, inversion or response curve is imposed. Eight-bit preview is a local
   comparison, not an approved wire/API decision.
3. Release both sticks and select **Measure rest (2 s)** to capture their rest
   range and median. This changes the local preview centre only. It is not a
   persistent controller setting. The window samples the latest observed state;
   it does not create new USB measurements. A centre beyond the middle half of
   declared travel is rejected. Inspect the displayed spread before trusting a
   measurement. Disconnect or an input gap cancels the rest window.
4. Select **Clear observations**, then move each stick slowly along each axis
   and around its full travel. Squeeze each trigger slowly, then both together.
   Press and release each button, click both sticks and try diagonal D-pad
   combinations. Check actual directions and labels. This requires physical
   input; stationary detection does not prove button mapping or travel.
5. Report rate counts *changed evdev reports* during the last second, capped by
   a retained 512-report window. Idle controls can produce zero reports without
   disconnection. Last-change age is not device heartbeat age, USB polling rate
   or end-to-end input latency. Smallest steps/GCD describe only this session's
   delivered values; driver filtering, movement speed and incomplete traversal
   prevent calling them proven sensor resolution.
6. On unplug, indicators and numeric values clear; the window waits for replug.
   On return, held controls are shown as a new baseline and counters restart.
   The Author's recording verifies a physical unplug/replug with resumed input.
   Disconnect with a button held is a separate, unperformed physical case.
7. Escape or **Close** exits normally. Controller buttons never exit or invoke
   another program. The viewer restores no game or benchmark because it starts
   none. There are no MOS mode changes, firmware changes or startup edits.

## Recording and replay checks

**Start recording** creates a new timestamped JSONL file under `--record-dir`.
**Stop recording** or normal window close flushes and fsyncs a clean end marker.
The displayed path identifies the file. Each stream preserves metadata,
connection/session baselines, raw events and their kernel monotonic timestamps,
local receive times, committed state frames, rest measurements and disconnects.
Starting during a partial report preserves pending state for later replay.
Files are created exclusively and existing captures are never overwritten.
Errors are displayed; a failed recording is not a complete capture.

The file timestamps use Linux CLOCK_MONOTONIC nanoseconds on the capture host;
there is no cross-machine clock synchronization or one-way LAN latency claim.
The initial attach/resync state is a driver-query baseline, not an assertion of
simultaneous hardware sampling of every control. Later frames commit at
SYN_REPORT. SYN_DROPPED causes discard through the next report and a fresh
state query; transitions across that gap are unknown and the gap count rises.
Counts do not invent lost taps. JSONL is a provisional local capture format,
not the network or EMOS wire protocol.

For a finite capture without a window:

```bash
.venv/bin/python scripts/controller_view.py --headless --seconds 10 \
  --record agents/input001/captures/finite.jsonl
```

The JSON summary says whether a controller connected. A completed observation
with no connected controller is not an input pass. Interrupted headless captures
close cleanly on Ctrl-C; abrupt process/power failure can leave an incomplete
file. Buffered writes are flushed at least on a subsequent record after one
second and on clean close; no crash-proof or power-loss durability is promised.

Replay and independently compare committed frames to the raw event stream:

```bash
.venv/bin/python scripts/controller_view.py \
  --validate agents/input001/captures/finite.jsonl
```

Validation opens no device. Missing end markers, frame disagreement or session
mismatches fail. A complete zero-event recording proves enumeration/clean capture
only; repeatable nontrivial input recording still needs movement. The first
tranche provides deterministic semantic replay/checking, not a timed LAN sender.

## Implementation and evidence

1. [Input observer](../../scripts/controller_input.py): native state, normalized
   preview, statistics, session lifecycle, recording and replay checks.
2. [Viewer/CLI](../../scripts/controller_view.py): Tk display and bounded headless
   observation. Linux evdev was selected over existing fsim SDL for raw ranges,
   kernel event times, overflow visibility and per-event recording without a new
   package. SDL remains useful prior art for future wider device mappings; this
   choice neither replaces fsim's input loop nor establishes network architecture.
3. [Semantic tests](../../tests/test_controller_input.py) cover coherent reports,
   short taps/repeats, trigger separation, initial-held state, overflow/resync,
   quantization, rest measurements, reconnect, ambiguous selection, fd cleanup,
   capture round trips, mid-report start, corruption and incomplete files.
4. Linux kernel [event semantics](https://docs.kernel.org/input/event-codes.html)
   and [gamepad specification](https://docs.kernel.org/input/gamepad.html) own the
   report/overflow and control-code conventions. The F310 XInput trigger layout
   is checked through its actual evdev capabilities rather than guessed from
   generic gamepad trigger names.
5. Local and Oryx tests pass; live enumeration and virtual-display checks pass.
   The [Author review](../tasks/INPUT-001/HOST-REVIEW-2026-10-24.md) records exact
   replay of full six-axis travel, all eleven buttons, D-pad and physical
   reconnect. Rest calibration and held-button unplug remain physically
   unreviewed. Machine-local receipts, screenshots and captures stay in ignored
   evidence; no end-to-end or production release claim follows.
