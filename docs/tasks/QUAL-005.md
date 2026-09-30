# QUAL-005 — Canonical firmware acceptance suite

## State

Active. The Author authorized immediate consolidation after an offline-only run
was incorrectly presented as hardware regression.

## Scope and policy

`qualification/` is the sole maintained executable authority for Extender and
EMOS firmware acceptance. Historical task fixtures remain frozen evidence and
do not become recurring acceptance tests unless deliberately promoted into the
canonical manifests.

A firmware revision is not accepted unless one complete run, bound to a verified
flash receipt, passes the full offline inventory and every applicable mandatory
installed-hardware case, restores startup state, and writes a durable summary.
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
- [ ] Q05-07 — Run the canonical suite against the currently verified P4 and
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

The first Q05-07 attempt passed all 55 offline cases but was classified as an
infrastructure failure because the runner sent consecutive commands after
transport acceptance without waiting for EMOS execution. Its capture retained
the prior Legacy screen and lacked the marker. This was a runner synchronization
defect, not a firmware failure; Q05-08 preserves the failure and its remedy.
