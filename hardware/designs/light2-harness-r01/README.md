# Light 2 harness r01

This revision is predecessor evidence. The later buffered r02 construction is
held; the [current hardware index](../../README.md) distinguishes that circuit
from active simplified r03 wiring and its bounded evidence.
The revision-specific descriptions below preserve its original scope and do
not make it the current UART or forward-transport test target.

`light2-harness-r01` is the authoritative first electrical and pin-assignment
target for the Agon Light 2 to Olimex ESP32-P4-DevKit Rev D1 prototype. It is a
clean-project adoption of the mature predecessor breadboard design, not a new
unproven pin assignment.

The normative machine-readable definition is [`profile.yaml`](profile.yaml).
This document explains its scope. In conflicts, authority order is:

1. `profile.yaml`;
2. this README;
3. textual files under `legacy-evidence/`; and
4. SVG diagrams under `legacy-evidence/`.

## Selected first design target

The selected forward transport is an eight-bit Agon-to-P4 bus:

| Function | Agon signal / header pin | P4 GPIO / header pin | Direction |
|---|---|---|---|
| `D0` | `PC0` / 17 | GPIO22 / EXT2-11 | Agon → P4 |
| `D1` | `PC1` / 18 | GPIO12 / EXT1-13 | Agon → P4 |
| `D2` | `PC2` / 19 | GPIO23 / EXT2-10 | Agon → P4 |
| `D3` | `PC3` / 20 | GPIO11 / EXT1-12 | Agon → P4 |
| `D4` | `PC4` / 21 | GPIO32 / EXT2-9 | Agon → P4 |
| `D5` | `PC5` / 22 | GPIO10 / EXT1-11 | Agon → P4 |
| `D6` | `PC6` / 23 | GPIO33 / EXT2-8 | Agon → P4 |
| `D7` | `PC7` / 24 | GPIO9 / EXT1-10 | Agon → P4 |
| `READY_N` | `PD4` / 13 | GPIO20 / EXT2-13 | P4 → Agon, open drain |
| `CLOCK` | `PD5` / 14 | GPIO14 / EXT1-15 | Agon → P4 |
| `VALID_N` | `PD7` / 16 | GPIO13 / EXT1-14 | Agon → P4 |

The first target retains 220-ohm series resistance on every data conductor,
10-kilohm pull-ups on `READY_N` and `VALID_N`, and a 10-kilohm pull-down on
`CLOCK`. Agon pin 33 and P4 EXT1 pin 2 provide the proved common signal ground.
Agon pin 34 supplies only the existing 3.3 V logic reference; it is not
authorization to join independently powered board rails.

The mapping preserves the predecessor's deliberate installed-view geometry:
odd Agon signals route to board-right EXT2 and even signals route to board-left
EXT1 without permuting the data bus. P4 header numbering runs from the Ethernet
end toward the USB end as documented in the vendored pinout source.

## Evidence and qualification boundary

The predecessor project physically exercised this pin map. Its retained
results report:

- complete forward records received through the P4 PARLIO path;
- approximately 0.84 MiB/s useful endpoint payload at the fastest tested
  zero-delay eZ80 sender profile;
- analyzer-confirmed control timing and partial observed data-bus agreement;
  and
- subsequent bounded ownership experiments on the optional PC0/PC1 buffered
  circuit.

Those results establish a mature prototype baseline. This adopted revision is
still a **candidate** for the clean project because production isolation,
either-order power safety, final connectors, and the current product's complete
transport architecture have not been qualified together.

## Buffered legacy-UART candidate

The predecessor's bounded 115,200-baud "reverse UART" experiment is the same
buffered `PC0`/`PC1` physical path intended for the official legacy UART
contract, not a separate candidate product channel. The fixture deliberately
reduced the rate by a factor of ten to establish wiring, framing, direction,
and break-before-make correctness before testing electrical margin.

Revision r01 therefore selects this circuit as the first legacy-UART wiring
target: GPIO22 receives from Agon `PC0`, GPIO12 drives toward Agon `PC1`, GPIO15
controls `FWD_OE_N`, and GPIO21 controls `REV_OE_N` through the documented
`SN74HC125N`/`SN74LV125AN` topology. Existing evidence qualifies bounded
operation at 115,200 baud only. The required 1,152,000-baud rate, complete
legacy flow-control behavior, and coexistence with the parallel bus remain
qualification and integration gates; the lower-rate pass must not be cited as
proof of target-speed capability.

## Explicit non-authority

Likewise, the vendored SVGs are useful installed-view references but are not
construction authority. Their layout and presentation deficiencies must not
override the YAML profile or text.

## Required change control

Moving a wire, changing a resistor or pull, selecting the reverse circuit,
changing ownership, or altering the power boundary requires Author approval
and a new harness revision. Qualification runs must use committed definitions
and identify the exact revision under `docs/versions/README.md`.
