# Olimex bench checkout through check-in

This is the working draft for [BENCH-019](../BENCH-019.md). The scheduler
manages the FIFO and wakes each operator when their slot opens. The operator
owns all bench preparation, test execution, recovery, and check-in. The
scheduler follows this document and uses only its chat for coordination and
queue bookkeeping.

## 1. Reserve and check out

The project operator contacts the **Olimex scheduling agent** at Codex chat
ID `01a1be59-b9fe-7ca1-a5b5-bef1230421f4`. Use immediate chat delivery. The
operator sends only the two messages quoted below. The scheduler uses the
sending chat to identify and wake the operator.

| Message | Sender | Action |
| --- | --- | --- |
| 1. Request a slot | Operator | “Reserve a spot for me on the bench in the FIFO.” |
| 2. Confirm the reservation | Scheduler | Append the request to the FIFO, record it in the scheduler chat, and tell the operator it was added. |
| 3. Open the slot | Scheduler | When the bench has no active slot, mark the head of the FIFO active and wake that operator in their chat. This gives the operator exclusive custody. |
| 4. Check in | Operator | “I’m done with my testing. You may release my reservation now.” On receipt from the active operator’s chat, the scheduler closes the slot and wakes the head of the FIFO if there is one. |

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
sole operator through check-in.

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
and prerequisites. Keep normal startup available. The operator records
what is staged and how the fixture will start.

## 4. Run and collect

The operator starts the fixture with the planned command once the bench is
ready. If Smith reserved that step, the operator finishes staging, sends Smith
the exact command once, and waits. Follow the test plan's observation and stop
conditions. Use its completion signal and collect its specified outputs.

## 5. Restore production firmware and check in

1. Leave the listed production firmware on all three processors. Restore
   each component the job changed away from production and verify the restore
   write. Leave untouched components alone.
2. Leave the bench at a working CLI.
3. Finish transfers.
4. Stop the operator's processes and close their device handles.

Record the result and send the check-in message in step 4 of the reservation
exchange.

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
