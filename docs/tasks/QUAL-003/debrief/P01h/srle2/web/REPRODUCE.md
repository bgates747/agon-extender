# Bench-free SRLE2 qualification

Run from the repository root on Linux. This suite uses only localhost and owned
child processes. It never discovers or connects to a board. A new output directory
is required; existing evidence is never overwritten.

## Dependencies

1. Project `.venv/bin/python`, `cc`, aiohttp and Playwright with Chromium installed.
   Install missing Python dependencies into the project virtual environment only:
   `.venv/bin/python -m pip install aiohttp playwright`, then
   `.venv/bin/python -m playwright install chromium` if necessary.
2. Emscripten4.0.23, installed privately using the
   [official emsdk procedure](https://emscripten.org/docs/getting_started/downloads.html).
   Pass its `upstream/emscripten/emcc` path explicitly. The tested SDK source commit
   is in TOOLING.json; no system installation or shell startup change is required.
3. All codec sources, the retained real firmware client baseline, the RLE2 decoder
   and generated-fixture inputs are tracked. No prior ignored candidate checkout
   is required. Generated native binaries/Wasm/corpus files belong in ignored output.
   Original GPL notices are retained; the staged client includes COPYING.GPL-2
   and codec provenance. Distribute the matching source/adapters with that client.

## One command

```sh
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/srle2/web/run_all.py \
  --emcc agents/srle2-web/emsdk/upstream/emscripten/emcc \
  --output agents/srle2-web/my-new-run --count 20
```

The default is two complete repetitions. The runner compiles the original Linux
encoder, generates its byte-golden corpus, builds native/Wasm adapters, stages the
actual client, checks native encode/decode and edge cases, then runs browser
recovery tests and raw/RLE2/SRLE2 exact-pixel/timing comparisons. It records progress
and completion in run.json, per-step logs, JSON samples, TABLES.md and screenshots.
On a nonzero result, inspect that step's log and failure.json; never infer success
from an open browser. The runner has a20-minute outer watchdog and terminates only
its own subprocess groups. Browser edge checks have a 180-second limit; each replay
has 900 seconds and each Worker decode has 2 seconds. These are desktop test guards,
not suggested board reset timeouts.

The qualifying run used 20 frames per fixture/format/repetition and excluded the
first 2 from steady timing means. First-frame samples are retained. Run duration
is recorded for future estimates; it includes compilation and browser startup.

## Individual controls

`replay.py --corpus DIR --client DIR --output NEW_DIR --pace 30 --count 20`
reuses generated inputs. Add `--browser PATH` for an explicit Chromium binary.
The server always binds 127.0.0.1 on an available port; no remote-host option exists.
`--pace 0` removes the server's delay, but the real client retains its30Hz credit cap.

For protocol-level single-frame stepping, open the loopback `/video?srle2=1`
WebSocket and send exactly one text `frame` credit per desired frame. No subsequent
frame is sent without credit. The suite's slow-consumer test exercises this by
withholding credits; its fragmentation case uses actual WebSocket continuation
frames, not fake independent TCP packets. The automated page is the normal client
with observation hooks and the decoder boundary added by prepare_client.py.

The replay manifest supplies exact raw originals, encoded bytes and hashes.
`source-hashes.json` pins the real page/parser/presenter; `decoder/build.json` pins
generated binaries. `comparison.json` retains stage means and cold-start timings;
full samples preserve the distinction between decoding, main-thread parsing,
submission and receipt. No result measures P4 encoding or Ethernet throughput.

## Scope after review

Keep this immutable task evidence. Promote the accepted decoder and reusable
runner to their production/testing homes only after review. Then release the bench
explicitly, rebuild the corrected P4 port, and use the same corpus for device-side
validation before enabling EVS1 in firmware. The earlier compiled r01 P4 image is
obsolete and must not be deployed. It does not contain the host-discovered fixes.
