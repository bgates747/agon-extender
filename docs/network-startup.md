# Console8 Wi-Fi startup

The separate `wifi-start` application connects the ESP8266 or returns to MOS
without opening UART1. It has no BBS check. The first candidate has host checks
and a native build; Smith's manual C8 review remains pending.

Prepare a private `wifi-start.cfg` from the secret-free example and use short
commands in its directory:

```text
CD /extender/network/wifi-start
LOAD wifi-start.bin
RUN .
```

For optional startup, add this before Jukebox starts (replace any earlier Wi-Fi
setup block). The final `CD /` returns subsequent root-relative commands to the
normal boot directory; use the appropriate directory if your next block expects
another working directory. The agent does not edit startup automatically.

```text
CD /extender/network/wifi-start
LOAD wifi-start.bin
RUN .
CD /
```

The program defaults to local `wifi-start.cfg` and append-only `progress.log`.
Use `RUN . private.cfg progress.log` for other local filenames. The only choices
are1 Connect as configured and2 Skip connection; Escape skips or cancels.
`auto_connect=1` bypasses the menu; default0 waits for a choice indefinitely.
Missing/invalid configuration still permits Skip. An existing setup cfg also
works: BBS keys are accepted here but never used. Do not pass new startup-only
keys to the original diagnostic utility.

The ESP8266 joins using DHCP without changing its MAC. Your router owns the
MAC-based canonical address. The concise screen shows stages, IP/MAC, waiting
breadcrumbs and outcomes; the log retains redacted command/error details. No
real configuration or log is part of the package or Git. Nothing modifies the
startup script, installed firmware, video mode or interrupt vectors.

Default `ping_host=gateway` queries the module's actual gateway and sends two
real `AT+PING` requests. An explicit hostname/IP or `none` is supported. Latency
comes from the module, not from timing UART characters. Ordinary ICMP integrity
belongs to its network stack; there is no custom CRC, remote echo service or TCP
port-scan substitute. Refused/unsupported ping is a warning distinct from a
successful Wi-Fi/DHCP join. Timeout/cancellation stops further module commands;
the log records potentially unfinished work instead of resetting or replaying.
Clock conversion defaults to120MOS counts/s at60Hz, configurable100 at50Hz.

The [source instructions](../tools/wifi-start/README.md) cover configuration,
command scope and build details. [NET-007](tasks/NET-007.md) retains validation
and the manual/public-release boundary. The accepted full
[setup/BBS diagnostic](network-setup.md) remains separately available unchanged.
Radiotux sources are untouched; our bounded support is project-owned and kept
outside his checkout. The new utility has no dependency on the proposed async
UART1 application driver.

The retained candidate is `wifi-start-b2026-11-06-17-51-28Z` (31856bytes),
with [exact manifest](tasks/NET-007/BUILD.json). Its generated manual package is
`dist/wifi-start/wifi-start-b2026-11-06-17-51-28Z.zip` in the build owner's
checkout. Cloning Git alone does not obtain generated binaries. This is a
manual-review candidate, not a selected public release.

At Smith's request the exact candidate is deployed on the mounted C8 card,
including a private cfg copied locally from the working diagnostic cfg. It
remains manual Connect-or-Skip by default; adding `auto_connect=1` to that
private file enables immediate connection. Startup and existing private files
remain unchanged. File verification is not a C8 execution/acceptance claim.
