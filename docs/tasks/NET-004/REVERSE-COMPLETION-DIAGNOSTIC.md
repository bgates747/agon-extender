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


## Consumer r10 source interpretation — 2026-11-06

MechAgon's later selected capture used installed diagnostic02addd54 and retained
EMOS8270 under its sole physical custody. The P4 failure now records requested93,
DMA done1/bytes93, callbackfault0, and cached `valid_edges=5`, then backendFault5
at native completion. The strict VALID proof starts at zero, counts both edge
polarities and requires exactly2; a sampled5 therefore takes its excess-count
failure branch. This attributes the backend rejection to the framing proof.
It does not establish where the extra counted transitions originated, validate
end-to-end payload contents, or turn exact DMA bytes into a successful block.

The odd cached count and later logged VALID-high are not an atomic snapshot.
The counter sample can precede additional pin activity, stop/cleanup and the
later GPIO log read. Do not infer parity/counter arithmetic failure from that
pair, or relax acceptance to count>=2. Pinned IDF5.5.5 `pulse_cnt.c` writes the
observed value and returns ESP_OK; the normal parameter-error path cannot
produce this populated5 from its local initial-1.

The retained native first16B SD witness equals the application RAM copy and
records deadline/three prefix bytes remaining, UART1 LSR0x60 and PortC0xFB:
FIFO/shifter empty, active-low CTS blocked, zero prefix transmission. This is
consistent with the next control request following the P4 block rejection.
Native evidence supports one decision/one FRAME; the host's52ticks/104colourstates
are a separate scope and do not count physical frames. Original fault/teardown
limitations remain; recovery is not an ordered native-exit pass.

Source review identifies an existing remedy to evaluate, not a selected change:
`p4_parallel_upload.cpp` already enables the fixed two-IO_MUX-cycle VALID pin
filter before capture, alongside CLOCK filtering, with exact VALID2 proof
retained. The bounded native TX leaf filters CLOCK but not VALID. The earlier
[upload repair](../PORT-008/UPLOAD-REPAIR-R01.md) passed bounded controls after
this mechanism was added, without proving the electrical source. Reusing that
existing filter inside the native owner's lifecycle is the narrow next candidate;
its actual partial-setup/cleanup/fault tests, tiny valid payload intervals and
continued rejection of sustained extra intervals must remain. No configurable
long debounce, software checksum, deadline increase or guard removal is implied.
EMOS's reviewed atomic PortD writes show one payload VALID-low then VALID-high,
held for the return handshake; no source-established extra software transition
was identified in this consultation.

This consultation changes no source, builds or hardware. Extender remains
stopped while MechAgon owns recovery, RAM preservation, exact native restoration
and release. Retain diagnostic02addd54/EMOS8270 for honest handback; the new evidence
does not itself require rolling back the diagnostic to its parent. The next
implementation/build/capture still needs concrete owner selection and normal
fresh admission. Production status remains unchanged.
