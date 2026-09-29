# AUDIT-010 A10-05a — Source lineage and functional-duplication reconciliation

## Executive summary

This current-source reconciliation separates the eleven A10-05 conclusions and
seven applicable firmware-bug inputs into inherited upstream behavior,
upstream code adapted for the P4, and project-new Extender behavior. It also
checks project-new conclusions against selected upstream facilities and checks
the project-owned closure for materially equivalent implementations. No Git
history, executable change, build, target run or hardware operation was used.

The result changes how A10-06 must assemble findings:

`A10-LS01` — `A10-LIN01` mode replacement crosses two ownership boundaries.
The old-mode and mode-1 fallback, destructive base allocation and unchecked
upstream allocations are inherited; the P4 detach/destroy/attach sequence and
its memory-pool experiment are local adaptations. They require separate repair
clauses even if one final finding describes the complete failed transaction.

`A10-LS02` — `A10-LIN06`, `A10-LIN07`, `A10-LIN11`, `A10-LIN14` through
`A10-LIN16`, and `A10-LIN18` are unchanged inherited defects or candidates.
An Extender-local fix may be necessary, but A10-06 must not describe their
origin as new P4 functionality.

`A10-LS03` — `A10-LIN02` through `A10-LIN05`, `A10-LIN09`, `A10-LIN10` and
`A10-LIN13` are project-new. The selected upstream supplies component
primitives but not those product policies or services. `A10-LIN13` is the
important exception: official VDP already has the complete updater command
consumer, although its ESP32 OTA action cannot execute unchanged on the P4.

`A10-LS04` — The selected stock-shaped P4 display path and the excluded
nonrelease P4 display path are two materially parallel controller/renderer
families. The profile prevents simultaneous runtime ownership, but fixes can
silently diverge. The selected stock-shaped path is the current product owner;
the nonrelease family may remain only as bounded qualification evidence until
its useful tests are extracted and the backend decision is closed.

`A10-LS05` — The tree contains smaller duplicate families in modeline
parsing/mode transactions, numeric conversion, ZDI access, CRC32, path
validation, USB HID acquisition, wire-header copies, and test helpers. Some
are defects or consolidation candidates; others are intentional
target-specific copies whose exact-equivalence tests are their accepted
synchronization mechanism.

This document does not authorize any consolidation or repair. A10-06 must give
each retained finding the lineage and duplicate disposition recorded here.

## Boundary and method

`A10-LM01` — The exhaustive product identities remain Extender P4 source
`755d6f37d332ba95b09519f86b24d352ebb03660`, host/test source `b75aae35`,
EMOS v0.1.23 source `21a9ba27f1f346473d767c2c3053ee18e8911335`, and
AgonDev integration `90034c23`. Official VDP v2.16.0 at `c7ac293d` and
official MOS v3.0.2 at `83364093` are read-only references. The bundled vdp-gl
reference is the selected official dependency at `ac2dd598`. Exact identities
and worktree boundaries remain in [IDENTITIES.md](IDENTITIES.md).

`A10-LM02` — Comparisons used tracked current files and the pinned detached EMOS
tree at `agents/audit010/emos-baseline`. The ordinary `../agon-emos` checkout
was not used because it is not the frozen source and contains later user work.
No reference or component-owner worktree was modified.

`A10-LM03` — Relevant local functions were compared directly with the selected
official VDP/MOS and bundled vdp-gl implementations. The project-owned closure
was then searched by symbol, normalized C/C++ and Python function body, and
whole-file SHA-256. The result is a semantic review: exact matches find only a
subset of duplicates, while similar names alone do not establish equivalent
contracts.

`A10-LM04` — “Upstream-unchanged” means the behavior relevant to the conclusion
is unchanged, even if an include, guard or unrelated function in the same file
differs. “Upstream-ported/adapted” means the P4 path copies or modifies an
upstream function or algorithm. “Project-new” means upstream supplies no
equivalent product function, even when ESP-IDF or Arduino supplies lower-level
primitives used to build it.

`A10-LM05` — No A10-H01 through A10-H07 trigger was needed. No Git history was
inspected.

## Conclusion and firmware-bug lineage

| Lineage ID | Input | Classification | Exact origin boundary | Eventual repair owner and A10-06 rule |
|---|---|---|---|---|
| `A10-LIN01` | `A10-MR01` mode replacement/allocation | **Mixed:** upstream-unchanged base lifecycle plus upstream-ported/adapted P4 coordination | Official `VDUStreamProcessor::vdu_mode` retains requested/current/mode-1 fallback. Bundled `VGABaseController::setResolution` still calls `end()` before replacement allocation; base viewport-pool/table checks and paletted-controller DMA-row checks are inherited. Local `agon_screen.h::changeResolution` adds P4 worker join, Canvas/mouse reset, controller destroy/recreate, clock configuration, service attach and delayed mode publication. Local `VGAPalettedController::allocateViewPort` adds PSRAM/internal-pool selection and retry policy. | The local product owns a transactional P4 mode seam. A10-06 must separate inherited allocator/fallback hazards from P4-introduced teardown and attach hazards; a local repair must not be presented as proof that upstream behavior is repaired generally. |
| `A10-LIN02` | `A10-MR02` mandatory browser snapshot resources | **Project-new** | `PresentationSnapshotPool`, `StockP4Service` and `WiredNetworkService` add P4 snapshot leases and browser codec scratch. Official VDP exposes synchronous screen reads but no immutable generation/lease pool, browser worker or maximum-size codec lifetime policy. | Extender P4 display/browser integration owns the resource policy. Reuse the existing snapshot abstraction; do not add a second snapshot owner. |
| `A10-LIN03` | `A10-MR03` partial WebDAV startup | **Project-new** | `storage/webdav/runtime.cpp` composes raw sockets and FreeRTOS tasks into a new WebDAV/admitted-application service. ESP-IDF supplies socket/task primitives, not this acceptor/worker transaction. | Extender WebDAV runtime owns start/rollback/readiness. |
| `A10-LIN04` | `A10-MR04` global socket overcommit | **Project-new integration policy** | ESP-IDF supplies per-server configuration and internal socket behavior. The independent limits in Extender video HTTP, local-SD HTTP and WebDAV create the product-wide contradiction; no selected upstream component owns an application-wide service budget. | Extender boot/network composition must own one declared socket budget. Preserve separate protocol services; consolidate capacity ownership, not the services themselves. |
| `A10-LIN05` | `A10-MR05` accumulated console profile | **Project-new** | `vdp/build/p4-profiles.json` and the selected definitions are Extender build policy. No upstream product profile combines these diagnostics. | The Extender native build authority owns definition classification and a minimal product-development profile. |
| `A10-LIN06` | `A10-MR06` mutable font metadata/lifetime | **Upstream-unchanged** | Relevant `agon_fonts.h::{createFontFromBuffer,setFontInfo,getCharPtr}` and context glyph sizing remain the official VDP implementation; the local material difference is include selection. | An Extender-local safety repair must be isolated as an upstream correction and accompanied by upstream-compatible font tests. Upstream publication is a separate decision. |
| `A10-LIN07` | `A10-MR07` numeric undefined behavior | **Upstream-unchanged** | Selected `video/types.h` is identical to official VDP for `convertFloatToValue` and related bit conversion. The local `encodeFixed` helper covers only one buffered path and does not replace the inherited helpers. | The VDP compatibility layer owns one validated conversion seam; A10-06 must distinguish repairing inherited helpers from removing the partial local duplicate. |
| `A10-LIN08` | `A10-MR08` P4 scanout-effects proof gap | **Upstream-ported/adapted; no demonstrated defect** | `stock_scanline.cpp` selects portable ISR row bodies and calls inherited `decorateScanLinePixels`; `stock_render_utils.cpp` retains selected upstream FabGL bodies. The P4 task, row publication and snapshot boundary are local adaptations. Retained span hashes in PORT-003 identify copied source. | Extender owns dynamic P4 proof because the physical executor changed. Do not rewrite inherited sprite/Copper decoration without a failing discriminating scene. |
| `A10-LIN09` | `A10-MR09` browser test callback oracle | **Project-new** | The Playwright browser layout harness has no official VDP/MOS equivalent. | Extender test infrastructure owns the callback lifetime and assertion repair. |
| `A10-LIN10` | `A10-MR10` stale maintained build command | **Project-new** | The guide and native/historical build selection are Extender authorities. | Extender documentation owns the correction; no executable reuse question applies. |
| `A10-LIN11` | `A10-MR11` unreachable filled arc/sector edge | **Upstream-unchanged** | The relevant `displaycontroller.h` branch and impossible `!hasLeftEdge` test are unchanged from selected vdp-gl. | Retain upstream provenance and first establish visual consequence with the bounded host matrix. A local correction must be isolated and compatibility-tested. |
| `A10-LIN12` | `FWBUG-001` palette iterator invalidation | **Upstream-ported/adapted file; inherited defect body** | The local `VGAPalettedController::deletePalette` adds a project guard, but the erase-then-advance body is the selected vdp-gl implementation. | Existing FWBUG ownership remains authoritative. Do not duplicate its identity or attribute the iterator defect to the guard/P4 port. |
| `A10-LIN13` | `FWBUG-006` unavailable updater handler | **Project-new defective adapter with an upstream equivalent** | `unavailable_maintenance_adapter.hpp::vdu_sys_updater` is an empty P4 substitute. Official VDP's updater handler completely consumes selector/payload and performs ESP32 OTA actions. The OTA backend is not valid for the P4, but its command grammar and consumption state machine are reusable. | The P4 unavailable-subsystem adapter owns a consume-and-report implementation derived from the official grammar. Do not invent a second grammar or port the incompatible OTA action. |
| `A10-LIN14` | `FWBUG-007` primitive completion/swap hazards | **Upstream-unchanged retained candidate** | The relevant queue, primitive-completion and swap behavior remains in selected vdp-gl. P4 locking/execution adapters surround it but do not establish or repair the candidate. | Preserve the existing FWBUG/UPSTREAM-001 identity and bounded applicability test. No blanket port defect or fix is established. |
| `A10-LIN15` | `FWBUG-008` raw SD write dispatch | **Upstream-unchanged** | Pinned EMOS `mos_api.asm::sd_api_writeblocks` retains official MOS v3.0.2's call to the read routine. Extender gateway additions are outside the defect span. | Existing mos-tests/firmware-bug ownership remains authoritative; do not create an Extender-specific duplicate finding. |
| `A10-LIN16` | `FWBUG-009` volume-label fallthrough | **Upstream-unchanged** | Pinned EMOS retains official MOS v3.0.2's missing return after `_f_setlabel`. Extender gateway additions are outside the defect span. | Existing mos-tests/firmware-bug ownership remains authoritative. |
| `A10-LIN17` | `FWBUG-010` short UART reply dispatch | **Upstream-ported/adapted receiver; inherited defect** | EMOS `vdp_protocol.asm` adds project routing/private-graphics behavior and fixes oversized-length discard. It retains official MOS's missing general per-reply minimum-length validation; the private graphics-result check is not a general repair. | EMOS owns the adapted receiver, but A10-06 must state that the missing validation is inherited and reuse the existing FWBUG trigger. |
| `A10-LIN18` | `FWBUG-012` queued operand/bitmap/sprite lifetime | **Upstream-unchanged behavior in the selected path** | The selected vdp-gl drawing queue and VDP bitmap/sprite cleanup retain the referenced lifetime behavior. Native P4 guards serialize access but do not retain destroyed operands. | Existing FWBUG/PORT-003 D012 ownership remains authoritative. Keep source repair and current-build trigger validation separate. |

## Closely ported/adapted comparison results

`A10-PA01` — `vdp/video/vdu.h` differs materially from official VDP only in a
mouse-controller binding outside `vdu_mode`; the requested/current/mode-1
fallback under review is the upstream function. `agon_screen.h`, by contrast,
is the P4 replacement coordinator. A10-06 must not use the phrase “mode-switch
bug” without naming which actor destroys or allocates each object.

`A10-PA02` — `VGABaseController::allocateViewPort` retains upstream behavior,
including progressive height reduction and unchecked allocation results. The
selected local `VGAPalettedController::allocateViewPort` wraps that allocator
with P4 memory-capability selection and an internal-to-PSRAM retry. The retry
discards a shortened internal attempt before republishing rows, but it does not
make the lower-level allocator transactional or add checks for the inherited
DMA-row allocations.

`A10-PA03` — `VGAPalettedController::deletePalette` has a project lock guard
around the inherited body. The guard does not cause or cure `FWBUG-001`.

`A10-PA04` — `stock_scanline.cpp` is a selected port of portable upstream scan
row composition, while `stock_render_utils.cpp` intentionally retains upstream
FabGL utility bodies behind P4 guards. Their local responsibility is executor,
locking and publication, not a second drawing contract.

`A10-PA05` — Pinned EMOS `mos_api.asm` adds Extender gateway entries outside the
raw-write and label spans. Pinned `vdp_protocol.asm` changes routing and private
result handling, but the general known-reply minimum-length omission remains in
the upstream-derived dispatch. These are mixed files, not evidence that the
specific bugs were newly written by Extender.

## Upstream-equivalent check for project-new work

| Check ID | Project-new conclusion | Selected upstream/component search | Reuse decision |
|---|---|---|---|
| `A10-UE01` | Snapshot/browser allocation (`A10-LIN02`) | Official VDP/vdp-gl has synchronous framebuffer reads and drawing locks, but no immutable multi-consumer snapshot generation, lease pool, browser codec worker or browser resource policy. | Retain one Extender snapshot service; change its lifecycle/policy rather than creating another capture implementation. |
| `A10-UE02` | WebDAV transaction (`A10-LIN03`) | ESP-IDF supplies sockets and task primitives; no selected component supplies Extender's WebDAV-to-admitted-EMOS transaction. | Retain the service and make its startup one rollback-capable transaction. |
| `A10-UE03` | Global socket policy (`A10-LIN04`) | ESP-IDF HTTPD owns a server's internal sockets and local maximum, not arbitration across two HTTP servers plus a raw listener. | Add one Extender composition budget; do not replace the component servers. |
| `A10-UE04` | Native product profile (`A10-LIN05`) | ESP-IDF/CMake and Arduino components provide build mechanisms, not the Extender feature selection. | Keep profile authority in `p4-profiles.json`; classify/remove experimental definitions there. |
| `A10-UE05` | Browser oracle (`A10-LIN09`) | No official Agon test provides this browser/Playwright lifecycle. | Repair the existing test callback; do not add another browser layout runner. |
| `A10-UE06` | Maintained build guidance (`A10-LIN10`) | No upstream document can own this repository's native-versus-historical build selection. | Correct the existing Extender guide. |
| `A10-UE07` | Unavailable updater adapter (`A10-LIN13`) | Official VDP has a complete updater parser/consumer, but its ESP32 OTA backend targets different hardware and policy. | Reuse its exact grammar and consumption semantics in the P4 unavailable adapter; omit/reject the unsupported action explicitly. |

## Functional-duplicate and parallel-owner register

The register distinguishes runtime duplication from mutually exclusive source
alternatives, target copies and small test-helper clones. A candidate is not a
finding merely because two implementations exist.

| Duplicate ID | Implementations and equivalence | Runtime/maintenance consequence | Canonical owner and disposition |
|---|---|---|---|
| `A10-DUP01` | Selected `StockRuntimeController`/`StockP4Service`/`stock_scanline`/`stock_render_utils` and excluded `P4DisplayController`/`P4FrameService`/`PlaneStorage`/`PaletteState`/`PresentationCompositor`/`fabutils_port` implement parallel P4 display families: mode storage, palette/Copper state, rendering, snapshots and frame service. | `p4-profiles.json` makes the families mutually exclusive, so there are not two live display owners. Source fixes and tests can nevertheless diverge; `PaletteState` already has safer palette deletion while the selected upstream-shaped class retains `FWBUG-001`. | **Selected stock-shaped family is the current product owner.** Keep the nonrelease family only for bounded PORT-008 qualification/LCD design evidence. A10-06 must require an explicit extraction/removal decision before product fixes are copied into both. |
| `A10-DUP02` | Local `parseOfficialModeline` extracts width/height/refresh from the official modeline label while public upstream `VGABaseController::convertModelineToTimings` parses the complete modeline. Nonstock-only `ScreenFacadeAdapter::configure`, compiled out of the selected stock profile, also contains a rollback-capable mode transaction parallel to selected `agon_screen.h::changeResolution`. | The small parser is not byte-equivalent and serves metadata, but it re-parses an upstream-owned syntax. The two coordinators encode different rollback behavior. | **Canonical syntax parser: upstream `convertModelineToTimings`; canonical product transaction: the selected stock-shaped mode seam.** A repair should expose needed dimensions from the upstream parse and consolidate transaction semantics instead of maintaining a label parser and two repair paths. |
| `A10-DUP03` | Upstream `convertFloatToValue` and local `encodeFixed` both encode numeric values; only one buffered branch uses the safer local helper while ordinary parser/buffer routes retain upstream helpers. | A partial parallel repair creates path-dependent validation and leaves `A10-MR07` active. | **Canonical future owner: one VDP-compatible checked numeric-conversion seam.** A10-06 must inventory all callers before selecting whether the upstream helper is corrected or wrapped; retire the partial duplicate after migration. |
| `A10-DUP04` | `diagnostic/p4_zdi_probe.cpp`, retired `diagnostic/p4_zdi_mos_recovery.cpp` and maintained `recovery/mos_recovery.cpp` repeat ZDI start/read/write/register/memory/initialization routines; the two recovery sources also repeat CRC/payload verification. | Recovery and diagnostics can acquire different pin timing or target-state fixes. The retired source is not selected, but it remains an attractive stale copy. | **Canonical product owner: `recovery/mos_recovery.cpp`.** If the probe remains maintained, extract a target-neutral ZDI transport used by recovery and diagnostics. Otherwise retain the probe as frozen evidence and remove/archive retired executable copies under their owning task. |
| `A10-DUP05` | P4 `storage/sd_wire.h` and EMOS `projects/sdserve/src/sd_wire.h` are byte-identical (`d78a251c…`); P4 `transport/console_wire.h` and EMOS `src/emos_console_wire.h` are byte-identical (`b83f1300…`). | These copies must compile independently for different processors/repositories. Manual synchronization could drift a public/private wire contract. | **Canonical contracts: `docs/protocols/mainboard-sd.md` and `docs/protocols/excom-console.md`; canonical SD codec is the Extender-owned header.** Retain target copies with byte-equivalence tests already required by their documents; do not force cross-repository build coupling. |
| `A10-DUP06` | CRC32 loops occur in telemetry, remote-keyboard/diagnostic paths, maintained and retired recovery, and EMOS admission, while `sd_crc_update` already supplies a reusable protocol implementation. | Repeated polynomial loops can drift; recovery's copies are part of `A10-DUP04`. Protocol-specific exclusion of an embedded CRC field is legitimately a wrapper concern. | **Canonical P4 primitive should be one dependency-free checksum helper; canonical SD framing remains `sd_crc_update` until migrated deliberately.** Retain protocol wrappers, remove repeated bit loops when their owning code next changes, and verify byte vectors. |
| `A10-DUP07` | `sdserve` and `sdjob` both validate transfer paths; `sdjob` already reuses the checked `sdserve` engine but separately validates its admitted descriptor with a stricter character policy. | The services are not duplicate transfer engines. Two path predicates can drift or reject different names without a named policy reason. | **Canonical owner: shared `lib/sdapp` path syntax with caller policy parameters.** Preserve stricter job admission if documented; consolidate only the common confinement/syntax primitive. |
| `A10-DUP08` | Video HTTP, local-SD HTTP and WebDAV are distinct services but each independently claims sockets/tasks and publishes its own capacity. | This is duplicate resource ownership, not duplicate user functionality; it produces `A10-MR04`. | **Canonical owner: one P4 boot/network composition budget.** Keep the protocol adapters separate and make each consume a declared share. |
| `A10-DUP09` | Standalone `boot/p4_usb_keyboard.cpp` qualification acquisition and production `input/p4_usb_host.hpp` contain closely parallel HID host/device/report handling. | The standalone fixture is an oracle, not a second product input path, but independent fixes can make the oracle cease to test production behavior. | **Canonical product owner: `input/p4_usb_host.hpp`.** Freeze the standalone fixture or make future qualification call a reusable acquisition module; do not repair both independently. |
| `A10-DUP10` | `tests/browser_network_containment_test.py` and `tests/video_takeover_test.py` are byte-identical (`f43e7d5f…`) wrappers for the same network runner. | The two names imply distinct tests while executing one implementation; this is low-risk compatibility-entry duplication. | **Canonical owner: the shared network runner.** Retain aliases only if external invocations require them; otherwise replace both with one named launcher during test-maintenance work. |
| `A10-DUP11` | The four `prepare_*` host helpers repeat Git snapshot/hash/write preparation, and capture helpers repeat completion parsing. | Test-support changes can drift, but none owns product behavior and no current conclusion depends on the clone. | **Canonical owner: a small shared fixture-preparation library when these scripts next change.** Low priority; do not expand A10-08 solely for cleanup. |
| `A10-DUP12` | Three pinned EMOS fixture `api.asm` files are exact copies (`aab845cd…`); three pinned EMOS and one Extender fixture `emos_gateway.asm` files are exact copies (`8e953763…`). | Separate MOSlet builds need local assembly inputs, but fixes can silently reach only one fixture. | **Canonical owner: a shared fixture include or generated verified copy in the owning test repository.** Until changed, preserve exact hashes and treat copies as fixtures, not product implementations. |
| `A10-DUP13` | Snapshot-pool and HTTP-video code contain the same small saturating atomic increment pattern. | This is an implementation idiom with no separate state-machine owner and negligible current risk. | **Disposed as non-material duplication.** Consolidate only if a general counter utility already becomes necessary. |

## Disposed lookalikes and intentional separation

`A10-ND01` — Browser codecs encode different documented formats. Shared frame
input does not make them duplicate implementations.

`A10-ND02` — Local-SD HTTP, WebDAV and browser video expose different protocols
and consumers. They need common resource arbitration, not a merged server.

`A10-ND03` — Foreground `sdserve` and finite admitted `sdjob` have different
session/lifetime contracts. `sdjob` already reuses the shared transfer engine;
only the path predicate overlap in `A10-DUP07` needs reconciliation.

`A10-ND04` — `scripts/sdcard.py` controls the mainboard SD service while
`scripts/p4sd.py` controls P4-local storage. Similar host operations do not make
the target or transaction contract equivalent.

`A10-ND05` — One `PresentationSnapshotPool` implementation is instantiated by
both mutually exclusive display profiles. That shared implementation is reuse,
not duplication.

`A10-ND06` — Porting portable scan-row bodies is justified because the classic
ESP32 physical scanout executor cannot run on the P4. The retained span
provenance and source-parity checks are the correct control; inventing new row
drawing code would be the duplicate.

## A10-06 mandatory handoff

`A10-LH01` — Every final finding must cite one or more `A10-LINnn` entries and
record the exact inherited, adapted or project-new defect origin in
`A10-FIELD08`.

`A10-LH02` — Every proposed repair must cite its applicable `A10-UEnn` and
`A10-DUPnn` disposition in `A10-FIELD09`. If no duplicate applies, state that
the current-source check found none rather than leaving the field implicit.

`A10-LH03` — Split repair items when upstream and project actors differ. In
particular, mode allocation safety, P4 transaction ordering and profile memory
policy are not one undifferentiated implementation change.

`A10-LH04` — Do not copy a correction into both P4 display families. Select the
product owner first; preserve or extract a discriminating test from the
nonrelease family as needed.

`A10-LH05` — Do not rewrite official updater grammar, modeline syntax, VDP
numeric encoding or retained FabGL row decoration when an upstream function is
already selected. Adapt the hardware-specific action or add a checked seam.

`A10-LH06` — `A10-DUP05`, `A10-DUP10`, `A10-DUP11`, `A10-DUP12` and
`A10-DUP13` are not automatic repair findings. A10-06 should retain only the
controls or bounded maintenance action justified by their actual drift risk.

`A10-LH07` — This reconciliation found no reason to invoke historical review.
Any later introduction-point or rationale search remains subject to the
accepted A10-H01 through A10-H07 pause-and-approval gate.
