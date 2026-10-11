# PORT-008 — Isolate modern forward and reverse corruption

## Executive summary

The modern DevKit control now passes independent 1,024-byte transfers in both
directions, using the same filtered native transport source and unchanged EMOS.
P4-PC reverse remains defective: filtering preserves all seven lower bits but
leaves bit7 corruption, which survives peripheral lane permutations on physical
GPIO46. P4-PC still fails after probe removal: all512 expected high-bit bytes
lose bit7, while the lower seven bits are exact. Removing probes is therefore
not a remedy. Wiring, pad, silicon and HDMI differences remain unisolated.
The exact preceding matched P4-PC HDMI image is restored, ordinary input ready
and original startup unchanged. Production remains unchanged. P4-PC repair and
real 1/255/4096-byte echo qualification remain incomplete under DI05-B/C.

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
Final filtered-run capture review finds 2,048 CLOCK transitions within the
141,436-sample active interval, while observed D7 is high for only 182 samples
(0.129%). Agon receives no high-bit bytes before offset917. These observations
corroborate that D7 is not holding its expected levels on the observed P4-side
wire, even after lower-bit ordering becomes exact. Retained analysis lives
beside reverse-remedy-r10; this does not establish the electrical cause.
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


## Renewed one-hour continuation — 2026-10-11

Author approved another bounded run at 07:12:01 UTC; deadline 08:12:01 UTC.
Prior turn yielded new wire evidence and restored operation; the objective
remains complete reverse integrity and both-direction/roundtrip verification.
Keep existing DI05-B/C open rather than redefining success around seven bits.

DI05-B1 [ ] — Recheck physical GPIO46 versus peripheral data routing with the
CLOCK filter held constant. Keep wiring a live hypothesis: a P4-side probe and
static-high response do not exclude external loading or a wrong connection.
Compare a compensated output inversion, lane permutation or independent
peripheral waveform only under the existing EMOS-owned parked-bus lease.
Use focused experiments, exact artifacts and exhaustive received-byte checks;
no public diagnostic API, direct Agon GPIO bypass or unrequested rewiring.

DI05-B2 [ ] — If a focused remedy passes, implement the smallest proper owned
resource lifecycle and regression coverage, then repeat independent forward and
reverse and existing 1/255/4096-byte roundtrips. A failed or nonmatching control
is evidence, never a substitute pass. Diagnostics remain outside resident EMOS.

DI05-C1 [ ] — Preserve results, remove rejected experiments, restore verified
ordinary firmware/input and original startup before the deadline. No production
promotion without the existing acceptance/version gates. Repaired historical
forward DevKit results do not establish modern reverse behavior there.

### Renewed run results and Author-directed DevKit B comparison

The Author clarified that the B test must use the original DevKit. Historical
DevKit forward passes do not establish modern reverse integrity. Stop further
P4-PC remedy trials and prepare this comparison before requesting a board swap.
A DevKit USB-only installation may precede the harness swap after the Author
confirms that USB-only topology; keep the Agon/P4-PC untouched during that
flash. Payload execution and Agon reset require subsequent Author confirmation
of the repaired original DevKit harness and Agon/card connectivity. No probe
move is required for the first full-byte comparison. Never infer harness
connectivity from USB alone.

The renewed P4-PC trials kept filtered CLOCK and unchanged EMOS/wiring. All
lower seven bits match across all 1,024 bytes in every trial. Rows are ranked by
incorrect-byte count, worst first; these are integrity counts, not performance.

| P4-PC comparison | Data build / local evidence | Incorrect bytes / 1,024 | Lower-seven-bit errors | Result |
|---|---|---:|---:|---|
| Swap peripheral lanes0/7 with compensating DMA bytes | r13 / reverse-remedy-r11 | 484 | 0 | Failure stays on physical D7 |
| GPIO-owned output enable plus drive setting3 | r15 / reverse-remedy-r13 | 484 | 0 | No correction; pad route/enable unchanged before/after DMA |
| Earlier filtered baseline | r12 / reverse-remedy-r10 | 480 | 0 | Remaining errors only bit7 |
| Invert DMA bit7 and compensate at GPIO output matrix | r14 / reverse-remedy-r12 | 473 | 0 | No correction |

Each new trial retains a separately verified four-segment image, source archive,
USB log, full Agon received bytes, and a 15-second 24 MHz capture. All status
values are0 and guards intact. The three new traces contain2,048 active CLOCK
transitions; observed D7 is high for only162/174/190 samples over approximately
141,000 active samples. The stronger-drive trial reports GPIO input enabled,
output enabled, push-pull, functionGPIO and matrix signal195 both before and
after DMA; its final self-read is high. This does not establish voltage margins,
exclude a wrong/load-bearing connection, or prove a silicon fault. No unrelated
P4 GPIO46 owner was found in the bounded source review.

An additional CPU-waveform control (data-r16) compiled but was **not flashed or
run** after the Author selected DevKit as B. It is unused preparation, not test
evidence. The maintained native payload source is restored after freezing the
DevKit comparison archive; no failed workaround becomes a production fix.

DI05-B3 [x] — Prepare and execute the same independently generated1,024-byte
reverse payload on the original DevKit, with the filtered CLOCK/native adapter,
current EMOS, unchanged Agon MOSlet, and original startup. Use the generated
DevKit GPIO/UART/fence tuple and silicon range, never the P4-PC image or pins.
Keep full received-byte comparison and guards authoritative; transport status0
alone is insufficient. Invoke from the admitted MOS CLI, with fresh evidence
under /agents/extender/results. First verify startup and executable readback.
The first comparison needs no analyzer: the retained P4-PC probes do not observe
DevKit signals. If reverse passes, run independent forward and validate retained
P4 bytes. Stop on failure; preserve ordinary input and report before new remedies.

DevKit lacks the P4-PC HDMI bridge. Its maintained browser presentation and full
USB host are selected instead of P4-PC HDMI/full-low-speed-only USB. Record
these composition differences explicitly: a DevKit pass establishes a working
modern reverse path there, but cannot by itself distinguish P4-PC wiring from
board-specific output or HDMI workload. Do not call it a single-variable test
or claim P4-PC fixed. Exact source, build configuration and hashes remain with
the ignored build/run evidence. The bounded build selector now admits the
DevKit data-check composition only with its data identity, native boot owner
and no diagnostic probe; release identities/unsupported outputs stay rejected.

At the board-swap boundary the preceding matched P4-PC data-r01 was restored;
all four segments independently verified. Original startup/MOSlet readback,
listener exit, admitted neutral keyboard and released reset verified. EMOS and
mainboard VDP unchanged. No P4-PC flash/reset/transfer continues while awaiting
Author confirmation of DevKit connectivity. Production selection unchanged.

DevKit preparation complete: port-008-data-r17-b2026-10-11-07-32-07Z, app SHA256
ca1e8109d5c708d071b8d585114a14479e9dbaa5a34ad7f82dcff901bc877163.
Maintained build validation and all retained artifact hashes pass;16 native-build
selection checks and5 board checks pass. Frozen native/coordinator/endpoint/
console source exactly matches the P4-PC filtered baseline. Temporary native
and console source restored. Image is **not installed or hardware tested**;
DI05-B3 remains open at the Author USB/harness confirmation boundary.

### DI05-B3 result — modern DevKit passes both directions

The Author confirmed that the repaired DevKit harness and USB were connected,
with no analyzer probes. This superseded the proposed USB-only installation
ordering. The host verified the DevKit's stable USB identity, held the Agon in
reset while installing the prepared image, independently verified all four flash
segments, confirmed DevKit HTTP startup, then released the Agon. No EMOS or
mainboard VDP change, firmware backup, startup edit or autoexec test occurred.

The unchanged EMOS admitted Extender keyboard input. Through the ordinary
foreground listener, the host read back the exact original 38-byte startup and
the diagnostic MOSlet before invoking either test from the CLI. The native TX,
coordinator, endpoint and console sources match the frozen P4-PC filtered
baseline; generated pins, board/silicon, browser/no-HDMI, USB composition and
analyzer absence remain explicit differences.

| Independent direction | DevKit, 1,024 bytes | Retained correctness evidence |
|---|---|---|
| DevKit → Agon | PASS; 0 mismatches, status0, guards intact | All1,024 Agon bytes retained in CSV and compared independently on the host |
| Agon → DevKit | PASS; 0 mismatches, status0, guards intact | P4 compares every retained byte; post-return USB report has mismatches0 and FNV cfb78805 |

Fresh Agon records are /agents/extender/results/P8DB01R.CSV and P8DB01F.CSV.
Local evidence devkit-reverse-r01 retains the exact source/build, installation
receipt, boot/USB logs, both CSVs, host comparison and final-verification hashes.
Flash/write verification took17.76hostseconds; the two tests plus CLI invocation
and SD retrieval took35.13hostseconds. These are host wall-clock workflow durations,
not payload throughput measurements. No wire capture was taken or claimed.

The listener was closed; admitted keyboard is neutral, held0/pending0, locale1;
Pi reset is released. Original startup is unchanged and SD stays in the Agon.
All three machine-local installed-current records now identify this DevKit image,
not the disconnected P4-PC. No active collector, transfer, flash or reset hold
remains. DevKit data-r17 is an experimental browser-runtime control, not promoted
production. Its independent endpoint is not an echo test: 1/255/4096-byte real
roundtrips and the P4-PC correction are still unproved.

The next useful P4-PC comparison is the same filtered reverse test with analyzer
leads disconnected, before requesting electrical changes. It requires the
Author's physical board/harness confirmation and a separately verified matching
P4-PC image; no board swap, probe move or further P4-PC experiment occurred here.

### DI05-B4 — Author-approved P4-PC comparison without probes

DI05-B4 [x] — Author confirms P4-PC reattached, analyzer leads removed and bench
available. Install the exact retained filtered data-r12 image from the earlier
P4-PC control, independently verify all segments, and keep EMOS, wiring, fixture,
source pattern and startup unchanged. Hold Agon reset during P4 installation;
release after HTTP startup, verify input and read back startup/fixture through
the ordinary listener. Invoke one fresh1,024-byte reverse test from admitted CLI
and compare every retained byte/guards. No analyzer capture, probe move, electrical
change, autoexec invocation or speculative remedy. If reverse passes, separately
check forward retention. If reverse fails, stop payload work and restore exact
preceding matched data-r01, verify ordinary input/startup and retain the failure.
This comparison tests whether removing the probes changes the filtered P4-PC
result. It does not isolate HDMI, silicon, pad configuration or harness loading
from each other, and cannot replace real echo qualification. Evidence is retained
separately as pc-no-probes-r01; do not overwrite either earlier board control.

### DI05-B4 result — P4-PC still fails without analyzer probes

Author confirmed P4-PC harness/USB reattached with sniffers removed. Correct
stable USB identity and admitted neutral input were observed before installation.
The host installed the exact earlier filtered control, data-r12-b2026-10-11-06-59-57Z
(appSHA9d4dc94f0a95af58ec7826cad16d8681f952fa52cb3edc04b3cf57ca539cbeaa),
independently verified all four segments, and recovered admitted input with Agon
held in reset only across installation. Original startup and diagnostic executable
were read back unchanged before one CLI reverse invocation.

| Reverse control, worst incorrect-byte count first | Incorrect bytes /1,024 | Lower-seven-bit errors | Received high-bit bytes |
|---|---:|---:|---:|
| P4-PC, filtered data-r12, no probes | 512 | 0 | 0 |
| P4-PC, same filtered data-r12, probes attached | 480 | 0 | 32 |
| DevKit, matched filtered transport source, no probes | 0 | 0 | 512 |

Every expected high bit is missing in the new P4-PC result. All low-seven-bit
values and byte positions match; first mismatch is offset2,0x7b instead of0xfb.
Agon status0/guards intact do not negate the corruption. P4's independent source
remains exact before/after transfer, FNVcfb78805. Fresh full receive bytes are
retained in /agents/extender/results/P8NP01R.CSV and local pc-no-probes-r01.
No forward or roundtrip was invoked after this failure; no wire capture exists.

Probe removal is not a fix and analyzer attachment is not required for the defect
to manifest. This result does not prove whether probes influenced the occasional
high samples in earlier runs; there is no no-probe waveform capture. It also does
not distinguish board/harness loading, physical GPIO46 behavior or HDMI activity.
The DevKit pass rules out a universal failure of the shared filtered transport
plus EMOS, but does not qualify every composition of that code.

Stopped payload testing and restored exact matched full-HDMI data-r01; all four
segments independently verified. Original startup and diagnostic executable
readback verified, listener closed, keyboardready/neutral locale1held0pending0,
reset released, card in Agon. EMOS/mainboard VDP unchanged; no wiring change or
backup. All three installed-current records identify this fresh P4-PC restoration.
Evidence retains installation/restoration receipts, P4 source report, full CSV,
host comparison, final state and file hashes. No active collector/flash/transfer
or reset hold remains; no promotion or completed repair is claimed.
