# Native P4 board configuration

## Executive summary

`scripts/build_p4.py --board NAME` selects a revisioned JSON file here and
generates compile-time constants for the shared VDP sources. Board selection
is independent of the software/source profile. The DevKit remains the default;
P4-PC Rev C is a candidate, not a qualified production target.

| Board | Configuration identity | Supported software profiles |
|---|---|---|
| `p4-devkit` | `olimex-p4-devkit-revd1-r01` | Console, MOS recovery, bounded parallel qualification |
| `p4-pc` | `olimex-p4-pc-revc-r01` | Console only |

## Inputs and outputs

1. `transport.data` lists D0–D7 in logical bus order. The P4 UART uses D0 as
   RX, D1 as TX, D2 as CTS and D3 as RTS. EMOS continues to coordinate ownership;
   these are shared pads, not independent UART and parallel wires.
2. `clock`, `valid` and `ready` identify parallel handshake pads. The ordinary
   console fences them as inputs but does not install the historical parallel
   qualification transport. `isolation` retains DevKit's old three enable-pad
   fence; the direct PC harness declares none. PC builds of the buffered
   qualification and recovery profiles are rejected.
3. `ethernet`, `sd` and `usb` describe the reviewed onboard peripherals.
   `sdkconfig_overrides` is restricted to reviewed USB hub settings. Both boards
   use external RMII clock GPIO50; changing the clock wiring requires further
   backend review, not just an arbitrary config integer.
4. `reserved_gpios`, physical header metadata and optional sensing conditions
   bound transport allocation. The PC profile avoids the USB pair, LED, audio,
   Ethernet, SD, bridge/control connections and flash pads.
5. The builder hashes this file and emits `board.json` plus a generated C++
   header in a fresh output. Those generated copies are evidence, not editable
   inputs. Changing a controlled mapping requires a new configuration revision
   and renewed wiring review; no historical harness is silently rewritten.

## P4-PC direct mapping

The [wiring diagram and mapping table](../../../hardware/designs/light2-p4pc-harness-draft/README.md)
retain the original allocation in `p4-pc.json`: D0–D7 GPIOs
17,18,19,20,32,33,36,46; READY_N/CLOCK/VALID_N 15/14/16;
UART TX/RX/RTS/CTS 18/17/20/19. The Author arranged the bench to suit the
original diagram and withdrew the ascending-PC alternate proposal before
firmware changes. The drawing and earlier build outputs therefore match the
unchanged compile-time profile. Physical qualification remains pending.

Five consecutive odd-side contacts and six even-side contacts preserve the
Agon signal ordering. EXT1-19/GPIO47 and EXT1-20/GPIO48 remain spare. The Author
requests omission of the old 220 Ω series resistors and reports approximately
15 kΩ fitted pull resistors. The later DevKit direct-harness record specifies
eight 15 kΩ pull-ups on PC0–PC7 to Agon 3.3 V; earlier three handshake biases
are a different circuit. This board file allocates pins only; it does not
certify resistor placement, either-order power behavior or a finished harness.
GPIO20 battery sensing and GPIO32 external-power sensing must remain
disconnected. Independently powered positive rails must not be joined.

The manufacturer's Rev C schematic and manual are indexed in
[the hardware references](../../../docs/hardware/esp32-p4-pc/README.md).
USB host uses the dedicated HS connection through the onboard hub, with active
low reset on GPIO21, a 20 ms assertion and 200 ms recovery matching Olimex's
factory USB test. USB Serial/JTAG remains separate. The Author selects the four onboard USB-A ports for keyboard attachment, with
one active keyboard at a time. Enumeration and reconnect checks on each port
are pending hardware gates. Neither board profile enables HDMI.

The historical hybrid build path retains its original DevKit literals for
bounded reproduction. It does not support native board selection. Standalone
task demos retain their own experimental configuration and are not these
ordinary VDP profiles.

The pending PC keyboard experiment uses the explicit native build flag
`--usb-fsls-only`; it does not revise this pin profile. See the
[build guide](../../../docs/building.md) for the source-bound IDF 5.5.5
backport, 12 Mbit/s hub-link limit and hardware-test boundary. Default builds
keep the existing USB speed selection.
