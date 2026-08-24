# REPO-001 migration inventory

## Preserved inputs

1. `agon-mos` official base: `8336409` (`v3.0.2`).
2. Former mixed EMOS source: `a8dc891` on `dev/emos`.
3. `mos-agondev` generic baseline: `c4b1f7a`.
4. Former mixed EMOS qualification history: `a695599`, including the earlier
   returned milestone `b12fcab`.
5. Frozen Extender input to the returned work: `10f2eb2`.

Verified bundles of every pre-migration ref were created before reconstruction.
Their machine-local paths are intentionally not tracked. They remain recovery
artifacts until the Author accepts Review Gate D.

## Accepted allocation

1. `agon-emos`: upstream-shaped EMOS source, module/container tools, provider
   fixtures, EMOS tests, product contracts, research, tasks, qualification
   evidence, hardware procedure, build entry point, and source profile.
2. `agon-mos`: official lineage plus the independently valid oversized VDP
   packet discard correction and its source regression test.
3. `mos-agondev`: generic translator, build/link/runtime machinery, emulator
   setup, source and binary audits, ABI/contract probes, generic regression
   tests, and explicit product-profile interface.
4. `agon-extender`: assembled-product architecture, EDP source, hardware,
   transports, compatibility requirements, cross-component tasks, and system
   qualification.
5. Generated source, objects, maps, binaries, emulator media, and temporary
   worktrees: excluded from maintained migration content.

## Ref disposition

1. Delete `agon-mos` local and remote `dev/emos` after publishing `agon-emos`.
2. Delete the temporary local `agon-mos` `dev/port-200` worktree/ref. It has no
   distinct source content.
3. Replace `mos-agondev` `main` with the reconstructed generic lineage using an
   exact force-with-lease, then delete local and remote `dev/emos` and
   `dev/port-200`.
4. Retain `mos-agondev` `dev/sort`; it is unrelated generic qsort work.
5. Retain `agon-mos` `spool` and `v233`; they predate this migration and were
   not classified as misplaced EMOS work.

Deleting or replacing refs provides ref-visible cleanup. It does not prove
immediate erasure of unreachable GitHub objects, caches, reflogs, recovery
bundles, or unknown copies.
