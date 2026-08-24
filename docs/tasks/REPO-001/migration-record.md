# REPO-001 resulting authorities

This record is completed as live repositories and remotes are updated. Dated
research may retain old branch and commit identities as historical provenance;
the authorities below govern current work.

| Repository | Current role | Resulting main | Remote state |
| --- | --- | --- | --- |
| `agon-extender` | assembled product and cross-component architecture | this record's commit | private `main` |
| `agon-emos` | maintained EMOS product | `b2a6d81` | private `main` published |
| `agon-mos` | upstream-oriented MOS fork | `9562b90` | public `main` published |
| `mos-agondev` | generic AgonDev MOS-family infrastructure | `2cd4128` | public `main` published |

The staged EMOS tree reproduces the previously accepted firmware binary at
SHA-256 `ae0432a84be4be2261095d449627af876c9662d40a08ac334981e12d6dda339f`.

## Verification

1. Fresh remote clones expose only `main` for `agon-emos`; `main`, `spool`, and
   `v233` for `agon-mos`; and `main` plus `dev/sort` for `mos-agondev`.
2. Fresh `agon-mos` does not possess commit `a8dc891`; fresh `mos-agondev` does
   not possess commit `a695599`.
3. Fresh-clone EMOS qualification passed 105 generic tests, 11 restricted
   runtime tests, 46 EMOS tests, build/link checks, emulator boot and shell
   parity, VDP regressions, MOS contract probes, linked EMOS ABI/VDU checks,
   and provider-module validation.
4. The canonical cleaned `mos-agondev` checkout passed 105 generic tests and
   built a verified 102,059-byte stock-MOS image from `agon-mos` `9562b90`.
5. The retained `agon-mos` oversized-packet regression passed all three cases.
6. GitHub reports `main` as the default branch for all three repositories;
   `agon-emos` is private, while the two pre-existing repositories retain their
   public visibility. None has a pull request, release, Actions run, or Actions
   artifact retaining the superseded work.
7. Ref-visible cleanup is complete. GitHub may retain unreachable objects in
   provider storage, and the verified local recovery bundles deliberately
   retain all former refs until the Author accepts Review Gate D.
