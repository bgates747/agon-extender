# Capture failure and uninstrumented controls

## Executive summary

Author-directed protocol, accepted 2026-09-20: a failure with capture
instrumentation marks that case; it does not end the suite. The host controller
preserves evidence, recovers the affected processor and continues independent
cases. After the suite, the controller reruns failed cases without capture
instrumentation on the affected endpoint. This separates rendering defects
from possible diagnostic interference without losing remaining coverage.

## Procedure

1. The host controller marks each crash, hang, incomplete acquisition or unstable
capture against its case, endpoint, firmware/build hashes and startup history.
Retain useful serial traces, input hashes and any partial images. Do not count
that case as a passing image comparison or immediately retry it to erase failure.
2. The host controller performs the established recovery/reset and verifies
readiness before the next independent case. Recreate each case's required state
from a fresh start; do not carry potentially corrupted state forward. Continue
other cases and the other endpoint where independent execution is possible.
If recovery cannot restore verified readiness, record the remaining cases as
blocked; do not send commands blindly into an unknown state.
3. After the capture suite, rerun every marked case on its affected endpoint:
mainboard uses the verified official stock VDP release; Extender uses the matching
EDP implementation with the capture routine/instrumentation absent. Merely
omitting a capture request or disconnecting the browser is not equivalent to
removing the routine. Record unavoidable binary/configuration differences.
4. Preserve the same fixture bytes, mode, setup/teardown history, pacing and
completion fences. Omit only capture-specific requests. Each control defines a
bounded observation interval and evidence for completion/responsiveness; collect
ordinary serial panic output without introducing new rendering instrumentation.
5. Report capture and control outcomes separately per case and endpoint:
reproduced without capture, not reproduced in the bounded control, or control
blocked/inconclusive. A negative control neither proves capture caused the fault
nor qualifies pixels that were never captured. Preserve repeat counts and limits.
6. Restore verified normal firmware/startup, release observers and confirm input
and prompt readiness after the campaign. Product repairs remain separate work.

## Applicability and traceability

This governs subsequent capture-suite execution, superseding stop-on-first-
capture-failure and immediate diagnostic-retry rules in older task contracts.
It does not rewrite historical outcomes or override explicit deferred test scope.
The motivating [sprite control](../tasks/QUAL-004/sprite-scroll/stock-control/RESULTS.md)
failed with diagnostic firmware but did not reproduce on one official-stock run;
its startup-history difference remains recorded rather than hidden.
