"""Deterministic KiCad projection helpers used by the HW-001 signal atlas.

These functions are retained from the superseded component-view generator.
They contain no electrical design authority: connectivity remains owned by
``hardware/designs/light2-harness-r02/connectivity.yaml``.

This file exists because SKiDL 2.3.0's public force-directed placer cannot
express the task's role-based floorplan constraints. It deliberately uses
SKiDL private preprocessing and KiCad writer APIs while replacing placement
with explicit coordinates. Review this workaround when SKiDL changes.
"""

from __future__ import annotations

import copy
import re
import uuid
from pathlib import Path


HEADER_ANNOTATION_OFFSET_MM = 8.255
REVIEW_DRAWING_DATE = "2026-08-28"


class ProjectionSupportError(ValueError):
    """A schematic projection cannot be generated without ambiguity."""


def split_j1_component(component: dict) -> tuple[dict, dict]:
    """Project physical J1 as independently placeable odd/even banks."""

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
            "description": (
                f"Projection-only {value}; aliases physical Agon connector J1"
            ),
            "terminals": terminals,
        }

    return (
        bank("JO1", range(1, 35, 2), "Agon GPIO odd-pin bank"),
        bank("JE1", range(2, 35, 2), "Agon GPIO even-pin bank"),
    )


def project_j1_member(member: dict[str, str]) -> dict[str, str]:
    """Map one physical J1 terminal to its projection-only bank terminal."""

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
    """Use SKiDL's writer with explicit placement and no automatic routing."""

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

    # SKiDL injects the host date, which would make deterministic projections
    # change merely because regeneration crossed midnight.
    text = output.read_text(encoding="utf-8")
    text, count = re.subn(
        r'\(date "\d{4}-\d{2}-\d{2}"\)',
        f'(date "{REVIEW_DRAWING_DATE}")',
        text,
        count=1,
    )
    if count != 1:
        raise ProjectionSupportError(
            "generated schematic has no unique title-block date"
        )
    output.write_text(text, encoding="utf-8")
    return output


def stable_uuid(net_id: str, index: int, view_namespace: str) -> str:
    """Return a stable UUID for one generated projection element."""

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"https://github.com/tomm/agon-extender/hw-001/"
            f"{view_namespace}/{net_id}/{index}",
        )
    )


def wire_block(
    net_id: str,
    index: int,
    start: tuple[str, str],
    end: tuple[str, str],
    view_namespace: str,
) -> str:
    """Build one deterministic literal KiCad wire block."""

    return (
        f"  (wire (pts (xy {start[0]} {start[1]}) (xy {end[0]} {end[1]}))\n"
        "    (stroke (width 0) (type default))\n"
        f"    (uuid {stable_uuid(net_id, index, view_namespace)})\n"
        "  )"
    )


def header_annotation_block(
    net_id: str,
    text: str,
    point: tuple[float, float],
    side: str,
    view_namespace: str,
) -> str:
    """Place a non-electrical pin/function annotation outside one header."""

    if side == "left":
        x = point[0] - HEADER_ANNOTATION_OFFSET_MM
        justification = "right"
    elif side == "right":
        x = point[0] + HEADER_ANNOTATION_OFFSET_MM
        justification = "left"
    else:
        raise ProjectionSupportError(
            f"{net_id}: invalid header-label side {side}"
        )
    annotation_uuid = uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"https://github.com/tomm/agon-extender/hw-001/"
        f"{view_namespace}/header-label/{net_id}",
    )
    return (
        f'  (text "{text}" (at {x:.3f} {point[1]:.2f} 0)\n'
        f"    (effects (font (size 1 1)) (justify {justification}))\n"
        f"    (uuid {annotation_uuid})\n"
        "  )"
    )


def header_annotation_blocks(
    segments: dict[str, tuple[tuple[str, str], tuple[str, str]]],
    labels: dict[str, tuple[str, str]],
    view_namespace: str,
) -> list[str]:
    """Build labels only for header endpoints represented in this view."""

    blocks = []
    for net_id, (side, text) in labels.items():
        try:
            endpoints = tuple((float(x), float(y)) for x, y in segments[net_id])
        except KeyError as error:
            raise ProjectionSupportError(
                f"{net_id}: header annotation has no represented segment"
            ) from error
        point = min(endpoints) if side == "left" else max(endpoints)
        blocks.append(
            header_annotation_block(net_id, text, point, side, view_namespace)
        )
    return blocks


def cross(
    first: tuple[float, float],
    second: tuple[float, float],
    third: tuple[float, float],
) -> float:
    """Return the 2-D cross product used by wire-geometry checks."""

    return (
        (second[0] - first[0]) * (third[1] - first[1])
        - (second[1] - first[1]) * (third[0] - first[0])
    )


def point_on_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    interior_only: bool = False,
) -> bool:
    """Return whether a point lies on a segment within numeric tolerance."""

    epsilon = 1e-9
    if abs(cross(start, end, point)) > epsilon:
        return False
    if not (
        min(start[0], end[0]) - epsilon <= point[0] <= max(start[0], end[0]) + epsilon
        and min(start[1], end[1]) - epsilon
        <= point[1]
        <= max(start[1], end[1]) + epsilon
    ):
        return False
    if interior_only and (point == start or point == end):
        return False
    return True


def validate_segment_instances(
    segments: list[tuple[str, tuple[tuple[str, str], tuple[str, str]]]],
) -> None:
    """Reject direct-wire hazards while allowing same-net fanout endpoints."""

    numeric = [
        (
            net_id,
            (
                (float(segment[0][0]), float(segment[0][1])),
                (float(segment[1][0]), float(segment[1][1])),
            ),
        )
        for net_id, segment in segments
    ]
    for index, (first_id, (first_start, first_end)) in enumerate(numeric):
        for second_id, (second_start, second_end) in numeric[index + 1 :]:
            shared = {first_start, first_end} & {second_start, second_end}
            if shared and first_id != second_id:
                raise ProjectionSupportError(
                    f"{first_id} and {second_id} share a wire endpoint"
                )
            if abs(cross(first_start, first_end, second_start)) < 1e-9 and abs(
                cross(first_start, first_end, second_end)
            ) < 1e-9:
                axis = 0 if abs(first_end[0] - first_start[0]) >= abs(
                    first_end[1] - first_start[1]
                ) else 1
                overlap = min(
                    max(first_start[axis], first_end[axis]),
                    max(second_start[axis], second_end[axis]),
                ) - max(
                    min(first_start[axis], first_end[axis]),
                    min(second_start[axis], second_end[axis]),
                )
                if overlap > 1e-9:
                    raise ProjectionSupportError(
                        f"{first_id} and {second_id} overlap collinearly"
                    )
            if first_id == second_id:
                continue
            for endpoint in (first_start, first_end):
                if point_on_segment(
                    endpoint, second_start, second_end, interior_only=True
                ):
                    raise ProjectionSupportError(
                        f"{first_id} endpoint lands inside {second_id}"
                    )
            for endpoint in (second_start, second_end):
                if point_on_segment(
                    endpoint, first_start, first_end, interior_only=True
                ):
                    raise ProjectionSupportError(
                        f"{second_id} endpoint lands inside {first_id}"
                    )


def hide_effects(property_text: str, wiring) -> str:
    """Add KiCad's hide flag to one property effects block."""

    effects = [
        block
        for block in wiring.immediate_blocks(property_text)
        if block.kind == "effects"
    ]
    if len(effects) != 1:
        raise ProjectionSupportError(
            "expected one effects block in connector property"
        )
    block = effects[0]
    if "\n        hide" in block.text:
        return property_text
    replacement = block.text[:-1] + "\n        hide)"
    return property_text[: block.start] + replacement + property_text[block.end :]


def clean_functional_connector_fields(path: Path, wiring) -> None:
    """Keep mirrored connector references readable and hide long values."""

    text = path.read_text(encoding="utf-8")
    replacements = []
    for symbol in wiring.immediate_blocks(text):
        if symbol.kind != "symbol":
            continue
        properties = [
            block
            for block in wiring.immediate_blocks(symbol.text)
            if block.kind == "property"
        ]
        reference = next(
            (
                block
                for block in properties
                if any(
                    block.text.startswith(f'(property "Reference" "{ref}"')
                    for ref in ("JO1", "JE1", "J2", "J3")
                )
            ),
            None,
        )
        if reference is None:
            continue
        value = next(
            (
                block
                for block in properties
                if block.text.startswith('(property "Value" ')
            ),
            None,
        )
        if value is None:
            raise ProjectionSupportError("mirrored connector has no Value property")

        readable_reference = reference.text
        if reference.text.startswith(
            ('(property "Reference" "JO1"', '(property "Reference" "JE1"')
        ):
            readable_reference = readable_reference.replace(" 180)", " 0)", 1)
        hidden_value = hide_effects(value.text, wiring)

        rebuilt = symbol.text
        for block, replacement in sorted(
            ((reference, readable_reference), (value, hidden_value)),
            key=lambda item: item[0].start,
            reverse=True,
        ):
            rebuilt = rebuilt[: block.start] + replacement + rebuilt[block.end :]
        replacements.append((symbol, rebuilt))

    if len(replacements) != 4:
        raise ProjectionSupportError(
            "expected JO1, JE1, J2, and J3 field cleanup, "
            f"found {len(replacements)} symbols"
        )
    for block, replacement in sorted(
        replacements, key=lambda item: item[0].start, reverse=True
    ):
        text = text[: block.start] + replacement + text[block.end :]
    path.write_text(text, encoding="utf-8")
