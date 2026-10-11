# Current checkpoint — minimum transport review complete

The bounded phase tranche is complete, including byte proof and exact UART
restoration. Control construction/offer/completion dominates; merely parking
and restoring UART is a much smaller measured cost. The Author requires removal
of ExExt CRC and a transport-only first pass preserving stock behavior above
byte transport. Existing extra control machinery must justify physical necessity.
Author also requests review of direct ExCom ↔ ExExt switching. No transport
optimization has been implemented. The authorized
[minimum-transport review](docs/tasks/PORT-008/MINIMAL-TRANSPORT-REVIEW.md)
TR01–TR04 is complete after freezing/pushing the contract. Its
[results](docs/tasks/PORT-008/MINIMAL-TRANSPORT-RESULTS.md) contain a fourteen-row
removal matrix and minimum path. CRC removal is the proposed first code cut;
COMPLETE/ACK removal follows actual physical completion proof. Partial-output
VBlank gating, key publication cadence and IRQ-disabled refusal also depart from
stock. Author now authorizes the [CRC-removal tranche](docs/tasks/PORT-008/CRC-REMOVAL-R01.md): freeze/push first, then paired wire3 CRC removal and offline checks. Retain sixteen-byte carrier and electrical path; bytes14–15 sent zero/ignored. No deployment in this tranche. The
broad eight-hour goal remains paused.

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
   electrical ownership/handshakes. No CRC-free build exists yet.
   ADR-0026 and normative architecture record the new requirement.
4. P08-P04 queues direct ExCom ↔ ExExt review. The runner currently returns via
   Legacy because EMOS rejects direct extended-to-extended requests. No change
   made. Persistent UART shutdown and game comparisons remain later/gated.
5. Diagnostic EMOS hooks remain in explicit profiles only. The RAM recorder
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
