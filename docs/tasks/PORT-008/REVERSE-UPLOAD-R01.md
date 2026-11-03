# Parallel uploads — reverse bulk and file-service integration r01

Improve host-to-mainboard deployment by reusing the staged upload service and
replacing its P4→eZ80 UART payload leg with a qualified eight-bit parallel path.
The Author authorizes this tranche on2026-11-03 after accepting BENCH-013's first
listener-adoption tranche. Keep the existing host workflow and UART baseline;
speed, scarce EMOS space and one admission per requested payload remain central.

## Authority and boundaries

1. Extender retains the Author-assigned physical checkout; other projects may
   queue but receive no automatic slot. Send no peer progress/instruction
   notifications until the Author opens the bench for their use. The Author
   requests a question dialog when a completion/review needs their attention.
2. Preserve the installed accepted sequential-reader utility and exact incoming
   firmware/startup/modes. Source assessment and host checks may proceed now.
   A new wire/admission or DMA-completion design must resolve the remaining
   architectural decision before dependent firmware implementation or flash.
3. Implementation owners remain Extender/P4 and agon-emos/eZ80. The public MOS
   API, ordinary VDU routing and native mainboard VDP are not replaced. EMOS
   retains all shared-pin/admission ownership. No raw application GPIO bypass,
   software CRC/checksum, per-byte acknowledgement or uncertain replay.

## Bounded research précis

1. Official read-only baseline: documentation
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOSv3.0.2
   `8336409351ee5314e02801a7b72a4f1bb5282519`, VDPv2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. MOS/VDP references are clean at
   those tags. [GPIO](../../../../../agon-docs/docs/GPIO.md) establishes physical
   sharing; [ffs_fwrite](../../../../../agon-docs/docs/mos/API.md#0x83-ffs_fwrite)
   supplies filesystem result and byte count. Do not replace this with a new
   resident filesystem implementation.
2. Source assessment starts from Extender `8aa3245d39f62202719226db64b67e305c91688b`
   and EMOS `08301e6d28f5cdd6a8bb01aa6806b6d4ddaf816c`, not an assumption that
   either HEAD equals installed firmware. Installed artifact identities and
   rollback evidence remain in the ignored bench record.
3. EMOS [native byte loop](../../../../agon-emos/src/emos_parallel_native_body.inc)
   generates CLOCK in both directions; reverse samples Port C after the edge
   pair. READY is sampled as an abort level, not a per-byte acknowledgement.
   The guard/coordinator bounds a call to4096 bytes and returns ownership to
   UART after each admitted block. It cannot be called repeatedly while
   claiming only one whole-file admission.
4. P4 [native adapter](../../../vdp/video/extender/transport/p4_native_payload.cpp)
   uses external-clock eight-bit PARLIO TX, one queued transaction and internal
   DMA payload storage. Its guard/egress cap is4096; ordinary return buffering
   and the current EMOS256-byte fetch policy are not a bulk-file contract.
   Preserve byte/VALID completion and pad-release distinctions.
5. The pinned ESP-IDF5.5.5 TX driver explicitly supports external PSRAM buffers
   in `components/esp_driver_parlio/src/parlio_tx.c`. Ordinary non-loop TX uses
   a0x7FFFF-bit frame limit on P4, so raising4096 alone cannot admit a65536-byte
   non-loop transaction. Loop TX can link the payload circularly and does not
   produce ordinary transaction-done completion. It requires a different,
   justified exact-length/VALID stop contract. Software support is not physical
   qualification; the earlier project PSRAM experiment remains unqualified.
6. [Official TX documentation](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/parlio/parlio_tx.html)
   defines borrowed source lifetime through completion and loop-buffer behavior.
   Local pinned driver, P4 HAL and SoC capability files own exact implementation
   details; keep their hashes and excerpts in the ignored research receipt.
7. The accepted file utility has5277 bytes between BSS end and its MOSlet limit
   for shared heap/stack. A4096-byte extra buffer leaves1181 bytes before new
   code/runtime costs; a full upload cannot live there. The utility can write
   bounded slices through existing FatFS calls. Because EMOS generates CLOCK,
   it can stop clocking while the utility writes a slice without demanding a
   per-byte P4 acknowledgement; this requires a new retained transfer owner.

## Work and gates

1. RU01 — Verify exact source/SDK limits, current reverse cores and relevant
   host failure/bounds checks. Retain no fabricated hardware rate or headroom
   claim. Quantify how many4096-byte admissions representative files need and
   the source-storage lower bound for a whole-file P4 DMA source.
2. RU02 — Resolve BENCH-013 B13-D02 with a concrete recommendation before new
   carrier code: keep the existing host/staging/file semantics and choose the
   bounded whole-payload implementation below. Record an accepted material
   decision in its ADR/architecture owners. Allocate no new global MOS ABI or
   wire identifier until that contract is explicit.
3. RU03 — After RU02, implement the selected carrier in the owning source
   checkouts. Keep P4 file I/O and EMOS utility file policy outside resident
   loops where practical. Bind logical payload length, buffer lifetime, busy
   refusal, exact finish, failure fencing and non-replay behavior. Report ROM,
   RAM, P4 storage and eZ80 CPU costs.
4. RU04 — Exercise actual retained cores/SDK boundaries and linked eZ80 code:
   exact first/last bytes, short/tail lengths, filesystem pauses, DMA cleanup,
   owner/busy/refusal and partial failure. Then build identified matched
   candidates through owner wrappers and all mandatory link/ABI checks.
5. RU05 — Prepare a finite physical comparison only after required protocol,
   deployment, reset/rollback, SD-layout and test-lifecycle review. Preserve and
   verify incoming components. Prove the reverse source and full received file
   bytes outside timing. Keep payload, admission, SD/HTTP and total deployment
   elapsed separate; compare matched UART and parallel variants.
6. RU06 — Restore exact incoming components unless the Author explicitly adopts
   the tested change, restore normal CLI/cursor/input and idle services, and
   retain Extender checkout. Publish scoped results/limits; raise the requested
   attention dialog. No full suite, peer notification or bench release follows
   automatically from completing this tranche.

## Pending carrier decision — B13-D02

Recommended first prototype: P4 retains one complete admitted upload in aligned
PSRAM for DMA, while the eZ80 file utility receives small slices and writes them
to Agon SD between clocking intervals. One payload admission covers the file;
there is no per-slice UART negotiation or acknowledgement. The P4 validates
capacity before admission and never promises a file larger than its actual
retained source capacity. This spends P4 PSRAM to keep the first implementation
small and avoid streaming refill races. The exact-length loop-DMA stop, source
release and buffer lifetime require explicit implementation/qualification.

Alternative: P4 fills/recycles bounded source buffers from its SD spool during
the same admitted file transfer. This saves whole-file PSRAM and handles larger
uploads, but needs a proved pause/refill protocol and protection against TX idle
data being clocked while a refill is late. Existing abort-only READY semantics
do not already implement that behavior. Do not silently use repeated4096-byte
OFFERs as the production alternative to the Author's whole-request requirement.

This decision selects storage/physical-completion behavior, not merely a C++
interface name. Preserve the shared UART/parallel semantic contract, and present
this one concrete choice before starting dependent implementation.
