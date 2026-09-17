# Initial physical codec results

## Executive summary

SRLE2 passes the initial exact-byte P4 codec controls, but is not yet qualified for live streaming. Encoding takes about 9–11 ms for sprite examples, 24–25 ms for scrolling patterns and 676 ms for noise. Unconditional live entropy encoding would therefore be unsuitable; game comparisons and asset-command qualification remain pending.

The exact saved EMOS ROM was restored and independently read back. Mainboard VDP remains stock 2.16.0, untouched. Candidate `srle2-p4-r02-b2026-09-17-02-24-44Z` was flashed and independently verified on P4. Mainboard has not been reset into EMOS yet: the mounted MOS-test card lacks the usual Extender service files, and the Author has been asked whether to prepare that card or use the usual card already in the Agon. No changes were made to the mounted card.

## Codec controls

Twelve original-CLI golden cases each passed P4 encode, decode and two-layer unpack: 36 controls, each with one warmup and three measured repetitions. Three bounded malformed streams were rejected, each followed by successful valid decoding. Collection took 17.53 seconds. Minimum reported HTTP-task stack reserve was 11,996 bytes. These are codec-only RPC tests, not rendering, asset command-stream or browser-output measurements.

Mean of three post-warmup device timings; original golden bytes are the correctness oracle. No mainboard timing baseline is claimed.

| Case | Encode ms | Decode ms | Unpack ms | RLE2 bytes | SRLE2 bytes |
|---|---:|---:|---:|---:|---:|
| noise | 675.948 | 613.966 | 621.911 | 196579 | 151696 |
| scroll2 | 25.148 | 16.908 | 23.792 | 49262 | 530 |
| scroll1 | 24.795 | 16.889 | 23.806 | 49214 | 491 |
| scroll0 | 23.793 | 16.881 | 23.690 | 49166 | 369 |
| stripes | 13.438 | 8.493 | 13.622 | 24590 | 145 |
| sprites1 | 10.813 | 6.493 | 10.121 | 15022 | 613 |
| sprites0 | 10.811 | 6.557 | 10.212 | 15031 | 654 |
| sprites2 | 10.809 | 6.508 | 10.167 | 15022 | 611 |
| retained-sprites | 8.974 | 5.193 | 8.232 | 7038 | 919 |
| solid | 6.492 | 2.975 | 5.531 | 3040 | 55 |
| colours | 5.745 | 2.557 | 2.575 | 78 | 111 |
| tiny | 5.474 | 2.381 | 2.390 | 15 | 46 |

## Next action and limits

Resolve card location/preparation, boot restored EMOS and verify keyboard/SD service, then finish H03 asset command controls before matched H04 game runs. Size-based fallback alone does not avoid the time already spent compressing a frame. Keep that distinction explicit when assessing any live-output policy. No scheduler, EMOS or mainboard VDP changes are justified by these measurements.

Private deployment receipts and per-repetition timing/header evidence are retained under `agents/srle2-hardware/`; source and procedures are in this task silo. Current P4 is the diagnostic candidate, not the production baseline. No product acceptance or hardware gameplay readiness is claimed.
