# Standalone reference selection and experiment design

## Executive summary

No directly comparable advertised 512×384 lossless Ethernet60 result was found.
Use the contract's official-example fallback: ESP-IDF HTTP server and Espressif
Arduino Ethernet APIs on the explicitly supported P4 target, with a small
project-authored deterministic producer. This is an isolation fixture, not a
claim to have found faster upstream VDP replacement firmware.

## Candidate dispositions

| Candidate | Existing evidence | Decision |
|---|---|---|
| Espressif simple_video_server | RESEARCH-002: MJPEG HTTP, no delivered-fps benchmark | Reuse supported HTTP chunk transmission pattern; camera dependency absent on bench |
| Espressif esp_lvgl_adapter | RESEARCH-001 C1: LCD ownership and headless dummy draw, no Ethernet benchmark | Retain source research; importing another graphics scheduler would confound first isolation |
| Espressif GMF player | RESEARCH-001 C4: codec/presentation performance, clock/drop semantics | Decode/display throughput not network egress |
| NINA P4 | RESEARCH-001 C3: occasional JPEG snapshots | No continuous exact-pixel benchmark |
| P4 Vectrex | RESEARCH-001 C5: sparse LCD rendering | Different workload, no Ethernet claim and ownership concerns |
| r4d10n esp32p4-uvc-video | https://github.com/r4d10n/esp32p4-uvc-video : P4 OV5647 1080p30 capture, USB MJPEG/H264 and Ethernet RTSP | Requires absent camera, compressed30fps not our60fps exact output |

Espressif-first search was followed by P4 Ethernet60fps/streaming searches.
LCD60fps results and secondhand claims were not accepted as network evidence.
Existing pinned C1–C5 source records remain authoritative; no upstream code
from independent projects is incorporated. SDK examples are local pinned package
sources, hashed in SOURCES.json; public URLs:
- https://github.com/espressif/arduino-esp32/tree/3.3.11/libraries/Ethernet/examples/ETH_LAN8720
- https://github.com/espressif/esp-idf/tree/v5.5.5/examples/protocols/http_server/simple
The HTTP example is public domain/CC0. Runtime libraries retain upstream licences.

## Selected fixture (agent-selected under the frozen fallback)

HTTP GET /run?mode=render|send|combined&fps=30|60&frames=600
starts a bounded run; /status reports completed metrics. The HTTP request
remains open for binary frames then a final metrics record. A separate
control HTTP server remains available during transmission. No VDP/FabGL,
Agon UART, keyboard, reset, SD service or web client implementation is linked.

Each512×384 byte frame is deterministically generated from x,y and logical
frameID using 6-bit colours, with moving filled rectangles. Every frame changes.
Render-only produces/discards frames; send-only reads precomputed phase frames;
combined renders into three preallocated PSRAM slots. Free/ready queues transfer
exclusive ownership; the sender returns each slot only after send completes.
No per-row graphics lock or shared mutable framebuffer. This changes ownership
and workload deliberately; it is not an apples-to-apples VDP speedup percentage.

Producer core0 priority5; HTTP sender core1 priority5. At deadlines with no
free buffer producer records a drop, never overwrites a leased slot. Producer
render time and intervals recorded in preallocated arrays, no live logging.
Sender wall times and unique received frames reported separately. Header has
frameID, payload length and producer completion timestamp. Host compares full
payload against independent reference, recording its own validation cost.
Send-only64 phase frames are pregenerated before timing; this explicitly has
different memory footprint/cache behaviour from combined and is a transport
control, not a render result.

Use existing board/SDK safe360MHz and200MHz PSRAM configuration. Only IP101
Ethernet pins31/52/51 and fixed EMAC signals are initialized, matching the
existing installed service. No camera/LCD pin defaults copied. Preserve existing
bootloader/partition/NVS; flash application only at verified existing offset.
Reject unexpected baseline or partition bytes before write, independently verify
candidate bytes. No speculative pin assignments.

Initial600 logical frames (10s at60,20s at30), discard first60 from interval
statistics, two repeats per condition. Whole-run rate includes stalls and drops.
Any corruption/reset stops escalation. Durable host evidence follows each run.
This first-pass fixture can establish concurrent raw output capacity without
VDP; it cannot establish browser presentation, sustained game performance or
prove any particular VDP lock defect. No compression in this pass.
