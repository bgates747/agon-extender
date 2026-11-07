# Provisional application-owned UART1 integration

Reuse UART's application TX core and bounded OTIRX leaf under EMOS admission,
without replacing EMOS RX or growing a resident engine. Smith explicitly selects
this provisional integration and a separate MechAgon trial. Current synchronous
clients and the already frozen consumer scheduler case remain unchanged.

## Scope and source précis

1. Extender owns shared SDK/adaptation; EMOS owns resident admission/IRQ glue;
   UART owns generic core corrections; MechAgon owns its consumer. Engine, source,
   callback and state reside in application RAM. One source, no additional queue.
2. Baseline EMOS source2c79c6006d6bcb0c2b3f9d8d6aae3ef4b36c730a is the
   installed UART-NM/guarded-RFC25 native branch. Raw ROM129108B leaves1964B.
   Its new isolated owner branch is codex/net004-uart1-app-r01, task INTEG-024.
   Mandatory native linked validators and the131072B ROM limit remain.
3. UART source823bb91dd4c1af5a1488e3d3361648646b601445 supplies unchanged
   experiments/uart1-async/include/u1_tx.h, src/u1_tx.c and src/u1_emit.src.
   No vanilla IRQ installer, UART reopen or new numeric MOS syscall is used.
4. Official reference baseline: agon-docs f9806bd3cbff6ed5d1c08bef1d51fed11764b86b
   (untagged; unrelated untracked ._.DS_Store preserved), MOS v3.0.2
   8336409351ee5314e02801a7b72a4f1bb5282519 and VDP v2.16.0
   c7ac293d2aa81ddfa693390549bcd909069c8fc3, both clean. MOS docs/mos/API.md
   0x14/0x15 define vector ownership; these stock APIs do not grant takeover of
   EMOS's active receiver. References remain read-only.
5. Existing src/emos_net.c serializes synchronously; src/emos_keyboard_io.asm
   owns RX/error sampling; src/emos_keyboard.c owns competing writers/retry;
   src/emos_uart0_rfc25.c owns UART0 admission. UART0 WAIT_CTS can still spin
   with interrupts masked; UART1 async does not fix that independent issue.
6. P4 transport/console_hardware.inc configures hardware CTS/RTS with RX stop
   threshold64; ESP32-P4 has128B UART FIFO. A16B eZ80 burst plus already queued
   local16B FIFO/shifter fits the64B post-stop margin under the single-writer
   contract. Audit the exact matched P4 source/configuration before admitting
   that reserve; do not infer a peer reserve from generic driver defaults.

## Selected compact binding to implement and check

1. Explicit optional ext.neta provider through the existing66B EMOS gateway;
   old ext.net remains synchronous. No silent behavioural change for old apps.
   Open supplies an ordinary application service entry; EMOS validates spans,
   caller/IFF/mode/RX owner and atomically excludes every other UART1 writer,
   source switch and shared-pin handover until positive detach.
2. EMOS owns the existing UART1 IRQ and RX drain. It supplies the application's
   bounded service entry one shared LSR/error/CTS observation after RX service.
   At most one authorized FIFO burst per service; no CTS polling inside ISR.
   TX-empty interrupts drive throughput, existing VBlank provides blocked-CTS
   retry, foreground progress supplies prompt later-TEMT retirement. Disable
   empty IRQ while blocked/tailing/idle to prevent storms. Preserve RX enables.
3. Application service uses unchanged u1_start/u1_step/u1_detach and emitter.
   EMOS retains only hook/demand/owner bookkeeping, never source/count/buffers
   or an async serializer. Specify actual callable registers/return states and
   exact open/submit/progress/detach operation sizes before consumers use it.
4. Source callback, a later positive TEMT sample, and correlated NM reply are
   independent. Early callback and early reply are legal. SDK must guard BEFORE
   query/header/payload construction against a live source/tail or unretired
   transaction. TAKE cannot alone permit buffer reuse. No extra staging queue.
5. Timeout/invalid-reply RELEASE refuses unsafe detach and retains source,
   application code, IRQ/callback and reply storage. RELEASE selector input[0]
   is outside the input+1 TX borrow; unsafe retirement is the distinct issue.
   First fault remains useful. A timeout never cancels or replays an NM request.
6. Application exit must retire the installed hook before application storage
   is reclaimed; abnormal live/faulted exit stops/faults the owned stream and
   removes pointers atomically, without claiming positive transfer completion.
   Preserve normal startup and the supported recovery path.

## Bounded implementation and validation tranche

1. [x] Publish this plan and the EMOS task before code; send concrete source/
   lifetime binding to UART and MechAgon, resolving material conflicts only.
2. [x] Implement the smallest owner glue and application adapter in their owner
   repositories. Pin/import unchanged reusable core with license/provenance.
   Preserve old synchronous provider and matched P4/working UART baseline.
3. [x] Check actual C early callback/reply, TAKE then next SUBMIT, delayed CTS,
   max146B/full count, masked calls, RX/errors, competing writers, tick retries,
   foreground progress, tail-live/invalid-reply/timeout detach and abnormal exit.
   Verify borrowed bytes/query/source remain identical on every refusal.
4. [x] Normal FIFO Pi build, finite15min tranche, serial compiler; host sanitizer
   checks and native linked EMOS validators/actual application link. Record full
   application text/BSS, adapter overhead, resident ROM delta and remaining space.
   Do not waive validators, drop features or claim physical behaviour from host.
5. [x] Publish exact SDK/ROM/map/capability and rollback pins to consumer before
   its adaptation. Prepare a separate finite trial/immutable kit/current tuple,
   fresh normal checkout and explicit stopped sole-operator handoffs. Current
   frozen scheduler case is independent; no new driver inserted there.
6. [ ] Return actual source/size/test and useful-work results and limitations to
   UART/MechAgon. No production acceptance, automatic adoption or version tag.

## Decision register

| ID | State | Decision |
|---|---|---|
| EA01 | Author selected | Provisional reuse/integration/trial now; no longer gated by longer vanilla benchmarks. |
| EA02 | Owner selected | Separate opt-in provider and immutable one-source guard before construction; preserve synchronous ABI. |
| EA03 | Implementation closure | Exact hook/result/capability layout, atomic sample/error retirement and competing-writer inventory must be checked before consumer binding. |
| EA04 | Qualification pending | Full16B/multi-FIFO CTS reserve and actual useful foreground work need matched physical trial. |

Human source IDs and exact build/network/device paths remain in ignored owner
records; no credentials or unique-device configuration belongs in this task.

## Checked provisional binding (not physically qualified)

The optional build flag EMOS_UART1_APP selects provider ext.neta through the
unchanged66B service gateway. It requires the UART-NM/guarded-RFC25 composition
and refuses the parallel profile. No new MOS syscall/vector number is assigned.

| Operation | Input | Output | Success and refusal |
|---|---|---|---|
| OPEN0 | selector +3-byte app hook pointer (4B) | existing7B token/saved callback |0 admitted,31 busy,19 invalid span,35 unavailable |
| SUBMIT2 | same147B maximum gateway input/146B wire frame | none |0 accepted source, including possible early callback;31/19/35 before acceptance |
| PROGRESS4 | selector only | none |0 later positive wire-idle,31 source/tail/retry,35 fault/unavailable |
| RELEASE3 | selector only | none |0 positive hook removal,31 live source/tail,35 retained fault/unavailable |

EMOS calls an ordinary C app hook under DI with both register sets protected:
event1 START returns admission; event0 SERVICE receives its existing RX drain's
shared final LSR with bit0 replaced by GPIO CTS STOP; event2 FAULT retains first
fault/source. Service returns0 idle,1 TX demand,2 CTS retry,3 tail,4 fault. The
actual source validates spans/IFF/Legacy mode, reserves the shared serializer/
Port C guard, services RX before at most one burst, preserves RX IER enables,
and retries via existing VBlank/explicit foreground progress. A16-byte RX cap
never treats its final data byte as a status sample. Abnormal exit removes the
hook atomically and faults a live stream without claiming completion.

The application adapter is include/agon/net_async.h in the single transport-owning
C unit, linked against the unchanged UART core/emitter. Its client contains the
existing NM client plus TX state/release flag, with one app-BSS active pointer.
The existing net.h has default-no-op adapter hooks; old synchronous users retain
provider/wire behavior. The async guard calls owner progress BEFORE query/header/
payload writes. A positive generic RELEASE also retires the app hook association;
a refused cleanup preserves all state. No additional staging or general queue.

Actual-C composition tests and target link/mandatory ROM validators pass. The
checked SDK/ROM binding is available for the selected consumer adaptation; it
is not installed or hardware-qualified. The current failed consumer run used old synchronous
UART1 submission and cannot be attributed to this uninstalled adapter.

[Offline result](EMOS-ASYNC-R01-RESULT.md) records the checked candidate, actual
linked sizes, malformed-OPEN lifetime correction and remaining physical boundary.

The application retains its cleanup association independently of NM admission.
A refused SUBMIT may clear NM admission without removing the app hook; progress
and positive RELEASE must remain possible until that association is retired.
The actual-C refusal regression and unchanged synchronous target-object control
pass. No second buffer, queue, wire change or resident-engine change is needed.

## Published binding and owner preparation

SDK correction39d4be6f is checked and delivered to MechAgon as a new immutable
r02 binding/package; r01 is retained unchanged. Compiler303 released after all
checks/children finished. The [owner installation/rollback plan](EMOS-ASYNC-PHYSICAL-R01.md)
is published before helper preparation. Its private helper passes syntax, exact
candidate/rollback/inventory rehash and seven refused-context policy checks;
central assertion was mocked and no hardware was contacted. The preparation
selection is deliberately request-unbound and cannot authorize target access.
MechAgon must freeze its own consumer/kit/request, followed by owner request
binding, fresh normal admission and stopped handoffs. Current Wolf custody is
preserved. No installation or physical readiness is claimed.

[First physical installation](EMOS-ASYNC-PHYSICAL-R01-RESULT.md) records exact
ROM staging, one FLASH, independent full readback and stopped consumer handoff.
The selected workload and same-lease working-ROM rollback remain pending;
installation is not an async workload, performance or production pass.
