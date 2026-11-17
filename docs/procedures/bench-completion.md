# Bench host process evidence

The host supervisor records process results directly. For Olimex custody,
physical handback and response to failures, follow the
[bench procedure](../operations/olimex-bench/README.md).

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

## Wake the owner when background work ends

For a background bench operation, arrange a bounded supervisor and an
owner-thread wake-up on **both success and failure** before launch. The
supervisor retains its actual terminal result and log; the notification must
direct the owner to those records and must not claim the bench was released.
Use a unique delivery ID and retain the sender's receipt. Do not blindly retry
an uncertain send; inspect the delivery receipt and recipient state first.

For example, the VDPlet owner's existing wrapper can wrap an already-bounded
supervisor (replace all placeholders with the current run's actual values):

```sh
python ../agon-vdplet/tools/notify_bench_completion.py \
  --thread OWNER_THREAD_UUID --delivery-id UNIQUE_RUN_ID \
  --log /absolute/path/to/new-supervisor.log -- \
  /absolute/path/to/bounded-supervisor ARGUMENTS
```

The wrapper records the supervisor's exit and log, invokes the maintained
`pi_chat.py send --resume` for the owner, and retains a notification receipt.
Its success and failure paths have offline verification. For the Olimex
operator’s response to any result, use the linked bench procedure.
