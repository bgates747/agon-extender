# PORT-008 — Isolate modern forward and reverse corruption

## Executive summary

The repaired P4-PC passes the historical forward-only sweep, but the modern
full-HDMI paired comparison still fails a255byte roundtrip atoffset2. Determine
which modern direction corrupts data before implementing a remedy. Author
approved this bounded plan on2026-10-11: freeze/push, execute the first two
checks, recover ordinary input and pause for discussion.

DI01 [ ] — Reuse the existing private retained-data endpoint and snapshot hook.
EMOS sends a position-dependent1024byte pattern through its existing gateway
and native sender. P4 compares **every retained byte** with the known pattern
only after matched completion and reciprocal UART restoration. Report mismatch
count, first offset/actual/expected, FNV and bounded first/last bytes over USB.
Do not infer integrity merely from DMA callbacks or matching fingerprints.
Keep full-HDMI services, native leaf, coordinator, control sequence and installed
EMOS unchanged. No per-byte logging in the transfer, ISR tracing or edge counters.

DI02 [ ] — P4 generates a separate deterministic1024byte pattern locally before
arming TX; it does not echo RX storage. The MOSlet independently invokes reverse
transfer and compares every byte/guards. Report source integrity at P4 before
transfer and retained integrity after return. Distinguish a bad source from a
reverse-path corruption. This is a compile-selected private diagnostic variant
of the existing endpoint, with prominent source comments, not a public protocol
or production service. No new wire opcodes or raw application GPIO bypass.

DI03 [ ] — Build/check the endpoint's lifecycle, expected-vector computation,
bounds, rejection and independent reverse preparation. Compile the adapted
existing MOSlet. Verify exact artifacts before flashing the P4 and deploying the
MOSlet over the ordinary UART listener. Read back deployed executable and original
startup; invoke directly from the CLI, never autoexec. No EMOS reflash or backup.
After P4 installation, permit one explicit Agon recovery reset if needed for the
known boot-admission fault; record that separately from payload correctness.

DI04 [ ] — Run each direction once with fresh durable CSV paths. Forward integrity
failure does not prevent the independent reverse experiment; transport cleanup
or readiness failure does. No uncertain replay. Collect passive bounded USB
output without serial-control reset, and compare P4 and Agon evidence. Restore
the exact preceding matched full-HDMI comparison P4 image, verify all segments,
original startup and ready/neutral input, close listener/collector and record
handback. Do not roll back to pre-handshake firmware against current EMOS.

DI05 [ ] — Pause with a direction-specific result. Only after Author discussion,
compare the failing native implementation/configuration/cache/publication/GPIO
sequence against the proven historical implementation and change one variable
at a time. Then rerun the existing roundtrip/boundary/direction/recovery checks.
This item is **not authorized for execution in this tranche**.

## Research boundary and evidence

Reuse pinned official references in [native payload](NATIVE-PAYLOAD.md), the
[prior snapshot mechanism](DATA-SNAPSHOT-R01.md), and the
[historical/modern results](DEVKIT-CONTROL-R01.md). Official checkouts stay
read-only. Firmware build and physical identities follow the version policy;
local endpoints, serial identity, manifests and evidence live in ignored
`agents/port008-live-qualification/direction-isolation-r01/`.

Pattern is the existing parcheck function:
`uint8_t((i*73)^((i>>3)*29)^(i>>8)^0x69)`.
A1024byte block directly matches the historical size, but the sender/protocol
and normalHDMI composition differ; this is direction isolation, not a controlled
performance comparison. No throughput claim, mode implementation, electrical
repair, warm-reset fix or production promotion is in scope.
