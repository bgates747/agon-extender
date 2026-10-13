# Test execution protocol

Tests start through an explicit MOS CLI command. Reset and normal startup must
not launch a test. This protocol controls staging, invocation, observation,
collection and restoration; each is a separate execution boundary.

## TE-01 — Prepare without invoking

1. The agent reads the active task contract, bench constraints, SD layout and
   current machine-local bench record. Confirm Author authorization, bench
   availability, exact firmware/fixture identities and the actual application
   state. Do not assume keyboard-ready means MOS is at the prompt.
2. Preserve ordinary startup and any existing fixture configurations. Stage
   identified files in their documented directories and verify their readbacks.
   Prefer an existing fixture; do not alter a frozen executable casually.
3. Keep `/autoexec.txt` limited to the intended startup setup, such as keyboard
   admission and an explicitly selected video mode. Do not put test `LOAD`,
   `RUN`, test `EXEC`, chained benchmarks or test retries there. The existing
   requirement to select fixture modes in autoexec remains: setup the mode
   there, then launch separately after boot. Testing boot autorun itself requires
   a distinct explicit Author request; it is not an ordinary test-launch method.
   Startup must finish with EMOS in Legacy. A task-specific startup that
   temporarily routes mode selection to P4 through ExCom must explicitly
   return to Legacy before startup completes. The later explicit test launch
   owns any ExCom selection required for that test.
4. Prepare a separate MOS command file for a sequential suite. The agent or
   Author invokes it with `EXEC /path/to/suite.txt` at a verified prompt. A
   single test may use explicit `LOAD`/`RUN` commands. The command file must not
   reset/reflash boards or silently change the selected video mode.
5. Inspect the whole host helper and command file. Reject a launch path that
   installs a test autoexec and pulses reset, even if a historical runner did so.
   Resolve startup/configuration side effects before calling it.

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
3. Restore temporary fixture configurations and startup through an admitted
   CLI/listener or an explicitly selected recovery path. Verify the restored
   bytes. Reset only if separately needed and covered by the reset protocol.
4. Record terminal state and remaining validation. Do not claim a visual pass,
   input-latency pass or paired speedup from counters alone.
