# PORT-008 — Isolate modern forward and reverse corruption

## Executive summary

The modern 1,024-byte forward path passes exact P4 retained-byte comparison.
Independent reverse transmission produces 955 incorrect Agon bytes, first at
offset 2, despite correct P4 source before/after transmission. This establishes
a reverse-path defect without echo contamination; its electrical/DMA/sampling
location remains open. Exact preceding matched HDMI firmware and ordinary input are restored. Author
approved this bounded plan on2026-10-11: freeze/push, execute the first two
checks, recover ordinary input and pause for discussion.

DI01 [x] — Reuse the existing private retained-data endpoint and snapshot hook.
EMOS sends a position-dependent1,024-byte pattern through its existing gateway
and native sender. P4 compares **every retained byte** with the known pattern
only after matched completion and reciprocal UART restoration. Report mismatch
count, first offset/actual/expected, FNV and bounded first/last bytes over USB.
Do not infer integrity merely from DMA callbacks or matching fingerprints.
Keep full-HDMI services, native leaf, coordinator, control sequence and installed
EMOS unchanged. No per-byte logging in the transfer, ISR tracing or edge counters.

DI02 [x] — P4 generates a separate deterministic1,024-byte pattern locally before
arming TX; it does not echo RX storage. The MOSlet independently invokes reverse
transfer and compares every byte/guards. Report source integrity at P4 before
transfer and retained integrity after return. Distinguish a bad source from a
reverse-path corruption. This is a compile-selected private diagnostic variant
of the existing endpoint, with prominent source comments, not a public protocol
or production service. No new wire opcodes or raw application GPIO bypass.

DI03 [x] — Build/check the endpoint's lifecycle, expected-vector computation,
bounds, rejection and independent reverse preparation. Compile the adapted
existing MOSlet. Verify exact artifacts before flashing the P4 and deploying the
MOSlet over the ordinary UART listener. Read back deployed executable and original
startup; invoke directly from the CLI, never autoexec. No EMOS reflash or backup.
After P4 installation, permit one explicit Agon recovery reset if needed for the
known boot-admission fault; record that separately from payload correctness.

DI04 [x] — Run each direction once with fresh durable CSV paths. Forward integrity
failure does not prevent the independent reverse experiment; transport cleanup
or readiness failure does. No uncertain replay. Collect passive bounded USB
output without serial-control reset, and compare P4 and Agon evidence. Restore
the exact preceding matched full-HDMI comparison P4 image, verify all segments,
original startup and ready/neutral input, close listener/collector and record
handback. Do not roll back to pre-handshake firmware against current EMOS.

DI05 [ ] — Author authorized a one-hour diagnosis and remedy on 2026-10-11,
06:11:05–07:11:05 UTC. Compare the P4 TX driver/pad sequence and EMOS sampling
against pinned driver contracts and retained forward proof. Obtain bounded
received-byte/wire evidence where needed; change one relevant variable at a
time. Keep full HDMI, EMOS transport ownership and existing matched handover.
Then rerun independent directions and existing roundtrip/boundary checks,
verify startup and ordinary ready input, preserve exact artifacts and findings.
Do not claim production promotion or general fault-recovery qualification.
Stop at the time limit; if unresolved restore the preceding matched pair.

## Research boundary and evidence

Reuse pinned official references in [native payload](NATIVE-PAYLOAD.md), the
[prior snapshot mechanism](DATA-SNAPSHOT-R01.md), and the
[historical/modern results](DEVKIT-CONTROL-R01.md). Official checkouts stay
read-only. Firmware build and physical identities follow the version policy;
local endpoints, serial identity, manifests and evidence live in ignored
`agents/port008-live-qualification/direction-isolation-r01/`.

Pattern is the existing parcheck function:
`uint8_t((i*73)^((i>>3)*29)^(i>>8)^0x69)`.
A1,024-byte block directly matches the historical size, but the sender/protocol
and normalHDMI composition differ; this is direction isolation, not a controlled
performance comparison. No throughput claim, mode implementation, electrical
repair, warm-reset fix or production promotion is in scope.


## Direction-specific results — 2026-10-11

Ranked failing path first. One 1,024-byte transfer in each direction, no replay.
Byte comparisons are exhaustive; fingerprints are supporting observations.

| Observation | Expected | Forward Agon → P4 | Reverse P4 → Agon |
| --- | --- | --- | --- |
| Destination incorrect bytes | 0 | 0, exact P4 comparison | 955, exact Agon comparison |
| First incorrect offset | None | None | 2 (third byte) |
| First incorrect actual / expected | Equal | Not applicable | 0x7b /0xfb |
| Completed native status | 0 | 0 | 0 |
| Destination guards | Intact | Intact | Intact |
| P4 retained-buffer incorrect bytes after return | 0 | 0 | 0 |
| P4 retained-buffer FNV-1a32 | cfb78805 | cfb78805 | cfb78805 |
| P4 locally generated TX source FNV before arming | cfb78805 | Not applicable | cfb78805 |

The reverse source was generated afresh at offer acceptance; forward data was
not reused. Source generation occurs before native arming, and retained checks/
USB publication occur after matched receipt and reciprocal UART restoration.
Both directions report actual completed native status 0; that status demonstrably
does not establish destination integrity. The source comparison is CPU-visible
memory, not proof of the bytes seen by DMA or on the wires.

This1,024-byte forward success is **not** blanket RX qualification: the earlier
3,456-byte snapshot differed, and255-byte roundtrip direction remains unisolated.
Native TX/DMA publication, P4 pad output, electrical behavior and EMOS sampling
remain candidates within the reverse path. The first discrepancy clears bit7,
but this single observed byte does not establish a D7-only failure.
No remedy or additional payload run was attempted after obtaining this result.

### Exact experimental composition and validation

P4 port-008-data-r03-b2026-10-11-05-39-57Z, app SHA256
14d0a3c4b8c4f4f6ffe25680cf6c66f10a742d95cdd9f3867b384ad1bfee915b.
All four flash segments independently verified. Installed matching EMOS remains
agon-emos-v0.1.24-b2026-10-10-01-48-39Z; no EMOS/mainboardVDP flash.
Adapted pariso.bin9,536 bytes SHA256
2cea793f4e750d5c008420f587c2124aaad1bbf22d969556e695620b462066bb,
deployed/readback verified as /emos/pariso.bin.

Against the preceding data-only build, source changes are the private endpoint,
post-receipt console reporting and a previously committed build-wrapper extension
for DevKit selection that does not change the P4-PC branch. Native payload,
coordinator/handshake, SDK/dependency/board settings and HDMI inputs match.
The private build selects constructor Mode::independentDirections; ordinary
maintained source retains default echo selection. Frozen source archive and
selection patch are retained. No public wire opcode, SDK driver or API change.
Endpoint host checks: 25independent-source/corruption/lifecycle cases plus 12
existing echo cases, ASan/UBSan; LeakSanitizer disabled. AgonDev MOSlet compiles.
Compiled P4 excludes PCNT/probe symbols. One 100 ms Agon recovery reset was needed
for admission after P4 installation; known boot-reset limitation is not fixed.

Durable SD results: /agents/extender/results/P8IF01.CSV and P8IR01.CSV.
Passive raw POSIX USB capture kept CLOCAL/CREAD and cleared HUPCL; opening did
not change admission epoch, and collector closed without errors. Host run,
including CLI typing, 8-second allowances per operation, retrieval and 5-second
quiet tail, took 50.928 seconds; **not** native link throughput or exact fixture
runtime. No logic-analyzer acquisition. Build/install/recovery durations remain
separate in local receipts. Original startup was untouched throughout.


### Handback and discussion boundary

DI04 complete: exact preceding P4 port-008-data-r01 restored and all four
segments independently verified. Pi held Agon reset during restoration, released
it after P4 HTTP initialized, and ordinary input admitted without an additional
recovery pulse. Original 38-byte startup and deployed MOSlet readback verified;
foreground listener closed, keyboard ready/neutral with held0/pending0. EMOS and
mainboard VDP unchanged. No active reset hold, capture, transfer or serial collector.
Production selection unchanged. DI05 remains open for Author discussion before
any reverse-path remedy. Results and diagnostic source are available for review;
the contract and prior findings were committed/pushed before execution.


## One-hour continuation contract

DI05-A [ ] — Freeze isolated findings and inspect actual TX clock/pad/DMA and
EMOS byte-read contracts. Distinguish a byte alignment error from sampled bit
corruption before choosing a remedy. Pinned IDF source performs C2M cache sync
inside transmit; adding a redundant flush without evidence is not a remedy.

DI05-B [ ] — Build and bench-test the focused correction. Retain the failing
control, exact source/build hashes, full-byte comparison and any helpful wire
capture. Use CLI invocation, fresh result paths and unchanged startup.

DI05-C [ ] — Rerun both directions, 1/255/4096-byte roundtrips and ordinary
startup/input readiness. Record limits and leave a verified usable pair.
