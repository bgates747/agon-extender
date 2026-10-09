# PORT-008 — Session control-owner binding

This bounded increment binds the existing version-2 session exchange to the
existing UART control owners, without enabling parallel pads or changing boot.
EMOS reuses its fixed reply buffer and bounded console wait; P4 handles the
same framed request on its sole console task. Mandatory reciprocal physical
release remains a prerequisite, not a fact inferred from a session reply.

C01 [x] — EMOS adds a private foreground negotiate function, callable only
after its real serializer reservation and handover UART state are established.
The existing FF/16 ISR reply dispatcher validates version, operation, transaction,
challenge, capability and CRC, then captures one reply. Foreground code advances
the lifecycle. No diagnostic command or second UART writer is added.
EMOS refuses to borrow the buffer while a version-1 ExCom lease owns its
identity; its future mode coordinator must close that lease first.

C02 [x] — P4 adds the version-2 branch at the existing F7 control owner. A
staged preparation expires after 2,000 ms, including unsigned clock wrap. Expiry,
console TX timeout or fatal transport failure invalidates capability and requests
release through the existing handover sequencer. It never acknowledges release
or touches shared pads. Version-2 prepare must not reset the display as version-1
prepare does. An accepted version-1 console transition also cancels prior
parallel capability. Ordinary startup leaves this sequencer unrecovered and rejects
version-2 traffic until the future physical adapter supplies completed recovery.

C03 [x] — Test the actual EMOS reply dispatcher and foreground exchange against
the P4 control owner, including version separation, malformed/stale/duplicate
replies, missing peer, stalled EMOS clock, reservation refusal and cancellation.
Reuse existing session and console tests. Compile both target firmware trees,
retain source/build evidence and account for ROM before claiming completion.

C04 [x] — Record results and pause. EMOS's reused wait is 600 mainboard-clock
units (nominally 5 s at 120 units/s) with its existing stalled-clock iteration
fuse; each send retains the existing bounded private-send deadline. This is not
a calibrated performance measurement or a deadline for native payload phases.
Fresh boot identities, stale-wire quarantine, boot GPIO fencing, block-status
exchange and native payload activation remain outside this increment.

## Research and implementation constraints

The official documentation and fixed-carrier baseline are those recorded in
[the session contract](PARALLEL-SESSION.md). Existing EMOS `emos_console.c`
owns the fixed reply buffer, ISR effects and bounded foreground wait; existing
P4 `console_hardware.inc` owns F7 framing and transmission. Reuse those owners.
EMOS has only 860 ROM bytes free at entry; do not relax the image/link guards.
If this binding cannot fit, retain the compile result and stop for discussion
rather than start a further extraction or omit correctness checks.

Boot inspection found EMOS `main.c` calls `init_UART1()` before `emos_init()`;
`uart.c` installs the Port C defaults there. Subsequent inspection of the actual
F92 header confirms these defaults are all inputs and ALT1=ALT2=0, so this
function does not itself enable UART outputs. `open_UART1()` is the first
EMOS UART mux enable to gate. P4
`beginConsole()` releases fence pins but subsequently calls `uart_set_pin()`
unconditionally. These UART-only startup paths cannot qualify as the mandatory
parallel-pair release handshake. Leave ordinary installed startup unchanged;
the future physical binding must fence the first alternate-function/output
enable, not merely add a late negotiation to these current paths.


## Checkpoint

[Results](PARALLEL-CONTROL-RESULTS.md): 218 paired control cases and 10
complete-image eZ80 control cases pass, along with existing session, admission,
handover, console and UART ownership regressions. Both target builds pass;
P4's final frozen source closure is verified. EMOS is 130,480 ROM bytes (+268),
leaving 592 free; static RAM remains 4,058. No bench operation or commit.
Author review precedes the physical boot-release and native payload binding.
