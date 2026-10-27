# Agon controller viewer

This mode20 AgonDev C++ application recreates the host viewer's controls in
512×384/64 colours with12×16 text. It reads live input through the matched
EMOS/P4 development service, or plays explicitly labelled recorded input.
All three components build and the native software pipeline passes. The
checksum-free viewer-r03/EMOSv27/P4r14 development combination is installed.
The Author previously reported live input working; a subsequent interactive
review reported another freeze, which remains under investigation. Native
checks and the improved host/P4 timing do not qualify application reliability.

## Build without operating a bench

```sh
.venv/bin/python tests/fixtures/controller/build.py \
  --output agents/input001/controller-view-local \
  --toolchain-bin "$AGONDEV_BIN" --capture "$CONTROLLER_CAPTURE"
```

Supply a verified native JSONL capture from the host viewer and host-native
AgonDev tools. The builder requires Pillow, DejaVu Sans Mono Bold, librsvg/Cairo
and a native C++ compiler. It creates a fresh directory with a stopped Agon
binary, a54-byte-record replay, checksummed manifest and a native layout preview.
It never connects to a device, deploys files, resets hardware or changes startup.
The preview uses the same layout code; it does not validate Agon execution.

## Invocation after separately authorized installation

Live input requires matching controller-enabled EMOS/P4 firmware, existing
healthy Extender keyboard/UART admission and an explicitly invoked Linux sender.
This application does not enable admission or install firmware. Old EMOS returns
service-not-found/unavailable before the app changes mode. The mainboard VDP
does not require a controller-specific firmware change.

Place the package under `/extender/controller`. Keep evidence under
`/agents/extender`; preserve unknown card files and `/autoexec.txt`. The app
does not change the EMOS display route. Select the intended route separately
through EMOS. For this interactive viewer, invoke directly from the existing
CLI mode; do not preselect mode20 outside the application:

```text
CD /extender/controller
LOAD ctrlview.bin
RUN &040000
```

The viewer records its entry mode, selects mode20 only when necessary, verifies
the change and waits at least one second before drawing. Escape restores the
recorded mode, with the same settling interval after an actual restoration
switch. Preselecting mode20 would instead make mode20 the recorded entry mode.
This interactive invocation follows the Author's clarification on2026-10-26;
unattended suite coordination retains its separately specified mode lifecycle.

For recorded-input review use `RUN &040000 replay`. An optional path after
`replay` selects another `.cvr` file; that mode requires no controller service.

1. Two crosshairs show signed native stick positions and eight-bit previews.
   The adjacent LT/RT bars show separate0–255 triggers. All eleven buttons and
   four D-pad directions have large labelled indicators; press totals retain
   short presses between display updates.
2. The display clearly labels live/replay and connection status. It updates changed
   controls at nominal20Hz, conservatively below30Hz with either60/70Hz onboard
   VBlank clock. Replay clocks use nominal120Hz MOS
   sysvar units, not a measured physical sample or LAN clock. A capture gap is
   rejected by the converter rather than presented as complete press history.
   Live reads/refresh requests run independently at nominal60Hz, with one
   outstanding reply. Source-session changes reset observed press counts;
   repeated cached reads never count a tap twice. Link loss remains visible
   until Escape, including the failed gateway operation and numeric status; a new application invocation explicitly reopens the service.
   Healthy wire leases renew before sequence exhaustion without resetting the
   input source or observed counts.
3. R clears only displayed counts. Escape exits; other keys, including Alt-Tab,
   do not exit. End of recording leaves the viewer open for inspection.
4. The app queries the invoking display, enters mode20 only if necessary and
   restores its single-buffered entry mode/visible CLI on exit, including monitor
   settling after actual switches. Double-buffered entry is refused before
   mode changes until its CLI cleanup is qualified. No automatic test run occurs.
5. Temporary VDP font buffer64001 is cleared/released by the viewer. This
   development appliance reserves that ID while running; no preservation claim
   is made for a pre-existing application resource with that ID. Cleanup selects
   the built-in CLI font before releasing it. Agon physical lifecycle/font/input
   behavior remains untested.

The existing scrolling fixture's pure mode policy is an explicit source
dependency; the app uses its own MOS assembly bindings and no scrolling callback.
Its counted-output status interpretation is pinned to the maintained EMOS
contract. [INPUT-001](../../../docs/tasks/INPUT-001.md) owns interface review and
physical gates. The [candidate service contract](../../../docs/protocols/controller-emos.md)
owns the private CI/8E carrier, cached read and application-consumption rules.
Existing gateway call/function definitions are generated from maintained EMOS
`mos_api.inc`, with its hash recorded; no new global MOS API slot is allocated.

## Offline rendering check

```sh
c++ -std=c++17 -Wall -Wextra -Werror tests/controller_view_test.cpp \
  -o /tmp/controller-view-test
/tmp/controller-view-test
```

This checks geometry bounds, axis endpoints, unchanged-frame suppression,
disconnect status and count reset/reconnect behavior. It does not replace
Author review on Agon.

The combined software-path test uses the actual P4 receiver/peer, actual resident
EMOS C service and this app's actual live client, with only hardware boundaries
replaced:

```sh
.venv/bin/python tests/test_controller_pipeline.py
```

It verifies axes/triggers, short taps, repeated cache reads, source expiry and
session changes. The paired controller-enabled firmware must still be
identified, installed and reviewed on hardware before live readiness is claimed.
