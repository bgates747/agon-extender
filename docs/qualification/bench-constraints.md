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
