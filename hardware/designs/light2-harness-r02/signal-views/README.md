# Light 2 harness r02 function views

This directory contains deterministic, non-authoritative projections of the
maintained r02 schematic. Each drawing is made by copying
`../schematic.kicad_sch` and retaining all 45 source symbol blocks unchanged.
Wires belonging to the signal or circuit function selected in `views.yaml`
remain ordinary green electrical wires. Every other canonical wire segment is
converted to a light-gray graphical polyline at the same coordinates. The gray
context therefore remains visible in KiCad and SVG without reconnecting the
focused circuit or appearing in its exported netlist.

The temporary SKiDL label view uses conventional functional IC symbols, while
the canonical drawing uses custom physical top-view DIP symbols. The extractor
therefore derives U1--U4 pin coordinates from the embedded symbol definitions
in both files and remaps temporary markers onto the canonical physical pins.
This remapping changes presentation geometry only. Every generated view is
subsequently exported through KiCad and its endpoint partitions must match the
selected canonical nets exactly.

The views make one path reviewable without redefining it. Electrical topology
remains owned exclusively by `../connectivity.yaml`; the maintained complete
human drawing remains `../schematic.kicad_sch`. The generator rejects every
endpoint absent from the connectivity authority and verifies each generated
KiCad netlist before publishing its schematic and explicit-white SVG.
The generator also proves that every canonical master wire appears exactly
once in each view: either unchanged as a selected electrical wire or as the
prescribed gray non-electrical context. It rejects invented, missing, or
modified context segments.

Generated filenames begin with the zero-padded construction and qualification
order, followed by the required `schematic_` role prefix and function
descriptor. Each KiCad schematic has a matching `.svg` for human viewing.
`views.yaml` is the ordering authority; the generator rejects duplicate,
missing, or non-contiguous order numbers. The combined power-domain view is the
first construction and qualification stage; separate power-domain views are
intentionally omitted as redundant.

The controlled order is:

1. `01_schematic_power-domains` (combined common ground and both 3.3 V
   domains);
2. `02_schematic_startup-and-fail-safe-bias-network`;
3. `03_schematic_uart-forward-enable`;
4. `04_schematic_d0-uart-rx-lane`;
5. `05_schematic_d2-uart-cts-lane`;
6. `06_schematic_uart-return-enable`;
7. `07_schematic_d1-uart-tx-lane`;
8. `08_schematic_d3-uart-rts-lane`;
9. `09_schematic_parallel-forward-enable`;
10. `10_schematic_d4-lane`;
11. `11_schematic_d5-lane`;
12. `12_schematic_d6-lane`;
13. `13_schematic_d7-lane`;
14. `14_schematic_clock`;
15. `15_schematic_valid-n`;
16. `16_schematic_ready-control`; and
17. `17_schematic_ready-n`.

This sequence establishes common ground, both power domains and their
bypassing, and fail-safe biasing before any active transport. It then brings up
the complete forward UART path before the reverse UART path, adds the remaining
parallel data lanes in numeric order, and finishes with the parallel strobes
and READY return path.

Use this order through the accepted
[staged circuit validation process](../../../../docs/qualification/staged-circuit-validation.md).
The operator records the cumulative installed subset; a view's gray context
neither connects an omitted wire nor proves previous construction. Power/bias
measurements may use passive diagnostic firmware. Active stages exercise
applicable production-candidate components without requiring a complete release
image, and retain stage-specific safety and evidence gates. These views are
construction guidance, not executable test procedures or passed results.

The 17 projections cover combined power and ground, D0 through D7, CLOCK,
VALID_N, READY_N, the four control functions, and the startup/fail-safe bias
network. Every selected wire, junction, and global net label is the original
master-schematic block at its original coordinates. This
preserves the Author's wire routing and purposeful label placement, including
the positions that communicate bypass-capacitor associations. Temporary
named-net stubs are used only to locate selected source endpoints and never
appear in a published view. Unrelated symbols and gray wire routes remain
visible as placement and breadboard-routing context.

Generate and then verify from the repository root:

```text
.venv/bin/python \
  hardware/designs/light2-harness-r02/signal-views/generate_signal_views.py \
  --write
.venv/bin/python \
  hardware/designs/light2-harness-r02/signal-views/generate_signal_views.py
```
