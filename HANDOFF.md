# Current review — indexed framebuffer source inventory complete

[RESEARCH-007](docs/tasks/RESEARCH-007.md) R07-01 alone is complete;
[pipeline inventory](docs/tasks/RESEARCH-007/PIPELINE-INVENTORY.md) and normalized
source hashes pin the inspected current rendering path and retained r17 graph.
Packed lower-colour indices and one-byte native RGB222 already exist. Selected
HDMI geometries use three-byte B,G,R drawing storage, while software-sprite saved
backgrounds remain one byte/pixel. RGB888 panel images, DMA2D/SRAM strips, PPA
staging and the allocated but bypassed browser snapshot pool are mapped.
All 5,501 retained source inputs match; no runtime performance claim. No code,
build, emulator, device, SD, startup or production changes. Fsim retains bench;
stop for review before R07-02. The separate ExExt checkpoint below is unchanged.

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
