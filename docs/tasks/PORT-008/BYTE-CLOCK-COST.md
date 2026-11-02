# Native parallel byte-clock cost

The existing parallel payload has no per-byte receiver acknowledgement. The
eZ80 nevertheless spends repeated calls, interrupt-state saves and general
length arithmetic on each byte. Remove that avoidable CPU work first, retaining
the existing electrical behavior and measuring actual linked instructions and
firmware space before any hardware performance claim. The Author authorizes
Extender implementation after agreement with UART; that agreement is recorded
in the [shared contract](../../../../agon-dev-env/cross-agent/parallel_uart_async/contract.md).

## Scope and decisions

1. BC-D01 — Implement the first bounded Extender increment in EMOS's private
   native assembly leaf. Keep the physical byte/clock/VALID ordering, READY
   abort check, forward-only 16 inactive start clocks and 16 inactive tail
   clocks, guarded coordinator, control carrier and 4096-byte maximum unchanged.
   This is a CPU-cost change, not the new async admission API or a proof of
   whole-request single-handshake operation.
2. BC-D02 — Select enabled/masked loops once using the caller's IFF state.
   Inline the payload clock edge pair; when enabled, mask only the short Port D
   read/modify/write pair and reenable interrupts between bytes. Each pair must
   preserve freshly read ISR-owned Port D bits. Do not cache an epoch-start
   Port D value, mask interrupts across a block or add per-byte instrumentation.
3. BC-D03 — Replace repeated 16-bit decrement/nonzero tests with bounded
   inner/outer counts if linked instruction evidence shows an improvement.
   The guard's 1..4096 bound remains; test byte/page edges and early aborts.
4. BC-D04 — No new public MOS index, callback ABI, queue, payload copy,
   resident diagnostics, P4 source change, wire version, firmware identity
   increment or production selection is needed for this internal increment.
   The agreed request/completion model remains the authority for later async
   admission integration, not a feature claimed by this patch.

## Bounded research

1. Official documentation `agon-docs` commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`:
   [GPIO](../../../../../agon-docs/docs/GPIO.md) establishes shared physical
   connections; [MOS API](../../../../../agon-docs/docs/mos/API.md) defines
   RST10/18 and interrupt APIs. The private native leaf changes none of these.
2. Official read-only sources remain MOS v3.0.2
   `8336409351ee5314e02801a7b72a4f1bb5282519` and VDP v2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. Pre-existing untracked desktop
   metadata in the docs reference is preserved; no reference tree is repaired
   or modified by this work.
3. Maintained owners: EMOS `src/emos_parallel_native_body.inc`, C guard
   `src/emos_parallel_native.c`, coordinator `src/emos_parallel_coordinator.c`;
   P4 `vdp/video/extender/transport/p4_native_payload.cpp` already uses PARLIO
   hardware/DMA with an external eZ80 clock. Both byte directions currently
   sample READY as an abort level, not a fresh per-byte acknowledgement.
4. Existing linked eZ80 test `tests/uart_put_cpu/src/bin/parallel_native.rs`
   already models live changes to unrelated Port D bits, bytes/edges, bounds,
   READY withdrawal and IFF/ABI. Extend it for every 1..4096 length and retain
   deterministic instruction counts; model counts are not calibrated hardware
   cycles or throughput. Update exact linked-owner guards for the intentional
   new loop sites rather than weakening them.

## Work and validation

1. [x] BC01 — Record the shared UART contract/Author authorization and current
   EMOS implementation scope; retain unchanged source/build baseline.
2. [x] BC02 — Implement the private loop optimization in the EMOS owner with
   comments beside its timing/IFF behavior and no new wire operations.
3. [x] BC03 — Execute actual linked C/assembly for both directions and entry
   IFF states, lengths 1..4096, page boundaries, partial/initial READY loss,
   register/stack/buffer bounds and fresh Port D interleavings. Compare matched
   baseline/changed instruction counts; negative controls must reject missing
   atomic masking, wrong counts or a corrupted owner/call instruction.
4. [x] BC04 — Build through EMOS wrappers with all profile-owned linked/ROM/
   divisor checks; compare full ROM and static RAM with the same profile and
   tools, including timing/non-timing wrapper coverage. Preserve source/config/
   image identities and explain any size change. No emulator GUI or hardware
   execution is part of this offline increment.
5. [x] BC05 — Record results and remaining async admission/burst work in the
   parent task and dated logs. Notify UART through mail of relevant findings,
   followed by a short steering alert. No physical speedup or general async
   implementation claim without the corresponding evidence.

Bench deployment, physical clock-rate qualification and new public async
interfaces need their own concrete continuation contract/procedure. This
increment does not activate a new transport, alter startup or take the bench.

[Results](BYTE-CLOCK-COST-RESULTS.md) and
[portable evidence](BYTE-CLOCK-COST-EVIDENCE.json) retain the completed offline
implementation: 16,492 instruction cases, exact linked negative controls,
matched full builds, roughly 40% fewer enabled-path instructions and 128 extra
ROM bytes with unchanged RAM. Physical performance remains unqualified.
UART receives the implementation findings through `parallel-byte-clock-results-six`
and the short steering chat alert. EMOS source checkpoint is `08301e6`; the
shared contract is preserved in `agon-dev-env` commit `46be75c`.
