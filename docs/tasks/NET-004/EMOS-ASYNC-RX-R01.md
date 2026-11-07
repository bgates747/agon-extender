# UART1 receive-service investigation and bounded correction

Resolve the reported receiver overrun before treating asynchronous UART1 as a
reliable MechAgon carrier. Smith's verified owner delegation selects correction,
measured eZ80 headroom and then maximum sustainable presentation rate. Extender
owns EMOS/P4/SDK work and physical scheduling. Existing Wolf custody and queued
work finish first; all source preparation below is independent of that bench.

## Selected scope and original evidence

1. Preserve failed physical76: exact EMOS2c47053/fullROM043a, consumercf910/map3306,
   original SD0da0db39 and post-reset RAM4a7aa3d3 agree on UART1LSROE0x02 after
   source release, before later drain/close. Source bytes are released; the
   failed first source and unsafe detach must never be replayed or suppressed.
2. Working baseline P4d9bcb/fullEMOSa25f/nativeprofile8 is restored. The revised
   consumer idle cache92f083f is checked, not hardware-qualified and not a cure
   for OE. No implicit parallel fallback or new normal production selection.
3. Official API baseline: agon-docs f9806bd3, docs/mos/API.md14h–18h, defines
   UART/vector ownership, not live takeover of EMOS RX. Read-only MOSv3.0.2
   83364093/VDPv2.16.0c7ac293d remain the established references. Native owner
   source and matched linked validators govern EMOS-specific hooks.
4. Matched1152000/8N1/16-byteFIFO gives138.889us empty-scale, not a safe delay
   bound. Initial occupancy, in-flight character and peer hardware CTS response
   matter. P4's own receive reserve protects the other direction.

## First offline tranche

1. [x] Join actual eZ80 owner source/generated/linked code to the failed ROM.
   Inventory IRQ exclusions, RX STOP assertion/release, RX parser/app callback,
   UART0 and VBlank paths. Distinguish bounded native instruction paths from
   unbounded CTS waits and unmeasured callback work; do not invent cycle totals.
2. [x] Join matched retained P4 source/IDF UART queue and hardware CTS setup to
   its installed artifact. Identify the maximum queued transmit path and actual
   source guarantees about STOP; do not infer electrical response from APIs.
3. [ ] Coordinate generic UART0/U1 contracts with UART owner. Keep its unchanged
   core/emitter; any generic correction is UART-owned. Extender may correct its
   derivative EMOS-specific admission/ISR glue, preserving register/IFF, RX/error
   sample, writer/mode guard, source/drain/reply and positive-close contracts.
4. [x] Select the smallest concrete owner correction supported by those source
   findings, or a bounded opt-in discriminator if physical timing is missing.
   Candidate contracts include asserting STOP before long owner exclusions and
   releasing it only after corresponding RX/IRQ readiness; avoid globally
   changing nested locks or introducing a resident serializer without proof.
5. [ ] Check actual-source nested/foreground/IRQ cases and first-fault lifetime,
   delayed CTS, RX-first cap and callback behavior. Use normal serial compiler
   FIFO, finite15min build/check tranche, all mandatory native validators and
   exact identified ROM/map/full size. Preserve synchronous default object and
   full working rollback. Report ROM/BSS cost, not only the tiny generic leaf.
6. [ ] Return concrete artifacts/contracts/regressions and the next smallest
   finite isolation case to MechAgon; freeze it before reserving normal fresh
   physical time. No current Wolf lease access or extra consumer case here.

## Measurement and qualification boundary

1. EMOS owns any IRQ instrumentation and timer admission. First use retained
   assembly/source and bounded tests; do not instrument every byte by default.
   If timing needs a physical diagnostic, make it opt-in, record overhead and
   exact timer ownership/wrap/latch rules, store bounded RAM events outside the
   source path and retrieve after the case. No print/log/SD write in the ISR.
2. Shared PRT+exclusive all-IRQ totals require an owner-supported timer contract
   with the consumer. Label UART-only counters as partial, inclusive callback
   brackets as inclusive, and missing data as unavailable. Never add overlapping
   brackets and call the sum free CPU or reserve the consumer's timer silently.
3. Physical isolation follows the protected entry queue, under a new real
   checkout with sole operator, normal startup and one explicit CLI invocation.
   The frozen case names endpoints, traffic, bounds, first-error stop, source/
   tail/reply/retirement evidence, SD result, exact install/readback/rollback
   and clean handback. No sensor, replay, blind reset, error suppression or
   relaxed timeout manufactures a pass. Current task does not invoke that case.
4. Only after owner isolation may MechAgon integrate its corrected app and
   profiling. Sustainable rate and bot headroom are separate measured scopes;
   no comparison above30Hz follows from an async correctness check.

## Owners and coordination

Extender: EMOS/P4/SDK and scheduler. UART: generic UART0/U1 and reusable IRQ facts.
MechAgon: caller/server/bot/profile integration and dependency ordering after the
protected entry queue. VDPlet: runtime/SDK/mainboard performance hooks. Jukebox's
separate vanilla ESP8266 stream supplies useful receive evidence, not EMOS/P4
qualification. Internal read-only source reviewers may partition eZ80 and P4
analysis; no duplicate hardware fixture or component takeover is delegated.

This plan extends the active NET-004 async task; TODO.md stays the only queue.
Exact human source, private artifact paths, lease snapshots and source inventories
remain ignored local evidence. No production promotion, emulator diversion or
firmware installation is selected by publishing this preparation plan.

## Selected first correction — foreground hold and post-service validation

C1: a private one-byte foreground RX hold is entered only for an IRQ-enabled
async gateway call and owned UART1. Its native entry masks and asserts STOP
before owner validation/START/service. RX completion cannot lower STOP while
held. The paired native exit checks full receiver health/demand, clears the hold
and lowers STOP only immediately before restoring IRQs. Refused IRQ-disabled
entry never changes an outer hold. Generic/nested keyboard locks and old
synchronous paths remain unchanged. Abort, demandFAULT, pending keyboard fault/
stop or owner loss must keep STOP asserted; no EI-then-C-STOP race is permitted.

C2: owner PROGRESS must revalidate hook/ownership/fault after its RX-first call.
RX may synchronously report a line error and reset/abort the hook, clearing
resident demand to zero. That cleared demand is not positive wire-idle or
authority for close. Preserve original first fault and return unavailable;
never double-release a writer guard after error-driven abort.

Implement/check these in an isolated EMOS worktree, preserving failed-trial
source and binaries. They close identifiable owner contract/readiness gaps;
neither is asserted to explain76OE. The standalone IRQ epilogue gap, unrelated
UART0 CTS wait and unknown peer electrical response remain separate limits.

## Checked first correction and next bounded derivative

C1/C2 pass actual-C sanitizer/lifetime checks, distinct historical-source
negative controls and the complete native identified-ROM validators. Source
54abf57, raw ROM130422 bytes,650 free; delta281 ROM bytes and1 BSS byte against
failed043a. Full ROM e74df3582e1d2a301c15362df8a1bc06f9f8f43019711436770a7ca275544119.
No installation or causal attribution follows. The first build correctly stopped
at the Port C inventory: two narrowly gated new leaves now have exact linked
write/IFF/health/return verification. No validator was skipped.

C3 selected before integration: incorporate UART owner's immutable bounded-CTS
source derivative05b8b10 (handoff5f568c1), preserving its native admitted copy
paths and saved AF/EI/RETI frame. EMOS calls its bounded rearm from the existing
saved VBlank path. The pending flag precedes IER/TEMT in EMOS ownership checks:
TX interrupt masked plus empty FIFO does not retire a deferred source. Existing
route/reset admission must refuse it; no new cancellation API is introduced.
Only accepted new publication/final copy or actual reset teardown may clear the
pending flag. BSS initialization is the existing actual-reset teardown; a route
request cannot clear it. No UART generic donor/IRQ installer is imported.

Qualification must compare exact generic defer/rearm source and linked bytes,
reject missing pending ownership and admission-after-count mutations, preserve
all original validators and check the complete ROM fit. Generic+52 ROM/+1 BSS
is a standalone cost, not the EMOS integration size. No unbounded WAIT_CTS is
allowed in the selected optional TX leaf. One VBlank retry may add one refresh
interval; no latency/throughput improvement or76 cure is assumed.

## First isolated physical case — selected before fixture code

1. A separate application-owned UART1 async echo appliance reuses the existing
   four-session/176-record deterministic matrix (eleven lengths0..128 and four
   binary patterns). eZ80 sends through EMOS/U1 to P4 NM/TCP; the Pi echo peer
   returns the exact payload through P4/UART1. Both endpoints compare exact
   bytes. No CRC, additional sensor, renderer, module or game is added here.
2. The app installs the existing checked NM callback bridge, services only its
   app-owned core through supported EMOS hooks, and retires source, later wire
   idle and reply independently. Every session must positively close and restore
   its saved callback before the next declared session. Failure never reconnects
   or resubmits an uncertain request. Refused close retains static storage and
   original fault, logs what is safely possible, and waits for owner recovery.
3. First isolation deliberately keeps UART0 display and SD activity outside live
   NM/source ownership. It qualifies the owner integration/lifecycle, not mixed
   graphics overlap, useful-work capacity or async performance. Quiet UART0 does
   not exercise C3 blocked CTS physically; linked/source checks remain explicit.
4. Record entry mode, conditionally select mode20, settle at least one second,
   restore entry mode and visible cursor/CLI. Escape is checked between bounded
   calls. Native case ceiling14400 nominal120Hz MOS counts; independent loop
   fuses and peer's150-second original envelope stop missing progress. Startup
   is untouched; one explicit LOAD/RUN only, no automatic restart on reset.
5. The Pi runner stages and verifies one new identified app and peer, installs
   and independently reads back the exact combined candidate ROM only, retains
   current P4/native/startup/listener, then invokes this case once. It preserves
   SD results and, on unsafe failure, original application RAM before LOAD;
   follows supported recovery, restores exact retained working a25f ROM/readback
   and full idle handback/release. No P4 installation or unrelated firmware write.
6. Freeze ROM/ELF/map/config, app/listing/core/SDK/callback, peer/runner, fresh SD
   namespace and retained rollback hashes before READY. Normal fresh admission
   after actual77 release; no old token. MechAgon remains first priority and
   Wolf may use finite gaps while this source preparation is incomplete.


The first separate fixture native build stopped before firmware build on a C++
list-initializer narrowing error in the provisional SDK sample mask. The bounded
uint8_t mask now has an explicit uint8_t cast, preserving C value semantics.
No source or IRQ runtime claim follows; recheck actual C binary equivalence and
compile the actual C++ fixture before hardware qualification. Compiler323 joined
and released normally; this was offline build preparation, not a physical retry.


### C3 foreground ownership observation — correction before installation

Source review of checked244030d found a real interleave: foreground mode request
reads pending0; UART0 IRQ defers and masks TXempty/sets pending1; the resumed
helper sees IERoff/TEMT1 and clears ownership. Pending-first ordering alone is
insufficient outside DI. The candidate was not installed, and its deployment
selection is withdrawn while its source/check evidence remains frozen.

Before another build, make the complete owned/pending/IER/TEMT observation a
bounded caller-IFF-preserving atomic leaf. Preserve BC, no spin/callback/byte
copy, retain disabled entry without EI and restore enabled entry once. Exact
linked validation must require this wrapper and its pending-first locked body.
This is an EMOS foreground composition defect, not a generic donor fault or
assigned76 cause. There is still no supported cancellation on arbitrary app
return/unload: callbacks plus later wire idle must retire positively, otherwise
retain storage/quarantine and recover before LOAD. The first quiet-UART0
isolation does not qualify cancellation. Wolf's qualified finite gap may run
while this source correction/owner runner remains unready.
