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
action, then runs the notification once with a 15-second bound. It retains the
actual notification process result. Command success is not a claim that a
recipient read the message. Notification failure is itself visible in status;
do not claim delivery or loop forever. Use the documented alternate authorized
communication route when available and report any undelivered alert.

## Launch a long run and wake the owner at exit

For multi-minute bench phases and automated batches on Pi5, run the job's
bounded supervisor under a transient `systemd --user` service. The Pi service
owns the run independently of the Codex command session. The completion wrapper
records the supervisor's output and exit status. It wakes the owning chat on
both success and failure with `pi_chat.py send --resume`.

Use the packet's supervisor command and bounds, absolute `RUN_EVIDENCE`
directory, and `OPERATOR_CHAT_ID`. Choose a fresh `SERVICE_UNIT` name and
`DELIVERY_ID` for each launch. Set `SERVICE_LIMIT` longer than the supervisor's
full bound, including cleanup and notification. A batch stops at the first
unexpected failure. Prepare any required Oryx alert in the packet and keep
the failure evidence before sending it. The chat wake-up also runs after a
handled failure.

From the commissioned checkout on Pi5, set the shell variables above. For a
single ordinary phase, use the job, manifest SHA-256, bench config and phase
name from the packet as shown below. For a batch, use the packet's bounded
batch command as the `SUPERVISOR_ARGV` array.

```bash
SUPERVISOR_ARGV=("$PWD/.venv/bin/python" "$PWD/scripts/olimex_bench.py"
  --job "$JOB" --sha256 "$JOB_SHA256" --config "$BENCH_CONFIG"
  --out "$RUN_EVIDENCE" --operator "$OPERATOR_CHAT_ID" "$PHASE")

mkdir -p -- "$RUN_EVIDENCE"
SUPERVISOR_LOG="$RUN_EVIDENCE/$SERVICE_UNIT.log"
systemd-run --user --unit="$SERVICE_UNIT" --property=Type=exec \
  --property=RuntimeMaxSec="$SERVICE_LIMIT" --property=TimeoutStopSec=15s \
  --property=KillMode=control-group --working-directory="$PWD" \
  "$PWD/.venv/bin/python" /Agon/mystuff/agon-vdplet/tools/notify_bench_completion.py \
  --thread "$OPERATOR_CHAT_ID" --delivery-id "$DELIVERY_ID" \
  --log "$SUPERVISOR_LOG" -- "${SUPERVISOR_ARGV[@]}"
```

Record the successful launch, service name and evidence location in chat.
End the turn and keep the reservation active. The service runs without
periodic polling, a sleep loop, or a tool session kept open.

When the chat wakes, read the supervisor log and its `.terminal.json` and
`.notification.json` receipts. Verify the phase receipts and bench handback
before any check-in. On failure, report the first failure and follow the bench
stop rule. If a host interruption or delivery error leaves a receipt missing,
inspect the service journal and retained phase records when you resume. Treat
an unknown outcome as unresolved and reconcile it before any replay or release.
