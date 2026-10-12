# Current stop — EMOS-only rollback complete

Author requested rollback then stop. Restored verified
`agon-emos-v0.1.24-b2026-10-07-23-11-33Z`; imageSHA256
`44d217b555f68a7d030bc0a89a2fa1d27f0fb537576f2925e90ef055b0a44d02`.
Independent128KiB ROM readback matches image plus erased padding; fullROM SHA256
`6f83bc21558ea7dcb665b60c18aa3a5c3030367f901e3e32ccbbf99eaf7f4019`.
FLASH automatic reboot restored fresh neutral keyboard admission. Listener exited.
Original38-byte startup unchanged/readback verified. No test auto-start.
P4 indexed r04 and fsim mainboard P1-count VDP remain unchanged. No P4 flash/reset
or test replay occurred. Paired/cold boot with this combination is untested.
Local evidence: agents/bench010/emos-rollback-r01. Bench released; stop here.

Operation protocols remain mandatory before further work. BENCH-010 diagnosis
and matched renderer comparisons remain pending. Author observed sprite flicker
in the candidate run; timing completion is not visual acceptance. Production unchanged.

Earlier checkpoints below are history and do not supersede this stop.

# Current stop — protocols installed; candidate results filed

The Author requires operation-specific protocol dispatch before tools. Read
[the operation index](docs/procedures/README.md), now required early in AGENTS.md.
Ordinary tests start through explicit CLI EXEC, never autoexec/reset. Corrections
invalidate dependent plans; explicit stop prohibits further tool calls.

The Author confirmed the recovered candidate suite finished and authorized
retrieval. [Four candidate-only results](docs/tasks/RESEARCH-007/INTEGRATION-CANDIDATE-R01.md)
are complete: Nurples60 nominal application updates/s, about30.1 P4 background
publications/s and60Hz DMA scanout. No matched baseline or visual acceptance.
Original38-byte startup is restored/readback verified without reset. Candidate
run.cfg files remain selected; originals retained. Listener exited, Legacy CLI,
keyboard ready/neutral, no pending SD request. P4 indexed r04, current EMOS and
fsim mainboard P1-count VDP unchanged during collection.

Requested EMOS-only rollback remains pending, not performed. Identified retained
working image: agon-emos-v0.1.24-b2026-10-07-23-11-33Z; imageSHA256
44d217b555f68a7d030bc0a89a2fa1d27f0fb537576f2925e90ef055b0a44d02.
Do not pair-roll back P4: Author requires the current P4 stay installed. No more
autoexec test launches. BENCH-010 investigation also pending. Do not resume
paused hardware work without current Author direction. Production unchanged.

Earlier checkpoints below are retained history and do not supersede this state.

# Current stop — indexed/PPA candidate flashed; fixtures deployed, not run

Author requested deployment only, then stop. Full P4 candidate
indexed-hdmi-r04-b2026-10-12-01-53-19Z is flashed; all four segments independently
verify. Four frozen SCAN binaries and five resident control/data files match
local bytes. Ten package files are staged below `/agents/extender/results/r07-i01`,
not activated. Ordinary 38-byte startup and existing run.cfg files are unchanged.
Listener exited; Legacy CLI with ready/neutral input, no pending SD transaction.
No game/benchmark invocation. EMOS and fsim P1-count mainboard VDP preserved.

[Integration results](docs/tasks/RESEARCH-007/INTEGRATION-RESULTS.md) record the
checkpoint; R07-I04/I05 remain open. Future baseline/candidate runs need fresh
authorization and actual paired identities; no integrated speedup is established.
[BENCH-010](docs/tasks/BENCH-010.md) captures fsim's admission/reset and USB loss
report for near-term investigation. No investigation executed. Production unchanged.

The checkpoints below retain earlier states and do not supersede this stop.

# Current review — linear-byte/PPA full firmware verified offline, uninstalled

[Integration results](docs/tasks/RESEARCH-007/INTEGRATION-RESULTS.md) close
R07-I01–I03. Full candidate indexed-hdmi-r04-b2026-10-12-01-53-19Z compiles/links,
actual source/CLUT bindings and candidate/rollback packages pass. Both controller
golden runs,14 selection checks and2 collector-unit cases pass. Linear physical
RGB222 drawing avoids full-frame VGA lane reorder; HDMI still scans RGB888.
Existing rolling overlays, automatic carriers and320 SRM remain selected.

R07-I04/I05 await bench handover: fsim has the newer reservation and reserves
initial campaign execution to the Author. No integration device/network/serial/
reset/SD/flash operation occurred. Exact retained data-r20 is the rollback,
not a freshly observed installed-state assertion during another bench owner.
Finite paired SCAN T03/T07/T08/T09 and resident controls are prepared under
`agents/research007/integration-r01/INDEX.md`. Read that index and the current
machine-local bench record before resuming. Preserve EMOS/mainboardVDP/games/
wiring and original startup/configurations. No integrated speedup or visual
pass yet; production unchanged. Wider AUDIT-011 remains parked.

The checkpoints below retain earlier evidence and do not supersede this state.

# Current review — physical indexed-expansion comparison complete

[RESEARCH-007 physical results](docs/tasks/RESEARCH-007/PHYSICAL-RESULTS.md)
close R07-B01–B05. All768 timing samples and firmware pixel/source/guard checks
pass in one14.439231s fresh run. PPA total p95 conversion takes72–85% less time
than the old CPU RGB222 path, or53–59% less including byte-lane reorder. At512×384:
old24.783ms, linearPPA3.779ms, reorder+PPA10.251ms. This is unloaded conversion,
not current directRGB888/HDMI/gameplay qualification or product integration.

Exact ordinary data-r20 P4 restored; all4segments independently verify, Agon
reset released, fresh admittedCLI input and5s neutralready keyboard/idleSD pass.
EMOS/mainboardVDP/SD/startup/wiring unchanged; no active fixture/collector/hold.
Bench released in HARDWARE.local.md. Local journal:
`agents/research007/benchmark-r01/bench`. No further bench or integration work
started; stop for review. The earlier preparation/checkpoints below are retained
history, not the latest installed state.

# Current review — complete conversion benchmark prepared, uninstalled

[RESEARCH-007](docs/tasks/RESEARCH-007.md) R07-B01–B04 complete after the Author
required an executable performance comparison rather than another compile-only
sample. [Preparation results](docs/tasks/RESEARCH-007/PREPARATION-RESULTS.md)
and [recipe](docs/tasks/RESEARCH-007/benchmark/README.md) identify the complete
self-running P4 image, exact old CPU/PPA comparisons, six workloads, 768 samples,
independent pixel/guard/input checks, dedicated durable NVS and host results tool.
Build `ppa-clut-benchmark-r01-b2026-10-12-00-21-22Z` compiles/links without warnings;
actual API/header/kernel bindings and deployment bytes/hashes pass. Five offline
checks and a labelled synthetic collector run pass. No physical measurements.
The ignored local index is `agents/research007/benchmark-r01/INDEX.md`.

R07-B05 requires bench handover: hold Agon reset, verify P4 identity, write and
verify listed segments only, capture/validate all samples, restore the exact
ordinary installed P4 and readiness before handback. Do not flash the merged
factory span over ordinary NVS. No hardware, SD/startup, product integration,
SDK selection or production changes were made. Consult `HARDWARE.local.md` for
current bench ownership; it changed from fsim to agon-6502 during preparation.
Original r05 example/evidence and the separate paused ExExt checkpoint stay
unchanged. Stop before hardware access or product integration.

# Current review — indexed PPA capability and compile-only example complete

[RESEARCH-007](docs/tasks/RESEARCH-007.md) R07-01 and R07-03 complete;
[capability report](docs/tasks/RESEARCH-007/CAPABILITY-REPORT.md) distinguishes
direct indexed scanout (not documented) from PPA programmable CLUT expansion
(explicitly documented on v1.3 silicon). Isolated
[sample](docs/tasks/RESEARCH-007/clut-example/README.md) r05 compiles/links real
CLUT calls through a six-file upstream-derived generated override; product
SDK5.5.5 and renderer stay unchanged. Independent physical-memory checks are
prepared, not run. No ISR submission or fused L8 scaling through public APIs;
two input streams and shared palette ownership constrain later integration.
No device, SD, startup, emulator, performance or production change. R07-02 and
R07-04–07 remain unstarted; stop for review. Bench owner is recorded in HARDWARE.local.md. The completed
[inventory](docs/tasks/RESEARCH-007/PIPELINE-INVENTORY.md) and separate ExExt
checkpoint below are unchanged.

# ExExt checkpoint — software completion removed, offline only

[Completion-removal contract](docs/tasks/PORT-008/COMPLETION-REMOVAL-R01.md)
CP01–CP05 complete after freeze/push. [Results](docs/tasks/PORT-008/COMPLETION-REMOVAL-R01-RESULTS.md)
record paired CRC-free format4: COMPLETE/ACK removed; native/DMA cleanup and
reciprocal UART return own completion. P4 stages its local result before final
READY-high and retains storage until consumption. Full ordinary/ExExt EMOS and
P4-PC HDMI builds, actual-owner host and linked eZ80 checks pass. ExExt EMOS
130,334 bytes, 738 free (another 264 reclaimed); ordinary 128,482 bytes, 2,590 free.
Builds are exploratory/uninstalled, with exact local snapshots and evidence.
No speedup or stock-equivalence claim. Fsim owns the bench; this tranche made
no hardware, SD, startup or production change. The installed-pair section below
records the last verified handback, not a new observation during fsim's work.
Next: discuss remaining minimum control/scheduling and a separately authorized
matched-pair hardware comparison. Format3 cannot pair with format4. Old diagnostic
completion-phase callsites are retired; rebind any later phase fixture to the new
ELF/ROM. The broad eight-hour goal remains paused; production unchanged.

## Start here

1. Read AGENTS.md, the handbook/production selection and HARDWARE.local.md.
   Stop at an unanswered Author question; do not continue dependent work.
2. [Completed phase contract](docs/tasks/PORT-008/PHASE-TIMING-R01.md) PT01–PT06
   and [results](docs/tasks/PORT-008/PHASE-TIMING-R01-RESULTS.md) own current
   measurements, hashes, selection provenance and restoration evidence.
3. [Original UART comparison](docs/tasks/PORT-008/STREAM-TIMING-R01-RESULTS.md)
   remains frozen. [Broader goal/results](docs/tasks/PORT-008/EXEXT-STREAM-R01-RESULTS.md)
   retain gameplay regression and uninstalled r15; do not resume implicitly.

## Findings and next discussion

1. Twenty-four selected samples verify 196,608 bytes. Five complete invocations
   retain 30 original endpoint/phase rows; two incomplete USB dumps exclude those
   samples, one matching fresh-repeat index supplies the missing byte proof.
2. Control construction/offer/completion is 70.3–80.7% of stream+query/reply time.
   Native runner is 2.1–15.8%. Offers following full 4096-byte blocks add ~33–35 ms;
   EMOS/P4 share unresolved. These are not rendering FPS or raw byte bandwidth.
3. Stock ordinary MOS/VDP UART has no CRC. Our custom control protocol added it.
   P08-D01/D03 accepted: no CRC or substitute checksum; first pass changes only
   transport and necessary link operations. Keep stock streams/parsers/replies,
   callbacks/sysvars/interrupt behavior. Review offers, completion exchanges,
   polls, sessions and batching against specific physical necessity. P08-D02
   owns minimum link control/paired deployment; P08-P05 owns implementation.
   Review contract/results are complete, including code/test locations. Keep
   electrical ownership/handshakes. CRC-free exploratory builds now pass offline;
   no installation or physical comparison yet.
   ADR-0026 and normative architecture record the new requirement.
4. P08-P04 queues direct ExCom ↔ ExExt review. The runner currently returns via
   Legacy because EMOS rejects direct extended-to-extended requests. No change
   made. Persistent UART shutdown and game comparisons remain later/gated.
5. Version-record validation exposes a pre-existing light2-harness-r02
   connectivity hash mismatch; both files unchanged from the contract baseline.
   Not fixed in this cut. A stale mode-lifecycle fake now supplies controlReply;
   current/negative controls pass. No product mode-lifecycle change.
6. Diagnostic EMOS hooks remain in explicit profiles only. The RAM recorder
   has 512 eight-byte entries; exact ELF/ROM callsite binding required. No logging
   occurs inside measurements. The read-only CRC model counts old ROM leaf
   instructions; it adds no CRC code to product firmware and measures no time.

## Installed bench pair and release

1. P4 `port-008-data-r20-b2026-10-11-09-07-32Z`; all four segments verified.
   App SHA256 `01cbd53255fbbae4760bc2ba64fc0f987cb9ef828b397d17a7cd7a64b9322771`.
2. EMOS `agon-emos-v0.1.24-b2026-10-10-01-48-39Z`; full 128 KiB ROM verified.
   ROM SHA256 `69d7b11ac1fa6fcd48cc3770356c3b8806d8f308c345bd670075a7eb21b613dd`.
3. Mainboard custom fsim VDP unchanged. Original 38-byte startup readback restored;
   card in Agon. Actual Legacy CLI ECHO and five seconds of neutral readiness pass.
   Listener/collector/test stopped; no pending/held keys or reset hold.
4. Bench released 2026-10-11T21:30:45Z; all three installed-current records updated.
   Receipts in ignored agents/phase-timing-r01/bench-r01/final-handback.json and
   restore-p4/restoration/receipt.json. The old build predates the newer pad-release
   log marker: installer waited unnecessarily, released reset in cleanup, and
   actual input/listener/ROM verification recovered without another reset/flash.
5. Production selection/version unchanged; no firmware promotion or new tag.
   All owned earlier dirt was logically committed/pushed before phase work.
   Unrelated agon-dev-env work remains owned by another agent.
