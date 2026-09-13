# Ordinary palette and colour-depth coverage — 2026-09-13

This PORT-008 slice compares visible palette and bitmap behavior in single-
buffer modes8/9/10/11 (64/16/4/2 colours, all320×240). It uses ordinary MOS
EXEC/VDU input and the unchanged installed P4 candidate. It does not change
upstream painting algorithms, firmware, timing hooks or the held QUAL-003 plan.
All experiments remain local for the Author's visual and publication review.

## Bounded plan

1. [x] P008-P01: Read official Screen-Modes.md, VDU-Commands.md palette/GCOL
   sections and Bitmaps-API.md, and inspect retained palette/depth selection.
   Define separate expectations for indexed and direct-colour output.
2. [x] P008-P02: Generate one finite command case per colour depth, with
   explicit synthetic pixels and palettes. Cover ordinary graphics, RGBA8888,
   RGBA2222, byte-aligned mono, inclusive capture, and later palette mutation.
   Select modes outside scripts and keep complete MOS lines below256 bytes.
3. [x] P008-P03: Execute each exact input headlessly through canonical stock
   profiles. Check ideal pixels and untouched halos, retaining informative
   discrepancies. No timing or full mode qualification follows.
4. [x] P008-P04: Transfer exact scripts via sdserve and invoke sequentially
   through EMOS ExCom. Compare P4 pixels, restore the palette/Legacy CLI, and
   verify unchanged startup/input readback and released keyboard admission.
5. [x] P008-P05: Record mode-specific results and remaining scope. Any port
   defect gets a separate bounded diagnosis before repair. Keep review gates.

## Source précis

Official reference commits remain VDP2.16.0
c7ac293d2aa81ddfa693390549bcd909069c8fc3, MOS3.0.2
8336409351ee5314e02801a7b72a4f1bb5282519 and documentation
f9806bd3cbff6ed5d1c08bef1d51fed11764b86b. Official checkouts are read-only.
Relevant source is agon_screen.h (mode/palette selection), agon_palette.h,
retained VGAPalettedController and the separate 2/4/16/64-colour controllers.
The active P4 path is StockRuntimeController/StockBoundController, which binds
the retained depth controllers; do not diagnose it from the superseded custom
P4DisplayController merely because that source still exists.

1. VDU19 maps logical to physical colour; physical255 selects supplied RGB,
   physical0..63 selects RRGGBB, and64..254 must be ignored while consuming
   their RGB parameters. VDU20 resets the palette and painting defaults.
2. In64-colour modes, redefining the palette affects future drawing only.
   Indexed2/4/16-colour surfaces store indices, so changing the selected entry
   changes already drawn pixels. These require different independent oracles.
3. Bitmap RGB input is mapped to the destination palette. Keep exact palette
   colours and unambiguous nearest-colour samples; avoid ties or duplicate
   entries masquerading as transport defects. Alpha zero stays transparent;
   nonzero alpha is opaque. Mono colour is captured at creation time.
4. Palette index lookup and already-selected graphics colour are related but
   distinct; explicitly reselect a logical colour for the post-mutation tile.
   Do not let palette cleanup erase the observation before the host captures
   it. Recovery commands restore defaults after evidence collection.
5. The input never changes modes itself. Each native startup/EMOS invocation
   selects its mode before EXEC. Assertions require actual capture geometry,
   not a filename label. This single-buffer slice does not qualify swaps,
   Copper palettes, mode7, scanout cadence or bitmap deletion while drawing.

Retain task-local generated scripts/oracles and captures under ignored agents/
paths, with exact input/runtime identities. Private hardware access, installed
candidate, rollback and admission remain in HARDWARE.local.md. The prior bitmap
checker's strict image decoder and explicit pixel/halo checks are reused; no
third-party artwork is required.

The generator defines nine tiles per depth, with 539 checked pixels including
halos. Palettes are explicit: black0, white1, remaining entries are distinct
RRGGBB values in indexed modes. Bitmap blue is exact where the palette has it;
in the two-colour black/white mode the initial RGB-distance assumption predicted
black. Stock instead uses HSV distance and maps it white, as established below. Alpha-zero
pixels carry magenta RGB and draw over white, while opaque-black pixels must
overwrite that backdrop. A nine-pixel monochrome mask exercises byte-aligned
rows and creation-time colour. Readback capture, XOR erasure and invalid
physical-colour rejection provide additional selected command checks.

After drawing, physical-colour form48 remaps logical1 to red. Indexed pixels
already drawn with entry1 must become red; mode8 must retain their white RGB.
The completion prompt leaves this palette in place for capture. Recovery
restores defaults explicitly afterward, rather than silently changing the
observation before the host reads it. Native comparison is next.

## Stock result and corrected colour-distance assumption

The64/16/4-colour inputs pass all nine ideal tiles. The2-colour case initially
differs in nine pixels across the two RGBA tiles and their captured copy: blue
became palette1/white, later red, rather than the predicted palette0/black.
Inspection of retained vdp-gl VGAPalettedController::updateRGB2PaletteLUT shows
that distance is computed in HSV, not RGB. Against black and white, both have
equal hue/saturation differences from blue, while blue shares white's value.
Thus white is the intended retained result. The documentation does not promise
Euclidean RGB distance. This is a test-specification assumption, not a port
defect or justification for changing the upstream colour algorithm.

The initial case01 oracle and nine-pixel failure remain preserved. The corrected
generator uses a literal white expectation for blue only at depth2, then the
documented later palette remap changes it to red. Case02 changes the oracle,
not the command bytes; equality with the exact natively executed input must be
verified before reusing that reference capture. This is distinct from ignoring
a pixel difference or introducing a stock-parity-only acceptance exception.

The corrected depth2 oracle passes all nine tiles against the original capture;
an explicit byte-equality record binds it to the unchanged natively executed
script. All four depths now pass their specified independent pixel expectations.
No emulator/renderer source changed. The actual-generator hashes and first
failed assumption remain in the preserved case manifests, rather than replacing
historical files with current generated derivatives.

## Physical result and scope closure

All four depths independently pass all nine specified tiles on P4: 36 tile
comparisons and 2,156 logical pixels including halos. The native/P4 observations
confirm both indexed recolouring and retained direct-colour pixels. This is
ordinary mode8/9/10/11 output, not a custom renderer approximation. No drawing,
palette, decoder or firmware change was needed for these cases. The retained
upstream controller baseline is vdp-gl all-the-plots at
ac2dd5986daf496c43ae8e7fe41836274aec54a0, recorded in PORT-003's R1 source binding.

| Mode | Colours | Script bytes | Script SHA256 |
| --- | --- | --- | --- |
| 8 | 64 | 3015 | beb7e33235b4b3ca907e38d026fceb249dadbe339c3fb23035999d8b987f4386 |
| 9 | 16 | 2055 | 5def3f42fbc3e97c1b4caa07734c652504c6a45607c5af53acf390c418fde414 |
| 10 | 4 | 1826 | 9b79e80ddca1fa235001057896f5ed5693387932a8e2bf01f2d2c1c660927fbb |
| 11 | 2 | 1790 | 636dfe23795395e891f6ada765babe73ef616e385aae54fd2c5688eecf1c884a |

Generated input/oracle, native results and their exact PNG hashes live under
ignored agents/palette-coverage. Physical EVF bytes, decoded PNGs, checker
results and browser observations are in its p4-depth*-case01 directories.
The four native profiles/captures are isolated under .emulator and
agents/video-throughput. The corrected generator reproduces the original
64/16/4 command bytes and pixel expectations exactly; its depth2 case02 retains
identical commands with the explicitly corrected HSV expectation. Historical
case01 and source hashes remain unchanged.

The four five-second physical observations retain 295/298/300/302 snapshots,
all 320×240, with no sequence gaps. They show static output; snapshot delivery
does not measure drawing throughput or physical scanout. No timing comparison
with earlier performance runs is made.

Each exact input passes staged and active SD readback before execution. After
capture, VDU20 restores the ExCom palette, ordinary EMOS returns to Legacy and
selects mode3, then sdserve independently reads back unchanged startup and all
four scripts. The service exits with no pending request. A final read-only
keyboard check proves the same owned canceled session is ready, neutral and
released under the same boot. Observers are closed, and no reset, flash,
accepted product/startup edit or publication occurred. Exact installed candidate
identity and foreground remain in HARDWARE.local.md.

P008-P01–P05 are machine-complete. This does not qualify all palette colours,
quantisation ties, Copper/secondary palettes, every graphics mode, swaps,
mode7, all sprite/bitmap combinations, query returns or sustained throughput.
Author visual/commit review and general command qualification remain open.

Reproduction from the Extender root:

```text
.venv/bin/python docs/tasks/PORT-008/palette-coverage/make_case.py agents/palette-coverage/new-case --depth 2
.venv/bin/python docs/tasks/PORT-008/bitmap-coverage/check_pixels.py agents/palette-coverage/new-case/oracle.json <capture.png-or-evf> --output <result.json>
```

Depth may be2/4/16/64; select its mode11/10/9/8 outside the generated script.
EXEC palette.txt, capture before restoring the palette, then issue VDU20 in
ordinary CLI recovery. Bind fresh input/runtime evidence and preserve these
historical observations.
