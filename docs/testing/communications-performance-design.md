# UART1 versus eight-bit parallel performance — design r01

The main performance objective of Extender is faster communication between MOS
and the VDP. A faster renderer is a separate benefit. This comparison will
measure what the carrier contributes while keeping the eZ80, P4 renderer,
logical workload and output requirements matched. It must establish gains or
regressions rather than assume that an eight-bit link is faster.

**State:** Design only. [COMMS-002](../tasks/COMMS-002.md) owns implementation and
qualification. This is a separate test program, run and result set from the
[accuracy/endurance appliance](communications-accuracy-design.md). Neither
test's timings or outcomes substitute for the other's evidence.

## 1. Questions and comparison boundary

1. How long does UART1 versus parallel take to carry the same logical MOS→P4
   VDU command stream or opaque data block, and to return the same reply?
2. Where is the crossover between small-command setup cost and sustained
   transfer gains? How much do admission, batching, turnaround and ownership
   return cost?
3. What eZ80 work is required or prevented while transmission completes? Lower
   elapsed time is not by itself lower CPU occupation or asynchronous progress.
4. Does a carrier gain reduce complete application time with the same renderer,
   or is the renderer/application pacing the limiting factor?
5. The primary comparison is eZ80/EMOS↔P4, UART1 against eight-bit parallel.
   Changing from a mainboard VDP to a P4 renderer at the same time is not this
   comparison. UART0 graphics, Pi networking and consumer integration are
   separately labelled contexts when selected, never substitutes for the local
   carrier measurements.

## 2. Independent benchmark

1. Use a dedicated benchmark executable, coordinator, configuration, invocation,
   SD output namespace and result schema. Do not time the endurance fixture's
   CRC/retry/logging loop or add speed verdicts to that fixture.
2. Shared source may be limited to already-qualified transport helpers or
   immutable workload data. Performance must not require a full hours-long
   endurance run, its fault injector, or its mixed-leg service to execute.
3. Retain correctness checks before/after measured batches and a receiver
   completion witness. Reject corrupt, incomplete or failed samples instead of
   counting them as fast. Do not add an in-band CRC/retry protocol to ordinary
   carrier traffic as an incidental benchmark feature. Preserve strict existing
   framing, count, ownership and completion checks in both arms.
4. No deliberate faults or retry-until-success timing. An unexpected failure
   stops the selected benchmark tranche and is reported separately. The accuracy
   appliance owns fault detection/endurance/repeat behaviour.

## 3. Matched arms and workload families

| Workload family | UART1 arm | Parallel arm | What stays equal |
|---|---|---|---|
| Transfer-only sink | Supported UART1 path | Supported eight-bit path | Logical bytes, receiver sink/check, block schedule |
| Short VDU commands | Ordinary admitted UART1 VDU path | Admitted parallel VDU path | Same commands, target renderer, required reply/fence |
| Medium VDU batches | Same logical batch | Same logical batch | Commands, parser work, state and output |
| Sustained buffer/image VDU stream | Same stream | Same stream | Payload, format, resources and completed output |
| Reply/turnaround | UART1 return | Parallel return | Same request/result semantics and completion |
| Application-shaped replay | Selected UART1 binding | Selected parallel binding | Same deterministic input, rendering and completion requirements |

1. Vary legal logical sizes, including isolated tiny commands, realistic command
   batches and long streams. Select exact sizes after checking the actual API
   limits. Keep logical application batching equal; record carrier-specific
   fragmentation, overhead and transactions instead of inventing an unrestricted
   raw API or handicapping one arm with unnecessary handshakes.
2. Prefer one matched pair exposing both explicit carrier choices. If separate
   firmware compositions are necessary, pin their minimum transport-only delta
   and prove renderer/features/configuration/clocks equal. Label results as the
   supported carrier paths, not pure electrical bus speed.
3. Preserve P4/eZ80 clocks, baud, physical wiring, receiver state, image format,
   display mode and output-completion requirements. Warm/cold setup is explicit.
   Installation/reset/boot and setup time never disappear into a sample.
4. Interleave/reverse matched batches, such as ABBA, to expose drift. Record every
   invocation and failed/incomplete sample. Use repeated controls and enough
   work for the selected timer resolution; do not claim calibrated absolute
   rates from nominal clocks alone.
5. Start with local sink and real VDU streams. A deterministic application replay
   then tests practical benefit. Live Pi/network/game time, if selected later,
   is additional evidence with its own variability, not the primary bus verdict.

## 4. Measurement scopes

| Scope | Begin/end | Interpretation |
|---|---|---|
| Caller/source lifetime | Public submit entry → positive source release | How long the application must retain its input |
| Complete transfer | Owner admission entry → receiver complete-byte witness | Software/handshake/transport cost, including actual waits |
| Setup and turnaround | Per-session/per-batch admission and direction/return boundaries | Fixed overhead and cost of small transactions |
| VDP execution | Receiver command start → required execution fence | Same P4 renderer/parser work, separate from transport |
| Complete workload | Application work entry → all required replies/output completion | Practical effect of the selected carrier path |
| eZ80 occupation/progress | Explicitly instrumented busy/wait/service or available-work evidence | CPU cost/opportunity; never inferred from wall time alone |

1. Use local clocks within each endpoint. The selected EMOS nominal clock is
   120 counts/s; P4 and Pi use separately identified monotonic clocks. No
   subtraction across unsynchronised epochs. Short intervals require an
   appropriately qualified timer or longer measured batches, not invented
   sub-tick precision.
2. Receiver rendering may overlap transport. Do not add overlapping scopes and
   claim the sum is total application time. Source release, DMA completion,
   receiver acceptance, command execution and visible presentation are distinct.
3. Logging, result retrieval and outside-window validation costs are recorded
   separately. Any instrumentation retained inside the measured path is matched
   and disclosed. No additional physical probes are required by this design.
4. Record eZ80 busy-wait work and useful foreground/interrupt progress only where
   instrumentation actually supports that interpretation. Mark CPU utilisation
   unknown if unavailable; a synchronous return or faster wire is not a CPU
   percentage measurement.
5. Report UART1 baseline and parallel side by side, bytes and units explicit,
   with medians/tails/worst cases, dispersion and sample count. Define elapsed
   reduction as `(UART1 - parallel) / UART1 * 100%`; negative values are
   regressions. Keep rendering, transport, CPU and complete-workload tables
   separate. Identify the tested break-even size/workload if the data supports it.

## 5. Ownership, qualification and delivery

1. EMOS owns ordinary VDU routing, mode and transport selection. P4 owns its
   receive/peripheral/buffer lifecycle. The Agon benchmark calls supported owner
   APIs; no direct register bypass or route-independent VDU injection.
2. Check the actual UART1 and parallel VDU/data interfaces before coding.
   Existing `ext.net`/`ext.netp` network providers are distinct compositions;
   a network message comparison alone cannot qualify MOS↔VDP stream acceleration.
3. Freeze source/configuration, exact binaries, supported completion contracts,
   workload, clocks, timers, instrumentation and rollback before target work.
   Qualify output equality, timer boundaries and failure refusal offline first.
4. Use normal fresh reservations and sole custody, explicit CLI invocation,
   normal startup preservation, mode settling and entry-state/CLI cleanup.
   Wolf's retained lease is not available merely because its hardware is idle.
5. Publish a bounded first comparison, including losses and limitations, before
   proposing optimisations. Use the accuracy appliance's separate findings to
   choose sensible failure-sensitive workloads; do not merge their runs or
   turn absence of benchmark failures into endurance qualification.

## 6. Basis

The [appliance lifecycle](../procedures/test-appliances.md) and
[execution protocol](../procedures/test-execution.md) govern this separate test.
The [parallel application contract](../protocols/application-network-parallel.md)
and [repeated result](../tasks/PARALLEL-001/REPEAT-RESULT-R01.md) distinguish bounded
transport proof from speed evidence. The existing
[live result](../tasks/PARALLEL-001/LIVE-RESULT-R01.md) records composite timing,
not an isolated matched UART1/parallel speedup. No new measured gain is claimed.
