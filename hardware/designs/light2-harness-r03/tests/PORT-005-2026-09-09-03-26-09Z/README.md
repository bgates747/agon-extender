# Controlled P4 keyboard sender — PASS

P4 sent twelve controlled stock keyboard events through the retained VDP
keyboard handler, callbacks and serializer. Resident EMOS received them over
UART1 and the SD observer verified public callback/count, held-key map,
modifier and repeat effects. The Author confirmed SD/CLOCK and keyboard PASS
with return to the mainboard MOS prompt on the captured run and two further
Agon-only resets. The repeat runs are operator observations, not additional
waveform captures.

Original trace, serial and capture-helper hashes verify. The frozen serial
checker passes all twelve ordered events. Independent sigrok and raw-sample
decoding agree on exactly eight forward admission bytes and 75 return bytes:
one three-byte General Poll reply and twelve six-byte keyboard packets.
Framing is valid 8N1 at 1152000 baud. The analyzer retained all 288 million
samples at 24 MHz (12 seconds), including 7.590125 seconds quiet on all four
signals. P4 serial monitoring remained clean for 8.005626 seconds after PASS.
No acquisition or quiet-tail exception is required.

## Flow-control interpretation

Every UART character begins with active-low CTS permission. EMOS's
`uart1_keyboard_irq` raises PC2 RTS while processing its receive FIFO.
Thirty-seven return characters were already underway when that happened;
they complete with valid framing, and P4 starts no new character until CTS
returns LOW. The raw review records these transitions explicitly.

The earlier counting-only review helper assumed CTS stayed LOW for the entire
character. That assumption does not fit this resident interrupt receiver;
its initial assertion was corrected in the offline analysis, without changing
firmware, capture data or the frozen test procedure. The reviewed criterion is
permission at every character start and valid complete framing. See the
[ESP32-P4 TRM](https://documentation.espressif.com/esp32-p4_technical_reference_manual_en.pdf),
section 45.4.9.1, for active-low hardware flow-control signal meanings.

## Evidence and limits

`run.yaml` identifies the three clean candidate builds and evidence hashes.
`logic.sr` is the original acquisition; `uart-decoder.txt` contains independent
annotations and `measurements.json` contains event timing and CTS observations.
`serial-excerpt.txt` preserves keyboard diagnostics. Full logs, bench identities
and the reproducible analysis helper remain in the private capture bundle.

The SD result byte has not yet been copied back because the card remains with
Agon. The Author-observed final PASS follows the fixture's successful result
file write. Retain that byte when the card is next returned; do not invent a
readback or treat the three resets as three retained result files.

This completes the bounded controlled-sender hardware proof within PORT-005
and EMOS INTEG-009. Both tasks remain open for browser/session and broader
integration work. No layout translator, typematic generator, browser focus
handler, ExCom display switch, overload margin or abrupt-disconnect behavior
is qualified here. Registry r39 and all artifact identities/status remain
unchanged. No new implementation or commit is included in this result record.

## Supplemental SD readback — 2026-09-09 03:44:25 UTC

The Author returned the SD. Its `keyboard-state.bin` contains exactly `01`
(PASS), now retained here with `sd-readback.json`. The candidate observer,
same-build smoke, autoexec and consumed EMOS payload hashes still match their
preparation record. The card was read without modification and remains mounted.

This closes the supplemental collection item above. The original `run.yaml`
records what had been collected at capture review; the separately timestamped
readback records this later observation. Because each fixture run overwrites
the file, this byte represents the last completed run, not three separate
machine-readable results. All-three-run confirmation remains the Author's
observation.
