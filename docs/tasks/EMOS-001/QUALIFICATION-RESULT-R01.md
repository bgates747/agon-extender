# Eirene-based EMOS — first complete qualification attempt

The full paired qualification attempt did not pass. It completed all13
integrated service checks and native mode8, then stopped on the previously
deferred P4 HDMI refill-budget defect during mode8→20. Raw-SD was never invoked.
Recovery restores healthy mode0/Legacy input, scanout and SD services without
firmware or startup changes. The Author's priority FSIM native-mainboard work
can use that verified Legacy scope; full paired qualification remains open.

## Exact inputs and preparation

1. EMOS `agon-emos-eirene-r02-b2026-11-04-08-17-43Z`, source
   `16ec1f78c7ead1f38378c5ee9bee4633bcb62c1d`; full131072-byte ROM SHA256
   `f62eed7f6bab8c164dcfe5e700132d289d52352f19d955acccbe1cff81b5e893`.
   The runner obtains another complete matching ROM before its physical cases.
2. P4 `port-008-upload-r02-b2026-11-04-01-42-41Z`, source
   `9897b1d152f9df5a96e9292312bad6cc71bd5451`; app1851248 bytes/SHA256
   `5db0c0a0c378ca80a7947150501f9b2a0fa44b12544873a691c4de94f2d8c527`.
   A new independent full16MiB read matches the retained expected image,
   SHA256 `2aab04e810b224848c02087583cfc8ed9e80cab3adce64014461ff471dae27ca`.
   No flash erase/write occurs; controlled normal boot/actual CLI follow the read.
3. Native VDP remains the retained1094512-byte application/SHA256
   `8ade1e7dbc8b82cfbb20bfc92bdeb02e909c38c9f93c37723f9c9d409a9af7c4`,
   with full4MiB restoration image SHA256
   `17caa5b0b2ede84bb627e207f10994b13dd3abfa2d04fc807ec393414fe33378`.
   This is retained verified provenance, not a new native-device read or a stock
   source/capability claim. The host restoration image is rehashed exactly.
4. Canonical schema2 receipts pass without relaxing their comparisons. EMOS
   uses a clearly retrospective archive of all298 contemporaneous guarded
   source inputs plus exact generated identity/original command. Original build
   and installation manifests remain unchanged; no reproduction build is claimed.
5. The retained QSTATE and raw-SD binaries match every maintained source input;
   no rebuild is necessary. Their hashes are respectively
   `2b30ae62c595595f3fe937e9b1ed0831ee293ab09a3f59b24d2f40be4c62b62b` and
   `f78e86653748b34f8c8945405affe7af3d070542b58806ec109196b2f1c442f8`.
   Both are deployed/read back stopped. Existing cue, browser/reset endpoint,
   neutral keyboard/controller, setup-only startup and free ports pass preflight.
6. Author authorization supersedes the earlier readiness stop. The canonical
   runner/assertions are unchanged. A private launcher asserts the central
   physical lease before each bench HTTP operation, including its alert child.

## Outcome

| Existing case | Passed checks | Required checks | Outcome |
|---|---:|---:|---|
| Mode transaction |1|7|Mode8 passes; transition to20 aborts scanout |
| Raw SD |0|5|Blocked; no raw-sector write attempted |
| Integrated services |13|13|PASS |
| Total |14|25|Full invocation failed; not qualified |

Rows place unresolved cases first. Integrated coverage includes actual reset/
input readmission, Legacy/ExCom handoffs, fresh text, HDMI DMA progress, fast
checksum-free SD roundtrip, owned-file cleanup and normal startup recovery.
This is stronger installed-EMOS evidence than the earlier focused UART tests;
it does not waive the failed output gate or pending physical/manual cases.

Mode20 commits512×384×64 with684×384 HDMI carrier, then stops after6 frames.
The first fault is a1641us refill against the existing1600us limit. Same-job
phases include427us queue wait,12us preparation,8us source cache,
1181us submit-to-callback and13us finish. The inner DMA/IRQ interval is1149us;
this includes interrupt delivery/driver work and is not pure DMA transfer time.
One subsequent underrun follows the recorded abort. Do not raise the limit,
weaken the oracle, call the stopped picture an EMOS crash, or treat another
clean observation as resolution of the retained failure.

The known output investigation and next hardware-event measurement are retained
in [HDMI-002's repair plan](../HDMI-002/WIDE-CLEAR-REPAIR.md). That task previously
rejected the32-byte burst change as a remedy; do not repeat burst guesses.
The current occurrence is recorded as E01-QF01 in the qualification plan.

## Recovery and disposition

1. Retain the full failed invocation and counter/capture snapshots. A fresh
   logical text capture shows a prompt, but ordinary mode0 restoration stalls
   event drain; its unconfirmed-input journal is preserved, with no replay.
2. One Agon reset fails to restore fresh neutral input. P4 reset, five clean
   initialization seconds, then one Agon reset restores it. Actual listener/
   startup-read/EXIT and advancing mode0 DMA verify recovery. No operator reset,
   firmware replacement, startup edit or raw test replay is needed.
3. Restore both saved mode0 states, Legacy route, original working directory
   and visible/flashing cursor controls. Archive and remove only positively
   identified failed-run temporary support. Original startup/listeners remain
   byte-identical; input/controller are healthy, listener/worker idle and ports
   free. Optical flashing/pixels are not inferred from commands or counters.
4. Defer the previously open HDMI campaign while FSIM uses its priority native
   mainboard/Legacy slot. Preserve Eirene EMOS/P4; any FSIM-native VDP replacement
   follows its separate Author authorization and exact-image restoration plan.
   Do not describe this handoff as full-pair acceptance or production promotion.

The ignored run directory retains canonical summary/checks, source closure,
installation receipts, independent dumps, lifecycle/transfer journals, timing,
failed-job phases, recovery and clean handback records. Preparation and retrieval
are included in operational durations; no UART/rendering performance comparison
is inferred. All clocks are Pi monotonic seconds, not independently calibrated.
[The portable attempt record](test-reuse/paired-attempt-r01.json) binds the
individual case counts/timing and retained evidence hashes.

Actual FSIM priority handoff completes2026-11-04T10:15:16Z through the central
registry after fresh physical checks. The durable grant message includes exact
Eirene/P4/native identities, established fast UART/staged SD workflow, reset and
native application-only preservation/restoration instructions, and the failed
HDMI qualification limit. Outgoing app steering failed; the Author explicitly
takes responsibility for notifying FSIM. Extender performs no further target
access after the grant and retains scheduling/owned-defect repair responsibility.

## Remaining work

1. Resolve the existing P4 HDMI deadline defect under its own tracked plan when
   the bench is available and FSIM does not need it.
2. Run a new complete25-check canonical invocation; partial passing runs cannot
   be combined. Preserve the uninvoked raw-SD gate until that run reaches it.
3. Complete actual Author visual/input reviews and acceptance/version/promotion
   closeout. Existing production selection remains unchanged.
