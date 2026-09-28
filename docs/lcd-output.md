# Experimental V2 LCD output

The optional LCD build presents EDP output on the Olimex MIPI-LCD2.8-640x480
V2 panel, landscape with its ribbon edge at the left. This is a development
candidate under [LCD-001](tasks/LCD-001.md), not selected production firmware.

Build from clean committed inputs using `scripts/prepare_console.py --lcd
--output <new-directory>`, retaining any other explicitly needed build options.
The ordinary build leaves LCD output disabled. Panel connection and deployment
use the machine-local bench record. The LCD is attached to DSI, not CSI.

EMOS still selects Legacy or ExCom and owns VDU routing. In ExCom, normal output
is rendered by EDP and shown on the LCD without a browser connection. In Legacy,
new ordinary VDU output goes to mainboard VDP; the LCD can retain EDP's last
image. No application changes or new display-switch commands are introduced.

The adapter preserves aspect ratio with nearest-neighbor scaling into640×480,
including exact2× pixels for320×240. Other aspect ratios receive black borders;
large modes are downsampled, so their smallest details may not remain legible.
PPA performs only unit-scale rotation into native480×640 scanout buffers. The
original renderer and sprite/scanline composition are unchanged.

The current two-buffer handoff conservatively waits two DSI completions before
reusing the previous scanout buffer. Its update ceiling is therefore roughly
23fps with the unchanged vendor16MHz timing. Physical panel refresh, application
frame timing and these output updates are different measurements. Simultaneous
browser/LCD output shares snapshot availability and is not performance-qualified.
The previous vendor demo's LVGL CPU/fps counters do not measure this adapter.
