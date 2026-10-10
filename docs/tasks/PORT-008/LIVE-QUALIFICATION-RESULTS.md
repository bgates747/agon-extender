# PORT-008 LC03-A — Private qualification callers

Software/build checks passed on 2026-10-09. The private EMOS service, diagnostic
MOSlet and P4 storage/receipt caller now exercise the actual paired coordinators
in modeled tests. No physical installation, SD deployment, reset or device
network operation occurred. [Contract](LIVE-QUALIFICATION.md) LC03-A is complete;
LC03-B awaits Author review. [Portable evidence](LIVE-QUALIFICATION-RESULT.json)
records exact artifacts, source snapshots, checks and durations.

## Complete builds and ROM boundary

Worst ROM pressure first; capacity remains 131072 bytes in every composition.

| EMOS composition | ROM used, bytes | ROM free, bytes | Static RAM, bytes | Activation |
|---|---:|---:|---:|---|
| Private qualification | 130984 | 88 | 4079 | Sole admitted diagnostic MOSlet caller |
| Private native coordinator | 130473 | 599 | 4064 | No activation caller |
| Ordinary | 128739 | 2333 | 4058 | No qualification service |

Qualification adds 511 ROM bytes and 15 static RAM bytes over the unactivated
native composition. Patterns, CRC calculation, file output and reporting live
in the 10750-byte SD MOSlet, not resident ROM. Mandatory ordinary/native GPIO,
baud, interrupt and linker guards remain enabled. Probe ELF controls require
exactly one coordinator activation in the private service and one service call
from the existing admitted gateway. Ordinary builds reject these symbols.

The final private EMOS identity is
`agon-emos-v0.1.24-b2026-10-09-20-35-19Z`. Its complete wrapper check took
91.35 host seconds, excluding 1.34 seconds of preparation. The complete P4-PC
browser-output private probe compiled and validated in 527.00 host seconds;
its archived source remained unchanged. Its identity is deliberately
`UNVERSIONED-DO-NOT-DEPLOY`: this is compilation evidence, **not an installation
candidate**, and it does not reproduce the installed HDMI composition.

## Verification

| Check | Passing coverage | Evidence scope |
|---|---:|---|
| Actual paired C/C++ coordinator/service | 82 base; 111 including private probe | Includes 20 two-way blocks, corruption, lost control replies and early refusal; native assembly/UART/SDK scheduling modeled |
| Actual private gateway bounds | 35 cases | Direction, complete MOSlet span, nonzero/max length and failed service |
| Actual diagnostic MOSlet program | 11 invocation/report/failure cases | Host gateway and file I/O; no Agon execution claim |
| Linked eZ80 startup/runtime | 86 cases | Complete private ROM, actual instruction execution; includes probe early refusal and missing-control deadline/fuse |
| Linked native payload / control | 124 / 65 cases | Actual eZ80 assembly/C, modeled inputs |
| Linked UART parking / reservation | 289 / 22 cases | Actual eZ80 instructions, modeled registers/interrupt inputs |
| Actual ELF profile/negative controls | 8 probe; 9 native | Wrong profile, extra/wrong caller and owner checks |
| Host UART/gateway regressions | 4 suites | Existing flow, probe, resident gateway and adapter checks |
| P4 build selection | 13 tests | Private probe requires native boot composition |
| Offline result collector | 2 methods, including 9 negative variants | Synthetic complete/missing/duplicate/corrupt evidence and mirrored-header identity |

Sanitized host tests retain their checks; low-address MOSlet gateway mapping
uses its documented compatible host harness. Case totals overlap: the 111
paired cases include the 82 base cases and must not be added together.

## Prepared physical fixture

The private `parprobe` MOSlet requests lengths 1, 2, 255, 256 and 4096 bytes,
both directions, twice with distinct patterns: 20 blocks. EMOS validates the
entire MOSlet output span, retains fresh session/transaction identity, reserves
UART ownership and invokes the existing native coordinator. P4 prepares its
bounded buffer before offer acknowledgement and logs a completed receipt after
UART return. Neither diagnostic caller owns GPIO or bypasses EMOS admission.

The MOSlet checks every reverse byte and guard, stops at the first error, and
writes CSV under `/agents/extender/results`. It refuses an existing result file;
the foreground file existence check is not an atomic create-only operation.
It does not select a video mode. Invocation remains private and requires the
matching qualification firmware pair; the component README supplies syntax.

Forward MOSlet success alone proves no receiver integrity. The offline
`scripts/parallel_probe_results.py` collector must match all 20 distinct P4 USB
receipts to the Agon CSV and independently generated expected patterns/CRCs.
P4 labels its forward pattern as `na`, rather than claiming an independent
check it did not perform. Guard or descriptor mismatches invalidate the run.

Agon durations are nominal 120 Hz MOS ticks, uncalibrated. P4 durations are
offer-admission-to-receipt microseconds, including coordination and driver
work. Neither measures link-only throughput or establishes electrical timing.

## Findings and next boundary

The boot handover intentionally retains a historical failed-payload marker.
New-block readiness therefore checks the real completed boot grant and UART
phase; treating that old marker as a readiness veto would reject every first
qualification block. The linked ROM test explicitly starts with that marker
set and proves that negotiation is attempted. This preserves existing boot
semantics; block admission resets its own status.

Uncertain PREPARE/COMMIT/OFFER outcomes must enter the physical release fence,
not merely invalidate the logical session. The private service now calls the
existing failed-block recovery boundary and retains reservation until reset.
Modeled lost replies and actual linked missing-control tests cover this path.

LC03-B must establish exact identified installable P4 bytes and restoration
files, refresh bench ownership/wiring, install and verify both components and
the MOSlet, then prove boot release, real two-way blocks and UART input recovery.
First/last-byte alignment, electrical pulse timing, reset/fault recovery and
throughput remain unproved. Formal ExExt, ordinary parallel VDU routing, SD
transport and production selection remain unchanged. New implementation remains
uncommitted pending Author review under the EMOS emulator-coupled-change rule.
