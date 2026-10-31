# Test execution protocol

Tests start through an explicit MOS CLI command. Reset and normal startup must
not launch a test. This protocol controls staging, invocation, observation,
collection and restoration; each is a separate execution boundary. Read the
[test appliance lifecycle](test-appliances.md) whenever designing, deploying or
running a suite or individual appliance. It owns mode selection/restoration,
monitor settling and the prohibition on test-driven startup changes.

## TE-01 — Prepare without invoking

1. The agent reads the active task contract, bench constraints, SD layout and
   current machine-local bench record. Confirm Author authorization, bench
   availability, exact firmware/fixture identities and the actual application
   state. Do not assume keyboard-ready means MOS is at the prompt.
   The Author's handoff "bench is yours" confirms a ready, idle bench for the
   agreed work; do not ask them to repeat that confirmation. The agent can
   establish actual command handback through a finite listener/read/EXIT
   exchange. Stop and reconcile only if fresh evidence contradicts readiness.
2. Preserve ordinary startup and any existing fixture configurations. Stage
   identified files in their documented directories and verify their readbacks.
   Prefer an existing fixture; do not alter a frozen executable casually.
3. Test runners, appliances and test-deployment helpers must not modify
   `/autoexec.txt`, even temporarily. Preserve normal startup so a reset returns
   Agon to a usable CLI without launching or resuming a test. Appliances own
   conditional mode switching and cleanup. Interactive commands and Pi runners
   may preselect a mode through `VDU 22 n`, followed by at least one whole second
   of monitor settling before test invocation. Restoration ownership follows
   the linked lifecycle procedure. A separately authorized normal-startup
   commissioning or repair is an independent operation, not runner setup.
4. Prepare a separate MOS command file for a sequential suite. The agent or
   Author invokes it with `EXEC /path/to/suite.txt` at a verified prompt. A
   single test may use explicit `LOAD`/`RUN` commands. The command file must not
   reset/reflash boards or change startup. Any mode selection follows the
   declared mode lifecycle and settling requirement.
5. Inspect the whole host helper and command file. Reject a launch path that
   installs a test autoexec and pulses reset, even if a historical runner did so.
   Resolve startup/configuration side effects before calling it.
6. Preparation does not authorize running a test. Rendering checks and smoke
   programs remain tests regardless of duration. If the Author reserves
   invocation, finish independent preparation and leave every test stopped.

## TE-02 — Invoke and honor the stopping point

1. Establish positive CLI/service handback before sending launch commands. A
   successful listener EXIT or separately observed prompt supplies evidence;
   keyboard acceptance alone does not prove command execution.
2. Record the command file, configuration, output paths and firmware identities.
   Retain prior results rather than overwrite or confuse them with the new run.
   Give a duration estimate only from comparable retained runs, with units and
   calibration limits; it is not an automatic collection/reset deadline.
3. Issue one explicit CLI launch. If the Author says “start then stop,” return
   after submission. Report “invoked, execution unverified” when no observation
   is authorized. Do not poll HTTP, open serial/video, inspect live output files,
   schedule a collector, reset, retry or send input afterward.
4. If the Author permits unrelated work during an unmonitored run, use saved
   evidence, source and offline checks. Do not run reset/admission, USB capture,
   SD transfers or other live bench checks alongside that run.
5. Preserve the bench reservation and unmonitored-run state. Do not claim the
   bench is free merely because the launching host process has exited.

## TE-03 — Collect and restore when authorized

1. Confirm completion through the task's admitted evidence channel before
   transferring results or injecting commands. A missing result is not proof
   the application has stopped. Apply the Author's standing
   [recovery order](../bench-reset.md#standing-recovery-order--author-instruction-2026-10-13)
   during authorized monitored work before requesting operator recovery;
   never automatically replay the uncertain operation.
2. Retrieve and validate durable results against their build, run/configuration,
   workload and completeness contracts. Separate application timing, rendering
   and presentation; preserve informative failures.
3. Restore fixture configurations and the appliance/runner-owned mode and route
   state through admitted interfaces. Verify a visible, responsive CLI,
   including double-buffer cleanup. If inherited startup was already changed,
   report that condition; repair requires a separately authorized operation.
   Reset only if separately needed and covered by the reset protocol.
4. Record terminal state and remaining validation. Do not claim a visual pass,
   input-latency pass or paired speedup from counters alone.
