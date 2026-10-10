# PORT-008 — Historical receiver build comparison results

## Executive summary

The original passing DevKit and failed P4-PC reproduction both identify ESP-IDF
5.5.5 and ESP32-P4 silicon v1.3. The retained SDK's relevant receiver, DMA,
cache and GPIO sources match the reproduction SDK byte for byte. No changed
DMA implementation or different silicon revision was found to explain the
failure. One observed build difference is flash clock: original 40 MHz versus
reproduction 80 MHz. This is the instruction/data flash interface, not the
parallel sampling clock or PSRAM speed.

The original executable and complete generated configuration were not recovered
from the bounded retained-artifact search. Later legacy builds cannot fill that
evidence gap. Recommend a single slow-profile record with the existing
standalone reproduction rebuilt for 40 MHz flash as the smallest remaining
build-control experiment; discuss before rebuilding or touching the bench.
Harness and signal timing remain competing explanations, not diagnosed faults.

## Frozen work and evidence scope

BC01 completed before research: Extender `826c6da5` preserves host migration
preparation, `2ead90d6` preserves transport development, and `43fb2706` freezes
transport evidence and this contract. EMOS `a843a1e` preserves its related
transport changes. Unrelated EMOS `scripts/application_peer.py` was left alone.
These are development checkpoints, not production promotion. No push was
requested for this tranche.

1. Original run: [retained passing evidence](../../../../agon-extender-legacy/tests/runs/2026-08-16_005754_prx-06-speed/),
   especially `p4-console.log`, `measurements.json` and `fixture-sources.sha256`.
   Original receiver source is pinned by its manifest and recovered from legacy
   commit `4626fcc41a0da5811a4374175fe803957ec5ab4f`.
2. Failed reproduction: [experiment and restoration](DEVKIT-CONTROL-R01.md).
   Ignored local `agents/port008-live-qualification/devkit-control-r01` retains
   build manifest, generated configuration, compile command, image descriptions,
   installation silicon identification, USB verdict and analyzer evidence.
3. Later legacy material: `.pio/build/p4/project_description.json` identifies
   `legacy-archive-2026-08-26`; `build/project_description.json` identifies
   `c1e6666-dirty`. Neither is the passing run's `7985506-dirty`. The later ELF
   SHA256 starts `799f772b`; the passing log reports `fcb8f943a...`.
   These artifacts are supporting comparisons, not recovered original binaries.
4. Source comparison: the retained legacy PlatformIO SDK package declares
   `3.50505` / IDF `5.5.5`; it has no independent Git metadata. The reproduction
   SDK is IDF commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`.
   Compared source scopes have no local tracked differences from that commit.
   Ignored local `agents/port008-live-qualification/build-comparison-r01`
   contains per-file hashes and the bounded later-configuration comparison.

## Side-by-side findings

| Property | Original passing DevKit | Failed P4-PC reproduction | Interpretation |
|---|---|---|---|
| Endpoint integrity | All 22 records pass full pattern/sequence/CRC | First 1,024-byte record fails; next 21 not run | Receiver source reuse did not restore correctness |
| Silicon | v1.3, boot log | v1.3, installation/verification log | Same reported chip revision; no PC-specific DMA silicon difference established |
| IDF identity | v5.5.5, boot and application logs | v5.5.5, pinned SDK and image description | Same release label; original full source tree identity remains unknown |
| Build frontend | PlatformIO platform commit `9905818f69da26fffb7b6871b5b99523eba91890` in pinned source configuration | Native IDF CMake/Ninja on ARM host | Different frontend/host does not establish different RISC-V instructions; original invocation missing |
| Compiler | Original invocation/version not retained in this run | GCC 14.2.0, `esp-14.2.0_20260121`; RISC-V `ilp32f` | Later legacy ELF/package identifies the same compiler version, but does not prove the original compiler |
| CPU clock | 360 MHz, boot log | 360 MHz, generated configuration | No configured CPU underclock found; no fresh runtime measurement in this review |
| Flash | DIO, 16 MB, **40 MHz**, boot log | DIO, 16 MB, **80 MHz**, generated configuration/flash arguments | Concrete remaining build-control difference; not a PARLIO clock measurement |
| Supported silicon range | v1.0–v1.99, boot log | v1.0–v1.99, image descriptions | Same silicon family; does not select newer v3 hardware registers |
| Receiver source | Manifest SHA256 `0e0f76c0…` | SHA256 `9d2291a6…`; reverse GPIO substitution reproduces original exactly | Payload configuration and lifecycle unchanged; pins changed |
| Buffer | Source requests internal DMA-capable memory, cache-line alignment, 1,024-byte record | Same allocation and alignment source | Neither experiment logged the allocation address; identical address/bank placement not proved |
| Generated DMA/cache settings | Complete original config not recovered | L1/L2 line 64 B, L2 128 KiB; PARLIO handlers in IRAM; cache-safe ISR option disabled; GDMA control/handler in IRAM | Later legacy configs match these settings; do not label those later settings original measurements |
| PSRAM | No PSRAM initialization/heap shown in the retained original boot | Disabled in standalone reproduction | Buffer is explicitly internal in both sources; later PSRAM-enabled legacy configs belong to other builds |
| Slow-profile completion | 5,197 / 5,192 / 5,190 µs, valid records | 5,180 µs, corrupt record | Similar completion time does not make the corrupt record a throughput result |
| Harness | Author reports short breadboard runs and roughly 200–220 Ω series data resistors | Author reports roughly twice the lead length and no corresponding series resistors | Material uncontrolled physical difference; not an electrical measurement |

The legacy board JSON advertises 400 MHz CPU, 80 MHz flash and QIO. Those are
board declarations, not the passing device's observed 360 MHz / 40 MHz / DIO.
Copying that board JSON alone would not reproduce the original operating state.
The pinned original `sdkconfig.defaults` does not explicitly select flash speed.

## Receiver, DMA and cache review

1. **Source equality:** 120 files match across PARLIO (34), DMA support (22),
   memory/cache support (59), PARLIO HAL/LL (3), and heap allocation (2).
   Eight additional files match: P4 GDMA/cache/GPIO low-level headers, AXI GDMA
   HAL, cache HAL, P4 capability and GPIO signal maps, and GPIO driver.
   This comparison covers retained SDK material, not a recovered original build.
2. **Sampling and completion:** `parlio_rx.h` documents falling/rising sampling,
   active-low level qualification, and length-triggered EOF. Both receiver
   sources request falling edges, active-low VALID and `eof_data_len = 1024`.
   `parlio_rx.c` selects RX_FULL for nonzero EOF length. Completion therefore
   does not itself prove correct samples or an electrically clean VALID signal.
3. **Memory visibility:** `parlio_rx.c` registers descriptor-done and EOF
   callbacks. Descriptor-done performs memory-to-cache synchronization for
   cache-backed internal memory and counts bytes. `gdma.c` handles descriptor
   completion before EOF when both are pending; the EOF callback merges aligned
   buffers before notifying completion. The standalone receiver waits for all
   transactions before validating. No omitted application cache call was found
   that distinguishes the old receiver source from the reproduction.
4. **Allocation and alignment:** the receiver requests
   `MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA`; its 1,024-byte allocation is aligned
   to the internal cache line. The driver defaults to 16-byte DMA bursts and
   raises internal alignment to the cache line where required. Original actual
   allocation address and configuration are unknown; this is source review,
   not proof that every cache/DMA corner case is impossible.
5. **Interrupt settings:** handler placement in IRAM and permission to execute
   while cache is disabled are separate options in PARLIO Kconfig. Reproduction
   uses the former, not the latter. Later legacy configs agree. No flash write,
   network stream or HDMI worker is part of this standalone record experiment;
   no evidence ties cache-disabled interrupt handling to the corrupt payload.
6. **Revision paths:** P4 PARLIO LL includes a v3-specific TX valid-delay/gating
   branch. Both physical chips report v1.3 and the reproduction selects the
   less-than-v3 family. That TX distinction does not explain this forward RX
   failure. No differing relevant revision workaround was found in the
   compared source set.
7. **Known inherited choice:** the original receiver sets `free_clk = true`
   although the eZ80 clock runs only during a block. The vendor API describes
   a different setting for such clocks, and the driver changes start/stop
   behavior accordingly. This was deliberately retained for the faithful
   comparison: it passed previously and is not a newly introduced difference.
   Changing it would be a separate experiment, not an upstream fix in this pass.

Primary source reviewed: IDF 5.5.5 `docs/en/api-reference/peripherals/parlio/parlio_rx.rst`,
`components/esp_driver_parlio/include/driver/parlio_rx.h`,
`components/esp_driver_parlio/src/parlio_rx.c` and `Kconfig`,
`components/esp_hw_support/dma/gdma.c`, `components/esp_mm/esp_cache_msync.c`,
and `components/hal/esp32p4/include/hal/parlio_ll.h`. Local copies are under the
ignored reproduction SDK recorded above; retain the pinned commit when following
these conclusions rather than substituting a newer SDK.

## Ranked explanations and next boundary

Ranked by evidence specific to this comparison, not numerical probability:

1. **Harness/pad timing or signal integrity remains a leading candidate.**
   Receiver source is faithful and current coordination/HDMI are absent, while
   the harness changed materially. Correct source-side data on five observed
   bits does not prove signals at the P4 pads; three data bits were unobserved.
   This review cannot assign a hardware fault or ask for the infeasible second
   probe in an occupied header hole.
2. **Build reproduction remains incomplete.** Flash clock differs; original
   compiler invocation, binary and generated config remain missing. The
   smallest reversible software control is a 40 MHz flash rebuild of the
   existing standalone image, with no other source/config changes, followed by
   one first-profile record using the already approved historical sender.
   Compare both bootloader/application settings and readback, retain the verdict,
   then restore the current full EDP/startup/input as before. This is a proposed
   next experiment, not performed or implicitly authorized by this review.
3. **DMA/cache placement or a shared SDK corner case remains possible.** No
   different relevant driver implementation was found. An allocation-sensitive
   issue could appear on different builds despite the same SDK; original actual
   allocation addresses were not retained. Do not diagnose DMA from the failed
   record alone or start adding unrelated diagnostics.

A passing 40 MHz control would establish build/timing sensitivity, not prove the
flash frequency is the fundamental cause. A failure would narrow that specific
difference while leaving physical timing and missing original configuration open.
If source-faithful controls still fail, discuss a practical short-wire/series-R
comparison or another bounded sampling experiment before any physical change.

No builds, flashes, resets, network tests, SD writes, captures or probe moves
occurred during this offline review. Installed firmware and production selection
remain unchanged. BC01–BC04 are complete; pause for Author discussion.
