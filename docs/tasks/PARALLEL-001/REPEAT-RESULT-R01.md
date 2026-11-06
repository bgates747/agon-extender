# Repeated parallel boundary checks — bench64

The filtered development pair passes both selected176-record cases, including
four positive session closes per case and176 guarded UART0 source releases and
ordered replies. Both endpoints compare every opaque byte. This strengthens
bounded transport evidence; it does not identify the electrical cause of the
old extra VALID edge, establish long reliability or qualify Wolf over parallel.

## Actual results

The mixed UART0/parallel workload appears first. Timing scopes differ; the table
is a qualification comparison, not a pure-wire speed ranking or speedup claim.

| Observation | Guarded UART0 + parallel | Plain parallel |
|---|---:|---:|
| Native / independently checked peer records | 176 / 176 | 176 / 176 |
| Positive OPEN / session closes | 4 / 4 | 4 / 4 |
| Opaque payload bytes per direction | 9,936 | 9,936 |
| First error / RELEASE result / restore witness | 0 / 0 / 1 | 0 / 0 / 1 |
| Required-size checks | 360 | 360 |
| UART0 source-release witnesses | 176 / 176 | Not selected |
| Ordered point replies | 176 / 176 | Not selected |
| Native elapsed, nominal120Hz MOS counts | 636 | 572 |
| Native elapsed, nominal seconds | 5.300000 | 4.766667 |
| Peer host interval, seconds | 15.351701406 | 14.900588900 |
| Saved native result / actual CLI / collection | PASS | PASS |

Each case uses four declared sessions and four rounds of eleven lengths:
0,1,2,17,63,64,65,75,79,127,128 bytes. Ramp, complement, alternating00/FF and
walking-bit patterns vary by session/round/record. eZ80 and host compare all
bytes; no communication checksum, retry, payload fallback or uncertain replay
is added. Required-size queries retain the same pending record. Each new
session follows positive RELEASE/peer EOF. Guarded operation serializes a
static67-byte UART0 batch, source release and ordered point reply before the
next parallel record. Callback retirement is checked separately.

Native elapsed excludes mode-entry/restoration settling and includes epochs,
progress, closes and selected work. Peer elapsed includes registration and
setup and ends at the final close. They are different intervals, neither a
calibrated transport rate nor optical/render FPS. No IRQ-latency, failure-
injection, unattended long-watch or arbitrary receiver-completion claim follows.

## Frozen implementation and evidence

1. Final selected78-input [physical freeze](REPEAT-PHYSICAL-FREEZE-R03.json)
   identifies local manifest SHA
   `c8399d96a41b2bfa2d20f13f0551187cf27bb3e74e74ffcecbddd50a777e383a`.
   Earlier unexecuted R01/R02 and their narrow host admission-path/digest
   corrections remain preserved. Runtime inputs were not changed under64.
2. P4 app1764368B
   `37ba69e3648ea2e7663d071149acc057fab64f8546af3d784afa711505f8e38e`,
   build `net-004-r04-b2026-11-06-09-24-54Z`, source
   `f3a102d574df0d76a0bfab7676b9a5807cbdffd8`.
   Full1765376-byte touched span including known suffix is
   `bfb8962872bd832c5627a49cbf68d8a82bd3774b09aa30bf0eee5b2b9bcf2cbf`.
   EMOS complete131072B is
   `8270ecd709138fe5ae617a91d5d365eeede0738025d5043fc790541b19b8f281`.
   Both temporary writes were independently read back before invocation.
3. Native source `d59c796d5766611454bb7aef68eb5ed3038be786`:
   plain16799B
   `3ae08d0f574e86472f04b4c37119460bc6bfe108f2a99ae6f8993533bde21e5e`;
   guarded17886B
   `d343dd13171d13058daa44dcff1dbb160f2e779e2b9504f6d26af14b0dcc9df8`.
   Fourteen owner-control checks and sixteen runner/peer checks passed under
   normal compiler FIFO. Each physical RUN was issued once.
4. Plain result210B
   `c9477a52ced15a5f8c94a12fce7764c2e24523fc6890e1a09b395de53521bd10`;
   guarded result275B
   `a95d74ea80c8c2139506e709d0835e552bb1ecba36783b68380524ace18ad474`.
   Machine-local evidence retains original actor/peer/native/P4 captures,
   complete collected results, twelve evidence hashes, raw state, collection
   and retirement receipts. All original actors/readers/peers joined.
5. Partial ordinary P4 telemetry1614B/2132B contains no observed fault or reboot
   marker. It is not a complete trace or proof that no P4 fault could occur.
   Strict edge counts, DMA completion, byte totals and deadlines remain intact.

## Restoration and custody

Extender restored and independently compared the complete131072-byte UART
EMOSa25f ROM and maximum1765376-byte incoming UART P4 span629a, including the
suffix beyond the shorter UART application. UART P4d9bcb boot, input and actual
CLI passed. Mainboard5d657/profile8, bootloader/partitions/NVS, startuped403 and
listener0566 were unchanged. Final getter4999 confirmed exact feature absence,
ordered clear, restored callback and no retained buffer. Fresh mode0/callback0/
Legacy0, actual CLI/cursor, unchanged files, neutral input, offline listener,
idle worker, free USB and joined actors all passed. SD remains mounted; RAM
holds the getter.

Actual64 release: **2026-11-06T23:09:34.586437UTC**. Wolf's new bytewise-span
comparison was the actual next request and requires its own fresh grant. No
further test, live match or replay was added to64. MechAgon's separately frozen
finite live case follows normal FIFO; its preparation does not transfer custody.
The [goal task](../PARALLEL-001.md) remains active: Wolf's specific parallel
endpoint remains unresolved and its ordinary-carrier results are separate.
