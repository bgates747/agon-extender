# AUDIT-009 — Findings

Findings distinguish erroneous current guidance from valid historical evidence.
The task checklist owns execution; this register tracks claims and dispositions.

| ID | Class and affected claim | Evidence / correction | State |
|---|---|---|---|
| A09-F001 | Incorrect availability: README says SD source not on public main and browser input deferred | EMOS published 7c15439/895715e and Extender 77c25ebc/b1d799e7; REMOTE-001 deployment history | Correct current landing page |
| A09-F002 | Stale orientation: HANDOFF still calls screen capture uncommitted and browser input unimplemented | Subsequent committed/deployed REMOTE-001, REMOTE-003, AUDIT-008 records | Replace handoff, retain Git history |
| A09-F003 | Operational circularity: remote agent told to type its own unavailable KEYINPUT admission | Author correction; keyboard.py Client.open requires ready/neutral; EMOS owns admission | State already-enabled keyboard as prerequisite; startup/operator recovery if absent |
| A09-F004 | Conflicting keyboard guidance: remote-keyboard.md planned-only browser section; web README manual lock selectors | REMOTE-001 later UI/deployment records; current app.js/keyboard_session.js, browser_keyboard.inc | Consolidate deployed behavior and explicit remaining platform/human gates |
| A09-F005 | Obsolete reset prohibition in mainboard-sd.md | bench-reset.md and REMOTE-003 document corrected Pi actuator/button; SD protocol itself still has no reset | Link independent authorized reset path; retain ROM-recovery distinction |
| A09-F006 | Wrong browser asset claims: no keyboard endpoints, RGB888 only, pre-input page | Current wired_network_service.cpp registers /keyboard/browser; frame_protocol.js handles additional encodings | Replace source README duplication with current role/links |
| A09-F007 | Suspect SD protocol admission wording excludes MOSlet RAM | EMOS v0.1.18 gateway changes and v0.1.19 physical /emos checks | Compare against source; correct only established ranges/ownership |
| A09-F008 | Normative 30fps text versus later 60Hz browser request behavior | architecture.md/ADR-0020 versus BENCH-005, QUAL-003 and app.js | Investigate documentary provenance; do not invent a new pacing decision |

Resolution evidence and additional findings will be appended per bounded batch.

## Additional findings and dispositions

| ID | Class and affected claim | Evidence / correction | State / owner |
|---|---|---|---|
| A09-F009 | Operationally consequential build gap: base p4-console instructions look like a rebuild of the installed combination | `prepare_console.py` invokes base source; BENCH-005 and REMOTE-001/003 record snapshot parents and codec/browser overlays, some in ignored artifacts | Documented in building.md and web README. Source/build consolidation remains unresolved; Extender build/PORT-003 owner, separate implementation scope required. No equivalent fresh-clone build claimed. |
| A09-F010 | Architecture still says browser input deferred and selects a separate browser ingress | Accepted ADR-0022 common `KEYINPUT extender` arbitration supersedes the old paragraph | Corrected architecture to already accepted decision, without changing behavior or qualification. |
| A09-F011 | Publication review's old findings read as current | September 13 findings versus current commands/README/EMOS commits | Added dated disposition table; preserved old security checks and unresolved test failures. |
| A09-F012 | Broken historical navigation | Local Markdown scan: P01h RLE2 ADR path has one excess parent; three predecessor hardware evidence references lack targets | Corrected P01h link only. Hardware references require archive-owner provenance, not guessed replacements. |

A09-F001–F007 are corrected in the current guides/entry points. For F004,
the actual stale web claims were retirement/no-keyboard/RGB888-only; manual
lock controls are already absent from the maintained page. Existing pending
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
| A09-F013 | Cancelled `.emo` design still presented as the EMOS v1 contract | AUDIT-008 and current EMOS utility contract retire discovery/registry/load/swap; retained SD range includes MOSlets | Added explicit applicability boundary to old contract; retained resident sections corrected. EMOS owns any further ABI-document promotion. |
| A09-F014 | EMOS listener README leads with ordinary application and old `/mos` location | Later v0.1.19 physical migration and current service build variables | Rewritten around current EMOSlet, two memory layouts, authoritative external guide, normal/fast and chronological evidence. |
| A09-F015 | Ambiguous stock reference versus working MOS fork in sibling ownership guide | Extender OWNERSHIP and canonical instructions distinguish canonical stock checkout from `mystuff/agon-mos` | Clarified both roles without changing ownership or editing either checkout. |
| A09-F016 | EMOS migration handoff has fourteen broken former-workspace links | Local scan and repository-migration provenance | Historical-context banner and current redirects added; former links retained as history. Not a current operational blocker. |
| A09-F017 | REMOTE-005 TODO still names v0.1.18 as current listener combination | AUDIT-008/HARDWARE later v0.1.19 and `/emos` deployment | Updated queue summary; broader REMOTE-005 work remains open. |
