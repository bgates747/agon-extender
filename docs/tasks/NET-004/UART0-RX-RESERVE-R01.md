# NET-004 — UART0 receive reserve source preparation

The bounded UART0 receive-reserve candidate passed a new four-session owner overlap case and was then rolled back cleanly. The new fixture checked ordinary MODE/cursor completions while UART1 requests were logically active. This supports finite functional health, with electrical timing margin and the original renderer failure's cause still unresolved. A subsequent consumer case requires its own exact freeze and fresh custody; the candidate remains experimental and default-OFF.

## Scope and ownership

1. Extender owns UART0/UART1 masked boundaries, parser/context preservation and the candidate EMOS composition. The native VDP owner supplies its exact installed sender CTS configuration and wiring facts; the generic UART owner provides bounded contract advice, with its separate RX-005 prototype/review work untouched.
2. Preserve frozen witness ROM3bb38d/source03e05c2, carry controlc1047/source9dd099f, incominga25f, exact native5d657 and all actual108 failure/post-reset provenance. Use a new source checkout. No P4/baud/native firmware change or blind renderer replay.
3. The source candidate must address both standalone UART1 IRQ/foreground DI intervals and repeated UART0 one-byte receive followed by full UART1 service tails. PC2 STOP controls incoming UART1, not UART0. Preserve IFF0/IFF1, primary/index/alternate registers, actual source/drain/reply lifetimes, bounded error/cap behavior and real-zero carry.
4. Do not add nested EI, unbounded drains/waits, extra speculative acknowledging LSR/RBR probes, packet drops/resynchronization, forced CLOSE or fabricated completions. Each serviced byte retains its one acknowledging status/RBR pair. Cap exhaustion is not clean-empty.

## Bounded reference précis

Official read-only MOSv3.0.2/8336409351ee5314e02801a7b72a4f1bb5282519 and VDPv2.16.0/c7ac293d2aa81ddfa693390549bcd909069c8fc3 remain clean at their tags. Official docs API mos_setkbvector defines the DE24 payload and removal lifetime; System-Commands defines header/length/payload framing. Stock VDP agon.h maps native RTS13 to eZ80 CTS, native CTS14 to eZ80 RTS; these stock definitions alone do not establish exact installed5d657 sender configuration or physical compliance.

Exact retained EMOS03e source: src/uart.c enables UART0 FIFO07 and MCTL02 RTS; src/interrupts.asm reads one UART0 byte before the APP UART1 tail; src/emos_keyboard_io.asm asserts PC2 STOP and runs bounded UART1 service under DI. src/emos_uart0_rfc25_io.asm ownership/TEMT LSR reads remain outside IRQ witness coverage. Source assessment and pins: agents/net004/uart0-rx-witness-r01/ACTUAL108-SOURCE-ASSESSMENT.md and actual108-source-assessment.json.

Actual108 raw[2,6,7] is the software BODY/MODE-index6/seven-remaining state before the available byte. It does not authenticate a real MODE packet on the wire after possible earlier framing loss. OE is positive receive-overrun evidence, without a timestamp/lost-byte count or causal order to the first-poison deadline. Sustained per-byte service deficit and a single long blackout are both source risks, not measured causes.

## Work and dependencies

1. [x] Close exact installed native manifest/source/dependency pins, RTS-to-CTS wiring and active polarity, sender reaction/in-flight bound, UART0 RTS ownership and entry-state restoration. Record a precise unsupported dependency if source cannot establish it. No speculative physical probe.
2. [x] Implement the smallest justified bounded UART0 RX-first/reserve change in a separate checkout. Factor register/context ownership deliberately; UART1 service must not recursively re-enter itself. Preserve other modem bits and any pre-existing STOP.
3. [x] Choose an explicit experimental build composition and exact OFF control. Retain optional witness source; the identified witness-ON build has only26ROM bytes free, whereas carry-controlc1047 has335. Report any required composition or code-sharing tradeoff rather than deleting guards or silently disabling a selected diagnostic.
4. [x] Qualify meaningful actual-C/linked-native boundaries and negative controls under normal compiler FIFO: initial RTS states, nested/IFF0/1, cap/empty/error/zero, pending bytes, byte/carry/register preservation, callbacks/lifetimes and nonrecursive receive arbitration. Report exact ROM/BSS/stack costs and calibrated limits; abstract or linked checks are not executed full ISA/IRQ/hardware.
5. [x] Package source/config/images/maps/checks/retained rollback and propose ONE bounded owner isolation exercising both receive directions and relevant masked boundaries. Root selects physical dependency ordering before fresh ordinary bench admission; no current run or consumer replay.

## State

The source/native candidate and new MODE/cursor overlap appliance passed their selected checks. Actual112 completed ONE four-session case, preserved original application RAM before later LOAD/reset, restored the exact incoming ROM with full independent readback, and released after fresh complete handback. All owner target access is stopped. MechR13 source-only templates and the physical dependency record were returned; its final coherent kit and new admission remain separate. No default adoption or cause/performance claim. Publication hold persists.


## Checked source/native result and selected next fixture

Compiler545 reproduced the exact old witness ROM with reserve OFF. Reserve+witness ON failed the physical ROM guard; that linker failure is retained. The explicit APP-only reserve image uses130952 ROM bytes (+215 versus c1047),120free,3503BSS (+4),802initialized RAM bytes unchanged. It uses OPEN4, with no SDK/callback/source/drain API change; checked7ded can be reused for a later consumer if other composition choices remain unchanged. OPEN7/f1de is incompatible with this chosen image. All mandatory native guards and823 linked leaf cases plus3 bad-code controls pass; this is not full ISA/IRQ/hardware execution. Local helper saved frame36B excludes stub-callee return frames: parser CALL adds3, giving39B at local parser entry including RX helper entry return, plus existing IRQ/tail/parser/callback stack unknown. No complete application stack peak is established.

Source7e1c7a3; full ROM1e4e54dda8692f141a56114147eb775e315295cd68e3ac409484ca127d6fd830; private23-member archive52abd7c3ad77121f2b4c0cf12006a3c793f25e2b6f100bfbab37ec2a218defd3 independently verifies every member. Source/native package and a bounded physical proposal returned by durable mail and immediate steering. Root selected the next owner fixture/case after complete closure; admitted6502 actual111 remains protected and Extender target-stopped.

6. [x] Prepare and qualify a NEW four-session176-case overlap fixture and actual controller: UART0 MODE/cursor burst while UART1 transaction is pending, independent flag/value oracles, zero/nonzero, continued IRQ/VBlank/cap service, source/TEMT/reply storage lifetime and four positive CLOSEs. The serialized old176 comparator is insufficient. The root corrigendum removes startup-reserved GP completely; only documented MODE and cursor flags/values are used. Count logical pending and sampled nonidle engine state separately from physical wire overlap. Freeze all dependencies and negative controls before READY; no target access from PREPARING.
7. [x] Run only the selected ONE finite owner case after normal actual111 restore/release, fresh current tuple/admission/sole install and full readback. Apply60nominal native/120host/600whole incl180cleanup reserve, firstfault/evidence/RAM preservation/standing bounded recovery, exacta25f rollback/fullreadback/fullhandback/release. Functional finite hold/resume is the supported claim; numerical electrical reserve/108cause/30Hz/default adoption remain unproved. Fresh MechR13 depends on owner actualPASS and cleanrelease, then its own final coherent kit.


## New overlap appliance and runtime closure

The root query corrigendum omits GP entirely. Compiler552 built the19505-byte new appliance and passed actual helper sanitizer controls, five compiled bad-code controls and actual controller admission/result negatives in8.110host seconds. Four sessions contain176 byte-pattern records and352 MODE/cursor query bursts. Each burst expects two independent documented completions; MODE10 plus cursor4 are14 logical response bytes, not FIFO occupancy or a cap-hit measurement. The foreground samples pending-without-ready and nonidle serializer state before issuing the ordinary VDU query; neither sample proves physical simultaneity. Positive source release/laterTEMT/reply and four positive CLOSE boundaries still govern storage/callback reuse. Continued clock/IRQ service is required; no numerical electrical reserve is assumed.

The linked48-byte application witness and all static appliance storage fit the selected040000–04FFFF SAVE window; stack peak remains unmeasured. The immutable runtime freeze has124 inputs, including explicit dynamic bootstrap/reset dependencies and exact source/config controls. Compiler552 released with all owned children joined and no next request. The historical serialized comparator and all old evidence stay unchanged. Request-local R13 source templates were returned with OPEN4 binding; root final freeze and physical admission remain conditional on owner functional PASS and clean rollback/release.


## Actual112 result

| Check | Required | Observed |
|---|---:|---:|
| Exact echoed payload records |176|176|
| Positive session/CLOSE retirements |4|4|
| MODE/cursor query pairs |352|352|
| Zero/nonzero cursor positions |176/176|176/176|
| Pending-without-ready samples |Positive, at most352|352|
| Nonidle serializer samples |Positive, at most352|352|
| Query failures |0|0|

The durable result and independent48-byte linked RAM witness agree. Original64KiB application-window RAM was saved before any later LOAD or reset, with no recovery reset needed. Native elapsed270ticks uses nominal120Hz; the14.202host seconds include command delivery and terminal observation, not exclusive processor time. Logical state samples are not simultaneous-wire measurements, numeric CTS reaction/inflight reserve, measured cap hits, a proof of the actual108 cause or30Hz qualification.

Exact selected candidate ROM installation and incoming rollback both passed independent full131072-byte readbacks. Fresh final rootCLI/cursor/mode0/callback0/route0, whole startup/listener, neutral input, offline listener/idle worker/free USB and joined actors passed. The full493.970second owner window stayed within600seconds. Native VDP, P4, startup and listener were unchanged; SD remains mounted. Normal release preceded offline reporting and the next Mech consumer received immediate steering. Machine-local exact evidence is retained outside tracked source.
