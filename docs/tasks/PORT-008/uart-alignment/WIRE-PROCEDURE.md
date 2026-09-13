# U12 — pure-data wire attribution

Experimental continuation of the frozen UART alignment plan. RX changes leave
approximately31KB/s forward throughput; return FIFO refill improves the reply
burst but does not reach stock. Obtain wire evidence before another speculative
transport change. No renderer or EMOS changes in this procedure.

## Channel verification and ownership

1. Reuse HW-002's maintained generic header-pinwalk assembly unchanged. Prepare
   an isolated boot-entry variant: mode3 belongs in external startup; remove the
   entry's VDU22; require and consume an owned one-shot SD marker before GPIO;
   after the walk release pins, print completion on mainboard VGA and remain
   idle until the existing Pi reset. Retain source/build hashes. The original
   diagnostic and `/bin/pinwalk.bin` remain unchanged. PD4–PD7/PB5 are still the
   documented isolated legacy walk outputs; no new pin assignment is introduced.
2. Before editing startup, exit the current SD child and launch sdserve directly
   from the CLI. Preserve exact `/autoexec.txt` and any existing `.p17bak`, both
   locally and under fresh owned SD names, with readback. Only then clear its
   old service backup slot and install a guarded one-shot branch. The marker
   is deleted by the application **before** the walk; subsequent recovery reset
   follows ordinary startup. Do not edit a batch file held open by MOS.
3. Put P4 into its existing USB ROM download mode, without flashing. Through the
   ROM register interface, disable output on only the eight connected GPIOs and
   select GPIO matrix input mode. Use IDF5.5.5's ESP32-P4 hardware-v1 register
   definitions: clear GPIO enable bits, select GPIO output256 with OEN_SEL1,
   select IO_MUX function1 and input-enable. Read back every value and both
   enable registers. Keep ROM running with its UART console firmware stopped;
   do not assume reset defaults or restore P4 on a timer. No mainboard walk
   starts until all eight endpoints are verified inputs.
4. Start the existing FX2 capture at100kHz/all8channels, then reset the Agon once
   through the verified Pi circuit. Acquire the complete walk plus at least
   five quiet seconds, with a60second overall capture. Preserve exact sample
   count and failures; inspect actual pulses instead of applying an old map.
   Use the retained legacy analyzer to verify the observed one-through-eight
   pulse mapping. No cable moves, parallel protocol, buffer-OE switching or
   obsolete legacy pin assignments are imported.
5. After acquisition proves the completed walk/quiet tail, explicitly resume
   P4's unchanged installed application, then reset Agon for ordinary startup.
   Establish fresh neutral keyboard admission. Exit the startup SD child,
   relaunch directly, restore exact original startup and its pre-test backup,
   verify both byte-for-byte, and prove a normal boot/SD recovery. Preserve the
   temporary files and journals as evidence; no diagnostic firmware remains
   installed by this channel check.

## UART acquisition

1. Use the measured pure-data fixture/probe pair and the verified channel map.
   Freeze a short marked invocation before capture. No browser output, serial
   observer, SD reads/writes inside a timed transfer or independent UART owner.
2. Capture all four existing TX/RX/RTS/CTS wires at24MHz with a bounded extent.
   Require complete expected payload bytes, valid8N1framing and packet sequence.
   Decode with the retained sample-level method and compare to sigrok decoding.
3. Report wire byte occupancy, inter-byte idle with receiver permission, and
   idle under receiver backpressure separately. Check permission at each start
   bit. Attribute each handshake to its receiver; UART return has the opposite
   owner from forward UART. Neither digital capture nor a clean byte stream
   alone proves analogue signal integrity or a cable-length diagnosis.
4. Compare direction-specific wire spans with the matching application result;
   MOS clock has16.7ms quantum. Retain sample indices and capture hashes. A
   cross-run inference from old graphics data must not substitute for this
   pure-data measurement. Only then select any remaining software work or
   record a bounded wiring limitation for human follow-up.

Input-only ROM register adaptation follows Espressif's `gpio_reg.h`,
`io_mux_reg.h`, `reg_base.h` and `gpio_sig_map.h` for the selected silicon. It
is a temporary ownership safeguard for the existing fixture, not a production
GPIO or UART API. Stable USB/specimen identity and exact host commands remain
in the ignored bench record. If input verification, acquisition or recovery
fails, preserve the state and diagnose before repeating a reset or capture.

### Short invocation frozen before acquisition

Use optional `wire` selection of the existing application: one repetition,
PRNG pattern3, one65535byte forward upload per route followed by one256packet
return per route. The existing forward/reverse functions, seed0x12345678,
probe requests, EMOS APIs, deadlines and recovery remain unchanged. Expected
CSV order is forward/Legacy, forward/ExCom, reverse/Legacy, reverse/ExCom;
four exact rows and terminal recovery0 are required. Token2 identifies the
ExCom forward window; token4 identifies the ExCom return window. Both are
visible in the existing privateEE requests, so no extra UART marker is added.

The external batch configures both displays to mode20, loads the fixture and
returns to foreground sdserve. Capture starts before its CLI EXEC and requires
24MHz ×720million samples. Use the newly verified map, preserve physical bit
positions, write uncompressed samples during acquisition, then archive them.
No reset, browser, serial observer or SD service traffic during timed sections.
Run control and result collection happen outside those sections. Decode and
check all65535forward bytes, the three relevant reply records, and all257return
records; exclude unrelated keyboard/lease traffic by packet type and window.
All captured valid-frame payloads must agree with the independent decoder.
