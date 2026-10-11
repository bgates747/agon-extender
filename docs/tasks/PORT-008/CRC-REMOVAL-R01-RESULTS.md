# PORT-008 — CRC-removal r01 results

## Executive summary

Parallel CRC calculation/validation is removed from both EMOS and P4 EDP,
including session, offer/admission, completion and START/POLL/STOP controls.
Both endpoints use CRC-free wire3; former CRC bytes14–15 are sent zero and
ignored. Ordinary version1 ExCom activation retains its CRC. Full EMOS/P4
compiles and bounded host/linked instruction checks pass. The ExExt EMOS image
shrinks by 370 bytes, leaving 474 bytes free. No physical test or speedup claim;
the installed UART pair and production remain unchanged. The next proposed cut
removes the separate COMPLETE/ACK round trip after actual physical completion.

## Scope and implementation

1. [Contract](CRC-REMOVAL-R01.md) CR01–CR05 complete. Contracts were committed
   and pushed before code: Extender `131b7f04`, EMOS `7dd1efd`. Maintained source changes
   belong to their respective component owners. Official read-only references
   and unrelated other-agent work were untouched.
2. Mirrored wire/session headers no longer depend on the CRC helper. EMOS's
   shared console exchange selects zero padding for parallel and retains CRC for
   version1. Its reply, admission and offer constructors use the same distinction.
   P4 request/admission/completion helpers likewise have no CRC calls. A standalone
   parallel Stream test poisons CRC identifiers at compile time. Format2 fails
   semantic version admission; legal metadata changes are not error-detected.
3. All physical phases, DMA/native byte loops, ownership fences, queue sizes,
   sequence/session lifecycle and completion receipt lifetime stay in this cut.
   Ordinary application/VDU/reply formats, renderer and game source are unchanged.
   Partial-output VBlank gating, one-key-per-tick publication and IRQ-disabled
   refusal remain existing departures, not evidence of stock equivalence.
4. The private qualification MOSlet is r02 and reads the shared wire discriminator;
   otherwise it would have rejected the new EMOS descriptor. Its independent
   payload evidence stays diagnostic-only. The host receipt reader accepts
   historical CRC-bearing format2 evidence and CRC-free format3 evidence without
   changing old captures. No private diagnostic is added to ordinary firmware.

## Verification

All executable checks below are offline. Host sanitizers model peripheral/peer
boundaries; linked eZ80 tests execute the actual compiled instructions with
modeled registers/interrupts. Neither establishes electrical timing or FPS.

| Check | Result / scope |
|---|---|
| Paired parallel host suite |16 tests pass; real EMOS/P4 owners, all 1–4096 lengths, directions, semantic rejection, ignored padding, missing peer, physical recovery, split/reverse queues and receipt lifetime |
| P4 peripheral adapter suite |16 tests pass; native DMA/clock/VALID/UART/cleanup and independent data-check endpoints |
| ExCom host regressions |6 P4 +2 EMOS tests pass; version1 CRC rejection, mode lifecycle, display lease restoration, UART owner and parser progress |
| Actual EMOS queue owner |Both ordinary/timing compositions pass, including 4,096 split-return/header/body/STOP cases per composition |
| Linked admission |18,234 host/target vectors pass; actual ELF, ABI/IX/SP/IFF/memory guards, immutable input, no I/O |
| Linked session |950 vectors pass; lifecycle, actual reservation/IRQ guards and cancellation |
| Linked controls |157 cases pass; UART/framer/ISR, sessions, blocks, START/POLL/STOP, bounds, ignored padding, errors/timeouts |
| Linked output |Counted and byte output agree for 1,000 bytes; refusal/ABI/state checks pass; no physical transfer timed |
| Linked VBlank/input |Nested/non-nested cases pass; SD deferral, split input, callbacks and register/IFF restoration |
| Private MOSlet / receipt reader |Target MOSlet builds;11 modeled execution cases and3 evidence-reader tests pass, including historical wire2/current wire3 |
| Full firmware builds |Ordinary and ExExt EMOS pass all profile-owned ROM/baud/ABI/VDU/keyboard/link guards; full P4-PC ExExt HDMI build and source/graph validation pass |

The retained mode-lifecycle harness lacked the already-existing `controlReply`
seam before this cut. Its minimal fake now supplies that method; the current
owner and historical negative control pass. This changes test scaffolding only.
Initial worktree setup required preparing the generated source before the wrapper;
no generated source was edited. Ordinary setup failure detail was discarded.

The separate version-registry validator reports a **pre-existing**
`light2-harness-r02/connectivity.yaml` hash mismatch. Both that file and its
profile are byte-identical to the frozen contract baseline; this transport cut
does not fix or qualify that unrelated hardware record. The diagnostic is retained
locally. No blanket all-repository validation pass is asserted.

## Build identity and ROM

| EMOS composition | Before CRC removal (bytes) | This build (bytes) | Free of 131,072 bytes | Change from same-profile baseline |
|---|---:|---:|---:|---:|
| ExExt stream |130,968|130,598|474|−370 bytes (−0.283% ROM use) |
| Ordinary profile |Not compared|128,695|2,377|No size comparison asserted |

1. ExExt `agon-emos-v0.1.24-b2026-10-11-22-09-26Z`, ROM SHA256
   `d3bf93b4a9ed5af3f144ac04ea45fc9b89545d05934651c038515a19e3b4e0f2`.
   Baseline is retained phase ordinary-control image, same ExExt profile.
2. Ordinary `agon-emos-v0.1.24-b2026-10-11-22-14-22Z`, ROM SHA256
   `294db3428f182a215cb79c1d5abf66e5a9999126114f7ac40c5343fd869d6e7e`.
3. P4 `port-008-stream-r16-b2026-10-11-22-11-17Z`, app SHA256
   `fb041eef959ed3122acc1e82c972a610c415b34985ab437bf239a8b36c66b80d`.
   Full P4-PC HDMI/rolling/PPA/USB composition, retained r15 dependency lock;
   no renderer changes. This compile has no private reset endpoint configured.
4. Builds are **exploratory dirty-source builds**, not clean-input qualification
   or installation readiness. Exact generated sources, source snapshot/input
   inventories, compiler provenance, ELF/ROM and logs are retained locally under
   `agents/crc-removal-r01`. Linked tests use its copied `emos-image`, not whichever
   firmware a later build leaves in the generic builder's output directory.
   No measured-byte identities were renamed and no version/tag/promotion selected.

## Next boundary

Discuss the following code cut: P4 publishes completed payload and EMOS retires
its buffer only after the current native completion/DMA cleanup/reciprocal pad
release, removing the software COMPLETE/ACK exchange. Preserve actual failure
fencing and descriptor/storage lifetime. After committed paired inputs, the
existing 256/4096/4097/8192-byte proof/timing suite remains the hardware gate;
this tranche does not authorize its execution or predict a speedup. P08-D02
retains minimum-control/scheduling questions. Direct mode switching, persistent
UART shutdown and gameplay comparisons remain later work. Bench released and
exact UART rollback/startup remain installed; broader eight-hour goal paused.
