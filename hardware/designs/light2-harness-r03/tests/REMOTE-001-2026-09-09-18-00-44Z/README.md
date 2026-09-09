# Browser typing latency and connection-loss observation

Operator session under browser-keyboard-probe-r04, starting at
2026-09-09T18:00:44.704Z according to the browser export. The Author typed
several lines at separated and normal cadence (approximately 20–30 wpm),
recaptured after keyboard failures, and reported video disconnection while
Agon remained within the sample's five-minute session. This is informative
failure evidence and a measurement result, not hardware qualification.

## Evidence

1. `timing.json` is the unmodified operator download: 2896 browser and 7541
   P4 records, zero overwrites, no export error. The agent retrieved/froze P4
   records after the reported failure and before the operator's download;
   the two P4 exports match exactly. Functional traffic continues after
   recording freezes; later events are not measured.
2. Installed identities and previously verified hashes are in `run.yaml`.
   P4's clean source is 1ce96dc97177c9818fe9254ad5a5500ffd6142c9; its prior
   deployment run is REMOTE-001-2026-09-09-17-58-10Z. EMOS and SD are unchanged.
3. `analysis.json` is produced by running the unchanged
   `scripts/analyze_browser_timing.py timing.json` with project Python.
   Analyzer source at evidence review is commit 9497042. No duration calculation
   subtracts a browser timestamp from a P4 timestamp.
4. `stale-clock-reproducer.cpp` includes the maintained keyboard class.
   Compile from the repository root with C++17 and `-I vdp/video` into an
   ignored temporary location. Its saved output intentionally demonstrates
   current defective behavior; it is not an acceptance test for a future fix.

## Intervals

| Interval | Samples | Median (ms) | Maximum (ms) |
|---|---:|---:|---:|
| Browser key event → admission acknowledgement received | 264 | 49.000 | 343.000 |
| Browser message send → acknowledgement, including heartbeat/control | 383 | 42.000 | 137.000 |
| P4 key-message receipt → UART submission | 109 | 59.086 | 112.390 |
| P4 UART submission → matching EMOS/sample text received | 109 | 1.114 | 2.865 |
| P4 echoed text receipt → drawing flush complete | 102 | 1.222 | 96.085 |
| P4 snapshot composition interval | 1232 | 116.376 | 121.827 |
| P4 complete successful video send | 916 | 89.726 | 978.315 |
| Browser frame receive → WebGL submission | 916 | 5.000 | 19.000 |
| Browser key event → first guaranteed-containing submitted frame | 90 | 422.000 | 743.000 |

The last row is a conservative visibility bound: an earlier frame may already
contain the character. It does not measure physical monitor scanout. The
analyzer excludes 23 unpaired/nonprintable key-down transmissions; other echo
matches may lack an unambiguous flush/frame association. Counts differ, so
medians must not be added as one serial budget. The analyzer's combined
video-send summary includes two failures (918 total, median 89.728 ms,
maximum 1662.395 ms); this table separates successful sends.

The large measured intervals are in P4 queue servicing and the browser video
path; UART/EMOS/sample echo is small. This does not establish stock-performance
equivalence or one-way Ethernet delay. Snapshot timing measures its work
interval, not separate CPU utilization. The configured snapshot minimum uses
logical boundary time and does not guarantee wall-clock five-fps delivery.

## Keyboard revocation

Five owner revocations report reason 3 (two-second lease expiry) despite
successful recent heartbeats/keys. Indices refer to P4 CSV records in the JSON.

| Revocation index | P4 timestamp (us) | Last accepted message age (ms) | Queued events discarded |
|---|---:|---:|---:|
| 501 | 163761487 | 10.447 | 0 |
| 815 | 173761135 | 7.720 | 0 |
| 1861 | 203278897 | 6.493 | 1 |
| 4211 | 237112555 | 19.362 | 1 |
| 5652 | 256629544 | 84.210 | 2 |

Each follows snapshot completion by about 0.3 ms. P4 subsequently rejects a
message from that owner and closes its keyboard socket. The browser records
the corresponding abnormal close. No browser acknowledgement timeout occurs.
Missed heartbeats during HTTP stalls do not explain these five revocations.

The P4 loop in `vdp/video/extender/diagnostic/browser_typing_hardware.inc`
caches `now=millis()`, executes retained VDU processing (including potentially
blocking drawing flush), then calls `browser.pop(key,now)` with that old time.
Meanwhile the HTTP task can record a newer heartbeat in `BrowserKeyboard::seen_`.
The class's `uint32_t(now-seen_) >= 2000` then wraps and falsely expires the
owner. The mutex protects state, but cannot refresh an old caller timestamp.
Both callers derive milliseconds from `esp_timer_get_time()/1000`; differing
clock origins do not explain it. The deterministic reproducer confirms:

```text
take(100)=1; heartbeat(150)=1; pop(100); heartbeat(151)=0
take(100)=1; heartbeat(150)=1; pop(150); heartbeat(151)=1
```

The same cached-time loop and unsigned lease calculation exist in original
r01 at 5e8ebf5, before instrumentation. Physical records do not expose the
cached argument itself, so attributing every occurrence to that interleaving
is a source-supported inference; the defect itself is directly reproduced.

## Video closure

P4 fails two incomplete 921600-byte video payload sends:

| Snapshot token | Bytes sent | Send-loop budget observation (ms) | Browser close time since page start (ms) |
|---|---:|---:|---:|
| 725 | 856758 | 1661.464 | 10407 |
| 1691 | 809238 | 1633.982 | 203685 |

Each produces `send_budget`, failed `video_send_end`, then P4 `socket_close`;
matching browser video sessions close with code 1006. P4 initiates closure.
`completeSend` in `vdp/video/extender/network/wired_network_service.cpp`
checks its one-second budget only between blocking `send()` calls, explaining
why observed failure can exceed one second. No P4 UART failure is recorded.

The underlying stall remains unresolved: records cannot distinguish network
delivery/backpressure, browser consumption, or lower-level scheduling.
Increasing a deadline would not explain that cause. Video and keyboard share
the HTTP task, but these two stalls do not account for the five false lease
expirations above.

## Review recommendation and remaining limits

First correct keyboard lease timing across task interleaving while preserving
true two-second expiry, clock-wrap behavior and held-key cleanup, then repeat
paired typing. No EMOS or SD sample change is indicated. Keep video scheduling,
send stalls and snapshot cost under I001/I002 for the next bounded investigation.
No firmware repair or timing-policy change accompanies these records.

P4 hook cost totals 87087 us, maximum 221 us; this excludes some instrumentation
effects. No recording-off physical comparison was performed, so that part of
I001-M4 remains open. Escape/MOS return and full qualification remain unclaimed.
Stop for Author review before implementing the original-behavior repair.
