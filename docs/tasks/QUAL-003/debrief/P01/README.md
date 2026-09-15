# P01 — matched output comparison

## Executive summary

In progress. Archived r43 has been flashed and readback verified after preserving
the installed r44 image. No renderer, MOS or mainboard VDP changes. The first
comparison uses the same r05 software-sprite fixture with production wired-Pi
web output, then no viewer/output, followed by reverse-order repeats if material
or apparently passing. Results are not yet available.

## Execution boundaries

1. Fresh nonce and result filename per run; validate all2400 states, trace
   completions, terminal checks and deterministic state hash.
2. One passive USB capture is opened before controlled reset, with no reopening
   during measured work. Existing recorder dumps only after the terminal fence.
3. Observer runs180seconds. Off controls wait the same duration. No periodic
   HTTP/SD status polling during measured work; collection begins afterward.
   This removes historical host polling from both new conditions equally.
4. Reverse-order repeat criterion: at least1ms difference in enqueue or
   completion p95, or either run appears to pass the existing stock gate. This
   is a diagnostic selection rule, not statistical significance.
5. Original startup is restored after exiting the child autoexec's SD service
   and starting SD directly. Preserve raw evidence and restore neutral input.
6. Historical stock data remains the comparison baseline; no new mainboard
   measurement is implied. Actual task-affinity timing remains unmeasured.

[Provenance](provenance.json) records candidate/input identities. Private bench
controller and rollback evidence live in ignored `agents/p01/`. P01c/d are
conditional; P02 and later work remain unapproved. Golem is excluded.

## Preparation note

The workstation-side asset readback was interrupted cleanly before any test;
the SD client retained its outstanding read request. Verification resumed on
the wired Pi using that request identity. No asset or startup mutation occurred.
This is a preparation-path change, not a performance result or proof that Wi-Fi
caused the delay. Capture is restarted before the first measured run so the
preparation transfer cannot exhaust its bounded collection lifetime.

The1ms reverse-repeat threshold is an agent-selected diagnostic criterion
within the approved material-contrast instruction; it is not an Author-specified
acceptance threshold. Existing stock mean/p95 gates remain unchanged.
