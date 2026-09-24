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

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B21 | firmware-bugs; firmware-bugs/mos-tests-coverage; QUAL-004; sprite-scroll/RESULTS; extender-followup/RESULTS; packed-expansion/RESULTS | Reconciled current FWBUG-002/QUAL-004 coverage with later paired passes. Source-baseline MOS findings and dated mos-tests cross-reference retained; no new MOS tests or current-branch defect revalidation. Original failure remains unresolved, not a blanket block on subsequent accepted checkpoints. |

Second-pass checkpoint prepared at 2026-09-24 04:24:31 UTC, within the one-hour
ceiling. Eight additional batches B14–B21 complete their stated review scope;
whole-audit coverage remains open. Whitespace checks pass. All 55 TODO-linked
task/evidence targets exist (this counts repeated and evidence links, not 55
distinct queue tasks). Added-line private home/mount/LAN pattern scan found no
matches. Changed file types are Markdown and inventory CSV only. Final mailbox
empty; sibling EMOS worktree clean. No push performed.

## Third unattended pass

Authorized window: 2026-09-24 04:26:44–05:26:44 UTC. Baseline Extender
8c3d67a8; opening worktree and mailbox clean. Documentation/local checks only.

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B22 | PORT-006; MODE-001; MODE-002; DIAG-001; PORT-004; PORT-005; PORT-007; P4PC-001; LINK-001; QUAL-001 | Current capability/task summaries inspected; future requirements kept distinct from implemented services. Removed active stale video-only/input-deprecated and pre-framing instructions. Retired LINK-001's cancelled MOS-module reconsideration. Existing unlabelled action steps in MODE/DIAG/LINK normalized to stable IDs/check boxes without adding work. Long task execution histories remain partial. |
| B23 | PORT-004/audio-framing/results/README; current console/keyboard/SD contracts; qualification/README | Supporting accepted scope: Rally framing visual review accepted, audio synthesis absent; bounded keep-display exists; matrix candidate still superseded; P4-local SD distinct from mainboard service. Evidence review, no new test or current firmware claim. |

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B24 | ADR-0001–0008 metadata; decisions/README | Navigation/metadata extraction only; no new body or qualification review. Added current decision index with explicit authority/completeness limits. |
| B25 | ADR-0009–0016 metadata | Index consistency only; prior body-review states preserved. |
| B26 | ADR-0017–0022; SD-layout ADR | Metadata indexed; bodies of ADR-0018/0019/0022 inspected for current applicability. Original 5-fps removal linked to later pacing/codec decisions; stale goal-specific flash/demo authorization removed from current ADR prose. No accepted architecture changed. |

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B27 | versions/README; EXAMPLES; REVIEW; SCHEMA; baselines/README; dependencies/schema/README | Body review of policy/field/navigation guidance. Corrected baseline filename explanation and hypothetical-example scope; reconciled failure-retention wording with the Author's existing local rule. No registry/status/hash or evidence changed. Validator implementation inspected for declared shape/status limits, not blanket semantic proof. |

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B28 | agentcoms.py; analyze_browser_timing.py; bench_job.py; capture_general_poll.py; capture_keyboard.py; capture_uart_flow.py; capture_uart_roundtrip.py; capture_visible_text.py; check_numeric_port.py; console_peer.py | Script role/description inspection for host-tool index only; no hardware, emulator, build or benchmark execution. Previously reviewed active contracts retain their stronger scoped checks. |
| B29 | keyboard.py; measure_video.py; mos_recovery_console.py; plot_rally_learning.py; prepare_browser_typing.py; prepare_console.py; prepare_console_review.py; prepare_general_poll.py; prepare_keyboard.py; prepare_mos_recovery.py | Script role/description inspection for host-tool index only; no hardware, emulator, build or benchmark execution. Previously reviewed active contracts retain their stronger scoped checks. |
| B30 | prepare_sd_headless.py; prepare_text_sample.py; prepare_uart_flow.py; prepare_uart_forward.py; prepare_uart_roundtrip.py; prepare_usb_cli.py; prepare_usb_keyboard.py; prepare_visible_text.py; qualify_keyboard.py; qualify_rally_drive.py | Script role/description inspection for host-tool index only; no hardware, emulator, build or benchmark execution. Previously reviewed active contracts retain their stronger scoped checks. |
| B31 | qualify_rally_headless.py; qualify_rally_traffic.py; qualify_sd_headless.py; qualify_sd_keyboard.py; qualify_sdcard.py; rally_drive.py; rally_race.py; rally_trial.py; report_rally_learning.py; reset_agon.py | Script role/description inspection for host-tool index only; no hardware, emulator, build or benchmark execution. Previously reviewed active contracts retain their stronger scoped checks. |
| B32 | reset_bridge.py; review_text_sample.py; run_hello_demo.py; screen_text.py; sdcard.py; validate-hardware-objects.py; validate-version-records.py; vdp-pio.sh | Script role/description inspection for host-tool index only; no hardware, emulator, build or benchmark execution. Previously reviewed active contracts retain their stronger scoped checks. |

All 48 root scripts have an index entry. This establishes discoverability and
role classification, not full body review or current fixture readiness. Script
descriptions were parsed locally without importing or executing their modules.

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B33 | assemblies/README; assembly r01/r02 README; harness r01/r02 README; r02 BOM and signal-view README; LA03 r01 README; visible-text fixture README; HDMI-DRIVERS | Current applicability/provenance review; revisioned circuit and generated artifacts unchanged. Corrected r01's stale current-r02 pointer and assembly index. Visible-text contract checked against current EMOS text-probe bounds/admission; corrected placement/readiness guidance. Large revisioned design bodies only partly reviewed; HDMI report remains a dated source-research result, not tested integration. |

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B34 | EMOS browser_typing_peer; keyboard_api_peer; keyboard_wire_peer; prepare_boot_review; prepare_browser_typing_review; prepare_keyboard_api_review; prepare_sdserve; prepare_usb_cli_review; review_boot; review_general_poll | Tool descriptions parsed without import/execution. prepare_sdserve body/default Makefile and current listener guide checked: identified helper is ordinary application, not MOSlet. |
| B35 | EMOS review_keyboard; review_uart_flow; review_uart_probe; review_visible_text; stage_emos_media; usb_cli_peer; verify_hardware_capture; new scripts/README; docs/README | Completed all 17 root-tool role entries. stage_emos_media source still expects cancelled provider media; index distinguishes it from EMOSlet installation. No helper run or source changed. |
| B36 | EMOS port-200-qualification; port-203-hardware; tasks/README; research/README; projects/{emos,emos-utility,keyboard-wire,keyboard-api,port008-forward,integ014-dual-uart}/README | Current applicability checked; original physical procedure clearly historical, module manual points to current utilities, old parallel fixture no longer selects current route. Retained keyboard fixture paths need refresh; no profile/fixture changed. |
| B37 | EMOS tests/uart_put_cpu/README | Full documentation body inspected for stated scope: linked instruction comparisons, not physical timing or hardware acceptance. No execution. |

Inventory role labels for retained hardware test captures/procedures and generated
dependency output were corrected by path. Review states were not promoted by
that classification. EMOS tool coverage is 17/17 entries; documentation does not
assert these historical tools currently run with new inputs.

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B38 | PORT-003; PORT-008; AUDIT-007; AUDIT-008; PORT-008 UART findings; PORT-003 key-query results; AUDIT-007 findings and MODE-LIFETIME; AUDIT-008 HARDWARE and IMPLEMENTATION summaries | Current opening/status claims reconciled with later evidence; long histories remain partial. E07P restoration/E09 completion supersede incomplete recovery; accepted audio/query slices supersede planning-only claims. Palette mainboard manifestation remains Author-reported, not newly captured. No defect fix, test or acceptance gate added. |

Third-pass checkpoint: 2026-09-24 04:48 UTC, about 22 minutes into the one-hour
ceiling. Seventeen additional batches B22–B38 completed their stated scopes.
Script indexes cover 48/48 Extender and 17/17 EMOS root tools. All 55 Extender
and 17 EMOS TODO-linked task/evidence targets exist. Added-line private home,
mount and LAN-address pattern checks pass; changes are documentation/CSV only.
Relative-link scans retain the known 3 Extender / 14 EMOS historical missing
targets and report no new changed-document failures. Mailbox empty. No bench,
network endpoint, source implementation, firmware, SD or emulator operation;
no push. Main handbook use does not depend on finishing every archive body.

Local subject commits: Extender 89efe5d0 (capabilities and tool applicability),
EMOS 2408f31 (tool index and historical procedure boundaries); final current-task
summary/coverage closeout is committed separately in Extender.

## Fourth unattended pass

Authorized window: 2026-09-24 04:50:15–05:50:15 UTC. Baseline Extender 836d399d,
EMOS 2408f31; both worktrees and opening mailbox clean. Contract frozen in
580c4ab5. Documentation/source inspection and safe local checks only.

| Batch | Inputs (at most ten) | Scope / disposition |
|---|---|---|
| B39 | ADMIN-001; AUDIO-001; BENCH-002; BENCH-006; BENCH-008; REMOTE-003; REMOTE-004; REMED-003; NET-002; UPSTREAM-001 | Entire task bodies read for current scope, status and authorization. Reconciled test-only pacing, completed text readback, delta rollback and implemented Pi browser reset. Closed/deferred research remains closed/deferred; no human gate waived or old experiment restarted. |
| B40 | AUDIO-001/RESULTS and sdbench source/CSV; BENCH-002/RESULTS; BENCH-006/RESULTS and README; BENCH-008/RESULTS; NET-002/REVIEW; REMED-003 issue draft; ADMIN-001 findings opening | Supporting evidence/applicability checked. Storage range corrected from its six retained rows, not new timing. ROM headroom updated from already-reviewed AUDIT-008. Networking upstream claims and emulator defect were not freshly revalidated. Historical fixture output paths need owner refresh. |
| B41 | screen_text.py; network/screen_text.hpp; HTTP registration; new screen-text guide; handbook; using-extender; host-tool index; bench-reset | Current source/guide comparison: sampling bounds, shared pending/result consumption, 200/202/409, polling and timeout limits. Promoted recurring screen-text instructions out of the task silo, leaving evidence/local check there. Executed only screen_text.py --help; no endpoint, compile or capture. Reset comparison used existing maintained contract, not hardware inspection. |
| B42 | ADR-0001–0010 | Full decision bodies read; source/build boundaries, framework, silicon, flash, memory, partitions, CMake, wrapper and frequency compared with the following batch. Kept original architectural decisions and qualification distinctions. Added updater/crash-product applicability and documented existing wrapper pin guard. |
| B43 | platformio.ini selected sections; board JSON; sdkconfig.defaults; partitions.csv; vdp-pio.sh; generated CMake adapters; SETUP-001 bring-up/configuration excerpts; building guide | Read-only configuration and retained evidence check. Build guide now separates 360-MHz SDK from 400-MHz board field, first-stage DIO header from configured QIO, and partition reservation from implemented services. Local generated SDK bounds 199 observed only as generated state, not a new qualified build. No build/dependency install or physical operation. |

The storage CSV advertises CLOCKS_PER_SEC=100, and source uses clock() with that
application constant. Range calculations here follow its stated convention;
no independent wall-clock calibration is added. The six rows yield 186.86–199.22
KiB/s and modeled read-plus-historical-send 1.0700–1.1272 seconds per audio second.
The historical send and current read observations are still separate experiments.

Fourth-pass checkpoint: approximately 9 minutes, below the one-hour ceiling.
B39–B43 complete within their recorded scope; full audit remains open. Final
mailbox empty. Both source repositories were clean at entry; EMOS remains
unchanged. Local commits: 580c4ab5 freezes scope, ccb347c1 consolidates task/build
and screen-text guidance; final coverage closeout committed separately. No push.

## A09-N01 — upstream fidelity and dependency ownership

Contract frozen in 1beae077 before review. Documentation/source inspection only;
no goal time allowance was requested for this bounded step. No bench, build,
network request, firmware, emulator or upstream checkout change.

| Batch | Inputs | Scope / disposition |
|---|---|---|
| B44 | ADR-0011, ADR-0012, ADR-0013 | All three decision bodies read. Compared against maintained architecture, ADR-0014/0022, keyboard/build guides, reviewed source-baselines.yaml, vendor library.json records, p4-console-source-selection.json and select_sources.py. PlatformIO C++17/platform pins and the console dependency lock inspected as build inputs. No source-baseline regeneration or new upstream release survey. |

ADR-0011 now distinguishes recorded import identity from newest-release policy
and reiterates the already accepted first-port fidelity/no incidental bug-fix
rule. ADR-0012 records selected ESP32Time 2.0.6 and CRC 1.0.4 and distinguishes
vendored upstream libraries from managed components/toolchain downloads.
ADR-0013 aligns input with accepted P4 USB/browser/agent arbitration, limits the
physical-keyboard exclusion to FabGL PS/2, and separates deferred services from
implemented capability. Decision status/completeness and architectural choices
are unchanged. The build guide provides the corresponding current navigation.

Reviewed graph declarations are fingerprinted historical inputs, not a complete
present-day patched-tree audit. No exhaustive compatibility delta or new runtime
qualification is claimed. Findings A09-F053–F055 record these corrections.

Validation: 714 Markdown files / 2635 relative links; only the same three
known historical missing targets, no new link findings. CSV coverage totals
reconciled; whitespace check passed after preserving LF inventory line endings.
No fresh source-delta verification or claim of full upstream parity.

## A09-N02 — display backend contract

Prior N01 commits pushed to origin/main with no remote divergence. N02 contract
frozen in 6f583fa0 before execution. No build, benchmark or bench operation.

| Batch | Inputs | Scope / disposition |
|---|---|---|
| B45 | ADR-0015 full body; architecture display section; maintained console selection; stock_p4_service.cpp/.hpp; stock_native_access.cpp; stock_runtime_controller.cpp/.hpp; snapshot pool admission/acquisition; agon_screen.h refresh binding; PORT-003 current summary and QUAL-004 results scope | Reconciled current ownership and evidence limits. Original depth controllers remain native storage/rendering owners. Timer accounts elapsed frames and separately wakes drawing/output workers; mode refresh supplies its period. Drawing drains until empty/suspended. Output uses per-row exclusion and normalizes outside it; base snapshots are demand-driven. No fresh jitter, runtime parity or installed-overlay verification. |

ADR-0015 no longer calls the generic controller the existing implementation or
implies a single frame-service task. Architecture reflects the same maintained
binding. Original phase gates are evidence of their identified builds, not an
automatic instruction to restart them. A source/evidence table separates clock,
drawing, snapshot composition, delivery and mode lifetime. Experimental flags
are explicitly not qualification of alternate exclusion/scheduling policies.
Static-image comparisons do not establish animation or performance parity.

N02 validation: whitespace check passed; 714 Markdown files / 2646 relative
links checked, with the same three historical missing targets and no new
changed-document findings. No firmware or emulator tests required for these
documentation-only corrections.

## A09-N03 — remediation-plan reconciliation

Contract frozen in e4a06f79 before editing either remediation plan. Opening
worktree/mailbox were clean. Documentation only; no source, generator, build,
firmware, network or bench operation.

| Batch | Inputs | Scope / disposition |
|---|---|---|
| B46 | REMED-001 and REMED-002 bodies; supporting current SETUP-005 integration/F018 statement, PORT-008 summary, PORT-006 F003/F012 execution record, REMOTE-001 and LINK-001 ownership, QUAL-002 state, qualification README, original preactivation corrective action scope | Replaced obsolete global current-state instructions with bounded applicability and explicit remaining gates. Preserved dated execution/provenance evidence. Current UART/ExCom acceptance is not global four-mode, parallel, or electrical qualification. |

F010 ownership separation is recorded complete from REMOTE-001/LINK-001; F016
status bookkeeping is reconciled with already checked REMED-002 Work 4.c and
QUAL-002's explicit hold. Neither closes underlying physical/user gates.
F003/F012 now describe implemented, host-tested corrections with physical
resilience validation still open. F018 remains open outside the separately
accepted no-restart CLI increment. Superseded hardware-task-creation and
parallel-first sequencing instructions no longer direct current work.

All historical P001–P044 correction identities and evidence remain intact.
Their individual source fixes and test outcomes were not rerun or independently
reproved. Both remediation tasks remain open; generated matrix and dependency
records were not changed. Review-state promotion covers document bodies and
current applicability only, not exhaustive validation of linked historical
artifacts or wholesale closure of the underlying findings.

N03 validation: 714 Markdown files / 2654 relative links, with only the same
three historical missing targets and no new changed-document findings.
Whitespace and inventory totals checked: 111 reviewed, 145 partial, 140
metadata-only, 44 provenance-only, 668 pending; 1108 total. The two remediation
bodies moved from pending, not partial.

## A09-03 — workflow traceability follow-up

Author approved filling the map after the reporting review. Prior N03 commits
were pushed through 5d9aac49 before the report edit. Compared the required nine
fields with using-extender/building, SD start/stop/install guidance, reset and
ROM recovery boundaries, game-timing use/collection, console mode commands and
P4-PC reference provenance. Read canonical emulator instructions for ownership
and setup boundaries only; no emulator-specific procedure/profile was changed.
RESULTS now accounts explicitly for each field in seven workflow tables.

No new document body is promoted in the inventory and no new runtime test is
claimed. Existing build gap F009 remains; F060 records the uncompleted portable
emulator-guide path under existing A09-04/08. A09-03 is complete as mapping,
not as operational qualification. N04 remains unstarted.

Validation: whitespace passed; 714 Markdown files / 2696 relative links,
only the same three historical missing targets and no new link findings.
Seven field-accounting tables cover entry point, tool, command, owner, transport,
build, SD location, evidence and stop/recovery. No bench endpoints used.
