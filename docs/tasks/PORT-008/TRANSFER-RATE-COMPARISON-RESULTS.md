# Forward UART / parallel transfer-rate results

The optimized EMOS byte loop raises the 8192-byte parallel command-stream rate from 220.8 to 340.3 kB/s (+54.1%). That is 3.38 times the matched UART rate. UART remains faster at 256 bytes. All 96 selected samples have complete 8192-byte receiver-buffer proof. The required no-dump controls pass, and the exact incoming firmware pair is restored.

## Findings and scope

1. Larger transfers benefit: parallel rate improves 44.5–58.7% at 4096/4097/8192 bytes. At 256 bytes the improvement is 28.8%, but fixed costs leave UART about 5% faster in sender drain. These are whole command-stream rates, including existing handovers, not isolated electrical-bus bandwidth.
2. The block boundary remains visible: optimized drain rises from 11.361 ms at 4096 bytes to 15.056 ms at 4097 bytes. This benchmark preserves the existing 4096-byte internal admission units; it does not implement one admission for an arbitrarily larger application request.
3. Ordered processing/reply at 8192 bytes falls from 133.333 to 117.181 ms (12.1% less time). This scope includes synchronous buffer processing and the existing small query/reverse reply; it is distinct from sender drain and says nothing about renderer or HDMI completion.
4. UART controls agree closely across the two EMOS images: median drain is identical at the three smaller lengths and differs by +0.69% at 8192 bytes. The P4 application, endpoint configuration, fixture source and measured workload remain fixed. Passive Pi collection changed as recorded below.
5. EMOS still supplies the parallel byte clocks. No public async API, autonomous transfer, useful CPU-headroom result, reverse bulk-rate result or production promotion follows from this forward comparison.

## Measured tables

U0/P0 use baseline EMOS; U1/P1 use optimized EMOS. U means UART1 ExCom, P means Port C parallel ExExt, both between the same eZ80 and P4. Lengths rank by largest baseline parallel drain time first. Five measured samples per cell; original-index warm-ups are retained and excluded only from statistics. kB means 1000 bytes; the tables below use explicit bytes/s.

Every cell is median [minimum, maximum]. Command-stream rates count all N bytes,
including the eleven-byte buffer-SET header; useful upload rates count N − 11.
Percentage changes are `100 × (candidate / baseline − 1)` for the named metric.

## Command-stream bytes/s

| Stream bytes | U0 | P0 | U1 | P1 |
|---:|---:|---:|---:|---:|
| 8192 | 101292 [98881, 101484] | 220825 [219674, 221239] | 100601 [99314, 102010] | 340349 [332483, 344322] |
| 4097 | 110896 [110855, 110938] | 188368 [187768, 191052] | 110896 [110896, 111063] | 272125 [268167, 287789] |
| 4096 | 110953 [110911, 110953] | 227205 [222240, 227380] | 110953 [110828, 110994] | 360528 [357903, 360528] |
| 256 | 109714 [109065, 109714] | 80842 [79107, 89912] | 109714 [109065, 109714] | 104136 [89912, 110371] |

## Useful upload bytes/s

| Stream bytes | U0 | P0 | U1 | P1 |
|---:|---:|---:|---:|---:|
| 8192 | 101156 [98748, 101348] | 220529 [219379, 220942] | 100466 [99180, 101873] | 339892 [332036, 343860] |
| 4097 | 110598 [110557, 110640] | 187862 [187264, 190539] | 110598 [110598, 110765] | 271395 [267447, 287017] |
| 4096 | 110655 [110613, 110655] | 226595 [221643, 226769] | 110655 [110530, 110696] | 359560 [356942, 359560] |
| 256 | 105000 [104379, 105000] | 77368 [75708, 86049] | 105000 [104379, 105000] | 99661 [86049, 105629] |

## Rate and elapsed-time differences

| Stream bytes | P1/P0 drain time change | P1/P0 stream rate change | P1/U1 stream rate | U1/U0 drain time change |
|---:|---:|---:|---:|---:|
| 8192 | -35.12% | +54.13% | 3.383× | +0.69% |
| 4097 | -30.78% | +44.46% | 2.454× | +0.00% |
| 4096 | -36.98% | +58.68% | 3.249× | +0.00% |
| 256 | -22.37% | +28.81% | 0.949× | +0.00% |

## Application submission, ms

| Stream bytes | U0 | P0 | U1 | P1 |
|---:|---:|---:|---:|---:|
| 8192 | 80.861 [80.708, 82.833] | 37.889 [37.806, 37.972] | 81.403 [80.292, 82.458] | 24.750 [24.611, 25.389] |
| 4097 | 36.931 [36.917, 36.944] | 18.917 [18.806, 19.028] | 36.931 [36.875, 36.931] | 12.111 [11.986, 12.333] |
| 4096 | 36.903 [36.903, 36.917] | 18.764 [18.694, 19.083] | 36.903 [36.875, 36.944] | 12.069 [11.986, 12.181] |
| 256 | 2.319 [2.319, 2.319] | 0.083 [0.083, 0.083] | 2.319 [2.319, 2.319] | 0.083 [0.083, 0.083] |

## Sender drain, ms

| Stream bytes | U0 | P0 | U1 | P1 |
|---:|---:|---:|---:|---:|
| 8192 | 80.875 [80.722, 82.847] | 37.097 [37.028, 37.292] | 81.431 [80.306, 82.486] | 24.069 [23.792, 24.639] |
| 4097 | 36.944 [36.931, 36.958] | 21.750 [21.444, 21.819] | 36.944 [36.889, 36.944] | 15.056 [14.236, 15.278] |
| 4096 | 36.917 [36.917, 36.931] | 18.028 [18.014, 18.431] | 36.917 [36.903, 36.958] | 11.361 [11.361, 11.444] |
| 256 | 2.333 [2.333, 2.347] | 3.167 [2.847, 3.236] | 2.333 [2.333, 2.347] | 2.458 [2.319, 2.847] |

## Local parallel completion, ms

| Stream bytes | U0 | P0 | U1 | P1 |
|---:|---:|---:|---:|---:|
| 8192 | — | 37.917 [37.833, 38.000] | — | 24.778 [24.625, 25.403] |
| 4097 | — | 22.264 [22.069, 22.361] | — | 15.597 [14.819, 15.792] |
| 4096 | — | 18.792 [18.708, 19.111] | — | 12.097 [12.000, 12.194] |
| 256 | — | 3.778 [3.542, 3.819] | — | 2.972 [2.778, 3.361] |

## Ordered processing and reply, ms

| Stream bytes | U0 | P0 | U1 | P1 |
|---:|---:|---:|---:|---:|
| 8192 | 163.153 [162.486, 164.611] | 133.333 [133.222, 133.431] | 162.681 [161.917, 163.958] | 117.181 [116.750, 134.111] |
| 4097 | 81.194 [80.569, 82.069] | 83.458 [82.972, 83.778] | 81.708 [80.903, 83.097] | 66.764 [66.319, 67.111] |
| 4096 | 81.681 [81.514, 82.569] | 83.750 [82.972, 83.778] | 82.111 [80.958, 82.917] | 66.667 [66.389, 66.750] |
| 256 | 6.431 [6.417, 6.625] | 16.694 [16.528, 16.972] | 6.708 [6.528, 6.806] | 16.792 [16.486, 17.542] |

PRT1 is nominally 72,000 counts/s (13.8889 µs/count), without independent oscillator calibration. Drain is observed in software; interrupts and observation delay remain included. Parallel local completion is physical cleanup/UART return, with no software receipt. The ordered fence adds a seven-byte query and six-byte reverse reply; it does not prove rendering or HDMI presentation. These uploads do not measure reverse bulk rate, autonomous transmission or useful CPU headroom.

The final-edge observation path also changes with the optimized loop. Counting
executed instructions after that edge through the first timer `IN0`, the
uninterrupted enabled path changes from 10 instructions to 7; the masked path
changes from 9 to 5. These are instruction counts, not calibrated cycles.
Both measured arms include their own exit bookkeeping and any interrupts;
no assumed fixed offset is subtracted. Exact linked disassembly is retained.

## Exact controlled inputs

| Component | Baseline | Optimized |
|---|---|---|
| EMOS source | `2fc7b269d57f95ead9ba3a6748852cb84e311186` | `08301e6d28f5cdd6a8bb01aa6806b6d4ddaf816c` |
| EMOS build | `agon-emos-v0.1.27-b2026-11-02-16-20-40Z` | `agon-emos-v0.1.27-b2026-11-02-16-22-52Z` |
| Raw ROM bytes / free bytes | 128,871 / 2,201 | 128,999 / 2,073 |
| Data + BSS | 8,589 bytes | 8,589 bytes |
| Fixture build | `port-008-stream-timing-r01-b2026-11-02-16-23-56Z` | `port-008-stream-timing-r01-b2026-11-02-16-32-30Z` |

Both owner builds use the same timing/controller profile and builder. Firmware source inputs differ only in `src/emos_parallel_native_body.inc`; ROM grows 128 bytes with unchanged RAM. Existing full build/link guards and exact-ELF fixture ABI/native checks pass. Fifteen host tests cover the four-arm analyzer and existing contracts. The actual bench data then passes that analyzer unchanged.

The fixed P4 source is `dddc10a2a31d993af577be436b5d14f6aee9de15`, build `port-008-stream-r19-b2026-11-02-13-28-51Z`, app SHA256 `102014003d771e1c917782e281bdde607da4632d7b255e0c2ba8285bd8c0fd45`. Its independent full-chip readback proves application bytes and unchanged outside sectors. Both displays remain mode 0/single-buffered. Mainboard VDP retains F060 provenance and is never flashed; no fresh full VDP readback is claimed.

Complete EMOS/fixture hashes, ROM readbacks, all 96 selected rows, every acquisition row, capture hashes, selection provenance and restoration proof are retained in [portable evidence](TRANSFER-RATE-EVIDENCE.json). The [comparison task](TRANSFER-RATE-COMPARISON.md) records setup, owner research and remaining reverse coverage. The [raw archive record](TRANSFER-RATE-ARCHIVE.json) identifies the verified generated local archive containing original captures, CSVs, build artifacts, source recipes and installation/restoration journals.

## Acquisition failures and matched controls

There were 22 six-sample acquisitions (132 timing rows), including 7 short USB acquisitions. Every application completed, returned to an observed CLI and reported six zero-flag rows. No complete wrong-byte buffer was found. Each failed acquisition remains failed; its original bytes and timing rows are retained.

Selection takes the first complete correct buffer for each original arm/length/repeat index and keeps that same invocation’s timing row. It never selects by elapsed time. 6 rows use labelled acquisitions; the others come from the original matrix. A valid sample from a short acquisition does not turn the whole acquisition into a pass.

| Arm / stream bytes | Short acquisitions | No-dump P4 control | Limit |
|---|---:|---|---|
| P0 / 4096 | 1 | Six zero-flag rows, actual CLI, no panic | 60 seconds; no byte proof |
| P0 / 8192 | 1 | Six zero-flag rows, actual CLI, no panic | 60 seconds; no byte proof |
| P1 / 256 | 2 | Six zero-flag rows, actual CLI, no panic | 60 seconds; no byte proof |
| P1 / 4096 | 1 | Six zero-flag rows, actual CLI, no panic | 60 seconds; no byte proof |
| U1 / 4096 | 1 | Six zero-flag rows, actual CLI, no panic | 60 seconds; no byte proof |
| U1 / 8192 | 1 | Six zero-flag rows, actual CLI, no panic | 60 seconds; no byte proof |

Every marked case uses its exact EMOS/fixture with the matching P4 implementation whose buffer-dump body is absent. The control P4 source is `d74185caa47107b52bb2633eb9d27291f5f98c1e`, app SHA256 `d49d88e54879372db4e1f61252b83f67daf8be5d984f89b0284b285033e29927`. It differs from the fixed measurement partner only by that removed capture body and necessary build identity/layout. These controls did not reproduce a functional fault within their bounded intervals; they neither establish why USB lines were lost nor replace missing byte proof. Installing the no-dump P4 required a fresh P4/Agon boot; grouped controls do not recreate the earlier long-session uptime or intervening reset history, so history-dependent effects remain outside that negative result.

Each short acquisition was followed by one Agon reset and two successful listener/read/EXIT exchanges before independent work continued. No uncertain command was replayed. Pi collection initially parsed byte lines during USB receipt; later it scanned only completion/panic markers and deferred interpretation. Thirty-two retained-log chunking checks and every marker split pass. Short acquisition persisted after that change, so host parsing is not established as the cause. All source revisions and per-case journals are retained.

## Duration and restoration

| Observed host scope | Median seconds | Min–max seconds |
|---|---:|---:|
| One six-sample invocation, including setup/retrieval | 67.03 | 65.64–73.20 |
| Route command issue to RUN issue | 38.32 | 37.60–44.59 |
| RUN issue to Legacy return issue, including dumps/clean wait | 22.86 | 21.91–23.82 |
| Listener start to final cursor command | 2.28 | 2.14–2.32 |
| Fixture setup/measurements/dumps before CSV save, nominal MOS clock | 11.32 | 10.53–12.43 |

Each invocation records UTC start/end and host monotonic duration. The host scopes above come from issued-command journals; they exclude or include command injection as their labels state and do not sum to the whole without gaps. Fixture duration uses retained MOS ticks at nominal 120 counts/s, without independent oscillator calibration. The six timed transfers themselves are much shorter than setup, byte-dump acquisition and result retrieval. Control intervals and firmware installation/full-readback time are additional. No estimate authorized a reset deadline.

After controls, the complete incoming 16 MiB P4 flash and 131072-byte EMOS ROM match the incoming bytes exactly. Startup remains the original 108 bytes; the listener is unchanged. Final actual CLI/listener/read/EXIT checks pass, ordinary routing is Legacy, both displays retain mode 0, and text/visible/flashing cursor controls are sent to both displays. Input is admitted/neutral, the USB controller is valid, the foreground listener is offline and all owned serial readers/reset holders are closed. SD remains in Agon. Optical validation is not claimed.

The original installation’s known wide-mode limitations remain. Reverse bulk needs a separate matched producer/receiver fixture; generalized async admission and whole-request burst capacity remain in the parent task.
