# AUDIT-004 — Inventory stock MOS and VDP communication contracts

## State

- Status: Complete — accepted by the Author; frozen audit checkpoint
- Started: 2026-09-07 14:29 EDT
- Finished: 2026-09-07 17:06 EDT
- Task drafted: 2026-09-07

The Author authorized W1–W5 on 2026-09-07. The baseline, communication
inventory, bounded endpoint traces, coverage reconciliation and W5 presentation
are complete. The [review overview](AUDIT-004/README.md) presents the result
and its limits. The Author accepted this bounded audit on 2026-09-07 and
authorized freezing it with a commit. The later Extender comparison has not
been authorized or started.
The present hardware hold remains in effect.

## Intent

Establish a source-backed inventory of how standard MOS and the onboard VDP
communicate, and how applications and external devices participate in those
exchanges. Separate documented contracts, implementation behavior, and unknowns
before using stock behavior to assess Extender interface requirements.

The immediate motivation is to reassess the basis for the present transport
design without assuming either that its four buffers are necessary or that
direct wiring with pull-ups is sufficient. This task's first deliverable is
the stock inventory alone, with no circuit redesign recommendations.

The present hardware remains on hold under [HW-001](HW-001.md),
[SETUP-006](SETUP-006.md), [QUAL-002](QUAL-002.md), and the hardware-dependent
portion of [PORT-008](PORT-008.md). The r02 design work is incomplete, physical
wiring of the full circuit as drawn is incomplete, and the complete circuit
is untested. Earlier partial power-domain observations do not establish a
complete-circuit result.

## Scope

1. Primary: every communication path between stock MOS on the eZ80 and stock
   VDP on the onboard processor, including data, commands, responses,
   unsolicited events, flow control, synchronization, and lifecycle signaling
   where supported by the selected sources.
2. Supporting: application-facing entry points and results that initiate or
   consume those exchanges, including asynchronous delivery and shared state.
   Internal calls are traced as evidence, not inventoried indiscriminately.
3. Secondary: separately list the communication interfaces each stock firmware
   exposes to external devices or operators. Trace these deeply enough to
   identify ownership and dependencies on the primary paths; record any
   unreviewed device-protocol detail explicitly.
4. Include startup, normal operation, alternate operating configurations,
   interruption, reset, timeout, malformed traffic, and recovery to the extent
   that the stock sources define them. Do not infer a recovery guarantee from
   an undocumented absence of handling.
5. Use Agon Light 2 as the initial board context. Record relevant board/version
   dependencies and explicitly bound variants rather than silently extending
   Light 2 conclusions to other Agon machines.
6. Inventory stock facilities even when the current Extender compatibility
   policy excludes them. A stock inventory entry does not add a product
   requirement or reverse an accepted carve-out.

This is a read-only documentation/source audit. It includes no source patches,
new firmware, builds, emulator changes, bench operations, wiring changes,
qualification runs, or automatic resumption of held work. Existing evidence
may be cited with its original scope; source inspection is not a physical test.

## Authority and baseline selection

1. Read relevant official `agon-docs` documentation first. Follow it into the
   official `agon-mos` and `agon-vdp` source where implementation details or
   missing documentation require it. All three checkouts remain read-only.
2. Record exact documentation and firmware commits, tags, build options, board
   configuration, and local modifications before relying on their contents.
   The Author clarified that stock MOS and VDP references must be clean at
   their most recent official tagged releases. Verify those releases against
   official upstream tags, then pin the exact commits for this audit; do not
   silently change an audit's recorded source identity partway through tracing.
   Keep local changes in separate project-owned checkouts. Present any material
   ambiguity or change from an established audit baseline before dependent work.
3. Use existing research, including [AUDIT-001](AUDIT-001.md),
   [AUDIT-003](AUDIT-003.md), and
   [the VDU inventory](SETUP-004/VDU-inventory.md), as discovery aids. Verify
   relevant conclusions against the selected official baseline rather than
   treating inherited Extender assumptions as stock facts.
4. Consult official board schematics and processor/peripheral documentation
   when pin assignments, voltage domains, peripheral behavior, or electrical
   requirements are material. Keep observed board wiring separate from the
   processor's configurable capabilities.
5. Use exact repository-relative source paths, symbols, and commit-qualified
   references in tracked evidence. Keep machine-specific checkout locations
   and private bench details in the existing ignored local records.

## Inventory structure

Assign a stable reference ID to each communication path. Keep physical links
and logical exchanges distinct: several command or event families can share
one link, and the reverse direction may have different ownership and pacing.
Cross-reference shared transports rather than duplicating them as unrelated
wiring. Do not recreate every opcode table when a verified existing inventory
provides the required coverage.

| Field | Required content |
| --- | --- |
| Identity and purpose | Stable path ID, function, and scope/configuration |
| Participants | Initiator, sender, receiver, and response/event consumer |
| Ownership | Processor, software component, and relevant interrupt/task context controlling each action |
| Physical transport | Peripheral, pins, direction, wiring, and electrical assumptions where applicable |
| Logical protocol | Command/event families, framing, payloads, responses, and encoding references |
| Coordination | Flow control, buffering, blocking behavior, acknowledgements, ordering, and timing |
| Application effects | Entry points, delivered results, flags, callbacks, or shared-state effects where applicable |
| Lifecycle | Initialization, idle state, resets, interrupted exchanges, errors, and recovery |
| Evidence | Exact documentation and source references for both endpoints |
| Evidence limits | Documented guarantee, implementation observation, inference, discrepancy, or unresolved question |

Use explicit `not applicable`, `not specified`, or `not yet verified` values
where appropriate; do not leave blanks that imply completeness. Numerical
timing, capacity, throughput, or electrical claims require their own evidence
and conditions. Distinguish configured values from guaranteed limits.

## Work — W1–W5 complete and accepted

1. [x] **W1 — Establish the baseline and bounded research map.** Record the
   selected source identities, relevant official documents, existing research,
   coverage boundary, and baseline ambiguities in a short task-local précis.
   Completed: [baseline and research map](AUDIT-004/baseline-and-research-map.md).
   Stock MOS v3.0.2 and VDP v2.16.0 were verified as the latest official tagged
   releases. Both canonical checkouts are now clean at those tags; pre-existing
   MOS changes were preserved separately. No communication inventory or
   endpoint trace was produced.
2. [x] **W2 — Enumerate the communication paths.** Build the primary MOS/VDP
   link map first, then the supporting application and external-interface
   inventory. Assign stable IDs and identify the source entry points to trace.
   Completed: [communication inventory](AUDIT-004/communication-inventory.md),
   with 11 transport references and 46 path families: 25 primary processor
   exchanges, 11 application/operator boundaries, and 10 external-interface
   families. This established the document/source entry map; W3 now supplies
   detailed traces, reconciled against source/document surfaces by W4.
3. [x] **W3 — Trace both endpoints.** Follow senders through transport and
   receiver handling to responses or observable effects. Inspect relevant
   initialization, buffering, interrupts, pacing, and failure paths. Record
   the distinction between documentation and actual implementation.
   Completed: [communication traces](AUDIT-004/communication-traces.md), with
   a trace location for each W2 family and explicit external-peer, dependency,
   hardware, and timing limits. Authenticated the reached vdp-gl/Arduino UART
   source and selected Light 2 Rev B schematic. This family-level trace does
   not claim exhaustive opcode coverage or physical qualification.
4. [x] **W4 — Check coverage and evidence.** Reconcile the interface map with
   the selected documentation and source entry points. Identify omissions,
   conflicting sources, unverified configurations, and any questions that
   require later measurement. Do not hide gaps behind a completeness claim.
   Completed: [coverage review](AUDIT-004/coverage-review.md), including positive
   documentation/source matrices, configurations, incorporated corrections and
   remaining evidence limits. No additional family was needed beyond the 46
   families and 11 transport references. This is a bounded source review, not
   exhaustive program verification or hardware qualification.
5. [x] **W5 — Present the stock inventory and stop.** Give the Author the
   inventory, coverage statement, and unresolved questions. Do not proceed
   automatically into an Extender comparison or recommendations.
   Completed: [review overview](AUDIT-004/README.md), linking the full inventory,
   traces, coverage statement and remaining evidence questions. This is the
   presentation checkpoint; the Author subsequently accepted the audit below.

## W1 evidence register

| ID | Observation / remaining boundary | Disposition and owner |
| --- | --- | --- |
| `AUDIT-004-E01` | Stock MOS is v3.0.2 at `8336409351ee5314e02801a7b72a4f1bb5282519`. W1 initially found local HEAD `5f67b1ca` plus two unstaged source edits; these were preserved separately and the canonical checkout restored to the verified latest release. | Resolved source selection and reference checkout state. The reviewer must use the pinned clean release and recheck older research that used patched MOS sources during any authorized W2/W3 work. |
| `AUDIT-004-E02` | The selected clean documentation snapshot covers multiple firmware versions. | W3/W4 distinguish selected-source behavior from documentation per family; W4 records concrete discrepancies. The reviewer presenting W5 must retain that distinction; the snapshot does not certify the firmware pair. |
| `AUDIT-004-E03` | W4 authenticated the F92/F93 manual `PS015317-0120` at `ps0153.pdf`, matching the inherited hash; the conflicting `ps0130.pdf` is an L92 manual. The explicit Light 2 Rev B schematic is authenticated but its SHA-256 differs from the older record. | Processor identity resolved; [board evidence](AUDIT-004/trace-hardware-and-dependencies.md) records the reached register semantics and verified schematic path/blob/hash. A bounded search did not recover the older PDF bytes. The W5 reviewer must retain that provenance gap; any later use of the older record requires its owner to recover/authenticate it. No specimen identity or circuit change is inferred. |
| `AUDIT-004-E04` | W1 recorded dependency declarations and historical resolutions without validating local build products. W3 authenticated reached vdp-gl and Arduino UART files against official Git trees. | Resolved for the files explicitly used by W3/W4, as recorded in [dependency evidence](AUDIT-004/trace-hardware-and-dependencies.md). Deeper driver, RTC-library and device behavior remains bounded in each trace; no new build or deployed-image identity is claimed. |

These are research provenance and scope boundaries, not circuit defect findings
or new architecture decisions. No unresolved choice of stock firmware release
blocks the W1 result.

## W2 evidence register

The following were enumeration findings. W3 dispositions now distinguish
verified selected-source behavior from remaining boundaries. They are not
implementation instructions or authorization to fix upstream firmware.

| ID | Enumeration observation | Later verification boundary |
| --- | --- | --- |
| `AUDIT-004-E05` | P018: VDP echo types `0x0A`/`0x0B` have no stock MOS consumer. | Resolved in [primary trace](AUDIT-004/trace-primary-protocol.md): echo defaults off; MOS consumes/ignores unsupported accepted-length types, while larger configured echo chunks can reach its oversize defect. This is not supported stock MOS echo reception. |
| `AUDIT-004-E06` | P010: documentation's packet summary omits the mode byte. | Resolved in [primary trace](AUDIT-004/trace-primary-protocol.md): VDP sends and MOS consumes eight payload bytes, including final mode byte; selected automatic notifications use the same family. |
| `AUDIT-004-E07` | P017: after-send prose misidentifies direction/ownership. | Resolved in [primary trace](AUDIT-004/trace-primary-protocol.md): VDP calls the event after attempting output; it does not confirm MOS receipt. Suppression skips the event; a null or failed output is not distinguished by send_packet. |
| `AUDIT-004-E08` | P016/P020: one-way-flow-control prose is too broad for the selected releases. | Resolved at stock-source boundary: VDP initially requests RTS-only; MOS startup requests CTS+RTS. [Session trace](AUDIT-004/trace-vdp-interfaces.md) records inherited settings and protocol ACKs separately. Third-party utility setup and measured pacing remain unverified. |
| `AUDIT-004-E09` | A001: `mos_getfunction` documentation lists out-of-range status 20. | Resolved in [MOS trace](AUDIT-004/trace-mos-interfaces.md): with MB=0 and flags C=0, an out-of-range index returns A=19 and HL=0 through the public path. No source correction is authorized. |
| `AUDIT-004-E10` | X003: the C-function documentation labels a block count as bytes. | Resolved in [MOS trace](AUDIT-004/trace-mos-interfaces.md): the WORD count is in 512-byte blocks; wrappers and loops retain those units. |
| `AUDIT-004-E11` | Alternate-session/device peers extend beyond the selected pair; W2 also left timing production and board routes unresolved. | Partially resolved: [VDP trace](AUDIT-004/trace-vdp-interfaces.md) and [board evidence](AUDIT-004/trace-hardware-and-dependencies.md) establish GPIO15 VSync to PB1, reached peripheral defaults, and absent built-in GPIO26/27-to-ZDI wiring. External peer implementations, added attachments and untraced processor/framework semantics remain explicit limits. The reviewer must present any material audit expansion before dependent work. |

## W3 source findings and remaining interpretation

The detailed traces retain command-specific discrepancies and failure paths
under their existing path IDs. The additional stable entries below highlight
material findings retained by W4 reconciliation; none starts a repair task.

| ID | Selected-source finding | Disposition and owner |
| --- | --- | --- |
| `AUDIT-004-E12` | T001: MOS accepts known types without exact/minimum payload validation; oversized packets enter discard without storing the new length. The parser has no elapsed-time recovery. | Verified source finding in [primary trace](AUDIT-004/trace-primary-protocol.md). The reviewer must distinguish this stock behavior from the separately preserved fork fix and from a measured failure. Result flags alone do not validate packet completeness. |
| `AUDIT-004-E13` | X003: raw API `0x73` dispatches to the read wrapper, whereas C-function `0x02` and FatFS writes reach the write driver. | Verified dispatch/effect in [MOS trace](AUDIT-004/trace-mos-interfaces.md). The reviewer must retain the distinct API paths; no physical write/read test or firmware patch was performed. |
| `AUDIT-004-E14` | A007/A009/X003: RTC convenience calls discard wait status; refresh-after-unpack also waits despite contrary documentation. Named getters and FatFS timestamp operations can trigger VDP RTC traffic. | Verified source dependencies in [MOS trace](AUDIT-004/trace-mos-interfaces.md). W4 retained these indirect producers and added pathname expansion through code variables to the coverage map. |

W3 also records unchecked/truncated command cases, response exceptions,
unbounded session and I2C waits, output-attempt semantics, reserved/no-op
graphics branches, and maintenance cleanup/peer limits in the corresponding
traces. These bound communication and recovery claims; they do not establish
exhaustive defect coverage or authorize redesign. W4 has reconciled these
findings with the selected documentation/source surfaces.

## W4 findings and unresolved validation scope

W4 reconciled source/document surfaces within the existing IDs, corrected the
owning traces and compact inventory, and resolved processor-manual identity.
The entries below retain material interpretation and measurement questions for
W5. They authorize neither upstream fixes nor a bench campaign.

| ID | W4 observation / remaining question | Disposition and owner |
| --- | --- | --- |
| `AUDIT-004-E15` | T001: MOS statically asserts UART0 RTS during setup and polls CTS before transmit; no receive-occupancy-driven RTS writer was found. | Resolved selected-source/register semantics in the [primary](AUDIT-004/trace-primary-protocol.md) and [hardware](AUDIT-004/trace-hardware-and-dependencies.md) traces. The W5 reviewer must distinguish VDP CTS+RTS configuration from a guarantee of automatic MOS receive backpressure. Actual loss/pacing behavior remains E19. |
| `AUDIT-004-E16` | P004/P017: callbacks use unordered sets; clearing a buffer leaves registration until later missing-buffer handling; same-buffer recursion and tail calls differ from ordinary call restoration. Maintenance packet helpers bypass ordinary before-send callbacks. | Resolved source distinctions in the [command](AUDIT-004/trace-command-stream.md) and [primary](AUDIT-004/trace-primary-protocol.md) traces. W5 must preserve these limits on ordering, lifecycle and output guarantees. Mutation/recursion correctness under execution remains outside the audit. |
| `AUDIT-004-E17` | P013–P017/X004/X005: documentation misaddresses keyboard event variables, mislabels writable event fields, and misstates repeat units/range/rounding. Mouse reset/reply promises exceed selected source behavior. | Reconciled documentation versus source in the [primary](AUDIT-004/trace-primary-protocol.md) and [VDP](AUDIT-004/trace-vdp-interfaces.md) traces. The W5 reviewer must use source-qualified descriptions; cached settings do not prove device behavior. No documentation or firmware change in official references is authorized. |
| `AUDIT-004-E18` | X003: FatFS API `0xA4` calls `f_setlabel`, then falls through to unavailable status 23. | Verified source path in the [MOS trace](AUDIT-004/trace-mos-interfaces.md). The W5 reviewer must distinguish a possible completed storage effect followed by error from a pure unavailable stub. No physical storage test or source fix performed. |
| `AUDIT-004-E19` | Which remaining configuration/measurement gaps matter to the Author's intended use of the inventory? Unverified subjects include alternate builds/compiler ABI, callback mutation/recursion, queue loss/latency and stalled peers, VSync timing across modes, device reconnect, reset/session interruption, UART/I2C/SD failures and physical signals. | W5 reviewer must present the [coverage limits](AUDIT-004/coverage-review.md) alongside E03/E04/E11, without treating configured constants as measured guarantees. The Author owns any later scope expansion; a separately authorized task must own selected experiments, peer baselines and acceptance criteria. No such work starts under W4. |

W4 closes coverage reconciliation for the declared source-entry/family boundary.
It does not close E03's older-byte provenance, E04/E11's deeper dependency and
external-peer limits, or E19's validation scope. W5 has presented these limits;
The Author accepted the audit with these evidence limits retained; the hardware
hold is unchanged.

## W5 presentation and Author review

The Author accepted the stock inventory and bounded source review on
2026-09-07 and requested a commit to freeze this checkpoint. All five work
items are complete; the task is removed from TODO. Acceptance covers the
recorded source identities, communication inventory, traces and coverage
statement with their explicit limits. It does not resolve the retained
unknowns, qualify hardware, adopt Extender requirements or authorize repairs.
The Author deferred discussion of subsequent tasks until after the commit.

The following evidence questions remain limitations of the accepted result,
not unfinished work under this closed audit:

| Evidence entries | What remains unknown | Owner and present disposition |
| --- | --- | --- |
| E04/E11 | Which exact external terminal, transfer, update, debugger and peripheral implementations interoperate with the selected stock pair? What guarantees do the untraced driver/OTA/RTC/debug-hardware layers supply? | Stock-side boundaries are delivered; these peer/lower-layer conclusions are not. The Author owns any expansion of this audit scope. A later authorized task must select exact sources and the required contracts before investigating them. |
| E19 | How do alternate builds, compiler ABI choices, callback mutation/recursion and other runtime combinations behave? | The source review identifies branches and limits; it contains no build/runtime verification. The Author owns any later selection of configurations and acceptance criteria. |
| E19 | What are the actual timing, throughput/loss, stalled-peer, VSync, reconnect, reset/interruption and electrical results on a particular specimen? | No measurement campaign was performed or is authorized by W5. If the Author requests one, its owning task must define the specimen, candidate code, conditions and evidence separately; the existing hardware hold still governs. |
| E03 | Which bytes produced the older schematic hash, and would any conclusion depend on them? | The selected Rev B PDF is authenticated; older bytes remain unrecovered. Retain the discrepancy. Any later owner relying on the older record must authenticate it before reuse. |

These unknowns delimit the result rather than silently becoming follow-on work.
Stock defects and documentation discrepancies recorded among E05–E18 are
observations within the evidence, not outstanding repair instructions. No comparison, hardware
resumption or promotion to normative product documentation is part of this
audit. The subsequent acceptance instruction authorizes the local checkpoint
commit; it does not authorize a push or any new task.

## Deliverables and acceptance

Start with the [W5 review overview](AUDIT-004/README.md). Supporting deliverables
are the [W1 précis](AUDIT-004/baseline-and-research-map.md),
[W2 communication inventory](AUDIT-004/communication-inventory.md), and
[W3 trace index and findings](AUDIT-004/communication-traces.md), which links
the detailed source and board records, and the
[W4 coverage review](AUDIT-004/coverage-review.md). This task file remains the
sole owner of actionable audit work.

The stock inventory is ready for review when every discovered in-scope path
has an identified owner and evidence, or an explicit unresolved entry; both
ends of primary exchanges are traced; shared transports and configuration
dependencies are clear; and the report states its exact coverage and limits.
The Author supplied acceptance on 2026-09-07. If the
accepted inventory becomes recurring reference material, promote it to a
durable role-named documentation location under the
[task-documentation convention](README.md).

After reviewing the inventory, the Author may separately authorize a comparison
that distinguishes stock compatibility obligations, EMOS/P4 responsibilities,
and Extender-specific requirements and their rationale. That later comparison
may challenge buffers, signals, handshakes, and power/reset assumptions. It
must preserve EMOS ownership of routing and transports unless the Author
explicitly changes the architecture through its decision process. Neither
that comparison nor its implementation is authorized by the W1–W5 instructions.

## Firmware bug register cross-reference — 2026-09-20

[FWBUG-008](../firmware-bugs.md#fwbug-008), [FWBUG-009](../firmware-bugs.md#fwbug-009), [FWBUG-010](../firmware-bugs.md#fwbug-010), [FWBUG-011](../firmware-bugs.md#fwbug-011). These stable bug identities supplement the original
finding IDs and evidence. Registration does not authorize repairs or turn
source-only findings into hardware reproductions. Use the same FWBUG ID for
any future dedicated disposal task; current dispositions remain in the register.
