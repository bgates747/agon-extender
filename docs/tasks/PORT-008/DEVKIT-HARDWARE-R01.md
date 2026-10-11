# PORT-008 — Original DevKit hardware control

## Executive summary

**Current disposition:** The repaired DevKit passes all 22 historical forward
1 KiB records, including the fastest zero-NOP profile. All byte counts,
sequences, patterns and CRCs match. Fastest median receiver time is 1,193 µs
(0.819 MiB/s per-record payload rate, not sustained file-transfer throughput).
Exact normal September30 DevKit firmware was restored and all four segments
independently verified; original startup read back, listener closed and neutral
Extender keyboard admitted. EMOS/mainboard VDP unchanged. No active reset hold,
capture, serial collector or automated input remains.

The Author repaired the three missing onward control connections through
220 Ω series resistors. The [reverse pinwalk](DEVKIT-PINWALK-R01.md) passes
all eight observed paths; three data paths remain unprobed, while receiver
validation checks the complete eight-bit payload for these bounded cases.
P4-PC still requires 220 Ω series resistors on all eleven signals. Modern
ExExt and reverse payload are not qualified by this historical comparison.

### Original parallel comparison contract

### Authorized faster-profile sweep — 2026-10-10

DH08 [x] — Reuse the existing complete22-record sender, unchanged, with the
same source-faithful40MHz receiver. Seven profiles (24,16,10,6,3,1,0NOPs),
three records each, plus the fixture's original final0NOP record. Verify exact
retained executable/assembly/canary hashes; no rebuild or firmware modification.
Stage/read back its existing self-restoring startup through the Legacy listener.
Preserve the preceding single-record result; no new firmware backup.

DH09 [x] — Capture the unchanged eight Agon-side probes at1MHz for60seconds.
Require observed CLOCK waiting activity with READY/VALID high before every USB
arm. Record each receiver byte-count/pattern/sequence/CRC verdict and elapsedµs;
stop arming at the first missing/failed verdict. Retain full capture and five
clean seconds after the final verdict. The1MHz capture demonstrates handshake
activity, not full payload decoding. No automatic replay or slower-profile retry.

DH10 [x] — Verify the final control-release/quiet tail, hold powered Agon in
reset across exact normal P4 restoration, independently verify all four segments,
release after HTTP initialization, verify original startup and neutral keyboard.
The unchanged full-sweep sender prints completion but writes no SD result;
do not reuse the preceding one-record SD result as proof of this sweep.
Durable host receiver logs own integrity. Report per-profile medians/ranges
and relative improvements; receiver timing includes admission/logging overhead
and is not sustained application/file-transfer throughput. Keep modern ExExt,
reverse payload and unmodified P4-PC outside this result.

#### Repaired-harness speed sweep result

All 22 historical forward records passed: 1,024 bytes each, sequence 1,
complete pattern validation, stored/calculated CRC 6474. No retry was needed.
The unchanged sender and retained 40 MHz receiver exercised seven delay
profiles three times each, followed by the original extra zero-NOP record.

Rows are ranked slowest first. Rate is 1,024 payload bytes divided by the
receiver elapsed time; improvement is `(baseline median / profile median - 1)`.
Timing includes receiver admission/logging overhead and excludes host spacing.
These are per-record rates, **not sustained file-transfer throughput**.

| Delay NOPs | Median µs | Range µs | Payload MiB/s | Rate improvement vs 24 NOPs |
| ---: | ---: | ---: | ---: | ---: |
| 24 | 5,191 | 5,190–5,197 | 0.188 | 0% |
| 16 | 3,857 | 3,857–3,859 | 0.253 | 35% |
| 10 | 2,858 | 2,858–2,860 | 0.342 | 82% |
| 6 | 2,192 | 2,191–2,192 | 0.446 | 137% |
| 3 | 1,693 | 1,693–1,694 | 0.577 | 207% |
| 1 | 1,360 | 1,359–1,361 | 0.718 | 282% |
| 0 | 1,193 | 1,193–1,195 | 0.819 | 335% |

The final extra zero-NOP record also passed at 1,195 µs. Total validated
payload was 22 KiB. Before every USB arm, the host observed CLOCK waiting
activity with READY/VALID high. All eight unchanged Agon-side probes were
captured for 60 seconds at 1 MHz (60 million samples); the archive was checked
against the retained raw SHA-256. This capture establishes handshake activity,
not complete high-speed payload decoding or P4-pad electrical margins.

The unchanged full-sweep sender writes no SD completion result. Receiver USB
logs provide durable integrity evidence; the earlier single-record SD result
is not evidence of completion for this sweep. Exact components, tools, logs,
capture and receipts are retained in the ignored speed-sweep-r01 evidence silo.
Modern ExExt, reverse payload and P4-PC qualification remain outside this test.

Recovery passed: final five waveform seconds show READY/VALID high and CLOCK
low. Pi held Agon reset across exact normal P4 restoration and independent
four-segment verification, releasing it after P4 HTTP initialization. Through
the foreground listener, the host verified the original 38-byte startup and
unchanged full-sweep executable. The host closed the listener and verified
neutral admitted keyboard with no held/pending events. No EMOS/mainboard VDP
change, new firmware backup or production promotion occurred.


### Authorized repaired-harness payload repeat — 2026-10-10

DH05 [x] — Reuse the retained 40 MHz historical DevKit receiver and unchanged
single-record sender (1,024 bytes, sequence1, CRC6474, profile0/24 NOPs).
Verify retained hashes, normal recovery segments and admitted keyboard. Through
the current Legacy foreground listener, verify/stage the sender and reviewed
startup; inspect existing sibling recovery files before replacement. The
sender restores and readback-verifies original startup before any GPIO drive.
No EMOS/mainboard VDP change or new firmware backup. Preserve prior results.

DH06 [x] — Install and independently verify the existing receiver. Capture
all eight unchanged probe channels at 1 MHz for60seconds; waveform evidence
establishes sender waiting activity, not high-rate payload bit correctness.
Require delivered samples before one Agon reset. Observe CLOCK transitions
with READY/VALID high before sending one USB arm command, replacing the old
unobserved17-second delay. Require receiver byte-count/sequence/pattern/CRC
PASS and five clean seconds. Stop on failure; no sweep, retry or automatic
replay. Analyzer contacts remain Agon-side, before series resistors.

DH07 [x] — Restore and independently verify the exact normal September30
DevKit firmware. Hold Agon reset across restoration if sender ownership is
uncertain; only release after P4 initialized. Retrieve durable sender result
and verify original startup through the listener; then close the listener and
verify neutral admitted keyboard. Report receiver integrity, sender completion
and recovery separately. This is one slow-profile forward historical check,
not modern ExExt or reverse-payload qualification.

#### Repaired-harness payload result

The historical forward transfer passes on the repaired DevKit harness. The
unchanged sender and source-faithful40MHz receiver transferred exactly1,024bytes,
sequence1, with stored and calculated CRC both6474. Receiver pattern validation
passed, READY returned high, and five clean USB seconds showed no failure/reboot.
Receiver-reported elapsed time was5,198µs for this single24NOP slow-profile case;
this is integrity evidence, not a speed sweep or modern transport benchmark.

The host observed15,042CLOCK transitions in a20ms source window while READY
and VALID remained high before its one USB arm request. This directly verifies
the sender entered its waiting loop; no fixed17second readiness assumption was
used. The source-side capture has60,000,000samples at1MHz for60seconds. It
establishes activity/handshake timing only; it is not a complete high-speed data
decode or P4-pad signal-integrity measurement. No retry/sweep or EMOS/VDP update.
Exact installed receiver, sender, host tools, USB verdict and waveform are retained
in the ignored payload-after-repair-r01 evidence directory.

Normal recovery completed: final five waveform seconds show READY/VALID high
and CLOCK low. Pi held Agon reset while restoring and independently verifying
all four exact September30 P4 segments, waited for P4 HTTP initialization, then
released reset. Original38-byte startup was read back through the foreground
listener. The durable Agon record reports bytes=1024, delay_nops=24,
sender_rc=0 and state=released. Listener closed; fresh neutral admitted keyboard
verified, held0/pending0, locale1. No active flash, serial, capture, reset hold,
listener or automated input remains. No new firmware backup, EMOS/mainboard
VDP change, retry or broader qualification. Production selection unchanged.

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

### Control-bias repeat — admission blocked, recovery pending

After the Author reported “output on extender,” explicit `EMOS LEGACY` allowed
the foreground listener to start. The existing startup backup was preserved and
readback verified under `/agents/extender/backups/startup/prx06one-old.txt` before
explicit transaction cleanup. The 11,012-byte single-record sender and 52-byte
temporary startup both passed whole-file readback. The sender's original assembly
and canary remained unchanged; no ordinary application was modified.

The historical DevKit receiver's three flash segments independently verified;
its boot confirmed 40 MHz. Before any Agon reset, USB status reported
`state ready=0 valid=0 clock=0 state=released`. Only READY has its input enabled
at this stage; the other two readings are not physical evidence. The collector
stopped at its mandatory released-READY precondition, with no reset or USB arm.
No record, CRC verdict or throughput result exists for this attempt. The cause
of the low reading remains unresolved; an Author report of fitted resistors is
not a voltage or continuity measurement.

The exact September 30 normal P4 was restored and all four segments independently
verified. HTTP is online, but keyboard admission did not return after P4 reboot.
EMOS and mainboard VDP were not flashed. The test startup was never executed, so
its self-restoration did not occur. Do not reset with that trigger present beside
the normal UART-serving P4. The prepared offline recovery checks the card identity
and exact temporary contents, preserves that unused startup under
`/agents/extender/backups/startup/prx06one-unrun.txt`, writes the original 38 bytes,
and verifies readback. Actual offline restoration and subsequent keyboard proof
remain pending Author card mounting/return. No process remains active.

### Offline startup recovery completed; bench hold

The Author mounted the card and withdrew the bench for shutdown, reporting the
pull-up appears one pin off. Do not treat that tentative observation as verified
wiring or request live measurements while the bench is off. The prepared offline
recovery verified mount/card identity and the exact 52-byte unused test startup,
archived it under `/agents/extender/backups/startup/prx06one-unrun.txt`, restored
the original 38-byte startup and verified whole-file readback after syncing.
Startup SHA-256 is
`7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`.
The card was left mounted. No firmware change, Agon reset or test occurred during
this recovery. Normal P4 restoration is already independently verified; keyboard
recovery remains untested until the Author returns the bench and confirms the
card in the Agon. The comparison still has no attempted payload or CRC verdict.

### READY pull-up meter check — Author correction

Author confirms blue READY_N was correctly placed and measures 10 kΩ from the
pin to the rail. Withdraw the earlier tentative one-pin-offset hypothesis.
This agrees with the harness contract: READY_N takes a 10 kΩ pull-up to Agon
3.3 V, not a pull-down. Record the measurement as Author-observed resistance/path
verification; it does not establish powered READY voltage or whether an endpoint
holds the line low. No further hardware access or measurement requested while
the bench is shut down. Reconcile the P4 input reading with actual powered line
voltage and both endpoint pin configurations when the bench next returns.

### Files-only review completed while Author uses Jukebox

The [READY software review](READY-SOFTWARE-REVIEW-R01.md) traces exact installed
EMOS source/compiled startup, original receiver source/compiled GPIO calls, SDK
GPIO input/open-drain behavior, unchanged sender assembly and host sequencing.
No firmware cause for the low READY reading was established. Agon PD4 initializes
as input; P4 GPIO20 input is enabled and its open-drain output released.
The runner's caught failures incorrectly return shell status zero, while retained
JSON correctly records non-invocation. Its new pre-reset gate and unobserved
17-second delay differ from the old passing procedure. These are recorded limits,
not permission to force READY high or retry blindly. No hardware/service access,
flash, reset, input injection, SD operation or firmware edit during review.
Author reports Nurples/Aginvadors still play in browser and Rally retains its
known control issue; these demonstrate ordinary UART operation, not parallel.

## Idle READY voltage checkpoint

Author clarifies that Jukebox is running on a separate Console8 and releases the
bench. Stage the retained 40 MHz historical DevKit receiver for a powered READY
voltage reading only. Verify its installation and query USB status without
arming reception. Keep Agon EMOS, mainboard VDP and SD startup unchanged; do not
reset Agon or run a parallel payload. Verify the retained exact normal DevKit
recovery files before installation. Pause with the receiver idle for the Author
to measure the blue READY signal relative to common ground. No DMA or transfer
conclusion follows from this checkpoint.

Idle receiver installed and independently verified at 40 MHz; USB status reports
READY=0 with output released. Receiver was not armed and Agon was not reset.
No parallel data sent. USB collector closed. Standalone receiver remains
installed awaiting the Author's blue READY-to-common-ground voltage reading;
normal Extender keyboard/network services are temporarily unavailable. Exact
normal-firmware restore helper and hash-verified files are retained locally.

Author reports **3.27 V** for the requested powered blue READY_N-to-ground
measurement. The measured point is high, conflicting with the receiver's
preceding GPIO20 input reading of zero. The exact probe endpoint (Agon versus
DevKit end) is not yet confirmed. The reviewed receiver still selects GPIO20
input/open-drain output and reads that input; static review found no mapping
or release-polarity typo. Do not infer end-to-end continuity, failed hardware
or a DMA fault from this observation. No new flash, reset, arm or transfer.

Author confirms the **3.27 V reading was at the DevKit end**, as instructed.
The signal at that measured header point is therefore high. Rechecking the
pinned SDK and compiled receiver confirms `gpio_get_level(20)` reads input
register bit 20 and initialization requests input plus released open-drain
output. This static evidence does not establish the live IO_MUX configuration
or actual chip-pad voltage. Next proposed bounded diagnostic: read live IO_MUX,
GPIO input/output/enable and output-selection registers for GPIO20, alongside
the SDK configuration dump. It must leave READY released and must not arm
PARLIO, drive a test level, reset Agon or transfer data. This would be a separate
instrumented receiver build, not the unchanged historical baseline. No such
build or installation has occurred; await agreement before changing firmware.

## Approved live GPIO readback — RG01

RG01 [x] — Author approves the bounded GPIO20 readback probe. Build the
[probe source](fixtures/ready-gpio-r01/main.c) against the retained receiver's
SDK/configuration, independently verify installation, and capture live input,
IO_MUX, output latch, output enable and routing registers plus the SDK dump.
Preserve READY initialization; leave its open-drain output released. The probe
has no arm command or PARLIO initialization. No Agon reset, SD mutation, other
pin setup or transfer. Compare with the Author's DevKit-end 3.27 V observation
and stop to discuss the result before another electrical or transfer test.

Live register check complete; see [bounded results](READY-REGISTER-RESULTS-R01.md).
Raw input bit20 remains zero; no missing input-enable, pin hold or disabled
GPIO/IOMUX clock found. Cause remains unresolved. Pause for discussion before
changing GPIO mode or starting any transfer.

## Approved input-only comparison — RG02

RG02 [x] — Author approves GPIO20 input-only with sleep selection disabled.
Retain r02 source/images/receipts, then build/install/verify r03. At startup
record three stages: original released open-drain configuration; input-only;
input-only with sleep selection disabled. Read live state at each stage to
separate the two changes. No drive-low, internal bias, other GPIO setup,
PARLIO, Agon reset or SD mutation. Leave the probe input-only and stop for
discussion after retaining the results. Exact normal recovery remains prepared.

RG02 completed: both configuration changes verified live, but GPIO20 remained
low at all stages. See [r03 results](READY-REGISTER-RESULTS-R01.md). Stop for
discussion; no pull-up experiment, transfer or restoration performed.

## Approved weak internal pull-up comparison — RG03

RG03 [x] — Author approves enabling GPIO20's weak internal pull-up while
remaining input-only and sleep selection disabled. Retain r03 source/images
and receipts. Build/install/verify r04, record three samples each before,
during and after the weak pull-up, and restore the no-internal-pull baseline
at completion. Only GPIO20 configuration may change. Keep external bias,
Agon firmware/startup and wiring untouched. No drive-low command, PARLIO,
Agon reset or transfer. Retain results and stop for discussion.

RG03 completed: GPIO20 reads 0/0/0 without its pull-up, 1/1/1 with it,
then 1/0/0 after removal. See [r04 results](READY-REGISTER-RESULTS-R01.md).
Input can detect high. External connection/pin identity needs reconciliation;
internal bias is not a validated handshake fix. Pause before physical work.

Author moved analyzer probes to DevKit using the prior P4-PC arrangement and
requested the existing pinwalk. [DevKit pinwalk contract](DEVKIT-PINWALK-R01.md)
owns staging, input ownership, acquisition and restoration; no new wire
algorithm or firmware flash is required for the pinwalk itself.
