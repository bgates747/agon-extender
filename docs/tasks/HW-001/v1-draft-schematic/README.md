# HW-001 V1 draft schematic workspace

This directory keeps the task-local KiCad projection inputs and separates each
human-view projection family so drawings remain easy to locate.

1. `hardware/designs/light2-harness-r02/connectivity.yaml` is the frozen
   placement-independent electrical authority.
2. `kicad-projection.yaml` and `HW001_Draft.kicad_sym` are shared task-local
   projection inputs consumed by every view family.
3. `generate_draft_inputs.py --check` deterministically reproduces and checks
   the frozen authority and projection metadata. Its explicit
   `--write-authority` mode must never be used to revise r02 in place.
4. `signal-views/` contains canonical placement, the complete 1--19 signal,
   mux, control, and infrastructure atlas, and the neutral KiCad helpers needed
   to generate and validate that family.

The view-family directory owns its generated KiCad, XML, and SVG outputs and
documents its regeneration and validation commands.
