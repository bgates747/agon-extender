# PORT-008 — Native payload binding tranche

## Executive summary

The Author authorized F02c3 development on 2026-10-09. Implement private P4-PC
PARLIO RX/TX leaves and eZ80 assembly payload loops, with actual handover guards
and deterministic boundary tests. Reuse the current eleven-wire mapping and
proved forward clock; ordinary UART/HDMI behavior remains unchanged. This
tranche stops before physical activation: unresolved full drain/deadline/status
composition and ROM fit must not be bypassed merely because the bench is free.

N01 [x] — Reconcile pinned driver APIs, first/last-byte ownership, current board
mapping, assembler ABI and available ROM. Freeze this contract before edits.
N02 [x] — Add a private native P4 RX/TX payload adapter. Arm only at the admitted
handover's local-arm phase on the UART owner core after explicit completed UART
parking. Exact bounded buffers, externally clocked bytes, latched VALID edges,
release/acquire completion publication, bounded polling and explicit stop/pad
release. READY must not rise on cleanup failure. Keep final TX byte as idle
output until VALID ends. Do not reuse the old 74-series endpoint configuration.
N03 [x] — Add EMOS-owned assembly loops for both directions, with the same
CLOCK/VALID ownership and preservation of unrelated Port D bits. Entry requires
coordinator-owned parked pins and admitted handover state; no standalone public
GPIO/API bypass. Execute actual instructions against register/clock models;
check bounds, direction, first/last byte, IFF, ABI and failure cleanup. Measure
full candidate ROM; stop resident integration if the 131072-byte guard fails.
Do not place diagnostics in resident firmware or relax memory checks.
N04 [x] — Exercise both payload directions with real handover/adapter code and
fake SDK/register boundaries: failed allocation/configuration/start/stop, short
and late completion, wrong owner, stale callbacks, cancellation and no clocks.
Compile affected P4 and EMOS targets, record hashes, durations and exact limits.
Update parent/current docs. Stop for review before any live payload/flash.

## Bounded research and reuse

Official Agon GPIO documentation at agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` confirms Port C/D ownership and shared
UEXT signals; official MOS v3.0.2 and VDP v2.16.0 remain clean/read-only.
[GPIO](../../../../../agon-docs/docs/GPIO.md),
[forward proof](FORWARD-PROTOTYPE-REUSE.md),
[handover](HANDOVER.md), [development](BIDIRECTIONAL-DEVELOPMENT.md),
[P4 runtime recovery](P4-RUNTIME-RECOVERY.md) and retained reverse cores bound
this work. Current PC board mapping is `vdp/build/boards/p4-pc.json`, not the
old `p4_parallel_target_config.hpp` isolation circuit.

Pinned IDF5.5.5 source commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`:
`esp_driver_parlio/include/driver/parlio_tx.h`, `parlio_rx.h` and `src/parlio_tx.c`.
[TX documentation](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/parlio/parlio_tx.html)
defines bit lengths, external clocks, paired enable/disable and retained idle
output. Set TX idle_value to the final byte, then explicitly detach outputs;
disable alone never proves high impedance.
[RX documentation](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/parlio/parlio_rx.html)
and pinned level delimiter permit EOF on VALID release. Allocate one sentinel
byte beyond the admitted length to reject excess clocks; do not publish data
until exact completion and both VALID edges are observed. Short pulse capture,
first-byte alignment and final-byte electrical hold remain hardware gates.

EMOS code belongs in agon-emos under INTEG-016. The starting private candidate
has 130981 ROM bytes used /91 free; ordinary firmware has320 free. No unrelated
utility extraction, upstream edits, new wire IDs, mode command, SD transfer,
firmware flash or performance claim is authorized by this native-leaf tranche.

## Tranche result

Private leaves and software checks complete; resident integration stopped at
the required ROM gate (265 bytes over). See [results](NATIVE-PAYLOAD-RESULTS.md)
and the hashed result index. Parent F02c3 remains open for live coordinator
integration and ROM fit. Nothing was installed, committed or promoted.

The Author subsequently authorized the safety checkpoint and
[ROM-fit continuation](NATIVE-ROM-FIT-RESULTS.md). Prior work is committed/pushed;
the new full native EMOS image fits with 309 bytes free. The original result
above and its hashes remain historical evidence. Live coordinator binding and
physical qualification are still open.

Subsequent continuation: [LC02 software integration](LIVE-COORDINATOR-LC02-RESULTS.md)
now passes complete builds with the private coordinator bound but unactivated.
Its result supersedes the earlier integration/ROM position above; physical
qualification remains open. Historical identities and hashes remain unchanged.
