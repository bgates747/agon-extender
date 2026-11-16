# NET-009 — Pi UART / Pi TCP comparison

The same ESP8266 lost bytes in the same direction at 1,152,000 baud when
Pi5 replaced P4 as the UART transmitter. Pi5's TCP receiver was unchanged.
This rules out a P4-specific transmitter fault as necessary for the failure.
It does not distinguish effects in the Pi-to-modem electrical path from
ESP8266 UART receive, AT buffering or its network send path.

## Setup and short runs

Pi5 RP1 UART0 uses GPIO14/15, 8N1, no RTS/CTS; module power and wiring
moved from P4 to Pi5. GPIO17 and the debug console stay unchanged. With the
explicit machine credential provider, the modem associated and obtained a
station IP using runtime-only AT commands. No manual keyring unlock was needed
by the test runner. Reboot persistence of the credential provider has not been
tested, and the UART overlay is live only.

Each arm uses a nominal three-second producer interval and independently
verified 1,024-byte payload frames. The reverse UART can continue draining
data already accepted by TCP after its producer interval.

| Nominal baud | Pi UART TX → ESP8266 → Pi TCP | Pi TCP → ESP8266 → Pi UART RX |
|---:|---|---|
|1,152,000|Fail: 25 valid frames (25,600 B) before CRC error|Pass: 361 frames (369,664 B)|
|576,000|Pass: 167 frames (171,008 B)|Pass: 192 frames (196,608 B)|
|384,000|Pass: 111 frames (113,664 B)|Pass: 136 frames (139,264 B)|
|230,400|Pass: 67 frames (68,608 B)|Pass: 94 frames (96,256 B)|
|115,200|Pass: 34 frames (34,816 B)|Pass: 57 frames (58,368 B)|

The failing TCP stream has its first differing byte at offset 26,230
(zero-based, including frame headers). Its remaining 810 captured bytes
match the expected stream 300 bytes later. This is an end-to-end missing-byte
signature. The Pi UART wire was not captured, so the good physical P4 trace
from NET-008 cannot be used as a Pi wire measurement. All arms returned
positively to AT command mode. No device reset, firmware flash, or Olimex
target access occurred. The Pi-to-P4 Ethernet comparison was not run; it
needs a prepared P4 test receiver and fresh scheduler custody.

## Upload backoff

All three 576,000 baud upload runs returned to AT command mode and matched
frame counts, payloads and CRCs end to end.

| Nominal producer window | Valid frames | Valid payload bytes |
|---:|---:|---:|
|60 s|3,326|3,405,824|
|30 s|1,663|1,702,912|
|10 s|555|568,320|

The 60 s run spans 60.048 s at the receiver, approximately 56.7 kB/s of
validated payload. That qualifies this one-way upload at 576,000 baud; it
does not qualify duplex operation or a 60 s download. Pi throttling
flags were zero before and after this test series; module voltage was not
measured. The modem is associated with CUR baud 576,000 in command mode.
The header tty is closed; its runtime overlay remains active.

Execution contract: [PI-PEER-R01](PI-PEER-R01.md). Runner source at
`164f7bbf`; original results and raw test bytes (no credentials) are retained
in the ignored NET-009 agent evidence directory.
