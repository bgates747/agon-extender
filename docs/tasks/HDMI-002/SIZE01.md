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
- HDMI02-SIZE01b [ ] Build an identified experimental image from the pinned release source. Reuse the normal P4 renderer, core-1 carrier lifecycle and private PPA scaler. Keep experimental mode IDs gated. Preserve EMOS, mainboard VDP, PARLIO, startup, physical wiring, production selection and existing scanout guards.
- HDMI02-SIZE01c [ ] Verify actual shutdown code, including a pending frame, a delayed stop, and cleanup before first frame. Require evidence that the target compiled and linked the verified shutdown path. Record the boundary between host/target-code evidence and physical observation.
- HDMI02-SIZE01d [ ] Prepare matched production/candidate human visual arms, exact firmware, restore extent and fixture pins, read-only status observations, responsive CLI and cleanup criteria. Measure 0→20→0 across both carriers and use mode 3 to check proportions. Stop before reservation. Physical execution, acceptance and release require further direction.

The original production application SHA-256 is 539dc7176f079bc6c298c48352b7e94c54db654fb6fdbb9c42897370fb19834b. The released 1,769,472-byte padded app0 write at 0x20000 hashes to 10d4b60a67888c2363e79ad29adbfd68d58a8638fd9013af413973655cb33ae4. Match the restore extent to the candidate. Keep binaries and private settings in ignored local storage. Finite Pi compile and host checks use the compiler FIFO, up to two build jobs, 80 °C stop and 512 MiB minimum available memory. No physical device or firmware write occurs in this tranche.
