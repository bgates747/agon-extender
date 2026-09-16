# Search ledger

Accessed 2026-09-16 UTC (local evening September15). Research only; no new bench measurements.
Initial broad discovery: P4 Ethernet slow latency; P4 PSRAM/cache dual-core performance; P4 Arduino WebSocket throughput.
Then P4-specific searches below, widening to common IDF/Arduino mechanisms after no exact causal match.
Search results were leads; substantive conclusions use primary documentation, source, upstream issues or original project reports.

1. `site:github.com/espressif/esp-idf "esp32p4" "performance" "cache"`
2. `site:github.com/espressif/esp-idf "ESP32-P4" "Ethernet" "slow"`
3. `site:github.com/espressif/esp-idf "ESP32-P4" "latency"`
4. `site:github.com/espressif/arduino-esp32 "P4" "stutter"`
5. `ESP32-P4 Ethernet graphics LVGL freezes slow memory contention`
6. `ESP32-P4 errata cache synchronization performance dual core`
7. `site:github.com/espressif/esp-idf "P4" "memcpy" "slow"`
8. `site:github.com/espressif/arduino-esp32 "P4" "Ethernet" performance`
9. `site:github.com/espressif/esp-idf "httpd_ws_send_frame_async" slow`
10. `site:github.com/espressif/esp-idf websocket Nagle delayed ack TCP_NODELAY`
11. `site:github.com/espressif/esp-idf "esp32p4" "starvation"`
12. `site:github.com/espressif/esp-idf "esp32p4" "cache" "performance" issue`
13. `site:github.com/espressif/esp-idf "ESP32-P4" "spinlock"`
14. `site:github.com/espressif/esp-idf "P4" "Ethernet" "throughput"`
15. `site:github.com/espressif/arduino-esp32 "performance" "3.3.11"`
16. `site:docs.espressif.com esp32p4 performance cache misses task priorities`
17. `site:github.com/espressif/esp-idf "esp32p4" "pin" "FPU"`
18. `site:github.com/espressif/esp-idf "ESP32-P4" "PSRAM" "contention"`
19. `site:github.com/espressif/esp-idf "websocket" "throughput"`
20. `site:github.com/espressif/arduino-esp32 "Ethernet" "TCP_NODELAY"`
21. `site:documentation.espressif.com/esp-chip-errata esp32p4 "MSPI-750" "v1.3"`
22. `site:documentation.espressif.com/esp-chip-errata esp32p4 "APM-560"`
23. `site:github.com/espressif/esp-idf "coprocessor" "pinned" "riscv"`
24. `site:github.com/espressif/esp-idf "ESP32-P4" "timer" performance jitter`
25. `site:github.com/espressif/esp-idf ethernet websocket throughput latency slow send 40 ms`
26. `site:github.com/espressif/esp-idf ESP32 P4 PSRAM cache random performance boot`
27. `site:github.com/espressif/arduino-esp32 P4 USB serial performance blocking`
28. `site:freertos.org priority inheritance mutex release reacquire starvation`
29. `site:github.com/espressif/esp-idf "mutex" "priority inheritance" performance`
30. `site:github.com/espressif/esp-idf "ESP32-P4" "L2" "slow"`

Direct reads also covered versioned IDF5.5.5 external RAM/lwIP docs, P4 errata,
IDF/Arduino releases, FreeRTOS SMP, HTTP server send semantics, Ethernet iperf
configuration and local selected-build sources. Several versioned Espressif
pages failed to open through the web tool; successful latest/stable pages were
labelled as such and checked against local5.5.5 source where material.
One guessed deep erratum URL did not resolve and is not evidence; use the
official errata index instead. No exact matching issue was established; this
is a bounded search result, not proof that no upstream defect exists.

## Implementation scouting extension

Accessed 2026-09-16 UTC. Author-approved source review beyond HTTP; no samples
built, flashed, executed or benchmarked. Search snippets discovered candidates;
claims were checked against pinned source, README/test records and original
issue reports. Full provenance: CANDIDATE-SOURCES.json.

31. `ESP32 P4 audio graphics multicore PSRAM performance github`
32. `ESP32 P4 emulator optimization task buffer contention github`
33. `site:github.com/espressif esp32p4 pipeline video audio performance buffer`
34. `site:github.com ESP32 P4 PSRAM benchmark concurrent cores`
35. `ESP32 P4 tgx multithreaded renderer github`
36. `ESP32 P4 dual core audio benchmark micro-mp3`
37. `ESP32 P4 esp_lvgl_adapter throughput buffers render benchmark`
38. `ESP32 P4 NINA display PSRAM contention github`
39. `ESP32 P4 micro-mp3 concurrent benchmark PSRAM github`
40. `ESP32 P4 Vectrex malbanGit PSRAM core rendering`
41. `ESP32 P4 esp_lvgl_adapter buffers performance PPA`
42. `site:github.com "ESP32_P4_Vectrex" renderer_task`
43. `site:github.com "ESP32-P4-NINA-Display" PPA`
44. `site:github.com "esp32p4_fpu_benchmark" cache benchmark`

Read-only API retrieval pinned seven repositories, their trees and five-commit
history samples. Selected source/test/configuration files retained locally in
ignored research storage; no media/ROM download or execution. Five shortlisted
implementations, two demoted architectural/benchmark references, wider leads
recorded in CANDIDATES.md. The guessed adapter benchmark README returned404;
benchmark-tree presence is not a claim that that README or test results exist.
No independently replicated benchmark matching our workload was established.
