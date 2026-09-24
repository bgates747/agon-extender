# Active bench constraints

This document records temporary constraints that affect more than one tracked
test task. It is not product architecture and does not identify private bench
topology or a particular specimen. Machine-specific observations remain in
`HARDWARE.local.md`.

## BC-001 — Mainboard keyboard unavailable; admitted P4 input permitted

**Status:** The mainboard USB/PS/2 keyboard path remains unavailable. The exact
failed component and repairability have not been established. This constraint
does not prohibit the accepted P4 replacement input path.

1. **Ordinary interaction:** Native P4 USB input is accepted at the EMOS CLI and
   in gameplay, with startup selecting `EMOS KEYINPUT extender`. It may be used
   for ordinary interactive application testing. Browser and agent input use
   that same prior EMOS admission, under the [keyboard guide](../remote-keyboard.md).
   A remote agent cannot type its own admission command over a disabled path.
2. **Installation and recovery:** Provide a noninteractive path whenever the
   required P4 firmware, EMOS firmware or input admission is unavailable. Do
   not make the interface under test a prerequisite for its own installation,
   first admission or recovery. Prepared `/autoexec.txt` can perform setup before
   an explicit readiness cue requests keystrokes.
3. **Fixture preparation:** Record the executable, exact startup invocation,
   files, ordering, terminal state and evidence channel. Select the video mode
   only in `/autoexec.txt`, before the fixture; use `VDU 22 n`. The fixture
   itself must not switch modes. A test of a new input candidate must not assume
   that candidate already provides reliable setup or recovery input.
4. **Acceptance boundary:** Working P4 input does not repair the mainboard port
   or qualify every source-switch/fault-recovery case. Retained native-input
   acceptance is in [PORT-015](../tasks/PORT-015.md); further platform and browser
   limits remain in the keyboard guide. Do not broaden those recorded passes.
5. **Clearing the original fault:** The Author must report the mainboard path
   repaired and a separate smoke must demonstrate ordinary press/release
   delivery before instructions may depend on that path again.

## Capture completion for subsequent UART procedures

Author-approved on 2026-09-08: subsequent paired UART capture procedures end
as soon as the analyzer has completed its required acquisition and the host
has observed at least five clean seconds after the P4's final PASS. The host
continues checking for late errors, extra traffic and restarts during that
interval; any such event fails the run. Retain a bounded overall timeout for
missing progress, rather than making successful runs wait for that timeout.
Agon's own PASS and final MOS prompt remain separate operator observations.

Apply this convention when preparing the next procedure revision. Previously
frozen procedures and evidence, including uart-flow-probe-r02's 90-second
serial window, retain their original definitions.

## Production/test application separation — 2026-09-16

Author directs Nurples experiments to `/test/nurples` and Rally experiments to
`/test/arcade/rally`, with independent runtime assets. Keep production programs
under `/mystuff` unchanged during qualification and performance work. The one-time
BENCH-002 repair consolidation is explicitly authorized; production Nurples uses
normal single-vblank pacing, and its 30fps review build belongs only under `/test`.
Do not infer deployment targets from an old script's defaults. Existing historical
fixture paths remain evidence; migrate deliberately, without deleting unrelated
fixtures or rewriting frozen run records.

## Capture-suite failure handling — 2026-09-20

Apply the Author-approved [capture failure protocol](capture-failure-protocol.md):
mark failures, recover and continue independent cases, then run marked cases
without capture instrumentation on the affected endpoint. This supersedes older
capture stop/retry rules; unrecoverable readiness still blocks further execution.
