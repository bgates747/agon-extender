# SETUP-006.3 Fritzing wiring-diagram scaffold

This directory contains the accepted canonical, task-local, reproducible
Fritzing representation of the prototype's unwired breadboard and Olimex
ESP32-P4-DevKit Rev D1 placement. The Author froze this scaffold on 2026-08-25
as the mechanical and diagrammatic base for subsequent SETUP-006 wiring work.

## Scope

The scaffold represents mechanically and electrically relevant placement facts
in a diagrammatic breadboard view:

1. The BusBoard BB1460 supplies two detachable 630-tie-point terminal areas.
   Each terminal area has 63 numbered columns on a 0.1-inch grid.
2. Both detachable 100-tie-point BB100R distribution strips are installed in
   the observed physical layout: one along the top edge and one shared between
   the two terminal areas. Each retains its 0.35-inch overall width. Its two
   contact rows occupy the center, while the red and blue polarity-color
   legends straddle rather than pass through those rows. In this landscape
   drafting orientation, each blue/GND rail is above its red/hot rail; the hot
   rail voltage and source remain unspecified.
3. The P4 DevKit has two 20-pin, 0.1-inch headers whose centerlines are exactly
   1.0 inch apart.
4. P4 header pin 1 is placed at breadboard column 1. The USB Serial/JTAG end of
   the P4 therefore overhangs the numbered end of the breadboard.
5. Each P4 header occupies the middle hole of the facing five-hole terminal
   group, leaving two holes exposed on both sides of that header.
6. The P4 body is Olimex red and is deliberately drawn flush with the outer
   edges of its two header rows. This is not the physical 30 mm PCB silhouette;
   it keeps adjacent breadboard sockets unobscured in the wiring diagram.
7. The P4 is rotated clockwise from Olimex's canonical drawing orientation:
   Ethernet, canonically up, is at the right in this landscape breadboard view.
   EXT1 and EXT2 pin numbers and signal names are consequently printed 90
   degrees clockwise immediately inward from their corresponding header pads.
8. The Agon even-pin harness bank is a distinct 16-contact part on the upper
   terminal area's outermost row, spanning columns 6–21. Its left-to-right
   order is pins 32, 30, ..., 2.
9. The Agon odd-pin harness bank is a distinct 16-contact part on the lower
   terminal area's outermost row, spanning columns 4–19. Its left-to-right
   order is pins 31, 29, ..., 1.
10. Rotating the landscape view counterclockwise restores the accepted
    canonical orientation: even pins face P4 EXT1 at board left, odd pins face
    P4 EXT2 at board right, and the low Agon pin numbers are at the top.
11. Agon pins 33 and 34 are not contacts in either breadboard header. Their
    separate power wiring is deliberately omitted from this drawing stage.
12. Both Agon header parts are compact, label-free colored contact blocks.
    Two separate movable label-bank parts contain the corresponding labels:
    exactly 16 odd-pin labels and exactly 16 even-pin labels. Each bank uses
    exact 0.1-inch breadboard-hole pitch, 0.5-inch label depth, matching colors,
    and left-justified `number name` text. Their clockwise rotation is baked
    into the SVGs so the strips initially align horizontally outside their
    corresponding headers without a Fritzing instance transform. Labels
    identify only official physical Agon pin names and immutable eZ80 mux
    roles—most notably `13 PD4 / RTS1`,
    `14 PD5 / CTS1`, `17 PC0 / RXD1`, and `19 PC2 / TXD1`. Mutable Extender
    functions such as `READY_N`, `VALID_N`, and parallel-data assignments
    belong in the wiring and design records.
13. Column indices increase from left to right. The outer index series sit
    immediately above the top Agon header and below the bottom Agon header.
    Additional index series in both BB630 center grooves are deliberate
    diagram-only orientation aids; those interior legends are not printed on
    the physical breadboards.

Each BB100R overlaps its neighboring snap edge by half a 0.1-inch grid
interval. This preserves the exact 1.0-inch P4 header spacing and captures the
alignment that was difficult to achieve by hand in Fritzing.

Except for the two recovered Agon header banks, the generated sketch does
**not** specify product wiring, hot-rail voltage, power-source ownership, signal
conditioning, component placement, or an electrically safe test configuration.
In particular, the color-coded Agon contacts are not yet routed to P4 GPIO.
Those remain outputs of the subsequent firmware-driven electrical design
review and qualification tasks.

## Why generated

Fritzing's interactive placement proved unreliable for aligning detachable
breadboard sections and overlapping grid-sensitive parts. The source generator
therefore owns all dimensions, connector coordinates, internal breadboard
buses, and part placement. The `.fzz` is a generated review artifact, not the
only editable authority.

### Fritzing integration constraints discovered during review

The first generated draft reproduced correctly in the standalone SVG but not
inside Fritzing. The Author's saved `_usermod` sketch exposed three format
details that the generator must preserve:

1. Fritzing sketch geometry uses 90 scene units per inch while its part SVGs
   conventionally use 72 SVG units per inch. Sketch placement must convert
   between them explicitly.
2. `breadboardbreadboard` is Fritzing's special always-underneath layer. It is
   correct for the BB1460 but caused the P4 to be obscured. The P4 uses the
   normal `breadboard` layer.
3. The P4 SVG includes deliberate transparent padding. Its part origin and all
   40 connectors now share the BB1460 holes' phase relative to the 0.1-inch
   grid. Moving the P4 with **Align to Grid** enabled should therefore preserve
   header alignment instead of snapping the headers between holes.
4. The corrected P4 part uses a new Fritzing-only module revision whenever its
   integration geometry changes.
   Fritzing caches imported custom parts by module ID, so retaining the first
   identity could cause it to reuse the defective layer and placement metadata
   after the `.fzz` itself had been regenerated.
   The generated Agon header parts follow the same rule; removing their
   integrated labels advanced each header from Fritzing revision `r01` to
   `r02`, preventing cached label-bearing artwork from reappearing.
5. On the locally installed Fritzing 1.0.1 Linux build, the Author's first
   saved review sketch showed a first-arrow displacement of +0.05 inch
   horizontally and +0.025 inch vertically. That displacement was initially
   consistent with an off-grid canvas center, so revisions `r03` and `r02`
   padded the P4 and BB1460 canvases to 0.1-inch dimensions. Repeating the test
   with both padded revisions produced the same displacement, disproving canvas
   center as the controlling cause. P4 part revision `r04` adds the accepted
   landscape-orientation pin labels without reusing cached `r03` artwork.
6. This local trigger sits inside a broader unresolved Fritzing limitation. The
   part format cannot designate a connector as the per-view alignment origin,
   and reports show Fritzing choosing an unsuitable or changing anchor. The
   behavior has been observed on multiple operating systems and releases; no
   reliable evidence establishes one OS as the sole cause. Treat the generated
   coordinates as authority and lock accepted placement. During review, use
   `_usermod` files only to recover observed coordinates into the generator;
   they are disposable after the corresponding canonical revision is accepted.
7. The decisive GUI review selected each padded part and pressed Right Arrow
   once. Fritzing applied the same +0.05-inch horizontal and +0.025-inch
   vertical translation to both. Their relative geometry remained exact, and
   the terminal holes and P4 headers moved from grid-cell interiors onto grid
   intersections. The generator now emits these observed post-snap scene
   coordinates directly: BB1460 `(4.5, 2.25)` and P4 `(-40.5, 74.25)` in
   Fritzing's 90-unit-per-inch scene coordinates.
8. Moving the BB1460 after a displaced P4 also caused the breadboard sockets to
   capture the P4 header pins. If recovery is needed, move the breadboard until
   its sockets capture both headers, verify the fit visually, and lock both
   parts.
9. Fritzing 1.0.1 visibly overlaid or dropped text from adjacent SVG `<tspan>`
   elements even though Inkscape rendered the same files correctly. The label
   label banks therefore use one complete plain `<text>` node per label. The
   original one-part-per-label draft also used 0.16-inch row spacing, which did
   not match the breadboard. Each accepted 16-label bank derives every row from
   the common 0.1-inch `PITCH` constant.
10. The first combined 32-label palette was a normal custom part with zero
    connectors. Fritzing substituted a second copy of the P4 artwork at its
    position instead of rendering it. Each replacement 16-label bank therefore
    has one invisible, unconnected connector named `Non-electrical Fritzing
    placement anchor`. It is solely a loader workaround, carries no net, and
    must never be interpreted as an electrical label-bank terminal.
11. The Author's saved `_usermod` review placed each 16-label bank outside its
    matching header, rotated it clockwise into a horizontal strip, and showed
    that the original 1.0-inch label depth was excessive. The generated banks
    preserve that orientation with 0.5-inch depth. Their invisible anchors are
    placed at local `(0.05, 0.05)` inch, and generated scene origins put those
    anchors directly on Fritzing's 0.1-inch grid. This avoids relying on the
    application's unstable rotation and snap calculations.
    These geometry changes advanced both bank module identities from `r01` to
    `r02` so Fritzing cannot reuse the earlier cached vertical artwork.
12. The SETUP-006.4 schematic audit found that P4 part `r04` transposed the
    printed GPIO16 and GPIO17 names. Official Rev D1 connectivity is EXT1-17 =
    GPIO16 and EXT1-18 = GPIO17. P4 part `r05` corrects those labels without
    changing connector IDs, coordinates, or any other geometry. The module
    identity advanced so Fritzing cannot reuse cached `r04` artwork.

These are Fritzing-format workarounds, not physical dimensions or electrical
design decisions. Locally saved `*_usermod.fzz` files are review evidence and
are ignored rather than treated as generated authority.

## Inputs

1. [BusBoard BB1460 product data](https://www.busboard.com/BB1460): 1260 terminal-area tie points, two 100-point
   distribution strips, detachable sections, and 0.1-inch terminal convention.
2. [BusBoard BB100R product data](https://busboard.com/BB100R): two 50-point
   physical power-rail rows in each detachable distribution strip.
3. [Official Olimex ESP32-P4-DevKit hardware](https://github.com/OLIMEX/ESP32-P4-DevKit): Rev D1 KiCad PCB with a 30 mm by 72 mm board outline, two 1x20
   2.54 mm headers, and 25.4 mm header-center separation.
4. Author's physical description: one BB100R along the top edge and one between
   the terminal areas; P4 centered over the latter; two free holes around each
   header; pin 1 at column 1; USB connection overhanging the end.
5. [Fritzing issue #3927](https://github.com/fritzing/fritzing-app/issues/3927):
   the part format has no declared connector origin and grid alignment may
   choose between unsuitable connector phases.
6. [Fritzing forum alignment report](https://forum.fritzing.org/t/pins-not-lining-up-with-breadboard/19380):
   intermittent 0.05-inch offsets, changing anchors after reload, and the
   practical align-at-0.05-inch-then-lock workaround.
7. [Fritzing Linux notes](https://github.com/fritzing/fritzing-app/wiki/1.3-Linux-notes):
   official AppImage and Qt Wayland/X11 guidance. This workstation uses a
   Wayland session, but the available evidence does not tie the observed part
   jump specifically to Wayland.
8. `hardware/designs/light2-harness-r01/legacy-evidence/wiring-diagram.svg`:
   accepted Agon odd/even pin identities, legacy color coding, and EXT1/EXT2
   side ownership. Its separate pin 33/34 leads are out of scope here.
9. `hardware/designs/light2-harness-r01/legacy-evidence/carrier-breakout-design.md`:
   text authority that Agon even pins face board-left P4 EXT1 and odd pins face
   board-right P4 EXT2.
10. Official `agon-docs` files `docs/GPIO.md` and
    `docs/images/iopinsAL2.png`: physical header names and the immutable UART1
    mux roles `RTS1`, `CTS1`, `RXD1`, and `TXD1`.

## Intended outputs

1. A portable `.fzz` containing the sketch, composite breadboard, P4, and the
   two distinct Agon 1x16 header parts plus separate 16-label odd and even
   movable banks.
2. Portable, independent P4 and accepted composite-breadboard `.fzpz` bundled
   parts suitable for importing separately into Fritzing's My Parts bin.
3. A standalone SVG preview for review without Fritzing.
4. Deterministic source files and structural validation suitable for revision
   control and later extension with electrical wiring.

## Install the custom parts in My Parts

1. In Fritzing, open the **My Parts** bin.
2. Use the bin menu's **Import…** command and select
   `generated/agon-extender-olimex-esp32-p4-devkit-rev-d1-fritzing-r05.fzpz`.
3. Repeat the import for
   `generated/agon-extender-bb1460-two-rail-scaffold-fritzing-r04.fzpz`.
4. Confirm that the labeled Olimex P4 D1 and composite breadboard appear as
   separate parts in My Parts.
5. Use **Save Bin** from the bin menu so the imported parts remain available
   after Fritzing exits. Fritzing stores imported user parts in its local user
   data and parts database; do not copy package members there by hand.

## Regeneration and validation

From the repository root:

```sh
python3 docs/tasks/SETUP-006/SETUP-006.3-fritzing/generate.py
python3 docs/tasks/SETUP-006/SETUP-006.3-fritzing/generate.py --check
unzip -t docs/tasks/SETUP-006/SETUP-006.3-fritzing/generated/light2-extender-breadboard-scaffold.fzz
```

The generator validates XML well-formedness, unique connector identities,
1,460 breadboard sockets, 40 P4 pins, exactly 16 contacts in each Agon header,
the exclusion of Agon pins 33/34 from both headers, exact pitch and placement,
two label-bank parts containing exactly 16 plain-text labels each on exact
0.1-inch pitch and 0.5-inch depth, their required invisible non-electrical
loader anchors, exact official label text, matching colors, left justification,
immutable UART1 mux names, absence of Extender-specific mappings,
grid-compatible anchor and scene coordinates, required sketch and bundled-part
archive contents, and deterministic output bytes. The generated `SHA256SUMS`
records the sketch and both independent bundled-part identities.

Fritzing 1.0.1's official batch SVG exporter could not be used as a final
headless acceptance test in this environment: it waits indefinitely under the
offscreen Qt backend for both this sketch and a packaged stock example. The
standalone preview was successfully rendered with Inkscape. The Author
completed normal Fritzing GUI review and accepted this canonical scaffold on
2026-08-25.
