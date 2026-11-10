# NET-008 — Remove the P4 receiver bottleneck before probing ESP8266 limits

Smith extends the existing experiment to find and fix the test platform's receive
overruns. Actual168's230400 result remains a valid operating point;384000 FIFO
overruns do not establish the module's maximum. Freeze this contract before
implementation. Preserve all existing results and current6502 bench custody.

## Scope and work

1. Inspect the exact identified P4/IDF UART ISR, ring buffer, event queue, task
   scheduling, CRC/pattern cost and USB progress paths. Map observed event3 to
   actual IDF behavior. Distinguish proved source defects from causal hypotheses.
   Record pinned source and a bounded diagnosis before selecting corrections.
2. Fix the isolated NET-008 P4 appliance and necessary host tools. Keep existing
   frame/payload/CRC/sequence oracles and real simultaneous duplex workload.
   No EMOS/mainboard VDP hacks, no ESP8266 firmware replacement or persisted
   modem settings, no hidden throttling to make a rate pass. Flow-control wiring
   remains TX/RX/GND without RTS/CTS. No unrelated product transport changes.
3. Make receive draining independent of slow USB formatting and lower-priority
   production/verification. Preserve meaningful overflow/error counters, finite
   bounds, explicit start, safe task joins and UART retirement. Do not erase an
   overrun and relabel the run successful. Preserve credential privacy.
4. Qualify the receiver independently with deterministic continuous input up to
   nominal1152000baud before attributing any repeat ladder failure to ESP8266.
   Prepare an isolated P4 UART TX-to-RX hardware-loopback control where the pinned
   IDF explicitly supports it through existing internal routing; otherwise use
   existing bench injection equipment with a declared wiring/setup dependency.
   No unapproved wiring alteration. A software loopback validates processing only;
   identify the actual peripheral/ISR/ring path exercised and remaining limits.
5. Native controls must exercise correction-relevant queue/scheduling/lifecycle
   behavior and framing under fragmented/coalesced input; strict P4 builds pin
   effective task/core/IRQ/buffer settings. Reserve normal compiler FIFO. Finish
   preparation before asking scheduler for a fresh bench slot; no current token
   reuse or preemption. Use genuine grant-first admission and one sole operator.
6. Hardware controls: finite short checks first, then one minute at1152000 with
   independent endpoint frame/byte/CRC checks, no FIFO/ring/event loss, explicit
   producer/receiver timestamps and errors. A failing harness control stops module
   ceiling claims. If a control requires physical setup not already present,
   complete source work and identify that exact dependency rather than inventing
   a passing platform qualification or silently broadening hardware operations.
7. After platform qualification, repeat the authorized modem ladder115200,
   230400,384000,576000,1152000: short checks until first genuine transfer fault;
   back down one step and qualify10/30/60s. Retain first faults and reconcile
   command mode positively before deliberate continuation. Report both endpoints,
   wire-rate ceiling, useful payload throughput and measurement-window limits.
   UART receive overrun remains platform failure unless independently explained.
8. Reuse private Pi5 keyring provisioning, runtime CUR-only join, and no capture
   during credentials. App-only P4 install/readback preserves other firmware,
   startup/partitions/NVS. Current explicit release ended old hold168; any new
   bench custody/retention follows the new scheduler booking and user direction,
   not a revived old hold. Restore supported product P4 for clean final release
   unless Smith explicitly directs retaining the new development image.

## Completion evidence

1. Source cause analysis with exact corrective behavior and remaining hypotheses.
2. Passing relevant native controls and identified P4 build.
3. Actual receiver qualification path/limits; one-minute1152000 result or concrete
   unresolved platform defect, with no unsupported claim of modem limitation.
4. Corrected modem baud results after platform qualification, genuine task/process
   joins, installed firmware identity and normal scheduler handback.

The user authorizes finding/fixing and proceeding under this frozen extension;
there is no additional per-change approval round. Publication remains within the
existing logical-group commit/push instruction. Hardware operations still require
normal exclusive scheduling. This contract starts no unattended monitor or suite.

## Source candidate and qualification preparation

Contract frozen/pushed03aae5cd before implementation. Bounded diagnosis in
[RX-SOURCE-R01.md](RX-SOURCE-R01.md) distinguishes source hazards from unproved
actual cause. Corrected source fc061128: main/RX priority8 over TX5 pinnedcore1,
no active receive-loop USB formatting in corrected profile, early32-byte FIFO
threshold, supported IRAM/level2 UART ISR/internal storage. Diagnostic counters
retain ring/queue high-water and read-call gaps; no data/error concealment.

Strict identified P4 build passes in45.797host seconds,243168B, SHA256
8e0f2f627d9f74a0e324152ea7d2398a18b12e6e4203519c4eee5cf2de8bd403. Six receiver
acceptance fault controls pass alongside unchanged native CRC/private-packet
and real loopback TCP controls. A strict misleading-indentation build refusal
was corrected before this successful build. Compiler867 joined/released/nextnull.
This is source qualification only; no physical receiver fix is yet established.

Normal fresh hardware request59d6d7bd0618 queued; current6502 custody preserved.
App-only write/restore span245760bytes (larger than the previous241664 prefix),
with retained normal product suffix/provenance. Bind exact new span; do not reuse
old restoration length. Whole proposed4200s includes admission120, installation
300, internal controls360, modem ladder2700, cleanup600 and120margin. No clock
starts before actual grant, and no test is dispatched without genuine sole
handoff. Independent internal profile comparisons precede one-minute1152000
control at>=95% wire utilization; any corrected platform failure stops modem
ceiling claims. Restore verified product P4 for normal release unless Smith
subsequently selects different retention. No old168 hold/token is reused.
