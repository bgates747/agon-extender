# PORT-008 — Paired ExExt CRC removal, r01

## Executive summary

Author authorizes the next implementation tranche on 2026-10-11 after the
minimum-transport review. Remove all CRC calculation and validation from the
EMOS/P4 parallel transport, keeping its electrical handover and storage lifetime
unchanged in this first cut. Use the existing wire discriminator value **3**
instead of 2; keep the sixteen-byte carrier, send zero in bytes14–15 and ignore
those bytes on receipt. This is an experimental paired format, not a production
version or a new negotiation mechanism. Compile and exercise real maintained
owners and linked eZ80 code offline. Do not deploy or claim physical speedup.
Separate COMPLETE/ACK removal is the following tranche, not this one.
CR01–CR05 are complete; [results](CRC-REMOVAL-R01-RESULTS.md) record source,
compile/offline checks, ROM reduction and unchanged bench boundary.

## Authority and research boundary

1. Parent [PORT-008](../PORT-008.md), P08-P05/D01–D03 in the
   [phase contract](PHASE-TIMING-R01.md). The
   [completed review](MINIMAL-TRANSPORT-RESULTS.md) MT01 and first code cut
   identify exact callers/tests. Author's latest instruction authorizes freeze,
   commit/push and implementation; the broad eight-hour goal stays paused.
2. Clean source baseline: Extender f9615acf, EMOS 6c76b4b. Official read-only
   docs f9806bd3cbff6ed5d1c08bef1d51fed11764b86b,
   [MOS API](../../../../../agon-docs/docs/mos/API.md) RST10/RST18,
   [packet contract](../../../../../agon-docs/docs/vdp/System-Commands.md);
   MOS v3.0.2 8336409351ee5314e02801a7b72a4f1bb5282519 and
   VDP v2.16.0 c7ac293d2aa81ddfa693390549bcd909069c8fc3. Stock serial byte
   transport adds no CRC. Detailed source maps remain in the completed review.
3. EMOS owns eZ80 routing and shared pins; P4 EDP owns its counterpart and
   retained parser. Application bytes, replies, callbacks, sysvars, ISR/ABI
   behavior, GPIO mappings, DMA and electrical phases stay as in the baseline.
   Existing scheduling departures remain unresolved; this cut is not full
   stock equivalence. No substitute checksum, replay, renderer/game change,
   wiring change, emulator profile change or bench operation.
4. Ordinary version1 ExCom activation uses shared CRC helpers and remains
   unchanged, including the existing console lease obtained before ExExt entry.
   Only parallel format3 paths stop using those helpers. SD verification is
   unrelated. Preserve historical measurements and exact UART rollback bytes.

## Work items

CR01 [x] — Freeze the paired format and this contract; commit/push owned dirt
and the contract before code. Update current task navigation and EMOS owner
instructions. Leave unrelated other-agent repository dirt alone. P08-D02 stays
open for the later minimum carrier/session/scheduling design.

CR02 [x] — Remove parallel CRC in both owners, including shared request/reply
branches, session, admission, offer, completion, START/POLL/STOP and the private
probe constructor. Mirror wire/session headers exactly. Transmit zeros in the
former CRC slots without validating them; remove parallel dependency on the CRC
header. Retain existing semantic length/direction/identity/phase checks and
physical completion fences. A format2 peer must be rejected before admission.

CR03 [x] — Adapt existing paired host and linked instruction tests. Replace
CRC-corruption assumptions with actual semantic rejection and explicit ignored
reserved-byte checks. Test both directions/boundaries, session/control lifecycle,
missing peer, stale versions, reverse fragments, split commands and real callback
ordering using existing fixtures. Verify ordinary version1 CRC still works.
Tests must not imply all bit errors are detected by the new transport.

CR04 [x] — Build ordinary and ExExt EMOS through profile-owned link/ROM guards;
compile the complete P4 ExExt composition. Run relevant linked output/IRQ/control
checks against the exact new ELF. Record ROM usage versus the same-profile
baseline and exact output identities/hashes in local build evidence. Confirm
parallel owners have no CRC calls and ordinary ExCom code remains. Dirty builds
are exploratory only; clean committed builds precede later qualification.

CR05 [x] — Update current protocol/build guidance, bounded results, handoff and
owner task. Commit/push changes in logical groups, check mailbox and stop for
Author discussion. No flash, hardware timing, production selection/tag or broad
goal resumption. Next proposed code cut removes the separate software completion
receipt while preserving actual native completion and reciprocal pad release.

## Pairing and compatibility

EMOS and P4 must both use parallel wire byte3; format2 is historical and is not
accepted as a fallback. Both versions keep magic EX, sixteen-byte body, current
operations/session/length/direction/status fields and existing console carrier.
An old/new mix cannot negotiate parallel admission. Neither processor gains pad
ownership from a version mismatch or timeout. Ordinary version1 console controls
remain distinct. Future deployment must freeze/install/verify a matching pair,
reuse the 256/4096/4097/8192-byte proof/timing suite and restore UART afterward.
No legacy peer is silently upgraded and no new production version is selected.
