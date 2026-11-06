# Guarded UART0 coexistence isolation — first physical result

The unfiltered eight-bit network carrier passed four byte-exact records while
EMOS also submitted guarded UART0 drawing batches and received point replies
from the mainboard VDP. This small control does not reproduce or clear the
larger MechAgon fault, establish repeatability, or qualify Wolf integration.

## Result and scope

| Witness | Actual result | Interpretation |
|---|---|---|
| Pi TCP peer / eZ80 payloads | 0, 1, 127, 128 bytes; 4/4 exact echoes | Both directions exercised, including all eight data bits in the selected patterns |
| UART0 guarded RFC25 batches | 4/4, each 67 bytes | EMOS accepted the source through its guarded owner path |
| Source-release callbacks | 4/4 | The eZ80 application may reuse each source; not a physical drain witness |
| Mainboard point replies | 4/4 | Separate ordered receiver completion witnesses |
| Application cleanup | error=0, RELEASE=0, restore=1 | Positive carrier teardown and mode restoration |
| Size refusal/required-size checks | 10 | Existing fixture checks retained |
| Application elapsed clock | 16 nominal MOS ticks at 120 ticks/s | Uncalibrated; not a rendering or optical speed measurement |
| Point query clocks | 0, 2, 0, 0 raw MOS ticks | Zero is below this clock's resolution, not zero physical latency |
| Host peer duration | 8.748966540 seconds | Includes host connection/record lifecycle, not comparable with the application clock |
| Dispatch | Exactly one native invocation | No retry, analyzer, filter, game module or consumer replay |

The fixture is `network-cycle-parallel-rfc25-r01-b2026-11-06-11-10-35Z`,
17953 bytes, SHA256
`d04442f1af37bbf06c253f155caf9a684961d74e8d74bf1c0ce8bb4fd23de952`.
Its source is `0af5834a010a08a3fd7db6177c0da1cda684f26b`; the new checked
parent and [64-input freeze](RFC25-OWNER-FREEZE.json) govern this use.
The durable result is 288 bytes, SHA256
`fd8276d3fee0cce04ce9e885ed7103b2301d1d66638559e85a073773a67a9734`.
Raw host actors retired and actual native CLI was established before collection.
No failure RAM preservation or recovery was needed.

## Component identities

| Component | During the one control | Incoming/restoration selection |
|---|---|---|
| P4 application | `02addd547f3af3a00cf4fb975ef9d259f2e48d0ded64ef80a053f9b4de10ccf9` | `d9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e` |
| Complete EMOS ROM | `8270ecd709138fe5ae617a91d5d365eeede0738025d5043fc790541b19b8f281` | `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca` |
| Mainboard VDP | `5d65797e53a70db8716cc3bc31dc936e431aea975ffad8efb76d5d7e8c1e3d07` | Unchanged profile8 explicitly retained by Smith |

The P4 application update preserves the active partition, bootloader, partition
table and mutable storage. Restoration covers the entire maximum 1765376-byte
touched application span, including bytes beyond the shorter UART prefix;
expected span SHA256 is
`629aab118e03e7b42b3235d7eed633b6103931273d524f097ef446e92fc3d17f`.
Each new firmware write has its independent readback comparison. No redundant
backup or unchanged mainboard firmware read was selected. Startup and listener
files remain unchanged.

## Evidence retention and next discrimination

Machine-local raw evidence, exact lease and actor identities live in the ignored
`agents/parallel001/rfc25-physical-r01` record. Keep the passing SD receipt,
peer/serial capture, source freeze and installation/restoration receipts.
No broader firmware acceptance or production promotion follows this result.

The next consumer discriminator is MechAgon's separately published, finite
24-turn semantic replay using the real client, mainboard module and assets,
after normal fresh reservation and stopped operator handoff. It distinguishes
that larger workload from the small generic control without a Java match.
Extender retains transport ownership and prepares independent repeat/boundary
controls while peers use the bench. Wolf's existing mainboard VDPL byte stream
still lacks an agreed drop-in eight-bit route; its fill-only comparison remains
on one matched carrier, and that owner contract gap is explicit.

## Final physical handback

Bench generation59 was granted at20:37:07.739943UTC and cleanly released at
20:52:33.747342UTC on2026-11-06. Complete preparation, one control, collection,
firmware restoration and final checks took15min26.007399s. The peer itself ran
8.748966540s; setup/restoration dominate this small test. These durations are
observations for comparable future estimates, not new automatic deadlines.

The supported final getter reports exact feature2 absence, callback restoration,
ordered clear and released disposable buffer. Fresh raw state is mode0,
callback0 and Legacy0; startup/listener are unchanged, actual CLI/cursor is
restored, keyboard input is ready/neutral, listener offline and worker id0,
both serial endpoints free and every owned actor joined. SD remains mounted;
RAM contains the getter, not a prepared consumer. No target access remains.
The actual next reservation is Wolf's PREPARING request, notified immediately
with its needed current-profile rollback/bootstrap context; no grant is inferred.
MechAgon's separately reserved replay follows normal prepared FIFO admission.

The original source documents and64-input freeze are retained with the closed
local run; publication checkpoint `c6175925` reconstructs the original plan.
This result closes only the first finite tranche, not PARALLEL-001.
