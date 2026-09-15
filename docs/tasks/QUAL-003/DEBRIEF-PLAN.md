# Overnight performance debrief — review contract

## Executive summary

Author-directed on 2026-09-15: audit the completed overnight work, compare
mainboard VDP and Extender graphics performance in milliseconds and applicable
frame rates, research official documentation, and deliver a focused next-action
plan with hardware voice notification. This is a documentation/research goal,
not authorization to resume the paused performance experiments.

QUAL-003 remains the owning task; TODO.md remains the sole queue. Preserve
experimental code, prior evidence and the bench. No firmware changes, new
benchmarks, emulator changes or experimental pushes during this debrief.

1. [ ] D01: Inventory current identities and evidence; classify valid, invalid,
   historical, instrumented and non-comparable results. Include Nurples,
   current non-Golem Rally and informative bespoke graphics/transport fixtures.
2. [ ] D02: Recompute comparative tables from retained machine results. Separate
   per-operation/batch rendering, queue completion, paced game cycles, uploads,
   snapshots, socket sends and browser delivery. State baseline, counts,
   quantization, instrumentation and percentage convention.
3. [ ] D03: Research pinned official Agon/FabGL and Espressif documentation and
   source for scheduling, task priorities/affinity, UART buffering/flow control,
   framebuffer memory and output behavior. Distinguish cause from hypothesis.
4. [ ] D04: Write the full debrief, review contradictions and evidence gaps,
   then append ranked first investigations to its executive summary. Put the
   granular proposed actions and decision gates in this task's review plan;
   do not execute them before review.
5. [ ] D05: Check calculations/references, commit documentation in discrete
   local steps, notify through the accepted hardware voice path and stop.

Deliverable: `OVERNIGHT-DEBRIEF.md` beside this contract, with reproducible
derived data where useful. Completion means the report and proposed plan are
ready for Author review, not that Nurples parity has been achieved. Report any
unavailable measurement explicitly instead of manufacturing a game FPS or a
single-operation cost from a mixed scene. Human acceptance remains separate.
