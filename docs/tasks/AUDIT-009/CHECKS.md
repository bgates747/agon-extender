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
