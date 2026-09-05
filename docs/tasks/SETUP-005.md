# SETUP-005 — Resolve EDU operating modes and system integration

## State

- Status: In progress — mode vocabulary and D001–D002 accepted; D003–D008 remain open
- Started: 2026-08-21 00:49 EDT
- Finished: --

## Intent

Resolve the remaining architectural decisions governing EDU operating modes,
transparent legacy compatibility, MOS integration, response ownership, and
optional use of the onboard VDP as a service behind Extender. This task is the
authoritative open-decision tracker for
[ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md).

Do not let these system-integration decisions block SETUP-004's source and
driver disposition survey. SETUP-004 determines what code and behavior must be
retained, replaced, stubbed, omitted, or deferred; this task determines how the
retained behavior is routed between processors and MOS.

## Accepted operating-mode vocabulary

The Author accepted the following formal names and stable identities on
2026-08-23:

- **Legacy mode** — `mode:extender:legacy`; Extender is inactive and behaves as
  if absent.
- **Exclusive Compatible mode** — `mode:extender:exclusive-compatible`; the EDP
  is exclusive and uses the stock VDP UART transport contract.
- **Exclusive Extended mode** — `mode:extender:exclusive-extended`; the EDP has
  the same exclusive compatibility authority and uses the enhanced
  parallel-forward/UART-return transport.
- **Dual mode** — `mode:extender:dual`; the onboard VDP owns ordinary VDU and
  canonical stock state while EDU addresses the active EDP separately.

“Compatible” and “Extended” are permitted short forms in unambiguous
operating-mode context. “Exclusive” is mandatory in the two official names.
Naming is resolved; lifecycle, routing, reverse capabilities, carve-outs, and
the remaining questions below stay open.

## Accepted MOS terminology

**Extender MOS (EMOS)** is the project-owned complete backward-compatible
replacement build of official stock MOS. EMOS is not a companion installed or
run beside stock MOS. It retains stock MOS behavior and interfaces while adding
the VDU dispatcher, mode-transition coordinator, and other explicitly accepted
Extender support. Use “stock MOS” for the unmodified official firmware and
“EMOS” for this replacement from this point forward.

## Open decisions

- [x] **SETUP-005-D001 — Exclusive EDP routing:** accepted 2026-08-23. Use one
  EMOS semantic VDU dispatcher for `RST.LIL 10h`,
  `RST.LIL 18h`, and MOS C-runtime `putch`/`printf`, with byte and block-stream
  operations. Legacy and Dual select onboard UART0; Exclusive Compatible
  selects the future EDP stock-UART backend; Exclusive Extended selects the EDP
  forward-parallel backend. Raw UART APIs retain their device identities. Rev
  1 uses MOS/eZ80 as the sole onboard-VDP/EDP intermediary and retains a private
  onboard-VDP control route only for input bootstrap and accepted delegated
  configuration. Fixed-backend MOS builds are permitted and required as
  developmental/qualification stages, but do not resolve D002 lifecycle.
  Application entry point and destination remain distinct: reset-vector and
  C-runtime output are always VDU calls, while explicit EDU calls use the
  separate versioned EDU interface and result domain. EDU-aware applications
  may combine both call classes without defining another operating mode. In
  Dual they address different processors; in either exclusive mode both may
  reach different interfaces of the EDP. Mode-dependent applications may
  require Exclusive Extended and use conventional VDU restart calls as their
  efficient compatible-output path, but must verify or request that mode before
  issuing output that would be unsafe or meaningless through the onboard VDP.
- [x] **SETUP-005-D002 — Mode lifecycle:** accepted 2026-08-24. Define selection, discovery,
  transition, reset, failure, and recovery behavior for Legacy, Exclusive
  Compatible, Exclusive Extended, and Dual modes. Legacy mode must make
  Extender electrically and logically absent from the Agon interface. Mode
  activation must be transactional: missing or incompatible MOS hooks, EDP
  firmware support, resident/TSR-like support, MOS Modules, transport backends,
  or other prerequisites must leave the current mode and routing unchanged and
  report a bounded failure. On stock MOS, the normal `Invalid command` or
  unavailable-API result for an uninstalled Extender facility is acceptable
  graceful failure; stock MOS supports only Legacy and direct Extender hardware
  access is out of scope. Accepted lifecycle foundation: formal mode is the
  committed combination of two distinct EMOS-owned logical planes, VDU routing
  and EDP service. The only supported combinations are Legacy
  (onboard/inactive), Dual (onboard/active), Exclusive Compatible
  (EDP-compatible/active), and Exclusive Extended (EDP-extended/active).
  Exclusive routing with inactive EDP is invalid. A third independent state
  dimension requires explicit architectural review. Live Legacy↔Dual
  activation is accepted. The proof-of-concept/beta baseline uses a disruptive
  controlled restart for every ordinary-VDU route change and remains an
  acceptable v1 fallback. Preserving the loaded eZ80 program/data and resident
  processor state is an aspirational v1 target and firm v2 requirement under
  [MODE-001](MODE-001.md); preservation does not imply migrating display
  assets between processors. Every activation uses a
  prepare/readiness/commit/recover transaction: validate all prerequisites and
  initialize the complete target before publishing new routing, restore a
  stable mode after bounded pre-commit failure, and let the EMOS coordinator
  make no more than one transition attempt per explicit request. This
  routing-coherence guarantee is independent of later
  state-preservation work. Legacy is the mandatory hub for all transitions:
  there are no contracted direct transitions between two non-Legacy modes.
  Every cold boot reaches fully operational Legacy and contacts Extender only
  after an explicit late `autoexec.txt` or manual invocation. A successful
  explicit presence/version probe activates EDP and commits Dual; failure
  leaves Legacy. Exclusive entry begins only after Legacy. Persisted preferred
  mode selection is exploratory and not a v1 contract. Pending state is needed
  only if a selected implementation carries an attempt across reset; retained
  cross-boot circuit breaking is not a beta requirement and remains a
  regression-driven conditional v1 target under [MODE-002](MODE-002.md).
  After commit, detected EDP failure in Dual invalidates EDU work and commits
  Legacy while onboard VDU continues. Exclusive EDP/transport failure blocks
  VDU and allows only bounded reinitialization before disruptive recovery to
  Legacy; it must not claim that application/display state survived. Structured failure
  reporting is advisable during beta and a hard v1 requirement, but not a beta
  gate. It requires best-effort descriptive onscreen reporting and durable
  machine-readable logs of consequences and safely obtainable processor
  context under [DIAG-001](DIAG-001.md). Reset invalidates the affected
  component's sessions, parsers, pending work, readiness, and authority even
  when RAM bytes or another processor survive; invalidation does not require
  erasure. eZ80/MOS and whole-system resets return through Legacy, and P4 reset
  in Dual commits Legacy. EMOS is a single complete
  backward-compatible stock-MOS replacement whose dispatcher alone owns
  ordinary VDU routing and whose lifecycle/EDU machinery alone owns EDP
  activation in Dual and both exclusive modes. Formal mode is derived from the
  two committed planes. Lifecycle
  records include requested, conditionally pending, committed, failure, and
  fallback information. Exact APIs and storage remain deferred, persisted user
  preference is not a v1 contract, and fixed-backend builds still require
  explicit activation after Legacy startup. Successful explicit
  probe/activation latches Dual as system state; foreground exit or zero known
  callers does not deactivate EDP. Normal return to Legacy is an explicit
  coordinated shutdown which may refuse or time out when registered work
  cannot quiesce. A separately explicit forced shutdown may invalidate work
  after warning. Reset/failure follows the accepted recovery rules; exact
  session and shutdown APIs remain deferred.
  EDP presence is pull-discovered as a hard v1 policy. EDP/P4 firmware and
  carrier wiring remain quiescent while Legacy is committed or a mode
  transaction is uncommitted. EMOS prepares the eZ80 receiver, issues the
  explicit request, validates the EDP response, and alone commits mode.
  Asynchronous EDP traffic requires a negotiated, armed post-activation
  receiver; P4 reset revokes that permission and EMOS quarantines stale traffic.
  Rev 1 defines no proactive presence signal. QUAL-002 owns electrical and
  power/reset qualification; D003 owns parser and response-domain mechanics.
  Before EMOS commits an exclusive route, a reviewed transport/wiring profile
  must be selected, EMOS must arm the eZ80 receiver and request readiness, and
  EDP/P4 firmware must return compatible identity, protocol, and capability
  data. That handshake establishes protocol readiness only; QUAL-002 remains
  the physical-wiring electrical authority.
  EMOS uses one fixed set of modified reset-vector and C-runtime output handlers
  which call one VDU dispatcher; mode changes switch only its committed backend,
  not vector tables. Each active invocation retains one backend snapshot. The
  EMOS coordinator blocks new calls, waits for active calls and owned response
  work to finish or be abandoned, reinitializes affected parser state, and then
  commits atomically. Beta adds no second semantic VDU parser and does not
  preserve multi-call partial commands across a disruptive transition.
  The EMOS dispatcher, EDP/P4 firmware, and carrier wiring never mirror
  ordinary application VDU to both processors. Legacy/Dual send it only to
  onboard VDP; exclusive modes send it only to EDP. Targeted private
  input/bootstrap control, recovery diagnostics, and separately identified
  qualification traffic are not mirrored application output.
  EMOS recovery may use the onboard VDP for diagnostics or restored Legacy
  output after exclusive EDP failure only after explicitly disclaiming
  application/display continuity; it must not claim that lost or unknown EDP
  display, audio, buffer, or application-visible state survived.
  Every active Extender mode requires EMOS. Before a valid activation
  transaction, carrier hardware must hold P4-to-Agon drivers disabled through
  hardware-safe defaults and EDP firmware may accept only the bounded
  activation exchange. Valid pre-activation logic patterns or GPIO-direction
  changes through project-owned supported paths may be ignored or fail safely.
  Ordinary VDU, EDU, updater, and persistent-write operations remain
  unavailable. External code that directly violates EMOS ownership receives no
  non-bricking guarantee. Any
  best-effort unmanaged-traffic warning uses only an Extender-owned out-of-band
  display or log and never the unactivated Agon interface. QUAL-002 owns the
  electrical proof; protocol and parser owners must prove bounded handling.
  EMOS recovery/reporting code and EDP/P4 diagnostic firmware must not send the
  only report through a failed component when another accepted sink survives,
  and diagnostic delivery must not delay safe recovery.
  V1 requires a bounded durable crash-log sink in P4 onboard flash independent
  of optional microSD. The existing `coredump` partition is the initial
  candidate pending DIAG-001 integrity, interrupted-write, wear, native-crash,
  retrieval, and evidence-scope qualification. Video/browser reporting alone
  is not durable.
  EMOS is the only supported authority for ordinary VDU routing, Extender
  transport hardware, and committed mode. Applications, linked clients, TSRs,
  MOS Modules, and resident services may request those operations only through
  documented EMOS interfaces. This is not an adversarial guarantee against
  deliberate unrestricted eZ80 register/GPIO access; no bomb-proof privilege
  system is a proof-of-concept or v1 requirement, and violating code may
  corrupt, damage, or brick either system.
  EMOS alone names the current formal mode from its committed state. EDP/P4
  firmware and applications may report local, requested, pending, readiness,
  transport, or failure state but must not present an uncommitted, failed, or
  partial combination as a formal mode.
  The EMOS mode-transition coordinator completes a committed return to Legacy
  before attempting any different non-Legacy destination. Direct non-Legacy
  transitions require later separate architecture, implementation, and
  qualification approval.
- [ ] **SETUP-005-D003 — Compatible response delivery:** determine how EDP
  responses and onboard-VDP input packets populate canonical MOS sysvars in
  both exclusive modes, and define the separate EDU result domain used in Dual
  mode. Exclusive Extended's adopted return path terminates on eZ80 UART1.
  Both exclusive modes select HW-001's current r02 common four-signal UART
  circuit; the remaining decision concerns firmware routing and response
  ownership, not a future unidentified circuit. R01 supplies no stock-UART
  authority. Stock MOS feeds only the onboard VDP's
  UART0 stream through its VDP packet parser. Extender, applications, and a
  resident service must not write MOS-owned sysvars directly; compatible
  updates require an explicitly selected MOS-owned parser route. Full D003
  disposition may use relevant PORT-008 staged circuit and component evidence.
  The former Exclusive Extended prototype is historical discovery input, not
  a required preliminary r01 run. PORT-008-D003 permits isolated UART/parallel
  stage tests but does not select a production response parser, settle the
  general EDU result domain, or authorize EDP/P4 writes to eZ80 memory.
  Any response/sysvar experiment must retain a separately reviewed EMOS-owned
  parser boundary and cannot imply acceptance of full mode behavior.
- [ ] **SETUP-005-D004 — Legacy abstraction boundary:** define which classes of
  non-EDU-aware software can be supported through wrappers or loaders in
  Dual mode and the qualification required for each class.
- [ ] **SETUP-005-D005 — Audio output routing:** decide whether any mode forwards
  EDP audio commands to the onboard VDP for local hardware playback. Retaining
  the complete audio command surface does not require this route; the currently
  scoped Rev 1 output is network/browser audio.
- [ ] **SETUP-005-D006 — Unsupported maintenance-command behavior:** define the
  closest practical stock-VDP-compatible command consumption, parser recovery,
  and externally observable failure behavior used in both exclusive modes for
  printer/USB serial, console/terminal, ZDI, Intel HEX, YMODEM, updater, and
  local-debug commands. Determine the stock behavior for each command and
  classify behavior by operating mode. Strict compatibility modes must permit
  stock-observable Bad Things—including corrupted output, resets, crashes, or
  Guru Meditations—where suppressing them would violate compatibility. Modes
  without that strict promise should improve the behavior with deterministic
  no-op, rejection, status, timeout, parser recovery, and diagnostics. Define
  explicitly which modes are strict before assigning command behavior.
- [ ] **SETUP-005-D007 — Peripheral-input ownership and routing:** retain the
  onboard VDP as the initial physical keyboard and mouse owner and preserve its
  stock packets to MOS as the canonical legacy input path. The proof of concept
  uses an EDU-aware eZ80 application to read stock input and explicitly forward
  processed events to Extender. Injected events update EDP-local behavior and do
  not automatically echo stock input packets back to the forwarding eZ80
  application. This does not support untouched applications or constitute
  transparent exclusive routing. Determine whether and how v1 adds
  a more automatic route by which an exclusive EDP session receives events for
  display-local behavior—including paged mode, control-key handling, mouse
  cursor state, VDP variables, and callbacks—without creating competing MOS
  sysvar writers. Compare an Extender-enabled MOS relay, aware-application
  forwarding, and other eZ80-owned routing mechanisms. Rev 1 selects no
  direct onboard-VDP/EDP bridge: MOS/eZ80 software must relay every message
  between them, including bootstrap, input, configuration, and any accepted
  delegation. A possible bidirectional high-speed direct link, probably SPI,
  is a post-v1 aspiration owned by LINK-001 rather than a current requirement.
  REMOTE-001 now supplies concrete browser-keyboard, remote-terminal, and
  agent-control reasons to revisit that schedule. The current Rev 1 exclusion
  remains authoritative until D007 and the architecture receive an explicit
  reviewed amendment; task creation alone does not select or authorize a link.
  Rev 1 also adds no P4-owned keyboard, mouse, or other peripheral hardware
  beyond facilities already present on the selected P4 DevKit; any such
  expansion is post-v1.
- [ ] **SETUP-005-D008 — RTC authority and synchronization:** define the
  authoritative clock and read/set routing in Legacy, Exclusive Compatible,
  Exclusive Extended, and Dual modes. Specify how MOS RTC sysvars, the onboard
  VDP, the EDP system clock, and optional network time interact; prevent
  competing writers; define reset persistence, timezone expectations, conflict
  and failure behavior, and any capability/status reporting. Do not allow
  network synchronization to silently override an application-set clock unless
  the selected policy explicitly permits it.

When all eight decisions are accepted and incorporated into ADR-0014, change its
completeness to `Complete` and remove the resolved items from this task after
recording their disposition in the development log.

## Qualification and implementation gates

- Every accepted decision must update the corresponding QUAL-001 operating-mode,
  transport, MOS/sysvar, carve-out, blocker, and qualification fields.
- `SETUP-005-D001` and `D002` retain EMOS routing and lifecycle authority.
  PORT-008-D003 now sequences r02 circuit/component tests independently of a
  complete exclusive-mode implementation. Full SETUP-005-D003
  acceptance still gates production response routing, broad General Poll and
  response-class qualification, Exclusive Compatible integration, Dual's EDU
  result domain, and any general compatibility claim. Bounded physical-link
  analysis and stage tests that make no mode or MOS claim remain independently
  permissible under their applicable procedure gates. The
  [staged process](../qualification/staged-circuit-validation.md) does not
  release any mode-dependent freeze or authorize physical execution itself.
- `SETUP-005-D002` gates QUAL-002's complete legacy-absence, reset, failure, and
  recovery state matrix.
- `SETUP-005-D005` gates only optional onboard-VDP audio forwarding; it does not
  block PORT-004's guaranteed network/browser sink.
- `SETUP-005-D006` through `D008` continue to block their exact mode-dependent
  compatibility rows and physical procedures until accepted.

## Current routing analysis

D001's EMOS-owned VDU dispatcher/backend map and D002's lifecycle contract are
accepted. Exact response parsing, input integration, transport details, and
implementation remain gated by D003, D007, REMED-001, and their owning PORT
tasks.

The common required behavior of Exclusive Compatible and Exclusive Extended is:

```text
all application audio/video output -> EDP
onboard VDP keyboard/mouse input    -> Extender compatibility path
Extender compatibility path         -> one coherent MOS response/sysvar domain
```

A normal resident program cannot transparently intercept untouched applications
through the documented MOS interrupt-vector API because the VDU restart handlers
are fixed in low ROM. The evaluated implementation families are:

1. **Hardware interposition:** place switching or gateway hardware between the
   eZ80, onboard VDP, and EDP. This offers strong transport ownership but is
   disfavored because requiring users to modify an Agon with a soldering iron is
   incompatible with the intended product experience.
2. **Narrow MOS transport support:** leave `RST.LIL 10h` and `RST.LIL 18h`
   unchanged while adding a selectable output backend to the MOS routines they
   already invoke. Legacy mode targets the onboard UART, Exclusive Compatible
   targets the Extender stock-UART transport, and Exclusive Extended targets
   the Extender enhanced forward transport.
3. **Runtime ROM shadowing or patching:** redirect the low-memory handlers using
   eZ80 mapping facilities if such a safe mechanism exists. Feasibility has not
   been established.
4. **Application loaders or binary rewriting:** adapt selected programs. This
   may support useful compatibility profiles but cannot establish a guarantee
   for arbitrary untouched binaries.

The accepted narrow MOS direction keeps the onboard VDP's input packets arriving
on UART0 and reuses MOS's normal parser to update canonical sysvars. MOS could mirror
those parsed events to the EDU service so the EDP sees the same input. When the
EDP parser recognizes a keyboard or mouse configuration command in the diverted
VDU stream, it could ask the MOS backend to forward the corresponding bytes to
the onboard VDP; this avoids adding a second complete VDU parser to MOS.

This direction keeps sysvar memory under MOS ownership, avoids competing packet
writers, and requires no user hardware modification. It would, however, make an
Extender-enabled MOS release a prerequisite for full exclusive compatibility
and requires a defined stock-mode fallback. The MOS requirement and lifecycle
fallback are accepted under D001 and D002; the remaining response-path and
input mechanics stay open under D003 and D007.

## Review gate

Present the open decisions individually with recommendations, alternatives,
tradeoffs, prerequisites, and downstream effects. Do not implement MOS changes,
resident-service behavior, transport routing, mode transitions, or onboard-VDP
delegation until the corresponding decision is accepted and promoted into
ADR-0014.

## Accepted REMED-002 findings

The Author accepted SETUP-005's portions of F004, F009, and F018 through
[REMED-002](REMED-002.md). The audit evidence and provenance remain in
[`AUDIT-2026-09-01-001`](../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md).
These actions do not decide D003--D008 or authorize EMOS/EDP implementation.

1. [ ] **F004 policy split:** Under D006, decide the actor-explicit behavior for
   a complete but unsupported audio or updater command in each reachable mode,
   including full-byte consumption, bounded failure reporting, and whether the
   command is prohibited before transport activation. PORT-003 and PORT-004
   own parser and audio implementation contracts.
2. [x] **F009:** Promote every already accepted D002 lifecycle, transition,
   reset, discovery, recovery, and EMOS-ownership rule into ADR-0014 and
   `docs/architecture.md` before any downstream task consumes D002 as a
   satisfied implementation gate. Record the promotion in the development log.
3. [ ] **F018:** Resolve the disruptive beta transition carrier separately:
   name which processor restarts, where the requested target survives, which
   actor reissues or consumes it, when EMOS commits the target, and how failed
   or absent retained state returns to Legacy. If accepted, assign the EMOS
   implementation and cross-project qualification to a separately approved
   task rather than MODE-001 or MODE-002 by implication.

F009 is correction of normative authority, not a reopening of accepted D002
content. F018 remains an unresolved architecture question and must be presented
one decision at a time under this task's normal review gate.

### F009 promotion record

On 2026-09-01, ADR-0014 and `docs/architecture.md` received the complete
accepted D002 mode-state, transaction, transition, dispatcher, discovery,
activation, shutdown, reset, failure, recovery, and diagnostic-lifecycle
contract. The promotion also corrected two stale durable statements: the EMOS
committed-backend dispatcher is accepted rather than unresolved, and ordinary
application VDU is never mirrored even under controlled ownership. D003--D008
remain open, and the promotion deliberately leaves F018's disruptive-restart
actor and carrier unresolved.
