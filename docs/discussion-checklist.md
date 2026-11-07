# Temporary project discussion checklist

Seven topics remain to discuss following the November 6 status update. These
checkboxes track our conversation, not implementation authorization or test
completion. `TODO.md` and the owning task documents remain the work authorities.

Keep the numbering stable. Check an item only after we discuss it, and record
the outcome beside it. Carry any agreed work into its owning task. Retire this
temporary agenda when all seven topics are covered.

1. [ ] **Extender parallel transport.** Review the passing VALID-filter
   candidate, remaining reliability checks and the particular Wolf operation
   that should use eight-bit parallel. The goal remains blocked on that last
   choice. [Task and evidence](tasks/PARALLEL-001.md). We discussed the fixed
   hardware VALID filter, retained strict checks, absence of automatic production
   retransmission, and lack of a suppressed-pulse counter. Smith now requests a
   deterministic mixed UART1/parallel CRC accuracy appliance with UART1 repeats,
   five failed attempts and SD logs: [design](testing/communications-accuracy-design.md)
   and [task](tasks/COMMS-001.md), prepared before coding.

2. [ ] **MechAgon.** Discuss the successful 663-frame live parallel case and
   what it means for the application's next steps, including whether to retain
   its working UART baseline for now. A later outline UART watch froze on a
   decision overrun and required reset; discuss pacing and native exit behaviour.
   [Live result](tasks/PARALLEL-001/LIVE-RESULT-R01.md).

3. [ ] **Wolf.** Discuss the matched draw-time improvement from 68.32 to
   37.01 ms, possible adoption, and the remaining gap to 30 FPS gameplay.
   Completed fixture throughput was 24.69 FPS; this was not a parallel test.
   [Wolf result](../../Wolf3dOrig/agonport/doc/tasks/WOLF-PERF-005/PHYSICAL67-RESULT.md).
   Wolf's separately selected `-Os` versus `-O2` comparison passes its matched
   cohort: mean draw36.79→32.44ms,11.84% less time; completed fixture27.84FPS,
   still below30Hz. [Result](../../Wolf3dOrig/agonport/doc/tasks/WOLF-PERF-006/PHYSICAL69-RESULT.md).
   Exact incoming image is restored; lease69 was subsequently released for the
   selected communications benchmark. Consult current custody before access.

4. [ ] **ESP8266 and Console8.** Review the working connection utility and the
   temporary separate-UART P4 development adapter: available header pins,
   wiring, software selection and implementation priority. The adapter plan is
   frozen; implementation and wiring have not started.
   [Connection utility](network-startup.md), [adapter task](tasks/NET-008.md).

5. [ ] **UART asynchronous driver.** Discuss the corrected Console8 fixture
   rerun, UART's application-owned vanilla driver, and Extender's separate EMOS
   adaptation. No resident asynchronous engine is selected.
   [UART-owned task](../../agon-mos/docs/tasks/U1-001/README.md).

6. [ ] **VDPlet and shared development machines.** Review outstanding owner
   dependencies, priorities and compiler/bench scheduling. Oryx's manager
   reports it down for the November 7 unattended period; normal Pi compilation
   and fresh physical bench checkout continue. Availability is time-sensitive.

7. [ ] **Olimex bench.** Review the retained working firmware and choose the
   next reservation. Wolf 67 was cleanly released and the registry was empty
   when this agenda was created; consult the live registry before any access.
   [Central reservation procedure](../../agon-dev-env/cross-agent/olimex-bench/README.md).

## Discussion outcomes

November 6: the parallel discussion selected the mixed-carrier accuracy design
above. Filter-enabled state cannot establish that glitches are still occurring;
  actual rejection observability remains a source question. No fixture code or
  new physical test has begun. The wider first agenda item remains open, including
  the Wolf endpoint choice.

Smith clarified that previously observed communication failures, with severity
and causes unresolved, are the main reason for the accuracy fixture. His earlier
approximately one-to-two-hour uninterrupted UART match explains why he suspected
communications in the later freeze. That freeze is additional motivation, not
the sole basis for the investigation or a proven transport diagnosis.

Smith also clarifies that faster MOS↔VDP communication is his primary project
motivation; a faster renderer is a side benefit. The
[matched UART1/parallel performance task](tasks/COMMS-002.md) and
[separate design](testing/communications-performance-design.md) retain this
objective. They are complementary to the accuracy appliance, with independent
programs, invocations, logs and conclusions.

Both designs were committed/pushed before implementation. The first independent
source tranche now passes24 Python checks, separate C++ sanitizer suites and two
stopped eZ80 engine links. See the linked task results; hardware adapters and
physical qualification remain. No tests were run on Wolf's held bench.


The selected forward performance tranche now has [physical results](tasks/COMMS-002/PHYSICAL-R01-RESULT.md):
8192-byte parallel command-stream rate3.371×UART1,4096-byte3.202×; UART wins256.
Same diagnostic360MHzP4 for botharms, current240MHzUARTpair restored.4097 remains
unqualified after USB acquisition loss. This is a communication result separate
from gameFPS, CPUheadroom and COMMS001 accuracy/endurance. Discuss the scope and
remaining application-matched/reliability work; no agenda checkbox closes yet.


November 7 carrier disposition: Smith retains MechAgon UART1 until further
notice after joint small-batch parallel performance discussion with Extender.
The large-buffer speedup does not authorize application migration. Results and
this explicit decision are relayed to MechAgon; independent accuracy/performance
work remains separate. This records a disposition without closing the wider
parallel/Wolf endpoint and reliability discussion.

November 7 UART follow-up: the application-owned EMOS adaptation is implemented,
but overlapping MechAgon runs reported receive overrun twice; its cause remains
unresolved. A later serialized-I/O control completed1078 matching frames and
3332 accepted replies with zero reported UART faults, then closed cleanly.
Host frame-send cadence was12.675Hz, below30Hz. Discuss that correctness/rate
tradeoff and the separately prepared lightweight observer and paired576000
source control; neither is an established cause/fix or production selection.
Exact incoming EMOS was restored and independently read back after the case.
[Current receive investigation](tasks/NET-004/EMOS-ASYNC-RX-DIAGNOSTIC-R01.md),
[paired baud control](tasks/NET-004/UART1-BAUD-CONTROL-R01.md).
