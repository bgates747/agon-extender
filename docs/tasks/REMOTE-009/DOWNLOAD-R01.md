# Foreground sequential-read candidate

The accepted listener opens, sizes, seeks, reads and closes its source for every
216-byte reply. Reuse one foreground read handle for consecutive fast READs,
without changing resident EMOS, the P4 image, packet framing or payload limits.
This is a self-assigned candidate under the Author's download-speed instruction;
its performance benefit requires a controlled bench measurement.

## Pinned research and implementation contract

1. Listener source is EMOS commit9a92d811df0a597c6369409f316a95e9ca7e7d70,
   matching accepted sdserve-v0.3.0/22968B04e7ef59. Relevant listener service/main
   and host tests are unchanged in the current EMOS checkout, but use an isolated
   owner-repository branch so unrelated resident development is not imported.
2. Official documentation baseline is agon-docs
   f9806bd3cbff6ed5d1c08bef1d51fed11764b86b, specifically MOS API FatFS0x80-0x82
   and seek/error/size APIs. `ffs_fopen` accepts caller-owned FIL and absolute
   resolved paths; pair it with `ffs_fclose`, not MOS integer-handle closure.
   The documented multi-read file lifetime already supports this reuse.
   Official source baseline MOSv3.0.2/8336409351ee5314e02801a7b72a4f1bb5282519
   remains clean/read-only. No ABI or header adaptation is proposed.
3. P4 source `vdp/video/extender/storage/fast/engine.hpp` creates one HELLO/session,
   STATs a source and issues monotonically advancing READs<=216B in that session.
   Existing per-record roundtrips remain; P4 spool/HTTP code stays fixed.
4. In fast mode only, retain one FIL, literal validated path, initial file size
   and current offset. Seek only when the requested offset differs. No whole-file
   buffer, read-ahead task, digest or new resident hook. Checked-mode behavior
   stays unchanged.
5. Close the reader at EOF, any read/seek/size/error, path change, initialization,
   stop or any executed non-READ operation, including HELLO/session transition,
   metadata or mutation. Close before mutation can affect a cached source. Exact
   duplicate requests continue to return the existing cached reply with no I/O;
   stale/conflicting packets do not execute file operations. Invalid paths never
   acquire a new handle. The listener owns foreground filesystem operations;
   it does not promise concurrent external media mutation coherence.
6. Add meaningful host filesystem counters and read lifecycle/error checks to
   the actual C-engine harness. Verify one open/close and no redundant seek for
   a multi-record fast download; legacy checked reads keep their original calls.
   Cover random offsets, EOF/empty, path switches, HELLO, stop and close/read/seek
   failures, plus existing write/recovery/sequence protections. Fast tests must
   still report zero CRC invocations.
7. Identify an experimental MOSlet below32KiB and stage it under a distinct
   supported /emos name during an explicit finite own lease. Never overwrite
   active or accepted /emos/sdserve.bin. Preserve installed P4r27/EMOS/native
   firmware/startup and test baseline and candidate through the same P4 worker,
   media, payload and output scopes. Close utilities/resources and return accepted
   listener/CLI at handback. A host pass does not establish a speedup.

## Offline implementation evidence

The isolated owner branch is committed/published at
`b8e72c9` from accepted `9a92d811`. Actual C-engine tests pass61 cases (58
executed/three explicit skips), with seven application-helper checks passing and
direct codec equality checked separately. Fast sequential1000B reads issue
open/size/seek/read/close counts1/1/0/5/1 versus checked5/5/5/5/5; no fast CRC
calls. The identified draft MOSlet is
`sdserve-v0.3.0-b2026-11-03-08-07-19Z`,24753B,
SHA256`0566e17f18747c2e625d2450ce5324a2b1097bce323a5e4d70fad6dcb41cdff2`.
It uses the already approved software lineage with a new build timestamp, not a
new version/revision or acceptance. The immutable build manifest records clean
source and compiler hashes; no resident EMOS or P4 build changes.

Prepare an exact accepted-source control through the same wrapper/compiler/layout
for causal timing. Temporarily place the control/candidate under distinct
`/emos/sdrd00.bin` and `/emos/sdrd01.bin` names, never overwrite the installed
accepted listener. Compare the same65537B source through both utilities and the
unchanged P4 worker. Run the1.1MB pair only if candidate short-file worker time
is at least10percent lower. Preserve raw timings and host bytes separately.
This preparation does not reserve, deploy, invoke or establish hardware readiness;
the6502 consumer currently has exclusive physical custody.

The exact accepted-source control is
`sdserve-v0.3.0-b2026-11-03-08-08-38Z`,22968B,
SHA256`03738afc179955b9212eb29a0848777862e04e5cc22e044b7fa9fcd20b573310`.
Both manifests pin the same compiler SHA256
`b26b8b361834c7af13d272408efafd350cf8d6493c89e50cecd73f9d9e70a220`.
An offline byte comparison also proves the rebuilt control equals the freshly
retrieved installed22968B listener except for its single UTC build-ID string.
Retained linker maps place BSS end at0xB63C4 for control and0xB6B63 for candidate,
leaving7228B and5277B respectively for shared heap/stack below0xB8000. This
static layout check does not measure runtime stack high water.

## Finite physical comparison plan

1. Finish independent builds, byte/code checks and reviewed local helper before
   reservation. Obtain a fresh Extender-owned central lease after the current
   consumer's verified release; assert its token before target operations.
   Read latest handback/component/operation records again at entry.
2. Require actual Legacy CLI, mounted P4 card, unchanged matched P4/EMOS/native
   components, neutral input, idle staged worker/listener and ownerless serial
   ports. No serial reader or printer mirror during timed transfers. Source
   fixture directory is new under `/extender/diagnostics` with a UTC run suffix.
3. Explicitly start the installed canonical fast listener. Verify startup and
   listener bytes with the pinned staged client. Refuse existing alias/fixture
   paths rather than overwriting them. Deploy/read back the two identified
   aliases through that listener, and seed one65537B deterministic source.
4. Exit through a fresh metadata session, explicitly launch control then candidate
   with `EMOS sdrd00 --fast /` and `EMOS sdrd01 --fast /`, download the same source
   once per utility, and exit each cleanly. Compare host bytes after timing.
   Keep P4 `mainboard_us` (inclusive local spool/UART/eZ80 service work), `stage_us`,
   HTTP delivery and host monotonic end-to-end seconds separate. These counters
   cannot isolate eZ80 filesystem time or establish CPU-exclusive throughput.
5. If short-case worker elapsed falls by at least10percent, seed1.1MB once using
   the canonical listener and run one matched large pair. Otherwise omit it.
   No full suite, PCM, firmware/reset/startup/mode change or unattended replay.
6. Preserve uncertain job state and stop on error. A timeout allows bounded
   observation of the same durable job only, never another POST or implicit
   reset/replay. No automatic cleanup commands into an unknown foreground state.
7. On normal completion use the canonical listener to recheck startup/listener,
   remove only the two owned temporary aliases, and fresh EXIT. Preserve payload
   fixtures/results, normal CLI/cursor, idle jobs and ownerless resources. Obtain
   fresh central release evidence and return custody before offline analysis.
8. Estimated preparation/cleanup1–2minutes plus short-pair about30seconds, with
   an optional large pair up to about8minutes from retained baseline243.20s per
   download. Candidate time is uncalibrated; allow a roughly12minute slot. Each
   transfer has a900second observation bound that stops dispatch rather than
   causing reset/replay. Pi monotonic seconds/P4 microseconds have no independent
   oscillator calibration. This estimate is not a collection deadline.

References: [official MOS API](../../../../../agon-docs/docs/mos/API.md),
[owner service](../../../../agon-emos/projects/sdserve/src/service.c),
[P4 worker](../../../vdp/video/extender/storage/fast/engine.hpp),
[measured baseline](STAGED-RESULTS.md). Private build/source paths stay in the
ignored run record. Production and canonical suite selection remain unchanged.
