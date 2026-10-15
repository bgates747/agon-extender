# Test appliance and suite lifecycle

Tests must be understandable to a person watching either monitor. A video-mode
switch must not hide the beginning of a test or make normal execution look like
an error. Applications should avoid redundant switches, restore their entry
mode, and leave a visible, responsive CLI. Long suites use a Python coordinator
on the Pi. Neither the runner nor its test setup may modify `/autoexec.txt`:
reset must remain an escape to normal boot, without launching or resuming tests.

## Responsibilities and scope

1. The Pi Python runner coordinates explicitly authorized unattended suites:
   it sequences individual tests, paces CLI commands and records outcomes.
2. Each Agon test appliance owns its workload, checks its active video mode,
   manages any mode change it needs, and performs cleanup on return.
3. EMOS owns display routing and ordinary VDU output. The runner and appliance
   use supported EMOS/MOS interfaces for mode queries, selection and routing.
4. An individual test remains independently invocable. Batch execution calls
   those same individual tests rather than a separate benchmark implementation.
5. Setup, mode switching, monitor settling and result retrieval stay outside
   measured rendering intervals. Their time can be recorded separately.

## Mode selection and visible starts

1. The appliance records the actual active mode when invoked. It checks that
   mode against the requested test mode before changing anything.
2. If the mode already matches, the appliance skips the switch. Matching means
   the required mode and buffering behavior, not just equal pixel dimensions.
3. If a switch is needed, the appliance selects the required mode through EMOS,
   verifies that selection succeeded, and allows at least one whole second for
   the monitor to settle before beginning the test.
4. The initial minimum is one second for both mainboard and Extender monitors.
   Experience may establish a longer interval. The pause is required for human
   observability even when the processors can execute the test sooner.
5. The test identifies the case, target display/processor and selected mode
   visibly at its start. A person watching an unattended suite must be able to
   understand what has begun. Mode changes and settling are not test failures.
6. A failed mode selection must not be followed by a test in an unintended mode.
   The appliance reports the failure and performs its normal cleanup.

## Interactive commands

1. The agent provides the MOS CLI command `VDU 22 n`, where n is the required mode,
   then the explicit command that runs the selected test.
2. The Author pastes the mode command into the browser interface, waits at least
   one second after the switch, then pastes the test command. Present these as
   separate command blocks with the pause stated between them. A multiline
   paste alone does not create a delay.
3. If a display route must be selected, provide its explicit EMOS command before
   the mode command. Do not assume Legacy and Extender have the same mode.
4. The appliance still checks the mode on entry. Interactive preselection should
   therefore avoid another switch and another monitor blackout inside the test.
5. The agent does not execute the supplied commands on the Author's behalf when
   the Author has reserved test invocation for the web client.

## Unattended Pi runner

1. The runner injects the same CLI mode-selection command and a minimum one-second
   pause before invoking the test. The pause belongs in Python, not autoexec.
2. Start the pause after the mode has taken effect, using a fresh mode response
   when available. Keyboard delivery or a queued command alone is not proof
   that the monitor has switched. A failed or uncertain selection stops dispatch
   until its state is resolved; do not blindly continue after a timer.
3. Where the required mode is already active, the runner can omit the redundant
   switch. It must still provide a clearly identifiable start for each case.
4. The runner records the actual mode, target, case, invocation, completion and
   elapsed time durably. Process exit or keyboard acceptance alone is not a pass.
5. There is no test autorun or implicit resume on boot. After a reset interrupts
   a run, the Pi runner must stop further dispatch and record the interruption;
   it must not type the next test into the newly booted CLI automatically.
6. Restarting or resuming interrupted execution requires an explicit invocation.
   A retained journal supports diagnosis and deliberate recovery, not automatic
   replay of an uncertain test.

## Appliance cleanup and reset failsafe

1. On completion, cancellation or handled failure, the appliance restores the
   mode it recorded on entry. If that mode is already active, avoid a switch.
2. Cleanup leaves the prompt and subsequent typing visible. Double-buffered
   modes require explicit handling of which buffer receives CLI output and
   which buffer is displayed; a successful mode-number restoration is not
   sufficient if the user sees a frozen screen.
3. Preserve a clear completion or failure indication and the saved result's
   identity. Do not describe an unverified or interrupted test as passed.
4. The runner and appliance must never rewrite `/autoexec.txt`, even temporarily
   with a promise to restore it later. An interrupted process must not leave
   startup dependent on its cleanup running successfully.
5. Reset must boot Agon normally to a usable CLI with its normal startup, and
   must not launch or resume tests. Reset is recovery, not a test launcher.
6. If a crash prevents appliance cleanup, the ordinary reset remains the failsafe.
   Recovery does not itself authorize another test, a replay, or a firmware change.

## Restoration ownership and execution boundaries

1. Nested ownership: an appliance restores the mode present at its own invocation.
   If the Pi runner selected that mode beforehand, the runner owns restoration
   of the earlier pre-suite state. The runner must save the original mode for
   each display it will use, and the original EMOS route, before preselection;
   restore those states when the suite finishes, is cancelled or fails. This
   avoids extra switches between consecutive cases in the same mode.
2. Interactive preselection likewise becomes the appliance's entry mode. It does
   not retain a mode that existed before the Author's VDU command. If a return
   to the earlier CLI mode is wanted, the agent should supply an explicit final
   restoration command using a recorded mode, without guessing its number.
3. Treat mainboard and Extender mode state separately. Query the intended target
   through EMOS, rather than trusting a mode cached from the other route. A test
   that changes both displays must save and restore each display it changes.
4. For an entry mode that is itself double-buffered, preserve that mode while
   arranging supported buffer selection so CLI output is visible. Do not silently
   substitute a different mode. If the required cleanup cannot be made reliable
   for a mode, keep that mode out of ready-to-run suites until the limitation is
   resolved; do not claim a usable CLI merely from a matching mode number.
5. Apply the settling minimum to actual restoration switches as well, before
   presenting output the Author needs to read. The runner must not shorten an
   appliance-owned settling interval or include it in rendering measurements.
6. Preparation is not test invocation. Rendering checks, smoke runs and programs
   that exercise test workloads are still tests, regardless of their short
   duration. When the Author reserves invocation, obtain explicit authorization
   before executing those checks; do not hide them under readiness verification.

## Authority and implementation status

The Author accepted this procedure on 2026-10-15 after reviewing the scratch
agreement. [The decision record](../decisions/ADR-2026-10-15-test-appliance-lifecycle.md)
records the rationale. This procedure governs design, deployment and execution
of new or reused test suites and their individual appliances. It supersedes the
former test-mode-in-autoexec rule; historical evidence retains its original setup.

The older Pi Python rendering runner and the current individual/batch scrolling
fixture exist, but acceptance of this procedure does not qualify them against
these requirements. The scrolling fixture does not yet implement the new mode
lifecycle or integration with the Pi runner. [SCROLL-001](../tasks/SCROLL-001.md)
records its remaining implementation and migration boundary. Review and adapt
historical runners before reuse; do not execute a startup-mutating helper and
repair its consequences afterward.

For operational authorization, staging, monitoring and collection, also follow
[test execution](test-execution.md). Neither this procedure nor its promotion
authorizes tests, startup repair, resets, firmware deployment or a production
release. A separately authorized normal-startup commissioning or repair is an
independent operation; test runners and test-deployment helpers must not perform it.
