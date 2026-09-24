# Bounded VDU frame marker

PORT-003 video-throughput experimental fixture. Select mode 8 only in
`/autoexec.txt` before invocation (`VDU 22 8`); the program never selects a mode.
Prepare `/extender/video-marker` for the executable and
`/agents/extender/results/video-marker` for receipts during an authorized
deployment. After the chosen display route is ready, invoke at an admitted CLI:

```text
CD /agents/extender/results/video-marker
LOAD /extender/video-marker/vidmark.bin
RUN
```

These paths describe a newly prepared test, not the installed card. Preserve
previous receipts before reuse. Build with
`make -C examples/video-marker AGONDEV_TOOLCHAIN=/path/to/agondev`.

For20seconds, the app targets one update each two raw MOS120Hz ticks. It shows
the low8bits of the Gray-coded target frame at x16+16*bit, y32..43, and its
complement at y56..67. Only changed bits are redrawn using ordinary filled
rectangles. It records elapsed ticks, submitted updates, skipped target intervals,
VDU bytes and last target frame to VIDMARK.CSV after output stops, then returns.
No fixture counters/fences/private callbacks are sent during drawing.

The independent browser observer samples code cells at x22+16*bit,y38 and62.
White is RGB222 value63, black0. Mismatched code/complement indicates a snapshot
which crossed a marker update; report it separately, without silently repairing
stock rolling/single-buffer behavior. Sequence gaps show observed frame progress,
not packet loss or proof of VDP scanout timing. The raw MOS target is mainboard
time in ExCom, not a measurement of the P4 renderer's completed frames.

The loop is finite if ordinary MOS output returns. Inherited blocking UART/CTS
can prevent its own timeout; host observation/recovery must remain bounded.
Preserve the normal SD-service startup and remote keyboard/Pi-reset recovery.
This is a local experiment pending review, not a published utility or speed claim.
