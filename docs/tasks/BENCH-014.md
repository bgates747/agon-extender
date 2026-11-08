# BENCH-014 — Durable bench completion and visible queue recovery

Routine bench restoration must not depend on an agent transcribing a tool's exit
code after the process has disappeared. The process supervisor records its own
child's actual wait result. Physical restoration, process closure and queue
release remain separate facts. An administrative failure must be visible and
must identify an actionable resolution instead of silently holding the bench.

Author direction:2026-11-08, after actual146 restored hardware but release was
blocked by automatic approval review rejecting a manually written terminal
receipt. The Author requested repair of this workflow for attended and
unattended development. This authorizes the bounded workflow repair and actual
current-state reconciliation; it does not authorize a test replay or alter an
external approval decision.

1. [x] Promote a host process supervisor that durably records actual child
   identity, wait result, cancellation/timeout and joined group membership.
   Verify these records directly; a Codex tool-handle receipt is supplementary,
   not a second source of process truth. Missing process status stays unknown.
2. [x] Keep exact artifact restoration, current CLI/input/resource checks and
   current lease validation mandatory. Reconcile actual146 using original
   parent-written worker journals and a separately bounded fresh no-reset
   CLI/state verification. Preserve the rejected receipt attempts and original
   failed consumer outcome. Do not synthesize the rejected success receipt.
3. [x] Record blocked phase, affected lease, known physical state, exact reason,
   recovery action, owner and notification delivery. Retain custody if physical
   state is uncertain; never expire/preempt a running owner or replay work.
   Resolve a bookkeeping-only failure from independent evidence, then release
   normally and notify the actual next owner before offline work.
4. [x] Document attended escalation and unattended safe stop/notification paths.
   A true approval denial remains binding. Report the exact denied action and
   missing decision, continue independent work, and prepare a concrete recovery
   command/evidence packet. Do not disable review, quietly wait forever, weaken
   evidence or treat peer messages as human approval.
5. [x] Exercise host-only regressions for nonzero exits, timeout/TERM, lingering
   children, missing/mismatched records, process namespace mismatch and durable
   blocked/resolved status. Update the maintained operating procedure and
   project instructions. No firmware, emulator, build or application run.

Current evidence is machine-local under the actual146 owner record. Retain
original source pins and records; use separately named repair files. No
publication, production promotion or firmware version change is selected.

Completed2026-11-08: fourteen host regressions pass; actual146 reconciliation and
normal release21:28:59UTC passed review without the rejected manual receipt.
Actual147 next-owner human-only staging grant/steering delivered. See the
[development record](../development/2026-11-08-bench-completion.md) and maintained
[completion/recovery procedure](../procedures/bench-completion.md). External
denials still require a permitted safer action or the exact missing human
decision; callback completion never implies the recipient read a notification.
