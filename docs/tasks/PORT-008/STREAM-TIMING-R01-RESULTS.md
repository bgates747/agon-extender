# Matched UART and parallel stream timing — physical results

## Executive summary

The byte-verified comparison confirms substantial overhead in the current
parallel application path. Parallel wire drain takes **6.57× UART time for 256
bytes**, **2.30× for 4097 bytes**, and **1.37× for 8192 bytes**. Exactly one 4096-byte
batch drains **17.2% faster** than UART, but its ordered processing/reply endpoint
still takes 62.6% longer. A one-byte boundary crossing increases parallel drain
from 30.6 to 84.8 ms. This points first to block handover, residual batching and
return-service scheduling, rather than assuming the parallel byte loop itself
is uniformly slower. Exact phase attribution remains unmeasured.

All 48 selected samples have zero flags and exact full-buffer evidence:
393,216 checked bytes, including eight warm-ups excluded from timing summaries.
Five USB dumps across twelve completed invocations are incomplete; four missing
original samples use their matching repeat from a fresh invocation. Original
records and every selection are retained. No measured firmware, transport or
workload optimization was made. Exact UART pair/startup restoration and independent verification are complete.

## Common conditions and clocks

1. Both routes send the identical RAM-resident buffer-adjust command through
   one counted RST18 call. Total command lengths are 256, 4096, 4097 and 8192
   bytes; each includes an eleven-byte header. EDP preallocates one 8192-byte
   target buffer before timing. Each sample poisons it with AA, performs the
   measured update, then dumps all 8192 bytes outside timing for exact checking.
   UART means ExCom to the same P4 EDP; this is not a mainboard-VDP rendering
   comparison.
2. Both routes use the same P4, parser, mode 3 and HDMI configuration. Browser
   video has no connected client. Ordinary interrupts remain enabled. The
   mainboard retains the fsim project's custom VDP, not a stock control.
3. PRT1 divides the nominal 18.432 MHz eZ80 clock by 256: 72,000 counts/s,
   13.889 µs/count and a 0.9102-second single-pass range. Equivalent CPU cycles
   are elapsed counts × 256, including interrupts and waits; they are not
   retired instructions or CPU utilization. Saturated intervals are invalid.
4. MOS 3.0.2's VBlank handler increments the coarse clock by **two** per
   interrupt (`agon-emos/src/interrupts.asm`). Calibration records about 1200
   PRT counts and two MOS units per VBlank: approximately 16.667 ms. At this
   observed cadence MOS accumulates about 120 units/s, not 60. Retain raw coarse
   units; do not label them centiseconds or divide them by 60. This is a
   consistency check, not an independent oscillator calibration.
5. M01 measures submission return; M02 observes final transmission in software;
   M03 observes parallel block completion; M04 includes the subsequent seven-byte
   pixel query and reverse reply. The query proves synchronous buffer processing,
   not renderer completion. M02 can precede M01 when the final output call blocks.
   M03−M02 covers only the final block's tail/receipt, not previous handovers.
6. One warm-up plus five comparison samples per length/route are retained.
   Medians and ranges exclude warm-ups. Positive percentage changes mean
   parallel took longer than UART. Tables rank worst wire-drain slowdown first.
7. Immediate-read controls record zero PRT counts; empty UART drain records
   zero and parallel drain one. Zero counts mean below the timer's resolution,
   not literally zero instruction cost. No constant overhead is subtracted.

## Build and evidence identities

| Component | Selected identity | Verification |
|---|---|---|
| Timing EMOS | `agon-emos-v0.1.24-b2026-10-11-19-00-57Z`, source `d7f25d8` | Full 128 KiB ROM readback |
| P4 EDP | `port-008-stream-r14-b2026-10-11-16-29-33Z`, base `0154daf7d308866ec01ee233aaa481ebf219832a` plus retained source snapshot | All four flash segments independently verified |
| MOSlet | `port-008-stream-timing-r01-b2026-10-11-19-32-51Z` | Exact ROM fingerprint/bindings; full SD readback; linked ABI checks |
| Mainboard VDP | fsim custom image; unchanged | Identity from preceding verified fsim handover, no fresh readback |

1. Timing EMOS image SHA256:
   `74c3b1f438c06d8107f151e26e32187f0b50f7d3c831dae5db3f38e43f52e3c4`.
   Full ROM SHA256:
   `a4e46930022332264cf0dad78d1e129d8edc7757c3c702a1ec65b1a080184b99`.
2. P4 application SHA256:
   `5833c4aa3a54e734c91b855b37271c43c7e5db8b7b2269a3410bddb7f5e1c4ad`.
3. MOSlet SHA256:
   `b20f3845d6d9e22494aa63c920afbc1b6dd03bcfd793c22e36e0ff241987e24f`.
4. Mainboard VDP SHA256:
   `67f6f11f53209ef06ab9452024caf87beb357a2a8280a858df4e5cd3a796f9bb`.
5. The P4 build declares dirty source and a verified snapshot. Its Git base
   alone does not reproduce these bytes. Retained `p4-r14/source.tar.gz` SHA256:
   `e0acc254cf2660ab4b47a3c87c9d5abacade9b0f51c7af4c6af5b510c481e6ff`.
   Source-input inventory SHA256:
   `a610a71cdb3705731e49139d55b146a0656a143a86abdf8dbd1759f3e7f69d30`.
   Full local build-manifest SHA256:
   `f1998a512a4d75879d3a0511dd51497b64a95b408e5b5d4652889d4caeb8e3fd`.
6. Full serial captures, installation/readback receipts and machine-local
   invocation journals remain in ignored `agents/stream-timing-r01/bench-r01/`.
   Payload hashes and reproducible source are in the
   [fixture instructions](../../../tests/performance/stream_timing/README.md).

## Capture qualification and sample provenance

1. Twelve invocations complete, each saving six zero-flag rows and returning to
   the CLI. Five individual USB dumps fail completeness: UART256 repeat3,
   UART256-r02 repeat4, UART8192 repeat3, parallel4097 repeat3 and parallel8192
   repeat2. The first loses 108 trailing AA bytes; the parallel4097 loss is 78
   trailing bytes; parallel8192 loses 110 bytes including a gap within uploaded
   data. A shifted comparison after a capture gap is not proof of wrong received
   data. Incomplete samples are excluded, never padded or reconstructed.
2. Initial serial reading/parsing shares a thread. Later collection uses a
   dedicated raw-reader process; the final five groups use host tmpfs before
   retention. Both approaches still see occasional loss. No collector cause
   is established and no EDP logging change is made.
3. After independent cases, four fresh invocations repeat only cases already
   observed complete at the CLI. There are no uncertain replays or resets during
   acquisition. For each route, length and original repeat index, use the first
   chronological zero-flag row with its complete exact dump. Four original
   indices need their matching fresh repeat; the other 44 remain original.
   No row is renumbered and no timing fields are spliced. The selection rule is
   recorded before processing the complete comparison and depends only on byte
   integrity, not elapsed time.
4. The unchanged full validator accepts 24 selected rows and 24 complete dumps
   per route. [Raw selected rows](STREAM-TIMING-R01/samples.csv),
   [numeric results](STREAM-TIMING-R01/results.json) and
   [source hashes, exclusions and row origins](STREAM-TIMING-R01/evidence.json)
   preserve the comparison. Original serial logs/CSVs remain in the ignored
   evidence silo; selected log fragments retain their source text with normal
   text-reader newline normalization, not synthesized expected bytes.

## Sender submission — M01

Median [minimum–maximum], µs. Equivalent cycles/byte use the median elapsed PRT counts; they include waits and interrupts.

| Wire bytes | UART µs | Parallel µs | Parallel elapsed change | UART cycles/byte | Parallel cycles/byte |
|---:|---:|---:|---:|---:|---:|
|256|2319.4 [2319.4–2333.3]|83.3 [83.3–83.3]|-96.4%|167.0|6.0|
|4097|36902.8 [36888.9–36916.7]|35902.8 [35833.3–36097.2]|-2.7%|166.0|161.5|
|8192|73791.7 [73763.9–73805.6]|106250.0 [104972.2–107138.9]|+44.0%|166.0|239.1|
|4096|36916.7 [36902.8–36916.7]|35944.4 [35888.9–35986.1]|-2.6%|166.1|161.8|

## Sender wire drain — M02

Median [minimum–maximum], µs. Equivalent cycles/byte use the median elapsed PRT counts; they include waits and interrupts.

| Wire bytes | UART µs | Parallel µs | Parallel elapsed change | UART cycles/byte | Parallel cycles/byte |
|---:|---:|---:|---:|---:|---:|
|256|2333.3 [2333.3–2347.2]|15333.3 [15319.4–15361.1]|+557.1%|168.0|1104.0|
|4097|36916.7 [36902.8–36958.3]|84847.2 [83833.3–85458.3]|+129.8%|166.1|381.7|
|8192|73805.6 [73777.8–73819.4]|100861.1 [99611.1–101763.9]|+36.7%|166.1|226.9|
|4096|36930.6 [36916.7–36930.6]|30569.4 [30527.8–30583.3]|-17.2%|166.2|137.6|

## Ordered processing and reply — M04

Median [minimum–maximum], µs. Equivalent cycles/byte use the median elapsed PRT counts; they include waits and interrupts.

| Wire bytes | UART µs | Parallel µs | Parallel elapsed change | UART cycles/byte | Parallel cycles/byte |
|---:|---:|---:|---:|---:|---:|
|256|5763.9 [5666.7–6083.3]|66694.4 [66638.9–67097.2]|+1057.1%|415.0|4802.0|
|4097|71083.3 [70958.3–72097.2]|133430.6 [133333.3–150138.9]|+87.7%|319.8|600.3|
|8192|141305.6 [140763.9–142444.4]|183625.0 [183430.6–200152.8]|+29.9%|317.9|413.2|
|4096|71791.7 [70833.3–71930.6]|116722.2 [116611.1–116791.7]|+62.6%|323.1|525.2|

## Parallel completion — M03

No UART counterpart: UART has no matched block-completion receipt. M03−M02 below is calculated per sample before taking its median.

| Wire bytes | M03 µs, median [min–max] | Final block tail/receipt µs, median [min–max] |
|---:|---:|---:|
|256|20388.9 [20333.3–20597.2]|5041.7 [5013.9–5236.1]|
|4097|90027.8 [88875.0–90472.2]|5013.9 [5000.0–5180.6]|
|8192|106277.8 [105000.0–107166.7]|5416.7 [5388.9–5472.2]|
|4096|35958.3 [35916.7–36013.9]|5388.9 [5375.0–5444.4]|

## Duration and calibration

Fixture duration includes allocation, poisoning and verbose USB dumps before CSV saving. Approximate seconds use each group’s measured PRT/VBlank ratio. Host total additionally includes CLI setup, CSV retrieval and validation; neither is pure benchmark time.

| Route | Bytes | Raw MOS run units | Approximate fixture s | Host group s | Read/empty-drain PRT counts | PRT counts / MOS units per VBlank |
|---|---:|---:|---:|---:|---:|---|
|excom|256|1276|10.633|62.644|0/0|1200/2|
|excom|256|1300|10.833|63.565|0/0|1200/2|
|excom|4096|1286|10.717|63.859|0/0|1200/2|
|excom|4097|1298|10.817|63.789|0/0|1200/2|
|excom|8192|1386|11.550|65.045|0/0|1200/2|
|excom|8192|1382|11.517|64.551|0/0|1200/2|
|exext|256|1394|11.607|65.544|0/1|1199/2|
|exext|4096|1440|12.020|66.142|0/1|1202/2|
|exext|4097|1484|12.346|66.925|0/1|1198/2|
|exext|4097|1474|12.253|66.233|0/1|1197/2|
|exext|8192|1510|12.615|66.975|0/1|1203/2|
|exext|8192|1480|12.364|66.705|0/1|1203/2|

## Findings and next investigation boundary

1. EMOS quickly queues the 256-byte parallel stream (83 µs), but transmission
   finishes at 15.3 ms and ordered reply at 66.7 ms. Submission return is not
   evidence of completed work or equivalent spare CPU time: real VBlank service
   can perform later synchronous transport work.
2. The full 4096-byte batch is the only measured wire-drain win. The 4097-byte
   stream adds one residual byte yet more than doubles parallel drain. The
   8192-byte stream is 36.7% slower than UART. Small fragments and batch-boundary
   behavior deserve priority over an assumption of uniformly slow GPIO writes.
3. Final parallel tail/receipt costs another roughly 5.0–5.5 ms. Earlier block
   handovers remain inside M02. M04 also includes query submission, eZ80 return
   polling/publication, reverse transport and EDP processing; its extra time
   cannot be attributed solely to EDP or renderer work.
4. Next recommendation: split a block's measured cost into EMOS reservation/
   offer, UART parking, native byte loop, completion/release and VBlank return
   service. Reuse these byte-verified workloads before optimizing. The existing
   synchronous VBlank service and shared-pin control exchanges are concrete
   source suspects, not yet separately quantified causes. Preserve EMOS-owned
   routing and the existing electrical release contract.
5. This test performs buffer updates, not a graphics workload. It establishes
   no physical FPS, gameplay improvement, CPU utilization, raw electrical
   bandwidth or universal root cause. No transport changes or production
   promotion are authorized by the result itself.

## Handback

1. P4 `port-008-data-r20-b2026-10-11-09-07-32Z` restored; all four flash
   segments verify. Application SHA256:
   `01cbd53255fbbae4760bc2ba64fc0f987cb9ef828b397d17a7cd7a64b9322771`.
2. EMOS `agon-emos-v0.1.24-b2026-10-10-01-48-39Z` restored with one FLASH
   submission. All 131072 ROM bytes match the retained image plus FF padding;
   full ROM SHA256:
   `69d7b11ac1fa6fcd48cc3770356c3b8806d8f308c345bd670075a7eb21b613dd`.
3. Original 38-byte startup independently read back; SHA256:
   `7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`.
   Temporary backup resolved. No startup-triggered test remains.
4. Restoring P4 first leaves the mixed pair without keyboard admission; a paired
   reset does not recover it. Reinstalling its matching stream-r14 partner
   restores input. Submit old EMOS once, then finish old P4 restoration; only
   the complete restored pair supplies the final ROM/readback proof. This is
   a restoration-order/admission limitation, not a new timing result. Its
   precise cause and broader warm-reset qualification remain open.
5. Actual Legacy CLI input and five seconds of stable admitted neutral input
   pass. No held/pending keys, listener transaction, collector, test, flash or
   reset hold remains. Mainboard custom fsim VDP, wiring, probes, games and
   production selection are unchanged. Bench released at 20:20 UTC.
6. Final local receipt: `agents/stream-timing-r01/bench-r01/final-handback.json`;
   P4 restoration receipt: `restore-p4-r02/restoration/receipt.json` below that
   silo. All three installed-current local records are refreshed. Stop for
   Author discussion before transport optimization; the broader goal stays
   paused.
