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
6. [x] Return actual source/size/test and useful-work results and limitations to
   UART/MechAgon. No production acceptance, automatic adoption or version tag.

## Decision register

| ID | State | Decision |
|---|---|---|
| EA01 | Author selected | Provisional reuse/integration/trial now; no longer gated by longer vanilla benchmarks. |
| EA02 | Owner selected | Separate opt-in provider and immutable one-source guard before construction; preserve synchronous ABI. |
| EA03 | Implementation closure | Exact hook/result/capability layout, atomic sample/error retirement and competing-writer inventory must be checked before consumer binding. |
| EA04 | First trial failed | Receiver overrun after source release; cause unresolved. Full16B/multi-FIFO CTS reserve and useful foreground work remain unqualified; working ROM restored. |

Human source IDs and exact build/network/device paths remain in ignored owner
records; no credentials or unique-device configuration belongs in this task.

## Checked provisional binding (first physical trial failed)

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
is not hardware-qualified. The earlier synchronous failure is separate from the
subsequent first U1 trial, which reported UART1 receiver overrun and deliberate
quarantine; its cause is unresolved. The candidate is rolled back.

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
The selected first trial failed with receiver overrun after source release.
Original status and post-reset RAM are retained; exact working-ROM restoration
and normal clean release are complete. This is no async-performance or
production pass. UART and consumer source feedback is retained in that result.

## Remaining owner receive-service investigation

1. [ ] Correlate exact owner RX STOP/peer TX behavior and masked/callback service
   intervals against the reported first overrun. Distinguish source facts from
   measured timing and preserve the reciprocal UART0/NM guard. No error clearing,
   forced close, generic-core rewrite or replay follows from the first result.
2. [ ] Select and publish a concrete minimal correction or bounded discriminator
   only after that source analysis; use fresh normal custody for any later
   physical case. Keep the working synchronous ROM baseline. This record does
   not select another invocation or a performance comparison.

## Positive drain cache versus live ownership — source contract

MechAgon's owner question after the first trial is resolved against unchanged
EMOS2c47053 and checked SDK39d4be6f; this is source interpretation, not another
physical qualification. A consumer may skip redundant foreground PROGRESS4 calls
only after a positive per-source wire-idle result, while an IRQ-coherent snapshot
still shows core IDLE and no fault. This retains a completed drain fact; it does
not establish that EMOS still owns UART1 or that an NM reply is valid/present.

1. `emos_neta_abort` calls the app fault hook only when resident demand is
   nonzero. For already-idle demand0 it can clear its hook and release its writer
   guard silently; `emos_net_reset` also clears NM admission. The application's
   IDLE/open-valid/association fields have no guaranteed revocation notification.
2. An IRQ-reported line error still calls the attached app fault hook, including
   while its core is idle; fault always outranks cached drain. Source/TAIL/FAULT/
   unknown states keep using the supported owner progress path. Initial core
   IDLE from OPEN alone is not proof a particular submitted source drained.
3. Every actual new SUBMIT retains the existing SDK guard before packet/query/
   payload construction. It performs owner progress/admission validation even
   if the caller has a cached drain fact. Prearm per-source wire-idle false for
   the next request and preserve correlation; failed/uncertain submissions do
   not authorize replay or buffer reuse while any borrow survives.
4. Positive close remains owner-validated. A silent idle abort makes later
   owner progress/close unavailable; local IDLE cannot manufacture successful
   RELEASE, remove a separate callback chain or authorize reclaiming storage.
   Existing cleanup/refusal handling remains conservative.
5. While merely awaiting a correlated NM reply, a cached completed drain may
   satisfy the caller's reciprocal TX scheduling barrier. Revocation/error can
   still stop NM delivery; existing receive faults/deadlines must handle that.
   This shortcut gives up immediate foreground probing of an otherwise silent
   idle revocation and redundant foreground RX assistance. It supplies no new
   RX-latency guarantee or explanation/cure for the observed overrun.

No resident generation field, generic driver change, IRQ takeover, direct UART
access or firmware/build/test change is selected by this clarification.

## Jukebox audio-stream consumer consultation

Smith requests Jukebox join the UART1 discussion for its already-selected
Pi5→ESP8266→eZ80→mainboard-VDP audio stream. Jukebox owns its NET-001 player,
binary parser, request cadence and PCM queues in its dedicated streaming branch;
UART owns the generic driver, Extender the EMOS hooks, MechAgon its consumer.
This consultation creates no duplicate implementation or qualification gate.

Jukebox's selected initial receiver uses vanilla Console8 at1152008N1 without
RTS/CTS, one bounded JPCM request at a time, counted binary +IPD framing and
separate receive/capture/UART0 staging storage. Its accepted full-track8kHz
U8mono result was Pi/Oryx desktop playback; device-free/native receiver checks
do not establish ESP8266 or simultaneous-UART hardware behaviour. Higher-rate
operation remains unqualified. Its future playback cadence belongs to VDP
audio consumption; a timer posts flags rather than performing I/O.

At576000input and1152000output8N1, fully disjoint wire windows give an ideal
38400PCMbytes/s ceiling before protocol overhead.44.1kU8mono needs actual wire
overlap, a faster qualified input or another change. Playback from VDP buffers
during receive does not remove either wire cost. RC3 integer divisor behaviour
must be matched to actual ESP baud; requested460800/921600 may become576000/
1152000 respectively. These are arithmetic/source facts, not measured rates.

Extender supplied the exact manually tested Wi-Fi-start binding and clarified
that it creates no TCP session, chooses no +IPD/TCP mode, and also does not close
a pre-existing module socket. Jukebox owns its explicit TCP setup and binary
receive parser; the Wi-Fi diagnostic's printable-text sanitizer is unsuitable
for PCM. Credentials stay in private configuration. The shared receive-service
concern is UART0 masked/CTS service versus UART1 FIFO headroom; a larger software
ring and a source-release callback do not prove receive safety or wire drain.
No new generic-driver correction or physical test is selected by this note.

### First Console8 receive evidence returned by Jukebox

Jukebox's NET-001-R0003 owner reports that Smith ran the standalone receiver
and returned an 8192-byte PCM capture identical to the Pi source after offline
comparison. The runtime used no PCM checksum. Unchanged vanilla U1 r05 at
1152008N1/noRTSCTS, 4096-byte receive ring and32requests of256PCMbytes recorded
result0, parsererror0, overflow0, UARTfault0, lineerrors0 and close0; sampled ring
highwater21. UART bytes10376 include setup and framing. This is the first physical
ESP8266 binary+IPD/JPCM receive evidence; there was no UART0/audio forwarding.

The8192PCMbytes represent1.024audio seconds. Reported134MOS counts at nominal
120counts/s give1.117s and7336PCMbytes/s, below8000PCMbytes/s consumption. This
is a short uncalibrated receive interval; it does not isolate the credit/AT
overhead or qualify sustained playback. Jukebox proposes larger bounded windows
within its own task before playback; this report assigns no new build/run/baud
change or owner work. The separate EMOS/P4 overrun remains unresolved.

### Longer Console8 receive result

Jukebox NET-001-R0004 corroborates the first short receive result:213760PCMbytes
from835requests of256bytes exactly match the Pi source prefix in offline
comparison. Unchanged vanillaU1r05/1152008N1 recorded zero UART overflow/fault/
lineerror/parsererror and positive close; sampledRXhighwater26. No runtimePCM
checksum, capture-time SDwrite or audio/UART0 forwarding occurred.

At nominal120MOS counts/s,3602counts are30.0167s:7121.38PCMbytes/s,89.02% of the
8000bytes/s target, or26.72audio seconds delivered in that interval. Timing is
conditional on60Hz and uncalibrated. Timed GET-loop UART RX267200bytes is separate
from lifetimeRX267336; its53440nonPCMbytes equal64bytes/request in aggregate,
not an attribution to individual AT/Wi-Fi/driver costs. This is an extended
receive-integrity pass, not sustained8kplayback. Larger bounded request windows
remain Jukebox's proposed next comparison; no new owner work is assigned.

## Goal-directed receive correction tranche

Smith's independently verified MechAgon goal delegation selects reliability
first, measured eZ80 headroom and then maximum sustainable presentation rate.
The [receive-service plan](EMOS-ASYNC-RX-R01.md) bounds Extender's owner source,
correction, measurement and separate isolation work. Protected current/queued
bench owners finish first; no active lease is transferred or preempted.
