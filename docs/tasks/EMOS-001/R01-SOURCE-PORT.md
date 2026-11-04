# Eirene EMOS isolated source-port checkpoint

## Executive summary

The isolated source branch starts at Eirene RC2 and now contains the existing
EMOS controller/parallel-upload composition. Both source variants now compile and link in the isolated Pi exception.
The UART divisor check passes; remaining linked checks stop on an inherited
RST-symbol naming assumption. No image is installed or qualified.

| Area | Eirene foundation retained | EMOS adaptation |
|---|---|---|
| Native build/startup | Native C/GNU assembly, RAM restart slots, startup and FatFS | Explicit active resident object list; separate ELF and all product link checks |
| UART0 async | RC2 calls42h/43h, borrowed buffer, IRQ/OTIRX leaf | Submission only on mainboard route; route mutation BUSY until explicit finish |
| Ordinary output | Synchronous call semantics | RST10/18 call existing EMOS output dispatch |
| ABI | Upstream API and sysvars | Existing51h and getfunction20h gateway; no61h/RST-hook import |
| Input and replies | Native core keyboard/UART0 ISR | Existing source selection, parser/IRQ preservation, controller gateway, VBlank work |
| Foreground services | Native CLI and FatFS | Existing EMOS utility loader, silent CLI admission and SD transport |
| Parallel ownership | Eirene UART hardware names | Existing Port C lock/parking/boot owner and private upload leaf |

## Inputs and source review

Eirene825eaf77176247f5b5ba2f940ae73fcace34e7e5;
EMOS6ececd56ff80029523464a5027633a7b74e84cf6;
common ancestor8336409351ee5314e02801a7b72a4f1bb5282519.
Official reference MOS remains clean atv3.0.2; VDP remains clean atv2.16.0.
Documentation reference f9806bd3cbff6ed5d1c08bef1d51fed11764b86b.

Three-way source migration preserves native Eirene changes and EMOS deltas.
Reviewed textual conflicts cover key-table end, function table, serial
constants, UART I/O spelling/lifecycle and VDP key/length dispatch. Eirene
already selects the correct SD write driver, so no duplicate fix is added.
The native caller table uses D24; the old source-level assertion follows its
spelling while retaining linked transfer checks. Baud-source validation follows
Eirene src/main.c. All four mandatory EMOS link validators remain enabled.

Imported EMOS leaf assembly is explicitly promoted to maintained native source.
A limited existing lvalue I/O adapter is temporarily retained for EMOS units;
native Eirene core retains numeric I/O calls. This is migration debt to remove,
not a new regeneration layer. No prepared/generated builder tree was edited.

## Remaining limits and next evidence

Pi request f75c7d98ee77 is transferred by Author instruction to Oryx request
ea58b0bf482e, preserving order behind existing work. Native x86 compiler LLVM
revision and runtime-library hash match the Pi tools. All631 prepared input
files are independently hashed after staging, with a fresh native interpreter.
The original chat-alert failures are historical; notification now works. No
lease is inferred from silence, and no compilation starts before FIFO checkout.

The next admitted build compares pristine RC2 and this exact composition,
then runs mandatory linked checks and records ROM/static RAM costs. A build
failure stays in this task branch. UART1 async reuse/CTS batches and automatic
cleanup of caller-contract violations are not claimed by this UART0 cut.
Consumer utilities, firmware, production, startup and physical queue remain
unchanged. No emulator execution or coupled change is made.

## First guarded build and UART owner review

Pristine source-built RC2 is100965B; the complete EMOS candidate is128098B,
leaving2974B ROM. Both link. The initial run stops after the parallel validator
looks for old `_rst_10_handler`, while Eirene names it `rst_10_handler`. Three
lookup names are adapted without removing route/call checks. UARTbaud linked
validation passes before that stop; remaining validators are not yet passed.

The5.084s guarded attempt peaks52.35C, host37.5% across4cores, job98.394% of
onecore, with6.24GiB available at minimum and no throttling. Owned teardown,
fresh native scan and Pi release precede offline analysis. No automatic retry.
A separately prepared request owns any follow-up.

UART owner reports no new RC2 sender erratum/allocation. Its finish restores
the named `_uart0_handler`, and TX/modem IER bits belong exclusively to the
async sender; this candidate keeps EMOS's authoritative named RX handler and
blocks route mutation until finish. Source completion is not wire/VDP completion.
Input-only callbacks remain allowed under the documented callback contract.
UART1 reuse and RST-hook API remain separate. Existing exact-ROM fixtures must
be rebound to any eventual candidate; none has been launched by this task.

Published RC2 is reported100950B/SHA
`a47130d78b70fa1e0e54aa61e4340831036d766a0c59e2738935bd9d04b94a3a`.
Our source-built control differs by15B and is a matched-toolchain comparison
control, not a reproduced published artifact. Reconcile compiler/library/build
inputs before claiming release reproduction; preserve both identities.
