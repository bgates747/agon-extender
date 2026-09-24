# AUDIT-009 — Documentation authority map

Use existing role-named contracts; add one shared operation entry point and
promote the README's build detail. This changes navigation, not feature ownership
or accepted architecture. Task evidence stays at its recorded location.

| Subject / audience | Maintained authority | Disposition |
|---|---|---|
| One current handbook, distinct from evidence | docs/README.md | Index only current role-named guides; historical instructions remain outside routine reading |
| Discover capabilities, human or agent | root README.md | Replace stale summary; link procedures and bounded evidence |
| Operate an existing installation from another project | docs/using-extender.md | New short entry point; prerequisites/reading order, not another protocol catalog |
| Choose a reusable procedure versus historical qualification | docs/procedures/README.md | Current applicability index; preserve exact older procedure identities/evidence |
| Build firmware | docs/building.md | Promote existing README build material, retain source ownership and deployment distinction |
| SD service and client | docs/mainboard-sd.md | Correct prerequisites; own normal/fast/session/recovery examples |
| SD wire fields and invariants | docs/protocols/mainboard-sd.md | Keep exact packet contract; reconcile foreground MOSlet admission |
| Keyboard operation and arbitration | docs/remote-keyboard.md | Own host/browser behavior; replace planned-only wording with evidenced current status |
| Video transport and presentation | docs/protocols/browser-video.md | Keep wire/pacing authority; expose unresolved implementation-policy divergence |
| Screen-text operation | docs/using-extender.md, linking BENCH-006 evidence and script | Promote concise usage; no duplicate pixel/recognition specification |
| Reset versus ROM recovery | docs/bench-reset.md and docs/mos-recovery.md | Keep separate; remove obsolete prohibition from SD guide, not historic evidence |
| SD paths | docs/sd-layout.md | Keep current production/evidence/temporary placement and transaction exception |
| Firmware ABI and /emos dispatch | agon-emos docs/emos-utilities.md | EMOS owns ABI; Extender guides link rather than reimplement description |
| Current assembled architecture | docs/architecture.md and accepted ADRs | Preserve accepted decisions; label conflicts pending disposition |
| Open work, known defects, acceptance | TODO.md; task files; docs/firmware-bugs.md; qualification records | Keep separate roles; no new queue in this map |
| Browser source directory entry | vdp/video/extender/web/README.md | Reduce duplicate protocol/UI prose; link maintained authorities and local source/test entry points |
| Returning developer orientation | HANDOFF.md | Replace time-capsule status with concise current orientation and evidence links |
| Machine-specific installed state | ignored HARDWARE.local.md | Keep private; newest applicable dated receipts, never infer from checkout HEAD |
| External/canonical repositories | their own authoritative instructions | Consult read-only; no unrelated edits |

This map was selected within the approved consolidation scope. No ownership or
architecture change requiring a new decision is proposed.

Author clarification during execution: the end state is one current set, not
a collection of dated amendments. Current authorities are rewritten to remove
superseded instructions. Historical evidence is retained separately or through
Git; merely adding a warning banner is insufficient for an operating manual.
