# Console8 Wi-Fi setup utility

The experimental native `wifi-setup` utility configures a four-wire ESP8266 and
checks a small TCP BBS, with private configuration, English progress, Escape and
redacted progress/error logs. It is for a manually operated Console8 with MOS3.0
or later; it does not borrow UART1 from an active Extender installation.

At the MOS prompt, change to the utility directory once and use local filenames:

```text
CD /extender/network/wifi-setup
LOAD wifi-setup.bin
RUN . wifi-setup.cfg progress.log
```

[Usage, configuration and build instructions](../tools/wifi-setup/README.md)
include the secret-free example, clock-rate setting and timeout/cancellation
limits. [NET-006](tasks/NET-006.md) records preparation, validation and the pending
manual hardware review. Do not mistake a native build/host peer simulation for
an ESP8266 or C8 pass. Firmware and normal startup are preserved; no automatic
boot service, async/OTIRX driver or public-release tag is selected.

The private `.cfg` holds SSID/password and the BBS endpoint. The router owns the
MAC-based DHCP reservation; the utility never assigns a static IP or changes
MAC. Its BBS check displays `help`, `time`, `uptime`, `quit` requests and replies.
Progress logs remain private operator records. Keep real configs/logs out of
source control and generated distribution packages.

If a run fails, read the application result and the last progress-log entries.
Nonzero MOS exits use128 plus that result, so MOS does not label an application
timeout as a missing file or path. EXEC/autoexec still stops at a failed RUN;
the named script line identifies that invocation, not a missing log. The first
manual build returned overlapping MOS error numbers; the corrected candidate
also collects complete BBS replies before printing or synchronizing its log.
Its host checks pass; the corrected C8 exchange still requires manual review.
