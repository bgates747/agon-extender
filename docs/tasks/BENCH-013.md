# BENCH-013 — Shorten agent deploy–run–collect cycles

## Executive summary

Coordinate existing file-transfer, parallel-transport and test-control tasks so
agents spend less bench time deploying programs, waiting for known completion
and collecting results. Reuse the P4 staging and host tools across transports;
preserve stock MOS/VDP behavior for ordinary application traffic. Rank work by
its effect on complete development cycles, not isolated wire throughput.

**State:** Coordination priorities approved and first tranche authorized,
2026-11-03. The Author directs commit/push, then adoption of the tested faster
download listener. The Author assigns Extender the physical bench and requires
it to retain custody until the Author and Extender decide another project needs
a slot; other agents may continue to reserve through the existing queue.
Completing a subtask does not release this checkout. Changes to a file-service
ABI/carrier architecture remain separate decisions; B13-D02 and B13-D03 are open.

## First tranche result

Priority1 bench adoption is complete: the exact tested faster listener is
installed and readback-verified, rollback is retained,65537-byte paired file
checks pass, and maintained selection/guidance and verified archives are in
place. See [adoption evidence](REMOTE-009/DOWNLOAD-ADOPTION-R01.md). Full paired
production release qualification/version closeout remains separate. Extender
retains the checkout as instructed; priorities2–5 are not started by this result.

## Four traffic quadrants

Directions below are between the mainboard eZ80 running EMOS and the Extender
P4 running the ported VDP and its services. A host upload travels through the
P4 to the mainboard; a host download travels in the opposite direction.

| Workload | Mainboard eZ80 → Extender P4 | Extender P4 → mainboard eZ80 |
|---|---|---|
| Application/control | EMOS routes application VDU commands and rendering requests to the P4 parser. | The P4 supplies input, notifications and replies to the EMOS receiver. |
| Bulk files | The mainboard file utility reads Agon SD; the eZ80 sends file payloads to P4 staging for host downloads and result collection. | The P4 stages host uploads, then sends payloads to the mainboard file utility for Agon SD writes. |

UART and parallel are carrier choices across this table, not four independent
service implementations. Current staged files use the EMOS-owned UART1 path;
parallel direction/capacity support must be established separately. The native
mainboard VDP's UART0 is a different endpoint. Coordination with its UART owner
shares applicable semantics without assuming a common binary ABI or wiring.

## Ownership and reuse

1. [PORT-008](PORT-008.md) owns both parallel directions, byte movement,
   receiver capacity, admission and applicable async transport work. Existing
   forward VDU measurements do not qualify a bulk-file path or reverse bulk.
2. [REMOTE-009](REMOTE-009.md) owns staged fast file jobs and their host client;
   [REMOTE-005](REMOTE-005.md) owns the underlying mainboard file service.
   Preserve their file/session/error contracts while examining a carrier seam.
   The component-owner checkout owns changes to the EMOS utility.
3. [QUAL-006](QUAL-006.md) owns explicit job admission, lifecycle observation
   and correlated completion. Select a bounded development-cycle increment
   there rather than starting its entire qualification migration by implication.
   [BENCH-012](BENCH-012.md) and the central physical registry continue to own
   scheduling; this task creates no second queue or lease authority.
4. EMOS alone owns ordinary VDU routing, admission, committed modes and shared
   eZ80 pins. The P4 owns its matching parser, transport endpoints and staging.
   Applications and host tools receive no supported direct transport bypass.
5. Preserve stock MOS/VDP framing and behavior, and reuse the ported P4 code
   where applicable. File-open caching benefits file I/O; P4 SD/HTTP staging
   does not belong in ordinary VDU calls. Admission, ordering, buffer lifetime
   and readiness/completion semantics are the principal cross-workload overlap.
   Respect the existing [UART/parallel coordination contract](../../../agon-dev-env/cross-agent/parallel_uart_async/contract.md).

Implementation checklists remain in those owning tasks. This document owns only
the bounded priority/dependency decisions and tranche completion assessment;
`TODO.md` remains the single unfinished-work index.

## Proposed sequence

| Priority | Owning work | Development benefit and dependency |
|---:|---|---|
| 1 | REMOTE-009: review and adopt the proven sequential-reader utility | Establish the measured faster download baseline after Author acceptance. No further UART-specific tuning is proposed. Version, deployment and production closeout stay with the owning task; unresolved release work need not block independent offline parallel preparation. |
| 2 | PORT-008 + file-service owners: P4 → eZ80 bulk uploads | Shorten repeated program/asset deployment. Establish the presently missing reverse bulk path and file integration before promising an upload gain. |
| 3 | PORT-008 + file-service owners: eZ80 → P4 bulk downloads | Reuse the existing forward transport where suitable, connecting file payloads to the P4 staging service and measuring actual result retrieval. |
| 4 | QUAL-006: bounded launch/completion/CLI-return improvement | Reduce command sequencing uncertainty and bench occupation during reconciliation. Reuse actual EMOS lifecycle knowledge; keep resident code and RAM costs explicit. |
| 5 | PORT-008/application owners: measured ordinary VDU/control bottlenecks | Optimize only an evidenced development workload. Small VDU transfers may favor UART; file throughput does not justify moving every command or notification to parallel. |

The upload-before-download recommendation reflects repeated agent deployments;
the actual workload mix has not yet established its relative time savings. The
forward download carrier may be cheaper to integrate. Resolve that tradeoff
from retained workload timings and bounded source/capability assessment before
committing to implementation order. Do not spend a new benchmark campaign just
to choose an order if existing evidence is sufficient.

The proposed reuse target is one maintained file-transfer service with a small
carrier boundary, keeping host operations, P4 staging, file semantics and error
handling common where practical. This is not a mandate for a generic framework,
a new resident API, simultaneous carriers or automatic transport fallback.

## Decision register

Present remaining unresolved decisions to the Author one at a time, starting
with B13-D02 when its implementation assessment is ready.
Accepted material architecture follows the project's ADR/architecture workflow;
this draft changes neither accepted contracts nor production selection.

| ID | Decision and recommendation | Alternative, prerequisite and effect | State |
|---|---|---|---|
| B13-D01 | Adopt this bounded objective and proposed priority order; treat deployment uploads as the first parallel file target. | Integrate forward downloads first if retained workload share and lower implementation cost justify it. Requires direction/capacity and development-cycle cost assessment, not a presumed symmetric pipe. Determines which owner prepares the first implementation tranche. | Accepted 2026-11-03 — commit/push and first tranche authorized |
| B13-D02 | Reuse the maintained file service and staging/client machinery through a minimal carrier seam. The completed [reverse assessment](PORT-008/REVERSE-UPLOAD-R01.md) recommends a whole-file P4 PSRAM DMA source and small eZ80 SD-write slices for the first prototype. | Bounded P4 SD-refill buffers save whole-file PSRAM but require a new pause/refill contract. Existing4096-byte admission and non-loop TX limits do not supply whole-file operation; completion and capacity must be explicitly qualified. | Open — concrete carrier choice ready for Author review |
| B13-D03 | Choose one bounded reliable launch/completion improvement under QUAL-006. | Retain current CLI/listener observation temporarily if transport integration yields more immediate benefit. Requires measured orchestration cost and an EMOS resident-size budget; does not authorize the full control-plane migration. | Open — after initial file integration assessment |

## Evidence and validation requirements

1. Use retained [forward transport results](PORT-008/TRANSFER-RATE-COMPARISON-RESULTS.md),
   [staged file results](REMOTE-009/STAGED-RESULTS.md) and
   [sequential download results](REMOTE-009/DOWNLOAD-RESULTS.md) as scoped
   baselines. Do not compare a VDU drain rate directly with SD-to-host delivery.
2. The owning host runner records deployment, readiness/launch, application
   runtime, retrieval, cleanup and total occupied time separately. Compare the
   same representative binaries/assets/results on matched compositions; report
   explicit units, baseline and elapsed reduction. Exclude application runtime
   from transfer savings and state capture/clock limitations.
3. Owning tasks must demonstrate complete payload correctness, explicit
   busy/error outcomes, no uncertain replay and clean CLI/resource handback.
   Keep sender-buffer release, remote receipt and remote execution distinct.
   Report eZ80 CPU occupancy and EMOS flash/RAM costs, not just throughput.
4. No CRC or replacement software checksum enters EMOS–P4 traffic. Host-side
   artifact comparison remains separate. Whole-request admission is the speed
   objective; per-byte acknowledgement or smaller admissions require the
   evidence and review already specified by PORT-008.
5. Before any new API/hardware implementation, the owning task refreshes its
   official documentation/source précis and exact component baselines. Before
   tests or deployment, it follows the operation protocols, physical checkout,
   [test-appliance lifecycle](../procedures/test-appliances.md) and SD layout.
   No autoexec edits, reset-driven tests or occupied-bench access. Drafting this
   coordination task invokes no tests or firmware operations.

## Tranche completion

1. The Author has selected the coordination priorities and owners have recorded
   dependencies and bounded implementation contracts in their existing tasks.
2. The selected parallel upload/download integrations have comparable complete
   development-cycle evidence, or an explicit Author-accepted blocker/deferral;
   UART remains an identified fallback and baseline without silent replay.
3. The selected orchestration increment has evidence of reliable completion and
   handback, or an explicit scoped disposition. Do not close this item merely
   because a runner can type commands successfully.
4. Accepted recurring services/tools/instructions are promoted through their
   owning tasks, with exact versions, evidence and current documentation.
   Unfinished broader transport, rendering and qualification work remains with
   its owners. Record this coordination outcome in the dated log and remove
   its TODO entry when the bounded tranche is closed.
