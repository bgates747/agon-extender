# BUILD-001 hardware-equivalence procedure

State: proposed; execution requires explicit Author authorization. This
procedure performs no production promotion and does not modify EMOS or SD
application assets.

## Exact candidates and rollback

| Role | Identity | Application SHA-256 |
|---|---|---|
| Native candidate | `build001-bd733100-console-lcd`; source commit `bd7331005e69d298c724559c534f3fe19c9be6e6` | `a2ebff97a91c006afa9a6bb57a5343740d2687e1d910f1dcb5bf96cb03fa56dc` |
| Production rollback | `uart-excom-console-r55-b2026-09-25-02-18-28Z`; production v0.1.0 bundle `extender-installation-r02` | `a2d41a29ee9f5b42a10df9c3d724202b1db5ab561f3c3fc29f134f4f15fe54cb` |

The candidate manifest is retained at
`agents/build001/native-console-09/manifest.json`. Before execution, the Linux
operator must reverify its ELF, application, bootloader, partition table,
initial OTA data and flash-argument hashes. The operator must independently
verify the production archive and rollback bytes against
`production/bundles/extender-installation-r02/bundle.yaml`. The operator uses
the machine-local bench record for endpoints and commands; no private topology
belongs in this procedure.

## Preconditions and stopping conditions

B01-H01 [ ] The Author explicitly authorizes this exact procedure.

B01-H02 [ ] The operator confirms the current P4 identity, EMOS v0.1.19,
foreground `sdserve` v0.2.0, admitted Extender keyboard and recoverable MOS CLI.
Unknown or conflicting identity stops the run.

B01-H03 [ ] The operator confirms the immutable production rollback archive is
available and hash-correct before flashing. Missing rollback bytes stop the run.

B01-H04 [ ] The operator records start time, candidate hashes and bench state in
ignored evidence. Any flash verification failure, boot loop, panic, loss of both
admitted input and noninteractive recovery, filesystem corruption indication or
unexplained reset stops candidate testing and invokes the recorded rollback.

## Execution order

B01-H05 [ ] At a verified MOS prompt, clear the Legacy screen with `VDU 12` so
an older completion cue cannot be mistaken for this run's result. The Linux
operator then flashes only the P4 candidate using its generated flash arguments
and verifies every written region. EMOS, the eZ80 flash and SD files remain
unchanged.

B01-H06 [ ] After ordinary boot, the operator records the candidate's exact
serial identity and confirms stable Legacy output, ExCom activation/return and
native LCD initialization. The Author compares the known mode0 asymmetric
color/edge fixture on Legacy and LCD; all colors, four source edges and the
accepted LCD mapping must remain correct.

B01-H07 [ ] The Author exercises admitted Extender keyboard input at the EMOS
CLI and confirms ordinary Legacy/ExCom return. The operator performs bounded
read-only checks of the SD service, browser status endpoint and one browser
frame while the LCD sink remains active. Browser disconnected and connected
observations remain separate; no performance equivalence is inferred.

B01-H08 [ ] Run a mode20 static-grid control only after `/autoexec.txt` selects
mode20 before fixture launch. The automated fixture must not switch modes. The
Author must observe A1 through H6 in order, all asymmetric edges, 64-pixel
pillarboxes and 48-pixel letterboxes. One bounded raw Ethernet snapshot must
agree with the LCD; its collection then disconnects. This checks geometry and
presentation but does not reproduce the asset-loaded mode-switch failure.

B01-H09 [ ] After every automated hardware pass has terminated, hand control to
the Author for manual execution of Nurples and any other real game that changes
mode after loading significant VDP-buffer assets. Record LCD layout,
keyboard/Escape behavior, HTTP availability and any allocation/fallback report
separately. These manual cases preserve the known late-switch failure for its
own resolution outside this audit; they do not authorize an automated fixture
to switch modes or an opportunistic fix. A changed result is evidence to
investigate, not automatic acceptance or failure attribution.

B01-H10 [ ] Exercise the accepted ordinary boot smoke and clean recovery path.
If all required checks pass, leave the final Legacy status visible and invoke
the established spoken hardware attention cue. On failure, leave the failure
identity visible and invoke the failure cue only when the admitted recovery path
can do so without overwriting that text. The runner, not an agent polling loop,
owns progress, durable duration and terminal notification where automation is
available.

B01-H11 [ ] Restore the selected production P4 firmware after evidence capture
unless the Author explicitly directs the candidate to remain temporarily for
continued BUILD-001 review. Independently verify restored identity. This is
rollback, not production promotion of the candidate.

## Mode-selection disposition

B01-HQ01 [x] The Author declined an exception to the repository mode-selection
rule. Automated fixtures select their mode only through `/autoexec.txt`. The
asset-loaded switch failure belongs to real applications such as Nurples and is
deferred until the end of the automated passes for manual Author testing. The
manual result remains a separate known-defect case requiring later resolution
outside this audit.
