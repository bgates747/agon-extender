# Stock communication traces — forward command stream

[AUDIT-004](../AUDIT-004.md), W3, 2026-09-07. Covers AUDIT-004-P001 through
AUDIT-004-P005 at the [fixed stock identities](baseline-and-research-map.md).
The official [VDP overview][D-VDP], [VDU commands][D-VDU], and family documents
were read before following their implementations. This is a family-level
communication trace; it does not claim that every rendering opcode or malformed
operand has been exhaustively reviewed. The [W4 coverage review](coverage-review.md)
records the reconciliation and its limits.

## Shared forward contract

1. The eZ80 application or MOS command handler generates VDU bytes. MOS's
   RST 10h/18h handlers and C `_putch` wrapper call `UART0_serial_PUTCH`;
   the [MOS interface trace](trace-mos-interfaces.md)
   records those call boundaries. MOS does not add an overall command length,
   transaction ID, checksum, or acknowledgement wrapper. The onboard UART
   carries the resulting stream using the configuration and pacing in the
   [primary protocol trace](trace-primary-protocol.md). Splitting one command
   over multiple calls does not create multiple commands; the VDP parses bytes
   by opcode and operand grammar. [D-VDP], [M-VEC], [M-SER]
2. VDP `setup` creates one main `VDUStreamProcessor` over `VDPSerial` and a
   `processLoop` task pinned to core 0. After startup synchronization,
   `processLoop` calls `processNext` unless terminal mode owns processing.
   `processNext` handles queued events, keyboard/mouse, cursor and frame state,
   then dispatches the next available command in the active state. A command
   handler synchronously consumes its operands before returning to that loop.
   UART reception and graphics/audio library work have their own contexts;
   they are not all executed by the command loop. [V-MAIN], [V-STREAM]
3. `readByte_t` polls with a configured default of `COMMS_TIMEOUT=200` ms;
   `readWord_t` and `read24_t` assemble little-endian values through separate
   byte reads. A timeout yields `-1`; many handlers return immediately.
   `readIntoBuffer` instead uses the input stream's `readBytes` timeout and
   retries a zero-length read once. Its own `timeout` argument is not applied
   inside that function. These are configured code paths, not one global
   200 ms command deadline. The authenticated Arduino wrapper semantics are
   recorded in the primary trace. [V-CONFIG], [V-STREAM]
4. There is no common command rollback, error packet, or resynchronization
   delimiter. After an operand timeout, later bytes can be interpreted as new
   command bytes; already executed effects remain. Unknown or disabled command
   branches do not know a generic length to discard. This is a consequence of
   the selected parser structure, not a measured corruption rate. Particular
   commands may emit query results or mode notifications described separately.
   [V-VDU], [V-SYS]
5. `processNext` can pause command dispatch for frame waits, paged output, or
   Ctrl-Shift while continuing its outer-loop services. A long buffer execution
   or synchronous operand/library wait does not return to those services until
   it finishes. `processAllAvailable`, used by stored command execution, runs
   its own loop and deliberately does not process the event queue. No universal
   bound on command-loop latency follows. [V-STREAM], [V-CONTEXT-STATE]

## AUDIT-004-P001 — text and ordinary VDU drawing

MOS forwards application/CLI bytes through T001. VDP `vdu` dispatches control
characters to cursor, colour, viewport, mode, and plot handlers, and printable
characters to `vdu_print`. `vdu_print` may collect adjacent printable bytes;
`Context::plotString` selects the active text/graphics state and submits font
characters or mapped bitmaps to the canvas. Teletext instead calls its own
`draw_char` path. `vdu_plot` reads the plot selector and two little-endian
coordinates, then calls `Context::plot`. The resulting effect is display state
or drawing work; normal text/plot commands have no generic reverse ACK.
[V-VDU], [V-GRAPHICS], [L-CANVAS]

Canvas primitives can execute immediately or be queued according to the
display controller's background/double-buffer state. Its queue insertion and
buffer-swap notification waits use `portMAX_DELAY`. MOS returning from a byte
write therefore does not prove that pixels have appeared. Certain ordinary
VDU operations also emit P010 mode information, including cursor-type and
viewport changes. P005 records explicit drawing coordination. [L-DISPLAY],
[V-VDU]

VDU 21 disables the normal command dispatcher until VDU 6; the disabled branch
still handles the printer escape. Printer/console side effects use T004 and
are traced as X009/X010. Screen mode changes reinitialize relevant display
state and send mode information; they are not an application-wide reset of
all VDP resources. [V-VDU], [V-SCREEN]

## AUDIT-004-P002 — bitmap, sprite, and font resources

The sender uses VDU 23,27 selectors or the system font commands; VDP dispatches
to `vdu_sys_sprites`/`vdu_sys_font`. For streamed RGBA8888 bitmaps, width and
height determine a `4 * width * height` data count. `receiveBitmap` clears the
old buffer, receives data through P004's `bufferWrite`, then builds the bitmap.
The receive failure path does not restore the old resource. Creation from an
existing buffer requires a single block and an exact format-dependent byte
count. Buffer existence/size failures return locally without a dedicated MOS
error packet. [D-BITMAP], [V-SPRITES]

Sprite operations select frames, visibility, position and refresh; their
observable results reach the canvas/display controller. Font operations create
metadata over stored buffers, change active fonts, or update the system font.
Some font operations send P010 mode information because text dimensions can
change. This notification is not a universal resource-upload status. The
selected font source explicitly leaves naming/selection-by-name branches
unimplemented, so family membership must not imply all proposed subcommands
work. [D-FONT], [V-FONTS], [V-SPRITE-STATE]

Resource lifetimes are VDP-owned: buffers can outlive an eZ80 application;
clear/reset calls remove associated bitmap/font/sample users. A new application
cannot infer empty VDP storage from its own launch. Partial transfers, resource
allocation failure and missing resources have command-specific handling, with
no common replay guarantee. [D-BUFFER], [V-BUFFER]

## AUDIT-004-P003 — contexts, transforms, tiles and Copper

These use the same MOS byte output and VDP system dispatcher. Context commands
under `&C8` select/copy a stack, save/restore it, or reset selected drawing
state. `selectContext` creates or activates the stored context; commands that
affect reported text state emit P010 mode information. Missing/active-context
deletion and an empty restore history have local no-op paths. [D-CONTEXT],
[V-CONTEXT]

Affine-transform (`&96`), tile (`&C2`) and Copper (`&C4`) dispatch is conditional
on VDP variables. In the selected source a disabled feature returns before
consuming its remaining operands, so sending its full command without enabling
it can leave operand bytes to enter the main VDU dispatcher. The tile handler
contains reserved/no-op cases and several unchecked conversions of timed-read
results to byte operands. The trace establishes the active branch and its
communication limits; it does not certify arbitrary tile input. [D-TILE],
[V-SYS], [V-LAYERS]

Copper commands create/update palettes or pass the first block of a stored
buffer to `updateSignalList` as pairs of little-endian 16-bit values. The screen
wrapper applies these only to palette-based modes; vdp-gl owns the scanout
effect. Affine transforms reference a stored matrix used by bitmap drawing;
tile commands update VDP-owned bank/map/layer buffers and draw through their
helpers. These are local display effects, with no dedicated reverse packet
family. Mode, feature-variable, resource, and display-library dependencies
remain part of the contract. [D-COPPER], [V-SYS], [V-SCREEN], [V-GRAPHICS],
[V-LAYERS]

## AUDIT-004-P004 — buffered data and command execution

The sender writes `23,0,&A0,bufferId(low),bufferId(high),command,...`.
For command 0, a 16-bit length precedes the block bytes. VDP `bufferWrite`
stores the block only after all requested bytes arrive, appending to that ID's
existing blocks. A short transfer discards the new partial block; reserved
ID 65535 consumes but does not store the data. The dispatcher ignores the
helper's return count and sends no upload result. Clear/create/adjust/copy and
other operations act on the same VDP-owned storage. [D-BUFFER], [V-BUFFER]

For call/jump commands the VDP switches its input from the UART or current
stored stream to a `MultiBufferStream`, then uses the same VDU parser. The
ordinary cross-buffer call branch restores its saved stream/offset and output
route. Same-buffer recursion restores only the input position; an exhausted
stored-input call becomes a jump. Jumps replace the stored input, with top-level
UART jumps implemented as calls. Thus output-route restoration is branch-specific,
not a universal property of every call. Missing buffers return
locally. Stored commands can themselves send ordinary query responses through
the current output stream or enter further calls/jumps. Buffer code is not an
eZ80 execution context or shared memory region. [V-BUFFER], [V-STREAM]

There is no generic success ACK, cancellation deadline, or guaranteed return
for a self-looping stored program. Event callbacks can execute buffers too;
P017 records their ordering, response modification/suppression, and output
redirection. In particular, execution from stored input can generate traffic
without a fresh eZ80 command for each response. [D-BUFFER], [V-BUFFER]

## AUDIT-004-P005 — drawing completion and buffer swap

For `23,0,&CA`, VDP calls `waitPlotCompletion(false)` and then
`Canvas::waitCompletion(false)`, which asks the display controller to process
pending primitives immediately. For `23,0,&C3`, `switchBuffer` enqueues a swap
in a double-buffered mode, or enqueues a no-op and waits on background queue
processing otherwise. The double-buffered swap path waits for its executor's
task notification. No dedicated completion packet is sent to MOS. [D-SYS],
[V-SYS], [V-SCREEN], [L-CANVAS], [L-DISPLAY]

Documentation describes the swap as synchronized to VSync. The source proves
the selected queue, processing, and notification paths; `primitivesExecutionWait`
itself observes queue occupancy when background execution is enabled. It does
not measure monitor presentation or impose a timeout. This local drawing
coordination is distinct from the physical VSync edge delivered to the eZ80
on T002/P024, traced in the VDP and board records. Neither operation is a
generic transport barrier with a transaction-correlated acknowledgement.

[D-VDP]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/VDP.md
[D-VDU]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/VDU-Commands.md
[D-SYS]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#L436-L448
[D-BUFFER]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Buffered-Commands-API.md
[D-BITMAP]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Bitmaps-API.md
[D-FONT]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Font-API.md
[D-CONTEXT]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Context-Management-API.md
[D-COPPER]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Copper-API.md
[D-TILE]: https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Tile-Engine.md
[M-VEC]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/vectors16.asm#L112-L160
[M-SER]: https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/serial.asm
[V-MAIN]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/video.ino#L98-L156
[V-STREAM]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h
[V-CONFIG]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon.h
[V-VDU]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu.h
[V-SYS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h
[V-CONTEXT-STATE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context.h#L1312-L1336
[V-GRAPHICS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context/graphics.h#L650-L937
[V-SPRITES]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sprites.h
[V-SPRITE-STATE]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/sprites.h#L145-L240
[V-FONTS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_fonts.h
[V-BUFFER]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h
[V-CONTEXT]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_context.h
[V-LAYERS]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_layers.h
[V-SCREEN]: https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/agon_screen.h
[L-CANVAS]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/canvas.cpp
[L-DISPLAY]: https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/displaycontroller.cpp#L525-L632
