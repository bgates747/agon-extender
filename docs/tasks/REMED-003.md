# REMED-003 — Reproduce Fab directory-backed filesystem contract failures

## State

- Status: Identical binary passes on physical Agon and raw image, fails both contracts in upstream Fab directory mode. Report ready for Author review; unsubmitted.
- Started: 2026-09-10
- Finished: --

The Author requests a simple test for Tom: use the same executable on hardware
and in Fab, then report the differing create-new and sync results. This arose
while implementing [AUDIT-005](AUDIT-005.md). It is independent of that UART
benchmark; do not change its firmware or relax its storage checks to make the
emulator pass. Publication to the upstream issue tracker is not yet performed.

## Bounded work

1. [x] Build a stock-MOS-API SD application that creates an isolated run
   directory, verifies an existing file rejects `FA_CREATE_NEW` with
   `FR_EXIST`, and verifies `f_sync` succeeds on an open, written file.
   Close/reopen and compare sentinel contents; save explicit numeric results.
2. [x] Run the identical binary in Fab directory mode and raw FAT-image mode;
   record emulator/MOS/binary identities, commands, outputs and scope limits.
   Keep the canonical upstream checkout read-only.
3. [x] Deploy the binary alongside the UART benchmark and obtain Author
   hardware results from the currently installed EMOS, without reflashing.
   Confirm whether its FatFS implementation matches stock MOS before drawing
   an upstream comparison. Returned SD result and sentinels verify both checks.
4. [x] Finish a concise, reproducible issue draft for Tom, separating observed
   behavior from source interpretation. No hardware PASS may be inferred from
   an emulator result; leave the report unsubmitted for Author disposition.

## Initial source evidence

Fab reference `fbb7d7ca887a06966ca8a62ed22272409a5ab640`,
`agon-ez80-emulator/src/agon_machine.rs`, opens a create-new request using
Rust `OpenOptions::create` rather than `create_new`; an existing file is
therefore accepted. Its mapped FatFS dispatcher does not trap `_f_sync`,
although the host-backed `FIL` is synthetic and cannot be validated by the
real MOS FatFS function. The initial benchmark returned `FR_INVALID_OBJECT`
(9) on sync. The standalone reproducer must establish these independently.

The UART-peer emulator used by AUDIT-005 is a project-owned derivative of
that reference. Test the unchanged Fab reference as well before attributing
the result to upstream. Do not edit its existing local SD tree.

The standalone test now reproduces the failures with the unchanged upstream
executable, not just the UART-peer derivative. Raw-image mode returns the
expected create-existing=8 and sync=0; directory mode returns 0 and 9. Closing
and rereading the sentinel succeeds in both modes. Source, exact binary
identities and reproduction steps are in the [issue draft](REMED-003/issue-draft.md).
EMOS's `src_fatfs/ff.c` matches official MOS v3.0.2 byte-for-byte. Physical
results now agree with raw-image mode. The returned SD's binary hash matches
both emulator runs, and CREATE.DAT/SYNC.DAT contain the expected sentinel.
No stock firmware flash was needed for this comparison.

The binary is deployed at `/extender/fscheck/FSCHECK.BIN` on the Author's
SD. The initial card return contained no filesystem-probe result; its failed
UART benchmark is a separate failure, not evidence against this test. The
second startup ran FSCHECK automatically before the short pixel diagnostic.
The returned `R00001/RESULT.TXT` passes; its original bytes, both sentinels and
collection hashes are retained in [hardware evidence](REMED-003/evidence/hardware/).
The report is complete for this comparison and remains unsubmitted for review.

## Current disposition and reuse

The report remains an unsubmitted comparison of the exact recorded emulator and
firmware, not a claim about every later Fab release. Current operation uses the
[handbook](../README.md); no new emulator build, test or upstream submission is
pending under this documentation review. Preserve the original identical-binary
comparison. Before any new physical run, review the fixture's receipts under
`/extender/fscheck` against [SD layout](../sd-layout.md) and identify a separate
refreshed candidate rather than modifying frozen evidence.
