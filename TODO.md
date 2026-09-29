# Agon Extender TODO

This is the single authoritative unfinished-work index. Task files own detailed
subtasks, gates and evidence. Completed history remains in task records and the
development log. Ordering below replaces historical competing priority headings;
classification does not grant new execution or waive human acceptance.

## Networking prior-art review — awaiting review

- [ ] **[NET-002 — Agon networking prior art and Extender reuse](docs/tasks/NET-002.md)** — Review PerryZi/Zimodem, get/zget and related Agon tools against our networking capabilities; recommend reusable code/interfaces and bounded adaptations. Source review N02-01–05 complete; recommendations await Author review. Preserve the existing SD service; proposed AT compatibility is a separate decision.

## Transparent text — scope review

- [ ] **[TEXT-001 — Transparent text backgrounds](docs/tasks/TEXT-001.md)** — Prototype implemented; native pixel checks and P4 compile pass. Lenovo bespoke rainbow demo awaits Author visual acceptance; no hardware deployment.

## Do now — PLAN-001

- [ ] **[AUDIT-010 — Implementation integrity and resource-lifecycle audit](docs/tasks/AUDIT-010.md)** — Audit the latest working pre-LCD P4 product with current EMOS v0.1.23 for architectural cohesion, ownership, allocation/lifetime, failure handling and accumulated ad hoc behavior. Complete audit and review before itemized fixes; LCD support is reintroduced afterward as a separately reviewed delta.

- [ ] **[AUDIT-009 — Documentation accuracy and consolidation](docs/tasks/AUDIT-009.md)** — Current-handbook closeout complete through N25; broader historical inventory remains incomplete. [Closeout](docs/tasks/AUDIT-009/CLOSEOUT.md) identifies usable guides and remaining owners. No automatic archive-review or bench tranche; revisit unresolved records when current work depends on them.

- [ ] **[REMOTE-005](docs/tasks/REMOTE-005.md)** — Ad hoc fast-transfer implementation deployed; local and bounded physical checks accepted; broader research/discussion: human-friendly access to Agon SD through P4; compare browser, FTP, SMB and WebDAV. Selected production retains EMOS v0.1.19, while development EMOS v0.1.23 and its finite application-card path have bounded hardware evidence and form AUDIT-010's current pre-LCD baseline. YMODEM comparison complete; external protocol unselected. SD layout cleanup recorded; `/tmp/extender` transaction migration, interactive session handling and R05-10 qualification-procedure refresh remain.

- [ ] **[AUDIT-008 — EMOS ROM headroom and SD-loaded EMOSlets](docs/tasks/AUDIT-008.md)** — Delivered tranche closed out; further extraction and broader qualification parked. Revisit for measured ROM pressure or a concrete utility benefit, not routine splitting for its own sake.

- [ ] **[PLAN-001 — Timing closeout and next-work selection](docs/tasks/PLAN-001.md)**. T01 committed; T02 reconciliation prepared for review in [the disposition table](docs/tasks/PLAN-001/QUEUE-REVIEW.md). T03 source audit and mode-startup investigation delivered; inherited palette defect recorded, with upstream/Extender patches deferred for credits. Aginvadors optimization and further browser-performance experiments are deferred.

## Next-work candidates and remaining implementation

- [ ] **[REMOTE-006 — Independent browser-requested Extender reset](docs/tasks/REMOTE-006.md)** — Add a Reset Extender button beside Reset Agon while preserving two independent actions. Select an external P4 reset executor capable of recovering more than a responsive self-restart; define Legacy/ExCom and in-flight-service outcomes before implementation. Queued behind the active AUDIT-010 review/repair gate unless explicitly reprioritized.

- [ ] **[RESEARCH-006 — Mainboard VDP via Pico 2/Cowbell](docs/tasks/RESEARCH-006.md)** — Initial assessment recorded; investigate header-only serial transport versus digital VGA taps, fidelity and bandwidth. Research only; no implementation or bench work selected.

- [ ] **[TRS-80-003 — Shared P4 services and native-eZ80/MAME bridge](docs/tasks/TRS-80-003.md)** — Feasibility study first: coordinate detached MAME reuse, then native Agon execution with P4 device models, EMOS bridge and eight-bit parallel transport. Cross-project orientation recorded; common Ethernet boundary extracted for detached build evaluation; hybrid feasibility and image leases remain open.

- [ ] **[LCD-001 — Olimex MIPI LCD exploration](docs/tasks/LCD-001.md)** — Preserve the working experimental panel evidence and implementation. After AUDIT-010 reviews and fixes the pre-LCD baseline, redeploy LCD support as a separately reviewed delta and rerun geometry, late-mode, browser/service, performance and gameplay regressions.

- [ ] **[PORT-003](docs/tasks/PORT-003.md)** — Display backend works; wider command consumption and faithful coverage remain incomplete. Primary implementation owner for T03; retain accepted key-query/audio slices and all explicit command deferrals.

- [ ] **[AUDIT-007](docs/tasks/AUDIT-007.md)** — Parked by the Author: first graphics-backend review and mode-startup investigation delivered; exhaustive remainder deferred. Resume only on explicit Author direction; preserve existing finding owners and feature deferrals.

- [ ] **[PORT-008](docs/tasks/PORT-008.md)** — Bulk UART parity qualified; E08/E09 evidence complete; E10 unstarted. Review existing evidence and coordinate with EMOS INTEG-014 before new transport work.

- [ ] **[QUAL-003](docs/tasks/QUAL-003.md)** — Many bounded results complete; correctness gaps and review gates remain; browser experiments parked. Separate retained correctness/exception work from dormant performance branches; no automatic new run.

- [ ] **[PORT-006](docs/tasks/PORT-006.md)** — Network service works; resilience/update-service scope incomplete. Browser keyboard was reintroduced. Keep remaining network obligations; browser input belongs to REMOTE-001, not a retired-service claim.

- [ ] **[QUAL-001](docs/tasks/QUAL-001.md)** — Matrix scaffold exists; four-mode reconciliation and validator integrity gates remain. Retain infrastructure work; partial records do not certify complete compatibility.

- [ ] **[REMED-001](docs/tasks/REMED-001.md)** — Some architecture promotions complete; broader conformance/replacement work incomplete. Reconcile only applicable remaining obligations; old global freeze wording is not evidence that accepted ExCom ceased to work.

- [ ] **[REMED-002](docs/tasks/REMED-002.md)** — Findings have mixed fixes, deferrals and outstanding validation. Retain finding IDs and owning-task gates; no blanket closure from successful gameplay.

- [ ] **[SETUP-005](docs/tasks/SETUP-005.md)** — Immediate ExCom/input decisions accepted; broader mode-integration questions remain. Resolve decisions only when selected scope depends on them; do not reopen settled keyboard choices.

- [ ] **[HW-002](docs/tasks/HW-002.md)** — Simplified wiring accepted within scope; USB schematic/as-built and endpoint review incomplete. Keep documentation obligations; remove the obsolete tomorrow/date framing from the queue.


## Review and closeout queue — no automatic new experiments

- [ ] **[BENCH-002](docs/tasks/BENCH-002.md)** — 30-Hz test deployment exists; later feedback and production/test split supersede initial awaiting-review wording. Review final disposition; production Nurples is single-vblank and the slower build is test-only.

- [ ] **[BENCH-004](docs/tasks/BENCH-004.md)** — Mailbox implementation/local tests complete; task still lacks an explicit Mac handshake receipt. Locate or obtain a peer round-trip only if needed; empty mailbox checks do not establish that gate.

- [ ] **[RESEARCH-001](docs/tasks/RESEARCH-001.md)** — Five source reviews complete; synthesis available. Accept/archive research separately from any proposed optimization; no new search or implementation.

- [ ] **[RESEARCH-002](docs/tasks/RESEARCH-002.md)** — Published-throughput research complete. Accept/archive findings; published link/codec rates are not measured application throughput.

- [ ] **[RESEARCH-003](docs/tasks/RESEARCH-003.md)** — Twelve standalone runs complete; 60-fps delivery unmet. Historical candidate-left-installed note is obsolete as a current bench description. Review bounded result; consult latest restoration authority rather than assume the old candidate is installed.

- [ ] **[BENCH-001](docs/tasks/BENCH-001.md)** — Bounded telemetry/driving work complete and frozen; human review/remaining game continuation separate. Close accepted scope after review; retain AgonArcade RALLY-22 ownership of further driving.

- [ ] **[REMOTE-002](docs/tasks/REMOTE-002.md)** — Host input implemented, tested and used; current task summary links the implementation commit and operating guide. Review remaining physical/human gates; no duplicate implementation required.

- [ ] **[REMED-003](docs/tasks/REMED-003.md)** — Identical filesystem probe passes hardware/raw image and fails directory backend; report prepared. Author reviews report; submitting to upstream requires explicit authorization.

- [ ] **[NET-001](docs/tasks/NET-001.md)** — Viewer takeover implemented; six connections/five handovers passed. Retain pending human browser acceptance; later use does not automatically establish every gate.

- [ ] **[QUAL-004](docs/tasks/QUAL-004.md)** — 77 static scene pairs matched, including [static teletext](docs/tasks/QUAL-004/teletext/RESULTS.md). [Sprite/scroll follow-up](docs/tasks/QUAL-004/sprite-scroll/RESULTS.md): stock INITIAL visual/exit control passed; mainboard OVERLAP/EDGES/HIDDEN passed repeat capture, HIDDEN also full oracle. Extender checks passed; three checkpoints match mainboard exactly, INITIAL has visual control only. [Packed expansion BM02](docs/tasks/QUAL-004/packed-expansion/RESULTS.md) passed; BM03 parked. Capture-interference investigation QUAL-004-CI01 and four Copper controls deferred; no claim of complete dynamic-sprite parity.



## Parked, blocked and unscheduled work


- [ ] **[BENCH-008](docs/tasks/BENCH-008.md)** — Correct output but worse frame rate with replacement deltas; initial experiment complete. B08-06 cost investigation deferred until Author resumes; pre-experiment P4 firmware restored after the regression.

- [ ] **[RESEARCH-005](docs/tasks/RESEARCH-005.md)** — Deferred VGA pillarboxing, P4 VGA output and aspect-preserving output research; FabGL investigation and existing P4 VGA driver lead retained. No implementation or bench work scheduled.

- [ ] **[REMOTE-004](docs/tasks/REMOTE-004.md)** — Low-priority copy/paste feasibility: Extender first, possible stock MOS/VDP subset later. Investigate existing input/readback reuse and application-consumption guarantees; proposal before implementation.

- [ ] **[BENCH-007](docs/tasks/BENCH-007.md)** — Package/results committed; F01 mainboard panic, F02 Rally fixture discrepancy and B07-R01 procedure refresh remain. Retain these unscheduled follow-ups here; measurement implementation is complete, not another half-built package. Refresh the retained runner/startup procedure before reuse under current fixture rules.

- [ ] **[AUDIO-001](docs/tasks/AUDIO-001.md)** — SD feasibility measured; integrated parallel/audio stages not executed. Keep behind current porting priority; AF02 needs its own bounded contract.

- [ ] **[P4PC-001](docs/tasks/P4PC-001.md)** — Board backordered; plan only, delivered revision/HDMI qualification absent. Resume with hardware availability and authorization; preserve current DevKit bench.

- [ ] **[TRS-80-001](docs/tasks/TRS-80-001.md)** — Ecosystem survey/reference acquisition complete; architecture unselected. Retain future design work; no new implementation implied.

- [ ] **[HW-003](docs/tasks/HW-003.md)** — Alternate board desk assessment complete; collaborator specimen unresolved. Await exact hardware/variant and separate adaptation scope.

- [ ] **[PORT-005](docs/tasks/PORT-005.md)** — Native USB input works; broader keyboard parity/settings refinements deferred. Preserve working input and fix blocking regressions only; browser-specific follow-up remains separate.

- [ ] **[REMOTE-003](docs/tasks/REMOTE-003.md)** — Pi-backed browser reset accepted. Direct P4 reset wiring remains deferred.

- [ ] **[REMOTE-001](docs/tasks/REMOTE-001.md)** — Browser input/UI deployed; game/fullscreen follow-ups explicitly deferred. Preserve committed input/UI work; do not expand optimization or infer physical takeover acceptance.

- [ ] **[SETUP-006](docs/tasks/SETUP-006.md)** — Old full-circuit wiring target remains on hold/incomplete. Retain predecessor evidence; reconcile applicability when hardware design resumes.

- [ ] **[HW-001](docs/tasks/HW-001.md)** — Old full r02 circuit incomplete and unqualified. Do not treat simplified harness success as full r02 qualification; re-scope before resuming.

- [ ] **[PORT-004](docs/tasks/PORT-004.md)** — Audio command framing slice passed; actual synthesis/output deferred. Retain Wolf3D and wider audio obligations; framing success does not implement sound.

- [ ] **[PORT-007](docs/tasks/PORT-007.md)** — P4-local SD HTTP file/directory management r57 passes bounded hardware checks; Author acceptance/promotion pending. Broader storage remains required v1 work. Keep distinct from the accepted mainboard SD service; EMOS read access remains required.

- [ ] **[QUAL-002](docs/tasks/QUAL-002.md)** — Full-circuit electrical absence/power/reset qualification on hold. Requires applicable hardware design and separate physical contract.

- [ ] **[UPSTREAM-001](docs/tasks/UPSTREAM-001.md)** — Lifecycle correction A/B research not started. No upstream fixes imported into strict-compatible first-pass port by default.

- [ ] **[MODE-001](docs/tasks/MODE-001.md)** — Broader state-preserving transitions not implemented; bounded ExCom switching already exists. Retain future transition contracts without describing current ExCom as absent.

- [ ] **[MODE-002](docs/tasks/MODE-002.md)** — Post-beta automatic retry-protection evaluation not started. Require evidence and explicit scope before adding retry machinery.

- [ ] **[DIAG-001](docs/tasks/DIAG-001.md)** — General recoverable diagnostics/crash-record product work not started. Retain release requirement and evidence/privacy decisions; task-local capture is not the full feature.

- [ ] **[LINK-001](docs/tasks/LINK-001.md)** — Direct onboard-VDP/EDP link is optional deferred research. Not a prerequisite for existing keyboard/ExCom path.

- [ ] **[PORT-016](docs/tasks/PORT-016.md)** — MicroPython long-term feature; v1 placement undecided. No timing or input dependency; remain deferred.

- [ ] **[BENCH-003](docs/tasks/BENCH-003.md)** — Author stopped after first Legacy acquisition timeout; no FPS conclusion. Do not restart; BENCH-007 does not retroactively pass this different experiment.

- [ ] **[BENCH-005](docs/tasks/BENCH-005.md)** — Initial latency and later packing/mode investigations retained; further output experiments now parked. Retain unresolved Legacy acknowledgement/readout limits; no new browser-performance work.

- [ ] **[BENCH-006](docs/tasks/BENCH-006.md)** — ExCom text readback implemented; Legacy S04 explicitly deferred. Keep only Legacy follow-up as remaining scope; preserve functioning ExCom endpoint.

## Governing limits

EMOS owns ordinary VDU routing and Extender activation/transports. Preserve
accepted Legacy/ExCom, input and mainboard SD capabilities. Official references
stay read-only. No Golem, upstream publication, new hardware qualification or
experimental push follows from queue cleanup.

[ADR-0020](docs/decisions/ADR-0020-web-output-30fps.md) remains unchanged. Its
scope versus later higher-rate client/experiment records must be reconciled
before future output qualification; do not assume that a current firmware cap
has been verified. See PLAN-001-N04 in the disposition table. Old experiment
headings no longer compete with the approved current sequence.
