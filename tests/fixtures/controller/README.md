# Agon controller viewer

This mode20 AgonDev C++ application recreates the host viewer's controls in
512×384/64 colours with12×16 text. It reads live input through the matched
EMOS/P4 development service, or plays explicitly labelled recorded input.
Current source uses the single public [controller include](../../../include/agon/controller.hpp)
and the matching reduced EMOS transport endpoint. New gateway operations4–7
replace the earlier application operations0–3; the physical P4 CI2/CIS2 carrier
is unchanged. Software pipeline checks and AgonDev builds pass. This new
application/EMOS combination has not been installed or physically accepted.

Earlier physical evidence belongs to the checksum-free viewer-r03/EMOSv27/P4r14
combination and its [frozen gateway contract](../../../docs/tasks/INPUT-005/CONTROLLER-GATEWAY-V1.md).
The Author reported working input and later latency/reliability observations;
native checks do not qualify end-to-end timing or application reliability.
The corrected `controller-viewer-r03-b2026-10-27-22-23-38Z` passed actual P4 USB
resting-state delivery and Escape/mode0 restoration. Subsequent control exercise
and remaining USB/coexistence gates are recorded in the [input guide](../../../docs/controller-input.md).
Those physical results do not qualify this new gateway or identify current
firmware on an occupied bench.

## Build without operating a bench

```sh
.venv/bin/python tests/fixtures/controller/build.py \
  --output agents/input001/controller-view-local \
  --toolchain-bin "$AGONDEV_BIN" --capture "$CONTROLLER_CAPTURE"
```

Supply a verified native JSONL capture from the host viewer and host-native
AgonDev tools and the matching maintained EMOS source (override the sibling
checkout with `--emos-source` when needed). The builder requires Pillow, DejaVu Sans Mono Bold, librsvg/Cairo
and a native C++ compiler. It creates a fresh directory with a stopped Agon
binary, a54-byte-record replay, checksummed manifest and a native layout preview.
It never connects to a device, deploys files, resets hardware or changes startup.
The preview uses the same layout code; it does not validate Agon execution.

## Invocation after separately authorized installation

Live input requires the matching new controller-enabled EMOS endpoint and P4
CI2/CIS2 peer, existing
healthy Extender keyboard/UART admission and either an admitted P4-local F310
USB source or an explicitly invoked Linux sender.
This application does not enable admission or install firmware. An earlier
controller endpoint rejects the new OPEN as invalid parameter; absent services
retain their ordinary not-found/unavailable result. The app reports failure
before changing mode. The mainboard VDP
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
   repeated retained transition IDs never count a tap twice. The application
   include validates the complete reply before advancing its edge acknowledgement
   and neutralizes stale controls using nominal age bounds. Link loss remains visible
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
   behavior has bounded physical mode20/entry-mode0 coverage; broader lifecycle
   and human control review remain pending.

The existing scrolling fixture's pure mode policy is an explicit source
dependency. The app retains its counted-output/clock assembly bindings and no
scrolling callback. The public controller include contains its own
register-preserving MOS gateway leaves; the builder checks their existing slot
constants against maintained EMOS `mos_api.inc` and records its hash. It also
checks the include's mechanically embedded wire definitions against P4/EMOS
before compiling. No new global MOS API slot is allocated.

The [application API guide](../../../docs/controller-api.md) describes static
application-RAM storage, named controls, host-model binding and freshness limits.
The [transport contract](../../../docs/protocols/controller-emos.md) owns new
gateway operations4–7, raw96-byte CIS2 plus two timing bytes, fixed19-byte SEND
and application validation/acknowledgement. EMOS retains transport ownership
and independent controller/SD leases. [INPUT-005](../../../docs/tasks/INPUT-005.md)
owns this offline extraction; [INPUT-001](../../../docs/tasks/INPUT-001.md)
retains earlier physical integration evidence.

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

It verifies axes/triggers, short taps, duplicate suppression, source expiry and
session changes. The same command tests the standalone public include against
a foreground transport model for malformed replies/no partial ACK, raw timing
bounds, local clock wrap, failure cleanup and healthy lease renewal. These
models do not invoke the default binding's physical MOS/UART path.
The paired controller-enabled firmware must still be
identified, installed and reviewed on hardware before live readiness is claimed.
