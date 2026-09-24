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
