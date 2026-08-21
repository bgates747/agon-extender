# SETUP-004 VDU interface inventory

Source: official `agon-docs` VDU documentation; VDP baseline `v2.16.0`.

Legend: ✅ supported · 🟡 accepted no-op · 🔀 retained, mode-dependent ·
❓ unresolved · ⬜ unreviewed

## Base VDU commands

- ✅ `VDU 0` — Null (no operation).
- ✅ `VDU 1` — Send next character to the printer.
- ✅ `VDU 2` — Enable printer output.
- ✅ `VDU 3` — Disable printer output.
- ✅ `VDU 4` — Write text at the text cursor.
- ✅ `VDU 5` — Write text at the graphics cursor.
- ✅ `VDU 6` — Enable screen processing.
- ✅ `VDU 7` — Make a short beep (BEL).
- ✅ `VDU 8` — Move cursor back one character.
- ✅ `VDU 9` — Move cursor forward one character.
- ✅ `VDU 10` — Move cursor down one line.
- ✅ `VDU 11` — Move cursor up one line.
- ✅ `VDU 12` — Clear the text area (`CLS`).
- ✅ `VDU 13` — Carriage return.
- ✅ `VDU 14` — Enable paged mode.
- ✅ `VDU 15` — Disable paged mode.
- ✅ `VDU 16` — Clear the graphics area (`CLG`).
- ✅ `VDU 17, colour` — Set text colour (`COLOUR`).
- ✅ `VDU 18, mode, colour` — Set graphics colour (`GCOL`).
- ✅ `VDU 19, logical, physical, red, green, blue` — Define a logical colour.
- ✅ `VDU 20` — Reset palette, colours, and drawing modes.
- ✅ `VDU 21` — Disable screen processing.
- ✅ `VDU 22, mode` — Select screen mode (`MODE`).
- ✅ `VDU 23, char, b1...b8` — Redefine a display character.
- ✅ `VDU 24, left; bottom; right; top;` — Set graphics viewport.
- ✅ `VDU 25, mode, x; y;` — Execute a PLOT command.
- ✅ `VDU 26` — Reset graphics and text viewports.
- ✅ `VDU 27, char` — Output a character to the screen.
- ✅ `VDU 28, left, bottom, right, top` — Set text viewport.
- ✅ `VDU 29, x; y;` — Set graphics origin.
- ✅ `VDU 30` — Home the text cursor.
- ✅ `VDU 31, x, y` — Move text cursor to a text position (`TAB`).
- ✅ `VDU 127` — Backspace.
- ✅ `bytes 32–126, 128–255` — Display character data.

## Direct VDU 23 commands

- ✅ `VDU 23, 1, n` — Control the cursor.
- ✅ `VDU 23, 6, n1...n8` — Set dotted-line pattern.
- ✅ `VDU 23, 7, extent, direction, movement` — Scroll.
- ✅ `VDU 23, 16, setting, mask` — Define cursor movement behaviour.
- ✅ `VDU 23, 23, thickness` — Set line thickness.
- ✅ `VDU 23, 27, command, <params>` — Execute bitmap or sprite command.
- ✅ `VDU 23, 28` — Enter Intel HEX loader.

## System commands — VDU 23, 0

- ✅ `VDU 23, 0, &0A, n` — Set text-cursor start line and appearance.
- ✅ `VDU 23, 0, &0B, n` — Set text-cursor end line.
- ✅ `VDU 23, 0, &80, n` — General poll; echo `n` to confirm Extender is alive.
- 🔀 `VDU 23, 0, &81, locale` — Set keyboard locale.
- ✅ `VDU 23, 0, &82` — Request text-cursor position.
- ✅ `VDU 23, 0, &83, x; y;` — Read character at a text position.
- ✅ `VDU 23, 0, &84, x; y;` — Read pixel colour at a graphics position.
- ✅ `VDU 23, 0, &85, channel, command, <params>` — Execute audio command.
- ✅ `VDU 23, 0, &86` — Fetch screen dimensions and mode information.
- ❓ `VDU 23, 0, &87, <params>` — RTC ownership and MOS synchronization unresolved.
- 🔀 `VDU 23, 0, &88, delay; rate; led` — Control keyboard repeat and LEDs.
- 🔀 `VDU 23, 0, &89, command, <params>` — Control the mouse.
- ✅ `VDU 23, 0, &8A, n` — Set cursor start column.
- ✅ `VDU 23, 0, &8B, n` — Set cursor end column.
- ✅ `VDU 23, 0, &8C, x; y;` — Move cursor by a relative pixel offset.
- ✅ `VDU 23, 0, &90, char, b1...b8` — Redefine any system-font character.
- ✅ `VDU 23, 0, &91` — Restore all system-font characters.
- ✅ `VDU 23, 0, &92, char, bitmapId;` — Map a character to a bitmap.
- ✅ `VDU 23, 0, &93, x; y;` — Read character at a graphics position.
- ✅ `VDU 23, 0, &94, n` — Read a colour-palette entry.
- ✅ `VDU 23, 0, &95, command, <params>` — Manage fonts.
- ✅ `VDU 23, 0, &96, flags, bufferId;` — Set an affine transform matrix.
- 🔀 `VDU 23, 0, &98, n` — Enable or disable control keys.
- 🔀 `VDU 23, 0, &99, virtualKey` — Request current keyboard data for a key.
- ✅ `VDU 23, 0, &9A` — Temporarily enable paged mode.
- ✅ `VDU 23, 0, &9B, bufferId;` — Print a buffer to the screen.
- ✅ `VDU 23, 0, &9C` — Set text viewport using graphics coordinates.
- ✅ `VDU 23, 0, &9D` — Set graphics viewport using graphics coordinates.
- ✅ `VDU 23, 0, &9E` — Set graphics origin using graphics coordinates.
- ✅ `VDU 23, 0, &9F` — Move graphics origin and viewports.
- ✅ `VDU 23, 0, &A0, bufferId;, command, <params>` — Execute buffered command.
- ✅ `VDU 23, 0, &A1` — Receive and install a VDP firmware update.
- ✅ `VDU 23, 0, &C0, n` — Enable or disable logical screen scaling.
- ✅ `VDU 23, 0, &C1, n` — Enable or disable legacy modes.
- ✅ `VDU 23, 0, &C2, command, <params>` — Execute tile-engine command.
- ✅ `VDU 23, 0, &C3` — Swap screen buffer and/or wait for VSYNC.
- ✅ `VDU 23, 0, &C4, command, <params>` — Execute Copper command.
- ✅ `VDU 23, 0, &C8, command, <params>` — Manage graphics contexts.
- ✅ `VDU 23, 0, &CA` — Flush current drawing commands.
- ✅ `VDU 23, 0, &F2, n` — Set dot-dash pattern length.
- ✅ `VDU 23, 0, &F8, variableId; value;` — Set a VDP variable.
- ✅ `VDU 23, 0, &F9, variableId;` — Clear a VDP variable.
- ❓ `VDU 23, 0, &FE, n` — Console-mode implementation unresolved.
- ❓ `VDU 23, 0, &FF` — Terminal-mode support unresolved.

## Mouse commands — VDU 23, 0, &89

These commands are required in exclusive compatibility mode. Their cooperative
mode routing and ownership remain unresolved. Retain their parsers and visible
protocol behavior for the port survey; this does not require retaining the
upstream physical PS/2 controller implementation.

- 🔀 `..., 0` — Enable mouse.
- 🔀 `..., 1` — Disable mouse.
- 🔀 `..., 2` — Reset mouse.
- 🔀 `..., 3, cursorId;` — Select mouse cursor.
- 🔀 `..., 4, x; y;` — Set mouse position.
- 🔀 `..., 5, x1; y1; x2; y2;` — Set reserved mouse area.
- 🔀 `..., 6, sampleRate` — Set mouse sample rate.
- 🔀 `..., 7, resolution` — Set mouse resolution.
- 🔀 `..., 8, scaling` — Set mouse scaling.
- 🔀 `..., 9, acceleration;` — Set mouse acceleration.
- 🔀 `..., 10, acceleration; highByte` — Set mouse-wheel acceleration.

## Audio commands — VDU 23, 0, &85

The supported status applies to the command surface, not to every stock physical
audio destination. Extender Rev 1 is presently scoped to render EDP-generated
audio through the network/browser output path and may provide no direct local
audio output. Forwarding selected audio commands from the EDP to the onboard VDP
for playback on its audio hardware remains undecided and is not implied by the
checks below.

- ✅ `..., channel, 0, volume, frequency; duration;` — Play note.
- ✅ `..., channel, 1` — Read channel status.
- ✅ `..., channel, 2, volume` — Set channel volume.
- ✅ `..., channel, 3, frequency;` — Set channel frequency.
- ✅ `..., channel, 4, waveformOrSample, <params>` — Set waveform or sample.
- ✅ `..., channelOrSample, 5, command, <params>` — Manage samples.
- ✅ `..., channel, 6, type, <params>` — Set volume envelope.
- ✅ `..., channel, 7, type, <params>` — Set frequency envelope.
- ✅ `..., channel, 8` — Enable channel.
- ✅ `..., channel, 9` — Disable channel.
- ✅ `..., channel, 10` — Reset channel.
- ✅ `..., channel, 11, position; highByte` — Seek playback position.
- ✅ `..., channel, 12, duration; highByte` — Set duration.
- ✅ `..., channel, 13, sampleRate;` — Set sample rate.
- ✅ `..., channel, 14, parameter, value` — Set waveform parameters.

## Bitmap and sprite commands — VDU 23, 27

All bitmap and sprite operations are retained. Command `&40` is mode-dependent:
upstream dispatches it from `vdu_sprites.h` into mouse/PS/2-owned cursor state in
`agon_ps2.h`. The P4 port needs a project-owned cursor adapter or delegation
boundary rather than the upstream physical PS/2 implementation.

- ✅ `..., 0, bitmap` — Select 8-bit bitmap ID.
- ✅ `..., 1, width; height; <data>` — Load bitmap data.
- ✅ `..., 1, bitmap, 0, 0;` — Capture screen data into a bitmap.
- ✅ `..., 2, width; height; colour` — Create solid-colour bitmap.
- ✅ `..., 3, x; y;` — Draw current bitmap.
- ✅ `..., &20, bufferId;` — Select bitmap by 16-bit buffer ID.
- ✅ `..., &21, width; height; format` — Create bitmap from selected buffer.
- ✅ `..., &21, bitmapId; 0;` — Create bitmap from RGBA8888 buffer.
- ✅ `..., 4, sprite` — Select sprite.
- ✅ `..., 5` — Clear current sprite frames.
- ✅ `..., 6, bitmap` — Add 8-bit bitmap to current sprite.
- ✅ `..., 7, count` — Activate sprites.
- ✅ `..., 8` — Select next sprite frame.
- ✅ `..., 9` — Select previous sprite frame.
- ✅ `..., 10, frame` — Select sprite frame.
- ✅ `..., 11` — Show current sprite.
- ✅ `..., 12` — Hide current sprite.
- ✅ `..., 13, x; y;` — Move sprite to position.
- ✅ `..., 14, x; y;` — Move sprite by offset.
- ✅ `..., 15` — Update sprites.
- ✅ `..., 16` — Reset bitmaps and sprites.
- ✅ `..., 17` — Reset sprites only.
- ✅ `..., 18, mode` — Set sprite GCOL paint mode.
- ✅ `..., 19` — Use hardware sprite.
- ✅ `..., 20` — Use software sprite.
- ✅ `..., 21, bitmap` — Replace current sprite frame.
- ✅ `..., &26, bufferId;` — Add 16-bit bitmap to current sprite.
- ✅ `..., &35, bufferId;` — Replace current frame with 16-bit bitmap.
- 🔀 `..., &40, hotX, hotY` — Define mouse cursor bitmap.

## Font commands — VDU 23, 0, &95

- ✅ `..., 0, bufferId; flags` — Select font.
- ✅ `..., 1, bufferId; width, height, ascent, flags` — Create font from buffer.
- ✅ `..., 2, bufferId; field, value;` — Set or adjust font property.
- ✅ `..., 3, bufferId; <params>` — Reserved font command.
- ✅ `..., 4, bufferId;` — Delete font.
- ✅ `..., 5, bufferId;` — Copy system font to buffer.

## Context commands — VDU 23, 0, &C8

- ✅ `..., 0, contextId` — Select context stack.
- ✅ `..., 1, contextId` — Delete context stack.
- ✅ `..., 2, flags` — Reset context state.
- ✅ `..., 3` — Save context.
- ✅ `..., 4` — Restore context.
- ✅ `..., 5, contextId` — Save and select a context copy.
- ✅ `..., 6` — Restore all context state.
- ✅ `..., 7` — Clear context stack.

## Copper commands — VDU 23, 0, &C4

- ✅ `..., 0, paletteId;` — Create palette.
- ✅ `..., 1, paletteId;` — Delete palette.
- ✅ `..., 2, paletteId; index, red, green, blue` — Set palette entry.
- ✅ `..., 3, bufferId;` — Set or update signal list.
- ✅ `..., 4` — Reset signal list.

## Tile commands — VDU 23, 0, &C2

- ✅ `..., 0, tileBank, 0, 0, 0` — Initialize or reset tile bank.
- ✅ `..., 1, tileBank, tileId, <data>` — Load tile into bank.
- ✅ `..., 6, tileBank, tileId, <position-and-attributes>` — Draw tile.
- ✅ `..., 7, tileBank` — Delete tile bank.
- ✅ `..., 16, 0, tileMapSize, 0, 0` — Initialize or reset tile map.
- ✅ `..., 17, 0, x, y, tileId, attributes` — Set tile properties.
- ✅ `..., 23, 0` — Delete tile map.
- ✅ `..., 24, 0, tileLayerSize, 0, 0` — Initialize or reset tile layer.
- ✅ `..., 26, 0, x, y, xOffset, yOffset` — Set tile-layer scroll.
- ✅ `..., 28, 0` — Update tile layer.
- ✅ `..., 29, 0` — Draw tile layer.
- ✅ `..., 30, 0` — Update and draw tile layer.

## Buffered commands — VDU 23, 0, &A0, bufferId;

Command 128 writes only to the EDP diagnostic console. It does not return a VDP
protocol packet, update MOS sysvars, or provide application-readable results.

Callback commands 80 and 81 are unqualified keepers. Registration and removal
are EDP-internal, but invoked callback buffers may alter or suppress later
protocol packets. Preserve callback event dispatch and execution, including its
MOS-visible effects in exclusive compatibility mode.

- ✅ `..., 0, length; <data>` — Write block.
- ✅ `..., 1` — Call buffer.
- ✅ `..., 2` — Clear buffer.
- ✅ `..., 3, length;` — Create writable buffer.
- ✅ `..., 4` — Redirect output stream.
- ✅ `..., 5, operation, <params>` — Adjust buffer contents.
- ✅ `..., 6, operation, <condition>` — Conditionally call buffer.
- ✅ `..., 7` — Jump to buffer.
- ✅ `..., 9, offset, <params>` — Jump to buffer offset.
- ✅ `..., 10, offset, <condition>` — Conditionally jump to offset.
- ✅ `..., 11, offset, <params>` — Call buffer at offset.
- ✅ `..., 12, offset, <condition>` — Conditionally call buffer at offset.
- ✅ `..., 13, <sourceBufferIds>` — Copy blocks into one buffer.
- ✅ `..., 14` — Consolidate blocks.
- ✅ `..., 15–22, <params>` — Split or spread blocks and buffers.
- ✅ `..., 23` — Reverse block order.
- ✅ `..., 24, <params>` — Reverse data within blocks.
- ✅ `..., 25–26, <sourceBufferIds>` — Copy blocks by reference or consolidated.
- ✅ `..., 32–34, <matrix-params>` — Create or manipulate transform matrices.
- ✅ `..., 40, <params>` — Create transformed bitmap.
- ✅ `..., 41, <params>` — Transform buffer data.
- ✅ `..., 48, <params>` — Read VDP variable into buffer.
- ✅ `..., 64, sourceBufferId;` — Compress buffer.
- ✅ `..., 65, sourceBufferId;` — Decompress buffer.
- ✅ `..., 72, <params>` — Expand bitmap.
- ✅ `..., 80, eventType;` — Register callback buffer.
- ✅ `..., 81, eventType;` — Remove callback buffer.
- ✅ `..., 128` — Emit buffer information to the EDP diagnostic console.

## PLOT families — VDU 25, mode, x; y;

- ✅ `mode &00–&3F` — Draw lines and move graphics cursor.
- ✅ `mode &48–&4F, &58–&5F, &68–&6F, &78–&7F` — Draw line fills.
- ✅ `mode &50–&57` — Draw filled triangles.
- ✅ `mode &60–&67` — Draw filled rectangles.
- ✅ `mode &70–&77` — Draw filled parallelograms.
- ✅ `mode &80–&8F` — Perform flood fills.
- ✅ `mode &90–&9F` — Draw circles.
- ✅ `mode &A0–&B7` — Draw arcs, segments, and sectors.
- ✅ `mode &B8–&BF` — Copy or move rectangles.
- ✅ `mode &C0–&CF` — Draw ellipses.
- ✅ `mode &D8–&DF` — Fill paths (experimental).
- ✅ `mode &E8–&EF` — Plot bitmaps.
