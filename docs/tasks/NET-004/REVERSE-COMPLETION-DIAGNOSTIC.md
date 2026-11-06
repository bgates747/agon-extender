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

N04-012.01 Publish this plan before changing code. [ ]

N04-012.02 Append the cached VALID count to the existing task-context TX failure
log only. Preserve the original fields and all successful-path behavior.
No new MMIO reads, ISR logging, checksums or recovery changes. [ ]

N04-012.03 Reserve the normal Pi compiler FIFO for the existing native payload
and counter sanitizer checks. One compiler at a time, at most 120 seconds total;
join owned children and release before reporting. Preserve exact output. [ ]

N04-012.04 Publish checked source and an honest diagnostic handoff. A full
identified P4 rebuild and installation are separate subsequent preparation;
this tranche produces no deployable firmware or physical qualification. [ ]

## Custody and installed disposition

MechAgon remains the sole operator during its current restoration/release.
Extender performs no target operation. Existing diagnostic EMOS stays retained
as explicitly handed back; the checked diagnostics-off ROM is available for a
separately selected rollback, not an obligatory flash before release. Record
actual installed identities for the next owner. Future owner reproduction
requires fresh normal admission and stopped operator handoff; never reuse the
old lease or rerun an uncertain transfer.
