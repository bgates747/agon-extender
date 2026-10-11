# PPA indexed strip example — experimental, compile only

This example expands a one-byte L8 index image through a programmable 256-entry
PPA palette into a 512×32 RGB888 strip. It prepares independent pixel checks for
SRAM and PSRAM destinations, two palettes without rewriting indices, nonzero
source-row offset, missing/disabled-table rejection and an output guard. **No
hardware run has been authorized or performed.** It does not generate HDMI.

Current fixture identity: `ppa-clut-example-r05`. The source-only r01 was revised
so the final input-integrity check invalidates CPU cache. Preparation of r02
exposed two build-integration issues, corrected before meaningful target results:
explicitly depend on `esp_psram` to include its Kconfig/initialization, and force
the sample consumer's overlay headers before the stock HAL as well as doing so
for the PPA component. Revision r04 also invalidates the complete RGB output
and guard after DMA, so a cached guard cannot conceal a physical overrun.
Revision r05 publishes the complete indexed source before conversion: the driver
flushes only the selected lower half, while the integrity check covers both
halves. The SDK itself remains unchanged; r03 was source-only.

## Origin and SDK boundary

1. Espressif added public BLEND CLUT support in
   [commit 76b4cf1336168aad6d1db4b8d1d2743137db4092](https://github.com/espressif/esp-idf/commit/76b4cf1336168aad6d1db4b8d1d2743137db4092).
   Operation and B,G,R verification idioms follow its Apache-2.0 correctness
   tests. The newer
   [palette example](https://github.com/espressif/esp-idf/blob/86f72d0982d3ef38b62cb7cc87ae03c9da96a83b/examples/peripherals/ppa/ppa_palette/main/ppa_palette_example_main.c)
   independently demonstrates programmable L8 input through the public API.
2. Extender retains ESP-IDF5.5.5 commit
   `b774170ff46c393eeb5e495ea37936038d3f4f4f`. Unmodified, that SDK has CLUT register
   helpers and colour-depth definitions but leaves the public API/format cases
   disabled. The negative-control build deliberately selects it unchanged.
3. [clut-backport.patch](clut-backport.patch) applies only the upstream CLUT
   feature to six hash-pinned old SDK files. It adapts moved HAL paths,
   newer FOURCC names to existing `COLOR_TYPE_ID` values, and readiness flags
   to the older platform structure. It retains upstream transaction, DMA,
   cache, synchronization and error handling; no custom transaction engine.
   [backport.json](backport.json) records both commits and base/derived hashes.
4. [build.py](build.py) generates a project-local PPA component plus two header
   overrides under the fresh ignored output directory. It never edits the
   selected SDK, product components, build profiles or production selection.
   The copied driver retains upstream copyright/licence notices; its Apache
   licence is provided in [LICENSE](LICENSE).

## Building

Use the repository Python environment and retained native tools. The helper
reuses `scripts/build_p4.py` tool validation. Both output paths must be fresh:
select host-native `--tools-path` and `--python-env` overrides where required,
as described in [the build guide](../../../building.md).

```sh
.venv/bin/python docs/tasks/RESEARCH-007/clut-example/build.py \
  --output agents/research007/indexed-r01/stock-sdk-control --without-backport

.venv/bin/python docs/tasks/RESEARCH-007/clut-example/build.py \
  --output agents/research007/indexed-r01/backported-build
```

The first build is expected to fail on missing CLUT API/types. The second must
compile and link actual calls into the backported driver, not placeholders or
an excluded feature branch. `build.log` and `manifest.json` retain build identity,
source/tool hashes, exit status and generated artifact identities. These are
experimental target builds, not qualified firmware. The helper contains only
configure/build actions, no flash, monitor, reset, network or device actions.

## What the program would do on a separately authorized hardware run

1. Allocate a 512×64 indexed source and a zeroed 512×32 A8 mask in PSRAM. Source
   pixels cover all 256 indices; the RGB palette is deliberately not grayscale
   or RGB222. The bottom 32 source rows form each output strip.
2. Register one ordinary PPA BLEND client. An L8 background and transparent A8
   foreground produce RGB888. This uses **two input DMA streams**, even though
   the A8 foreground contributes no visible colour. No bandwidth saving is
   inferred from ignoring its pixels.
3. Reject a transaction before its CLUT is set. Convert with one opaque palette,
   wait for completion, verify every B,G,R byte and guard, replace the palette
   and repeat without changing indices. Run those checks with internal SRAM
   and external PSRAM output; verify missing/disabled-table rejection again.
4. Unregister the client and release allocations. The CPU computes expected
   values independently and never fills the actual RGB result. All palette
   writes/submissions happen in task context; no ISR submission is attempted.

Compile success would not establish any of those runtime outcomes. The sample
does not test DSI timing, strip ownership against scanout, sprites, Copper,
palette updates during queued transactions, scaling, input response or gameplay.
It allocates one strip destination at a time, but does not remove the product
driver's full RGB framebuffer allocations. Public SRM has no indexed input;
combining expansion with scaling remains a separate question.
