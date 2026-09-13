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
