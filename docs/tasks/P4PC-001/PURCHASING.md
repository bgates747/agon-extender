# P4-PC purchasing and companion experiment

Author reports ESP32-P4-PC backordered from Mouser US on September 18, 2026.
No receipt or delivery date is confirmed. Mouser US is preferred, DigiKey US
secondary. Other items below are suggestions, not reported purchases.

## P4-PC accessories

Use existing full-size HDMI and Ethernet cables if available. Provide a USB-C
data/power connection; Olimex recommends USB-CABLE-AM-USB3-C in its manual.
No separate MIPI-HDMI board or DSI ribbon is required for onboard HDMI.
PoE module, battery, LCD and camera are optional and not needed for this task.

[Official board and documentation](https://www.olimex.com/Products/IoT/ESP32-P4/ESP32-P4-PC/open-source-hardware).
[Olimex USB cable Mouser lookup](https://www.mouser.com/c/?q=USB-CABLE-AM-USB3-C).

Defer special harness purchases until PC03 establishes connector genders and
pin allocation. Plan header-to-breadboard breakouts for Agon and P4-PC, then
short cross-connections and only electrically justified pullups/pulldowns.
A straight UEXT cable is not a qualified Extender connection.

## Optional Pico/Cowbell experiment

Author reports owning original RP2040 Pico SC0915 and Adafruit HSTX Cowbell 6363.
The proposed new processor board is RP2350 Pico 2, not another RP2040 Pico.

| Quantity | Item | Mouser US link |
| --- | --- | --- |
| 1 | Pico 2 with headers, SC1632 / 358-SC1632 | [SC1632](https://www.mouser.com/en/ProductDetail/Raspberry-Pi/SC1632?qs=jcD%2FCkGBYeOeITPoQs%252BB3Q%3D%3D) |
| 1 set if absent | Adafruit 5583: two separate 20-pin female socket strips | [5583](https://www.mouser.com/es/ProductDetail/Adafruit/5583?qs=T%252BzbugeAwjicPo%2FCTvtw2w%3D%3D) |
| 1 if absent | P571-006-MINI, mini-HDMI to full-size HDMI | [Lookup](https://www.mouser.com/c/?q=P571-006-MINI) |
| 1 if absent | MB-A-1M-BK, USB-A to Micro-B data cable | [Cable](https://www.mouser.com/en/ProductDetail/Connective-Peripherals/MB-A-1M-BK?qs=rSMjJ%252B1ewcRtebLUUuIRgw%3D%3D) |

Stock/price/checkout not confirmed for every accessory. Socket headers may
already be fitted; review [Adafruit assembly choices](https://learn.adafruit.com/adafruit-picowbell-hstx-dvi-output/pico)
before ordering. Stacking headers are an alternative if GPIO access requires it.
The Cowbell connector is mini-HDMI, not micro-HDMI. Pico uses Micro-USB;
P4-PC uses USB-C. Existing RP2040 can remain available for bench automation.

A Pico/Cowbell demonstration does not establish a P4 frame receiver. Transport,
framebuffer and firmware development would be separate work, not an off-the-shelf
MIPI substitute. No such implementation is authorized by creating this record.
