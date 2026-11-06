# Wi-Fi startup for Console8

Connect the ESP8266 using private settings, or skip and return to MOS. This
separate utility does not contact the BBS. Native MOS3 or later is required.
Use only on the standalone ESP8266 UART1 wiring, not an Extender-owned UART1.

1. Copy `wifi-start.cfg.example` to `wifi-start.cfg` and fill in the SSID and
   password locally. The file is private; never add it to Git or a public package.
2. Change directory once, load, and run with local filenames:

```text
CD /extender/network/wifi-start
LOAD wifi-start.bin
RUN .
```

Defaults are `wifi-start.cfg` and `progress.log` in that directory. Optional
explicit local names: `RUN . private.cfg progress.log`.

Choose **1 Connect as configured** or **2 Skip connection**. Escape skips the
menu or cancels an operation. There is no menu timeout or implicit choice.
`auto_connect=1` in the private cfg connects without the menu; default0 waits.
Missing/invalid cfg still allows Skip. Skip does not open UART or disconnect
an existing association. This tool never changes `/autoexec.txt`.

Connection uses1152008N1 without RTS/CTS by default. MOS owns UART admission;
the ESP8266 handles volatile station setup and DHCP. Your router assigns the
canonical address from the module's unchanged MAC reservation. The program
prints the IP/MAC and concise English stages, while appending redacted details
to the log. Connection waits show periodic breadcrumbs; Escape remains polled.
Nominal MOS conversion is120 counts/s at60Hz,100 at50Hz; not calibrated timing.

`ping_host=gateway` queries the actual DHCP gateway and requests two genuine
ESP8266 ICMP pings. Set an explicit hostname/IP instead, or `none` to disable.
The module reports round-trip milliseconds; this is not MOS serial latency.
Normal ICMP integrity belongs to the module, with no custom CRC or echo server.
A missing/unsupported ping or blocked ICMP produces a warning separately from
successful Wi-Fi/DHCP. An ERROR cannot distinguish unsupported firmware from an
unreachable peer. A timeout/cancel stops further commands because the module may
still be busy. Do not automatically rerun an uncertain command; the log explains
whether manual module recovery may be needed. No reset, passthrough, persistent
credential save or TCP port scan is performed. Wi-Fi is left connected on exit.

The full accepted `wifi-setup` BBS diagnostic remains a separate utility. An
existing diagnostic cfg may be supplied here; its BBS settings are accepted but
not used. Startup-only keys are not accepted by the older diagnostic parser.
No actual cfg/log is packaged. Upstream Radiotux files remain read-only and
unchanged: they are monolithic applications, not a cancellable linkable driver.
We reuse our own bounded adapter/AT/config support from `../wifi-setup`, with
its attribution and notices. Public distribution/license/version closure and
manual C8 acceptance of this new utility remain pending. No emulator result.

Build with an explicit compatible AgonDev toolchain:

```sh
make -C tools/wifi-start AGONDEV_TOOLCHAIN=/your/agondev \
  WIFI_BUILD_ID=wifi-start-development
```
