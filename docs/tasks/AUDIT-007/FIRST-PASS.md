# AUDIT-007 first graphics-backend tranche

## Executive summary

Author authorized this bounded source audit on 2026-09-20 after PLAN-001 T03
selection. Compare stock VDP graphics execution with the current P4 EDP source,
identify concrete retained/adapted/missing behavior, and recommend one useful
follow-up. This is a first pass within the exhaustive audit, not its completion.
No product source edits, compilation/deployment, hardware tests, browser
optimization, upstream bug fixes or Aginvadors optimization.

## Frozen contract

**AUDIT-007-A01** [x] Read official graphics documentation and prior AUDIT-006
restoration findings; record exact upstream/docs/vdp-gl and current P4 identities,
including dirty-source limits. Official references remain untouched.

**AUDIT-007-A02** [x] Inventory the upstream vdp-gl source tree and current
vendored selection, marking unchanged/modified/absent units and explicit build
inclusions/exclusions. This file census is not semantic qualification.

**AUDIT-007-A03** [x] Trace current concrete controller selection, native storage,
viewport scroll, clipped bitmap plotting, sprite refresh/composition and buffer
swap/output boundaries. Prioritize actual departure points and no-op branches;
link earlier qualification without treating it as exhaustive parity.

**AUDIT-007-A04** [x] Produce a source-backed gap table separating necessary
processor/output adaptations, existing functionality, confirmed omissions,
previously deferred features and unresolved correctness questions. Report exact
symbols and reproducible source references; do not label an untested suspicion a
confirmed runtime defect.

**AUDIT-007-A05** [x] Recommend one bounded useful next tranche with its owner,
reason and proposed acceptance. Stop for Author review before implementation or
broader exhaustive tracing. Mouse/audio/maintenance deferrals remain intact.

## Completion boundary

Deliver the baseline/census, concise findings and recommendation. Keep AUDIT-007
F01–F07 open where their exhaustive coverage is not achieved. File equality does
not establish identical compile paths or runtime behavior. Current working-tree
findings do not identify installed firmware without deployment evidence.

## Delivery

Completed bounded source pass; see [findings and proposed follow-up](FINDINGS.md),
[source census](SOURCE-CENSUS.md) and [baseline](baseline.json). The proposal
remains subject to Author review; exhaustive F01–F07 are not closed.
