# R05-A07 — mainboard directory primitives and client operations

Develop and locally test EMOSlet filesystem primitives plus host orchestration.
No resident EMOS change, bench access, flash or production promotion. Current
manual listener remains Legacy-only; future finite-job integration is separate.

A07-01 [x] Reuse official MOS APIs: ffs_mkdir 0x9B, ffs_unlink 0x97,
ffs_rename 0x98, directory enumeration and existing checked transfers. Reference
agon-docs f9806bd3 `docs/mos/API.md`; stock MOS v3.0.2 remains read-only. Keep
implemented behavior in agon-emos, host client and shared wire contract here.

A07-02 [x] Add capability-gated MKDIR 12, REMOVE 13 and fragmented MOVE 14 records.
Existing operations 1–11 and framing remain unchanged. Feature bit 0x20 advertises
these primitives. MOVE uses the existing A03 descriptor/fragment layout, class 6,
options 0, both paths up to 120 bytes. Each fragment acknowledges next offset plus
completion flag. Only the final validated descriptor renames; ordinary cached
record replies prevent repeating a successful mutation. Another operation/session
retires partial descriptor state. No overwrite MOVE in this tranche; report
collision, never remove a destination. Existing staged replacement remains the
file-copy/overwrite mechanism.

A07-03 [x] Enforce FAT-case-aware scope containment, no root mutation, no traversal,
no mutation of journal siblings or maintained listener paths/ancestors. Reject
mutations during an active file transaction. REMOVE deletes one file or empty
directory only; recursion stays in foreground host orchestration, not eZ80 stack.

A07-04 [x] Add host mkdir/parents, move, remove/recursive and copy/recursive calls
and CLI switches. Require capability before mutation. Copy reuses checked/fast
transfer APIs, with explicit replacement choice and retained backups. Bound tree
depth and validate every returned leaf/path. No directory merging or all-tree
atomicity; emit per-entry outcomes and stop on failure/cancellation. Preserve
uncertain RPC journals rather than submitting a new mutation.

A07-05 [x] Run real C engine tests via host filesystem adapter, fault/replay and
path/collision checks, client tests and AgonDev MOSlet compile/size checks. No
emulator changes in this tranche. Update current guides with development-only
availability, protocol, recovery and remaining deployment boundaries.

Frozen 2026-09-27 under Author's development-only authorization. Build ordinary
unversioned development output only; identify a deployable listener candidate
later under the version policy. Do not overwrite installed/approved artifacts.

Implementation refinement: REMOVE mode 1 performs guard-only validation before
host recursion; mode 0 executes deletion. This prevents recursive removal of
children before discovering that their export root is protected. Local validation
is complete; physical qualification remains under A09–A12. See A07-RESULTS.md.
