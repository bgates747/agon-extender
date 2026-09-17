# Reproduce the bench-free codec screen

## Executive summary

All commands run on Linux from the repository root. Only loopback sockets and
owned child processes are used. No board address, serial port, SD mount, firmware
or reset enters this workflow. Use new private output directories for fresh runs.

## Dependencies and execution

Project `.venv/bin/python`, Pillow, aiohttp, Playwright Chromium, native C/C++
compiler and zlib development library, plus the pinned Emscripten SDK from the
previous browser task. Original szip sources/notices remain under `../srle2/vendor`.
The generated Wasm/client is GPL-derived: preserve the notices and matching source
when distributing it. It is not a production firmware or negotiated web format.

```sh
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/srle2/web/corpus.py agents/my-codec-corpus
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/codec-screen/build.py agents/my-codec-build \
  --emcc agents/srle2-web/emsdk/upstream/emscripten/emcc
.venv/bin/python -u docs/tasks/QUAL-003/debrief/P01h/codec-screen/screen.py \
  --build agents/my-codec-build --corpus agents/my-codec-corpus --out agents/my-codec-native
.venv/bin/python -u docs/tasks/QUAL-003/debrief/P01h/codec-screen/browser.py \
  --native agents/my-codec-native --build agents/my-codec-build --out agents/my-codec-browser
```

After the browser run, repeat paired native timing without browser load:

```sh
.venv/bin/python docs/tasks/QUAL-003/debrief/P01h/codec-screen/repeat.py \
  --native agents/my-codec-native --build agents/my-codec-build \
  --selected agents/my-codec-browser/selected.json --out agents/my-codec-browser/paired.json
```

Wait for native `complete.json` before launching the measured browser run. The
native harness checkpoints every result and can resume its same output directory;
do not reuse that directory after changing inputs, codec binaries or the matrix.
A clean rerun with the five-second guard may exclude additional order0 cases that
completed in the original unbounded portion. Preserve those historical timings;
this is expected, not a requirement to disable the guard again.

`report.py --native DIR --browser DIR --out EVIDENCE_DIR` writes compact CSV/JSON
and TABLES.md beside the evidence directory. Keep full private samples if further
statistical work is needed; every successful native payload has an integrity hash.

## Measurement contract

1. Native: one warmup plus three encode samples. Time includes codec allocation
   and, for SRLE2, the first RLE2 pass. It excludes Python setup, process startup,
   exact verification and file writes. Timeout covers the complete worker.
2. Browser: eight exact frames per case/selected variant, first two excluded from
   means. All12 cases share the same raw originals. PNG native decoder output is
   checked by RGBA readback against the64-colour palette; other codecs compare
   decoded indices. Verification readback is excluded from inner decode timing.
3. Paced:90 frames per selected variant across full-size cases, capped at30Hz by
   loopback server credit admission. Verification readback is off; presentation
   remains WebGL2. Times include Worker handoff where labelled decode-wall.
4. Mixed fallback:24 exact frames switch codec/raw on the same connection when
   the compressed message would not be smaller. Header/error/Worker-timeout tests
   reject invalid data and then verify recovery to a valid raw frame.
5. CPU submission is not physical refresh, GPU completion or displayed fps.
   Headless Chromium uses SwiftShader. No Ethernet ceiling, P4 encode time,
   embedded memory fit or game/rendering throughput is measured by this suite.
6. The64-colour screen does not qualify future256-colour PNG/RLE2 behavior.
   PNG indexed8-bit layout can represent256 entries, but this encoder deliberately
   writes the present64-entry palette. RLE2 keeps its existing64-colour contract.
