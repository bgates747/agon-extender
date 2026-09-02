# AUDIT-2026-09-01-001 — Open-task and implementation integrity

- Status: Complete — findings dispositioned or explicitly deferred
- Date: 2026-09-01
- Trigger: Author-requested adversarial review of every open task and related code
- Scope: All 18 open tasks and their directly related architecture,
  implementation, validators, procedures, evidence, and version records
- Owning task: AUDIT-003
- Provenance extension: 2026-09-01
- Work 2.a extension: 2026-09-01

## Purpose and authority boundary

This audit records a repository-wide adversarial review of the work indexed by
`TODO.md`. It looks for unsafe interleavings, false-positive qualification,
broken provenance, stale authorities, unreachable recovery, contradictory task
ownership, and design gaps that ordinary success-path validation may not
expose.

The audit identifies observed defects and proposes disposition owners. It does
not amend architecture, accept a mechanism, modify a task's scope, authorize
implementation, promote evidence, qualify hardware, or permit a physical run.
At review time each finding was deferred pending Author disposition. Subsequent
accepted work or explicit deferral is recorded in the named task, applicable
ADR or normative architecture, and current development log.

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

At audit creation every finding below was deferred pending Author disposition.
Later dispositions are recorded beside affected findings and in REMED-002;
“proposed owner” never silently adds work to a task.

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
| F001 | Present in upstream `vdp-gl`; independently reimplemented and extended by EDP | Recorded; no local correction without deterministic D012 trigger evidence |
| F002 | Present in upstream `vdp-gl`; independently reimplemented with plausible EDP amplification | Recorded; no local correction without deterministic D012 trigger evidence |
| F022 | Present in official VDP v2.16.0 together with pinned vdp-gl's raw queued operands | Recorded upstream behavior; correction and regression design deferred under D012 |
| F003 | Present in upstream ESP-IDF; exposed by EDP's documented API use | Wired EDP browser service is product-directed |
| F004 | Absent upstream; created by making disconnected-only EDP stubs reachable | Audio stub is temporary; an omitted updater must still be framing-safe |
| F005 | Created during PORT-008 porting; upstream PARLIO behaves as documented | Rejected predecessor only; replacement now distinguishes indefinite idle from a bounded active-record stall after P017, target-runtime proof open |
| F006 | Created in the project qualification validator | Durable project tooling, not product firmware |
| F007 | Created in the project build stager | Durable project tooling, not product firmware |
| F011 | Created in project test runners by misusing intentional UBSan recovery | Qualification tooling, not product firmware |
| F012 | EDP loses ownership on a legitimate but incompletely documented ESP-IDF failure | Wired EDP browser service is product-directed |
| F013 | Created during PORT-008 porting; regression from the predecessor receiver | Rejected predecessor only; transactional replacement and qualification-owner cleanup were corrected through P020/P021, target-runtime proof open |
| F014 | Created in uncommitted PORT-008 analyzers | Prototype evidence tooling only |
| Existing pre-activation corrective action | Created by P4 boot integration; absent from EMOS and official upstream | Rejected predecessor retired; production activation correction open |

For the thirteen rows above, F001--F003 and F022 are source-proved upstream
defects with local EDP exposure or reimplementation. That provenance does not
prove a distinct Extender runtime manifestation for F001, F002, or F022. F004,
F005, F012, F013, and the
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

### PORT-008 provenance observations

The main matrix covers defects newly established by this audit plus the open
pre-activation corrective action. PORT-008 recorded P001 through P006 during
its physical investigations, found P007 during the later production-
equivalence source trace, found P008 while building the replacement EMOS
objects, found P009 through P014 during adversarial production factoring and
dispatcher/UART integration, and found P015/P016 in the final coordinator
transaction review. The later P4 adversarial pass found P017 through P021 in
the new target/data-plane, retained-Stream, qualification-owner, and boot
integration. The Work 2.e provenance audit then found P022 in generic
`mos-agondev` root orchestration, P023 in the P4 qualification build boundary,
P024 in the EMOS profile-flag boundary, P025 in the P4 build-identity boundary,
and P026 in the EMOS fixed-composition identity boundary. The same pass then
found P027 in the P4 qualification-composition identity boundary, P028 in the
EMOS toolchain wrapper, P029/P030 in the new generic and P4 actual-step
recorders, and P031 in the new product comparison gate. They are included
here so the upstream/local and permanent/prototype boundaries are complete
rather than silently excluding code that had already been corrected,
contained, or found discrepant.
The first real rehearsal subsequently exposed P032 in the active P4 recorder
installation boundary.

| Recorded defect | Provenance classification | Maintained-surface status |
|---|---|---|
| `PORT008-PROV-P001` — EMOS UART divisor overflow | Latent official MOS v3.0.2 source portability defect exposed by AgonDev | Corrected permanently in EMOS |
| `PORT008-PROV-P002` — EMOS `_port008_length` storage overlap | Created by the EMOS PORT-008 adapter | Exact adapter is retired from production closure; replacement preserves exact-width bounded counts and chunking |
| `PORT008-PROV-P003` — EMOS PORT-008 clock cadence | Created by the EMOS adapter; regression from qualified predecessor timing | Exact adapter is retired from production closure; replacement preserves the durable cadence rule |
| `PORT008-PROV-P004` — P4 direction-enable omission | Created by the EDP PORT-008 adapter; regression from predecessor ownership | Replacement target owner implements fail-safe direction and teardown; predecessor remains prototype evidence |
| `PORT008-PROV-P005` — P4 pre-activation READY | Created by EDP boot integration | Fixed data-plane composition gates readiness on its supplied active epoch; production activation and corrective action remain open |
| `PORT008-PROV-P006` — P4 ZDI recovery refusal path | Created in a local temporary wrapper and corrected before its first commit | Diagnostic-only; never product EDP or EMOS |
| `PORT008-PROV-P007` — bounded RST 18 return-value mismatch | Present between official Agon documentation and official MOS source; not created by Extender | Record and defer; do not silently change de-facto success behavior while factoring the production parallel engine |
| `PORT008-PROV-P008` — EMOS selected-worktree forwarding omission | Created in the EMOS repository build wrapper; generic `mos-agondev` honored the input it actually received | Corrected in durable EMOS build tooling with regression coverage |
| `PORT008-PROV-P009` — epoch commit erased a concurrent writer fault | Created in the project-owned EMOS parallel epoch implementation; no official-MOS counterpart exists | Corrected with atomic begin/commit and contention regression |
| `PORT008-PROV-P010` — epoch commit overwrote a concurrent leave | Created in the project-owned EMOS parallel epoch implementation; no official-MOS counterpart exists | Corrected by invalidating in-progress entry and failing commit closed |
| `PORT008-PROV-P011` — rejected writer unlocked before publishing failure | Created in the project-owned EMOS lease/writer implementation; no official-MOS counterpart exists | Corrected with failure-before-unlock ordering and regression |
| `PORT008-PROV-P012` — linked verifier claim overstatement | Created in project EMOS evidence tooling; official MOS has no parallel linked verifier | Corrected by bounding success claims, checking exact fixed-coordinator call edges and bridge ABI shapes, and retaining false-green tests |
| `PORT008-PROV-P013` — UART1 open raced a parallel Port C epoch | Created when EMOS added a second Port C owner without serializing the inherited UART1 API; stock MOS has no competing parallel epoch | Corrected with one shared atomic reservation held across UART1 transition publication |
| `PORT008-PROV-P014` — UART1 guard was initially profile-optional | Created in EMOS build/profile integration; the controlling macro and parallel owner have no upstream counterpart | Corrected by making the guard unconditional and adding native-ZDS/AgonDev parity checks |
| `PORT008-PROV-P015` — failed adapter recovery could be discarded or followed by an ownership switch | Created in the project-owned EMOS mode coordinator; official MOS has no Extender adapter lifecycle | Corrected by propagating recovery failure, retaining old ownership, and retrying retained cleanup on a repeated Legacy request |
| `PORT008-PROV-P016` — private parallel statuses escaped into the public command-error domain | Created when EMOS integration exposed project-private lifecycle statuses to a public MOS/FatFS error consumer; official `mos_error()` is correct for its supported domain | Corrected by retaining the raw diagnostic internally and mapping the public result to `EMOS_UNAVAILABLE` |
| `PORT008-PROV-P017` — an idle target receive period was treated as a fatal record timeout | Created in the project-owned P4 target adapter; upstream PARLIO supplies primitives but no Extender record/READY policy | Corrected by keeping one armed advertised transaction through idle and starting the fatal deadline only after active `VALID_N` |
| `PORT008-PROV-P018` — a fault between `available()` and `read()` could inject synthetic `0xFF` | Created by the project `ExtenderVdpStream` adapter violating the retained upstream parser's advertised-read expectation; the parser's cached-read behavior is inherited | Corrected with a one-byte advertised-read permit and fail-closed gating of every later byte |
| `PORT008-PROV-P019` — fault publication raced record admission and success reporting | Created in the project-owned P4 data-plane composition; no upstream equivalent exists | Corrected with one nonblocking sequentially consistent admission edge, quarantine of a pre-fault winner, and post-commit fault/cancel/lease checks |
| `PORT008-PROV-P020` — the qualification owner revoked its lease after an unverified cleanup attempt | Created in the project non-release qualification composition; no upstream equivalent exists | Corrected by retaining ownership and retrying idempotent teardown until success before lease revocation |
| `PORT008-PROV-P021` — retained process-task creation failure continued into a false-live boot | Created in the project P4 boot integration; official VDP has no corresponding Extender qualification branch | Corrected by requesting transport stop and returning before boot-screen or network startup |
| `PORT008-PROV-P022` — selected EMOS source/prepared-tree preflight authenticated the default stock pair | Created in generic project `mos-agondev` root orchestration; official MOS has no prepared-copy or product-profile build boundary | Corrected by binding the explicit maintained source and prepared tree before compilation and rejecting redirected assembly output paths |
| `PORT008-PROV-P023` — a qualification-only P4 definition contaminated production-object compile commands | Created in the project PlatformIO qualification profile; official VDP has no Extender qualification macro or composition | Corrected by moving the definition into two qualification-only translation units and rejecting its reintroduction through global build flags; fresh target provenance remains required |
| `PORT008-PROV-P024` — EMOS role definitions were applied to every C translation unit | Created in the project EMOS/generic-build profile integration; official MOS has no EMOS identity or fixed-qualification role | Corrected by applying the role definitions only to `src/emos.c`; fresh ordinary/fixed target provenance remains required |
| `PORT008-PROV-P025` — P4 identity values were applied to every translation unit | Created in the project P4 identity injector; official VDP has no Extender source/build/status identity layer | Corrected by making only the boot identity owner consume varying identity bytes while common production commands remain role-independent; fresh target provenance remains required |
| `PORT008-PROV-P026` — the EMOS fixed profile substituted a composition label for firmware identity | Created in the project EMOS fixed-qualification profile; official MOS has neither EMOS firmware identity nor an Extender qualification composition | Corrected by supplying the same EMOS firmware lineage independently from the separately revisioned non-release composition; Author-approved identities and fresh target provenance remain required |
| `PORT008-PROV-P027` — the P4 fixed composition had no independently revisioned qualification identity | Created in the project P4 qualification/identity integration; official VDP has no Extender fixed composition | Corrected by making the boot identity owner carry a separate qualification-composition identity and diagnostic; Author approval and fresh target evidence remain required |
| `PORT008-PROV-P028` — the EMOS wrapper did not forward its selected target toolchain to the producer | Created in the project EMOS/generic-build wrapper; official MOS has no AgonDev wrapper | Corrected by forwarding the exact absolute toolchain through every recursive build/qualification target and retaining regression coverage; fresh target evidence remains required |
| `PORT008-PROV-P029` — the first generic actual-step recorder/build-interface draft admitted cross-unit or cross-session ambiguity | Created while implementing new project `mos-agondev` evidence infrastructure; official MOS has no actual-step recorder | Corrected before retained evidence in generic commits `7e00798` and `64bbf34`; the earlier rehearsal is invalid and was not retained |
| `PORT008-PROV-P030` — the first P4 actual-step recorder draft underbound executed argv, runtime roots, response forms, and dispatched subtools | Created while implementing project P4 evidence tooling; the Espressif multi-call dispatchers are intentional upstream behavior, but failure to authenticate the selected backends was local | Corrected before the recorder's first commit with direct execution, exact response/runtime/root records, dispatcher/backend binding, and adversarial tests; a clean real capture remains required |
| `PORT008-PROV-P031` — the first product-gate draft admitted incomplete command, lineage, path, role, and linked-instruction comparisons | Created while implementing project Work 2.e comparison tooling; official MOS and VDP provide no corresponding gate | Corrected before any eligible evidence; command fingerprints deliberately remain empty until a clean rehearsal and therefore the gate still fails closed |
| `PORT008-PROV-P032` — the active P4 recorder assumed Python `__file__` exists in a SCons extra-script namespace | Created in project Work 2.e PlatformIO integration; official VDP has no actual-step recorder or extra-script hook | First real rehearsal stopped before evidence creation; corrected by resolving the committed hook from SCons `PROJECT_DIR`, with a no-`__file__` active-install regression; new clean capture pending |

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
   no such object. At the original review boundary, committed EMOS still
   contained the defect and the Author's then-current prototype correction
   expanded the object, rejected nonzero `BCU`, and added a linked symbol-span
   check. The later production composition removes the exact adapter and uses
   an exact 16-bit bounded interface with record chunking.
3. The same EMOS adapter commit emitted adjacent clock-high/clock-low writes
   and left CLOCK low after a record. The qualified predecessor sender instead
   establishes VALID with CLOCK high, changes data during setup, and emits
   falling then rising phases for every byte. At the original review boundary,
   committed EMOS still contained the deviation and the then-current prototype
   correction restored that cadence. The later production engine preserves the
   cadence while removing the exact adapter from its source/link closure.
   Official MOS has no parallel sender.
4. EDP commit `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73`
   introduced `ForwardParallelStream` without GPIO15/GPIO21 direction-control
   ownership even though the predecessor had explicit fail-safe release and
   break-before-make selection. The Author's then-current prototype correction
   added those controls; the later replacement target owner now owns direction
   and deterministic teardown in the production data-plane composition. This
   does not resolve the separate production-activation defect recorded by the
   corrective action.
5. The temporary P4-to-ZDI recovery wrapper initially routed identity refusal
   through a helper that halted the eZ80. Official `agon-recovery` remains
   passive on failed identity and is not the origin. The wrapper separated
   passive refusal from post-halt failure before the source first entered Git
   in commit `ff1814733375476e6ab0af090c11a558fa5423c7`; consequently no
   committed faulty revision exists.
6. Official `agon-docs` commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` says bounded RST 18 returns the
   last displayed byte in A. Official MOS
   `5f67b1ca77eb7a77d3b37cc7b029db51f0d1548e` loads A from B, ORs C after the
   final decrement, and therefore returns zero on successful length-mode
   completion. EMOS's current onboard path and production parallel bridge also
   return zero on success. This is an upstream documentation/source divergence,
   not a defect introduced by the port. No distinct Extender manifestation is
   established.
   Under `PORT-003-D012` and `REMED-002-D004`, correction and broad regression
   design are deferred; the parallel-engine factoring must avoid changing the
   current de-facto result accidentally.
7. The EMOS repository `Makefile` accepted a `MOS_WORKTREE` selection but its
   firmware and qualification targets did not forward that value to the
   generic `mos-agondev` wrapper. The first isolated fixed-profile build
   therefore consulted the generic wrapper's default source tree instead of
   the caller-selected prepared tree. `mos-agondev` used its received inputs as
   designed; the omission was created in EMOS integration tooling. Every EMOS
   build and qualification target now forwards the selection explicitly, and
   repository-local tests require that propagation. The failed first attempt
   supplied no artifact or qualification evidence.
8. The first project-owned epoch commit could publish success after an
   interrupting writer had recorded a lifecycle fault, erasing that fault. No
   official MOS source implements this epoch, lease, or parallel writer. EMOS
   now begins and commits entry through IFF-preserving atomic helpers; commit
   observes contention and fails closed. This is `PORT008-PROV-P009`.
9. The same initial entry path could overwrite an interrupting leave request
   when the suspended entry resumed. This is likewise local to the new EMOS
   epoch implementation. Leave now invalidates the in-progress entry, and the
   atomic commit refuses publication. This is `PORT008-PROV-P010`.
10. An initial rejected stale or nested writer released its lifecycle lock
    before publishing the deferred failure. A newly admitted caller could
    therefore observe a false-clean interval. Official MOS has no corresponding
    lease/writer path. EMOS now publishes the failure before unlock and retains
    an adversarial ordering regression. This is `PORT008-PROV-P011`.
11. Initial linked-image verifiers described source/object origin, linker
    contribution, or semantic reachability more broadly than their actual
    symbol and instruction checks established. Those tools are project-owned;
    official MOS supplies no parallel verifier. Their checks and success text
    now distinguish exact structural dispatcher, fixed-coordinator, bridge-ABI,
    and guard properties from unproved provenance, target-runtime selection,
    and physical behavior. False-green tests cover the exact newly claimed
    shapes. This is `PORT008-PROV-P012`.
12. Official MOS `open_UART1()` legitimately changes PC0/PC1 mux and UART state
    without a parallel-epoch guard because stock MOS has no second Port C owner.
    The race appeared only when EMOS added project-owned parallel ownership
    without initially serializing the inherited API. EMOS now uses the same
    atomic lifecycle reservation for UART1 open and epoch admission, holds it
    across every serial-flag, Port C, and UART mutation, and releases it only
    after publishing UART1 active. This local integration defect is
    `PORT008-PROV-P013`, not an upstream MOS defect.
13. The first UART1 correction was conditional on a macro supplied by the
    AgonDev profiles even though the maintained native ZDS project also linked
    the production parallel objects. Native builds could therefore omit the
    guard. The macro and competing parallel owner are both project additions;
    official MOS has no equivalent profile split. EMOS made the guard
    unconditional and added native-ZDS/AgonDev parity regression coverage.
    This is `PORT008-PROV-P014`.
14. The initial fixed-profile coordinator discarded a failed adapter-recovery
    result after entry failure, overwrote the raw recovery diagnostic with the
    earlier prepare/ready result, and could change selected-adapter ownership
    after recovery failed. A failed cleanup could also leave the logical mode
    at Legacy while a repeated Legacy request returned false no-op success.
    Official MOS has no Extender adapter lifecycle or equivalent transaction.
    EMOS now propagates recovery failure, retains the old mode, backend, and
    adapter ownership, and retries retained fixed-route cleanup on a repeated
    Legacy request. This is the local `PORT008-PROV-P015` defect.
15. The initial coordinator returned private parallel lifecycle statuses in
    the `0xE0..0xE8` range through the public EMOS command path. The inherited
    `mos_error()` consumer supports the official MOS/FatFS result domain and
    therefore could not print those project-private values. Upstream MOS is
    correct for its domain and has no parallel lifecycle status. EMOS now
    retains the exact private failure in `lastStatus` while mapping the public
    result to printable `EMOS_UNAVAILABLE`. This is the local
    `PORT008-PROV-P016` integration defect.
16. The first target adapter applied its five-second completion timeout even
    while no sender had asserted `VALID_N`. An authorized but quiet epoch could
    therefore fault and stop without any record, and a periodic release/re-arm
    response would race the EMOS sender after it observed `READY_N`. The target
    now keeps the same armed PARLIO transaction and asserted readiness through
    idle, polls cancellation in bounded slices, and begins the fatal deadline
    only when active `VALID_N` proves a record started. This policy belongs to
    Extender, not upstream PARLIO, so this is local `PORT008-PROV-P017`.
17. The retained upstream parser caches `Stream::available()` and later casts
    `Stream::read()` to `uint8_t`. The first project Stream adapter rechecked
    the fault latch in `read()`, so a concurrent output fault could change an
    already-advertised byte into `-1`, which the inherited parser consumed as
    synthetic `0xFF`. The local adapter now permits exactly that advertised
    byte and blocks later bytes. This contract violation, not the inherited
    parser behavior, is `PORT008-PROV-P018`.
18. Initial record commit checked health and lease state separately from its
    queue-head publication. A concurrent output fault could therefore admit a
    record or allow the service call to report success after cancellation. The
    project data plane now uses one sequentially consistent cancellation edge:
    a record whose admission check wins first may finish publication but is
    quarantined, while cancellation that wins first prevents admission. Final
    health, lease, and cancellation checks forbid post-fault success. This is
    local `PORT008-PROV-P019`; the nonblocking edge also avoids a parser/service
    priority-inversion spin.
19. The first non-release qualification owner ignored
    `P4ParallelDataPlane::stop()` failure and revoked its fixed epoch
    immediately. That could abandon
    target resources while falsely relinquishing authority. The sole owner now
    retries idempotent teardown and preserves the lease until cleanup succeeds
    on every startup and service exit. This qualification-only integration
    defect is `PORT008-PROV-P020`, not an upstream firmware defect.
20. On retained process-task creation failure, the P4 top level requested
    cancellation but continued to the boot screen and network service. The
    resulting device could look live without a parser consumer. The branch now
    requests qualification stop and returns before those publications. This
    project boot-integration defect is `PORT008-PROV-P021`.
21. The EMOS wrapper eventually forwarded its selected prepared tree, but the
    generic `mos-agondev` root `worktree-check` still authenticated only the
    default stock source/tree pair. Later object recipes compiled the selected
    EMOS tree, so the successful preflight did not bind maintained source to
    compiled input. Generic commit `7e00798` makes both paths explicit, checks
    the exact pair before compilation, rejects symlinked assembly output roots
    and parents, and behaviorally verifies linked-object provider authority.
    This local evidence-orchestration defect is `PORT008-PROV-P022`; it is
    absent from official MOS and prevents promotion of pre-correction v10.
22. The non-release P4 PlatformIO environment originally supplied
    `AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION` as a component-wide build
    definition. The three production translation units therefore received a
    qualification-only command input even though none intentionally consumed
    it. Official VDP has no Extender profile or corresponding macro. The
    project now defines the role only inside a qualification boot wrapper and
    qualification owner translation unit, selects those files only for that
    composition, and makes the selector reject global reintroduction. This
    local build-profile defect is `PORT008-PROV-P023`; a fresh captured target
    build must still prove exact production-object command and byte equality.
23. The ordinary and fixed EMOS profiles originally supplied identity and
    fixed-role definitions through component-wide `CPPFLAGS_EXTRA`, although
    only `src/emos.c` consumes them. The five production equality units
    therefore carried role-specific command inputs and relied on those unused
    definitions not changing their object bytes. Official MOS has no EMOS
    profile or fixed qualification role. Generic `mos-agondev` now scopes
    profile definitions to one selected C source, and both EMOS profiles
    select `src/emos.c`. This project integration defect is
    `PORT008-PROV-P024`; fresh ordinary/fixed capture must establish equality.
24. The project P4 identity injector supplied source identity, build ID, and
    lifecycle status through component-wide compiler definitions, although the
    retained boot sketch is their only production consumer. Qualification and
    release builds necessarily have different build IDs, so the three common
    production units could never have identical recorded commands after real
    identities were assigned. Official VDP has no Extender identity injector
    or corresponding role boundary. This local build-identity defect is
    `PORT008-PROV-P025`; the varying identity input must be scoped to the boot
    identity owner and then proved by fresh target capture, not ignored during
    comparison.
25. The fixed EMOS profile used `PORT008-D002-FIXED-QUALIFICATION` as its
    firmware source identity and `NONRELEASE-DO-NOT-DEPLOY` as its build ID,
    rather than identifying an `agon-emos` firmware build and the independently
    revisioned qualification composition. It therefore could not authenticate
    as a qualification consumer of the same EMOS lineage as the ordinary
    composition. Official MOS has neither identity layer. The fixed profile
    now consumes the ordinary EMOS firmware identity tuple plus a separate
    `port-008-forward-qualification` composition identity, both scoped to
    `src/emos.c`, and reports the latter explicitly as non-release. This local
    profile defect is `PORT008-PROV-P026`; both identities remain unversioned
    until the Author approves successors and fresh target records are made.
26. The P4 fixed qualification composition initially had only the common
    firmware source/build/status tuple. It lacked the independently revisioned
    composition identity needed to distinguish the non-release caller from an
    eventual release consumer. Official VDP has no Extender fixed composition
    or corresponding identity. The qualification boot owner now consumes and
    reports `AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY`, while ordinary
    boot owners reject that value and common production units consume neither
    identity layer. This local identity-integration defect is
    `PORT008-PROV-P027`; its successor revision remains Author-unapproved.
27. The EMOS wrapper exposed `AGONDEV_TOOLCHAIN` and used it for linked-image
    inspection, but its recursive generic firmware/fixed/qualification targets
    did not forward that selection as `TOOLCHAIN`. A caller could therefore
    build with the generic default and inspect with a different requested
    toolchain. Official MOS has no AgonDev wrapper. Generic provenance would
    have recorded the producer that actually ran, so this was not a passing
    authenticated-record forgery; it was a silently ignored controlled input
    and split producer/inspector authority. All three targets now forward the
    exact absolute root with regression coverage. This local wrapper defect is
    `PORT008-PROV-P028`.
28. Adversarial review of the first generic actual-step implementation found
    that a `%` source selector became a Make pattern and could apply supposedly
    source-local definitions to every object; a constant session marker and
    incomplete producer-record binding admitted cross-invocation association;
    nested response indirection was not in the recorded grammar; and the
    compiler driver's selected assembler/effective invocation was not fully
    bound. These mechanisms were all new `mos-agondev` project infrastructure,
    not official MOS behavior. Commits `7e00798` and `64bbf34` require a
    literal selected source, unique recorder session, same-recorder/session/
    kind producer chain, one-level non-nested response policy, exact external
    assembler selection, and sanitized driver probes. This grouped local
    pre-baseline recorder defect is `PORT008-PROV-P029`; the earlier rehearsal
    was explicitly invalidated and no retained evidence depends on it.
29. Adversarial review of the first P4 recorder draft found rendered shell text
    being treated as actual argv, insufficient child-environment and root
    authority, incomplete SCons response/TEMPFILE grammar, unsafe generated-
    identity-header traversal, incomplete generated-source inventory, and no
    authentication of the backend selected by Espressif assembler/inspection
    dispatchers. The dispatch executables themselves are intentional upstream
    toolchain behavior; the failure to record the selected backends was in the
    project recorder. The corrected recorder directly executes the decoded
    compiler/link vector, binds the sanitized environment and runtime trees,
    round-trips the pinned response grammar, writes the identity header through
    anchored no-follow descriptors, inventories generated CMake input, records
    both the assembler dispatcher and `as-xespv2p1` selection, and makes the
    gate invoke pinned `objdump-xespv2p1` directly. This grouped local
    pre-baseline evidence defect is `PORT008-PROV-P030`; a clean real
    PlatformIO capture must still confirm the live action shapes.
30. The first product-gate draft could accept or miscompare evidence because
    it lacked frozen complete command fingerprints, did not bind all Git/
    registry/prepared/coordinator lineage, mishandled the per-session nonce
    across roles, omitted normalized linked-instruction comparison, accepted
    substring-only identity matches plus incomplete role/undefine/response
    forms, and did not reject every symlinked
    authority ancestor or root-graph contradiction. It also overstated capture
    runtime and implicit link closure. Official MOS/VDP provide no such gate;
    these were defects in newly written project evidence tooling. The gate now
    revalidates each raw capture independently, requires distinct sessions and
    build IDs, exact role and lineage inputs, policy-owned normalized compile/
    link fingerprints, exact object bytes, direct nonzero map contribution,
    independently terminated identity strings, owned symbols, and normalized
    linked instructions; it also rejects duplicate registry artifact IDs and
    non-calendar UTC build timestamps while stating its host
    runtime and implicit-link limits. This grouped local pre-baseline gate
    defect is `PORT008-PROV-P031`. Its fingerprint slots remain deliberately
    null until clean rehearsal, which makes validation ineligible rather than
    permissive.
31. The first clean live PlatformIO recorder installation failed before
    evidence creation because the project hook referenced Python's
    `__file__`, which SCons does not inject when it executes an extra script.
    Official VDP has no corresponding recorder. The hook now derives the
    committed project-relative file from SCons `PROJECT_DIR`, and a regression
    invokes active installation after removing the module global. This local
    integration defect is `PORT008-PROV-P032`; only a new clean capture at the
    corrective commit can authenticate production steps.

None of these classifications promotes the fixed-purpose PORT-008 adapters or
temporary recovery image into production. For P002 through P006, EMOS's mode
coordinator and ordinary Legacy route were not the source of the adapter, P4
readiness, or temporary recovery-wrapper defects. P009 through P016 separately
identify defects introduced and corrected while building or integrating the
new permanent EMOS production boundary; P015 is specifically in that
coordinator's new fixed-adapter transaction. P017 through P021 identify later
P4 production-data-plane or qualification/boot integration defects. P017--P019
are in maintained production objects; P020 is confined to the explicitly
non-release composition; P021 is in its guarded boot branch.
P022 is generic project build infrastructure rather than EMOS product code;
P023 is P4 qualification-composition tooling; P024 spans generic build tooling
and EMOS product profiles without changing EMOS runtime semantics; P025 is P4
identity/build tooling rather than retained VDP behavior; and P026 is EMOS
qualification-profile identity integration rather than official MOS behavior.
P027 is likewise P4 qualification identity integration; P028 is EMOS wrapper
tooling; and P029 through P031 are generic recorder, P4 recorder, and product-
gate infrastructure created and corrected before any eligible Work 2.e
evidence. P032 is a later local P4 recorder-installation defect caught by the
first clean live rehearsal before evidence creation. Their corrections are
prerequisites for fresh target provenance, not evidence that any
pre-correction build was authentic.

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
- Current disposition: Recorded under PORT-003-D012. Do not correct or design
  the isolating regression now; reopen only if deterministic comparison shows
  that selected Extender scheduling or presentation activates the failure in a
  way regular VDP operation does not, or the finding blocks a selected
  Extender function.

### `INTEGRITY-AUDIT-F002` — Palette and Copper mutation race frame publication

- Severity: High
- Observed state: The retained parser task calls palette and Copper mutations
  directly through `agon_screen.h`. The P4 controller forwards those calls to
  `PaletteState` without exclusion, while the independent frame task reads the
  same state during browser snapshot composition.
- Work 2.a extension: Official counted buffer adjustment may modify backing
  used by an active bitmap or sprite one inline operand at a time. Current
  `bufferAdjust()` retains a target span while it calls `readByte_t()`, so a P4
  exclusion scope around the current loop would either span blocking ingress or
  leave the independent frame reader racing each applied byte. The proposed
  D011 rule reads one operand without a lease, re-resolves the target, and
  commits that decoded unit under a bounded lease, retaining official partial-
  prefix timeout behavior.
- Consequence: Secondary-palette deletion and Copper-array replacement can free
  memory while the frame task dereferences it. This is a C++ data race with a
  plausible use-after-free, not merely a torn-colour presentation risk.
- Evidence: `vdp/video/agon_screen.h:70-108` and `:121-125`;
  `vdp/video/vdu_buffered.h:946-1041` and official
  `agon-docs/docs/vdp/Buffered-Commands-API.md:77,245-258`;
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
  upstream report if the D012 trigger threshold is met.
- Current disposition: Record the plausible local amplification, but defer
  correction and isolating regression design. Source reasoning alone does not
  establish a current forward-transport blocker.

### `INTEGRITY-AUDIT-F022` — Queued renderer operands and persistent users outlive their owners

- Severity: High
- Observed state: Pinned vdp-gl byte-copies raw `Bitmap const *`, transformed-
  bitmap pointers, and `CopyToBitmap` destinations into its primitive FIFO.
  Its dynamic-payload helper copies transform matrices, but copies path points
  only below `FABGLIB_PRIMITIVES_DYNBUFFERS_SIZE`; official
  `Context::plotPath()` submits the vector and immediately clears it. Official
  VDP also submits temporary `.get()` bitmap pointers and tile-layer member
  bitmaps, then permits buffer, bitmap, cursor, or tile backing to be cleared
  before the queued primitive executes. The generic glyph, glyph-buffer, and
  direct Canvas path interfaces are borrowed APIs whose lifetime remains the
  direct caller's obligation; no current `vdp/video` caller of
  `renderGlyphsBuffer()` was found. Font backing remains in PORT-003's compiled
  lifetime inventory rather than this finding's definite provenance.
- Definite retained failures: `clearBitmap()` erases bitmap ownership before it
  clears registered sprite frames. The all-buffer command destroys backing
  streams and clears the bitmap map without first resetting sprites, despite
  `resetBitmaps()` documenting that prerequisite. A queued draw or
  `CopyToBitmap` can therefore dereference a destroyed descriptor/backing on a
  later frame, an oversized official Context path can read cleared/reused vector
  storage, and an active sprite can retain a dangling frame pointer after all-
  buffer clear even without a concurrent parser mutation.
- Consequence: Legal sequential command ordering can produce use-after-free,
  invalid writes through a stale `CopyToBitmap` destination, or persistent
  dangling sprite/cursor state. F001's escaped-frame interleaving widens
  the window but is not required for the defect.
- Evidence: `vdp/vendor/vdp-gl/src/displaycontroller.h:392-400,473-489,558-577,738-760`;
  `vdp/vendor/vdp-gl/src/canvas.cpp:442-456,604-619,657-675`;
  `vdp/vendor/vdp-gl/src/displaycontroller.cpp:525-580,887-922,1616-1755`;
  `vdp/video/context/graphics.h:345-366,865-896`;
  `vdp/video/sprites.h:32-42,74-88,238-249`;
  `vdp/video/vdu_buffered.h:390-425`;
  and `vdp/video/vdu_layers.h:1092-1096,1127-1137`.
- Coverage gap: Existing renderer and presentation fixtures either draw
  synchronously or keep descriptors/backing alive. None forces a raw operand
  to remain queued across individual/all-buffer deletion, oversized managed
  path clear, or tile backing free, then execute the later consumer and a post-
  delete frame under the required memory-safety runner.
- Provenance: The cited vendored controller files match official VDP v2.16.0's
  pinned vdp-gl `all-the-plots` checkout, and the official parser deletion,
  sprite, context, and tile-layer paths have the same order at commit
  `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. EDP retained this composition;
  the P4 port did not create it. EDP's independent frame task and full overlay
  publication amplify the reachable interleavings.
- Current disposition: Record the inherited behavior and defer both correction
  and isolating regression design under PORT-003-D012. Reopen only if a future
  deterministic comparison demonstrates distinct Extender activation or the
  behavior prevents a selected Extender function. Rejected D011's synchronous
  drain and ownership alternatives remain research, not implementation
  requirements.

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
  timeout and released READY afterward, so the audited behavior is a porting
  regression rather than inherited PARLIO behavior.
- Product boundary: The audited r01 forward receiver was prototype code and is
  now rejected/retired. The replacement implements bounded completion, while
  target-runtime proof remains open.
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
- Resolution, 2026-09-01: The Author's stale-work directive selected the
  already-committed `f866660c...` schematic as the maintained r02 authority.
  HW-001 refreshed its profile digest, complete SVG/XML projection, and 19
  explicitly non-authoritative focused views. Version, topology, projection,
  BOM, and focused-view validators pass. F008 is closed as artifact-control
  drift; construction, electrical behavior, and qualification remain open.

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
- Disposition: Remediated 2026-09-01. ADR-0014 and `docs/architecture.md` now
  contain the complete accepted D002 lifecycle contract, including the
  two-plane state map, Legacy-hub transaction graph, dispatcher quiescence,
  pull discovery, shutdown, reset/failure recovery, and diagnostic-lifecycle
  rules. The promotion also removes the stale unresolved-dispatcher and
  controlled-ordinary-VDU-mirroring claims. SETUP-005, REMED-001, and
  REMED-002 record F009/Work 4.a complete without resolving D003--D008, F016,
  or F018.

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
- Audit-snapshot boundary: The predecessor boot abandoned startup after the
  first failure, while PORT-008 required retry and recovery behavior.
- Evidence: `vdp/video/extender/transport/forward_parallel_stream.cpp:134-178`.
- Provenance: PORT-008 commit
  `c03656c87ff10d39d52ba59a9fbbf914a0bb1d73` introduced the sentinel and
  partial-initialization exits. ESP-IDF and FreeRTOS provide the necessary
  disable/delete primitives. The predecessor receiver at
  `agon-extender-legacy` commit
  `df54cf6a7a23cd40e98076856f68cff0559d1c77` already unwound its PARLIO unit,
  delimiter, DMA storage, and READY state, so this is a direct porting
  regression.
- Product boundary: The audited r01 receiver is rejected/retired. Its
  replacement has transactional initialization and deterministic host retry
  tests; target-runtime proof remains open.
- Proposed owner: PORT-008.

### `INTEGRITY-AUDIT-F014` — PORT-008 capture analyzers can report invalid evidence as usable

- Severity: Medium
- Observed state A: The predecessor clock-discriminator script does not invalidate
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
  `mos-agondev` commit `5079d4c...`; the corrected candidate and then-current
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

1. The rejected predecessor P4 startup selected the forward direction and
   admitted READY before an EMOS session or committed-mode transition. That
   violated Legacy absence and is already recorded in
   `CA-2026-09-01-001-port008-preactivation-ready`; it is not assigned a second
   finding ID here. Its retired forward-build validator required the prohibited
   startup order and remains historical evidence under that corrective action's
   disposition.
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
   new defect was found in that task's existing lifecycle patch set. F001,
   F002, and F022 are separate upstream-composition findings and are not
   silently added to UPSTREAM-001; D012 records and defers them unless a future
   Extender-specific trigger or separately authorized upstream study appears.
6. Intel HEX/YMODEM feedback semantics, no-authentication browser exposure, and
   other explicitly accepted exclusions remain open decisions rather than
   accidental compatibility claims.

## Coverage register

| Area | State | Result |
|---|---|---|
| Open TODO and task-detail correspondence | Reviewed | All 18 open TODO IDs have task records and valid local links. |
| Display, frame service, palette, Copper, sprites, and snapshots | Reviewed | F001, F002, and F022; existing fixtures omit decisive concurrency and queued-operand lifetime. |
| Retained parser, deferred audio, maintenance adapters, and source selection | Reviewed | F004; HEX/YMODEM distinction retained. |
| Browser/network frame provider and ESP-IDF HTTP adapter | Reviewed | F003 and F012; abstract host tests pass. |
| Forward-parallel predecessor and historical diagnostic tooling | Reviewed | F005, F013, F014, and R001; preactivation defect remains under the existing corrective action. |
| Build closure, staging, version records, and r02 artifacts | Reviewed | F007 and F015 remain; F008 was reconciled on 2026-09-01. |
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
12. The PORT-003 Work 2.a design extension resolved 45 local links across its
    seven amended durable documents; targeted trailing-whitespace and private-
    value scans and `git diff --check` passed. The pass performed source
    inspection only: it did not build, run a sanitizer/fault fixture, deploy,
    or operate physical hardware.
13. The Author's D011/D012 scope disposition was propagated through the same
    seven durable documents. Forty-five local links, targeted whitespace and
    private-value scans, and `git diff --check` passed. No product source,
    fixture, build, deployment, or physical state changed.
14. Three read-only adversarial consistency passes verified the F009/D002
    normative promotion and the PORT-008 activation design. They confirmed D002
    coverage and corrected the listener's CTS bootstrap, Safe/fault versus
    Dormant-listen states, cross-domain corrective-action net set, EMOS-only
    commit ownership, post-commit General Poll boundary, finite
    resynchronization oracle, artifact-identity gate, F008 scope, and retained
    r01 diagnosis. The local resolver passed 111 links across the 14 amended
    documents; targeted whitespace/private-value scans and `git diff --check`
    passed. No product test was run because this pass changed documentation and
    proposed design only.
15. The later F008 reconciliation reran the version-record validator, complete
    schematic topology/projection check, 41-component BOM check, 44-net/50-no-
    connect authority check, 41-object hardware registry check, and all 19
    focused-view checks successfully. Items 5 and 6 preserve the original
    failure observation; they are not the current validator state.

## Disposition order recommended for Author review

This order is advisory and does not authorize work:

1. Contain demonstrated local runtime and hardware-ownership risks: F003--F005,
   F012, plus the existing preactivation corrective action.
2. Repair evidence trust before accepting more qualification: F006, F007,
   F011, F014, and F015. F008 was reconciled on 2026-09-01.
3. Reconcile accepted architecture and task ownership: F010, F016, and F018.
   F009's normative promotion completed on 2026-09-01.
4. Resolve the remaining prototype lifecycle defect: F013.
5. Complete future implementation gates: F017 and F019--F021, then retain
   R001--R003 in their named task designs. Retain F001, F002, and F022 as
   upstream research observations until D012 trigger evidence exists.

## Audit conclusion

The repository's existing success-path validation is substantial and mostly
reproducible. Demonstrated parser-framing, WebSocket transmission, clock-
recovery, qualification-reference, provenance, configuration-control, and
preactivation defects still constrain their named gates. F001, F002, and F022
remain source-level upstream observations with plausible EDP exposure, but
under the later D012 disposition they do not independently block bounded
forward-parallel transport work or require present hardening. F009's accepted
operating-mode content is now in normative authority; remaining cross-task
ownership and mode-conformance work stays with its named tasks.

The audit does not require one new monolithic remediation owner. Every finding
can be dispositioned into an existing open task, ADR, or normative authority.
Keeping this record under `docs/decisions/` preserves the reviewed snapshot and
stable finding IDs without making it a competing task list or architecture
specification.

The provenance extension distinguishes source origin from current action.
F003's demonstrated EDP exposure still requires local correction; F001, F002,
and F022 remain recorded under D012 without present correction until distinct
Extender activation is demonstrated. Project origin does not promote any
prototype adapter. The exact PORT-008 sender/receiver implementations remain
prototype-only, and the committed EMOS UART-width fix is the sole reviewed
permanent EMOS correction in the historical provenance set.

### 2026-09-01 post-audit implementation addendum

The final sentence above is snapshot-specific: the UART-width correction was
the sole committed permanent EMOS correction reviewed in the original
provenance set. Later the same day, Author-authorized PORT-008 Work 2 added
replacement P4/EMOS production objects, subsequently source-frozen in Extender
commit `e134f3d` and EMOS commit `b823e0e`. The v10 EMOS software
reconciliation corrected P008 through P016 and establishes exact ordinary-entry-
to-dispatcher and dispatcher-to-common-route call edges, excludes predecessor
symbols from normal and fixed closures, establishes exact fixed-coordinator-to-
wrapper and wrapper-to-common-route call edges, and serializes UART1 open with
parallel Port C ownership. Its linked bridge check fixes the bounded RST 18
argument and success/failure epilogue instruction shape; extracted production-
code tests exercise coordinator commit, recovery-failure retention/retry, and
private-to-public error mapping. Those additions and source commits do not
retroactively change the audit snapshot, promote the prototype adapters, or
create a frozen firmware artifact.

A subsequent P4 adversarial pass corrected P017 through P021: idle no longer
expires as a failed record; an already-advertised parser byte cannot become a
synthetic sentinel; cancellation has a nonblocking total order with record
admission and quarantines any pre-fault winner; the qualification owner retains
its lease through successful cleanup; and retained process-task creation
failure returns before boot/network publication. These are project-created P4
integration defects with no upstream implementation counterpart. Their host,
source-contract, compile/link, and closure checks do not close the still-open
target-runtime and retained-parser execution gates.

The Work 2.e build-provenance audit then found P022. EMOS had begun forwarding
its selected prepared tree, but generic `mos-agondev` authenticated the default
stock maintained-source/prepared-tree pair before compiling the different
selected tree. Generic commit `7e00798` now checks the exact caller pair,
rejects symlink-redirection of assembly outputs before object recipes, and
behaviorally derives profile provider authority from linked target objects.
This correction is project build infrastructure, not an official-MOS change,
and it requires fresh evidence rather than promoting v10.

The same pass found P023 through P025. The P4 qualification environment had
globally supplied its non-release role definition to the three production
translation units; the EMOS ordinary and fixed profiles had globally supplied
different identity/role definitions to five production equality units. Both
defects were introduced by project build/profile integration and have no
official VDP or MOS counterpart. Qualification-only P4 wrappers and
source-scoped EMOS profile flags now remove those role inputs from the common
production-object commands. Only fresh fail-closed target records can prove
that the commands, objects, and linked contribution are now equivalent.

P025 separately records that the P4 identity injector supplied varying
source/build/status definitions component-wide even though only the boot sketch
uses them. That local project mechanism has no official-VDP counterpart and
would prevent exact common-command equality once qualification and release
build IDs exist. Work 2.e must scope the identity input to its boot owner and
must bind the compiled values back to the approved build record.

P026 records the corresponding EMOS identity-role error: the fixed profile
used a qualification label where the common EMOS firmware source identity
belonged and had no separate procedure revision input. The profile now keeps
the firmware and non-release composition identities independent and confines
both to `src/emos.c`. This is a project profile correction, not an official-MOS
change, and remains unbuilt under approved successor identities.

P027/P028 record the remaining product-wrapper identity defects: the P4 fixed
composition lacked its own revision and the EMOS wrapper did not forward its
selected producer toolchain. Both were project integration errors with no
official VDP/MOS counterpart and both now have focused source regressions.

P029 through P031 group the pre-baseline false-authentication paths discovered
while implementing the generic recorder, P4 recorder, and product gate. All
were created in new project evidence tooling, not inherited firmware. The only
upstream behavior implicated is Espressif's intentional assembler/objdump
dispatcher mechanism; the local defect was failing to authenticate the actual
selected backend. The corrected recorders and gate pass adversarial host tests,
but command fingerprints, clean captures, approved identities, and a P4 release
consumer remain open, so no pre-correction rehearsal or current unversioned
record is production-equivalence evidence.

P032 was then exposed by the first clean PlatformIO rehearsal rather than by a
synthetic producer session. The project-owned P4 actual-step hook referenced
Python's `__file__`, while PlatformIO/SCons executes its extra scripts with
`exec()` and does not provide that module global. Official VDP has no
actual-step recorder, so this is a local Work 2.e integration defect rather
than inherited VDP behavior. The invocation stopped before creating its
evidence root. The hook now derives its exact committed path from SCons'
`PROJECT_DIR`, and an active-install regression deletes `__file__` before
installation. Only a new clean capture at the corrective commit can supply
evidence.

PORT-008 and INTEG-002 still own authenticated source/tool and final-link object
provenance, target-runtime behavior, retained-parser fault injection,
production activation and response integration, artifact identity, deployment,
and physical qualification.
