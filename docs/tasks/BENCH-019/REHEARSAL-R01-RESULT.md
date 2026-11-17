# BENCH-019 rehearsal r01 analysis

**All three firmware checks passed and the scheduler closed the slot after a verified
production handback. The draft and kit failed the independent-operation test.**
The cold operator needed two decisions from Smith and wrote ten Python helpers
(663 physical lines, plus inline shell) to turn the instructions into executable
work. The two stops were a failed post-flash CLI readiness check and a false
fixture stop caused by the operator's prompt matcher. The scheduler also
consulted legacy state, so this run establishes that a chat grant can work on an
empty bench while leaving independent FIFO operation unproved.
[Frozen draft](PROCEDURE-DRAFT.md) · [Frozen kit](REHEARSAL-KIT.md) ·
[Operator log](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md) ·
[Physical handback](../../../agents/bench019/rehearsal-r01/operator-run/handback/handback.json)

The biggest operational gap was between *what to do* and *how to do it on this
bench*. The kit gave image hashes, flash ranges, the install order, the fixture
commands, and the expected outputs. The operator still had to reconstruct the
Pi5 programmers and reset route, an SD staging transaction, and a way to tell
whether MOS had accepted a command or returned an error. The queue exchange
itself was short. Making the draft shorter will help discovery, but the flash,
transfer and observation gaps need maintained commands. The [r02 working draft](PROCEDURE-DRAFT-R02.md)
already addresses the reservation message content. Its operational steps still
specify outcomes without an executable entry point.

## What the rehearsal proved

| Processor | Custom behavior actually observed | Production image independently verified before release |
| --- | --- | --- |
| eZ80 / EMOS | The diagnostic accepted the exact command with status 0 and rejected the other argument with status 19. | `a25f1612…`, all 131,072 ROM bytes |
| Extender ESP32-P4 / Extender VDP | The host probe got 9 and 25 for inputs 3 and 5. | `d9bcb1a2…`, exact app and all 1,761,280 bytes of its recorded write extent |
| Mainboard ESP32 / VDPlet | The Agon fixture got a fresh VDP reply, status 0 and value 86. | `dc43ecb8…`, exact app and all 1,130,496 bytes of its recorded write extent |

All 21 kit pins matched before the operator contacted the bench. The restored
ESP32 extents covered the sectors written by the custom images,
including padding. I compared the six saved candidate and production readbacks
with their respective artifacts and verified the recorded extent hashes. The
final production evidence also shows a working Legacy CLI, an unchanged startup
file and listener, neutral admitted input, offline listener, idle staged
transfer, closed serial handles, and joined workers. The preceding operator had
left a different, recorded mainboard image under the earlier policy. This pilot
established the production handback baseline in the draft.
[Agon result](../../../agents/bench019/rehearsal-r01/operator-run/fixture-corrected/result.txt) ·
[P4 result](../../../agents/bench019/rehearsal-r01/operator-run/fixture-corrected/p4-result.txt) ·
[Final checks and check-in](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L1107)

## Time and discovery

| Boundary or measured work | Elapsed | What the interval contains |
| --- | ---: | --- |
| Assignment to reservation-send call | 2m02s | Role and policy discovery, authorization cross-check and offline kit verification |
| Request accepted to slot-open visible to the operator | 1m17s | Separate acknowledgment, rejected grant notification and accepted retry |
| Slot-open visible to scheduler closure | 38m22s | Post-grant setup, all bench work, Smith's holds and final check-in |
| First staging worker through final handback worker | 35m39s | Fourteen supervised spans and the intervals between them |
| Sum of the fourteen supervised spans | 9m52s | Worker launch through parent-recorded child exit, including two failed workers |
| Of those spans, listener startup, entry checks and SD staging | 2m37s | Five files staged and read back, plus startup and entry checks |
| Of those spans, three custom installs | 2m46s | The classic ESP32 write and readback, and the P4 and EMOS write, readback and boot checks |
| Of those spans, separate mainboard readiness check and recovery | 1m03s | 45.2s to the initial timeout and 17.6s for the authorized recovery |
| Of those spans, initial fixture observer and successful continuation | 22.9s | 15.7s to the false prompt timeout, then 7.2s for the worker that ran and collected |
| Of those spans, three verified production restores | 3m04s | Restore writes, independent readbacks and boot checks |
| Between recorded workers | 25m47s | Host-side preparation, research, tool calls, explicit holds and coordination |

Timing uses retained chat events and the timestamp differences between each
`supervisor-started.json` and `child-terminal.json`. Worker durations include
host and device work. The 9m02s from the false prompt stop to the corrected
worker includes a stop and human response, offline parser correction and
dispatch. The 5m28s from successful collection to restoration includes the
operator's report and Smith's explicit hold. The receipts cannot allocate every
second to research, review, or waiting, or predict the duration of a clean
cycle.
[Worker and stop evidence](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L855) ·
[Restore start](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L933)

Before the operator even requested a slot, its logged commands targeted **29
distinct files**, including the kit manifest and two fixture source files.
The other 26 were guidance, configuration or references for the full job.
Searches while waiting for the slot already concentrated on execution. The
operator reread the 15,888-line local hardware file after a truncated read and
jumped to four distant sections to identify the commissioned programmers and
reset route. After the grant it continued reading predecessor handbacks and
source. The durable log has 164 numbered entries, including outputs and grouped
actions. In those entries, 54 lines contain recorded `rg` or `grep` snippets,
47 through the three candidate installs. These are counts of named files and
logged search lines, rather than a count of tool calls, bytes returned, or
billed tokens.
[Before requesting](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L5) ·
[While queued](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L75) ·
[After grant](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L100)

## Where the instructions broke down

### Checkout and scheduler

1. **The chat contract was easy to use. The entry point sent the operator to
   the old system.** The operator sent the draft reservation text, received an
   acknowledgment and a separate custody grant, then sent only the normal
   check-in. It used no legacy lease token or live registry. But OP-10 sent it to
   a shared guide prescribing both, and the operator had to retrieve Smith's
   original messages to establish the pilot's precedence. The scheduler's own
   retained event log shows four read-only consultations of legacy registry
   state from briefing through release. The scheduler made zero legacy
   registry writes during that interval.
   The regular FIFO was empty, so the pilot exercised neither saving and
   restoring waiters nor waking a queued successor. It provides no evidence
   of durable FIFO updates, ordering among competing requests, or applying a
   forwarded priority instruction.
   [OP-10](../../procedures/README.md#L30) ·
   [Operator's authority reconciliation](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L18)

2. **Automatic review rejected the means of sending the first grant.** Review
   said original human authorization for consequential custody was missing
   from its trusted evidence and the peer messages were insufficient. The
   scheduler opened the source chat and cited Smith's original messages,
   together with the actual occupancy facts, on a second call to the same
   sender. It succeeded 24 seconds after the rejection, with no new instruction
   from Smith. This was a chat send rejection, with no failed FIFO write
   observed. The accepted call carried citations. R02's standing authorization
   and short message still need an actual delivery test under the scheduler's
   settings. Keep routine messages at chat ID and action. Only a Smith-directed
   exception carries the forwarded instruction. On a rejected or uncertain
   grant send, keep the same slot reserved and establish delivery before
   advancing the FIFO.
   [Operator grant log](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L86) ·
   [R02 exchange](PROCEDURE-DRAFT-R02.md#L9)

   The operator's run contains 18 tool-call batches requesting sandbox
   escalation and no recorded rejection of a physical operator action. The
   two physical stops have parent-written exits from workers that actually
   ran. The available events do not measure the review cost or time for each
   call. The scheduler evidence comes from its retained Codex session
   `01a1be59-b9fe-7ca1-a5b5-bef1230421f4`, event-log lines 23398, 23419,
   23432–23447 and 23504. The operator's actions are in session
   `01a1e711-fec3-7f61-afa1-26ca22b20845` and the durable run log.

3. **Mailbox failures added unrelated traffic.** The operator ran inherited
   startup and turn-end administrative checks. Eight recorded `EROFS`
   occurrences refer to the mailbox lock. Direct reservation and check-in
   worked. The new procedure should have one direct-chat route, with mailbox,
   help, authorization lookup and compatibility mechanics removed from its
   normal scheduling path. In the cold-operator setup, inherited role
   instructions should also stop sending a rehearsal operator to the Extender
   owner's inbox. Operator problems go to Smith in the operator chat.
   [Initial mailbox failure](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L18) ·
   [Check-in](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L1161)

### Firmware preparation and return to CLI

4. **The operator could find the artifacts and still had to design the
   programmer sequence.** The kit named the classic ESP32 app at `0x10000`,
   the P4-PC app at `0x20000`, and the EMOS full ROM. It left the operator to
   tie the two programmers to stable USB identities, resolve the version and
   syntax of each flasher, prove app selection, and pick the normal boot path.
   The classic app selection came from the matching retained partition and OTA
   evidence, with target identity checked at the write. The P4 worker read
   back the table and both OTA selection sectors and verified app0 before
   writing. The prominently discoverable P4 flash helper instead backs up
   all 16 MiB and writes a factory image at `0x0`. That helper would have had
   the wrong side effects for this test. The operator avoided it and composed
   separate command chains. The EMOS chain likewise needed fresh CLI input,
   the existing FLASH utility, a post-write boot, full-ROM SAVE and retrieval,
   and explicit listener shutdown.
   [Kit write scope](REHEARSAL-KIT.md#L63) ·
   [Classic layout discovery](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L250) ·
   [P4 and EMOS sequences](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L619) ·
   [Factory helper](../../../scripts/p4_flash_remote.py#L91)

5. **Byte verification and readiness were separate, and the latter actually
   failed.** An advancing boot epoch and neutral keys established that the P4
   observed an admission change. They did not establish a working MOS CLI.
   After the classic programmer's candidate read finished with `hard_reset`,
   the readiness worker stopped after 45.2s. Smith authorized one commissioned
   Agon-only reset. An actual listener start, read of a known file, and EXIT
   then succeeded. The final classic production restore left the programmer in
   the loader through readback and used one deliberate commissioned restart
   before the same CLI check. That worked on the first attempt. It is a
   concrete sequence to qualify as normal startup. The observations leave the
   earlier failure's cause open. The installer's per-image receipt has a
   pending readiness field at byte verification and the final installed-state
   writer fills in a separate boot receipt. Use explicit phase evidence to
   avoid interpreting either record alone as the whole operation.
   [Initial stop and recovery](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L589) ·
   [Final classic sequence](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L986)

6. **Old lifecycle rules gave different answers about failure and check-in.**
   The old firmware procedure allowed routine handback with custom firmware
   installed. The draft requires production on all three processors and
   restoration only of the ones the operator changed. The standing reset
   procedure prescribes a recovery sequence before asking the Author and says
   to use ordinary chat. The draft directs an attended operator to stop, keep
   custody and use **Agent has a question**. The operator used the draft and
   waited. At cutover, link each entry point to the new lifecycle and retain the
   reset and bare-metal repair commands as technical instructions for that
   authorized recovery. Define any planned restart as part of the component's
   normal install sequence. An unexpected timeout invokes the draft's stop
   rule, including its narrowly defined unattended exception.
   [Old firmware handback](../../procedures/olimex-firmware.md#L138) ·
   [Standing reset rules](../../bench-reset.md#L49) ·
   [Draft restoration and stop](PROCEDURE-DRAFT-R02.md#L84)

### Staging, invocation and evidence

7. **File transfer primitives worked. Package staging was missing.** The run
   needed a real prompt, explicit foreground listener start, two ROM payloads,
   the test executable and two generated ROM verification command files. The
   operator wired together the keyboard, fast SD client and process supervisor,
   checked for a stale result, created directories, read back each file, and
   exited the listener before flashing. The existing SD clients already provide
   transfer and pending-operation primitives. Provide one package-level command
   with declared directories, destination and expected bytes per file, fresh
   result handling, and a durable receipt. Keep one owner for the transfer
   session. Resolve a pending or uncertain commit before another submission.
   Reusing stale session state after switching transfer paths has caused
   trouble in the paired Moon Patrol fixture staging as well.
   [Staging and readback](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L169) ·
   [SD client](../../../scripts/sdcard.py#L53) ·
   [Staged client](../../../scripts/sdcard_staged.py#L25) ·
   [Moon Patrol transfer report](../../../../agon-dev-env/cross-agent/agentcoms/messages/2026-11-16_15-05-37_rally_mp006-standard-sd-transfer-guidance-one.md)

8. **The fixture plan gave commands and an oracle, with no command-correlated
   observer to run them.** A positive keyboard status proves input admission.
   A P4 screen-text response can describe the P4 display. Neither supplies the
   current Legacy mainboard prompt. The agent made eight numbered rounds of
   document and source lookups to derive command, mirror and prompt behavior.
   It found the bare `*` fallback in the MOS source and missed the normal
   `CLI$Prompt` initialization to `<Current$Dir> *`. The first runner enabled
   the mirror, captured exactly three bytes, `2f 20 2a` (`/ *`), rejected
   them, and stopped before `LOAD`, `RUN` or the P4 diagnostic. It left the
   mirror enabled and recorded that state. Smith saw the valid prompt and
   authorized the correction. The next worker captured a fresh sentinel,
   matched the actual command and return for `LOAD`, issued `RUN` once, and
   saw PASS plus a fresh prompt. It issued the mirror-off command, retrieved
   the Agon result, exited the listener, and ran the P4 probe. The physical
   test succeeded on its first actual invocation. Use a maintained observer
   with a declared output channel and capture grammar. The stream used here
   observed newly emitted bytes. An on-demand read of already displayed
   mainboard text remains separate work.
   [Observation discovery](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L643) ·
   [Stops and corrected invocation](../../../agents/bench019/rehearsal-r01/operator-run/OPERATOR-LOG.md#L855) ·
   [Serial routes](../../serial-monitor.md#L45) · [On-demand mainboard text](../BENCH-017.md)

9. **The patched runner passed this case and has an untested failure-path
   defect.** Its prompt matcher covers bare and root prompts. The fixture can
   also print `BENCH019 FAIL`, return 1, and have MOS emit its generic
   `Error accessing SD card` before the prompt. The parser expects only line
   breaks between FAIL and the prompt. It can time out despite having received
   the explicit failure. If the FAIL does match, the runner can issue further
   commands before treating it as a failure. This is a static finding and was
   not observed on the passing run. Test the observer offline against the
   actual capture, a non-root configured prompt, split reads and line endings,
   stale and echoed bytes, rejected LOAD, an early error plus returned prompt,
   explicit fixture FAIL and successful completion. Record the last command
   and whether it was submitted, observed to return, or left in doubt.
   Stop further dispatch on an unexpected problem. Treat the last known mirror
   and listener state as evidence for Smith.
   [Fixture source](fixture/src/main.c#L27) ·
   [Patched observer](../../../agents/bench019/rehearsal-r01/operator-run/run-frozen-fixture-resume.py#L53) ·
   [Frozen MOS return code and dispatch](../../../agents/bench019/rehearsal-r01/emos-src/src/mos.c#L1313)

10. **Check-in evidence was good, but the proof was specific to this run.**
    The operator's handback script expects three restore records and the
    corrected fixture's PASS. It discovers the available receipts through a
    glob. A reusable check should reconcile every recorded worker start to
    its original terminal receipt, check finished transfers and closed
    handles, and bind readiness evidence to only the components affected by
    the job. It should support a safe, authorized handback after a failed test
    as well as one after a pass. Use the supervisor's parent-written exits.
    The scheduler receives only the operator's ordinary release message.
    [Run-specific check](../../../agents/bench019/rehearsal-r01/operator-run/verify-final-handback.py#L23) ·
    [Existing supervisor](../../../scripts/bench_process.py#L63) ·
    [Final receipt](../../../agents/bench019/rehearsal-r01/operator-run/handback/handback.json)

## Corrective work following the rehearsal

| Priority | Deliverable | Evidence required |
| --- | --- | --- |
| 1. Usable job entry point | Link one current operator procedure from the controlling index and routine project instructions. The procedure links the maintained commands and a short current Pi5 bench binding. Keep device selectors, tool variants, network origin and reset wiring in the machine-local binding. Keep prior task transcripts and the firmware-owner publication process outside normal operator discovery. | A fresh operator reaches every required command from the single procedure and the job packet. Zero lookups in historical runs or component source for ordinary execution. Use the BENCH-018 cleanup inventory to fix references when promoting. |
| 2. Component install and restore | Provide a bounded install/restore entry point for each processor. Validate the named artifact and scope offline. After checkout, use the approved hardware binding and active write target, record the attempted change, write and independently verify the affected bytes, then prove normal startup. Reuse installed-state provenance for routine production checkout. | Production-only run has zero firmware reads, backups or writes. For a custom job, demonstrate bounds, rejection of a mismatched device or layout, exact post-write comparison and a fresh usable CLI. Restore only modified components, including the complete changed application extent. |
| 3. Package and foreground runner | Build on the existing keyboard, SD clients, passive serial and supervisor. Give the job packet explicit paths and required directories, invocation owner and commands, completion and error signals, bounds and output files. Expose staging, explicit start, collection and handback as separately callable phases so a human-start test can stop after staging. | Offline transcripts cover the two r01 stops and the failure paths above. A fresh runner can stage, verify, run and collect without reconstructing protocol code. Stage-only emits zero fixture invocations. A returned error is reported promptly and an uncertain dispatch has a durable receipt. |
| 4. Independent FIFO and notification test (deferred to real jobs) | Exercise the chat-only scheduler and its writable FIFO during real jobs, with actor identity from chat metadata, ordinary ID-only messages and forwarded Smith instructions for exceptions. | Verify durable queue contents across two ordinary waiters, check-in and immediate wake, rejected or uncertain send, and forwarded priority. The independent FIFO test is outside synthetic acceptance. |
| 5. Cold acceptance | Give a fresh operator the current procedure, job packet and pinned payloads. Have it keep the same kind of durable log and run the custom three-processor cycle. Check the production-only path offline. | Report queue time, preparation, fixture runtime, collection and restoration using parent timestamps. Count guidance lookups and unexpected help requests, and retain actual outcomes and clean handback. A passing normal path needs no project-source searches, local helper authoring, or additional instructions from Smith. |

Smith approved implementing the observer and supported commands, followed by
cold acceptance and cutover. The independent FIFO test is deferred to real
jobs. The next operator uses the draft's ordinary reservation and check-in
while rehearsing the maintained physical execution path.
[Cutover inventory](../BENCH-018/INVENTORY.md) · [Rehearsal pass condition](../BENCH-019.md#L104)
