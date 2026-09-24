# AUDIT-009 — Documentation audit checkpoint

## Outcome

The approved unattended passes establish a [current handbook](../../README.md)
for humans and agents. Routine operation no longer starts with dated task
amendments: use [Using Extender](../../using-extender.md), then the maintained
SD, keyboard, reset/recovery and protocol guides. The same rule now governs
future documentation changes. Historical evidence remains separate; no frozen
experiment is silently reclassified as a current deployment recipe.

**The full audit remains open.** Two bounded passes prioritize external-agent
operation, current contracts and applicability within the Author's separate
one-hour allowances. Inventory and link
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
| Architecture/hardware | Working service boundaries separated from future requirements; held r02 isolation not applied to active direct r03; Legacy SD admission reconciled |
| Procedure/example reuse | Current applicability indexes; old fixed-path and application-listener helpers require owner refresh; relative-output fixture instructions corrected |
| Evidence/status | Old instructions removed from current manuals; frozen procedure reuse limits and later task dispositions explicit; no blanket new acceptance |

## Coverage

Inventory excludes the audit's own bookkeeping documents. It includes newly
promoted guides, relevant help producers and a few explicitly identified local
operational records. Vendor/archival classification is not verification of all
its contents. Every record has a disposition in [INVENTORY.csv](INVENTORY.csv).

| Review state | Extender | EMOS | Total |
|---|---:|---:|---:|
| Current body reviewed within recorded scope | 45 | 9 | 54 |
| Partially reviewed / selected claims only | 42 | 12 | 54 |
| Historical metadata classified, body not reviewed | 118 | 22 | 140 |
| Vendor/reference provenance role only | 44 | 0 | 44 |
| Pending body review | 746 | 67 | 813 |
| **Inventory total** | **995** | **110** | **1105** |

Twenty-one bounded batches and two documentation-only reader walkthroughs are
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
| F035 | Fixed-path examples and old qualifier/service handovers need code/procedure refresh before reuse | PORT-003, REMOTE-002, DEMO-001 |
| F024 | Held r02 hardware connectivity digest mismatch predates audit | HW-002 / hardware-version owner |
| F012, F016 | Historical cross-references need provenance repair; current handbook does not depend on them | Hardware archive / EMOS migration record owners |

[FINDINGS.md](FINDINGS.md) records all 36 findings and their dispositions.
Assigning an owner or exposing a gap does not authorize a fix or bench run.

## Exact continuation

Continue existing A09-04/05/06/08; do not restart inventory or create a competing
queue. The recorded architecture/procedure batch is complete within its stated
scope. Next bounded batch: current capability/task summaries for PORT-006,
MODE-001, MODE-002, DIAG-001, PORT-004, PORT-005, PORT-007, P4PC-001, LINK-001 and
QUAL-001, using accepted architecture and current guides as already-reviewed
inputs. Reconcile future requirements versus implemented coverage; do not
reopen accepted decisions or start deferred implementation.

Then review remaining pending maintained documentation by role, consulting
source only for the claim at hand. Historical transcripts and generated/vendor
material need explicit provenance/disposition, not implied body review. Finish
each bounded batch with link checks and honest inventory coverage.

## Second-pass local verification

No source, tool, firmware, SD, network endpoint or emulator changed. EMOS had
no new edits during this pass. Hardware-object validation passes for 41 objects;
all 39 P4-PC original/derivative hashes match provenance. Numeric-runner help
was checked without compiling or running regressions. The current local link
scan covers 712 Markdown files and 2465 links, retaining only the three known
historical hardware missing targets. No new changed-document failure appeared.
The earlier known version-record failure remains unresolved; no frozen digest
was rewritten. Documentation source checks are not fresh hardware acceptance.

The second tranche reached its checkpoint in about 17 minutes, below the
one-hour budget. Local commits separate architecture reconciliation, procedure/
example consolidation, and evidence/status closeout. No push was requested.
