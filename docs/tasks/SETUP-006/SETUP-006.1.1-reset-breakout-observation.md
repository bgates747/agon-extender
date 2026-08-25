# SETUP-006.1.1 — Reset-breakout bench observation

## Observation

At 2026-08-24 20:24 EDT, the Author reported the following current physical
state:

1. The reset breakout sits on the Raspberry Pi 5.
2. View the Pi from above with its header bank on the right and its USB-A and
   network connectors at the bottom.
3. Two breakout wires attach to the fifth and sixth positions from the top on
   the left side of that header bank.
4. The upper wire is black.
5. The lower wire is white.
6. Viewed from the flat face of the 2N2222 package, its left lead has no
   connection apparent to the Author.
7. The physical wiring looks wrong to the Author.

At 2026-08-24 20:42 EDT, the Author supplied a front-facing photograph of the
removed module and clarified the omitted Pi connections:

8. The visible black and white leads go to the Agon.
9. The omitted black Pi lead had occupied the same terminal strip as the
   visible black lead; the Author identifies both as ground.
10. The omitted white Pi lead had occupied the hole immediately right of the
    transistor's rightmost lead and immediately above the upper resistor's
    right-hand connection.
11. The 2N2222 is shown flat face toward the camera at the top center of the
    breadboard.
12. The photographed assembly is a Pi-5-controlled Agon reset actuator used to
    support unattended agent work on the Agon.
13. A P4-controlled Agon reset circuit was contemplated but never realized,
    because no safe VDP/MOS-compliant reverse-UART facility was established on
    the P4. Whether the product P4 needs authority to reset the Agon remains
    undecided.

The chat attachment was not exposed as a local filesystem object and therefore
could not be copied into the task evidence directory. This tracked visual trace
preserves the findings used for inventory; the original photograph should be
added later if it becomes available as a file.

## Interpretation boundary

The reported geometry may be correlated with documented design intent, but it
does not prove present electrical continuity or conformance. Package pinouts
vary, the exact installed part has not been independently identified, and the
reported visual observation is not a qualified net trace.

The legacy reset-actuator document is historical design intent, not present
as-built authority. The breakout is present but electrically unresolved and
must not be actuated, powered as a separate circuit, rewired, or used as reset
evidence until a dedicated unpowered inspection is planned and approved. No
physical action occurred while recording or researching this observation.

## Recovered alternate Pi-to-P4 design intent

The read-only legacy file `design/reset-actuator-module.md`, introduced by
legacy commit `248a835`, defines the intended module as a Pi-controlled 2N2222
open-collector pull-down for the P4 `ESP_EN` reset net:

```text
Pi physical pin 11 / GPIO17 -- 10 kOhm -- transistor base
Pi physical pin 9 / GND ----------------- transistor emitter
P4 EXT2 pin 15 / GND -------------------- transistor emitter
P4 EXT2 pin 14 / ESP_EN ----------------- transistor collector
```

The text records the transistor with its flat face toward the viewer and its
leads left-to-right as emitter, base, collector. It specifies no positive power
connection. Driving Pi `GPIO17` High turns the transistor on and pulls P4
`ESP_EN` Low; setting the GPIO Low or to input releases reset.

This is an alternate configuration of the reusable actuator, not the
photographed as-built endpoint assignment. The photograph records Pi-to-Agon
reset control. The shared transistor topology still makes the legacy text
useful for interpreting the Pi-side base drive, grounding, and probable missing
emitter connection.

Under the operator's stated Pi orientation, the fifth and sixth positions from
the top in the header's left column are physical pins 9 and 11 respectively.
The observed black upper wire therefore occupies the intended Pi ground
position, while the white lower wire occupies the intended `GPIO17` position.
The colors are consistent with black as ground and white as the switched
control signal. White is not a supply rail: `GPIO17` is normally Low or an
input and is driven to 3.3 V only while reset is asserted through the specified
10-kilohm base resistor. This positional and color agreement does not establish
where either wire terminates on the breakout.

If the installed transistor and orientation match the legacy record, the
reported apparently unconnected left lead is the emitter, which the intended
design requires to join both Pi ground and P4 ground. That is a suspected
as-built discrepancy requiring unpowered identification and continuity tests;
it is not yet a fault finding.

## Photograph interpretation

The breadboard is rotated so that each visible vertical group of five holes is
one internally common terminal strip. Against that topology and the Author's
connection description, the photograph supports the following provisional
as-built trace:

1. The transistor's three leads occupy three adjacent vertical strips.
2. The upper resistor connects the middle transistor lead's strip to the strip
   formerly occupied by the white Pi `GPIO17` lead. This agrees with the
   intended 10-kilohm GPIO-to-base path.
3. The lower resistor connects the middle transistor lead's strip to the
   reported black ground strip. This agrees with the optional base-to-emitter
   pull-down only if the emitter is also joined to that ground strip.
4. The left transistor lead occupies the strip immediately to the right of the
   reported ground strip. No component or jumper visibly bridges those strips.
5. The right transistor lead occupies a separate strip consistent with an
   open-collector reset output, but the visible Agon-bound white lead's exact
   insertion point is hidden by its connector shell and remains unverified.

Items 3 and 4 expose a probable assembly omission: the base has a pull-down to
ground, but the recorded left/emitter lead appears to remain floating. If so,
the transistor cannot provide the intended reliable open-collector pull-down.
This strengthens the need for an unpowered trace but still does not substitute
for continuity measurement or identification of the installed transistor's
actual pinout.

The visible pair's Agon destination is now confirmed. It establishes that the
legacy P4 `ESP_EN` text describes another use of the reusable actuator rather
than the photographed configuration. The current Agon reset pin and connector
assignment remain to be recovered from Pi-side automation or other evidence.

## Documentation and implementation findings

1. `design/reset-actuator-module.md` and the legacy `design/README.md` both
   reference `design/reset-actuator-module.svg`.
2. That SVG is absent from every reachable legacy revision, all surviving
   unreachable Git trees and SVG blobs, and the wider `~/Agon` workspace. The
   Markdown was committed with a broken image reference; no drawing was
   recovered.
3. The legacy reset-capture utility does not drive `GPIO17`; it asks the
   operator to press the P4 reset button manually. The Markdown separately
   reports that an earlier bounded 10 ms `GPIO17` pulse worked, but the code
   used for that actuation is not preserved in the repository.
4. The text netlist above is the complete recovered record for the alternate
   Pi-to-P4 `ESP_EN` configuration. No corresponding text or drawing has yet
   been found for the photographed Pi-to-Agon configuration.
5. The legacy claim that a 10 ms pulse proved reset actuation records only that
   the P4 USB device was present afterward. Without a captured reset transition
   or another before/after reset effect, that observation cannot rule out a
   no-op pulse from an open emitter and must not be promoted as qualification.
6. A replacement drawing for either configuration must be generated only after
   the installed component, pinout, terminal-strip continuity, and endpoint
   assignment have been inspected.
7. The historical P4-to-Agon reset concept is a third configuration. It was
   never built and is not a current v1 requirement. Its possible value and its
   dependency on safe P4-to-EMOS/eZ80 communication remain open design matters,
   not properties of the photographed module.
