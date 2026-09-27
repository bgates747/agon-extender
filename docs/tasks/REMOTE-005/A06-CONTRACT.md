# R05-A06 — P4 staging and recovery storage

Implement the storage layer locally, without enabling a new network/UART service.
Author restricts this tranche to development and local tests; TRS-80 owns the bench.
No device access, reset, flash, remote test or production selection change.

A06-01 [ ] Define a single-owner, caller-supplied quota and bounded-buffer spool.
Use a dedicated, already provisioned P4-card directory, separate from Agon paths.
The future mount/service owner supplies the directory only after mount validation.
No automatic creation beneath an absent mount; no RAM fallback. Preserve unknown
files and reject an occupied/unrecognized staging directory.

A06-02 [ ] Persist an immutable, checksummed job manifest containing the complete
admission identity, descriptor, declared size and optional expected CRC. Bind every
operation to that identity. Stream consecutive bounded chunks and incremental CRC;
never allocate the whole file. Seal only after sync, close and independent readback.
Expose reads only from a sealed snapshot, never from a partially received upload.

A06-03 [ ] Journal the boundary before remote activation, then explicit confirmed
commit. Loss of acknowledgement, reset or invalidated admission must retain bytes;
neither complete local staging nor a reboot implies mainboard success. New owners
cannot resume old work. Cleanup requires explicit abandonment/release or persisted
commit; interrupted cleanup must remain distinguishable from an unconfirmed job.
Do not claim FAT power-loss atomicity or implement a hidden retry queue.

A06-04 [ ] Test real local filesystem execution plus injected write/sync failures:
empty/binary/chunk-boundary files, quota, missing storage, partial versus complete,
wrong identities, corruption/truncation, invalidation/restart, uncertain commit,
confirmed commit, explicit abandonment and interrupted cleanup. Preserve unrelated
files. Compile the same storage code with the P4 toolchain where available.

A06-05 [ ] Document API/ownership, placement, recovery order, test evidence and
remaining wiring. Keep existing manual listener, P4 HTTP storage, UART protocol,
normal capability flags and approved firmware unchanged. A later integration
tranche must serialize this layer with local-card HTTP operations and implement
active leases/native-client timing before deployment.

## Bounded design choices

1. One spool slot matches the already accepted single admitted mainboard job.
   Retained recovery files occupy that slot and its quota; there is no unbounded
   startup scan or automatic age-based deletion. Quota is explicit in the API;
   production capacity/deadline defaults remain an integration decision.
2. Use existing SD CRC32 code and P4 POSIX/FatFS idioms. Do not reuse local Upload's
   destructor cleanup: it removes partial data, whereas this spool must preserve
   recovery state. Metadata records use explicit little-endian encoding, not C
   struct layout. Closed/synced markers avoid relying on replacement rename.
3. Proposed P4-only directory: `/tmp/extender/spool`, relative to the mounted card.
   This is not the Agon card's reserved path. No current endpoint instantiates or
   exports this module. Integration must reserve/exclude the namespace from the
   existing P4 file-management service before enabling it.
4. References: A03 admission contract and A05 refinement in
   [ADMISSION-CONTRACT.md](ADMISSION-CONTRACT.md); existing local filesystem code
   `vdp/video/extender/storage/local/files.hpp`; current
   [P4 SD guide](../../p4-sd.md). No MOS/VDP API or wire format changes in A06.

Frozen for local execution, 2026-09-27, under Author's explicit development-only
instruction. No new deployable firmware identity or emulator profile is created.
