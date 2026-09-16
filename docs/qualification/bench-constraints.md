# Active bench constraints

This document records temporary constraints that affect more than one tracked
test task. It is not product architecture and does not identify private bench
topology or a particular specimen. Machine-specific observations remain in
`HARDWARE.local.md`.

## BC-001 — No interactive hardware keyboard input

1. **Status:** Active.
2. **Reported:** 2026-08-28 by the Author.
3. **Condition:** The current Agon bench machine's USB/PS/2 keyboard-input path
   is inoperative after a separate direct-eZ80 VGA experiment. The exact failed
   component, damage boundary, and repairability have not been diagnosed. The
   experiment reportedly produced direct VGA output successfully; that result
   is outside this project's qualification scope.
4. **Execution constraint:** Until the Author explicitly clears BC-001, every
   eZ80 text fixture must be a noninteractive cold-boot path that can be
   launched through the Agon SD card's root `/autoexec.txt`. A fixture may not
   require typed setup, mode selection, confirmation, command entry, or
   recovery.
5. **Fixture requirements:** Each affected fixture must define its executable,
   exact `/autoexec.txt` invocation, required files, startup ordering or delay,
   deterministic terminal state, and non-keyboard evidence channel before a
   bench run. Prefer visible browser output plus machine-readable logs or
   captures where available.
6. **Scope:** This currently constrains PORT-008's visible-command fixture,
   PORT-005 input work, and any QUAL-001/QUAL-002 or later eZ80 fixture that
   would otherwise assume an interactive keyboard.
7. **Removal condition:** The Author reports the hardware path repaired or
   replaced and a separately recorded smoke test proves ordinary key press and
   release packets reach MOS/EMOS. Removing BC-001 does not itself qualify the
   repaired circuit for broader compatibility.

## Browser-keyboard qualification while BC-001 remains active

The Author selected browser-focused input as the next replacement path on
2026-09-08. Autoexec still launches and configures the identified test without
physical-keyboard setup. That test may then request browser keystrokes after
its explicit readiness cue; the path under test must not be assumed available
for installation, recovery or earlier setup. Keep the physical-keyboard fault
record and require Author-observed successful input qualification before
relaxing BC-001 for fixtures that use the browser path.

On 2026-09-09 the Author selected direct USB keyboard input through P4 as
another replacement path, owned by PORT-015. The same qualification exception
applies: autoexec performs setup, then the test may request USB keystrokes
after readiness. Do not require this unqualified keyboard for installation or
recovery. Mainboard VGA may show the test and ordinary EMOS prompt; browser
video is not required. BC-001 remains active until the replacement smoke and
Author confirmation satisfy its removal condition.

### Accepted native USB use — 2026-09-09

The Author has now accepted native P4 USB input at the ordinary EMOS CLI and
in gameplay, with autoexec selecting `EMOS KEYINPUT extender`. That demonstrated
path may be used for ordinary interactive application testing. This does not
restore the broken mainboard keyboard interface or establish every source
switch/recovery case. Installation and recovery procedures must still provide
their established noninteractive path when the required P4/EMOS candidate or
input admission is unavailable; BC-001 must not be read as banning use of the
now-demonstrated replacement keyboard.

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
