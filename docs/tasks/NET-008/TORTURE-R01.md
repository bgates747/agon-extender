# ESP8266 bidirectional baud ladder and sustained integrity test

Smith selects an actual P4/ESP8266/Pi5 torture test: increase UART baud through
short checked exchanges until an error or the Agon-exact1152000 baud ceiling,
then step down after error and lengthen the successful rate to a full minute.
Extender owns this work. Keep the working wiring, development firmware and
Smith-held bench. C8 comparison and possible UART1 multiplexing are later work.

## Direct authority and scope

1. Smith explicitly authorizes CRC checking in both directions: the Pi5 checks
   incoming P4 data and the P4 checks incoming Pi5 data. This is an exception
   for this test's application transfers through ESP8266/Wi-Fi/TCP, not a blanket
   change to EMOS/P4 control framing or the project's no-CRC default.
2. Physical path: P4 UART2 TX48/orange and RX47/teal, existing4-wire ESP8266,
   its actual AT1.3.0.0/SDK2.0.0 modem firmware, Wi-Fi and a finite Pi5 TCP peer.
   No flow-control pins exist on this modem header; use8N1/noRTSCTS throughout.
3. Adjust current UART baud through AT+UART_CUR only; never save new UART or
   Wi-Fi defaults, flash/reset the ESP8266, change mainboard firmware/startup,
   replace unchanged components or silently use P4 Ethernet as the data path.
   Reuse actual associated Wi-Fi when available. Missing network setup is a
   concrete prerequisite, not a serial-rate failure.
4. The development image remains installed after each iteration by explicit
   instruction. Retire UART drive and stop owned captures/clients after bounded
   cases; record the module's actual current baud for the next command.
   Keep the bench held until Smith explicitly releases it. No automatic rollback.

## Selected sequence and acceptance

1. Rates:115200,230400,384000,576000,1152000 baud. They correspond to integer
   divisors10,5,3,2,1 of the standard Agon18.432MHz clock divided by16. Record
   the actual P4 programmed/readback rate separately; do not equate this source
   arithmetic with physical clock calibration or a successful C8 run.
2. At each rate first establish bounded AT/connection readiness, then run short
   simultaneous upload/download data (at least2s active per direction, with a
   one-second producer margin). Stop ascending on the first CRC, sequence,
   framing, UART overflow/parity/break, missing/truncated data or timeout error.
   Preserve exact error, case, data/counters and trace; do not relabel a failed
   rate or retry it until it happens to pass.
3. Candidate is the immediately preceding successful rate, or1152000 if every
   short rung passes. Run progressively10s,30s,60s active checks, using2s sender
   margin on the final60s check to ensure both receive windows cover a minute.
   A longer-run error backs down one rung and repeats this duration progression.
   A115200 failure means no rate is qualified; stop with the concrete evidence.
4. Success requires both endpoints to verify all received frames, byte counts,
   frame order and CRC32, with no UART faults, drops, resync, omissions or
   incomplete direction. The final receive windows at both endpoints must each
   cover at least60s of ongoing transfer. Test preparation, baud switching,
   connection setup, producer/receiver drainage and cleanup are separate timings.
5. Use deterministic varied binary payloads and explicit frame length/sequence.
   CRC32/IEEE covers header identity/sequence/length plus payload; validate
   implementations against standard vectors and the actual shared codec.
   Distinguish a receiver's CRC check from sender submission or TCP SEND OK.
   Record both endpoint results and useful payload bytes/s separately from
   framed serial bytes and nominal8N1 capacity (baud/10 bytes/s).
6. Record highest qualifying **tested** baud for this exact combination and
   workload, as Smith's requested acceptance result. Do not claim a universal
   physical limit, arbitrary-day reliability or C8 performance. If1152000 passes,
   call it the selected test ceiling, not proof the P4/ESP8266 cannot go higher.

## Progress, bounds and recovery

1. P4 and Pi5 report elapsed time/bytes/frames/errors at least once per second
   during an active test. A sleeping host or unchanged UI is not progress.
2. Each connection/control wait is bounded; data cases have the requested active
   duration plus bounded drain/cleanup. Whole ladder and backoff progression
   have a finite2700s ceiling. No automatic clock extension, application replay
   or firmware restoration follows a timeout.
3. For data-mode cleanup stop producers, join owned tasks, retire UART safely
   and use the documented guarded +++ escape/AT close sequence. Keep any failed
   case intact; distinguish cleanup failure from data-integrity failure. Actual
   known baud and command/data state remain explicit between cases.
4. Pi compiler work follows its separate FIFO, expected under120s with600s
   bound/under2GiB. Native codec/host-peer tests precede physical installation.
   The modest Pi TCP peer is part of this authorized bench test, not an emulator
   or unrelated heavy workload. Retain genuine parent waits and close owned
   sockets/readers/reset holders without releasing Smith's hardware hold.

## Optional wire observation selected by Smith

Smith offers spare sniffers; use two receive-only channels on GPIO48/P4TX and
GPIO47/P4RX, plus existing common ground, without power/TX drive. Actual channel
numbers/colours and attachment remain pending his construction report. Keep
existing probe assignments intact. Verify the instrument's input-only mode,
current supported sample rate and host identity before acquisition. Wire traces
can distinguish framing/baud/byte-path faults from endpoint parser/CRC failures;
they do not replace the two endpoint integrity checks. Capture only after any
secret Wi-Fi setup, keep trace data private and record its timing/loading scope.

## Bounded source references

1. Official MOS v3.0.2 reference `src/uart.h` MASTERCLOCK18432000 and
   `src/uart.c::init_UART1`, integer divisor from clock/(16*baud), read-only.
2. [Espressif AT instruction set v1.5.4 (2016)](https://www.espressif.com/sites/default/files/4a-esp8266_at_instruction_set_en_v1.5.4_0.pdf):
   AT+UART_CUR current configuration, AT+CIPMUX single link, AT+CIPSTART TCP,
   AT+CIPMODE/AT+CIPSEND transparent data, guarded+++ escape. Actual old modem
   support must be checked; never substitute newer AT-firmware assumptions.
3. Pinned IDF5.5.5 source commitb774170ff46c393eeb5e495ea37936038d3f4f4f:
   UART pin matrix, event errors, baud setting/readback, bounded receive and
   UART retirement, plus esp_timer_get_time clock units. Existing task header
   and full diagram retain actual P4 wiring/allocation and3.3V-bank requirements.

## Later work, not this hardware iteration

MechAgon consumes the measured contract after bring-up. Smith selects C8 as the
next comparison after this qualification. He raises rewiring Olimex UART1 through
a small mux as an alternative; no chip, schematic, wiring change or MOS/P4 mux
implementation is selected here. Retain that option for an explicit circuit
choice rather than silently changing the current bench during measurement.
