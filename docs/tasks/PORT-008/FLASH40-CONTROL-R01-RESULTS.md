# PORT-008 — 40 MHz flash control results

## Executive summary

**40 MHz flash did not repair the forward transfer.** One slow-profile record
failed with the same last-byte and CRC signature as the earlier 80 MHz control.
The P4 boot log confirms actual 40 MHz flash operation. Exact clock count and
five observed source data bits pass independently; receiver integrity fails.
Full EDP restoration and operational handback are recorded below. No further
record, EMOS update, wiring change or production promotion belongs to this run.

## Controlled build and invocation

1. Build `prx06-p4pc-flash40-r01-b2026-10-10-05-41-22Z`: application SHA256
   `a9923b0a399ddce95956a8968695541348caf74e7190622b551c506630b2fe47`,
   231,872 bytes. SDK/compiler and source match the retained 80 MHz reproduction.
   Generated configuration differs in exactly four keys, all representations of
   `ESPTOOLPY_FLASHFREQ` 80 MHz → 40 MHz. Application build identity/date changes
   are retained as normal generated metadata.
2. Receiver/canary source and compiled allocated sections match the previous
   reproduction exactly. Whole object hashes differ because build/debug metadata
   differ. Both bootloader/application headers specify 40 MHz, all three flash
   segments verify, and captured boot reports `SPI Speed : 40MHz`, silicon v1.3,
   IDF 5.5.5 and CPU 360 MHz.
3. The already-deployed 11,284-byte sender was verified by complete SD readback,
   SHA256 `bb80b22e961739b560d185bd218ba3bfed16ce2d0350b56e43f26e586cf42213`.
   It was not rebuilt or redeployed. Temporary startup alone selects mode3 and
   loads/runs the sender; the sender restores original startup before GPIO use.
4. Exactly one 1,024-byte record was armed at the first 24-NOP sender profile,
   gated on observed sender admission. No retry or subsequent sweep record.
   EMOS, mainboard VDP, wiring and probes remained unchanged; the historical
   raw-GPIO sender exception remains confined to this experiment.

## Comparison

The two failed runs use the same payload and scope. Receiver elapsed time is
completion evidence only; corrupt records do not establish useful throughput.

| Observation | Earlier 80 MHz control | New 40 MHz control | Expected |
|---|---|---|---|
| Endpoint verdict | Fail | **Fail** | Full pattern/sequence/CRC pass |
| First / last byte | `41` / `f4` | `41` / `f4` | `41` / `74` |
| Sequence | 1 | 1 | 1 |
| Stored CRC | `f3f4` | `f3f4` | `6474` |
| Calculated CRC | `ba67` | `ba67` | `6474` |
| Receiver elapsed, µs | 5,180 | 5,189 | Not a performance gate |
| Qualified source falling clocks | 1,024 | 1,024 | 1,024 |
| READY at those clocks | Low throughout | Low throughout | Low throughout |
| Source D2/D4/D5/D6/D7 mismatches | 0 | 0 | 0 |
| Source D0/D1/D3 | Unobserved | Unobserved | Not inferred |

Both acquisitions retain 45 seconds at 24 MHz, 1,080,000,000 samples.
The new trace is stored as a complete `logic.sr`, independently extracted and
verified against raw SHA256
`7e9597cd75c1d2a91d7a14636290dba253130cb2a14198735d977cd4e71ec4de`.
Source observations are at the Agon header; they do not prove P4-pad waveforms.
Matching CRC signatures are not a dump proving every received byte identical.

## Interpretation and evidence

1. Returning flash to the original observed 40 MHz is insufficient to restore
   correctness. Do not describe flash speed as the diagnosed cause or repeat
   the same control automatically.
2. This does not eliminate all software/configuration possibilities. The complete
   original executable/configuration remains unavailable; current EMOS/mainboard
   firmware were preserved, not replaced with their historical counterparts.
   Harness/pad timing and memory/DMA behavior remain unresolved candidates.
3. Ignored local `agents/port008-live-qualification/devkit-control-flash40-r01`
   retains preparation/build/config comparison, source/object hashes, image
   descriptions, actual boot log, installation/restoration receipts, USB verdict,
   full analyzer trace, decoded source observations and operational handback.
   [Previous 80 MHz experiment](DEVKIT-CONTROL-R01.md) remains unchanged.

## Restoration and completion boundary

Exact prior full EDP `port-008-data-r02-b2026-10-10-04-14-34Z` was restored;
all four segments verify, application SHA256
`86f112f59d641de85c2061e94955223f080d9df9c38b0c94be93c91e208db6ce`.
P4 HTTP availability was established before one Agon recovery reset. Fresh boot
and Extender input admission passed. Original 38-byte startup was independently
read back, SHA256
`7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`.
Actual remote command delivery accepted all 52 packets; final input is ready and
neutral with zero held/pending keys. Foreground listener exited. No active
capture, fixture, reset, flash or transfer remains. Bench is idle; Agon SD stays
in Agon. No new physical experiment is authorized by this result.
