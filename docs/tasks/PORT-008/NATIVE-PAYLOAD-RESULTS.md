# PORT-008 — Native payload leaves: off-bench result

## Executive summary

Private P4 PARLIO RX/TX and EMOS assembly payload leaves now pass focused
software checks. Real P4-PC compilation passes. The complete EMOS composition
correctly fails the unchanged ROM guard: the addition needs 356 bytes when
only 91 were available, an overflow of 265 bytes. No oversized firmware was
emitted. No flash, reset, physical link test or production change occurred.
Live coordinator integration and hardware proof remain open in F02c2/F02c3.

## Implementation and checks

1. P4 `p4_native_payload.cpp` uses the selected board's supplied pin array,
   external eZ80 CLOCK, active-low VALID and exact 1..4096-byte records. It arms
   only on the owner core, at the real handover local-arm phase, after the
   caller reports completed UART parking. The caller must bind direction and
   length to its retained offer. Cancellation of the handover invalidates the
   leaf; it does not itself establish admission or commit ExExt.
2. P4 receives into internal DMA storage with an excess-byte sentinel. It
   copies exact received data into the caller's provisional buffer only after
   DMA/ISR shutdown, pad release and READY publication succeed. TX retains
   the last byte as PARLIO idle data until VALID release. Both paths require
   completion plus the latched VALID start/end; final inactive level alone is
   insufficient. Out-of-order/repeated edges, foreign/duplicate callbacks,
   timeout and SDK failures reject the record. Failed cleanup retains storage
   and context and cannot advertise a new release. The owner must remain alive
   and retry explicit cancellation; no automatic destructor recovery exists.
3. EMOS `emos_parallel_native.c` checks the caller's parked grant, block phase,
   bounds, direction, UART exclusion and actual GPIO configuration before
   calling `emos_parallel_native_io.asm`. EMOS clocks both directions, tests
   READY before every byte, releases data/VALID on return and preserves
   unrelated Port D bits across modeled ISR updates. Only the Port D RMW is
   interrupt-masked. This bounded leaf has no READY wait, UART restoration,
   mode command or public MOS API. The coordinator must still apply admission
   and completion deadlines, quarantine provisional RX bytes, and exchange
   matching UART status. Successful byte emission is not transfer success.
4. The P4 build selects its new source/dependency only with the explicit
   private boot candidate flag. EMOS selects the addition only through
   `port/parallel-native-candidate.mk`. Ordinary build selections exclude both.
   The old DevKit/isolation-chip endpoint was not rebound to the P4-PC harness.

| Check | Result | Scope |
| --- | ---: | --- |
| P4 native adapter | 151 cases pass | Real adapter/handover/egress; fake SDK boundary, ASan/UBSan |
| EMOS native payload | 124 cases pass | Actual compiled C/assembly in pinned eZ80 interpreter; modeled registers |
| Existing paired reverse core | 48 cases pass | Software wires; retained reference path |
| Existing boot/runtime adapters | 718 cases pass | Real leaves/sequencers; modeled GPIO/SDK |
| Existing P4 runtime reset suite | 4 tests pass | Host transport cancellation |
| P4 profile selection | 12 tests pass | Private source exclusion and existing profile contracts |
| P4-PC native IDF build/validator | Pass | Final source snapshot verified; unbound payload object compiled |
| Full EMOS resident link | Refused as required | ROM capacity gate; not an installable candidate |

The instruction tests cover 1, 2, 3, 7, 255, 256, 257, 1024, 4095 and 4096
bytes in both directions and both IFF states, zero/oversized/null calls,
missing ownership and GPIO grants, READY loss, byte/edge order, buffer guards,
IX/SP/IFF and the raw assembly helper's IY preservation. C's IY register is
caller-clobbered under the existing compiler ABI; no new ABI is inferred.
These independent boundary models are not a physical end-to-end test.

## ROM and timing

Worst ROM fit first. Baseline is the preceding private candidate (130981
bytes). The addition is 356 /130981 = 0.272%; capacity remains 131072 bytes.
Neither row below is a new installed firmware identity.

| EMOS composition | ROM bytes | Difference from baseline | Capacity margin |
| --- | ---: | ---: | ---: |
| Private candidate plus native leaves | 131337 | +356 (+0.272%) | 265 bytes over |
| Previous private boot/runtime candidate | 130981 | Baseline | 91 bytes free |

C guard: 210 object text bytes; assembly: 146. No extra static RAM is defined
by these two objects. Runtime stack consumption is not separately qualified.
The retained generic C receive reference remains present; replacing redundant
reference code is a potential next source of space, not a performed change.

Native host compilation/tests took 1.465 host seconds; the actual interpreter
execution took 0.108 host seconds with an already built test executable. Other
suite durations and final incremental IDF duration are retained in the result
index. Initial complete IDF compilation duration was not separately measured.
All use host monotonic clocks, not calibrated eZ80 or GPIO timing. No throughput
or performance improvement is claimed.

## Evidence and next boundary

[Result index](NATIVE-PAYLOAD-RESULT.json) preserves source/artifact hashes,
ROM measurements and test durations. Machine-local evidence lives under
`agents/port008-native-payload`; the initial complete P4 build is retained
separately from the final incremental source/archive/validator record.
The final adapter is unreferenced by the live console and may be removed from
the final app by the linker; compilation is not payload activation.

EMOS has a reproducible RAM-only test linker, `tests/link_parallel_native.py`.
After the maintained private-profile compile attempt, give it the builder's
`projects/mos-port` directory, toolchain and fresh output directory. Then run
`parallel_native` using the existing `tests/uart_put_cpu/Cargo.toml` with that
output directory. The image loads at 0x40000 only in the instruction interpreter;
it is not firmware and must never be flashed or used as a MOS executable.

Before any bench payload test: resolve ROM fit, compose complete packet drain,
per-phase deadlines and matched status with the retained admission and parking
owners, then review actual GPIO/driver configuration. Hardware must establish
first-byte alignment, final-byte hold, short VALID pulse capture, reset behavior
and contention. The GPIO ISR can miss coalesced pulses; software timeout does
not prove electrical capture. Native API success cannot waive these gates.
No current supported user procedure or production selection changed. Changes
remain uncommitted for Author review; unrelated EMOS application_peer.py was
not edited or staged.
