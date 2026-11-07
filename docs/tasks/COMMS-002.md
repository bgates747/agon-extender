# COMMS-002 — Matched UART1 versus parallel performance

Smith clarifies that faster MOS↔VDP communication is the project's primary
motivation, well ahead of the faster renderer as a side benefit. Determine where
eight-bit parallel improves or worsens supported communication relative to
UART1, and whether those changes improve the complete application workload.

**State:** The selected [physical forward tranche](COMMS-002/PHYSICAL-R01.md)
completed with three qualified paired size sets and an unresolved 4097-byte
capture. [Results](COMMS-002/PHYSICAL-R01-RESULT.md): parallel reaches 3.371×
UART1 command-stream rate at 8192 bytes on the identical 360 MHz diagnostic
pair; UART1 wins 256 bytes. Exact incoming 240 MHz UART pair restored and
normal lease released. Broader corpus, reverse bulk, useful CPU headroom and
application-matched performance remain. The independent new core/engine source
tranche is host/native-link checked, not the live executable used for r01.
**Owner:** Extender owns reusable transport benchmark and EMOS/P4 accommodations.
Consumer-specific replays remain with their owners.
**Design:** [Performance comparison r01](../testing/communications-performance-design.md).

## Boundaries

1. Keep this test separate but complementary to [COMMS-001](COMMS-001.md).
   Different executable/runner, invocation, configurations, records, runs and
   conclusions. Do not extract speed results from the endurance/CRC/retry loop.
2. Match the same eZ80 and P4 renderer, logical bytes, command/scene workload,
   clocks, receiver state and output requirements. A mainboard-VDP versus P4
   rendering comparison answers a different question.
3. Separate transfer, setup/turnaround, receiver execution, eZ80 occupation and
   complete application time. Count failures honestly and preserve strict
   completion/ownership checks; do not time retries as successful transfers.
4. Accuracy is a prerequisite for a usable sample, not permission to add a new
   carrier checksum/retry protocol. Keep outside-window correctness checks and
   matched instrumentation visible. Performance does not prove endurance.
5. Prepare offline while others hold the bench. Normal ownership, task freeze,
   explicit invocation, no autoexec modification, mode restoration and exact
   rollback govern any later selected run. No current lease takeover.

## Decision register

| ID | State | Decision |
|---|---|---|
| C02-D01 | Selected by Smith | Separate performance test; faster MOS↔VDP communication is the primary project objective, faster renderer a secondary benefit |
| C02-D02 | Selected by Smith | Separate but complementary to accuracy/endurance testing; no conflation of their runs or conclusions |
| C02-D03 | Proposed | Matched UART1 baseline and parallel arms, same P4 renderer and command/data corpus, local sink and actual VDU streams before application replay |
| C02-D04 | Selected physical r01 | Reuse exact optimized timing EMOS and ordinary VDU P4 pair with ExCom/ExExt selection; both arms share one renderer/build. Current networking composition is not the ordinary VDU benchmark |
| C02-D05 | Forward timer selected; CPU scope deferred | Retained PRT1 /256, nominal72000counts/s and bounded saturation checks; configured360MHz P4 shared by both arms. No CPU-headroom measurement in r01 |

The selected forward r01 uses one retained matched pair with explicit carrier
selection and complete receiver-byte verification outside timing. Its P4 runs
at configured360MHz; current network/application firmware runs240MHz and is
restored after acquisition. Reverse bulk, the broader corpus and useful CPU
progress remain separate future bindings; r01 does not invent those results.

[Offline r01](COMMS-002/OFFLINE-R01.md) defines the independent source/check
tranche. The existing EMOS-owned ExCom/ExExt VDU stream is the relevant source
donor; current networking providers alone are not the benchmark interface.

## Work sequence

1. C02-01 [x] Record the separate objective/design and primary project motivation
   before coding, linked from the sole authoritative TODO.
2. C02-02 [ ] Audit actual public MOS/VDP documentation and owned UART1/parallel
   VDU/data source paths; pin baseline/source/build identities and completion
   semantics. Reuse existing bounded transport evidence without calling it a
   speed comparison. Keep official references read-only.
3. C02-03 [ ] Freeze workload sizes/patterns/VDU commands, exact matched arms,
   clocks, timer resolution, instrumentation, repetition/order and correctness
   checks. Include setup-dominated tiny cases and sustained streams.
4. C02-04 [ ] Implement the dedicated benchmark/coordinator and meaningful
   timer-boundary/byte-equality/refusal checks. Keep endurance fault injection,
   five-attempt retry state and hours-long schedule out of this program.
5. C02-05 [ ] Build/check through normal compiler FIFO; freeze binaries/manifests
   and finite deployment/invocation/restoration before requesting target time.
6. C02-06 [ ] Run a selected bounded paired comparison under fresh sole custody,
   with repeated/reversed controls and exact incoming restoration/clean handback.
7. C02-07 [ ] Report side-by-side UART1/parallel units, median/tails/worst cases,
   sample counts and percentage change from UART1. Identify crossover and
   separate transport gains from rendering/application limits. Propose changes
   from measured costs, including an honest negative outcome if needed.

## Evidence limits and relationship to existing tasks

1. The physical r01 result establishes a bounded forward VDU buffer-update
   comparison on one matched diagnostic pair, with explicit capture failures.
   Prior upload, echo, MechAgon and rendering results retain separate scopes;
   none establishes a general current networking/application speedup.
2. PARALLEL-001's selected Wolf endpoint remains unresolved. This independent
   transport performance task neither silently chooses that endpoint nor closes
   the goal. It can provide reusable owner evidence for later consumer choices.
3. COMMS-001 remains an accuracy/endurance design. It supplies separate failure
   knowledge; COMMS-002 supplies speed/CPU-cost evidence. Neither replaces the other.

## Offline implementation result

[Result r01](COMMS-002/OFFLINE-RESULT-R01.md) records nine Python/actual collector
CLI checks, the C++ ASan/UBSan corpus/timer/measurement-order suite, four
independent corpus families and a2,988-byte identified eZ80 core/engine link.
Synthetic arithmetic/model controls are source tests, not a physical speed
measurement. The dedicated benchmark still needs live EMOS/P4/timer adapters
for the wider corpus. Physical r01 instead reuses the exact retained ordinary
VDU timing appliance and records its narrower live comparison separately.

## Selected forward tranche outcome

The [physical result](COMMS-002/PHYSICAL-R01-RESULT.md) supplies bounded r01
evidence for C02-02 through C02-07. The wider checklist remains open: r01 does
not implement every proposed corpus, reverse or useful CPU-progress adapter.
The 4097-byte boundary is explicitly unqualified after incomplete captures;
existing historical numbers are not substituted for it. No promotion or new
parallel/Wolf endpoint choice is inferred.

## MechAgon application-shaped workload context

The Author directs reading MechAgon's existing byte-budget discussion rather
than treating large-buffer throughput as the application workload. The source
count in MechAgon's `docs/tasks/PERF-001.md`, “Discussion: current message sizes”,
provides this historical two-tank/no-bullet, one-scene/one-decision baseline:

| Endpoints and carrier | Minimum bytes per turn | Scope |
|---|---:|---|
| Pi bridge → P4, TCP payload | 144 | 56-byte STATE + 80-byte FRAME, each with four-byte TCP record length |
| P4 → eZ80, UART1 | 184 | Two framed record replies plus SEND acknowledgement |
| eZ80 → mainboard VDP, UART0 | 117 | 80-byte FRAME + 37-byte buffer/upload/RUN wrapper |
| Mainboard VDP → eZ80, UART0 | 12 | Tagged completion plus framing |
| eZ80 → P4, UART1 | 78 | Two POLLs plus framed 24-byte intent SEND |
| P4 → Pi bridge, TCP payload | 28 | 24-byte intent plus four-byte record length |

Each additional empty UART1 POLL adds 18 eZ80→P4 and 16 P4→eZ80 bytes.
Each bullet adds 12 display bytes; beyond four bullets, scene chunking adds
further record and mainboard-command overhead. TCP rows exclude IP/Ethernet
headers. These are source-derived baseline counts, not new captured traffic;
ASYNC-001 changes scheduling, so its actual polling count must not be assumed.
The Royale server's original JSON/WebSocket traffic is not included in the
compact Pi-bridge rows and does not reach the eZ80.

This workload is dominated by small bidirectional transactions, with more UART1
bytes P4→eZ80 than eZ80→P4. The completed physical r01 measures large forward
ordinary VDU buffers eZ80→P4; it does not measure that dominant reverse path or
these network-message envelopes. Its 256-byte result also cannot decide the
complete application's winning carrier. UART0's 117/12-byte rendering exchange
is a separate physical link; replacing UART1 with parallel does not accelerate
UART0 itself. Preserve these distinctions when selecting a later matched replay,
including supported transaction sizes, actual poll count and turnaround. This
narrow source discussion does not release MechAgon's held full-cycle profiling
campaign, select a new fixture invocation, or change the current bench owner.
