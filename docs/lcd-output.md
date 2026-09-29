# Experimental V2 LCD output

The optional LCD build presents EDP output on the Olimex MIPI-LCD2.8-640x480
V2 panel, landscape with its ribbon edge at the left. This is a development
candidate under [LCD-001](tasks/LCD-001.md), not selected production firmware.

BUILD-001 deliberately excludes this experimental implementation from the
native pre-LCD audit baseline. There is currently no maintained LCD build
profile. LCD-001 must reintroduce the implementation after AUDIT-010 as a
separately reviewed delta and add a native profile before another build. Do not
reuse the historical `prepare_console.py --lcd` command. Panel connection and
deployment use the machine-local bench record. The LCD is attached to DSI, not
CSI.

EMOS still selects Legacy or ExCom and owns VDU routing. In ExCom, normal output
is rendered by EDP and shown on the LCD without a browser connection. In Legacy,
new ordinary VDU output goes to mainboard VDP; the LCD can retain EDP's last
image. No application changes or new display-switch commands are introduced.

The adapter preserves aspect ratio with nearest-neighbor scaling into640×480,
including exact2× pixels for320×240. Other aspect ratios receive black borders;
large modes are downsampled, so their smallest details may not remain legible.
PPA performs only unit-scale rotation into native480×640 scanout buffers. The
original renderer and sprite/scanline composition are unchanged.

The tested rev1.3 P4/V2 panel requires native horizontal HBP/HFP19/11 at the
vendor16MHz pixel clock, retaining htotal514 and active width480. Use ordinary
documented RGB888 memory order B,G,R; do not apply the earlier experimental
R,B,G channel compensation. The Author confirms matching Legacy and ExCom LCD
colors and all four one-pixel edges in the mode0 asymmetric fixture with this
combination. This is bounded candidate evidence, not application/gameplay or
production qualification.

The current two-buffer handoff conservatively waits two DSI completions before
reusing the previous scanout buffer. Its update ceiling is therefore roughly
23fps with the unchanged vendor16MHz timing. Physical panel refresh, application
frame timing and these output updates are different measurements. Simultaneous
browser/LCD output shares snapshot availability and is not performance-qualified.
The previous vendor demo's LVGL CPU/fps counters do not measure this adapter.

LCD-001 owns adapting the paired game/performance package used for the earlier
Ethernet/browser work. Its baseline must separate renderer work, snapshot
pressure, RGB expansion, PPA rotation, DSI handoff/completion and physical panel
presentation. Measure LCD-only before simultaneous browser output. The retained
runner is currently reuse-blocked pending BENCH-007 procedure refresh; do not
rerun its historical batch unchanged.
