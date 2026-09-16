# RESEARCH-003 — Standalone P4 reference experiment results

## Executive summary

**Without VDP, this P4 renders the test workload at60fps and delivers complete,
exact raw frames at47.02–47.29fps while rendering, about74Mbit/s.** Transmission
alone delivers49.59–49.60fps, about78Mbit/s. Every30fps case meets its target
without drops. Twelve bounded hardware runs completed, with4,342 transmitted
frames checked byte-for-byte and no payload mismatches or reported send errors.
**The60fps delivered-output target is not met.**

This is a project-authored diagnostic fixture using Espressif's P4 Ethernet and
HTTP APIs, not a discovered upstream firmware with a matching advertised
performance guarantee. Espressif-first discovery and reused candidate research
found no such guarantee; the frozen contract's documented fallback was used.
No camera, LCD, VDP/FabGL, Agon command source or production Extender services
are involved.

The result establishes that the same physical P4/Ethernet path can sustain far
more than the23.817Mbit/s observed in the failed VDP ladder. It does **not**
prove that VDP locks alone caused that failure: graphics workload, ownership,
output protocol and scheduling all differ. One combined run also had a19.103ms
render outlier, so this fixture is not free of scheduling/memory tails.

**Recommended next investigation, not started:** establish the remaining raw
transport limit with this isolated fixture (TCP window/buffering and send cost),
then use a matched workload/ownership comparison to isolate VDP-specific cost.
Alternatively apply the separately frozen lossless compression experiment to
reduce payload demand. No new optimization or production change is implied.

## Main comparison

Values span two repeats,600 logical slots each. Worst delivered performance at
60Hz first. Rates use the device window including pending-output drain; the
receiver independently checks all sent frames and its own intervals. These
are not browser display rates.

| Workload | Target fps | Produced frames/s | Received frames/s | Pixel payload Mbit/s | Render mean ms | Dropped slots per600 |
|---|---:|---:|---:|---:|---:|---:|
| Render + send |60|47.019–47.285|47.019–47.285|73.955–74.373|6.184–6.214|126–128|
| Precomputed send only |60|49.589–49.598|49.589–49.598|77.996–78.012|Not rendered|102|
| Render only |60|59.996–59.999|Not sent|0|5.711–5.712|0|
| Render + send |30|29.999–30.000|29.999–30.000|47.184–47.186|5.716–5.719|0|
| Precomputed send only |30|29.999|29.999|47.184–47.185|Not rendered|0|
| Render only |30|29.999–30.000|Not sent|0|5.710|0|

At60Hz, concurrent drawing reduces delivered rate by approximately4.7–5.2%
relative to the corresponding send-only repeat. Render mean wall time rises
approximately8.3–8.8% relative to the corresponding render-only repeat.
Those comparisons use this fixture's own controls, not mainboard VDP as a
baseline. No legitimate mainboard percentage comparison exists for this new
workload.

[All cases](TABLES.md), [machine-readable summary](SUMMARY.json), and
[raw received-frame records](evidence/) preserve detailed statistics. Render
p95 is5.754–5.756ms without sends and7.445–7.653ms with sends at60Hz. Combined
send mean is21.098–21.216ms; send-only is20.136–20.142ms. These overlapping wall
times include waiting/preemption and cannot be added as CPU costs.

## What happened under overload

The producer follows logical30/60Hz deadlines and has three exclusively owned
output buffers. When all buffers are retained by the sender, or a logical
slot is overdue by a whole period, the producer records a dropped slot rather
than overwriting live data. At60Hz, combined completed-frame intervals have
p95 near34ms. Thus47fps average is **not** a promise of uniformly paced47fps.
The buffers bound queue depth; they do not manufacture missing bandwidth.

Every send/combined payload matched an independently computed reference,
including moving rectangle overdraw. Frame sequence gaps correspond to the
reported dropped slots. No frame was partially accepted or counted twice.
Send-only near-zero render time is descriptor bookkeeping, not miraculous
rendering. Render-only emits no pixels: its collector's generic
`pixel_validation=pass` is a no-error status, not a hardware pixel readback.
The host kernel comparison and transmitted combined controls supply the
separate pixel evidence.

## Relationship to earlier evidence

| Observation | Scope | Legitimate conclusion |
|---|---|---|
| P01g96KiB:23.817Mbit/s,35.981native completions/s, failed query15 | VDP workload plus snapshot composition and WebSocket known payload | Diagnostic failure below Ethernet line-rate saturation |
| Standalone196608-byte frames:73.955–74.373Mbit/s,47.019–47.285received/s | Deterministic software fill/rectangles plus HTTP full-frame sends | Correct concurrent output at a much higher payload rate is possible on this board |
| Our target94.37184Mbit/s |512×384×60×8 pixel bits, before protocol overhead | Very tight100Mbit/s link budget remains even if software improves |

This does not exonerate every wire, quantify retransmissions, or diagnose a
specific mutex. It rules out interpreting the earlier23.817Mbit/s observation
as an inherent board/wire maximum. Both ladder and current receiver use the
wired Pi; the laptop's Wi-Fi is outside the frame-data path. No browser
rendering/output performance was measured.

## Identity, deployment and verification

1. [BUILD.json](BUILD.json) pins committed source, embedded UTC identity and
   binary hashes. ESP-IDF5.5.5/Arduino3.3.11, chipv1.3, CPU360MHz, PSRAM200MHz/
   32MiB observed at boot. [Boot checks](BOOT-CHECKS.json).
2. Installed r43 baseline application matched before write; prefix and baseline
   image retained privately on host/Pi. Existing partition table matched.
   Only the candidate application at0x20000 was flashed and independently
   verified. No bootloader/partition/NVS flash write, MOS flash or mainboard
   reset. [Deployment receipt](DEPLOYMENT.json).
3. One USB boot capture before measurements confirmed selected image and clocks;
   no serial capture during timed tests. The SDK's cached App version label is
   older than the application source commit; use the embedded full build ID
   and image hash rather than that generated label. No timing claim relies on it.
4. Host C++/independent Python comparison checked all64 phases. Invalid HTTP
   mode/rate/count requests return400 and final control status remains healthy.
   [Host checks](HOST-CHECKS.json), [control checks](CONTROL-CHECKS.json).
5. All experiment code/configuration is task-local. Generated dependencies,
   binaries and machine identities are ignored. Production VDP sources unchanged.
6. Candidate remains installed and idle for review, as requested. Consequently
   Extender keyboard/SD/web-video services are absent until baseline restoration.
   Mainboard startup/SD contents were not changed. No background test remains.

## Duration and limits

Twelve timed windows total180.150seconds, excluding reference generation,
SSH/file transfer, preparation, builds and deployment. Each30Hz case occupies
about20seconds; each60Hz case about10seconds plus a small drain interval.
This is short repeatability evidence, not a soak qualification.

The renderer fills every pixel and draws16 moving24×24 rectangles; it does not
reproduce Nurples/Rally graphics complexity. The animation repeats after64
phases but every adjacent background phase changes. Send-only64-phase PSRAM
storage has different locality from three rendered buffers. All modes keep
those allocations present to avoid changing heap capacity between cases.

No source proven to advertise our exact target was silently labelled a match;
no lossy codec, hidden frame duplication or game-specific sparse redraw was
used to improve the numbers. No physical monitor or browser presentation
claim is made. Golem and the P01h compressor remain unexecuted.

Completion cue: emulator spoken alert issued; stage6/audio_commands=pass receipt
verified. Window left open, human hearing unconfirmed. Physical test image was
not replaced for notification. See [receipt](NOTIFICATION.json).
