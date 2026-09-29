# AUDIT-010 A10-05 — Manual integration review

## Executive summary

The complete manual pass reviewed all 35 frozen coverage areas and all eleven
A10-04 candidates against the A10-01 risk checklist, A10-03 ownership/resource
maps, current architecture, official Agon contracts and accepted decisions. It
used the frozen pre-LCD source identities, current-source comparisons and
retained evidence only. It did not inspect Git history, change executable code,
build firmware, run a target or operate hardware.

The review carries eleven new conclusions into A10-06. The most consequential
are not isolated style problems:

| Review ID | Summary |
|---|---|
| `A10-MR01` | A VDU mode change destroys the current native display before the replacement is known to be viable; allocation failures can also dereference unchecked allocation results. The official old-mode/mode-1 fallback therefore repeats a destructive operation rather than rolling back a prepared transaction. |
| `A10-MR02` | The three-slot browser snapshot pool is a mandatory dependency of every stock display attach, despite being described as optional and on-demand. Together with eagerly retained codec scratch it reserves 4,522,002 bytes of PSRAM before application assets and makes unrelated mode success depend on browser-output resource policy. |
| `A10-MR03` | WebDAV can publish a live accept task and listener, fail to create its application worker, return failure without rollback, then report success on the next start while the runtime is not ready. |
| `A10-MR05` | The ordinary `p4-console` profile combines multiple comments' explicitly bounded/default-off diagnostics and experiments. The graph is reproducible, but the selected scheduling, allocation and instrumentation behavior is not a principled product default. |
| `A10-MR06` / `A10-MR07` | Application-controlled font metadata and numeric conversion paths contain source-proven memory-safety or C++ undefined-behavior hazards. |

The review also carries the already-authoritative unresolved current defects
from `docs/firmware-bugs.md`; it does not give them duplicate identities.
Automated warnings that did not survive semantic review are disposed below.
No conclusion in this document authorizes a fix or physical diagnostic.
A10-05a must now reconcile source lineage, upstream equivalents and internal
functional duplicates. A10-06 then assembles stable findings and the smallest
independent validation proposals for the Author's complete review.

## Method and evidence boundary

`A10-RM01` — The P4 target was source commit
`755d6f37d332ba95b09519f86b24d352ebb03660`; host/test evidence was
`b75aae35`; EMOS was the detached pinned v0.1.23 source
`21a9ba27f1f346473d767c2c3053ee18e8911335`; AgonDev integration was
`90034c23`. Exact tool and reference identities remain in `IDENTITIES.md` and
`AUTOMATED-ANALYSIS.md`.

`A10-RM02` — Official [screen modes](../../../../../agon-docs/docs/vdp/Screen-Modes.md),
[buffered commands](../../../../../agon-docs/docs/vdp/Buffered-Commands-API.md),
[font API](../../../../../agon-docs/docs/vdp/Font-API.md),
[context management](../../../../../agon-docs/docs/vdp/Context-Management-API.md)
and the tagged official MOS/VDP sources supplied the API contracts. Project
architecture, decisions, the current firmware-bug register and retained
qualification supplied accepted local constraints. Untouched third-party
internals were entered only through an active selected call path.

`A10-RM03` — “Source-proven” below means the control/data flow follows from the
selected source. It does not mean the consequence has been reproduced on the
P4. “Coverage gap” means source supports the intended route but no current
test demonstrates the material dynamic behavior. A10-06 owns severity,
confidence and final finding identifiers.

`A10-RM04` — No A10-H01 through A10-H07 trigger required a new bounded history
review. No history was inspected.

## Primary source trace

| Review input | Exact selected implementation |
|---|---|
| Mode lifecycle and allocation | [`vdu.h`](../../../vdp/video/vdu.h), [`agon_screen.h`](../../../vdp/video/agon_screen.h), [`vgabasecontroller.cpp`](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp), [`vgapalettedcontroller.cpp`](../../../vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp) |
| Snapshot/browser resource lifetime | [`stock_p4_service.cpp`](../../../vdp/video/extender/display/stock_p4_service.cpp), [`presentation_snapshot_pool.cpp`](../../../vdp/video/extender/display/presentation_snapshot_pool.cpp), [`wired_network_service.cpp`](../../../vdp/video/extender/network/wired_network_service.cpp) |
| WebDAV and socket composition | [`runtime.cpp`](../../../vdp/video/extender/storage/webdav/runtime.cpp), [`http_video_service.cpp`](../../../vdp/video/extender/network/http_video_service.cpp), [local SD HTTP](../../../vdp/video/extender/storage/local/http.cpp), [`sdkconfig.p4-console`](../../../vdp/sdkconfig.p4-console) |
| Selected profile policy | [`p4-profiles.json`](../../../vdp/build/p4-profiles.json) |
| Font and numeric safety | [`agon_fonts.h`](../../../vdp/video/agon_fonts.h), [context font paths](../../../vdp/video/context/fonts.h), [`displaycontroller.h`](../../../vdp/vendor/vdp-gl/src/displaycontroller.h), [`types.h`](../../../vdp/video/types.h) |
| Stock scanout effects | [`stock_scanline.cpp`](../../../vdp/video/extender/display/stock_scanline.cpp), [`stock_runtime_controller.hpp`](../../../vdp/video/extender/display/stock_runtime_controller.hpp) |
| Tests and maintained guidance | [`browser_layout_test.py`](../../../tests/browser_layout_test.py), [`shared-p4-services.md`](../../shared-p4-services.md) |

## Manual review conclusions

### A10-MR01 — Mode replacement is destructive and allocation failure is unsafe

**Evidence class:** source-proven contract violation; retained physical mode-
switch failure is consistent evidence, not a proven cause.

The P4 parser's `VDUStreamProcessor::vdu_mode` first clears the current context,
waits for drawing, disables Teletext and removes the VSYNC callback. Its
`changeResolution` path invalidates published `modeStatus`, joins the stock
workers, resets the Canvas/mouse binding and can destroy the current controller
when colour depth changes. `VGABaseController::setResolution` then calls
`end()` and frees the old viewport before allocating the new one.

The allocator has no transactional result. It can shorten the viewport, and it
dereferences the allocation for `m_viewPortMemoryPool` without checking it.
Row-pointer tables and the four DMA-capable prepared rows are also used without
checking every allocation. `changeResolution` detects shortened geometry only
after constructing a Canvas; task-attach failure occurs later still. On any
failure, official fallback calls `changeMode(videoMode)` and, if needed, mode 1,
but neither call restores a saved allocation. Logical mode metadata is
correctly withheld until success, while physical/drawing objects can already
represent the failed attempt.

The violated integration contract is not the official fact that a mode change
may fail for memory. It is the promise that failure can return to the current
mode safely and truthfully. A10-06 should treat the null-allocation path and
non-transactional fallback as one lifecycle finding with separable repair and
validation clauses.

### A10-MR02 — Browser output resources are globally coupled to display modes

**Evidence class:** source-proven architecture/resource violation; exact
causality for the retained Nurples failure remains a hypothesis.

`PresentationSnapshotPool` eagerly allocates three 1024×768 RGB222 slots when
the first `StockP4Service` is constructed. If any slot fails, the pool frees
the others and disables itself. `StockP4Service::attach`, however, refuses to
attach any mode when `snapshots_.enabled()` is false. The pool is therefore not
an optional browser facility in this build: a basic display mode cannot run
unless all 2,359,296 snapshot bytes are reserved, even with no Ethernet lease or
browser client.

After HTTP startup, `WiredNetworkService` additionally allocates and retains
three maximum-size codec blocks totaling 2,162,706 bytes. Codec failure
degrades to fewer encodings and raw video, so eager maximum lifetime is not
required by correctness. The output worker already composes snapshots only on
consumer demand, but the backing allocations are product-long. These policies
make later application asset and mode-plane allocation depend on whether
unrelated browser facilities started earlier. They correct A10-03's description
of the snapshot pool as operationally optional; the raw pool can disable, but
the stock display attach then fails.

### A10-MR03 — WebDAV partial startup leaks ownership and later lies about readiness

**Evidence class:** source-proven lifecycle/state defect.

`webdav::startRuntime` creates a listening socket and `sd-dav-accept` task,
publishing the task handle in `acceptTask`, before it creates the persistent
`sd-application` worker. If the second task creation fails, the function
returns false without closing the listener, deleting/joining the accept task or
clearing `acceptTask`. It does not publish `storage::sd_runtime_ready`.

A later call returns true immediately because `acceptTask` is non-null, even
though the application worker is absent and runtime readiness is false. The
network caller logs only the first failure and continues starting other
services. This is exactly the partial-start/stale-publication pattern from
A10-01; process-long lifetime does not excuse a failed initialization
transaction.

### A10-MR04 — Configured network services overcommit the global socket budget

**Evidence class:** source/configuration-proven capacity conflict; saturation
behavior has not been target-tested in this audit.

The selected SDK configuration provides ten lwIP sockets. ESP-IDF documents and
implements three internal sockets per HTTP server in addition to
`max_open_sockets`. The main video server requests seven clients and the P4-SD
server requests two, so those two servers alone declare fifteen sockets. The
raw WebDAV listener and its admitted client add two more potential sockets.
Ethernet/DHCP and other component users are outside that total.

`docs/shared-p4-services.md` already acknowledges that ten is not a sufficient
worst-case combined budget, but the ordinary selected profile retains the
conflicting limits. In practice the services can start only while fewer sockets
are live than their independently advertised limits. A10-06 should distinguish
the proven capacity contradiction from any unmeasured user-visible failure
under concurrent browser, P4-SD and WebDAV traffic.

### A10-MR05 — The ordinary console profile is an accumulated diagnostic bundle

**Evidence class:** source/configuration-proven architecture-policy defect.

The `p4-console` profile is reproducible and correctly excludes alternative
controllers, but it simultaneously enables definitions whose own source
comments call them a bounded mode-20 comparison, an optional diagnostic,
experimental/default-off scheduling, or QUAL-003 instrumentation. Material
examples are internal framebuffer pools restricted to mode 20, four drawing
opportunities per logical frame, output below the parser, snapshot lookahead,
refresh tracing, video timing and dispatch timing. It also defines both
`AGON_EXTENDER_DRAW_FOUR` and `AGON_EXTENDER_DRAW_TWICE`; preprocessor order
silently selects four.

This is not a build-reproducibility failure. It is a configuration-ownership
failure: the ordinary development product has no minimal declared behavioral
profile against which one experiment can be changed and regressed. A10-06
should require an itemized classification of each definition as required
product behavior, temporary diagnostic or rejected experiment before fixes are
evaluated.

### A10-MR06 — Mutable font metadata can escape its validated backing storage

**Evidence class:** source-proven memory-safety/API-contract defect.

`createFontFromBuffer` checks one fixed-width buffer against the original width
and height, then stores a raw data pointer. `setFontInfo` subsequently permits
an application to change width, height and flags without revalidating the
backing size. It can also install a raw character-offset pointer from another
buffer without validating 256 entries or retaining that buffer. Official
`Font-API.md` makes width and height mutable properties but says variable-width
fields remain reserved and do not affect rendering; the current source can make
them affect pointer selection.

`getCharPtr` trusts the mutated geometry/offsets. `Context::getScreenChar`
multiplies glyph bytes and height into an eight-bit `charSize`, creates a
variable-length stack array of that wrapped size and fills it using the full
dimensions. vdp-gl's full glyph path can additionally `alloca` nearly an entire
8,192-byte display-worker stack for application-controlled maximum dimensions.
The initial size check therefore does not bound later reads, writes or stack
demand. Existing `FWBUG-012` remains authoritative for broader buffer/sprite
operand lifetimes; this conclusion is the distinct mutable-font contract.

### A10-MR07 — Numeric conversion uses undefined aliasing and shift operations

**Evidence class:** source-proven C++ undefined behavior.

The selected `types.h` converts float bit patterns through references/pointers
to unrelated scalar types, violating C++ strict-aliasing rules. The active
fixed-point conversion also computes `1 << shift` with signed `int`; the
application-controlled 32-bit format admits shift 31, for which the operation
is undefined. The dedicated newer `encodeFixed` path uses `std::ldexp`, but
ordinary buffer/parser conversion still reaches the older helpers. This retains
A10-AF03 and adds the adjacent shift defect under one conversion owner.

### A10-MR08 — Stock scanout effects have source parity but no current dynamic P4 proof

**Evidence class:** coverage gap, not a demonstrated rendering defect.

Every selected colour-depth row path calls the retained
`decorateScanLinePixels`, so Copper palette changes, the text cursor and
hardware sprites are present in the stock row-composition route rather than
being omitted from the stored framebuffer. The runtime also preserves the
sequential Copper cursor under its native guard. Current active tests do not,
however, exercise Copper mutation and hardware-sprite overlay through the P4
snapshot/browser boundary. Prior visual evidence is bounded and does not prove
all dynamic interaction. A10-06 should propose one static deterministic scene
covering ordered Copper spans, overlapping hardware sprites, clipping and
hidden sprites before LCD is redeployed.

### A10-MR09 — Browser layout test can misattribute a late page error

**Evidence class:** source-proven weak test oracle; low impact.

`browser_layout_test.py` closes over the loop-local `errors` binding in an
asynchronous page-error callback. A late callback after the loop advances can
append to a later iteration's list or arrive after the current assertion. The
page is synchronously closed, which reduces but does not remove the scheduling
seam. Binding the list in the callback and draining/assessing errors before
close are the bounded repair requirements.

### A10-MR10 — One maintained shared-service check still invokes the historical build

**Evidence class:** source-proven documentation defect; low impact.

`docs/shared-p4-services.md` accurately explains native component versions and
the combined socket deficit, but its console-check block still invokes
`.venv/bin/pio run -d vdp -e p4-console`. Current `docs/building.md` declares
native ESP-IDF/CMake the sole maintained outer authority and gates PlatformIO as
historical rollback. The historical wrapper itself fails closed, so this is not
a silent alternate build; it is a stale maintained validation instruction.

### A10-MR11 — Filled arc/sector edge logic contains an unreachable branch

**Evidence class:** source-proven control-flow defect; visual consequence needs
a discriminating host scene.

In selected vdp-gl `displaycontroller.h`, the two-part filled-row branch is
entered only when both `hasLeftEdge` and `hasRightEdge` are true, then tests
`if (!hasLeftEdge)` before emitting `firstLine.minX`. That inner block is
unreachable. The surrounding one-part paths conditionally emit the same start
edge, so the dead condition is not just generic style. A10-06 should retain the
candidate and use a small quadrant/sector matrix to decide the affected shapes
before assigning repair scope.

## Existing authoritative defects consumed by this review

The complete audit cannot call the affected coverage clean merely because a
defect already has another stable identity. The following current-baseline
records remain authoritative and should be cross-referenced, not renumbered, in
A10-06:

| Existing ID | Current affected area | A10-05 disposition |
|---|---|---|
| `FWBUG-001` | P4/vdp-gl palette cleanup | Applicable, source-proven and physically manifested; patch remains deferred. |
| `FWBUG-006` | P4 unavailable updater command grammar | Applicable source-level payload-consumption defect; no application manifestation claimed. |
| `FWBUG-007` | Primitive completion/swap lifecycle | Retained unresolved candidate; restored-backend applicability still needs the bounded test already owned elsewhere. |
| `FWBUG-008` | Complete EMOS/MOS raw SD write API | Applicable source defect with retained physical EMOS evidence; ordinary FatFS writes use another path. |
| `FWBUG-009` | Complete EMOS/MOS volume-label result | Applicable source defect with retained physical EMOS evidence. |
| `FWBUG-010` | Complete EMOS/MOS UART0 reply validation | Applicable source defect; no new physical injection run. |
| `FWBUG-012` | P4 buffered operands, bitmaps and sprites | Applicable source-proven lifetime defect; native locking does not repair destroyed ownership. |

## A10-04 candidate disposition

| Candidate | Manual disposition |
|---|---|
| `A10-AF01` | Disposed as a compiler false positive under the maintained compression bit-count invariant: the command is 0–3; case 0 continues and cases 1–3 initialize `size`. |
| `A10-AF02` | Disposed. Omitted state-switch arms require no transition side effect; paged-mode switches intentionally divide stable/temporary states; bitwise Boolean and mask-expression operands are side-effect-free and semantically equivalent here. |
| `A10-AF03` | Retained as `A10-MR07`; strict aliasing is violated on active conversion paths. |
| `A10-AF04` | Disposed as tool idioms/bounded input: status assignments are intentionally captured, string comparisons test nonzero mismatch, and selected modelines are retained constants. The eighteen Clang-incomplete units remain a coverage limit. |
| `A10-AF05` | Disposed for the selected product call graph. The Arduino `WString` return is in managed header code not reached by the numeric ESP32Time methods used here. |
| `A10-AF06` | Split: retained stack/font exposure as `A10-MR06` and dead edge control as `A10-MR11`; the code-page count is semantically wrong but coincidentally correct for the two-word target structure and is maintenance debt; the unbounded vendor modeline label is unreachable from external product input. |
| `A10-AF07` | Retained as `A10-MR09`. |
| `A10-AF08` | Disposed. Partial browser-state collection occurs only while preserving and re-raising an existing failure; it cannot turn that run into PASS. |
| `A10-AF09` | Disposed as staged typing limitations. Validators perform runtime schema/shape checks; optional socket/file operations follow runtime guards; malformed performance evidence fails loudly rather than producing a successful measurement. |
| `A10-AF10` | Retained as `A10-MR03`. |
| `A10-AF11` | Provenance/licence inventory is present, but OSV supplied no coverage for ESP-IDF locks, managed components, vendored C++ or tool pins. Retain that explicit vulnerability-survey limit; do not convert it into a vulnerability finding. |

## Complete coverage disposition

| Coverage ID | A10-05 result |
|---|---|
| `A10-COV001` | Reviewed boot order and singleton construction; `A10-MR02` and `A10-MR05` apply. Fail-stop USB/boot errors are visible and require reset. |
| `A10-COV002` | Reviewed UART framing, sole writer, admission, timeout and corruption containment; no new defect. |
| `A10-COV003` | Reviewed mode coordinator, detach/join and published state; `A10-MR01` applies. |
| `A10-COV004` | Reviewed selected controller allocation and cleanup; `A10-MR01`, `A10-MR11` and existing `FWBUG-001` apply. |
| `A10-COV005` | Reviewed active drawing/font/sprite/Copper paths; `A10-MR06`, `A10-MR08`, `A10-MR11`, `FWBUG-001`, `FWBUG-007` and `FWBUG-012` apply. |
| `A10-COV006` | Reviewed slot allocation, transition locking, leases and teardown; ownership is bounded, but `A10-MR02` applies to mandatory eager lifetime. |
| `A10-COV007` | Reviewed frame shapes, scratch bounds, codec fallback and lease release; bounds are coherent; `A10-MR02` applies to allocation policy. |
| `A10-COV008` | Reviewed one-viewer callback/send/stop lifecycle; callback ownership is coherent; `A10-MR04` applies to sockets. |
| `A10-COV009` | Reviewed Ethernet events, worker ownership and HTTP startup; `A10-MR02`, `A10-MR03` and `A10-MR04` apply. |
| `A10-COV010` | Reviewed USB/browser input queues, disconnect and console arbitration; no new defect. |
| `A10-COV011` | Reviewed route rollback, media lease and process-long mount/server contract; `A10-MR04` applies. One-shot mount retry is an explicit product-lifetime policy, not silently treated as teardown. |
| `A10-COV012` | Reviewed admission, staging, verification, socket deadlines and task startup; `A10-MR03` and `A10-MR04` apply. |
| `A10-COV013` | Embedded bytes are identity-tested against five sources; browser error/status paths reviewed; no new defect. |
| `A10-COV014` | Reviewed EMOS prepare/commit/recover sequencing and truthful committed route/mode publication; no new defect. |
| `A10-COV015` | Reviewed finite admission generations, terminal proof, key priority and fail-closed exhaustion; no new defect. |
| `A10-COV016` | Reviewed Extender keyboard/UART source transitions, ISR ownership, held-key cleanup and timeouts; documented silent-idle peer loss remains an accepted hardware limit. |
| `A10-COV017` | Reviewed bounded SD/telemetry mailboxes, foreground-only filesystem work and UART serialization; no new defect. |
| `A10-COV018` | Reviewed `sdserve` path confinement, verified staged writes and cancel behavior; no new defect. |
| `A10-COV019` | Reviewed finite `sdjob` admission, cancellation/deadline and terminal record behavior; no new defect. |
| `A10-COV020` | AgonDev source selection, translation, link and provenance are identity-validated; no new defect. |
| `A10-COV021` | Native build creates fresh identified output, pins ESP-IDF, validates actual actions and hashes artifacts; no new defect. |
| `A10-COV022` | Source/forbidden profile isolation passes, but ordinary profile semantics carry `A10-MR05`. |
| `A10-COV023` | Historical entry points fail closed and are excluded from maintained builds; `A10-MR10` is the one stale current-doc invocation. |
| `A10-COV024` | Reviewed maintained clients' no-shell command boundaries, timeouts, CRC/hash receipts, no-clobber downloads and no implicit mutation retries; no new defect. |
| `A10-COV025` | Reviewed builders/validators and detached job terminal records; no new defect. Future changed suites remain subject to A10-T01–T09 rather than receiving blanket credit here. |
| `A10-COV026` | Active host suites pass within their declared substitutions; `A10-MR08` and `A10-MR09` identify missing/weak coverage. |
| `A10-COV027` | Correctly deferred LCD implementation delta; retained grid/bars/Nurples evidence remains the required post-audit regression matrix. |
| `A10-COV028` | Historical fixtures remain excluded unless a current finding explicitly reuses one; no scope expansion. |
| `A10-COV029` | Official documents/tags were used as read-only contracts; no defect assigned to references. |
| `A10-COV030` | Production/installed identities remain bounded comparisons, not substituted audit targets; no new defect. |
| `A10-COV031` | Reviewed compiled-but-inactive EMOS parallel epoch ownership, pin release, generation exhaustion and deferred-fault cleanup; no new defect. |
| `A10-COV032` | Complete selected EMOS image consumes existing `FWBUG-008`, `FWBUG-009` and `FWBUG-010`; project hooks add no newly demonstrated base-image defect. |
| `A10-COV033` | Reviewed retained textual parser/buffer/font/sprite and unavailable-subsystem grammar; `A10-MR06`, `A10-MR07`, `FWBUG-006` and `FWBUG-012` apply. |
| `A10-COV034` | Exact managed-component identities and notices are frozen; `A10-MR04` applies to ESP-IDF socket semantics. A10-AF11 remains an explicit security-database coverage limit. |
| `A10-COV035` | Reviewed SDK memory/socket limits, partitions, native CMake and definitions; `A10-MR04` and `A10-MR05` apply. |

## A10-06 handoff

`A10-HAND01` — A10-06 must assign final stable finding IDs only after
deduplicating A10-MR01 through A10-MR11 against the existing authoritative
FWBUG records. New and existing findings must remain separately identifiable.

`A10-HAND02` — Static evidence is sufficient to propose repairs for A10-MR01,
A10-MR02, A10-MR03, A10-MR05, A10-MR06, A10-MR07, A10-MR09 and A10-MR10.
Target execution is not required merely to prove their source conditions.

`A10-HAND03` — A10-MR04 needs a bounded concurrent-service saturation test only
if the Author needs observed user impact beyond the proven configured deficit.
A10-MR08 needs a deterministic visual/byte scene. A10-MR11 needs the smallest
host-renderer shape matrix that distinguishes the unreachable edge path.

`A10-HAND04` — No A10-05 conclusion authorizes diagnostic code, hardware
operation or repair. The Author's later source-lineage clarification adds
A10-05a as a prerequisite: classify upstream-unchanged, upstream-ported/adapted
and project-new code, check upstream equivalents and internal functional
duplicates, then begin A10-06. A10-06 remains documentation/proposal work,
followed by the complete A10-07 Author review gate.
