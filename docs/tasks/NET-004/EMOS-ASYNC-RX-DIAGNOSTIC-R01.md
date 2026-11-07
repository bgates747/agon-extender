# First-overrun service diagnostic preparation

Preserve the service context before the next UART1 error instead of repeating an
uninstrumented game. The receiver reported overrun again in consumer83; neither
the error nor the preceding software service interval has an established cause.
Extender will prepare small optional EMOS marker hooks, with the recorder and
timer work in application RAM. No hardware case or firmware installation is
selected by this source/build plan.

## Evidence and bounded research

1. Consumer83 used EMOS source954e3c54/fullROM8de66, native9be4582a/map2886cb1c.
   Startup registered43.597s after dispatch. The first error has rawLSR0x02,
   sourceNULL/remaining0, pendingPOLL57 and no positive drain/close. The exact-map
   consumer decoder finds the mainboard renderer retired, without a first
   renderer/token error. Preserve original SD2ac3ac64 and post-reset64KiBRAM
   eca958f2. A later renderer-idle observation does not prove first-error UART
   quiescence. The failed result remains failed.
2. Quiet owner79 passed176 records/four sessions. It excluded active renderer
   overlap and did not qualify service latency, STOP reserve or the failed
   consumer. The two results have different workload scopes.
3. Exact source954e3c54: `src/emos_keyboard_io.asm` drains at most16 bytes and
   can dispatch a whole NM callback before continuing; its first-error branch
   already owns the acknowledging LSR sample in C. `src/interrupts.asm` owns
   UART0 RX/protocol dispatch and VBlank. `src/uart0_async.asm` has bounded CTS
   deferral; callbacks in the matched app store flags. `src/emos_neta.c` owns
   the app service hook and positive-close association. Do not rewrite the
   generic UART sender or assign causality from source length.
4. Official reference baseline remains agon-docs f9806bd3, MOSv3.0.2 83364093
   and VDPv2.16.0 c7ac293d, read-only. UART/vector APIs do not authorize replacing
   EMOS RX. Existing timer provider is MechAgon `native/profiling/prt.s` and
   `prt.c`; its foreground scratch reader must never be called from an ISR.
5. UART owner's `U1-001/actual83-irq-source-assessment.md` and MechAgon's
   `GOAL-001/irq-timing-contract/PROPOSAL.md` c3a486bb supply the current source
   seams and128-byte little-endian record. Retain exact source/hash joins in
   ignored evidence. The nominal16-byte/1152000baud empty-FIFO scale is139us,
   not an available blackout budget or physical peer-tail measurement.

## Selected source mechanism

1. Extender preserves frozen source954e3c54 and creates an isolated diagnostic
   derivative. A compile option defaults OFF. OFF source/link composition must
   retain the established operational path. The production selection, generic
   U1 core, P4, native VDP and normal syscall ordinals remain unchanged.
2. Put the bounded native recorder in application code, with its static128-byte
   record in application RAM. EMOS has575 ROM bytes free; moving the recorder
   out of ROM preserves space for small admission/dispatch hooks. This is a
   register-defined assembly marker, not a general C callback on every byte.
3. In the diagnostic-only private composition, extend existing async OPEN from
   four to seven input bytes: operation0, existing U1 hook24, optional diagnostic
   marker entry24. Four-byte OPEN remains the unobserved control. Validate both
   entries against the existing app-code range before association. Output stays
   seven bytes. No new public syscall, guessed private address or resident TX
   engine is added. Exact manifest/SDK/private-profile binding precedes use.
4. Keep the marker association with the admitted app hook. Positive close clears
   both only after source, later drain and existing owner checks pass. Refused
   close retains both and their application storage. Actual owner abort/reset
   clears the association with existing teardown; it must not erase a frozen
   application record. Application unload/free while associated remains unsafe.
5. The marker receives event A, retained raw LSR C and drain remaining B where
   applicable, plus owner-supplied STOP/hold/parser context at first error. It
   reads only its admitted disposable timer, not UART/GPIO registers. Extender
   supplies the context without an extra acknowledging LSR read. Exact register
   assignments and numeric events are source-contract outputs before consumer
   integration; they must preserve all interrupted ADL registers and caller IFF.
6. Place markers at source-supported UART0 RX/TX, UART1 drain, VBlank and the
   scoped foreground gateway boundaries. Nested packet/service tags describe
   the current outer span; they are not summed as extra CPU durations. Preserve
   the preceding completed observed span across UART1 entry. Missing hooks and
   save/restore tails stay explicit. Foreground render guards are consumer-owned.
7. Freeze the first already-read error before fault callbacks/reset alter it.
   Retain parser/drain/STOP/hold, recent span and raw timer samples. Count cap
   hits separately from clean-empty exits. No per-byte logging, hot SD/serial,
   extra LSR acknowledgement, implicit retry or suppressed error is supported.

## Timer and observer lifetime

1. MechAgon's new unprofiled diagnostic caller explicitly admits inactive,
   disposable PRT1. PRT0, timer IRQ/vector and the foreground profiler stay out.
   Use system source, single pass /256, reload0000/full65536 and bounded ready
   observation. Only nonzero count/control0x0d begins an epoch. Sample low84,
   latched high85, then control83 atomically in a separate native marker path.
2. Same-epoch descending endpoints alone permit subtraction. Exhaustion, zero,
   count increase, ownership loss, rearm gap or counter overflow means UNKNOWN.
   Never apply modular arithmetic to turn an expired stall into a short span.
   Raw128-byte evidence stays immutable; stopped decoding derives durations and
   gaps instead of adding avoidable arithmetic to every interrupt.
3. A pre-NM boundary with no pending request is not RX-wire quiet. During rearm,
   atomically disarm timer observation, retain any first fault and publish the
   new epoch only after readiness. The256-sample readiness loop must remain
   IRQ-enabled, with bounded atomic register operations between opportunities
   for normal RX service; never put the entire loop under DI while READY.
   No live source/drain or active observed span may cross rearm. Keep explicit
   gaps and refuse timing admission rather than lengthening transport deadlines.
4. Capture first error even if timing is disarmed/expired: raw error/context is
   useful while its duration remains unknown. Rearm must not clear a concurrent
   frozen-first-fault bit. Do not clear the record after association begins.
5. Report nominal72000counts/s,13.889us/count, up to two counts of endpoint
   quantization, marker perturbation and omitted tails. No exclusive-CPU,
   physical STOP-tail, wire-occupancy or complete all-IRQ claim follows.

## Itemized implementation and validation

1. [x] Publish exact optional OPEN/marker/record lifetime contract to the consumer
   and generic UART owner. Resolve register preservation and rearm publication
   against actual assembly before consumer edits; no additional human gate.
2. [x] Implement the app-RAM native marker/decoder and minimal opt-in EMOS hooks
   in their owner trees. Preserve default/OFF bytes and all current validators.
3. [ ] Check range and malformed association, refused cleanup, fault before
   callback, immutable first error, nested tags, recent-span retention, expired
   or crossed epochs, counter saturation and unsafe detach with real source
   controls. Host models do not claim executed IRQ timing.
4. [ ] Under normal Pi FIFO, assemble/link exact OFF/ON compositions and app
   observer, validate actual instruction/relocation/register/IFF paths and full
   ROM fit. Report ROM/BSS/app text/record/stack costs and marker boundaries.
   Stop on overflow or unsupported timing; do not remove guards to make it fit.
5. [ ] Only after exact source/binding/fit checks, freeze one finite diagnostic
   reproduction with first-fault stop, unchanged deadlines, SD/RAM preservation,
   exact installation/readback/rollback and normal fresh bench custody. That
   later physical selection is not made by this document. Wolf84 stays sole.

This extends the existing NET-004 receive investigation; TODO.md remains the
only queue. The diagnostic is experimental source preparation, not acceptance,
production promotion or a new normal application ABI.

## Concrete private marker contract selected for source preparation

1. Retain the proposed128-byte `MGIRQ001` little-endian record, tag meanings and
   invalid/partial-coverage limits from proposalc3a486bb. Runtime stores raw
   endpoint samples/context; stopped decoding derives durations/gaps. Native
   zero derived-duration fields do not claim valid zero elapsed time. No global
   all-IRQ totals or recursive CPU timing stack is introduced.
2. Seven-byte diagnostic OPEN contains `[0, service_hook24, marker_entry24]`;
   both three-byte pointers are little endian. It uses the existing private
   async gateway, unchanged operation0/output7. The marker is independent of
   the U1 service hook. Normal four-byte OPEN leaves it NULL. Only the new
   diagnostic build accepts length7; baseline8de66 must refuse it. No generic
   U1 service event or emitter API changes.
3. Native marker register inputs: A event; B current drain remaining0..16 and C
   the existing sample only for corresponding RX events; D owner-sampled PC_DR;
   E scoped RX-hold byte; HL points at the owner's six-byte parser prefix only
   for immediate copying during this call. The application never retains HL
   or uses guessed EMOS addresses. Non-RX events must not interpret B/C. No
   caller UART/GPIO reads or additional LSR sample are supported.
4. The EMOS bridge preserves interrupted registers while supplying context.
   The admitted assembly marker preserves primary AF/BC/DE/HL/IX/IY, all ADL
   upper bytes and alternate registers; it enters under DI and never EI/RETI,
   waits, calls C, allocates, logs or touches transport state. It may read only
   its admitted PRT1 and update bounded app data. A register-safe ordinary RET
   returns to the existing owner flow. Exact linked wrappers/cost remain gates.
5. Event codes are outer begin1..5 (UART0 RX, UART0 TX, UART1 drain, VBlank,
   foreground owner), outer end0x81..0x85; app-owned critical begin6/end0x86.
   Nested packet dispatch0x10/0x90 and clean-empty U1 service0x11/0x91 supply
   inner context. RX first-read0x20, cap0x21, clean-empty0x22, first-error0x40
   are point events. Only0x40 interprets C as raw error LSR. First-read C is
   data and never an LSR. First-RBR sampling is optional; absent last-RBR
   sampling leaves its validity bit clear rather than relabelling drain-end.
6. Observe only outer spans as durations; nested entry/exit updates inner tag
   and depth without summing another duration. Preserve preceding completed
   observed span until first-error freeze. Saturation/overflow, missing entry/
   exit or unexpected nesting sets explicit unknown/partial flags. Initial
   OPEN publication and positive CLOSE removal may leave an unmatched edge;
   it must not manufacture a measured span. Freeze once before fault callbacks.
7. Bind/retain marker lifetime atomically with the U1 hook. Refused close cannot
   detach either association. Actual reset clears the callback pointers without
   writing the retained app record. Stopped collection still requires original
   RAM before any LOAD/reset overwrite and explicit post-reset qualifications.
8. Rearm uses one app/timer owner. Before the short atomic epoch publication,
   disarm marker time reads while retaining raw first-error capture. Keep the
   bounded readiness loop IRQ-enabled: individual existing register writes and
   low/high/control snapshots may use bounded IFF-preserving exclusions, never
   a256-sample DI loop. Markers see either a fully armed epoch or an explicit
   unknown/gap. Publish only if no first fault/span/live source/drain crossed
   the boundary. Recheck frozen state before publication, do not clear it.
   No-pending-NM is not wire silence and does not waive ordinary RX service.

This selects a small app-owned assembly observation interface for implementation,
not a successfully linked image, a runtime safety bound or a selected bench run.

## Record closure and current source checkpoint

The reusable header is `include/agon/rxdiag/observer.h`, schema2. It keeps the
128-byte extent but explicitly stores rawLSR80, raw drain **remaining**81,
ownerPC_DR82, owner RXhold83 and all six parser bytes84..89, with validity90.
First/last-RBR fields stay invalid when not sampled. Query96/cap100/empty104
remain independent; stopped decoding must reject schema1 reinterpretation.
The native recorder/API implementation and executed register controls are still
in preparation; header publication is not readiness to deploy or call a stub.

Actual353 OFF assembly/link/allmandatorychecks passed. ON assembled/linked and
passed existing product validators, but the new checker used the wrong IN0-D
opcode (ED50 instead of actual ED10). The failed checker receipt is retained;
actual disassembly proves IN0 D,(9e). Correcting that checker does not alter
firmware instructions. All owned compiler children joined;353 released normally.
No observer or new EMOS installed; Wolf85 retains sole finite PERF017 custody.

## Checked app/owner source checkpoint

Compiler358 passed six actual-C foreground lifecycle sanitizer cases, three
draft-dispatch negative source controls, native app C/assembly/link and every
EMOS OFF/ON mandatory validator in22.503s. Released13:05:23UTC/all children joined;
automatic359 Wolf was notified by durable mail/immediate steering. Root recorder
now has explicit FIRST_READ point handling, actual-active and matching bounded
eight-tag nesting, pure one-time NULL-control init and consistent terminal
readiness-failure retirement. Query96 and gap116..127 are unknown/reserved until
an actual writer/validity contract is provided; zero is not measured latency.

EMOS optional hooks committed1727fa1 in isolated owner tree. Raw unidentified
OFF130436/ON130835B (+399ROM/+3BSS), ON237free before identified header. Standalone
app link1610text/166BSS includes record128, bounded tag storage and providers;
consumer incremental cost still requires its own link. Marker stack/saves and
copy/clear costs perturb the measured paths, with no executed register/IFF or
hardware service-latency claim. No first-error cause is assigned.

Next finite compiler tranche binds OFF to the exact retained identity header
solely for a bit-exact unchanged-control comparison, then builds clean committed
ON with a fresh identified build/diagnostic composition manifest. Retain old
8de66 artifacts; never deploy the control identity as a changed candidate.
No physical diagnostic case is selected by these source/build checks.

## Identified source/artifact handoff, 2026-11-07

Compiler362 passed refreshed six actual-C lifecycle sanitizer cases, three
source dispatch negative controls, native observer assembly/C/link, byte-exact
identity-matched OFF baseline comparison and fresh identified ON/all mandatory
validators in20.916s. All children joined; released13:10:23.924490UTC/nextnone.
The OFF control raw368b00b2 is identical to retained954e3c54 raw baseline; its old
identity header was used only for this comparison, never as a changed candidate.

The clean experimental diagnostic ON source is1727fa19, build
`agon-emos-eirene-r05-b2026-11-07-13-10-14Z`: raw130896/free176, full131072-byte
ROM80fe235938071f5910f6f127ceb14416fc9c4c9407843232adffa82d6c0761b6,
map7a5965d6272c7c55983e612f706900859b7cec1d2aed36b964c4fa0ced98e09c.
Its optional bridge/admission/markers cost399ROM/+3BSS versus the exact control.
The current standalone app observer links1620text/0data/166BSS, including record
128 and providers. This is not a consumer incremental size or whole-stack bound.
A small endpoint-only clear replaces the initial24-byte full-span clear; the
remaining24-byte history copy, register saves and calls still perturb IRQ spans.

The ignored source/artifact ZIP is184789bytes/SHA
0a9e85ac6e004bc3a39994d9256ea889081115bf9172ffeccb38505d024b3ea9; owner-local
manifest joins exact header/C/assembly/SDK and retained ROM/ELF/map bytes. The
consumer must bind this exact source before its own checked application link.

1. Schema2 defines captured start/end independently of derived validity.
   Runtime duration-valid stays clear, gap flags116..127 and query96 stay
   reserved/unknown. First/last-RBR hooks are not emitted in this owner build;
   their validity fields stay clear. FIRST_READ is nevertheless a tested
   supported point dispatch and cannot corrupt nesting if deliberately added.
2. Marker coverage excludes save/restore tails and other IRQs/foreground masking.
   Eight bounded nested tags retain pairing context, not recursive CPU totals.
   Error freeze reuses the original LSR; expiry/disarmed samples remain unknown.
3. No native IRQ execution/register/IFF/PRT acceptance, physical service bound,
   STOP peer-tail measurement or cause/cure claim follows. Match the NULL
   observer control, account for marker work and independently retain the
   current uninstrumented failed artifacts. Mandatory baseline rollback stays
   a25f; neither identified candidate nor its app library is installed.
4. Mech owns caller changes, source/protocol checks, final size/map bindings and
   selection of the next finite case. Extender owns component installation,
   actual sole-operator handoff, preservation/rollback and normal cleanup.
   A ready source package is not a physical grant or per-test approval gate.

Wolf85 completed its separate four-room/five-INFO cohort and cleanly released;
all target actors stopped and baseline native/tail85f9 restored/read back.
No new diagnostic physical reservation exists at this checkpoint.
