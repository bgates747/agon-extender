# P01f A — findings and next discrimination

## Executive summary

**The port has an identifiable scheduling dependency; the failed priority test
did not cleanly test its remedy.** A low-priority snapshot task can retain the
native graphics mutex while networking runs. Parser/drawing then need that same
mutex. Mainboard scanline preparation runs in an ISR without this task-mutex
dependency. Immutable web leases already keep actual sending outside the native
mutex, so simply “unlock before sending” would change nothing on this path.

The S treatment added **192 scheduler-yield requests, 384 priority changes and
768 priority queries per complete 384-row snapshot**. Those are source-derived
API counts, not measured context switches or elapsed costs. Priority inheritance
can additionally carry its boost into foreground work beyond a single native
unlock. The audit establishes these mechanisms, not that they explain the whole
regression or terminal query timeout.

Recommend one bounded next experiment: apply the same ceiling **once per
admitted snapshot**, restoring it before publication, while retaining every
two-row mutex boundary and all original rendering. This removes the repeated
priority transitions, but also raises normalization priority; both differences
must be stated. It is a diagnostic candidate for Author review, not an approved
fix, not evidence that priority19 is the eventual policy. No build/flash/test was
performed during this audit.

## Existing performance evidence, not new measurements

Worst diagnostic pacing first. Delta is `(P4 − historical mainboard) / mainboard`;
larger spacing is worse. Historical mainboard was not rerun. Failed S treatment
must not be presented as a qualified benchmark.

| Condition | Completed refreshes/s | Refresh spacing p95 ms | p95 difference vs mainboard | Status |
|---|---:|---:|---:|---|
| S priority per row pair | 39.971 | 53.909 | +215.94% | Terminal query failed15; diagnostic only |
| B streaming second | 60.053 | 29.291 | +71.66% | Valid run; pacing parity fails |
| B streaming first | 60.056 | 24.990 | +46.46% | Valid run; pacing parity fails |
| S same-image control | 60.046 | 21.345 | +25.10% | Valid control |
| Mainboard reference | 59.927 | 17.063 | baseline | Historical retained fixture |
| B output disabled | 60.053 | 17.052 | −0.06% | Valid run |

| S operation, wall time | Control ms | Failed treatment ms | Difference vs control |
|---|---:|---:|---:|
| Full snapshot composition mean | 6.725 | 28.897 | +329.70% |
| Full-frame socket send mean | 17.790 | 17.267 | −2.94% |

These wall scopes include blocking/preemption and can overlap. They are not
exclusive CPU costs or single-bitmap drawing times. B streaming delivered
27.232–28.226 game-window sends/s; that remains distinct from roughly60 native
refresh completions/s. Scope is SW2400 Nurples-derived fixture, not new Rally or
hardware-sprite testing. Full values/raw records: parent B tables, S/TABLES.md,
P01cd and P01e. Golem excluded.

## Indexed findings

1. **A-F01 — Shared ownership is the concrete coupling.** `prepareRows` holds
   N while executing retained row bodies. Parser mutations and drawing also
   acquire N. P01e captured one25.210ms hold with24.737ms of same-core `tiT`
   residency; P01cd separately measured parser/drawing waits around22ms under
   streaming. This supports investigating owner descheduling. It does not align
   those separate runs' individual waiters, measure exclusive TCP/IP CPU time,
   or prove that one rare hold explains the full p95 distribution.
2. **A-F02 — S inserted a scheduler boundary after every row pair.** In pinned
   SDK `tasks.c::vTaskPrioritySet` (around1785–1955), lowering the currently
   running task's base priority sets `xYieldRequired`, then invokes
   `taskYIELD_IF_USING_PREEMPTION`. The selected RISC-V port sends a yield interrupt to the calling core;
   it is deferred until the kernel critical section exits. The S destructor calls this after N is released and before
   normalization. With192 batches: two sets and four `uxTaskPriorityGet` calls
   per batch, plus192 yield requests. Queries/sets enter kernel critical
   sections; their cost was not cancelled by a disabled same-image control.
   A request need not switch to another task. No numerical CPU-cost estimate
   is justified by these counts alone.
3. **A-F03 — The priority effect can spread and persist.** Before acquiring N,
   S raises the snapshot waiter to19. FreeRTOS can promote N's current holder.
   `xTaskPriorityDisinherit` only restores base priority after the holder's
   count of held mutexes reaches zero. A parser holding F and N can therefore
   retain19 after releasing N until F is released. Recursive depth is released
   at the outermost give, not every nested unlock. This is SDK behavior, not a
   newly discovered RTOS defect. The S report already warned of propagation;
   this audit adds the exact retention condition and F → N path.
4. **A-F04 — The S guard restores the snapshot's own priority at the intended
   boundary.** It saves priority before acquiring N and lowers after all row
   guards unwind. No source evidence of an accidental permanent19 setting was
   found on its normal path. The failed run's complete ordered2400-record trace
   and zero unfinished output accounting weigh against a permanent graphics
   deadlock, but do not explain the later pixel query timeout.
5. **A-F05 — No direct framebuffer-lock/socket-send cycle was found.** HTTP
   sends immutable leased data, retaining dispatch D but not native N. Provider
   and pool locks protect short metadata transitions. The selected pool uses
   the corrected blocking mutex, not its historical starvation-prone spin
   branch. [Ownership map](OWNERSHIP.md) records actual nesting and scoped
   negative evidence. This is not a whole-firmware absence-of-deadlock proof.
6. **A-F06 — Copying the ISR's row count did not copy its scheduling contract.**
   Physical VGA scanout prepares/decorates rows in an ISR; P4 does it in a
   preemptible task under a newly added mutex. Identical two-row code is thus
   necessary rendering fidelity, not equivalent timing. Original Agon disables
   the optional primitive time budget, and its suspension routine is a
   counter/wait despite the “vertical sync interrupt” comment. Neither an
   artificial blanking budget nor blanket interrupt masking is justified.
7. **A-F07 — Allocation is real but not established as this fixture's cause.**
   Sprite/background mutation and retained dynamic primitive allocation can
   run under exclusion. The inherited pool retry yields while the port keeps F;
   inherited priority could matter for future transformed/path workloads.
   SW2400 largely reuses assets. Snapshot slot acquisition itself does not
   allocate a full frame each time. Earlier internal-memory controls did not
   remove the tail, and S control/treatment free-heap layout differed. Keep
   allocation/layout as a confound; do not relabel it a measured allocator stall.
8. **A-F08 — Network execution remains distributed.** HTTP's “async” WebSocket
   function calls the socket sender in the HTTP callback. Selected lwIP hands
   work to `tiT` through mailbox/semaphore. Moving only the priority3 dispatcher
   misses HTTP5, TCP/IP18, Ethernet RX15 and interrupts. Runtime residency and
   runnable state are not fully characterized; the audit provides no basis to
   assert that every24ms `tiT` residency consists of packet-processing CPU.

## Review of alternatives and missing observations

| Explanation | Evidence for / against | Remaining limitation |
|---|---|---|
| Owner preempted while N blocks graphics | Source path plus retained owner trace and streamed wait maxima | Representative same-run owner/waiter/refresh correlation remains missing; heavy trace candidate changed performance. |
| Per-row scheduler/priority machinery caused S regression | Newly enumerated forced yield path; S composition worsened much more than send | No measured cost attribution; priority propagation, network relocation and memory/order changes remain. |
| Wrong priority restore or simple lock-order deadlock | Normal guard lifetime is correct; complete2400 traces | Transient long waits remain possible; terminal query failure is unresolved. |
| Socket holds graphics mutex for entire send | Audited call graph rules this out | Network can still delay N's owner through scheduling, interrupts or shared memory. |
| Pure PSRAM bottleneck | Prior all-internal framebuffer controls still had tails | Other buffers and SDK allocations still use memory/cache; memory contention not disproved. |
| Port needs assembly or removal of RTOS | No evidence of an identified CPU-bound instruction loop explaining these waits | Such changes do not inherently repair ownership or scheduling. |
| Reuse old same-core policy | r35 core0/priority2 starved; r36 priority4 degraded | Those results remain rejected. New proposal below does not revive them. |

No source-only audit can apportion the21–54ms completion tails among runnable
delay, lock wait, actual drawing, transport-related interrupts and shared-memory
stalls. The answer so far is a verified dependency and a confounded intervention,
not a proven single root cause or completed performance fix.

## Next experiment proposed for review — one scope change

**Agent recommendation, not yet authorized for implementation by this report.**
Use the existing low-overhead r45-derived diagnostic and unchanged SW2400/wired
observer. Control is ordinary base2 output. Treatment uses19 once after a
snapshot slot has been admitted, before the first row, and restores2 after the
last normalization, before `snapshots.finish`. Preserve N per two rows, row
order, full payload, demand/lookahead, all other priorities/affinities and IRQs.
Restore on stop/early exit as well. No high priority while idle or waiting for
browser credit. No owner-trace rings or per-row diagnostic output.

This reduces full-frame priority API work from384sets/768queries/192yield
requests to2sets/4queries/1yield request, retaining the same nominal ceiling
and core. It tests whether the ceiling remains harmful after removing repeated
transitions. It also raises normalization priority and can move eligible network
work onto core0; therefore it is **not** a pure “cost per yield” measurement.
Inheritance into native holders also remains. A good result would justify a
second measured design decision, not automatic shipment at19.

1. Freeze a separate implementation/test contract before code. Reuse exact
   archived source and verify selected branches; normal current source contains
   unrelated dormant diagnostic hooks that must not enter the candidate.
2. Host-check scope lifetimes/early exits; inspect linked API placement. One
   matched image and control/treatment/treatment/control with identical startup
   and recorded memory placement. Do not rerun the known failing per-row variant
   merely to produce another failure. About14minutes retained observation time,
   plus preparation and rollback; not an automatic reset deadline.
3. Retain S's baseline admission58–62refresh/s and p95≥20ms. Require2400matching
   states/ordered completions, successful terminal query, no output accounting
   failure, valid browser pixels/sequence, working keyboard and SD. Stop on
   first failure; preserve evidence, restore r43/startup and notify.
4. Record per-operation wall times, achieved composition/send rates and refresh
   p95/p99/max, never merely average FPS. If repeat controls are materially
   different, stop at inconclusive. No claims from fewer frames or reduced work.
5. If it improves, the next decision is how to obtain bounded ownership without
   unnecessary scheduler transitions and without displacing rendering/network
   elsewhere. If it still harms pacing or correctness, retire this priority
   remedy instead of sweeping more numeric priorities. Review a single graphics
   owner/cooperative snapshot handoff as a separate architecture experiment,
   including parser/lifecycle/hardware-sprite contracts; do not implement that
   redesign inside this test.

No repetition of the broad research survey is needed before this discrimination.
AUDIT-007 remains mandatory and separately scheduled; A only supplies focused
findings. RLE, output load ramp, chunk pacing, fixed frame-rate fallback and
assembly remain in their existing downstream buckets.
