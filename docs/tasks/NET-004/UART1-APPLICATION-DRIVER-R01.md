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
3. EMOS retains physical admission, ordinary VDU routing, Port C/UART1/parallel
   handover and committed mode. Preserve its existing keyboard/NM receive
   assembly and callback delivery. The application must not silently replace
   an EMOS-owned vector, reinitialize UART1 or bypass its current transport API.
   Negotiate a supported ownership/IRQ arrangement before implementation relies
   on one. The current public NM SUBMIT remains synchronous until integrated.
4. First consumer is MechAgon on the tested UART-NM/guarded-UART0 pair. Preserve
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
  Resolve concrete owner conflicts without creating a duplicate driver here. [ ]

N04-019.03 Have component owners integrate only their own source after the
  supported ownership contract is settled. Preserve the working live renderer;
  test only through separate normal admitted work. [ ]

## Delegated decision register

| ID | State | Owner and required disposition |
|---|---|---|
| U1-D01 | Accepted | Smith: generic driver and async engine in application RAM; UART owns development outside Extender. |
| U1-D02 | Delegated/open | UART with Extender: callable ABI and whether any optional RST entry is useful; no invented number. |
| U1-D03 | Delegated/open | UART with Extender: stock versus EMOS interrupt/admission and RX chaining arrangement; identify any minimal firmware-owner hook. |
| U1-D04 | Delegated/open | UART with MechAgon: initial TX scope, source/drain/error/stop semantics and consumer integration. |

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
