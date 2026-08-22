# CA-2026-08-22-001 — Phase C compatibility-scope review

- Document type: Corrective action
- Status: Resolved — corrected candidate approved; physical qualification pending
- Date opened: 2026-08-22
- Affected task: PORT-003 Phase C
- Affected commit: `8aecb0e1a9efb671db2bff56143b11ab7b69aae5`
- Authoritative work tracker: `docs/tasks/PORT-003.md`

## Trigger

The Author questioned whether PORT-003 Phase C introduced novel code to repair
undesirable upstream behavior, especially a new protocol or application-visible
semantic change, despite the project's primary requirement to port the stock VDP
with complete backward compatibility.

The controlling rule is stricter than “improve behavior while retaining the
API.” Project-authored replacement code is warranted when the ESP32-P4 lacks an
equivalent for retained upstream behavior or when omitting an unneeded upstream
subsystem leaves a required integration hole. An inherited defect is not, by
itself, authority to change strict-compatible behavior.

This document is an audit and containment record, not approval of the affected
implementation and not an ADR superseding an existing decision.

## Controlling compatibility requirement

`SETUP-001` makes full stock-VDP backward compatibility an architectural product
guarantee and requires a port rather than an independent behavior-compatible
rewrite. ADR-0011 permits only P4-required upstream changes or connections for
accepted Extender features. ADR-0013 requires the replacement display backend
to preserve observable ordering, completion, refresh, readback, buffering, and
other retained behavior.

Consequently, delegated implementation authority and approvals of PORT-003
design recommendations did not implicitly waive the compatibility requirement.
No such waiver was requested, described, or accepted.

## Immediate containment

1. Preserve commit `8aecb0e` as the exact review candidate; do not rewrite it
   before the audit has established what should be retained, gated, or removed.
2. Do not advance Phase C into physical qualification, official-facade
   integration, transport integration, or a later implementation phase while
   this corrective action remains open.
3. Do not treat the Phase C written-contract fixtures as stock-behavior proof.
   They independently test the newly written contract, but that contract was
   not independently derived from measured stock behavior in every disputed
   area.
4. Keep corrective work in the authoritative PORT-003 task when execution is
   authorized. This document records findings and the required disposition; it
   is not a second task checklist.

On 2026-08-22 the Author directed the project to restore upstream behavior in
the Extender candidate and separately preserve the proposed improvements for
A/B regression testing and a possible upstream contribution. That research is
tracked by `UPSTREAM-001`; it does not relax the product compatibility rule.

## Scope reviewed

The initial audit covers the production and vendored-source changes committed
for Phase C:

- `vdp/video/extender/display/logical_frame_service.{hpp,cpp}`;
- `vdp/video/extender/display/p4_frame_service.{hpp,cpp}`;
- Phase C changes to `p4_display_controller.{hpp,cpp}` and `plane_storage`;
- the PORT-003-D008 patch to
  `vdp/vendor/vdp-gl/src/displaycontroller.{h,cpp}`; and
- the Phase C canary, host fixtures, generators, evidence, and documentation.

Palette/Copper composition, the official `agon_screen.h` facade, VDU dispatch,
MOS integration, UART, the forward parallel link, networking, and physical
display sinks were explicitly excluded and are absent from the candidate.

## Preliminary findings

### No new wire protocol was introduced

Phase C defines no UART, parallel-GPIO, network, MOS, VDU, EDU, or
application-facing packet format. `FrameNotice` and the latest-notice mailbox
API are in-process C++ interfaces under the Extender-owned display boundary.
The Phase C host harness command language and canary diagnostics are test-only;
they are not product protocols.

No legacy Agon application can presently reach the Phase C candidate through
the stock VDU facade because official facade and transport integration have not
yet occurred. There is therefore no current deployed application-visible
behavior change from this commit.

This does not make every Phase C choice compatible. Some choices would become
observable once connected to the retained facade.

### Change classification

| Change | Preliminary class | Operational effect | Compatibility assessment |
|---|---|---|---|
| Replace physical VGA VSYNC timing with a short `esp_timer` callback and one FreeRTOS owner task | Necessary P4 replacement | Supplies frame edges after the classic ESP32 GPIO/I2S/DMA/VSYNC engine was intentionally excised | Permitted in principle, but cadence, jitter, ordering, and overload behavior still require a stock oracle and P4 qualification |
| Replace VGA framebuffer pointers with P4-owned logical plane identities and constant-time drawing/visible exchange | Necessary P4 replacement | Preserves a drawing plane, visible plane, and frame-edge swap without the excluded VGA storage engine | Intended to preserve stock buffering behavior; not yet proven through official-facade fixtures |
| Maintain a writable 32-bit frame counter from elapsed logical ticks | Necessary P4 replacement with provisional policy | Preserves the stock-visible counter without a physical VGA interrupt | Counter existence and wrap are retained; advancing by all elapsed ticks while rendering one coalesced edge may differ observably under overload |
| Bound primitive execution per logical edge and coalesce accumulated ticks | Novel replacement policy | Prevents backlog from making the service task process every missed edge; the counter may advance by several while one render/publication pass occurs | Potential application-visible timing and callback divergence; not established as stock-compatible |
| Add default-no-op lifecycle hooks and a virtual wait to vendored `displaycontroller` | P4 integration seam | Exposes private common queue lifecycle to the P4 subclass while leaving existing non-P4 controllers on default behavior | The seam may be necessary because the old physical executor was removed, but its exact surface was not required by a stock protocol and must remain minimal |
| Define P4 completion by submitted/started/completed sequences rather than stock queue-depth polling | Behavioral correction embedded in a replacement | A dequeued primitive remains incomplete until execution and Phase C publication finish; waits can return later than stock | Probable Prime Directive conflict unless stock evidence establishes equivalent observable behavior or the stronger rule is isolated outside strict compatibility |
| Defer `SwapBuffers` submitter notification until publication/completion | Behavioral correction embedded in a replacement | The waiting caller resumes after Phase C publication rather than immediately after the logical pointer/identity swap | Potentially application-visible ordering change; strict compatibility has not been demonstrated |
| Drain/cancel the trailing `Refresh` produced by upstream disable ordering | New lifecycle workaround | Prevents stale queued work when configuring, stopping, or restarting the P4 frame service | May be required to close a lifecycle hole created by the replacement executor, but it changes whether inherited queued work executes and needs explicit compatibility review |
| Publish fixed-capacity latest-generation metadata mailboxes with drop counters | Extender-owned output infrastructure | Future sinks poll independently; a slow sink loses presentation notices but cannot stall logical rendering | Not a wire protocol and not currently application-visible. Acceptable only as a downstream sink mechanism that cannot alter strict stock behavior |
| Replace the pre-candidate direct consumer-callback design with polling mailboxes | Pre-commit correction to project-owned code | Removes any opportunity for a slow callback to block the frame-service task | The rejected callback interface was never committed. The mailbox interface is still novel and provisional, but this change did not patch a stock-firmware flaw |
| Canary line commands, host trace fixtures, stress harnesses, and diagnostic identity strings | Test/qualification infrastructure | Drives and observes the candidate without the official VDP facade | Not product behavior or a product wire contract |

### Exact area of highest concern

The D008 recommendation and Phase C documentation state that queue-depth
polling is inadequate and that leaving it unchanged “is not an option.” That
was too strong. It omitted a relevant alternative: strict compatibility may
require reproducing an inherited timing defect or otherwise preserving its
observable consequences, while a non-strict profile may opt into corrected
semantics.

The vendored patch leaves non-P4 controller defaults unchanged, but the P4
override deliberately changes when completion waits and swap submitters are
released. Phase C then tests the stronger project-authored contract rather than
first proving the stock contract. This is the clearest potential technical
departure and the clearest procedural defect in the approval process.

## Effect on system operation if integrated unchanged

The current canary compiles but has neither the official VDU facade nor a
physical sink, so the following are prospective effects rather than observed
legacy-application failures:

1. A call that waits for queued drawing may block until actual execution and
   Phase C publication where stock code may return as soon as the queue is
   empty, including while an item is already executing.
2. A double-buffer swap submitter may resume later than under stock code because
   Phase C places publication before completion notification.
3. If the service misses multiple nominal frame periods, the compatibility
   frame counter advances by the elapsed count while rendering and publishing
   only the newest serviced edge. Frame-sensitive software could distinguish
   this from one execution opportunity per physical stock frame.
4. Stop or reconfiguration may cancel queued payloads and a trailing Refresh
   instead of reproducing stock queue processing exactly.
5. Future output consumers may drop intermediate presentation generations.
   This is intended to affect only output delivery; it becomes incompatible if
   consumer state can alter VDP completion, frame count, callback order, or
   logical framebuffer behavior.

There is no evidence in the committed candidate of changed VDU bytes, MOS
sysvars, response packets, UART framing, parallel framing, or network framing.

## Approval assessment

The Author approved the high-level non-blocking latest-generation consumer
behavior (`PORT-003-D006`), later accepted the D008 vendored seam, and delegated
implementation review and check-in. The exact initial callback API and its
mailbox replacement were not individually presented for approval.

Those approvals did **not** override the Prime Directive:

- the compatibility guarantee remained an explicit controlling requirement;
- no recommendation disclosed that strict mode might intentionally differ from
  stock queue-completion or swap-notification timing;
- no compatibility waiver was requested; and
- ADR-0015 itself says strict compatibility and exact callback ordering remain
  claims to qualify.

The preliminary determination is therefore:

- **Confirmed process nonconformance:** the Agent treated a stronger completion
  model as mandatory and obtained approval without presenting faithful
  reproduction of inherited behavior as an alternative.
- **Potential technical nonconformance:** the P4 completion, swap-notification,
  tick-coalescing, and teardown semantics may differ from application-visible
  stock behavior once integrated.
- **No present wire-protocol nonconformance:** Phase C introduced no product
  wire protocol.
- **No present application impact:** the candidate has not reached official
  facade integration or physical qualification.

## Required disposition before Phase C resumes

The PORT-003 tracker must eventually authorize and record a bounded corrective
pass that:

1. derives stock queue, wait, swap, frame-counter, overload, and lifecycle
   behavior from the pristine tagged implementation and, where source is
   ambiguous, from stock-target fixtures;
2. separates code strictly necessary to replace the removed VGA executor from
   optional robustness or performance improvements;
3. identifies which Phase C semantics must be literal in strict compatibility
   and which may exist only in an explicitly non-strict profile;
4. reviews every D008 vendored-source change and removes, narrows, relocates,
   or mode-gates anything not necessary for the strict port;
5. keeps any sink mailbox wholly downstream of logical stock behavior and
   postpones interface freeze until an actual sink demonstrates the minimum
   required contract;
6. amends or supersedes the affected portions of ADR-0015 and the PORT-003
   decision register after the Author reviews the evidence; and
7. regenerates tests from the corrected compatibility contract before target
   or physical qualification continues.

## Initial audit conclusion

The Phase C candidate is not evidence that the Prime Directive has already
been violated in a running system: it is neither facade-integrated nor deployed,
and it contains no new wire protocol. It does, however, encode several
project-authored behavioral policies that have not been shown to reproduce
stock behavior. One of them was expressly justified as correcting an inherited
queue-completion flaw, which is outside the Author's clarified scope unless it
is unavoidable replacement machinery or explicitly confined to a non-strict
profile.

The candidate therefore had to remain frozen and unqualified while those
semantics were audited. The Author's prior approval remained valid only for work
consistent with the pre-existing compatibility requirement; it is not a waiver
of that requirement.

## Corrective implementation outcome

The Author directed implementation on 2026-08-22. The corrected worktree now:

1. restores both modified vdp-gl common-controller files byte-for-byte to the
   pinned `all-the-plots` release;
2. removes P4 explicit completion sequences, completion-wait override,
   notification deferral, queue cancellation, and trailing-`Refresh` cleanup;
3. uses the unchanged upstream task-context dequeue, primitive executor,
   queue-depth wait, immediate post-swap notification, background drain, and
   dynamic-payload behavior;
4. services every accumulated timer tick as a distinct logical frame edge
   rather than coalescing several ticks into one renderer pass;
5. retains fixed-capacity presentation mailboxes only as downstream
   Extender-owned sink infrastructure; and
6. preserves the rejected improvements in commit `8aecb0e` and the prominent
   `UPSTREAM-001` A/B regression task.

Corrected host, retained-controller, stress, provenance, dependency, and P4
compile/link checks pass. No firmware was deployed and no physical behavior is
claimed. The prior r01 canary and qualification-procedure identities describe
the superseded candidate and cannot identify the corrected source. The Author
approved `port-003-frame-service-canary-r02`,
`p4-frame-service-qualification-r02`, and artifact registry r07 for the
corrected source. Physical qualification still requires their clean committed
and pushed checkpoint.
