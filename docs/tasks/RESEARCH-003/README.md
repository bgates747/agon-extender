# Standalone P4 HTTP rendering/output fixture

## Executive summary

This task replaces VDP/FabGL temporarily with a project-authored deterministic
producer using Espressif's Ethernet and HTTP APIs. It is the frozen contract's
fallback after no matching upstream advertised lossless Ethernet60 firmware
was found. It does not claim to be an unmodified upstream video application.
See [design/source selection](DESIGN.md), [contract](../RESEARCH-003.md) and
[build identity](BUILD.json). Measurements are in TABLES.md/SUMMARY.json; final
interpretation belongs in RESULTS.md when completed.

## Reproduction

1. Use the repository `.venv/bin/python`; host C++ compiler validates the pixel
   kernel against receiver.py's independent Python reference. HOST-CHECKS.json
   records all64 phases and byte hash.
2. Commit all build inputs. From the repository root run
   `.venv/bin/python docs/tasks/RESEARCH-003/build.py`. It uses pinned PlatformIO
   packages, records source commit and embeds a UTC build identity. Generated
   files remain ignored. SDK-generated App version can retain a cached older
   Git label; the explicit embedded build ID plus manifest/hash is authoritative.
3. Supply ignored `private/config.json` using the bench authority, with SSH
   options/host, remote directory/Python/esptool, stable USB port/serial, P4 host
   and verified baseline directory. `bench.py deploy` preserves the installed
   prefix, rejects unexpected app/partitions, writes application only and
   independently verifies flash. Do not deploy from an unexpected baseline.
4. `bench.py test` now runs two repeats of600 logical frames at30Hz for render,
   send and combined cases. Results persist individually; private progress/logs
   identify current case. About3minutes of timed windows plus reference creation,
   transfer and setup; preparation/flashing are separate. No browser viewer.
5. `report.py` derives TABLES.md and SUMMARY.json from retained raw evidence.
   Passing exact-pixel checks do not mean the requested frame rate was met.
6. Current image remains installed for review; verified original image/prefix
   remain in private deployment storage. Do not claim ordinary Extender input,
   SD or display services are present in this standalone image. Emulator voice
   is the completion cue. Rollback requires stable-identity verification and
   exact original app readback, then ordinary service re-admission if needed.

## Protocol and measurement details

Control/data endpoint: HTTP GET `/run?mode=render|send|combined&fps=30|60&frames=600`.
Accepted frames range120–1800. HTTP port8080 `/status` stays independent of the
stream server; no polling during timed measurements. Sender uses standard HTTP
chunking; decoded application stream consists of little-endian six-word headers
and a payload. Header words: magic, sequence, bytes, render microseconds,
completion timestamp low/high. `R3F1` payload is196608 raw colour bytes; `R3J1`
payload is final JSON. IDs are strictly increasing with explicitly counted gaps.
Run handlers are serialized by the HTTP server; do not queue competing runs. Socket waits are bounded by5seconds;
receiver timeout90seconds exceeds the maximum60second render-only run.

Three exclusively owned PSRAM slots pass through FreeRTOS queues. Producer
core0/priority5 never overwrites a leased buffer; HTTP sender core1/priority5
returns it after send. No per-row graphics mutex. 64 precomputed phase buffers
exist in every mode; send-only selects them instead of invoking the renderer.
No control of Agon UART, GPIO bus, keyboard, SD, camera or LCD.

1. Rendering means full-frame software pattern fill plus16 moving24×24 filled
   rectangles. It is not Nurples, LVGL, VDP sprite drawing or browser drawing.
2. Send-only produced count measures admitted buffer descriptors, not rendering.
   Its near-zero render_us is bookkeeping and must not be sold as rendering time.
3. Slots skipped for unavailable buffers or a deadline overdue by a full period
   are counted as dropped. Pending output drains after final logical slot.
4. Reported fps uses complete device run window including final drain. HTTP
   submission/completion is distinct from host receipt, which is counted and
   validated separately. Host interval statistics are included in SUMMARY.json.
5. Render-only sends no pixels; its raw collector `pixel_validation=pass` means
   no protocol/check failures, not hardware pixel readback. Full byte validation
   applies to all send/combined frames; host kernel comparison covers renderer
   logic separately. No visual/browser/monitor presentation claim.
6. Render/send times are wall time including preemption; they overlap and must
   not be added as CPU time. Producer interval percentiles exclude first60
   produced frames; render-time summaries include all produced frames.
7. Task fixture/SDK choices and memory layout differ from VDP. The comparison
   isolates removal of the entire VDP workload, not a single causal variable.

Cadence amendment: historical evidence includes explicitly requested60Hz cases.
The current runner is capped at30Hz under ADR-0020; it does not rerun those
stress cases. Installed firmware still exposes its diagnostic60Hz option; no
production limiter or new flash is claimed by this host-runner change.
