# PORT-013 — General Poll through the retained EDP handler

Status: active; both candidates installed, paired hardware test pending. Started: 2026-09-08.

## Scope and decisions

The Author authorized one real MOS/VDP General Poll exchange at 1,152,000
baud and approved EMOS v0.6.0, uart-general-poll-probe-r01 and registry r31.
EMOS owns an explicit Legacy-only VDPPOLL diagnostic. Its UART1 uses the
seated r03 harness and RTS/CTS; ordinary console output and clock remain with
the onboard VDP. This is a bounded protocol proof, not mode activation or a
public application transport bypass. Preserve passing v0.5.0/r02 rollback.

## Bounded references and contract

1. Official `agon-docs/docs/vdp/System-Commands.md`, General poll and VDP
   Serial Protocol sections, defines `23,0,0x80,n` and return framing
   `type|0x80,length,payload`; General Poll is MOS/VDP startup traffic, not an
   application API. Use n=0xA5 and require exactly `80 01 A5` in this test.
2. Read-only MOS v3.0.2 commit
   `8336409351ee5314e02801a7b72a4f1bb5282519`, `main.c:wait_ESP32` and
   `src/vdp_protocol.asm:vdp_protocol_GP`, and VDP v2.16.0 commit
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`,
   `video/vdu_sys.h:sendGeneralPoll` and `video/vdu_stream_processor.h:send_packet`,
   supply the implementation contract. AUDIT-004 P006 records the trace.
3. The P4 qualification composition admits only one complete four-byte poll
   into the retained VDUStreamProcessor. The real dispatch, General Poll
   variable/callback handler and packet serializer produce the return. The
   fixture buffers/checks the serializer's result, then sends those exact bytes
   through the UART driver with hardware CTS; it never synthesizes an ACK.
4. The fixture invokes processNext for this single command rather than
   wait_eZ80: the latter's boot-only loop additionally sends mode information
   and has reset-dependent behavior. This diagnostic isolates General Poll;
   startup mode information and full activation remain outside its claim.
   The fixture does not start the browser/network service. Reject malformed,
   partial, duplicate or late traffic, and retain finite deadlines/cleanup.
5. EMOS keeps reply state local to the diagnostic, leaving the onboard VDP's
   UART0 receiver and sysvars intact. It validates all three return bytes,
   detects extra bytes and timeout/error, closes UART1/releases RTS and returns
   to MOS. A stalled MOS clock also has a finite polling escape.
6. The next capture ends after required analyzer acquisition and five clean
   seconds after final P4 PASS, with a longer deadline only for stalled runs.
   Keep 24 MHz, 240M samples, D3 falling trigger/1% pretrigger. Record the actual
   extent and both endpoint observations. Video mode stays in autoexec only.

## Work

1. [x] Implement EMOS VDPPOLL, P4 bounded adapter/retained-parser composition,
   negative tests, build identity and capture checks.
2. [x] Run complete EMOS configured/linked/runtime gates and P4 compilation;
   prepare same-build smoke/no-peer review and launch graphical validation.
3. [x] After Author acceptance, freeze candidates, prepare rollback/SD/capture,
   and deploy under the bench authorization boundary.
4. [ ] Prove exact request/response and prompt return on hardware; retain
   results beside the r03 design. No sustained-load or mode-activation claim.

EMOS implementation belongs to INTEG-007 in agon-emos. Private bench details
remain in HARDWARE.local.md and agents records. Held parallel/r02 tasks stay held.

## Implementation checkpoint

The P4 composition builds with the retained processNext, sendGeneralPoll and
send_packet symbols. Its adapter admits one fixed complete poll; networking
is linked through the existing closure but startup is omitted in this target.
No handler or serializer implementation was copied or replaced. Host tests
exercise adapter malformed/partial/extra request and reply rejection, plus
capture readiness/order/late-failure and completion conditions.

EMOS's parallel source guard needed one narrow exception for the Legacy-only
Core VDPPOLL call. It still rejects any additional Core poll or any poll in
parallel/serial sources; mutation tests cover both that boundary and removal
of the Legacy guard. UART_POLL_BLOCKED is a wait, distinct from empty FIFO;
the new command test covers CTS held then released as well as stuck CTS.

## Draft review checkpoint — 2026-09-08

EMOS `agon-emos-v0.6.0-b2026-09-08-17-43-51Z` passes the complete
configured qualification gate, linked UART-divisor/ABI/VDU/parallel checks,
runtime regression and all 71 host tests. The General Poll harness covers
14 cases including CTS held then released, stuck CTS, wrong/short/extra reply,
clock stall and cleanup. Ordinary and bad-SD smoke pass for stock and EMOS;
the no-peer review fails within its deadline and returns to the prompt.

P4 `uart-general-poll-probe-r01-b2026-09-08-17-41-34Z` builds successfully;
its linked symbols include retained processNext, sendGeneralPoll and send_packet.
The actual admission/return model's sanitized tests pass, as do all 21 UART
capture-checker tests (including three new General Poll/completion tests).
Registry r31 artifact validation passes; the unrelated held-r02 connectivity
hash mismatch remains as previously documented.

Graphical review is ready for Author validation. Neither candidate source is
committed; identities remain draft. No hardware flash/reset, analyzer acquisition
or SD modification occurred. Private bundles and capture preparation live under
the coordinator's ignored agents/general-poll directory.

## Author graphical observation — 2026-09-08

The Author supplied a screenshot of draft
`agon-emos-v0.6.0-b2026-09-08-17-43-51Z` showing SD/CLOCK PASS,
`VDP POLL: 1152000 baud`, `VDP POLL FAIL: transmit timeout`, and the final
MOS prompt. This matches the expected no-peer outcome. The accompanying
`Volume timeout` is MOS's generic FR_TIMEOUT text, not an SD failure.
Explicit source-freeze approval is pending; no physical result is inferred.

## Source freeze authorized — 2026-09-08

After the recorded graphical review, the Author approved proceeding with
source freeze and clean candidate preparation. Promote v0.6.0 and the General
Poll fixture lifecycle metadata to candidate with reviewed implementation
unchanged. Commit before building and retain passing v0.5.0/flow-r02 rollback.
Physical flashing remains subject to the recorded bench authorization boundary.

## Clean candidates and installation media — 2026-09-08

Reviewed sources are frozen at Extender `6ed3232` and EMOS `e5d9921`, with
unchanged builder `cf24304`. Both clean candidate builds carry timestamp
`b2026-09-08-17-50-12Z`. EMOS passes the full configured/linked/runtime gate,
all 71 host tests, stock/EMOS ordinary and bad-SD smoke, and bounded no-peer
General Poll failure with prompt return. The P4 candidate is staged with
matching hashes and verified stable USB identity; it is not yet flashed.

[Installation-media record](../../hardware/designs/light2-harness-r03/tests/PORT-013-2026-09-08-17-55-37Z/README.md)
records verified SD preparation and safe unmount. EMOS is 120901 bytes, CRC32
`642B19C0`; working v0.5.0 remains as EMPREV.BIN, with older images archived
and off-card backups verified. The card runs only the guarded installer.
After the Author observes successful installation and remounts the card,
prepare the frozen smoke/VDPPOLL media for the paired test. P4 flashing still
requires authorization for this candidate. No physical General Poll result
or processor reset/flash is claimed by this preparation.

## P4 identity-cache defect — 2026-09-08

Author reported successful EMOS installation; consumed payload hash matched,
and same-build test media was prepared and safely unmounted in
PORT-013-2026-09-08-18-06-37Z. Author authorized P4 deployment. Flash write
and independent verification passed, but startup rejected the image because
it embedded the earlier draft identity b2026-09-08-17-41-34Z rather than the
manifest's candidate b2026-09-08-17-50-12Z. Retain this informative failure;
the latter P4 bundle is invalid for qualification. EMOS is unaffected.

The generated header contained the correct candidate identity, but the boot
object was not recompiled: its shared bridge includes the header through a
macro. The General Poll boot wrapper now also includes that header literally
for dependency scanning. The bundle builder checks embedded identity in ELF,
application and factory images before publishing a manifest; regression tests
reject stale and prefix-only matches. Verify successive incremental builds
before restaging and completing the already-authorized P4 deployment.

## General Poll deployment ready — 2026-09-08

Corrected P4 build uart-general-poll-probe-r01-b2026-09-08-18-09-42Z from
d29f55d passed successive incremental identity checks, flash verification and
exact candidate/pin/baud/empty-WAIT startup checks. Deployment evidence is
PORT-013-2026-09-08-18-10-29Z beside r03. EMOS v0.6.0 remains the accepted
build b2026-09-08-17-50-12Z; its verified smoke/VDPPOLL SD is safely unmounted.
Both endpoints are installed. Next is operator-triggered paired capture with
powered Agon reset only at the readiness cue. No General Poll PASS is claimed.
