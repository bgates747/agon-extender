# Pi-controlled Agon reset

The existing 2N2222 actuator provides ordinary mainboard reset independently
of the P4. The Pi's physical pin11 / BCM GPIO17 drives the base through 10 kohm;
physical pin9 / ground joins emitter and mainboard ground. The collector goes
to Agon Light2 ZDI1 pin2, RST/EN. ZDI1 pins3 and5 are ground. Pin1 is +3.3V and
is not used. The connector name does not mean the ZDI debug protocol is used.
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
