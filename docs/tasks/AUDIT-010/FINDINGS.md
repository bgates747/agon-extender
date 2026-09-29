# AUDIT-010 A10-06 — Complete findings and validation proposals

## Executive summary

This document is the complete pre-repair findings set for the frozen pre-LCD
audit baseline. It promotes eleven manual-review conclusions and three material
duplicate-owner results into fourteen new `AUDIT-010-Fnnn` findings. Seven
already-authoritative firmware bugs remain under their existing `FWBUG-nnn`
identities and are carried into review without renumbering.

No finding is based on suspected AI authorship. No finding was created merely
because a scanner emitted a warning or because two files look similar. Each
finding follows an active call path, a violated contract, a material ownership
risk or an explicit coverage gap. Intentional target copies, distinct services,
test compatibility aliases and trivial helper clones remain disposed in
[LINEAGE-AND-DUPLICATION.md](LINEAGE-AND-DUPLICATION.md).

The highest-priority result is a cluster, not one root cause:

`A10-FS01` — Mode replacement is not transactional (`AUDIT-010-F001`), and the
selected product makes maximum browser snapshot storage mandatory
(`AUDIT-010-F002`). These facts can interact with application assets and heap
topology, but static evidence does not prove that either one alone caused the
retained late-mode20 Nurples failure.

`A10-FS02` — Application-controlled font state can escape its validated storage
and stack bounds (`AUDIT-010-F006`). This is the new finding with the clearest
direct memory-safety consequence.

`A10-FS03` — WebDAV startup can publish a partial runtime
(`AUDIT-010-F003`), while the independently configured network services request
more sockets than the selected global limit can provide (`AUDIT-010-F004`).

`A10-FS04` — The ordinary console profile is an accumulated experiment bundle
(`AUDIT-010-F005`), and a second mutually exclusive P4 display family remains
in the maintained tree (`AUDIT-010-F012`). Product-profile and display-owner
decisions must precede display repairs so that fixes are not validated against
an unstable or duplicate owner.

`A10-FS05` — Three findings require validation before a repair scope is fixed:
dynamic scanout effects (`AUDIT-010-F008`), the filled arc/sector consequence
(`AUDIT-010-F011`) and path-policy drift (`AUDIT-010-F014`). None of those is
represented as a demonstrated user-visible failure.

## Severity and evidence vocabulary

`A10-SEV01` — **Critical** means a demonstrated or source-proven path can cause
irrecoverable data loss, defeat the maintained recovery boundary, or make a
supported safety/authority guarantee false. No new A10 finding reaches this
threshold on present evidence.

`A10-SEV02` — **High** means a supported input or ordinary resource failure can
cause memory unsafety, a crash, loss of the primary display contract, or a
major service failure without truthful rollback.

`A10-SEV03` — **Medium** means incorrect output, bounded service unavailability,
architecture/resource contradiction, or a material qualification gap without
present evidence of memory corruption or irreversible loss.

`A10-SEV04` — **Low** means a weak oracle, stale instruction or maintenance
duplication whose present runtime consequence is limited or unproven.

`A10-EV01` — **Demonstrated** identifies a retained host or physical result.
**Source-proven** means the faulty control/data flow follows from the frozen
source without requiring runtime reproduction. **Configuration-proven** means
selected limits or definitions contradict one another. **Coverage gap** means
the intended path is present but material behavior has not been demonstrated.
**Maintenance risk** means parallel code can drift; it is not a claim that its
current outputs differ.

## Findings ranked by severity

`A10-RANK01` — Ranking is by severity first, then direct memory/lifecycle
consequence, then evidence confidence. Equal-severity position is not the repair
order; dependencies are recorded later under `A10-ORDnn`.

| Rank | Finding | Severity | Evidence | Concise result |
|---:|---|---|---|---|
| 1 | `AUDIT-010-F006` | High | Source-proven | Mutable font metadata and offsets can cause out-of-bounds access, wrapped stack sizing and excessive `alloca`. |
| 2 | `AUDIT-010-F001` | High | Source-proven; consistent physical symptom | A mode request destroys/reconfigures the live display before replacement success and contains unchecked inherited allocations. |
| 3 | `AUDIT-010-F002` | High | Source/resource-proven; failure causality hypothetical | The display requires a 2,359,296-byte browser snapshot pool and later retains another 2,162,706 bytes of codec scratch. |
| 4 | `AUDIT-010-F003` | High | Source-proven | WebDAV can retain a listener/accept task, lack its application worker, and later report startup success. |
| 5 | `AUDIT-010-F007` | Medium | Source-proven language UB | Active numeric conversion violates strict aliasing and permits an undefined signed shift; a safer local helper covers only one path. |
| 6 | `AUDIT-010-F004` | Medium | Configuration-proven | Two HTTP servers plus WebDAV request up to seventeen sockets from a selected limit of ten. |
| 7 | `AUDIT-010-F005` | Medium | Source/configuration-proven | The ordinary product-development profile silently composes mutually inconsistent experiments and diagnostics. |
| 8 | `AUDIT-010-F012` | Medium | Source-proven parallel ownership | Two mutually exclusive P4 display/controller families encode overlapping product behavior and different fixes. |
| 9 | `AUDIT-010-F008` | Medium | Coverage gap | P4 source retains Copper/cursor/sprite decoration, but no current deterministic target proof covers dynamic effects through snapshots. |
| 10 | `AUDIT-010-F011` | Medium | Source-proven branch; consequence unresolved | An inherited filled arc/sector edge branch is unreachable. |
| 11 | `AUDIT-010-F014` | Low | Source-proven policy drift risk | `sdserve` and `sdjob` share the transfer engine but apply overlapping, differently expressed path rules. |
| 12 | `AUDIT-010-F013` | Low | Source-proven maintenance duplication | Multiple P4/EMOS facilities repeat the same CRC32 bit loop without one target-appropriate primitive. |
| 13 | `AUDIT-010-F009` | Low | Source-proven weak oracle | A browser page-error callback can append to the wrong loop iteration or arrive after assertion. |
| 14 | `AUDIT-010-F010` | Low | Source-proven documentation defect | Maintained service guidance still invokes the gated historical PlatformIO build. |

## Detailed new findings

`A10-FMAP01` — Each finding's `-01` item is `A10-FIELD01`, `-02` is
`A10-FIELD02`, `-03` is `A10-FIELD03`, `-04` is `A10-FIELD04`, `-05` combines
the consequence and confidence required by `A10-FIELD05` and `A10-FIELD06`,
`-06` is `A10-FIELD07`, and `-07` records `A10-FIELD08` and `A10-FIELD09`.
Combined fields remain separately stated inside their item.

### AUDIT-010-F001 — Mode replacement is destructive before commit

`A10-F001-01` **Statement/severity (`A10-FIELD01`).** High. A supported VDU 22
request can destroy or reconfigure the live native display before the requested
mode has allocated, passed geometry checks and attached both P4 workers. The
official old-mode/mode-1 fallback repeats that destructive path rather than
rolling back a prepared replacement.

`A10-F001-02` **Actors/source (`A10-FIELD02`).** EMOS/application requests the
mode; `VDUStreamProcessor::vdu_mode` owns official fallback;
`agon_screen.h::changeResolution`, `StockP4Service`, `VGABaseController` and
`VGAPalettedController` own P4 teardown, allocation and attach. Frozen P4 source
is `755d6f37`; affected coverage is `A10-COV003`, `A10-COV004`,
`A10-COV030` and `A10-COV033`.

`A10-F001-03` **Contract (`A10-FIELD03`).** A failed request may report memory
failure, but fallback must leave a usable, truthfully published current mode or
mode 1. Allocation failure must not dereference null or partially published
storage.

`A10-F001-04` **Evidence/counter-evidence (`A10-FIELD04`).** Source proves live
Canvas/worker/controller teardown precedes all replacement checks; base viewport
pool/table and paletted DMA-row allocations are not fully checked. Logical mode
publication is correctly withheld until success, and detach joins readers
before destruction. Retained hardware shows a late mode20 request preserving
mode8-like geometry, but does not identify which allocation or fallback edge
caused it.

`A10-F001-05` **Consequence/confidence (`A10-FIELD05`/`06`).** High confidence in
the transaction and null-allocation defects; medium confidence that they explain
the retained Nurples symptom. Consequences include crash, blank/wrong geometry,
or logical/physical state divergence under ordinary memory pressure.

`A10-F001-06` **Owner/validation/disposition (`A10-FIELD07`).** Proposed owner is
the selected stock-shaped P4 mode transaction. Accept for repair after A10-07,
split into checked allocation and prepare/commit/rollback items. Validate first
with host allocation/task failure injection, then with bounded early/late
mode8↔20 hardware cases after a candidate exists. Acceptance requires preserved
old-mode or mode1 state at every injected failure and truthful status.

`A10-F001-07` **Lineage/duplicates (`A10-FIELD08`/`09`).** `A10-LIN01` is mixed:
fallback and lower allocation hazards are inherited; P4 object ordering is an
adaptation. `A10-DUP02` identifies the nonstock rollback coordinator and local
modeline parser. Reuse upstream modeline parsing and implement one product
transaction; do not copy a repair into both display families.

### AUDIT-010-F002 — Browser resources are mandatory global display costs

`A10-F002-01` **Statement/severity.** High. Basic stock display attach requires
three maximum 1024×768 snapshot slots even when no browser client exists, and
network startup eagerly retains maximum scratch for three codecs.

`A10-F002-02` **Actors/source.** P4 `PresentationSnapshotPool`,
`StockP4Service`, `WiredNetworkService` and browser codec owners; coverage
`A10-COV001`, `A10-COV003`, `A10-COV006`, `A10-COV007` and `A10-COV009`.

`A10-F002-03` **Contract.** Optional browser output must degrade independently
and must not make an otherwise supportable display mode fail. Maximum transient
capacity requires an explicit lifecycle owner.

`A10-F002-04` **Evidence/counter-evidence.** Source calculates 2,359,296 bytes
for snapshot slots and 2,162,706 bytes for codec scratch, totaling 4,522,002
bytes before native planes and assets. Snapshot allocation failure disables the
pool, but `StockP4Service::attach` then rejects every mode. Codec failure already
degrades by codec, proving all codecs are not required for raw correctness.

`A10-F002-05` **Consequence/confidence.** High confidence in global coupling and
retained bytes; only hypothetical causality for late mode20. A disconnected
browser can still reduce application/mode capacity and make allocation order
observable.

`A10-F002-06` **Owner/validation/disposition.** Proposed owner is the one P4
snapshot/browser service. Accept for repair: make basic display independent,
allocate dimensions/lifetime from actual demand, and retain bounded leases.
Host tests must inject every slot/codec allocation failure. Later target
qualification measures capability-specific free/largest blocks across isolated
display, browser and asset-loaded orders.

`A10-F002-07` **Lineage/duplicates.** Project-new under `A10-LIN02` and
`A10-UE01`. The shared `PresentationSnapshotPool` is already the canonical
implementation; no second capture pool is justified. `A10-DUP01` prevents
copying policy into the nonrelease controller family.

### AUDIT-010-F003 — WebDAV can publish a partial runtime

`A10-F003-01` **Statement/severity.** High. WebDAV startup can create and
publish its listener and accept task, fail application-worker creation, return
failure without rollback, then return success on a later call although the
runtime cannot serve admitted filesystem work.

`A10-F003-02` **Actors/source.** P4 `storage/webdav/runtime.cpp::startRuntime`
and the wired-network caller; coverage `A10-COV009` and `A10-COV012`.

`A10-F003-03` **Contract.** Startup must be atomic: success means every required
worker is ready; failure owns and retires every socket/task created by the
attempt; retry must inspect complete readiness.

`A10-F003-04` **Evidence/counter-evidence.** Source publishes `acceptTask` before
creating the application worker. The second failure path neither closes the
listener nor retires the accept task, and the entry guard later treats non-null
`acceptTask` as success. Listener creation failure itself does close its socket.

`A10-F003-05` **Consequence/confidence.** High confidence. A rare task-allocation
failure produces stale readiness, leaked process-lifetime resources and a live
network endpoint unable to complete its advertised service.

`A10-F003-06` **Owner/validation/disposition.** Extender WebDAV runtime owns the
repair. Accept for repair using staged local ownership and publish only after
both workers are ready. A host seam must fail each socket/task step, prove
reverse-order cleanup and then prove a clean retry.

`A10-F003-07` **Lineage/duplicates.** Project-new under `A10-LIN03` and
`A10-UE02`; no upstream or project-equivalent WebDAV transaction was found.

### AUDIT-010-F004 — Network services overcommit the selected socket budget

`A10-F004-01` **Statement/severity.** Medium. The ordinary profile selects ten
lwIP sockets while video HTTP requests seven client plus three internal sockets,
local-SD HTTP requests two plus three, and WebDAV can hold a listener and one
client: seventeen potential sockets before other component users.

`A10-F004-02` **Actors/source.** P4 boot/network composition,
`HttpVideoService`, `storage/local/http.cpp`, WebDAV runtime and selected
sdkconfig; coverage `A10-COV008`, `A10-COV009`, `A10-COV011`, `A10-COV012`,
`A10-COV034` and `A10-COV035`.

`A10-F004-03` **Contract.** Each advertised concurrent-service limit must fit an
application-wide socket budget or be rejected/admitted explicitly.

`A10-F004-04` **Evidence/counter-evidence.** The configured contradiction is
source-proven. Actual traffic rarely reaches all independent maxima, so the
audit has not demonstrated a particular user request failing under saturation.

`A10-F004-05` **Consequence/confidence.** High confidence in insufficient
capacity; medium confidence in user-visible frequency. Startup or accepted
connections can fail according to order and unrelated clients.

`A10-F004-06` **Owner/validation/disposition.** P4 boot/network composition owns
one budget. Accept for repair by assigning service shares/admission against a
documented reserve. Static budget tests are required; a hardware saturation run
is optional only if the Author requires observed impact beyond the proven
contradiction.

`A10-F004-07` **Lineage/duplicates.** Project-new integration policy under
`A10-LIN04`, `A10-UE03` and `A10-DUP08`. Services are intentionally distinct;
centralize resource ownership, not protocol implementations.

### AUDIT-010-F005 — The ordinary console profile is an experiment bundle

`A10-F005-01` **Statement/severity.** Medium. The product-development profile
enables temporary diagnostics, bounded experiments and conflicting draw-count
definitions without an itemized product contract.

`A10-F005-02` **Actors/source.** Native build authority and
`vdp/build/p4-profiles.json`; coverage `A10-COV001`, `A10-COV021`,
`A10-COV022` and `A10-COV035`.

`A10-F005-03` **Contract.** An ordinary development profile must declare one
deterministic product behavior. Diagnostics and experiments require separately
named profiles or explicit default-off options.

`A10-F005-04` **Evidence/counter-evidence.** Internal mode20 pools, four drawing
opportunities, output-below-parser, snapshot lookahead and timing/refresh
instrumentation are simultaneously selected. Both `AGON_EXTENDER_DRAW_FOUR`
and `AGON_EXTENDER_DRAW_TWICE` are defined; preprocessor order silently chooses
four. The graph itself is reproducible and excludes forbidden sources.

`A10-F005-05` **Consequence/confidence.** High confidence. Performance, memory
and scheduling observations cannot be attributed to a minimal intended product
configuration, and a later repair can silently depend on an experiment.

`A10-F005-06` **Owner/validation/disposition.** Native build/profile authority
owns repair. Accept for repair before behavioral firmware fixes: classify every
definition as required, diagnostic or rejected; create named diagnostics only
where retained; rebuild and graph-check the minimal profile.

`A10-F005-07` **Lineage/duplicates.** Project-new under `A10-LIN05` and
`A10-UE04`. `A10-DUP01` makes a stable profile especially important; it must
select only one display owner.

### AUDIT-010-F006 — Mutable font state escapes validated storage bounds

`A10-F006-01` **Statement/severity.** High. Application commands can mutate font
geometry and offsets after one initial backing-size check, causing out-of-bounds
glyph access, wrapped stack sizing and application-sized `alloca` on an
8,192-byte worker stack.

`A10-F006-02` **Actors/source.** Retained official-shaped
`agon_fonts.h::{createFontFromBuffer,setFontInfo,getCharPtr}`, context glyph
paths and vdp-gl font drawing; coverage `A10-COV005` and `A10-COV033`.

`A10-F006-03` **Contract.** Every mutable font property and offset table must be
validated against retained backing ownership and size at use or mutation; stack
allocation must have a fixed safe bound.

`A10-F006-04` **Evidence/counter-evidence.** Initial fixed-width creation checks
one size, but later metadata/offset mutation is not revalidated or retained.
`Context::getScreenChar` stores calculated glyph size in eight bits, creates a
VLA of that wrapped size, then fills using full dimensions; the full glyph path
can allocate near the worker stack size. No physical exploit was run.

`A10-F006-05` **Consequence/confidence.** High confidence in source-level memory
unsafety. Supported VDU/buffer input can read/write beyond backing or stack and
crash/corrupt the P4 process.

`A10-F006-06` **Owner/validation/disposition.** The selected VDP compatibility
layer owns an isolated upstream correction. Accept for repair with size-owning
font metadata, validated offset lifetime and fixed bounded scratch. Host
ASan/UBSan tests cover maximum dimensions, short data, offset-table lifetime,
metadata mutation and screen-character capture.

`A10-F006-07` **Lineage/duplicates.** Upstream-unchanged under `A10-LIN06`.
No project-equivalent font owner was found. Preserve official API behavior and
separate any upstream publication decision.

### AUDIT-010-F007 — Numeric conversion retains undefined behavior and two owners

`A10-F007-01` **Statement/severity.** Medium. Active VDP conversion type-puns
through unrelated scalar references/pointers and permits signed `1 << 31`; a
safer project helper handles only one buffered branch.

`A10-F007-02` **Actors/source.** Retained `video/types.h`, buffered conversion in
`vdu_buffered.h`, and `extender/port/fixed_conversion.hpp`; coverage
`A10-COV033`.

`A10-F007-03` **Contract.** Numeric wire conversion must be defined for every
accepted width/shift and use one validation/encoding policy across parser and
buffered paths.

`A10-F007-04` **Evidence/counter-evidence.** `types.h` is byte-identical to
official VDP and violates strict-aliasing rules; signed shift 31 is undefined.
Local `encodeFixed` uses defined math but does not cover all callers. No wrong
value was required to prove language UB.

`A10-F007-05` **Consequence/confidence.** High confidence in UB, medium severity
because present optimizer manifestation is not demonstrated. Results can vary
by compiler/optimization and accepted path.

`A10-F007-06` **Owner/validation/disposition.** VDP compatibility conversion
seam owns repair. Accept for repair after inventorying all callers; use bit-safe
conversion and explicit range/shift rules. Run UBSan plus boundary/golden-vector
tests for every width, shift and parser/buffer entry.

`A10-F007-07` **Lineage/duplicates.** Upstream-unchanged defect under
`A10-LIN07`; partial local duplicate `A10-DUP03`. One checked seam replaces the
path-dependent pair; do not add a third helper.

### AUDIT-010-F008 — Dynamic scanout effects lack current P4 proof

`A10-F008-01` **Statement/severity.** Medium coverage gap. Source retains
Copper palette changes, cursor and hardware-sprite decoration in every selected
row path, but no current deterministic test proves ordered dynamic effects,
clipping and snapshot/browser visibility on the P4.

`A10-F008-02` **Actors/source.** P4 stock scanline port, retained
`decorateScanLinePixels`, output worker and snapshot/browser boundary; coverage
`A10-COV005`, `A10-COV026` and deferred `A10-COV027`.

`A10-F008-03` **Contract.** The P4 executor must preserve upstream scanout-time
effects in native presentation and snapshots before LCD adds another consumer.

`A10-F008-04` **Evidence/counter-evidence.** Source parity and prior bounded
visual evidence support the path. Current active tests do not exercise ordered
Copper spans, overlapping/hidden/clipped hardware sprites and browser capture
in one deterministic scene. No defect is demonstrated.

`A10-F008-05` **Consequence/confidence.** High confidence in the coverage gap;
unknown confidence in any rendering defect. A missed interaction could make
native, browser and later LCD outputs disagree.

`A10-F008-06` **Owner/validation/disposition.** Accept for validation, not repair.
Build one static deterministic fixture with machine-checkable expected regions,
run native P4 and browser capture, and use the unattended completion/failure cue
contract. Repair scope is opened only by a discriminating mismatch.

`A10-F008-07` **Lineage/duplicates.** Ported/adapted under `A10-LIN08` and
`A10-PA04`. The selected stock row port is canonical; `A10-DUP01` forbids
implementing a second effect pipeline as the test remedy.

### AUDIT-010-F009 — Browser page-error attribution is racy

`A10-F009-01` **Statement/severity.** Low. `browser_layout_test.py` closes over
the loop-local `errors` binding, so a late async callback can append to another
iteration or arrive after assertion.

`A10-F009-02` **Actors/source.** Host Playwright test harness; coverage
`A10-COV026`.

`A10-F009-03` **Contract.** Each page run owns its immutable error sink and must
drain/report page errors before close and PASS.

`A10-F009-04` **Evidence/counter-evidence.** Closure binding is source-proven.
Synchronous page close narrows but does not remove the scheduling seam; no known
false pass is retained.

`A10-F009-05` **Consequence/confidence.** High confidence, low impact: a browser
regression may be misattributed or missed.

`A10-F009-06` **Owner/validation/disposition.** Test infrastructure owns repair.
Accept for repair by binding per-page state and adding a delayed-error canary.

`A10-F009-07` **Lineage/duplicates.** Project-new under `A10-LIN09` and
`A10-UE05`; no equivalent current runner was found.

### AUDIT-010-F010 — Maintained guidance invokes the historical build

`A10-F010-01` **Statement/severity.** Low. `docs/shared-p4-services.md` instructs
the operator to run PlatformIO for a routine console check although native
ESP-IDF/CMake is the sole maintained outer build authority.

`A10-F010-02` **Actors/source.** Maintained Extender documentation and gated
historical wrapper; coverage `A10-COV023`.

`A10-F010-03` **Contract.** Routine guidance must invoke the maintained native
entry point; historical reproduction requires explicit acknowledgement.

`A10-F010-04` **Evidence/counter-evidence.** The stale command is direct source
evidence. The historical wrapper fails closed, so it will not silently produce
an unlabelled routine build.

`A10-F010-05` **Consequence/confidence.** Certain but low impact: an operator
receives a confusing failure or is encouraged toward the wrong path.

`A10-F010-06` **Owner/validation/disposition.** Documentation owner repairs the
existing block and checks referenced native commands; no target run is needed.

`A10-F010-07` **Lineage/duplicates.** Project-new under `A10-LIN10` and
`A10-UE06`; no executable duplication applies.

### AUDIT-010-F011 — Filled arc/sector edge branch is unreachable

`A10-F011-01` **Statement/severity.** Medium pending consequence. In the
two-edge filled-row branch, code enters only when `hasLeftEdge` and
`hasRightEdge` are true, then tests `!hasLeftEdge` before emitting the first
edge; that block cannot execute.

`A10-F011-02` **Actors/source.** Selected vdp-gl `displaycontroller.h` filled
arc/sector rasterizer; coverage `A10-COV004`, `A10-COV005` and `A10-COV026`.

`A10-F011-03` **Contract.** Filled arc/sector rows must emit each required edge
for all quadrant and wrap combinations without unreachable state tests.

`A10-F011-04` **Evidence/counter-evidence.** Control-flow defect is source-proven
and unchanged upstream. Neighboring one-part branches emit analogous edges,
but no minimal scene currently demonstrates a pixel error.

`A10-F011-05` **Consequence/confidence.** High confidence in dead logic; unknown
runtime consequence. Severity remains medium until the host shape matrix
distinguishes affected inputs; it may be reduced if outputs are equivalent.

`A10-F011-06` **Owner/validation/disposition.** Accept for validation first. Run
a host-rendered matrix across quadrants, wrap, radii and filled arc/sector modes
against a simple geometric oracle. Repair only the proven cases.

`A10-F011-07` **Lineage/duplicates.** Upstream-unchanged under `A10-LIN11`.
No project duplicate was found; any local fix is an isolated upstream correction.

### AUDIT-010-F012 — Parallel P4 display families have no final retirement boundary

`A10-F012-01` **Statement/severity.** Medium. The selected stock-shaped display
family and a nonrelease controller/compositor family implement overlapping mode,
palette, Copper, rendering, snapshot and frame-service behavior with different
fixes and transaction semantics.

`A10-F012-02` **Actors/source.** Selected stock runtime/controller/scanline
sources, nonrelease `P4DisplayController`, `P4FrameService`, `PlaneStorage`,
`PaletteState`, `PresentationCompositor`, `fabutils_port`, and profile manifest;
coverage `A10-COV003`–`A10-COV005`, `A10-COV021` and `A10-COV022`.

`A10-F012-03` **Contract.** One implementation owns product display behavior.
A parallel qualification implementation must have an explicit retained purpose,
test-extraction plan and retirement condition; repairs must not be copied ad hoc.

`A10-F012-04` **Evidence/counter-evidence.** Profiles prove mutual exclusion, so
there are not two live display owners. Source comparison proves overlapping
facilities and divergence: nonrelease `PaletteState` avoids the selected
`FWBUG-001`, and nonstock `ScreenFacadeAdapter::configure` has rollback behavior
absent from the selected coordinator.

`A10-F012-05` **Consequence/confidence.** High confidence in maintenance risk,
no claim of simultaneous runtime conflict. Tests/fixes can validate the wrong
family or drift silently.

`A10-F012-06` **Owner/validation/disposition.** Architecture/profile owner must
confirm the selected stock-shaped family as product owner, inventory unique
nonrelease tests, extract useful oracles, and define removal/archive conditions.
Accept for architecture correction before display fixes.

`A10-F012-07` **Lineage/duplicates.** Project-owned parallel implementation
`A10-DUP01`; modeline/transaction overlap `A10-DUP02`. Upstream row bodies are
not the duplicate; the second product-shaped ownership stack is.

### AUDIT-010-F013 — CRC32 primitives are repeated across active owners

`A10-F013-01` **Statement/severity.** Low. Telemetry, remote keyboard, SD
framing and EMOS admission repeat the same reflected CRC32 bit loop under
different local functions.

`A10-F013-02` **Actors/source.** Active P4 telemetry/input/storage and EMOS
admission actors; coverage `A10-COV010`, `A10-COV012` and `A10-COV017`.

`A10-F013-03` **Contract.** One target-appropriate primitive should own the
polynomial/update operation; protocol wrappers own seeds, final XOR and skipped
fields.

`A10-F013-04` **Evidence/counter-evidence.** Direct source comparison proves
repeated loops. Existing protocol vectors currently agree; separate P4/eZ80
builds and frozen fixtures legitimately require independently compilable code.

`A10-F013-05` **Consequence/confidence.** High confidence, low present impact.
A future optimization or fix may create wire incompatibility.

`A10-F013-06` **Owner/validation/disposition.** Defer standalone cleanup unless
an owning file changes. Then use one dependency-free primitive per processor
toolchain and preserve protocol wrappers with cross-target golden vectors.

`A10-F013-07` **Lineage/duplicates.** Project-new duplication `A10-DUP06`.
Intentional byte-identical wire-header copies in `A10-DUP05` remain accepted and
are not part of this finding.

### AUDIT-010-F014 — SD path policy is duplicated and implicit

`A10-F014-01` **Statement/severity.** Low. `sdjob` reuses the shared SD transfer
engine but separately validates admitted descriptor paths with a stricter
character set than the shared path validator, without one named policy boundary.

`A10-F014-02` **Actors/source.** Pinned EMOS `lib/sdapp`, `projects/sdserve` and
`projects/sdjob`; coverage `A10-COV018` and `A10-COV019`.

`A10-F014-03` **Contract.** Common confinement and syntax have one owner;
caller-specific restrictions are explicit policy parameters with shared test
vectors.

`A10-F014-04` **Evidence/counter-evidence.** Source proves two predicates and a
stricter `sdjob` forbidden-character set. The finite admitted job has a different
trust/lifetime boundary, so stricter policy can be intentional. No accepted path
is known to fail incorrectly.

`A10-F014-05` **Consequence/confidence.** High confidence in implicit divergence,
low current impact. Future paths can be accepted by one frontend and rejected by
the other without a documented reason.

`A10-F014-06` **Owner/validation/disposition.** Accept for contract clarification
and a shared path corpus before code consolidation. `lib/sdapp` owns common
syntax/confinement; `sdjob` may retain explicit stricter admission.

`A10-F014-07` **Lineage/duplicates.** Project-new duplicate `A10-DUP07`.
The two services' session models are intentionally distinct and are not to be
merged.

## Existing authoritative findings carried into A10-07

These IDs remain authoritative. Their original evidence and dispositions are in
the [firmware-bug register](../../firmware-bugs.md); this table supplies
AUDIT-010 lineage, scope and review recommendation without creating aliases.

| Existing ID | Severity / evidence in this audit | Lineage and duplicate result | Proposed A10-07 disposition |
|---|---|---|---|
| `FWBUG-001` | High; source-proven with retained physical P4 crash | `A10-LIN12`: inherited erase/iterator defect inside a guarded adapted file. `A10-DUP01` shows the nonrelease palette implementation does not contain the same defect; it is not the product owner. | Accept isolated selected-vdp-gl repair plus existing host reproducer and palette/Copper regression; do not switch display families as the fix. |
| `FWBUG-006` | Medium; source-proven parser-consumption gap | `A10-LIN13`: project-new empty P4 adapter; official updater supplies the grammar/consumer but not a P4-compatible OTA action. | Accept consume-and-report adapter repair derived from official grammar; validate every selector/payload followed by an ordinary VDU command. |
| `FWBUG-007` | Medium unresolved candidate; source concern, manifestation unproven | `A10-LIN14`: relevant completion/swap behavior is upstream-unchanged; no duplicate product owner is accepted. | Validate first under the existing bounded UPSTREAM-001 trigger; repair only demonstrated/applicable subconditions. |
| `FWBUG-008` | High; source-proven and physically demonstrated on EMOS | `A10-LIN15`: unchanged official MOS raw-write dispatch retained by EMOS. Ordinary FatFS and `sdserve` are different paths. | Accept EMOS/MOS wrapper correction using existing mos-tests raw-write control and physical evidence; coordinate the owning repository rather than duplicating the fixture. |
| `FWBUG-009` | Medium; source-proven and physically demonstrated on EMOS | `A10-LIN16`: unchanged official MOS missing return retained by EMOS. | Accept one wrapper-return correction with existing label tests; preserve actual FatFS status. |
| `FWBUG-010` | Medium; source-proven, no physical injection | `A10-LIN17`: inherited missing minimum-length validation in an EMOS-adapted receiver. | Accept per-reply length validation using the retained complete-then-short packet trigger; keep private graphics and general validation distinct. |
| `FWBUG-012` | High; source-proven lifetime defect, isolated physical trigger absent | `A10-LIN18`: upstream-unchanged operand/bitmap/sprite lifetime; P4 locks do not retain ownership. | Accept ownership repair only after the existing bounded trigger suite establishes all-buffer, managed-point and active-sprite cases; preserve D012 ordering. |

## Independent validation proposals

No proposal below is authorization to alter firmware, run hardware or revive a
historical fixture. Host proposals become part of the A10-07 repair plan if the
Author accepts them. Hardware proposals require a later explicit procedure and
authorization and must satisfy A10-T01 through A10-T09.

| Proposal | Findings | Smallest discriminating validation | Decision produced |
|---|---|---|---|
| `A10-VP01` | F001 | Host seam injects failure at every viewport pool/table/DMA row, controller construction, clock start and worker attach step while recording old/new object and published-mode state. | Separates allocator safety from P4 transaction rollback and defines exact repair clauses. |
| `A10-VP02` | F001, F002 | After a candidate, bounded P4 early/late mode8↔20 matrix with browser absent/present and assets absent/loaded; record capability-specific free/minimum/largest blocks and first failed allocation. | Determines whether the retained mode20 symptom is total/capability exhaustion, fragmentation, task failure or transaction failure. |
| `A10-VP03` | F002 | Host allocation policy tests fail each snapshot slot and codec block with zero browser demand and active demand. | Proves basic display independence and graceful codec degradation. |
| `A10-VP04` | F003 | Fake socket/task factory fails every WebDAV startup step, verifies reverse cleanup, complete readiness and retry. | Proves atomic startup without hardware. |
| `A10-VP05` | F004 | Static selected-config budget assertion with declared reserves; optional bounded simultaneous-service P4 saturation only if observed impact is needed. | Proves capacity coherence; optional run measures user-visible order effects. |
| `A10-VP06` | F005, F012 | Manifest test classifies every definition/source, rejects conflicting product flags and proves exactly one display family linked. | Freezes the product owner and behavioral baseline before firmware repairs. |
| `A10-VP07` | F006 | Host ASan/UBSan font corpus for short backing, mutable dimensions, maximum glyph, invalid/short offset table, destroyed offset buffer and screen-character copy. | Establishes memory-safe bounds and lifetime behavior. |
| `A10-VP08` | F007 | UBSan plus golden conversion matrix for all widths, shifts, special floats, parser and buffered entry points. | Establishes one defined numeric contract and complete caller migration. |
| `A10-VP09` | F008 | Static deterministic Copper/cursor/sprite scene with native-region oracle and browser byte capture; later reuse for LCD. | Determines parity across native and snapshot outputs without game variability. |
| `A10-VP10` | F009 | Delayed page-error canary bound to two consecutive pages. | Demonstrates that each run owns and drains its error sink. |
| `A10-VP11` | F011 | Host shape matrix for filled arcs/sectors across quadrants, wrap and radii against a simple edge oracle. | Determines whether the dead branch changes pixels and bounds repair. |
| `A10-VP12` | F013 | Cross-target CRC golden vectors, incremental splits and embedded-field-skip cases. | Permits shared primitive extraction without wire drift. |
| `A10-VP13` | F014 | Shared accepted/rejected path corpus annotated as common syntax, confinement or stricter job policy. | Converts accidental difference into explicit policy before consolidation. |

## Dependencies and review order

`A10-ORD01` — Review and, if accepted, repair F005 and resolve F012 before
building or benchmarking display fixes. They establish the profile and product
display owner against which all later evidence is meaningful.

`A10-ORD02` — Within display work, separate F001 allocator safety, F001 P4
transaction ordering, FWBUG-001 palette cleanup, and F002 browser allocation
policy. They may share regression tests but require independent commits and
receipts.

`A10-ORD03` — F008 and F011 are validation-first. FWBUG-007 and FWBUG-012 retain
their existing validation/ordering boundaries. No speculative renderer rewrite
is part of an accepted repair merely because these items are present.

`A10-ORD04` — F003 and F004 can be handled after the profile baseline and before
combined network tests. F004's source contradiction does not require a target
saturation run to authorize a coherent budget.

`A10-ORD05` — F006 and F007 are independent host-first safety repairs. Their
upstream origin does not require changing read-only official repositories; the
project may carry isolated compatibility corrections with provenance.

`A10-ORD06` — F013 should normally ride with an already accepted owner change
rather than become a standalone cleanup tranche. F014 begins with contract and
test-corpus clarification, not an assumed merged policy.

`A10-ORD07` — Existing EMOS FWBUG-008 through FWBUG-010 remain component-owner
changes in the pinned development lineage. Their existing fixtures are reused;
AUDIT-010 must not fork duplicate MOS tests.

## Explicit limits and disposed inputs

`A10-LIM01` — Clang-Tidy fully parsed 15 of 33 actual-action P4 units; 18 failed
under recorded embedded-dialect/target-model limits. Cppcheck attempted all 33
with two preprocessor-model failures. Complete manual source review covers the
closure, but automated silence in failed units is not negative evidence.

`A10-LIM02` — Offline OSV produced no useful coverage for the ESP-IDF lock,
managed components, vendored C++ or tool pins. This is a vulnerability-survey
limit, not a finding that a dependency is safe or vulnerable.

`A10-LIM03` — `A10-DUP04`, `A10-DUP05`, `A10-DUP09` through `A10-DUP13`, and
the intentional separations `A10-ND01` through `A10-ND06` do not receive repair
findings. The ZDI sources in `A10-DUP04` are explicit retired historical
tombstones beside one maintained recovery owner; the standalone USB program in
`A10-DUP09` is a frozen superseded diagnostic. Their retained/fail-closed
status, exact-copy tests, distinct contracts, shared implementation or
negligible risk are the recorded dispositions.

`A10-LIM04` — No current evidence joins the retained mode20 failure,
FWBUG-001 palette crash, FWBUG-007 completion concerns, FWBUG-012 operand
lifetime or historical sprite crashes into one cause.

`A10-LIM05` — LCD source remains outside this baseline. After accepted audit
repairs, LCD-001 must redeploy LCD as a reviewed delta and rerun early/late mode,
assets, browser, scanout-effects, colour and edge/geometry regressions.

## A10-07 handoff

`A10-RG01` — A10-07 reviews all fourteen `AUDIT-010-Fnnn` findings, seven carried
FWBUG identities, thirty-five coverage rows, thirteen validation proposals and
five explicit limits as one complete set.

`A10-RG02` — The Author records one disposition for each finding: accept for
repair, accept validation first, defer with owner/condition, or reject with
rationale. Acceptance of a finding is not yet permission to change source.

`A10-RG03` — After those dispositions, A10-07 produces one manually numbered,
dependency-ordered repair plan. The Author approves that complete plan before
A10-08 changes executable product code.

`A10-RG04` — Any accepted host or physical suite adopts the unattended status,
durable timing, Legacy completion/failure display and audible cue contract. A
test failure must leave its error visible after the cue when the mainboard
remains controllable.
