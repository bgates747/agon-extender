# Paired graphics hardware observations

Observations for [QUAL-003](../../../../docs/tasks/QUAL-003.md), following the
[r01 test sheet](paired-graphics-probe-r01.md). The Author accepted the completed
EDP graphics-suite visual review as PASS on 2026-09-10. The chronological reports
below are operator observations, not automated pixel/timing measurements.

## Accepted result — 2026-09-10

**PASS: Extender EDP graphics-suite visual review.** The Author reports EDP
remained steady throughout the suite and everything else passed. The notable
sprite artifacts occurred on **mainboard VDP**, on BSP-28, BSP-29 and BSP-30;
they are reference-display observations, not Extender suite-rendering failures.
Their exact cause is unconfirmed. Stock documentation describes VGA scanline
overload as a possible source of jitter under hardware-sprite load.

This acceptance covers the manually launched visual suite with the identified
candidate pair. The automatic-start diagnostic remains a separate unresolved
startup issue, and apparent relative rendering speed remains unmeasured. No
firmware lifecycle status changes here. The Wolf3D failure reported below is
outside this passing suite scope and remains an unresolved EDP compatibility
issue; the pass does not establish general game compatibility.

## 2026-09-10 — Manual launch and initial visuals

1. The Author reports the graphics look good so far. Exact pages/stages and
   complete suite coverage have not been reported.
2. Manual loading and running of the programs works better than autoexec
   launch. The browser showed an SD-related complaint in the automatic path,
   while EMOS could load the files manually. Exact text and timing are pending.
3. Installed pair from the preceding receipts: EMOS
   `agon-emos-v0.1.12-b2026-09-10-03-50-35Z`, P4
   `uart-excom-console-r04-b2026-09-10-03-50-36Z`, and fixture
   `paired-graphics-probe-r01-b2026-09-10-03-50-35Z`. No new binary readback
   accompanied this report.
4. Manual LOAD/RUN differs from the r01 automatic-start sequence. Preserve that
   distinction; these observations do not qualify automatic startup. The
   investigation and next startup handover are tracked under QUAL-003-I001.

Source inspection identifies a diagnostic ambiguity: EMOS renders a generic
program return value 1 as an SD-access error, while these fixtures can return
1 for a mode or route failure. That is a possible explanation for the wording,
not a finding that establishes this incident's cause.

## 2026-09-10 — Sprite pages 28 and 29

1. While continuing the review, the Author reports shaking and tearing on
   mainboard VDP for pages 28 and 29 of the sprite suite; Extender EDP output
   appears steady. This records the observed difference without assigning its
   cause or declaring either renderer fully correct.
2. The fixture identifies page 28 as hardware paint-mode exceptions: SET/XOR
   and other requested paint modes, software demotion and hardware reselection.
   Page 29 compares transformed frame lists on software and hardware sprites,
   including fixed/fitted frames and independent RGBA8888 controls.
3. Exact affected sub-stages, whether artifacts persist during the keypress
   pause, repeatability and video recordings are not yet recorded. Review is
   still in progress; no firmware or running test was changed in response.
4. EDP is observed through the current five-fps browser presentation, while
   mainboard VDP drives VGA. Their different presentation paths must be
   considered when investigating a temporal artifact; browser steadiness alone
   does not isolate the cause.

## 2026-09-10 — BSP-30 bounded sprite population

The Author also reports abnormal mainboard VDP output on BSP-30. The precise
artifact and affected sub-stages are not yet described; do not automatically
classify this as the same shaking/tearing reported for pages 28 and 29. EDP's
behavior on BSP-30 has not been separately reported.

This page steps 1, 2, 4, 8 and 16 active sprites across software/hardware and
RGBA2222/RGBA8888 cases, then changes scanline alignment and exercises larger
or distinct frames. The population/backend/format at the first abnormal stage
is not yet known. Review continues with the deployed candidates unchanged.

## 2026-09-10 — Visual review completed

The Author reports everything else passed and EDP remained steady throughout
the review. This includes the previously unspecified EDP behavior on BSP-30.
Retain the mainboard abnormalities on BSP-28–30 and the automatic-start issue
as exceptions; no further visual defect was reported. This is Author-observed
visual acceptance, not an automated pixel comparison or a new flash readback.

Some EDP tests appeared slower to finish rendering than mainboard VDP. The
Author explicitly leaves open whether this is slower rendering or the lower
browser presentation rate. No measured performance difference is established.
The Author requests a proposal for unattended mainboard-then-EDP suite timing
with results durably saved to a file. No benchmark has been run.

## 2026-09-10 — Additional game observations

The Author reports Wolf3D behaved incorrectly with EDP: text appeared out of
place and the game became apparently unplayable. The Author clarified the
initial description of a crash: Escape/quit still worked, the game exited
cleanly to EMOS, and operation was normal afterward. **No crash is confirmed.**
Nurples appeared fine. Exact game binary identities and reproduction steps are
not established, and no independent reproduction was performed. Preserve this
as an unresolved EDP/application compatibility issue, separate from the passing
graphics suite and mainboard-only sprite artifacts.

The Author additionally confirms the **same Wolf3D build operates properly on
mainboard VDP**. This establishes a same-binary comparison and directs follow-up
to the EDP compatibility path. Do not attribute the difference to a different
game build or describe Wolf3D itself as generally broken. The exact artifact
hash and failing EDP behavior still need identification.

The Author suggests some VDP calls may be incompletely implemented. This is a
diagnostic hypothesis, not an identified missing command or confirmed cause.
Task QUAL-003-I003 tracks follow-up.
