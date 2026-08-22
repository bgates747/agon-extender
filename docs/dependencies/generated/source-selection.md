# Source-selection guide

Canonical graph: `graph:agon-extender:vdp-source-selection-v2`

The YAML companion is exhaustive. This compact view lists target selections,
exclusions, and source-region seams; available and non-runtime content remains
queryable in the YAML projection.

## Profile summary

| Profile | Selected | Excluded | Available | Non-runtime | Unresolved |
|---|---:|---:|---:|---:|---:|
| `build-profile:extender:p4-default` | 129 | 89 | 882 | 4111 | 0 |
| `build-profile:upstream:agon-vdp-v2.16.0-esp32` | 171 | 0 | 882 | 4111 | 0 |

## P4 target closure and boundaries

| Subject | Status | Why | Disposition |
|---|---|---|---|
| `file:CRC:src/CRC.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC12.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC12.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC16.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC16.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC32.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC32.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC64.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC64.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC8.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CRC8.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CrcDefines.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-core-types:retain |
| `file:CRC:src/CrcFastReverse.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CrcFastReverse.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/CrcParameters.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/FastCRC32.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:CRC:src/FastCRC32.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:ESP32Time:ESP32Time.cpp` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-core-types:retain, SETUP-004.1.b:rtc-esp32time-provider:retain |
| `file:ESP32Time:ESP32Time.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-core-types:retain, SETUP-004.1.b:rtc-esp32time-provider:retain |
| `file:agon-vdp:video/OneWire_direct_gpio.h` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-zdi-direct-gpio-helper:omit |
| `file:agon-vdp:video/agon.h` | selected | retained-compatibility-requirement | SETUP-004.1.b:rtc-protocol-surface:retain, SETUP-004.1.c:transport-stock-uart-hardware:replace |
| `file:agon-vdp:video/agon_audio.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-timing:retain, SETUP-004.1.a:framework-freertos-concurrency:retain, SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/agon_fonts.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/agon_palette.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/agon_ps2.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | SETUP-004.1.a:framework-debug-serial-binding:omit, SETUP-004.1.f:input-official-compatibility-integration:replace |
| `file:agon-vdp:video/agon_screen.h` | selected | retained-compatibility-requirement | SETUP-004.1.d:display-vdp-screen-facade:retain |
| `file:agon-vdp:video/agon_ttxt.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/audio_channel.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-timing:retain, SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/audio_sample.h` | selected | retained-compatibility-requirement | SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/buffer_stream.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-stream-contract:retain |
| `file:agon-vdp:video/buffers.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/compression.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/context.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-psram-and-capability-heap:retain, SETUP-004.1.d:display-vdp-screen-facade:retain |
| `file:agon-vdp:video/context/cursor.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/context/fonts.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/context/graphics.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/context/viewport.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/enhanced_samples_generator.h` | selected | retained-compatibility-requirement | SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/envelopes/adsr.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-core-types:retain, SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/envelopes/frequency.h` | selected | retained-compatibility-requirement | SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/envelopes/multiphase_adsr.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-core-types:retain, SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/envelopes/types.h` | selected | retained-compatibility-requirement | SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/hexload.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-timing:retain, SETUP-004.1.a:framework-debug-serial-binding:omit, SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `file:agon-vdp:video/mem_helpers.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/multi_buffer_stream.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-stream-contract:retain |
| `file:agon-vdp:video/span.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/sprites.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/ttxtfont.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/types.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-psram-and-capability-heap:retain |
| `file:agon-vdp:video/updater.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-timing:retain, SETUP-004.1.a:framework-idf-ota-and-restart-primitives:retain, SETUP-004.1.a:framework-stock-serial-updater:omit |
| `file:agon-vdp:video/utils/thread_safe_variant_deque.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/vdp_protocol.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | SETUP-004.1.a:framework-primary-vdp-serial-binding:replace, SETUP-004.1.c:transport-stock-uart-hardware:replace |
| `file:agon-vdp:video/vdp_variables.h` | selected | retained-compatibility-requirement | SETUP-004.1.b:rtc-esp32time-provider:retain, SETUP-004.1.b:rtc-protocol-surface:retain, SETUP-004.1.f:input-official-compatibility-integration:replace |
| `file:agon-vdp:video/vdu.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-debug-serial-binding:omit, SETUP-004.1.a:framework-idf-interrupt-and-critical-services:retain, SETUP-004.1.d:display-vdp-screen-facade:retain |
| `file:agon-vdp:video/vdu_audio.h` | selected | retained-compatibility-requirement | SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain |
| `file:agon-vdp:video/vdu_buffered.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-timing:retain, SETUP-004.1.a:framework-idf-interrupt-and-critical-services:retain, SETUP-004.1.a:framework-psram-and-capability-heap:retain |
| `file:agon-vdp:video/vdu_context.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/vdu_fonts.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/vdu_layers.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-psram-and-capability-heap:retain |
| `file:agon-vdp:video/vdu_sprites.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | SETUP-004.1.f:input-official-compatibility-integration:replace |
| `file:agon-vdp:video/vdu_stream_processor.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-stream-contract:retain, SETUP-004.1.b:rtc-protocol-surface:retain, SETUP-004.1.f:input-official-compatibility-integration:replace, SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `file:agon-vdp:video/vdu_sys.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-stock-serial-updater:omit, SETUP-004.1.a:framework-watchdog-and-core-control:replace, SETUP-004.1.b:rtc-esp32time-provider:retain, SETUP-004.1.b:rtc-protocol-surface:retain, SETUP-004.1.f:input-official-compatibility-integration:replace, SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `file:agon-vdp:video/version.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:agon-vdp:video/video.ino` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-sketch-lifecycle:retain, SETUP-004.1.a:framework-arduino-stream-contract:retain, SETUP-004.1.a:framework-arduino-timing:retain, SETUP-004.1.a:framework-debug-serial-binding:omit, SETUP-004.1.a:framework-freertos-concurrency:retain, SETUP-004.1.a:framework-idf-interrupt-and-critical-services:retain, SETUP-004.1.a:framework-idf-ota-and-restart-primitives:retain, SETUP-004.1.a:framework-primary-vdp-serial-binding:replace, SETUP-004.1.a:framework-psram-and-capability-heap:retain, SETUP-004.1.a:framework-stock-serial-updater:omit, SETUP-004.1.a:framework-unused-wifi-include:omit, SETUP-004.1.a:framework-watchdog-and-core-control:replace, SETUP-004.1.b:rtc-esp32time-provider:retain, SETUP-004.1.b:rtc-protocol-surface:retain, SETUP-004.1.c:peripheral-zdi-direct-gpio-helper:omit, SETUP-004.1.c:transport-stock-uart-hardware:replace, SETUP-004.1.d:display-vdp-screen-facade:retain, SETUP-004.1.e:audio-vdp-command-and-channel-runtime:retain, SETUP-004.1.f:input-official-compatibility-integration:replace, SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `file:agon-vdp:video/ymodem.h` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-arduino-timing:retain, SETUP-004.1.a:framework-debug-serial-binding:omit, SETUP-004.1.a:framework-psram-and-capability-heap:retain, SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `file:agon-vdp:video/zdi.h` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-zdi-direct-gpio-helper:omit |
| `file:vdp-gl:src/canvas.cpp` | selected | retained-compatibility-requirement | SETUP-004.1.d:display-canvas-common-rendering:retain |
| `file:vdp-gl:src/canvas.h` | selected | retained-compatibility-requirement | SETUP-004.1.d:display-canvas-common-rendering:retain |
| `file:vdp-gl:src/codepages.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/codepages.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/collisiondetector.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/collisiondetector.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/comdrivers/ps2controller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-esp32-ulp-rtc-domain:omit, SETUP-004.1.f:input-vdp-gl-physical-ps2-controller:omit |
| `file:vdp-gl:src/comdrivers/ps2controller.h` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-esp32-ulp-rtc-domain:omit, SETUP-004.1.f:input-vdp-gl-physical-ps2-controller:omit |
| `file:vdp-gl:src/comdrivers/ps2device.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/comdrivers/ps2device.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/comdrivers/tsi2c.cpp` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-vdp-gl-i2c-service:omit |
| `file:vdp-gl:src/comdrivers/tsi2c.h` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-vdp-gl-i2c-service:omit |
| `file:vdp-gl:src/devdrivers/DS3231.cpp` | excluded | deliberate-exclusion | SETUP-004.1.b:peripheral-vdp-gl-ds3231:omit, SETUP-004.1.c:peripheral-vdp-gl-i2c-service:omit |
| `file:vdp-gl:src/devdrivers/DS3231.h` | excluded | deliberate-exclusion | SETUP-004.1.b:peripheral-vdp-gl-ds3231:omit, SETUP-004.1.c:peripheral-vdp-gl-i2c-service:omit |
| `file:vdp-gl:src/devdrivers/MCP23S17.cpp` | excluded | deliberate-exclusion | SETUP-004.1.b:peripheral-vdp-gl-mcp23s17:omit |
| `file:vdp-gl:src/devdrivers/MCP23S17.h` | excluded | deliberate-exclusion | SETUP-004.1.b:peripheral-vdp-gl-mcp23s17:omit |
| `file:vdp-gl:src/devdrivers/cvbsgenerator.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-composite-video-generator:omit |
| `file:vdp-gl:src/devdrivers/cvbsgenerator.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-composite-video-generator:omit |
| `file:vdp-gl:src/devdrivers/kbdlayouts.cpp` | excluded | deliberate-exclusion | SETUP-004.1.f:input-vdp-gl-keyboard-and-layout:omit |
| `file:vdp-gl:src/devdrivers/kbdlayouts.h` | excluded | deliberate-exclusion | SETUP-004.1.f:input-vdp-gl-keyboard-and-layout:omit |
| `file:vdp-gl:src/devdrivers/keyboard.cpp` | excluded | deliberate-exclusion | SETUP-004.1.f:input-vdp-gl-keyboard-and-layout:omit |
| `file:vdp-gl:src/devdrivers/keyboard.h` | excluded | deliberate-exclusion | SETUP-004.1.f:input-vdp-gl-keyboard-and-layout:omit |
| `file:vdp-gl:src/devdrivers/mouse.cpp` | excluded | deliberate-exclusion | SETUP-004.1.f:input-vdp-gl-mouse-device:omit |
| `file:vdp-gl:src/devdrivers/mouse.h` | excluded | deliberate-exclusion | SETUP-004.1.f:input-vdp-gl-mouse-device:omit |
| `file:vdp-gl:src/devdrivers/soundgen.cpp` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-idf-interrupt-and-critical-services:retain, SETUP-004.1.a:framework-psram-and-capability-heap:retain, SETUP-004.1.c:architecture-cpu-clock-and-cycle-counter:replace, SETUP-004.1.c:interrupt-pinned-allocation-helper:retain, SETUP-004.1.c:timing-idf-high-resolution-service:retain, SETUP-004.1.e:audio-classic-esp32-physical-output:replace, SETUP-004.1.e:audio-waveform-and-mixer-core:retain |
| `file:vdp-gl:src/devdrivers/soundgen.h` | selected | retained-compatibility-requirement | SETUP-004.1.e:audio-classic-esp32-physical-output:replace, SETUP-004.1.e:audio-waveform-and-mixer-core:retain |
| `file:vdp-gl:src/devdrivers/swgenerator.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/devdrivers/swgenerator.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/dispdrivers/vga16controller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga16controller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga2controller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga2controller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga4controller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga4controller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga64controller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga64controller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga8controller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vga8controller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vgabasecontroller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vgabasecontroller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vgacontroller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vgacontroller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vgapalettedcontroller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vgapalettedcontroller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-concrete-controller-family:replace |
| `file:vdp-gl:src/dispdrivers/vgatextcontroller.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-text-controller:omit |
| `file:vdp-gl:src/dispdrivers/vgatextcontroller.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-text-controller:omit |
| `file:vdp-gl:src/displaycontroller.cpp` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-freertos-concurrency:retain, SETUP-004.1.a:framework-psram-and-capability-heap:retain, SETUP-004.1.d:display-canvas-common-rendering:retain |
| `file:vdp-gl:src/displaycontroller.h` | selected | retained-compatibility-requirement | SETUP-004.1.d:display-canvas-common-rendering:retain |
| `file:vdp-gl:src/fabfonts.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fabfonts.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fabgl.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | SETUP-004.1.b:peripheral-vdp-gl-ds3231:omit, SETUP-004.1.d:display-fabgl-scene-helper:omit, SETUP-004.1.d:display-vga-text-controller:omit |
| `file:vdp-gl:src/fabglconf.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | SETUP-004.1.a:framework-watchdog-and-core-control:replace |
| `file:vdp-gl:src/fabutils.cpp` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-watchdog-and-core-control:replace, SETUP-004.1.c:architecture-cpu-clock-and-cycle-counter:replace, SETUP-004.1.c:interrupt-pinned-allocation-helper:retain, SETUP-004.1.c:peripheral-portable-gpio-services:retain, SETUP-004.1.c:peripheral-spi-services:retain, SETUP-004.1.c:peripheral-terminal-adc-services:omit, SETUP-004.1.c:timing-idf-high-resolution-service:retain, SETUP-004.1.h:storage-vdp-gl-esp32-mount-format-backends:omit, SETUP-004.1.h:storage-vdp-gl-filebrowser-api:omit |
| `file:vdp-gl:src/fabutils.h` | selected | retained-compatibility-requirement | SETUP-004.1.c:architecture-cpu-clock-and-cycle-counter:replace, SETUP-004.1.c:interrupt-pinned-allocation-helper:retain, SETUP-004.1.c:peripheral-terminal-adc-services:omit, SETUP-004.1.h:storage-vdp-gl-esp32-mount-format-backends:omit, SETUP-004.1.h:storage-vdp-gl-filebrowser-api:omit |
| `file:vdp-gl:src/fonts/font_10x20.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_4x6.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_5x7.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_5x8.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_6x10.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_6x12.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_6x13.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_6x8.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_6x9.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_7x13.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_7x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_8x13.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_8x16.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_8x19.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_8x8.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_8x9.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_9x15.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_9x18.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_bigserif_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_bigserif_8x16.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_block_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_broadway_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_computer_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_courier_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_lcd_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_oldengl_8x16.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_sanserif_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_sanserif_8x16.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_slant_8x14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_12.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_14.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_15.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_16.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_17.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_18.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_22.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_std_24.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/fonts/font_wiggly_8x16.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/images/cursors.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/network/ICMP.cpp` | excluded | deliberate-exclusion | SETUP-004.1.g:network-vdp-gl-icmp-helper:omit |
| `file:vdp-gl:src/network/ICMP.h` | excluded | deliberate-exclusion | SETUP-004.1.g:network-vdp-gl-icmp-helper:omit |
| `file:vdp-gl:src/scene.cpp` | excluded | deliberate-exclusion | SETUP-004.1.d:display-fabgl-scene-helper:omit |
| `file:vdp-gl:src/scene.h` | excluded | deliberate-exclusion | SETUP-004.1.d:display-fabgl-scene-helper:omit |
| `file:vdp-gl:src/terminal.cpp` | selected | retained-compatibility-requirement | SETUP-004.1.a:framework-freertos-concurrency:retain, SETUP-004.1.a:framework-primary-vdp-serial-binding:replace, SETUP-004.1.c:peripheral-portable-gpio-services:retain, SETUP-004.1.c:peripheral-terminal-adc-services:omit, SETUP-004.1.c:transport-stock-uart-hardware:replace |
| `file:vdp-gl:src/terminal.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/terminfo.cpp` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/terminfo.h` | selected | retained-compatibility-requirement, inherited-broad-build-selection | — |
| `file:vdp-gl:src/ulp_macro_ex.cpp` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-esp32-ulp-rtc-domain:omit |
| `file:vdp-gl:src/ulp_macro_ex.h` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-esp32-ulp-rtc-domain:omit |
| `source-region:agon-vdp:video/agon.h:transport-stock-uart-hardware` | excluded | deliberate-exclusion | SETUP-004.1.c:transport-stock-uart-hardware:replace |
| `source-region:agon-vdp:video/agon_ps2.h:framework-debug-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-debug-serial-binding:omit |
| `source-region:agon-vdp:video/agon_ps2.h:input-official-compatibility-integration` | excluded | deliberate-exclusion | SETUP-004.1.f:input-official-compatibility-integration:replace |
| `source-region:agon-vdp:video/hexload.h:framework-debug-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-debug-serial-binding:omit |
| `source-region:agon-vdp:video/hexload.h:transfer-stock-hex-and-ymodem` | excluded | deliberate-exclusion | SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `source-region:agon-vdp:video/updater.h:framework-stock-serial-updater` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-stock-serial-updater:omit |
| `source-region:agon-vdp:video/vdp_protocol.h:framework-primary-vdp-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-primary-vdp-serial-binding:replace |
| `source-region:agon-vdp:video/vdp_protocol.h:transport-stock-uart-hardware` | excluded | deliberate-exclusion | SETUP-004.1.c:transport-stock-uart-hardware:replace |
| `source-region:agon-vdp:video/vdp_variables.h:input-official-compatibility-integration` | excluded | deliberate-exclusion | SETUP-004.1.f:input-official-compatibility-integration:replace |
| `source-region:agon-vdp:video/vdu.h:framework-debug-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-debug-serial-binding:omit |
| `source-region:agon-vdp:video/vdu_sprites.h:input-official-compatibility-integration` | excluded | deliberate-exclusion | SETUP-004.1.f:input-official-compatibility-integration:replace |
| `source-region:agon-vdp:video/vdu_stream_processor.h:input-official-compatibility-integration` | excluded | deliberate-exclusion | SETUP-004.1.f:input-official-compatibility-integration:replace |
| `source-region:agon-vdp:video/vdu_stream_processor.h:transfer-stock-hex-and-ymodem` | excluded | deliberate-exclusion | SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `source-region:agon-vdp:video/vdu_sys.h:framework-stock-serial-updater` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-stock-serial-updater:omit |
| `source-region:agon-vdp:video/vdu_sys.h:framework-watchdog-and-core-control` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-watchdog-and-core-control:replace |
| `source-region:agon-vdp:video/vdu_sys.h:input-official-compatibility-integration` | excluded | deliberate-exclusion | SETUP-004.1.f:input-official-compatibility-integration:replace |
| `source-region:agon-vdp:video/vdu_sys.h:transfer-stock-hex-and-ymodem` | excluded | deliberate-exclusion | SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `source-region:agon-vdp:video/video.ino:framework-debug-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-debug-serial-binding:omit |
| `source-region:agon-vdp:video/video.ino:framework-primary-vdp-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-primary-vdp-serial-binding:replace |
| `source-region:agon-vdp:video/video.ino:framework-stock-serial-updater` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-stock-serial-updater:omit |
| `source-region:agon-vdp:video/video.ino:framework-unused-wifi-include` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-unused-wifi-include:omit |
| `source-region:agon-vdp:video/video.ino:framework-watchdog-and-core-control` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-watchdog-and-core-control:replace |
| `source-region:agon-vdp:video/video.ino:input-official-compatibility-integration` | excluded | deliberate-exclusion | SETUP-004.1.f:input-official-compatibility-integration:replace |
| `source-region:agon-vdp:video/video.ino:peripheral-zdi-direct-gpio-helper` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-zdi-direct-gpio-helper:omit |
| `source-region:agon-vdp:video/video.ino:transfer-stock-hex-and-ymodem` | excluded | deliberate-exclusion | SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `source-region:agon-vdp:video/video.ino:transport-stock-uart-hardware` | excluded | deliberate-exclusion | SETUP-004.1.c:transport-stock-uart-hardware:replace |
| `source-region:agon-vdp:video/ymodem.h:framework-debug-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-debug-serial-binding:omit |
| `source-region:agon-vdp:video/ymodem.h:transfer-stock-hex-and-ymodem` | excluded | deliberate-exclusion | SETUP-004.1.g:transfer-stock-hex-and-ymodem:omit |
| `source-region:vdp-gl:src/devdrivers/soundgen.cpp:architecture-cpu-clock-and-cycle-counter` | excluded | deliberate-exclusion | SETUP-004.1.c:architecture-cpu-clock-and-cycle-counter:replace |
| `source-region:vdp-gl:src/devdrivers/soundgen.cpp:audio-classic-esp32-physical-output` | excluded | deliberate-exclusion | SETUP-004.1.e:audio-classic-esp32-physical-output:replace |
| `source-region:vdp-gl:src/devdrivers/soundgen.h:audio-classic-esp32-physical-output` | excluded | deliberate-exclusion | SETUP-004.1.e:audio-classic-esp32-physical-output:replace |
| `source-region:vdp-gl:src/fabgl.h:display-fabgl-scene-helper` | excluded | deliberate-exclusion | SETUP-004.1.d:display-fabgl-scene-helper:omit |
| `source-region:vdp-gl:src/fabgl.h:display-vga-text-controller` | excluded | deliberate-exclusion | SETUP-004.1.d:display-vga-text-controller:omit |
| `source-region:vdp-gl:src/fabgl.h:peripheral-vdp-gl-ds3231` | excluded | deliberate-exclusion | SETUP-004.1.b:peripheral-vdp-gl-ds3231:omit |
| `source-region:vdp-gl:src/fabglconf.h:framework-watchdog-and-core-control` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-watchdog-and-core-control:replace |
| `source-region:vdp-gl:src/fabutils.cpp:architecture-cpu-clock-and-cycle-counter` | excluded | deliberate-exclusion | SETUP-004.1.c:architecture-cpu-clock-and-cycle-counter:replace |
| `source-region:vdp-gl:src/fabutils.cpp:framework-watchdog-and-core-control` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-watchdog-and-core-control:replace |
| `source-region:vdp-gl:src/fabutils.cpp:peripheral-terminal-adc-services` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-terminal-adc-services:omit |
| `source-region:vdp-gl:src/fabutils.cpp:storage-vdp-gl-esp32-mount-format-backends` | excluded | deliberate-exclusion | SETUP-004.1.h:storage-vdp-gl-esp32-mount-format-backends:omit |
| `source-region:vdp-gl:src/fabutils.cpp:storage-vdp-gl-filebrowser-api` | excluded | deliberate-exclusion | SETUP-004.1.h:storage-vdp-gl-filebrowser-api:omit |
| `source-region:vdp-gl:src/fabutils.h:architecture-cpu-clock-and-cycle-counter` | excluded | deliberate-exclusion | SETUP-004.1.c:architecture-cpu-clock-and-cycle-counter:replace |
| `source-region:vdp-gl:src/fabutils.h:peripheral-terminal-adc-services` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-terminal-adc-services:omit |
| `source-region:vdp-gl:src/fabutils.h:storage-vdp-gl-esp32-mount-format-backends` | excluded | deliberate-exclusion | SETUP-004.1.h:storage-vdp-gl-esp32-mount-format-backends:omit |
| `source-region:vdp-gl:src/fabutils.h:storage-vdp-gl-filebrowser-api` | excluded | deliberate-exclusion | SETUP-004.1.h:storage-vdp-gl-filebrowser-api:omit |
| `source-region:vdp-gl:src/terminal.cpp:framework-primary-vdp-serial-binding` | excluded | deliberate-exclusion | SETUP-004.1.a:framework-primary-vdp-serial-binding:replace |
| `source-region:vdp-gl:src/terminal.cpp:peripheral-terminal-adc-services` | excluded | deliberate-exclusion | SETUP-004.1.c:peripheral-terminal-adc-services:omit |
| `source-region:vdp-gl:src/terminal.cpp:transport-stock-uart-hardware` | excluded | deliberate-exclusion | SETUP-004.1.c:transport-stock-uart-hardware:replace |

## Project-owned replacement boundaries

| Build unit | State | Project path | Task |
|---|---|---|---|
| `build-unit:extender:p4-display-controller` | phase-c-qualified-host | `video/extender/display/p4_display_controller.cpp` | `PORT-003` |
| `build-unit:extender:p4-frame-service-canary` | diagnostic-frame-service | `video/extender/canary/frame_service_canary.cpp` | `PORT-003` |
| `build-unit:extender:p4-frame-task-adapter` | phase-c-target-closure | `video/extender/display/p4_frame_service.cpp` | `PORT-003` |
| `build-unit:extender:p4-logical-frame-service` | phase-c-qualified-host | `video/extender/display/logical_frame_service.cpp` | `PORT-003` |
| `build-unit:extender:p4-native-pixel-codec` | phase-b-qualified-host | `video/extender/display/native_pixel_codec.cpp` | `PORT-003` |
| `build-unit:extender:p4-plane-storage` | phase-c-qualified-host | `video/extender/display/plane_storage.cpp` | `PORT-003` |
| `build-unit:extender:p4-port-adapters` | phase-c-logical-frame-service | — | `PORT-003` |
| `build-unit:extender:p4-vdp-gl-port-utility-closure` | phase-b-narrow-port | `video/extender/port/fabutils_port.cpp` | `PORT-003` |
