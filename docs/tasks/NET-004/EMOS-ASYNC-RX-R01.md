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

1. [ ] Join actual eZ80 owner source/generated/linked code to the failed ROM.
   Inventory IRQ exclusions, RX STOP assertion/release, RX parser/app callback,
   UART0 and VBlank paths. Distinguish bounded native instruction paths from
   unbounded CTS waits and unmeasured callback work; do not invent cycle totals.
2. [ ] Join matched retained P4 source/IDF UART queue and hardware CTS setup to
   its installed artifact. Identify the maximum queued transmit path and actual
   source guarantees about STOP; do not infer electrical response from APIs.
3. [ ] Coordinate generic UART0/U1 contracts with UART owner. Keep its unchanged
   core/emitter; any generic correction is UART-owned. Extender may correct its
   derivative EMOS-specific admission/ISR glue, preserving register/IFF, RX/error
   sample, writer/mode guard, source/drain/reply and positive-close contracts.
4. [ ] Select the smallest concrete owner correction supported by those source
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
