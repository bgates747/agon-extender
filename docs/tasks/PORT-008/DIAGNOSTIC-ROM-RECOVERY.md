# PORT-008 — Diagnostic ROM recovery

State: recovery and ordinary hardware qualification complete, 2026-10-09.
The initial off-bench contract was frozen before implementation while the bench
was occupied. The Author subsequently released the bench; the bounded hardware
contract and results below record that separately authorized follow-up.

DR01 [x] — Extract the resident UARTTEST and VDPPOLL sequences into SD-backed
MOSlets, preserving `EMOS UARTTEST` and `EMOS VDPPOLL` through the existing
`/emos/<name>.bin` loader. Reuse UARTFLOW's admitted diagnostic transport and
stock MOSlet ABI. Retain resident text services, their waits and all transport,
mode, caller and pin-ownership checks. Do not count earlier UARTFLOW savings.

DR02 [x] — Add only a fixed 115200/8N1/no-flow open operation to the existing
`ext.uartdiag` v1 development service for UARTTEST. Existing operations 0–4
remain unchanged. EMOS, not the MOSlet, opens/closes UART1 and owns RTS; a slow
lease cannot manipulate RTS. Keep the original request/reply bytes, deadlines,
quiet interval and stopped-clock fuse. Both utilities reject extra arguments.

DR03 [x] — Reuse the existing diagnostic failure/cleanup scenarios; exercise
the actual utility algorithms and resident service together. Check UARTFLOW
regression, text-service retention, old-firmware refusal, utility envelopes,
and complete-image eZ80 service/admission/parallel instruction checks.

DR04 [x] — Build both MOSlets at B0000 and compile complete ordinary/private
native EMOS through the unchanged root wrappers and mandatory link guards.
Reuse AUDIT-008/account.py for before/after ROM and RAM accounting; preserve
exact source/build/artifact hashes. Recover enough for the combined private
image and report remaining room without promising the later coordinator fits.

DR05 [x] — Update current build/utility guidance and both component task records;
record measured results and remaining deployment/physical qualification gates.
Do not deploy, flash, reset, use device networking, access the Lenovo SD card,
change production selection, or commit emulator-coupled changes before review.

## Bounded research and compatibility

Official reference baseline remains agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOS v3.0.2 and VDP v2.16.0.
[Executable contracts](../../../../../agon-docs/docs/mos/Executables.md)
place MOSlets at B0000 within 32 KiB, and do not encode that load address in the
MOS header. The existing EMOS loader explicitly selects that slot. Official
[UART APIs](../../../../../agon-docs/docs/mos/API.md) provide blocking reads;
the diagnostics retain the existing EMOS nonblocking leaves with bounded waits
instead of changing those stock APIs. References remain read-only.

Component-owned implementation is in sibling agon-emos: src/emos.c,
src/emos_uart_probe.c, src/emos_uart_flow.c and projects/uartflow. UARTTEST uses
`EMOS UART1 -> P4\r\n` / `ACK\r\n` at 115200 with no flow control; VDPPOLL uses
`17 00 80 A5` / `80 01 A5` at 1152000 with CTS/RTS. These are deliberate
different peers, not a request to use either against ordinary active input.

The loader now needs `/emos/uarttest.bin` and `/emos/vdppoll.bin` for the two
commands; missing files use normal MOS load errors. Resident service admission
still requires Legacy and utility context and refuses a keyboard-owned UART.
New slow-open operation 5 requires the paired newer EMOS; older EMOS refuses it.
This is a development service extension, not production acceptance or ExExt
activation. The previous ordinary image uses 130677 bytes (395 free); the
combined private image was correctly refused at 131262 (190 over capacity).

## Initial off-bench result

Complete for the authorized off-bench scope: 1938 ROM bytes recovered, with
1748 free in the combined private native image. See the
[results](DIAGNOSTIC-ROM-RECOVERY-RESULTS.md) for exact checks and open physical
qualification gates. No deployment or production selection.

## Authorized hardware qualification — 2026-10-09

The Author released the bench and explicitly waived backups of installed
firmware. The ordinary candidate, not the unfinished private parallel build,
is the installation target. Mainboard VDP remains unchanged. EMOS continues to
own UART admission; temporary dedicated P4 peers replace ordinary input only
while the Agon executes bounded startup scripts. Preserve and restore the exact
startup file; verify newly installed ROM by full readback.

DRH01 [x] — Deploy the frozen ordinary ROM and all three diagnostic MOSlets;
verify SD bytes, flash EMOS once, verify its complete 128 KiB ROM and input.
DRH02 [x] — Exercise MOSlet loading, argument/admission refusal and wrong-peer
cleanup. Retain durable Agon results and confirm input recovers without reset.
DRH03 [x] — Exercise exact UARTTEST/VDPPOLL replies with dedicated P4 peers and
UARTFLOW regression where feasible. Restore the exact current ordinary P4
application, original startup and an idle recoverable prompt afterward.
DRH04 [x] — Record precise installed identities, outcomes and remaining gates.
No production promotion or live parallel activation is implied.

Hardware qualification passed; see [hardware results](DIAGNOSTIC-ROM-RECOVERY-HARDWARE.md).
