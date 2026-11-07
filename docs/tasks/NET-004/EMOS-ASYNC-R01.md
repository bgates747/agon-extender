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

1. [ ] Publish this plan and the EMOS task before code; send concrete source/
   lifetime binding to UART and MechAgon, resolving material conflicts only.
2. [ ] Implement the smallest owner glue and application adapter in their owner
   repositories. Pin/import unchanged reusable core with license/provenance.
   Preserve old synchronous provider and matched P4/working UART baseline.
3. [ ] Check actual C early callback/reply, TAKE then next SUBMIT, delayed CTS,
   max146B/full count, masked calls, RX/errors, competing writers, tick retries,
   foreground progress, tail-live/invalid-reply/timeout detach and abnormal exit.
   Verify borrowed bytes/query/source remain identical on every refusal.
4. [ ] Normal FIFO Pi build, finite15min tranche, serial compiler; host sanitizer
   checks and native linked EMOS validators/actual application link. Record full
   application text/BSS, adapter overhead, resident ROM delta and remaining space.
   Do not waive validators, drop features or claim physical behaviour from host.
5. [ ] Publish exact SDK/ROM/map/capability and rollback pins to consumer before
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
