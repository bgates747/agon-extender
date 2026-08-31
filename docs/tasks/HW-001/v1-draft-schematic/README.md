# HW-001 V1 draft schematic workspace

This directory retains the task-local KiCad bootstrap inputs used to establish
the frozen r02 model and its maintained human schematic.

1. `hardware/designs/light2-harness-r02/connectivity.yaml` is the frozen
   placement-independent electrical authority.
2. `kicad-projection.yaml` and `HW001_Draft.kicad_sym` preserve the checked
   projection metadata and custom logic symbols used during schematic design.
3. `generate_draft_inputs.py --check` deterministically reproduces and checks
   the frozen authority and projection metadata. Its explicit
   `--write-authority` mode must never be used to revise r02 in place.
4. The accepted complete human drawing has been promoted out of this task
   workspace to `hardware/designs/light2-harness-r02/schematic.kicad_sch`.
   Its XML and explicit-white SVG projections and dedicated checker live beside
   it. Experimental whole-circuit layouts and transformation scripts were
   removed after promotion.
5. The task-local signal atlas was removed after promotion because its component
   placement was obsolete and the maintained complete schematic superseded its
   review function. It remains recoverable from prior Git history.
