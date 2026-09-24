# P4 mode-startup lifetime investigation

## Executive summary

Author authorized contract freeze and immediate execution on 2026-09-20.
Investigate two retained P4 restarts during repeated mode9 startup after Copper
scenes. Neither the exact failing command nor root cause is known. PORT-003 owns
any implementation correction; QUAL-004 owns the affected qualification gap.
This bounded tranche stays within AUDIT-007 rather than creating another audit.

## Frozen work contract

**AUDIT-007-M01** [x] Preserve current state and read official mode/Copper/sprite
contracts. Trace EDP mode selection, worker shutdown, queued draws, native
controller teardown and resource ownership against pinned stock sources. Record
historical versus current differences before attempting reproduction.

**AUDIT-007-M02** [x] Verify bench identity/readiness and preserve startup and
rollback artifacts before mutation. Use existing admitted EMOS/P4 control and
SD paths. Capture P4 serial before replaying the retained mode9/Copper setup
sequence; record reset cause/boot identity and exact last completed step. Start
on the installed candidate. At most two unexplained restarts before stopping
replay to inspect evidence; do not repeat blind resets. Baseline target: ten
completed repetitions if no failure. Label altered sequences explicitly.

**AUDIT-007-M03** [ ] If source/runtime evidence identifies a local defect,
implement the smallest correction preserving upstream drawing semantics. Add
necessary regression checks and build under a recorded identity, preserve and
verify actual firmware before authorized deployment. No upstream bug fixes,
browser optimization, game work or drawing budgets. If no cause is established,
retain the bounded result rather than inventing a fix or expanding indefinitely.

**AUDIT-007-M04** [ ] Repeat the reproducer after any fix for twenty iterations;
retain complete serial evidence and startup identities. Where diagnostic firmware
and retained controls permit, finish mode136 displayed/drawing-page comparisons
against mainboard reference. Record any dependency preventing those controls
instead of declaring full graphics qualification. Fixtures select modes only in
startup as required by bench constraints; no hidden fixture mode switching.

**AUDIT-007-M05** [x] Restore original startup and temporary firmware unless a
verified correction is deliberately left for Author review. Release input,
serial readers and SD service; verify prompt/input. Save findings, exact scope,
remaining gaps and restoration receipt. No emulator notification requested.

## Execution boundaries

The Author's instruction authorizes this bounded investigation and necessary
bench reproduction/deployment, not unrelated physical changes. Keep existing
uncommitted browser/UI work intact. No EMOS/mainboard firmware change unless a
necessary diagnostic requires it and its rollback is preserved. Prefer existing
fixtures and firmware. Version identities follow the standing preapproval and
project policy. Exploratory dirty builds cannot establish qualified status.
Preserve informative failures and stop on unsafe state or missing recovery.

## Evidence basis

[Original observations](../QUAL-004/RESULTS.md#p4-restart-between-copper-scenes),
[first source pass](FINDINGS.md), and [coverage gaps](../QUAL-004/COVERAGE.md).
Mode9 was reselected during startup; do not describe this as a proven transition
between two different resolutions or a proven mode-command crash.

## Execution result

Reproduced and diagnosed; [results](mode-lifetime/RESULTS.md). M03/M04 remain
blocked on the upstream-correction scope decision, not on a speculative local
fix. Bench restored; Author then requested functional-state confirmation after
app safety notices. No further bench work.

## Author disposition — 2026-09-20

[FWBUG-001](../../firmware-bugs.md#fwbug-001--palette-deletion-advances-an-erased-map-iterator)
records the finding. Author reports mainboard manifestation; physical mainboard
reproduction was not performed by this investigation. Upstream and Extender
patching are deferred until more credits. M03/M04 are parked, not awaiting
immediate execution; the original and reproduced evidence remain intact.
