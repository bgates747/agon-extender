# Six-bit packing — Nurples results

## Executive summary

Six-bit packing works and is worth retaining as a lossless raw-frame alternative, but it does not improve this Nurples workload. Automatic mode correctly kept RLE2: about39KB/frame versus147KB for six-bit output. Forcing six-bit packing reduced browser output from26.27 to9.92fps. Leave automatic selection enabled for subjective testing; no new Nurples speed improvement is established.

| Variant | Browser submissions fps | Change vs prior | Mean packet bytes | Selected format | Game cycles fps |
|---|---:|---:|---:|---|---:|
| prior | 26.27 | +0.0% | 38806 | EVR1 | 60.00 |
| six | 9.92 | -62.3% | 147492 | EVP1/6bit | 60.00 |
| auto | 27.20 | +3.5% | 38800 | EVR1 | 60.00 |

## Interpretation and limits

1. Prior means the previous RLE2/1–4-bit selection policy on the same new firmware, not a second flash of the older image. Automatic adds six-bit eligibility. Its approximately3.5% output difference is a single-run variation, not an established improvement.
2. All three runs used the unchanged deterministic Nurples fixture, fresh startup, full1800 recorded cycles, the same host/browser and60fps client ceiling. No browser errors or fixture vblank timeout occurred. Game cycles remained60fps on all paths; this is separate from received/presented video.
3. Browser statistics use a20-second interior window ending five seconds before the final capture, excluding startup/asset loading and terminal output. Each fixture run took about45seconds including launch and collection. Headless WebGL submission is not physical monitor scanout.
4. Every measured six-bit-only frame used EVP1 six-bit payloads; every measured prior/automatic frame used EVR1 RLE2. Raw frame size is196640bytes; six-bit is147492 including headers. RLE2 exploits the game’s repeated colours far more effectively.
5. Host validation passed93 exact C++→browser round trips, including all raster geometries and odd six-bit tails;27 malformed packets were rejected. Only Nurples was tested on hardware. No all-mode hardware requalification is claimed.
6. Previous W08 firmware, source overlay, measurements and rollback artifacts remain intact. New source and manifests live in this subdirectory; ignored raw evidence is agents/sixbit. Mainboard firmware and production applications are unchanged.
7. The interactive review uses the existing /test/nurples/nurples.bin two-vblank build, unchanged. Benchmark fixture uses single-vblank pacing to stress output. Refresh the browser to load the new decoder/capability negotiation. Human visual acceptance remains pending.
