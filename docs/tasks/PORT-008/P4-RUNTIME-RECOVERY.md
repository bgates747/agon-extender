# PORT-008 — P4 runtime cancellation and reattachment

The Author approved the next off-bench tranche after publishing observed-loss
invalidation. The private P4 candidate must sample EMOS CLOCK/VALID while UART
is live, fence shared pads on observed withdrawal, discard old transport state,
and require reciprocal release before UART reattachment. EMOS remains unchanged
at 91 ROM bytes free. No bench use, ordinary-profile behavior change, native
payload activation, production promotion or automatic commit.

P01 [x] — Extend the actual private P4 startup coordinator to monitor live
controls on its installing core. On observed withdrawal, complete a new pad
fence before invoking a one-time transport-cancellation callback. Failed cleanup
must latch refusal, not permit a later timer to restore UART. Repeated waiting
polls must not repeat cancellation. Keep existing boot tests and ordinary startup.

P02 [x] — Bind the candidate console owner before its next USB/parser/serializer
iteration. Clear software replies, cached/setup/preactivation bytes, console and
parallel capabilities, keyboard/repeat/admission queues and old service records.
Reuse existing cleanup primitives. Reset only transport/parser control state;
do not select a video mode, clear the framebuffer, or publish an EMOS route.
Invalidate USB report epochs at loss and again before reattachment without
dropping connection/handle lifecycle events; require neutral input before new
physical presses. After the fence, discard hardware TX/RX queues and UART event records without
using the existing cancellation helper that reattaches UART pins. Require actual
TX idle before reattachment. Drop stale asynchronous application completions
using the existing mailbox generation; preserve already-confirmed terminal
service results rather than turning completed mutations into failures.

P03 [x] — Test real coordinator, adapter and cancellation leaves against the
SDK boundary: live withdrawal at every held level, repeated cancellation,
wrong core, queue/restore errors, fresh peer recovery and stale lease/keyboard/
application records. Reuse existing paired adapter, session, storage, keyboard
and lifecycle fixtures; add only focused reset cases. Compile and validate full
ordinary and private P4-PC targets, retain source/artifact hashes and measured
host test durations. Update parent/current development records and pause.

Completed off-bench: [results](P4-RUNTIME-RECOVERY-RESULTS.md) and
[portable artifact index](P4-RUNTIME-RECOVERY-RESULT.json). Author review pending;
this completion does not close the parent reset/payload or hardware gates.

## Bounded research

Reuse [HANDOVER.md](HANDOVER.md), [BOOT-STARTUP.md](BOOT-STARTUP.md) and
[observed EMOS loss](RUNTIME-RELEASE.md). Official MOS UART and GPIO contracts
are documented in the latter at agon-docs commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.
The official [VDU command reference](../../../../../agon-docs/docs/vdp/VDU-Commands.md)
defines retained enable/disable processing; private reset must not leave old
disabled/paused parsing or echo output active on a new lease. This is a transport
boundary in the private candidate, not an upstream behavior correction.

The retained Context::setProcessorState intentionally executes cursorAutoNewline
when ordinary pause resumes. That may scroll the screen, so this private reset
uses a guarded context control reset without invoking cursor or drawing actions.
Stock pause/resume remains unchanged; this is not an upstream bug fix.

Use the retained ESP-IDF 5.5.5 source at
`b774170ff46c393eeb5e495ea37936038d3f4f4f`: esp_driver_uart/src/uart.c
uart_flush_input removes RX ring/FIFO bytes but does not discard TX or reset
the event queue. The existing console driver has no TX ring and one owner on
core 0. Reuse its existing TX interrupt/FIFO cancellation idiom while pads
remain detached; never call console_cancel_tx during reset recovery because
it rebinds shared UART pins. A FIFO reset is not proof the shift register is idle.

## Deliberate limits

This increment reacts to sampled control withdrawal; it does not prove universal
reset detection or fix the short READY reset indication. Existing VDU execution
returns to the sole owner before it can cancel; no claim of instantaneous abort
or undoing completed drawing/file mutations. Stock resource callbacks and scene
contents are not comprehensively invalidated. A surviving EMOS after a P4 reset
still needs later foreground reconnect and committed ExCom-route recovery.
P4 reattachment requires the existing exchange, typically restarted by EMOS
boot; it does not automatically admit a keyboard or display lease. Fresh console
prepare must issue a new challenge. Version-2 parallel control stays cold because
its payload coordinator is still unbound. Native block/status, full reset protocol
and physical asymmetric-reset qualification remain parent integration gates.
