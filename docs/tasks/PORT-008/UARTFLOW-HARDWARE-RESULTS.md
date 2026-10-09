# UARTFLOW MOSlet — bounded hardware qualification

**Pass.** The extracted MOSlet completes the real paired UARTFLOW diagnostic
and releases UART ownership on both success and wrong-peer failure. Candidate
EMOS remains installed with **1,608 ROM bytes free**. The original ordinary P4
application and Agon startup are restored; input and file service were checked
and the bench is released. Author review is next; no production promotion or
commit is claimed. This does not qualify the unfinished parallel transport.

## Results

| Check | Observed result |
|---|---|
| Candidate EMOS installation | Automatic reboot; complete 131,072-byte ROM readback equals the 129,464-byte candidate plus erased padding |
| MOSlet deployment | 9,326-byte `/emos/uartflow.bin`, independently read back and compared |
| Wrong-peer control | Nonzero command return; UART-open/flow bits, diagnostic lease and RTS ownership clear; Extender input and listener reacquired without reset |
| Paired forward exchange | P4 deliberately held CTS, then received exactly `FLOW\r\n` (6 bytes) |
| Paired reverse exchange | P4 queued `FLOWACK\r\n` (9 bytes) while stopped; observed approximately 992 ms before completion after EMOS released RTS |
| Blocked reverse transmission | P4 queued one byte while stopped, observed a 1,000 ms block, cancelled it and released outputs |
| Late-error observation | P4 passed its five-second quiet phase, followed by 5.10 additional clean seconds in the host capture |
| Agon completion | Startup continued through the zero-return branch and saved `uf-pass.bin`; no peer-failure marker |
| Agon cleanup | Saved RAM: `serialFlags=3` (only mainboard UART0 bits), diagnostic lease 0, UART1 RTS ownership 0 |
| Restoration | Ordinary P4 application, bootloader, partition table and preserved live OTA metadata independently verified; original 38-byte startup compared exactly |
| Final readiness | Fresh admitted/neutral Extender input; no held/pending keys; listener successfully used then exited, no pending SD request |

P4's timestamps describe its own observed state transitions, **not a logic-analyzer
measurement** of baud or line edges. Both endpoints were configured for
1,152,000 baud, 8N1. The paired capture lasted 25.78 seconds including readiness
and Agon boot; this is not a transport-throughput benchmark. Candidate flash,
automatic reboot and complete ROM retrieval took 96.35 seconds in this run.
Other setup/transfers and restoration are additional; no voice notification was
requested or used.

## Reused fixtures and procedure

H01 — The maintained `uart_flow_peer.hpp` state machine is unchanged. The
`uart_flow_receiver.cpp` adapter now supports native ESP-IDF entry, timer/delay
calls and generated board pins while retaining isolated historical Arduino
defaults. The PC peer uses the current board profile's UART/data/handshake pins;
the old DevKit peer must not be flashed onto this board. Original peer host tests
and five capture-parser tests pass. The native peer is temporary test firmware,
with no video, network or keyboard service.

H02 — The normal P4 console served as the wrong peer. MOS `TRY` caught the
expected nonzero diagnostic return, and `IF Try$ReturnCode` selected a durable
failure-state save. A subsequent `EMOS KEYINPUT extender` and foreground listener
proved reacquisition without reset. The saved marker establishes a nonzero
return, not its exact numeric value or a captured mainboard error string.

H03 — For paired success, one-shot startup selected mode 3, renamed itself into
the startup-backup directory, copied the preserved ordinary startup back to
`/autoexec.txt`, then ran `TRY EMOS UARTFLOW`. MOS selected the corresponding
success/failure RAM-save path. This provided recovery without depending on the
unavailable mainboard keyboard or the P4 test peer for input. Official MOS
`TRY`/`IF`, `RENAME` and `COPY` behavior was checked in the local official
documentation and maintained MOS source before use. No fixture changed modes
internally. After the peer's readiness report, the host reset Agon once and
captured the finite exchange, then restored ordinary P4 services and reset Agon
to its restored startup before retrieving results.

H04 — Evidence and exact hashes are in
[the hardware manifest](UARTFLOW-HARDWARE-RESULT.json). Complete private logs,
readbacks, source/configuration closure and scripts are retained under
`agents/port008-uartflow/hardware/`. The successful standalone build is `peer-r02`;
`peer-serial.log`, `uf-pass.bin`, `failure-ram.bin` and `handback.json` distinguish
endpoint completion, cleanup and restoration. The RAM interpretation uses the
candidate's actual linked addresses: serial flags `0xBC32E`, diagnostic lease
`0xBC858`, RTS ownership `0xBCF07`. Do not reuse those offsets for another build.

## Setup lessons and limits

L01 — Agent packet delivery alone did not establish CLI command completion.
Slower character-at-a-time input reached the listener. Keyboard-source withdrawal
also completed asynchronously; wait for the not-ready/neutral status rather than
checking once immediately after Enter. Neither observation is a new gameplay
latency diagnosis.

L02 — This card lacked the documented backup folders and its installed listener
predated directory-operation support. MOS created the folders; firmware/listener
functionality was not broadened merely to prepare this test.

L03 — Live OTA metadata marks slot 0 valid and naturally differs from the build's
initial template. Preserve and verify the actual bytes. Only the P4 application
slot was written; no bootloader, partition, OTA, NVS or mainboard VDP write was
needed. A first standalone attempt never reached readiness and did not start the
Agon test. Matching the native build's partition configuration and explicitly
starting the verified application through the accepted USB reset sequence enabled
the subsequent pass; these setup changes were not separately isolated as causes.
No flow-control algorithm correction was made.

L04 — No logic-analyzer acquisition, electrical contention qualification,
sustained throughput measurement, full-system Fab run, new parallel payload,
or production acceptance is implied. Earlier host/linked-CPU coverage and ROM
accounting remain in [the extraction report](UARTFLOW-RESULTS.md). The candidate
also contains prior bench-free admission/reservation work; its live coordinator
and mandatory-release boot integration remain unfinished.
