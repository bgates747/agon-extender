"""Deterministic KiCad projection support for r02 function views.

The checked ``schematic.kicad_sch`` owns presentation geometry and
``connectivity.yaml`` owns electrical topology.  This helper only lets SKiDL's
KiCad writer reproduce a bounded projection at explicit coordinates.  It uses
SKiDL private writer APIs because the public force-directed placer cannot
preserve the Author-arranged schematic geometry; revisit this workaround when
SKiDL changes.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path


REVIEW_DRAWING_DATE = "2026-09-01"


class ProjectionSupportError(ValueError):
    """A function view cannot be generated without ambiguity."""


def split_j1_component(component: dict) -> tuple[dict, dict]:
    """Project physical Agon J1 as independently placed odd/even banks."""

    by_pin = {int(terminal["pin"]): terminal for terminal in component["terminals"]}

    def bank(ref: str, physical_pins: range, value: str) -> dict:
        terminals = []
        for local_pin, physical_pin in enumerate(physical_pins, start=1):
            terminal = copy.deepcopy(by_pin[physical_pin])
            terminal["pin"] = str(local_pin)
            terminal["name"] = f"J1_{physical_pin}_{terminal['name']}"
            terminals.append(terminal)
        return {
            "ref": ref,
            "kind": "connector",
            "orientation": "keyed",
            "terminal_scope": "complete",
            "value": value,
            "description": f"Projection-only {value}; aliases physical Agon J1",
            "terminals": terminals,
        }

    return (
        bank("JO1", range(1, 35, 2), "Agon GPIO odd-pin bank"),
        bank("JE1", range(2, 35, 2), "Agon GPIO even-pin bank"),
    )


def project_j1_member(member: dict[str, str]) -> dict[str, str]:
    """Map one physical Agon J1 terminal to its drawing bank terminal."""

    pin = int(member["pin"])
    return {
        "component": "JO1" if pin % 2 else "JE1",
        "pin": str((pin + 1) // 2 if pin % 2 else pin // 2),
    }


def write_fixed_label_view(
    generator,
    circuit,
    floorplan: dict[str, tuple[int, int, str]],
    output_dir: Path,
    top_name: str,
    title: str,
) -> Path:
    """Write one label-connected schematic at explicit component positions."""

    from skidl import KICAD7
    from skidl.geometry import Point, Tx
    from skidl.schematics.sch_node import SchNode
    from skidl.tools import tool_modules
    from skidl.tools.kicad7.gen_schematic import (
        finalize_parts_and_nets,
        preprocess_circuit,
    )
    from skidl.tools.kicad7.sexp_schematic import write_top_schematic

    parts = {part.ref: part for part in circuit.parts}
    if set(parts) != set(floorplan):
        raise ProjectionSupportError(
            f"floorplan mismatch: missing={sorted(set(parts) - set(floorplan))}, "
            f"extra={sorted(set(floorplan) - set(parts))}"
        )
    for ref, (_, _, symtx) in floorplan.items():
        parts[ref].symtx = symtx

    options = {"orientation_pin_limit": 0}
    preprocess_circuit(circuit, **options)
    node = SchNode(circuit, tool_modules[KICAD7], str(output_dir), top_name, title, 1.0)
    for ref, (x, y, symtx) in floorplan.items():
        parts[ref].tx = Tx.from_symtx(symtx).move(Point(x, y))

    generator.suppress_unsupported_kicad7_erc_probe()
    try:
        output = Path(
            write_top_schematic(
                circuit,
                node,
                str(output_dir),
                top_name,
                title,
                version=20230409,
            )
        )
    finally:
        finalize_parts_and_nets(circuit, **options)
    generator.downgrade_skidl_output_for_kicad7(output)

    text = output.read_text(encoding="utf-8")
    text, count = re.subn(
        r'\(date "\d{4}-\d{2}-\d{2}"\)',
        f'(date "{REVIEW_DRAWING_DATE}")',
        text,
        count=1,
    )
    if count != 1:
        raise ProjectionSupportError("generated schematic lacks its dated title block")
    output.write_text(text, encoding="utf-8")
    return output
