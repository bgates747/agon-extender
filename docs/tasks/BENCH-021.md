# BENCH-021 — Audit fast file transfers for Olimex tests

Routine file transfers should use the fast parallel path and skip CRCs and
readbacks. If a test fails, the operator alerts Smith and includes possible
transfer corruption in the investigation. The review and documentation are
complete. The existing runner still needs a matching parallel staging profile
and implementation. The [audit findings](BENCH-021/RESULTS.md) explain the
runner's history and distinguish the retained failures from corrupted files.

## Scope and policy

- The Pi5 operator stages fixture programs and assets onto the Olimex mainboard
  SD card through the commissioned Extender service. The intended bulk path is
  PARLIO. Routine transfer staging skips CRCs, substitute content checksums and
  pre- or post-upload payload readbacks on either end. Retain ordinary protocol
  completion, filesystem errors and the test's own output checks.
- The operator retrieves the outputs the fixture was commissioned to produce.
  Audit the actual carrier in both directions. The documented parallel trial
  covers uploads, with UART for downloads and a control-only path for empty
  files. Identify which parts of the requested policy the current matched
  profile can deliver and name any gap for the relevant owner.
- If a transfer or test fails, the operator preserves first-failure evidence,
  describes the failure in its own chat and alerts Smith through **Agent has a
  question** under the current bench stop rule. Transfer corruption becomes a
  diagnostic possibility at that point. The scheduler receives routine FIFO
  messages only. Keep the distinction between reading a generated result,
  independently verifying a processor flash write, and rereading a staged
  fixture to check its transfer.

## Review checklist

- BENCH-021-001 [x] Trace the current instructions from the curated checkout's
  entry point and sparse path list through the bench procedure, authoring guide,
  worked example, execution guide and linked SD instructions. Record conflicting
  or duplicate directives, including anything that a cold operator can follow
  into an older checked-transfer workflow. Recorded in the audit findings.

- BENCH-021-002 [x] Check retained Extender and consumer run receipts for actual
  content corruption on the relevant commissioned hardware and carrier. Start
  with the parallel upload trial, both Wolf upload repair records and the Moon
  Patrol staging failure. Classify a completed transfer with mismatched bytes,
  an aborted or unactivated transfer, a session fault, and incorrect application
  output separately. Identify the applicable firmware and direction, and the
  limits of the evidence. Bring confirmed corruption relevant to the proposed
  default to Smith before updating the operating guidance. The reviewed records
  show no confirmed mismatch after activation on the matched PARLIO file path.

- BENCH-021-003 [x] Audit the commissioned runner and its reachable SD clients.
  Record the selected listener and actual carrier, local pin checks, wire CRC or
  digest work, post-upload GETs, checks on pre-existing targets, compatibility
  fallback, and the result collection path. Include ordinary and custom firmware
  jobs. Name each policy violation and its source location. Identify the exact
  matched P4, EMOS and listener dependencies for parallel staging and any missing
  runner support. Recommend a disposition for each violation. Source locations
  and dispositions are recorded in the audit findings.

- BENCH-021-004 [x] Update the curated operating instructions and their upstream
  source after the evidence review. Give an operator one clear path to the
  commissioned commands, the no-validation transfer rule, and the failure alert
  and diagnosis procedure. State actual runner and firmware limitations plainly
  so the written policy does not claim support that the selected tools lack.
  Updated the bench, authoring, execution and SD guides.

- BENCH-021-005 [x] Walk the revised instructions from the sparse entry point for
  a fixture upload, a result collection and a failed transfer or test. Check
  links and consistency with the audited commands. Return the evidence summary,
  runner findings and any implementation dependency to Smith. The document
  walk, link checks, two offline preflights and 15 existing runner tests passed.

## Starting points and boundary

The audit follows the [bench procedure](../operations/olimex-bench/README.md),
its [sparse path list](../operations/olimex-bench/sparse-paths.txt), and the
[commissioned runner](../../scripts/olimex_bench.py). The [SD operating guide](../mainboard-sd.md#parallel-uploads--working-development-trial)
describes the matched parallel trial. The two retained Wolf incidents are
[first repair](PORT-008/UPLOAD-REPAIR-R01.md) and [second repair](PORT-008/UPLOAD-REPAIR-R02.md).
The approved tranche covers the documentation review, retained evidence and
runner audit. Physical qualification, firmware promotion and runner
implementation are outside this tranche. The [audit findings](BENCH-021/RESULTS.md)
record the frozen baseline, local evidence scope and remaining dependencies.
