# Analog controller input

The reviewed Linux viewer displays the Logitech F310's two sticks, separate
analog triggers, D-pad and eleven buttons. A developmental UDP sender and P4
receiver, resident EMOS service and Agon mode20 viewer now pass software checks
and target builds. The Author-approved experimental P4r14/EMOSv0.1.27,
sdserve-v0.3.0 and viewer-r03 installation is independently verified. The masked
READ/UART failure was corrected with checksum-free controller records and
interrupt-enabled copies. The Author subsequently reported that the controller
worked and identified latency as the next problem. EMOSv27 also admits bounded
mainboard VDPlet discovery replies and leaves270 resident ROM bytes free.
[INPUT-001](tasks/INPUT-001.md) retains integration evidence and acceptance gates.

The [latency investigation](testing/controller-latency.md) found a low-priority
P4 UDP worker waiting behind parser/video work. r14 raises that worker from
priority2 to4, below drawing/output. In the matched120Hz comparison, all3600
packets were acknowledged and median ACK round trip fell from261.703ms to
1.794ms (99.31% lower). The60/240Hz cases, independent Pi source and real CLI/
fast-SD coexistence also pass. [Current results](tasks/INPUT-002/R14-COMPARISON.md)
retain exact installation, counts, units and limits.

These are host/P4 round trips. EMOS/application/display latency remains
unmeasured; the viewer's nominal20Hz redraw is a separate possible delay.
The EMOS/mainboard firmware and normal startup were preserved during r14's
application-only P4 installation. Production acceptance remains open.

Earlier r13 physical-review sessions used `--timeout-ms 1000` at120Hz to tolerate
ACK stalls. The matched r14 Oryx tests use the250ms default; existing review
launchers may still specify1000ms. That option changes failure detection, not
input latency or EMOS's250ms cached-input freshness check. Neither setting
establishes end-to-end120Hz application delivery.

Use the [viewer guide](testing/controller-viewer.md) for local handling and
recording. Select X on the F310's rear switch, then unplug/replug after changing
it. The tools read nonexclusively and do not change controller calibration or
fsim mappings.

The F310's separate front **Mode** button can swap the left analog stick and
D-pad. If the left stick drives only the viewer's directional labels while
the right stick plots normally, check that setting before changing software
axis mappings. Logitech calls the swapped setting sports mode (Mode light on)
and the ordinary analog setting flight mode (light off); see its
[F310 guide](https://www.logitech.com/assets/47879/f310-gamepad-quick-start-guide.pdf).
This is separate from the rear XInput/DirectInput switch.

## Direct P4 USB candidate

The experimental P4-PC build `indexed-hdmi-r14-b2026-10-27-22-46-52Z`
accepts the F310 directly through the onboard USB-A hub in rear-switch XInput
mode (`046d:c21d`). A bounded physical check delivered its real resting state
through EMOSv27 to the mode20 viewer, without a Linux controller sender.
Escape and entry-mode0 restoration pass with the corrected viewer build
`controller-viewer-r03-b2026-10-27-22-23-38Z`.
[INPUT-003](tasks/INPUT-003.md) records exact installation and remaining review.
Author control exercise found a latched USB report error at D-pad up-left. The
current correction cancels opposite contacts on each hat axis, matching Linux
xpad, while preserving normal diagonals. The Author subsequently accepted
the physical retry and reports other controls in order. The original rejected
raw packet was unavailable; broader qualification remains open.

1. Connect the F310 to a P4-PC onboard USB-A socket. Keep existing Extender
   keyboard admission and the intended EMOS display route. Use the same viewer
   invocation below; the app needs no different controller configuration.
2. Inspect `/controller/status`: `source: "usb"` with top-level `valid: true`
   identifies the admitted source. The `usb` object reports attachment, VID/PID,
   endpoint, actual report count and USB errors. `dpad_conflicts` counts normalized
   opposite contacts; `malformed` counts framing rejects. `anomaly_kind` is0
   for none,1 for framing and2 for opposite contacts; `anomaly_bytes` and
   `anomaly_hex` retain one bounded latest raw anomaly. Its `report_age_ms` measures
   time since the last actual USB report; a quiet controller can retain its
   state while the live USB task renews the cache. It is not input latency.
3. A recognized USB pad with a valid first report reserves local input. It
   cannot steal an active LAN source; a conflicting LAN open is rejected while
   USB owns/reserves input. Unplug or USB failure invalidates local input. A new
   app invocation can rearm cache overflow/expiry; physical USB faults require
   reconnect. These source policies remain experimental.
4. Native USB acquisition currently starts with the HTTP/controller runtime
   after Ethernet initialization. Cold boot without that network startup is
   unqualified. Physical unplug/reconnect, complete control exercise,
   simultaneous physical keyboard/controller and end-to-end latency remain
   review gates. The bounded pass used browser/agent keyboard input.

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
incremental at nominal20Hz while the admitted USB or Linux source publishes
independently.

For interactive use, launch from the current CLI mode without a separate
`VDU 22 20` command. The viewer captures that entry mode, switches to mode20
only if necessary, verifies/settles the switch and restores the captured mode
on exit. See the fixture guide for the explicit `CD`/`LOAD`/`RUN` commands.

The2026-10-26 interactive retry initially appeared frozen. The Author confirmed
the viewer still responded to Escape and displayed "Waiting for controller";
the physical sender had stopped on transition-queue overflow. Explicitly
starting a fresh sender restored usable input. The initial fault ordering
remains unproven; restarting the Agon app alone cannot restart an ended host
sender. The retained observations are in [INPUT-002](tasks/INPUT-002.md).

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

The corrected October27 viewer waits for the selected mode after a switch:
stock VDP font changes also send mode information, and an older reply must not
make successful restoration appear to fail. The physical check confirms
mode20 input followed by Escape and a fresh mode0/640×480/16-colour CLI query.

Controller transport compatibility does not establish application-renderer
compatibility. The VDPlet native-line/wireframe image and fsim's asynchronous
flight compositor are different compositions. Fsim subsequently restored its
exact accepted compositor under separate Author authority, preserving EMOS/P4.
A consumer must verify its own renderer dependency before physical readiness;
working controller input does not authorize replacing either image.

Fsim's2026-10-26 retained physical results now cover finite neutral flight with
the real F310/Oryx/P4/EMOS stream in both textured and flat editions, plus pause,
cached reset, explicit rearm and Escape. Each neutral case completes120physics
ticks and242controller polls; maximum observed service gap is2nominal MOS units,
with no reported drops/input/flight errors. These are foreground polling
observations, not controller-to-photon measurements. Author gameplay/handling
review remains open in the [fsim-owned task](../../agon-fsim/docs/tasks/FLIGHT-057.md).

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
physical latency/load and Author handling gates. Fsim owns its consumer
integration and flight mappings. Direct F310 USB qualification continues under
[INPUT-003](tasks/INPUT-003.md); other USB controllers and rumble remain separate
work.
