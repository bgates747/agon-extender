# PORT-008 — Original DevKit hardware control

## Executive summary

**Current disposition:** the Author parked the comparison and requested the last
working pre-PC DevKit pair. Restoration is now complete: exact September 30 P4
segments and the entire EMOS ROM independently verify, normal startup is restored,
and real remote commands/SD service work. No wiring or mainboard VDP change.
The Author clarifies that restoration prepares the original DH parallel
comparison; DR01–DR04 record the completed prerequisite. Resolve the rebuilt
harness READY bias before another historical receiver installation. Production selection is unchanged. No further bench test is running.

### Original parallel comparison contract

Author has connected the original DevKit and explicitly confirms the complete
parallel harness has remained in place. Preserve that assembly. Compare one
1,024-byte slow-profile historical receiver record with the failed P4-PC
40 MHz control. Keep current Agon EMOS and mainboard VDP unchanged. Current
EMOS requires reciprocal boot release, so first prepare a current DevKit EDP
composition for setup and recovery; the older installed EDP cannot provide it.
No missing-wire diagnosis is established by the outdated r03 drawing.

DH01 [x] — Freeze contract and prepare current EDP for DevKit pin assignments,
with the existing reciprocal release implementation and browser/input services.
Allow this explicit nonrelease composition through the maintained builder; no
new protocol, diagnostic, GPIO assignment or resident EMOS change. Verify build
selection gates, native linked composition and exact installation segments.
Identify the physical DevKit before installation and record its identity locally.

DH02 [ ] — Install/read back that DevKit EDP, await HTTP before Agon reset, and
prove input admission and original SD startup through the foreground listener.
Verify the already-deployed historical sender and stage its reviewed temporary
startup. Preserve original startup and exact DevKit recovery image. Do not
substitute the P4-PC recovery image or require unavailable input to bootstrap.

DH03 [ ] — Rebuild the source-faithful historical receiver for the original
DevKit GPIO constants, retaining the 40 MHz control's SDK/compiler/configuration.
Prove only GPIO mappings/build identity differ from that control. Flash/read back
all segments and run exactly one 1,024-byte record at 24 NOPs. Retain USB verdict
and a source capture only if the analyzer is attached to the DevKit harness.
The Author confirms it remains on the disconnected P4-PC; use the receiver USB
verdict for this comparison, with no DevKit waveform claim.
Do not infer receiver-pad waveforms from source observations. No retries/sweep.

DH04 [ ] — Restore/read back the new current DevKit EDP and verify original
startup, actual remote command delivery and neutral input. Record the comparison
with the P4-PC controls and stop. This changes board, harness and P4 pin map
jointly, so neither a pass nor failure identifies an individual physical cause.
No production selection, reverse-transfer or ordinary ExExt enablement follows.

## Source and scope

The [40 MHz control](FLASH40-CONTROL-R01.md) owns the unchanged receiver
configuration/canary and deployed sender identity. The [historical comparison](DEVKIT-CONTROL-R01.md)
records the Author-approved original raw-GPIO sender exception; this repeat is
confined to that historical experiment, not a supported EMOS bypass. Official
read-only `agon-docs/docs/GPIO.md`, current `vdp/build/boards/p4-devkit.json`,
EMOS `src/emos_parallel_boot.c` and P4 `transport/console_hardware.inc` establish
that Agon GPIO assignments stay fixed while P4 assignments are board inputs.
Existing native payload/coordinator objects take their pins from those inputs.
The setup/recovery build adds no physical payload invocation; the historical
standalone receiver remains the measured endpoint. Keep private identities,
URLs, installed receipts and runtime artifacts in ignored local evidence.

## Setup admission checkpoint

Current DevKit EDP builds, validates, flashes and passes independent segment
verification. One Agon reset does not admit input. Author reports `KEYINPUT FAIL:
UART or keyboard service busy`, autoexec line2 and `EMOS dispatcher busy`.
This generic refusal can represent missing reciprocal boot permission; it is not
proof of a competing application. No SD startup mutation or payload invocation.
DH02 remains incomplete. The attempted passive boot capture observed the
disconnected P4-PC: the Author confirms no analyzer is attached to the DevKit.
Discarded that invalid capture; it establishes nothing about DevKit signaling.
Do not repeat capture or request probe movement. No payload has been armed.

The prepared historical sender can instead be staged through a host-mounted
Agon SD card, preserving and verifying the original startup first. This avoids
requiring working Extender keyboard input to launch the comparison. Keep the
Agon unchanged until the Author mounts the card and explicitly confirms its
return before any reset. Startup restoration and input recovery remain DH04
gates; neither is presently established.

## Offline SD staging checkpoint

Author mounted the Agon SD on the development host. Whole-file hashes verify
the original 38-byte startup and already-deployed 11,284-byte sender. Preserved
the original startup at
`/agents/extender/backups/startup/devkit-hardware-r01/original-autoexec.txt`.
Temporary startup selects mode 3, loads `/extender/install/prx06pc.bin`, then
runs it. Independent readback verifies all 51 bytes. The sender restores and
verifies the original startup before accessing GPIO. No sender rebuild or
redeployment, EMOS change, Agon reset or historical receiver installation.
An existing `autoexec.txt.p17bak` remains untouched; resolve it through the
listener's recovery protocol when that service is available. Card stays mounted
until the Author returns it. Wait for explicit return confirmation before reset.
Input admission remains unproven; this completes only offline staging within
DH02, not that item's input gate or DH03's comparison.

## Historical receiver installation checkpoint

Author confirms both boards powered and SD inserted in Agon, and explicitly
authorizes the receiver flash. Installed the prepared original-DevKit historical
receiver at 40 MHz flash speed. All three segments pass independent readback
verification; the boot log confirms 40 MHz and the receiver's idle USB command
prompt. No arm command, Agon reset or test invocation. EMOS and mainboard VDP
remain unchanged. DH03 installation is complete; its one-record result remains
unmeasured. This standalone receiver has no network or keyboard service.

## Reset and returned-card inspection checkpoint

One planned Agon reset was issued with the Author-confirmed inserted card.
The receiver reports READY low before and after reset despite releasing its
open-drain output. The collector refused to arm; no receiver record or payload
integrity verdict exists. CLOCK/VALID pre-arm readings are not evidence because
the original receiver does not enable those GPIO input buffers until arming.
READY low does not establish a missing wire, damaged board or DMA defect.

Author then returned the card to the development host and requested inspection.
Read-only whole-file checks find the exact original 38-byte startup restored,
matching its preserved backup, and the unchanged expected sender binary. This
is consistent with the sender executing its startup-restoration code during
that boot; it does not prove the sender transferred data. No startup mutation
or repeat test during inspection. Card remains mounted on the host. Any next
reset requires explicit card-return confirmation and a deliberately restaged
launch if another comparison is authorized.

## READY bias review

The source-faithful historical receiver configures READY as input/output open
drain, with internal pull-up and pull-down disabled. Writing 1 releases the
wire; it does not drive it high. The original
[harness contract](../../../hardware/designs/light2-harness-r01/README.md)
and [legacy design](../../../../agon-extender-legacy/design/README.md) require
a 10 kΩ READY pull-up. The eight 15 kΩ Port C pull-ups do not bias PD4/READY.
Current `p4_boot_release.cpp` instead drives READY as a push-pull output during
boot, so its electrical behavior is different from this historical receiver.

The older simplified-harness record says the three bias resistors were removed.
That does not establish their current presence or absence: the Author confirms
the original parallel harness remains installed. Verify the READY pull-up
physically before attributing its low released level or altering the original
receiver. The relevant existing conductor is blue: Agon PD4/header13 to DevKit
GPIO20/EXT2 contact13. No wiring change or new diagnostic firmware yet.
This possible bias mismatch does not establish the cause of modern boot
admission failure or either P4-PC corruption result.

## Author confirms fitted bias components

Author reports exactly eight fitted pull resistors, all data-line pull-ups to
Agon 3.3 V. Thus the original receiver's external READY pull-up is absent.
This is a concrete difference from the passing prototype, not an inference
that the parallel conductors are missing. It can explain an undefined/low
released READY input; no voltage/continuity measurement yet establishes the
complete electrical cause.

Proposed prerequisite for the source-faithful receiver comparison: with both
boards off, fit the original 10 kΩ pull-up from the blue READY conductor
(Agon PD4/header13 ↔ DevKit GPIO20/EXT2-13) to Agon 3.3 V. Do not join board
power rails or change the eight data pulls, data mappings, CLOCK or VALID.
Await Author acceptance/installation; record this fitted configuration as a
new harness variant before qualifying it. Keep SD mounted on the development
host and both boards off while staging the next launch. No firmware or SD
change in this observation turn. The current card holds normal startup, not
a pending test launch. Historical receiver remains installed.

## Author redirects to last working DevKit installation

The Author has parked further parallel comparison and withheld the bench while
reassembling it. Prepare the exact last verified DevKit pair immediately before
the P4-PC transition; do not substitute an older formal release, a freshly rebuilt
candidate or the failed October 10 boot-handshake build. No wiring change is
part of this normal restore. The previous READY pull-up proposal is parked.

DR01 — [x] Identify and preserve the September 30 pair: P4 source
`fd0c1d368574be57bd91bd136c6230d003c15de4`, build
`hwval-p4-fd0c1d368574-2026-09-30-18-44-01Z`; EMOS source
`9b67182cca4cb51f9fee0473ab32dda1e766e3db`, build
`hwval-emos-9b67182cca4c-2026-09-30-22-09-08Z`. Retained joint qualification
passed 25/25 required checks, followed by Author Nurples/Legacy/reset review;
see [development evidence](../../development/2026-09-30.md), DEV-20260930-19.
This is the last working installed pair, newer than selected production v0.1.0.
Production manifests and tags remain unchanged.

DR02 — [x] Copy exact retained bytes, verify build/flash receipt hashes, compare
all four P4 segments against the factory prefix, and compare EMOS against the
independently verified full-ROM readback. No rebuild. Machine-local preparation
and receipts are under the ignored `devkit-hardware-r01/prepared-pre-pc/` silo.

DR03 — [x] Stage EMOS at `/extender/install/em-prepc.bin` on the Author-confirmed
host-mounted Agon card: 128579 bytes, SHA-256
`812cd23f20b1254e019e5b6d6c33e00eaa30e05603774152b609b8ef83c154a4`.
Readback passes; existing normal startup and matching foreground listener remain
unchanged. No automatic flash launch; card remains mounted. User files intact.

DR04 — [x] After the Author returns the bench, install the prepared P4/EMOS pair
and independently verify installed bytes and real keyboard admission. Retain
mainboard VDP. Use a reviewed offline startup/recovery path if the existing
experimental EMOS cannot admit input with the older P4; do not ask a disabled
keyboard route to enable itself. Reconfirm card insertion before resetting.
No hardware installation or input recovery is claimed by preparation/staging.

### Bench returned — one-shot restoration installation

Author confirms the bench rebuilt. DR04 resumes only for the selected September
30 pair. Before requesting card insertion, prepare a separate installer batch
that runs a small normal-startup restorer, then invokes the existing FLASH utility.
The restorer reuses the historical sender's proven write/close/readback idiom;
it performs no GPIO, transport, display-mode or reset operation. A failure returns
nonzero and MOS stops the installer batch before FLASH. The separate batch avoids
rewriting the file that supplies the FLASH instruction.

The prepared helper is a normal ADL application, not a MOSlet, at
`/extender/install/preboot.bin`. Root startup selects mode 3 and executes
`/extender/install/prepc.txt`; that file loads/runs the helper, then executes
`FLASH mos /extender/install/em-prepc.bin -f`. Original 38-byte startup backup
remains verified. All staged files pass host readback. No Agon reset until the
Author confirms the card reinserted. Install and independently verify the exact
P4 segments first; preserve mainboard VDP and perform no historical parallel test.

P4 installation checkpoint: exact selected DevKit image installed; all four
segments pass independent flash verification, and HTTP service responds. EMOS
replacement and actual input admission remain pending; ready=false is observed
before EMOS restoration, not a claimed pass. No Agon reset yet. Card remains
host-mounted with the verified one-shot installer. Await Author confirmation of
card insertion, then perform one Agon reset and observe FLASH automatic reboot.

### Restoration completed

Author confirmed card insertion; one reset launched the staged installer.
FLASH rebooted automatically and fresh Extender keyboard admission appeared after
30.9 host seconds. No repeated flash or reset. Full 131072-byte EMOS readback
matches the September 30 image and erased padding, SHA-256
`341cab32e2ba0cc49d8327ec91fa0673d69e960836b5da18c14c37b07cc434e0`.
Original 38-byte startup readback matches; remote CLI commands successfully opened
the foreground listener, saved ROM and returned to Legacy MOS. All 120 keyboard
packets accepted, none discarded; final neutral input with no held/pending keys.
Listener exited. Startup/ROM verification including setup and retrieval took
87.1 host seconds, separate from flashing and automatic reboot.

Local `prepared-pre-pc/restoration.local.json` joins verified component receipts;
ROM evidence is under `/agents/extender/results` on the card. Installer support
files remain under `/extender/install`, with no automatic startup trigger.
Card stays in Agon; existing listener, mainboard VDP and wiring remain unchanged.
Author ordinary gameplay review is next; no parallel retry or resistor change.

### Author correction — parallel comparison remains the objective

Normal firmware restoration was preparation for parallel testing, not a handoff
to gameplay. Continue the existing DH03 single 1024-byte slow-profile comparison;
do not invent a game review or broad test sweep. The last physical resistor
inventory was only eight data-line pull-ups. The Author has since rebuilt the
bench, but has not confirmed a READY pull-up. Ask that one physical question
before reflashing the standalone open-drain receiver: the previous attempt did
not arm because released READY read low. Do not repeat it unchanged or infer
that bench rebuilding added components. No new flash, reset or test performed
in this correction. Retain the restored exact normal pair as recovery.

### Complete historical control-bias requirements

Author confirms rebuilding did not add READY bias. Before further comparison,
the authoritative `hardware/designs/light2-harness-r01/profile.yaml` electrical
section requires all three control resistors: READY_N 10 kΩ pull-up, VALID_N
10 kΩ pull-up, CLOCK 10 kΩ pull-down. Existing eight data pull-ups do not supply
these biases. READY is concretely required by the historical receiver's OD
output with both internal pulls disabled; VALID/CLOCK preserve inactive levels
while Agon pins are released. Original prototype also specifies 220 Ω data
series resistors; those are distinct from pull resistors. No new resistor is
reported fitted or approved by this research response. No hardware action.

### Control pulls installed — bounded comparison resumed

Author confirms all three nominal 10 kΩ control resistors now fitted and
explicitly authorizes resumption. Record the bounded physical variant as
`devkit-parallel-control-harness-r01`: existing DevKit data/control conductors
and eight data pull-ups retained; READY_N and VALID_N pulled to Agon 3.3 V,
CLOCK pulled to common ground. Values/install are Author reports, not meter
verification; no new buffered circuit or P4-PC qualification claim.

DH03 uses the exact existing historical receiver, with no diagnostic/code
change. Adapt the existing sender wrapper to call only original profile 0 once,
then release pins and write durable completion. Its original assembly, canary,
and 24-NOP transfer are byte-identical source; the old sweep binary stays
unchanged. This closes the former unobservable terminal-state gap without
leaving the Agon waiting for further arms. Sender completion is not receiver
integrity: USB must report the exact 1024-byte sequence/CRC pass separately.
Stage mode only in autoexec; restore normal startup before GPIO access. Verify
READY=1 before the single reset/arm. No target analyzer or automatic retry.
Restore exact September 30 P4 afterward, confirm Agon sender completion and
normal startup through the listener, then hand back for parallel-test discussion.
No game test, speed sweep, reverse test or modern ExExt enablement is authorized.
