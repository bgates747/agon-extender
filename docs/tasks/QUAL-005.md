# QUAL-005 — Canonical firmware acceptance suite

## State

Accepted on 2026-09-30. The canonical paired-component run passed all 17
mandatory physical checks, and the Author accepted its scope and result.

## Scope and policy

`qualification/` is the sole maintained executable authority for Extender and
EMOS firmware acceptance. Historical task fixtures remain frozen evidence and
do not become recurring acceptance tests unless deliberately promoted into the
canonical manifests.

A firmware revision is not accepted unless one complete run, bound to a verified
flash receipt, passes every applicable mandatory installed-hardware case,
restores startup state, and writes a durable summary. The offline source suite
is a separate development regression and is not repeated during hardware tests.
Zero selected hardware cases, an offline-only pass, or a flash receipt alone can
never satisfy this gate.

## Work items

- [x] Q05-01 — Create the role-named `qualification/` authority.
- [x] Q05-02 — Move maintained manifests, runners, notifier and their structural
  tests under that authority; retain thin old-path compatibility launchers.
- [x] Q05-03 — Add a mandatory integrated installed-hardware smoke covering P4
  web assets, browser reset, P4-to-EMOS keyboard input, ExCom display/capture,
  mainboard-SD round trip and startup recovery.
- [x] Q05-04 — Preserve the destructive EMOS raw-SD repair case as a separately
  applicable mandatory physical case.
- [x] Q05-05 — Make empty physical selection an error and mark every canonical
  hardware-manifest entry acceptance-required.
- [x] Q05-06 — Publish the acceptance rule in current testing, handbook,
  production and versioning documentation.
- [x] Q05-09 — Separate installed-firmware qualification from the offline source
  suite so physical retries neither rebuild unrelated commits nor repeat passed
  host tests.
- [x] Q05-10 — Require paired P4 and EMOS installation receipts for a full run;
  expand the ordinary-firmware suite to 17 named checks including fresh decoded
  WebSocket frames and the destructive/restored EMOS raw-sector oracle.
- [x] Q05-07 — Run the canonical suite against the currently verified P4 and
  EMOS pair and obtain Author acceptance of its physical behavior.
- [x] Q05-08 — Correct the first physical run's command-ordering defect: use
  fresh screen captures as parser-progress barriers and require observed ExCom
  transition plus the unique marker before starting the SD-service stage.

## Boundaries

The canonical suite does not silently absorb historical QUAL-003 visual and
performance tours or QUAL-004 diagnostic-firmware pixel comparison. Those
procedures require special firmware, private adapters, human judgment, or a
different timing purpose. Promote a bounded case only after making it safe and
repeatable for ordinary installed firmware.

Loaded-asset mode-switch cases such as Nurples remain the agreed manual tail of
the audit cycle. Their manual disposition must be recorded before accepting a
revision when the changed code can affect that behavior.

## Accepted run

The accepted run used P4 commit
`9537350a59a2d7b7f6ab359190ea04d1aec89c10` and EMOS commit
`8ecea5bc6cb4f9f563bc570316afbdaa08648632`. Both physical cases and all 17
required checks passed; startup restoration and notification also passed. The
retained local summary is
`agents/hardware-validation/qualification-2026-09-30-02-23-05Z-8ecea5bc-9537350a/summary.json`,
SHA-256 `db60257fd4fad20e89a41990ccdff44953a2877bb4b63c87abfc89a908aef4d5`.
The Author then ran Nurples manually in ExCom: mode switching and gameplay
passed at an observed 25–29 frames per second. This satisfies the loaded-asset
manual tail for the present audit stage; it is not a general performance target.

The first Q05-07 attempt passed all 55 offline cases but was classified as an
infrastructure failure because the runner sent consecutive commands after
transport acceptance without waiting for EMOS execution. Its capture retained
the prior Legacy screen and lacked the marker. This was a runner synchronization
defect, not a firmware failure; Q05-08 preserves the failure and its remedy.

The second attempt proved every ExCom synchronization gate, including the
unique captured marker and returned prompt, then failed because the runner tried
to launch the mainboard SD listener while EMOS still owned ExCom. The listener
correctly remained offline. The runner now performs `EMOS LEGACY` and completes
a fresh capture as a parser-progress barrier before issuing `EMOS sdserve`.

The third attempt passed through listener startup, fast upload activation and
exact download, then failed only because the runner used the optional protocol
directory/remove capability absent from the installed production listener. The
runner now exits the listener, deletes its owned temporary file through MOS's
independent `DELETE` command, restarts the listener, and requires a remote
not-found result before recording cleanup success.

The fourth attempt again passed the transfer and reached cleanup, but injected
the cleanup listener command immediately after `DELETE`; P4 accepted both input
batches while EMOS had not yet returned to its prompt, so the listener never
started. The runner now completes a fresh screen capture as the same bounded
parser-progress barrier already proven by the Legacy handoff before launching
the cleanup listener.
