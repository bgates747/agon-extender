# P4 reverse completion diagnostic

The P4 rejected a completed 93-byte reverse transfer before EMOS's next control
request stalled on blocked CTS. Retain the edge count already used by the P4's
proof so a later admitted reproduction can distinguish an extra/missing edge
from another backend rejection. The cause is unresolved; no timeout, polarity,
proof guard, ownership or protocol change is selected.

## Evidence and interpretation

MechAgon's retained r08 first-error record shows all three control-prefix bytes
unsent, UART1 LSR 0x60 and Port C 0xFB. PC3 is active-low peer CTS, therefore
blocked. Mainboard UART0 graphics does not directly drive the P4 UART1 RTS pad.
The earlier P4 USB record reports TX result 5, requested/completed 93 bytes,
DMA done, callback fault zero, CLOCK low and VALID high. TX result 5 denotes
backend fault. In the matched strict composition, the independent VALID proof
can reject exact DMA completion; its actual count was not logged.

Source references are `p4_native_payload.cpp`, `p4_parallel_egress.cpp` and
`p4_valid_counter.hpp` under `vdp/video/extender/transport/`. The selected
maintained P4 parent is 221e6207cc25adab344adb7adffe822ada1fbbda.
`observedCount()` returns only the cached value previously used by the proof;
it does not read a peripheral. It survives cleanup for the existing failure log.
A count alone cannot identify electrical noise, API failure or all proof races.

The reciprocal completion/recovery handshakes can restore UART after a failed
payload; a later UART-ready state does not retroactively prove payload success.
An exact DMA byte count likewise does not establish the independent edge proof.
Do not weaken those checks based on this observation.

## Finite source tranche

N04-012.01 Publish this plan before changing code. [x]

N04-012.02 Append the cached VALID count to the existing task-context TX failure
log only. Preserve the original fields and all successful-path behavior.
No new MMIO reads, ISR logging, checksums or recovery changes. [x]

N04-012.03 Reserve the normal Pi compiler FIFO for the existing native payload
and counter sanitizer checks. One compiler at a time, at most 120 seconds total;
join owned children and release before reporting. Preserve exact output. [x]

N04-012.04 Publish checked source and an honest diagnostic handoff. A full
identified P4 rebuild and installation are separate subsequent preparation;
this tranche produces no deployable firmware or physical qualification. [x]

## Custody and installed disposition

MechAgon remains the sole operator during its current restoration/release.
Extender performs no target operation. Existing diagnostic EMOS stays retained
as explicitly handed back; the checked diagnostics-off ROM is available for a
separately selected rollback, not an obligatory flash before release. Record
actual installed identities for the next owner. Future owner reproduction
requires fresh normal admission and stopped operator handoff; never reuse the
old lease or rerun an uncertain transfer.


## Checked source checkpoint

Plan c1aa8401 preceded code. Owner branch `codex/net004-valid-trace` commits
source e14e0b8a, adding `valid_edges` only to the existing TX failure line.
Strict compositions report the cached proof count; other compositions report
-1 because they have no strict counter. No MMIO inventory, successful-path
transport behavior, state transition, deadline or guard changes.

The initial existing ExExt compile check caught an unguarded reference to the
optional counter member. The corrected conditional-owner selection passes all
three existing test methods: 246 retained ExExt DMA cases, 213 native payload
cases and 70 counter cases, with address/undefined-behavior sanitizers. Final
check wall duration is 4.072 seconds on the host, not transport timing. Compiler
212 was released after all owned checks/children joined, with no successor.

This publishes checked source only. No new P4 firmware image was built or
installed. The physical cause remains unresolved; `valid_edges` may narrow a
later admitted capture but does not itself prove why the backend rejected it.
MechAgon subsequently restored its exact incoming mainboard application/tail
and cleanly released generation43; Wolf is first awaiting its current-binding
readiness. Retained diagnostic EMOS and existing P4 identities are explicit in
the private release record. Original r08 evidence remains unchanged.
