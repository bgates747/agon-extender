# PORT-008 — Repeat the proved DevKit receiver on P4-PC

## Executive summary

The repaired P4-PC now passes all 22 historical forward 1 KiB records, including
zero-NOP speed. Byte count, full pattern, sequence and CRC all match. Fastest
median receiver elapsed time is 1,194 µs, essentially identical to DevKit's
1,193 µs. This is about 0.82 MiB/s per-record payload rate, not sustained file
transfer throughput. CLI launch leaves autoexec untouched. Normal recovery must
use compatible pre-handshake P4-PC r11 while September30 EMOS remains installed;
selecting the newer data-r02 recovery image caused a separate admission failure.

The reverse pinwalk identifies all eight monitored patterns and all eleven pad
readbacks pass, but D7 has brief extra transitions near rising edges. That
remains an electrical observation despite successful payload validation. Full
modern ExExt, reverse payload and electrical margins remain unqualified.
Capture completion and final normal recovery are recorded below.

DC01 [x] — Extract legacy commit `4626fcc41a0da5811a4374175fe803957ec5ab4f`;
verify original receiver/canary/sender hashes against the retained run manifest.
Change P4 receiver READY/VALID/data GPIO constants only, and mechanically prove
reversing that mapping yields the original source exactly. Build the standalone
USB-command receiver with original CMake/defaults; freeze compiler/config/image
identities. It contains no HDMI, networking, Extender keyboard or modern EMOS
handshake. Preserve current full-HDMI snapshot image for exact restoration.

DC02 [x] — Historical sender ownership exception approved; staging/readback complete.
The old eZ80 sender controls GPIO directly, conflicting with the current
EMOS-ownership rule. Author approved this one historical sender exception; do not substitute a covert
application bypass or claim the current native gateway can talk to the old
USB-only receiver. If approved, retain the exact original sender assembly and
canary, adapting only unattended launch/menu and mode selection outside the
fixture. Record that this is an isolated historical experiment, not a supported
Extender API. Stage/read back fixture and temporary startup through the current
listener before removing input support. Restore exact original startup afterward.

DC03 [x] — Verify identified P4 and original receiver build, flash/read back
its complete partition composition. Execute the original bounded 22-record
sweep (seven delay profiles, three repeats plus the analyzer record) only if
DC02 is resolved. Retain P4 whole-record pattern/sequence/CRC results and a
complete capture using the existing current probe map. Stop on failure without
uncertain replay. A forward-only success says nothing about reverse parallel.

DC04 [x] — Restore/read back the exact current full-HDMI P4 image, original
startup and input readiness; retrieve Agon evidence, leave listener stopped.
Report DevKit versus P4-PC results and changed variables. No EMOS ROM/mainboard
VDP change, wiring modification, new diagnostics or production promotion.

## Reuse and limits

[Original evidence and pinned research](FORWARD-PROTOTYPE-REUSE.md) identify
`src/prx_receiver.c` and `common/p4_canary.*` from the retained PRX-06 run.
Receiver SHA256 before remapping is
`0e0f76c0b252ebba0f61ebd74390ec086e95a163b1ba32c4c57e294a1a0969c5`.
Current board mapping comes from `vdp/build/boards/p4-pc.json`. GPIO contracts
were checked in the official read-only `agon-docs/docs/GPIO.md`; no new API.
The [snapshot run](DATA-SNAPSHOT-R01.md) and Author-reported harness difference
remain independent evidence. This experiment changes hardware/harness, pin map,
firmware composition and build environment relative to the historic DevKit run;
it cannot alone identify which difference causes a failure.

## Prepared result

Receiver build `prx06-p4pc-control-r01-b2026-10-10-04-38-26Z` compiles and
passes configuration, image integrity and pin-only source checks. Application
231872 bytes, SHA256
`2911baa324857b0eb9a483213d127a3532b2701c5893ed53c5545f03339e1cbe`.
Original USB console, less-than-v3 silicon selection and16MiB flash configuration
are retained. Native IDF build took71.56 host seconds. Original CMake/defaults
and canary remain byte-identical. Native compiler/config/segment identities are
retained separately; the original PlatformIO build environment was not reproduced
byte-for-byte. This is a source-faithful remap, not the original flash image.

Agon launcher compiled with unchanged original sender assembly and sweep function.
It removes interactive confirmation and in-program mode switching, and restores/
readback-verifies original startup before any original GPIO function runs.
This executable is prepared only; its direct GPIO execution is now authorized for this one historical
comparison. Fixture and temporary startup deployed/read back through the current UART listener; standalone receiver installation is next.

Ignored local preparation: `agents/port008-live-qualification/devkit-control-r01`,
including exact extracted sources, pin-only patch, manifest/hash verification,
compiler/SDK records, receiver and sender binaries. Exact current snapshot firmware is retained for restoration. No other source repair attempted.

Author explicitly approved the historical sender exception in chat. It applies
only to this bounded reproduction and does not change the normative product
architecture or create a supported bypass. No resident EMOS modification.

## Execution checkpoint — paused for card return

The standalone receiver was flashed and all three segments read back correctly.
No USB arm command or parallel payload was issued. The unattended launcher
returned15 before GPIO access: its startup readback used text mode, which converts
CR/LF and invalidates a byte-exact comparison. MOS displays15 as “Volume timeout”;
that message alone did not establish a card fault. The launcher is rebuilt with
binary file access; original sender assembly/sweep and P4 receiver are unchanged.
The corrected launcher is not yet deployed.

Exact full-HDMI rollback was subsequently flashed and all four segments verified.
Input readiness is not yet recovered. The agent reset Agon while the earlier
card-reseat request remained pending; Author had removed the card. This was an
agent sequencing error, not transport evidence. No further bench operation is
permitted until Author returns the card and resumes this comparison.

Author mounted the card on Lenovo and requested startup syntax inspection.
Read-only inspection confirms the original38-byte startup exactly, SHA256
`7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`:
`SET KEYBOARD 1`, then `EMOS KEYINPUT extender`. Both are implemented commands;
there is no BOM, stray text or remaining test launch. The earlier temporary
`VDU 22 3`, `LOAD /extender/install/prx06pc.bin`, `RUN` also use implemented MOS
commands. No nonexistent command was found. The separately reported syntax
error is not reproduced or explained by the current file. Card contents were
left unchanged. Original superseded launcher remains in the install directory;
normal startup does not execute it. DC03/DC04 remain incomplete; no historical
transfer verdict or performance claim is available.

## Author photo — startup error identified

The subsequent mainboard photo shows `KEYINPUT FAIL: receiver readiness timeout`,
`Keyboard input: mainboard`, `Error executing autoexec.txt at line 2`, then
`Volume timeout`. This resolves the reported “syntax error”: EMOS recognizes the
second startup command but cannot admit the P4 keyboard service. No nonexistent
command or startup syntax defect is shown. `Volume timeout` here is the generic
MOS text for FR_TIMEOUT returned by EMOS KEYINPUT, distinct from the launcher's
earlier explicit return15. It does not itself demonstrate an SD-volume failure.
P4 input recovery remains pending; no reset, flash or card write was performed
in response to the photo.

## Corrected Author report — post-flash keyboard regression

Author clarifies that keyboard input worked BEFORE the agent's firmware flash,
not afterward. The post-flash photo shows EMOS KEYINPUT receiver-readiness timeout
and fallback to mainboard input. Treat this as an unresolved post-flash/restoration
regression. The agent's claim that current keyboard operation was confirmed or
that the failure was transient was a misreading and is withdrawn. Exact full-HDMI
flash readback passed, but successful input restoration has NOT been established.
No additional bench operation follows from this correction.

## Completed historical comparison and verified restoration

Original PRX-06 receiver with GPIO-only P4-PC remap failed its first1024-byte
record at the slowest24-NOP profile. First byte41, lastF4 (expected74), stored
CRC F3F4/calculatedBA67 instead of6474. Remaining21records were not armed.
Original sender assembly/sweep unchanged; only unattended launch adapted.
Analyzer acquisition passed:45seconds at24MHz,1,080,000,000samples; exactly1024
qualified falling clocks with READYlow, zero mismatches on observed source
D2/D4/D5/D6/D7. D0/D1/D3 were not observed; probes are on Agon header, not P4.
Full hash-verified logic.sr and USB verdict retained in ignored local evidence.
Failure without modern coordinator or full EDP means those are not its sole
necessary cause. Harness, hardware, SDK/toolchain and receiver memory/cache/DMA
attribution remain unresolved. No usable throughput or reverse-transfer claim.

After Author confirmed card in Agon, keyboard admission and actual remote-command
checks recovered. Final exact full-HDMI snapshot restored/all four segments
verified; P4 HTTP availability awaited before final Agon recovery reset.
Original38-byte startup independently read back,52remote packets accepted,
input ready/neutral, held0/pending0, listener exited. No active bench operation.
EMOS/mainboardVDP/wiring unchanged. No repair or production change. Earlier
unverified-restoration and current-keyboard-status statements above are history.
Evidence: agents/port008-live-qualification/devkit-control-r01/handback.json,
run-result.json, analyzer-summary.json, installation and restoration receipts.

## Authorized repaired P4-PC repeat — 2026-10-11

PC01 [x] — Author confirms P4-PC connected with 220 Ω series resistors on
all eleven signals. Reuse retained 40 MHz historical pins-only receiver and
unchanged 22-record sender from the passing repaired DevKit sweep. Verify/stage
through existing admitted keyboard and foreground listener. No EMOS/mainboard
VDP change, new diagnostics, firmware backup or production promotion.

PC02 [ ] — Author explicitly directs transfers without analyzer; probes remain
on DevKit. Before each USB arm, require sampled receiver status to observe both
CLOCK levels while READY/VALID remain high. This is a readiness indication, not
a waveform capture. Stop at first missing/failed verdict; no retry. Retain byte
count/pattern/sequence/CRC verdicts and receiver elapsed µs for up to 22 records.
Observe five clean USB seconds. Full sweep provides no SD completion result.

PC03 [ ] — Hold powered Agon reset while restoring exact retained full HDMI
P4-PC image; independently verify all four flash segments. Release only after
P4 HTTP initializes; verify original startup and unchanged sender through the
listener, close listener and verify neutral admitted keyboard. Keep uncertainty
about electrical margins and reverse/modern transfers explicit.

### Repaired P4-PC repeat: sender admission not established

The host independently installed/readback-verified the retained 40 MHz receiver
and staged/read back the unchanged 11,284-byte sender and 51-byte startup.
Receiver USB status never established waiting CLOCK activity: READY=1,
VALID=0, CLOCK=0 throughout the bounded sampling window. The host issued no
arm commands; zero payload records were received or validated. The Author
reports “admission or completion timeout,” autoexec line 3 failure and “error
accessing SD card.” The sender's admission timeout establishes fixture execution;
its normal startup restoration/readback precedes GPIO access. The generic MOS
error after RUN is not independent evidence of an SD hardware fault.

This result is **not payload corruption**, a DMA failure, or a failed speed
profile: no receiver transfer was admitted. Without analyzer evidence the
control-path discrepancy remains unresolved. Next physical diagnostic is the
existing mapped probes on the P4-PC harness; do not replay the sweep blindly.


## CLI-only launch correction — 2026-10-11

CL01 [x] — Remove the sender's autoexec write/readback, preserving historical
sweep/canary/byte kernels. Extend only bounded admission polling 16-fold to
allow receiver installation after CLI RUN. Loop budget is not calibrated wall
time; no infinite wait or automatic retry. Compile and mechanically compare
unchanged kernels/canary before deployment. Preserve historical binaries.

CL02 [x] — With normal P4-PC services and admitted EMOS input, deploy/read back
new fixture under /extender/install. Keep /autoexec.txt byte-for-byte unchanged.
Select mode at existing CLI before fixture preparation if necessary; fixture
must not change it. Issue LOAD then RUN through admitted CLI. Only after RUN
is delivered may host install/verify retained historical receiver. Require
sender waiting activity before arming; now Author is moving analyzer probes.
Do not run until Author confirms probes and returns SD to Agon after card work.

CL03 [x] — Retain bounded first-failure sweep/receiver verdicts. Recover by
holding Agon reset through exact normal P4 restore/verification, then release.
No startup restoration required by this fixture. Verify ordinary CLI/input and
SD access. If Pi reset does not visibly restart Agon, resolve reset wiring;
do not compensate with repeated flashes or autoexec changes.

The preceding no-analyzer repeat never armed a transfer. Normal P4-PC image
restored/all four segments verified, but subsequent keyboard admission timed
out. Author still saw timeout screen; Pi-to-Agon reset reach is not verified.
Original startup readback after recovery remains unverified. No active reset
hold/collector remains. Author is now moving probes and will bring SD to Oryx;
no flash, reset or SD deployment authorized while that physical work proceeds.

### CLI sender deployment checkpoint

Author mounted card on development host and confirms analyzer probes now on
the P4-PC side of the series resistors. Deployed /extender/install/prxcli.bin
(9,261 bytes), independently read back/hash verified and flushed writes.
Original 38-byte autoexec is intact and unchanged. No card dismount, fixture
invocation, flash or reset. Await card returned to Agon before CLI admission
and subsequent receiver installation/capture. CL02 remains incomplete until
that sequence executes; probe location differs from previous Agon-side traces.

## Reverse P4-PC pinwalk before transfer — Author directed

RP01 [x] — Adapt existing reverse helper only for P4-PC's eleven mapped pins.
Author confirms probes P4-PC side after resistors. Keyboard admission is not a
prerequisite: Pi holds powered Agon reset before USB ROM drives one mapped pin
at a time. Capture unchanged eight channels, 100 kHz, 60 seconds; verify P4
readbacks, count/attribute pulses, release/read back every output, restart normal
P4 while Agon held, then release Agon and check keyboard admission. No flash,
SD changes, arbitrary pin search or retry. Preserve known initial ready=false.
Transfer remains subsequent and requires recovered admitted CLI.

### Reverse P4-PC result

Full 60-second capture passes at 100 kHz (6 million samples); raw and archive
hash verified. All eleven P4 low/high readbacks pass. All eight monitored paths
show their expected deliberate pulse counts: D7=8, READY=9, D5=6, D2=3,
VALID=11, D4=5, CLOCK=10, D6=7. CLOCK also has its expected enable/release
pair. **D7 has 27 additional short low pulses clustered near rising edges**;
retain this as an unresolved electrical anomaly, not a clean signal-integrity
pass. Measurements are digital at 100 kHz, not analog voltage/rise-time data.
D0/D1/D3 are unprobed. Probes are after the P4-PC series resistors.

All eleven P4 outputs independently released before normal firmware restart,
Pi reset hold released afterward. No flash or SD modification. P4 normal HTTP
returns, but keyboard admission remains false after bounded wait. No active
reset hold, ROM serial session or capture remains. Need actual Agon restart/
input recovery before subsequent CLI transfer; transfer not yet invoked.

### Recovery pairing correction

The prior “normal” recovery selected port-008-data-r02, a P4 build with
mandatory reciprocal boot release, while the Agon still runs the September30
pre-migration EMOS. This was an agent selection error: flash verification did
not establish a compatible pair. Static branding, live HTTP/telemetry and
ready=false are consistent with the P4 transport worker waiting at its boot
gate; they do not establish a whole-P4 hang or failed Pi reset actuator.
Two additional requested remote-reset checks did not establish fresh admitted
input. The browser actuator and maintained helper use the same GPIO/pulse.

Selected compatible recovery: retained rgb-001-r11-b2026-10-08-01-22-20Z,
P4-PC full HDMI with prior input/service evidence and no mandatory parallel
boot candidate. All artifact hashes checked before installation. Recovery is
in progress; do not claim admitted input until a fresh receipt passes. This
corrects restoration only, not the unresolved D7 anomaly or transfer result.

Compatible r11 recovery passed: all four segments verified, fresh Agon input
connection epoch, neutral admitted keyboard, all 52 command packets accepted,
original startup and CLI sender read back through listener, listener closed.
A subsequent ordinary 100 ms remote reset independently passed the helper's
fresh-epoch/admitted-input verification. No physical reset was required.
This establishes the preceding recovery failure was caused by selecting an
incompatible P4 composition; it does not diagnose the parallel electrical issue.
CLI sweep recovery now pins this compatible r11 image, not data-r02.

### First CLI invocation: no sender activity; no payload arm

Compatible normal r11 permits ordinary remote reset with fresh admitted epoch.
CLI LOAD/RUN packets delivered, then historical receiver installed/verified.
Capture at P4-PC pins never showed sender CLOCK activity; zero USB arms/records.
Author reports invalid-command message on mainboard and absent P4 picture.
The historical receiver intentionally has no HDMI/network/input; its USB startup
and independent verification passed, so absent HDMI is not itself a P4 crash.
No claim is made that MOS accepted LOAD/RUN merely because packets delivered.
Before another receiver flash, independently establish sender execution from
observed waiting CLOCK, and retain/resolve exact MOS command/error text.
Restore compatible r11 normal image; do not reuse data-r02 for recovery.

## Repaired P4-PC CLI sweep result

Second CLI attempt separated LOAD/RUN and required analyzer-observed waiting
CLOCK before receiver installation. Sender execution was established before
removing normal P4 services; all 22 receiver records passed. The earlier
invalid-command/no-CLOCK attempt is not evidence of a parallel payload fault;
command overlap is a plausible cause, not proven. Neither attempt changed
startup. Host now explicitly gates flash on actual sender activity.

Rows ranked slowest first. Elapsed times are receiver medians for three 1 KiB
records per profile, including admission/logging overhead. Percentage is
`(P4-PC median / DevKit median - 1) × 100`; positive means P4-PC took longer.
The CLI variant extends admission waiting only; admitted byte kernels,
completion wait, canary and full sweep were mechanically unchanged. These are
per-record timings, not sustained application/file-transfer throughput.

| Delay NOPs | DevKit median µs | P4-PC median µs | P4-PC range µs | P4-PC time difference | P4-PC MiB/s |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | 5,191 | 5,191 | 5,190–5,196 | 0.00% | 0.188 |
| 16 | 3,857 | 3,859 | 3,858–3,859 | +0.05% | 0.253 |
| 10 | 2,858 | 2,858 | 2,857–2,859 | 0.00% | 0.342 |
| 6 | 2,192 | 2,192 | 2,191–2,193 | 0.00% | 0.446 |
| 3 | 1,693 | 1,692 | 1,692–1,694 | −0.06% | 0.577 |
| 1 | 1,360 | 1,361 | 1,361–1,361 | +0.07% | 0.718 |
| 0 | 1,193 | 1,194 | 1,193–1,194 | +0.08% | 0.818 |

Final extra zero-NOP record passed at 1,193 µs. Total validated payload22 KiB;
all CRCs6474, sequence1. No retry after any payload failure: there were none.
Both boards use retained source-faithful 40 MHz historical receivers with
board-specific GPIO mappings. P4-PC probes are after series resistors;
DevKit reference probes were before them. One run per board, three repeats per
profile, microsecond clocks without independent calibration: tiny percentage
differences are not a material performance distinction.


Final recovery passed: five capture seconds READY/VALID high and CLOCK low;
compatible r11 normal P4-PC restored, all four segments independently verified.
Pi held Agon reset across restoration and released after P4 HTTP initialization.
A fresh admitted connection followed; original 38-byte startup and CLI sender
were read back through the foreground listener, then listener closed. Final
keyboard ready/neutral, held/pending zero, all52command packets accepted.
No active reset hold, capture, collector, listener or automated input remains.
EMOS/mainboard VDP unchanged; no production promotion or new firmware backup.
Complete passing capture/verified archive/raw/USB verdicts and receipts retained
in the ignored pc-cli-r02 silo. Recovery receipt's analyzer_capture=false refers
to recovery itself; the sweep has its own complete acquisition receipt.

## Modern paired transfer repeat — Author approved 2026-10-11

MP01 [ ] — Install retained matching EMOS v0.1.24 build from 2026-10-10
01:48:39Z and full-HDMI port-008-data-r01 from 03:07:07Z on repaired P4-PC.
Reuse the data-only comparison composition: no PCNT, phase tracing or received
snapshot logging. EMOS owns native GPIO access through the existing private
qualification gateway; this is not a new supported public interface. Verify
P4 flash segments and complete EMOS ROM. Temporary startup may save the installed
ROM and enter the ordinary listener solely for verification; restore the original
38-byte startup before payload tests. Do not run a parallel fixture at boot.
No prior-firmware backup, mainboard VDP change or production promotion.

MP02 [ ] — Invoke the existing parcheck MOSlet from the admitted CLI, using a
fresh result path. It alternates forward and reverse at 1,255,4096 bytes,
compares every returned byte and guards, and stops at first failure. Host may
advance to the next size only through the existing fixture's passing result.
Do not replay an uncertain block or relax integrity/completion criteria.
Retrieve the durable CSV independently; keep receiver/render/output timings
separate and make no sustained-throughput claim from this fixture.

MP03 [ ] — Restore original startup, establish admitted neutral input and closed
listener, record exact installed identities, results and remaining boundaries.
If paired boot stalls, permit one explicit recovery reset before any payload;
record it as the known unresolved warm-reset limitation, not a clean boot pass.
Do not restore pre-migration EMOS against mandatory-handshake EDP. If payload
fails, stop further data operations and preserve evidence for discussion.
Local fresh evidence is in ignored pc-modern-r01; earlier campaigns remain frozen.

### Modern paired result — integrity failure remains

MP01 [x] — Exact retained pair installed: full-HDMI data-only P4
port-008-data-r01-b2026-10-10-03-07-07Z, app SHA256
c6ee15085de8dd9a2a81c9ab5e28d82971a4b6c9bb4339cc74d0377a7981144c;
EMOS agon-emos-v0.1.24-b2026-10-10-01-48-39Z, image131017bytes SHA256
55aafe657987754bd6dcda0d2747d145702da9d995e90d9409e8509ccd41c343.
All four P4 segments independently verified; full131072byte installed EMOS ROM
matches image padded with ff, ROM SHA256
69d7b11ac1fa6fcd48cc3770356c3b8806d8f308c345bd670075a7eb21b613dd.
Initial paired boot admission did not complete; one separately recorded100ms
Agon recovery reset restored listener/admission. This is not a clean boot pass.
Original38byte startup restored/readback verified before payload invocation.

MP02 [x] — One CLI invocation of unchanged9,420byte parcheck MOSlet completed
its failure-stopping protocol. Result /agents/extender/results/P8M01.CSV retrieved.
Worst outcome first; statuses are completion reports, not integrity proof.

| Length bytes | Agon → P4 status | P4 → Agon status | Exact roundtrip | Guards |
| ---: | ---: | ---: | --- | --- |
| 255 | 0 | 0 | Fail, first mismatch at zero-based offset2 | Pass both legs |
| 4096 | Not attempted | Not attempted | Stopped after mismatch | Not measured |
| 1 | 0 | 0 | Pass | Pass both legs |

The repaired harness reproduces the same offset2 failure as the preceding
[data-only comparison](DATA-ONLY-CONTROL-R01.md). Historical forward1024byte
success does not qualify the modern RX implementation or either reverse TX/RX
path. This comparison does not establish which leg first corrupts data, nor
prove DMA rather than electrical causation. No retries, relaxed checks, analyzer
capture, timing instrumentation or throughput claim. The next discriminator is
modern forward retained-byte integrity versus reverse integrity, preferably
using the existing bounded retained-data inspection mechanism; not executed here.

MP03 [x] — Original startup readback verified after fixture, foreground listener
closed, ready/physical-neutral input with held0/pending0. Modern matched pair
remains installed; mainboard VDP and production unchanged. Existing warm-reset
fault remains unresolved. No active transfer, collector, reset or flash.
Ignored pc-modern-r01 retains installation identities, segment/ROM verification,
CSV, exact helpers and handback. Earlier historical/harness evidence is unchanged.

Author approved [modern direction isolation](DIRECTION-ISOLATION-R01.md):
forward1024byte retained comparison and independently generated reverse1024byte
comparison, followed by exact full-HDMI paired recovery and discussion before
any transport remedy. Execution follows the committed/pushed contract.
