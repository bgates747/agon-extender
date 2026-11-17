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

| Processor | Owner | Binary | SHA-256 |
| --- | --- | --- | --- |
| Olimex eZ80, EMOS | Extender | [EMOS ROM.bin](../../../dist/bench-standards/emos-eirene-r04/ROM.bin) | `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca` |
| Extender ESP32-P4, Extender VDP | Extender | [Olimex P4-PC production application](../../../dist/bench-standards/extender-p4-pc-d9bcb1a2/agon_extender.bin) | `d9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e` |
| Mainboard ESP32, VDPlet | VDPlet | [VDPlet v0.1.2-alpha release binary](https://github.com/bgates747/agon-vdplet/releases/download/v0.1.2-alpha/vdp-vdplet-0.1.2-alpha.bin), [release checksums](https://github.com/bgates747/agon-vdplet/releases/download/v0.1.2-alpha/SHA256SUMS) | `dc43ecb8b1c324ffd1a032e6cc0c56d8c05dd33a355ce170c23adb35ffb533ab` |

### Stage the fixtures

Stage the identified fixtures in the agreed location and verify the bytes
and prerequisites. Preserve `/autoexec.txt`. Reset returns to normal boot,
and the operator starts the fixture with its explicit CLI command. The
operator records what is staged and how the fixture will start.

## 4. Run and collect

The operator starts the fixture with the planned command once the bench is
ready. If Smith reserved that step, the operator finishes staging and uses
the desktop **Agent has a question** alert with the exact start command and
what to check. The operator holds the slot and setup while waiting for Smith
to start. Use ordinary chat for follow-up. Follow the test plan's observation and stop
conditions. Use its completion signal and collect its specified outputs. If a
fixture switches display mode, allow at least one second for the monitor to
settle and restore the entry mode and visible CLI at the end.

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
summary includes the result, exact byte comparison, CLI/cleanup status and
evidence references required by that assignment.

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
.venv/bin/python scripts/olimex_bench.py --job JOB.json --sha256 JOB_SHA256 preflight
```

The offline command prints the applicable phases in order. Prepare before the
slot opens. After checkout, use this command for each listed phase in order.
Keep the same job, config and evidence directory throughout. Use your chat ID
as the operator value.

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
| `stage` | Check commissioned ports and working CLI. Create the job directories, verify the staged bytes and exit the foreground listener. Stage the two ROM images only when the job changes EMOS. |
| `install-mainboard`, `install-p4`, `install-emos` | Run only phases printed by preflight. Write the approved image after confirming its applicable target. Compare the complete write extent. Bring the component back to a verified CLI. |
| `run` | For a job with an operator-started Legacy fixture, witness the CLI, issue one `LOAD` and one `RUN`, then collect the specified result. Each physical phase produces a durable process receipt. |
| `restore-emos`, `restore-p4`, `restore-mainboard` | Restore only the components the job changed. The same component verification and startup checks apply. |
| `handback` | Verify CLI, idle transfer services, serial handles and the changed components' restores. The parent records joined worker completion before you send check-in. |

A production-only job lists no install or restore phases. A staging-only or
human-start job stops its automation before `run` and follows the invocation
boundary in its own packet. The runner collects results from its own observed
`RUN`. Name the exact commands and observation path in the packet for any
other workload.

### Firmware methods used by the phase runner

| Phase | What the Pi operator does |
| --- | --- |
| Mainboard VDPlet | Open one classic ESP32 programmer session using esptool 4.12. Verify the commissioned device and app0 layout, write the job extent at `0x10000`, and independently compare it. Hold Agon reset, restart the installed P4 and wait for its boot-pad release. Release Agon reset and prove a working CLI. |
| Extender VDP | Hold the Agon reset through its commissioned USB RTS circuit. Use stock esptool 5.1.0 on the P4 USB at 460,800 baud. Read the partition table and OTA selector, write app0 at `0x20000` with all three flash settings set to `keep`, and independently compare the written extent. Restart the P4 once and wait for its boot-pad release. Release Agon reset, then prove a working CLI. |
| EMOS | At the Legacy CLI, run the prepared `FLASH mos … -f` for the staged ROM. Wait for the updater to restart and admit input. Use `SAVE` to read the full 128 KiB ROM, retrieve it from the SD listener, compare it with the requested image and exit the listener. |

Poll the original tool session until it exits. Live worker output is at
`RUN_EVIDENCE/PHASE/output.log`. The phase directory also contains the
parent-written `child-terminal.json` and, on success, `complete.json`.
A firmware phase writes `independent-verification.json` and a completed
handback writes `handback.json`. Record the first failure and its phase before
recovery.

## Stop on an unexpected problem

1. Stop work and keep the reservation active.
2. Describe the problem and the last known bench state in the operator's own
   chat session.
3. Notify Smith with the desktop **Agent has a question** dialog.
4. Wait for Smith's response. Take no further action while waiting, including
   troubleshooting, retries, cleanup, restoration, or check-in.

On a long unattended goal task, the operator may restore the bench to its
production state if needed and check it in without waiting for Smith. The
operator can then trace the problem away from the bench. If the operator
finds and fixes the problem, they may request a new slot through the normal
FIFO. If the operator cannot return the bench to its production state,
follow the stop rule above.
