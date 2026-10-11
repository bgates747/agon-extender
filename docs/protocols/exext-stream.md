# Experimental ordinary ExExt stream

The explicit paired experimental builds route unchanged application VDU bytes
and actual VDP/keyboard replies through the existing eight-bit parallel pipe.
Software checks pass; physical integration and performance are under
[PORT-008](../tasks/PORT-008/EXEXT-STREAM-R01.md). This is outside selected
production and does not change the current Legacy/ExCom operating contract.

## Owners and activation

1. EMOS alone commits the display route, reserves its UART1 serializer and
   coordinates eZ80 Port C/Port D ownership. P4's sole parser task owns its
   matched UART/parallel handover and VDP parser. Applications use unchanged
   RST10/RST18/MOS interfaces, without direct GPIO or transport access.
2. EMOS first obtains the existing version1 console lease, synchronizes display
   queries, then negotiates the version2 exact-block capability and stream
   START. Only successful preparation permits the ExExt route commit. Entry
   requires Legacy; return to Legacy before selecting ExCom or ExExt again.
3. UART carries framed control between parallel blocks. Ordinary VDU, keyboard
   and VDP reply payload uses parallel while the stream is active. The boot
   release handshake and board-specific I/O supply requirements still apply.

## Stream control

Use the existing19-byte forward carrier:23,0,F7 followed by16 bytes; returned
control remains FF,16 followed by16 bytes. Body0–2 is `EX`,wire version2;
body4–9 is the active six-byte session identity, including current block number.
Body12–13 is zero; body14–15 is the established CRC16/CCITT. Requests have
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
   output on mainboard VBlank. It polls up to256 return bytes per service.
   P4 has separate8192-byte input/output rings and one4096-byte DMA payload.
2. The real saved VBlank bridge temporarily enables interrupts for bounded UART
   control waits. A shared busy guard excludes nested transport and foreground
   writers. Returned bytes enter the retained parser/callbacks with interrupts
   masked under an actual VBlank handler, including during foreground stop.
3. P4's bounded I/O-only progress hook services control/handover while a retained
   VDU command waits for split parameters/uploads. It never reenters the parser.
   Full input rings apply backpressure before physical admission.
4. STOP with pending output keeps the stream active; EMOS drains it, lets the
   real ISR publish effects, then retries. Only empty STOP allows normal LEAVE
   using the independent original console lease. Failed completion fences the
   owner; uncertain output is never replayed automatically.
5. This first adapter's block negotiations and byte kernel have not yet been
   measured under gameplay. IRQ-disabled output refuses admission. No SD
   service migration (automatic SD admission stays Legacy/ExCom only), new renderer/mode, generalized callback ABI or automatic
   UART payload fallback is provided. Legacy/ExCom remain separate paths.
