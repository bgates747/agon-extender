# BENCH-025 — Own fixture reports from invocation through SD cleanup

Keep each fixture's SD workspace reusable and move attempt history to the Pi.
The runner should be able to prove which attempt produced a report, recover
collection without replaying the fixture, and remove an owned SD copy only
after the Pi has safely recorded it. Smith approved the plan on November 27,
2026, with the revised D03 cleanup rule below.
Extender owns the shared design and runner. Nurples owns its pilot fixture
and the meaning of its timing measurements.

## Starting evidence

The Nurples Earth direct retry reported `561 skipped / 5105 VBlanks` and
`EARTH AB FAILED`. Nurples reports that the on-card `POSE.BIN` instead held
`525 / 5069` and a clipped row 4. The retained inspection of
`/test/earth-pose-r01/direct/POSE.BIN` independently records the expected
27,297 bytes and the validator's rejection, “VBlank interval not exactly
representable.” The path and length therefore cannot associate the file with
the retry. Keep the mismatch distinct from the cause of the fixture failure.
The Nurples evidence index is
`earth-pose-r01/bench-parlio-20261127-r01/inspect-direct-report/finding.json`
under that project's ignored build records. The coordinated evidence return is
`2026-11-27_15-29-18_nurples_fixture-report-lifecycle-plan`.

The [shared runner](../../scripts/olimex_bench.py) checks for fresh paths
during stage and collects named reports as part of the run phase. A stage
receipt cannot establish that a reusable output is vacant immediately before
a later invocation. Build on the [bench procedure](../operations/olimex-bench/README.md),
[fixture authoring guide](../operations/olimex-bench/AUTHORING.md), and
[SD layout](../sd-layout.md).

## Proposed contract

### Paths, attempt identity and fixture writes

- The Pi runner binds a distinct attempt ID to the manifest, fixture build,
  actual firmware receipt, arm, exact SD paths and reservation. It journals
  that binding before dispatch. Each project/fixture uses a reusable scratch
  location with one fixed slot per declared output. Pi evidence directories
  remain unique per attempt. The runner rejects aliases, FAT case collisions,
  report/input overlaps and paths outside the approved output namespace.
- The runner can reuse a program or shared asset when a completed stage
  receipt binds the host content and exact SD path and custody history
  supports reuse. If reuse is uncertain, handle it through the normal staging
  and stop rules. Neither reuse nor report collection adds blanket input
  rereads, transfer CRCs or substitute digests. Use the job's admitted carrier,
  with required two-way PARLIO on the normal production stack.
- Under the existing operation lock and lease, the runner obtains a fresh
  metadata-only absence check just before each explicit invocation, after any
  reset or stage. It establishes idle SD writers, then preserves exclusive
  operator control through dispatch and collection. A collision blocks
  launch. The runner may archive the existing bytes as stale or unassigned
  evidence under the appropriate disposition. It cannot assign them to the
  new attempt or claim ownership from a basename or matching length.
- A new fixture receives the attempt ID through a qualified invocation
  argument, echoes it in a versioned status record, and includes it in a
  small versioned report header or envelope. The fixture writes outside its
  timed workload. An opt-in helper exclusively creates the declared path,
  checks each write's status and byte count, checks close, and emits the
  attempt, filename, total expected/actual bytes, failure stage and original
  error where the target API exposes one. Keep the first I/O error and any
  close error. The helper cannot report saved after a short write or failed
  close. Confirm support and footprint of the public MOS/FatFS
  `FA_CREATE_NEW`, `ffs_fwrite` and `ffs_fclose` route against both selected
  builds and the fixture SDK. A plain buffered `fwrite` return is insufficient.
- The fixture owns workload and timing status. A failed workload or invalid
  trace may still produce a diagnostic report. The runner's generic
  validation binds serial and report identity, path and lengths. The fixture
  owner supplies the format decoder and semantic assertions, including
  serial-versus-report totals for Nurples. Keep the app verdict, I/O status,
  validation and cleanup separately visible.

### Collection, durability and recovery

| State | Required evidence and action |
| --- | --- |
| Saved | The fixture reports a matched attempt and successful close. A missing or incomplete witness remains unknown or failed, even if SD metadata shows a file. |
| Collected | The Pi archives each transferred report once, with length and local SHA-256, the attempt binding, terminal or failure transcript, serial totals where available and transfer receipt. Use temporary local files, file sync, atomic publication and directory sync before marking the archive durable. |
| Validated | The Pi records the result of identity, shape and fixture-specific checks. Keep rejected bytes with the reason. Do not turn an archived or cleaned report into a test pass. |
| Cleaned | Under the same custody and writer fence, the Pi reopens the durable archive record, confirms exact file and attempt ownership, journals delete intent and uses exact-file removal through the admitted SD service. Record the acknowledgement or a safe subsequent presence check. |

The runner requires a durable archive and recorded verdict before cleanup.
It may automatically remove a semantically rejected report when it can
conclusively bind that exact SD file to the attempt and has durably archived
both its bytes and rejection reason on the Pi. Retain stale, unidentified or
otherwise uncertain SD copies pending disposition. Lost retrieval, incomplete
Pi archival, uncertain ownership, or uncertain custody leave the SD copy
intact. Preserve report and runner failure evidence independently.

Resume collection and cleanup as explicit actions on the original attempt
under valid custody, the operation lock and the appropriate stop-rule
disposition. Require a joined previous worker and a proved quiescent fixture.
Neither action issues `LOAD` or `RUN`. After interrupted deletion, the
runner can record a proved absent file as already removed if the durable
archive and delete intent match. If still present, retry exact removal only
when continuity proves the path still names the archived object. A gap in
custody, a reset with uncertain writes, or an intervening writer blocks
speculative deletion. Reconciliation may inspect the exact report under the
normal recovery authority. Reuse the durable archive when available, avoiding
a second download on the healthy path.

Operator display should answer where each file went. For example, after an
illustrative pilot attempt, the runner could show:

| Arm and attempt | Agon SD | Pi evidence | Status |
| --- | --- | --- | --- |
| Direct 003 | `/test/nurples/earth-pose/direct/POSE.BIN` | `<job-evidence>/attempts/003/direct/POSE.BIN` and lifecycle receipt | Saved, collected, validated, cleaned |
| Sync 004 | `/test/nurples/earth-pose/sync/POSE.BIN` | `<job-evidence>/attempts/004/sync/POSE.BIN` and archived rejection reason | Saved and collected, timing rejected, exact owned SD copy cleaned |
| Sync 005 | `/test/nurples/earth-pose/sync/POSE.BIN` | `<job-evidence>/attempts/005/sync/collision.json` | Launch blocked. Unidentified SD copy retained pending disposition |

### Compatibility and existing SD backlog

Keep existing manifests and human-start jobs on their commissioned behavior
until migrated explicitly. A fixed-name older fixture can opt into absence
check and archive management only after its single invocation and sole writer
are proved. Its record must say that provenance is based on controlled
invocation and path freshness. A missing receipt or ambiguous retry blocks
automatic attribution and cleanup. New fixtures can adopt token correlation
without changing existing application-specific report semantics.

Inventory the historical backlog separately and read-only, using path, size,
owner, current references, and evidence or recovery purpose. Produce a reviewed
keep/delete list with exact paths and separate approval for removal. Protect
`/autoexec.txt`, EMOS and its listener, firmware and recovery files, other
owners' data, current evidence, and `/test/earth-ab-vl1/control`. Nurples'
current pose binaries still load that historical directory's assets. Unknown
ownership or references mean keep. Compare metadata-only inventory through
the ordinary bench route with inventory from a card Smith mounts on Oryx.
Any Oryx cleanup is a separate, approved operation with an identified mount and
exact reviewed file list. Neither route includes recursive deletion.

## Proposed deliverables and acceptance

- BENCH-025-001 [ ] Pin the manifest and fixture contract under the accepted
  decisions below. Compare the public MOS API and SDK in the selected
  firmware revisions. Record the command transport,
  supported path and size limits, exact deletion primitive, archive durability
  and lease/lock behavior.

- BENCH-025-002 [ ] Add opt-in lifecycle support at the runner's ordinary
  entry points. Cover the supported result sets and failure paths offline.
  Tests must prove that a stale same-size report and case-folded collision
  block dispatch, a reused filename cannot override a token mismatch, a
  second owner or live worker blocks recovery, and an unchanged confirmed
  asset needs no fresh transfer. Prove exact cleanup of a conclusively owned
  rejected report only after durable archival of bytes and reason. Prove
  retention of an unidentified or uncertain report regardless of its size.

- BENCH-025-003 [ ] Qualify the reusable fixture writer on selected EMOS/MOS
  builds. Verify create collision, short write, failed close, exact recorded
  counts and error codes, and no report-file work inside the timed loop.
  Replay the historical POSE mismatch and an invalid timing trace as
  distinct negative cases. Prove legacy fixtures and ordinary human-start
  flows keep their expected behavior.

- BENCH-025-004 [ ] Exercise recoverable loss of the link before and during
  retrieval, Pi interruption before archive publication, and interruption
  before and after the delete reaches SD. Include partial multi-output
  collection, reset and a changed path after interrupted cleanup.
  Assert that the first evidence survives, the runner never replays a
  workload to collect a file, and deletion stays blocked until each file
  has a durable archive, verdict and still-confirmed ownership.

- BENCH-025-005 [ ] Run a separately approved Nurples pilot on a bounded
  fixture and reused workspace. Compare fresh attempts with retained
  records, verify serial/report identity and totals, and record SD occupancy,
  transfer count and elapsed time for staging, target workload, collection
  and cleanup. Prove normal CLI and handback. Review the pilot before
  adopting the contract in the shared sparse checkout and authored examples.

- BENCH-025-006 [ ] Present the read-only backlog inventory and exact
  keep/delete proposal for separate approval. Report bytes by owner and
  disposition. Any approved cleanup produces per-file removal receipts and
  preserves the pilot, active assets and recovery records.

## Accepted decisions

Smith accepted the draft identified by SHA-256
`9d7af0eb7c67f245c568b97eb905de86807cdb88a91e1260cbd82333100a5213`
with a change to D03.

| ID | Decision |
| --- | --- |
| D01 | Use stable runner-owned fixture directories under `/test/<project>/<fixture>/<arm>`. Keep attempt IDs on the Pi and in new reports. |
| D02 | Use a short runner-supplied argument and an in-band token in new reports, verified against a versioned serial record. Qualify the argument delivery and encoding before pinning the pilot. |
| D03 | Allow exact-file cleanup after durable archival when ownership of the exact attempt and file is conclusive. This includes semantically rejected reports when the archive contains their bytes and rejection reason. Retain stale, unidentified or uncertain copies pending disposition. |
| D04 | Pilot with Nurples, then review opt-in shared adoption. Review the historical backlog separately. Ordinary bench inventory and an Oryx-mounted card are possible access routes for that later review. |

The current `POSE.BIN` remains subject to Smith's explicit leave-in-place
direction. The sync test remains on hold. The approved plan does not select
a live pilot, authorize historical cleanup or transfer bench custody.
