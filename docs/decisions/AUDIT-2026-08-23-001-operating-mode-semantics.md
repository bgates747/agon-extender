# AUDIT-2026-08-23-001 — Operating-mode semantics and ownership consistency

- Status: Complete — findings await Author disposition
- Date: 2026-08-23
- Trigger: Author clarification during QUAL-001 Review Gate 2
- Scope: All tracked architecture, decisions, tasks, qualification data,
  procedures, hardware records, implementation, tests, generated artifacts,
  and development logs that encode Extender operating-mode semantics
- Owning task: QUAL-001

## Purpose and authority boundary

Audit the repository against the Author's clarified top-level operating-mode
boundaries before QUAL-001 accepts or promotes its mode matrix. This record
captures observed state and required disposition. It does not itself rename a
mode, resolve an implementation mechanism, amend ADR-0014, or authorize code,
MOS, transport, wiring, or generated-data changes.

QUAL-001 Review Gate 2 decision `RG2-02` is withdrawn and replaced by
`RG2-02R`. Current qualification mode records remain superseded candidate data
and must not be promoted before the accepted four-mode vocabulary and remaining
boundaries are reflected and reviewed.

## Clarified target contract

The audit uses the following Author-supplied boundary as its review baseline.
The names below are authoritative as accepted by the Author.

| Mode | Active display processors | Compatibility command transport | Reverse path | MOS/eZ80 ownership boundary |
|---|---|---|---|---|
| Legacy | Onboard VDP only; an attached Extender behaves exactly as if it were not attached | Stock onboard-VDP path | Stock onboard-VDP path | Onboard VDP and stock MOS retain all ownership. Official ID: `mode:extender:legacy`. |
| Exclusive Compatible | P4 EDP is the exclusive compatibility display processor | Stock VDP UART transport contract rather than the eight-bit forward path | Stock-compatible UART response path | EDP has the same unrestricted logical access to MOS integration hooks, canonical VDP sysvars, restart-vector routing, and related eZ80 assets that the onboard VDP has through MOS. Official ID: `mode:extender:exclusive-compatible`; **Compatible** is the accepted short form. |
| Exclusive Extended | P4 EDP is the exclusive display processor | Eight-bit forward parallel transport | Enhanced UART return contract, capabilities not yet selected | Same exclusive logical ownership and integration reach as Exclusive Compatible mode; transport enhancement does not reduce compatibility ownership. Official ID: `mode:extender:exclusive-extended`; **Extended** is the accepted short form. |
| Dual | Onboard VDP behaves normally while Extender capabilities are also active | Ordinary VDU remains with the onboard VDP; EDU addresses Extender separately | Extender uses a separate restricted result/return domain | Onboard VDP retains canonical MOS VDP sysvars and other exclusive stock assets. Extender must not collide with or impersonate that ownership; exact restrictions remain to be enumerated. Official ID: `mode:extender:dual`. |

“Logical access” is intentionally mechanism-neutral. The P4 cannot directly
write eZ80 memory across the presently selected physical links. Equivalent
ownership must be supplied through an accepted MOS/eZ80 route; this audit will
distinguish the required externally visible authority from the mechanism used
to implement it.

On 2026-08-23 the Author accepted **Exclusive Compatible mode** and
**Exclusive Extended mode** as the two official P4-exclusive names. The word
“Exclusive” is mandatory in formal naming; **Compatible** and **Extended** are
permitted short forms where the operating-mode context is unambiguous.
The Author also accepted **Dual mode** as the official name for simultaneous,
separately addressed onboard-VDP and EDP operation.

## Initial findings

### `MODE-AUDIT-F001` — “Legacy mode” is ambiguous between two incompatible system states

- Severity: Critical
- Observed state: ADR-0014 decision 20 and `docs/architecture.md` define legacy
  mode as a stock-machine bypass in which Extender is electrically and
  logically absent and the onboard VDP owns VDU, responses, input, sysvars, and
  maintenance facilities.
- Clarified boundary: A P4-active, P4-exclusive mode using the stock UART
  transport contract and full compatibility ownership is mandatory. The Author
  may retain “legacy mode” for the existing electrically absent bypass state
  and coin a new name for this strict-compatible P4 mode.
- Consequence: Existing prose may remain correct for the bypass state if its
  name is retained, but it must not be mistaken for the missing P4-exclusive
  stock-UART mode. Any use of “legacy” without naming the active processor and
  transport is unsafe until terminology is frozen.
- Disposition: Resolved for the two P4-exclusive states as Exclusive Compatible
  and Exclusive Extended. Legacy remains the bypass/inactive name. Amend
  affected architecture where it currently treats bypass as the only
  legacy/stock-compatibility profile.
- Known affected authorities: ADR-0014, `docs/architecture.md`, SETUP-005,
  AUDIT-001, QUAL-001, QUAL-002, PORT-008, SETUP-004 records, and the current
  qualification mode data and generators.

### `MODE-AUDIT-F002` — The required stock-UART exclusive mode is missing

- Severity: Critical
- Observed state: Current documents define one `EDP-exclusive compatibility
  mode`, generally associated with the split parallel-forward/UART-return
  architecture. They do not model a separate P4-exclusive stock-UART mode.
- Clarified boundary: Exclusive Compatible and Exclusive Extended are both
  P4-exclusive and have equivalent compatibility ownership, but use different
  transport profiles and may expose different reverse capabilities.
- Consequence: Current three-way mode matrices cannot represent the clarified
  contract by relabeling rows. A second exclusive identity and transport axis
  are required, or mode records must otherwise encode the distinction without
  losing ownership equivalence.
- Disposition: Names and IDs are resolved as
  `mode:extender:exclusive-compatible` and
  `mode:extender:exclusive-extended`; transport is intrinsic to those mode
  identities. Exact reverse capabilities remain unresolved.

### `MODE-AUDIT-F003` — Dual-mode ownership is directionally correct but incomplete

- Severity: High
- Observed state: ADR-0014 already gives ordinary VDU and canonical MOS VDP
  sysvars to the onboard VDP in Dual mode and requires a distinct EDU
  result domain. This matches the clarified top-level boundary.
- Gap: The repository does not exhaustively enumerate which MOS hooks, sysvars,
  completion flags, restart-vector routes, eZ80 memory, callbacks, input state,
  RTC state, and asynchronous packet domains are exclusive or safely shareable.
- Consequence: “Separate EDU result domain” is directionally sound but too
  abstract to qualify non-collision or to design the reverse transport.
- Required disposition: Produce an explicit ownership inventory after the
  current audit identifies every existing assumption and unresolved item.

### `MODE-AUDIT-F004` — “Access to MOS/sysvars/reset vectors” needs a logical-versus-physical distinction

- Severity: High
- Observed state: Existing accepted architecture correctly prohibits the P4,
  applications, and resident services from writing MOS-owned memory directly.
  Current physical transport also provides no direct memory bus.
- Clarified boundary: Both exclusive modes must enjoy the same externally
  visible integration authority as the stock VDP.
- Consequence: Documentation must state the compatibility contract as logical
  ownership mediated by MOS/eZ80 code, while separately tracking the unresolved
  routing mechanism. Otherwise “unrestricted access” could be misread as
  unsafe direct memory ownership.
- Required disposition: Preserve MOS ownership of memory writes while defining
  the exclusive EDP as authoritative source/consumer for the same logical
  hooks, parser effects, completion flags, and sysvar updates.

### `MODE-AUDIT-F005` — Current QUAL-001 candidate mode matrix is incomplete

- Severity: Critical
- Observed state: QUAL-001 currently assigns all 211 interfaces to the onboard
  VDP in `mode:extender:legacy`, all 211 ordinary VDU interfaces to the onboard
  VDP in cooperative mode, and 185 required/8 unsupported/18 unresolved entries
  to one EDP-exclusive mode.
- Clarified boundary: If “legacy” remains the bypass name, its current ownership
  row may remain. A new Exclusive Compatible row is required, and the current
  EDP-exclusive row is the predecessor candidate most closely aligned with
  Exclusive Extended. Dual remains onboard-VDP-owned for ordinary VDU.
- Consequence: `RG2-02` cannot be accepted as written. Reviewed modes,
  mode-expectations, obligations, fixture data, seed scripts, generated views,
  tests, and the task execution record require correction after terminology and
  the stock/bypass disposition are accepted.
- Required disposition: Keep RG2-02 open and suspend all authority promotion.

### `MODE-AUDIT-F006` — Stock UART compatibility has three distinct layers

- Severity: Critical
- Observed state: Official VDP `v2.16.0` consumes a byte stream at 1,152,000
  baud and returns protocol packets over `Serial2`. Its concrete binding uses
  fixed ESP32 TX, RX, RTS, and CTS pins, starts with RTS flow control, and may
  enable CTS/RTS full duplex. Stock MOS sends VDU bytes through UART0 from the
  fixed restart handlers and feeds UART0 receive bytes directly to the
  MOS-owned VDP packet parser.
- Clarified boundary: Exclusive Compatible mode requires the stock
  application and MOS-visible contract, but the current Extender attachment
  reaches eZ80 UART1 rather than the onboard VDP's UART0 path.
- Consequence: Documentation currently uses “stock UART contract” without
  consistently separating (a) VDU and response bytes, (b) MOS routing and
  parser effects, and (c) physical signaling and flow control. A software/MOS
  route can preserve the first two while using different physical pins, but
  that is not literally the stock electrical path.
- Required disposition: SETUP-005 must define the required fidelity at all
  three layers. PORT-008 then owns the selected implementation and
  qualification; no direct P4 write to MOS memory is permitted.

### `MODE-AUDIT-F007` — The current harness is not a stock-UART design candidate

- Severity: Critical
- Observed state: `light2-harness-r01` maps eZ80 PC0 to P4 GPIO22 as receive,
  and conditionally maps P4 GPIO12 to eZ80 PC1 as transmit through buffered
  direction control. That circuit has inherited 115,200-baud, 8-N-1,
  break-before-make evidence for the predecessor's enhanced
  parallel-forward/reverse-UART experiment. It was not designed to conform to
  the stock VDP UART's physical, flow-control, endpoint-routing, or firmware
  requirements. No separate RTS/CTS conductors are selected.
- Author disposition: Do not treat this circuit as the first stock-UART design
  target and do not qualify it into that role by incremental testing. The
  stock-UART profile requires a fresh hardware design review, a new design, and
  the complete validation and qualification appropriate to that design.
- Sequencing consequence: Hardware design does not gate development of the
  stock-compatible firmware behavior. Firmware work must first establish the
  exact endpoint, signaling, flow-control, timing, reset, failure, and recovery
  demands using hardware-independent boundaries and deterministic tests. Once
  those requirements are mature enough to drive circuitry, create the formal
  hardware design-review task and new versioned design. Physical testing begins
  only after that review is accepted.
- Existing-harness boundary: `light2-harness-r01` remains relevant only to the
  enhanced split-link profile and as inherited evidence about its own circuit.
  It supplies no stock-UART hardware authority or qualification claim.

### `MODE-AUDIT-F008` — PORT-008 owns only the enhanced split transport

- Severity: Critical
- Observed state: PORT-008's intent and work plan define one compatibility
  transport: eight-bit parallel Agon-to-P4 commands and UART1 P4-to-eZ80
  responses. Its General Poll, MOS parser, physical ownership, and bench stages
  all presume that profile.
- Gap: No task owns an end-to-end P4-exclusive stock-UART command and response
  profile, including selection, MOS routing, flow control, General Poll, exact
  packets, sysvar effects, malformed traffic, reset, and recovery.
- Required disposition: After mode names and transport fidelity are accepted,
  revise PORT-008 into explicit transport-profile work or split out a separate
  firmware task. Permit hardware-independent firmware implementation and host
  qualification to proceed. Create a separate hardware design-review task only
  after the firmware requirements can authoritatively drive the new design.
  Keep shared parser and compatibility evidence factored once; do not make two
  unrelated implementations of the official wire semantics.

### `MODE-AUDIT-F009` — “Strict” and “full compatibility” currently exceed the accepted v1 scope

- Severity: High
- Observed state: ADR-0014 promises compatibility only for the declared normal
  application-facing surface and explicitly carves out printer/USB serial,
  console/terminal, ZDI, Intel HEX, YMODEM, firmware updating, and local debug.
  Some current prose nevertheless calls EDP-exclusive operation “strict” or
  “complete” compatibility.
- Consequence: A final mode name containing “strict” or “compatible” can be
  read as restoring those omitted facilities. Transport fidelity and
  compatibility-surface coverage are independent claims.
- Required disposition: The naming discussion must either preserve the
  accepted carve-outs visibly or explicitly reopen them. QUAL-001 must encode
  the selected surface for both P4-exclusive modes rather than infer it from a
  mode label.

### `MODE-AUDIT-F010` — Exclusive Compatible and Exclusive Extended share ownership but not transport

- Severity: High
- Observed state: The clarified contract gives both exclusive modes the EDP as
  the sole audio/video compatibility authority and grants the same logical
  reach into MOS-owned parser effects, completion flags, sysvars, input
  integration, and related eZ80 state. Their required distinction is command
  transport and, eventually, enhanced reverse capabilities.
- Consequence: Most retained VDU, display, audio, RTC, input, malformed-stream,
  and MOS-state obligations apply to both exclusive modes. Copying those rules
  independently would invite drift; transport-specific obligations must remain
  distinct.
- Required disposition: Model both modes explicitly while factoring their
  common exclusive-ownership contract into one reusable profile or domain.
  Duplicate only the interface/mode expectation tuples required by the matrix,
  not the explanatory authority.

### `MODE-AUDIT-F011` — Dual mode does not imply stream or state duplication

- Severity: Medium
- Observed state: The Author accepted Dual mode as the official name. ADR-0014
  explicitly rejects sending one uncontrolled ordinary VDU stream to both
  processors because state and response packets can diverge.
- Consequence: “Dual mode” accurately says both processors are active, but must
  not be documented as dual ownership, mirrored VDU, or shared canonical
  sysvars.
- Disposition: Define Dual mode as VDU/onboard-VDP plus separately addressed
  EDU/EDP, with stock state remaining onboard-owned. “Dual” describes two
  active processors, not dual ownership, mirrored VDU, or shared sysvars.

### `MODE-AUDIT-F012` — Existing source-selection decisions generally survive the four-mode correction

- Severity: Medium
- Observed state: SETUP-004 and ADR-0013 classify upstream code by retained
  behavior versus replaceable or omitted physical implementation. Display,
  audio, RTC surface, parser, packet, and shared type decisions do not depend on
  whether P4 commands arrive by UART or parallel transport. Physical PS/2,
  classic video, analog audio, and maintenance-driver omissions remain
  deliberate.
- Consequence: The audit does not reopen the completed source survey. Its
  mode-dependent language must be expanded so retained behavior is required in
  both P4-exclusive modes and proof-of-concept input injection is not mistaken
  for the final exclusive input route.
- Required disposition: Correct reviewed SETUP-004 evidence and dispositions
  only where they encode a three-mode assumption, then regenerate their
  projections and dependency data. Do not alter accepted source dispositions
  without a separate substantive finding.

### `MODE-AUDIT-F013` — Dual-mode EDU behavior is not the same thing as stock VDU compatibility

- Severity: High
- Observed state: The candidate matrix assigns every ordinary VDU interface to
  the onboard VDP in Dual mode, which matches ADR-0014. Some obligations
  nevertheless associate EDP display, audio, and input behavior with those VDU
  interface subjects in Dual mode.
- Consequence: Those obligations may describe useful EDP behavior reached via
  EDU, but a stock VDU interface row cannot prove an EDU operation that has not
  yet been specified or mapped. This risks conflating stock compatibility with
  analogous extended capability.
- Required disposition: During QUAL-001 correction, keep stock VDU expectations
  onboard-owned in Dual mode. Represent EDP behavior there through
  explicit EDU interfaces, mapped obligations, or another reviewed subject
  type after the EDU contract exists; do not silently reuse stock VDU rows.

### `MODE-AUDIT-F014` — Qualification infrastructure needs bounded correction, not redesign

- Severity: Medium
- Observed state: The schema and semantic validator derive the complete
  interface/mode cross product from reviewed mode records and can support four
  modes. The one-time seed script emits exactly three modes, the compact matrix
  renderer hard-codes three columns, one unit test fixes the count at 633, and
  current reviewed/generated data contain three mode identities.
- Consequence: Adding the missing mode should produce 844 interface/mode tuples
  for the present 211 interfaces. The existing normalized model, duplicate
  protection, references, deterministic generation, and authority boundary
  remain valid.
- Required disposition: After terminology is accepted, update reviewed data,
  make rendering order data-driven or explicitly four-mode, change invariant
  tests to assert the reviewed cross product, and regenerate all projections.
  Do not hand-edit generated files.

### `MODE-AUDIT-F015` — No system-mode behavior is encoded in current firmware

- Severity: Low
- Observed state: No Extender system-mode ID, selector, transition, or routing
  implementation exists under `vdp/`. Current PORT-003 code implements a
  mode-neutral display backend and frame service. Occurrences of upstream
  `legacyModes` in `agon_screen.h`, `context.h`, and `vdu_sys.h` refer to the
  stock VDU display-mode interpretation, not Extender operating modes.
- Consequence: No firmware rollback is required. Future code and generated
  dependency queries must distinguish “legacy display modes” from Extender
  “legacy mode.”
- Required disposition: Reserve stable machine IDs for Extender operating
  modes and use qualified terminology in prose. Do not rename upstream
  `legacyModes`, because preserving upstream names supports future merges.

### `MODE-AUDIT-F016` — Legacy/bypass is also an electrical contract

- Severity: High
- Observed state: ADR-0014, QUAL-002, and AUDIT-001 already require a connected
  and powered or unpowered Extender to be electrically and logically absent in
  legacy mode. The current harness leaves production isolation, power order,
  reset order, and released shared lines unqualified.
- Consequence: Retaining “legacy mode” for bypass is semantically coherent, but
  it is not satisfied merely by firmware deciding not to parse commands. The
  inactive board must release every shared net and avoid back-powering,
  contention, reset interference, and partial activation.
- Required disposition: Keep QUAL-002 as owner and expand its state matrix to
  all four modes after lifecycle decisions. Legacy/bypass remains its strongest
  absence case.

### `MODE-AUDIT-F017` — Top-level capability prose is incomplete, not contradictory

- Severity: Medium
- Observed state: README promises stock-compatible UART communication and an
  enhanced one-way parallel path but does not assign them to operating modes.
- Consequence: The public overview supports the clarified product direction but
  leaves readers unable to tell when each transport or VDP is authoritative.
- Required disposition: Add a compact operating-mode summary only after final
  names and boundaries are accepted.

### `MODE-AUDIT-F018` — Historical records and mode-neutral procedures do not need rewriting

- Severity: Low
- Observed state: Development logs record decisions as they occurred, including
  the earlier three-mode model. Existing P4 canary and frame-service procedures
  do not exercise system modes; their uses of “legacy” generally mean the
  predecessor repository or inherited evidence.
- Consequence: Rewriting history would destroy provenance, while globally
  replacing “legacy” would corrupt unrelated meanings.
- Required disposition: Add a dated correction/supersession entry when the new
  taxonomy is accepted. Amend only active or normative records. Preserve old
  logs, run manifests, and mode-neutral procedures as historical evidence.

### `MODE-AUDIT-F019` — Hardware terminology also overloads “legacy”

- Severity: Medium
- Observed state: The hardware profile names its UART section
  `legacy_uart_candidate`, where “legacy” means the inherited stock-compatible
  UART target, while fixture paths use `legacy-evidence` to mean provenance
  imported from the predecessor repository.
- Consequence: Neither term identifies Extender legacy/bypass mode. Automated
  searches can therefore produce false mode matches.
- Required disposition: Preserve `legacy-evidence` as provenance vocabulary.
  After transport names are accepted, rename or explicitly qualify
  `legacy_uart_candidate` as the stock-VDP UART transport candidate and update
  dependent references through the profile's normal revision process.

### `MODE-AUDIT-F020` — Active task and authority correction order is constrained

- Severity: High
- Observed state: ADR-0014 and `docs/architecture.md` are the normative mode
  authority; SETUP-005 owns unresolved architecture; QUAL-001 is paused before
  mode promotion; PORT-008 and QUAL-002 consume those decisions; SETUP-004 and
  AUDIT-001 are accepted planning inputs; generated qualification and
  dependency files are projections.
- Consequence: Editing consumers first would create another incoherent state.
- Required disposition: Apply accepted corrections in this order: (1) freeze
  names and boundaries in SETUP-005/ADR-0014/architecture, (2) revise active
  transport and qualification tasks, (3) correct reviewed source data, (4)
  regenerate projections and dependency artifacts, (5) rerun validators and
  tests, and (6) resume QUAL-001 Review Gate 2.

## Coverage register

| Area | State | Initial observation |
|---|---|---|
| Normative architecture and ADRs | Reviewed | ADR-0014 and `docs/architecture.md` correctly define legacy/bypass and Dual ownership but originally contained only one P4-exclusive mode. ADR-0013 source boundaries remain valid. |
| Active setup/port/qualification tasks | Reviewed | SETUP-005 must own the four-mode correction; PORT-008 lacks stock-UART-exclusive work; QUAL-001 is correctly paused; QUAL-002 remains the absence/power owner; PORT-003 through PORT-007 need only bounded mode-language corrections. |
| Reviewed and generated qualification data | Reviewed | Three-mode data are incomplete. Core model is reusable; seed, renderer, fixed-count test, reviewed records, and generated projections require correction and regeneration. |
| Hardware and transport records | Reviewed | The PC0/PC1 circuit belongs to the enhanced split-link experiment and is not a stock-UART candidate. Stock UART requires a fresh firmware-driven hardware review and new design; shared-pin and electrical-absence work for the existing enhanced harness remains unqualified. |
| Firmware and tests | Reviewed | No Extender system-mode implementation exists. PORT-003 is mode-neutral. Upstream `legacyModes` is unrelated display-mode vocabulary and must remain recognizable for mergeability. |
| Procedures and run manifests | Reviewed | Current procedures and runs are mode-neutral and use “legacy” chiefly for predecessor provenance; no result is invalidated by the taxonomy correction. |
| Development logs and historical evidence | Reviewed | Preserve historical statements. Add a current supersession entry after decisions are accepted rather than rewriting prior logs. |

## Artifact disposition map

| Class | Artifacts | Disposition after Author decisions |
|---|---|---|
| Normative authority | ADR-0014; `docs/architecture.md` | Amend first with final names, four functional boundaries, common exclusive ownership, and mode-specific transports. |
| Open architecture tracker | SETUP-005 | Expand D001–D008 across four modes; add or split questions where strict UART and enhanced reverse contracts differ. |
| Active qualification authority candidate | QUAL-001 task, reviewed YAML, seed script, renderer, tests | Keep RG2-02 open; correct to four modes and 844 tuples; separate stock VDU from EDU behavior in Dual mode; regenerate. |
| Transport and physical qualification | PORT-008; QUAL-002; `light2-harness-r01` | Add hardware-independent stock-UART firmware ownership and preserve enhanced split-link work. After firmware requirements mature, create a separate stock-UART hardware design-review task and new design. Retain legacy/bypass electrical absence qualification; do not repurpose `light2-harness-r01` as stock-UART hardware. |
| Accepted source survey and planning | ADR-0013; SETUP-004; AUDIT-001; PORT-004/005 | Preserve dispositions and findings; add bounded correction notes and regenerate derivative inventories where mode scope changes. |
| Implementation | `vdp/` and current host/target tests | No corrective code action now; modes are not implemented. Later implementation waits for accepted architecture and task gates. |
| Public overview | README | Add mode summary after terminology is frozen. |
| Historical evidence | development logs, procedures, run manifests, `legacy-evidence/` | Preserve; add supersession provenance later. |

## Issues requiring later Author disposition

These are audit findings, not decisions or an independent actionable checklist.
They will be promoted into SETUP-005 or another approved task before work begins.

1. Does “full compatibility” restore the maintenance/operator facilities
   currently carved out of Extender v1, or do those carve-outs apply to both
   exclusive modes despite the broader phrase?
2. Which exact physical and flow-control requirements must the new stock-UART
   design satisfy after firmware work has frozen its externally visible,
   endpoint, timing, reset, failure, and recovery demands?
3. Which reverse capabilities distinguish Exclusive Extended mode once both
   exclusive modes have equal canonical MOS ownership?

## Audit conclusion

The clarified design is a four-mode system, not a corrected three-mode system:

1. legacy/bypass — Extender inactive and indistinguishable from absence;
2. Exclusive Compatible mode — P4 exclusive over the stock-UART contract;
3. Exclusive Extended mode — P4 exclusive over the enhanced transport; and
4. Dual mode — both processors active, but with separate command
   and state domains and onboard VDP primacy for stock VDU/MOS state.

The repository has no implemented system-mode behavior to remove. Its accepted
source-selection and completed display work remain usable. The material defects
are in mode vocabulary, transport task coverage, qualification classification,
and the boundary between stock VDU compatibility and EDU capability. The
correction must begin with a naming and contract discussion, then proceed
through the ordered authority map above before QUAL-001 Review Gate 2 resumes.
