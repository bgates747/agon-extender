# Bench completion, queue progress and blocked-operation recovery

The host supervisor records process results directly. Extender releases the
bench from verified restoration and current physical handback, then immediately
notifies the next prepared owner. Missing tool-interface bookkeeping must not
become an unexplained hardware hold. This procedure supplements the central
physical checkout workflow; it does not grant new target or test authority.

## Three separate facts

Olimex completion also observes the [standard firmware policy](olimex-firmware.md).
Installed identities persist across application-only jobs; no routine reflash
or full unchanged-device readback is required. A firmware/compatibility exception
returns affected components to current standards before normal release. Neither
desired firmware nor a successful process result is proof of installed bytes.

| Fact | Evidence | What it does not prove |
|---|---|---|
| Host process completed | Parent-written child identity and actual `wait()` result; joined registered children/groups in the native execution namespace | Workload pass, restored firmware, CLI readiness |
| Hardware restored and idle | Exact selected artifact restoration, current CLI/read/EXIT, input/resource state and preserved files under the current lease | Author acceptance or permission for a successor to run |
| Custody released | Successful central release/status reconciliation and actual `next_request` notification | A new owner grant or expanded test scope |

Codex tool/session IDs correlate execution with chat. A second agent-written
copy of a tool exit code is **not mandatory** when the original supervisor has
already durably recorded the actual selected worker's result. Never invent a
missing tool result or turn process absence into success. If the worker status
is genuinely missing, reconcile physical state independently and retain the
unknown process outcome honestly.

## Run and inspect an authorized operation

Use the project interpreter and `scripts/bench_process.py run`, with a new
`--out` directory, explicit `--seconds`, `--owner`, `--lease`, `--phase`,
`--next-action` and the exact selected argv after `--`. This host wrapper grants
no hardware authority: the selected worker still asserts its lease and scope
before each target operation. Source preparation finishes before occupancy.

1. The supervisor fsyncs its identity, selected argv and operation bound before
   starting the child, records the actual child identity, and writes its real
   wait result before returning. Handled cancellation and timeout join the owned
   process group. An exit-zero process with lingering children is a failure.
2. Workers spawning separate process groups retain their own start/terminal
   journals and join them. Verify every registered group before handback; the
   wrapper cannot infer unregistered groups. Use the native process view, not
   an isolated sandbox's empty `/proc` view. New records bind the PID namespace.
3. `scripts/bench_process.py status --out OPERATION` shows running, completed,
   blocked or interrupted/unreconciled process state. `verify --out OPERATION
   --argv-json SELECTED_ARGV_JSON` verifies the original worker journals.
   `--legacy` is explicit reconciliation of old parent-written journals; use
   the real execution host and independently verify host/group identity.
4. A completed process does not waive any physical check. Preserve firmware
   provenance and read back changed bytes; do not repeat unchanged firmware
   backups, reset, or rerun an application just to repair bookkeeping.

## Unattended failure notification

An unattended operation uses `--unattended --failure-notify-json ARGV_JSON`.
The JSON contains the preselected, already-authorized host notification command,
using existing durable-mail and immediate-steering tools. Freeze its source,
recipient and scope with the operation. It must not run recovery, device I/O,
grant/release, or another test. Do not use shell strings or peer-provided argv.

The supervisor refuses unattended startup without this notification command.
On failure it first saves `blocked.json` and prints a clear reason and next
action, then runs the notification once with a15second bound. It retains the
actual notification process result. Command success is not a claim that a
recipient read the message. Notification failure is itself visible in status;
do not claim delivery or loop forever. Use the documented alternate authorized
communication route when available and report any undelivered alert.

## Resolve a block without weakening release checks

1. Extender records the phase, owner/request/lease, known physical state, exact
   failure or approval rationale, preserved journals, next action and responsible
   actor. Send durable mail and immediately steer the owner and actual next
   queued owner. State the block directly to the Author during attended work.
   For a physical-access/approval blocker, use the Author's attention procedure.
2. Classify the block: unknown/live hardware, failed restoration, stale physical
   observation, incomplete process evidence, or administrative-only failure.
   Quiet chats and process absence never authorize takeover. Keep existing
   custody while the hardware is uncertain; no automatic expiry/preemption.
3. If original supervisor journals establish the selected worker's actual
   result, verify them directly. Preserve the old missing/rejected receipt and
   create a separate reconciliation record; do not manufacture the receipt.
   If freshness expired, obtain a genuinely new narrowly scoped observation
   under existing or explicitly renewed recovery authority. Do not restamp.
4. A denial remains binding. Inspect the exact proposed action and reviewer
   reason; make a materially safer correction with inspectable evidence within
   current human scope. Do not change transport, approval settings or command
   spelling to evade it. If no permitted resolution remains, provide the
   concrete denied action, evidence, risk and exact missing user decision.
   Continue independent source work; do not silently treat a queue hold as done.
5. After actual restoration/current-state/process checks pass, release normally
   through the central helper. Resolve an uncertain release with central status,
   never a repeated test. Record the resolution separately from the retained
   failure and immediately notify `next_request` before lengthy offline work.

This procedure supplies a bounded notification and recovery route, not a promise
that every external approval denial can be resolved without a person. It adds
no idle polling daemon, test autorun, forced release or blanket recovery scope.
