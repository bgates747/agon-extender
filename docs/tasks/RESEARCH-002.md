# RESEARCH-002 — Espressif P4 board network-video throughput claims

## Executive summary

Espressif publishes a 10/100 Mbit/s Ethernet interface for the original
ESP32-P4-Function-EV-Board and a maximum P4 hardware H.264 encoding capability
of 1080p at 30 fps. These describe different stages. The official browser
server example streams compressed JPEG over HTTP; its reviewed documentation
does not provide a measured sustained Ethernet payload bitrate or delivered
frame-rate benchmark.

Our 512×384×60 target at one byte per pixel requires 94.37184 Mbit/s before
protocol overhead. Compression explains how higher-resolution camera video
can fit that link. It does not explain our graphics degradation at 23.817
Mbit/s in the [P01g ladder](QUAL-003/debrief/P01g/RESULTS.md). That observation
does not yet isolate scheduling, memory traffic or networking overhead.

Research complete; awaiting Author review. No firmware change or additional
experiment is authorized by this record.

## Retrospective authorization and scope

On 2026-09-16 the Author requested reading the board documentation for
advertised network throughput while serving frames. The research and chat
report preceded this task. The Author then requested this durable task record.
This is retrospective, **not a claim that a contract was frozen beforehand**.

1. [x] Identify the original board and its advertised Ethernet capability.
2. [x] Distinguish encoding/camera specifications from network delivery figures.
3. [x] Compare the claims with our payload requirement and existing ladder.
4. [x] Record sources, limitations and review boundary.

Documentation only: no builds, flashing, bench access, new measurements or
Golem work. This supplements RESEARCH-001 without repeating its five candidate
reviews or starting the frozen P01h compression experiment.

## Findings and official sources

Consulted 2026-09-16. Latest URLs are mutable; this review records published
claims, not a pinned implementation qualification.

| Subject | Published capability | Measurement limit | Source |
|---|---|---|---|
| Original Function EV board, guide v1.5.2 | 10/100 Mbit/s adaptive Ethernet | Physical link rate, not application goodput | [Board guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32p4/esp32-p4-function-ev-board/user_guide.html) |
| P4 hardware H.264 encoder | Maximum 1920×1080 at 30 fps | Encoding capability; not guaranteed browser delivery under simultaneous rendering load | [Espressif announcement](https://www.espressif.com/en/node/7617) |
| esp_video v1.2.0 simple_video_server | MJPEG over HTTP; Ethernet supported | Compressed frames; no measured sustained Ethernet bitrate/delivered-fps benchmark found in reviewed documentation | [Versioned example](https://components.espressif.com/components/espressif/esp_video/versions/1.2.0/examples/simple_video_server?language=en) |
| Same example's camera configuration | JPEG 640×480 at 25 fps example setting | Camera configuration, not measured browser delivery | Same versioned example |

The board guide distinguishes the newer P4X/chip revision v3.x. Do not silently
substitute its performance for the original P4. Board revision v1.5.2 is not
the chip revision. No board purchase or equivalence is established here.

The missing network benchmark is a bounded search finding, not proof that
Espressif has never published one elsewhere. Capture-only, codec-only, local
LCD and iperf figures cannot individually demonstrate concurrent graphics
rendering and frame delivery.

## Comparison with retained evidence

| Quantity | Value | Interpretation |
|---|---:|---|
| Our raw-pixel target | 512×384×60×8 = 94.37184 Mbit/s | Pixel payload only, before WebSocket/TCP/IP/Ethernet overhead |
| Board Ethernet maximum | 100 Mbit/s | Line rate, not achievable payload promise |
| P01g failed 96 KiB rung payload | 23.817 Mbit/s | Existing measurement; all 2,023 received messages validated |
| Same rung native completions | 35.981/s | Diagnostic timing from failed terminal query 15 run |
| Same rung native interval p95 | 55.710 ms | Failed-run timing, not qualified performance |

P01g stopped at the correctness gate; larger/repeated/browser rungs were not
run. Therefore 23.817 Mbit/s is neither maximum network capacity nor a proven
repeatable failure threshold. Its known-pattern sender plus independently
requested full compositions differs from compressed camera streaming. P01g
remains authoritative for exact artifacts, controls and timing scopes.

## Implication and review boundary

A useful further source comparison would trace how Espressif's capture
producer hands completed buffers to the encoder and network sender: buffer
lifetime, queue depth, blocking and scheduling. Our implementation already
separates transmission from the native graphics lock through completed-frame
leases; recommending that separation alone is not a new fix.

This is a proposed follow-up, not an automatically started task. Review against
existing research and P01g before expanding scope. P01h AGM/SRLE2 remains
separately frozen and unstarted. Nothing here establishes a reason to abandon
the raw-pixel target or adopt a lossy codec.
