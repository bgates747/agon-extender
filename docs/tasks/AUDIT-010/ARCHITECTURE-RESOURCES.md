# AUDIT-010 A10-03 — Functional and resource architecture

## Status and method

This is the accepted pre-LCD baseline's source-derived architecture map. It
uses the identities frozen in `IDENTITIES.md` and the closure frozen in
`COVERAGE-LEDGER.md`. The Author accepted A10-02 on 2026-09-29. No diagnostic
source, target run, hardware mutation or Git history was used for A10-03.

The official Agon contracts establish that VDU 22 owns mode selection, a mode
change may fail for lack of memory, and failure falls back first to the current
mode and then to mode 1. They identify mode 8 as 320x240x64 and mode 20 as
512x384x64. The implementation details below come from the frozen P4 and EMOS
sources; they do not amend that public contract.

Quantities labelled **calculated** follow directly from constants and active
branches in source. **Configured** quantities are requested limits or task
stacks, not proof of actual heap consumption. **Observed** quantities would be
target measurements; A10-03 made none. FreeRTOS control blocks, allocator
metadata, C++ objects, lwIP/HTTP/Ethernet/USB component allocations and stack
high-water use are therefore outside the byte subtotals unless expressly
listed.

## Actor and ownership map

| ID | Operation and actors | Allocation/order and lifetime | Failure, rollback and published state | Consumer-visible consequence |
|---|---|---|---|---|
| A10-MAP01 | **P4 Arduino entry task** invokes `setup`; retained VDP code creates the initial display; **P4 parser task** then consumes EMOS VDU bytes; **network worker** starts Ethernet; **WebDAV accept/application workers** start when enabled. | The persistent three-slot snapshot pool is constructed with the first stock display service. A native mode is then allocated and its draw/output workers attached. Parser state, font state and services follow. Network worker starts before link/IP; HTTP and its three codec scratch buffers start after a lease. WebDAV listener/application workers start from the network lifecycle. | Display setup treats unrecoverable failures as boot failures. Network start records `Faulted` and stops Ethernet/worker on `ETH.begin` failure. HTTP registration failure stops its server. WebDAV listener failure closes its socket, but failure to create the application worker after the accept worker succeeds returns false without retiring the already-created accept worker; this is an A10-05 review point, not yet a finding. | A display can remain usable when the browser service is absent. Network state and diagnostic counters distinguish link, lease and HTTP failure. WebDAV availability is not independently published beyond its readiness flag/routes. |
| A10-MAP02 | **EMOS/application** sends VDU 22; **P4 parser** calls `changeMode`; **stock frame service** and **stock controller** perform the transition. | `modeStatus` is invalidated; frame-service draw/output tasks are joined; mouse and Canvas are detached; a controller is replaced only when colour depth changes; `setResolution` frees/reallocates native rows; the logical clock and two 8,192-byte worker stacks are started/attached; Canvas is recreated; geometry is checked; committed state is published only after success. | Return values are invalid mode `-1`, bad depth `1`, memory/configuration `2`. The retained official VDU caller owns old-mode then mode-1 fallback. The local operation is not a full prepare/commit transaction: it destroys Canvas and may reconfigure the live controller before all later checks and task creation succeed. `videoMode` and `modeStatus` are withheld on failure, but native objects may already reflect the attempted mode. A10-05 must judge the fallback path and state truth end to end. | On success applications, Canvas, browser metadata and diagnostics see the new geometry. On failure the official contract promises fallback, but this layer alone cannot promise that the old native allocation survived unchanged. |
| A10-MAP03 | **P4 parser** enqueues drawing primitives; **stock draw worker** drains them; **stock output worker** composes requested presentation snapshots. | The parser and draw worker share the retained primitive queue/dynamic pool. At logical boundaries the output worker obtains one free immutable slot, prepares one or two rows through the native guard into a 1,024- or 2,048-byte stack row buffer, normalizes directly to RGB222, and publishes the slot. The pool persists across modes. | A busy transition, producer, absent demand or absent slot skips publication and increments a bounded metric; drawing continues. Detach stops notifications, joins both workers, flushes retained work while native storage still lives, then permits replacement. | Mainboard drawing can progress without a browser. A slow browser holds at most one leased slot; the producer does not block and may skip frames. |
| A10-MAP04 | **Browser** opens HTTP/WebSocket; **ESP-IDF HTTP task** owns callbacks and socket sends; **network worker** polls credits; **browser provider** owns one snapshot lease. | HTTP server has one configured 4,096-byte stack, up to seven open sockets and 18 handlers. A new viewer replaces the old viewer. Each credit requests the latest generation; provider forms a 32-byte header plus the leased RGB222 plane. The HTTP task alone serializes optional pair/packed/RLE2 encoding through three persistent scratch blocks. | Failed codec allocation silently removes that codec choice while raw frames remain possible. Queue/send failure disconnects the client and releases its lease. Failed `httpd_stop` deliberately retains the live callback target and reports fault rather than freeing it. | Page assets work without a video client. Only one live video viewer is supported; replacement is explicit. A browser connection adds a lease/socket but the large snapshot and codec reservations already exist after service startup. |
| A10-MAP05 | **Browser file client** connects to P4 WebDAV; **accept worker** admits one transfer worker; **P4 SD media/spool owner** stages bytes; **console/UART owner** exchanges bounded records with **EMOS**; **EMOS sdlink** invokes filesystem work. | One 4,096-byte accept stack and one persistent 32,768-byte application stack exist after startup. At most one 32,768-byte transfer worker is admitted. A 4,096-byte GET buffer is stack-local. Mainboard exchanges use 240-byte requests/replies; downloaded files are staged on P4 SD under a 32 MiB quota rather than held in RAM. EMOS statically owns 240 + 240 + 244 byte sdlink mailboxes, while its keyboard receive record embeds a 240-byte payload. | Busy admission returns a bounded refusal. Socket operations have five-second deadlines and a ten-minute connection lifetime. RAII releases media, snapshot and channel state. Transfer verification precedes activation. P4 reset drops volatile ownership; staged files provide recovery evidence. | Video and file transfer use different TCP services but share P4 memory, network stack, SD and the sole EMOS console/UART owner. Mainboard file operations are serialized rather than run concurrently through a second UART writer. |
| A10-MAP06 | **USB HID task** and **browser HTTP callback** supply input; **P4 console owner** arbitrates it; **EMOS keyboard owner** selects Extender, browser or mainboard source. | USB host uses a configured 4,096-byte library-task stack and a 3,072-byte LED worker. Browser key messages traverse bounded HTTP parsing and the console owner. EMOS statically retains 144 asynchronous bytes, a 32-byte held-key set and one 240-byte keyboard payload record. | Source changes are acknowledged; busy, timeout and fault states preserve the prior source or mark it faulted according to EMOS tests. Browser disconnect releases its source. No input path owns display storage. | Input may change independently of display mode. Extender keyboard availability depends on the selected EMOS source and UART ownership, not merely network link state. |
| A10-MAP07 | **Mode owner/network owner** performs orderly detach/stop; **operator/reset hardware** supplies ultimate recovery. | Display detach joins draw/output readers before controller/Canvas destruction. HTTP stop joins callbacks before lease release; network stop waits for its worker then stops Ethernet. EMOS keeps bounded static mailboxes across ordinary operations, cleared/reinitialized by reset/boot. | Several destructors abort rather than permit use-after-free if a live callback/task cannot be stopped. A P4 or Agon reset is therefore the recovery boundary for a failed-stop condition. `modeStatus` invalidation prevents a transition snapshot from being reported as committed. | Orderly shutdown avoids stale pointers; abrupt reset discards volatile sessions and requires clients to reconnect. P4 SD staged files may outlive the volatile transfer session. |

## Source-derived resource ledger

| ID | Owner / capability | Calculated or configured demand | Lifetime and contiguous-allocation rule | Static limit not captured |
|---|---|---:|---|---|
| A10-RES01 | Stock presentation pool / PSRAM + 8-bit | 3 x (1024 x 768 x 1) = **2,359,296 B** | Product lifetime after first controller creation; three separate **786,432 B** contiguous allocations. The pool frees earlier slots and disables if any allocation fails, but A10-05 found that `StockP4Service::attach` then refuses every display mode: operationally this is mandatory, not optional. | Pool object, mutex and allocator metadata. |
| A10-RES02 | Browser codec scratch / PSRAM + 8-bit | pair **786,432 B**; packed **589,828 B**; RLE2 **786,446 B**; total **2,162,706 B** | HTTP-service lifetime after first start; three separate persistent blocks; allocation failure disables only that encoding. | Codec/object metadata and HTTP/lwIP buffers. |
| A10-RES03 | Mode 8 VGA64 native plane / normally PSRAM + 8-bit | 320 x 240 = **76,800 B** single-buffer plane | Mode lifetime; allocator may split rows over at most 128 pools while retaining a 4,000 B largest-block reserve. Each pool is individually contiguous. | Up to 129 pool pointers; allocator metadata. |
| A10-RES04 | Mode 20 VGA64 native plane / internal diagnostic policy, else PSRAM | 512 x 384 = **196,608 B** single-buffer plane | Mode lifetime. Active profile tries internal pools only for 512x384, requires total internal free >= 200,608 B, and rejects a shortened allocation before PSRAM fallback. | Capability overlap means this cannot be added blindly to general 8-bit free memory. |
| A10-RES05 | VGA64 row pointers / internal 32-bit | mode 8 **960 B**; mode 20 **1,536 B** on a 32-bit P4 | One contiguous pointer table per active plane; double buffering would require a second table and doubles plane rows. | Controller/palette/signal-list objects. |
| A10-RES06 | VGA64 prepared scanlines / DMA | 4 x width: mode 8 **1,280 B**, mode 20 **2,048 B** | Four separately allocated scanlines for controller lifetime. The pre-LCD stock runtime does not allocate physical VGA DMA descriptors or blanking buffers. | Heap metadata. |
| A10-RES07 | Display workers / FreeRTOS-capable memory | draw **8,192 B** + output **8,192 B** configured stacks | Recreated on successful mode attach; both coexist. Task creation failure enters failed mode/fallback handling. | TCBs, guards and actual high-water use. |
| A10-RES08 | Parser/process task | **4,096 B** configured stack | Product lifetime after setup. | TCB and queue/component stacks. |
| A10-RES09 | Network/HTTP tasks | network **8,192 B** + HTTP **4,096 B** configured stacks | Network task persists after start; HTTP task exists while serving a lease. | Ethernet event/task, lwIP sockets and seven-session structures. |
| A10-RES10 | WebDAV tasks | accept **4,096 B** + application **32,768 B** persistent; one transfer **32,768 B**; GET local **4,096 B** | Runtime lifetime except transfer task/request-local buffer. One concurrent transfer worker. | `std::string`/vector/XML growth, FAT/VFS/lwIP allocations. |
| A10-RES11 | USB input tasks | host **4,096 B** + LED **3,072 B** configured stacks | USB input service lifetime. | Managed HID/component allocations. |
| A10-RES12 | Retained primitive queue and dynamic payload pool / internal | queue capacity **1,024 primitives**; dynamic pool **512 B** | Controller lifetime. Primitive object/queue byte total depends on target `sizeof` and FreeRTOS queue representation; commands may also allocate retained bitmap/sprite/buffer assets outside this pool. | Application-loaded VDP assets are workload-dependent and have no source-constant aggregate ceiling. |
| A10-RES13 | EMOS sdlink / eZ80 static RAM | two receive mailboxes **480 B** + transmit **244 B** = **724 B** | Image lifetime; fixed arrays. | State fields and stack-local filesystem structures. |
| A10-RES14 | EMOS keyboard / eZ80 static RAM | async **144 B** + held keys **32 B** + embedded receive payload **240 B**, at least **416 B** | Image lifetime; fixed arrays. | Record fields, stack and base MOS keyboard storage. |
| A10-RES15 | EMOS admission/console / eZ80 static RAM | admission arrays **120 B**; console arrays depend on `CONSOLE_SIZE` plus 14 B shown state | Image lifetime; fixed arrays. | Base MOS/FatFS buffers and utility working memory require map/symbol accounting in A10-04/A10-05. |

The two dominant explicit P4 PSRAM reservations total **4,522,002 B**:
2,359,296 B of presentation slots plus 2,162,706 B of codec scratch. This is a
source minimum for those successful optional facilities, not the product's
complete PSRAM use. It excludes native planes, loaded VDP assets, managed
components and allocation overhead.

## Worked comparison: ordinary mode 8, mode 20 and browser coexistence

| Rank by explicit extra plane demand | State/order | Persistent explicit PSRAM before plane | Plane request | Minimum largest block relevant to the next step | Result established by source |
|---:|---|---:|---:|---:|---|
| 1 | Browser services established, assets retained, then request mode 20 | **4,522,002 B** plus assets/components | **196,608 B** internal if eligible, otherwise PSRAM pools | internal policy begins with **>=200,608 B total** and >=4,000 B largest; PSRAM requires each selected pool plus 4,000 B reserve | Later mode allocation competes with resources whose large blocks persist even with no browser connected. Source does not establish which capability heap fails in the observed Nurples case. |
| 2 | Mode 20 established before later assets/browser use | snapshot pool may already exist; codec scratch appears at HTTP start | **196,608 B** | same allocation rule, but earlier heap topology | The plane can be admitted before later allocations fragment or consume the candidate heap. This order difference is real; causality for the retained regression remains unproven. |
| 3 | Ordinary mode 8 with browser services | **4,522,002 B** plus assets/components | **76,800 B** PSRAM pools | selected pool plus 4,000 B reserve | Mode 8 needs 119,808 B less plane storage than mode 20 (61.0% less relative to mode 20). |

Mode 20 adds **119,808 B** over mode 8. The pointer-table increase is only
576 B and the four DMA scanlines add 768 B. Thus the known geometry symptom is
consistent with allocation-order sensitivity, but these calculations cannot
distinguish total exhaustion, capability exhaustion, fragmentation, task-stack
failure or a failed fallback transaction. Only capability-specific free and
largest-block observations at the transition could do that.

## Coexistence and exclusion matrix

| ID | Functions | Relationship in the frozen baseline |
|---|---|---|
| A10-CO01 | Drawing + snapshot composition + browser send | Designed to coexist. Drawing owns mutable native rows; output owns composition; HTTP owns the immutable lease/send. |
| A10-CO02 | Browser disconnected + HTTP service running | Coexist. Snapshot slots and codec scratch remain allocated; on-demand snapshots avoid composition when not requested. |
| A10-CO03 | Browser video + WebDAV | Network services coexist, but WebDAV admits one transfer and both share lwIP, SD and internal task memory. No source-wide admission budget reserves memory between them. |
| A10-CO04 | WebDAV mainboard operation + ordinary SD service/application channel | Mutually serialized by admission and the sole console/UART owner. |
| A10-CO05 | Mode transition + drawing/output | Mutually exclusive through detach/join and the native execution guard. Browser may retain an old immutable slot during the transition. |
| A10-CO06 | Legacy/ExCom transport mode + P4 rendering | Rendering exists in either mode; EMOS owns routing and committed mode. Storage and selected keyboard source impose additional admission rules. |
| A10-CO07 | Pre-LCD browser output + future LCD output | LCD is excluded from this baseline. LCD-001 must later demonstrate a reviewed shared-snapshot policy and all coexistence orders; no A10-03 conclusion grants that design. |

## Review inputs, not premature findings

A10-RV01 — The mode operation publishes committed metadata only on success, but
destroys/reconfigures live native objects before all allocations, geometry
checks and task creations succeed. A10-05 must trace the official old-mode and
mode-1 fallback through this partially destructive layer.

A10-RV02 — Browser startup permanently reserves all three maximum-size codec
scratch buffers even when no browser is connected. Raw video remains available
when any codec allocation fails, so A10-05 must review whether eager lifetime
is required or duplicated maximum capacity.

A10-RV03 — The three maximum-size snapshot slots are also eagerly allocated at
first display-service construction. Their fixed capacity makes ownership safe,
but A10-05 must review whether product-lifetime maximum dimensions are required
for an on-demand consumer.

**A10-05 correction:** `StockP4Service::attach` requires the pool to be enabled.
The pool's internal failure path disables cleanly, but the selected stock display
cannot then attach, so this allocation is operationally mandatory. See
`MANUAL-REVIEW.md` A10-MR02.

A10-RV04 — WebDAV startup can create its accept task before application-task
creation fails. The source returns failure without an evident rollback of the
listener/task. A10-05 must confirm whether callers can reach this state and
whether it constitutes a finding.

A10-RV05 — Application-loaded VDP buffers, sprites, bitmaps and primitive
payloads are intentionally workload-dependent. No static calculation proves
their aggregate peak or the capability heap they leave available. A10-04 map
and call-graph evidence plus A10-05 lifetime review must bound this risk before
any target diagnostic is proposed.

## Deferred measurement questions

A10-U01 — Exact linked DRAM/IRAM/flash sections and large static symbols belong
to A10-04's ESP-IDF size/map pass.

A10-U02 — FreeRTOS TCB/queue/semaphore/timer allocation, actual stack high-water
marks, lwIP/HTTP/Ethernet/USB dynamic demand and capability overlap are not
derivable as additive totals from these sources.

A10-U03 — If A10-05 cannot resolve the late mode failure statically, the first
permitted proposal is the already bounded capability-heap diagnostic in
`AI-RISK-AND-TOOLS.md`: free, minimum and largest blocks at defined mode
boundaries plus first failed allocation. It still requires a recorded procedure
and explicit Author authorization before source change or hardware execution.

A10-U04 — LCD-001 retains the required post-audit matrix: early and late mode
20, isolated browser, isolated LCD, simultaneous browser/LCD, assets loaded and
unloaded, successful and failed fallback. The baseline audit must not import
LCD code or claim that this resource map explains its behavior.

## A10-03 disposition

A10-03 is complete as a static architecture and budget pass. It opens five
manual-review inputs and four explicit unknowns, but no repair finding. A10-04
may now run only the frozen automated-analysis set; A10-05 must reconcile its
results with this ownership map before the Author is asked to accept fixes.
