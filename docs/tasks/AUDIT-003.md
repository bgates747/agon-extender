# AUDIT-003 — Review open tasks and related implementation integrity

## State

- Status: Complete — findings await Author disposition
- Started: 2026-09-01 11:02 EDT
- Finished: 2026-09-01 12:19 EDT
- Provenance extension completed: 2026-09-01 12:43 EDT

## Intent

Perform a bounded adversarial review of every open task in `TODO.md` and the
implementation, validators, procedures, evidence, version records, and
architecture directly related to those tasks. Identify defects that ordinary
success-path tests or task-local reviews could miss, while distinguishing new
findings from already recorded blockers and deliberately unfinished work.

This audit did not authorize implementation, task expansion, architecture
changes, hardware or bench operations, evidence promotion, deployment, or
qualification. It preserved the Author's pre-existing dirty worktree.

## Scope

The review covered all 18 tasks open on 2026-09-01:

1. PORT-003, QUAL-001, and REMED-001;
2. SETUP-005, SETUP-006, and HW-001;
3. PORT-004 through PORT-008;
4. QUAL-002 and UPSTREAM-001;
5. MODE-001, MODE-002, and DIAG-001; and
6. REMOTE-001 and LINK-001.

For implemented surfaces, the review followed the task's code and evidence
boundary into the P4 display/frame service, retained VDU parser and adapters,
wired-network/browser service, forward-parallel transport, qualification
model, version controls, hardware records, and task-local validation tools.
For tasks not yet implemented, the review tested their authority, ownership,
dependency, safety, and acceptance boundaries rather than treating absent code
as a defect.

## Required output

The durable review is
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).
That record owns stable finding identities, evidence, severity, affected
artifacts, proposed disposition owners, and the boundary between definite
defects, design blockers, prospective risks, and previously recorded gaps.

The audit record is evidence and a correction map. It is not a new
architecture authority or an independent actionable checklist. Every proposed
disposition remains deferred until the Author accepts, rejects, reassigns, or
splits it into its named task authority.

## Code-defect provenance extension

At the Author's request, the completed audit was extended with a source-history
and upstream comparison for every proved implementation or validation-tool
defect: F001--F007, F011--F014, and the existing PORT-008 pre-activation
corrective action. The extension also classifies six already recorded
PORT-008/EMOS/P4 defects from the surrounding task and development evidence;
the first pass did not assign them duplicate F-numbers.

The review compared exact official `agon-vdp` v2.16.0, `vdp-gl`
`all-the-plots`, official MOS v3.0.2, and ESP-IDF v5.5.5 source with project
history, the clean legacy predecessor, and the Author's current uncommitted
EMOS/EDP corrective work. Official VDU documentation was consulted first for
the continuous-stream, audio, updater, and Copper contracts. All external
checkouts were read-only.

The provenance result is:

1. F001 and F002 already exist in pinned upstream `vdp-gl`, but EDP
   independently reimplemented and amplified them in permanent P4 display
   surfaces. An upstream correction would not repair the local code.
2. F003 is an ESP-IDF WebSocket short-write defect exposed through documented
   API use by permanent EDP network code.
3. F004, F005, F012, F013, and pre-activation READY were created by local EDP
   porting or integration. F012 also exposes an upstream ESP-IDF stop-API
   documentation inconsistency, but the lost live handle and callback lifetime
   remain EDP ownership errors.
4. F006, F007, F011, and F014 are local validation or evidence-tool defects;
   none is a defect in `jsonschema`, PlatformIO, UBSan, or the capture runtime.
5. The already recorded EMOS UART divisor problem is a latent official-MOS
   portability defect exposed by AgonDev and now has a committed permanent EMOS
   correction. The EMOS length overlap and sender cadence, P4 direction
   omission, and P4 pre-activation behavior were prototype-integration defects.
   The ZDI refusal-path bug was local, diagnostic-only, and corrected before
   its first commit.
6. No audited defect originates in the EMOS mode coordinator or ordinary
   Legacy routing. The exact PORT-008 transport adapters remain prototype-only;
   their width, timing, fail-safe ownership, and activation invariants are
   nevertheless durable requirements.

The audit record contains the exact classifications, introducing commits,
upstream evidence, maintained-surface boundaries, and the strengthened F012
use-after-free consequence. This extension changes no task disposition and
authorizes no source correction or physical operation.

## Validation performed

1. Ran 96 repository Python unit tests across dependency, qualification,
   hardware, and PORT-003 Phase A--F suites; all passed.
2. Ran the Phase B host fixtures, Phase C host frame fixtures, Phase D host
   presentation fixtures, PORT-006 network host tests, and browser tests; all
   passed within their declared boundaries.
3. Regenerated or validated dependency, qualification, hardware-object,
   electrical-model, BOM, and Markdown-link authorities where safe.
4. Confirmed that version-record validation fails on the frozen r02 schematic
   hash and that the r02 schematic-view validator rejects the stale SVG.
5. Used bounded adversarial probes to demonstrate qualification-reference,
   UBSan-exit-status, and invalid-clock-report false-green behavior without
   changing tracked data.
6. Performed no physical build, deployment, reset, power, network-bench, or
   wiring operation.
7. Confirmed `git diff --check` passes and final repository status preserves
   the pre-existing worktree changes.
8. For the provenance extension, resolved every cited introduction commit in
   its owning repository, reconfirmed the pinned VDP/MOS/ESP-IDF source
   identities, and compared the relevant retained source with its official or
   predecessor counterpart.
9. Re-ran the repository's local Markdown-link resolver on the four amended
   durable documents and performed a targeted trailing-whitespace scan; both
   passed. Product tests were not rerun because the extension changed only
   audit documentation.

## Completion record

The review completed its declared coverage and recorded every finding with a
proposed existing-task owner or an explicit prospective-risk disposition.
The provenance extension subsequently classified each code/tool defect without
altering that ownership boundary. Author disposition and promotion into those
task authorities remain separate work. AUDIT-003 is therefore complete and is
not added to `TODO.md`.
