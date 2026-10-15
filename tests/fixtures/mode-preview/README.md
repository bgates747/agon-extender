# Interactive mode preview

Candidate HDMI-004 r02, built by `build.py` with the project Python. Source
rasters must first exist under the ignored display-pattern working directory.
The generated package belongs at `/extender/mode-preview-r02` on the mainboard SD.

From MOS CLI:

    LOAD /extender/mode-preview-r02/preview.bin
    RUN

The program asks EMOS to activate ExCom, displays the mode list in mode 0,
and accepts a decimal mode number followed by Enter. Wait for the pattern to
finish loading before reviewing or pressing a key. Escape returns to the menu;
Escape at the menu returns to Legacy mode 0. Startup is never modified.
The Author explicitly requested runtime mode selection for this visual fixture.

For a black or unusable picture, wait for upload then press Escape to recover the
mode-0 menu. If execution has returned to CLI but routing/picture is unusable,
use `EMOS LEGACY`. An application hang requires the normal bench reset protocol;
this fixture has no automatic reset or retry.

The mainboard streams 4 KiB chunks from the SD card. The P4 assembles an opaque
RGBA2222 bitmap, receives colours already quantized to the selected mode defaults, plots, and swaps
if double-buffered. Standard modes receive the 4:3 interior; the physical HDMI
carrier supplies its pillars. Experimental 96–99 receive the wide pattern.
Mode 7 uses a separate text-only control. The menu lists selectable IDs, including
modes whose current HDMI timing/cropping may fail Author visual review. It does
not verify selected mode readback or record results; the Author reports those.

No firmware is installed by this build or launch. No measured FPS, motion,
flicker or performance acceptance follows from this static visual check.

All drawing pixels use nearest RGB matching against agon_palette.h defaults,
without dithering. This includes swatches, text, backgrounds and antialiasing.
The source swatch indices retain their original RGB222 identities after mapping.

For UART deployment, run `compress_package.py` after `build.py`. It builds a
host adapter around the maintained VDP TurboVega codec, roundtrips every bitmap,
and replaces buffer consolidation with public buffer-decompression command 65.
The command expands in place before the unchanged bitmap-create/plot commands.
Generated compressed package: ignored display-pattern/fixture-r02-packed.
Compression changes storage and upload size; decoded drawing pixels are identical.

Escape-only revision: all other preview characters, including Tab, are ignored.
Escape at the menu still exits the application.
