# Light 2 harness r02 function-view definitions

The definitions and deterministic extraction helpers are retained for renewed
focused views of the canonical physical direct-wire schematic. Generated views
from the superseded functional-symbol schematic were removed rather than left
as stale construction evidence.

The current extractor stops safely when direct-wire geometry touches more than
one selected electrical net. It must be updated and requalified for the
physical canonical drawing before generated signal views are restored. Do not
weaken or bypass that check merely to produce drawings.

This directory contains deterministic, non-authoritative projections of the
maintained r02 schematic. Each drawing is made by copying
`../schematic.kicad_sch`, retaining all 45 source symbol blocks unchanged, and
deleting connectivity graphics that do not belong to the signal or circuit
function selected in `views.yaml`.

The views make one path reviewable without redefining it. Electrical topology
remains owned exclusively by `../connectivity.yaml`; the maintained complete
human drawing remains `../schematic.kicad_sch`. The generator rejects every
endpoint absent from the connectivity authority and verifies each generated
KiCad netlist before publishing its schematic and explicit-white SVG.

Generated filenames use the required `schematic_` prefix followed by the
function descriptor. For example:

1. `generated/schematic_d0-uart-rx-lane.kicad_sch`;
2. `generated/schematic_ready-n.kicad_sch`; and
3. matching `.svg` files for human viewing.

The 19 projections cover D0 through D7, CLOCK, VALID_N, READY_N, the four
control functions, both 3.3 V domains and bypassing, common ground, and the
startup/fail-safe bias network. Every retained wire, junction, and global net
label is the original master-schematic block at its original coordinates. This
preserves the Author's wire routing and purposeful label placement, including
the positions that communicate bypass-capacitor associations. Temporary
named-net stubs are used only to locate selected source endpoints and never
appear in a published view. Unrelated symbols remain visible as placement
context.

Generate and then verify from the repository root:

```text
.venv/bin/python \
  hardware/designs/light2-harness-r02/signal-views/generate_signal_views.py \
  --write
.venv/bin/python \
  hardware/designs/light2-harness-r02/signal-views/generate_signal_views.py
```
