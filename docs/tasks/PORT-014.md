# PORT-014 — EMOS UART text rendered by EDP in the browser

Status: active; paced graphical review accepted and SD deployment requested.
Candidate freeze/preparation in progress; physical counting not yet run.
Started: 2026-09-08.

## Scope and roadmap relationship

Author authorized the first visible EMOS-to-EDP text diagnostic, and approved
EMOS v0.7.0, uart-visible-text-probe-r01 and registry r32. This connects the
accepted PORT-013 UART/parser proof to PORT-003's retained renderer and browser
service. It advances Exclusive Compatible without activating that mode or
resuming the held parallel/r02 work. Ordinary console and clock remain on
the onboard VDP; EMOS owns this Legacy-only bounded diagnostic.

## Initial r01 references and contract

1. Official agon-docs at f9806bd3cbff6ed5d1c08bef1d51fed11764b86b,
   docs/vdp/VDU-Commands.md: VDU 12 clears text and homes the cursor;
   VDU 31,x,y uses character coordinates. Ordinary printable bytes draw text.
   docs/vdp/System-Commands.md: VDU 23,0,&CA flushes drawing commands;
   VDU 23,0,&80,n returns 80,01,n and belongs to MOS/VDP coordination.
2. Clean read-only stock MOS v3.0.2 at
   8336409351ee5314e02801a7b72a4f1bb5282519 and VDP v2.16.0 at
   c7ac293d2aa81ddfa693390549bcd909069c8fc3 remain the reference baselines.
   VDP video/vdu_sys.h dispatches flush to waitPlotCompletion and General Poll
   to sendGeneralPoll. The maintained retained parser/serializer must execute
   these commands; no locally synthesized ACK or browser-injected test text.
3. EMOS sends VDU 12; VDU 31,2,2; ASCII EMOS TO EDP: UART TEXT; CR/LF;
   VDU 23,0,&CA; VDU 23,0,&80,&A6 at 1152000/8N1 with RTS/CTS on r03.
   Require exact return 80 01 A6. EMOS prints a bounded diagnostic result and
   returns to MOS. No mode switch appears in this byte stream or fixture;
   the Agon video mode is selected only by autoexec's VDU 22 3.
4. P4 admits the exact complete request before retained parser dispatch,
   rejects malformed/partial/extra traffic and captures the real serializer's
   reply. UART deadlines and cancellation follow the proven bounded probe.
   Browser/network startup uses PORT-003/PORT-006's existing implementation;
   framebuffer contents persist for operator viewing after EMOS returns.
5. Parser ACK and browser-visible text are separate evidence gates. Retain
   exact UART bytes/flow control, browser screenshot and Author confirmation
   of Agon SD/CLOCK PASS and final prompt. Keep the 24MHz/240M acquisition and
   shorter success window; shortened acquisitions require explicit disposition.
   No sustained-load, complete startup or mode-activation claim.

## Work

1. [x] Implement EMOS VDPTEXT and the P4 bounded text composition; verify real
   parser admission, malformed/extra-byte rejection, deadlines and cleanup.
2. [x] Build both drafts; run configured EMOS/linked/runtime/host checks and
   P4 host checks. Launch same-build ordinary/no-peer graphical review from
   .emulator; await Author acceptance before committing emulator-coupled work.
3. [x] Freeze clean candidates after review; preserve working v0.6.0/General
   Poll rollback, prepare guarded SD installation/test media and authorized P4
   deployment with network/browser readiness checks.
4. [ ] Capture the paired exchange and browser text; accept or diagnose the
   bounded result before proposing another increment.
5. [ ] Make successful text transactions repeatable after Agon-only resets;
   qualify r02 with two further successes while P4 and browser stay running.
6. [ ] Build the SD-loaded C clear/banner/decimal 1..10 sample, the bounded
   EMOS gateway and payload-independent P4 text receiver; qualify the sample
   through the gateway and repeat it after Agon-only resets.

EMOS implementation belongs to INTEG-008. Physical wiring remains unchanged.
Current bench coordinates and preparation live only in ignored local records.

## Draft checkpoint — 2026-09-08

1. EMOS agon-emos-v0.7.0-b2026-09-08-19-16-36Z passes the full configured
   qualification, linked UART/parallel checks, runtime checks and 74 host tests.
   Same-build stock/EMOS ordinary and deliberately invalid SD smoke pass.
   The CLI no-peer diagnostic reports no reply from EDP and returns to MOS.
   Graphical review may instead report transmit timeout because the two
   emulator backends expose different unconnected UART1 states; both are
   permitted no-peer outcomes, neither proves a physical UART exchange.
2. P4 uart-visible-text-probe-r01-b2026-09-08-19-11-35Z builds with the
   retained processNext, sendGeneralPoll, send_packet, Canvas drawChar and
   browser/network service linked. Embedded identities match the manifest.
   Transaction admission/return checks pass under ASan/UBSan; all 24 capture
   checker tests pass. The exact sequence has not yet been rendered on P4.
3. Registry r32 validates independently. The full registry/profile validator
   retains the previously recorded held-r02 connectivity-hash mismatch;
   this increment does not repair or qualify that held circuit.
4. The first EMOS draft's shell checker reported a missing HELP marker.
   Re-execution against the same binary produced complete candidate/stock
   transcripts which pass the unchanged strict comparator. The fresh full
   build above also passes. Cause remains unestablished; no check was waived
   or generic builder code changed. Private logs preserve this observation.
5. The new graphical profiles live under the project's ignored .emulator
   directory. The Author's screenshot confirms the same EMOS build, SD/CLOCK
   PASS, expected transmit timeout and final MOS prompt. The Author explicitly
   approved source freeze and clean candidate preparation on 2026-09-08.
   Physical installation, UART capture and browser-visible acceptance remain
   pending.

The Author is separately curating Extended Compatible-mode example programs
in agon-utils/examples/extender, with emulator testing in that repository.
Examples may move into agon-extender as they mature. This diagnostic continues
the current Exclusive Compatible bring-up sequence.

## Installation media prepared — 2026-09-08

Clean candidates from Extender a3ab788 and EMOS 5a9549c use build timestamp
b2026-09-08-19-24-57Z. Build/identity and same-build automated emulator checks
pass. Preparation record
[PORT-014-2026-09-08-19-28-52Z](../../hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-19-28-52Z/README.md)
records the verified, safely unmounted EMOS install SD. Working v0.6.0 and
older rollbacks are preserved on card and backed up off-card. Physical Agon
installation, separate smoke/VDPTEXT media and P4 deployment remain pending.

The Author subsequently reported successful installation. Post-install record
[PORT-014-2026-09-08-19-32-11Z](../../hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-19-32-11Z/README.md)
confirms the consumed candidate payload and prepares the same-build SD/CLOCK
smoke and VDPTEXT media with no flash command. SD is safely unmounted. The
P4 candidate is staged and hash-verified with read-only device identification;
P4 deployment and paired UART/browser acceptance remain pending.

The Author authorized P4 flashing. Deployment record
[PORT-014-2026-09-08-19-34-11Z](../../hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-19-34-11Z/README.md)
confirms independent flash verification, exact candidate identity, correct UART
settings and empty receiver readiness. The served browser index matches its
source and a requested startup frame passes EVF1 validation at 640×480.
Both endpoints are installed; the operator-triggered paired capture, Agon
result and browser-visible message remain pending.

## Repeatability correction — 2026-09-08

The Author reports Agon success and supplies r01 capture with P4 stages and
24MHz/240M acquisition PASS. The browser screenshot shows the exact expected
text. A subsequent Agon-only reset timed out: r01 deliberately retained its
completed transaction and released UART outputs until P4 restart. The Author
rejected this restriction for ordinary text testing and approved
uart-visible-text-probe-r02 and registry r33. EMOS stays v0.7.0.

R02 preserves parser/framebuffer state, emits one PASS per successful cycle,
waits for EMOS RTS to stop before clearing that cycle, and reconnects P4 TX/RTS
only when the next EMOS request starts. Idle waiting no longer expires. Active
deadlines and fail-latched diagnostics remain. ESP-IDF 5.5.5 uart_wait_tx_done
re-enables TX_DONE after the existing cancellation helper disables it; no
driver reinstall or FIFO replay is used. Host tests compile the real hardware
orchestration with fake UART/GPIO and prove two exchanges, a long idle interval,
malformed-input rejection and transmit timeout/release. The retained parser
and electrical repeatability still require physical checks.

Use [the r02 sheet](../../hardware/designs/light2-harness-r03/tests/visible-text-repeatable.md)
for repeatability. R01 source/procedure remains frozen in a3ab788 and its
capture uses the original deployed checker.

First-run record
[PORT-014-2026-09-08-19-36-36Z](../../hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-19-36-36Z/README.md)
preserves the capture: exact 35/3 bytes, valid framing/flow control, full
240M acquisition, 9.444288-second final waveform quiet tail and 9.005480
seconds clean serial after PASS. Author reports Agon success; screenshot
shows the exact browser text. Explicit SD/CLOCK and final prompt confirmation
remain pending. R02 host checks and P4 draft build pass; freeze the clean
candidate before physical repeatability checks. EMOS and its emulator inputs
are unchanged by this P4-only correction.

R02 candidate uart-visible-text-probe-r02-b2026-09-08-19-48-35Z from a18432b
passes the clean build and was deployed with explicit Author authorization.
[PORT-014-2026-09-08-19-50-29Z](../../hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-19-50-29Z/README.md)
records independent flash verification, exact startup identity/UART settings,
empty WAIT and matching HTTP browser asset. The launcher now selects r02;
EMOS/SD remain unchanged. Captured and repeated physical exchanges are pending.

R02 capture
[PORT-014-2026-09-08-19-52-44Z](../../hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-19-52-44Z/README.md)
passes P4 stages and exact-byte/framing/flow review; the Author reports the
browser banner. Acquisition is 119128764/240M samples (4.9636985s), with a
4.391214s final waveform tail; both remain failed checks. Serial stays clean
7.004348s after PASS. Repeated-reset and Agon smoke/prompt confirmations and
exception disposition remain pending.

## SD-loaded sample decision — 2026-09-08

D001 accepted: the Author selected C and approved separating the sample from
EMOS so changes to its banner/count do not require reflashing either processor.
The sample owns its text and decimal conversion; EMOS owns UART configuration,
RTS/CTS, flush/General Poll completion, timeouts and cleanup. This is explicit
qualification traffic; ordinary VDU routing and committed mode stay Legacy.
The separate agent's agon-utils demo tree remains owned by that agent.

The Author approved EMOS v0.1.7 as a deliberate numbering reset, plus
uart-visible-text-probe-r03 and registry r34. All are draft until review.
Historical v0.7.0 and r01/r02 builds/evidence retain their original identities.

Bounded implementation contract: use existing resident gateway API 0x51,
operation 2, namespace `edu`, provider `text-probe`. Accept 1..1024 bytes in
ordinary application RAM; allow printable ASCII, VDU 8..13, VDU 30 and complete
VDU 31,x,y. Reject unsupported/incomplete commands before touching UART. This
qualification-only Core service does not load a module. EMOS appends flush
23,0,CA and General Poll 23,0,80,A7 and requires 80,01,A7. P4 accepts that
bounded grammar independent of a particular banner/count and dispatches only
complete transactions through the retained parser. Neither endpoint synthesizes
a successful parser result. Legacy VDPTEXT keeps its original fixed A6 exchange.

References: EMOS projects/emos/README.md defines the existing 66-byte gateway
and project-owned API 0x51. Official docs/MOS.md gives application RAM
040000..0AFFFF; docs/mos/Executables.md gives the MOS ADL application header.
Official docs/vdp/VDU-Commands.md defines the admitted text controls. Same clean
tagged MOS/VDP references listed above verified again. No stock source changes. Official docs/mos/Star-Commands.md specifies
`RUN . <parameters>` for a default-address application with arguments; the
preview/check review scripts use that syntax.


## SD-sample draft validation — 2026-09-08

EMOS agon-emos-v0.1.7-b2026-09-08-20-34-02Z is 122624 bytes and passes
configured qualification, linked UART/parallel checks, runtime checks and all
74 host tests. The text-engine harness covers 42 success/failure scenarios,
including the historical A6 command, different application text, the full
1024-byte limit, invalid grammar, finite waits and cleanup.

The independently built sample uart-visible-text-probe-r03-b2026-09-08-20-35-00Z
is 10757 bytes. The real emulated eZ80 runs its C decimal conversion, displays
1..10 in the onboard preview, rejects invalid gateway inputs, passes same-build
SD/CLOCK smoke and returns to MOS after the expected no-peer status 15. The
isolated graphical review has been launched for Author acceptance. This
preview does not claim P4 rendering or electrical validation.

P4 draft uart-visible-text-probe-r03-b2026-09-08-20-40-14Z builds successfully
with embedded identities verified. Host transaction/orchestration checks cover
different payloads on successive cycles, maximum length, partial/unsupported/
extra traffic, idle/rearm and TX failure; capture checker tests pass. Artifact
registry validation passes independently of the already recorded held-r02
hardware-profile mismatch. No hardware/SD operation or commit was performed.
Candidate freeze, installation and physical counting/repeatability checks
remain pending Author review.


## Visible pacing — Author correction

The Author confirmed the initial SD preview counted correctly and requested
250 ms between increments. The sample now submits the banner and each number
as separate bounded gateway transactions, with a 250 ms MOS-clock pause after
each completed call before the next line. Formatting delays inside a single
buffer would not make P4 rendering incremental. The P4 generic receiver needs
no source change for this. EMOS suppresses per-call start/success chatter for
the application gateway; the sample reports one final result, and failures
remain visible. Legacy VDPTEXT keeps its original diagnostics.

The r03 draft sheet now defines 11 transactions (136 forward and 33 return
bytes), waits for all 11 before capture success, and requests 24MHz/288M samples
(12 seconds) to include the paced run and five-second quiet tail. The original
single-buffer draft review is recorded above; the paced sample needs a fresh
build and graphical check. Identities remain the approved v0.1.7/r03 drafts.


Paced review checkpoint: EMOS agon-emos-v0.1.7-b2026-09-08-20-46-22Z
(122641 bytes), SD sample uart-visible-text-probe-r03-b2026-09-08-20-47-59Z
(10987 bytes), and P4 uart-visible-text-probe-r03-b2026-09-08-20-48-19Z
build successfully. Configured/linked/runtime EMOS gates and all 74 host tests
pass; P4 transaction/orchestration and 11-cycle capture verdict tests pass.
The paced sample passes the actual emulated gateway's invalid-input/no-peer
checks, count preview and same-build SD/CLOCK smoke. A fresh graphical profile
is ready for Author pacing review. No commit, SD edit or physical operation.


The Author confirmed the paced graphical result and requested deployment to
the mounted SD card. Reviewed implementation is unchanged; v0.1.7/r03 advance
to candidate in registry r34. The required clean-source freeze precedes new
candidate builds, automatic same-build review, then guarded MOS-only install
media. Physical counting and P4 deployment remain separate later steps. No
historical identity or result is relabelled.


## Paced sample candidate — guarded SD installation ready

The accepted source is frozen in EMOS `026ac46` and Extender `18024d8`.
Clean candidate EMOS `agon-emos-v0.1.7-b2026-09-08-20-53-57Z` passes its
configured, linked and runtime gates, ordinary/bad-SD emulator checks, and
same-build sample gateway rejection, decimal preview and bounded no-peer
return. Clean sample `uart-visible-text-probe-r03-b2026-09-08-20-53-57Z`
and P4 receiver `uart-visible-text-probe-r03-b2026-09-08-20-54-40Z` build
successfully. The Author already accepted the paced graphical behavior.

Preparation record `hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-20-57-20Z/`
records the verified, safely unmounted installer SD: 122645-byte EMOS image,
CRC32 `F61FA518`. Autoexec renames EMNEW.BIN to EMDONE.BIN before
`FLASH mos EMDONE.BIN -f`. Working v0.7.0 remains available as EMPREV.BIN;
former v0.6.0 rollback is archived as EMV060.BIN. Verified off-card backups
and older rollback images are retained.

Hardware installation is pending the Author's reset and updater Done report.
The counting-test autoexec will be prepared after the SD returns; P4 remains
r02 pending its separate deployment. No physical board flash/reset or capture
was performed during SD preparation. This record does not claim a hardware
counting pass.


## EMOS v0.1.7 installed; counting-test media prepared

The Author reports good flash. `PORT-014-2026-09-08-21-03-54Z` records matching consumed candidate
payload, absent EMNEW.BIN, preserved rollback hashes and the verified,
safely unmounted SD. Autoexec now selects mode 3, runs same-build EMBOOT,
then independently built VTEXT with the accepted 250 ms pauses. No flash
command remains. Paired SD/CLOCK, counting, browser and prompt checks are
still pending.

P4 `uart-visible-text-probe-r03-b2026-09-08-20-54-40Z` and r03 capture helpers are staged and
hash-verified, including the 11-transaction verdict and 24 MHz / 288M request.
Read-only stable USB identity passed. Installed P4 remains r02 until explicit
flash authorization; no P4 serial open/reset/flash or paired capture occurred.
Evidence: `hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-21-03-54Z/`.


## Counting receiver deployed; paired test ready

The Author authorized P4 flashing. `PORT-014-2026-09-08-21-17-51Z` records the exact candidate
`uart-visible-text-probe-r03-b2026-09-08-20-54-40Z` written and independently verified on P4 v1.3,
with stable USB identity checked, correct UART pins/baud, empty WAIT and
matching browser asset. No browser video client was opened by the agent.

The workstation launcher now selects the r03 11-transaction counting procedure
and 24 MHz / 288M analyzer extent. EMOS v0.1.7 and the already prepared
EMBOOT/VTEXT SD remain unchanged. The Author runs the capture and resets Agon
only at its cue, then observes sample PASS, browser count and MOS return.
Two subsequent Agon-only resets test repeatability after capture finishes.
Paired and repeatability results remain pending; startup is not a counting pass.
Evidence: `hardware/designs/light2-harness-r03/tests/PORT-014-2026-09-08-21-17-51Z/`.
