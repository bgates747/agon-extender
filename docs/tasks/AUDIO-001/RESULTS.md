# AUDIO-001 AF01 — Stereo streaming feasibility

## Executive summary

**Worth pursuing, but uncompressed 44.1 kHz/16-bit stereo is not yet feasible at the measured read-and-send budget.** The current Agon card supplies about 189–199 KiB/s; the audio alone needs 172.27 KiB/s. Applying the historical fast parallel result to today's SD measurements predicts approximately 1.07–1.12 seconds of producer work per second of audio, before framing, handovers, video or other overhead. This is a model using separate experiments, not an end-to-end measurement or proof that the hardware cannot be made fast enough.

**The next useful experiment is a sustained, CRC-checked SRAM-to-P4 parallel benchmark through EMOS, followed by the combined SD/read/send loop.** The current EMOS byte loop is substantially different from the historical fast assembly loop. Do not promise that old throughput for the integrated path. At today's best SD rate, parallel would need roughly 1.31 MB/s (1.25 MiB/s) just to break even, with no allowance for other work. Alternatively, a verified storage improvement could change the result.

No firmware was flashed. A new storage-only fixture ran on the Agon's own card, all six profiles passed its bounded checks, and startup was verified unchanged. No parallel transfer or stereo playback was claimed. AF01 is complete; AUDIO-001 integration remains pending AF02. Golem was excluded.

### Current hardware results

Each profile read 1,048,576 bytes. Times use the application's 100 Hz clock. The final column adds **historical** parallel time at 838.9 KiB/s (205.35 ms per audio second), for planning only.

| Read chunk (bytes) | Whole read (ms) | SD KiB/s | SD work per audio second (ms) | Model: read + historical send (ms) |
|---|---:|---:|---:|---:|
| 512 | 5,480 | 186.86 | 921.9 | 1127.2 |
| 2,940 | 5,420 | 188.93 | 911.8 | 1117.1 |
| 4,096 | 5,140 | 199.22 | 864.7 | 1070.0 |
| 8,192 | 5,280 | 193.94 | 888.2 | 1093.6 |
| 16,384 | 5,160 | 198.45 | 868.1 | 1073.4 |
| 8,192 | 5,220 | 196.17 | 878.2 | 1083.5 |

4096-byte reads were fastest in this small sample, but the 8192-byte repeat varied and there are too few trials to select a permanent optimum. Opening each file took 20–40 ms, excluded from the read column; a continuous player should keep the stream open. A 2940-byte chunk is exactly 735 stereo sample frames, or 1/60 second of the requested audio. Larger storage reads may be divided into bounded transport records without copying their entire contents again.

## Method, reproducibility and limitations

- Fixture: [source](sdbench/src/main.c), [Makefile](sdbench/Makefile), [raw CSV](results.csv), [deployed identity](deployment.json).
- Build: `make -C docs/tasks/AUDIO-001/sdbench`, using `agondev-config --prefix` and its C toolchain. No external audio/video assets.
- Run from MOS: `LOAD /test/audio001/sdbench.bin`, then `RUN`. It returns to MOS; no key wait or mode change.
- Fixture creates its own 1 MiB `/test/audio001/data.bin` and writes `/test/audio001/results.csv`. Setup writes are outside timings. Re-running overwrites only those task files.
- Counts, first/last bytes of every read and close results passed. These checks are **not a full CRC**, nor exhaustive storage correctness tests. Reports/console output occur outside timed reads. Loop and endpoint-check overhead is included.
- Six sequential reads of the same new file, one card, current installed EMOS; not a cold-cache experiment or latency-distribution study. Current EMOS binary hash was not established. The source revision below is inspected source, not proof of the flashed image.
- Deployment was read back before execution. SD service provided the result file; it was exited afterward. Host-mounted MOS-test SD was untouched. Test files remain in `/test/audio001` for reuse; no production application changed.
- Initial keyboard admission was unavailable. Mainboard reset attempts and a P4 serial capture/restart sequence restored admission, followed by clearing the mainboard screen. No firmware update was necessary. Private control/serial logs remain in ignored `agents/audio001/`.

## Existing code and evidence

| Component | What exists | What this establishes / does not establish |
|---|---|---|
| Legacy `agm/design-considerations.md` | Stock MOS 2 MiB reads, best 196.54 KiB/s | Consistent with today's scale; different historical run, not paired firmware comparison |
| Legacy `docs/prx-06-results.md` | Isolated 1024-byte fast assembly records, roughly 837–839 KiB/s; endpoint byte/CRC validation | Parallel can be fast; only 22 valid short records and older wiring/contracts, not sustained integrated audio |
| EMOS `src/emos_parallel.c`, `emos_parallel_engine.c`, `emos_parallel_io.asm` | Port ownership, READY-boundary handshake, bounded records, target GPIO binding | Implementation exists; this study did not qualify it on the present harness |
| P4 `vdp/video/extender/transport/p4_parallel_target.cpp` and associated config/data-plane/qualification files | PARLIO RX/GDMA, capture and queue machinery | Not a complete production stereo ingress route; configured 10 MHz is not achieved throughput |
| Jukebox `src/asm/play.inc` | SD chunks then VDP sample-buffer uploads; alternating mono playback channels | Working design to reuse, not existing 16-bit stereo support |
| Legacy `agm/buffered-playback-results.md` | Network Web Audio clock and PSRAM lookahead, native 15,360 Hz/8-bit mono | Browser playback precedent at much lower audio load; not the requested format/rate |
| PORT-004 | Audio framing repair, PCM scheduler/network sink design | Current production framing support must not be confused with implemented audio synthesis or stereo playback |

### Revisions inspected

- Extender contract freeze: `4a19d02498048023a76ee8f68b8751bdf2826976`.
- EMOS: `26ba8776bc147e262cd45dc808d5869740b1396e`.
- Extender legacy: `df54cf6a7a23cd40e98076856f68cff0559d1c77`.
- AgonJukebox: `0a09cee58327ecded770d835d3f7c7ac503980de`.
- Local official MOS reference: `8336409351ee5314e02801a7b72a4f1bb5282519` (v3.0.2).
- Local Agon docs: `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.
- Installed P4 serial identity: `rle2-fullscreen-r02-b2026-09-17-08-02-06Z`, ESP-IDF 5.5.5. Retained, not flashed.

Sibling repositories are under the common `Agon/mystuff` workspace. Legacy evidence is read-only; do not import its historical GPIO contracts into current firmware.

## Why the budget is tight

For sequential read and send, sustainable payload rate is `1 / (1/SD_rate + 1/parallel_rate)`, before other work. eZ80 execution cannot simultaneously run its polling SD read and GPIO transmit loop. P4 receive DMA does not change that fact. A second Agon buffer alone therefore does not make those producer stages overlap.

Current MOS storage goes through FatFS to sector reads and polling SPI, directly into the supplied buffer. Do not charge an imaginary full SRAM copy in addition to this. Nor assume interrupt-driven scheduling creates producer throughput. Stock-compatible SD improvements, if attempted, need their own controlled contract and paired tests.

The historical parallel fast loop omitted per-byte helpers and READY checks. Current EMOS performs three indirect operation calls per byte, fault checks, and target control helpers which preserve interrupt state around masked Port D updates. That is a concrete candidate cost to measure, not a proven bottleneck yet. Preserve unrelated pin states, interrupt semantics, bounds and backpressure when optimizing.

At the fastest measured SD rate, serial-stage break-even requires about 1.31 million parallel payload bytes/s. With the old 838.9 KiB/s sender, SD would need about 222,000 bytes/s (217 KiB/s), already above today's results. Production also needs margin for card stalls and video/control work. A 32 kHz/16-bit stereo control case needs 128,000 B/s and has a more plausible budget; it would be a diagnostic step, not fulfilment of the 44.1 kHz target.

## Routing and pin ownership: required integration

The eight-bit bus owns all of eZ80 Port C. UART1 also owns PC0/PC1, and EMOS explicitly rejects entry while UART1 is active. Thus the existing Extender keyboard/control/SD-service path cannot simply run unchanged during a parallel epoch. Mainboard video uses its separate VDP path and should remain in Legacy mode.

AF02 must define an EMOS-owned admission/handover: quiesce UART1, enter a bounded forward epoch, transfer records under READY control, drain/terminate, release pins and restore UART1. Decide how queued keyboard events, stop requests, timeouts, acknowledgement and receiver abort work. Do not assume an inbound UART keyboard interrupt remains available while the pins are repurposed. A finite autonomous benchmark with automatic return is preferable for the first test. Existing Pi reset/recovery remains the escape route.

The Author reports the full harness installed. Source pin mappings and historical design records were inspected, but there was no new pinwalk or electrical qualification this run. Before enabling the parallel peripheral, confirm the current harness against its current contract, especially older record holds and different historical buffer arrangements.

## Buffer location and memory

The useful correction to earlier discussion is **where the lookahead lives**. Jukebox alternates VDP-side sample buffers; it need not hold a whole second in Agon SRAM. The old AGM design uses a 12 MiB P4 PSRAM queue with a roughly four-to-five-second scheduling horizon, not five seconds of media in Agon SRAM.

For the new format, one second of PCM is 176,400 bytes and five seconds is 882,000 bytes. Keep small Agon read/transfer buffers and the long queue on P4. The 16 KiB fixture buffer proves only this fixture's allocation, not production memory headroom. The eventual player link map and P4 heap/queue accounting remain required. Historical EMOS flash-budget figures are not a current build measurement; remeasure before adding a route. Do not consume application SRAM as a hidden firmware extension.

## Network/browser sink feasibility

Raw audio is only **1.4112 Mbit/s** before framing. This is far smaller than the framebuffer traffic that drove the earlier Ethernet experiments; it is plausible for the network, but not measured here with concurrent video. Start with mainboard-only video and no web framebuffer subscription to isolate audio.

Proposed payload for AF02: PCM16 little-endian, interleaved L/R, explicit sample rate, channel count, sequence and sample-frame timestamp; bounded frames and discontinuity reporting. This is a proposal, not a newly assigned wire command. Reuse the PORT-004 sink boundary and existing transport command ownership.

Browser `AudioBuffer` uses planar float32 samples: deinterleave and convert signed PCM16 to `sample/32768`. Schedule against the audio clock, not packet-arrival time; arrange user gesture/context resume for autoplay restrictions. Handle underrun, reconnect, overflow and clock drift explicitly. Reuse the old AGM Web Audio scheduling ideas, while measuring the new format. A ring/AudioWorklet is an option, not an implementation decision established by this study.

Official references consulted September 18:

- [Espressif P4 PARLIO RX](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/peripherals/parlio/parlio_rx.html): hardware RX/DMA facilities and buffer ownership; match actual APIs against installed IDF 5.5.5 rather than copying latest blindly.
- [MDN AudioBuffer](https://developer.mozilla.org/en-US/docs/Web/API/AudioBuffer): planar float32 representation.
- [MDN Web Audio best practices](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices): context/autoplay requirements.
- Local Agon `docs/vdp/Enhanced-Audio-API.md`: existing sampled audio describes eight-bit formats, not a stock 16-bit stereo command. Local `docs/mos/API.md`: synchronous file API semantics.

## Recommended AF02 scope

1. Freeze an EMOS-owned finite parallel benchmark and recovery contract. No new general audio synthesis implementation yet.
2. Verify pins; measure sustained pre-generated SRAM payload through the actual sender and P4 queue, using sequence/full CRC and timings. Include UART handover and record-size sweeps. No network initially.
3. Measure the combined SD/read/send loop on the same article. This is the decisive throughput test; quantify stalls and useful margin.
4. If promising, add P4 buffering and browser PCM output, then listening plus underrun/occupancy evidence. Only then add mainboard video load and AGM encoded-video budgets.
5. If 44.1 kHz fails, identify whether storage or sender changes can recover enough margin before expanding implementation. Record lower sample-rate results separately; do not silently relax the target.

This stops at an actionable feasibility result rather than flashing an incomplete split-route design within the hour.
