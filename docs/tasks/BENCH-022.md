# BENCH-022 — Audit recent Olimex runner reliability

**Three shared runner corrections approved.** See the [findings and recommendations](BENCH-022/FINDINGS.md) and [phase ledger](BENCH-022/PHASES.md). The approved scope was frozen and pushed at `11d2a5d396c04091db2c20e9bbaa4f406f76dfdd`.

**Original scope.** Extender will determine where recent Olimex jobs
stopped and which recurring needs the shared runner should cover. Compare
first-attempt successes and failures against actual commands and receipts.
Return findings, ranked changes, and proposed approval wording for custom
runner code. The first tranche reviews retained evidence.

## Starting evidence

- **VDPL-057 exposed a shared feature gap and two adapter defects.** Smith
  wanted the fixture preloaded so he could type only `RUN`. The shared
  run phase issues both commands. The job-specific adapter passed text
  markers to a bytes parser after successful INSTALL, then reused a
  receipt name after a successful restart. The shared path already encodes
  markers, and the evidence writer correctly refused to overwrite the
  original receipt. The choice to reproduce the app1 SD OTA path added
  orchestration beyond preloading. [VDPL-057 task](../../../agon-vdplet/docs/tasks/VDPL-057/TASK.md)
- **Standardization introduced two confirmed regressions in rehearsal.**
  A programmer failed to reconnect after the runner split verification
  and writing across serial sessions. A P4 adapter rejected a flash-size
  reading the stock tool could handle. Both were corrected. Compare
  later failures against Extender’s proven methods and the exact revisions
  operators actually ran. [Cold rehearsal evidence](BENCH-020/EVIDENCE.md)
- **The recent failures have different signatures.** OLX-06 passed the
  stock SD OTA round trip and F060 startup. It exposed a case-sensitive
  command error, a missed post-update MOS prompt, and separate USB
  programmer first-sync failures before flash access. FLY-07 lost keyboard
  admission before Escape was sent, and its cause remains unresolved. The
  available records do not establish a hardware reliability trend.
  [OLX-06](../../../agon-fsim/docs/tasks/PINGO-083/STOCK-OLIMEX-06.md) ·
  [FLY-07](../../../agon-fsim/docs/tasks/PINGO-083/FULL-FLIGHT-OLIMEX-07.md)

## Review process

- BENCH-022-001 [x] After Smith reviews the draft, freeze the audit scope
  in Git and publish it. Inventory Olimex jobs from November 12 through
  this request on November 19, 2026, in Eastern time. Start with
  Extender’s own production and custom firmware jobs, VDPL-057, FSIM
  OLX-06 and FLY-07, and the recent Nurples visual runs. Use reservation
  and check-in records to find other jobs and operators. Include passes,
  failed attempts, retries and jobs stopped before target access. Mark
  earlier comparison runs separately.

- BENCH-022-002 [x] Build a ledger from each job’s exact commands,
  checkout and runner revisions, tool versions, firmware tuple, manifest
  and parent-written receipts. For each relevant phase record whether
  shared or job-specific code ran, the first-attempt outcome, the last
  proved target action, elapsed time where available, recovery and final
  handback. Keep original failures and recovery outcomes separate.
  Link the evidence, mark missing fields, and keep machine-local bindings
  and raw captures in their existing ignored locations.

- BENCH-022-003 [x] Ask each recent operator with gaps in the records
  one consolidated question. Request the missing evidence, exact deviation
  from the shared procedure, reason for the deviation, first failure, and
  workaround or recurring need. Record unknowns and missing responses.
  Operators provide technical details. Use scheduler records for
  inventory while preserving the scheduler’s FIFO-only role.

- BENCH-022-004 [x] Trace each first failure to the instruction or code
  path that selected the operation. Compare the command, programmer
  session, reset order, observer and completion criteria with an
  applicable proven predecessor. Classify each as shared runner or
  guidance, job-specific adapter, fixture or firmware, transport symptom,
  or unresolved. Distinguish a target failure from a host failing to
  observe a completed action. Count failed first attempts over recorded
  first attempts by comparable phase and revision. Show missing receipts
  and unmatched workloads separately. If the USB sync records lack a
  comparable baseline, describe a separate read-only control with fixed
  wiring, firmware and starting state for Smith to consider.

- BENCH-022-005 [x] Rank the consolidation candidates. For each, name
  the jobs that needed it, any shared helper already available, the
  smallest supported interface, failure handling, and qualification
  evidence needed. Identify cases that can use the existing runner
  directly. Retain one-off recovery adapters with their original
  evidence. Return the ledger, conclusions with evidence limits, ranked
  recommendations, and draft policy wording to Smith.

## Recommendations for review

- **Add a shared preload-only phase first.** Reuse the command-correlated
   Legacy prompt and `LOAD` checks. The operator stages the pinned
   files, selects the manifest’s working directory, preloads at the
   pinned address and verifies the prompt. The worker writes a joined
   preload receipt. Smith enters `RUN` and reports his verdict and
   return of control in chat. The operator follows the normal restore
   and handback procedure. Keep the human verdict distinct from the
   host receipt. A focused offline check should prove the phase sends
   only `LOAD` for the fixture, refuses readiness without both a
   confirmed load and prompt, and preserves the first failure.
- **Reuse shared observer and evidence handling.** Use the shared
   runner directly for ordinary phases. When multiple observations
   are needed, give each CLI check a distinct label and preserve the
   append-only receipts. Use the retained VDPL-057 transcript and
   receipt collision as offline cases for any change to these interfaces.
- **Consider SD OTA and app1 as an explicit later option.** If the
   audit shows recurring need, start from the proven OLX-06 sequence.
   It needs separate scope and qualification for slot and image
   verification, stock table preservation, exact store ownership and
   cleanup, and production rollback. Keep direct app0 programming as
   the ordinary path.
- **Require approval before writing custom runner code.** Proposed
   authoring-guide wording. Use the shared runner, normal manifests and
   documented phase commands for routine jobs. When a job needs
   executable orchestration outside the supported runner, stop before
   writing or modifying it. Bring Smith the missing action, the
   existing feature checked, and the smallest proposed scope and
   validation. This covers job-local wrappers and inline automation.

## Inputs and review boundary

Start with the [bench procedure](../operations/olimex-bench/README.md),
[authoring guide](../operations/olimex-bench/AUTHORING.md), [shared
runner](../../scripts/olimex_bench.py) and [CLI observer](../../scripts/olimex_cli.py).
Use Extender’s mailbox report `vdpl057-runner-failures-smith-followup-one`
to find the VDPL-057 task and original receipts. FSIM and Nurples retain
their own task and run records. [BENCH-020](BENCH-020.md) records the
instruction cutover, [BENCH-021](BENCH-021.md) the transfer policy, and
[BENCH-010](BENCH-010.md) the earlier reset and serial-open diagnostics.

Smith authorized the evidence review and operator consultation. Bring the
findings to Smith before changing runner code or bench policy. Hardware
tests and commissioning are outside this audit.
Close the audit once Smith has the ledger, evidence-backed findings and
a disposition for each recommendation.

## Disposition

Extender completed the inventory, phase ledger, operator consultation, attribution and ranked recommendations. Smith’s disposition of the recommendations is pending. No runner or operating-policy changes or physical controls were executed.

## Approved implementation tranche, November 19

Smith selected recommendations 1–3. Keep the separate USB first-sync
investigation deferred. Its cause remains unknown. Stock SD OTA/app1
and the proposed custom-runner approval rule remain separate decisions.

- BENCH-022-006 [ ] Add an explicitly invoked recovery route for a proved
  failed, joined phase. Bind the operator, original packet, successful
  predecessors and absent successors. Restore only proved changed components
  through the ordinary verifier and finish with the ordinary handback.
  Preserve the original failure and refuse uncertain writes or live actors.

- BENCH-022-007 [ ] Support stage-only and preload-only human-start jobs.
  A preload requires one observed LOAD and the returned working-directory
  prompt. Smith runs the fixture and reports the result and return to MOS
  in chat. Use the ordinary production restore and check-in afterward.

- BENCH-022-008 [ ] Preserve the keyboard admission sample on failure.
  Bind distinct CLI observations, validate marker inputs before dispatch,
  and verify the needed runtime/interpreter before target work. Update the
  curated operator and author guides. Exercise the normal entry points,
  failed receipts and saved transcripts offline, and retain the distinction
  between host qualification and qualification on a separately approved real job.
