# W9 stock-drain preparation

Contract and prior progress frozen in `1cac8ee`. Implementation follows
[the accepted W9 contract](stock-queue-drain.md) and PORT-003-D013.
Physical deployment and the single measured comparison pass; the
[findings](stock-drain-findings.md) were accepted by the Author. The separate
W9 keyboard observation remains unconfirmed; authorized W10 includes its own
post-run check. The sections below retain the preparation/deployment sequence.

Candidate inputs frozen in `b9d4ff6`; clean build
`uart-excom-console-r08-b2026-09-10-21-23-43Z` passes and is staged with
matching remote hashes. [Build receipt](evidence/stock-drain-local/candidate-build.json)
records the exact images, source changes and unchanged managed dependencies.
Stable P4 identity and analyzer presence were verified without opening P4
serial; the mounted SD fixture hash matches. The capture launcher remains
bound to the successful deployment receipt below. Review is notification-only, not
a new emulator or P4 visual-validation claim.

## Implementation

The P4 executor now drains until empty or suspended. It checks suspension
after each primitive, matching the pinned stock worker. The count-budget
argument and stored value are removed from the production frame interfaces.
Their existing callers and host substitutes use the corrected interface.
No new scheduler, lock, timing cap or tunable option is introduced. Task
placement/priorities, tick handling, common vdp-gl, UART/parser/input/network
code, web assets, EMOS and the benchmark executable remain unchanged.

The independent logical-frame oracle now expects FIFO draining. Its generated
current fixtures were regenerated from that written rule. Historical target
qualification and host evidence were preserved. Old standalone canary callers
received the signature correction solely for source consistency; their old
artifact identities are not selected or rebuilt for this comparison.

## Local validation

1. [Frame/controller regression](evidence/stock-drain-local/frame-regression.yaml):
   12 logical traces, seven retained controller/lifecycle checks and three concurrency
   stress pass with ASan/UBSan. New checks execute 514 queued primitives in one
   opportunity, verify ordered red/blue pixels, and preserve immediate flush
   without another tick. A host-only dequeue barrier and observation of the
   existing suspension wait deterministically request suspension during a
   drain; only the in-flight primitive finishes, later work stays queued and
   resumes in FIFO order. No production test hook was added.
2. [Presentation regression](evidence/stock-drain-local/presentation-regression.yaml):
   19 fixtures and three fixed harnesses pass. The eight-gate mode aggregate
   also passes, including mode facade, retained Teletext, exact VDU lifecycle,
   native renderer and cross-phase regressions. Its generated results are
   archived in the same evidence directory; original phase evidence files
   retain their prior bytes. These are host checks, not P4 timing evidence.
3. Capture r03 records the stock-drain comparison and requires the r08 build,
   image/manifest hashes and verified deployment-record hash before the host
   runner can arm. Existing r01/r02 behavior is retained. Browser-off closure,
   five-second settlement, acquisition mechanics and decoder are unchanged.
   The host explicitly overrides both stale CSV annotations without modifying
   the Agon executable or its output. All 16 capture/result/condition tests
   and six independent frame-fixture tests pass.
4. P4 draft compilation succeeded. The builder correctly declined to freeze
   that exploratory bundle because the aggregate mode runner rewrote generated
   evidence during compilation. Those writes were saved separately and the
   historical files restored. The subsequent clean build from `b9d4ff6` passes; no image from the
   declined bundle is eligible for deployment.
5. Registry/template/source-identity validation passes. The full validator
   still fails the previously recorded r02 hardware `connectivity.yaml` hash;
   both that file and its profile are unchanged from HEAD. This correction
   does not rewrite the held hardware design to conceal that separate issue.

Standing identity approval selects console r08, capture r03 and registry r64.
The r07 rollback bundle remains intact. No physical flash, serial open, reset,
capture, SD write or unmount occurred during these local checks.

## Authorized deployment and benchmark handover

The Author authorized flashing. Deployment `PORT-003-2026-09-10-21-31-49Z`
wrote the exact candidate, independently verified flash readback and observed
its matching startup identity, native USB keyboard readiness, UART at
1,152,000 baud and HTTP service startup. No startup fault was logged. The
[deployment receipt](evidence/stock-drain-local/deployment.json) binds the
image, manifest and original private deployment record to capture r03.
The bounded serial session is closed; no further P4 serial open or reset is
part of the benchmark.

The SD executable, autoexec and all five earlier CSVs retain their recorded
hashes. The card was safely unmounted for the operator. EMOS is unchanged.
The prepared launcher now accepts the verified deployment binding; no timed
capture has started. The operator closes all Extender video clients, runs
the launcher and resets only Agon at its cue. After the result and MOS prompt,
check keyboard usability outside the timed interval and return the SD. No
screenshot is required. Physical workload correctness and timing remain open.

The subsequent returned SD and capture now validate the exact workload and
timing, recorded separately in the linked W9 findings. No preparation inputs
or original capture/CSV records were rewritten during collection.
