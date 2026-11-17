# BENCH-019 — One Olimex bench procedure

Extender will maintain one document for the complete Olimex bench cycle,
from checkout through firmware, fixtures, results and check-in. Smith and
Extender will develop the policy one decision at a time. Once Smith accepts
the procedure, Extender will remove superseded instructions using the
[BENCH-018 audit](BENCH-018/INVENTORY.md) as the cleanup list.

1. **Draft the full procedure.** Use the [working draft](BENCH-019/PROCEDURE-DRAFT-R02.md)
   to review a complete job. Cover what one human instruction authorizes,
   queue admission, sole custody, firmware choice and verification, fixture
   loading and invocation, data collection, firmware recovery or restoration
   when required, check-in and the next wake. Document the four-message exchange
   and the operator's direct route to Smith for bench issues.
2. **Develop the policy in chat.** Extender presents one decision at a time
   with a recommendation, alternatives and a concrete example. Smith decides
   how a normal job should work and where an exception starts. Extender records
   each answer in the register below and updates the draft before the next
   question. Walk through an ordinary job, a custom firmware job, a manual
   invocation, an unattended failure, and a denied action.
3. **Rehearse the draft with a fresh operator.** Complete the
   [physical rehearsal](#pre-promotion-physical-rehearsal) before promoting the
   procedure. Fix any gaps the operator encounters and bring the result to Smith.
4. **Publish one operating document.** After the rehearsal and Smith's
   acceptance, Extender publishes the Olimex bench procedure. Routine
   project instructions and tooling guides point directly to it. Carry forward
   the queue and custody handling verified in the rehearsal, and align any
   operator tools that still depend on the old lease mechanism.
5. **Remove outdated bench instructions.** Use the
   [document catalog](BENCH-018/CATALOG.md) and
   [repository index](BENCH-018/REPOSITORY-INDEX.md) to account for every
   audited instruction and copy. Delete documents devoted to superseded bench
   procedures. In mixed documents, remove the bench instructions and use a
   single link to the current procedure where readers need an entry point.
   Preserve test data, source and frozen evidence. Use Git history or evidence
   archives for needed historical records, and remove stale local copies and
   manuals from places that agents search for current instructions. Record the
   disposition by checkout and follow its ownership.
6. **Verify discovery and execution.** Search the same locations as the audit,
   starting from the usual agent entry points. Follow links and verify that
   they lead to the one published procedure. Use the next cold checkout to
   verify the planned physical work and ordinary reservation exchange. Record
   who acted and any unexpected requests for approval. Exercise two waiters,
   next-owner wake, priority exceptions and failed notification handling on
   real jobs. These are deferred from the synthetic acceptance run.
7. **Pin the production restore baseline before the rehearsal.** Extender owns the
   EMOS and Extender VDP images. VDPlet owns the mainboard VDP image.
   Use the [firmware owner guide](../../production/olimex-bench-firmware.md)
   to confirm the three builds and publish the direct links. The rehearsal
   handback establishes the installed baseline for subsequent checkouts. The
   bench procedure carries only the current restore images and the test
   lifecycle. The owner guide covers baseline changes.

## Pre-promotion physical rehearsal

Use a synthetic workload on the real Olimex bench. The rehearsal checks
whether an operator who missed the policy discussions can follow the draft
from a FIFO request to a clean check-in after a three-processor firmware test.

1. **Extender creates the [test kit](BENCH-019/REHEARSAL-KIT.md).** Make one small test-only firmware change
   each to EMOS, the Extender P4 VDP, and the mainboard VDPlet. Build a fixture
   that exercises an observable behavior introduced by each change and records
   a separate pass or fail for each processor. Each assertion distinguishes
   the custom behavior from production behavior. Keep normal boot and recovery
   available. Freeze the draft revision, test binaries, production restore
   images, fixture, commands, and expected outputs before handing off.
2. **Extender briefs the Olimex scheduling agent.** Notify the scheduler that
   the draft's new lease procedure controls reservation, exclusive custody,
   and check-in for this rehearsal. Send the same frozen draft before the
   fresh operator requests the slot. The operator gets the first available
   slot as the rehearsal's only queue exception. If the regular FIFO has
   waiting requests, have the scheduler save the pending FIFO in a temporary
   file in its original order, confirm the copy, and empty the live FIFO.
   Leave any active operator's custody in place until check-in. Keep saved
   requests and any arrivals during the rehearsal for reinstatement.
3. **A fresh operator runs the rehearsal.** Create a new chat in the same
   Agon Extender project on Oryx as the procedure discussion. Use GPT-6.1 Sol
   with high reasoning, and run the agent in the existing `agon-extender`
   workspace on Pi5. Give the agent the draft and frozen test kit as its task
   inputs. Start it without the policy discussion or a prepared walkthrough.
   The operator requests the slot, installs all three custom images, stages
   and runs the fixture, collects the three results, restores and verifies all
   three production images, and checks in. The slot-open message under the
   draft grants exclusive physical custody for the rehearsal.
   If the operator encounters a gap, capture it as a rehearsal finding and
   follow the draft's stop rule.
4. **The operator keeps a durable run log.** Start an `OPERATOR-LOG.md` in the
   run's local evidence directory before the first rehearsal action. Update it
   as work happens through check-in or the point where work stops. Record in
   order every command run, including commands sent to the bench, and every
   skill and tool used. Record every search with its exact query or command
   and the path of each file opened because of it, even when the file did not
   help. Tie each lookup to what the operator needed to learn. Record which
   attempted actions were blocked by tool review, the reason shown, and
   whether the action ran. Omit credential values from the log.
5. **Extender tells the scheduler to restore the regular FIFO.** On rehearsal
   check-in, or if the rehearsal is canceled before checkout, have the scheduler
   restore the saved FIFO document if a copy was made. Preserve the original
   order and place later arrivals after the saved requests in arrival order.
   Confirm that the scheduler resumes normal dispatch and wakes the head when
   the bench is free.
6. **Extender reviews the rehearsal.** Record the reservation exchange, the
   elapsed time for setup, execution, and restoration, the three test results,
   and the operator's check-in evidence. The pass condition is that all three
   behaviors are observed, the operator completes normal check-in with all
   three production images restored, and the draft and kit suffice without
   extra guidance. Use the run log to find missing instructions, stale
   guidance the operator followed, unnecessary work or messages, and approval
   interruptions. Add specific prohibitions to the draft where the rehearsal
   shows what an operator should avoid. Correct the source of each problem
   before proposing cutover.

Rehearsal r01 used the frozen local kit under `agents/bench019/rehearsal-r01`
and the [r01 draft](BENCH-019/PROCEDURE-DRAFT.md). The operator exercised all
three custom images, restored all three production images, and checked in.
The regular FIFO had zero waiting requests. The [r01 analysis](BENCH-019/REHEARSAL-R01-RESULT.md)
records two operator stops that needed Smith, missing maintained execution
commands, and the scheduler's remaining reliance on legacy occupancy state.
The physical checks passed. The draft and kit did not suffice for independent
operation. Use the analysis's priority and acceptance table to prepare the
next rehearsal, with the FIFO-specific test deferred as recorded below.

## Approved corrective work

Smith approved the observer, supported bench commands and cold rehearsal with
cutover on 2026-11-16. The independent FIFO test will use real jobs later.
The synthetic run follows the draft's ordinary reservation and check-in
exchange and sends the scheduler only the operator's chat identity and action.

1. **CLI observation.** Provide a maintained command-correlated observer for
   a test that selects Legacy serial output. Check a fresh prompt and confirm
   each command's return before dispatching the next. A returned CLI error or
   explicit fixture failure ends dispatch, preserving the raw transcript and
   last known action. Verify the saved root prompt, configured working-directory
   prompts, fragmented output, stale output, rejected LOAD, and explicit FAIL
   with a MOS error before the prompt. Use the existing stop rule for an
   unexpected problem.
2. **Supported operator commands.** Link the exact commands for verified SD
   staging, bounded per-component install and restore, explicit fixture
   invocation and collection, and handback from one draft revision. Reuse the
   maintained keyboard, serial, SD, reset, programming and supervision
   primitives. Pin the rehearsal's binaries and command plan, and keep host
   device bindings in local configuration. Prove offline that a production-only
   job has no firmware operations and that staging has no fixture invocation.
   Custom jobs independently verify and restore only their changed components.
3. **Cold acceptance and cutover.** Give a fresh operator the revised draft,
   pinned kit and documented commands. Repeat the custom three-processor
   fixture in one normal checkout. Record tool use and actual timings, all three
   diagnostic outcomes and a verified production handback. The normal path
   must need zero historical/source searches, local helper authoring or extra
   instructions from Smith. After a pass, publish the single procedure and
   use the BENCH-018 inventory to remove superseded operating instructions.

## Decision register

| ID | Decision | State |
| --- | --- | --- |
| 1 | One instruction to run the planned test covers checkout, setup and verification of the named firmware, fixture loading and invocation, observation and collection, in-scope recovery and required restoration, and check-in. Explicit limits, steps Smith reserves, and the unexpected-problem stop rule apply. | Accepted |
| 2 | The scheduler opens the slot for one project operator at a time. The operator checks physical readiness after receiving the slot-open message and owns the job through check-in. | Accepted |
| 2a | Routine scheduler messages are brief. The operator's unique chat ID is the only reservation detail. The FIFO holds the active chat ID and the ordered waiting IDs. Job details and authorization stay with the operator. | Accepted |
| 2b | For a scheduling exception, the operator must forward Smith's authorization message. The scheduler must honor it as given, including priority for a new or existing reservation. | Accepted |
| 3 | The scheduler follows this single procedure, keeps the FIFO document in its writable workspace, and coordinates through direct chat. Smith gives standing authorization to add requests, open the next slot when the bench is free, notify the operator, and process check-in. The operator's routine messages are a reservation request and a release message. Smith is the operator's sole contact for help with bench and test problems. | Accepted |
| 4 | Check in with current production firmware on all three processors. The incoming operator relies on that guarantee and skips routine firmware inspection and backups. The operator restores the components they changed and verifies those writes. The bench procedure supplies direct links to the current binaries. | Accepted |
| 4a | Production release publication and baseline changes belong in the firmware owner guide. Keep the bench procedure focused on the test and reservation lifecycle. | Accepted |
| 5 | The operator handles all setup needed for the test. Stage the listed fixtures, use the planned command unless Smith reserved invocation, and use the test plan's own completion signal and outputs. | Accepted |
| 6 | On an unexpected problem, the operator stops and retains the reservation, describes the problem in their own chat, alerts Smith with the **Agent has a question** dialog, and waits for his response before taking any further action. | Accepted |
| 6a | On a long unattended goal task, the operator may restore the bench to its production state if needed, check it in without waiting for Smith, and trace the problem away from the bench. If the operator finds and fixes the problem, they may request a new slot through the normal FIFO. | Accepted |
| 7 | For normal check-in, the operator leaves production firmware on all three processors and a working CLI, finishes transfers, stops owned processes, and closes device handles. The scheduler closes the slot and wakes the head of the FIFO if one exists. | Accepted |

The working draft is for discussion. Existing instructions remain in effect
until Smith accepts the replacement. The audit cleanup starts after that
decision.
