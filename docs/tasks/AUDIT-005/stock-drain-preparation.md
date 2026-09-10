# W9 stock-drain preparation

Contract and prior progress frozen in `1cac8ee`. Implementation follows
[the accepted W9 contract](stock-queue-drain.md) and PORT-003-D013.
Physical deployment and the measured comparison remain pending.

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
   historical files restored. A clean, committed candidate build is required
   next; no image from that declined bundle is eligible for deployment.
5. Registry/template/source-identity validation passes. The full validator
   still fails the previously recorded r02 hardware `connectivity.yaml` hash;
   both that file and its profile are unchanged from HEAD. This correction
   does not rewrite the held hardware design to conceal that separate issue.

Standing identity approval selects console r08, capture r03 and registry r64.
The r07 rollback bundle remains intact. No physical flash, serial open, reset,
capture, SD write or unmount occurred during these local checks.
