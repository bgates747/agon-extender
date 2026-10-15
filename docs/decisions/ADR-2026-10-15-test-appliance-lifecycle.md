# Test appliances preserve normal boot and manage video modes

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-15
- Related task: SCROLL-001

The Author selected a Pi Python coordinator for long unattended suites and
individually invocable Agon test appliances. EMOS remains the owner of display
routing and ordinary VDU output. The appliance checks its entry mode, changes
mode only when necessary and restores its entry mode and a visible CLI on
completion, cancellation or handled failure. The Pi runner restores any earlier
mode/route state that it changed before appliance invocation.

Actual mode changes require at least one whole second of monitor settling before
test execution or restoration output that the Author needs to see. This applies
to both mainboard and Extender monitors. The purpose is visible, understandable
test starts: monitor blanking must not make normal execution look like an error.
Interactive instructions provide `VDU 22 n` and the test command separately;
the Pi runner injects the same pause. Double-buffer cleanup must preserve the
entry mode while making CLI output visible.

Test runners, appliances and test-deployment helpers never modify `/autoexec.txt`,
including temporary changes. Reset remains an escape to normal boot and a usable
CLI. A reset interrupts runner dispatch; it never launches or resumes a test.
Preparation does not authorize smoke runs or other test execution when the
Author has reserved invocation.

The [test appliance lifecycle](../procedures/test-appliances.md) is the maintained
operational authority. It replaces the former test-mode-in-autoexec convention,
whose monitor-settling purpose is now explicit in CLI/application pacing.
Acceptance defines the procedure, not qualification of existing runners or
fixtures. Implementation and migration remain in
[SCROLL-001](../tasks/SCROLL-001.md); historical setup and evidence are preserved.
