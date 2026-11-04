# EMOS migration — reused compatibility tests

The installed Eirene-based EMOS passes nine existing Extender host-test methods,
UART's functional regression twice, and UART's C example. Both physical
functional runs verify all 8,192 receiver bytes and return cleanly. These are
focused compatibility results; the complete paired qualification suite remains
uninvoked and is not yet ready. EMOS, P4, native VDP and normal startup remain
unchanged during this tranche.

## Frozen inputs and adaptations

1. Installed EMOS `agon-emos-eirene-r02-b2026-11-04-08-17-43Z`, source
   `16ec1f78c7ead1f38378c5ee9bee4633bcb62c1d`, full-ROM SHA256
   `f62eed7f6bab8c164dcfe5e700132d289d52352f19d955acccbe1cff81b5e893`.
   The prior installation record owns the independent full readback. No new
   installation or firmware source change occurred for these tests.
2. UART RC2 source `825eaf77176247f5b5ba2f940ae73fcace34e7e5`, published ZIP
   SHA256 `48d2fefa319f174ab4368287e40743c7610a3aeac61c0e32653fa26858166cd4`;
   all319 published inventory entries verified. UART supplied exact contract,
   coverage, source paths and portability limitations through the mailbox.
3. Host tests compile actual installed EMOS C, preserving assertions. The
   private native-I/O include adapter reuses existing register mocks; mock header
   include ordering avoids a duplicate BOOL definition. No resident C changed.
4. UART's original functional/example workloads, assertions, comparator data
   and29-byte C callback gate are preserved. Only exact-ROM/fixture identities,
   the functional identification banner, entry-point naming, build integration
   and the [lifecycle wrapper](test-reuse/lifecycle.cpp) are adapted. C++ uses
   the existing appliance flags `-fno-exceptions -fno-rtti`; the target toolchain
   does not supply default C++ exception machinery. Frozen adapted-input hashes
   and complete sources remain in local retained evidence.
5. The wrapper requires a fresh native mode0 query, uses the existing mode
   lifecycle policy, reserves a per-run completion file and emits its unique
   token only after the original function returns and cleanup completes. The
   Pi additionally requires a subsequent MOS prompt before retrieval or another
   invocation. UART's uncertain-source infinite hold is preserved.
6. UART's existing local-ROM identity guard is unchanged in purpose; no new
   checksum or framing is added to EMOS–P4 communications. PERF2 and its timing
   experiment remain deferred. The example's arithmetic is checked with UART's
   frozen `metrics.py`, and functional results with its existing marker oracle.

## Results

| Existing test coverage | Host mocked I/O | Physical native VDP / Legacy mode0 |
|---|---|---|
| Keyboard receive/IRQ harness, including existing variants | PASS | No synthetic keyboard exercise claimed |
| Console/session harness, two methods | PASS | Broader ExCom case pending |
| Controller resident service | PASS | Physical controller exercise pending |
| SD link and admission, two selections | PASS | Foreground retrieval worked; no throughput claim |
| Parallel engine, binding and UART1-open guard, three selections | PASS | Parallel qualification pending |
| UART RC2 functional, first invocation | Not substituted for hardware | PASS;8,192 receiver bytes compared |
| UART RC2 functional, independent second invocation | Not substituted for hardware | PASS;8,192 receiver bytes compared |
| UART RC2 C example | Not substituted for hardware | PASS; original work/state oracle and clean return |

The host rows represent eight selections containing nine unittest methods.
Optional ExCom C-reference and inactive fixed-backend variants are supplemental
coverage, not proof that those variants are the installed active implementation.

Both physical functional runs pass lengths1/15/16/17/255/256/257/1024, zero-length
INVALID, second-write BUSY, callback-once/NULL callback, source overwrite after
release, GP RX during TX, synchronous output before/after and explicit finish.
They do not force physical CTS-edge races, inject keys, qualify arbitrary caller
contexts, guarantee abnormal-exit cleanup, or exercise UART1/P4 async routing.

## Duration and evidence

| Physical invocation | RUN submission to later MOS prompt (s) | Retrieval and listener handback (s) |
|---|---:|---:|
| Functional1 | 9.933 | 6.444 |
| Functional2 | 9.924 | 6.297 |
| C example | 3.616 | 3.691 |

The Pi runner records UTC2026-11-04T09:24:36.100506Z through09:25:57.729203Z,
81.629 seconds total including command pacing, LOAD/setup, all three invocations,
result retrieval and final restoration. Binary building and earlier SD staging
are outside this total. These are Pi monotonic host observations, with command
delivery/polling overhead and no cross-processor calibration. They are neither
rendering time nor UART throughput measurements, and are not directly comparable
to UART's Console8 performance runs. No attention/voice latency is included.

[Machine-readable results](test-reuse/results-r01.json) retain exact binary
identities, individual timing scopes and evidence hashes. Machine-local source
manifests, original logs/counters, tokens, serial captures, completion files,
compile telemetry, lease records and SD locations remain in ignored evidence.
The final input is ready/neutral; listener and transfer worker are idle, both
serial ports are free, original working directory and mode0/Legacy are restored.
The runner verified startup bytes unchanged and sent visible/flashing cursor
controls without clearing completion output. No optical acceptance is claimed.

The host adapter initially encountered duplicate mock/native BOOL declarations;
include ordering fixed it without changing product code. Fixture preparation
also corrected a wrapper comment delimiter and reused the established C++ flags
after the target linker rejected default exception support. Before any physical
test, the runner's route-status parser rejected valid doubled carriage returns;
the captured later MOS prompt proved normal completion. The parser was corrected
before the first RUN. These were harness/build setup corrections, not firmware
failures. No uncertain test was reset or replayed.

## Remaining gates

1. Prepare canonical schema2 installation receipts for the exact installed pair,
   preserving original evidence. EMOS needs complete source/archive provenance
   bound to its retained readback. P4 has independent application-sector readback
   and complete expected-image verification, but that constructed expected image
   must never be labelled an independent complete flash dump. Reconcile this
   honestly with the canonical receipt contract before claiming readiness.
2. Reuse and pin the maintained raw-SD fixture from its owner source, plus QSTATE,
   after current lifecycle/API review. Do not resurrect historical startup-writing
   recipes or import unrelated peer source into the isolated EMOS port.
3. Complete canonical offline admission, live staging/readback, current identity,
   input, reset-bridge and notification readiness. The canonical suite remains
   stopped until the Author has been notified that all preparation is complete.
4. After separately admitted full invocation: all25 paired checks, declared
   physical/manual review, any later matched performance work, Author acceptance
   and production closeout. Existing bounded passes do not waive these gates.

Actionable ownership remains in [EMOS-001](../EMOS-001.md). Extender retains
physical custody; this result does not open the bench to queued consumers.
