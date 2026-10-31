# FWBUG-013 — ExCom prompt cursor stops flashing at column zero

## Executive summary

At an EMOS command prompt in ExCom mode, the active text cursor does not flash
when it is initially on the first character position of an empty line. Typing
one character advances the cursor and starts flashing. Backspacing to the first
position stops flashing again, but using the left arrow to return to that same
position does not stop flashing.

The same screen coordinate therefore has different visible behavior depending
on how EMOS moved the cursor there. Preserve that asymmetry as the principal
diagnostic clue; do not classify this as a simple column-zero clipping defect
without evidence.

Created: 2026-09-29. Register identity: [FWBUG-013](../firmware-bugs.md#fwbug-013).
Related current audit: [AUDIT-010](AUDIT-010.md). Owning queue: `TODO.md`.

## State and evidence

F13-S01 — **Repair prepared; physical qualification and Author review pending.**
The renewed 2026-10-31 report identifies physical HDMI. Exact installed EMOSv27
polling and retained P4 source reproduce the cursor starvation under a controlled
120 Hz host clock; the repaired parser passes that negative-control regression.
The combined candidate also restores mode8 scaling. Physical regression exposes
a separate wide-clear abort; r21 writeback chunking alone fails physical checks.
R22 extends task chunking to invalidation; native build and offline review pass.
The Author withdraws bench access until further notice. The candidate remains
uninstalled; physical cursor/scaler and full qualification are pending under
the linked repair plan.

F13-S02 — The renewed Author report and ongoing repair authorization supersede
the original filing-only boundary for this bounded correction and monitored
qualification. They do not establish visual acceptance or production selection.

F13-S03 — The current Author observation is physical HDMI. Host cursor state,
browser replication and command receipts do not establish optical flashing.
Keep those evidence scopes separate through final review.

## Reported reproduction

F13-R01 [ ] Boot the currently selected EMOS and EDP combination, enter ExCom,
and reach an ordinary EMOS command prompt with an empty input line.

F13-R02 [ ] Observe the cursor at the first character position, column zero.
Reported result: the cursor is visible but does not flash.

F13-R03 [ ] Type any ordinary character. Reported result: EMOS advances the
cursor and the cursor begins flashing.

F13-R04 [ ] Press Backspace so EMOS returns the cursor to column zero. Reported
result: the cursor stops flashing.

F13-R05 [ ] Type a character again, then press the left-arrow key so EMOS moves
the cursor to column zero without deleting the character. Reported result: the
cursor continues flashing.

F13-R06 [ ] Repeat the sequence after enough flash periods to distinguish a
stopped cursor from a phase reset or delayed first toggle. Record timing and
whether the cursor is persistently shown or hidden while stopped.

## Expected behavior

F13-E01 — At an active EMOS prompt, the text cursor flashes at every valid text
position, including column zero, unless EMOS or the VDP protocol explicitly
disables cursor flashing.

F13-E02 — Backspace and cursor-left may change text contents differently, but
arriving at the same active cursor position must not accidentally select
different flash behavior.

## Investigation items

F13-01 [x] Reconcile the exact installed EMOS and EDP build identities from the
current deployment evidence before attributing the observation to production,
the audited pre-LCD baseline or another development build.

F13-02 [x] Review the official MOS/VDP cursor and text-editing contracts in
`../../agon-docs`, then consult the read-only official MOS/VDP source only where
implementation detail is material. Record exact reference tags and commits.

F13-03 [ ] Reproduce the four states—initial column zero, typed column one,
backspace to column zero and left-arrow to column zero—on Legacy and ExCom.
Observe the physical output and browser output separately where applicable.

F13-04 [ ] Capture the forward VDU traffic and applicable reverse/input events
for each transition. Determine whether EMOS sends different cursor visibility,
flash, position or redraw commands for Backspace and left-arrow paths.

F13-05 [ ] If the command streams are equivalent, trace EDP cursor state,
flash-timer state, cursor bitmap/sprite visibility, text invalidation and frame
publication at column zero. If they differ, assign the producer-side behavior
to EMOS before altering EDP rendering.

F13-06 [ ] Construct the smallest deterministic fixture that distinguishes
coordinate from transition history. Follow the current test-appliance protocol:
record entry mode, switch only if needed, settle at least one second, restore
entry mode and CLI; never modify `/autoexec.txt`.

F13-07 [ ] Complete the current bounded repair and its qualified-source record.
Retest ordinary prompt editing, all screen edges, cursor
enable/disable, cursor shape, browser replication and existing text fixtures.

## Validation gates

F13-G01 [ ] Exact EMOS/EDP identities and output surfaces are recorded.

F13-G02 [ ] A retained reproduction distinguishes initial placement,
Backspace-to-zero and arrow-to-zero, including flash timing.

F13-G03 [x] Evidence identifies whether EMOS command production, EDP command
consumption, cursor timing or output publication owns the defect.

F13-G04 [ ] The repaired cursor flashes at column zero after all three arrival
paths and retains correct behavior elsewhere.

F13-G05 [ ] Legacy behavior and existing text/cursor regressions remain intact;
no LCD, browser or other output is declared fixed without direct evidence.

## Non-goals

F13-N01 — This report does not redesign the cursor, change flash cadence, merge
Legacy and ExCom rendering, or infer that all column-zero cursor behavior is
broken.

F13-N02 — Do not mask the symptom by forcing a redraw or restarting the flash
timer on every input event until the responsible contract and actor are known.

## Renewed Author report and bounded repair — 2026-10-31

The Author confirms r19's96→3 repair and other mode changes work, but the
physical HDMI cursor does not flash until a character is typed. This authorizes
investigation/correction under the current operation procedures, superseding
the old filing-only/audit scheduling boundary. Keep EMOSv27, onboard VDP,
normal startup and exact r19 rollback unchanged; no added processor-link
integrity work or new display timing.

1. Official docs f9806bd3 record VDU23,1 show/steady/flash and text-cursor
   behavior. Read-only VDPv2.16.0 c7ac293d and MOSv3.0.2 83364093 remain clean.
   Stock processNext hides the cursor for every input command and resets idle
   accounting on pending input; Context restores it after three idle frames.
2. Exact installed EMOSv27 source archive70eee01c (557 verified inputs, patched
   base9844ecf3) shows mos_editor.c calling emos_admission_idle only for an
   empty top-level CLI line. emos_admission.c emits VDU23,0,F6 polling through
   the EMOS-owned UART at keyboard-clock cadence. A nonempty line stops polling.
   That explains typed/backspace/arrow asymmetry without a coordinate defect.
   Keep this owner/source distinct from the later EMOS development checkout.
3. P4 processNext currently treats those file/control envelopes as display
   activity: hideCursor suppresses flashing and repeated polls prevent the
   three-idle-frame restoration. Classify at existing VDU/VDU23/video dispatch
   boundaries, defer suppression until the subcommand is known, and exempt
   the existing Extender F6/F7 control envelopes. Actual drawing resets display
   idle accounting; control traffic does not. Retain ordinary hide/show,
   flash timing, graphics-cursor exclusion and processor pause behavior.
4. Reproduce with actual retained cursor/idle/processNext bodies under a
   controlled host stream/tick clock; include old-source negative control,
   120Hz control traffic, text/backspace/arrow returns, continuous drawing,
   cursor disabled/steady and wrapping tick arithmetic. Refresh only the
   necessary stale host seams before reusing HDMI lifecycle/scaler checks.
5. Prepare a clean r19-based P4 candidate with only this repair and the
   existing320×240 scaler selection restored. Compare every compiled/config
   delta, preserve full readback/rollback, install only the P4 application,
   verify actual CLI/startup and re-run targeted transitions/full qualification.
   Do not claim an optical cursor pass from command receipts or host fields;
   actual Author HDMI review remains required. No emulator is needed.

The companion mode8 observation belongs to HDMI-002: both accepted r16 and
repair r19 omit AGON_EXTENDER_HDMI_PPA_320, so320×240 is centered unscaled in
684×384. The existing reviewed scaler selects848×480 and composes all overlays
before a2× PPA scale to640×480. Restore that explicit selection, not another
scaling algorithm or a logical-mode change. Preserve r19's early renderer join
and1600µs scanout guard.

The r20 parser repair passes the old-source negative control and 120 Hz host
regression. Its physical transition checks expose a separate mode96 clear
deadline failure before any 320-mode case runs. Preserve that failure and the
completed standing recovery. [The wide-clear repair plan](HDMI-002/WIDE-CLEAR-REPAIR.md)
owns the additional SDK scheduling correction required before this combined
candidate can complete physical cursor/scaler qualification.
