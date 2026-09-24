# Queue reconciliation — PLAN-001-T02

## Executive summary

Review draft, 2026-09-20. The incoming queue had **44 open entries plus one
already-completed entry** (45 total, including PLAN-001). It was not 44 unfinished
implementations. This review classifies every entry using its task record and
later linked evidence. Classification is not new human acceptance.

| Disposition | Count | Meaning |
|---|---:|---|
| Active | 1 | This closeout/planning task. |
| Implementation | 10 | Remaining port, integration or documentation work; not all immediately authorized. |
| Review | 11 | Completed bounded work or audit findings needing disposition, not automatic closure. |
| Parked | 22 | Deferred, blocked, unscheduled or residual follow-up only. |
| Closed | 1 | Already completed research removed from the unfinished queue. |

## Proposed sequence

**PLAN-001-Q01** [x] Account for every incoming task and retain evidence links.

**PLAN-001-Q02** [x] Replace contradictory current-priority headings in TODO
with the approved PLAN-001 sequence; retain separate review and parked sections.

**PLAN-001-Q03** [ ] Author reviews these dispositions. All existing explicit
human gates stay open unless already recorded as accepted. No block approval
of this table is inferred to publish reports or authorize hardware work.

**PLAN-001-Q04** [ ] Following review, T03 proposes one concrete PORT-003
fidelity/command-coverage slice, using AUDIT-007 and PORT-008 obligations as
inputs where relevant. This is a candidate direction, not an implementation
contract or authorization to begin the exhaustive audit.

Aginvadors optimization remains deferred by D01. Browser-performance and codec
experiments remain parked. Hardware availability does not automatically start
P4PC-001 or lift existing circuit holds.

## Per-task disposition

| Task / evidence | Category | Current finding | Proposed disposition / remaining work |
|---|---|---|---|
| [PLAN-001](../PLAN-001.md) | Active | Timing closeout committed; queue review prepared. | Review this table, then T03 selects one bounded porting tranche. |
| [PORT-003](../PORT-003.md) | Implementation | Display backend works; wider command consumption and faithful coverage remain incomplete. | Primary implementation owner for T03; retain accepted key-query/audio slices and all explicit command deferrals. |
| [AUDIT-007](../AUDIT-007.md) | Implementation | Required exhaustive FabGL completeness audit not started. | Use as a candidate source of bounded fidelity work; do not make a whole audit an automatic prerequisite. |
| [PORT-008](../PORT-008.md) | Implementation | Bulk UART parity qualified; E08/E09 evidence complete; E10 unstarted. | Review existing evidence and coordinate with EMOS INTEG-014 before new transport work. |
| [QUAL-003](../QUAL-003.md) | Implementation | Many bounded results complete; correctness gaps and review gates remain; browser experiments parked. | Separate retained correctness/exception work from dormant performance branches; no automatic new run. |
| [PORT-006](../PORT-006.md) | Implementation | Network service works; resilience/update-service scope incomplete. Browser keyboard was reintroduced. | Keep remaining network obligations; browser input belongs to REMOTE-001, not a retired-service claim. |
| [QUAL-001](../QUAL-001.md) | Implementation | Matrix scaffold exists; four-mode reconciliation and validator integrity gates remain. | Retain infrastructure work; partial records do not certify complete compatibility. |
| [REMED-001](../REMED-001.md) | Implementation | Some architecture promotions complete; broader conformance/replacement work incomplete. | Reconcile only applicable remaining obligations; old global freeze wording is not evidence that accepted ExCom ceased to work. |
| [REMED-002](../REMED-002.md) | Implementation | Findings have mixed fixes, deferrals and outstanding validation. | Retain finding IDs and owning-task gates; no blanket closure from successful gameplay. |
| [SETUP-005](../SETUP-005.md) | Implementation | Immediate ExCom/input decisions accepted; broader mode-integration questions remain. | Resolve decisions only when selected scope depends on them; do not reopen settled keyboard choices. |
| [HW-002](../HW-002.md) | Implementation | Simplified wiring accepted within scope; USB schematic/as-built and endpoint review incomplete. | Keep documentation obligations; remove the obsolete tomorrow/date framing from the queue. |
| [BENCH-002](../BENCH-002.md) | Review | 30-Hz test deployment exists; later feedback and production/test split supersede initial awaiting-review wording. | Review final disposition; production Nurples is single-vblank and the slower build is test-only. |
| [BENCH-004](../BENCH-004.md) | Review | Mailbox implementation/local tests complete; task still lacks an explicit Mac handshake receipt. | Locate or obtain a peer round-trip only if needed; empty mailbox checks do not establish that gate. |
| [RESEARCH-001](../RESEARCH-001.md) | Review | Five source reviews complete; synthesis available. | Accept/archive research separately from any proposed optimization; no new search or implementation. |
| [RESEARCH-002](../RESEARCH-002.md) | Review | Published-throughput research complete. | Accept/archive findings; published link/codec rates are not measured application throughput. |
| [RESEARCH-003](../RESEARCH-003.md) | Review | Twelve standalone runs complete; 60-fps delivery unmet. Historical candidate-left-installed note is obsolete as a current bench description. | Review bounded result; consult latest restoration authority rather than assume the old candidate is installed. |
| [BENCH-001](../BENCH-001.md) | Review | Bounded telemetry/driving work complete and frozen; human review/remaining game continuation separate. | Close accepted scope after review; retain AgonArcade RALLY-22 ownership of further driving. |
| [REMOTE-002](../REMOTE-002.md) | Review | Host input implemented, tested and used; historical task text still says active goal/uncommitted. | Review remaining physical/human gates and reconcile commit references; do not claim uncommitted implementation from old prose. |
| [REMED-003](../REMED-003.md) | Review | Identical filesystem probe passes hardware/raw image and fails directory backend; report prepared. | Author reviews report; submitting to upstream requires explicit authorization. |
| [NET-001](../NET-001.md) | Review | Viewer takeover implemented; six connections/five handovers passed. | Retain pending human browser acceptance; later use does not automatically establish every gate. |
| [QUAL-004](../QUAL-004.md) | Review | 71 static scene pairs matched after page, low-depth and static teletext controls; exceptions remain open. | Review exceptions and four deferred Copper controls; no claim of complete dynamic-sprite parity. |
| [AUDIT-005](../AUDIT-005.md) | Review | Stock reuse findings retained; later UART work supersedes old current-slowdown narrative. | Propose audit closure with remaining obligations mapped to PORT-008/PORT-003; do not rerun old investigations. |
| [BENCH-007](../BENCH-007.md) | Parked | Package/results committed; only F01 mainboard panic and F02 Rally fixture discrepancy remain. | Retain these two unscheduled follow-ups here; measurement implementation is complete, not another half-built package. |
| [AUDIO-001](../AUDIO-001.md) | Parked | SD feasibility measured; integrated parallel/audio stages not executed. | Keep behind current porting priority; AF02 needs its own bounded contract. |
| [P4PC-001](../P4PC-001.md) | Parked | Board backordered; plan only, delivered revision/HDMI qualification absent. | Resume with hardware availability and authorization; preserve current DevKit bench. |
| [TRS-80-001](../TRS-80-001.md) | Parked | Ecosystem survey/reference acquisition complete; architecture unselected. | Retain future design work; no new implementation implied. |
| [HW-003](../HW-003.md) | Parked | Alternate board desk assessment complete; collaborator specimen unresolved. | Await exact hardware/variant and separate adaptation scope. |
| [PORT-005](../PORT-005.md) | Parked | Native USB input works; broader keyboard parity/settings refinements deferred. | Preserve working input and fix blocking regressions only; browser-specific follow-up remains separate. |
| [REMOTE-003](../REMOTE-003.md) | Parked | Remote-reset feasibility written; Author deferred wiring/implementation. | Resume only on renewed direction. |
| [REMOTE-001](../REMOTE-001.md) | Parked | Browser input/UI deployed; game/fullscreen follow-ups explicitly deferred. | Preserve current uncommitted UI work; do not expand optimization or infer physical takeover acceptance. |
| [SETUP-006](../SETUP-006.md) | Parked | Old full-circuit wiring target remains on hold/incomplete. | Retain predecessor evidence; reconcile applicability when hardware design resumes. |
| [HW-001](../HW-001.md) | Parked | Old full r02 circuit incomplete and unqualified. | Do not treat simplified harness success as full r02 qualification; re-scope before resuming. |
| [PORT-004](../PORT-004.md) | Parked | Audio command framing slice passed; actual synthesis/output deferred. | Retain Wolf3D and wider audio obligations; framing success does not implement sound. |
| [PORT-007](../PORT-007.md) | Parked | P4-local SD service not started; required v1 work scheduled after beta. | Keep distinct from the accepted mainboard SD service; EMOS read access remains required. |
| [QUAL-002](../QUAL-002.md) | Parked | Full-circuit electrical absence/power/reset qualification on hold. | Requires applicable hardware design and separate physical contract. |
| [UPSTREAM-001](../UPSTREAM-001.md) | Parked | Lifecycle correction A/B research not started. | No upstream fixes imported into strict-compatible first-pass port by default. |
| [MODE-001](../MODE-001.md) | Parked | Broader state-preserving transitions not implemented; bounded ExCom switching already exists. | Retain future transition contracts without describing current ExCom as absent. |
| [MODE-002](../MODE-002.md) | Parked | Post-beta automatic retry-protection evaluation not started. | Require evidence and explicit scope before adding retry machinery. |
| [DIAG-001](../DIAG-001.md) | Parked | General recoverable diagnostics/crash-record product work not started. | Retain release requirement and evidence/privacy decisions; task-local capture is not the full feature. |
| [LINK-001](../LINK-001.md) | Parked | Direct onboard-VDP/EDP link is optional deferred research. | Not a prerequisite for existing keyboard/ExCom path. |
| [PORT-016](../PORT-016.md) | Parked | MicroPython long-term feature; v1 placement undecided. | No timing or input dependency; remain deferred. |
| [BENCH-003](../BENCH-003.md) | Parked | Author stopped after first Legacy acquisition timeout; no FPS conclusion. | Do not restart; BENCH-007 does not retroactively pass this different experiment. |
| [BENCH-005](../BENCH-005.md) | Parked | Initial latency and later packing/mode investigations retained; further output experiments now parked. | Retain unresolved Legacy acknowledgement/readout limits; no new browser-performance work. |
| [BENCH-006](../BENCH-006.md) | Parked | ExCom text readback implemented; Legacy S04 explicitly deferred. | Keep only Legacy follow-up as remaining scope; preserve functioning ExCom endpoint. |
| [RESEARCH-004](../RESEARCH-004.md) | Closed | Research already checked complete; purchasing choice proceeded to P4PC-001. | Remove completed research entry from TODO; retain assessment and separate hardware integration task. |

## Reconciliation notes and boundaries

The pre-review queue is preserved in Git at `c7bb4ee3:TODO.md`; full historical
measurements remain in their task silos. This table is a review artifact, not a
second authoritative queue. TODO owns current ordering; task files own subtasks.

**PLAN-001-N01:** PORT-008's leading incomplete-recovery paragraph predates its
later E07P restoration and E08/E09 findings. It must not be read as current bench
state. BENCH-007 restoration is later still; no hardware was queried in this review.

**PLAN-001-N02:** BENCH-002's initial two-vblank production plan was superseded
by its accepted production/test split. Production Nurples remains single-vblank.

**PLAN-001-N03:** PORT-006's retired-browser-input statement predates REMOTE-001's
accepted reintroduction and deployment. Network resilience remains unfinished.

**PLAN-001-N04:** The old 30-Hz web-output ADR and later 60-Hz experiment/client
records need a specific applicability reconciliation before any future streaming
qualification. This review changes neither the ADR nor current firmware, and
claims no enforced output cap. The issue stays with QUAL-003; it is not a reason
to restart browser optimization now.

**PLAN-001-N05:** BENCH-007-F01/F02 remain explicit unscheduled findings in their
existing owner. No new task is created merely to move them off a completed package.

**PLAN-001-N06:** Current dirty browser/UI files remain untouched. No firmware,
code, registry, hardware, source ownership, upstream report or push changed.
