# PORT-008 current-circuit production-equivalence audit

- Status: Software-only production data plane and ordinary/fixed EMOS
  compositions integrated; provenance, target-runtime, activation, return,
  artifact, and physical gates open
- Date: 2026-09-01
- Owning task: [PORT-008](../../PORT-008.md)
- Corrective action:
  [`CA-2026-09-01-001`](../../../decisions/CA-2026-09-01-001-port008-preactivation-ready.md)
- Integrity audit:
  [`AUDIT-2026-09-01-001`](../../../decisions/AUDIT-2026-09-01-001-open-task-and-implementation-integrity.md)

## Purpose and placement

This task-local audit answers one bounded question: which work can use the
present `light2-harness-r01` circuit while executing code intended to remain
unchanged in production, and which work would exercise only a temporary r01
workaround?

The record belongs in the PORT-008 task silo because it selects an
implementation and qualification boundary, not a new system architecture or a
production transport authority. When stable transport interfaces are accepted
and implemented, PORT-008 must promote them into a durable role-named transport
document and leave this file as decision and evidence traceability.

No current working-copy source or concurrent hardware-document change was used
as authority in the initial boundary review. Dirty P4 and EMOS transport files
were inspected only through their committed Git objects. That review performed
no build, deployment, wiring change, reset, or powered operation. The later
authorized software-only execution is recorded separately below.

## Answer

The current circuit is useful for a substantial but sharply bounded production
slice: the complete **forward-parallel data plane inside one already-authorized
parallel epoch**. The eZ80 and P4 endpoint pins, bit order, CLOCK sample edge,
`VALID_N` polarity, and `READY_N` assertion/release meaning are identical in
r01 and the committed r02 candidate. Production EMOS sender code, production
P4 PARLIO ingress code, the retained VDU parser, and the retained display and
browser pipeline can therefore execute unchanged on r01 after those components
are separated from prototype activation and return-transport behavior.

The current circuit cannot safely execute the intended full-duplex UART state.
On r01, the r02 UART enable tuple would enable opposing PC1 drivers at once.
Nor can r01 qualify production activation, response delivery, flow control,
electrical break-before-make, reset, either-order power, isolation, or r02
timing. Those areas must wait for the intended circuit or use host-only models.

The permitted bridge is a separately identified, non-release, fixed-backend
qualification composition. It may call the same production epoch-entry and
data-plane APIs that the future activation coordinator will call, but it may
not add an r01 protocol, product conditional, fake success path, supported
runtime bypass, or alternate VDU grammar. It proves behavior only from the
active-parallel call boundary inward; it does not prove why or how that state
was authorized.

## Authority and identity boundary

1. The reviewed `agon-extender` source identity is
   `a495911945e8b4f55c95a00e901cd93cb5b68c73`.
2. The reviewed EMOS identity is
   `0e24b06abdb322fdb4e681a21242ccfebfc8ea65`. Its dirty PORT-008 files were
   read only with `git show` at that commit.
3. Official contracts were reviewed at `agon-docs`
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, official VDP v2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, and official MOS
   `5f67b1ca77eb7a77d3b37cc7b029db51f0d1548e`.
4. The current-circuit design authorities are
   [`light2-harness-r01`](../../../../hardware/designs/light2-harness-r01/README.md)
   and
   [`light2-extender-solderless-assembly-r01`](../../../../hardware/assemblies/light2-extender-solderless-assembly-r01/README.md).
   The last tracked physical record identifies that pair, but the exact present
   bench specimen remains machine-local and must be confirmed powered off
   before another run.
5. The intended comparison authority is committed
   [`light2-harness-r02`](../../../../hardware/designs/light2-harness-r02/profile.yaml).
   F008's schematic digest and generated projections were reconciled to the
   committed authority on 2026-09-01, so the identity is no longer stale. Its
   initial physical assembly remains draft with no construction authority,
   and no electrical or qualification claim follows from that repair.
6. R02 is a controlled-beta candidate core, not yet a complete production
   electrical claim. Its own eZ80-only reset and Legacy electrical-absence
   questions remain open. This audit does not infer answers for them.

Relevant official sources are the pinned
[VDP byte-stream description](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/VDP.md),
[MOS RST API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md),
[retained VDU Stream boundary](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h),
[General Poll implementation](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h),
and
[official MOS reset vectors](https://github.com/AgonPlatform/agon-mos/blob/5f67b1ca77eb7a77d3b37cc7b029db51f0d1548e/src_startup/vectors16.asm).

## Classification rules

1. **Production-identical** means the same maintained source and object code,
   with the same state preconditions, endpoint constants, error semantics, and
   parser-visible bytes. A different artifact identity or qualification
   top-level does not change that component's code. This is an artifact claim,
   not an inference from matching source: a future linker-provenance target-
   object gate must prove it mechanically. Host-native objects establish same-
   source behavior only. The current preliminary checker described below does
   not prove this classification.
2. **Qualification composition only** means an explicitly non-release caller,
   fake HAL, scripted peer, or fixed-backend profile invokes a production API
   or supplies its external precondition. It may observe and fault-inject, but
   it cannot claim the omitted activation or hardware behavior.
3. **Predecessor evidence only** means r01 can inform a value or test case but
   changed circuitry prevents the result from qualifying r02.
4. **Must wait** means running the intended production state on r01 would be
   electrically unsafe, semantically false, or incapable of observing the
   required result.

### Current evidence-tool limitation

The genuine Work 2.e gate is now specified and implemented under
[`object-equivalence/`](object-equivalence/README.md). It consumes generic EMOS
and P4 raw actual-step records, authenticates clean source/capture/tool
authority, owns the complete role/unit/symbol sets in tracked policy, binds
each required object to the final link and nonzero map contribution, and
compares independently captured qualification/release objects plus normalized
linked instructions. The product gate remains unexercised on target evidence;
no approved successor firmware/procedure identities exist, and no production
P4 release consumer exists. Work 2.e therefore remains open and no production
equivalence report exists.

The historical `validate-target-object-equivalence.py` remains only a
preliminary compile-output/final-symbol similarity checker. It does not prove
actual linker consumption, Git/source/tool authority, or the EMOS assembly
boundary. It is explicitly superseded for Work 2.e claims, but retained to
interpret preliminary records. No preliminary report is D002
object-consumption evidence.

## Electrical equivalence matrix

| Operation | r01 | Intended r02 | Disposition |
|---|---|---|---|
| eZ80 `PC0..PC7` to P4 data | GPIO22, 12, 23, 11, 32, 10, 33, 9 | Exact same endpoints | Production-identical endpoint constants, bit order, and byte values |
| eZ80 `PD5/CLOCK` to P4 | GPIO14 | Exact same endpoint | Production-identical logical edge and receiver pin; r01 timing is predecessor-only |
| eZ80 `PD7/VALID_N` to P4 | GPIO13, active low | Exact same endpoint and polarity | Production-identical record-delimiter semantics |
| P4 GPIO20 to eZ80 `PD4/READY_N` | Direct P4 open-drain sink | GPIO20 controls a low-only U4 sink | Production-identical assert-low/release operation in stable powered use; no transferred isolation or edge claim |
| Stable parallel enable state | GPIO15 low enables buffered D0/D1; GPIO17 is unconnected; GPIO21 released | GPIO15 and GPIO17 low enable all forward banks; GPIO21 released | Production tuple `(GPIO15=0, GPIO17=0, GPIO21=released)` functions on both |
| All-released state | Disables only r01 PC0/PC1 buffers; other forward wires remain connected | Disables every forward and return buffer | Not electrically equivalent; r01 cannot qualify Legacy absence or r02 break-before-make |
| Full-duplex UART state | GPIO15 low enables the r01 PC1 forward driver while GPIO21 low enables its opposing reverse driver | Separate forward and return banks support full duplex | **Unsafe and prohibited on r01**; intended production UART code must not run there |
| UART RTS/CTS and target rate | Only a bounded two-wire/direction-switched 115,200-baud predecessor experiment | Four-wire 1,152,000-baud UART with RTS/CTS | Pin constants only; all functional UART claims must wait |
| Bias, buffering, damping, and load | One HC125, direct lines, different series placement | Two LVC244 plus two LV125, full bias and series network | No r02 waveform, margin, contention, or loading claim |
| Power and reset | Controlled order; HC125 lacks selected `Ioff`; direct cross-domain controls | Separate domains and low-only controls, still awaiting complete qualification | No either-order-power, back-power, P4-reset, eZ80-reset, or final V1 claim |

## Initial design baseline and current disposition

The control, object-factoring, and host/build sections below preserve the
accepted initial design requirements. Their status annotations reconcile those
requirements with the later execution record; unannotated imperative wording
is a retained constraint, not evidence that implemented work remains undone.

### Control representation required for unchanged use

The production P4 control API should express each active-low control as either
**assert low** or **release**. The recommended P4 GPIO representation is
open-drain low versus high-impedance release for GPIO15, GPIO17, GPIO21, and
GPIO20:

1. On r01, this avoids a P4 push-pull high into Agon-powered enable pull-ups.
2. On r02, the P4-domain pull-ups release U4 inputs and an open-drain low
   enables the intended low-only sinks.
3. The logical parallel tuple is unchanged, and unconnected r01 GPIO17 needs no
   r01-specific no-op in production code.
4. This common representation does not make the circuits electrically
   equivalent during reset or partial power. Those claims remain excluded.
5. Before asserting either parallel-forward enable, production P4 code must
   remove UART2 output ownership from shared GPIO12 and GPIO11, configure the
   complete parallel input pad set, arm PARLIO, and only then admit the eZ80
   sender. GPIO11 is a direct r01 forward conductor, so an enabled P4 UART RTS
   pad there would be unsafe even if every external buffer enable were
   released.

At initial review the exact GPIO initialization and reset policy required
implementation. `P4EpochHardware` now implements the active-parallel ordering
in maintained source; target-runtime GPIO, reset, partial-power, and electrical
qualification remain open. This requirement and status do not authorize a
physical operation.

## Production code boundary

### P4/EDP

No predecessor P4 transport class is promotable unchanged. The retired
`ForwardParallelStream` combines r01 identity, boot-time activation, PARLIO,
buffering, open-drain READY, and discard-success return behavior. It also owns
no committed GPIO15/GPIO17/GPIO21 implementation, waits forever for external
CLOCK, leaks partial startup resources, poisons retry state, and publishes
callback state through an unproved `volatile` handoff.

The accepted production boundary separates these roles:

These began as descriptive working names. The implemented names below are now
maintained internal source names; they still do not freeze a public API.

1. **Implemented software-only:** `ExtenderVdpStream` is the one production
   `Stream` passed to the retained
   `VDUStreamProcessor`. It reads ordered bytes from parallel ingress and
   delegates exact packet bytes to an injected output interface. The eventual
   production binding will use `P4UartReturn`; the implemented qualification
   binding uses a byte-capturing observer. The Stream contains no discard-
   success branch.
2. **Implemented software-only:** `P4ParlioIngress` owns the PARLIO unit,
   delimiter, DMA storage, bounded
   active-record completion, indefinite sender-idle wait, byte queue,
   cancellation, stop, and reverse-order cleanup. It does not authorize an
   epoch or write control GPIOs directly.
3. **Implemented active-parallel subset; target-runtime proof open:**
   `P4EpochHardware` is the sole owner of GPIO15, GPIO17, GPIO21, and GPIO20
   plus shared-pad mux and direction changes. It disables the GPIO12/GPIO11
   UART TX/RTS outputs before enabling a parallel-forward bank, and it accepts
   READY requests only under a live parallel epoch lease. The non-release top
   level supplies that fixed lease; the future production coordinator will own
   it. The active-parallel path is production-identical on r01.
4. **Open return tranche:** `P4UartReturn` will own UART2 output, RTS/CTS
   behavior, bounded failure, and teardown. It must not be physically selected
   on r01.
5. **Open activation tranche:** `ActivationCoordinator` will own authorization,
   break-before-make, epoch
   transitions, rollback, shutdown, and reset invalidation. A qualification
   top-level may call its already-authorized active-parallel boundary, but r01
   cannot exercise the production request carrier or prove its transition.

The retained parser, display controller, frame service, compositor, snapshot
pool, wired network service, browser provider, and web client remain the real
production path after `ExtenderVdpStream` supplies bytes. Physical ingress
must initially use a command corpus that does not enter the known reachable
audio/updater empty-handler defect. No EMOS filter or alternate grammar may be
added to hide that parser limitation.

### EMOS/eZ80

No complete committed r01 physical adapter is promotable unchanged. The useful
production seams are narrower:

1. **Integrated and linked in v10:** the RST 10, RST 18, and C-runtime entry
   points call the one EMOS semantic VDU dispatcher. The mode coordinator
   remains the only supported route-commit owner.
2. **Local/fixed ownership integrated; production activation open:** the EMOS
   parallel-epoch owner is the sole actor that changes
   eZ80 UART1 versus GPIO mux/direction on `PC0..PC7` and `PD4/PD5/PD7`. It
   prepares idle output latches before enabling output drivers and supplies a
   lease only after local preparation and the caller's accepted peer-readiness
   condition. The fixed profile passes the procedure-controlled assertion
   carried by its explicit mode request; EMOS has no separate external
   attestation channel. Failure restores or retains ownership fail-closed.
3. **Integrated:** the epoch-preconditioned parallel record engine uses the same
   `PC0..PC7`, `PD4/READY_N`, `PD5/CLOCK`, and `PD7/VALID_N` operations on r01
   and r02. It receives an already-owned parallel epoch from the EMOS transport
   coordinator; it does not perform activation, General Poll readiness,
   whole-mode commit, or whole-port policy itself.
4. **Implemented in host/link evidence:** the engine preserves byte order and
   flattens physical records below the
   raw VDU stream. A nonzero RST 18 length above the selected physical-record
   maximum is split without adding a length or command envelope. VDU
   commands may cross records, and multiple application calls may share parser
   state.
5. **Implemented; target-runtime proof open:** the engine bounds READY admission
   and completion, restores idle
   `CLOCK`/`VALID_N`, releases its busy state, and reports failure to the EMOS
   lifecycle owner. It must not disable interrupts for an entire maximum-size
   record without a separately proved latency and UART-ingress contract.
6. **Implemented separation; response coexistence open:** epoch pin acquisition/
   release and the sender hot loop are separate so qualification can test both
   independently without copying the prototype's global interrupt exclusion.

The predecessor `PORT008_send`, precommit General Poll, 4096-byte rejection,
spin-count deadlines, r01 register snapshot, discard-only readiness inference,
and former `port/port008-forward.mk` behavior remain historical qualification/
prototype evidence. The production engine preserves only their proven pin and
cadence invariants; it is not a line-for-line repair of that adapter, and the
former EMOS profile is now a fail-fast supersession marker.

## Work that can proceed before the intended circuit

### Host and build work using production source

The following work needs no physical circuit and can exercise the eventual
production classes themselves:

1. Factor the P4 objects above behind injected GPIO, clock, PARLIO, queue, and
   UART interfaces. Host tests use fakes at those interfaces; production code
   contains no `UNIT_TEST`, r01, or fake-success branch.
2. Prove safe default state, ordered parallel entry, READY-after-arm, bounded
   stopped-CLOCK and stuck-VALID abort, direction release before teardown,
   every partial-start failure, retry, cancellation, stop, and callback/task
   synchronization.
3. Prove record flattening, every byte value, ordered repeated records, queue
   backpressure, short/maximum records, and parser command boundaries that
   split immediately before and after physical-record limits.
4. Instantiate the real retained `VDUStreamProcessor` with a heap-owned
   scripted duplex `Stream`; feed exact General Poll and safe visible VDU bytes;
   capture the complete exact output sequence, including the General Poll
   packet and the Mode Information packet emitted when startup wait exits; and
   verify the retained display/frame result. The fixture must respect the
   upstream constructor's ownership of its raw `Stream *` rather than passing a
   stack object that the processor may own.
5. Factor the EMOS parallel engine below the existing semantic dispatcher and
   test Port C bytes, `VALID_N`/CLOCK cadence, READY deadlines, chunking,
   register postconditions, cleanup, and internal lifecycle failure reporting
   through host/emulator and linked-image checks. Public RST-call failure
   semantics remain a separate compatibility decision; factoring must preserve
   the present de-facto successful return behavior unless that decision changes
   it.
6. Repair F007 build-to-source provenance before any staged artifact supports
   a decision-bearing claim. Repair F014 capture-oracle coverage before a logic
   trace is accepted. Reconcile F015 version records for any new controlled
   package.

Execution status: the initial lower-layer completion statement was superseded
by local P4 defects P017 through P021. Their corrected bounded host/source pass
now completes 25 sanitizer cases and 46 task-local Python tests for item 1 and
the lower-layer portions of items 2 and 3; target-runtime control behavior and
retained-parser execution remain open. Item 4 remains target-native work. Item
5's EMOS host/link portion is complete, while emulator and target-runtime
evidence remain open. Item 6's
source/object provenance, controlled-package, and physical capture-evidence
gates remain open.

Work item 4 is not yet executable as a host runtime test. The
[retained-parser fixture feasibility record](retained-parser/README.md)
documents the missing target-runtime seam, rejects the older/classic
userspace closure as a substitute, defines the target-native removal test, and
separates the bounded source/composition guards from real parser/display
evidence.

These tests can establish production software behavior. They cannot substitute
for r02 electrical qualification.

### Physical r01 work using production source

After the prerequisites below, r01 can execute this exact production chain:

```text
ordinary RST 10 / RST 18
  -> EMOS semantic dispatcher
  -> production epoch-preconditioned parallel engine
  -> PC0..PC7 + PD4/PD5/PD7 on r01
  -> production P4 active-parallel controls and PARLIO ingress
  -> production ExtenderVdpStream
  -> retained VDUStreamProcessor
  -> retained display/frame/snapshot/browser pipeline
```

The bounded physical program can cover:

1. single-byte and block writes, all eight data bits, fixed and generated byte
   patterns, repeated records, zero application-level framing, and exact order;
2. lengths around the physical record limit, including a bounded RST 18 block
   split into multiple records while the parser sees one continuous stream;
3. VDU sequences split at arbitrary record and RST-call boundaries, proving
   that physical records carry no command semantics;
4. READY admission/backpressure, receiver queue saturation, sender timeout,
   receiver stopped-CLOCK/stuck-VALID abort, and the production software
   cleanup/retry path, using separately identified fault fixtures rather than
   product conditionals. R01 can observe READY, GPIO15, GPIO21, retry, and
   parser integrity; it cannot prove r02's external bank disable, GPIO17 load,
   isolation, or break-before-make behavior;
5. the existing safe visible VDU fixture and independent RGB888 frame hash,
   with browser connection treated only as an observation requirement;
6. repeated transfers and a bounded soak across EMOS, the physical forward
   path, parser, renderer, snapshot publication, and browser delivery; and
7. r01-specific throughput and electrical observations, clearly labelled as
   predecessor evidence rather than r02 timing qualification.

### Compatibility-command breadth on r01

The raw forward link does not need a command whitelist. Once the production
record engine and ingress flatten records into one byte stream, every retained
command in the current
[SETUP-004 VDU inventory](../../SETUP-004/VDU-inventory.md) can traverse the
same production data plane when the accepted mode architecture selects EDP.
Whether r01 can qualify the command's complete effect depends on what the
command requires after ingress:

| Command class | What r01 can establish with production code | Claim boundary |
|---|---|---|
| Text/control, colour/palette, graphics/plot, viewports/origins, fonts, bitmaps/sprites, buffers/matrices/compression, tile/Copper/context, scaling, flush, and other forward-only retained display operations | Exact RST-call bytes reach the real parser and retained P4 consumer; deterministic P4 state, frame, snapshot, and browser results can be checked | Subject to the owning PORT-003/command fixture; this is forward-path and presentation evidence, not whole-mode qualification |
| Screen-mode changes and other operations that also emit Mode Information | The real mode change and display/frame result execute, and the qualification output observer captures every generated packet byte | No UART delivery, MOS mode/sysvar update, or response timing claim |
| General Poll and synchronous read/query commands such as cursor, character, pixel, palette, or variable queries | The real request parser and packet generator execute; exact generated bytes and ordering can be captured locally | No EDP identity, return transport, canonical MOS parser, completion flag, or sysvar claim |
| Buffered/callback operations that generate later packets | Forward registration and retained P4-side state may be exercised where its owner has a deterministic fixture; generated output may be captured | No asynchronous UART delivery, session validity, event ordering, or eZ80 consumption claim |
| Keyboard, mouse, RTC, audio, and other input-, return-, or currently incomplete consumer classes | Raw delivery and complete grammar consumption may eventually be transport tests | No functional claim now; response ownership, device integration, or known reachable empty handlers block it |
| Printer, console/terminal, Intel HEX/YMODEM, updater, and other architecture-excluded facilities | Nothing beyond proving that a selected safe rejection consumes the complete grammar | They are not made production requirements merely because the forward wire can carry their bytes |

This classification avoids two opposite mistakes: restricting the r01 run to
one decorative demo when the production forward path can carry the selected
display corpus, or treating successful ingress as proof of a return path or an
unfinished command consumer. The SETUP-004 inventory remains the command-scope
authority pending QUAL-001 Review Gate 2. The generated three-mode matrix is
superseded candidate data and supplies no current architecture authority; this
audit only classifies what the current circuit can observe.

The exact General Poll parser function may run in this fixed-backend
composition so the retained parser leaves its stock startup wait, but its
captured, non-transmitted response cannot establish EDP identity, EMOS
readiness, MOS sysvars, or production activation. The qualification adapter
emits no precommit Poll. After the non-release fixed backend commits using the
procedure-controlled assertion carried by its explicit mode request, the first
ordinary RST 18 fixture sends the exact Poll through the production dispatcher
and record engine; only then does the visible fixture follow. This tests the
real parser startup function without promoting the prototype's Poll-before-
commit sequence into the production lifecycle.

## Qualification-only composition

The minimum acceptable composition is independent of r01 and reusable for
later data-plane qualification on the intended circuit:

1. A non-release P4 top-level initializes the production objects in Safe,
   explicitly selects only their active-parallel call boundary, and never
   links or calls a UART state on r01. It uses production shared-pad, GPIO, and
   PARLIO code from that boundary onward and proves the GPIO12/GPIO11 UART
   output drivers disabled before any parallel-forward enable is asserted.
2. A non-release EMOS profile binds the existing mode command to a fixed
   adapter whose only substitution is the procedural precondition that the
   operator or qualification top level has already prepared the peer's parallel
   epoch. EMOS does not discover or validate that condition: the explicit mode
   request asserts it for this identified composition. The adapter emits no
   activation or precommit General Poll. Ordinary VDU calls after the fixed-
   backend commit then use the production dispatcher and production parallel
   engine.
3. The composition has a separately approved identity, manifest, source
   closure, and non-production banner. Its target-object record freezes the
   target compiler, relevant flags/defines, compile commands, and cryptographic
   digests of every claimed production object or archive member. The intended
   P4 and eZ80 release compositions must link target objects with the same
   digests and mechanically compare linked symbols and normalized disassembly;
   a host-native build is not object-equivalence evidence. The production
   release manifest excludes the qualification top-level/profile and proves no
   supported runtime bypass exists.
4. The composition does not expose a new application command, wire grammar,
   network activation, browser activation, timed auto-arm, or circuit-specific
   product branch.
5. The qualification output binding captures every parser-generated byte and
   reports only capture acceptance to `ExtenderVdpStream`; it neither discards
   bytes invisibly nor impersonates UART delivery. The production release links
   `P4UartReturn` at the same injected interface. Because the retained parser's
   byte-write helper ignores the return value, `ExtenderVdpStream` and
   `P4UartReturn` must also latch a write failure through an out-of-band
   lifecycle/fault interface. The real retained-parser fixture must inject
   failure at every General Poll and Mode Information output byte; a short
   write must remain observable and must not become readiness or formal-mode
   evidence. Current host evidence covers the production Stream/data-plane
   side at every source-derived startup-packet byte offset, but does not
   execute the parser or display closure.
6. The evidence claim begins at “active parallel epoch supplied” and ends at
   the observed forward consumer. It says nothing about production activation,
   UART return, formal-mode commit, or electrical equivalence.

The Work 2.e product gate under `object-equivalence/` now implements item 3's
required final-link replay, direct map contribution, symbol-origin, Git,
source, tool, identity, and cross-role comparison checks. Its tracked intended-
command fingerprints still await a clean rehearsal, and no eligible target
capture has passed it. Item 3 therefore remains a gate rather than an achieved
evidence claim. The preliminary similarity checker remains historical input
only and is superseded for this claim.

This is test scaffolding, but it is not a circuit bodge: it supplies a missing
external precondition at a stable product interface and leaves every
data-plane component under test unchanged.

## Software-only execution result

1. The P4 production boundary is implemented as separate epoch-hardware,
   transactional PARLIO ingress, flattened queue, data-plane, retained-parser
   Stream, output-fault, and target-adapter objects. The maintained objects
   contain no r01 or test-success conditional. A separately selected
   non-release P4 top level links these objects into the real retained parser,
   display, frame, snapshot, wired-network, and browser source closure while
   capturing generated output visibly instead of claiming UART delivery.
2. At this earlier software-only checkpoint, the P4 sanitizer binary passed 25
   behavioral and fault cases and the then-current task-local Python suite
   passed 46 tests, including four fail-closed predecessor/ZDI retirement
   guards. These counts are historical, not the current Work 2.e gate-suite
   result. The non-release ESP32-P4 target
   composition builds successfully: reported total image size is 1,252,995
   bytes, the padded application binary is 1,253,024 bytes, application flash
   use is 1,252,148 of 7,340,032 bytes, and RAM use is 63,984 of 512,000 bytes.
   Its fresh application-relink ELF SHA-256 is
   `1c7b03ff48e47db84f07c4e693990760ab53a31a6a69c0508c1ce3d8480d1c6e`;
   the padded application binary SHA-256 is
   `4d0f882904496e17c3418c783d8fb28550fe615ea765b481191957291a042a07`;
   its map SHA-256 is
   `890725a9f3447dded44a27a519fd02fe4f0fa35791eb32de53745436e62149e0`.
   The respective ELF, padded-binary, and map sizes are 24,079,432,
   1,253,024, and 13,675,025 bytes.
   The build used repository identity
   `a495911945e8b4f55c95a00e901cd93cb5b68c73+tracked-dirty`; that source delta
   was not frozen at build time and must not be confused with the clean
   authority used by the initial boundary review. The implementation was later
   source-frozen in `e134f3d`; the recorded artifacts remain pre-freeze,
   unidentified evidence.
   The closure checker proves the bounded API/source/symbol/exclusion claims it
   reports, not source provenance, final-link object contribution, release
   equivalence, target runtime, or physical behavior.
3. The EMOS production epoch, record engine, GPIO helpers, semantic-route
   bridge, and UART1 transition guard are integrated. A fresh v10 isolated
   clean-scope snapshot contains 146 files and reports prepared-source identity
   `0e24b06abdb322fdb4e681a21242ccfebfc8ea65+tracked-dirty`; the complete EMOS
   host suite passes 64 tests. The ordinary image is 116,520 bytes at SHA-256
   `a4c2d3f87286dd32e7b2e3a7b30786ae4156208e2440ba096c733f76256d09a4`,
   with ELF SHA-256
   `8315db0fd2f519a16d35d4b668d74ed9b6d52e65cee0c1ca947acf9b64f88373`
   and map SHA-256
   `75a5a45de6099c1e12596752000defde76e5b46efb30705988792f5218179357`.
   The non-release fixed image is 116,966 bytes at SHA-256
   `4f0c0db7d419c6a0f17fe9d07dd3bd2107fb110371fa0a44b444c1e3417d2e66`,
   with ELF SHA-256
   `7186c10373f6f642eedc0949fb443cd5dd7b6eedeed43a44b86f877c78bb382d`
   and map SHA-256
   `539375306a4f830ec300131e033b556df519fd0cee9819bff63364f4ffbcc341`.
   All five common production objects are byte-identical across the profiles.
4. Both EMOS profiles now contain the complete ordinary-VDU composition. The
   linked checks establish exact RST 10, RST 18, and C-runtime-to-dispatcher
   call edges and dispatcher-parallel-branch-to-common-route call edges, while
   backend zero retains the onboard UART path. The bounded RST 18 check also
   fixes its argument and success/failure epilogue instruction shape.
   The predecessor symbols and behavior are absent from both linked closures.
   The fixed profile has exact coordinator-to-enter/ready/leave and wrapper-to-
   common-route call edges and contains its explicit non-release identity; the
   normal profile excludes those fixed-only symbols.
   `open_UART1()` holds the shared lifecycle reservation from before its first
   serial flag, Port C, or UART mutation until after UART1-active publication.
   Extracted production-code host tests additionally cover coordinator commit,
   recovery-failure retention/retry, and private-to-public error mapping. These
   source and linked checks establish only those bounded structural and host-
   execution claims, not authenticated source/object origin, indirect-call
   impossibility, runtime route selection on the target, target execution, or
   electrical behavior.
   The EMOS implementation was subsequently source-frozen in `b823e0e`; the
   v10 artifacts remain pre-freeze and `UNVERSIONED-DO-NOT-DEPLOY`.
5. A real retained-parser/display host runtime cannot be formed without
   substituting target semantics. Current evidence therefore includes source
   guards and source-derived output-fault offsets but not the required real
   General Poll and startup Mode Information failure injection. The retained-
   parser feasibility record owns the target-native removal test.
6. The configured P4 10 MHz ceiling and 5000 ms active-record deadline remain
   provisional software policy, not qualified electrical or timing values.
   Stopped CLOCK, stuck VALID, real GPIO release, partial peripheral start,
   and retry still need separately authorized target-runtime evidence. The
   source/compile guard also cannot prove target sampling of a transient
   `VALID_N` pulse shorter than the one-millisecond cancellation poll when
   PARLIO reports no completion; such a pulse publishes no partial record, but
   its runtime diagnosis remains open.
7. No flash, SD mutation, deployment identity, emulator behavior test, wiring
   or probe change, reset, power operation, or physical transfer occurred.
   The implementation stopped at the accepted software-only boundary.
8. An incremental PlatformIO configure/build can leave `firmware.map` holding
   a CMake compiler-probe map when the application link is already up to date.
   The bounded closure validator rejected that file because the required
   direct LOAD records were absent. The result above was regenerated by a
   clean application relink and then revalidated. Until build provenance is
   repaired, any map-based claim requires that sequence; target-build success
   by itself is not map evidence.
9. The production factoring and adversarial reconciliation exposed
   `PORT008-PROV-P009` through `P016`: three local lifecycle-publication races,
   a local verifier-claim defect, the local UART1/parallel Port C integration
   race, a local native-profile parity omission, discarded adapter-recovery
   failure, and private parallel statuses escaping into the public command-
   error domain. All eight were created in project EMOS production or
   integration work, not in official MOS. P012's final verifier strengthening
   and P015/P016's transaction/error-domain corrections pass in the v10 suite
   and linked builds. The integrity audit owns their exact upstream/local
   classifications.
10. The final P4 adversarial pass exposed and corrected the project-created
    `PORT008-PROV-P017` through `P021`. An idle authorized receiver now keeps
    the same PARLIO transaction armed and READY asserted; only active
    `VALID_N` starts the fatal deadline. `ExtenderVdpStream` preserves exactly
    one byte already advertised by `available()` or `peek()` across a fault,
    avoiding inherited-parser consumption of synthetic `0xFF`. One
    nonblocking sequentially consistent cancellation edge orders record
    admission; a record that won first is quarantined, and post-commit checks
    prohibit a post-fault success report. The non-release owner retries
    cleanup before revoking its lease, and retained process-task creation
    failure returns before boot-screen/network publication. These host/source/
    compile corrections do not replace target-runtime or retained-parser
    execution evidence.

## Work that must wait

The following work cannot receive physical production evidence from r01:

1. the activation request carrier, grammar, identity/capability response,
   confirmation, and EMOS-only formal-mode commit;
2. any r02 UART enable tuple, UART2 output, eZ80 UART1 receive path, 1,152,000-
   baud timing, RTS/CTS, or the retained RTS-only to CTS+RTS transition;
3. General Poll response delivery, stale-Poll rejection/session binding,
   canonical MOS packet parsing through UART1, sysvar updates, or completion
   flags;
4. asynchronous keyboard, mouse, RTC, audio, or other response packets;
5. UART-to-parallel and parallel-to-UART break-before-make timing;
6. Legacy electrical absence, arbitrary Legacy pin loading, buffer disable,
   contention, isolation, either-order power, back-power, and r02 analog margin;
7. eZ80-only reset, P4 reset during a committed mode, stale epoch invalidation,
   coordinated shutdown, and whole-mode recovery;
8. Exclusive Compatible, Dual, broad Exclusive Extended compatibility, or any
   complete V1/product claim; and
9. response-bearing or currently unsupported audio/updater/maintenance command
   classes whose production consumers and parser recovery remain gated.

R01 UART testing is not merely weak evidence. Selecting the intended r02
full-duplex control state can enable both r01 PC1 directions and is therefore
prohibited.

## Existing prototype defects and production disposition

| Existing item | Production disposition | R01 use |
|---|---|---|
| P4 infinite external-clock wait, F005 | Active `VALID_N` starts a bounded abort; indefinite idle retains one armed advertised transaction; direction/READY release is fail-closed; target-runtime proof open | Exercise the production software path plus READY/GPIO15/GPIO21 outcomes; do not claim r02 bank isolation |
| P4 partial-start leak/retry poison, F013 | Transactional init, reverse-order unwind, explicit started state, and qualification-owner retry-before-revoke implemented; target-runtime proof open | Exercise startup/retry and observable r01 controls; r02 external-disable behavior must wait |
| P4 callback `volatile` handoff, R001 | Replaced with release/acquire generation publication; target-runtime proof open | Host complete; physical stress later |
| P4 idle/fault/admission integration, P017--P019 | Corrected idle/active deadline, one-byte advertised-read permit, and nonblocking admission/quarantine semantics; retained-parser and target-runtime proof open | Exercise exact production objects; do not infer physical timing from host/source checks |
| P4 qualification cleanup/false-live boot, P020/P021 | Cleanup retains ownership through successful stop; process-task failure returns before boot/network publication | Non-release composition only; target execution remains open |
| P4 preactivation READY, P005/CA | Removed from maintained boot path; READY requires an active epoch lease; production activation open | Qualification composition supplies the lease; no activation claim |
| P4 direction omission, P004 | GPIO15/17/21/20 ownership centralized in the target owner; target-runtime/electrical proof open | Active-parallel subset works on r01 |
| EMOS length-object overlap, P002 | Replacement engine uses exact-width state, chunking, and linked guards | Preserve width invariant; do not promote adapter |
| EMOS sender cadence, P003 | Qualified high/falling/rising/idle phases preserved in the replacement engine | Exact production cadence can run on r01 |
| EMOS full-record interrupt disable | Replacement limits masking to small atomic helpers; target-runtime latency/coexistence proof open | Target/emulator evidence before physical soak |
| Prototype 4096-byte rejection | Replacement chunks below the raw stream boundary | Exact production split behavior can run on r01 |
| Discard-success return Stream | Replaced in the qualification composition by an explicit injected byte-capture observer; production UART return remains open | Never silently discard or claim captured bytes were transmitted |
| Empty reachable audio/updater handlers, F004 | Keep corpus away now; owner tasks must later consume or safely reject full grammar | No filtering workaround in EMOS or transport |

## Upstream observation: bounded RST 18 return value

Official documentation at `agon-docs` `f9806bd` says bounded RST 18 returns the
last displayed byte in A. Official MOS `5f67b1c` overwrites A with `B OR C` at
the end of its length loop and therefore returns zero after success. EMOS's
onboard and committed r01 block paths also return zero on success.

This is an upstream documentation/source divergence, not a defect created by
the parallel port. In accordance with `PORT-003-D012` and `REMED-002-D004`, do
not correct official behavior or design a broad upstream regression now. While
factoring the parallel engine, do not silently change the current de-facto
successful return behavior. A later Extender-specific failure or an explicit
compatibility decision may reopen the documented-versus-observed contract.

## Preconditions before any physical r01 run

1. Resolve or explicitly supersede the open corrective-action hold. D001's
   receive-only listener and no-CTS bootstrap workaround are rejected; a
   fixed-backend data-plane run needs its own reviewed containment rationale
   and cannot be called production activation.
2. With both boards off, confirm that the present specimen still implements
   `light2-extender-solderless-assembly-r01`: U1 identity, GPIO15/GPIO21
   enable fanout, GPIO17 truly unconnected, GPIO20 READY path, resistors and
   pulls, common ground, and separated positive rails. The invalid last
   diagnostic does not establish today's physical state.
3. Resolve the missing r01 CLOCK observation or show that the new production
   sender and passive continuity checks remove it. Do not alter production code
   to accommodate an unexplained missing edge.
4. Keep the old READY-isolated CLOCK discriminator as a last-resort r01 fault
   diagnostic, not part of the production-equivalent tranche. It changes the
   temporary fixture and proves no product behavior.
5. Complete F007/F014/F015 evidence-integrity work relevant to the proposed
   package. Exploratory runs may diagnose but cannot qualify through known
   false-green tooling.
6. Present the exact new firmware, profile, fixture, procedure, build,
   baseline, and run identities under `docs/versions/README.md`; do not reuse
   the historical r01 candidate identity for materially different production
   objects.
7. Follow BC-001: every eZ80 fixture cold-boots through exact root
   `/autoexec.txt`, terminates deterministically, and has a non-keyboard
   evidence path.
8. Obtain separate Author approval for every flash, SD mutation, wiring/probe
   change, reset, power operation, and decision-bearing run.
9. Retain the r01 controlled-power discipline. No r01 result supports
   either-order-power or powered-off isolation.

## Decision and next-work effect

`PORT-008-D001` is rejected. The controlled-beta receive-only listener and its
dedicated no-CTS bootstrap sender are not production work. The current
all-controls-released Legacy rule and corrective action remain in force; a
production activation path requires an intended-circuit solution rather than
an r01 or firmware-only exception.

`PORT-008-D002` accepts the boundary in this audit: implement new production
parallel data-plane objects, exercise them on r01 only through an identified
fixed-backend qualification composition, and make no r01-specific behavior a
supported product path. This also resolves `REMED-002-D003` in favor of
replacement rather than repair/promotion of the exact prototype adapters.

The 25-case host-tested P4 ingress/control/Stream objects, 46-test task-local
suite, and the complete EMOS
ordinary/fixed forward-data-plane compositions now exist. The next software
evidence steps are target-native retained-parser fault injection and a genuine
linker-contribution/release-object provenance gate. Production activation,
return UART, General Poll confirmation, response/sysvar integration, artifact
promotion, deployment, and physical work remain subject to their separate
decisions and gates.
