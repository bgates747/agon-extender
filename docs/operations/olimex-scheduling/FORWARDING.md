# Supervised request forwarding and round records

Extender remains the public scheduling inbox during training. A forwarded packet
preserves the original request and direct human scope, so the scheduling agent
does not reconstruct authority from compressed alerts or interpret a forwarded
message as permission for unrelated work. The central registry remains the sole
queue; round records are evidence, not an alternative reservation system.

## Extender-to-scheduler packet

| Field | Meaning |
|---|---|
| Round / assignment | Stable local round name and whether coordination or specifically delegated execution |
| Original mail | Exact message ID/path and original body; immutable parent reference |
| Human scope | Direct instruction or source locator, restrictions and actual delegation |
| Owner / task / request | Existing canonical identities; request null if not reserved |
| Current stage | Proposed, preparing, ready, admitted, running, stopped, restored or released |
| Inputs | Owner plan/manifest, commands/oracles/budgets/restoration, or explicit missing items |
| Live custody source | Canonical registry location; observations do not replace an actual read |
| Responsible contacts | Extender, consumer and technical owner; actual thread IDs in ignored local records |
| Next action | Concrete bounded action and responsible actor, no assumed grant |

Extender publishes the packet as substantive mail to `olimex-scheduler`, then
immediately steers the created thread. The scheduler replies to `linux-extender`
with the same subject/thread and backward mail reference, plus immediate steering.
Both identities share the existing immutable-mail infrastructure; neither edits
the other's published messages or acknowledgement state.

## Scheduler response and running record

1. Intake: actual stage, canonical current occupancy/FIFO and unchanged scope.
2. Decision: one next action, exact reason/evidence, responsible actor, any
   missing technical fact. Do not require blanket reapproval or create extra
   checks without a material missing contract.
3. Execution, if assigned: real grant/token and original clock, operator handoff,
   actual selected argv/parent process journals, pending state and stop boundary.
4. Completion: workload verdict with limits, true wait/join evidence, restoration
   evidence, actual central release and next-owner delivery. Unknown fields stay
   unknown; no synthesized successful receipt.
5. Block: reason, phase, custody, evidence, next action/owner and actual alert
   delivery. Keep the block visible until its disposition is recorded.
6. Review: Extender notes any correction and whether this completed round counts
   toward training. Original failures and earlier incomplete records remain.

## Initial concrete assignment

6502's `perf022-delegated-original-fixtures-prep-one` asks Extender to operate
the forthcoming original Lode/Choplifter/C8 seed fixtures while 6502 develops
new fixtures. At initial intake the package is explicitly not ready, no request
or slot is promised, and the owner asks current component/async/fence/deploy
details. Smith directly assigns that job to the new scheduler as its first job.

First action: acknowledge the assignment substantively, identify the specific
technical questions for Extender, coordinate the prepared package with 6502,
and proceed through normal admission when ready. Neither agent starts another
fixture to fill the wait. No queue grant or physical readiness follows from the
initial preparation mail.
