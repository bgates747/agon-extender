# AUDIT-009 — Checks and coverage ledger

Baseline 2026-09-24 03:12:34 UTC: Extender b1d799e7, EMOS 895715e4, both main.
Only the proposed AUDIT-009 plan/TODO/log were dirty in Extender; EMOS was clean.
Approved contract frozen as 3fc623da. No bench endpoint is used by this audit.

Inventory: 1098 initial document/tool/reference records across Extender and EMOS.
Enumeration includes Markdown/text/manuals, relevant root script help sources,
identity records and hardware diagrams. Binary run payloads, screenshots, raw
captures, generated measurement tables and manifests are not individually body-
reviewed; their owning evidence index/provenance is retained. Vendor text is a
reference, not project operating guidance. The inventory labels metadata-only,
provenance-only and pending distinctly from a completed body review.

| Batch | Input documents (at most ten) | Work / state |
|---|---|---|
| B01 | README; HANDOFF; AGENTS; OWNERSHIP; docs/tasks/README; PLAN-001/QUEUE-REVIEW; canonical documentation conventions | Entry-point/authority review; consolidation map prepared |
| B02 | mainboard-sd; protocols/mainboard-sd; remote-keyboard; bench-reset; mos-recovery; sd-layout; web/README; EMOS docs/emos-utilities; REMOTE-005/FAST-TRANSFER; AUDIT-008/HARDWARE | Operating-journey review in progress; source checks scoped to their commands/contracts |

Source inspection is not a hardware test. Local help invocations and link checks
will be recorded here with limitations. Historical test passes retain their exact
scope; this audit does not rerun or broaden them.

## First operations/consolidation tranche

B01/B02 corrections are written. New role-named entry points are
`docs/using-extender.md` and `docs/building.md`; existing protocol/operation guides
remain authoritative. No scripts, source code, firmware or hardware changed.

| Batch | Inputs | Scope / disposition |
|---|---|---|
| B03 | architecture; protocols/browser-video; ADR-0020; ADR-0021; ADR-0022; BENCH-005; QUAL-003/mode-transition/AGENT-QUESTIONS; public-release-readiness; P01h/README | Relevant input/pacing/build claims checked; architecture body otherwise remains partly unreviewed. Old 30-Hz decision and later 60-Hz experiment separated. Publication findings retained with current dispositions. |
| B04 | EMOS README; projects/sdserve/README; OWNERSHIP; emos-v1-contract; emos-v1-qualification; repository-migration; tasks/AUDIT-008; initial-implementation-handoff; INTEG-014/E07P-results/README | Current SD/utility entry points corrected; cancelled module contract explicitly historical. Qualification/migration evidence not reinterpreted. Two similarly named MOS checkout roles clarified, not reassigned. |

Safe local CLI checks executed: `sdcard.py --help`, `sdcard.py ... put --help`,
`keyboard.py --help`, `screen_text.py --help`. All exited successfully without
opening an endpoint or creating a session. Options/examples also inspected
against argparse and service source. Rebuild commands were inspected against
Makefiles/wrappers, not compiled. No macOS execution is claimed; POSIX/Python
portability statements follow imports and retained use, not a new Mac test.

A lightweight local Markdown scan checked inline relative destinations and
GitHub-style heading anchors outside fenced code. The first Extender scan covered
707 Markdown files and 2320 links: four missing targets, no flagged anchors.
The extra-parent P01h ADR link was corrected. Three remaining predecessor
hardware links require archive provenance review. The first EMOS scan covered
74 files and 238 links: one misplaced INTEG-002 reference (corrected) and fourteen
migration-era handoff references. The handoff now explicitly redirects readers
to current authority; historical workspace links are not silently fabricated.
This scanner does not validate reference-style links, images, arbitrary HTML,
external HTTP destinations, case sensitivity on other filesystems or every
possible Markdown slug. These are mechanical checks, not body-review coverage.

`git diff --check` passed in both repositories after this tranche. Later totals
and checks will be recorded in the closeout. Private-address/path checks apply
to additions; historical source citations and Git author metadata are separate.

## Further bounded batches

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B05 | qualification/bench-constraints; qualification/capture-failure-protocol; testing/game-timing; qualification/README; hardware/esp32-p4-pc/README; firmware-bugs; BENCH-007 | Current input exception consolidated. Capture controls and test-measurement distinctions inspected. Timing runner needs procedure refresh before reuse. Bug entries/hardware library only scoped review, not exhaustive revalidation. |
| B06 | PORT-005; SETUP-005; ADR-0014; REMOTE-005; REMOTE-005/MOSLET-CHECK; TODO; EMOS REMOTE-005 | Current status reconciled with later acceptance; original evidence retained. Completed EMOS listener-MOSlet subtask removed from sibling unfinished queue; wider parent tasks remain. |
| B07 | protocols/browser-video; QUAL-003/debrief/P01h/CONTRACT; BENCH-005/composed-packing/PROTOCOL; BENCH-005/composed-packing/sixbit/PROTOCOL; dependencies/README; mainboard-sd-qualification-r01 | Promote wire details; retain frozen experiments and qualification identity. Dependency graph and frozen SD procedure explicitly bounded, not treated as current deployment recipes. |
| B08 | docs/README; using-extender; building; tasks/README; EMOS README; EMOS docs/README; EMOS emos-v1-contract | Apply Author's current-only handbook requirement. Resident ABI rewritten against maintained source; cancelled loader removed from current manual. Two reader walkthroughs below. |
| B09 | EMOS TODO; INTEG-009; INTEG-010; INTEG-011; INTEG-012; BENCH-001; QUAL-001 | Reconcile first four integration summaries with later Extender physical evidence. BENCH-001/QUAL-001 broader bodies remain partial; no blanket acceptance or queue completion. |

Current EMOS gateway table was checked against `src/emos.h`, `src/emos.c`,
`src/mos_api.asm`, `src/emos_sdlink.c` and `src/emos_uart_probe.c`. This is source
inspection, not ABI execution. The table preserves the 66-byte byte-array layout
and distinguishes resident services from disk utility admission.

Qualification generation: bare `python3` lacked jsonschema; retry using the
**documented repository virtual environment** succeeded:
`.venv/bin/python docs/qualification/scripts/regenerate-qualification.py --check`
reported 17 deterministic files. No generated file changed. A consistent
superseded candidate matrix is not current-mode acceptance.

Aggregate version validation still fails on the pre-existing r02 connectivity
hash mismatch. Both affected hardware files are unchanged from b1d799e7.
No identity was advanced and no digest rewritten to conceal that failure.

## Desk walkthroughs and journey map

These walkthroughs follow links from the new handbook; they do not contact any
endpoint, run a command on Agon or claim a new Mac/physical test.

| Journey | Human on Mac/Linux | Agent in another project | Result / remaining boundary |
|---|---|---|---|
| Discover / start | README → handbook → using-extender; owner supplies URL, bench availability and installed receipt | Same guides; ignored local bench record supplies private configuration | Endpoint and admission are explicit prerequisites, not inferred from checkout or stale status |
| Transfer | SD guide: local Python interpreter, `/emos/sdserve.bin`, Legacy/admitted input, normal or paired `--fast`, staged versus activated file | Same commands/contracts; local journal retained; independent application RAM preservation limit | Exact examples/options source/help checked; no hardware run |
| Uncertain request / stop | Same state journal; `resume` repeats only uncertain request; inspect before further action; Escape/EXIT returns to caller | Do not discard uncertainty, assume idle prompt or overwrite an executing batch | Service restart/new journal distinction is explicit; no automatic workflow resume promised |
| Observe / control | Browser Connect/Capture distinct; USB takeover; fullscreen Escape limitation | keyboard.py pacing/journal; `/screen/text` is ExCom pixel recognition, not MOS RAM or a Legacy prompt proof | Delivery counters do not prove command execution; unknown running application blocks CLI assumptions |
| Run another project | Current SD placement and LOAD versus EMOSlet distinction; mode/input independent | Preserve unknown/open files; no ad hoc direct UART ownership | Implemented subset and bug register constrain claims; no universal compatibility |
| Build / recover | Build guide → owning wrappers; reset guide distinct from ROM recovery | Same identities/receipts and owner authorization; no base-build equivalence assumed | F009 remains: public base builder does not reconstruct deployed overlays |
| Interpret tests / future hardware | Timing guide separates rendering, pacing, transport and fps; handbook distinguishes planned P4-PC/local output | Same scope plus capture controls, stale-runner reuse gate and evidence ownership | No HDMI/P4-local SD capability inferred from vendor samples; no new performance claim |

The two walkthroughs required no unindexed source excavation after the guide
corrections. Installed state and access authorization necessarily come from the
owner/local receipt; they are not missing public documentation. Full fresh-build
reproduction remains an identified product/build gap, not a solved walkthrough.

B10 reviewed `vdp/video/extender/web/protocol.md` and the maintained video
contract against `wired_network_service.cpp` and `app.js`. Replaced the obsolete
RGB888-only duplicate with a redirect. Retained single-viewer replacement,
explicit reconnect, malformed-credit/frame handling and static-response socket
closure in the canonical contract; did not infer all service failures have the
same WebSocket close code.

B11 reviewed the complete `protocols/excom-console.md` against EMOS's
`emos_console.c`/`emos_console_wire.h` and P4's `console_session.hpp`,
`console_hardware.inc` and `console_wire.h`. The paired wire headers compare
byte-identically. Updated the obsolete draft-only lead and made prepare-keep's
zero-challenge request explicit. Other bounds/lease/keep-display behavior agree
with inspected source. No control request was sent and no fault proof inferred.

B12 reviewed the complete `protocols/mainboard-sd.md` with `mainboard-sd.md`
and current listener `service.c`/host `sdcard.py`. Removed superseded ROM/reset
claims from the maintained contract. Corrected ACTIVATE description against its
actual finished-state, rename, digest and error branches, including the lack of
a global open-handle monitor. The standalone host `activate` is only an RPC;
independent target readback belongs to `put --activate` in normal mode or a
separate explicit comparison. No transfer was executed.

B13 reviewed `mos-recovery.md`, `bench-reset.md` and RECOVERY-001's acceptance
summary against maintained recovery-console/programmer source. The normal reset
bridge remains separate from ZDI programming. The current recovery path requires
a verified durable pre-erase dump and full 128-KiB post-write comparison;
optional historical-tool wording was removed. `mos_recovery_console.py --help`
and `prepare_mos_recovery.py --help` succeeded in the repository environment;
argument help does not open a serial port or generate/deploy a payload.

## Final local checks for this tranche

Final Markdown scan: Extender 709 files / 2394 inline relative links, three
known predecessor-hardware missing targets; EMOS 75 files / 260 links,
fourteen migration-handoff missing targets. No flagged local anchors or new
changed-document failures. A separate check of revised tracked documents found
no in-repository link target existing only as an ignored local file after the
handoff correction. External repository/HTTP links were not fetched.

All 51 linked authoritative Extender TODO entries resolve to detail files.
EMOS's linked entry titles/details resolve too. Cross-repository task mentions
are not misclassified as missing local task files. Canonical dependency-graph
validation passed (`graph:agon-extender:vdp-source-selection-v2`); no source-root
reconstruction or new reviewed graph input was performed.

Final whitespace checks pass in both repositories. A temporary CSV CRLF output
was normalized back to LF before commit. Added tracked content has no matches
for the checked private home/mount path or LAN-address patterns; this is a
bounded pattern check, not a proof against every possible identifying datum.
No endpoint, board, emulator or SD operation was performed. No source or tool
implementation changed. The cross-machine mailbox contained no requests at
both the opening check and the closeout check.

## Second unattended pass

Window authorized 2026-09-24 04:07:22–05:07:22 UTC. Starting commits:
Extender 461b59f4, EMOS b2eff09; both worktrees clean. Opening mailbox empty.

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B14 | architecture; architecture/vdp-upstream-precis; decisions/README; hardware/README; SETUP-005; HW-002; r03 hardware README; ADR-0014; ADR-0016; ADR-0017 | Architecture body reconciled with current guide/evidence boundaries. Hardware and callback capability claims corrected; Legacy SD exception promoted from accepted PORT-017 operation. SETUP-005/ADR-0014 historical decisions retain dates with current authority explicit. HW-002 remains partial; no circuit or architecture decision changed. |

The pinned upstream video.ino creates processLoop with stack argument 4096.
Espressif's installed FreeRTOS task.h explicitly defines this argument in bytes,
unlike vanilla FreeRTOS; the précis's word unit was corrected. This is a source
contract check, not a new stack-usage measurement or a new upstream baseline.
The broader précis retains its dated release baseline; latest-release discovery
is outside this batch.

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B15 | The nine revisioned Markdown procedures under docs/procedures | Status/identity/applicability triage for all nine. Full bodies inspected for numeric import, canary r03 and frame-service r03; others retain metadata-only or previous partial coverage. Created one current applicability index, leaving frozen recipes intact. Numeric runner and parser/renderer sanitizer commands inspected; only --help executed, no compilation or tests claimed. |
| B16 | qualification/README; dependencies/UPSTREAM-WATCH; new procedures/README; handbook index | Linked current applicability, verified role separation and import ownership. Corrected the numeric procedure's abbreviated source-graph path. |

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B17 | TODO; PLAN-001/QUEUE-REVIEW; REMOTE-001; REMOTE-001/C01-ui-cleanup; REMOTE-002; BENCH-004; NET-001 | Selected current-status and acceptance claims checked against retained follow-ups and commits d86739bf, a67aa2d3, c73b458c. Removed stale current-uncommitted/installed claims from entry summaries. No human gate closed. Full historical execution-body verification remains partial. BENCH-004 still lacks the specified peer receipt; empty mailbox checks are not that receipt. |

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B18 | Six examples/*/README files; assets/notifications/README; sd-layout | Example bodies reviewed against output paths in source and qualify_keyboard.py. Road/video-marker invocation guidance corrected to mode-in-autoexec and evidence working directories. Fixed-path/old-listener fixtures explicitly require owner refresh before reuse; reusable notification receipt remains dated evidence, not current installed proof. No example executed or compiled. |

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B19 | hardware/objects/README; objects.yaml; schema.json; P4-PC library README; PROVENANCE.json | Object guide inspected and validator passed for 41 objects. Library provenance verified for all 39 originals/derivatives; no hash mismatch. This checks stored snapshot integrity, not accuracy of every upstream page or hardware compatibility. |
| B20 | LICENSING; root LICENSE header; retained agon-vdp-release LICENSE; vdp-gl displaycontroller notice | Scoped notice/provenance check: project GPLv3 text, retained MIT notice and upstream GPLv3-or-later attribution present. No new license terms, legal interpretation or exhaustive redistribution review. |
