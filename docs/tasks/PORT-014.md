# PORT-014 — EMOS UART text rendered by EDP in the browser

Status: active; Author accepted graphical review and approved source freeze
and clean candidate preparation; physical text/browser qualification pending.
Started: 2026-09-08.

## Scope and roadmap relationship

Author authorized the first visible EMOS-to-EDP text diagnostic, and approved
EMOS v0.7.0, uart-visible-text-probe-r01 and registry r32. This connects the
accepted PORT-013 UART/parser proof to PORT-003's retained renderer and browser
service. It advances Exclusive Compatible without activating that mode or
resuming the held parallel/r02 work. Ordinary console and clock remain on
the onboard VDP; EMOS owns this Legacy-only bounded diagnostic.

## Bounded references and contract

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
