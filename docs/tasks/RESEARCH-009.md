# RESEARCH-009 — SPI and I²C alternatives to PARLIO

Determine whether hardware SPI or I²C can replace the intermittent PARLIO
link between the Olimex AgonLight2 eZ80 and the Extender ESP32-P4. Compare
both options using the actual board connections, firmware ownership, retained
failure evidence and transfer performance. Deliver a recommendation, a
candidate pin assignment for each feasible route, and a controlled
qualification plan.

**Complete on November 26, 2026.** Qualify isolated shared-bus SPI first
for staged SD traffic. Keep I²C as a low-rate control option and keep the
PARLIO stall investigation open. No transport was selected for production.
[Findings and qualification plan](RESEARCH-009/FINDINGS.md)

## Frozen execution contract

Extender owns the review. Smith requested the task be frozen and the review
completed unattended in one tranche on November 26, 2026. Smith also authorized
candidate code and left pin selection to Extender. This tranche covers offline
research, calculations and isolated candidate code with host checks where they
clarify feasibility. Hardware rewiring, live device tests, flashing, adopting a
new interface and production promotion are outside this review.

Start from the [current production selector](../../production/current.yaml),
[mainboard SD guide](../mainboard-sd.md), [PORT-008](PORT-008.md) and its
[open stall investigation](PORT-008/PARLIO-UPLOAD-STALL.md). Preserve EMOS
ownership of VDU and transport, eZ80 ownership of the microSD, and ordinary
UART-only or P4-absent startup and operation. Keep normal transfer integrity
policy, including no routine CRCs or readbacks. Local hashes may identify
inputs and controlled qualification may compare known test data. Base any
candidate on the actual pins available on the commissioned AgonLight2 and
P4-PC, and distinguish a schematic assignment from verified harness wiring.

## Checklist

- RESEARCH-009-001 [x] Pin the relevant silicon, board, firmware and interface references. Trace the production host → P4 → EMOS → SD path in each direction. Compare retained PARLIO successes, recent failures and historical SPI/SD trouble. Identify proved stop boundaries and missing observations.

- RESEARCH-009-002 [x] Review both hardware SPI endpoints, usable pins, clocking and controller/peripheral roles. Reconstruct the SD sharing constraint, chip-select discipline, interrupt/reset conflicts and safe behavior with P4 powered off. Compare direct reuse with isolation or alternate pin/role designs. Identify scope and fit risks for EMOS and P4.

- RESEARCH-009-003 [x] Review both hardware I²C endpoints, usable pins, controller/peripheral roles, bus speed and electrical behavior. Evaluate receive/transmit buffering, repeated starts, flow control, reset and stuck-bus recovery, plus compatibility with existing peripherals and MOS/EMOS APIs. Identify scope and fit risks for EMOS and P4.

- RESEARCH-009-004 [x] Compare both options to measured PARLIO and ordinary UART in both directions. Show units, link ceilings, example job times, assumptions, CPU/interrupt cost, availability and failure/recovery tradeoffs. Separate estimates from measurements. Identify which real-job bottlenecks a replacement can address and which it inherits. Where useful, write isolated candidate code and exercise it on the host. Name any assumptions that require physical proof.

- RESEARCH-009-005 [x] Recommend a ranking for bulk SD transfer and control use, with a pin/wiring and firmware migration outline for any credible candidate. Specify the smallest discriminating future hardware tests, bidirectional mixed-size and soak acceptance, fault capture, and rollback. Close the review with traceable evidence and explicit remaining limits.

## Deliverables and completion

The task's findings record must let the Author choose whether to qualify SPI,
I²C, or continue debugging PARLIO. Include a side-by-side table, actor-specific
wire ownership, sources and commit pins, and a concise answer on whether the
previous SPI conflict is fundamental or an implementation/wiring problem.
Retain any prototype source and host test evidence in this task silo.

## Execution result

- Frozen and pushed before execution at `d6ae3f75bc8af341a73a42ec11a101c7c80359ca`.
- The [retained baseline](RESEARCH-009/PARLIO.md) binds production P4, EMOS and
  listener revisions, bidirectional file timings and the different failure
  boundaries in the recent PARLIO receipts.
- The [SPI review](RESEARCH-009/SPI.md) reconstructs the two shared-SD defects
  and the later DMA readiness failure, identifies their tested remedies on
  the WROOM, and specifies the P4 candidate wiring and adoption limits.
- The [I²C review](RESEARCH-009/I2C.md) maps the separate board pins,
  documents existing driver limits and silicon recovery constraints, and
  calculates both-direction ceilings.
- The [SPI block model](RESEARCH-009/candidate/README.md) passed strict host
  C11 compilation and AddressSanitizer/UndefinedBehaviorSanitizer checks for
  all 1,024 size/direction pairs plus admission, count and recovery controls.
- The findings give a staged hardware qualification and rollback plan.
  Actual harness continuity, link timing, target firmware fit, and comparative
  reliability remain unmeasured. This task closes the offline review. No bench
  lease or hardware changes were needed.
