# MOS/VDP firmware bug register

## Executive summary

Running cross-firmware record started 2026-09-20. Record defects in stock MOS/VDP
and Extender EMOS/EDP, including resolved defects and source-level hazards.
Platform manifestation and evidence strength are separate: an inherited source
bug is not automatically a reproduced hardware crash on both processors.
This is a findings register, not another work queue; TODO and linked tasks own
implementation and priority. No new tests or fixes are authorized by an entry.

## Recording convention

Use stable `FWBUG-NNN` IDs. Never renumber or reuse them. When a finding is
promoted to an implementation task, use the same ID and
`docs/tasks/FWBUG-NNN.md`; TODO remains the only work queue. Existing owning
tasks retain their history and reference this ID rather than creating a second
bug identity. Source task records must link back to the register and item.

Each ID is an identity, not automatic authority to begin fixing it.

Each entry identifies the affected component and
version where known, trigger/reproducer links, separate mainboard/Extender
observations, evidence status, disposition and owning task. Distinguish Author
reports, captured physical failures, host reproductions, source findings and
unverified suspicions. Keep fixed entries. Do not classify intentional behavior,
incomplete features or emulator-only problems as proven stock firmware bugs.

This initial index seeds the current palette finding and retained major records.
Older detailed findings remain authoritative at the links below; this is not a
claim that every historical audit item has already been individually backfilled.

## FWBUG-001 — Palette deletion advances an erased map iterator

| Field | Record |
|---|---|
| Component | Stock VDP v2.16.0 / vdp-gl `ac2dd5986daf496c43ae8e7fe41836274aec54a0`, inherited by EDP. `VGAPalettedController::deletePalette(65535)`. |
| Trigger | Custom Copper palettes exist, then palette cleanup runs during resolution setup. The loop erases its current unordered-map entry, then advances the invalid iterator. |
| Mainboard | **Manifests on mainboard — Author report, 2026-09-20.** Same faulty official source independently reproduced under host ASan. This investigation did not capture this palette fault on physical mainboard; its earlier sprite-scanout crashes are separate. |
| Extender | **Captured physical P4 crash**, installed `key-query-probe-r01-b2026-09-20-02-08-44Z`; fault PC resolves to this loop. EDP host extraction also reports heap-use-after-free. |
| Reproduction conditions | [Retained COP16_SETUP scene and hashes](tasks/QUAL-004/fixtures/SCENES.json), followed by the startup sequence described in [investigation results](tasks/AUDIT-007/mode-lifetime/RESULTS.md). Startup failed during 640×480 allocation before intended mode9 reselection. [Host reproducer](tasks/AUDIT-007/mode-lifetime/check_palette_iterator.py), [panic](tasks/AUDIT-007/mode-lifetime/panic.txt), [receipt](tasks/AUDIT-007/mode-lifetime/receipt.json). The hardware evidence here is P4 evidence, not a claimed mainboard test receipt. |
| Disposition | **Patching upstream and Extender deferred until more credits are available**, per Author. No patch applied. |
| Owner | [AUDIT-007 bounded investigation](tasks/AUDIT-007/MODE-LIFETIME.md); PORT-003 owns any later EDP correction. Upstream publication requires separate authorization. |

## Other retained findings

| ID | Defect / hazard and reproduction record | Mainboard | Extender | Disposition / evidence limits |
|---|---|---|---|---|
| <a id="fwbug-002"></a>FWBUG-002 | Sprite-scanout crash under bounded sprite scenes; [QUAL-004 results](tasks/QUAL-004/RESULTS.md), including BSP25_04; later [BENCH-007](tasks/BENCH-007.md) F01; [two-software-sprite setup](tasks/QUAL-004/sprite-scroll/RESULTS.md) stopped before its first capture. | Captured physical crashes in diagnostic runs. | No equivalent crash established by these records. | Unresolved. Latest first-scene reproduction blocks sprite/scroll qualification. [Official stock control](tasks/QUAL-004/sprite-scroll/stock-control/RESULTS.md) did not crash in one30-second observation; diagnostic influence, startup history and intermittency remain unresolved. Author deferred capture-interference investigation for token budget under [QUAL-004-CI01](tasks/QUAL-004.md#deferred-capture-interference-investigation--author-decision-2026-09-20). Subsequent stock visual review and clean exit passed. Keep separate from palette cleanup. |
| <a id="fwbug-003"></a>FWBUG-003 | Transform/sample numeric edge cases exposed by Rally; [Rally findings](tasks/QUAL-003/rally-excom/FINDINGS.md). | Same-game baseline does not establish equivalent manifestation. | Port numeric behavior required correction; see per-experiment evidence in linked findings. | Retained scoped corrections; not a claim that all Rally differences are solved or stock runtime is defective. |
| <a id="fwbug-004"></a>FWBUG-004 | Unsupported audio handler failed to consume complete VDU command payloads, disrupting later parsing; [grammar and fixture](tasks/PORT-004/audio-framing/PLAN.md), [results](tasks/PORT-004/audio-framing/results/README.md). | Reference behavior, not reported defective by this test. | Local parser defect, repaired with retained command grammar and unavailable audio backend. | Scoped framing repair accepted; audio synthesis remains unimplemented. |
| <a id="fwbug-005"></a>FWBUG-005 | Virtual-key query `VDU 23,0,&99,key` failed to generate its expected reply; [test contract](tasks/PORT-003/key-query/PLAN.md), [269-row physical results](tasks/PORT-003/key-query/RESULTS.md). | Reference behavior; no equivalent defect established. | Confirmed missing reply in old adapter; corrected on P4. | Bounded fix accepted. Preserve normal key-event semantics. |
| <a id="fwbug-006"></a>FWBUG-006 | Empty firmware-updater handler leaves selector/payload bytes in ordinary VDU stream; [exact grammars and source findings](tasks/PORT-003/command-consumption/README.md), [updater research](tasks/PORT-003/command-consumption/updater.md). | Stock handler is the reference, not the defective empty adapter. | Confirmed source-level consumption gap; do not inflate to a captured application failure. | All updater changes, including discard-only handling, deferred. |
| <a id="fwbug-007"></a>FWBUG-007 | Primitive completion and swap-notification hazards; [UPSTREAM-001 questions and preserved candidate](tasks/UPSTREAM-001.md). | Stock-hardware manifestation not established by the proposed A/B investigation. | Earlier local lifecycle findings/candidate retained; applicability to restored backend needs review. | Suspected upstream hazards, not blanket proven bugs. A/B research deferred; do not silently import old fixes. Queued operand lifetime is separately indexed as FWBUG-012. |


## Additional confirmed source findings — 2026-09-20

Source baseline for stock MOS below: v3.0.2,
`8336409351ee5314e02801a7b72a4f1bb5282519`. The audit documents contain exact
upstream source links. Read-only EMOS source check at `26ba877` confirms the
specific inheritance/correction notes below; no hardware run was made for this
register update. MOS and EMOS both execute on the mainboard eZ80: “Extender”
in these rows means the replacement EMOS build, not code executing on P4.

| ID | Bug and trigger / reproduction conditions | Stock mainboard | Extender | Status / disposition |
|---|---|---|---|---|
| <a id="fwbug-008"></a>FWBUG-008 | Raw SD write API `0x73` calls `_SD_readBlocks_API`. Valid unlock plus nonzero block count reads card data into the caller buffer instead of writing it. [Dispatch trace A010/A011](tasks/AUDIT-004/trace-mos-interfaces.md). | Source-proven v3.0.2 dispatch defect; stock emulator failure recorded. Stock physical cohort excludes this call. | Same call retained in EMOS `src/mos_api.asm::sd_api_writeblocks`. **Physical EMOS v0.1.17 failure recorded in mos-tests:** success returned but sector unchanged; C write control succeeds. [Existing tests/results](firmware-bugs/mos-tests-coverage.md). Ordinary FatFS writes use a different path. | **Independently discovered and verified:** Extender source audit plus existing mos-tests runtime evidence. Fix owned by mos-tests, deferred until tokens are available. If it blocks current Extender work, consider an EMOS-first patch and notify mos-tests with reusable patch/test evidence. No current blocker established; no patch started. |
| <a id="fwbug-009"></a>FWBUG-009 | Volume-label API `0xA4` calls `_f_setlabel` but lacks a return after restoring HL. It falls into setcp/not-implemented and reports status23 instead of the actual result, even if the label changed. [Wrapper trace](tasks/AUDIT-004/trace-mos-interfaces.md). | Source-proven v3.0.2 defect; stock emulator records status23. Stock physical cohort excludes it. | Same fallthrough retained in EMOS `src/mos_api.asm::ffs_api_setlabel`. **Physical EMOS v0.1.17 reports status23 for both seeds.** [Existing test/results](firmware-bugs/mos-tests-coverage.md). | **Independently discovered and verified:** Extender source audit plus existing mos-tests runtime evidence. Fix owned by mos-tests, deferred until tokens are available. If it blocks current Extender work, consider an EMOS-first patch and notify mos-tests with reusable patch/test evidence. No current blocker established; no patch started. |
| <a id="fwbug-010"></a>FWBUG-010 | Known UART reply type with payload shorter than its required length still dispatches; fields come partly from stale reusable-buffer bytes. Reproduce by a complete packet followed by a truncated-length packet of a known type. [T001 receiver trace](tasks/AUDIT-004/trace-primary-protocol.md#t001--reverse-framing-mos-receiver-and-failure-limits). | Source-confirmed missing per-type validation; no physical injected-packet run recorded. | EMOS retained UART0 parser still lacks general per-type checks. Its private graphics-result length check is not a general repair; the separate Extender UART receiver is not claimed affected by this record. | Open source-level defect; don't equate a result flag with validated payload receipt. |
| <a id="fwbug-011"></a>FWBUG-011 | Reply length above16 enters discard without saving that length. With previous length0 it discards256 following bytes, losing subsequent packets. [Exact state-machine trigger](tasks/AUDIT-004/trace-primary-protocol.md#t001--reverse-framing-mos-receiver-and-failure-limits). | Source-confirmed in selected stock MOS; correction not present in that reference. | **Corrected in EMOS source:** UART0 state1 saves received length before entering discard. Not a new physical retest. | Stock-side open; EMOS is not listed as still broken. |
| <a id="fwbug-012"></a>FWBUG-012 | Clearing bitmap/buffer ownership while queued primitives or active sprite frames still reference it can leave dangling operands. All-buffer clear calls `resetBitmaps` without its required prior sprite reset; oversized managed paths can clear borrowed points before execution. [F022 conditions and source evidence](decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md#integrity-audit-f022--queued-renderer-operands-and-persistent-users-outlive-their-owners), [PORT-003 D012](tasks/PORT-003.md). | Source-proven lifetime defect in pinned VDP/vdp-gl; isolated physical reproduction not established. | Historical retained exposure documented; current all-buffer clear still does not reset sprites. Native locking alone does not extend destroyed object lifetime. Full current-build trigger suite remains unexecuted. | Deferred under D012. Not asserted to be the root cause of FWBUG-002. Keep original F022/H002 IDs as aliases. |

No single-root-cause claim joins the sprite panic, palette iterator fault and
queued operand lifetime finding. They have different evidence and triggers.

## Existing MOS test-suite coverage

[Cross-reference against mos-tests](firmware-bugs/mos-tests-coverage.md) records
direct coverage for FWBUG-008/009, physical EMOS evidence, stock-hardware
exclusions and absent targeted coverage for the other registered bugs. Reuse
those tests rather than creating duplicate fixtures.

## Historical detailed registers

[REMED-002](tasks/REMED-002.md) indexes earlier EMOS/EDP transport, ownership and
implementation findings with their original stable IDs and mixed validation
states. Those records remain linked coverage rather than being relabelled as
current confirmed bugs. Add individual entries here as their source, applicable
build and reproducible conditions are reconciled; retain the original finding ID.
