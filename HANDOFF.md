# Active checkpoint — bounded DevKit parallel test resumes

Author confirms three10k control pulls installed and authorizes resume. Scope
one1024byte24NOP comparison with exact historical receiver, no analyzer on target.
Adapted single-record sender uses unchanged original wireasm/canary, restores
normal startup beforeGPIO, records durable completion after pins release.
Current September30 P4/EMOS pair verified; exact P4 rollback ready. SD in Agon.
Evidence agents/port008-live-qualification/devkit-hardware-r01/control-bias-r01.
Do not use old17second collector until new manifest/staging/install verified.
Do not substitute failed current boot-handshake build on restoration. No games.

# Current checkpoint — September 30 DevKit pair restored and verified

Author returned rebuilt bench and confirmed card insertion with “go”. Exact
last pre-PC pair is now installed: P4 `hwval-p4-fd0c1d368574-2026-09-30-18-44-01Z`,
EMOS `hwval-emos-9b67182cca4c-2026-09-30-22-09-08Z`. P4 all four segments
independently verified; EMOS complete131072byte readback matches retained ROM,
SHA256341cab32e2ba0cc49d8327ec91fa0673d69e960836b5da18c14c37b07cc434e0.
One Agon reset launched offline installer; FLASH reboot completed automatically.
Fresh keyboard admission observed after30.9seconds. No retry/reset afterward.

Original38byte /autoexec.txt restored and readback verified, SHA7b500d81...;
normal startup only selects keyboard locale and EMOS KEYINPUT extender.
Remote commands and foreground SD listener work:120 packets accepted,0discarded;
listener exited, keyboard ready/neutral,held0,pending0. Legacy MOS prompt;
card stays in Agon. Existing listener, mainboardVDP and wiring unchanged.
One-shot installer files remain /extender/install, no startup trigger remains.
ROM evidence under /agents/extender/results/devkit-prepc-20261010-072850-rom.bin.
ROM/startup verification including command/setup/retrieval took87.1hostseconds.

Local receipt: agents/port008-live-qualification/devkit-hardware-r01/
prepared-pre-pc/restoration.local.json and component installation subdirectories.
Older failed October10 reciprocal-handshake candidate and historical receiver
are no longer installed. The formal production selector remains v0.1.0;
this deliberate exact September30 restore is not a new release/promotion.
Author corrects next step: restoration is preparation for the parallel
comparison, not gameplay. Resume the existing single1024byte DevKit comparison
after resolving the rebuilt harness READY bias. Last confirmed inventory was
eight data pull-ups only; do not assume rebuilding added a READY pull-up. The
historical OD receiver previously refused to arm with released READY low.
No repeated flash/test until that prerequisite is resolved. No active bench
operation; Author physical clarification is next. Earlier checkpoints below are superseded.

# Current checkpoint — P4 restored; card ready for one-shot EMOS install

Author returned rebuilt bench. Exact September 30 P4 DevKit firmware
`hwval-p4-fd0c1d368574-2026-09-30-18-44-01Z` installed on original DevKit;
all four segments independently verified. HTTP service responds. Input is NOT
admitted yet: installed experimental EMOS still awaits replacement. Mainboard
VDP unchanged. No Agon reset, firmware backup or parallel test performed.

Card remains mounted Lenovo. All installer files read back verified. Root
startup is now44bytes: VDU22mode3 then EXEC /extender/install/prepc.txt.
That separate batch loads/runs /extender/install/preboot.bin (3520bytes), which
restores AND verifies original38byte startup, then invokes
FLASH mos /extender/install/em-prepc.bin -f. Helper return failure stops batch.
Payload128579bytes/SHA812cd23f... unchanged. No keyboard admission dependency
for installation. FLASH should reboot automatically; do not interrupt/repeat.

Next: Author safely ejects Lenovo card and inserts Agon, then confirms. Only
after that confirmation may agent reset Agon once and monitor installation.
Full-ROM readback, startup readback and actual remote input proof remain pending.
Evidence agents/port008-live-qualification/devkit-hardware-r01/prepared-pre-pc/
(p4-installation and installer-stage-receipt.local.json). Earlier holds below
are superseded by Author bench return; card return gate remains mandatory.

# Current checkpoint — last working pre-PC DevKit pair prepared; bench withheld

Author requests the last working DevKit installation immediately before the
P4-PC change, not another parallel experiment. Author is rebuilding the bench:
**no device access, flashing, reset or test until it is returned.**

Selected exact September 30 installed pair:
1. P4 `hwval-p4-fd0c1d368574-2026-09-30-18-44-01Z`, source `fd0c1d368574`.
2. EMOS `hwval-emos-9b67182cca4c-2026-09-30-22-09-08Z`, source `9b67182cca4c`.

Joint installed qualification passed 25/25 required checks; Author then accepted
Nurples, clean exit, Legacy return and browser reset (DEV-20260930-19). Exact
retained binaries are copied and hash-verified, P4 factory segments agree, and
EMOS matches the retained padded full-ROM readback. No rebuild. This pair is
newer than formal production v0.1.0; production selection remains unchanged.
The older `prepared-firmware/` files are fallback only, not this restore target.

Local preparation/manifest/README: `agents/port008-live-qualification/`
`devkit-hardware-r01/prepared-pre-pc/`. On Author-confirmed Lenovo SD,
`/extender/install/em-prepc.bin` is staged and readback-verified: 128579 bytes,
SHA256 `812cd23f20b1254e019e5b6d6c33e00eaa30e05603774152b609b8ef83c154a4`.
Normal 38-byte `/autoexec.txt` and matching `/emos/sdserve.bin` are unchanged;
no automatic flash/test launch. Card left mounted. Staging receipt retained.

Installed boards remain unchanged: standalone historical DevKit receiver
(no network/keyboard service) and experimental October 10 EMOS. Recovery is
NOT complete. When Author returns the bench, install the prepared pair together
using reviewed offline bootstrap/recovery if input cannot be admitted. Do not
assume the older P4 alone can satisfy the current experimental EMOS handshake.
Keep mainboard VDP intact. No resistor or wiring alteration requested for this
normal restore. Earlier READY-resistor proposal and comparison steps are parked.
Reconfirm card return before any Agon reset. No active hardware operation.

# Latest checkpoint — READY low; card inspected on Lenovo

[Current task](docs/tasks/PORT-008/DEVKIT-HARDWARE-R01.md): planned Agon reset
issued once, but original receiver reports READY low despite released OD output
both before/after reset. Collector closed without any arm; no record verdict.
No analyzer on target, CLOCK/VALID pre-arm inputs disabled so ignore their reads.
Author returned SD to Lenovo. Read-only inspection verifies ORIGINAL38byte startup
is now restored/hashmatches backup and sender11284bytes/hashunchanged. Sender
restoration code apparently executed; no proof of transfer. Card remains mounted
on Lenovo; do not reset Agon. Temporary test launch is no longer on the card.
Historical DevKit receiver remains installed; no network/keyboard service.
Source review: its READY release is OD/high impedance with no internal pull;
original harness requires10k external pull-up. Author confirms ONLY eight
data pulls to Agon3.3V fitted; READY pull-up absent. Proposed restoration of
10k on blue PD4/header13 to GPIO20/EXT2-13, awaiting Author installation/acceptance.
Keep card on Lenovo and both boards off during staging; current startup is
normal, not a test launch. Do not claim low READY has a fully measured cause. Eight15k data pull-ups do not cover READY. Full harness
confirmed by Author; do not infer missing wires from outdated draft records.
EMOS/mainboardVDP/harness unchanged. No active operation. Evidence
agents/port008-live-qualification/devkit-hardware-r01/run-result.json and
lenovo-after-reset-check.json. Earlier checkpoints below are superseded.

# Active checkpoint — original DevKit receiver installed

[Current contract](docs/tasks/PORT-008/DEVKIT-HARDWARE-R01.md), frozen4d5084bb.
Author confirms both boards powered, original full DevKit parallel harness in
place, SD inserted in Agon. Analyzer stays on disconnected P4-PC; no target
waveforms are available. Original DevKit receiver prx06-devkit-flash40-r01-
b2026-10-10-06-16-42Z installed/all3segments independently verified; boot confirms
40MHz and idle command prompt. No Agon reset/USB arm/payload invocation after
installation. App SHA7ecfd6577b4c7499fb0f8a4287c315d504f04014bbb0d92cd4bca3cbe398078f.
This standalone receiver has NO network/keyboard service. EMOS/mainboard VDP
unchanged. Exact current DevKit EDP restore retained locally, but its admission
previously failed busy; do not promise recovery passed.
Temporary startup selects mode3, loads /extender/install/prx06pc.bin, runs.
Original38bytes backed up under /agents/extender/backups/startup/devkit-hardware-r01.
Sender restores/byte-verifies original startup before GPIO access; already-
deployed11284byte binary hash verified. Existing autoexec.txt.p17bak untouched.
Next Agon reset WILL launch sender. Collector must be ready before that reset;
arm exactly one1024byte24NOP record, USB verdict only, no sweep/retry.
No active flash/capture/reset/test process. Installation/evidence under
agents/port008-live-qualification/devkit-hardware-r01. Older checkpoints below
refer to prior PC experiments, not current installation/input/card state.

# Current checkpoint — 40 MHz control fails, full EDP/input restored

[40 MHz result](docs/tasks/PORT-008/FLASH40-CONTROL-R01-RESULTS.md) supersedes
older next-step claims below. Exactly one slow-profile historical receiver record
fails with the same last byte f4, stored CRC f3f4/calculated ba67 as 80 MHz.
Actual boot confirms 40 MHz; generated config differs only in flash-speed keys,
receiver/canary allocated code/data sections unchanged. Full 45-second 24 MHz trace
retained/verified; 1,024 qualified source clocks and five observed source data bits
pass independently. No retry or later sweep records.
Exact full EDP data-r02/all four segments restored/verified. P4 HTTP awaited before
Agon recovery reset; original 38-byte startup readback verified, all 52 remote key
packets accepted, ready/neutral/held0/pending0, listener exited. No active bench
operation; SD remains Agon. EMOS/mainboard VDP/wiring/production unchanged.
Evidence agents/port008-live-qualification/devkit-control-flash40-r01.
Pause for Author discussion; slower flash alone did not repair corruption.

# Current checkpoint — offline build comparison complete, paused

[Build comparison results](docs/tasks/PORT-008/BUILD-COMPARISON-R01-RESULTS.md)
supersede older next-step claims below. Existing work was committed in logical
groups before review (Extender 826c6da5 / 2ead90d6 / 43fb2706; EMOS a843a1e).
Both original DevKit and current PC report silicon v1.3 and IDF 5.5.5. All 128
compared retained relevant SDK files match the reproduction, but later retained
build/config/compiler artifacts do not establish the original passing binary.
Original flash 40 MHz versus reproduction 80 MHz is a concrete difference, not a
proven cause. Recommend one otherwise unchanged standalone slow-profile record
at 40 MHz; stop for Author discussion before rebuilding or touching hardware.
No bench operations during this review. Latest completed experiment and verified
keyboard/startup restoration remain as recorded below. Production unchanged.
Unrelated EMOS scripts/application_peer.py remains uncommitted and untouched.

# Current handback: comparison completed, normal input restored

## Completed historical comparison and verified restoration

Original PRX-06 receiver with GPIO-only P4-PC remap failed its first1024-byte
record at the slowest24-NOP profile. First byte41, lastF4 (expected74), stored
CRC F3F4/calculatedBA67 instead of6474. Remaining21records were not armed.
Original sender assembly/sweep unchanged; only unattended launch adapted.
Analyzer acquisition passed:45seconds at24MHz,1,080,000,000samples; exactly1024
qualified falling clocks with READYlow, zero mismatches on observed source
D2/D4/D5/D6/D7. D0/D1/D3 were not observed; probes are on Agon header, not P4.
Full hash-verified logic.sr and USB verdict retained in ignored local evidence.
Failure without modern coordinator or full EDP means those are not its sole
necessary cause. Harness, hardware, SDK/toolchain and receiver memory/cache/DMA
attribution remain unresolved. No usable throughput or reverse-transfer claim.

After Author confirmed card in Agon, keyboard admission and actual remote-command
checks recovered. Final exact full-HDMI snapshot restored/all four segments
verified; P4 HTTP availability awaited before final Agon recovery reset.
Original38-byte startup independently read back,52remote packets accepted,
input ready/neutral, held0/pending0, listener exited. No active bench operation.
EMOS/mainboardVDP/wiring unchanged. No repair or production change. Earlier
unverified-restoration and current-keyboard-status statements above are history.
Evidence: agents/port008-live-qualification/devkit-control-r01/handback.json,
run-result.json, analyzer-summary.json, installation and restoration receipts.

## Corrected current state — post-flash keyboard regression

Keyboard worked BEFORE agent flashing. Post-flash photo shows KEYINPUT receiver
readiness timeout and mainboard fallback. Do not claim present keyboard operation
or a transient failure: those were agent misreadings. Full-HDMI flash readback
passed, but input restoration is NOT established. Historical comparison has sent
no payload. Further bench operations remain paused pending Author direction.

## Current pause — historical comparison not yet run

See [historical comparison](docs/tasks/PORT-008/DEVKIT-CONTROL-R01.md).
Standalone receiver flashed/verified, but no record armed or payload transferred.
Agent launcher text-mode startup comparison failed and returned15 (“Volume
timeout”); corrected launcher compiled but not deployed. Exact full-HDMI snapshot
rollback restored/foursegments verified. Agon SD currently mounted on Lenovo.
Original38-byte autoexec independently read/verified there, both commands valid;
no test launch remains. Author photo identifies the startup error as line2 KEYINPUT receiver-readiness
timeout, not syntax. MOS maps its FR_TIMEOUT to “Volume timeout”; not proof of
SD failure.
Agent reset while card-reseat reply pending; no more bench activity until Author
returns card and resumes. Current physical/input state in HARDWARE.local.md.

## New harness context — causal attribution remains open

Author reports roughly doubled P4-PC signal lead length and absent earlier
200–220ohm series data resistors. Signal integrity competes with DMA/publication
and TX configuration as explanation; do not interpret the snapshot as proof
of a software-only fault. Details in the latest snapshot record below and
HARDWARE.local.md. No further bench operation or rewiring performed.

## Latest bounded result — received-buffer snapshot

[Snapshot result](docs/tasks/PORT-008/DATA-SNAPSHOT-R01.md): P4 retained RX
fingerprint is already wrong before echo, while first/last16 bytes match.
Return D7 is low throughout first byte despite stored `ff`, so review TX
DMA/output too. Exact3456 clocks bothways; no remedy started. New full-HDMI
P4 data-r02 verified; same EMOS/mainboardVDP/startup/MOSlet. One run, no replay.
Startup verified, listener exited, input ready/neutral; bench idle/released.
Evidence agents/port008-live-qualification/data-snapshot-r01, current installation
and unchanged probe map in HARDWARE.local.md. Earlier checkpoints historical.

## Latest bounded result — clock and handshake capture

[Pinwalk r02](docs/tasks/PORT-008/PINWALK-R02.md): exact3456 payload clocks in
both directions; READY low throughout, one clean VALID interval each. Four
observed reverse bits match; D7 is wrong early, including entire first byte
cycle before Agon samples. Focus next review on P4 receive/storage/transmit;
no remedy started. Same firmware/fixture; no flash/startup edit/replay.
Missing mainboard SD was physically reseated, restoring input. Startup verified,
listener exited, input ready/neutral. Complete trace under ignored
agents/port008-live-qualification/pinwalk-r02; current probe map in HARDWARE.local.md.

## Latest bounded result — data pinwalk

[Eight-data-line pinwalk](docs/tasks/PORT-008/PINWALK-R01.md): all forward
wire mappings match; reverse waveform/readback corrupt. Existing fixture adapted
to EMOS-owned transport; no firmware/startup changes. Input ready/neutral,
listener exited, capture closed. Author controls next probe moves.

## Latest checkpoint — full-HDMI parallel data-only comparison

Author requested latest working full EDP/EMOS base without special transport
diagnostics. P4 port-008-data-r01-b2026-10-10-03-07-07Z installed/four segments
verified; existing latest verified EMOS retained; mainboard VDP unchanged.
No PCNT or private phase/pattern tracing. One-byte echo passes;255 bytes complete
both directions but returned byte3 differs.4096unrun; no uncertain replay.
Separate recovery resets restored input; original startup verified, listener
exited. Result docs/tasks/PORT-008/DATA-ONLY-CONTROL-R01.md. Production unchanged.
Earlier installed-image statements below describe preceding checkpoints.

# Returning developer / external-agent orientation

Documentation checkpoint: 2026-09-25 UTC. Begin with [README](README.md) and
[using an existing installation](docs/using-extender.md). Read the tracked `AGENTS.md` and the canonical workspace instructions it
references before work. Machine-specific bench configuration remains ignored. [TODO](TODO.md) owns
unfinished work; this handoff is not a competing task queue.

## 2026-10-09 active development checkpoint

The second authorized repair hour ends 2026-10-10 02:26:35 UTC.
[Current repair result](docs/tasks/PORT-008/LIVE-QUALIFICATION-BLOCK-R04.md)
and its receipt supersede earlier installation/bench checkpoints. P4 fixed-count
RX EOF plus independent PCNT CLOCK/VALID proofs and an EMOS forward-only
inactive preamble now pass physical one- and two-byte forward blocks. Two
fresh-session suite invocations both reject the 255-byte case: DMA reports 255,
PCNT counts 256 qualified clocks and 4 or 10 VALID edges. Seventeen later cases,
including reverse, are not run. Do not weaken exact proof or infer throughput.

Installed private P4 is `port-008-probe-r10-b2026-10-10-01-45-13Z`, fully
flash-verified. Installed EMOS is `agon-emos-v0.1.24-b2026-10-10-01-48-39Z`,
131,017 bytes / 55 free, with complete128KiB ROM readback. Mainboard Pingo VDP and
production remain unchanged. This private P4 is browser-output, not HDMI.
Original 38-byte startup and ordinary keyboard input have been recovered and
verified after each failed fixture. Retained batches are evidence, not retry scripts.

A separate warm Agon reset ambiguity was reproduced with actual boot adapters.
A proposed paired correction failed a reset-at-phase-3 counterexample and was
preserved under ignored `warm-reset-fresh-candidate`, then removed from maintained
source. The compiled EMOS-only candidate
`agon-emos-v0.1.24-b2026-10-10-02-17-41Z` uses 131,035 bytes / 37 free and is
NOT installed or qualified. Do not install it. The restored existing 736 paired
boot-adapter cases pass; the new counterexample remains a separate reproduction.

LC03-B/F03 remain open; no formal ExExt, ordinary parallel VDU or SD integration.
Emulator-coupled source remains uncommitted pending Author validation. Preserve
unrelated HOST-001 and EMOS application_peer work; older evidence is frozen.

## Current recorded position

1. EMOS v0.1.19 removes the cancelled external `.emo` loading machinery while
   retaining resident input, display and gateway services. Prefixed utilities
   load from `/emos`. [Implementation and physical deployment](docs/tasks/AUDIT-008/HARDWARE.md)
   record exact identities, ROM readback and the bounded checks; broader human
   gameplay acceptance is not implied.
2. The listener is an EMOSlet at `/emos/sdserve.bin`, invoked as
   `EMOS sdserve [--fast] /`. Both listener and host upload must opt into fast
   mode. [Current SD instructions](docs/mainboard-sd.md) supersede old `/mos`
   installation and bare `sdserve` examples. The ordinary application fallback
   remains separate.
3. P4 physical USB, browser capture and host keyboard automation exist.
   [Keyboard ownership](docs/remote-keyboard.md) applies in Legacy and ExCom.
   Remote typing requires Extender input to be admitted already; do not ask an
   agent to enable its own disabled path through that path.
4. The [current local bundle](production/README.md) selects accepted P4 r55,
   EMOS v0.1.19 and sdserve v0.2.0 with pinned host tools. Browser output requests
   full-frame RLE2/packed compression, not inter-frame differencing. Clean builds
   include the selected composition and validate both bootloader/application
   silicon settings. The earlier r01 package is non-deployable historical evidence.
5. Remote reset uses the separate Pi bridge described in the
   [reset guide](docs/bench-reset.md). It is neither a P4 reset nor a power cycle.
6. [AUDIT-009](docs/tasks/AUDIT-009.md) is reconciling documentation. Its inventory
   distinguishes reviewed procedures from unreviewed historical material. Do not
   infer full-documentation acceptance from this orientation update.

## Before bench work

Consult ignored `HARDWARE.local.md` and the latest applicable deployment receipt
for installed artifacts, owner and endpoints. Do not infer the live state from
this handoff or checkout HEAD. Read [bench constraints](docs/qualification/bench-constraints.md)
and [SD placement](docs/sd-layout.md) before fixture execution or deployment.
Observe current authorization and other agents' bench ownership.

Earlier handoff snapshots remain in Git history. Their installed-build claims,
uncommitted-work lists and startup descriptions were dated observations, not
current instructions. No firmware or hardware was changed for this documentation
checkpoint.
