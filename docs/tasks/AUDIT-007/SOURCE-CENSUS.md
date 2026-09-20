# Source census — first pass

Byte comparison, not semantic coverage. Header inclusion and conditional branches
need tracing; absence from the explicit translation-unit list alone does not prove
that a header implementation is omitted. Exact hashes are in baseline.json.

| Family | File | Comparison | Build selection |
|---|---|---|---|
| vdp-gl | `src/canvas.cpp` | identical | explicit TU |
| vdp-gl | `src/canvas.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/codepages.cpp` | identical | explicit TU |
| vdp-gl | `src/codepages.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/collisiondetector.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/collisiondetector.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/comdrivers/ps2controller.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/comdrivers/ps2controller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/comdrivers/ps2device.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/comdrivers/ps2device.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/comdrivers/tsi2c.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/comdrivers/tsi2c.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/DS3231.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/DS3231.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/MCP23S17.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/MCP23S17.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/cvbsgenerator.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/cvbsgenerator.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/kbdlayouts.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/kbdlayouts.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/keyboard.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/keyboard.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/mouse.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/mouse.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/soundgen.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/soundgen.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/swgenerator.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/devdrivers/swgenerator.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vga16controller.cpp` | modified | explicit TU |
| vdp-gl | `src/dispdrivers/vga16controller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vga2controller.cpp` | modified | explicit TU |
| vdp-gl | `src/dispdrivers/vga2controller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vga4controller.cpp` | modified | explicit TU |
| vdp-gl | `src/dispdrivers/vga4controller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vga64controller.cpp` | modified | explicit TU |
| vdp-gl | `src/dispdrivers/vga64controller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vga8controller.cpp` | modified | explicit TU |
| vdp-gl | `src/dispdrivers/vga8controller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vgabasecontroller.cpp` | modified | explicit TU |
| vdp-gl | `src/dispdrivers/vgabasecontroller.h` | modified | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vgacontroller.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vgacontroller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vgapalettedcontroller.cpp` | modified | explicit TU |
| vdp-gl | `src/dispdrivers/vgapalettedcontroller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vgatextcontroller.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/dispdrivers/vgatextcontroller.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/displaycontroller.cpp` | modified | explicit TU |
| vdp-gl | `src/displaycontroller.h` | modified | not explicit; includes/omission require trace |
| vdp-gl | `src/fabfonts.cpp` | identical | explicit TU |
| vdp-gl | `src/fabfonts.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fabgl.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fabglconf.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fabutils.cpp` | modified | not explicit; includes/omission require trace |
| vdp-gl | `src/fabutils.h` | modified | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_10x20.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_4x6.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_5x7.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_5x8.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_6x10.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_6x12.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_6x13.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_6x8.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_6x9.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_7x13.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_7x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_8x13.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_8x16.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_8x19.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_8x8.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_8x9.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_9x15.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_9x16.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_9x18.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_bigserif_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_bigserif_8x16.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_block_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_broadway_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_computer_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_courier_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_lcd_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_oldengl_8x16.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_sanserif_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_sanserif_8x16.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_slant_8x14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_12.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_14.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_15.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_16.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_17.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_18.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_22.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_std_24.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/fonts/font_wiggly_8x16.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/images/bitmaps.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/images/cursors.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/network/ICMP.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/network/ICMP.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/scene.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/scene.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/terminal.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/terminal.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/terminfo.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/terminfo.h` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/ulp_macro_ex.cpp` | identical | not explicit; includes/omission require trace |
| vdp-gl | `src/ulp_macro_ex.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/OneWire_direct_gpio.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/agon.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/agon_audio.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/agon_fonts.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/agon_palette.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/agon_ps2.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/agon_screen.h` | modified | declared header |
| VDP | `video/agon_ttxt.h` | identical | declared header |
| VDP | `video/audio_channel.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/audio_sample.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/buffer_stream.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/buffers.h` | modified | declared header |
| VDP | `video/compression.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/context.h` | modified | declared header |
| VDP | `video/context/cursor.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/context/fonts.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/context/graphics.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/context/viewport.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/enhanced_samples_generator.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/envelopes/adsr.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/envelopes/frequency.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/envelopes/multiphase_adsr.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/envelopes/types.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/hexload.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/mem_helpers.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/multi_buffer_stream.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/span.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/sprites.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/ttxtfont.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/types.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/updater.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/utils/thread_safe_variant_deque.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/vdp_protocol.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/vdp_variables.h` | modified | declared header |
| VDP | `video/vdu.h` | modified | declared header |
| VDP | `video/vdu_audio.h` | modified | not explicit; includes/omission require trace |
| VDP | `video/vdu_buffered.h` | modified | declared header |
| VDP | `video/vdu_context.h` | identical | declared header |
| VDP | `video/vdu_fonts.h` | identical | declared header |
| VDP | `video/vdu_layers.h` | identical | declared header |
| VDP | `video/vdu_sprites.h` | modified | declared header |
| VDP | `video/vdu_stream_processor.h` | modified | declared header |
| VDP | `video/vdu_sys.h` | modified | declared header |
| VDP | `video/version.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/video.ino` | modified | declared header |
| VDP | `video/ymodem.h` | identical | not explicit; includes/omission require trace |
| VDP | `video/zdi.h` | identical | not explicit; includes/omission require trace |
