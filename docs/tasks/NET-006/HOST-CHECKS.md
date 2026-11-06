# Wi-Fi setup host checks

The actual portable C core and native main/file adapter pass bounded host checks.
These checks establish parser/lifecycle/error behavior, not C8 UART or ESP8266
compatibility. The native image and manual package are separate build evidence.

## Core scenarios

1. Twenty scripted AT scenarios include complete setup/BBS exchange, no AT
   response, delayed replies and heartbeat breadcrumbs, unsupported DHCP,
   association timeout/refusal, delayed/missing lease, refused TCP, oversized
   `+IPD`, permanently/temporarily blocked TX, failed logging, frozen clock,
   refused/missing send prompt, send failure, truncated payload, `ERROR`/`OK`
   inside BBS data and byte-fragmented responses.
2. Escape is injected at eleven stages including setup commands, association,
   address query, connection, send prompt and payload transmission. No automatic
   cleanup command, reconnect or retry is emitted into uncertain module state.
3. Unsigned clock wrap and the100-count/second alternative pass; default is120.
4. Config tests cover special characters, empty open-network password, duplicate/
   unknown keys, invalid numbers/endpoints/baud/tickrate, missing required data,
   embedded NUL, oversized files, read error and Escape. Errors omit input values.
5. Raw and escaped SSID/password echoes are absent from retained test output.
   Complete `+IPD` payloads are parsed as data, not modem command statuses.

## Native file adapter scenarios

The actual `main.c` is compiled with a host-only MOS double. Six cases exercise
append without truncation, partial write, sync failure, file-size/seek failure,
Escape during config read and a counted read failure. Every file handle closes;
UART is not opened after failed preparation. The valid case deliberately refuses
UART open; it does not claim a physical UART test.

Both C targets use `-Wall -Wextra -Werror`, AddressSanitizer and
UndefinedBehaviorSanitizer. LeakSanitizer is disabled because this tool sandbox
runs under ptrace; the initial ordinary LSAN invocation reported that environment
limitation. No memory leak qualification is claimed. The utility core allocates
no heap. Tests run with finite60second watchdogs under normal compiler checkout.

## Native and manual limits

The native adapter uses MOS3 APIs and never inspects opaque internal `FIL` data.
It checks counted writes plus `ffs_fsync` because the pinned AgonDev `fputc`/
`fflush` contract does not expose card failures/sync. Configuration input also
uses counted MOS reads through the same tested bounded parser callback.

Hardware remains untested. In particular,115200 polling without RTS/CTS, actual
AT1.3 command acceptance, keyboard Escape latency, card sync and ordinary CLI
handback need Smith's manual C8 test. There is no emulator result, measured
UART throughput, public release/tag or completed license clearance.
