# AUDIT-010 A10-07 — Reviewed findings and itemized repair plan

## Executive summary

The Author approved the complete A10-06 findings set on 2026-09-29 and accepted
the proposed repair cadence: address one independently bounded defect at a time,
test it, present its evidence, and pause for Author acceptance before starting
the next item. This document records all finding and coverage dispositions and
proposes the complete dependency-ordered A10-08 plan.

The order is severity-first after two mandatory medium-severity authority
prerequisites. `AUDIT-010-F005` must establish the selected product profile and
`AUDIT-010-F012` must establish the sole product display owner before any
high-severity display repair can produce meaningful evidence. Within a severity
class, direct memory/lifetime risk, demonstrated impact and dependency order
take precedence over the numerical finding ID.

The Author approved this complete itemization on 2026-09-29. A10-07 is frozen
by its dedicated documentation commit before any executable A10-08 change.
Execution is authorized only one item at a time under the acceptance cadence
below; the first authorized item is `A10-RP01`.

## Review state

`A10-RP-S01` [x] The Author reviewed and approved the complete
[A10-06 findings](FINDINGS.md) on 2026-09-29.

`A10-RP-S02` [x] The Author accepted one-at-a-time correction and validation,
with a mandatory pause for Author acceptance before the next item.

`A10-RP-S03` [x] The Author reviewed and approved this complete disposition
matrix, dependency order and validation plan as a whole on 2026-09-29.

`A10-RP-S04` [x] A10-07 is frozen in its own dedicated documentation commit
after `A10-RP-S03`; A10-08 begins from that boundary with `A10-RP01` only.

`A10-RP-S05` — The later Author-reported `FWBUG-013` cursor defect was filed
after the frozen A10-06 findings set. It remains visible in its own task and does
not silently enter this repair plan. Reprioritizing it requires an explicit plan
amendment; it does not change the dispositions below.

## Immutable execution cadence

`A10-RP-C01` — Execute exactly one numbered plan item at a time. An item includes
its bounded research refresh, implementation or validation-only work, regression
manifest, tests, evidence, documentation and logical commit. Shared test
infrastructure may be reused, but unrelated source corrections may not share an
item or acceptance claim.

`A10-RP-C02` — At the end of every executable or validation-only item, stop and
present: exact repositories/commits, changed actors and contracts, test results,
remaining limits, target state, and the next proposed item. Do not begin that
next item until the Author explicitly accepts the completed item.

`A10-RP-C03` — A failed test, incomplete repair or Author-requested revision
remains within the current item. Diagnose and iterate only that item; failure
does not authorize work on a later item. Preserve informative failures under
the normal evidence policy.

`A10-RP-C04` — Before changing code, each item declares a regression manifest
covering its direct behavior, previously accepted neighboring behavior, build
profile and applicable cross-processor/wire contracts. Passing a targeted test
does not waive those regression checks.

`A10-RP-C05` — Source-contract, host, sanitizer, build and static checks are
normal item validation. Each executable repair uses the maintained independent
exact-commit flash command followed by the complete retained suite plus its
registered repair-specific physical case. Running either command is the bounded
operator invocation of its documented mutations; hardware evidence is never
inferred from host or emulator success.

`A10-RP-C06` — Reusable target suites run unattended where practical, print
progress on the Legacy/mainboard screen, preserve failure text, record durable
start/end timing, and emit the accepted audible completion or failure cue. The
agent does not spend the fixture runtime continuously monitoring it.

`A10-RP-C07` — Validation-first findings do not authorize speculative source
changes. Present their evidence and pause. If a mismatch or applicable trigger
is demonstrated, amend this plan with a bounded repair item and obtain Author
approval before implementing it.

`A10-RP-C08` — Each accepted item receives its own final disposition and commit.
Approval advances only to the next listed item; it is not blanket acceptance of
later repairs, production promotion or post-audit LCD redeployment.

## Coverage-row dispositions

The Author's approval accepts the final A10-06 disposition of every frozen
coverage row. The compact record below is explicit; detailed actors, sources
and cross-references remain in [COVERAGE-LEDGER.md](COVERAGE-LEDGER.md).

| Coverage ID | A10-07 disposition |
|---|---|
| `A10-COV001` | Accepted complete; F002 and F005 proceed under this plan. |
| `A10-COV002` | Accepted complete with no finding. |
| `A10-COV003` | Accepted complete; F001, F002 and F012 proceed. |
| `A10-COV004` | Accepted complete; F001, F011, F012 and FWBUG-001 proceed. |
| `A10-COV005` | Accepted complete; F006, F008, F011, F012, FWBUG-001, FWBUG-007 and FWBUG-012 proceed. |
| `A10-COV006` | Accepted complete; eager-lifetime defect remains F002. |
| `A10-COV007` | Accepted complete; persistent allocation policy remains F002. |
| `A10-COV008` | Accepted complete; socket composition remains F004. |
| `A10-COV009` | Accepted complete; F002, F003 and F004 proceed. |
| `A10-COV010` | Accepted complete; F013 is conditionally deferred. |
| `A10-COV011` | Accepted complete; global socket composition remains F004. |
| `A10-COV012` | Accepted complete; F003, F004 and conditionally deferred F013 apply. |
| `A10-COV013` | Accepted complete with no finding. |
| `A10-COV014` | Accepted complete with no finding. |
| `A10-COV015` | Accepted complete with no finding. |
| `A10-COV016` | Accepted complete with no finding and the recorded hardware limit retained. |
| `A10-COV017` | Accepted complete; F013 is conditionally deferred. |
| `A10-COV018` | Accepted complete; F014 contract work proceeds. |
| `A10-COV019` | Accepted complete; F014 contract work proceeds. |
| `A10-COV020` | Accepted complete with no finding. |
| `A10-COV021` | Accepted complete; F005 and F012 proceed. |
| `A10-COV022` | Accepted complete; F005/F012 proceed and retired predecessors remain disposed. |
| `A10-COV023` | Accepted complete; F010 proceeds. |
| `A10-COV024` | Accepted complete with no new client finding. |
| `A10-COV025` | Accepted complete with no finding. |
| `A10-COV026` | Accepted complete; F008/F011 validation and F009 repair proceed. |
| `A10-COV027` | Accepted deferred LCD delta; regress F001/F002/F008 after AUDIT-010. |
| `A10-COV028` | Accepted complete exclusion. |
| `A10-COV029` | Accepted complete read-only reference use with no finding. |
| `A10-COV030` | Accepted bounded comparison; mode20 evidence does not prove cause. |
| `A10-COV031` | Accepted complete with no finding. |
| `A10-COV032` | Accepted complete; FWBUG-008/009/010 proceed under their existing IDs. |
| `A10-COV033` | Accepted complete; F006/F007 and FWBUG-006/007/012 proceed. |
| `A10-COV034` | Accepted complete integration; F004 proceeds and the OSV limit remains explicit. |
| `A10-COV035` | Accepted complete; F004 and F005 proceed. |

## Finding dispositions

No finding is rejected. “Validation first” means evidence is accepted as a
real gap or source concern, but no repair is authorized until the planned
discriminating test establishes an applicable consequence. “Deferred” retains
the finding and its activation condition without scheduling a standalone edit.

| Finding | Severity | A10-07 disposition | Plan owner |
|---|---|---|---|
| `AUDIT-010-F001` | High | Accept for two separately committed repairs: checked lower allocation, then P4 prepare/commit/rollback. | `A10-RP05`, `A10-RP06` |
| `AUDIT-010-F002` | High | Accept for repair after display ownership and transaction repairs. | `A10-RP09` |
| `AUDIT-010-F003` | High | Accept atomic WebDAV startup/rollback repair. | `A10-RP10` |
| `AUDIT-010-F004` | Medium | Accept one application-wide socket budget/admission repair. | `A10-RP12` |
| `AUDIT-010-F005` | Medium prerequisite | Accept profile correction before behavioral firmware repair. | `A10-RP01` |
| `AUDIT-010-F006` | High | Accept isolated size/lifetime/stack-safety repair. | `A10-RP03` |
| `AUDIT-010-F007` | Medium | Accept one defined conversion seam after complete caller inventory. | `A10-RP11` |
| `AUDIT-010-F008` | Medium gap | Accept validation first; repair only through an approved amendment after a mismatch. | `A10-RP16` |
| `AUDIT-010-F009` | Low | Accept browser-test ownership/drain repair. | `A10-RP20` |
| `AUDIT-010-F010` | Low | Accept maintained-documentation correction. | `A10-RP21` |
| `AUDIT-010-F011` | Medium unresolved | Accept shape validation first; repair only proven cases through an approved amendment. | `A10-RP17` |
| `AUDIT-010-F012` | Medium prerequisite | Accept architecture/profile correction, oracle extraction and explicit retirement boundary. | `A10-RP02` |
| `AUDIT-010-F013` | Low | Defer standalone cleanup; activate only when an owning file changes, with golden vectors. | `A10-RP22` |
| `AUDIT-010-F014` | Low | Accept contract clarification and shared corpus first; no assumed consolidation. | `A10-RP19` |
| `FWBUG-001` | High | Accept isolated selected-vdp-gl iterator repair; do not change display family. | `A10-RP07` |
| `FWBUG-006` | Medium | Accept official-grammar-derived consume-and-report repair. | `A10-RP13` |
| `FWBUG-007` | Medium unresolved | Accept bounded validation first; repair only demonstrated applicable subconditions through an amendment. | `A10-RP18` |
| `FWBUG-008` | High | Accept EMOS raw-write wrapper correction using the existing mos-tests owner and fixture. | `A10-RP04` |
| `FWBUG-009` | Medium | Accept EMOS volume-label wrapper-return correction using existing tests. | `A10-RP14` |
| `FWBUG-010` | Medium | Accept general per-reply minimum-length validation in the EMOS UART0 receiver. | `A10-RP15` |
| `FWBUG-012` | High | Accept bounded trigger validation first; ownership repair only for established all-buffer, point and sprite cases through an amendment. | `A10-RP08` |

## Dependency-ordered repair and validation sequence

Every item below ends at the `A10-RP-C02` acceptance pause. Checkbox completion
means its evidence has been presented and accepted, not merely that code was
written or a test launched.

### Authority prerequisites

`A10-RP01` [x] **F005 — Minimal authoritative product-development profile.**
Classify every selected definition/source as required, diagnostic or rejected;
move retained diagnostics to explicitly named profiles; reject conflicting draw
flags; rebuild the native graph and prove one deterministic ordinary profile.
Validation: manifest/profile tests, native build, linked-source/definition graph
and unchanged required service inventory. This medium item precedes high repairs
because all later build and test identities depend on it.

Accepted by the Author on 2026-09-29 after the minimal-profile build/graph and
neighbor regressions passed and the audit-impacting browser oracles were repaired
and rerun. Implementation commits: `2105f50b`, `36131e8d`.

`A10-RP02` [x] **F012 — Sole product display owner and retirement boundary.**
Confirm the selected stock-shaped display family as product owner, inventory and
extract unique nonrelease oracles, define the nonrelease family's removal or
archive condition, and prove exactly one family links in each admitted profile.
Do not copy repairs between families. Validation: `A10-VP06`, architecture and
profile checks, plus build proof. This is the second and final severity-order
exception.

Accepted by the Author on 2026-09-29 after both isolated native profiles,
applicable host contracts, flash verification, boot/service smoke and the
Author-observed Nurples late ExCom mode-switch regression passed. Implementation
commit: `f8458a31`; hardware-observation record: `4307e94d`.

### High severity

`A10-RP03` [x] **F006 — Mutable font bounds, lifetime and fixed scratch.**
Refresh the official font contract, retain backing/offset ownership and size,
validate every metadata mutation/use, and replace unbounded or wrapped stack
scratch with a fixed safe strategy. Validation: `A10-VP07` under ASan/UBSan,
maximum/short/mutated/destroyed-offset cases, screen-character capture, P4
compile and declared neighboring text regressions. Upstream publication remains
a separate decision.

Accepted by the Author on 2026-09-29 after sanitizer, screen-capture,
neighboring renderer/text and actual selected P4 build evidence passed.
Implementation commit: `c789d45a`; see
[RP03-MUTABLE-FONTS.md](RP03-MUTABLE-FONTS.md).

`A10-RP04` [x] **FWBUG-008 — EMOS raw SD write dispatch.** Correct only the
EMOS/MOS API wrapper so valid write requests invoke the write path and preserve
status/ABI behavior. Reuse the owning mos-tests fixture and controls; do not
duplicate it in Extender. Validation: existing emulator/host controls, rebuilt
EMOS identity, and a separately authorized physical destructive-sector test
using a disposable controlled sector with restoration evidence.

Candidate and two-command hardware workflow complete; see
[RP04-RAW-SD-WRITE.md](RP04-RAW-SD-WRITE.md). Source, linked-image, four
independent raw-image cases, exact-commit full-ROM verification, the expanded
55-case retained closure and the registered physical write/readback/restoration
case pass. The Author accepted RP04 on 2026-09-30 after the canonical paired
hardware suite passed all 17 checks and a manual Nurples ExCom run passed.
RP05 is now the next authorized repair item.

`A10-RP05` [ ] **F001a — Checked display allocations.** Add complete failure
checks and local cleanup for inherited viewport pool/table and paletted DMA-row
allocation without yet redesigning the outer P4 transaction. Validation: the
allocation subset of `A10-VP01`, null/failure injection at every allocation,
sanitizers where host execution is meaningful, native build, and proof that no
partial object is published or dereferenced.

Candidate implementation and validation are recorded in
[RP05-CHECKED-DISPLAY-ALLOCATIONS.md](RP05-CHECKED-DISPLAY-ALLOCATIONS.md).
RP05 remains open pending clean-commit qualification, exact-commit hardware
evidence, the required manual loaded-asset transition and Author acceptance.

`A10-RP06` [ ] **F001b — P4 mode prepare/commit/rollback.** Build one selected-
family transaction that prepares geometry/controller/clock/workers before
retiring the live mode, publishes only after success, and retains a usable old
mode or mode1 fallback with truthful status. Reuse official modeline parsing.
Validation: the remaining `A10-VP01` failures, early/late mode transitions and,
after explicit authorization, `A10-VP02` mode8↔20 hardware cases. This item does
not absorb palette or browser-resource policy.

`A10-RP07` [ ] **FWBUG-001 — Palette erase iterator lifetime.** Repair the
selected vdp-gl cleanup loop without selecting the parallel display family.
Validation: retained ASan host reproducer, multiple-palette/all-palette cleanup,
Copper palette regression, native build and the bounded physical sequence only
if its procedure is authorized.

`A10-RP08` [ ] **FWBUG-012 — Queued operand/bitmap/sprite lifetime validation.**
Run the existing bounded current-build trigger suite in required D012 order for
all-buffer clear, managed-point teardown and active sprites. Make no speculative
source repair. Present results and pause. Any established repair becomes a new
subitem added by an Author-approved plan amendment before code changes.

`A10-RP09` [ ] **F002 — Optional, demand-sized browser presentation resources.**
Make basic display attach independent of snapshot availability; size/lifetime
snapshot and codec storage from actual demand with bounded leases and graceful
capability-specific degradation. Validation: `A10-VP03`, every allocation
failure with zero/active browser demand, browser reconnect/codec fallbacks,
native build and separately authorized `A10-VP02` resource measurements.

`A10-RP10` [ ] **F003 — Atomic WebDAV startup and retry.** Keep listener and
workers in staged local ownership, publish readiness only after the complete
runtime exists, unwind in reverse order on every failure and permit a clean
retry. Validation: `A10-VP04` failure at every socket/task step, cleanup/leak
proof, retry, network-service regressions and native build.

### Medium severity

`A10-RP11` [ ] **F007 — Defined numeric conversion seam.** Inventory every
parser and buffered caller, replace aliasing and signed-shift UB with one checked
bit-safe contract, and retire the partial duplicate rather than add a third
helper. Validation: `A10-VP08` UBSan and golden matrices for widths, shifts,
special floating values and all entry points; include Rally numeric regressions.

`A10-RP12` [ ] **F004 — Application-wide socket budget and admission.** Assign
declared shares/reserve across video HTTP, local-SD HTTP, WebDAV and component
internal needs; make startup/admission obey the selected global limit. Do not
merge distinct protocols. Validation: `A10-VP05` static selected-config budget,
boundary admission tests and combined service host checks. Hardware saturation
is optional and requires a later explicit request/procedure.

`A10-RP13` [ ] **FWBUG-006 — Firmware-updater command consumption.** Derive
selector/payload grammar from the official handler, consume every complete
unsupported command, report unsupported status as contracted, and preserve the
following ordinary VDU byte stream. Validation: retained selector/payload corpus
with a sentinel ordinary command after every case, truncation handling, parser
regressions and native build. No P4 OTA feature is implied.

`A10-RP14` [ ] **FWBUG-009 — EMOS volume-label API return.** Add the missing
wrapper return while preserving the actual FatFS result and ABI. Reuse existing
label tests and do not broaden filesystem behavior. Validation: success/failure
status cases, label state, rebuilt EMOS identity and separately authorized
physical reuse of the existing fixture if required.

`A10-RP15` [ ] **FWBUG-010 — EMOS UART reply minimum lengths.** Define the
minimum payload for every known reply type and reject/discard a short known
packet before dispatch without using stale bytes. Keep general validation
separate from the private graphics-result check. Validation: retained complete-
then-short trigger for every known type, following-packet recovery, ordinary
traffic regressions and rebuilt EMOS identity.

`A10-RP16` [ ] **F008 — Dynamic scanout-effects proof.** Build one deterministic
static Copper/cursor/sprite fixture with machine-checkable regions and compare
native P4 output with browser bytes under the unattended cue contract. Do not
repair on visual suspicion. Present `A10-VP09` results; a mismatch requires an
approved plan amendment before source work, while a pass closes only the stated
pre-LCD coverage gap and becomes a later LCD regression.

`A10-RP17` [ ] **F011 — Filled arc/sector consequence validation.** Run
`A10-VP11` across quadrants, wrap and radii against an independent simple edge
oracle. Present results before any code change. Equivalent output disposes the
runtime consequence while retaining the dead-code conclusion; a mismatch opens
only the proven cases through an approved plan amendment.

`A10-RP18` [ ] **FWBUG-007 — Completion/swap applicability validation.** Use
the existing bounded UPSTREAM-001 trigger against the selected product owner;
do not import the preserved candidate first. Present which, if any, completion
or swap subcondition manifests. Any repair requires an approved plan amendment
limited to demonstrated applicable behavior.

### Low severity and retained deferral

`A10-RP19` [ ] **F014 — SD path-policy contract and corpus.** Name common
syntax/confinement versus intentional `sdjob` restrictions and build
`A10-VP13` from shared accepted/rejected vectors. Do not merge the services or
predicates merely because they overlap. Present the policy/corpus result; only
an evidenced accidental divergence may open consolidation through an amendment.

`A10-RP20` [ ] **F009 — Browser page-error ownership.** Bind one immutable error
sink to each page iteration, drain it before PASS/close and prevent a late
callback from contaminating another run. Validation: `A10-VP10`, consecutive
pages with delayed injected failure, existing browser layout checks and a clean
resource shutdown.

`A10-RP21` [ ] **F010 — Maintained build guidance.** Replace the routine
historical PlatformIO invocation with the exact maintained native entry point;
retain explicit historical reproduction wording only where necessary.
Validation: command/link checks and documentation references; no target run.

`A10-RP22` [ ] **F013 — Conditional CRC consolidation watch.** No standalone
code change is scheduled. At each accepted item touching an owning P4 or EMOS
CRC file, either leave the primitive untouched with a recorded reason or amend
that item to introduce one dependency-free primitive per processor toolchain
and run `A10-VP12` cross-target vectors. Mark this finding deferred at A10-09 if
no owner changes; do not create churn solely to close it.

## A10-09 and post-audit boundary

`A10-RP-X01` — A10-09 assembles the individually accepted item receipts and any
approved conditional amendments. It does not rerun already sufficient tests
merely to create one monolithic pass, but it must run the smallest combined
integration matrix needed to detect cross-item regressions.

`A10-RP-X02` — Production promotion, bundle/version/tag selection and publication
occur only after the complete accepted repair set and required target evidence
are reviewed. No plan item independently promotes production.

`A10-RP-X03` — Only after AUDIT-010 closes may LCD-001 reintroduce LCD support as
a separately reviewed delta. That delta must regress mode lifecycle, browser
resource independence, dynamic effects, early/late modes, assets, colour,
geometry and browser/service coexistence.
