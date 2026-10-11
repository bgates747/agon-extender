# Indexed HDMI research — P4 capability and compile-only example

## Executive summary

**P4 hardware can expand a one-byte programmable palette index into RGB pixels.
The existing HDMI scanout path cannot consume those indices directly.** The
capability is documented for the older v1.3 silicon, not merely the newer P4
revision. Espressif recently enabled the public PPA BLEND CLUT API; our pinned
ESP-IDF 5.5.5 predates that support. An isolated example reuses the upstream
feature through a narrow generated backport without editing the SDK or product.

The promising pipeline is indexed PSRAM → PPA palette expansion → RGB SRAM
strips → DSI DMA → LT8912B → HDMI. It could avoid CPU expansion and perhaps full
expanded output images. **Neither advantage has been demonstrated on our
hardware.** Task-context submission, palette ownership and scanout deadlines
remain integration gates. No bench, emulator, deployed firmware, SD, startup, timing mode
or production changes occurred. This report closes only the bounded R07-03
research/sample tranche in [RESEARCH-007](../RESEARCH-007.md).

## What the hardware and software actually support

| Question | Finding | Evidence and limit |
|---|---|---|
| Does our older P4 have a programmable palette engine? | Yes: PPA BLEND has separate background/foreground CLUTs, each 256 × 32 bits; L8 and L4 select palette entries. | v1.3 TRM §35.5.1.2, printed p1662. This is hardware documentation, not a board test. |
| Does L8 mean grayscale here? | No. PPA BLEND L8 means an eight-bit table index. | PPA driver documentation and the upstream CLUT implementation. DSI GRAY8 is a different format. |
| Can that engine produce our HDMI pixel format? | Yes: BLEND supports RGB888 output in memory, as well as RGB565/ARGB8888. | TRM and pinned PPA LL. The example selects B,G,R byte-order RGB888. |
| Can DSI DMA read arbitrary palette indices? | No documented CLUT path in the inspected DSI bridge. | Selected HAL accepts RGB/YUV, plus grayscale in a newer-silicon branch. No programmable indexed mode. |
| Can LT8912B perform the expansion? | No indexed capability documented. | Manufacturer brief lists RGB666/RGB888 DSI input; Espressif's driver advertises RGB888. |
| Can PPA stream directly into the DSI output FIFO? | No documented connection established. | PPA writes system memory through DMA2D; DSI reads system memory through its VDMA/DW-GDMA path. |
| Can PPA write only a small strip into SRAM? | The driver supports internal SRAM destinations and cropped blocks. | Existing alignment/DMA checks accept internal RAM. Actual SRAM conversion is prepared, not executed. |
| Can one public PPA operation expand L8 and scale it? | Not with the inspected APIs. | BLEND supports CLUT; SRM's input formats do not. Expansion followed by SRM is two operations. |
| Is this enabled in our current public SDK? | No. A narrowly adapted upstream feature compiles separately; product SDK stays unchanged. | Exact target results below. |

Primary hardware references:

1. [ESP32-P4 v1.3 TRM, pre-release v0.4](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_technical_reference_manual_en.pdf),
   §35.5.1.2 p1662 and §35.5.4.1 pp1666–1667. Retrieved PDF SHA256
   `ae1fa2a411776760e03329adc3f9a7c13e98c440168cab208f06e3b2d5818830`.
2. [ESP32-P4 TRM, pre-release v0.7](https://documentation.espressif.com/esp32-p4_technical_reference_manual_en.pdf),
   PPA §§39.3–39.5.2 pp2255–2262; DSI §43.4.1 p2635 and register43.6 p2671.
   Retrieved PDF SHA256
   `622fe9625d19cf00bd7aa49e65f0b5dd6ef2197f83cb7a88b4405078d6a957d4`.
3. [LT8912B manufacturer brief, Rev1.3](https://www.lontiumsemi.com/UploadFiles/2022-03/LT8912B_Brief_R1.3.pdf),
   pp1–3, and [Espressif LT8912B driver0.2.1](https://components.espressif.com/components/espressif/esp_lcd_lt8912b/versions/0.2.1/readme).
   The proprietary manufacturer brief is linked rather than vendored. Current
   project driver provenance remains in [UPSTREAM.json](../../../vdp/components/esp_lcd_lt8912b/UPSTREAM.json).

The public errata reviewed at
[Espressif's errata source](https://github.com/espressif/esp-chip-errata/tree/fc6f59fc612eb75ecb4889786cc72d1440047e5e)
contains no PPA/CLUT-specific entry. Absence of an erratum is not physical
qualification. The CLUT feature is outside the new-silicon conditional guards;
the example deliberately builds for the older P4 revision range.

## Precise SDK gap and upstream reuse

| Role | Exact identity |
|---|---|
| Product SDK retained unchanged | ESP-IDF 5.5.5, `b774170ff46c393eeb5e495ea37936038d3f4f4f` |
| Upstream feature reused | `76b4cf1336168aad6d1db4b8d1d2743137db4092`, “feat(ppa): add color look-up table support for blend” |
| Newer source inspected | `86f72d0982d3ef38b62cb7cc87ae03c9da96a83b` |
| Sample lineage | `ppa-clut-example-r05`, compile-only experimental firmware |

The old [PPA types](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/hal/include/hal/ppa_types.h)
and [LL header](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/hal/esp32p4/include/hal/ppa_ll.h)
comment out L8/L4 cases, while retaining CLUT register helpers. The old
[BLEND driver](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_driver_ppa/src/ppa_blend.c)
likewise leaves indexed validation disabled. Missing public support was therefore
a driver gap, not evidence that the silicon lacks a CLUT.

Espressif's [feature commit](https://github.com/espressif/esp-idf/commit/76b4cf1336168aad6d1db4b8d1d2743137db4092)
and [palette example](https://github.com/espressif/esp-idf/blob/86f72d0982d3ef38b62cb7cc87ae03c9da96a83b/examples/peripherals/ppa/ppa_palette/main/ppa_palette_example_main.c)
provide the implementation and usage model. The
[public API documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/peripherals/ppa.html#color-look-up-table-clut)
is mutable; the pinned commits above bound this report.

The [six-file backport](clut-example/clut-backport.patch) preserves upstream
CLUT writes, readiness validation, DMA construction, cache handling, transaction
scheduling and cleanup. It adapts only moved HAL paths, newer colour-format
names to old `COLOR_TYPE_ID` values, and platform readiness-flag placement.
No custom DMA engine, ISR submission, scheduler, silicon bug fix or product
driver replacement was introduced. [Provenance](clut-example/backport.json)
records original and derived hashes for all six files plus the full upstream
commit-patch hash. The generated override is Apache-2.0 licensed.

The [build helper](clut-example/build.py) copies only the selected driver
component and two overridden headers into a fresh ignored example build. It
hash-checks the selected SDK, the patch results and compiler. Both the PPA
component and its sample consumer explicitly prefer the overridden HAL headers;
public include propagation alone did not ensure consumer precedence.

## Example and compile evidence

The [sample source](clut-example/main/main.c) exercises the real
`ppa_set_color_lookup_table` and `ppa_do_blend` APIs. It contains no substitute
CPU conversion for the actual output and no compile-time exclusion of the PPA
path. The CPU only calculates independently expected pixels after DMA.

1. A 512×64 PSRAM source covers all 256 byte values. The selected block begins
   at row32 and expands to a 512×32 RGB888 strip: 49,152 bytes plus a 64-byte guard.
2. The background uses L8 and an opaque arbitrary RGB palette. A separate zeroed
   A8 foreground supplies transparent alpha. Public BLEND still reads **both**
   input streams; no one-input bandwidth saving is claimed.
3. Two completely different palettes are installed between completed blocking
   transactions, without rewriting indices. The source prepares separate SRAM
   and PSRAM destination checks and rejects missing/disabled CLUT state.
4. Independent checks cover every B,G,R byte, the physical output guard and final
   physical index-buffer contents. Cache invalidation covers the guard as well
   as image bytes; cached CPU values cannot substitute for those physical reads.
5. The program unregisters the client and releases its allocations. All API
   calls occur in task context. No DSI, HDMI, keyboard, network or SD services
   are initialized.

Both final target builds used committed sample inputs from
`9c9179f775394d1292535f0b8bae96056eaaa37a`, pinned SDK5.5.5 and the same native
RISC-V GCC14.2.0 toolchain, compiler SHA256
`a58c7ac425b8b06ba0a4cb6f774553bcccf2ed2c496e738e50ea6c490227b784`.
The original manifests truthfully record repository dirt: this report draft was
untracked. Every sample input matches the committed, recorded hash. No sample
source changed between the paired builds.

| Build variant | Unmodified SDK control | Upstream CLUT backport |
|---|---|---|
| Build ID | `ppa-clut-example-r05-b2026-10-11-23-50-31Z` | `ppa-clut-example-r05-b2026-10-11-23-49-28Z` |
| Configure | Pass | Pass |
| Target compilation/link | Expected compilation failure | Pass, no compiler warnings |
| Result | Missing `PPA_BLEND_COLOR_MODE_L8`, `ppa_set_color_lookup_table`, `PPA_CLUT_BLEND_BG` | Real API calls linked into application ELF |
| Application image | None | 209,088 bytes |
| Hardware execution | Not performed | Not performed |

Application SHA256:
`8004b5f02d01e773acc70b5378c8d55a216661c20f3336bdcd32582f17da77c6`.
ELF SHA256:
`993c80e91f67d7462dd4e926d4f3688034dc6df9a958e77ed90715abf69d41ca`.

[Normalized evidence](COMPILE-EVIDENCE.json) retains exact source/configuration,
compiler, log, manifest and generated-artifact hashes plus the negative-control
errors. Actual Ninja dependencies prove the overridden `ppa_types.h` reached
the sample and PPA sources, and the overridden `ppa_ll.h` reached the driver.
The sample object calls both PPA APIs, both symbols appear in the final ELF,
and the application contains its build identity. No mocked or excluded API
path passed in their place. Effective configuration includes PSRAM boot
initialization/200MHz, CPU360MHz, 64-byte L1/L2 cache lines and the older-silicon
range. These are build selections, not measured clocks or electrical tests.

Generated builds, full logs and original manifests remain in ignored
`agents/research007/indexed-r01/{stock-sdk-control-r05,backported-build-r05}`.
The six base SDK file hashes remain exact and its Git tree is clean. The product
renderer, host tools, EMOS, build profiles and production selection are unchanged.
Neither build is a deployed firmware or a runtime correctness result.

Preparation exposed ordinary host/configuration issues, resolved before the
reported target comparison: migrated x86 tools were replaced by the existing
host-native ARM64 tool selection; the sample explicitly depends on `esp_psram`
so its Kconfig and initialization are included; consumer header precedence and
physical guard verification were corrected. Revision r05 also flushes the full
initialized source before its final whole-buffer physical integrity check; the
driver only flushes the cropped input region. Superseded incomplete configuration
attempts have no retained diagnostic value beyond this note. An earlier r04
comparison reused a timestamp across variants; its records must be identified
by variant and hashes. The final r05 comparison has distinct immutable build IDs.

## Integration constraints that remain real work

These findings bound later R07-02/R07-04–06; they are not a new implementation
contract or authorization to modify the renderer.

1. **Task versus interrupt ownership.** Current rolling refill callbacks run in
   interrupt context. Public `ppa_do_blend` uses ordinary `xQueueReceive` and
   `xSemaphoreTake`, including in nonblocking submission. The P4 rendering task
   would have to submit ahead of consumption; an ISR completion callback could
   publish/notify completed ownership. Calling the public API directly from
   the existing refill ISR is not supported. See the pinned BLEND driver above
   and [current refill implementation](../../../vdp/video/extender/display/rolling/strip_runtime.inc).
2. **Deadline, not just average throughput.** Existing output uses three 32-row
   SRAM slots and a conservative 1,600µs refill guard. Hardware conversion must
   complete before DSI consumes each slot while drawing/sprites/input remain
   active. Compilation establishes no latency distribution or 60Hz guarantee.
   [Current guard](../../../vdp/video/extender/display/rolling/strip_config.h)
   remains unchanged.
3. **Palette publication.** CLUT state is shared by clients using each engine
   input. The P4 must finish dependent transactions before replacing that table.
   The sample uses one client and blocking operations. Copper palette changes
   inside a strip require subdivision or another rendering path; a single CLUT
   update cannot silently stand in for multiple scanline palettes.
4. **Sprites and memory ownership.** A completed RGB strip could in principle
   receive the existing CPU sprite overlay, followed by the proper DMA/cache
   handoff. That integration has not been written or measured. The example
   allocates one destination at a time; it does **not** remove the product's
   two full RGB888 panel-image allocations or change scanout publication.
5. **Scaling is separate.** Public SRM supports RGB/YUV and silicon-dependent
   grayscale, not indexed CLUT input. A low-resolution mode requiring scaling
   would need expansion first and a separate SRM pass with these APIs. No fused
   indexed-expansion/scaling claim is supported.
6. **Single-input bypass is only a research lead.** The old LL contains
   `PPA_LL_BLEND_TRANS_MODE_BYPASS_BLEND`; public BLEND always selects normal
   blending. TRM prose says a bypassed background can still use A4/A8 foreground
   alpha, and its register-bit enumeration conflicts with its prose/LL polarity.
   Neither bypass availability nor that inconsistency proves foreground DMA
   can be removed. Preserve upstream LL behavior; do not invent a cheaper
   custom transaction from the name alone.
7. **Stock colour semantics still govern.** Logical palette remapping in stock
   64-colour modes differs from paletted lower-colour scanout. The
   [completed inventory](PIPELINE-INVENTORY.md) records that distinction.
   Hardware support for 256 entries does not authorize a 256-colour mode or
   establish transparent bitmap, raster-operation, Copper and readback fidelity.

## Practical conclusion

The earlier “yes” has a defensible meaning only when expanded to **yes, the P4
PPA can perform programmable index-to-RGB expansion in hardware**. It does not
mean direct indexed HDMI scanout, a free expansion/scaling pass, or a proved
performance improvement. We now have a bounded upstream-derived sample rather
than a speculative API. Physical conversion correctness and measured strip
deadlines require a separately authorized bench tranche; product storage and
rendering decisions remain open in the owning task.
