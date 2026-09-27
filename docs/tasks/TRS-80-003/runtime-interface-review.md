# Detached runtime interface owner review

## Executive summary

The proposed guest-disabled Ethernet/SD/resource-reporting composition is
consistent with Extender's current interfaces. This is a source/document review,
not Author architecture acceptance or hardware qualification. Media leases, raw
HID and display-provider APIs remain future work. The peer owns changes to its
SHARE-01-04 document and MAME composition.

Reviewed 2026-09-26 against Extender commit ea8b9f7e (Ethernet extraction
2ecd55b8) and the peer SHARE-01-04 runtime-interface proposal. No build or bench
operation performed.

## Review findings

| ID | Disposition | Required clarification |
|---|---|---|
| RI01 | First-candidate lifecycle supported | Consumer initializes Arduino once; a process-long worker owns Ethernet and starts SD HTTP once. Callback only notifies. Keep server alive through link loss; never stop Ethernet underneath it. Initial DHCP deadline reports degraded state, not automatic reboot. Current startHttp returns success only after route registration; failure cleans its partial server. |
| RI02 | Status scope clarification | startHttp success means server readiness, not card readiness. Mount/status implementation is private to the HTTP translation unit. The platform worker must not invent a callable mount accessor or directly race HTTP mount state. Serial can report server readiness; use existing HTTP status for card state until a common owner API exists. Do not promise SD HTTP task stack telemetry through the current public header: it exposes only startHttp. Report owned worker stack now; shared-server telemetry needs an owner interface. |
| RI03 | Future lease identity | FAT is case-insensitive and can expose short-name aliases. A raw path-string set is insufficient. Resolve stable canonical file identity (including aliases), check ancestor boundaries by components, and define both source and destination exclusions for copy/move/replacement. Keep staging/backup siblings protected. |
| RI04 | Future lease atomicity | Lease admission and conflicting filesystem operations must share arbitration. Hold a reservation for the whole operation, including open handles and streamed responses; a preflight check followed by an unlocked open/mutation races guest admission. Preflight recursive operations before mutation; do not partially delete then discover a leased descendant. This is exclusion, not a promise of power-loss atomicity. |
| RI05 | Future read scope | Exclusive guest image ownership must also cover content-search reads and recursive copies, not just GET /file. Explicitly decide whether stat/name listing is permitted and how recursive queries report excluded descendants. Do not silently return success with an incomplete search. Independent files can remain accessible. |
| RI06 | Close/failure semantics | Flush writable handles and confirm all guest handles closed before release. Retain exclusion and report a fault on ambiguous close. Guest reset retains leases while handles remain open. Before writable guests, define process-restart recovery; in-memory leases alone do not prove a dirty image safe after reboot. |
| RI07 | Ownership confirmed, API not supplied | Extender owns shared SD/mount/exclusion, USB acquisition/source arbitration and reusable snapshot/codec/transport implementation. MAME owns lifecycle, guest mappings, render/input adapters and UI. Generic raw HID and renderer-provider interfaces are not yet independently callable contracts. No console VDP/EMOS routes should be pulled in to obtain them. |

The first candidate can proceed through the peer's review gates without RI03–06
implementation because it admits no guest or image opens. Those requirements
must be settled before media integration. No need to expand this first candidate
into guest, input, rendering or writable-image work.

## Source basis

1. [Ethernet lifecycle](../../shared-p4-services.md) and
   [implementation](../../../vdp/video/extender/network/devkit_ethernet.hpp).
2. [SD HTTP public boundary](../../../vdp/video/extender/storage/local/http.hpp)
   and [implementation](../../../vdp/video/extender/storage/local/http.cpp):
   lazy private mount, single HTTP task, content search, route registration.
3. [File primitives](../../../vdp/video/extender/storage/local/files.hpp):
   path decoding, sibling staging/backup, recursive mutations; no image leases.

The peer mailbox reply carries the exact cross-project document location without
embedding a private machine path here. This review does not change the shared
API, production selection or installed candidate.
