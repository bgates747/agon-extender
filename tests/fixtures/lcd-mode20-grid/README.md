# LCD mode 20 static grid

This diagnostic isolates clean-start mode 20 allocation and static presentation
from Nurples assets and animation. The official mode contract is512×384 with64
colours. The fixture draws an8×6 native-pixel grid, labels cells A1 through H6,
marks every edge and waits for Escape.

The fixture application deliberately requests mode20 itself immediately before
drawing. `/autoexec.txt` remains the Author's admission-only configuration and
must not select the test mode. Run `make` to generate `grid.vdu` and assemble
`grid.asm` as `grid.bin`, then deploy the verified binary beneath
`/extender/fixtures`. Loading the executable does not run it.

Expected LCD presentation is a centered512×384 image with64-pixel pillarboxes
and48-pixel letterboxes. Cell A1 is at the upper left and H6 at the lower right.
The outer edges are white at top, red at left, blue at right and magenta at
bottom. The small corner blocks are yellow at upper left, cyan at upper right,
green at lower left and white at lower right.

This fixture tests one otherwise clean application-owned mode switch. It does
not test VDP asset pressure, animation, buffer swaps, sprites or Copper effects.
