# R05-A07 local directory operations results

Directory primitives and recursive host operations pass local validation and
compile as a MOSlet. No resident firmware changes, hardware access, deployment
or production promotion occurred. The installed listener remains unchanged.

| Check | Result | Scope |
| --- | --- | --- |
| EMOS full suite | 129 passed | Correct A05 prepared EMOS baseline selected |
| File engine subset | 42 passed | Checked and fast variants, real C engine |
| Host client suite | 12 passed | Includes real C filesystem adapter |
| AgonDev MOSlet build | Passed, 21981 bytes | Unversioned development compile |
| Binary growth versus v0.2.0 | 2738 bytes | SD/application bytes, not resident ROM |
| Remaining heap/stack region | 8216 bytes | BSS ends B5FE8, region ends B8000 |
| Resident ROM growth | 0 bytes | No resident source changes |

The engine tests cover full 120-byte source/destination paths, fragmented move,
replay, malformed/interrupted descriptors, busy transactions, collisions,
nonempty directories and protected paths. Existing transfer tests retain
interrupted-replacement and recovery coverage. Host tests cover nested/empty
directories, binary copy, explicit replacement/backups, per-entry completion,
cancellation, recursive removal, export-root preflight and old capability refusal.

A first full-suite invocation selected the default stock MOS prepared tree and
failed EMOS provenance checks; selecting the retained A05 EMOS prepared baseline
passed all 129 tests. No generated source was changed to satisfy those checks.

MKDIR/REMOVE/MOVE are capability-gated. REMOVE has a guard-only preflight before
recursive traversal. MOVE never overwrites. COPY uses existing checked transfers
unless fast mode is explicitly requested; replacement retains recovery backups.
Recursive operations stop at failure, report completed entries, and are not
whole-tree atomic. Host traversal is bounded to 16 levels. File copying uses the
existing host whole-file buffer; the future P4 integration must use its bounded
spool instead. Neither WebDAV wiring nor finite-job/ExCom integration is claimed.

No emulator profile/module was changed or executed. Physical FAT, UART and
end-to-end qualification remain in A09–A12 after bench release. Production remains
unchanged. Local generated logs are retained in the ignored agent evidence silo.
