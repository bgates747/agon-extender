# NET-009 — Soldered breakout for the Olimex ESP8266

Replace the stacked jumper leads with a short harness and a board-mounted
connector that grips the module firmly. Provide a series resistor position
on each UART signal and test pads for checking the signals with the module
plugged in. Use the current ESP-AT 2.3.0.0 image for the first retest so the
firmware stays fixed while the hardware changes.

## Design specification to prepare

NET-009-016 in the parent task owns completion of the design. Extender will
prepare a schematic, bill of materials and assembly drawing with enough
dimensions and pin labels for Smith to build it. Reuse the existing Pi5 and
female UEXT mating-face drawing and show the existing reset connections.

Specify the connector pitch, square mating-pin dimensions, receptacle type,
retention method and board mounting. Replace the stacked jumper connections
with short single-run leads terminated in properly matched header pins and
receptacles. Record the selected lead lengths and provide strain relief.

Account for the module's existing 200 Ω R5 in its TX path. The new resistor
decision concerns the Pi TX → module RX path: assess whether 200 Ω is
appropriate there. Place that resistor near the Pi's transmitting pin.
Select its value for that driver and lead arrangement, using received edge
shape and transfer results. Include ground and signal probe pads, decoupling
details and the power/ground path in the drawing.

## Construction and matched comparison

1. Smith builds the breakout with a soldered **2×5 square-pin header**
   that mates with the module's socket. Use the pin 1 mark and the viewed
   face in the [existing wiring drawing](PI5-ESP8266-WIRING.png) to orient the
   header. Use one short harness to the Pi5, with a ground conductor close
   to the signal wires. Provide strain relief so cable movement does not
   pull on the module contacts.
2. Wire only the four connections below. Label each signal from the
   transmitting or receiving device's viewpoint. Add probe pads for both
   signal lines and ground.

   | Pi5 header | Module UEXT | Series resistor position |
   | --- | --- | --- |
   | Physical 1, 3.3 V | Pin 1, 3.3 V | Direct |
   | Physical 6, ground | Pin 2, ground | Direct |
   | Physical 8, GPIO14 TX | Pin 3, module RX | Select a series value near the Pi TX pin; assess 200 Ω |
   | Physical 10, GPIO15 RX | Pin 4, module TX | Direct; the module already has 200 Ω at R5 |

3. Extender's design uses the module's existing TX resistor and specifies
   the added Pi-TX-to-module-RX resistor. Evaluate 200 Ω as a candidate;
   equal values on the two paths are not an electrical requirement because
   the Pi and ESP8266 output drivers differ. Check ringing and edge settling
   at the module RX pin at the selected baud before finalizing the value.
   The soldered connector and short harness address intermittent contact.
   See [Olimex's connector documentation](https://www.olimex.com/Products/IoT/ESP8266/MOD-WIFI-ESP8266/open-source-hardware),
   [Olimex's Rev B1 schematic](https://github.com/OLIMEX/ESP8266/blob/master/HARDWARE/MOD-WIFI-ESP8266/MOD-WIFI-ESP8266%20revision%20B1/MOD-WiFi-ESP8266_Rev_B1.pdf)
   and [TI's series termination guidance](https://www.ti.com/lit/an/scaa045a/scaa045a.pdf).
4. Before power is applied, Smith checks continuity, the actual resistor
   values, connector orientation and isolation between 3.3 V and ground.
   Extender verifies the Pi UART is idle before Smith swaps the harness.
   Leave GPIO17 and its separate reset wiring in place.
5. Extender verifies `AT` and the current firmware over the replacement
   harness, then repeats the [two failed uploads](MODEM-FLASH-R01.md#pi-to-pi-comparison)
   with the same Pi TCP peer and frame checks. Run 230,400 baud for 3 s and
   115,200 baud for 30 s. Record cable length, populated resistors, valid
   frame counts and any first divergence. Keep the firmware fixed for this
   comparison. If the runs pass, resume the separate baud and duration
   ladder with the new wiring recorded.
