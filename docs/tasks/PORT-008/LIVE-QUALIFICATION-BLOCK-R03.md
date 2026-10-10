# PORT-008 LC03-B — Bounded physical repair

Author authorized one hour, 2026-10-10 00:25–01:25 UTC, to diagnose and repair
the first physical block failure. This is a private qualification pair, not
production, formal ExExt activation, ordinary parallel VDU or SD transport.
Mainboard Pingo VDP and production selection remain unchanged.

## Findings and corrections

1. The P4 handover cancelled a native operation when EMOS had already finished
   its byte loop and held CLOCK low / VALID high, before the native callback
   reached the P4 task. The P4 now retains the bounded native operation until
   exact completion proof or its existing deadline. Pad levels alone authorize
   neither completion nor UART restoration.
2. A GPIO interrupt that samples VALID's current level cannot prove a short
   pulse. Forward reception now uses PARLIO's hardware level-delimiter EOF,
   exact nonzero byte count, buffer/unit/delimiter identity and an overrun
   sentinel. Reverse transmission uses a fresh hardware pulse counter to prove
   exactly two VALID transitions, initial/final high, and exact TX completion.
3. With the handover corrected, the physical one-byte forward case reached
   the native phase but timed out without an EOF callback. The older working
   forward prototype used repeated inactive clocks. EMOS now supplies sixteen
   bounded inactive clocks after releasing its data pins and deasserting VALID.
   Sixteen is an empirical diagnostic choice, not an established hardware
   minimum. The matched return/status exchange remains mandatory.
4. Host preflight initially accepted readiness from before an Agon reset.
   The runner now requires a fresh input transport epoch and stable admitted,
   neutral input before typing. The keyboard status `boot` field is that
   transport epoch, not independent proof of a physical P4 reboot.
5. The fresh gate exposed a separate recovery race: the P4 restarted its
   release handshake every two seconds. EMOS could mistake READY transitions
   from the restarted exchange for acknowledgements in its previous exchange.
   The P4 now holds the already released handshake while awaiting EMOS. Time
   alone neither rewinds the exchange nor restores UART; genuine GPIO/restore
   faults and observed live-link loss still trigger a physical fence.

## Physical observations

| Private P4 variant | EMOS variant | First one-byte Agon→P4 result | Scope |
|---|---|---|---|
| r05 | Earlier LC03-A image | Status35 after606 nominal MOS ticks;0/20 | Phase observation was below an early continue; exact failure phase unavailable |
| r06 | Earlier LC03-A image | Status35 after604 ticks;0/20 | Handover failed while native completion was still pending |
| r07 | Earlier LC03-A image | Status35 after846 ticks;0/20 | Entered native phase; two-second native timeout, no callback, zero reported bytes |
| r07 | Sixteen-clock EMOS image | Payload not invoked | Boot/input preflight failed; does not test the new clock tail |
| r08 | Sixteen-clock EMOS image | First forward case still times out;0/20 | Boot release and input admission succeeded; native phase received no EOF callback despite inactive tail |

MOS ticks are nominal120Hz and uncalibrated. These failed-call times include
waiting/recovery and are not throughput measurements. Host setup, compilation,
installation, retrieval and fixture timing are separate scopes.

## Software and installation evidence

The repaired native/coordinator suite passes29 counter cases,166 native cases,
279 block coordinator cases,82 ordinary plus111 private paired cases, and5208
handover/reset cases under host sanitizers. These model SDK/register boundaries;
they do not establish electrical behavior. The736 actual boot-adapter cases pass after removing the timed handshake
rewind, including four new delayed-peer/clock-rollover regressions which fail
with the old rewind.

EMOS `agon-emos-v0.1.24-b2026-10-10-00-55-33Z` builds at131001bytes, leaving71
ROM bytes. Its linked eZ80 native instruction suite passes124 cases, including
the inactive clock tail, exact payload length, registers/status and interrupt
state. Image SHA256:
`5f258aec58475f779f267bd7e7c33f8d9abcec3081be160497bde15a6423eaa8`.
The complete128KiB installed ROM was read back and matches; SHA256:
`20569f0f5df16110a2c697350317077f4a489ad545018731dbe2fed01b50255c`.
Original startup was restored and read back after installation. No prior-firmware
backup was taken under the Author's standing waiver.

Informative USB logs, Agon CSVs, source-frozen builds, flash verification and
recovery receipts are retained under ignored
`agents/port008-live-qualification/lc03d` through `lc03h`. Machine-specific
endpoints and device identities remain there and in the ignored bench record.
The existing MOSlet remains10750bytes at `/emos/parprobe.bin`. Results use
`/agents/extender/results`; installation batches use `/extender/install`.
Existing evidence is never overwritten or automatically replayed.

## Remaining qualification limits

The pinned PARLIO driver can partly destroy a unit before returning deletion
failure; blind retries are unsafe. Its TX arming path also has an unbounded
hardware-ready spin before application polling begins. PCNT deletion failure
now retains the unit until P4 reset, but equivalent PARLIO fault work remains.
Normal successful blocks would not establish full F03 fault/reset qualification.
No UART fallback, release based solely on elapsed time, or application bypass
of EMOS ownership is supplied.

Pinned IDF5.5.5 (`b774170ff46c393eeb5e495ea37936038d3f4f4f`) excludes P4 from
`components/esp_driver_parlio/test_apps/parlio/main/test_parlio_rx.c`'s external
SPI level-delimiter test, citing unresolved `IDF-9806` bit shifting on other
targets. This is a qualification caveat, not proof of the observed EOF timeout.
Driver review found no VALID-dependent input-clock gate or mandatory minimum
record size preventing the sixteen inactive clocks from reaching RX. The
two-byte sentinel buffer is supported by the driver's aligned DMA stash path.

The bounded hour did not establish a working parallel transfer. The final
r08 attempt passed boot release/input and reached native RX, but again timed
out after two seconds with done0/bytes0/callback-fault0. No reverse case ran.
The sixteen-clock tail did not resolve the demonstrated EOF boundary; further
work must inspect or replace that hardware completion mechanism, rather than
claiming a callback based on sampled pin levels. Recovery/handback receipt
records the final input and startup state.

Final handback: separate Agon reset recovered input; CSV retrieved, original
startup verified, listener stopped, collector closed. Input remains admitted
and neutral, held0/pending0 after capture close. First call844 nominal120Hz
ticks, fixture962ticks; neither is link-only timing. No block replay.
[Final receipt and evidence hashes](LIVE-QUALIFICATION-BLOCK-R03.json).
The authorized hour ends with LC03-B/F03 open; pause for Author review.
