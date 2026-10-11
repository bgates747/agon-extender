# Current checkpoint — verified UART rollback after failed ExExt performance

The Author reports a major regression. The ordinary parallel adapter passes
bounded functional checks but fails ordinary-use performance expectations and
reliable reset admission. The pre-goal UART pair is restored; experimental source and evidence are
preserved. The newer Author/fsim review reservation controls bench access.
Matched-stream timing preparation is complete offline. Production is unchanged.

## Start here

1. Read `AGENTS.md`, the handbook, production manifests and local hardware/bench
   constraints. The Author requires all work to stop at a question until answered.
2. [Work contract](docs/tasks/PORT-008/EXEXT-STREAM-R01.md) records the eight-hour
   goal and rollback disposition. [Results](docs/tasks/PORT-008/EXEXT-STREAM-R01-RESULTS.md)
   contain exact identities, comparisons, corrective controls and remaining limits.
3. Current hardware ownership/readiness, endpoint identities and retained receipts
   belong in ignored `HARDWARE.local.md` and the local evidence index. Do not
   infer current bench firmware from Git HEAD or a production manifest.

## Installed pair

1. P4 `port-008-data-r20-b2026-10-11-09-07-32Z`; app SHA256
   `01cbd53255fbbae4760bc2ba64fc0f987cb9ef828b397d17a7cd7a64b9322771`.
   All four flash segments independently verify.
2. EMOS `agon-emos-v0.1.24-b2026-10-10-01-48-39Z`; complete128KiB ROM SHA256
   `69d7b11ac1fa6fcd48cc3770356c3b8806d8f308c345bd670075a7eb21b613dd`.
   Image and complete ROM readback match the preserved pre-goal build.
3. Mainboard VDP remains the fsim consumer's custom image, not stock. No wiring,
   probes or user game files changed. Original38byte startup and Nurples T09
   configuration are readback restored after the finite UART control.
4. A later cached-input preparation loses admission before LOAD/RUN, also on
   the old pair. Paired reset recovers; Legacy CLI/ECHO and five seconds of
   neutral readiness pass. No running fixture/listener/collector/reset hold.

## Decisive results and continuation boundary

1. Frozen Nurples T09 returns to60.00application updates/s after UART rollback,
   versus14.55in the experimental ExExt pair. Both save120valid measured rows.
2. Lode Runner's fixed CPU workload takes34.233sExExt versus6.383sLegacy; all256
   sampled pixels and the DOS read pass, but adaptive presentation counts differ.
3. Rally and Aginvadors finish finite ExExt runs slowly; fine-timer overflow
   prevents precise per-interval timing claims. Choplifter finishes both existing
   native-core endpoint variants in276.117/266.867nominal seconds on ExExt; no
   matched UART comparison is claimed. These rates are not physical display FPS.
4. Empty-loop Legacy/ExExt controls stay60/59.02updates/s. Root cause is still
   unproved; idle polling alone does not explain loaded-workload performance.
5. P4stream-r15 split-upload progress change compiles/validates and remains
   **uninstalled**. Further candidate installation is deferred pending review.
6. The original eight-hour objective is incomplete. No acceptance, promotion or
   version tag is implied. Continue only from the recorded unresolved contract;
   do not silently replace the restored pair or replay uncertain invocations.

Only owned documentation/source checkpoints are committed. Other agents'
HOST-001, external game and consumer changes remain untouched.


## Next bounded task — matched stream timing

1. Author approved [matched UART/parallel timing](docs/tasks/PORT-008/STREAM-TIMING-R01.md).
   ST01–ST03 complete: exact-ROM-bound MOSlet and timing EMOS compile, mandatory
   link/owner and CPU-model checks pass, complete buffer validator tested.
2. Timing EMOS 2026-10-11 19:00:57Z uses 131048 bytes (24 free), 80 more than
   ordinary profile. The ordinary control is byte-identical to preceding
   stream-r11 except build identity. No new EDP instrumentation is needed;
   retained P4 stream-r14 is the paired candidate, not uninstalled r15.
3. Retained build/provenance/checks: ignored agents/stream-timing-r01/;
   final MOSlet fixture-r08. Reproducible source/procedure:
   tests/performance/stream_timing/README.md. Nothing has been deployed.
4. Obtain Author release of the newer fsim review reservation before ST04.
   Do not reset, flash, probe or assume idle CLI from older receipts. The mainboard
   custom fsim VDP must remain unchanged. Complete comparison and exact UART
   restoration, then stop for discussion before any optimization.
