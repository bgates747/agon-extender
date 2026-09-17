# SRLE2 browser tasklet results

## Executive summary

**Keep the browser implementation and replay suite. SRLE2 decoding works, and
it can substantially reduce frame payloads; a P4 performance win is still unproven.**
The final packaged run passed 1,440 exact frame comparisons:12 fixtures × raw/RLE2/
SRLE2 ×20 frames ×2 repetitions. Native encode/decode also matches the pinned
original szip CLI. All 22 browser rejection/lifecycle/resource controls passed,
including a single Worker decoding 24 changing-size fixtures. No bench access occurred.

| Representative fixture | RLE2 message bytes | SRLE2 message bytes | Change vs RLE2 | RLE2 browser decode/parse ms | SRLE2 browser decode/parse ms |
|---|---:|---:|---:|---:|---:|
| Seeded random noise,512×384 |196611|151736|−22.8%|0.531|18.808|
| Scrolling synthetic pattern,512×384 |49198|409|−99.2%|0.836|1.403|
| Retained synthetic sprite fixture,512×384 |7070|959|−86.4%|0.219|0.772|

These are repeated **Linux/headless-Chromium localhost** means, excluding the first
2 frames per repetition. They are not P4 encoding, Ethernet, Nurples gameplay or
physical display rates. The retained sprite image contains substantial black area;
it does not represent worst-case game entropy. Noise is the costly case: receipt
averaged 39.74 ms (about 25.2 frames/s), versus roughly 34.2 ms for regular patterns,
under the existing 30 Hz credit ceiling. Tiny images grow with SRLE2 headers.
Selecting a codec by complete size and total cost remains necessary before product
promotion; this diagnostic suite deliberately forces each codec for comparison.

**Next: review this browser candidate, then rebuild and qualify the corrected P4
port when the bench is released. Do not deploy the earlier compiled r01 image.**
It predates the output/lifetime corrections found by these tests. Nothing in this
run changes installed firmware or enables EVS1 on the P4.

## What was implemented

1. Pinned original szip C compiled to WebAssembly, bounded by a 64 MiB fixed memory
   reservation and an isolated Worker with a 2-second termination deadline.
   The same generated C adapter is checked natively against the unmodified original
   Linux CLI. EVS1 carries historical CmpS-wrapped RLE2; raw EVF1 and RLE2 EVR1 retain
   their meanings. Original source and license notices remain available.
2. The actual retained firmware webpage, parser and WebGL presenter are used.
   prepare_client.py inserts the reusable Worker decoder and observation hooks;
   a pinned source snapshot makes the suite independent of ignored build caches.
3. A localhost HTTP/WebSocket producer supplies golden frames using negotiated
   format and one-frame credits. Raw fallback, connection replacement, actual
   WebSocket fragmentation and withholding credits are tested. The one-command
   runner records durable progress, durations, samples and failure outcomes.

## Defects found and resolved in source

1. The earlier adapter incorrectly reinstated a commented fwrite: original
   sz_unsrt(NULL) already emits decoded output using putc. The extra write appended
   a work buffer. The shim also omitted putc redirection. Both are corrected;
   original vendor bytes remain untouched. Initial evidence remains in
   evidence/stop01 and the preceding commits.
2. Function-local static sort pointers survived invocation-owned allocation cleanup,
   causing stale pointer reuse. Generated sources now make those caches invocation
   local and reset the remaining global sort cache. Repeated native and Worker
   fixtures verify the corrected lifetime, including changing image sizes.
3. The desktop heap shim initially called macros redirected back into itself.
   It now undefines malloc/free before using host libc. This was a host adapter
   defect, not evidence of a P4 allocator fault.
4. The inherited webpage called WebSocket.close(1002), which browser JavaScript
   rejects. The staged client uses private code4002. Rejection now closes the
   connection, leaves the last valid image visible and permits explicit reconnect.
   The rule is defined in the [WebSockets standard](https://websockets.spec.whatwg.org/#dom-websocket-close).
   The production client is not silently modified; carry this correction forward
   with the accepted client. Server-originated1002 remains valid.

## Validation and limits

1. All 12 original-CLI corpus outputs decode to their exact input RLE2 bytes.
   Adapted native encode is byte-identical to that CLI; adapted native decode is
   byte-exact, with output canaries intact. Five tiny stored blocks, undersized
   destinations, asset-alpha preservation and 45 truncations passed separately.
2. Browser controls cover invalid headers/version/dimensions/lengths/sort order/
   index/record size, truncated messages, opaque-frame rejection of asset alpha,
   Worker deadline and page responsiveness, single in-flight admission, mixed
   fixtures, slow source/consumer, fragmentation, takeover and raw fallback.
   Twenty-four mixed-size frames supplement the1,440 paced comparisons.
3. This is a bounded negative corpus, not proof that the original codec is safe
   on every hostile bitstream. P4 heap/stack high-water, allocation exhaustion,
   watchdog behaviour, command65 integration and actual hardware encode/decode
   remain release-gated. Desktop Worker isolation does not protect a P4 task.
4. Full samples separate szip, RLE2 expansion, main-thread parsing, presenter
   submission and receipt cadence. GPU palette conversion is inseparable from
   submission here; submission is not GPU completion. Live allocation high-water
   was not measured:64MiB is reserved Wasm memory, while12MiB is the codec's
   cumulative invocation allocation budget. Do not call either measured usage.
5. First-frame module initialization is retained separately in comparison.json.
   Worker IPC/scheduling is not isolated by inner decoder timings. This headless
   software-renderer result must not be generalized to all browser machines.

## Evidence and reproduction

[One-command reproduction](REPRODUCE.md), [complete comparative tables](evidence/final/TABLES.md),
[wire contract](PROTOCOL.md) and [retained run identity/duration](evidence/final/run.json).
The final packaged run is `QUAL-003-2026-09-17-01-41-50Z` and took114.5 seconds
including preparation and two replays. The additional 22-case edge run took 14.9
seconds and is retained separately. Allow roughly 3 minutes for a comparable local
run; browser/tool cold startup may change that estimate.
No firmware, bench endpoint, physical SD, Pi or serial connection was touched.
No experimental remote push. Production promotion awaits review.
