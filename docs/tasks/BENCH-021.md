# BENCH-021 — Audit fast file transfers for Olimex tests

Routine file transfers should use the fast parallel path and skip CRCs and
readbacks. If a test fails, the operator alerts Smith and includes possible
transfer corruption in the investigation. Extender will check what the curated
instructions and runner actually do, and look for evidence of silently corrupted
files before making this the documented default. Smith approved the review on
2026-11-17.

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

- BENCH-021-001 [ ] Trace the current instructions from the curated checkout's
  entry point and sparse path list through the bench procedure, authoring guide,
  worked example, execution guide and linked SD instructions. Record conflicting
  or duplicate directives, including anything that a cold operator can follow
  into an older checked-transfer workflow.

- BENCH-021-002 [ ] Check retained Extender and consumer run receipts for actual
  content corruption on the relevant commissioned hardware and carrier. Start
  with the parallel upload trial, both Wolf upload repair records and the Moon
  Patrol staging failure. Classify a completed transfer with mismatched bytes,
  an aborted or unactivated transfer, a session fault, and incorrect application
  output separately. Identify the applicable firmware and direction, and the
  limits of the evidence. Bring confirmed corruption relevant to the proposed
  default to Smith before updating the operating guidance.

- BENCH-021-003 [ ] Audit the commissioned runner and its reachable SD clients.
  Record the selected listener and actual carrier, local pin checks, wire CRC or
  digest work, post-upload GETs, checks on pre-existing targets, compatibility
  fallback, and the result collection path. Include ordinary and custom firmware
  jobs. Name each policy violation and its source location. Identify the exact
  matched P4, EMOS and listener dependencies for parallel staging and any missing
  runner support. Recommend a disposition for each violation.

- BENCH-021-004 [ ] Update the curated operating instructions and their upstream
  source after the evidence review. Give an operator one clear path to the
  commissioned commands, the no-validation transfer rule, and the failure alert
  and diagnosis procedure. State actual runner and firmware limitations plainly
  so the written policy does not claim support that the selected tools lack.

- BENCH-021-005 [ ] Walk the revised instructions from the sparse entry point for
  a fixture upload, a result collection and a failed transfer or test. Check
  links and consistency with the audited commands. Return the evidence summary,
  runner findings and any implementation dependency to Smith.

## Starting points and boundary

The audit follows the [bench procedure](../operations/olimex-bench/README.md),
its [sparse path list](../operations/olimex-bench/sparse-paths.txt), and the
[commissioned runner](../../scripts/olimex_bench.py). The [SD operating guide](../mainboard-sd.md#parallel-uploads--working-development-trial)
describes the matched parallel trial. The two retained Wolf incidents are
[first repair](PORT-008/UPLOAD-REPAIR-R01.md) and [second repair](PORT-008/UPLOAD-REPAIR-R02.md).
These are starting records for the audit, not a finding about the current default.

The approved tranche covers the documentation review, retained evidence and
runner audit. Physical qualification, firmware promotion and runner
implementation are outside this tranche. The reviewed Git baseline preserves
the original guides and runner. Local run receipts are read-only inputs.
