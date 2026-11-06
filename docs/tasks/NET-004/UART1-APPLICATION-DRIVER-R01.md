# Application-owned asynchronous UART1 driver delegation

Smith directs UART to own a reusable application-space driver that gives UART1
the UART0 asynchronous transmission model. Keep its engine and buffers out of
resident EMOS. UART owns its task, source, tests and documentation in its own
generic MOS project; Extender supplies integration requirements and MechAgon
owns consumer changes. This record tracks coordination, not another driver tree.

## Accepted requirements

1. The driver, transfer state, source storage and ISR code live in application
   RAM. Do not add a resident UART1 async engine to Eirene or EMOS. Any minimal
   ownership/interrupt integration dependency must be identified separately,
   with exact source and byte cost, through the firmware owner.
2. Keep the public call shape and completion behavior as close as practicable
   to UART0 async: source pointer, full count, callback, explicit admission and
   source lifetime. Distinguish source release, wire drain and peer execution;
   never infer cancellation from a timeout. Document actual result semantics
   rather than confusing raw upstream IER-derived A with EMOS's guarded A0.
3. For the separate Extender adaptation only, EMOS retains physical admission, ordinary VDU routing, Port C/UART1/parallel
   handover and committed mode. Preserve its existing keyboard/NM receive
   assembly and callback delivery. The application must not silently replace
   an EMOS-owned vector, reinitialize UART1 or bypass its current transport API.
   Negotiate a supported ownership/IRQ arrangement before implementation relies
   on one. The current public NM SUBMIT remains synchronous until integrated.
4. The default driver targets vanilla MOS and Console8 ESP8266 TX/RX-only
   wiring. MechAgon on the tested UART-NM/guarded-UART0 pair is downstream
   Extender integration, not a vanilla driver gate. For that adaptation preserve
   current NM framing and opaque128B records, including up to146B forward wire
   frames. Keep ordinary mainboard UART0 graphics independent. No game schema,
   P4 networking implementation or checksum belongs in the generic driver.
5. Interrupt work must be bounded. Specify FIFO-sized OTIRX bursts, CTS/error
   handling, blocked-CTS wakeup and rearming without indefinite ISR spinning.
   Preserve RX service, registers/IFF/MB, prearmed completion and positive
   retirement before vector/storage restoration. Escape requests stop; it does
   not revoke a source that an ISR still owns. Preserve useful first faults.
6. Provision an explicit callable assembly entry/C adapter and install/restore
   lifecycle. A UART interrupt vector is needed for interrupt-driven service;
   a new CPU reset vector is not. Normal CALL may suffice for the application
   entry. Any optional RST restart entry must be justified against existing MOS
   dispatch and firmware-space cost, not assigned a new number by assumption.
7. UART publishes its task/plan before implementation, then owns development,
   focused checks and native builds in its project. Coordinate MechAgon's needs
   directly and return exact source/API/build requirements to Extender. Existing
   compiler/emulator/human/bench gates persist; no current live bench access,
   firmware replacement, game restart or emulator change is delegated here.

## Coordination actions

N04-019.01 Record Smith's placement/ownership decision and send substantive
  requirements plus an immediate UART chat alert. [x]

  Actual durable delegation `uart1-app-async-driver-author-delegation-one` and
  accepted immediate chat delivery are retained in the ignored owner inventory.
  UART's confirmed owning project is the Author's generic MOS fork. Its actual
  task is now U1-001 in the UART-owned project (task-first commit cc8d090);
  ABI/admission integration remains pending. No implementation or test pass is claimed.

N04-019.02 Record UART's actual owning task/source location and proposed ABI,
  interrupt lifecycle, EMOS dependencies and qualification plan when returned.
  Resolve concrete owner conflicts without creating a duplicate driver here. [x]

N04-019.03 Have component owners integrate only their own source after the
  supported ownership contract is settled. Preserve the working live renderer;
  test only through separate normal admitted work. [ ]

## Delegated decision register

| ID | State | Owner and required disposition |
|---|---|---|
| U1-D01 | Accepted | Smith: generic driver and async engine in application RAM; UART owns development outside Extender. |
| U1-D02 | Delegated/open | UART with Extender: callable ABI and whether any optional RST entry is useful; no invented number. |
| U1-D03 | Author clarified | Vanilla MOS is UART's default. Extender owns its separate EMOS adaptation/needed hooks; these do not gate UART development. |
| U1-D04 | Split scope | UART owns the initial vanilla Console8 ESP8266 test; MechAgon lifetime requirements remain downstream input. Current consumer is unchanged. |

## Source facts supplied to UART

Official read-only MOS documentation `docs/mos/API.md` defines0x14
`mos_setintvector`, and0x15 `mos_uopen` names UART1 interrupt vector1Ah.
These stock contracts do not grant ownership of an already admitted EMOS port.
The current matched EMOS source2c79c600 uses synchronous
`emos_net_gateway -> emos_keyboard_send -> emos_keyboard_transmit_block`, with
per-byte UART1 OUT0 and CTS/FIFO checks. Its UART1 RX ISR owns keyboard and NM
packet reception. UART0 guarded RFC25 uses IRQ-driven FIFO fills with OTIRX.
Exact maintained source/artifact paths remain in the ignored owner handoff;
canonical upstream checkouts remain read-only.

## UART owner return —2026-11-06

UART publishes `docs/tasks/U1-001/README.md` in its generic MOS project,
branch `codex/uart1-app-async`, commit `cc8d090`; source belongs in its
`experiments/uart1-async`. A normal CALL ABI is sufficient; no RST number is
selected. Its bounded application TX core can proceed independently. EMOS
RX/vector/LSR ownership and a supported optional TX dispatch/CTS retry seam
remain source-contract questions; no direct-register or vector takeover is
admitted and no resident engine/build/bench change follows from this return.

UART core checkpoint `45332e1` reports537B core text plus a30B OTIRX leaf
in application space. Host sanitizer/byte-event checks and native link pass;
there is no operational adapter or physical UART result. MechAgon146B wire
lifetime/writer exclusion is incorporated. Owner admission/IRQ/CTS retry/LSR
and positive tail retirement remain the concrete integration boundary, not a
new resident engine or an assumed public hook.

## Vanilla-first clarification and existing ESP8266 facts

Smith's original UART message was read directly: thread
`01a132e0-4787-7310-93e9-f5248ffb2ff8`, turn
`01a1b203-8a13-7640-a3ed-7936bd738a3d`, message
`01a1b203-8a97-7920-9ceb-87fb68c08ef5`. Vanilla MOS/application-owned UART1
is the default; Console8's ESP8266 is the initial test device without CTS/RTS.
Extender owns downstream EMOS adaptation and any needed owner hooks. This
supersedes the original EMOS-first/MechAgon-first integration dependency above;
it does not authorize new C8 access, alter live firmware or remove EMOS ownership
requirements when that separate adaptation is implemented.

Existing source-only facts were returned through
`uart1-vanilla-esp8266-existing-facts-one` with an accepted immediate chat alert:

1. Observed module self-report AT1.3.0.0/SDK2.0.0; no retained exact firmware
   BIN/source/hash or known receive-buffer capacity. No firmware replacement.
2. Accepted small-command host usage:1152008N1, flowcontrol0/eir0, four-wire
   power/GND/TX/RX. A polling setup/BBS pass is not an async bulk qualification.
3. AT/ATE0/GMR and bounded CIPSEND prompt, SEND OK, length-delimited IPD and
   expected BBS reply are distinct witnesses. There is no established arbitrary
   byte echo, replenishing credit, XON/XOFF or unlimited receive window.
4. The accepted diagnostic sends at most8 application bytes per selected BBS
   request, one transaction at a time. Complete logical replies before foreground
   display/card sync; prior polling RX gaps are reproduced in retained host tests.
5. Nominal MOS120counts/s at60Hz,100 at50Hz; raw counts are not milliseconds.
   The separate new startup utility's genuine ping is not yet a physical pass.

No new device query, serial reader, BBS service change or hardware test occurred
for this source-coordination return.

## Vanilla source/artifact return

UART returns source `510ad1ab26ccd8f3b07b1135b690cf087a7443e0`,
evidence `05a2513`, and `U1-001/vanilla-r03.md`. The default application-only
C interface now provides open/submit/read/finish/stop/close/snapshot and an
HL/BC/DE ordinary CALL entry. The host-tested/native-linked vanilla adapter
exists; no eZ80 execution or physical qualification has occurred. Earlier
core-only figures above remain historical and exclude the later adapter.

1. Application object text2542B, internal BSS34B plus caller RX ring. These
   exclude SDK/CRT/callbacks and do not represent resident firmware growth.
2. The generic core/emit are reusable by Extender's future owner adapter. Its
   backend must supply admitted status/emission, bounded RX-first/error service,
   atomic TX/retry effects and positive source/wire retirement. The vanilla
   installer owns stock UART1/vector1Ah and must not replace EMOS's RX owner.
3. Callback releases the source; finish observes local TEMT separately. Neither
   proves ESP8266 receipt. No-flow-control reserve bounds local FIFO only and
   leaves remote protocol pacing external; no remote credit is inferred.
4. Host sanitizer/byte/event/native-link checks are UART evidence. Prepared
   `u1test.bin` is15069B, SHA256
   `42410864fec9e492899d937152a5954a8b301d1e845449b29bdc26515fc34e5d`;
   it compares ordinary/async AT/GMR replies, not bulk throughput or CPU savings.
5. Locally retained `vanilla-prepared-r03.zip` SHA256
   `fd0902426f22ee3b90c21367525c41e7a53d4ac3a3c6c99aaa97b3d20384ff68`
   was independently rehashed on receipt. It is not deployed or a release.

This handoff changes no C8 card files, utility selection, live MechAgon/bench
custody, firmware, service or consumer. Extender's downstream integration remains
N04-019.03, subject to its own source contract and normal qualification.
