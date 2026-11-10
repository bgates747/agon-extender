# NET-008 — Wi-Fi connection and first baud qualification

The real P4/ESP8266/Pi5 route connected and passed a full minute of simultaneous
bidirectional CRC-checked payload exchange at230400baud. The next tested rate,
384000, produced P4 receive FIFO overruns. This qualifies230400 for this exact
appliance, wiring and workload, not an absolute ESP8266 or Agon UART limit.

## Results

Worst outcome first. Nominal baud baseline115200; percentages compare nominal
baud only, not measured payload throughput.

| Baud, bit/s | Change from115200 | Required receive window | Result |
|---:|---:|---|---|
|384000|+233.3%|2s short check|Failed:145 P4 UART FIFO overruns; stop/backoff|
|230400|+100%|2,10,30,60s|All pass, independent CRC/sequence/pattern/byte/frame checks|
|115200|Baseline|2s|Pass; long qualification performed at higher passing rate|

The final230400case produced62s, with actual receive windows62.464517s at P4
and62.131544s at Pi5. P4 sent1378frames/1411072payload bytes, exactly matching
Pi5 reception. Pi5 sent1398frames/1431552payload bytes, exactly matching P4
reception. Both endpoints passed; P4 UART, CRC and framing counters were zero.
The IDF baud-divider report was230423; this is a software report, not a measured
oscilloscope baud calibration. Durations use P4 esp_timer and Pi monotonic time.
No sustained Agon application, C8 UART or optical/display result is implied.

## Connection and correction trace

1. Private runtime Pi5 keyring JOIN succeeds in5.979host seconds with a nonzero
   station IP. Credentials were not placed in firmware, files, arguments or
   captures. Analyzer acquisition remained off for credential setup.
2. Initial appliance fe1299 installed/read back correctly but stack-protection
   halted during public INFO reply formatting, before credential retrieval.
   Corrected source cb6b7305 uses16KiB main stack and static wiped AT reply
   scratch. All controls/identified build pass; corrected application239968B,
   SHA256380b4ea673d5ca2bc80f84f4469c0a10d7384379550a38619c3701cea44a7348,
   build net008-uart2-join-r03-b2026-11-10-17-59-49Z. No product change/promotion.
3. Original short ladder stops at384000 with unresolved immediate cleanup.
   Its failure stays retained. After the original TCP peer/host joined, a separate
   positive384000 AT/status INFO established command-mode reconciliation. A
   deliberate lower-rate host continuation addb2837 then qualifies230400. The
   failed384000 arm was not replayed, and no higher baud was attempted.
4. UART type3 is UART_FIFO_OVF in the pinned IDF. This is an observed receiver
   overrun in the present P4 appliance; no evidence establishes faulty wiring,
   RF corruption or an absolute hardware maximum. CRC success at230400 applies
   to the actual simultaneous workload and the selected no-RTS/CTS wiring.

## Retained state and evidence

Smith subsequently explicitly ended the hold and ordered release to6502.
The owner restored product P4 d9b, independently compared the overwritten
241664-byte prefix, and verified normal boot, services, CLI/read/EXIT plus fresh
mode0/callback0/backend0 and idle resources. Original restoration and fresh-check
workers joined0; actual stopped handback was sent to the sole scheduler for
central release. The corrected diagnostic artifact remains retained, not installed.
During its installation product HTTP/input/SD services were unavailable. Mainboard
VDP dc43, EMOS a25f, startup/listener, partitions/NVS and ESP8266 firmware remain
unchanged. Restoration follows that later explicit human release instruction, not an automatic
cleanup at test end. Central release belongs to the scheduler.
Modem last positive baud230400, Wi-Fi associated, ordinary command cleanup passed;
P4 UART retired. Owned worker groups stopped and both USB ports free.

The mainboard reset holder retained across the first fault was explicitly
released and its group is absent. Its original parent had exited, so no original
holder wait code is inferred; the released-control journal and native absence
are retained separately. Successful and failed main workers have their real
parent-written results, not invented success receipts.

Ignored local evidence under agents/net008/connect-r02 includes build-stack-r03,
join168-r03, torture168-r03 (first rate failure), reconcile384-info,
qualify230400-r04 and final-held-state.json, each with original supervisor
journals. Installation/readback and reset-holder evidence are under
agents/net008/bench-test/physical168-connect-stack-r03 and its first-fault sibling.
The installed-firmware inventory records the actual development image separately
from the retained product rollback. No secret values appear in this report.
