# Draft offline validation — 2026-09-11

The Author accepted and froze the work contract in `fc14f02`. The new code
remains uncommitted pending Author emulator review. No physical firmware,
reset, serial connection or SD-card write occurred during this preparation.

## Completed checks

1. The EMOS repository wrapper passes firmware, ROM-size, ABI, baud, runtime,
   linked-input and boot-smoke checks. The diagnostic receiver adds 121 bytes:
   130340 total, leaving 732 bytes below 128 KiB. It reuses the existing
   selected-source dispatch and register-preserving callback path.
2. Classic ESP32 and P4 diagnostic images compile. Official MOS/VDP references
   remain clean at v3.0.2/v2.16.0. Removing the guarded diagnostic additions
   leaves the reviewed P4/stock renderer tokens unchanged in every edited
   renderer/dispatcher file. No renderer repair or scheduling change is hidden
   in this experiment.
3. Recorder tests exercise enabled/disabled scopes, boundary crossing and
   fence completion after normal software-sprite processing, including a
   separate thread. The original generated Shapes/Bitmaps suite checks pass.
4. A complete paired native run exercises real EMOS, both native VDP peers
   and a raw FAT image: 64 cases per route, drawing plus output windows,
   **256 intervals / 2048 metric rows** saved. All expected case/metric order,
   byte counts, statuses and terminal counts validate. The application also
   verifies that diagnostic replies do not increment the keyboard counter.
5. The peer injects wrong length, magic, version, source and stale token before
   a genuine admission. All five are ignored and the real transaction finishes.
6. Independent image checks pass **17/17**: quiet software-sprite position
   updates remain deferred, explicit updates appear, hardware movement works,
   and the repeated baked animation matches. Scrolling/clipped-row probes
   pass on both routes. The only two saved probe disagreements are the known
   SHP23 stock expectation, once on each route; they are not repaired here.
7. The reusable UART emulator adapter passes a real socket-saturation test
   and all **135** mos-agondev tests. It supplies host backpressure without
   dropping bytes or blocking the emulated CPU. A subsequent traced paired
   run also completes all 256 intervals and 17 presentation comparisons.

The ordinary complete native result CSV has SHA-256
`e1fef331d6e1eb9cebf535c66858e845745d95b9bd15bf50e518296db9747bb0`.
Its 17-check image report has SHA-256
`e692050623e1008e61af86c3fb88617d5add7ac3393a068873aa7ae227fd2a5f`.
The ignored local review record retains build manifests, profiles, results
and partial runs. These are functional results; native microseconds are never
physical ESP32/P4 performance evidence.

## Informative preparation failures and limits

1. RST18's count is BC16, not the full 24-bit register: a large initial stage
   was truncated before the fixture split stages into bounded public calls.
2. A burst of result records lost replies during native review. The current
   diagnostic retrieves one saved metric per request after completion; this
   retrieval is outside the timed drawing and first-reply interval.
3. The earlier project socket adapter exited with status 2 on `WouldBlock`.
   Its captured stderr identifies host-socket saturation. This was initially
   suspected to be a guest exit; it was not an EMOS crash. The maintained
   mos-agondev helper now models bounded backpressure instead.
4. One later native run reached the bounded COMBINED completion timeout and
   saved an incomplete terminal result. It is retained for investigation;
   subsequent ordinary and traced runs completed. No silent retry, ignored
   failure or longer bound was added. This does not establish repeatability
   under every host load, nor attribute a fault to physical mainboard VDP.

The Author accepted the completed visual review and MOS return on 2026-09-11
and authorized deployment with both boards powered and the SD card available.
The screenshot shows 256 completed intervals and the two expected probe
differences. Clean candidate preparation, actual mainboard flash backup,
physical comparison and restoration remain outstanding. The physical
procedure is in [README](README.md); automated Nurples remains deferred.
