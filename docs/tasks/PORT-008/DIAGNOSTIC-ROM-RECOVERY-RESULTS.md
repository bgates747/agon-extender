# Diagnostic MOSlet ROM recovery — results

This records the initial off-bench tranche. The subsequent authorized
[hardware qualification](DIAGNOSTIC-ROM-RECOVERY-HARDWARE.md) passed.

UARTTEST and VDPPOLL now run as SD-backed MOSlets through the existing EMOS
loader. **Net ROM recovery is 1,938 bytes.** The combined private native image
fits with **1,748 bytes free**. All complete firmware wrappers, mandatory link
guards and retained off-bench checks pass. No hardware was accessed or changed.

## ROM accounting

Ranked by least remaining ROM first. Capacity is 131,072 bytes. The unchanged
[AUDIT-008 accountant](../AUDIT-008/account.py) reconciled each ELF, map and
binary. Ordinary ROM use fell 1.48%, calculated as
`(128739 − 130677) / 130677 × 100`. No previous UARTFLOW saving is counted again.

| Composition | Before, ROM bytes | After, ROM bytes | After, free bytes | Static RAM bytes |
|---|---:|---:|---:|---:|
| Private native + block control | 131,262 required; link refused | 129,324 | 1,748 | 4,063, unchanged |
| Explicit C receive reference | Not rebuilt at the immediately preceding checkpoint | 129,313 | 1,759 | 4,058, unchanged |
| Ordinary + block control | 130,677 | 128,739 | 2,333 | 4,058, unchanged |

The refused native figure is required link space, not a previously emitted
firmware image. Recovery does not guarantee the remaining coordinator fits.

| Changed ordinary object | ROM before, bytes | ROM after, bytes | Change, bytes |
|---|---:|---:|---:|
| Resident probe/text object | 3,217 | 1,587 | −1,630 |
| EMOS command dispatch | 6,843 | 6,468 | −375 |
| Admitted diagnostic transport | 471 | 538 | +67 |
| Total | 10,531 | 8,593 | −1,938 |

Other ordinary objects and static RAM are unchanged. Resident text validation,
text exchange, text-probe service and their clock/deadline logic remain intact.
The two extracted algorithm symbols and their diagnostic messages are absent
from all three firmware images.

## Command compatibility and installation boundary

`EMOS UARTTEST` and `EMOS VDPPOLL` now require `/emos/uarttest.bin` and
`/emos/vdppoll.bin`. Their wire requests/replies, baud/flow settings, deadlines,
quiet interval and stopped-clock fuse are preserved. Both share UARTFLOW's
existing gateway adapter and the original clock helper. EMOS retains caller,
Legacy, IRQ, UART and parallel ownership admission and abandoned-lease cleanup.
The only added resident operation opens fixed 115200/8N1 without flow control;
that lease cannot manipulate RTS. Older EMOS refuses the new operation.

The two commands now use the common MOSlet acquisition-failure message and
return 15 for diagnostic/service/mode/ownership failure, rather than the former
resident branch's separate error messages/codes. They omit the resident build
identity preamble. Missing files use normal load errors; extra arguments return
19; `--version` performs no transport operation. Neither command takes over an
active keyboard owner. See the maintained
[component guide](../../../../agon-emos/projects/uartprobe/README.md).

| Disk utility | Binary bytes | Code/data/BSS end | Slot space left, bytes |
|---|---:|---|---:|
| UARTTEST | 9,523 | B25AF | 23,121 |
| VDPPOLL | 9,522 | B25AE | 23,122 |
| UARTFLOW, rebuilt shared adapter | 9,351 | B250D | 23,283 |

All have valid ADL MOS headers and load at B0000. Remaining slot space must
also accommodate heap/stack; it is not measured worst-case stack headroom.
No utility has been copied to SD or tested against a physical peer this tranche.

## Validation and retained identities

| Check | Result |
|---|---|
| Complete ordinary, native and reference wrapper/link guards | All pass |
| Original algorithms against actual resident lease, modeled UART leaves | UARTTEST 15, VDPPOLL 14, UARTFLOW 15 scenarios pass |
| Envelope, entry arguments/version, old-firmware refusal, slow-lease bounds/RTS/cleanup | Pass |
| Retained text service, loader, gateway, keyboard, console, admission, mode and source/provenance regressions | Pass |
| Linked eZ80 diagnostic gateway | 298 ordinary / 300 private cases pass |
| Linked eZ80 block control | 65 cases on each ordinary/private image pass |
| Linked native payload / boot runtime / receive reference | 124 / 26 / 38 cases pass |
| Paired EMOS/P4 block and session owners | 689 / 218 cases pass |
| Actual-ELF profile/corrupt-instruction refusal controls | 7 cases pass |

The private diagnostic fixture first verifies acquisition refusal before a
release grant, then models an acknowledged grant. Its parallel-contention
expectation permits exactly the required read-only READY sample; no GPIO write
is admitted on refusal. Host and CPU models do not prove electrical timing,
real peer deadlines, whole-system SD loading or performance. No P4 source
change/rebuild was needed for this extraction.

Final EMOS builds are v0.1.24 development identities dated 2026-10-09:
ordinary b16-28-01Z, native b16-28-28Z, reference b16-28-57Z (abbreviated here).
[Machine-readable results](DIAGNOSTIC-ROM-RECOVERY-RESULT.json) record full
identities, source closure, exact hashes, per-run start/end/duration, and evidence
under ignored `agents/port008-diagnostic-rom-recovery/`. The existing pinned
builder and accounting tool were reused unchanged.

Mandatory checks caught a source guard whose text exception depended on the
removed VDPPOLL branch. The guard now bounds the text branch itself and checks
the diagnostic gateway's MOSlet/Legacy/busy admission. An existing translation
inventory expectation also omitted the already-maintained private assembly
leaf; it now distinguishes translation inventory from ordinary link selection.
Mutation controls and all linked owner checks still pass; no guard was skipped.

The [contract](DIAGNOSTIC-ROM-RECOVERY.md) is complete for off-bench recovery.
Real utility loading/peer qualification and live parallel drain/park/native/
restore integration remain open. Bench, SD, device networking, installed bytes,
production selection and unrelated EMOS work are untouched. Emulator-coupled
changes remain uncommitted for Author review.
