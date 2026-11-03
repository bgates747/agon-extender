# Whole-file P4 PSRAM source for parallel uploads

- Status: Accepted
- Completeness: Complete
- Date: 2026-11-03
- Related task: BENCH-013 B13-D02 / PORT-008

P4 retains the complete upload source in PSRAM so the eZ80 can receive one
admitted parallel payload and pause its clock for Agon SD writes. The Author
selects this prototype over streamed P4 SD refills. This decision does not claim
physical qualification or change the selected production installation.

## Decision

1. The host finishes staging the upload on P4 SD using the maintained file
   service. P4 validates capacity and retains the complete source in aligned
   PSRAM for the lifetime of its DMA transaction before payload admission.
2. EMOS owns admission, UART parking, shared pins and the eZ80-generated clock.
   The foreground file utility receives small slices and writes them through
   existing MOS filesystem calls while that clock pauses. One payload admission
   covers the complete file; slices do not negotiate separate UART admissions.
3. P4 stops loop DMA only under the qualified exact-length/VALID ownership
   contract. Borrowed source storage remains live until DMA stops and pads are
   released. P4 refuses insufficient source capacity before admission.
4. File policy remains in the foreground utility and P4 file service. Preserve
   the UART baseline, host workflow, explicit failure and non-replay semantics.
   Do not add a processor-link checksum, per-byte acknowledgement, application
   GPIO bypass or silent streaming fallback.

## Consequences

P4 temporary source RAM scales with file size, plus alignment and DMA
resources. This avoids a new source-refill protocol and permits filesystem
pauses without P4 refill races. Bounded P4 SD refill remains a separate future
alternative. Implementation, resource costs and physical evidence belong to
[the reverse-upload tranche](../tasks/PORT-008/REVERSE-UPLOAD-R01.md).
