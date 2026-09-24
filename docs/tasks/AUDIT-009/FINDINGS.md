# AUDIT-009 — Findings

Findings distinguish erroneous current guidance from valid historical evidence.
The task checklist owns execution; this register tracks claims and dispositions.

| ID | Class and affected claim | Evidence / correction | State |
|---|---|---|---|
| A09-F001 | Incorrect availability: README says SD source not on public main and browser input deferred | EMOS published 7c15439/895715e and Extender 77c25ebc/b1d799e7; REMOTE-001 deployment history | Fixed: current landing page |
| A09-F002 | Stale orientation: HANDOFF still calls screen capture uncommitted and browser input unimplemented | Subsequent committed/deployed REMOTE-001, REMOTE-003, AUDIT-008 records | Fixed: current handoff; Git history retained |
| A09-F003 | Operational circularity: remote agent told to type its own unavailable KEYINPUT admission | Author correction; keyboard.py Client.open requires ready/neutral; EMOS owns admission | Fixed: prior keyboard admission explicit; startup/operator recovery if absent |
| A09-F004 | Conflicting keyboard guidance: remote-keyboard.md planned-only browser section; web README says retired/no keyboard | REMOTE-001 later UI/deployment records; current app.js/keyboard_session.js, browser_keyboard.inc | Fixed: deployed behavior and remaining platform/human gates explicit |
| A09-F005 | Obsolete reset prohibition in mainboard-sd.md | bench-reset.md and REMOTE-003 document corrected Pi actuator/button; SD protocol itself still has no reset | Fixed: independent reset path linked; ROM recovery distinct |
| A09-F006 | Wrong browser asset claims: no keyboard endpoints, RGB888 only, pre-input page | Current wired_network_service.cpp registers /keyboard/browser; base decoder supports RGB222 and deployed overlays provide later codecs | Fixed: source README gives role/links and base-versus-overlay boundary |
| A09-F007 | SD protocol admission wording excludes supported MOSlet RAM | EMOS v0.1.18 gateway changes and v0.1.19 physical /emos checks | Fixed: source-confirmed caller ranges and ownership |
| A09-F008 | Normative 30fps text versus later 60Hz browser request behavior | architecture.md/ADR-0020 versus BENCH-005, QUAL-003 and app.js | Documented unresolved: normal contract versus retained experiment; QUAL-003/BENCH-005 |

Resolution evidence and additional findings will be appended per bounded batch.

## Additional findings and dispositions

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F009 | Operationally consequential build gap: base p4-console instructions look like a rebuild of the installed combination | `prepare_console.py` invokes base source; BENCH-005 and REMOTE-001/003 record snapshot parents and codec/browser overlays, some in ignored artifacts | Documented in building.md and web README. Source/build consolidation remains unresolved; Extender build/PORT-003 owner, separate implementation scope required. No equivalent fresh-clone build claimed. |
| A09-F010 | Architecture still says browser input deferred and selects a separate browser ingress | Accepted ADR-0022 common `KEYINPUT extender` arbitration supersedes the old paragraph | Corrected architecture to already accepted decision, without changing behavior or qualification. |
| A09-F011 | Publication review's old findings read as current | September 13 findings versus current commands/README/EMOS commits | Added dated disposition table; preserved old security checks and unresolved test failures. |
| A09-F012 | Broken historical navigation | Local Markdown scan: P01h RLE2 ADR path has one excess parent; three predecessor hardware evidence references lack targets | Corrected P01h link only. Hardware references require archive-owner provenance, not guessed replacements. |

A09-F001–F007 are corrected in the current guides/entry points. Manual lock controls are already absent from the maintained page. Existing pending
physical LED/platform acceptance is preserved, not promoted to a pass.
F007 was checked against `agon-emos/src/emos_sdlink.c`'s complete-buffer range
`0x040000..0x0B7FFF` and the retained AUDIT-008 hardware result.

F008 is **documented but unresolved**, owned by QUAL-003/BENCH-005: ADR-0020
accepts 30fps at 512×384 and explicitly does not claim a production limiter.
BENCH-005 authorized a later 60-Hz request experiment. Retained candidates use
that experiment; no evidence reviewed here establishes a general replacement
of the normal-output contract. Current guides distinguish them and point to
the cross-agent comparison. No rate or firmware was changed.

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F013 | Cancelled `.emo` design still presented as the EMOS v1 contract | AUDIT-008 and current EMOS utility contract retire discovery/registry/load/swap; retained SD range includes MOSlets | Fixed: current resident ABI replaces the cancelled loader manual at its stable path; old design retained in Git. |
| A09-F014 | EMOS listener README leads with ordinary application and old `/mos` location | Later v0.1.19 physical migration and current service build variables | Rewritten around current EMOSlet, two memory layouts, authoritative external guide, normal/fast and chronological evidence. |
| A09-F015 | Ambiguous stock reference versus working MOS fork in sibling ownership guide | Extender OWNERSHIP and canonical instructions distinguish canonical stock checkout from `mystuff/agon-mos` | Clarified both roles without changing ownership or editing either checkout. |
| A09-F016 | EMOS migration handoff has fourteen broken former-workspace links | Local scan and repository-migration provenance | Historical-context banner and current redirects added; former links retained as history. Not a current operational blocker. |
| A09-F017 | REMOTE-005 TODO still names v0.1.18 as current listener combination | AUDIT-008/HARDWARE later v0.1.19 and `/emos` deployment | Updated queue summary; broader REMOTE-005 work remains open. |

## Current-handbook consolidation

The Author clarified that the deliverable is one current handbook, not old
instructions with correction banners. `docs/README.md` now indexes role-named
current guides. EMOS's stable resident-contract path has been rewritten to the
current ABI; the cancelled loader specification is retained in Git, not in that
manual. This completes the documentation correction for F013. The historical
migration handoff remains evidence outside the current reading path.

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F018 | Bench constraint reads as banning all interactive tests despite accepted replacement input | BC-001's later PORT-015 acceptance and current keyboard guide | Rewritten as one current constraint: mainboard input unavailable; admitted P4 input permitted; installation/recovery cannot depend on unavailable input. No qualification expanded. |
| A09-F019 | Timing-package reuse can appear ready under current fixture policy | `tests/performance/run.py` still generates mode selection in EXEC and ordinary application listener return; current AGENTS requires mode selection in autoexec | Guide and BENCH-007/TODO flag procedure refresh before reuse. BENCH-007 owns future runner/procedure work; no runner changed. |
| A09-F020 | Frozen SD qualification procedure predates current EMOSlet/reset behavior | mainboard-sd-qualification-r01 versus current service and reset guides | Current SD guide identifies r01 as historical, not a current deployment recipe. REMOTE-005/SD qualification owner must refresh it before new acceptance. Frozen identity unchanged. |
| A09-F021 | Canonical dependency graph may be mistaken for deployed P4 build closure | Reviewed `p4-default` profile versus actual `p4-console` selection and task overlays | Dependency guide now states exact baseline scope and links current build boundary. Underlying reconstruction gap remains F009. |
| A09-F022 | EMOS queue and task opening states lag later physical evidence | INTEG-009–012 original pending states versus PORT-015, PORT-008, QUAL-003 and game-timing results | Current summaries reconciled; broader parity and production callback gates remain open. No blanket task closure. |
| A09-F023 | Recurring browser encoding details scattered across experiments | P01h RLE2, BENCH-005 palette/direct-six-bit and pair contracts | Promoted established wire details to protocols/browser-video.md; task contracts link current authority. Optional candidate encodings remain distinct from accepted default and base-checkout support. |
| A09-F024 | Aggregate version validation already fails | light2-harness-r02 connectivity digest differs from its profile; both files unchanged from audit baseline | Existing failure retained, not repaired by rewriting hashes. Hardware/version-record owner under HW-002 must reconcile provenance before using that held design. |

All consequential unresolved findings have an existing owner: F008 pacing
reconciliation (QUAL-003/BENCH-005), F009 build reconstruction (PORT-003),
F019 timing-procedure refresh (BENCH-007), F020 SD qualification refresh
(REMOTE-005), F024 held hardware integrity (HW-002/version records). F012/F016
are archive-navigation defects owned by their respective hardware/migration
records. Finding ownership does not authorize implementation or a new bench run.

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F025 | Source-local browser protocol duplicates an obsolete RGB888-only contract | `vdp/video/extender/web/protocol.md` versus maintained browser-video contract and actual service/client | Replaced duplicate with a current-authority link; promoted viewer replacement and verified error behavior to the maintained protocol. Historical wire restriction stays in Git. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F026 | SD wire guide retains old reset prohibition/ROM figures and overstates ACTIVATE work | Current `service.c` FINISH/ACTIVATE and host `upload`: FINISH checks stage, ACTIVATE checks target in normal mode; no second stage digest or global handle closure | Current contract corrected; generic failures distinguished from RECOVERY_REQUIRED. Operator guide distinguishes `put --activate` host readback from standalone `activate ID`. No implementation or guarantees changed. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F027 | Maintained recovery sequence calls pre-erase dump optional despite current host guard | `mos_recovery_console.py` requires verified durable before-ROM before RESTORE and compares full 128 KiB afterward; maintained programmer requires DUMP first | Corrected current manual to its existing implementation, removed obsolete fallback wording and led with maintained programmer. Historical recovery retained through evidence links. Documentation erratum only: no new procedure identity, tool or hardware execution. |

## Architecture and hardware reconciliation

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F028 | Architecture applies held four-chip r02 isolation to active r03; hardware index denies later bounded validation | HW-002, r03 specification, PORT-008/015 and existing SD/console acceptance | Fixed current architecture/index and ADR-0016 applicability. Full r03 electrical/as-built review remains HW-002; no circuit promoted or frozen model edited. |
| A09-F029 | Accepted future callbacks/audio requirements read as implemented capabilities | ADR-0017 consequences and PORT-004/QUAL-003 scope | Explicit implementation-boundary table and requirement wording. No generalized callback ABI or audio implementation claimed. |
| A09-F030 | Legacy mode permits keyboard but appears to forbid already accepted SD service | PORT-017 physical acceptance and current EMOS ext.sdlink service | Current architecture and ADR-0014 acknowledge explicit foreground Legacy SD without implying Dual or general EDU admission. |
| A09-F031 | SETUP-005 opening says browser deferred and implementation not started | ADR-0022 and current keyboard/console contracts | Current integration summary replaces stale priority; original dated choices retain historical meaning. Wider decisions remain open. |
| A09-F032 | Upstream précis calls a 4096-byte ESP-IDF task stack 4096 words | Pinned video.ino argument and Espressif task.h byte-unit contract | Corrected unit; no measured high-water or current-release claim. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F033 | Procedure directory mixes active maintenance with old disconnected-board/no-backup qualification recipes | Nine procedure status/identity headers and current build, reset, SD and fixture guidance | New current applicability index distinguishes each scope; frozen recipes unchanged. New qualification still needs its owning task's refreshed contract. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F034 | Input queue/task summaries still call committed UI/host control uncommitted, and viewer task calls an old build installed | Commits d86739bf/a67aa2d3/c73b458c and dated C02 follow-up | Current summaries and TODO corrected, guides linked; physical takeover/visual gates stay open. NET-001 candidate explicitly historical. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F035 | Example recipes predate SD evidence layout, EMOSlet handover and mode-in-autoexec policy | qualify_keyboard.py still emits LOAD/RUN of the ordinary listener; key-query/screen/receiver hard-code old receipt paths; marker/matrix use relative output | Current example index separates refresh-required fixtures from corrected invocation guidance. Code remains unchanged. PORT-003 owns key-query; REMOTE-002 owns keyboard witnesses/qualifier; DEMO-001 owns hello replay refresh. No automatic authorization to rerun. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F036 | FWBUG-002 still says the first-scene failure blocks all sprite/scroll qualification | Later mainboard/P4 checkpoint results and packed-expansion cumulative count | Corrected bug scope and added current QUAL-004 summary: 77 static pairs; INITIAL diagnostic cause and dynamic parity remain unresolved. No failure erased or fresh acceptance inferred. |

## Capability and deferred-work summaries

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F037 | PORT-006 still actively prohibits implemented browser input; PORT-004 says stop before a completed repair and leaves Rally visual acceptance pending | Current keyboard/video guides, ADR-0022 and September 15 audio-framing acceptance | Rewrote current summaries; retained dated evidence. Synthesis, network resilience and remaining human gates are not closed. MODE/DIAG/storage/matrix summaries now distinguish their broader requirements from working bounded services. |
| A09-F038 | LINK-001 retains active MOS-module research despite Author cancellation | Resident EMOS direction in ADR-0014/SETUP-005 and current EMOS utility contract | Marked the existing research step cancelled and removed the dependency. No new replacement work or architecture introduced. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F039 | Old ADRs can read as blanket unthrottled-video policy or standing flash/demo authorization | Later ADR-0020/0021/0022 and dated REMOTE-002 scope | Added precise current applicability; original engineering decisions retained. Decision directory now has a navigable metadata index, not just an authoring template. No policy/qualification silently changed. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F040 | Policy describes draft as not yet exercised, while current registry retains physically tested EMOS v0.1.19 as draft | artifacts.yaml agon-emos entry and AUDIT-008/HARDWARE | Recorded terminology/status reconciliation for the version-policy owner under A09-05. No automatic promotion or identity edit. Current guides report exact status and bounded evidence separately. Not an operational blocker. |
| A09-F041 | Blanket failed-evidence retention conflicts with Author's explicit ordinary-setup-mistake exception; baseline filename sentence ambiguous | Standing project instructions and versioning baseline grammar | Clarified existing retention rule and single revision suffix; no evidence removed and no new retention policy selected. Examples explicitly do not select current artifacts. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F042 | Scripts directory exposes current clients and old bench/fixture builders without a shared applicability map | 48 root tools, their module descriptions and already-reviewed operating contracts | New host-tool index covers every root script, links current guides and distinguishes retained test helpers. Metadata classification does not qualify those helpers for reuse. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F043 | Predecessor harness calls held r02 current; assembly directory does not expose missing r03 as-built record | Current hardware index/HW-002 and preserved r01/r02 records | Corrected navigation/applicability without editing pins, profiles, models, generated BOM or historical hashes. Complete r03 assembly remains HW-002 work. |
| A09-F044 | Text diagnostic instructions retain old support path and can be confused with normal combined-console capability | Current EMOS edu.text-probe requires ordinary app RAM, Legacy and idle UART1; dedicated P4 sample peer | Current fixture guidance requires identified /extender placement and separate prepared peer/input readiness. No source/fixture identity or hardware changed. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F045 | EMOS tooling lacks current/historical map; provider-era physical procedure and old parallel fixture can look current | Source descriptions, stage_emos_media provider paths, prepare_sdserve application build and current resident/utility guide | Added tool index; marked old qualification applicability and corrected source-lineage pointers. Current MOSlet guide remains authoritative. No retired tool or old fixture requalified. |
| A09-F046 | Retained keyboard exerciser documents root receipt files and /bin deployment paths | EMOS keyboard-api/wire READMEs and existing SD-placement rule | Historical procedures retained; tool index requires refresh before physical reuse. INTEG-009 owns fixture/readiness refresh; source and frozen identities unchanged. |

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F047 | PORT-003 opens with no implementation started, PORT-008 still demands recovery despite later success, audit introductions lag completed work | Accepted audio/key-query slices; E07P restoration and E09 624-interval result; mode-lifetime disposition; AUDIT-008 measured ROM/hardware receipt | Replaced current opening summaries and stale immediate-next instructions. Long dated evidence stays separate; no broad parity claim, new bench plan or deferred fix. |

## Fourth-pass task and current-guide reconciliation

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F048 | Pacing/delta task openings still imply old candidates are current and direct reset study hides the accepted Pi browser button | BENCH-002 later production/test split; BENCH-008 rollback; REMOTE-003 accepted header revision and maintained reset guide | Rewrote present summaries and retired immediate old-candidate instructions. No fresh installation or human-gameplay claim. Direct-P4 reset remains deferred. |
| A09-F049 | Screen-text routine instructions still live in implementation silo and omit important retrieval limits | Actual screen_text.py, P4 shared-state capture and HTTP registration | Promoted one maintained screen-text guide with failure/timeout, ownership and sampling limits. Task README now links it; code unchanged. |
| A09-F050 | Networking decision brief uses obsolete 16-byte free-ROM figure; audio summary omits slowest retained profile | AUDIT-008 measured image headroom; AUDIO-001 six-row CSV | Current integration comparison now uses 6298 free bytes without approving an AT port. Audio range corrected to about 187–199 KiB/s and modeled 1.07–1.13 s. No new performance measurement or calibration. |
| A09-F051 | Historical storage probes still write receipts outside current evidence location | AUDIO-001 source /test/audio001; REMED-003 frozen fixture /extender/fscheck results | Owning tasks require path/identity refresh before new physical use. Exact old-binary comparison/evidence retained; no source or emulator procedure changed. |
| A09-F052 | Early build decisions can obscure current pin guard and make OTA reservation look like update-service readiness | Maintained wrapper, SDK defaults, board JSON, partitions and bounded bring-up result | Current build table and ADR applicability clarify existing behavior. No toolchain upgrade, build, hardware qualification or accepted-policy change. |

## A09-N01 — fidelity and dependency decisions

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F053 | Recorded VDP baseline and dependency graph can be mistaken for newest release or complete deployed compatibility evidence | Reviewed source identities; dependency README scope; console selection; existing build overlay limitation | ADR-0011 and build guide distinguish import policy, historical graph and current selection. Full later-overlay reconciliation remains the existing PORT-003/build-owner boundary (A09-F009), not newly verified here. |
| A09-F054 | ADR-0012 still directs selection of already pinned ESP32Time/CRC and can imply all dependencies are vendored | source-baselines.yaml and library.json identify 2.0.6/1.0.4; console manifest/lock and select_sources.py separately pin managed components | Corrected resolved pins and acquisition scope; package verification is distinct from Git commit identity. No dependency changed or requalified. |
| A09-F055 | ADR-0013 calls browser input the first future source, broadly excludes physical keyboard and leaves routing unresolved | Accepted ADR-0014/0022, current keyboard guide, architecture and console source selection | Corrected to existing USB/browser/agent ownership and PS/2-specific omission. Deferred mouse, audio synthesis and P4 SD are not claimed implemented. Historical proof-of-concept and unscoped Work 1.c instructions replaced with current applicability. |
