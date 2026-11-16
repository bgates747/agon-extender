# NET-009 — Pi UART / P4 Ethernet result

The ESP8266 stayed on the Pi5 header UART and 3.3 V supply. The P4-PC
replaced Pi5 as the TCP peer and used wired Ethernet. Each arm ran a
single bulk direction with 1,024-byte deterministic frames and checked
sequence, content, CRC and EOS. Both endpoints agreed on the frame counts
for every passing arm.

## Three-second producer windows

| Nominal baud | Pi UART → ESP8266 → P4 TCP | P4 TCP → ESP8266 → Pi UART |
|---:|---:|---:|
|1,152,000|Unrun after the upload fault|Pass, 346 frames|
|576,000|Unrun after the upload fault|Pass, 181 frames|
|384,000|CRC fault on frame 87, 86 verified|Pass, 125 frames|
|230,400|Pass, 67 frames|Pass, 81 frames|
|115,200|Pass, 34 frames|Pass, 46 frames|

## Backoff and sustained windows

| Direction and baud | 10 s | 30 s | 60 s | Verified payload in 60 s |
|---|---:|---:|---:|---:|
|Upload at 230,400|Pass, 222 frames|CRC fault on frame 616, 615 verified|Unrun after the fault|—|
|Upload at 115,200|Pass, 112 frames|Pass, 333 frames|Pass, 665 frames|680,960 B over 60.041 s, 11.3 kB/s|
|Download at 1,152,000|Pass, 1,126 frames|Pass, 3,356 frames|Pass, 6,702 frames|6,862,848 B over 60.142 s, 114.1 kB/s|

Payload rates use decimal kB/s and the Pi's measured interval, including
any drain after the producer window. The 60-second arms were one-way.

The P4's first failing upload frame at 384,000 baud has its first differing
raw stream byte at offset 90,431. The remaining 49 bytes align with the
expected stream 100 bytes later. At 230,400 baud the first differing raw
byte is at 640,060, and all 580 remaining captured bytes align three bytes
later. Offsets are zero-based and include frame headers but exclude HELLO.

The [Pi TCP control](PI-PEER-R01-RESULT.md) had already shown missing bytes
on upload, with a clean 60-second upload at 576,000 baud. The P4 Ethernet
run reproduced upload loss at lower rates. Both tests used the same Pi
UART and modem while the TCP receiver and its buffering differed. The
endpoint records do not locate the loss. The analyzer probes were still
mapped to the prior P4/modem UART wiring, so this comparison has no Pi UART
waveform.

## Fixture and handback

The [two setup faults and corrections](P4-PEER-R01.md#first-hardware-start)
preceded any TCP payload. The measured runs used fixture commit
`6af62814`, P4 app SHA-256
`bc774240e8c7edb5fedd20143fa247fa6e600f7489eb42778b289c4b595793cc`,
and the continuously open USB console from host commit `36680341`.
The modem's AT firmware was retained. The modem returned to command mode at
115,200 baud and remained wired to the Pi5. Pi GPIO17 was untouched.

The worker restored the working P4 application, independently reread the
385,024-byte changed extent and verified a fresh MOS CLI/read/EXIT with
neutral input and idle services. It left the mainboard firmware, startup
and listener unchanged. Both measurement workers joined and the bench was
released at 20:33:53 UTC on 2026-11-16. Raw result files, setup failures,
restore readbacks and the central release receipt are retained in the
ignored NET-009 agent evidence directory.
