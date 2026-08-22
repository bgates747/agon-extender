# Olimex ESP32-P4-DevKit Rev D1 expansion pinout

This is the text authority used to draw the P4 header cells in
`wiring-diagram.svg`. It was generated from the connectivity in Olimex's
machine-readable Rev-D1 KiCad schematic, not transcribed from the low-resolution
manual image:

`docs/olimex/hardware/ESP32-P4-DevKit-Rev.D1/ESP32-P4-DevKit_Rev_D1.kicad_sch`

The manual image establishes physical orientation. With the Ethernet connector
at the top and USB Serial/JTAG connector at the bottom, EXT1 is on the board's
left and EXT2 is on its right. Both tables therefore run from pin 20 at the
Ethernet end to pin 1 at the USB end.

## EXT1 — board left

| Pin | Schematic net / board function |
|---:|---|
| 20 | `GPIO19` |
| 19 | `GPIO18` |
| 18 | `GPIO17` |
| 17 | `GPIO16` |
| 16 | `GPIO15` |
| 15 | `GPIO14` |
| 14 | `GPIO13` |
| 13 | `GPIO12` |
| 12 | `GPIO11` |
| 11 | `GPIO10` |
| 10 | `GPIO9` |
| 9 | `GPIO8 / I2C_SCL` |
| 8 | `GPIO7 / I2C_SDA` |
| 7 | `GPIO6` |
| 6 | `GPIO5 / SPI_CSn (CS#)` |
| 5 | `GPIO4 / SPI_SCK (CLK)` |
| 4 | `GPIO3 / SD_DET` |
| 3 | `GPIO2 / USER_LED` |
| 2 | `GND` |
| 1 | `+3.3V` |

## EXT2 — board right

| Pin | Schematic net / board function |
|---:|---|
| 20 | `USB_DN` |
| 19 | `USB_DP` |
| 18 | `GND` |
| 17 | `USB1P1_1N (GPIO26)` |
| 16 | `USB1P1_1P (GPIO27)` |
| 15 | `GND` |
| 14 | `ESP_EN` |
| 13 | `GPIO20` |
| 12 | `GPIO21` |
| 11 | `GPIO22` |
| 10 | `GPIO23` |
| 9 | `GPIO32` |
| 8 | `GPIO33` |
| 7 | `GPIO46` |
| 6 | `GPIO47` |
| 5 | `GPIO48` |
| 4 | `GPIO53 / SPI_TX (MOSI)` |
| 3 | `GPIO54 / SPI_RX (MISO)` |
| 2 | `GND` |
| 1 | `+5V` |

The parenthetical GPIO26/GPIO27 names on EXT2 pins 17 and 16 come from the
ESP32-P4 symbol pin functions attached to nets `USB1P1_1N` and `USB1P1_1P`.
They are included to keep the exposed GPIO identity visible without replacing
Olimex's net names.
