# REMOTE-009 — What slowed bulk UART file transfers

The oldest working file service already made the Pi wait on each small UART
record. Later changes removed the expensive verification passes and moved the
file loop to the P4. The November 27 direct UART route brought the Pi back into
the loop. That explains most of the recent 3.8 kB/s result. Moving the loop back
to the P4 addresses that regression. The remaining gap to native UART streaming
is in the SD-file path and needs its own measurement. Historical transfers
already show that the P4 and mainboard VDP can sustain comparable UART rates.

Investigation contract `92e2476eb2258818edc10b74f5ee7a025464f6d0`. Source and
saved evidence only. No code, live bench, SD card, firmware or scheduler
operations were performed.

## What changed, oldest first

Dates are New York local. The first accepted run used a September 13 UTC run
ID and took place on September 12 local. The oldest source for the shipping
P4-to-mainboard SD service is Extender `69da46ac1795bbab748fefed22f9d73ffc96afcc`
and EMOS/foreground listener `71f362af4c64c8d2b74dd532f352358200a78f5c`. The
test host was `02e62e4e5ef2cba8409d55393fe4dd391331610a`. The older September 8
EMOS keyboard exerciser used an emulated UART peer and a one-byte local SD
test marker. It did not transfer files through the P4.
[First accepted physical build and complete image identities](../../qualification/mainboard-sd/2026-09-13.md)

| Stage | Source change and purpose | Measured effect or limit |
| --- | --- | --- |
| September 12, first working checked service | Pi sent one HTTP command per 212-byte WRITE or 216-byte READ, waited for its reply, slept 40 ms on the initial HTTP 202 and saved its journal before and after each command so an uncertain request could be resumed. P4 held one pending request and EMOS held one foreground mailbox. Records carried CRCs. The listener reread and digested the staged and activated file. The host reread both over UART. Every READ reopened, sized, sought and closed the file. WRITE used an open file and synced at FINISH, with separate metadata at BEGIN. | The largest accepted cycle replaced 131,731 bytes in **360.381 s**, including multiple reads and backup verification. The retained command trace attributes **238.764 s** to 1,524 successful READs, **36.911 s** to 622 WRITEs, and **34.042 s** to FINISH plus ACTIVATE. Those command times include host turnaround and cannot isolate the eZ80 CRC from its full-file rereads. |
| September 23, optional fast mode | Extender `77c25ebc` and EMOS `7c15439` skipped the host and listener whole-file verification passes at FINISH and ACTIVATE. Per-record CRCs, local acknowledgments, pre/post host journal saves and the 40 ms sleep remained. | Paired physical 8,192-byte uploads averaged **16.410 → 3.283 s**, a **13.127 s** saving (80.0%). The fast route eliminated 76 host READs for those two copies, each of which would have incurred the host pacing loop. The test changed the readback policies together. |
| October 25, checksum-free major 2 | Extender `0dd4f666` and listener `9a92d811` removed CRC work from fast records, upload descriptors and transaction metadata. The 20-byte envelope kept four reserved zero bytes. One record at a time, exact byte counts, file-error checks and host pacing remained. New path guards on metadata/mutations did not add a verification read to each fast WRITE. | The deployed route passed use checks. No retained one-variable timing isolates how much removing CRCs saved. A November 2 direct major-2 upload of 1.1 MB still needed **283.396 s**, with CRCs and whole-file verification already absent. |
| November 2, P4-staged UART | `ce3183ad` moved payload RPCs to the P4. The host exchanged a whole file with P4, which used its local SD spool and journaled at job boundaries. The P4 worker still waits for a local reply every 212/216 bytes, checks the transaction identity/offset, and sleeps one RTOS tick on pending status. The isolated `67dfc55b` comparison raised worker priority from 1 to 4. | For 1.1 MB, the priority-only change cut upload **301.930 → 43.240 s** (258.690 s, 85.7%) and download **308.909 → 243.200 s** (65.709 s, 21.3%). Against the original Pi-paced upload the final P4 path took **240.156 s less** (84.7%). That comparison covers a combination of changes. |
| November 3, sequential reader | Listener `b8e72c9`, adopted in Extender `8aa3245d`, held a single open file and reused the position on sequential fast READs. It kept read counts/errors and the same wire records. | Matched staged 1.1 MB download **250.920 → 43.573 s** (207.347 s, 82.6%). Both used 5,095 records. The P4 worker interval fell **249.277 → 42.100 s**. The filesystem change explains the measured saving in that comparison. |
| November 17, production two-way staging | `b2464214` selected the v0.3.0 P4 worker, EMOS and listener. Bench jobs defaulted to staged PARLIO. The P4 worker retained a checksum-free UART loop. Upload selects PARLIO only if the listener offers the capability and the P4 supports it. Download selects it when required by the job. Ordinary `sdserve --fast /` advertises neither parallel capability. | The recorded two-way production qualification used PARLIO. It cannot supply a fresh staged-UART rate for the current installed pair. The staged UART implementation is present in the pinned source. |
| November 27, direct UART used for bulk payload | The SET02 recovery upload and the isolated standard-runner candidate `0c0855e0` used the Pi direct client. That chose the original stop-and-wait leg even though the listener was checksum-free. | SET02 moved 1,089,200 bytes at **3,813 B/s**. November 2's direct major-2 baseline was **3,881 B/s**, about **1.8% faster** with a nearby payload size. The measurements are different runs. The source shows the same host pacing in both. |

Sources for the table are the [September per-command trace](../PORT-017/evidence/PORT-017-2026-09-13-01-21-04Z/requests.jsonl.gz),
[September checked/fast comparison](../REMOTE-005/FAST-TRANSFER.md),
[October installed baseline](../REMOTE-005.md), [November direct baseline](BASELINE-R01.json),
[staged worker A/B](STAGED-RESULTS.md), [sequential reader A/B](DOWNLOAD-RESULTS.md),
and the [production source pins](../../../production/bundles/olimex-parlio-v0.3.0/bundle.yaml).
For the September totals, group successful response durations by the
preceding request's operation byte (index 12), bounded by the last two
`cycle_pass` events. These are host durations. The timed test also reads the
previous backup and performs separate recovery cleanup, so its full cycle
is a different scope from an activated fast upload.

## What the recent upload spent

1. SET02's 285.684-second session and its activated UART receipt cover
   1,089,200 bytes. The retained dispatch-to-receipt file timestamps span
   about 287.2 seconds, a wider boundary. The upload receipt lives under
   VDPL-062 SET02 `uart-run/b-replacement-transfer/uart-receipt.json`
   (SHA-256 `5f1700397f2aeb40f7b722a30744a77641e08b5df3e232ca8d585bf237828ebe`).
2. A first fresh POST to P4's `/sd/rpc` queues the record and returns HTTP
   202 even if the UART owner quickly finishes it. The Pi client then sleeps
   40 ms before polling. `ceil(1089200 / 212) = 5138` payload WRITEs.
   Those initial sleeps alone schedule **205.520 seconds**, **71.9%** of the
   reported session. The file requires **10,276 host state fsync calls** for
   those WRITEs alone. No separate timing of those fsyncs, extra polls, SD
   service or IRQ/flow-control pauses survives for this run. Source owners are
   [Pi client](../../../scripts/sdcard.py), [P4 HTTP handler](../../../vdp/video/extender/network/wired_network_service.cpp),
   [P4 queue](../../../vdp/video/extender/storage/sd_service.hpp) and
   [P4 UART owner](../../../vdp/video/extender/transport/console_hardware.inc).
3. The released P4 source `be1d9432` configures UART1 at **1,152,000 baud,
   8N1, RTS/CTS**. EMOS `abefa2f` uses the same UART1 setting and its
   18.432 MHz F92 clock gives divisor 1. Its UART0 and the stock mainboard
   VDP v2.16.0 source (`c7ac293d2aa81ddfa693390549bcd909069c8fc3`) also select
   1,152,000 baud. That gives a nominal ceiling of **115,200 bytes/s** per
   direction. This establishes the configured value from source. SET02
   has no measured baud or active-versus-idle UART capture.
4. A full upload WRITE moves 212 useful bytes in 274 serial bytes across
   the two directions, including the request, reply and their envelopes.
   At the configured baud the same upload's payload WRITEs and replies
   account for about **12.22 seconds of nominal bit time**, absent gaps,
   control commands and retries. Much of the serial work can occur while
   the Pi sleeps, so do not add this figure to the 205.520 seconds. At
   that framing ratio even an ideal sequential request/reply loop has
   a useful-write ceiling of about **89.1 kB/s** before SD or scheduling.
   A 1 KiB+ credited window or a stream removes proportionally more of
   this cost than simply polling sooner.

## The two UART routes already have a matched reference

September's physical pure-data comparison ran the same eZ80 workload on
ordinary EMOS with the mainboard VDP on UART0 and the P4 on UART1. It used
the fused EMOS sender/receiver and the stock-shaped P4 owner loop. Bytes
were checked outside timing. These are historical measurements for their
pinned builds and scopes. The reverse test includes request handling and
256 small reply packets per return, so it measures relative parity and
does not give a reverse bulk-file ceiling.

| Scope | Mainboard VDP | P4 | P4 elapsed change against VDP |
| --- | ---: | ---: | ---: |
| eZ80 → VDP/P4, 65,535 payload bytes | 589.670 ms (111.14 kB/s) | 588.096 ms (111.44 kB/s) | −0.27% |
| VDP/P4 → eZ80, 2,048 useful bytes in matched return packets | 86.068 ms | 85.156 ms | −1.06% |

[Physical UART results](../PORT-008/uart-alignment/FINDINGS.md) ·
[Matched reverse method and clock limits](../PORT-008/uart-alignment/E07P-batch.md) ·
[Raw paired summary](../PORT-008/uart-alignment/results/e07p-transport.json)

The November P4-staged file results around 25 kB/s leave a substantial
forward gap even after the Pi waits and repeated READ setup are removed.
The worker timers combine P4 spool I/O, queue scheduling, UART transmission,
reply waits and eZ80 FatFS work. Available evidence does not apportion that
remaining time. It does demonstrate that extending host deadlines or removing
CRCs already absent from fast mode cannot close it.

## Repair and verification for review

1. **Remove the known regression in the shared bulk path.** Use the existing
   P4-owned, checksum-free staged UART worker for all ordinary bulk-file
   consumers. Require UART explicitly and preserve the carrier in the receipt.
   The Pi submits or retrieves one file and observes job status. P4 metadata
   operations may still use the direct client. This restores the November
   architecture with the existing EMOS and listener facilities. The matched
   historical evidence makes roughly 25 kB/s a useful staged comparison point,
   pending measurements on the current pair.
2. **Measure the gap that remains inside the P4-owned path.** Proposed physical
   comparison, pending review. Hold the same P4, EMOS, native VDP, media, baud
   and payload fixed. Compare one copy each way using direct and staged UART
   with an 8 KiB control and a 1.1 MB file. Repeat the matched ordinary VDP
   stream references on the same pair. Record one aggregate interval each for
   P4 spool/HTTP, active UART and idle (separate ready gaps from flow-control
   holds when observable), and eZ80 file read/write/sync. Compare payload
   bytes outside timing once for qualification. Use the current commissioning
   stop rule and decline any capture that requires new wiring before review.
3. **If the local record barrier dominates, remove it at both ends.** Reuse the
   existing P4 UART owner and EMOS admission. Negotiate a larger stream or
   window once, let the existing flow control and bounded buffers pace the
   payload, and exchange count/status at the agreed boundaries. Keep filesystem
   work in the foreground utility. Eliminate per-record waits and copies only
   where the measured change justifies it. Keep exact byte counts, filesystem
   errors and a clear terminal result. Full transfer time must report SD costs
   separately from the comparable native-stream rate. Check current ROM/RAM
   fit and the return-to-CLI path as part of any subsequent implementation.

The offline review is complete. A physical attribution run and any repair
await Smith's disposition.
