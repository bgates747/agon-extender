# VDU 22 screen-mode selection — proof dependency slice

Generated projection; the YAML dependency slice is authoritative.

## Summary

- Nodes: 59
- Edges: 105
- Explicit boundaries: 59
- Unresolved records: 71
- Node kinds: command=1, dispatch=1, function=14, method=12, physical-facility=5, platform-api=4, protocol-packet=1, subsystem=5, variable=16

## Nodes

| Kind | ID | Label | Selection | Port disposition |
|---|---|---|---|---|
| command | `command:agon-vdp:vdu-22` | VDU 22 | selected | retain |
| dispatch | `dispatch:agon-vdp:VDUStreamProcessor::vdu:vdu-22` | VDUStreamProcessor::vdu case VDU 22 | selected | — |
| function | `function:agon-vdp:changeMode(uint8_t%20mode)` | changeMode(uint8_t mode) | selected | — |
| function | `function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false)` | changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | selected | — |
| function | `function:agon-vdp:debug_log(const%20char%20*%20format,...)` | debug_log(const char * format,...) | selected | — |
| function | `function:agon-vdp:getMouse()` | getMouse() | selected | — |
| function | `function:agon-vdp:getVGAColourDepth()` | getVGAColourDepth() | selected | — |
| function | `function:agon-vdp:hideMouseCursor()` | hideMouseCursor() | selected | — |
| function | `function:agon-vdp:isDoubleBuffered()` | isDoubleBuffered() | selected | — |
| function | `function:agon-vdp:isSystemMouseCursor(uint16_t%20cursor)` | isSystemMouseCursor(uint16_t cursor) | selected | — |
| function | `function:agon-vdp:resetMousePositioner(uint16_t%20width,uint16_t%20height,fabgl::VGABaseController%20*%20display)` | resetMousePositioner(uint16_t width,uint16_t height,fabgl::VGABaseController * display) | selected | — |
| function | `function:agon-vdp:restorePalette()` | restorePalette() | selected | — |
| function | `function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value)` | setVDPVariable(uint16_t flag,uint16_t value) | selected | — |
| function | `function:agon-vdp:showMouseCursor()` | showMouseCursor() | selected | — |
| function | `function:agon-vdp:switchBuffer()` | switchBuffer() | selected | — |
| function | `function:agon-vdp:waitPlotCompletion(bool%20waitForVSync=false)` | waitPlotCompletion(bool waitForVSync=false) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset)` | VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::bufferCallCallbacks(uint16_t%20type)` | VDUStreamProcessor::bufferCallCallbacks(uint16_t type) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::bufferRemoveCallback(uint16_t%20bufferId,uint16_t%20type)` | VDUStreamProcessor::bufferRemoveCallback(uint16_t bufferId,uint16_t type) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::clearContextStack()` | VDUStreamProcessor::clearContextStack() | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::readByte_t(uint16_t%20timeout=COMMS_TIMEOUT)` | VDUStreamProcessor::readByte_t(uint16_t timeout=COMMS_TIMEOUT) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::resetAllContexts()` | VDUStreamProcessor::resetAllContexts() | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags)` | VDUStreamProcessor::resetContext(uint8_t flags) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id)` | VDUStreamProcessor::selectContext(uint8_t id) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::sendModeInformation()` | VDUStreamProcessor::sendModeInformation() | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::send_packet(uint8_t%20code,uint16_t%20len,uint8_t%20data[])` | VDUStreamProcessor::send_packet(uint8_t code,uint16_t len,uint8_t data[]) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::updateMouseVars(MouseDelta%20*%20delta)` | VDUStreamProcessor::updateMouseVars(MouseDelta * delta) | selected | — |
| method | `method:agon-vdp:VDUStreamProcessor::vdu_mode(uint8_t%20mode)` | VDUStreamProcessor::vdu_mode(uint8_t mode) | selected | — |
| physical-facility | `physical-facility:reviewed:active%20vga%20controller%20for%20mouse%20positioning%20and%20cursor%20rendering` | active VGA controller for mouse positioning and cursor rendering | external | — |
| physical-facility | `physical-facility:reviewed:dma%20descriptors%20and%20capability-specific%20heap%20allocation` | DMA descriptors and capability-specific heap allocation | external | — |
| physical-facility | `physical-facility:reviewed:esp32%20gpio%20matrix` | ESP32 GPIO matrix | external | — |
| physical-facility | `physical-facility:reviewed:esp32%20ulp,%20rtc%20gpio,%20sens%20registers,%20rtc%20interrupt,%20queues,%20and%20tasks` | ESP32 ULP, RTC GPIO, SENS registers, RTC interrupt, queues, and tasks | external | — |
| physical-facility | `physical-facility:reviewed:i2s1%20register%20block%20and%20interrupt%20source` | I2S1 register block and interrupt source | external | — |
| platform-api | `platform-api:external:xTaskGetTickCountFromISR` | xTaskGetTickCountFromISR() | external | — |
| platform-api | `platform-api:reviewed:fabgl%20canvas%20and%20vga2/vga4/vga8/vga16/vga64%20controllers` | FabGL Canvas and VGA2/VGA4/VGA8/VGA16/VGA64 controllers | external | — |
| platform-api | `platform-api:reviewed:fabgl%20ps2controller,%20keyboard,%20mouse,%20layouts,%20and%20cursor` | FabGL PS2Controller, Keyboard, Mouse, layouts, and Cursor | external | — |
| platform-api | `platform-api:reviewed:freertos%20primitive%20execution%20task` | FreeRTOS primitive execution task | external | — |
| protocol-packet | `protocol-packet:agon-vdp:packet-mode` | PACKET_MODE screen-mode information | selected | — |
| subsystem | `subsystem:agon-vdp:graphics-display` | Graphics Display | selected | — |
| subsystem | `subsystem:agon-vdp:memory-and-psram` | Memory And Psram | selected | — |
| subsystem | `subsystem:agon-vdp:physical-ps2-input` | Physical Ps2 Input | selected | — |
| subsystem | `subsystem:agon-vdp:primary-vdp-transport` | Primary Vdp Transport | selected | — |
| subsystem | `subsystem:agon-vdp:runtime-concurrency` | Runtime Concurrency | selected | — |
| variable | `variable:agon-vdp:DBGSerial` | DBGSerial | selected | — |
| variable | `variable:agon-vdp:_VGAController` | _VGAController | selected | — |
| variable | `variable:agon-vdp:callbackBuffers` | callbackBuffers | selected | — |
| variable | `variable:agon-vdp:canvas` | canvas | selected | — |
| variable | `variable:agon-vdp:canvasH` | canvasH | selected | — |
| variable | `variable:agon-vdp:canvasW` | canvasW | selected | — |
| variable | `variable:agon-vdp:contextStacks` | contextStacks | selected | — |
| variable | `variable:agon-vdp:legacyModes` | legacyModes | selected | — |
| variable | `variable:agon-vdp:logicalScaleX` | logicalScaleX | selected | — |
| variable | `variable:agon-vdp:logicalScaleY` | logicalScaleY | selected | — |
| variable | `variable:agon-vdp:mCursor` | mCursor | selected | — |
| variable | `variable:agon-vdp:mouseCursors` | mouseCursors | selected | — |
| variable | `variable:agon-vdp:mouseVisible` | mouseVisible | selected | — |
| variable | `variable:agon-vdp:ttxtMode` | ttxtMode | selected | — |
| variable | `variable:agon-vdp:ttxt_instance` | ttxt_instance | selected | — |
| variable | `variable:agon-vdp:videoMode` | videoMode | selected | — |

## Relationships

| From | Relationship | To | Confidence |
|---|---|---|---|
| Graphics Display | allocates | Memory And Psram | confirmed |
| resetMousePositioner(uint16_t width,uint16_t height,fabgl::VGABaseController * display) | calls | getMouse() | strong |
| VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | calls | VDUStreamProcessor::bufferRemoveCallback(uint16_t bufferId,uint16_t type) | strong |
| VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | calls | debug_log(const char * format,...) | strong |
| VDUStreamProcessor::bufferCallCallbacks(uint16_t type) | calls | VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | strong |
| VDUStreamProcessor::bufferRemoveCallback(uint16_t bufferId,uint16_t type) | calls | VDUStreamProcessor::bufferRemoveCallback(uint16_t bufferId,uint16_t type) | strong |
| changeMode(uint8_t mode) | calls | changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | strong |
| changeMode(uint8_t mode) | calls | debug_log(const char * format,...) | strong |
| changeMode(uint8_t mode) | calls | restorePalette() | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | calls | debug_log(const char * format,...) | strong |
| VDUStreamProcessor::clearContextStack() | calls | debug_log(const char * format,...) | strong |
| VDUStreamProcessor::resetAllContexts() | calls | VDUStreamProcessor::clearContextStack() | strong |
| VDUStreamProcessor::resetAllContexts() | calls | debug_log(const char * format,...) | strong |
| VDUStreamProcessor::resetAllContexts() | calls | VDUStreamProcessor::resetContext(uint8_t flags) | strong |
| VDUStreamProcessor::resetAllContexts() | calls | VDUStreamProcessor::selectContext(uint8_t id) | strong |
| restorePalette() | calls | getVGAColourDepth() | strong |
| VDUStreamProcessor::selectContext(uint8_t id) | calls | debug_log(const char * format,...) | strong |
| VDUStreamProcessor::sendModeInformation() | calls | VDUStreamProcessor::bufferCallCallbacks(uint16_t type) | strong |
| VDUStreamProcessor::sendModeInformation() | calls | getVGAColourDepth() | strong |
| VDUStreamProcessor::sendModeInformation() | calls | VDUStreamProcessor::send_packet(uint8_t code,uint16_t len,uint8_t data[]) | strong |
| VDUStreamProcessor::send_packet(uint8_t code,uint16_t len,uint8_t data[]) | calls | VDUStreamProcessor::bufferCallCallbacks(uint16_t type) | strong |
| VDUStreamProcessor::send_packet(uint8_t code,uint16_t len,uint8_t data[]) | calls | debug_log(const char * format,...) | strong |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | debug_log(const char * format,...) | strong |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | hideMouseCursor() | strong |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | showMouseCursor() | strong |
| showMouseCursor() | calls | hideMouseCursor() | strong |
| showMouseCursor() | calls | isSystemMouseCursor(uint16_t cursor) | strong |
| switchBuffer() | calls | isDoubleBuffered() | strong |
| switchBuffer() | calls | waitPlotCompletion(bool waitForVSync=false) | strong |
| VDUStreamProcessor::updateMouseVars(MouseDelta * delta) | calls | getMouse() | strong |
| VDUStreamProcessor::updateMouseVars(MouseDelta * delta) | calls | setVDPVariable(uint16_t flag,uint16_t value) | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | resetMousePositioner(uint16_t width,uint16_t height,fabgl::VGABaseController * display) | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | VDUStreamProcessor::bufferCallCallbacks(uint16_t type) | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | VDUStreamProcessor::bufferRemoveCallback(uint16_t bufferId,uint16_t type) | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | changeMode(uint8_t mode) | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | debug_log(const char * format,...) | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | isDoubleBuffered() | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | VDUStreamProcessor::resetAllContexts() | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | VDUStreamProcessor::sendModeInformation() | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | showMouseCursor() | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | switchBuffer() | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | VDUStreamProcessor::updateMouseVars(MouseDelta * delta) | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | calls | waitPlotCompletion(bool waitForVSync=false) | strong |
| Graphics Display | depends-on | Runtime Concurrency | confirmed |
| Physical Ps2 Input | depends-on | Graphics Display | confirmed |
| Physical Ps2 Input | depends-on | Primary Vdp Transport | confirmed |
| Physical Ps2 Input | depends-on | Runtime Concurrency | confirmed |
| VDUStreamProcessor::sendModeInformation() | depends-on | Primary Vdp Transport | confirmed |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | depends-on | Graphics Display | confirmed |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | depends-on | Physical Ps2 Input | confirmed |
| VDUStreamProcessor::vdu case VDU 22 | dispatches-to | VDUStreamProcessor::readByte_t(uint16_t timeout=COMMS_TIMEOUT) | strong |
| VDU 22 | dispatches-to | VDUStreamProcessor::vdu case VDU 22 | confirmed |
| VDUStreamProcessor::vdu case VDU 22 | dispatches-to | VDUStreamProcessor::vdu_mode(uint8_t mode) | strong |
| VDUStreamProcessor::bufferCallCallbacks(uint16_t type) | reads | callbackBuffers | strong |
| VDUStreamProcessor::bufferRemoveCallback(uint16_t bufferId,uint16_t type) | reads | callbackBuffers | strong |
| changeMode(uint8_t mode) | reads | canvasH | strong |
| changeMode(uint8_t mode) | reads | canvasW | strong |
| changeMode(uint8_t mode) | reads | legacyModes | strong |
| changeMode(uint8_t mode) | reads | logicalScaleX | strong |
| changeMode(uint8_t mode) | reads | logicalScaleY | strong |
| changeMode(uint8_t mode) | reads | ttxt_instance | strong |
| changeMode(uint8_t mode) | reads | videoMode | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | reads | _VGAController | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | reads | canvas | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | reads | canvasH | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | reads | canvasW | strong |
| debug_log(const char * format,...) | reads | DBGSerial | strong |
| hideMouseCursor() | reads | _VGAController | strong |
| isDoubleBuffered() | reads | _VGAController | strong |
| VDUStreamProcessor::resetAllContexts() | reads | contextStacks | strong |
| restorePalette() | reads | ttxtMode | strong |
| VDUStreamProcessor::selectContext(uint8_t id) | reads | contextStacks | strong |
| VDUStreamProcessor::sendModeInformation() | reads | canvasH | strong |
| VDUStreamProcessor::sendModeInformation() | reads | canvasW | strong |
| VDUStreamProcessor::sendModeInformation() | reads | videoMode | strong |
| showMouseCursor() | reads | _VGAController | strong |
| showMouseCursor() | reads | mCursor | strong |
| showMouseCursor() | reads | mouseCursors | strong |
| switchBuffer() | reads | canvas | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | reads | _VGAController | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | reads | canvasH | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | reads | canvasW | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | reads | mouseVisible | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | reads | videoMode | strong |
| waitPlotCompletion(bool waitForVSync=false) | reads | canvas | strong |
| Graphics Display | requires-hardware | DMA descriptors and capability-specific heap allocation | confirmed |
| Graphics Display | requires-hardware | ESP32 GPIO matrix | confirmed |
| Graphics Display | requires-hardware | I2S1 register block and interrupt source | confirmed |
| Physical Ps2 Input | requires-hardware | active VGA controller for mouse positioning and cursor rendering | confirmed |
| Physical Ps2 Input | requires-hardware | ESP32 ULP, RTC GPIO, SENS registers, RTC interrupt, queues, and tasks | confirmed |
| Graphics Display | requires-platform-api | FabGL Canvas and VGA2/VGA4/VGA8/VGA16/VGA64 controllers | confirmed |
| Graphics Display | requires-platform-api | FreeRTOS primitive execution task | confirmed |
| Physical Ps2 Input | requires-platform-api | FabGL PS2Controller, Keyboard, Mouse, layouts, and Cursor | confirmed |
| VDUStreamProcessor::readByte_t(uint16_t timeout=COMMS_TIMEOUT) | requires-platform-api | xTaskGetTickCountFromISR() | strong |
| VDUStreamProcessor::sendModeInformation() | sends-packet | PACKET_MODE screen-mode information | confirmed |
| changeMode(uint8_t mode) | writes | ttxtMode | strong |
| changeMode(uint8_t mode) | writes | videoMode | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | writes | canvasH | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | writes | canvasW | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | writes | logicalScaleX | strong |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | writes | logicalScaleY | strong |
| hideMouseCursor() | writes | mouseVisible | strong |
| showMouseCursor() | writes | mouseVisible | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | writes | ttxtMode | strong |
| VDUStreamProcessor::vdu_mode(uint8_t mode) | writes | videoMode | strong |

## Boundaries

| From | Relationship | Omitted target | Stop rule |
|---|---|---|---|
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | calls | function:agon-vdp:updateVGAController(uint8_t%20colours) | stop:depth:4 |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | requires-platform-api | platform-api:external:heap_caps_get_free_size | stop:depth:4 |
| changeResolution(uint8_t colours,const char * modeLine,bool doubleBuffered=false) | writes | variable:agon-vdp:rectangularPixels | stop:depth:4 |
| getVGAColourDepth() | reads | variable:agon-vdp:_VGAColourDepth | stop:depth:4 |
| restorePalette() | calls | function:agon-vdp:resetPalette(const%20uint8_t%20colours[]) | stop:depth:4 |
| restorePalette() | reads | variable:agon-vdp:defaultPalette02 | stop:depth:4 |
| restorePalette() | reads | variable:agon-vdp:defaultPalette04 | stop:depth:4 |
| restorePalette() | reads | variable:agon-vdp:defaultPalette08 | stop:depth:4 |
| restorePalette() | reads | variable:agon-vdp:defaultPalette10 | stop:depth:4 |
| restorePalette() | reads | variable:agon-vdp:defaultPalette40 | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:disableMouse() | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:enableMouse() | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:getKeyboard() | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:getVDPVariable(uint16_t%20flag) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setKeyboardLayout(uint8_t%20region) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setKeyboardState(uint16_t%20delay,uint16_t%20rate,uint8_t%20ledState) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMouseAcceleration(uint16_t%20acceleration) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMouseCursor(uint16_t%20cursor=mCursor) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMouseCursorPos(uint16_t%20x,uint16_t%20y) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMousePos(uint16_t%20x,uint16_t%20y) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMouseResolution(int8_t%20resolution) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMouseSampleRate(uint8_t%20rate) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMouseScaling(uint8_t%20scaling) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setMouseWheelAcceleration(uint32_t%20acceleration) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | calls | function:agon-vdp:setVDPProtocolDuplex(bool%20duplex) | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | reads | variable:agon-vdp:featureFlags | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | reads | variable:agon-vdp:kbRepeatDelay | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | reads | variable:agon-vdp:kbRepeatRate | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | reads | variable:agon-vdp:processor | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | reads | variable:agon-vdp:rtc | stop:depth:4 |
| setVDPVariable(uint16_t flag,uint16_t value) | writes | variable:agon-vdp:controlKeys | stop:depth:4 |
| VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | calls | function:agon-vdp:resolveBufferId(int32_t%20bufferId,uint16_t%20currentId) | stop:depth:4 |
| VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | calls | method:agon-vdp:VDUStreamProcessor::bufferJump(uint16_t%20bufferId,AdvancedOffset%20offset) | stop:depth:4 |
| VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | calls | method:agon-vdp:VDUStreamProcessor::processAllAvailable() | stop:depth:4 |
| VDUStreamProcessor::bufferCall(uint16_t callBufferId,AdvancedOffset offset) | reads | variable:agon-vdp:buffers | stop:depth:4 |
| VDUStreamProcessor::selectContext(uint8_t id) | calls | method:agon-vdp:VDUStreamProcessor::contextExists(uint8_t%20id) | stop:depth:4 |
| VDUStreamProcessor::send_packet(uint8_t code,uint16_t len,uint8_t data[]) | calls | function:agon-vdp:clearVDPVariable(uint16_t%20flag) | stop:depth:4 |
| VDUStreamProcessor::send_packet(uint8_t code,uint16_t len,uint8_t data[]) | calls | function:agon-vdp:isVDPVariableSet(uint16_t%20flag) | stop:depth:4 |
| VDUStreamProcessor::send_packet(uint8_t code,uint16_t len,uint8_t data[]) | calls | method:agon-vdp:VDUStreamProcessor::writeByte(uint8_t%20b) | stop:depth:4 |
| Graphics Display | owns | function:agon-vdp-runtime:change-mode | stop:relation-filter |
| Graphics Display | owns | interrupt:agon-vdp-runtime:vga-isr | stop:relation-filter |
| Graphics Display | owns | task:agon-vdp-runtime:primitive-task | stop:relation-filter |
| Memory And Psram | requires-platform-api | platform-api:reviewed:arduino%20psraminit%20and%20ps_malloc | stop:depth:4 |
| Memory And Psram | requires-platform-api | platform-api:reviewed:esp-idf%20heap_caps%20allocation%20and%20malloc_cap_spiram | stop:depth:4 |
| Memory And Psram | requires-platform-api | platform-api:reviewed:xtensa-specific%20optimized%20unaligned%20access%20when%20available | stop:depth:4 |
| Physical Ps2 Input | owns | function:agon-vdp-runtime:handle-input | stop:relation-filter |
| Physical Ps2 Input | owns | function:agon-vdp-runtime:setup-input | stop:relation-filter |
| Physical Ps2 Input | owns | interrupt:agon-vdp-runtime:ps2-isr | stop:relation-filter |
| Physical Ps2 Input | owns | task:agon-vdp-runtime:keyboard-task | stop:relation-filter |
| Physical Ps2 Input | owns | task:agon-vdp-runtime:mouse-task | stop:relation-filter |
| Primary Vdp Transport | owns | function:agon-vdp-runtime:process-next | stop:relation-filter |
| Primary Vdp Transport | owns | function:agon-vdp-runtime:setup-vdp-protocol | stop:relation-filter |
| Primary Vdp Transport | owns | function:agon-vdp-runtime:vdu-dispatch | stop:relation-filter |
| Primary Vdp Transport | owns | function:agon-vdp-runtime:wait-ez80 | stop:relation-filter |
| Primary Vdp Transport | requires-hardware | physical-facility:reviewed:uart2%20pins,%20rts/cts%20flow%20control,%20receive%20buffer,%20and%20timeouts | stop:depth:4 |
| Primary Vdp Transport | requires-platform-api | platform-api:reviewed:arduino%20hardwareserial%20and%20stream | stop:depth:4 |
| Runtime Concurrency | requires-hardware | physical-facility:reviewed:i2s0,%20i2s1,%20rtc/ulp,%20and%20uart%20interrupt%20sources | stop:depth:4 |
| Runtime Concurrency | requires-platform-api | platform-api:reviewed:esp32%20interrupt%20allocation%20and%20core%20affinity | stop:depth:4 |
| Runtime Concurrency | requires-platform-api | platform-api:reviewed:freertos%20tasks,%20queues,%20semaphores,%20and%20timers | stop:depth:4 |

## Unresolved

- `unresolved:call:function:agon-vdp:changeMode(uint8_t%20mode):init` — Call init() from function:agon-vdp:changeMode(uint8_t%20mode) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):Canvas` — Call Canvas() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):enableBackgroundPrimitiveExecution` — Call enableBackgroundPrimitiveExecution() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):enableBackgroundPrimitiveTimeout` — Call enableBackgroundPrimitiveTimeout() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):get` — Call get() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):getHeight` — Call getHeight() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):getScreenHeight` — Call getScreenHeight() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):getViewPortHeight` — Call getViewPortHeight() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):getWidth` — Call getWidth() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):reset` — Call reset() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false):setResolution` — Call setResolution() from function:agon-vdp:changeResolution(uint8_t%20colours,const%20char%20*%20modeLine,bool%20doubleBuffered=false) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:debug_log(const%20char%20*%20format,...):print` — Call print() from function:agon-vdp:debug_log(const%20char%20*%20format,...) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:getMouse():mouse` — Call mouse() from function:agon-vdp:getMouse() cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:hideMouseCursor():setMouseCursor` — Call setMouseCursor() from function:agon-vdp:hideMouseCursor() cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:isDoubleBuffered():isDoubleBuffered` — Call isDoubleBuffered() from function:agon-vdp:isDoubleBuffered() cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:resetMousePositioner(uint16_t%20width,uint16_t%20height,fabgl::VGABaseController%20*%20display):setupAbsolutePositioner` — Call setupAbsolutePositioner() from function:agon-vdp:resetMousePositioner(uint16_t%20width,uint16_t%20height,fabgl::VGABaseController%20*%20display) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:resetMousePositioner(uint16_t%20width,uint16_t%20height,fabgl::VGABaseController%20*%20display):terminateAbsolutePositioner` — Call terminateAbsolutePositioner() from function:agon-vdp:resetMousePositioner(uint16_t%20width,uint16_t%20height,fabgl::VGABaseController%20*%20display) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getContext` — Call getContext() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getDay` — Call getDay() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getHour` — Call getHour() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getLEDs` — Call getLEDs() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getMinute` — Call getMinute() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getMonth` — Call getMonth() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getSecond` — Call getSecond() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):getYear` — Call getYear() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):selectContext` — Call selectContext() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):sendKeyboardData` — Call sendKeyboardData() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):sendModeInformation` — Call sendModeInformation() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):sendMouseData` — Call sendMouseData() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):setEcho` — Call setEcho() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):setLEDs` — Call setLEDs() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):setTime` — Call setTime() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):setVariable` — Call setVariable() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):toCurrentCoordinates` — Call toCurrentCoordinates() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value):toScreenCoordinates` — Call toScreenCoordinates() from function:agon-vdp:setVDPVariable(uint16_t%20flag,uint16_t%20value) cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:showMouseCursor():end` — Call end() from function:agon-vdp:showMouseCursor() cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:showMouseCursor():setMouseCursor` — Call setMouseCursor() from function:agon-vdp:showMouseCursor() cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:switchBuffer():noOp` — Call noOp() from function:agon-vdp:switchBuffer() cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:switchBuffer():swapBuffers` — Call swapBuffers() from function:agon-vdp:switchBuffer() cannot be resolved safely from lexical context.
- `unresolved:call:function:agon-vdp:waitPlotCompletion(bool%20waitForVSync=false):waitCompletion` — Call waitCompletion() from function:agon-vdp:waitPlotCompletion(bool%20waitForVSync=false) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset):available` — Call available() from method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset):end` — Call end() from method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset):get` — Call get() from method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset):move` — Call move() from method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset):seekTo` — Call seekTo() from method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset):tellBuffer` — Call tellBuffer() from method:agon-vdp:VDUStreamProcessor::bufferCall(uint16_t%20callBufferId,AdvancedOffset%20offset) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::bufferRemoveCallback(uint16_t%20bufferId,uint16_t%20type):erase` — Call erase() from method:agon-vdp:VDUStreamProcessor::bufferRemoveCallback(uint16_t%20bufferId,uint16_t%20type) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::clearContextStack():clear` — Call clear() from method:agon-vdp:VDUStreamProcessor::clearContextStack() cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::readByte_t(uint16_t%20timeout=COMMS_TIMEOUT):pushEcho` — Call pushEcho() from method:agon-vdp:VDUStreamProcessor::readByte_t(uint16_t%20timeout=COMMS_TIMEOUT) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::readByte_t(uint16_t%20timeout=COMMS_TIMEOUT):read` — Call read() from method:agon-vdp:VDUStreamProcessor::readByte_t(uint16_t%20timeout=COMMS_TIMEOUT) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetAllContexts():clear` — Call clear() from method:agon-vdp:VDUStreamProcessor::resetAllContexts() cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):reset` — Call reset() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):resetCharToBitmap` — Call resetCharToBitmap() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):resetFonts` — Call resetFonts() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):resetGraphicsOptions` — Call resetGraphicsOptions() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):resetGraphicsPainting` — Call resetGraphicsPainting() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):resetGraphicsPositioning` — Call resetGraphicsPositioning() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):resetTextCursor` — Call resetTextCursor() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):resetTextPainting` — Call resetTextPainting() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):setCursorBehaviour` — Call setCursorBehaviour() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags):setLogicalCoords` — Call setLogicalCoords() from method:agon-vdp:VDUStreamProcessor::resetContext(uint8_t%20flags) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id):activate` — Call activate() from method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id):back` — Call back() from method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id):begin` — Call begin() from method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id):end` — Call end() from method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id):get` — Call get() from method:agon-vdp:VDUStreamProcessor::selectContext(uint8_t%20id) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::sendModeInformation():getNormalisedViewportCharHeight` — Call getNormalisedViewportCharHeight() from method:agon-vdp:VDUStreamProcessor::sendModeInformation() cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::sendModeInformation():getNormalisedViewportCharWidth` — Call getNormalisedViewportCharWidth() from method:agon-vdp:VDUStreamProcessor::sendModeInformation() cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::updateMouseVars(MouseDelta%20*%20delta):status` — Call status() from method:agon-vdp:VDUStreamProcessor::updateMouseVars(MouseDelta%20*%20delta) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::vdu_mode(uint8_t%20mode):cls` — Call cls() from method:agon-vdp:VDUStreamProcessor::vdu_mode(uint8_t%20mode) cannot be resolved safely from lexical context.
- `unresolved:call:method:agon-vdp:VDUStreamProcessor::vdu_mode(uint8_t%20mode):get` — Call get() from method:agon-vdp:VDUStreamProcessor::vdu_mode(uint8_t%20mode) cannot be resolved safely from lexical context.
