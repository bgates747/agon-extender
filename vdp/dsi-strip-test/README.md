# Standalone DSI strip experiment

SPRITE-001 owns scope, authorization and results. This is deliberately separate
from Extender firmware: no Agon transport, input, network or SD services.

The unchanged HDMI-002 custom848x480 timing/pattern and vendored LT8912B driver
provide the control. `patch_dpi.py` verifies the exact IDF5.5.5 DPI source hash,
then generates a build-local derivative. The SDK remains untouched.

The final r02 `main/strip_config.h` selects twelve40-row blocks and three rotating
101,760-byte **internal SRAM** scratch buffers (305,280 bytes total). Earlier frozen builds used
eight60-row blocks, PSRAM scratch storage or synthetic squares; select their
exact manifests when reproducing those comparisons. Never rebuild current
source and label it an earlier tested image.

The DMA2D engine copies only the logical512×384 background centered in848×480;
borders remain black. r01 used CPU copies. r02 reuses the pinned Espressif
`esp_async_fbcpy` helper unchanged with exactly one outstanding request and one
handle. Its shared static request configuration is not used concurrently.
After a block retires, its fixed-address scratch buffer asynchronously receives
the block three positions ahead, allowing two block intervals for preparation.
The final refill runs **after DMA rearming**;
otherwise the CPU can miss vertical blank and halve output cadence. Buffers
are retained until reset; there is no teardown or mode-change implementation.

The current fixture paints1/8/16/32 moving16×16 Nurples images, increasing every
600 frames. `stock_sprite_body.inc` retains the exact vendored FabGL scanline
function, its license and provenance. The C++ scaffold is deliberately smaller
than the real VDP object model. RGB888/RGB222 conversion touches covered spans
only. The independent host test compares every pixel for eight poses with both
strip sizes; it does not exercise live bitmap lifetime or the complete API.

At3600 frame completions, the other CPU core starts256×336 scrolling copies in
a **separate** PSRAM allocation at nominal60Hz. That creates concurrent memory
traffic without mutating the displayed background. It is neither real Nurples
nor a test of synchronizing live graphics with scanout.

Counters distinguish frames, blocks, invalid descriptors, underruns, missed
callbacks, refill duration, conservative timing-threshold exceedances and cache
errors. The threshold does not skip drawing or impose an application drawing
budget. Crucially,60 frame completions/s and zero hardware errors **can coexist
with visible corruption** when the CPU refills a buffer too late. r01 has no
late-buffer abort; r02 adds the bounded check described below.
Neither is ready for normal firmware. The original CPU-copy findings are in
`docs/tasks/SPRITE-001/ROLLING-SCANOUT.md`; the DMA comparison and subsequent
three-buffer result are in `docs/tasks/SPRITE-001/DMA-REFILL.md`.

r02 checks every prepared strip against CPU-composed pixels before scanout
starts. During scanout it tracks absolute strip generations; a detected late
next buffer, overlapping request, invalid block, cache error or refill exceeding
the conservative2,000µs threshold latches a failure and disables experimental
scanout. The duration check is independent: a slow completion ISR can delay the
block ISR and conceal lateness from the generation check. The ISR may detect a miss after the reader has begun, so
this is bounded failure handling, not a production guarantee of no corruption.
The earlier r01 deliberately lacked this abort path. Copy latency includes
submission/cache preparation and completion interrupt delay; composition is
measured separately. Cold preflight/priming is excluded from runtime statistics.

A later native integration must establish sufficient refill headroom under
concurrent load, protect bitmap/list lifetime and avoid task mutexes in the ISR.

Build with the project virtual environment:

```sh
.venv/bin/python vdp/dsi-strip-test/build.py --output agents/<new-build-directory>
```

Each build freezes source and verifies artifact hashes, silicon compatibility,
flash segmentation and source closure. The inherited generated executable/factory
filenames remain `hdmi_timing.bin` / `hdmi-timing.factory.bin`; the embedded build
identity and manifest identify the distinct `dsi-strip` artifact. Bench procedures
must read the machine-local hardware record and preserve the full firmware
rollback before flashing. Never select this fixture as production firmware.

For the retained negative control, the builder's `--inject-late-tag 500` changes
only the frozen build source. It deliberately holds completion for4,000µs at
strip tag500; the duration guard must stop output and prevent further frame
rearming. The maintained source defaults to zero (no injection). This deliberately
failed scene is a guard test, not a performance result or a playable image.
