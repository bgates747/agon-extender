# Experimental ordinary ExExt stream

The explicit paired experimental builds route unchanged application VDU bytes
and actual VDP/keyboard replies through the existing eight-bit parallel pipe.
Software checks, ordinary CLI/replies, cached-input delivery and finite game
execution pass in bounded runs. ExExt game rates currently regress from UART;
reset admission and broader application qualification remain under
[PORT-008](../tasks/PORT-008/EXEXT-STREAM-R01.md). The 2026-10-11 performance
experiment is rejected for ordinary use; the bench is restored to its
preceding verified UART pair. Experimental binaries require explicit matched
selection and are not the current bench recommendation. This is outside selected
production and does not change the current Legacy/ExCom operating contract.

The maintained source now uses **CRC-free parallel format3** under
[CRC-REMOVAL-R01](../tasks/PORT-008/CRC-REMOVAL-R01.md). Earlier physical
measurements used format2 with CRC; they do not measure the new source. This
first removal cut retains the same electrical phases, carrier width and receipt
lifetime. It does not yet correct the scheduling departures described below.

## Owners and activation

1. EMOS alone commits the display route, reserves its UART1 serializer and
   coordinates eZ80 Port C/Port D ownership. P4's sole parser task owns its
   matched UART/parallel handover and VDP parser. Applications use unchanged
   RST10/RST18/MOS interfaces, without direct GPIO or transport access.
2. EMOS first obtains the existing version1 console lease, synchronizes display
   queries, then negotiates the format3 exact-block capability and stream
   START. Only successful preparation permits the ExExt route commit. Entry
   requires Legacy; return to Legacy before selecting ExCom or ExExt again.
3. UART carries framed control between parallel blocks. Ordinary VDU, keyboard
   and VDP reply payload uses parallel while the stream is active. The boot
   release handshake and board-specific I/O supply requirements still apply.

## Stream control

Use the existing19-byte forward carrier:23,0,F7 followed by16 bytes; returned
control remains FF,16 followed by16 bytes. Body0–2 is `EX`,wire version3;
body4–9 is the active six-byte session identity, including current block number.
Body12–13 is zero; body14–15 is transmitted zero and ignored on receipt. There is no parallel
CRC or substitute checksum, including session and stream controls. Format2
peers cannot admit format3; install a matching pair. Ordinary version1 console
activation and unrelated SD verification remain unchanged. Requests have
body10–11 zero; acknowledgements report pending return bytes, capped4096.

| Operation | Request | Acknowledgement | Effect |
|---|---:|---:|---|
| START |6|134|Bind the active console lease and parallel capability to the ordinary stream |
| POLL |8|136|Report returned bytes without consuming them |
| STOP |10|138|Wait for queued input to drain; report returned bytes; close only when none remain |

Exact-length direction0/1 OFFER and COMPLETE retain the existing physical
coordinator, strict next block number, reciprocal UART restoration and matched
completion receipt. Neither DMA completion nor a queued reply alone publishes
bytes. Before block-number wrap, EMOS negotiates a fresh transport capability
at an idle UART boundary; the console lease and stream queues remain intact.

## Scheduling and limits

1. EMOS batches up to4096 forward bytes, flushing full buffers or residual
   output on mainboard VBlank. It fetches up to256 return bytes per service into
   a512-byte staging buffer, retaining any incomplete framed packet outside
   the UART control parser. Complete VDP packets alone enter that parser.
   P4 has separate8192-byte input/output rings and one4096-byte DMA payload.
2. The real saved VBlank bridge temporarily enables interrupts for bounded UART
   control waits. A shared busy guard excludes nested transport and foreground
   writers. Returned bytes enter the retained parser/callbacks with interrupts
   masked under an actual VBlank handler, including during foreground stop.
   EMOS retains unpublished bytes and publishes at most one keyboard event per
   VBlank: stock MOS's latest-event latch must expose down before a bundled up.
   Other replies drain in order to that boundary; no new block overwrites
   unpublished complete events. A split packet retains its tail and admits the
   next bounded return fetch. The existing UART control reservation therefore
   never sees an incomplete VDP packet left by the parallel carrier.
3. P4's bounded I/O-only progress hook services control/handover while a retained
   VDU command waits for split parameters/uploads. It never reenters the parser.
   Full input rings apply backpressure before physical admission.
4. STOP with pending output keeps the stream active; EMOS drains it, lets the
   real ISR publish effects, then retries. Only empty STOP allows normal LEAVE
   using the independent original console lease. Failed completion fences the
   owner; uncertain output is never replayed automatically.
5. EMOS defers physical ExExt work while stock SD chip select PB4 is low,
   preserving normal clock ticks and already-received packet publication. A
   later eligible VBlank resumes service; stock SD timeouts remain unchanged.
6. Measured finite games remain slower than UART. Empty-loop execution stays
   near60Hz, so idle polling alone does not explain the nonempty-work slowdown.
   Pacing intervals include preempting synchronous transport and are not spare
   CPU. IRQ-disabled output refuses admission. No SD
   service migration (automatic SD admission stays Legacy/ExCom only), new renderer/mode, generalized callback ABI or automatic
   UART payload fallback is provided. Legacy/ExCom remain separate paths.

## Experimental reset prefix

The revised experimental pair adds a boot-only prefix to distinguish an eZ80
reset from unchanged live UART levels. EMOS first releases its data pads and
holds CLOCK-high/VALID-low until READY-high, then CLOCK-high/VALID-high until
READY-low. P4 acknowledges these only after its actual data-pad fence. EMOS
then holds CLOCK-low/VALID-high and completes the established reciprocal release
and UART restoration. An old initial READY level cannot authorize UART.
P4 invalidates pad-release proof before attaching UART, including the interval
before LIVE. Native block return continues through its separate owner. These
changes require the matched experimental builds; no older-pair qualification
is inferred. An earlier held-prefix pair passes three Agon-only warm resets, but later full
application runs expose unreliable admission, including after a P4 install. The
USB boot-pad marker and HTTP readiness do not prove release acknowledgement.
Do not generalize those earlier passes to the current pair. Reset during an
owned payload, P4-only restart and power-loss remain unqualified; deliberate
later Agon-only resets have recovered UART readiness without a timed grant.
