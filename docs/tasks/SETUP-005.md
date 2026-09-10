# SETUP-005 — Resolve EDU operating modes and system integration

## State

- Status: In progress — mode vocabulary and D001–D002 accepted. D003/D007 have
  an accepted browser/UART direction; their remaining choices and D004–D006/D008
  stay open. Keyboard decisions accepted for freeze, 2026-09-08.
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

## Current priority — mainboard/Extender keyboard selection (2026-09-09)

The accepted browser keyboard slice now has physical typing and measured
latency/connection findings. On 2026-09-09 the Author selected PORT-015's
direct USB keyboard, now passing ordinary EMOS CLI and gameplay on mainboard
VGA. K010 makes selectable mainboard/Extender input the immediate goal and
defers browser input until explicitly reprioritized. Existing UART/keyboard
ownership decisions apply. Only the
keyboard portions of D003/D007 are on this path; other mode/service decisions
remain open.

| Decision | Accepted direction or remaining question | State / owner |
|---|---|---|
| SETUP-005-K001 | Browser → P4 processed keyboard → stock VDP packets on r03 UART1 → EMOS-owned keyboard handling/sysvars/keymap. Both directions use 1152000/8N1 RTS/CTS. No parallel or onboard relay. | Accepted by the Author, 2026-09-08; amended ADR-0014 and architecture. |
| SETUP-005-K002 | Explicit autoexec command enables EMOS browser-keyboard reception; for the first increment EMOS accepts P4 keyboard events exclusively while retaining other onboard VDP communications. On focus loss/disconnect, P4 sends stock key-up packets for held keys, then stops keyboard packets to EMOS. | Initial behavior accepted for trial by the Author, 2026-09-08. Detailed session mechanisms remain to be specified with REMOTE-001 and INTEG-009. |
| SETUP-005-K003 | Persistent UART1 reception and stock handler reuse with separate UART0 parser state, stock callback context/order and no conflicting keyboard writers. | Interrupt-driven UART1 and separate packet assembly accepted, 2026-09-08; detailed implementation/qualification belongs to PORT-008 and INTEG-009. |
| SETUP-005-K004 | Case-insensitive `EMOS <subcommand>` control; `EMOS EXCOM` / `EMOS LEGACY` destination selectors; `EDU` explicit Extender commands; `EMOS KEYINPUT [mainboard / browser / extender]` source selection/reporting; `SET KEYBOARD n` layout retained across mode changes; reboot persistence via autoexec. | Accepted, 2026-09-08; ADR-0014 CLI section is authoritative. K009 selects implementation of the reserved extender source. |
| SETUP-005-K005 | Keyboard source is independent of display mode. `EMOS LEGACY` restores mainboard VDU routing while preserving selected browser input; explicitly selected keyboard traffic is an exception to total Extender absence in Legacy. | Accepted by the Author, 2026-09-08; amends ADR-0014 and the two-plane model without treating keyboard-only activity as Dual. |
| SETUP-005-K006 | Start with mainboard input; restore desired source/layout and other explicit startup selections through `autoexec.txt` only. Commands retain runtime state across mode changes, not through separate saved configuration. | Accepted by the Author, 2026-09-08. No new state/.cfg/NVS settings store for this increment; revisit only if a later need justifies it. |
| SETUP-005-K007 | ExCom sends ordinary CLI/VDU output to EDP; mainboard VGA shows a static mode banner with cursor hidden. No double buffering or periodic redraw; VBlank continues. Dual retains active display roles. | Accepted by the Author, 2026-09-08; ADR-0014 display section. |
| SETUP-005-K008 | Initially, return to Legacy with a fresh mainboard screen, visible cursor and MOS prompt, preserving keyboard source/layout. | Accepted by the Author, 2026-09-08. Later, consider one-line transition notices and cursor hide/show while preserving the existing background; not a first-increment gate. |
| SETUP-005-K009 | Bring forward one directly attached USB keyboard using P4 native USB host and `EMOS KEYINPUT extender`; reuse stock packets over r03 UART1. First prove ordinary EMOS CLI on mainboard VGA, independently of browser focus/network. The DevKit USB connector/power assembly is permitted for this input. | Accepted by Author, 2026-09-09; PORT-015 owns implementation and physical proof; ADR-0014 amended. |
| SETUP-005-K010 | Prioritize selectable `mainboard` / `extender` keyboard input after native USB CLI and gameplay pass. Defer browser input until explicitly reprioritized, preserving its code, decisions and findings. Record the tested USB connection in the hardware specification now; defer the schematic update to the next Author session. | Accepted by Author, 2026-09-09; PORT-015/PORT-005 own input qualification, REMOTE-001 is deferred, HW-002 owns the drawing update. |


K002's initial behavior, K003's receiver direction and K005's independent
keyboard source are settled; K006 settles autoexec-only persistence. The
Author approved the documentation freeze; implementation has not started. No broad
mode-transition redesign or complete four-mode matrix is a prerequisite for
an explicitly bounded keyboard test. Product mode integration remains gated.

K002 cleanup was accepted for trial: P4 tracks held keys and emits their stock
key-up events before going quiet on focus loss or browser disconnect. This
avoids leaving EMOS's keymap in a held state. REMOTE-001/PORT-005 implement the
behavior; receiver qualification verifies the resulting EMOS state. Abrupt
browser loss must not depend on the browser sending its own final releases.

K005 explicitly permits selected browser input while mainboard VDU output
continues. Mode changes preserve the keyboard source. Keyboard-only P4 traffic
is an accepted exception to earlier total-inactivity language in D002 and the
linked lifecycle studies; it does not activate the ordinary EDP/EDU service or
commit Dual. EMOS still owns activation, transport and canonical state. K006
restores startup selections only by executing autoexec commands. The immediate
startup/source/receiver decisions are settled; broader task questions remain
outside this first increment.
The Author approved freezing these decisions on 2026-09-08; no implementation
has started.

## Later display refinement

The Author would prefer eventually retaining the mainboard display contents,
including a user-chosen background, with one-line mode-change confirmations
and cursor hide/show on departure and return. K008's initial fresh-screen
behavior is accepted for now, not a permanent requirement to clear the display.
When revisiting this, account for notice placement and scrolling so a status
line does not accidentally destroy the background it is meant to preserve.
No screen snapshot/restore machinery or new implementation is requested now.

## Implementation strategy — resident EMOS

The Author rejected the proposed moslet-space module foundation and runtime
relocation. Extend resident EMOS with normal compile-time linking and clear
command/service/interrupt ownership. No module loader, generic module manager
or moslet-space restriction gates the keyboard increment. INTEG-009 owns the
implementation; MOS-001 is cancelled and retains historical research only.
K001–K008 remain accepted. The documentation freeze is approved; coding is
separate.

## Accepted operating-mode vocabulary

The Author accepted the following formal names and stable identities on
2026-08-23:

- **Legacy mode** — `mode:extender:legacy`; mainboard VDU routing and inactive
  EDP/EDU service, with explicitly selected browser input permitted under K005.
- **Exclusive Compatible mode** — `mode:extender:exclusive-compatible`; the EDP
  is exclusive and uses the stock VDP UART transport contract.
- **Exclusive Extended mode** — `mode:extender:exclusive-extended`; the EDP has
  the same exclusive compatibility authority and uses the enhanced
  parallel-forward/UART-return transport.
- **Dual mode** — `mode:extender:dual`; the onboard VDP owns ordinary VDU and
  canonical stock state while EDU addresses the active EDP separately.

“Compatible” and “Extended” are permitted short forms in unambiguous
operating-mode context. “Exclusive” is mandatory in the two official names.
On 2026-09-08 the Author also accepted **ExCom** as conversational shorthand
for **Exclusive Compatible**, retaining its formal name and stable identity.
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
  controlled restart for ordinary-VDU route changes outside the accepted
  PORT-008-D005 idle-console Legacy↔ExCom exception, and remains an
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
- [ ] **SETUP-005-D003 — Compatible response delivery (partially accepted):**
  EMOS owns reception and canonical sysvar effects. K001 selects ordinary VDP
  keyboard packets from P4 over the existing r03 UART1 link for the next
  increment. Stock MOS currently parses VDP packets only from UART0; INTEG-009
  must preserve its keyboard semantics while providing an EMOS-owned UART1
  ingress. Sysvars and the virtual keymap are local MOS memory, not additional
  UART payload formats. Keep UART0/UART1 parser assembly and source authority
  separate; reuse stock handlers without competing canonical writers.
  K002/K003 track session/receiver details. Other packet classes, exclusive-mode
  integration and Dual's separate EDU result domain remain open. The old r02
  circuit and parallel Work 2.e are held, not prerequisites for this r03 UART
  keyboard increment. Do not conflate the completed bounded UART diagnostics
  with a persistent receiver or complete mode qualification.
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
- [ ] **SETUP-005-D007 — Peripheral-input ownership and routing (partially accepted):**
  K009/K010 select native USB keyboard input into P4, then stock keyboard
  packets over UART1 into EMOS, with explicit mainboard/extender selection.
  K001's browser acquisition remains deferred. Applications use normal MOS key reads, sysvars,
  virtual keymap and callbacks; no aware-application relay is required. P4
  preserves relevant EDP-local keyboard state and packet semantics. K002/K003
  retain exact source/session/receiver choices; PORT-015/PORT-005 own native
  USB mapping, repeat and release, while REMOTE-001 retains browser-specific
  session details. The stock onboard VDP remains the source
  for physical devices where selected and remains the current VBlank clock.
  Mouse, multi-source composition and later aware-application EDU forwarding
  remain open. Copied Agon-originated events retain non-echo behavior.
  Rev 1 selects no direct onboard-VDP/EDP bridge; LINK-001 is later research
  and is not a keyboard dependency. The P4 USB connector/power addition is
  selected; no direct onboard-VDP/EDP bridge is implied.
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
selected browser/physical input    -> Extender compatibility path
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

The immediate Extender keyboard route is USB keyboard → P4 → UART1 → EMOS. EMOS
preserves stock packet-handler effects and application interfaces; its
session/source-selection policy prevents conflict with onboard UART0 traffic.
A later selected physical onboard-input route may use an EMOS-owned relay and
controlled device configuration, but is not a prerequisite for native USB input.
D003/D007 retain the remaining parser/session decisions and broader mode scope.

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

PORT-008-D005, accepted 2026-09-09, authorizes the first idle-CLI ExCom/Legacy
implementation without restart. It preserves keyboard source/layout with fresh
destination screens. F018 is not a prerequisite for this bounded increment.
