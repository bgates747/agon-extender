# ESP8266 iterative firmware bring-up

Smith explicitly continues NET-008 until the real ESP8266 works and its bandwidth
limits are measured. A failed diagnostic is an iteration result, not an instruction
to restore normal P4 firmware and stop. Keep the identified development image
installed while this held work continues; restore ordinary operation only when
Smith requests it or the selected testing work is finished.

## Current selected correction

1. Smith suspects TX/RX wires were crossed and explicitly selects swapping the
   P4 firmware assignments instead of rewiring when both pins support it.
   Set P4 UART2 TX=GPIO48 and RX=GPIO47. Both EXT1 contacts are GPIO-matrix pins;
   the pinned IDF driver validates both as output-capable and routes UART TX/RX.
2. Release GPIO47/48 as inputs before assigning the swapped UART, then enable
   only TX48 as an output. Do not swap the physical wires or drive both pins.
   Existing mainboard transport pins, fixed3.3V LDO4 bank and other components
   retain their own allocation. No mainboard MOS or VDP firmware change.
3. Build an exact retained diagnostic, selectively install/read back only its
   affected P4 application sectors, then explicitly START one bounded AT/GMR
   and repeated-AT sequence. Freeze the new source before compilation; retain
   actual first-failure164 separately. No automatic invocation on boot.
4. Leave this development image installed after this iteration. Stop/join host
   serial/programming children when the bounded operation ends; preserve actual
   installed-state records and Smith's bench hold. This supersedes the earlier
   one-shot restore-after-each-attempt plan.
5. If swapped pins establish positive AT/GMR communication, retain exact modem
   identity and framing/command results, then prepare finite serial and network
   throughput measurements with host/modem/P4 scopes separated. Later bandwidth
   configurations remain explicit named iterations; do not claim a link limit
   from a short AT exchange.

## Source contracts

The retained ESP-IDF5.5.5 commit
`b774170ff46c393eeb5e495ea37936038d3f4f4f`,
`components/esp_driver_uart/src/uart.c:uart_set_pin` checks GPIO output validity,
routes TX through `esp_rom_gpio_connect_out_signal`, enables RX input and routes
it through `esp_rom_gpio_connect_in_signal`. No dedicated TX/RX role is required
for these header pins. Existing board/schematic mapping and full harness remain
in [the task-only pin record](PIN-SELECTION.md).

The original164 AT timeout is not proof of crossed wires. The swapped physical
run must establish the actual result. Human-reported wiring, observed byte
exchange and electrical/throughput limits remain separate facts.

## Wiring inspection pause and compiler work

Smith subsequently notes that the ESP8266 end may also be crossed and will
check it. Prepare the swapped build independently; do not drive modem UART
pins until his physical endpoint check resolves which TX/RX pairing is present.
Do not infer a result from elapsed time. Normal P4 firmware currently leaves
these unused pins undriven. The bench remains held.

Compile only: pinned Pi-native IDF/toolchain already used for the first probe,
expected under90s with600s bound and under2GiB memory. Retain identified binary,
manifest and original child waits; release compiler custody and notify the next
owner after owned compiler processes stop. Compiler work does not touch hardware.

## Latest Author direction supersedes the inspection pause

Smith explicitly says to do the swapped-assignment test first, check the modem
end later, and **not restore original firmware** afterward. Proceed with the
identified TX48/RX47 diagnostic under the existing admitted hold. Its boot and
post-test retirement keep both modem pins as inputs; only the explicit bounded
UART exchange enables TX48. Keep the development application installed after
success or failure; do not run the earlier install/test/restore helper unchanged.
