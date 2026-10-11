# PORT-008 — Isolate modern forward and reverse corruption

## Executive summary

The modern 1,024-byte forward path passes exact P4 retained-byte comparison.
Reverse remains defective after the authorized one-hour investigation. The
strongest candidate, a P4 CLOCK input glitch filter, preserves all seven lower
bits across 1,024 bytes but still corrupts bit 7 in 480 bytes. A lane permutation
keeps the fault on physical GPIO46, while a CPU-driven constant high works.
This narrows the investigation without establishing an electrical or silicon
root cause. The exact preceding matched HDMI image and ordinary input are
restored; production remains unchanged. DI05-B/C remain incomplete.

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

DI05-A [x] — Freeze isolated findings and inspect actual TX clock/pad/DMA and
EMOS byte-read contracts. Distinguish a byte alignment error from sampled bit
corruption before choosing a remedy. Pinned IDF source performs C2M cache sync
inside transmit; adding a redundant flush without evidence is not a remedy.

DI05-B [ ] — Build and bench-test the focused correction. Retain the failing
control, exact source/build hashes, full-byte comparison and any helpful wire
capture. Use CLI invocation, fresh result paths and unchanged startup.

DI05-C [ ] — Rerun both directions, 1/255/4096-byte roundtrips and ordinary
startup/input readiness. Record limits and leave a verified usable pair.

### DI05-A — Control trace and first focused candidate

The unchanged falling-edge TX control repeated reverse transmission with full
Agon receive bytes retained. This run had 957 incorrect bytes, first offset 2,
0x7b instead of 0xfb. A 15-second eight-channel digital acquisition at 24 MHz
retained exactly 360 million samples. The active interval contains 1,024 falling
and 1,024 rising CLOCK edges; the observed D7 wire is mostly low with brief
spikes, and the lower-seven-bit sequence skips source bytes at several offsets.
The defect therefore appears on observed P4-side wire signals before EMOS
sampling. This digital trace does not prove voltage margins or exclude glitches
shorter than the 41.67 ns sampling period. Unprobed data bits remain unobserved.

Pinned IDF 5.5.5 transmit already performs C2M cache synchronization. Its
`test_use_external_non_free_running_clock` uses rising-edge TX and a unit clock
divider. The first candidate changes only native TX shift edge to rising, with
EMOS, wiring, RX, handover, source pattern, SDK and full HDMI held constant.
This is a diagnostic comparison, not a claim that the edge change is a fix.
The [Espressif v1.3 TRM](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_technical_reference_manual_en.pdf),
sections 56.5.2–56.5.3, also describes non-free-running slave clock and reset
restrictions; pinned driver source remains the implementation baseline.
The full-byte dump is appended to the fixture CSV after native return, never
logged during the byte loop. Local control evidence is `reverse-remedy-r01`;
the first candidate is retained separately in `reverse-remedy-r02`.


### DI05-B — Bounded remedy experiments; no complete fix

Each row is a separate reverse 1,024-byte run on the unchanged EMOS build and
wiring, using the independently generated P4 pattern. The ranking below is
incorrect-byte count, lowest first. All native statuses were 0 and Agon guards
remained intact. These are correctness results, not throughput measurements.

| Change / local experiment | P4 data build | Incorrect bytes / 1,024 | Lower-seven-bit incorrect bytes | Conclusion |
|---|---|---:|---:|---|
| Fixed CLOCK input glitch filter / r10 | r12 | 480 | 0 | Byte ordering/lower bits now exact in this run; bit7 remains wrong |
| Rising shift edge / r02 | r04 | 883 | 745 | Not a correction |
| Constant CPU-driven GPIO46 high / r06 | r08 | 955 | 892 | Deliberately nonmatching payload; proves pad/wire can hold high |
| Unchanged falling-edge control / r01 | r03 | 957 | 888 | Reproduces reverse fault |
| GPIO and first DMA bytes readback / r03 | r05 | 958 | 888 | Matrix/pad configuration and CPU-visible source look correct |
| CPU output-enable override / r04 | r06 | 958 | 888 | Not a correction |
| Sixteen-bit packing, lane8 drives GPIO46 / r05 | r07 | 958 | 888 | Failure survives a different peripheral data lane |
| Swap lanes0/7, compensate source encoding / r07 | r09 | 958 | 888 | Failure stays on physical GPIO46 rather than logical data7 |
| Explicit GPIO initialization before matrix / r08 | r10 | 958 | 888 | Not a correction |
| Preload GPIO46 output latch high / r09 | r11 | 958 | 888 | Not a correction |

The filtered run has 32 high-bit bytes versus 512 expected. All 480 incorrect
bytes differ only in bit7. The CLOCK filter rejects pulses shorter than two
IO-MUX sampling cycles; this one positive change warrants a controlled repeat,
not adoption as a complete remedy. Earlier digital traces show 1,024 commanded
rising/falling edges, source-byte skips and brief D7 spikes. Their 24 MHz sample
rate cannot exclude shorter glitches or determine voltage/edge margins.
Constant-high behavior and lane swaps narrow the physical-pad/output path;
they do not prove a broken GPIO, bad harness or silicon erratum.

Temporary P4 changes were frozen separately in each exact build/source archive,
then removed from maintained source. Restored native source passes all 209
actual-source host lifecycle/cleanup cases with ASan/UBSan. The only maintained
fixture addition is a complete receive-byte hex dump written after transport
return; deployed separately as paridump.bin, leaving pariso.bin available.
It is not an application-side GPIO or routing bypass.

Exact final candidate: port-008-data-r12-b2026-10-11-06-59-57Z, app SHA256
9d4dc94f0a95af58ec7826cad16d8681f952fa52cb3edc04b3cf57ca539cbeaa.
Every candidate has independently verified flash segments and a 15-second,
24 MHz, 360-million-sample digital capture. Local reverse-remedy-r01 through
reverse-remedy-r10 retain CSV/full receive bytes, USB logs, source/build
manifests, raw capture hashes and installation/recovery receipts. The handback
folder retains a machine-readable consolidated summary. No undocumented retry
or data reconstruction was used to turn these failures into passes.

### Legacy resistor / buffer investigation

Author recalled a PARLIO erratum requiring external bias and the former
74-series buffer. Reviewed the retained official ESP32-P4 Series SoC Errata
v1.3 under agon-extender-legacy/docs/espressif (PDF SHA256
6fc2ce35aecbb692fa4c5f4ce2830a12d85a9fa2fa12bf5fbcb6793d0a76b543),
the revision-v1.3 datasheet, and legacy circuit/decision records at commit
042c2f15b00b2b18971f842200228bdaff05596a. No matching PARLIO/GPIO pull-resistor erratum was identified in this
bounded search. This does not establish that no such issue exists elsewhere.

Legacy design/carrier-breakout-design.md explicitly requires a 10 kΩ CLOCK
pull-down and 10 kΩ READY_N / VALID_N pull-ups. Its SN74HC125N circuit isolates
the two shared UART/data paths and switches forward versus reverse-UART
ownership, with pulled-up default-disabled output enables. Legacy DECISIONS.md
D-006/D-007 explain this bus-ownership purpose; they do not cite a PARLIO
silicon erratum. Do not reinstate that circuit or change bias based solely on
memory. Current documented pulls are already fitted; neither their presence
nor the earlier forward pass qualifies dynamic reverse signal integrity.

### DI05-C — Handback and remaining boundary

No complete correction was found within the authorized hour. Independent
forward/reverse requalification and 1/255/4096-byte roundtrips were not run
against a successful candidate because none existed. DI05-B/C remain open.
The exact preceding full-HDMI port-008-data-r01-b2026-10-10-03-07-07Z was
restored; all four flash segments independently verified. EMOS and mainboard
VDP were unchanged. Original 38-byte startup and deployed diagnostic readback
verified; listener closed, reset hold released, keyboard ready/neutral with
held0/pending0. Card remains in Agon. No ongoing capture, flash or transfer.
Three installed-current records identify the fresh handback receipt. Production
selection unchanged. Subsequent work should isolate filtered CLOCK and GPIO46
behavior, preferably with a controlled alternate pad/physical signal comparison;
no wiring change or further bench experiment is authorized by this suggestion.
