# PORT-003 bitmapped-controller consumers

Generated projection; the YAML dependency slice is authoritative.

## Summary

- Nodes: 16
- Edges: 31
- Explicit boundaries: 36
- Unresolved records: 0
- Node kinds: file=15, type=1

## Nodes

| Kind | ID | Label | Port disposition |
|---|---|---|---|
| file | `file:vdp-gl:src/canvas.h` | src/canvas.h | — |
| file | `file:vdp-gl:src/collisiondetector.h` | src/collisiondetector.h | — |
| file | `file:vdp-gl:src/devdrivers/mouse.cpp` | src/devdrivers/mouse.cpp | — |
| file | `file:vdp-gl:src/devdrivers/mouse.h` | src/devdrivers/mouse.h | — |
| file | `file:vdp-gl:src/dispdrivers/vga16controller.h` | src/dispdrivers/vga16controller.h | — |
| file | `file:vdp-gl:src/dispdrivers/vga2controller.h` | src/dispdrivers/vga2controller.h | — |
| file | `file:vdp-gl:src/dispdrivers/vga4controller.h` | src/dispdrivers/vga4controller.h | — |
| file | `file:vdp-gl:src/dispdrivers/vga64controller.h` | src/dispdrivers/vga64controller.h | — |
| file | `file:vdp-gl:src/dispdrivers/vga8controller.h` | src/dispdrivers/vga8controller.h | — |
| file | `file:vdp-gl:src/dispdrivers/vgabasecontroller.h` | src/dispdrivers/vgabasecontroller.h | — |
| file | `file:vdp-gl:src/dispdrivers/vgacontroller.h` | src/dispdrivers/vgacontroller.h | — |
| file | `file:vdp-gl:src/dispdrivers/vgapalettedcontroller.h` | src/dispdrivers/vgapalettedcontroller.h | — |
| file | `file:vdp-gl:src/displaycontroller.cpp` | src/displaycontroller.cpp | — |
| file | `file:vdp-gl:src/displaycontroller.h` | src/displaycontroller.h | — |
| file | `file:vdp-gl:src/fabgl.h` | src/fabgl.h | — |
| type | `type:vdp-gl:fabgl::BitmappedDisplayController` | fabgl::BitmappedDisplayController | — |

## Relationships

| From | Relationship | To | Confidence |
|---|---|---|---|
| src/displaycontroller.h | defines | fabgl::BitmappedDisplayController | confirmed |
| src/canvas.h | includes | src/displaycontroller.h | confirmed |
| src/collisiondetector.h | includes | src/displaycontroller.h | confirmed |
| src/devdrivers/mouse.cpp | includes | src/devdrivers/mouse.h | confirmed |
| src/devdrivers/mouse.cpp | includes | src/displaycontroller.h | confirmed |
| src/devdrivers/mouse.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vga16controller.h | includes | src/dispdrivers/vgapalettedcontroller.h | confirmed |
| src/dispdrivers/vga16controller.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vga2controller.h | includes | src/dispdrivers/vgapalettedcontroller.h | confirmed |
| src/dispdrivers/vga2controller.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vga4controller.h | includes | src/dispdrivers/vgapalettedcontroller.h | confirmed |
| src/dispdrivers/vga4controller.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vga64controller.h | includes | src/dispdrivers/vgapalettedcontroller.h | confirmed |
| src/dispdrivers/vga64controller.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vga8controller.h | includes | src/dispdrivers/vgapalettedcontroller.h | confirmed |
| src/dispdrivers/vga8controller.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vgabasecontroller.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vgacontroller.h | includes | src/dispdrivers/vgabasecontroller.h | confirmed |
| src/dispdrivers/vgacontroller.h | includes | src/displaycontroller.h | confirmed |
| src/dispdrivers/vgapalettedcontroller.h | includes | src/dispdrivers/vgabasecontroller.h | confirmed |
| src/dispdrivers/vgapalettedcontroller.h | includes | src/displaycontroller.h | confirmed |
| src/displaycontroller.cpp | includes | src/displaycontroller.h | confirmed |
| src/fabgl.h | includes | src/collisiondetector.h | confirmed |
| src/fabgl.h | includes | src/devdrivers/mouse.h | confirmed |
| src/fabgl.h | includes | src/dispdrivers/vga16controller.h | confirmed |
| src/fabgl.h | includes | src/dispdrivers/vga2controller.h | confirmed |
| src/fabgl.h | includes | src/dispdrivers/vga4controller.h | confirmed |
| src/fabgl.h | includes | src/dispdrivers/vga64controller.h | confirmed |
| src/fabgl.h | includes | src/dispdrivers/vga8controller.h | confirmed |
| src/fabgl.h | includes | src/dispdrivers/vgacontroller.h | confirmed |
| src/fabgl.h | includes | src/displaycontroller.h | confirmed |

## Boundaries

| From | Relationship | Omitted target | Stop rule |
|---|---|---|---|
| src/canvas.h | includes | file:vdp-gl:src/canvas.cpp | stop:depth:2 |
| src/canvas.h | includes | file:vdp-gl:src/terminal.h | stop:depth:2 |
| src/collisiondetector.h | includes | file:vdp-gl:src/collisiondetector.cpp | stop:depth:2 |
| src/collisiondetector.h | includes | file:vdp-gl:src/scene.h | stop:depth:2 |
| src/devdrivers/mouse.h | includes | file:vdp-gl:src/comdrivers/ps2controller.cpp | stop:depth:2 |
| src/devdrivers/mouse.h | includes | file:vdp-gl:src/terminal.cpp | stop:depth:2 |
| src/dispdrivers/vga16controller.h | includes | file:vdp-gl:src/dispdrivers/vga16controller.cpp | stop:depth:2 |
| src/dispdrivers/vga16controller.h | includes | file:vdp-gl:src/fabutils.cpp | stop:depth:2 |
| src/dispdrivers/vga2controller.h | includes | file:vdp-gl:src/dispdrivers/vga2controller.cpp | stop:depth:2 |
| src/dispdrivers/vga2controller.h | includes | file:vdp-gl:src/fabutils.cpp | stop:depth:2 |
| src/dispdrivers/vga4controller.h | includes | file:vdp-gl:src/dispdrivers/vga4controller.cpp | stop:depth:2 |
| src/dispdrivers/vga64controller.h | includes | file:vdp-gl:src/dispdrivers/vga64controller.cpp | stop:depth:2 |
| src/dispdrivers/vga64controller.h | includes | file:vdp-gl:src/fabutils.cpp | stop:depth:2 |
| src/dispdrivers/vga8controller.h | includes | file:vdp-gl:src/dispdrivers/vga8controller.cpp | stop:depth:2 |
| src/dispdrivers/vgabasecontroller.h | includes | file:vdp-gl:src/dispdrivers/vgabasecontroller.cpp | stop:depth:2 |
| src/dispdrivers/vgacontroller.h | includes | file:vdp-gl:src/dispdrivers/vgacontroller.cpp | stop:depth:2 |
| src/dispdrivers/vgacontroller.h | includes | file:vdp-gl:src/dispdrivers/vgatextcontroller.h | stop:depth:2 |
| src/dispdrivers/vgacontroller.h | includes | file:vdp-gl:src/fabutils.cpp | stop:depth:2 |
| src/dispdrivers/vgapalettedcontroller.h | includes | file:vdp-gl:src/dispdrivers/vgapalettedcontroller.cpp | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/agon_audio.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/agon_fonts.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/agon_ps2.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/agon_screen.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/audio_channel.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/context.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/context/cursor.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/context/fonts.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/context/graphics.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/context/viewport.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/enhanced_samples_generator.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/sprites.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/vdu_audio.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/vdu_sprites.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/vdu_stream_processor.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/vdu_sys.h | stop:depth:2 |
| src/fabgl.h | includes | file:agon-vdp:video/video.ino | stop:depth:2 |
