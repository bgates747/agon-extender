# Analog controller input

The reviewed Linux viewer displays the Logitech F310's two sticks, separate
analog triggers, D-pad and eleven buttons. A developmental UDP sender and P4
receiver, resident EMOS service and Agon mode20 viewer now pass software checks
and target builds. The Author-approved experimental P4r13/EMOSv0.1.27,
sdserve-v0.3.0 and viewer-r03 installation is independently verified. The masked
READ/UART failure was corrected with checksum-free controller records and
interrupt-enabled copies. The Author subsequently reported that the controller
worked and identified latency as the next problem. EMOSv27 also admits bounded
mainboard VDPlet discovery replies and leaves270 resident ROM bytes free.
[INPUT-001](tasks/INPUT-001.md) retains integration evidence and acceptance gates.

The [latency investigation](testing/controller-latency.md) now has a finite
deterministic Linux source and retained host/P4 measurements. At120Hz Oryx
publication, P4 stored691 of3600 states in30seconds; median ACK round trip was
260.658ms. A Pi source reproduced the degradation. Even5Hz traffic had about
27–29ms median round trips while Oryx ICMP averaged0.558ms. This narrows the
investigation toward P4 UDP processing/scheduling; it does not identify the
exact blocking call or measure EMOS/display latency. The viewer's nominal20Hz
redraw adds a separate potential delay. Firmware and normal startup were
unchanged during these measurements. Current [results](tasks/INPUT-002/RESULTS-2026-10-26.md)
record scope and limits; production acceptance remains open.

The correction's review sender uses the existing `--timeout-ms 1000` option
at120Hz to reduce premature missing-ACK shutdowns. This permits a one-second
network-failure timeout; it does not relax EMOS's250ms cached-input freshness
check or establish120Hz delivery. The tool's default remains250ms.

Use the [viewer guide](testing/controller-viewer.md) for local handling and
recording. Select X on the F310's rear switch, then unplug/replug after changing
it. The tools read nonexclusively and do not change controller calibration or
fsim mappings.

## Developmental LAN client

After a separately prepared P4 installation includes the receiver, the Linux
host runs the sender explicitly. `$EXTENDER_URL` names that installation's
existing HTTP origin, including its port. Endpoint discovery/bench access remain
machine-local. These commands do not install or reset firmware.

```sh
.venv/bin/python scripts/controller_udp.py --url "$EXTENDER_URL" --status
.venv/bin/python scripts/controller_udp.py --url "$EXTENDER_URL"
```

The default cadence is 120 Hz (8⅓ ms per update), with 250 ms timeout. For a
bounded run with those settings explicit:

```sh
.venv/bin/python scripts/controller_udp.py --url "$EXTENDER_URL" \
  --hz 120 --timeout-ms 250 --seconds 30
```

Use `--device` with a stable event-joystick path if more than one F310 is present.
`--record` creates a new native JSONL capture; it never overwrites an existing
capture. Capture timestamps and total sender duration are host monotonic time,
not end-to-end input latency.

Ctrl-C ends the sender and requests close. Unplug, Linux input overflow, full
transition queue, recording failure, missing ACKs or receiver loss stop it with
a reported reason. Restart explicitly after correcting the cause. If close
cannot be confirmed, P4's freshness timeout invalidates input. The final JSON
reports sent/acknowledged packet counts, unacknowledged transitions, elapsed
seconds and error. An ACK confirms P4 storage; it does not prove game consumption.

The matching Agon/EMOS candidate consumes transitions explicitly. Without that
consumer, P4's128-record queue eventually fills while exercising buttons and
invalidates the session. HTTP status does not drain it. No host service starts
automatically; the LAN sender does not change keyboard capture.

## Agon viewer candidate

The [mode20 viewer](../tests/fixtures/controller/README.md) is an AgonDev C++ app
with512×384/64colours and large12×16 text. It shows both sticks, native/eight-bit
values, separate triggers, all buttons/D-pad and observed press totals. Escape
exits and restores the entry mode/CLI; R clears displayed counts. Drawing is
incremental at nominal20Hz while Linux publishes independently at120Hz.

Live mode needs the matched controller-enabled EMOS/P4 candidates, healthy
pre-existing Extender keyboard/UART admission and Legacy or ExCom. The app
reports an absent service before changing mode. It also supports clearly
labelled recorded-input review. Neither the native layout preview nor native
pipeline test establishes physical font, mode restoration or controller timing.

The [development service contract](protocols/controller-emos.md) describes
EMOS's cached READ, bounded REQUEST and retained-edge acknowledgement. No
application UART access, SD-lease borrowing or new global MOS API is supported.
These experimental firmware builds are installed only within the recorded bench
scope; they are not accepted or selected production.

## Building and validation boundary

The canonical [P4 builder](building.md) accepts `--controller-input` with
`--profile p4-console` and an explicit physical board selection. The option adds
controller routes and one UDP worker, and raises the socket ceiling to 16.
Default builds retain their existing selection. A base console compilation is
not a reconstruction of every deployed HDMI overlay; preserve that distinction
before planning an installation.

Offline checks use the actual portable C++ receiver and Python sender, including
loopback sockets, tap retention, loss/reordering, expiry and bounded overflow:

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_controller*.py'
```

The [LAN protocol](protocols/controller-lan.md) supplies byte layout and lifecycle.
[INPUT-001](tasks/INPUT-001.md) records evidence and remaining interface review,
physical latency/load and Author handling gates. Direct P4 USB controllers,
rumble and fsim integration remain separate work.
