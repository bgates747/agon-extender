# HW-001 signal-oriented views

This directory is the working home for deterministic signal-, lane-, and
mux-oriented projections of the shared V1 circuit model. Each signal view
should follow one logical path from its originating endpoint through every
component that materially affects it to its destination endpoint. For
multiplexed D0--D3 lanes, the view must show every represented use and the
controls determining which buffers may drive the physical lane.

This is the sole retained schematic-projection family. Its task-local
`kicad_projection_support.py`, `kicad_sexpr.py`, and
`set_svg_white_background.py` files are neutral generation and validation
helpers; they do not define electrical connectivity.

View 0 defines the atlas coordinate system:

0. Canonical component placement. This generated wire-free drawing contains every
   component, including split JO1/JE1 Agon banks at left and both P4 banks at
   right. ICs, capacitors, and resistors use explicit staggered coordinates to
   avoid misleading alignment. It is the placement authority for this atlas,
   not an electrical-connectivity authority.

The complete view 0--19 atlas is generated and mechanically checked against
the frozen r02 authority. The stable signal/infrastructure view inventory is:

1. D0 / UART RX lane.
2. D1 / UART TX lane.
3. D2 / UART CTS lane.
4. D3 / UART RTS lane.
5. D4 lane.
6. D5 lane.
7. D6 lane.
8. D7 lane.
9. CLOCK.
10. VALID_N.
11. READY_N.
12. UART-forward enable.
13. Parallel-forward enable.
14. UART-return enable.
15. READY control.
16. Agon 3.3 V domain and bypassing.
17. P4 3.3 V domain and bypassing.
18. Common ground.
19. Startup and fail-safe bias network.

Items 1--15 are signal/control slices. Items 16--19 account for infrastructure
that cannot truthfully belong to only one signal. The shared model above this
directory remains the electrical source for every projection. A deterministic
coverage check proves that every connected canonical terminal is represented
by at least one appropriate view without redefining connectivity here.

Every signal/control view after 0 shows all 45 components with the same page
geometry, references, relative positions, orientations, and header-bank
arrangement declared by view 0. Only the represented connections and active-pin
annotations change between slices. The KiCad writer may apply one uniform page
offset but must not compact, reorder, rotate, or move any component relative to
another.
Views 1--15 use literal wires for every represented net. Infrastructure views
16--19 use conventional named-net labels: their dense shared power, ground,
and bias membership made literal wiring less legible and created unacceptable
accidental-pin hazards. Exported KiCad netlists, rather than presentation
style, prove every view's exact endpoint partition.

## Files and regeneration

1. `canonical-placement.yaml` is the machine-readable atlas placement
   authority in mils. It gives all 45 projected components explicit positions
   and orientations. U1--U4, C1--C6, and R1--R31 each have unique X
   coordinates within their component class.
2. `generate_signal_views.py` generates view 0 and the implemented atlas
   projections from the shared electrical model.
3. `check_signal_views.py` proves that view 0 contains exactly those 45
   components, that IC/capacitor/resistor staggering is present, and that the
   placement plate contains no wires, labels, junctions, or no-connect marks.
   For implemented signal views it also proves all-component scope, canonical
   relative placement, exact active-header annotations, wire count, and the
   declared endpoint partition exported by KiCad.
4. `generated/00-*.{kicad_sch,xml,svg}` is the placement plate;
   `generated/01-*` through `generated/19-*` are the complete machine and human
   review outputs.

## View 1 scope — D0 / UART RX

View 1 follows Agon `PC0/TXD1/D0` through U1 and R1 to P4
`GPIO22/D0/UART RX`. It also includes the P4-domain R14 inactive pull-up, U1's
output-enable input, the U4 control channel driven by P4
`GPIO15/UART FORWARD OE_N`, and the Agon-domain R25 and P4-domain R28 pull-ups
that establish the represented control defaults. Shared IC supply, ground, and
bypass terminals belong to infrastructure views 16--18 and are deliberately
not duplicated here.

All unrelated components remain visible as placement context but have no
connectivity graphics. The generator builds the complete canonical circuit so
KiCad creates every symbol normally, selects only the requested endpoint labels
for literal-wire conversion, and removes all other labels and no-connect marks.

## View 2 scope — D1 / UART TX

View 2 shows both mutually exclusive uses of the shared D1 conductor. During a
parallel-forward epoch, Agon `PC1/RXD1/D1` enters U1 and reaches P4 GPIO12
through R2. During a UART epoch, P4 GPIO12 enters U3 and reaches Agon
`PC1/RXD1/D1` through R11. It includes the U4 low-only controls and pull-ups for
both `PARALLEL_FORWARD_OE_N` and `UART_RETURN_OE_N`, together with the grounded
U4 data inputs that make those controls release-or-pull-low rather than
push-pull. The two data drivers must never be enabled together.

Two explicit orthogonal detours prevent the UART-return enable wire from
crossing U3's data input and the GPIO21 control wire from touching unrelated U4
and pull-up endpoints. The geometry validator rejects either accidental join,
and the exported KiCad netlist must reproduce the exact eleven-net endpoint
partition.

## Views 3--15 scope

Views 3 and 4 complete the lower-nibble UART multiplexing survey. D2/CTS uses
the forward-only U1 pattern shared with D0/RX. D3/RTS, like D1/TX, shows
mutually exclusive U1 parallel-forward and U3 UART-return drivers.

Views 5--8 follow D4--D7 through U2, their source-series resistors, inactive
pull-downs, and shared parallel-forward control. Views 9 and 10 apply the same
treatment to CLOCK and active-low VALID. View 11 follows the P4-owned U4
low-only READY control through R13 to Agon PD4 and its Agon-domain pull-up.

Views 12--15 isolate the four P4-owned U4 control functions: UART forward,
parallel forward, UART return, and READY. Each includes all four grounded U4
data inputs so the release-or-pull-low mechanism is explicit. Deterministic
detours route ground and control wiring around interleaved U4 pins.

## Views 16--19 scope

Views 16 and 17 record the Agon and P4 3.3 V domains, local bypass/bulk
capacitors, powered ICs, pull-up loads, and required ground endpoints. View 18
records complete common-ground membership. View 19 collects every selected net
touching R14--R31 to expose startup and fail-safe bias behavior.

SKiDL 2.3.0 drops a small set of resistor endpoints from dense bounded
label-based projections. Views 17 and 19 omit duplicated R25, R29, and R31
endpoints that are retained and exactly validated in dedicated views 11--15.
The atlas-wide checker still requires the union of views 1--19 to cover every
connected canonical terminal.

Run from the project root. `--views 3 7 19` may be supplied to regenerate only
selected additional views while developing; omit it for a full regeneration:

```sh
.venv/bin/python \
  docs/tasks/HW-001/v1-draft-schematic/signal-views/generate_signal_views.py

for schematic in \
  docs/tasks/HW-001/v1-draft-schematic/signal-views/generated/[0-1][0-9]-*.kicad_sch
do
  stem=${schematic##*/}
  stem=${stem%.kicad_sch}
  kicad-cli sch export netlist --format kicadxml \
    -o "docs/tasks/HW-001/v1-draft-schematic/signal-views/generated/$stem.xml" \
    "$schematic"
  .venv/bin/python docs/tasks/HW-001/normalize_kicad_netlist.py \
    "docs/tasks/HW-001/v1-draft-schematic/signal-views/generated/$stem.xml"
  kicad-cli sch export svg --no-background-color \
    -o docs/tasks/HW-001/v1-draft-schematic/signal-views/generated \
    "$schematic"
  .venv/bin/python \
    docs/tasks/HW-001/v1-draft-schematic/signal-views/set_svg_white_background.py \
    "docs/tasks/HW-001/v1-draft-schematic/signal-views/generated/$stem.svg"
done

.venv/bin/python \
  docs/tasks/HW-001/v1-draft-schematic/signal-views/check_signal_views.py
```
