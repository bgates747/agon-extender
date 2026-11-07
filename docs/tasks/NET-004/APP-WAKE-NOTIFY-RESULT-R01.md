# Optional UART1 application notification: checked source handoff

The opt-in SDK hook passes actual application/core/owner C checks and native
compile/link inspection. Undefined notification preserves the default binary
exactly. The enabled link-only probe adds145 text bytes and one application wake
byte, with no resident firmware change. This does not establish executed IRQ
behavior, reduced latency, receive safety or an overrun cure.

## Exact checked scope

1. The isolated source branch preserves root/frozen diagnostic headers. The
   generic UART core/emitter, EMOS ROM/IRQ, P4, baud, source/drain/reply/CLOSE
   semantics and deliberate fault quarantine are unchanged.
2. Define `AGON_NETA_NOTIFY(client)` before including `agon/net_async.h` in
   the sole transport-owning translation unit. It must only mark retained app
   RAM, with no EI/MOS/gateway/wait/log/allocation/reentry or storage retirement.
   Notification follows source-release publication and actual service
   phase/fault/error changes; duplicate source/TAIL notifications may coalesce.
   Undefined is the default. This is a scheduling hint, never proof of drain,
   positive CLOSE or owner health. Wire-only TEMT/CTS still use tick fallback.
3. Compiler386 passes19 guarded steps in2.043s (inner checks1.879s), with all
   descendants joined and normal release15:11:17.613481UTC/no next request.
   Actual-C ASan/UBSan checks cover publication/client identity, callback before
   SUBMIT returns, SOURCE/TAIL/IDLE/fault, quiet blocked/tailing/idle calls,
   early reply/unsafe reuse and refused-CLOSE borrowed lifetime. Original SDK
   compiles but fails the notification oracle at runtime, as expected.
4. The baseline/OFF target objects and whole link-only application binaries are
   byte-identical at identical build paths. ON core/emitter objects remain
   byte-identical. Native listing/relocations show source flag store before
   wake store. No instruction timing, ISA execution or all-IRQ bound was tested.

| Link-only probe scope | Notification ON | Default OFF/baseline | ON minus OFF |
|---|---:|---:|---:|
| Text, bytes |3742|3597|+145|
| Data, bytes |78|78|0|
| BSS, bytes |446|445|+1 app-owned sticky byte|
| Private service static frame, bytes |20|8|+12|

These totals include the retained link-only client/core/providers; they are not
an incremental whole MechAgon application measurement. Static frame rows exclude
call arguments, return/IRQ saves and nested providers. Native probe binaries are
compile evidence and MUST NOT be staged or RUN. The consumer owns its separate
coherent application integration and physical qualification.

## Preserved preparation corrections

Compiler382 stopped at link time because the older lifetime fake lacked the
current owner's scoped lock/RX substitutes. Compiler384 passed the maintained
RX-scope regression, then compilation rejected an implicitly-returning donor
`main` after test-symbol renaming. Compiler385 passed notifications through the
final synthetic abort, where the copied assertion used the older public fault
flag rather than current pending-fault publication. Correcting these test-model
bindings did not alter the SDK candidate. Their bounded receipts/source notes
remain; compiler386 is the passing coherent run, not a retroactive rewrite.
