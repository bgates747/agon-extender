# QUAL-006 protocol feasibility review

Date: 2026-10-13.
Status: Offline review complete; implementation feasibility remains conditional.
Owner: [QUAL-006](../QUAL-006.md), Q06-02/04/05/06/07a/08.

## Executive summary

The selected transport and record sizes have plausible implementation paths.
The full contract is not ready to freeze as implementable: paired parser routing,
supervisor lifecycle preservation and measured EMOS ROM cost require proof.
The retained P4 map establishes static placement, not runtime heap capacity.
Start with a costed observation-only publisher; retain the larger job/journal
contract as the later staged target. No accepted architectural decision needs
to be reversed based on this review.

No firmware was built, flashed or changed. No live endpoint, serial device,
benchmark output or running-suite input was accessed.

## Evidence scope

The inspected EMOS checkout is clean at
`76834b9eb58c7b105bbdb6b968c7b971ebd292d8`. Extender source reads use the current
maintained parser/network files; this review does not reclassify the September
audit baseline or claim these source revisions are the installed pair.
The retained RGB candidate map belongs to corrected build
`rgb-001-r13-b2026-10-13-17-52-17Z`; its private manifest/map paths remain in
ignored evidence. SDK asynchronous HTTP support was previously checked at
`b774170ff46c393eeb5e495ea37936038d3f4f4f`.

## Findings

| ID | Finding | Required proof and existing owner |
|---|---|---|
| PF01 | A complete F6 envelope can carry the proposed bounded record, but current service demultiplexing does not recognize it | Q06-04/06: route negotiated QC magic before storage/admission consumers; verify complete-envelope discard and both directions |
| PF02 | EMOS SD receive can copy an unknown record into an active service mailbox | Q06-04/05: classify magic/class before copying; prove observation cannot steal a pending SD slot or grant |
| PF03 | Existing application entry/leave resets service/admission state | Q06-05/07a/08: retain explicit supervisor/job context across child entry/return; preserve ordinary application and utility guards |
| PF04 | Resident EMOS ROM headroom is small and composition-dependent | Q06-02/05: build and link-check a minimal observation implementation against an explicitly selected composition before budgeting the full facility |
| PF05 | P4 draft RAM arithmetic fits no measured runtime budget yet | Q06-06: separate fixed storage placement, task/SDK cost, peak heap and both-board runtime qualification |
| PF06 | Existing telemetry transmitter runs in IRQ context | Q06-04/05: reuse bounded copy ideas only; do not reuse that transmitter as though it satisfied the accepted no-ISR-transmission contract |
| PF07 | P4 SD journal needs stronger ownership than an ordinary hidden file | Q06-06/13: serialize with storage consumers and protect active journal records from API mutation; prove crash/reclaim behavior on both boards |

## Parser compatibility

[The F6 envelope reader](../../../vdp/video/extender/storage/envelope.hpp)
consumes the whole declared body, copies at most 240 bytes, and dispatches only
lengths 20–240. [VDU dispatch](../../../vdp/video/vdu_sys.h) uses that reader at
a real VDU command boundary when the SD-service build capability is present.
Thus proposed 228-byte fixture frames and maximum 240-byte fragment frames fit
the outer length limit. This is not proof for every old peer/build/parser mode.

[P4 SD routing](../../../vdp/video/extender/storage/sd_target.hpp) dispatches to
application, admission and manual SD consumers. The
[admission peer](../../../vdp/video/extender/storage/admission/peer.hpp) checks
`SD` magic for control requests, but some preliminary response routing occurs
by class before the complete control check. QC must receive an explicit earlier
dispatch, not rely on every downstream consumer ignoring it harmlessly.

[EMOS keyboard dispatch](../../../../agon-emos/src/emos_keyboard.c) routes 8D
payloads to [SD receive](../../../../agon-emos/src/emos_sdlink.c). That routine
currently recognizes admission reply class 5 before copying other bounded
records into an active SD mailbox. A QC observation response with class 2 can
therefore occupy that mailbox even if the eventual file validator rejects it.
Separate bounded observation storage and early discriminator checks are needed.

Compatibility tests must cover Legacy and admitted active ExCom, old/new paired
versions, observation during each SD owner, malformed lengths/CRC, unknown class,
interleaved complete records and partial-record transport loss. Existing SD
opcodes/grants remain unchanged. Header arithmetic alone cannot close PF01/PF02.

## Supervisor lifecycle and memory

[Official executable documentation](../../../../../agon-docs/docs/mos/Executables.md)
describes conventional application and MOSlet load regions, not a complete
application heap/stack proof. The retained supervisor restriction remains needed.

[EMOS utility loading](../../../../agon-emos/src/emos.c) bounds the MOSlet at
0x0B0000 with size 0x8000 and rejects busy/non-Core entry. `emos_application_enter`
and `emos_application_leave` reset SD and optional telemetry state and generally
retire admission outside the existing dispatch context.
[MOS execution](../../../../agon-emos/src/mos.c) invokes these hooks around
`exec16`/`exec24`. Generic file execution also selects the MOSlet address by path.

The supervisor must use an explicitly bounded fixture loader and validated
return path, not arbitrary OSCLI/file execution that could replace its own slot.
Its admitted-job context must survive child entry/return without exempting
ordinary applications from existing cleanup or permitting another MOSlet load.
No supervisor implementation or fixture-specific memory proof exists in this
tranche, so generic launch feasibility remains unproved.

## EMOS ROM cost

[The EMOS handbook](../../../../agon-emos/docs/README.md) retains these distinct
software compositions; they are not one interchangeable current size:

| Retained composition | ROM used, bytes | Free within 128 KiB, bytes |
|---|---:|---:|
| Completion-removal ordinary | 128482 | 2590 |
| Completion-removal ExExt | 130334 | 738 |
| Earlier native coordinator | 130473 | 599 |
| Earlier diagnostic probe | 130984 | 88 |

No new build was performed. It is unjustified to claim that lifecycle hooks,
query framing, command parsing and gateway support fit any of these budgets.
The observation-only cost study must declare its source/profile and use the
maintained owner wrappers and mandatory link/ROM guards. Do not relax a guard,
drop a supported composition or move resident authority into a replaceable
utility merely to make the estimate fit. Reuse proven framing/CRC functions
where legal; quantify code and resident RAM separately.

## P4 placement and runtime budget

The retained RGB map exposes low-SRAM heap start 0x4FF28B90 with segment end
0x4FF2CBD0, and high-SRAM heap start 0x4FF56350 with segment end 0x4FFA0000.
The remaining mapped spans are 16448 and 302256 bytes respectively. These are
linker address spans, not measured free heap: task stacks, network/SD/runtime
allocations and capability restrictions consume or constrain them.

The external-RAM linker region is an address window, not evidence of physical
PSRAM size or allocatable free space. The proposed known RAM subtotal of 43008
bytes excludes SDK asynchronous request allocation, worker stack, journal cache,
locks and metadata. Large event/serialization buffers should be evaluated for
PSRAM placement; required internal state must be accounted independently.

The candidate map is for PC HDMI and cannot establish DevKit browser-mode
capacity. Both-board compile/maps, allocation failure behavior, peak memory,
HTTP/input/video latency and exact asynchronous cleanup remain required.

## Feasibility disposition

The observation-only tranche is the smallest useful next cost study: resident
lifecycle state, coherent bounded query/reply, P4 freshness handling and snapshot
access. It does not require remote launch, the full event ring, SD terminal slots
or every fixture schema to be implemented together.

Before contract freeze, prepare a bounded implementation baseline and measured
ROM/RAM cost for that tranche, paired parser regression cases and a concrete
supervisor lifecycle plan for later jobs. Hardware deployment/qualification
remains separately gated; this report provides no bench authorization.
