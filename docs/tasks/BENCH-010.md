# BENCH-010 — Paired-reset admission and USB capture reliability

## Executive summary

The serial-opening reset is corrected in the maintained host opener: DTR/RTS
now change together instead of briefly asserting Olimex's reset circuit. Three
open/close trials preserved actual keyboard/listener operation, and one normal
100 ms reset recovered input on its first attempt. Installed Pingo2/EMOS/EDP,
startup and wiring remained unchanged. Consumer fsim must adopt the helper;
no speculative firmware patch was needed. Broader USB loss/reset coverage remains.

**State:** Bounded host repair complete; Author review and consumer adoption
pending. See [repair evidence and limits](BENCH-010/SERIAL-REPAIR-R01.md) and
[installed source review](BENCH-010/CODE-REVIEW-R01.md). Earlier dated observations
retain their actual combinations and unresolved broader investigation scope.

## Authorized repair tranche — R02

Author authorized diagnosis/repair and handed over the bench on 2026-10-12.
Preserve the installed Pingo2/EMOS/EDP identities established in R01. Do not
substitute current development HEAD, launch games from startup, or reflash a
component merely to hide a host observer defect.

### B10-R02-01 [x] Establish the serial control-line mechanism

Trace installed pyserial POSIX open and Linux CH341 DTR/RTS handling against
Olimex's common reset circuit. Record exact sources and distinguish an observed
reset trigger from inferred electrical transition. Reconcile first/second-reset
keyboard admission against installed source; retain evidence of ready=true
without functional input.

### B10-R02-02 [x] Implement a maintained passive serial opener

The host must change DTR and RTS together, avoiding the intermediate reset and
boot-selection states of the Olimex circuit. Keep this in a reusable host helper
with explicit failure on unsupported control-line operations. Add a bounded
capture command and regression checks that reproduce the old differential state
and verify the new combined operation. Consumer-specific capture code stays in
its owning project; provide the reusable interface for fsim adoption.

### B10-R02-03 [x] Qualify the correction on the unchanged installed pair

Reserve the bench locally; establish a real harmless CLI/listener exchange and
verify ordinary startup before any deliberate reset. Use at most three corrected
open/read/close trials, with fresh logs and functional CLI/service checks before
and after, without firmware replacement. Record kernel USB control requests if
available without changing wiring. Stop and inspect any unexpected reset or input
loss; no blind recovery loop. Previously observed unsafe opens are the failing
control; do not repeat them merely to reconfirm a disruptive failure.

### B10-R02-04 [x] Resolve or bound first-reset keyboard recovery

After the observer fix, compare a deliberately authorized ordinary reset with
its verified input recovery while keeping the safe collector open. If the prior
failure disappears, record the observer-induced reset distinction and avoid an
unsupported firmware patch. If a normal reset still fails, diagnose its actual
boot/error and repair only the owning source, using the installed baseline as
the candidate parent. A second reset is evidence, not the proposed permanent fix.

### B10-R02-05 [x] Publish the operating correction and hand back

Update the maintained capture/reset guidance and task findings, leave the bench
at an actually qualified prompt with no collector or listener left running, and
report exact tested scope and remaining uncertainty. Preserve frozen captures
and consumer source. No release promotion/version claim without acceptance.

R02 closed with the bounded results above; consumer helper adoption and any
broader qualification remain outside its completed local repair claim.

## Evidence and boundaries

BENCH-010-E01: Fsim's immutable mailbox report is retained in the canonical
cross-agent mailbox under message ID
`2026-10-11_22-55-00_fsim_fsim-flight020-bench-diagnosis`.
Machine-local locations, timestamps, USB identities, current image identities
and access details belong in `HARDWARE.local.md` and the ignored task record.
Fsim owns its campaign evidence under `tests/0065-flight019-renderer-campaign/hardware`
in the sibling agon-fsim repository; preserve its failed capture and recovery
journals. Consumer execution code stays there, per `OWNERSHIP.md`.

1. Fsim observed a changed keyboard epoch but `ready=false` for 40 seconds after
   an Agon-only reset following mainboard VDP installation. Paired resets restored
   admission. This does not establish that ordinary Agon-only resets always fail.
2. The Pi kernel recorded the P4 USB disconnect/re-enumeration, then the mainboard
   CH341 disconnect/re-enumeration. The physical/power/operator cause is unknown.
   The passive mainboard reader exited with a serial exception. Do not label this
   an RTOS, renderer or USB driver defect without evidence.
3. The first completed application result passed all 900 ordered state/camera
   checkpoints and 2700 physics checks, with build/final-state validation.
   The reported 29,362 MOS ticks at 120 Hz equal 244.683 seconds and 3.678 frames/s.
   UART render counts are absent; application success cannot reconstruct them.
4. Fsim stopped its recovery worker and collectors before handover. Its custom
   P1-count mainboard image remains installed; the original P2 image is retained
   but not restored. Preserve this distinction when comparing future results.
5. Extender's subsequent indexed/PPA candidate deployment changes the P4 image.
   A new run must record the actual paired identities rather than present its
   result as reproduction on fsim's unchanged pair.

## Bounded work plan

### B10-01 [ ] Preserve and reconcile the evidence

Read the mailbox report, failed capture, recovery campaign and kernel excerpts.
Build one timestamped table of reset/flash/operator events, USB disconnects,
keyboard admission epochs, reader exits and completed application records.
Separate observed facts from missing evidence; establish the actual firmware,
startup, physical USB topology and bench owner for each interval. Do not replay
fsim's long campaign merely to gather these facts.

### B10-02 [ ] Isolate reset/admission behavior

Use existing reset and keyboard-status tools with an ordinary verified MOS CLI
and unchanged startup. Compare Agon-only, P4-only and paired resets under a small
explicit trial count. Record P4 boot identity, EMOS admission epoch, readiness,
neutral keys, SD ownership and actual command/service admission separately.
Inspect current EMOS/P4 boot-release and keyboard re-admission paths. Determine
whether the mainboard custom VDP is material through a separately authorized
control, not an assumed stock baseline. Stop on ambiguous application state.

### B10-03 [ ] Isolate USB loss and observer behavior

Use existing kernel/udev and bounded passive serial collectors, with device
identity checks. Determine whether reset/flash, cable/power changes or spontaneous
loss accounts for the recorded disconnects. Review collectors for clean failure,
durable partial evidence and stable-identity reconnection. No silent continuation
of a timing run across missing serial data; no automatic reset/replay of a game.
Do not change USB wiring or power without an explicit operator step.

### B10-04 [ ] Propose and implement only the evidenced remedy

Choose the smallest repair in the component owning the fault: EMOS admission,
P4 lifecycle, host observer or physical setup. Review the relevant existing
contracts and fixtures first. Preserve normal UART behavior and existing GPIO
ownership. Record the explanation, affected versions and removal conditions next
to unusual code. Do not bundle renderer optimization or ExExt changes.

### B10-05 [ ] Validate and close the loop

Repeat the bounded failing/control cases on the repaired pair, including ordinary
reset/input and listener readiness. Verify collector failure preserves an explicit
incomplete result. Coordinate any consumer campaign rerun with fsim, leaving its
fixtures and execution code in that repository. Report remaining uncertainty,
update current recovery guidance if warranted, and stop for Author review.
Production promotion requires tested acceptance and an agreed release version.

## EMOS-only rollback checkpoint — 2026-10-11

On explicit Author direction, the Pi restored the physically verified EMOS
`agon-emos-v0.1.24-b2026-10-07-23-11-33Z`, imageSHA256
`44d217b555f68a7d030bc0a89a2fa1d27f0fb537576f2925e90ef055b0a44d02`.
The retained on-card image matched local bytes before FLASH. One FLASH command
was submitted; its automatic reboot produced fresh admitted neutral input.
Independent full128KiB ROM readback matches the selected image plus erased
padding, SHA256`6f83bc21558ea7dcb665b60c18aa3a5c3030367f901e3e32ccbbf99eaf7f4019`.
Ordinary38-byte startup remained unchanged and was readback verified. Listener
exited. P4 indexed r04 and mainboard fsim VDP were not reset/reflashed/replaced.
No post-rollback tests or paired/cold-reset qualification occurred.

This establishes the requested component rollback and immediate input handback,
not the cause of the earlier readiness failure. B10-01–05 remain incomplete.
Author requires ExExt handling to remain irrelevant to Legacy/ExCom startup,
and explicitly rejected substituting a paired P4 rollback to hide coupling.
Local receipts remain in the ignored machine-local bench evidence. Production
selection and release tags are unchanged.

## EDP rollback and stock mainboard VDP restoration — 2026-10-12

Author directed EDP-only rollback to retained port-008-data-r20-b2026-10-11-09-07-32Z. All four segments independently verified; NVS preserved. Post-release keyboard admission timed out (ready=false); Author reports still broken. No listener/test invoked. EMOS remains restored v0.1.24, not reflashed.

Author then directed restoration of official stock mainboard VDP v2.16.0. Retained official release asset firmware.bin SHA256 b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f was checked against the retained release digest, written only at app0 offset0x10000 and independently verified. Bootloader, partitions, EMOS and EDP unchanged. Flash helper reset mainboard VDP; no Agon reset or test invocation. Post-restoration keyboard/CLI behavior is not yet qualified. The custom fsim mainboard VDP is a possible interaction, not an established cause. Evidence: ignored agents/bench010/{edp-rollback-r01,stock-vdp-r01}.


## Reset-only failure reproduced — 2026-10-12

Author cold-powered both boards, powered P4 first, waited five seconds and powered Agon: observed working; HTTP keyboard ready=true, locale1. One authorized reset-only reproduction then reset P4 through esptool, waited measured5.000076513 seconds after command completion and pulsed Agon reset100ms. Keyboard remained ready=false/locale0 through30seconds observation, with a new P4 epoch. Author confirms failure. Stock mainboard VDP v2.16.0, restored EMOS v0.1.24 and EDP data-r20 unchanged. This reproduces independently of fsim custom VDP and indexed/PPA integration. Cold-power versus reset-only initialization is now the focused boundary; root cause remains unknown. No further recovery attempted. Local receipt: agents/bench010/paired-reset-r03/receipt.json.

## Corrected pre-parallel rollback — 2026-10-12

Author rejected data-r20 because it retained parallel-boot integration and directed removal of parallel-enabled bench firmware, with matching EMOS. Restored exact accepted HDMI rgb-001-r10-b2026-10-07-22-56-28Z (source3303bab2185cd2cc86066d0859f515f97431f0be); all four retained segments were hash-checked and independently flash-verified. This is the earlier combination in HDMI-002/R10-PHYSICAL-RESULTS.md, before parallel-boot integration. Matching EMOS is agon-emos-v0.1.24-b2026-10-07-23-11-33Z, already installed and independently full-ROM verified at the previous rollback; no newer EMOS was substituted and no redundant FLASH performed. Stock mainboard VDP v2.16.0 unchanged. Parallel development source is preserved, not deleted.

EDP boot identity confirmed r10 and ordinary UART; post-release keyboard admission returned ready=true/locale1. Attempted SAVE ROM then explicit foreground listener for actual CLI/ROM requalification. Keyboard submissions completed, but listener never became online; later HTTP requests timed out. No fresh ROM download or listener EXIT is claimed. No reset/replay after failure. Startup was not edited; no tests launched. Immediate ready status is not a successful operation qualification. Evidence agents/bench010/pre-parallel-r01. Production selection unchanged.

## Newest verified pre-parallel pair restored — 2026-10-12

Author requested the most modern working builds before parallel startup handling.
EDP r11 `rgb-001-r11-b2026-10-08-01-22-20Z`, application SHA256
`5f1b42a161ec9df13701db3038e06019a27b2880cf608cdcf8eea109670ca13a`,
restored with four independently verified segments and NVS preserved. Retained
r11 source has no parallel boot/release/UART-parking path; it adds320 PPA scaling
to r10's native HDMI carriers. Source snapshot is the authority, not newer HEAD.

Installed EMOS `agon-emos-v0.1.24-b2026-10-07-23-11-33Z` already matches the
pre-parallel cf10f0b Pingo callback source hashes and earlier full-ROM receipt;
no redundant EMOS FLASH. Custom P2-count mainboard VDP retained unchanged.
Corrected host reader retained. Original38-byte startup read back identically
before and after; no tests launched from startup. Actual keyboard/listener/read/
EXIT passed after restoration, returning to LegacyCLI with neutral admitted input
and offline idle SD service. No gameplay acceptance or production promotion.
Local receipts: agents/bench010/nonparallel-restore-r01; installed-current records
updated. This restores an exact historical working baseline, not newer PPA-indexed
or browser features first integrated alongside subsequent parallel development.
