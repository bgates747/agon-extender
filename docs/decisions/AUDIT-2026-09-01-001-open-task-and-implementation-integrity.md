# AUDIT-2026-09-01-001 — Open-task and implementation integrity

- Status: Complete — findings await Author disposition
- Date: 2026-09-01
- Trigger: Author-requested adversarial review of every open task and related code
- Scope: All 18 open tasks and their directly related architecture,
  implementation, validators, procedures, evidence, and version records
- Owning task: AUDIT-003
- Provenance extension: 2026-09-01

## Purpose and authority boundary

This audit records a repository-wide adversarial review of the work indexed by
`TODO.md`. It looks for unsafe interleavings, false-positive qualification,
broken provenance, stale authorities, unreachable recovery, contradictory task
ownership, and design gaps that ordinary success-path validation may not
expose.

The audit identifies observed defects and proposes disposition owners. It does
not amend architecture, accept a mechanism, modify a task's scope, authorize
implementation, promote evidence, qualify hardware, or permit a physical run.
Each finding is explicitly deferred pending Author disposition. Accepted work
must be promoted into the named task, applicable ADR or normative architecture,
and current development log before implementation begins.

## Reviewed snapshot

1. Repository `agon-extender` was reviewed at tracked `HEAD`
   `45c45d5ef02285a737969a11b29dcc011aa4ef9b` plus the Author's pre-existing
   uncommitted PORT-008 diagnostic, transport, procedure, corrective-action,
   development-log, and run-evidence work visible on 2026-09-01.
2. The dirty worktree was review input, not an identified build or release.
   This audit records no source-to-binary identity for those uncommitted bytes.
3. Official Agon documentation and the pinned local VDP, MOS, ESP-IDF, and
   vdp-gl sources were treated as read-only contract references.
4. No physical bench, deployment, reset, power, wiring, or network-device
   operation was performed.

## Severity and disposition model

- **High:** permits data corruption, memory misuse, protocol loss, indefinite
  hardware ownership, false qualification/provenance, or bypass of a mandatory
  architecture gate.
- **Medium:** weakens a required recovery or qualification oracle, loses
  resource ownership, or leaves an active task materially misleading.
- **Low:** creates a future authority or implementation ambiguity without an
  immediate incorrect runtime or qualification claim.
- **Prospective risk:** no current implementation defect is proved, but the
  named task must test or resolve the risk before selecting a design.

Every finding below is **deferred pending Author disposition**. “Proposed
owner” identifies where accepted actionable work should live; it does not
silently add work to that task.

## Code-defect provenance extension

The Author requested a second pass to determine whether each proved code or
validation-tool defect already exists in the code from which Extender derives,
or was introduced while porting or extending it. “Upstream” below is
identity-specific: official `agon-vdp` v2.16.0 at
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`, official `vdp-gl`
`all-the-plots` at `ac2dd5986daf496c43ae8e7fe41836274aec54a0`, and
official ESP-IDF v5.5.5 at
`b774170ff46c393eeb5e495ea37936038d3f4f4f`. It does not make a claim about an
unpinned future release.

| Finding | Provenance classification | Maintained-surface status |
|---|---|---|
| F001 | Present in upstream `vdp-gl`; independently reimplemented and extended by EDP | P4 display-controller code is product-directed |
| F002 | Present in upstream `vdp-gl`; independently reimplemented and amplified by EDP | P4 palette, Copper, and browser publication are product-directed |
| F003 | Present in upstream ESP-IDF; exposed by EDP's documented API use | Wired EDP browser service is product-directed |
| F004 | Absent upstream; created by making disconnected-only EDP stubs reachable | Audio stub is temporary; an omitted updater must still be framing-safe |
| F005 | Created during PORT-008 porting; upstream PARLIO behaves as documented | Current forward receiver is prototype-only |
| F006 | Created in the project qualification validator | Durable project tooling, not product firmware |
| F007 | Created in the project build stager | Durable project tooling, not product firmware |
| F011 | Created in project test runners by misusing intentional UBSan recovery | Qualification tooling, not product firmware |
| F012 | EDP loses ownership on a legitimate but incompletely documented ESP-IDF failure | Wired EDP browser service is product-directed |
| F013 | Created during PORT-008 porting; regression from the predecessor receiver | Current forward receiver is prototype-only |
| F014 | Created in uncommitted PORT-008 analyzers | Prototype evidence tooling only |
| Existing pre-activation corrective action | Created by P4 boot integration; absent from EMOS and official upstream | Current forward receiver is prototype-only |

For the twelve rows above, F001--F003 are proved upstream defects with local
EDP exposure or reimplementation. F004, F005, F012, F013, and the
pre-activation READY defect are project-created runtime or integration
defects. F006, F007, F011, and F014 are project-created tool defects. F012 also
exposes an ESP-IDF documentation inconsistency, but EDP's loss of the live
handle is still a local ownership error.

No defect in that matrix originates in the official MOS code or the EMOS mode
coordinator. The affected product firmware is EDP. This statement does not
erase already recorded EMOS prototype defects; their provenance is recorded
separately below. An upstream origin also does not make a defect acceptable in
a permanent Extender surface: project-owned replacements require local fixes,
and retained dependency defects require a bounded workaround or a pinned
upstream correction with a removal condition.

The official VDU documentation was consulted before the source comparison. It
defines one continuous VDU byte stream, command-dependent audio arguments, and
the updater's mode-dependent payload. Those contracts make F004 a framing
defect when its empty handlers become reachable; unsupported feature scope
does not permit leaving command bytes in the shared parser stream.

### Provenance of previously recorded PORT-008 code defects

The main matrix covers defects newly established by this audit plus the open
pre-activation corrective action. PORT-008 already recorded the following
defects during its physical investigations. They are included here so the
upstream/local and permanent/prototype boundaries are complete rather than
silently excluding code that had already been corrected or contained.

| Recorded defect | Provenance classification | Maintained-surface status |
|---|---|---|
| `PORT008-PROV-P001` — EMOS UART divisor overflow | Latent official MOS v3.0.2 source portability defect exposed by AgonDev | Corrected permanently in EMOS |
| `PORT008-PROV-P002` — EMOS `_port008_length` storage overlap | Created by the EMOS PORT-008 adapter | Exact adapter is prototype-only; width invariant is durable |
| `PORT008-PROV-P003` — EMOS PORT-008 clock cadence | Created by the EMOS adapter; regression from qualified predecessor timing | Exact adapter is prototype-only; timing rule is durable |
| `PORT008-PROV-P004` — P4 direction-enable omission | Created by the EDP PORT-008 adapter; regression from predecessor ownership | Current adapter is prototype-only; fail-safe ownership is durable |
| `PORT008-PROV-P005` — P4 pre-activation READY | Created by EDP boot integration | Current adapter is prototype-only; EMOS-owned activation is durable |
| `PORT008-PROV-P006` — P4 ZDI recovery refusal path | Created in a local temporary wrapper and corrected before its first commit | Diagnostic-only; never product EDP or EMOS |

1. Official MOS v3.0.2 at commit
   `8336409351ee5314e02801a7b72a4f1bb5282519` contains the uncast
   `CLOCK_DIVISOR_16 * baudRate` expressions. Stock ZDS builds produce the
   intended result, but AgonDev's 24-bit integer evaluation overflows before
   assignment to `UINT32`. EMOS inherited those expressions verbatim through
   candidate `59c31026e1229395d9a9ba44f71cda7b8e78b9f3`. EMOS commit
   `0e24b06abdb322fdb4e681a21242ccfebfc8ea65` explicitly widens both
   operands and adds linked guards. The fault is therefore upstream-present as
   a portability defect, with an alternative-toolchain manifestation rather
   than intended official-MOS behavior.
2. EMOS commit `08fec4851f8917215a83168ca4e73b54a7d3dcbd`
   introduced both ADL three-byte `BC` memory operations and a two-byte
   `_port008_length` object. Official MOS and the predecessor receiver contain
   no such object. Committed EMOS still contains the defect; the Author's
   current uncommitted EMOS work expands the object, rejects nonzero `BCU`, and
   adds a linked symbol-span check.
3. The same EMOS adapter commit emitted adjacent clock-high/clock-low writes
   and left CLOCK low after a record. The qualified predecessor sender instead
   establishes VALID with CLOCK high, changes data during setup, and emits
   falling then rising phases for every byte. Committed EMOS still contains the
   deviation; the current uncommitted EMOS work restores that cadence and
   strengthens its source and linked checks. Official MOS has no parallel
   sender.
4. EDP commit `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73`
   introduced `ForwardParallelStream` without GPIO15/GPIO21 direction-control
   ownership even though the predecessor had explicit fail-safe release and
   break-before-make selection. The Author's current uncommitted EDP work adds
   those controls. It does not resolve the separate boot-time activation
   defect recorded by the corrective action.
5. The temporary P4-to-ZDI recovery wrapper initially routed identity refusal
   through a helper that halted the eZ80. Official `agon-recovery` remains
   passive on failed identity and is not the origin. The wrapper separated
   passive refusal from post-halt failure before the source first entered Git
   in commit `ff1814733375476e6ab0af090c11a558fa5423c7`; consequently no
   committed faulty revision exists.

None of these classifications promotes the fixed-purpose PORT-008 adapters or
temporary recovery image into production. EMOS's mode coordinator and ordinary
Legacy route remain separate permanent code and were not the source of the
PORT-008 adapter, P4 readiness, or recovery-wrapper defects.

After Author disposition, the exact then-current dirty P4 and EMOS deltas were
preserved as historical binary patches under
`docs/tasks/PORT-008/forward-r01/evidence/`. Those post-run snapshots prevent
loss of the prototype bytes but do not repair F007, retroactively bind any run
to clean source, or promote either adapter. The intermediate EMOS state used by
the second failed run is not reconstructed by the later combined snapshot.

## Definite implementation and evidence findings

### `INTEGRITY-AUDIT-F001` — P4 frame suspension does not guarantee exclusion

- Severity: High
- Observed state: `P4DisplayController::executeFrameWork()` reads
  `suspension_depth_` and later, in a separate atomic operation, sets
  `executing_frame_work_`. `suspendBackgroundPrimitiveExecution()` increments
  the depth and waits only while execution is already marked active.
- Failure interleaving: The P4 frame task can read depth zero; the parser or
  synchronous drawing task can then increment the depth, observe execution
  false, and return; the frame task can then mark execution true and continue.
- Consequence: Canvas update exclusion, immediate primitive draining, sprite
  pointer replacement, sprite background reallocation, and quiescent snapshot
  composition can overlap the escaped frame. Outcomes include competing queue
  consumers, framebuffer corruption, and sprite-memory use-after-free.
- Evidence: `vdp/video/extender/display/p4_display_controller.cpp:183-200`,
  `:262-274`, and `:561-575`; `vdp/vendor/vdp-gl/src/canvas.cpp:95-108`;
  `vdp/vendor/vdp-gl/src/displaycontroller.cpp:638-683`; upstream
  `vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp:346-351,785-800`.
- Coverage gap: Existing Phase C and D suspension tests are sequential and do
  not force the two-task interleaving.
- Provenance: The same unsafe check/suspend/mark handshake exists in pinned
  upstream `vdp-gl` `VGABaseController`. Upstream uses `volatile` fields and
  therefore also has formal C++ data races. Commit
  `8aecb0e1a9efb671db2bff56143b11ab7b69aae5` introduced the separate P4
  atomic implementation; atomics removed flag data races but retained the
  exclusion gap. EDP additionally exposes an escaped frame to browser snapshot
  composition, which upstream does not have.
- Product boundary: `P4DisplayController` is intended EDP code. A future
  upstream `vdp-gl` fix cannot repair this independent implementation.
- Proposed owner: PORT-003.

### `INTEGRITY-AUDIT-F002` — Palette and Copper mutation race frame publication

- Severity: High
- Observed state: The retained parser task calls palette and Copper mutations
  directly through `agon_screen.h`. The P4 controller forwards those calls to
  `PaletteState` without exclusion, while the independent frame task reads the
  same state during browser snapshot composition.
- Consequence: Secondary-palette deletion and Copper-array replacement can free
  memory while the frame task dereferences it. This is a C++ data race with a
  plausible use-after-free, not merely a torn-colour presentation risk.
- Evidence: `vdp/video/agon_screen.h:70-108` and `:121-125`;
  `vdp/video/extender/display/p4_display_controller.cpp:233-253` and
  `:578-618`; `vdp/video/extender/display/palette_state.cpp:129-176` and
  `:205-268`; `vdp/video/video.ino:189-201`;
  `vdp/video/extender/display/p4_frame_service.cpp:112-123`; upstream
  `vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp:285-393` and
  `vdp/vendor/vdp-gl/src/dispdrivers/vga16controller.cpp:754-796`.
- Coverage gap: `docs/tasks/PORT-003/qualification-plan.md` requires concurrent
  palette/Copper/sprite mutation, but current controller and snapshot fixtures
  mutate only serially.
- Provenance: Pinned upstream `vdp-gl` mutates and frees palette signal maps and
  Copper-list nodes while the VGA scanline ISR can retain and dereference them;
  official `agon-vdp` calls those mutations from its parser without an
  exclusion boundary. Commit `35995320bbea21988b7c7407f05b5fd8d29ce3cf`
  introduced project-owned `PaletteState` with the same lifetime omission,
  and commit `39b45df18622d872eb729644a56b2f92297da6cf` added the browser snapshot
  reader. This is an upstream defect reimplemented and amplified locally, not
  retained byte-identical code.
- Product boundary: The P4 palette/Copper implementation and browser publisher
  are intended EDP surfaces and require a local correction regardless of any
  upstream report.
- Proposed owner: PORT-003.

### `INTEGRITY-AUDIT-F003` — Positive short TCP writes are accepted as complete WebSocket frames

- Severity: High
- Observed state: `WiredNetworkService::performQueuedSend()` calls
  `httpd_ws_send_frame_async()` once per EVF1 segment and marks the immutable
  snapshot lease sent whenever ESP-IDF returns `ESP_OK`.
- Upstream behavior: Pinned ESP-IDF sends the WebSocket header once and payload
  once, rejects only a negative return, and uses one BSD `send()` in the
  default session transport. A positive short stream write is legal.
- Consequence: Under congestion, the P4 network task can release and reuse a
  partially transmitted snapshot. The WebSocket header still declares the
  original length, so later bytes can be consumed as the previous frame's
  missing payload and corrupt the connection's framing.
- Evidence: `vdp/video/extender/network/wired_network_service.cpp:373-403`;
  pinned ESP-IDF `components/esp_http_server/src/httpd_ws.c:411-468` and
  `httpd_txrx.c:68-83,790-801`.
- Coverage gap: Current host tests manually complete small abstract views and
  do not compile or fault-inject the ESP-IDF HTTP adapter.
- Provenance: This is an upstream ESP-IDF v5.5.5 defect exposed by EDP, not an
  Agon VDP porting mistake. Commit
  `39b45df18622d872eb729644a56b2f92297da6cf` uses the documented
  `httpd_queue_work()` and `httpd_ws_send_frame_async()` pattern. The upstream
  API returns only `esp_err_t`, so EDP cannot recover the discarded positive
  byte count through that interface. The predecessor browser implementation
  also inherited this behavior.
- Product boundary: The wired browser service is intended EDP code. PORT-006
  needs a defensive adapter or pinned upstream correction; a framework upgrade
  must not be presumed to fix it without re-audit.
- Proposed owner: PORT-006, with PORT-003 browser-frame regression coverage.

### `INTEGRITY-AUDIT-F004` — Reachable audio and updater stubs corrupt retained VDU framing

- Severity: High
- Observed state: The P4 forward build binds physical ingress to the retained
  VDU parser while selecting empty audio and updater member-function adapters.
  The dispatcher has consumed only the command prefix when it calls either
  empty body.
- Consequence: Audio channel, subcommand, and variable arguments, or updater
  mode, unlock, length, image, and checksum bytes remain queued and are parsed
  as top-level VDU traffic. An unsupported command can therefore corrupt
  display state and the alignment of following valid commands.
- Evidence: `vdp/video/vdu_sys.h:208-210,341-346`;
  `vdp/video/extender/audio/unavailable_audio_adapter.hpp:19`;
  `vdp/video/extender/maintenance/unavailable_maintenance_adapter.hpp:9-12`;
  retained implementations in `vdp/video/vdu_audio.h:27-230` and
  `vdp/video/updater.h:16-40,169-181`;
  `vdp/pio/p4-forward-vdp-source-selection.json`.
- Contract conflict: PORT-003 Phase F permitted these stubs only while physical
  ingress was disconnected. PORT-008 replaces only that ingress binding.
- Distinction: Intel HEX and YMODEM selectors are already consumed before
  their no-op adapters and their omitted bulk streams use `DBGSerial`; they do
  not share this residual-VDU-byte defect.
- Provenance: Official `agon-vdp` consumes the complete valid audio and updater
  grammars. Commit `39b45df18622d872eb729644a56b2f92297da6cf`
  introduced empty adapters behind an explicit disconnected-ingress boundary;
  they were harmless while unreachable. PORT-008 commit
  `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73` connected physical ingress to
  the retained parser without changing the adapters and thereby created the
  defect.
- Product boundary: The audio stub is temporary. Maintenance support may be
  omitted from an EDP release, but a reachable handler must consume or safely
  reject the complete command. EMOS avoiding these commands can contain a
  prototype; it is not a parser repair.
- Proposed owners: PORT-003 for safe parser binding, PORT-004 for retained
  audio semantics, and PORT-008/SETUP-005 for reachable unsupported-command
  behavior.

### `INTEGRITY-AUDIT-F005` — External-clock loss can leave READY_N asserted indefinitely

- Severity: High
- Observed state: The forward receiver configures no PARLIO hardware timeout,
  arms DMA, asserts `READY_N`, and calls
  `parlio_rx_unit_wait_all_done(..., -1)`.
- Consequence: If external CLOCK stops or VALID cannot be sampled inactive, the
  receiver task never reaches the code that releases READY or direction
  enables. The P4 can retain bus ownership indefinitely and cannot execute its
  documented recovery path.
- Evidence: `vdp/video/extender/transport/forward_parallel_stream.cpp:121-132`
  and `:199-223`; pinned ESP-IDF
  `components/esp_driver_parlio/include/driver/parlio_rx.h:277-289`, which names
  stopped external clock as a timeout case and defines `-1` as forever.
- Provenance: PORT-008 commit
  `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73` introduced the infinite wait.
  ESP-IDF behaves according to its documented caller-selected timeout. The
  separate predecessor receiver at `agon-extender-legacy` commit
  `df54cf6a7a23cd40e98076856f68cff0559d1c77` already accepted a bounded
  timeout and released READY afterward, so the current behavior is a porting
  regression rather than inherited PARLIO behavior.
- Product boundary: The current r01 forward receiver is prototype code, not an
  accepted permanent EDP transport.
- Proposed owner: PORT-008.

### `INTEGRITY-AUDIT-F006` — Qualification validation accepts nonexistent authority and evidence

- Severity: High
- Observed state: The qualification model accepts arbitrary suffixes after a
  real task or ADR stem, omits validation of several owner/decision/blocker
  fields, never resolves evidence `ref` paths, and schema-checks without
  recomputing stored generated-input hashes.
- Demonstration: In-memory mutations using dangling task/decision identifiers,
  a false digest, and a `qualified` obligation supported only by
  `tests/runs/DOES-NOT-EXIST/manifest.yaml` returned no validation errors.
- Consequence: Review Gate 2 could promote a machine-readable qualified state
  whose owners, decision authority, inputs, or physical evidence do not exist.
- Evidence: `docs/qualification/scripts/qualification_model.py:229-238`,
  `:315-373`, and `:376-384`;
  `docs/qualification/tests/test_qualification_tools.py:55-68`.
- Present containment: QUAL-001 Review Gate 2 is paused and the current
  three-mode candidate is already superseded.
- Provenance: The validator and its tests were introduced locally in commit
  `75ab4fe35b58fd936a8f9bab6f060389a774635b`. `jsonschema` correctly
  enforces the schema it is given; repository authority resolution, evidence
  existence, and digest freshness are application semantics omitted by the
  project validator. No upstream product or validation-library defect is
  involved.
- Proposed owner: QUAL-001.

### `INTEGRITY-AUDIT-F007` — Firmware staging does not bind build products to the recorded commit

- Severity: High
- Observed state: The Phase F stager verifies current clean `HEAD`, then accepts
  a caller-supplied pre-existing build directory and closure. The closure binds
  firmware hashes, build metadata, translation-unit names, and flags, but not
  object bytes to current source bytes or the source commit.
- Consequence: Products built at commit A can be staged while clean commit B is
  checked out, and the manifest records B as provenance when embedded version
  fields have not changed. Physical deployment and qualification evidence can
  therefore be falsely attributed despite the tool's fail-closed claim.
- Evidence: `docs/tasks/PORT-003/phase-f/scripts/stage-identified-build.py:120-126`,
  `:163-188`, and `:270-284`;
  `docs/tasks/PORT-003/phase-f/scripts/validate-phase-f-build.py:207-237` and
  `:381-426`; PORT-008's `stage-forward-build.py:53-73` delegates unchanged.
- Provenance: The Phase F stager and validator were created locally in commit
  `39b45df18622d872eb729644a56b2f92297da6cf`; commit
  `43cffd181058fa264cb9f9f78bc36eee17773746` changed identity handling but
  retained the gap. PORT-008 commit
  `b6907ea39fad8fc6b0c7e2d029d01ccef36caa40` delegates to it. PlatformIO's
  reusable build directory is ordinary upstream behavior; the project stager's
  inference that clean staging-time HEAD proves older object provenance is the
  defect.
- Proposed owners: PORT-003 and PORT-008.

### `INTEGRITY-AUDIT-F008` — Frozen r02 harness integrity and projections disagree

- Severity: High for configuration control; low demonstrated immediate
  electrical risk
- Observed state: `hardware/designs/light2-harness-r02/profile.yaml` records
  schematic SHA-256 `39af5b2d...`, while the committed schematic is
  `f866660c...`. The checked `schematic.svg` is also stale.
- Consequence: `light2-harness-r02` is not a valid frozen qualification input.
  A future construction or run cannot cite the profile as proving the exact
  maintained schematic bytes.
- Evidence: `hardware/designs/light2-harness-r02/profile.yaml:9-18` and the
  failing version-record and schematic-view validators.
- Electrical boundary: KiCad topology/XML and BOM checks pass; inspection found
  label-coordinate and project-name changes rather than a demonstrated
  connectivity change. No tracked run cites r02.
- Provenance: This is local artifact-control drift, not a runtime code defect.
  Commit `ff1814733375476e6ab0af090c11a558fa5423c7` changed the schematic
  without refreshing the profile digest or SVG. The version validator and
  KiCad are behaving correctly.
- Proposed owner: HW-001, with version-record reconciliation consumed by
  PORT-008 and QUAL-002.

### `INTEGRITY-AUDIT-F009` — Accepted mode-lifecycle decisions remain outside normative authority

- Severity: High
- Observed state: SETUP-005-D002 records accepted transactional activation,
  Legacy-hub transitions, controlled restart, reset invalidation, discovery,
  recovery, and EMOS ownership. ADR-0014 remains last amended on 2026-08-23 and
  omits much of this contract; `docs/architecture.md` likewise omits the
  accepted transition/reset rules.
- Consequence: Downstream tasks can read an accepted decision as a satisfied
  gate while the normative architecture still states an incomplete contract.
- Policy conflict: `AGENTS.md` requires accepted material architecture to be
  promoted immediately. REMED-001 Work 2.m currently defers that promotion,
  and SETUP-005's own gate prohibits implementation before it occurs.
- Evidence: `docs/tasks/SETUP-005.md:72-110,338-345`;
  `docs/decisions/ADR-0014-edu-operating-modes-and-service-architecture.md`;
  `docs/architecture.md:243-326`; `docs/tasks/REMED-001.md:224-234`.
- Provenance: The authority split was created locally in commit
  `75ab4fe35b58fd936a8f9bab6f060389a774635b`, which accepted expanded
  task-local decisions while deferring complete normative promotion. It is a
  project documentation-governance defect, not an official MOS or VDP defect.
- Proposed owners: SETUP-005 and REMED-001; accepted content belongs in
  ADR-0014 and `docs/architecture.md`.

### `INTEGRITY-AUDIT-F010` — REMOTE-001 and LINK-001 conflict on direct-link ownership

- Severity: High
- Observed state: REMOTE-001 assigns link research and selection to LINK-001,
  then makes link research, endpoint implementation, new wiring, and physical
  qualification REMOTE required work. LINK-001 prohibits protocol, firmware,
  pin, circuit, or product commitment without separate review and requires
  implementation to be split into approved tasks.
- Consequence: Following REMOTE literally can bypass LINK's research boundary
  and Author gate or create two competing implementation owners.
- Evidence: `docs/tasks/REMOTE-001.md:51-57,67-71,100-118,141-157` and
  `docs/tasks/LINK-001.md:104-124`.
- Provenance: Commit `bfd2bb08551772f0375eca825b07b67b491d8de1`
  introduced both sides of this local task-ownership contradiction. No
  upstream code behavior is involved.
- Proposed owners: REMOTE-001 for use cases, sessions, and remote semantics;
  LINK-001 for research only; separately approved tasks if implementation is
  accepted.

### `INTEGRITY-AUDIT-F011` — UBSan reports can produce passing qualification evidence

- Severity: Medium-high
- Observed state: Phase B, C, and D compile host binaries with ASan and UBSan,
  set only `ASAN_OPTIONS`, accept zero exit status, and ignore successful-run
  stderr. Default UBSan recovery can emit `runtime error:` and return zero.
- Demonstration: A bounded synthetic UBSan probe emitted a signed-overflow
  runtime error, printed its expected pass output, and exited zero under the
  same environment pattern.
- Consequence: The runners can describe a result as ASan/UBSan qualification
  even when UBSan reported undefined behavior.
- Evidence: `docs/tasks/PORT-003/phase-b/scripts/run-host-fixtures.py:25-35`
  and `:80-99`; Phase C `run-host-frame-tests.py:85-105,120-176`; Phase D
  `run-host-presentation-tests.py:311-320`; Phase E's strict environment at
  `run-host-mode-tests.py:90-105` applies only to its own binary.
- Provenance: The affected Phase B, C, and D runners were introduced locally
  by commits `89d66c406eb401b33fed8cdc4a5d54aae33a201b`,
  `8aecb0e1a9efb671db2bff56143b11ab7b69aae5`, and
  `35995320bbea21988b7c7407f05b5fd8d29ce3cf`. UBSan's default
  recover-and-report behavior is intentional; the project runners fail to
  select a strict mode or treat successful-run diagnostics as failures. This
  is local test-oracle misuse, not a compiler-runtime defect.
- Proposed owner: PORT-003.

### `INTEGRITY-AUDIT-F012` — HTTP stop failures discard the live server handle

- Severity: High
- Observed state: `WiredNetworkService::stopHttp()` atomically replaces the
  HTTP server handle with null before calling `httpd_stop()`. Both URI-
  registration rollback paths likewise clear the handle, ignore the stop
  result, and return failure.
- Consequence: If ESP-IDF cannot send its shutdown control message, the server
  remains active but EDP cannot retry, destroy, or account for it. A later
  start can create a second instance. The live server also retains callbacks
  and user contexts pointing at `WiredNetworkService`; destruction after a
  failed rollback or stop can therefore produce a stale-pointer use-after-free.
- Evidence: `vdp/video/extender/network/wired_network_service.cpp:232-269` and
  pinned ESP-IDF `components/esp_http_server/src/httpd_main.c:556-585`.
- Coverage gap: Host tests exercise the abstract network core, not ESP-IDF
  adapter failure injection.
- Provenance: ESP-IDF v5.5.5 legitimately can return `ESP_FAIL` before deleting
  a valid server, while its public header lists only success and null-handle
  failure. That documentation inconsistency is upstream. Commit
  `39b45df18622d872eb729644a56b2f92297da6cf` nevertheless introduced EDP's
  explicit result check followed by unconditional ownership loss. The live-
  handle and callback-lifetime defect is therefore project-created even though
  an upstream failure path triggers it.
- Product boundary: The wired service is intended EDP code; all three teardown
  paths require one ownership and failure contract.
- Proposed owner: PORT-006.

### `INTEGRITY-AUDIT-F013` — Failed forward startup poisons retry state and leaks resources

- Severity: Medium
- Observed state: `ForwardParallelStream::begin()` allocates `stream_buffer_`
  before hardware setup and uses non-null `stream_buffer_` as the only
  already-started sentinel. Later delimiter, unit, callback, enable, DMA,
  direction, or task failures return without deleting partial resources.
- Consequence: A second `begin()` returns true even if no receiver task exists,
  concealing a failed transport and leaking partially created resources.
- Present boundary: Current boot abandons startup after the first failure, but
  PORT-008 explicitly requires retry and recovery behavior.
- Evidence: `vdp/video/extender/transport/forward_parallel_stream.cpp:134-178`.
- Provenance: PORT-008 commit
  `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73` introduced the sentinel and
  partial-initialization exits. ESP-IDF and FreeRTOS provide the necessary
  disable/delete primitives. The predecessor receiver at
  `agon-extender-legacy` commit
  `df54cf6a7a23cd40e98076856f68cff0559d1c77` already unwound its PARLIO unit,
  delimiter, DMA storage, and READY state, so this is a direct porting
  regression.
- Product boundary: The current r01 receiver is prototype-only. Any promoted
  transport needs transactional initialization and deterministic retry tests.
- Proposed owner: PORT-008.

### `INTEGRITY-AUDIT-F014` — PORT-008 capture analyzers can report invalid evidence as usable

- Severity: Medium
- Observed state A: The current clock-discriminator script does not invalidate
  all procedure-required bad probe states, writes a bounded interpretation that
  is hard-coded to no D4 edges, no D5 edges, and equal clock counts, and exits
  zero even when its result is `invalid`.
- Demonstration A: The preserved invalid run printed `INVALID` and returned
  zero.
- Observed state B: The forward-capture analyzer checks a VALID window, four
  falling CLOCK edges, final READY release, and direction overlap, but not
  released-idle start/end, initial READY, READY-to-VALID ordering, data values,
  or setup/hold.
- Consequence: Automation can select the wrong diagnostic branch or pass a
  capture that does not prove the procedure's electrical claim.
- Evidence: `docs/tasks/PORT-008/forward-r01/scripts/analyze-clock-discriminator.py:289-333`;
  `analyze-forward-capture.py:147-194`;
  `docs/procedures/port-008-forward-qualification-r01.md:146-149`.
- Snapshot note: At the reviewed snapshot, the clock discriminator and
  associated procedure were uncommitted review inputs, not accepted
  authorities. The exact analyzer bytes used for the failed/invalid runs are
  now preserved as task-run audit copies; the maintained task-local scripts
  carry visible F014 warnings and remain unavailable for qualification.
- Provenance: At the reviewed snapshot, both analyzers were untracked
  workspace-local files with no Git introduction history and no same-named
  upstream Agon implementation. Their
  reviewed SHA-256 values are `a238287f468ca081c88aff26f6b9d1a060e45d73f8419e18b222bfc039b8e6a5`
  and `64d8d9f08eff0dca2bb27e48ab24b61c9a96ae225c37b7d38d4935da27cbaf7e`.
  Capture libraries can report sampled values but cannot establish the omitted
  procedure preconditions; the false-success and overclaim are local analyzer
  semantics, not a capture-tool defect.
- Proposed owner: PORT-008.

### `INTEGRITY-AUDIT-F015` — PORT-008 baseline and corrected candidate select different MOS build sources

- Severity: Medium
- Observed state: `docs/versions/baselines/port-008-forward-r01.yaml` selects
  `mos-agondev` commit `5079d4c...`; the corrected candidate and current
  procedure select `29cd336...`.
- Consequence: The named baseline does not identify the source used by the
  corrected candidate package and cannot be relied upon as its complete
  dependency authority.
- Evidence: baseline lines 36-42;
  `docs/tasks/PORT-008/forward-r01/candidate.yaml:16-23`; procedure lines 52-57.
- Provenance: Commit `acf9ded5c7936fe61c6377f367ac8c96c3984b78` changed
  the candidate and procedure but left the earlier baseline unchanged. This is
  local version-record drift; it does not establish a defect in EMOS or
  `mos-agondev` code.
- Proposed owner: PORT-008 under the versioning policy.

### `INTEGRITY-AUDIT-F016` — QUAL-002 does not expose the active remediation freeze

- Severity: Medium
- Observed state: QUAL-002 still says its plan is approved. Its local
  dependencies cite QUAL-001, PORT-008, and SETUP-005-D002 but not REMED-001
  Work 3.e, corrected four-mode gates, or release of the remediation freeze.
- Consequence: Once a controlled transport candidate exists, a reader can
  mistake QUAL-002 for locally startable despite the repository-wide
  prohibition on mode-dependent physical qualification.
- Evidence: `docs/tasks/QUAL-002.md:3-7,140-152` and
  `docs/tasks/REMED-001.md:37-65,486-488`.
- Provenance: Commit `75ab4fe35b58fd936a8f9bab6f060389a774635b` added the
  remediation freeze without updating QUAL-002's older local gate. This is a
  local task-status defect, not code or upstream behavior.
- Proposed owners: QUAL-002 and REMED-001.

## Preimplementation design findings

### `INTEGRITY-AUDIT-F017` — PORT-003 Gate G has no reviewable contract

- Severity: Medium
- Observed state: PORT-003 names Gate G as its remaining end-to-end closure and
  requires detailed phases and acceptance fixtures before coding, but the task
  ends after Phase F without a Gate G plan, fixtures, stop conditions, or
  acceptance criteria.
- Present containment: PORT-008 Gate 2 and applicable QUAL-002 work are not
  complete, so Gate G is not currently executable.
- Provenance: Gate G was named locally, and commit
  `329f669731d520954238dff717dba3b55ae41bbc` made it the remaining phase
  without adding its required plan. This is local preimplementation
  incompleteness, not an upstream or EMOS defect.
- Proposed owner: PORT-003 after its prerequisites are accepted.

### `INTEGRITY-AUDIT-F018` — Restart-mediated beta transition lacks a reset carrier and baseline owner

- Severity: Medium
- Observed state: The accepted lifecycle uses a controlled restart for route
  changes and permits loss of eZ80 RAM, while its reset table invalidates
  pending work and returns through Legacy. Carrying a target across an eZ80/MOS
  reset requires retained state that beta does not promise.
- Gap: No contract names which processor restarts, where the target survives,
  which actor reissues or consumes it, or when EMOS commits the target mode.
- Consequence: MODE-001 requires a working disruptive baseline before replacing
  it, but owns only the later state-preserving design; MODE-002 leaves
  cross-boot behavior conditional.
- Evidence: `docs/tasks/REMED-001/mode-lifecycle-analysis.md:188-242` and
  `:356-383`; `docs/tasks/MODE-001.md:74-83`;
  `docs/tasks/MODE-002.md:16-27`.
- Provenance: The lifecycle model and the unresolved carrier were introduced
  together locally in commit `75ab4fe35b58fd936a8f9bab6f060389a774635b`.
  This is a design gap, not current code or a stock-MOS defect. If accepted,
  the target request, retained selection, commit, and Legacy fallback are
  EMOS-owned implementation under the cross-project Extender contract.
- Proposed owners: SETUP-005/REMED-001 for the contract and a separately named
  implementation/qualification task if accepted.

### `INTEGRITY-AUDIT-F019` — Remote keyboard conversion can erase authorization provenance

- Severity: High design blocker
- Observed state: REMOTE-001 makes EMOS the sole privileged authorization owner
  but permits onboard-VDP firmware to translate remote events into ordinary
  stock keyboard packets.
- Consequence: Once converted, EMOS cannot distinguish authenticated remote
  input from physical typing. Remote keystrokes can reach shell, reset, flash,
  or mode operations outside a structured per-operation authorization path.
- Required disposition: Preserve remote-origin provenance through an
  EMOS-authorized service or explicitly constrain the authority of remote
  terminal input before choosing an endpoint design.
- Evidence: `docs/tasks/REMOTE-001.md:37-50,76-90,120-137`.
- Provenance: REMOTE-001 commit
  `bfd2bb08551772f0375eca825b07b67b491d8de1` introduced this local design
  conflict. Ordinary upstream keyboard packets lacking authenticated remote
  provenance are behaving normally; choosing that lossy representation for
  privileged remote intent would be the project defect.
- Proposed owner: REMOTE-001, with PORT-006 authentication/exposure and EMOS
  authorization as dependencies.

### `INTEGRITY-AUDIT-F020` — DIAG-001 lacks confidentiality and retention policy for memory evidence

- Severity: Medium design blocker
- Observed state: DIAG-001 requires durable register, stack, task, panic, and
  backtrace capture plus export. It bounds arbitrary-memory extent but does not
  define classification, redaction, authenticated retrieval, retention, or
  erase behavior.
- Consequence: Even a bounded stack can contain credentials, session tokens,
  private program data, or update material that later reaches flash, browser,
  network, or a bug report.
- Provenance: DIAG-001 and this omission were introduced locally in commit
  `75ab4fe35b58fd936a8f9bab6f060389a774635b`. Native ESP-IDF panic or
  coredump capture including memory is expected functionality, not an upstream
  defect. Policy ownership is cross-project; eZ80 capture hooks would be
  EMOS-owned while P4 capture/export is EDP-owned.
- Proposed owner: DIAG-001 before crash-context capture or export is
  implemented.

### `INTEGRITY-AUDIT-F021` — Promoted construction and board-resource authority remains ambiguous

- Severity: Low
- Observed state: SETUP-006 still describes r02 construction mapping as open
  and retains a stop condition saying electrical design/connectivity are not
  established. HW-001 and the durable assembly README assign the r02 assembly
  map to HW-001. PORT-007 does not cite the existing fixed-function SD1 pin
  audit. The draft hardware-object registry also mixes predecessor-specific
  channel descriptions into revision-independent role objects without
  applicability metadata.
- Consequence: Later construction, storage, or ERP work can consume a historical
  task-local statement as current authority or rederive accepted pin facts
  inconsistently.
- Evidence: `docs/tasks/SETUP-006.md:3-8,462-469`;
  `docs/tasks/HW-001.md:304-319`;
  `hardware/assemblies/light2-extender-solderless-assembly-r02/README.md:18-27`;
  `docs/tasks/PORT-007.md:19-30,58-71`;
  `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/electrical-requirements.md:122-131`;
  `hardware/objects/objects.yaml:253-277,444-465`.
- Provenance: This combines several local promotion and applicability
  omissions; no official schematic fact, component model, or EMOS code is
  alleged defective.
- Proposed owners: HW-001 for current construction mapping, SETUP-006 for
  retained provenance only, PORT-007 for SD1 consumption, and the future
  hardware-object promotion owner for applicability metadata.

## Prospective risks, not current defects

### `INTEGRITY-AUDIT-R001` — PARLIO callback publication uses volatile rather than an explicit synchronization contract

- `ForwardParallelStream::ReceiveState::received` is volatile, written by the
  PARLIO callback and read by the receiver task. The driver completion primitive
  may provide the required platform ordering, but ISO C++ `volatile` does not.
- The code was created locally in commit
  `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73`. No ESP-IDF defect is proved;
  this remains a question about EDP's application-owned publication contract.
- PORT-008 should confirm the ESP-IDF synchronization guarantee or use an
  explicit lock-free atomic/driver-owned result before claiming portability.

### `INTEGRITY-AUDIT-R002` — Reusing retained input coalescing may lose injected key transitions

- PORT-005 is correctly not started. If its injection design reuses
  `thread_safe_variant_deque`, note that the queue coalesces by event type while
  later packet generation reads mutable global VDP state.
- That queue behavior is byte-identical to official `agon-vdp` and is an
  intentional state-notification behavior, not a proved upstream defect. A
  defect would be created only if EDP reused it for ordered, distinct injected
  key transitions.
- PORT-005 fixtures should explicitly reject collapsed or reordered key-down,
  key-up, modifier, and repeat sequences before selecting that seam.

### `INTEGRITY-AUDIT-R003` — Remote exposure requires more than the accepted trusted-LAN browser boundary

- PORT-006's current no-authentication/no-TLS trusted-bench exposure is an
  accepted Phase F exclusion, not a present defect.
- ESP-IDF not supplying the project's authentication, Origin, authorization,
  or revocation policy automatically is not an upstream defect.
- Before REMOTE-001 permits input or commands, authentication, Origin policy,
  cross-site WebSocket behavior, privileged-service exposure, and session
  revocation require an accepted contract.

## Already recorded blockers and non-findings

1. P4 startup currently selects the forward direction and admits READY before
   an EMOS session or committed-mode transition. This violates Legacy absence
   but is already recorded in
   `CA-2026-09-01-001-port008-preactivation-ready`; it is not assigned a second
   finding ID here. The current uncommitted forward-build validator also
   requires the prohibited startup order and must follow that corrective
   action's disposition.
2. HW-001 already records the r02 eZ80-only-reset stale-enable hazard, imperfect
   Legacy electrical absence, floating-input concerns, unqualified target-speed
   UART, and unqualified power/reset behavior. Passing topology checks do not
   resolve those gates.
3. REMED-001 already records that the three-mode, 633-tuple qualification
   candidate, fixed renderer assumptions, and fixed-count tests are superseded.
   The present passing qualification tests prove reproducibility of that
   candidate, not architectural validity.
4. PORT-004 and PORT-005 are not started. No missing implementation was treated
   as a defect; only their currently reachable integration boundary or
   prospective design risks are recorded.
5. UPSTREAM-001's preserved commits exist, described diff spans match, and the
   current vendored source remains pristine relative to the named parent. No
   new defect was found in that task's existing lifecycle patch set. F001 and
   F002 are separate upstream vdp-gl findings and are not silently added to
   UPSTREAM-001 pending Author disposition.
6. Intel HEX/YMODEM feedback semantics, no-authentication browser exposure, and
   other explicitly accepted exclusions remain open decisions rather than
   accidental compatibility claims.

## Coverage register

| Area | State | Result |
|---|---|---|
| Open TODO and task-detail correspondence | Reviewed | All 18 open TODO IDs have task records and valid local links. |
| Display, frame service, palette, Copper, sprites, and snapshots | Reviewed | F001 and F002; existing fixtures pass but omit decisive concurrency. |
| Retained parser, deferred audio, maintenance adapters, and source selection | Reviewed | F004; HEX/YMODEM distinction retained. |
| Browser/network frame provider and ESP-IDF HTTP adapter | Reviewed | F003 and F012; abstract host tests pass. |
| Forward-parallel receiver and current diagnostic tooling | Reviewed | F005, F013, F014, and R001; preactivation defect remains under the existing corrective action. |
| Build closure, staging, version records, and r02 artifacts | Reviewed | F007, F008, and F015. |
| Qualification model, generators, reviewed data, and tests | Reviewed | F006 and F011; superseded candidate regenerates deterministically. |
| Operating-mode architecture, remediation, and system qualification | Reviewed | F009, F016, F018, and F021. |
| Audio, input, storage, diagnostics, remote interaction, and direct link tasks | Reviewed | F010, F019, F020, F021, R002, and R003; unstarted code was not presumed. |
| Upstream lifecycle candidate | Reviewed | No new finding. |

## Validation record

1. Ninety-six Python unit tests passed across dependency, qualification,
   hardware, and PORT-003 Phase A--F suites.
2. Phase B host fixtures passed. Phase C passed 12 frame fixtures. Phase D
   passed 19 presentation fixtures and three fixed harnesses.
3. PORT-006 network host tests passed, and browser tests passed 78 Firefox
   checks.
4. Dependency validation, deterministic qualification regeneration of 17
   generated files, hardware-object validation of 41 objects, HW electrical
   model tests, BOM generation for 41 fitted components, and non-generated
   Markdown local-link validation passed.
5. `scripts/validate-version-records.py` failed on the r02 schematic hash.
6. The r02 schematic-view check completed topology comparison and then failed
   because `schematic.svg` is stale.
7. PORT-008's forward-build closure validator passed against the existing
   build: 24 translation units, five embedded assets, 18 required symbols,
   C++17, and selected exclusions. That closure check does not execute the
   runtime failures above.
8. The invalid clock-discriminator run printed `INVALID` and exited zero.
9. `git diff --check` passed. The audit made no physical change and preserved
   the Author's pre-existing worktree.
10. The provenance extension resolved every cited local, EMOS, MOS, and legacy
    introduction commit and reconfirmed the pinned VDP, MOS, and ESP-IDF
    identities. Relevant vendored vdp-gl files matched the official dependency
    used by the pinned Agon VDP checkout.
11. The local Markdown-link resolver passed for all four amended durable
    documents, and a targeted trailing-whitespace scan passed. No product test
    was rerun because the extension changed audit documentation only.

## Disposition order recommended for Author review

This order is advisory and does not authorize work:

1. Contain runtime corruption and hardware-ownership risks: F001--F005, F012,
   plus the existing preactivation corrective action.
2. Repair evidence trust before accepting more qualification: F006--F008,
   F011, F014, and F015.
3. Reconcile accepted architecture and task ownership: F009, F010, F016, and
   F018.
4. Resolve the remaining prototype lifecycle defect: F013.
5. Complete future implementation gates: F017 and F019--F021, then retain
   R001--R003 in their named task designs.

## Audit conclusion

The repository's existing success-path validation is substantial and mostly
reproducible, but it does not presently justify advancing the forward P4
candidate or PORT-003 Gate G. Definite task-concurrency, parser-framing,
WebSocket transmission, clock-recovery, qualification-reference, provenance,
and configuration-control defects remain. Accepted operating-mode decisions
and cross-task ownership also remain inconsistent with their normative or
local authorities.

The audit does not require one new monolithic remediation owner. Every finding
can be dispositioned into an existing open task, ADR, or normative authority.
Keeping this record under `docs/decisions/` preserves the reviewed snapshot and
stable finding IDs without making it a competing task list or architecture
specification.

The provenance extension changes attribution, not containment: upstream
presence does not authorize retaining F001--F003, and project origin does not
promote any prototype adapter. Permanent EDP display and network surfaces need
local corrections; the exact PORT-008 sender/receiver implementations remain
prototype-only; and the committed EMOS UART-width fix is the sole reviewed
permanent EMOS correction in the historical provenance set.
