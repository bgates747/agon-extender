# Wi-Fi setup for Console8

Configure an ESP8266 over stock MOS3.0-or-later UART1, then read a small TCP BBS. The utility
shows English progress and two-second wait breadcrumbs, and appends the same
redacted messages to a log. Escape cancels. This first experimental build needs
Smith's manual Console8 test; it is not a qualified public release.

## Run manually

1. Copy `wifi-setup.cfg.example` to a **private** `wifi-setup.cfg`, edit it on your
   computer, and place it beside the program on the C8 card. Enter the real SSID,
   password and BBS hostname/IP. Do not send credentials to an agent or commit
   that file. Empty `password=` selects an open network.
2. Values after `=` are literal: **no enclosing quotes**, no inline comments.
   Leading/trailing spaces belong to SSID/password; `#`, comma, quote and
   backslash are accepted. The utility escapes AT metacharacters internally.
   Use printable ASCII, SSID1..32bytes, password0..64bytes; non-ASCII setup is
   outside the first build. Unknown/duplicate keys and files over4096bytes are refused before UART open.
3. From an ordinary C8 MOS prompt, after exiting any other UART1 application:

   ```text
   CD /extender/network/wifi-setup
   LOAD wifi-setup.bin
   RUN . wifi-setup.cfg progress.log
   ```

   Change directory once; the program, config and log names then refer to that
   directory. `RUN .` uses the default address `&040000`. If installed in `/bin`, use
   `wifi-setup <private.cfg> [progress.log]`. Default log is `wifi-setup.log` in
   the current directory. Start with `wifi-setup --help` if needed.
4. Expect firmware identification, station mode/DHCP, Wi-Fi association, address
   and actual MAC, then BBS welcome and `help`, `time`, `uptime`, `quit` requests
   and replies. A Wi-Fi pass alone is not a BBS pass. Result0 means the complete
   sequence passed; the router's DHCP reservation owns the canonical address.
5. Escape closes the host UART promptly without injecting commands into an
   unfinished join or length-announced send. The module may still finish a join
   or be waiting for payload. The program reports that uncertainty; manually
   restart the ESP8266 before another attempt if necessary. There is no reset,
   hidden reconnect, automatic retry or fallback firmware flash.

The eZ80 uses1152008N1 with no RTS/CTS, as the existing Radiotux utilities do.
`baud` is a host setting only; the module must already match it. Do not run this
on an Extender installation which owns UART1. This app is for the manual C8
four-wire connection, not an EMOS transport bypass.

## Configuration and privacy

`tick_hz=120` matches a60Hz VBlank with two MOS counts per blank. Use100 for50Hz.
The utility does not change the video mode, borrow a timer or claim calibrated
wall time. `command_seconds`, `join_seconds`, `bbs_seconds` are1..120 nominal
seconds. A separate bounded poll guard stops if the MOS clock freezes.

DHCP is enabled through `CWDHCP_CUR=1,1`; station mode/join use `_CUR` commands.
The app does not change MAC, set a static IP, save credentials/defaults to module
flash, enter TCP passthrough, change UART vectors or alter startup. It leaves
successful Wi-Fi association active after closing its own TCP/UART session.
The utility collects CONNECT/OK plus the complete welcome, and SEND OK plus
the complete BBS reply, before printing or syncing those records. This avoids
a synchronous display/card-write gap in the small polled UART receive FIFO.
Wait breadcrumbs are deferred briefly while receive bytes are arriving.
The BBS endpoint is plain TCP, not TLS/Telnet. Only use trusted local services.

SSID/password and escaped forms are redacted from all display/log messages;
the credential transaction accepts only known status text. No raw UART dump is
saved. Firmware/address/MAC/endpoint and BBS replies may be private too: logs are
local operator records, never package inputs or Git files. Credentials are still
plaintext in the private `.cfg` on the FAT card; this is not encrypted storage.
Use a lowercase `.cfg` input and distinct lowercase `.log` output. The log is
opened before config parsing and UART; config errors, write/sync errors and
Escape are reported without printing invalid values. Counted MOS writes and
checked `ffs_fsync` are used because the retained AgonDev character-write and
flush wrappers do not expose card errors/synchronization. The program uses
MOS file handles; it does not inspect or allocate MOS-internal file structures.
No program can make a blocked MOS/SD operation instantaneously cancellable;
all program-owned polling, TX readiness and response waits check Escape.

The table shows the application result printed in progress messages. MOS process
exit is0 on success and128 plus that result on failure (for example133 for a
reply timeout). This keeps private diagnostics outside MOS's built-in FatFS
error numbers. A startup/EXEC script still stops at its failed RUN line; that
script message does not establish that the log or script file is missing.

| Application result | Meaning |
|---:|---|
| 0 | Wi-Fi/DHCP/BBS sequence completed |
| 2 | Config/usage error |
| 3 | Escape cancellation |
| 4 | Modem refusal or UART unavailable |
| 5 | Deadline expired |
| 6 | Unexpected/truncated/oversized protocol response |
| 7 | Log open/write/close error |
| 8 | Clock stopped advancing |

## Build and test

Use an explicit AgonDev installation:

```sh
make -C tools/wifi-setup AGONDEV_TOOLCHAIN=/your/agondev \
  WIFI_BUILD_ID=wifi-setup-development
```

The exact build manifest records tool/source/output hashes. Native compilation
uses the normal shared compiler FIFO. Tests compile the **actual portable C
core** with a scripted AT peer; no emulator/hardware is started. The checked
adapter uses AgonDev nonblocking RX and a tiny THRE-before-MOS-write admission
wrapper so a full transmitter cannot hold an application polling loop.

## Provenance and public release boundary

Radiotux `Agon-Software` commit `e265db1de57c49142420324945c666049dc1ec53`,
`ifconfig/src/ifconfig.c` and `minicom/src/terminal.c` supplied the UART settings,
foreground polling and paced-byte baseline. The bounded setup/parser/log/BBS
implementation here is new GPL-3.0-only project code. Radiotux's README says
"Free Software" and permits use/study/modification/redistribution, without a
named license. Preserve that notice/attribution; clarify upstream terms before
public binary redistribution. Do not invent an upstream license.

The 2016 Espressif AT reference v1.5.4 documents the selected commands. The
observed module reports AT1.3.0.0/SDK2.0.0; physical command/latency acceptance
remains a manual test. Unsupported `_CUR` commands fail explicitly rather than
silently writing persistent settings. The log/protocol caps make this a setup
and small-text diagnostic utility, not a general high-volume serial driver.
