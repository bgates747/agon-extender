# Olimex bench checkout through check-in

For a new or adapted fixture, start with [Prepare an Olimex test job](AUTHORING.md).

The scheduler
manages the FIFO and wakes each operator when their slot opens. The operator
owns all bench preparation, test execution, recovery, and check-in. The
scheduler follows this document, uses direct chat for coordination, and keeps
the live FIFO in the scheduler's writable workspace.

## 1. Reserve and check out

**SMITH GIVES THE OLIMEX SCHEDULING AGENT STANDING AUTHORIZATION TO UPDATE THE FIFO, ACKNOWLEDGE EVERY RESERVATION REQUEST, GRANT EXCLUSIVE BENCH ACCESS TO THE NEXT OPERATOR AS SOON AS THE BENCH IS FREE, AND SEND THE SLOT-OPEN NOTIFICATION. THE SCHEDULER IS AUTHORIZED TO RECORD CHECK-IN, RELEASE THE SLOT, AND WAKE THE NEXT OPERATOR. THESE ROUTINE ACTIONS REQUIRE NO FURTHER APPROVAL FROM SMITH.**

The project operator contacts the **Olimex scheduling agent** at Codex chat
ID `01a1be59-b9fe-7ca1-a5b5-bef1230421f4`. Use immediate chat delivery. The
operator sends only the request or check-in shown below for routine scheduling.
Use the sender's unique chat ID from the message metadata. Include that ID in
the message only if the scheduler cannot see it automatically.

The chat ID is the only detail the scheduler needs for a routine reservation.
The FIFO document holds the active operator's chat ID and the waiting chat
IDs in order. Keep the job description, firmware requirements, test plan,
estimated duration, and job authorization in the operator's chat.

| Message | Sender | Action |
| --- | --- | --- |
| 1. Request a slot | Operator | “Reserve a spot for me on the bench in the FIFO.” |
| 2. Confirm the reservation | Scheduler | Append the chat ID to the tail of the FIFO and reply “Added to the FIFO.” |
| 3. Open the slot | Scheduler | When the bench is free, mark the head of the FIFO active and send that chat “Your Olimex slot is open.” This gives the operator exclusive custody. |
| 4. Check in | Operator | “I’m done with my testing. You may release my reservation now.” On receipt from the active operator’s chat, the scheduler closes the slot and wakes the head of the FIFO if there is one. |

### Check the commissioned operator files and Pi sender

Every Pi operator uses the maintained `pi_chat.py` sender for reservation,
check-in and authorized result return. The job packet supplies the operator's
actual chat UUID, evidence directory and the full commissioned checkout commit.
Run this host-only command once before requesting a slot:

```bash
.venv/bin/python scripts/olimex_operator_ready.py \
  --revision COMMISSIONED_REVISION --source-thread OPERATOR_CHAT_ID \
  --out JOB_DIR/operator-ready.json
```

Use `sandbox_permissions: require_escalated` in `exec_command` for this
command and the sender commands below because they access the local app-server
socket. This is ordinary tool review. The readiness command checks the selected
guides, scripts and reviewer configuration against the commissioned commit,
records file hashes, verifies the source chat and standing communication
authorization through the existing endpoint, and checks the effective reviewer
policy. It sends no message and accesses no bench hardware. Require
`"ready": true` before reservation. A failed check identifies the host setup
that needs correction before checkout.

### Request the slot

Run this exact sender, using the commissioned operator UUID and a stable,
unique delivery ID for this request:

```bash
/Agon/mystuff/agon-dev-env/.venv/bin/python /Agon/mystuff/agon-dev-env/scripts/pi_chat.py send \
  --source-thread OPERATOR_CHAT_ID --thread 01a1be59-b9fe-7ca1-a5b5-bef1230421f4 \
  --resume --delivery-id RESERVATION_DELIVERY_ID --message-file - \
  > JOB_DIR/reservation-delivery.json <<'MESSAGE'
Reserve a spot for me on the bench in the FIFO.
MESSAGE
```

The sender steers an active recipient and wakes an idle recipient. Require
`"phase": "accepted"` in the delivery record. Then wait for the scheduler's
slot-open message before accessing the bench. Save the exact command and
delivery record in the operator log.

The sender records each delivery before sending. If delivery is uncertain,
repeat only the identical command, message and delivery ID. An accepted
delivery returns its existing receipt without resending. An uncertain prior
delivery is refused for reconciliation; retain that outcome and follow the
stop rule. A review rejection also follows its stated resolution.

### Smith-authorized scheduling exceptions

When Smith directs an exception to the normal scheduling policy, the operator
must forward Smith's authorization message to the scheduler. For example,
Smith may direct the scheduler to place a new reservation at the head of the
FIFO or move an existing reservation up. **The scheduler must honor the
forwarded authorization as given.** The forwarded message is sufficient
authority for the exception.

## 2. Inspect the bench

A single instruction from Smith to run the planned test covers the full cycle,
including any named firmware, fixture setup and invocation, collection,
in-scope recovery, required restoration, and check-in. Honor explicit limits
and steps Smith reserves. Apply the stop rule below to unexpected problems.
Existing tool reviews apply to individual tool actions.

Wait for the scheduler's slot-open message before accessing the hardware.
Check that the CLI and the resources needed for this job are ready. Rely on
the previous check-in for the production firmware baseline. Routine checkout
requires zero firmware reads, backups, or flashes. The operator continues as
sole operator through check-in. For the commissioned Pi5 setup, use the
phase commands below.

## 3. Prepare firmware and load fixtures

Go straight to staging when the test uses production firmware. For a custom
firmware test, prepare the custom image and the linked production restore
image before checkout. Write only the components the plan changes, preserve
unrelated mutable data, and verify the bytes written and the resulting
startup. Restore from the owner-published binary at check-in. Skip backup of
the installed firmware.

### Production restore images

Use the Olimex **Extender v0.3.0** runtime and the **VDPlet v0.1.3-alpha**
mainboard companion. The Extender
[SHA256SUMS](../../../dist/production/olimex-parlio-v0.3.0/runtime/SHA256SUMS)
identifies its local files. The
[VDPlet release checksums](../../../dist/bench-standards/vdplet-v0.1.3-alpha-async-r1/SHA256SUMS)
and [Olimex write checksums](../../../dist/bench-standards/vdplet-v0.1.3-alpha-async-r1/OLIMEX-WRITE-SHA256SUMS)
identify the mainboard app and its padded write. The job packet supplies the exact
`restore_write` pin for every processor the job changes.

| Target | Production file | Bytes | SHA-256 | Use |
| --- | --- | ---: | --- | --- |
| Extender ESP32-P4, Extender VDP | [p4/app0-write.bin](../../../dist/production/olimex-parlio-v0.3.0/runtime/p4/app0-write.bin) | 1,769,472 | `10d4b60a67888c2363e79ad29adbfd68d58a8638fd9013af413973655cb33ae4` | Extender's padded app0 write image at `0x20000`. Use it for a job with the matching `0x1B0000` write extent. |
| Olimex eZ80, EMOS | [emos/ROM.bin](../../../dist/production/olimex-parlio-v0.3.0/runtime/emos/ROM.bin) | 131,072 | `9b90b5d94ec6888d85ef1fa1acf23a82b2e0eb1f179b75f549863fbd72343673` | Extender's complete MOS ROM for the `restore-emos` phase. |
| Mainboard ESP32, VDPlet | [VDPlet app0-write.bin](../../../dist/bench-standards/vdplet-v0.1.3-alpha-async-r1/app0-write.bin) | 1,138,688 | `1b661b9357c3952fcd807dc8aed74060abf26bffeb321deab2ae2697f2e5028f` | VDPlet's padded app0 write at `0x10000`. Use it for a job with the matching `0x116000` write extent. |
| Mainboard SD listener | [sd/emos/sdserve.bin](../../../dist/production/olimex-parlio-v0.3.0/runtime/sd/emos/sdserve.bin) | 26,127 | `98492acc7dcd29e484ef76c69026e8801375738c33c617ba61a94d8481151f08` | Extender's file for `/emos/sdserve.bin` on the SD card. |

For a P4 job, bind the raw [p4/agon_extender.bin](../../../dist/production/olimex-parlio-v0.3.0/runtime/p4/agon_extender.bin)
as `restore_app`. Use [p4/partition-table.bin](../../../dist/production/olimex-parlio-v0.3.0/runtime/p4/partition-table.bin)
only to verify the layout. For a mainboard job, bind the raw
[vdp-vdplet-0.1.3-alpha.bin](../../../dist/bench-standards/vdplet-v0.1.3-alpha-async-r1/vdp-vdplet-0.1.3-alpha.bin)
as `restore_app` and use the
[mainboard partition table](../../../dist/bench-standards/vdplet-v0.1.3-alpha-async-r1/partitions.bin)
to verify the layout. If an ESP32 candidate needs a different write extent,
use the job owner's pinned, equally sized candidate and restore files with
`0xff` padding. The release archives keep the previous baseline under
`rollback/` for owner recovery.

### Stage the fixtures

The commissioned `olimex_bench.py` runner defaults to schema 3. It starts
`EMOS sdserve --fast --parallel /` on the matched production stack. P4 sends
nonempty fixture files to EMOS over PARLIO during staging. EMOS sends
nonempty result files back to P4 over PARLIO during collection. UART carries
control records and empty-file operations. The runner records the carrier
and requires successful transfer completion in both directions.

Skip CRCs, substitute payload digests and verification reads of staged
contents on both ends. Local input hashes identify the files before the
job, and the fixture's result checks still determine the test outcome.
Verify firmware writes independently. If a required parallel capability is
missing or a transfer or test fails, follow the [stop rule](#stop-on-an-unexpected-problem).
Arrange a separate, explicit compatibility method in the job packet if
custom firmware requires one.

Preserve `/autoexec.txt` and use the job's explicit CLI start command. Record
what was staged and which transfer path completed.

## 4. Run and collect

The operator starts the fixture with the planned command once the bench is
ready. If Smith reserved that step, the operator finishes staging and posts
the exact command and what to check in the originating chat. If that handoff
needs urgent attention, use the short [Oryx spoken alert](../../../../agon-dev-env/codex/urgent-alerts.md).
The operator holds the slot and setup while waiting for Smith to start.
Use ordinary chat for follow-up. Follow the test plan's observation and stop
conditions. Use its completion signal and collect its specified outputs. If a
fixture switches display mode, allow at least one second for the monitor to
settle and restore the entry mode and visible CLI at the end.

Run multi-minute phases and automated batches under a Pi5 user service by
default. Use the [detached launch and wake-up procedure](../../procedures/bench-completion.md).
The packet supplies the bounded command and names the owning operator chat.
Once the service starts, record where it will write evidence and end the turn.
Keep the reservation active. The runner wakes the chat on success or failure.
Skip periodic status checks and keep the ordinary stop rule for unexpected
problems. A service can run while chat is idle without changing the job's
authorization for retries, recovery, or release.

## 5. Restore production firmware and check in

1. Leave the listed production firmware on all three processors. Restore
   each component the job changed away from production and verify the restore
   write. Leave untouched components alone.
2. Leave the bench at a working CLI.
3. Finish transfers.
4. Stop the operator's processes and close their device handles.

Record the result and send the check-in message using the same Pi sender:

```bash
/Agon/mystuff/agon-dev-env/.venv/bin/python /Agon/mystuff/agon-dev-env/scripts/pi_chat.py send \
  --source-thread OPERATOR_CHAT_ID --thread 01a1be59-b9fe-7ca1-a5b5-bef1230421f4 \
  --resume --delivery-id CHECKIN_DELIVERY_ID --message-file - \
  > JOB_DIR/checkin-delivery.json <<'MESSAGE'
I’m done with my testing. You may release my reservation now.
MESSAGE
```

Return an authorized result to the commissioning chat with this same sender.
The job packet supplies `COMMISSIONING_CHAT_ID` and the summary file. The
summary includes the outcome, the job's result checks, CLI/cleanup status and
evidence references.

```bash
/Agon/mystuff/agon-dev-env/.venv/bin/python /Agon/mystuff/agon-dev-env/scripts/pi_chat.py send \
  --source-thread OPERATOR_CHAT_ID --thread COMMISSIONING_CHAT_ID \
  --resume --delivery-id RESULT_DELIVERY_ID --message-file JOB_DIR/result-summary.txt \
  > JOB_DIR/result-delivery.json
```

### Cold-run log and procedure acceptance

For a commissioned cold run, record every tool/skill call, command, search,
file read and outcome in the job's durable operator log. Beside each action,
name the guide section or exact job-packet command followed. Record an
undocumented action, improvised search or missing prerequisite as a procedure
defect, even when the hardware test passes. The commissioning owner reviews
that action-to-instruction mapping before accepting the procedure. Keep
hardware outcome and instruction completeness as separate recorded results.

## Commissioned Pi5 operator commands

Use the job packet's manifest, its SHA-256, and the commissioned local bench
config it names. Run from the checkout containing this guide and the supplied
tools. The manifest lists staged payloads, expected results and the processors
this job changes.

```bash
.venv/bin/python scripts/olimex_bench.py --job JOB.json --sha256 JOB_SHA256 --config BENCH.local.json preflight
```

The offline command checks the local interpreter dependencies for the selected
firmware and prints the applicable phases in order. Prepare before the slot
opens. Use the phase command below directly for short work or as the command
passed to the Pi service for longer work. Keep the same job, config and evidence
directory throughout. Use your chat ID as the operator value.

In the commissioned Pi5 sparse checkout, the phase runner uses a shared
operation lock outside the workspace and needs access to the bench's local
devices and services. In `exec_command`, request
`sandbox_permissions: require_escalated` for the physical phase command so it
goes through ordinary tool review. The offline `preflight` uses only local
job inputs.

```bash
.venv/bin/python scripts/olimex_bench.py --job JOB.json --sha256 JOB_SHA256 \
  --config BENCH.local.json --out RUN_EVIDENCE --operator OPERATOR_CHAT_ID PHASE
```

| Phase | Operator effect |
| --- | --- |
| `stage` | Creates job directories and stages the fixture and assets over PARLIO without routine readbacks. Stages ROM images only for an EMOS job and exits the foreground listener. |
| `install-mainboard`, `install-p4`, `install-emos` | Run only phases printed by preflight. Write the approved image after confirming its applicable target. Compare the complete write extent. Bring the component back to a verified CLI. |
| `run` | For a job with an operator-started Legacy fixture, witness the CLI, issue one `LOAD` and one `RUN`, then collect the specified result. Each physical phase produces a durable process receipt. |
| `run-ID` | For a named arm, witness its working directory, issue one `LOAD` and one invocation, and keep the same UART reader open through any configured terminator. Follow the [authoring guide](AUTHORING.md) for a native-UART job with MOS-managed listener handoff. Collect reports in the arm's evidence directory. |
| `enter-cwd` | If the packet requests it for a `stage-only` human-start job, enter the fixture directory from the manifest and verify MOS returns the exact prompt there. The worker closes its reader and joins before Smith loads and runs the fixture. |
| `preload` | For a human-start fixture, enter its directory, issue one LOAD, observe the returned prompt and close the reader. After the worker joins, give Smith the packet’s RUN command. |
| `restore-emos`, `restore-p4`, `restore-mainboard` | Restore only the components the job changed. The same component verification and startup checks apply. |
| `handback` | Verify CLI, idle transfer services, serial handles and the changed components' restores. The parent records joined worker completion before you send check-in. |

For a `human_start` job, stop after the last install (or stage for a
production-only job). If the `stage-only` packet requests `enter-cwd`, run it
as a separate phase with the existing job, config and evidence directory.
Its `enter-cwd.json` records the prompt. If preflight lists `preload`, run that
phase. Require the applicable phase’s joined completion before giving Smith
the packet’s commands.
For preload, Smith types only `RUN &ADDRESS` from the confirmed directory.
Smith reports the visual verdict and return to MOS in chat. Record his
words, then follow his disposition and the ordinary restore and handback
phases. A human verdict requires no script or synthetic result file.

### Firmware methods used by the phase runner

**Use USB esptool by default for mainboard VDPlet.** Run the commissioned
`install-mainboard` or `restore-mainboard` phase when the job calls for an
app0 write. The Pi programs the mainboard directly through its USB port.
Running VDPlet and the SD listener require no special build for that write.

Keep the verified Agon Flash SD updater as a fallback. If USB programming
fails, preserve the failure and follow the stop rule. Agon Flash requires
a separately commissioned recovery packet, a working MOS prompt and a
running VDPlet receiver that supports verified OTA. The current production
VDPlet predates that receiver.

| Phase | What the Pi operator does |
| --- | --- |
| Mainboard VDPlet | Use the runner's standalone esptool 5.1.0 in one classic ESP32 programmer session. Enter ROM at 115,200 baud, verify the MAC, start the stub, and change to 460,800 baud. Verify the partition table and app0 selector, write the job extent at `0x10000` with flash mode, size and frequency set to `keep`, and independently compare the full readback. Hold Agon reset, restart the installed P4 and wait for its boot-pad release. Release Agon reset and prove a working CLI. |
| Extender VDP | Hold the Agon reset through its commissioned USB RTS circuit. Use stock esptool 5.1.0 on the P4 USB at 460,800 baud. Read the partition table and OTA selector, write app0 at `0x20000` with all three flash settings set to `keep`, and independently compare the written extent. Restart the P4 once and wait for its boot-pad release. Release Agon reset, then prove a working CLI. |
| EMOS | At the Legacy CLI, run the prepared `FLASH mos … -f` for the staged ROM. Wait for the updater to restart and admit input. Use `SAVE` to read the full 128 KiB ROM, retrieve it from the SD listener, compare it with the requested image and exit the listener. |

If `FLASH mos` leaves MOS unable to boot, stop and keep the slot. The
[bare-metal EMOS recovery procedure](../../mos-recovery.md) uses an external
ESP32-WROOM programmer under the Author's recovery disposition. The current
Extender P4-PC is unqualified to program the eZ80 through ZDI. Leave its
production firmware installed and keep the standard `FLASH mos` process
free of P4 ZDI preflight or temporary programmer firmware.

For a short foreground phase, wait for the tool result. For a detached phase
or batch, open the runner's terminal and notification receipts when the owning
chat wakes. Worker output is at `RUN_EVIDENCE/PHASE/output.log`. The phase
directory also contains the parent-written `child-terminal.json` and, on
success, `complete.json`. A firmware phase writes `independent-verification.json`
and a completed handback writes `handback.json`. Verify the applicable receipts
before starting another phase or checking in. On failure, record the first
failed phase and follow the stop rule.

## Stop on an unexpected problem

Use this rule for a failed transfer or test. Preserve the first failure and
existing evidence. A completed transfer followed by a test failure is a reason
to consider corruption during diagnosis. Any diagnostic readback happens as
part of that diagnosis under the applicable recovery instructions.

1. Stop work and keep the reservation active.
2. Describe the problem and the last known bench state in the operator's own
   chat session.
3. Send an [Oryx spoken alert](../../../../agon-dev-env/codex/urgent-alerts.md).
   Name the operator's recognizable session and describe the immediate issue
   in one short sentence. If the runner already sent the alert, record that
   receipt in chat.
4. Wait for Smith's response. Take no further action while waiting, including
   troubleshooting, retries, cleanup, restoration, or check-in.

On a long unattended goal task, the operator may restore the bench to its
production state if needed and check it in without waiting for Smith. The
operator can then trace the problem away from the bench. If the operator
finds and fixes the problem, they may request a new slot through the normal
FIFO. If the operator cannot return the bench to its production state,
follow the stop rule above.

### Restore and check in after a failed phase

Once recovery is authorized under the stop rule above, confirm the fixture
has stopped and MOS is available for the ordinary restore or handback
commands. In the **original slot**, from the **same checkout and working
directory**, use the original job, operator, config and evidence root. For
example, when the failed phase was `run-full`, invoke:

```bash
.venv/bin/python scripts/olimex_bench.py --job JOB.json --sha256 JOB_SHA256 \
  --config BENCH.local.json --out RUN_EVIDENCE --operator OPERATOR_CHAT_ID recover-after-run-full
```

Replace `run-full` with the exact failed phase name. The runner verifies the
joined failure and its predecessors, checks that later phases never started,
and compares the verified component records with the installed inventory.
It restores outstanding candidates in reverse install order and performs
normal handback. Keep the original failure. Check in only after the recovery
directory contains both `handback.json` and the parent's `complete.json`.
The original fixture outcome stands.

If recovery reports an uncertain write, a live worker, different custody,
or missing records, keep the slot and follow the stop rule. Older runs
that predate `operation-binding.json` require individual reconciliation.
