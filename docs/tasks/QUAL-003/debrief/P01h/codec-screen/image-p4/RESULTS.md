# RGB888 hardware JPEG and indexed PNG — physical assessment

## Executive summary

**Keep RLE2 for live Nurples streaming. Hardware JPEG from RGB888 is slower and
larger on this pixel-art workload; this first indexed-PNG implementation saves
bytes but spends too long encoding them. Neither is a replacement candidate.**
This is a conclusion about the tested implementations and workload, not a claim
that JPEG hardware or PNG is universally unsuitable.

JPEG90/YUV444 completed three clean-start runs at5.94–6.66 browser-received fps,
mean6.26, against paired RLE2 at12.77–13.80fps, mean13.22: **52.6% slower**.
PNG's smaller output did not offset software encoding on Nurples:

| Encoder | Received fps | Paired RLE2 fps | Difference | Mean wire bytes/frame |
|---|---:|---:|---:|---:|
| JPEG90 / RGB888 / 4:4:4 | 6.26 | 13.22 | −52.6% | 119,201 |
| Indexed PNG level1 | 6.71 | 13.65 | −50.8% | 23,344 |
| Indexed PNG level3 | 6.37 | 13.65 | −53.4% | 21,725 |

RLE2 transmitted about37.6–37.7KB/frame. JPEG added14.33ms source validation/
expansion plus4.80ms hardware encoding per attempt; PNG added5.4–5.5ms validation
plus79–81ms encoding. RLE2 encoding averaged6.3–6.4ms. Timing scopes differ from
the central-window FPS; [full tables](TABLES.md) also include browser decode/parse.

**One content-specific exception:** the frozen periodic pattern that defeats
RLE2 delivered9.51–10.01fps with PNG versus6.66fps with RLE2/raw fallback,
a43–50% improvement. It is not random noise and not the Nurples game. This
supports retaining PNG as an experimental option, not enabling it globally.

All15 principal game trials completed1800 application cycles with no VDU fault
or browser/encoder failure; all12 static conditions passed. The earlier PNG
network interruption remains a qualification limit. Do not substitute historical
task baselines or excluded stale-background trials for these paired controls.

## What was measured

1. P4 revision1.3,360MHz CPU,200MHz PSRAM, IDF5.5.5. One image owns unchanged
   RLE2 controls, official hardware JPEG, PNGenc and native browser image decode.
   No graphics algorithm, task priority, affinity, EMOS or stock VDP change.
2. Source is final00BBGGRR at512×384. JPEG conversion expands to exact8-bit
   channel levels0/85/170/255 in the driver's BGR-byte layout. RGB565 excluded.
   JPEG uses4:4:4: no chroma subsampling, but quantisation remains lossy.
3. Each principal game trial reapplies identical mode20 startup by mainboard
   reset; unchanged deterministic cadence fixture runs1800 application cycles.
   Browser output retains30Hz request ceiling. Receipt/submission rates are not
   proof of distinct fully rendered physical frames at those rates.
4. Browser host uses Wi-Fi to reach the wired P4. Comparisons use the same route,
   host/browser and interleaved controls, not a claim about pure Ethernet limits.
5. JPEG qualities80/90/95 were screened on13 cases; quality90 selected for game
   runs. PNG levels1/3 were screened on13 cases and both carried forward.
   Native ImageBitmap uploads avoid per-frame canvas readback during gameplay.
6. Encoder counters cover whole invocation; browser table uses central15 seconds
   ending5 seconds before final receipt. Screenshot instants differ; gameplay
   images are visual evidence, not identical-frame pixel-diff pairs.

## Fidelity and encoding cost

All39 JPEG case/quality combinations decoded successfully. The64 solid colour
patches at quality90 differed by at most2 values per channel, verifying correct
colour order. JPEG is not exact: the synthetic sprite scene had maximum error45
and mean absolute error0.533 at quality90; captured sparse sprites max21 and
mean0.066. Large black regions make mean error look better than edge fidelity.

All26 PNG case/settings combinations decoded pixel-exactly in the browser.
Malformed geometry, length, unsupported setting and illegal source colour were
rejected, with a healthy request afterward. All retained original/reference and
decoded images remain in private evidence, with selected review images here.

For a full-size captured sparse sprite frame, JPEG90 used13.686ms validation/
expansion plus4.685ms hardware-driver elapsed time, producing9,913 bytes. PNG
level3 used58.903ms encoding and produced2,562 bytes. Pure encoding measurements
exclude upload, browser decode and rendering; neither predicts game FPS alone.

PNGenc keeps its embedded MEM_SHRINK3 settings and preallocated workspace in
PSRAM. It is not the desktop zlib implementation from the earlier screening.
Internal-SRAM workspace may be a useful separate experiment; it was not tested
and is not an established fix. Official ESP-VISION's PNG entry point wraps
OpenMV-derived LodePNG, not dedicated PNG hardware. See RESEARCH.md.

## Exclusions and reliability limits

1. Initial candidate exhausted HTTP handler slots; add exactly two slots and
   rebuild before performance testing. No renderer/scheduler change.
2. A host import collision invalidated the first game attempt. Reused MOS SAVE
   names invalidated the next, because SAVE uses FA_CREATE_NEW. Final controllers
   preload standard Python modules and use unique phase/attempt file names.
3. Visual inspection found stale completion text and absent bezel regions when
   reusing application/display state. Partial game04 results are excluded. The
   principal game05 series resets startup for every trial, and representative
   screenshots show the restored bezel. Compression must compare comparable
   source content; altered backgrounds can materially change results.
4. Initial JPEG RPC screening encountered an unclassified HTTP400; a direct
   repeat passed, and remaining checks completed. Error bodies are now retained.
5. PNG RPC screening lost network access after13 successful rows. Serial opening
   subsequently observed boot but may itself reset P4; cause is unresolved.
   One clean-start resume completed the remaining checks. This is not a proven
   codec defect or a claim of production stability. Preserve the interruption.

## Practical decision

Keep the code and evidence, not an automatic production switch. RGB888 hardware
JPEG remains reusable for future native true-colour or photographic workloads;
those have not been benchmarked here. PNG is exact and can be encoded beforehand
for assets, but these measurements do not justify this live encoder replacing
RLE2. Pre-encoded AGM playback has a different cost model and is outside this run.

Source provenance, driver details and experimental wire contract: RESEARCH.md.
Reproduction: REPRODUCE.md. Full private artifacts: agents/image-p4. No experimental
firmware is to be promoted or pushed by this task. Restoration and voice receipt
are recorded below at closeout.

## Review images

Browser screenshots are CSS-scaled and taken at different gameplay instants:
[RLE2](images/nurples-rle2.png), [JPEG90](images/nurples-jpeg90.png),
[PNG1](images/nurples-png1.png). For identical-source fidelity inspection:
[reference](images/sprite-reference.png), [JPEG90](images/sprite-jpeg90.png),
[exact PNG3](images/sprite-png3.png). Human visual acceptance remains separate.

## Restoration and attention receipt

Exact original r43 P4 prefix was independently verified after restoration:
SHA256 `22d22c530d643ac2896aa624eba802eb8b3c0ad695f2f6425036d3f130f50604`.
Original48-byte startup restored/read back, SHA256
`c4407c0c0e7c7a14dc330c3ddb9ce3f6ef509f03e08ff896a71719ea5ed9549f`.
EMOS and stock mainboard VDP unchanged; host MOS-suite card untouched.
Experimental before-prefix retained, including diagnostic partition.

British female hardware voice returned a fresh stage6/audio_commands=pass
receipt. Human hearing is not assumed. Final state: Legacy MOS prompt, keyboard
ready/neutral, SD service exited. See evidence/restored-final.json and
notification-final.json. Bench released for Author review; no promotion or push.
