# AUDIT-009 — First bounded documentation pass

## Outcome

The approved unattended pass establishes a [current handbook](../../README.md)
for humans and agents. Routine operation no longer starts with dated task
amendments: use [Using Extender](../../using-extender.md), then the maintained
SD, keyboard, reset/recovery and protocol guides. The same rule now governs
future documentation changes. Historical evidence remains separate; no frozen
experiment is silently reclassified as a current deployment recipe.

**The full audit remains open.** This pass prioritizes external-agent operation
and current contracts within the Author's one-hour allowance. Inventory and link
coverage are not body-review coverage. No code, firmware, hardware, SD contents,
network endpoint or emulator state changed. Changes are committed locally;
publication was not part of this execution contract.

## What changed

| Subject | Result |
|---|---|
| Entry points | Compact root README/HANDOFF, one handbook index, shared operating and build guides; local agent instructions point to the same authorities |
| SD transfers | Current `/emos/sdserve.bin`, prior keyboard admission, checked/fast pairing, journals, foreground return and open-file limits; corrected exact FINISH/ACTIVATE/readback claims |
| EMOS | Current resident ABI replaces cancelled loader prose at its stable path; current utility/SD documentation and integration summaries reconciled |
| Browser/control | Current input arbitration and platform limits, one video wire authority including retained codec extensions, distinct video and keyboard ownership |
| Reset/recovery | Supported Pi reset separated from ROM recovery; maintained recovery requires verified durable pre-erase dump and full post-write comparison |
| Evidence/status | Old instructions removed from current manuals; frozen procedure reuse limits and later task dispositions explicit; no blanket new acceptance |

## Coverage

Inventory excludes the audit's own bookkeeping documents. It includes newly
promoted guides, relevant help producers and a few explicitly identified local
operational records. Vendor/archival classification is not verification of all
its contents. Every record has a disposition in [INVENTORY.csv](INVENTORY.csv).

| Review state | Extender | EMOS | Total |
|---|---:|---:|---:|
| Current body reviewed within recorded scope | 28 | 9 | 37 |
| Partially reviewed / selected claims only | 25 | 12 | 37 |
| Historical metadata classified, body not reviewed | 116 | 22 | 138 |
| Vendor/reference provenance role only | 29 | 0 | 29 |
| Pending body review | 794 | 67 | 861 |
| **Inventory total** | **992** | **110** | **1102** |

Thirteen bounded batches and two documentation-only reader walkthroughs are
recorded in [CHECKS.md](CHECKS.md). Reviewed means the document's stated contract
was inspected against the sources/evidence listed there; it is not a fresh
hardware or independent fresh-machine acceptance.

## Checks and limits

1. Local SD/keyboard/screen-text/recovery CLI help succeeds. Examples were
   inspected against parser/source; no endpoint contacted and no build executed.
2. Qualification generator reproduces all 17 tracked outputs using the
   documented virtual environment. Its superseded mode candidate remains
   superseded. Canonical dependency-graph validation passes for its own reviewed
   baseline, not the installed P4 overlay chain.
3. Relative Markdown destination/anchor scan finds no new broken links in
   revised current guidance. Three predecessor-hardware targets and fourteen
   migration-handoff targets remain historical defects, explicitly inventoried.
   Existing ignored-file targets in revised tracked guides were also checked;
   the public handoff no longer links to an untracked AGENTS file.
4. Whitespace and newly added private-path/address checks pass. The aggregate
   version validator still rejects the unchanged held r02 connectivity hash;
   documentation work did not rewrite it or manufacture new acceptance.
5. External HTTP destinations, all Markdown syntaxes, every historical body,
   fresh public-clone reproduction and macOS execution were not requalified.
   Details and scan totals are in CHECKS; this is not an exhaustive link proof.

## Remaining consequential issues

| Finding | What remains | Existing owner |
|---|---|---|
| F009 | Base P4 builder does not reproduce the deployed snapshot/overlay combination; a clean public rebuild is not established | PORT-003 / build owner; implementation contract required |
| F008 | Accepted 30-fps normal contract and authorized 60-Hz retained experiments need final configuration/policy reconciliation | QUAL-003 / BENCH-005 |
| F019 | Retained timing runner selects mode in EXEC and uses the ordinary listener fallback; refresh procedure before reuse | BENCH-007 |
| F020 | Frozen SD qualification r01 predates current EMOSlet/reset operation; refresh before another qualification | REMOTE-005 / SD qualification owner |
| F024 | Held r02 hardware connectivity digest mismatch predates audit | HW-002 / hardware-version owner |
| F012, F016 | Historical cross-references need provenance repair; current handbook does not depend on them | Hardware archive / EMOS migration record owners |

[FINDINGS.md](FINDINGS.md) records all 27 findings and their dispositions.
Assigning an owner or exposing a gap does not authorize a fix or bench run.

## Exact continuation

Continue the existing A09-04/05/06/08 work items; do not create a replacement
queue or restart inventory. Next bounded batch: finish `docs/architecture.md`
against `docs/architecture/vdp-upstream-precis.md`, `docs/decisions/README.md`,
`hardware/README.md` and SETUP-005's accepted decision register. Reconcile current
claims only; qualification and actual implementation remain separate. Consult
source only for the contract being checked, then update the inventory/findings.

After that, review remaining maintained procedure entry points for obsolete
execution instructions, then remaining task/evidence statuses using PLAN-001's
queue review as the baseline. Do not read every archived transcript before
classifying it. Preserve the current handbook/evidence separation and finish
each bounded batch with links, walkthrough implications and honest coverage.
