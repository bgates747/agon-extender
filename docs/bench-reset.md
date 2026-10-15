# Pi-controlled Agon reset

The existing 2N2222 actuator provides ordinary mainboard reset independently
of the P4. The Pi's physical pin11 / BCM GPIO17 drives the base through 10 kohm;
physical pin9 / ground joins emitter and mainboard ground. The collector goes
to Agon Light2 ZDI1 pin2, RST/EN. ZDI1 pins3 and5 are ground. Pin1 is +3.3V and
is not used. The connector name does not mean the ZDI debug protocol is used. The Rev B
schematic connects this RST/EN net to both eZ80 RESET and mainboard ESP32 EN.
The mainboard CH340 DTR/RTS auto-program circuit also drives it. Consequently,
esptool's mainboard hard-reset can restart both processors; it is not an
isolated VDP reset. Serial-open control-line behavior must not be assumed
harmless without qualification. Use the maintained [joined-control serial opener](serial-monitor.md); ordinary pyserial DTR-first deassertion was found to pulse this reset circuit. See [the installed-source review](tasks/BENCH-010/CODE-REVIEW-R01.md).
The optional 100 kohm resistor joins base to emitter. Do not join power rails.

The previously verified transistor lead order is E, B, C with flat face toward
the viewer and leads pointing down. In the Author's rotated 2026-09-13 photo,
the stated top-to-bottom order is E, B, C. Use that known part's pinout rather
than assuming every transistor package has the same order.

Looking down into the header with the plastic notch facing away:

```text
                    Notch
     [5 GND]       [3 GND]       [1 +3.3V]
                     ^
                   Black
     [6 TDI]       [4 TCK]       [2 RST/EN]
                                    ^
                                  White
```

Black/white here are the two Agon-bound leads. Confirm the pin1 marking when
orienting an actual board. Pi GPIO17 High asserts reset; Low/input with pull-down
releases it. The working desktop helper applies one 100 ms pulse and releases
the GPIO even on command failure; it does not retry automatically.

The Author corrected a miswired ground, requested the pulse while filming,
then confirmed success with "yay". A fresh service incarnation and stage3
audio-command receipt were subsequently read back. This establishes functional
reset/boot and the observed spoken greeting, not oscilloscope timing, broader
electrical qualification or a formal continuity measurement. This current
functional observation supersedes the old unresolved-ground warning for normal
use of this corrected assembly; retain the historical notes as evidence.

Machine-specific SSH identity and desktop helper path remain in HARDWARE.local.md.
The P4 is not connected as a reset controller and no P4/VDP firmware operation
is part of this pulse. See DEMO-001 evidence for the accepted demonstration.

## Standing recovery order — Author instruction, 2026-10-13

For an unresponsive bench during authorized monitored work, the agent must try
the following recovery before asking the Author to reset hardware:

1. Send one ordinary Agon reset through the commissioned Pi actuator. Verify
   fresh EMOS input admission and actual CLI/listener/read handback.
2. If that attempt fails, reset the P4 through its verified programming device
   without flashing, wait for P4 application/service initialization, then send
   one ordinary Agon reset. Verify input and actual CLI/listener/read handback.
3. Only if both attempts fail, stop and ask the Author in ordinary chat.
   Do not use question-dialogue tools.

This is standing recovery authorization, not authorization to replay a failed
test or transfer, alter firmware, discard transaction journals or reset during
an explicit stop/no-monitoring instruction. Before resetting, establish safe
setup-only startup from current readback or the latest verified unchanged
bytes. Retain failed operations and reconcile their actual effects after
recovery. A setup/listener timeout is a recovery trigger under this instruction,
not proof that a workload completed.

## Required pre-reset check

1. Read the [operation-protocol index](procedures/README.md) and current local
   bench record. Confirm the authorized target (Agon, P4, or both), the current
   application and whether any other owner has the bench.
2. Establish what `/autoexec.txt` will execute before pulsing Agon reset. Reset
   is not a test launcher. If startup contains test `RUN`/`EXEC`, restore ordinary
   startup through admitted access first. If that is impossible, stop and explain
   the conflict; do not reset into a known unwanted test or assume Escape will
   reliably interrupt it.
3. A paired input recovery means the host resets P4, waits for the required P4
   initialization, then resets Agon. It does not authorize reflashing either
   processor. Use the current local recipe and evidence, not a guessed delay.
4. After the authorized pulse, verify only what the Author permits. “Start then
   stop” or “no monitoring” forbids a subsequent status poll or automatic retry.
   A failed readiness check is evidence to inspect; further resets require the
   standing recovery order above or separate Author authorization.

## Host reset command

From the Extender checkout, after confirming reset authorization and the current
bench state:

```sh
.venv/bin/python scripts/reset_agon.py --config "$RESET_CONFIG"
```

For an automated reset that must establish usable Extender input, add
`--verify-url http://P4_ADDRESS`. The wrapper reads the current boot epoch
before pulsing, then requires a different input epoch with admitted, neutral
Extender input before printing `AGON RESET VERIFIED`; timeout exits nonzero.
This verifies the P4 admission state, not actual MOS command execution. A
separate harmless CLI/service exchange is required when qualifying functional
recovery; an unchanged ready=true snapshot alone can conceal lost input.
Without that option it reports `PULSE-ONLY COMPLETE` and makes no boot-success
claim; its message identifies the caller as the owner of subsequent
verification. Automated boot and qualification workflows must use the verified
form so that the pulse is immediately followed by an explicit verification
attempt. Bridge callers may retain pulse-only behavior when the browser owns
the separate post-reset observation.

`RESET_CONFIG` is an owner-provided local JSON file with `ssh` (complete SSH argv),
`chip` (gpiochip name) and `gpio` (line number). The wrapper uses noninteractive
`sudo -n bash -s` on the Pi; the existing authorized SSH/sudo setup must already
work without a password prompt. The Pi needs Bash, GNU `timeout`, libgpiod v2
`gpioset` and `pinctrl`. These are prerequisites, not instructions to change
privileges or wiring. On macOS use the local `python3`, not a Linux virtualenv.
A zero exit confirms the actuator command completed; observe Agon boot and fresh
input admission separately. Do not replay an uncertain pulse automatically.

## Browser button through the bench Pi

The header's top-right **Reset Agon** button uses `scripts/reset_bridge.py` on the Pi;
P4 only serves the UI. The bridge executes the same maintained 100 ms actuator
pulse described above. A confirmation precedes the request, browser keyboard
capture is released, and the operator captures again after boot. Successful reset adds no status text to the layout; failures use a dialog.
Exit fullscreen to access this header control. Neither page
load nor video reconnection requests a reset. No automatic retry occurs.

Deployment supplies the `agon-reset-url` HTML meta value in its private staged
`index.html`; the tracked default is empty and leaves the button disabled.
Run the bridge with `python3 scripts/reset_bridge.py --config <private-json>`.
The JSON contains `bind`, `port`, `origins` (exact browser origins), and `command`
(a fixed argv array invoking the maintained pulse helper). Install it as a
boot-enabled service on the bench Pi; exact service, endpoint and command paths
belong in the local bench record. The Pi must be reachable from the browser.

The endpoint accepts only POST `/reset`, a configured Origin, the
`X-Agon-Reset: 1` header and a JSON UUID `id`. It rejects concurrent operations;
duplicate IDs return the saved result without another pulse. History is bounded
at 1024 IDs and lasts only until service restart. This is a trusted-LAN bench
bridge, not authenticated Internet access: Origin checks prevent ordinary
cross-site browser requests but do not authenticate arbitrary network clients.
A successful response proves the pulse command returned, not that Agon booted.
An uncertain response requires checking Agon before any deliberate second press.

The Olimex AgonLight2 Rev B schematic, sheet 4 (Power Supply/USB), connects
RESET1 between RST/EN and ground. ZDI1 pin 2 uses that same net. Thus the bench
transistor and physical button assert the same reset signal. Pulse duration
and source differ; neither is a power cycle, and neither resets the Extender P4.

Implementation and bounded test evidence: [REMOTE-003](tasks/REMOTE-003.md).


## Separate P4 web reset (development candidate)

The web console's **Reset P4** button requests `/reset-p4` from the same configured
Pi bridge used by **Reset Agon**. The Pi executes only its locally configured
exact-device P4 USB reset command; the P4 request does not flash firmware or pulse
Agon. The bridge preserves origin checks, POST-only execution, target-specific
request deduplication and one shared operation lock. Without `p4_command`, P4
requests fail explicitly; they never execute the Agon actuator.

P4 reset clears its current display and transport admission. Use **Reset Agon**
after P4 initialization when fresh EMOS input admission is required. The buttons
remain separate; no automatic retry or paired reset occurs. Button visibility
alone does not establish a configured/working bridge. Implementation and physical
browser acceptance are tracked in REMOTE-008; selected production is unchanged.
