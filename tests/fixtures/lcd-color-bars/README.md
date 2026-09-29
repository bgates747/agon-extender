# Asymmetric mode 0 color and edge fixture

This static fixture checks mode 0 color ordering, orientation and all four
source edges. `/autoexec.txt` must issue `VDU 22 0` before launch. The fixture
does not switch modes; its first VDU byte clears the graphics screen.

Run `make` to regenerate `bars.vdu` and assemble `bars.asm` as `bars.bin`.
Deploy the verified executable beneath `/extender/fixtures`; loading it does not
run it. The fixture waits for Escape and returns to MOS.

Expected source layout is black, red, green, blue, cyan, magenta, yellow and
white from left to right. The one-pixel edges are white at top, red at left,
blue at right and magenta at bottom. Corner keys are white at upper left,
yellow at upper right, cyan at lower left and magenta at lower right. The labels
and edge keys deliberately distinguish palette errors, mirroring, clipping and
one-pixel wraparound.

The mode 0 source surface is 640 by 480. An output-specific scaler may apply a
separately documented presentation transform, but this fixture contains no LCD
policy and does not establish animation, sprites or Copper behavior.
