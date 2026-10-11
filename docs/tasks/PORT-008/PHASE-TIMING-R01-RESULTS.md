# Ordinary ExExt phase timing — physical results

## Executive summary

The principal measured cost is control work around each block, rather than UART
parking/restoration. Offer construction, offer/acknowledgement and completion
consume **70.3–80.7%** of the measured stream-plus-query/reply interval across the
four lengths. The guarded native payload runner accounts for only **2.1–15.8%**.
Full 4096-byte blocks also cause about **33–35 ms** of extra latency in the next
offer interval. Its precise EMOS/P4 split remains unresolved.

Twenty-four selected samples have exact full-buffer proof: **196,608 bytes**.
Five completed invocations retain every original endpoint/phase CSV and serial
capture; one matching fresh-repeat sample replaces an incomplete USB dump.
The exact original UART pair and startup are restored and verified. No transport
optimization, gameplay claim or production promotion follows this diagnostic run.

## Measured costs

Five comparison samples per length; warm-ups excluded. Values are median
[minimum–maximum] in **ms**. Ranking: largest fraction of M04 spent in the three
control intervals first. M04 ends after the seven-byte query and its six-byte
reverse packet; this is neither renderer completion nor HDMI FPS.

| Stream bytes | Parallel blocks, including query/reply | M04 ms | Three control intervals ms | Share of M04 | Native runner ms |
|---:|---:|---:|---:|---:|---:|
|256|3|66.875 [66.778–66.958]|53.931 [53.917–54.056]|80.7%|1.375 [1.361–1.389]|
|4097|4|133.778 [133.500–150.250]|106.028 [105.514–108.431]|79.0%|16.097 [16.097–16.111]|
|4096|3|116.847 [116.778–116.903]|88.861 [88.208–89.444]|76.0%|15.958 [15.958–15.972]|
|8192|4|200.181 [183.625–200.278]|140.472 [138.500–140.792]|70.3%|31.653 [31.639–31.667]|

The three control intervals contain CRC/construction, UART sending and waiting,
validation and coordinator admission; they do **not** isolate wire latency.

| Non-overlapping phase totals, median ms | 256 B | 4096 B | 4097 B | 8192 B |
|---|---:|---:|---:|---:|
|Offer/ACK plus admission guards|35.042|69.806|80.583|114.889|
|Matched completion exchange|13.486|13.639|18.125|18.361|
|Offer construction/CRC|5.417|5.417|7.222|7.222|
|Native runner incl. entry clocks/EOF|1.375|15.958|16.097|31.653|
|Electrical entry/arm|2.069|2.069|2.792|2.778|
|Electrical return + UART restoration|0.722|0.875|1.111|1.278|
|Remaining handover before completion|0.625|0.639|0.875|0.861|
|UART drain/park + coordinator setup|0.125|0.125|0.181|0.167|
|Serializer reservation|0.083|0.083|0.111|0.111|
|Outside block intervals|7.944|8.097|6.847|22.431|

Each sample conserves M04 exactly as its non-overlapping block intervals plus
outside-block time. Separately calculated medians need not add to the median
total. Full ranges, per-sample intervals and percentages are in
[results.json](PHASE-TIMING-R01/results.json). Outside-block time includes return
polling, ISR scheduling, caller/queue work and waits that these probes do not
separate. It is not idle CPU time.

## Findings and accepted direction

1. **Fixed EMOS control CPU work is a concrete suspect.** An ordinary offer
   interval is about 11.7 ms, and completion about 4.5 ms, even for the one-byte
   residual, seven-byte query and six-byte reverse packet. Source inspection
   finds six fourteen-byte CRC calculations on the successful offer path:
   initial offer validation; request sealing; ISR ACK validation; admission
   offer validation; admission ACK validation; coordinator self-validation.
   Construction adds one CRC and completion adds two. These are existing checks,
   not new probes. The exact-ROM [CRC instruction check](../../../tests/performance/stream_timing/crc_cpu.rs)
   returns the correct reference CRC for four inputs and executes 12,630–12,653
   instructions per CRC. This corroborates substantial local CPU work; it is
   not a physical CRC timer and does not prove all 11.7 ms belongs to CRC.

2. **The next offer after a full block carries additional backpressure.**
   Median offer/ACK intervals are 46.417 ms for the query after 4096 bytes,
   45.458 ms for the one-byte residual after 4096 bytes, and 44.986/46.208 ms
   for the second full block/query in the 8192-byte case. The initial offer and
   other short/reverse offers remain about 11.7 ms. The extra 33–35 ms is inside
   offer-to-coordinator admission, before the next payload runner. It is not
   explained by counting the next block’s byte loop. Existing eZ80 probes do
   not separate local pre-send checks, P4 parser/storage availability, ACK
   serialization or their scheduling; the source-path explanation is an open
   hypothesis requiring a smaller follow-up observation.

3. **UART park/unpark is not the leading measured cost.** Drain/park plus
   coordinator setup totals 0.125–0.181 ms per complete sample; electrical
   return plus UART restoration totals 0.722–1.278 ms. Electrical entry/arm adds
   2.069–2.792 ms. Combined median per-sample share for these three intervals is
   below 4.5%. Offer/completion UART control is outside those intervals: keeping
   UART disabled could still eliminate exchanges, but a saving cannot be
   predicted merely by removing the observed pad-transition work.

4. **Return servicing occupies real VBlank context.** Inclusive EMOS service is
   about 23.75–23.86 ms per sample, including a ~4.4 ms availability poll and
   reverse block. Buffered packet publication is 0.125–0.139 ms. These scopes
   overlap the block intervals and must not be added again. Their duration is
   relevant to responsiveness; this fixture does not measure a keypress latency
   distribution, IRQ utilization or game frame pacing.

5. **Author decision: no CRC in ExExt.** Ordinary stock MOS/VDP UART traffic
   does not perform these control CRCs; the project added them. The Author
   rejects the agent’s initial suggestion to accelerate that routine and requires
   removing CRC generation/validation from EMOS and EDP’s ExExt transport.
   No replacement per-block checksum is selected. Physical contention-prevention
   handshakes and the byte-verified qualification fixture remain. Define the
   paired control format/version, implement removal and repeat these streams
   in a separately frozen tranche. No removal has been implemented here.
   The extra post-full-block offer latency remains separately unresolved.

Stock references remain clean at MOS v3.0.2 and VDP v2.16.0:
[MOS byte output](../../../../../agon-mos/src/serial.asm),
[MOS returned-packet parser](../../../../../agon-mos/src/vdp_protocol.asm) and
[VDP serial setup](../../../../../agon-vdp/video/vdp_protocol.h). MOS dispatches
returned packets after their declared body length, without a CRC trailer.
The project's version-2 control CRC is an added protocol cost, not a stock
VDU requirement.

## Endpoint consistency and timing limits

PRT1 /256 divides nominal 18.432 MHz to 72,000 counts/s: 13.889 µs/count;
0.9102 s single-pass range. All selected rows have flags zero, monotonic complete
phase sequences and conserved forward bytes (stream plus query), with a reverse
block. Two probes plus call/arm/read control measure one PRT count; no assumed
constant is subtracted. Capacity is 512 records; no overflow occurs. No SD/USB
logging or HTTP video/status request runs inside a measured interval.

| Stream bytes | Preceding M04 median ms | Phase M04 median [range] ms | Median elapsed change |
|---:|---:|---:|---:|
|8192|183.625|200.181 [183.625–200.278]|+9.02%|
|256|66.694|66.875 [66.778–66.958]|+0.27%|
|4097|133.431|133.778 [133.500–150.250]|+0.26%|
|4096|116.722|116.847 [116.778–116.903]|+0.11%|

Positive percentages mean this diagnostic campaign took longer. This is a
context/overhead check against the [preceding campaign](STREAM-TIMING-R01-RESULTS.md),
not an identical-build causal comparison. The largest median shift is one
roughly 16.7 ms VBlank interval; ranges overlap at 8192 bytes. Probe perturbation
and scheduling phase are not isolated. M02 is deliberately zero/unmeasured;
the payload probe includes native entry/EOF and is not exact last-edge timing.

MOS increments two raw coarse units per VBlank, approximately 120 units/s here.
Calibration retains 1199–1205 PRT counts per two MOS units (~16.65–16.74 ms).
Five groups record 1616–1796 raw run units (~13.47–14.97 s at that nominal cadence),
including preparation/dumps before saving. Host invocation/setup/retrieval totals
385.5 s; individual groups take 73.4–79.3 s. Initial installation and final
restoration are separate from these figures. No spoken notification was needed.

## Exact builds, provenance and restoration

| Component | Measured identity | Verification |
|---|---|---|
|EMOS|`agon-emos-v0.1.24-b2026-10-11-20-54-06Z`, source `291ac9eb3b733b62254e0bd09dba89c310c369c6`|Full 128 KiB ROM readback|
|P4 EDP|`port-008-stream-r14-b2026-10-11-16-29-33Z`, same retained snapshot as preceding comparison|All four flash segments|
|MOSlet|`port-008-phase-timing-r01-b2026-10-11-21-02-50Z`, source `5c33e6d7`|Exact ELF/ROM binding; full SD readback|
|Mainboard VDP|Existing fsim custom VDP, unchanged|Previously verified handover identity; no new readback|

1. Diagnostic EMOS image SHA256 `f13cca9c3ca811e0a349b51d039075b760343b23269950d556cabc80b2452609`;
   full ROM SHA256 `837ede2c7fa7ed75b41297f5b13d44873ada9b3a94403568fb485cb2edad33ab`.
   Compiles at 131,063 ROM bytes (9 free), 95 bytes above its ordinary control.
   No product functions removed. Ordinary builds preprocess probes out.
2. MOSlet SHA256 `d8b2ca624ccedbfd0d5a65760dff06f82aba862f9b96c60f8c86e337d48f2bff`.
   Sixteen verified callsite PCs dispatch through one guarded ROM leaf into
   MOSlet RAM. All register/stack/IFF, disabled, capacity and overflow controls
   pass the retained CPU-model checks; those are not physical timing proofs.
3. All five invocations return to the CLI with six saved endpoint/phase rows.
   USB captures lose 50 bytes at original 256-byte repeat1 and 80 bytes at fresh
   256-byte warm-up. Neither is padded or treated as proved data corruption.
   The first chronological intact dump for each original repeat index selects
   23 original rows and fresh repeat1. Selection depends only on byte integrity.
4. [Selected endpoints](PHASE-TIMING-R01/samples.csv),
   [selected phase rows](PHASE-TIMING-R01/phases.csv),
   [callsite names](PHASE-TIMING-R01/phase-sites.json) and
   [evidence/origins/hashes](PHASE-TIMING-R01/evidence.json) retain reproducibility.
   Original serial logs, CSVs and local install/restore receipts remain under
   ignored `agents/phase-timing-r01/bench-r01`; retained P4 source-snapshot hashes
   remain in the preceding result record. Git HEAD is not substituted for them.
5. Restore old EMOS once, then its exact P4 data-r20 partner with Agon held reset.
   The old P4 build predates the newer pad-release log marker; installer waits
   for it unnecessarily, then releases reset in cleanup. Actual admitted input
   and the listener recover without another reset or flash. All four P4
   segments and full original EMOS ROM verify. Original 38-byte startup is
   independently read back, known temporary sibling resolved, actual Legacy CLI
   ECHO succeeds, neutral input remains ready for five seconds, listener/collector
   are stopped and reset released. No wiring/probe/game/mainboard VDP change.
   Bench released at `2026-10-11T21:30:45Z`. Production selection unchanged.

## Follow-up boundary

Only [PT01–PT06](PHASE-TIMING-R01.md) are complete. The broader ExExt goal stays
paused. Discuss optimization order before changing either processor’s transport.
Author also requested review of direct ExCom ↔ ExExt switching: EMOS currently
requires an intermediate Legacy request. P08-P04 in the contract owns that
follow-up; this run changes no transition behavior.
