# BENCH-010 — Paired-reset admission and USB capture reliability

## Executive summary

Fsim reports that an Agon-only reset did not restore Extender keyboard admission,
while a P4 reset followed by Agon reset did. Later, both programming USB devices
disconnected and the mainboard serial reader failed. The first completed game
result remains valid, but its UART render counts were lost. Investigate these
as separate observations; a common cause is not established. The Author requests
this task now, for investigation soon. No diagnosis or repair is performed here.

**State:** Proposed, high priority after the current indexed/PPA deployment stop.
Execution requires fresh Author authorization and an available bench.

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
