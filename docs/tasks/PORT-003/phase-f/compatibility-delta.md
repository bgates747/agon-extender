# PORT-003 Phase F compatibility delta

## Retained behavior

Phase F compiles the official Agon VDP `v2.16.0` setup/loop lifecycle,
`VDUStreamProcessor`, header-defined VDU handlers, context and buffer state,
screen facade, Teletext implementation, mode table, Canvas API, primitive
executor, and General Poll startup gate. It adds no VDU command byte, changes
no official command number, and defines no replacement application-visible VDU
protocol.

The P4 display backend continues the Phase A--E decisions: official logical
pixels use the retained native packed formats; official mode selection and
context lifecycle remain authoritative; and the project-owned frame service
replaces only the unavailable classic VGA physical frame engine. Phase F does
not apply the rejected lifecycle robustness changes preserved by
`UPSTREAM-001`.

## Required P4 and boot adaptations

The retained implementation is header-defined and tightly coupled to classic
ESP32 peripherals. The `AGON_EXTENDER_P4_BOOT` build boundary therefore makes
the following explicit substitutions while leaving the official non-P4 path
intact:

1. Official files that include the broad FabGL aggregate use the narrow
   project P4 compatibility surface. The selected vdp-gl closure is limited to
   Canvas, code pages, and the common bitmapped display controller.
2. The retained `agon_screen.h` facade constructs the project P4 display
   controller with logical-plane and immutable-snapshot allocators.
3. Physical PS/2 acquisition and processed input are replaced by a no-device
   adapter. Phase F executes no keyboard or mouse polling and claims no input
   compatibility.
4. Physical audio handlers bind to an explicit unavailable adapter. Phase F
   claims no audio output.
5. Updater, YMODEM, hex loader, ZDI, and terminal hardware are excluded through
   an explicit unavailable-maintenance boundary. Phase F claims none of those
   maintenance or terminal facilities.
6. The stock UART transport is replaced by a disconnected Arduino `Stream`.
   The official parser and General Poll call sites remain linked, but no VDU
   ingress or return packet can cross a physical wire in this target.
7. The retained Arduino lifecycle starts the project-owned wired network
   service only after display/parser initialization. Network failure reports
   through USB Serial/JTAG diagnostics and does not disable retained logical
   VDP execution.

These substitutions touch fifteen upstream-shaped files. Their paths and
byte-level differences from `agon-vdp@v2.16.0` are declared as
`vendored-patched` in `docs/dependencies/reviewed/source-baselines.yaml`; all
new behavior remains under `vdp/video/extender/`.

## New output behavior outside the VDU wire contract

At a quiescent frame boundary, the P4 display controller may compose a complete
packed RGB888 presentation into one of three fixed-capacity PSRAM slots. A
browser-video provider leases only immutable complete snapshots and prefixes
them with the frozen 32-byte `EVF1` header. The PORT-006 service owns Ethernet,
DHCP, HTTP, WebSocket lifecycle, one-client credit, and opaque sends; it cannot
interpret pixels or call into the VDP while holding its state lock.

The P4 directly serves the project browser interface. Browser JavaScript
validates the complete `EVF1` message, presents it through WebGL2, and grants
at most one next-frame credit after presentation. A missing, slow, malformed,
or disconnected browser can cause bounded presentation drops but cannot queue
unbounded frames or block official logical frame progression.

This browser-video surface is a new Extender output API. It is not visible as
a new VDU command and does not qualify any eZ80-to-P4 transport.

## Deliberate Phase F nonclaims

1. The target has no physical VDU ingress, return UART, EMOS route, Agon
   connection, sysvar update, or operating-mode transition. PORT-008 owns the
   first official-command transport slice.
2. Physical keyboard, mouse, joystick, audio, terminal/ZDI, updater, storage,
   Wi-Fi, OTA, authentication, TLS, multiple video clients, and internet
   exposure are absent or deferred to their owning tasks.
3. Classic VGA, CVBS, I2S display/audio, PS/2, DMA scanout, signal-table, and
   VSYNC ISR implementations remain vendored for provenance but are not linked
   into the Phase F application closure.
4. Arduino Ethernet packaging contributes four inert Wi-Fi global
   constructor/destructor symbols. No selected project source references
   Wi-Fi and no operational Wi-Fi API is linked.
5. Host and compile/link evidence does not qualify target runtime, electrical
   behavior, DHCP service, browser delivery from hardware, memory behavior on
   the P4, or production throughput. Those claims begin only with the separately
   approved P4-only deployment procedure.

