# Full-height stock HDMI modes on Olimex

Smith authorized a P4-only offline implementation and build on November 21. The comparison will use the same labelled mode-preview-r02 patterns on Extender v0.3.0 and the candidate. Stop at the completed packet for Smith's review before reserving the Olimex bench.

## Verified starting evidence

The v0.3.0 bundle pins P4 source be1d94329e55cc5e4243adbcdad73e3c530f9053 and build port-008-upload-r05-b2026-11-18-03-43-16Z. Its manifest SHA-256 is e471232f4bfa1551cfa1f518e1d9ad3b6b7fb71d197546c7216ba06ca9376fc9. The retained hdmi_output.cpp compile command enables HDMI, stock runtime and parallel upload. Automatic timing, PPA scaling, rolling scanout, direct RGB888 drawing storage and indexed PPA are absent. The compile database contains no scaler translation unit. The release uses centered native drawing in a fixed 1280×720 RGB888 signal. [Production bundle](../../../production/bundles/olimex-parlio-v0.3.0/bundle.yaml)

| Stock mode | Logical pixels | Release image, black rows per edge | Proposed image, carrier, black columns per edge |
|---|---|---|---|
| 8 | 320×240 | 320×240, 240 | 640×480, 848×480, 104 |
| 20 | 512×384 | 512×384, 168 | 512×384, 684×384, 86 |
| 0 | 640×480 | 640×480, 120 | 640×480, 848×480, 104 |
| 3 | 640×240 | 640×480, 120 | 640×480, 848×480, 104 |

Both target carriers fill the image height, preserving sidebars. Mode 3 repeats each decorated row twice. The existing mode 8 scaler composes a private decorated 320×240 RGB888 input, scales it bilinearly into a distinct panel back buffer and requires DMA acknowledgement before reuse. The ordinary framebuffer publisher already supports this. Neither transformation needs rolling scanout. Current carrier restart uses a core-1 worker compiled only for the alternative direct drawing path. Existing AUTO also exposes experimental modes 96–99. The rolling driver's 1600 µs deadline concerns servicing strips and its recorded wide-clear failures belong to that implementation. Earlier physical tests used full-frame DMA at 848 and rolling at 684. The new pairing needs monitor validation. [Accepted presentation](../../decisions/ADR-0024-centered-unscaled-hdmi.md) · [Runtime results](RUNTIME-RESULTS.md) · [Wide clear](WIDE-CLEAR-REPAIR.md)

The pinned IDF 5.5.5 full-frame driver rearms DMA at frame completion and its deletion path releases the channel and frame storage. Carrier changes need a positive stop before deletion. The existing rolling derivative gates rearming during shutdown. Retire old painters and frame callbacks, establish a stopped channel before freeing either buffer, and exercise late completion and failed initialization.

## Frozen execution contract

- HDMI02-SIZE01a [x] Verify the release flags, hashes and geometry, and locate the packed preview.bin and m000/m008/m020/m003.vdu. All five local files matched their manifest.
- HDMI02-SIZE01b [x] Build an identified experimental image from the pinned release source. Reuse the normal P4 renderer, core-1 carrier lifecycle and private PPA scaler. Keep experimental mode IDs gated. Preserve EMOS, mainboard VDP, PARLIO, startup, physical wiring, production selection and existing scanout guards.
- HDMI02-SIZE01c [x] Verify actual shutdown code, including a pending frame, a delayed stop, and cleanup before first frame. Require evidence that the target compiled and linked the verified shutdown path. Record the boundary between host/target-code evidence and physical observation.
- HDMI02-SIZE01d [x] Prepare matched production/candidate human visual arms, exact firmware, restore extent and fixture pins, read-only status observations, responsive CLI and cleanup criteria. Measure 0→20→0 across both carriers and use mode 3 to check proportions. Stop before reservation. Physical execution, acceptance and release require further direction.

The original production application SHA-256 is 539dc7176f079bc6c298c48352b7e94c54db654fb6fdbb9c42897370fb19834b. The released 1,769,472-byte padded app0 write at 0x20000 hashes to 10d4b60a67888c2363e79ad29adbfd68d58a8638fd9013af413973655cb33ae4. Match the restore extent to the candidate. Keep binaries and private settings in ignored local storage. Finite Pi compile and host checks use the compiler FIFO, up to two build jobs, 80 °C stop and 512 MiB minimum available memory. No physical device or firmware write occurs in this tranche.

## Offline result, November 21

The plan was frozen at `9d2fba40c4ef8f388c8aaf9ee0d0e8e554432afc`. The Pi5 built `hdmi-coverage-r01-b2026-11-21-16-58-59Z` from clean P4 source `21349e0a875042c80762e4665d08effa99350e5c`. The 1,790,480-byte application is 21,856 bytes larger than the release. Its SHA-256 is `a4743d29bccee3e0fbef37761e136cb9404e5b44aa305199ae5e7523e3e7091a`. Both builds use the same compiler, IDF commit, dependency lock, partition bytes and PARLIO configuration. The two effective sdkconfig differences are paths to the same partition layout. The candidate adds automatic carrier selection and the 320×240 scaler to the native full-frame profile. The existing size policy also applies to other stock modes; the four-mode packet qualifies only its specified observations. [Source and artifact pins](SIZE01-RESULT.json)

| Check | Offline result |
|---|---|
| Build and link | The validator passed 1,857 compile actions. It verified the selected full-frame driver objects and scaler in the archive and ELF link. The released and candidate source inventories differ in nine builder, validation and P4 display files. |
| Stop with an active transfer | The core-1 EOF handler sees the drain request, suppresses rearm and acknowledges the last transfer. The worker then reads the owning channel's hardware enable bit. Both conditions must hold before panel deletion. At 100 ms a timeout retains the old panel, buffers, descriptors and scaler, and fails the switch. A panel that never started DMA needs no drain. |
| Target instructions | In the linked ELF cleanup calls the stop at 0x4007b2b6. An error branches at 0x4007b2ba past deletion and scaler reset. Success reaches panel deletion at 0x4007b2c6. The retained driver deletes the channel before freeing its first framebuffer and unregisters its shared interrupt before releasing the peripheral group clock. |
| Modeled event ordering | The host ran the generated EOF gate and production stop function. Delayed hardware idle, missing EOF, missing idle, late callbacks and retry behaved as required. Removing the gate caused the expected failure. The sanitized HDMI lifecycle test retained the exact pending front and back addresses on failed stop and passed ten 848→684→848 round trips, scaler publication and failed-init recovery. |
| Regression and packet | The existing rolling lifecycle, mode 3 row geometry, 22 HDMI builder checks, paired PARLIO boot and 20 upload cases passed. The paired regressions used the release qualification harness with the candidate P4 sources and pinned EMOS ROM sources. The Pi5 compiled one common preview launcher and the commissioned runner accepted both jobs offline. |

The application contains the named Extender build ID. Its embedded ELF SHA-256 matches the disassembled ELF. ESP-IDF separately populated its generic app-version field from the outer build directory’s Git ancestry (`v0.3.0-42-g5d2a19a5-dirty`); the release also carries a generic dirty label. The operator identifies the image by its Extender ID and SHA-256.

The inspection and host tests verify the ordering enforced by the built image. Smith subsequently ran the [matched visual packet](SIZE01-VISUAL.md) and reported a pass. The [physical comparison](SIZE01-BENCH.md) records the observed carriers and scanout. The production selection is v0.3.0.
