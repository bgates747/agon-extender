#!/usr/bin/env python3
"""Generate ordered deterministic r02 schematics focused on one function at a time.

The maintained ``../schematic.kicad_sch`` supplies component placement and
orientation.  ``../connectivity.yaml`` supplies every electrical endpoint.
``views.yaml`` selects bounded endpoint partitions; it cannot introduce a
connection that is absent from the electrical authority.
"""

from __future__ import annotations

import argparse
from collections import Counter
import copy
from decimal import Decimal
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import yaml

import kicad_projection_support as support
import kicad_sexpr as sexpr


ROOT = Path(__file__).resolve().parent
DESIGN = ROOT.parent
REPOSITORY = ROOT.parents[3]
SOURCE_SCHEMATIC = DESIGN / "schematic.kicad_sch"
MODEL = DESIGN / "connectivity.yaml"
MANIFEST = ROOT / "views.yaml"
OUTPUT = ROOT / "generated"
PROJECTION = (
    REPOSITORY / "docs/tasks/HW-001/v1-draft-schematic/kicad-projection.yaml"
)
ELECTRICAL_GENERATOR = (
    REPOSITORY / "docs/tasks/HW-001/electrical-model/generate_kicad.py"
)
FIXED_SVG_DATE = "2026/09/01 00:00:00"
WHITE_BACKGROUND = (
    '  <rect id="explicit-white-background" x="0" y="0" width="100%" '
    'height="100%" fill="#ffffff" stroke="none"/>\n'
)
CONTEXT_STROKE = (
    "(stroke (width 0.127) (type solid) (color 160 160 160 1))"
)


class FunctionViewError(ValueError):
    """A function view or its generated evidence is invalid."""


def ensure_deterministic_process() -> None:
    """Re-exec this absolute entry point before changing working directory."""

    if os.environ.get("PYTHONHASHSEED") == "0":
        return
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    script = str(Path(__file__).resolve())
    os.execve(sys.executable, [sys.executable, script, *sys.argv[1:]], environment)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FunctionViewError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def orientation_code(angle: int, mirror: str | None) -> str:
    """Map equivalent KiCad transforms onto SKiDL's symbolic transforms."""

    mapping = {
        (0, None): "",
        (0, "y"): "H",
        (180, "x"): "H",
        (90, None): "L",
        (90, "x"): "HL",
        (270, None): "R",
        (270, "x"): "HL",
    }
    try:
        return mapping[(angle, mirror)]
    except KeyError as error:
        raise FunctionViewError(
            f"unsupported source transform: angle={angle}, mirror={mirror}"
        ) from error


def extract_symbol_layout(path: Path) -> dict[str, tuple[float, float, str]]:
    """Extract symbol coordinates and normalized orientation from a drawing."""

    text = path.read_text(encoding="utf-8")
    layout = {}
    for block in sexpr.immediate_blocks(text):
        if block.kind != "symbol":
            continue
        ref = sexpr.symbol_reference(block)
        x_mm, y_mm, angle, mirror = sexpr.symbol_transform(block)
        layout[ref] = (x_mm, y_mm, orientation_code(angle, mirror))
    return layout


def extract_source_floorplan() -> dict[str, tuple[int, int, str]]:
    """Extract exact relative placement from the maintained r02 schematic."""

    layout = extract_symbol_layout(SOURCE_SCHEMATIC)
    floorplan = {}
    for ref, (x_mm, y_mm, orientation) in layout.items():
        x_mil = round(x_mm / 0.0254)
        y_mil = round(y_mm / 0.0254)
        if abs(x_mil * 0.0254 - x_mm) > 1e-6 or abs(y_mil * 0.0254 - y_mm) > 1e-6:
            raise FunctionViewError(f"{ref}: source placement is not on a 1 mil grid")
        # KiCad page Y grows downward; SKiDL's explicit placement Y grows
        # upward. Negate only the placement coordinate so the generated page
        # preserves the maintained schematic's relative geometry instead of
        # silently reflecting the complete layout vertically.
        floorplan[ref] = (x_mil, -y_mil, orientation)
    if len(floorplan) != 45:
        raise FunctionViewError(
            f"expected 45 source symbols, found {len(floorplan)}"
        )
    return floorplan


def block_uuid(block: sexpr.Block) -> str:
    """Return the UUID of one top-level schematic object."""

    match = re.search(r"\(uuid\s+([^\s)]+)\)", block.text)
    if match is None:
        raise FunctionViewError(f"{block.kind}: object has no UUID")
    return match.group(1)


def wire_as_context_polyline(block: sexpr.Block) -> str:
    """Convert a canonical electrical wire into a gray non-electrical line."""

    text, kind_count = re.subn(r"^\(wire\b", "(polyline", block.text, count=1)
    text, stroke_count = re.subn(
        r"\(stroke\s+\(width\s+[^)]+\)\s+\(type\s+[^)]+\)"
        r"(?:\s+\(color\s+[^)]+\))?\s*\)",
        CONTEXT_STROKE,
        text,
        count=1,
    )
    if kind_count != 1 or stroke_count != 1:
        raise FunctionViewError("cannot convert canonical wire to context polyline")
    return text


def validate_source_geometry(path: Path) -> None:
    """Require selected wires and gray context to derive from the master."""

    source_text = SOURCE_SCHEMATIC.read_text(encoding="utf-8")
    actual_text = path.read_text(encoding="utf-8")
    source = {
        sexpr.symbol_reference(block): block.text
        for block in sexpr.immediate_blocks(source_text)
        if block.kind == "symbol"
    }
    actual = {
        sexpr.symbol_reference(block): block.text
        for block in sexpr.immediate_blocks(actual_text)
        if block.kind == "symbol"
    }
    if set(actual) != set(source):
        raise FunctionViewError(f"{path.name}: symbol set differs from source geometry")
    changed = sorted(ref for ref in source if actual[ref] != source[ref])
    if changed:
        raise FunctionViewError(
            f"{path.name}: changed source symbol blocks: {changed}"
        )
    source_blocks = list(sexpr.immediate_blocks(source_text))
    actual_blocks = list(sexpr.immediate_blocks(actual_text))

    source_wires = {
        block_uuid(block): block
        for block in source_blocks
        if block.kind == "wire"
    }
    actual_wires = {
        block_uuid(block): block
        for block in actual_blocks
        if block.kind == "wire"
    }
    actual_polylines = {
        block_uuid(block): block
        for block in actual_blocks
        if block.kind == "polyline"
    }
    source_polylines = {
        block_uuid(block): block
        for block in source_blocks
        if block.kind == "polyline"
    }
    for uuid, source_wire in source_wires.items():
        real = actual_wires.get(uuid)
        context = actual_polylines.get(uuid)
        if (real is None) == (context is None):
            raise FunctionViewError(
                f"{path.name}: master wire {uuid} must appear exactly once as "
                "a selected wire or gray context"
            )
        if real is not None and real.text != source_wire.text:
            raise FunctionViewError(f"{path.name}: changed selected wire {uuid}")
        if context is not None and context.text != wire_as_context_polyline(source_wire):
            raise FunctionViewError(f"{path.name}: changed gray context wire {uuid}")
    unexpected_wires = sorted(set(actual_wires) - set(source_wires))
    if unexpected_wires:
        raise FunctionViewError(
            f"{path.name}: invented electrical wires: {unexpected_wires}"
        )
    native_actual_polylines = {
        uuid: block
        for uuid, block in actual_polylines.items()
        if uuid not in source_wires
    }
    if set(native_actual_polylines) != set(source_polylines) or any(
        native_actual_polylines[uuid].text != source_polylines[uuid].text
        for uuid in source_polylines
    ):
        raise FunctionViewError(f"{path.name}: changed native graphical polylines")

    for kind in ("junction", "global_label"):
        source_graphics = Counter(
            block.text for block in source_blocks if block.kind == kind
        )
        actual_graphics = Counter(
            block.text for block in actual_blocks if block.kind == kind
        )
        invented = actual_graphics - source_graphics
        if invented:
            raise FunctionViewError(
                f"{path.name}: contains {kind} graphics not copied from the master"
            )
    if any(block.kind == "no_connect" for block in actual_blocks):
        raise FunctionViewError(f"{path.name}: retained unrelated no-connect marks")


def build_complete_split_projection(model: dict, projection: dict):
    """Represent all components while splitting physical Agon J1 for layout."""

    components = {component["ref"]: component for component in model["components"]}
    odd, even = support.split_j1_component(components["J1"])
    projected_components = [odd, even]
    projected_components.extend(
        copy.deepcopy(component)
        for component in model["components"]
        if component["ref"] != "J1"
    )
    mappings = [
        {"ref": "JO1", "library": "Connector_Generic", "symbol": "Conn_01x17"},
        {"ref": "JE1", "library": "Connector_Generic", "symbol": "Conn_01x17"},
    ]
    mappings.extend(
        copy.deepcopy(mapping)
        for mapping in projection["components"]
        if mapping["ref"] != "J1"
    )
    return projected_components, mappings


def parse_member(value: str) -> tuple[str, str]:
    try:
        ref, pin = value.rsplit(".", 1)
    except ValueError as error:
        raise FunctionViewError(f"invalid endpoint {value!r}; expected REF.PIN") from error
    if not ref or not pin:
        raise FunctionViewError(f"invalid endpoint {value!r}; expected REF.PIN")
    return ref, pin


def merge_selection(
    destination: dict[str, set[tuple[str, str]] | None],
    addition: dict,
) -> None:
    """Merge one group while preserving ``all`` as the dominant selector."""

    for net_id, raw_members in addition.items():
        if raw_members == "all":
            destination[net_id] = None
            continue
        if not isinstance(raw_members, list):
            raise FunctionViewError(f"{net_id}: members must be 'all' or a list")
        members = {parse_member(member) for member in raw_members}
        if net_id not in destination:
            destination[net_id] = members
        elif destination[net_id] is not None:
            destination[net_id].update(members)


def resolved_view_selections(document: dict, model: dict) -> list[dict]:
    """Resolve reusable groups and dynamic selectors into exact endpoints."""

    if document.get("schema_version") != 1:
        raise FunctionViewError("unsupported views.yaml schema")
    prefix = document.get("filename_prefix")
    if prefix != "schematic_":
        raise FunctionViewError("function-view filename prefix must be schematic_")
    groups = document.get("groups", {})
    canonical = {
        net["net_id"]: {
            (member["component"], member["pin"]) for member in net["members"]
        }
        for net in model["nets"]
    }
    views = []
    descriptors = set()
    orders = set()
    for record in document.get("views", []):
        order = record.get("order")
        if type(order) is not int or not 1 <= order <= 99:
            raise FunctionViewError(
                f"invalid function-view order: {order!r}; expected integer 1--99"
            )
        if order in orders:
            raise FunctionViewError(f"duplicate function-view order: {order}")
        orders.add(order)
        descriptor = record.get("descriptor")
        if not isinstance(descriptor, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", descriptor
        ):
            raise FunctionViewError(f"invalid function descriptor: {descriptor!r}")
        if descriptor in descriptors:
            raise FunctionViewError(f"duplicate function descriptor: {descriptor}")
        descriptors.add(descriptor)
        selection: dict[str, set[tuple[str, str]] | None] = {}
        for group_name in record.get("groups", []):
            try:
                merge_selection(selection, groups[group_name])
            except KeyError as error:
                raise FunctionViewError(f"unknown view group: {group_name}") from error
        merge_selection(selection, record.get("nets", {}))
        if record.get("selector") == "bias-resistors-r14-r31":
            bias_refs = {f"R{number}" for number in range(14, 32)}
            for net_id, members in canonical.items():
                if any(ref in bias_refs for ref, _ in members):
                    selection[net_id] = None
        elif record.get("selector") is not None:
            raise FunctionViewError(f"{descriptor}: unknown dynamic selector")
        if not selection:
            raise FunctionViewError(f"{descriptor}: empty function selection")

        resolved = {}
        for net_id, selected in selection.items():
            try:
                available = canonical[net_id]
            except KeyError as error:
                raise FunctionViewError(f"{descriptor}: unknown net {net_id}") from error
            endpoints = available if selected is None else selected
            if not endpoints <= available:
                raise FunctionViewError(
                    f"{descriptor}/{net_id}: noncanonical endpoints "
                    f"{sorted(endpoints - available)}"
                )
            if len(endpoints) < 2:
                raise FunctionViewError(
                    f"{descriptor}/{net_id}: projection needs at least two endpoints"
                )
            resolved[net_id] = endpoints
        views.append({**record, "resolved": resolved, "prefix": prefix})
    if len(views) != 17:
        raise FunctionViewError(f"expected 17 function views, found {len(views)}")
    expected_orders = set(range(1, len(views) + 1))
    if orders != expected_orders:
        raise FunctionViewError(
            "function-view orders must be contiguous from 1 through "
            f"{len(views)}; missing={sorted(expected_orders - orders)}, "
            f"extra={sorted(orders - expected_orders)}"
        )
    return sorted(views, key=lambda view: view["order"])


def projected_member(ref: str, pin: str) -> tuple[str, str]:
    if ref != "J1":
        return ref, pin
    projected = support.project_j1_member({"component": ref, "pin": pin})
    return projected["component"], projected["pin"]


def build_view_model(components: list[dict], view: dict) -> dict:
    nets = []
    for net_id, endpoints in sorted(view["resolved"].items()):
        nets.append(
            {
                "net_id": net_id,
                "members": [
                    {"component": projected_member(ref, pin)[0], "pin": projected_member(ref, pin)[1]}
                    for ref, pin in sorted(endpoints)
                ],
            }
        )
    return {"components": copy.deepcopy(components), "nets": nets, "unconnected": []}


def decimal_point(x: str | float, y: str | float) -> tuple[Decimal, Decimal]:
    return Decimal(str(x)), Decimal(str(y))


def parse_wire(block: sexpr.Block) -> tuple[tuple[Decimal, Decimal], tuple[Decimal, Decimal]]:
    points = re.findall(
        r"\(xy\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s+"
        r"(-?(?:\d+(?:\.\d*)?|\.\d+))\)",
        block.text,
    )
    if len(points) != 2:
        raise FunctionViewError("master wire does not contain exactly two points")
    return decimal_point(*points[0]), decimal_point(*points[1])


def parse_junction(block: sexpr.Block) -> tuple[Decimal, Decimal]:
    match = re.match(
        r"^\(junction\s+\(at\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s+"
        r"(-?(?:\d+(?:\.\d*)?|\.\d+))\)",
        block.text,
    )
    if match is None:
        raise FunctionViewError("malformed master junction")
    return decimal_point(*match.groups())


def point_on_segment(
    point: tuple[Decimal, Decimal],
    segment: tuple[tuple[Decimal, Decimal], tuple[Decimal, Decimal]],
) -> bool:
    (px, py), ((ax, ay), (bx, by)) = point, segment
    cross = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
    return (
        cross == 0
        and min(ax, bx) <= px <= max(ax, bx)
        and min(ay, by) <= py <= max(ay, by)
    )


def symbol_pin_points(
    path: Path,
    refs: set[str],
) -> dict[tuple[str, str], tuple[Decimal, Decimal]]:
    """Return exact sheet coordinates for selected angle-zero symbol pins.

    The physical DIP symbols deliberately have different pin geometry from the
    functional symbols used in the temporary SKiDL label view.  KiCad embeds
    both symbol definitions in each schematic, so derive the coordinates from
    those definitions instead of assuming equal geometry around equal symbol
    centers.
    """

    text = path.read_text(encoding="utf-8")
    root_blocks = list(sexpr.immediate_blocks(text))
    library_container = next(
        (block for block in root_blocks if block.kind == "lib_symbols"), None
    )
    if library_container is None:
        raise FunctionViewError(f"{path.name}: schematic has no embedded symbols")
    libraries = {}
    for block in sexpr.immediate_blocks(library_container.text):
        if block.kind != "symbol":
            continue
        match = re.match(r'^\(symbol "([^"]+)"', block.text)
        if match is not None:
            libraries[match.group(1)] = block

    points = {}
    for block in root_blocks:
        if block.kind != "symbol":
            continue
        ref = sexpr.symbol_reference(block)
        if ref not in refs:
            continue
        transform = re.match(
            r'^\(symbol\s+\(lib_id "([^"]+)"\)\s+'
            r'\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)\s+(0|90|180|270)\)'
            r'(?:\s+\(mirror\s+([xy])\))?',
            block.text,
        )
        if transform is None:
            raise FunctionViewError(f"{path.name}/{ref}: unsupported symbol instance")
        lib_id, x_text, y_text, angle_text, mirror = transform.groups()
        if angle_text != "0" or mirror is not None:
            raise FunctionViewError(
                f"{path.name}/{ref}: pin remapping currently requires "
                "an unmirrored angle-zero symbol"
            )
        try:
            library = libraries[lib_id]
        except KeyError as error:
            raise FunctionViewError(
                f"{path.name}/{ref}: missing embedded symbol {lib_id}"
            ) from error
        x_origin, y_origin = Decimal(x_text), Decimal(y_text)
        stack = [library]
        found = set()
        while stack:
            parent = stack.pop()
            for child in sexpr.immediate_blocks(parent.text):
                if child.kind == "symbol":
                    stack.append(child)
                    continue
                if child.kind != "pin":
                    continue
                at_match = re.search(
                    r"\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)\s+"
                    r"(?:0|90|180|270)\)",
                    child.text,
                )
                number_match = re.search(r'\(number "([^"]+)"', child.text)
                if at_match is None or number_match is None:
                    raise FunctionViewError(
                        f"{path.name}/{ref}: malformed embedded pin"
                    )
                pin = number_match.group(1)
                if pin in found:
                    continue
                found.add(pin)
                local_x, local_y = map(Decimal, at_match.groups())
                points[(ref, pin)] = (
                    x_origin + local_x,
                    y_origin - local_y,
                )
        if not found:
            raise FunctionViewError(f"{path.name}/{ref}: embedded symbol has no pins")
    missing = sorted(refs - {ref for ref, _ in points})
    if missing:
        raise FunctionViewError(f"{path.name}: missing pin geometry for {missing}")
    return points


def source_marker_points(
    label_view: Path,
    view_model: dict,
) -> dict[str, set[tuple[Decimal, Decimal]]]:
    """Translate temporary labels onto exact master pin coordinates."""

    source_layout = extract_symbol_layout(SOURCE_SCHEMATIC)
    label_layout = extract_symbol_layout(label_view)
    if set(source_layout) != set(label_layout):
        raise FunctionViewError("temporary label view changed the master symbol set")
    deltas = {
        (
            Decimal(str(label_layout[ref][0])) - Decimal(str(source_layout[ref][0])),
            Decimal(str(label_layout[ref][1])) - Decimal(str(source_layout[ref][1])),
        )
        for ref in source_layout
    }
    if len(deltas) != 1:
        raise FunctionViewError("temporary label view has no uniform master offset")
    dx, dy = next(iter(deltas))
    markers: dict[str, set[tuple[Decimal, Decimal]]] = {}
    for block in sexpr.immediate_blocks(label_view.read_text(encoding="utf-8")):
        if block.kind != "global_label":
            continue
        label = sexpr.parse_label(block)
        point = (Decimal(label.x_text) - dx, Decimal(label.y_text) - dy)
        markers.setdefault(label.net_id, set()).add(point)

    # U1--U4 use physical top-view DIP symbols in the canonical drawing but
    # functional symbols in the temporary label view.  Replace only those
    # temporary marker coordinates with coordinates derived from each file's
    # embedded symbol definition.  This is an intentional projection
    # workaround, not an electrical exception; exported netlists below remain
    # the final authority and must match exactly.
    physical_refs = {"U1", "U2", "U3", "U4"}
    source_pins = symbol_pin_points(SOURCE_SCHEMATIC, physical_refs)
    label_pins = symbol_pin_points(label_view, physical_refs)
    for net in view_model["nets"]:
        net_id = net["net_id"]
        for member in net["members"]:
            endpoint = (member["component"], member["pin"])
            if endpoint[0] not in physical_refs:
                continue
            label_point = (
                label_pins[endpoint][0] - dx,
                label_pins[endpoint][1] - dy,
            )
            try:
                markers[net_id].remove(label_point)
            except (KeyError, ValueError) as error:
                raise FunctionViewError(
                    f"{label_view.name}/{net_id}: temporary marker for "
                    f"{endpoint[0]}.{endpoint[1]} was not found"
                ) from error
            markers[net_id].add(source_pins[endpoint])
    return markers


def source_wire_components(
    wires: list[sexpr.Block],
    junctions: list[sexpr.Block],
) -> tuple[list[tuple[tuple[Decimal, Decimal], tuple[Decimal, Decimal]]], list[set[int]]]:
    """Return master wire geometry grouped by actual KiCad connectivity."""

    segments = [parse_wire(block) for block in wires]
    junction_points = [parse_junction(block) for block in junctions]
    parents = list(range(len(segments)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(first: int, second: int) -> None:
        first_root, second_root = find(first), find(second)
        if first_root != second_root:
            parents[second_root] = first_root

    for first_index, first in enumerate(segments):
        for second_index in range(first_index + 1, len(segments)):
            second = segments[second_index]
            shared_endpoint = bool(set(first) & set(second))
            junction_join = any(
                point_on_segment(point, first) and point_on_segment(point, second)
                for point in junction_points
            )
            if shared_endpoint or junction_join:
                union(first_index, second_index)

    grouped: dict[int, set[int]] = {}
    for index in range(len(segments)):
        grouped.setdefault(find(index), set()).add(index)
    return segments, list(grouped.values())


def filter_master_schematic(
    label_view: Path,
    output: Path,
    view_model: dict,
    title: str,
) -> None:
    """Keep selected nets real and render all other master wires as gray graphics."""

    source_text = SOURCE_SCHEMATIC.read_text(encoding="utf-8")
    blocks = list(sexpr.immediate_blocks(source_text))
    wires = [block for block in blocks if block.kind == "wire"]
    junctions = [block for block in blocks if block.kind == "junction"]
    labels = [block for block in blocks if block.kind == "global_label"]
    markers = source_marker_points(label_view, view_model)
    expected_counts = {
        net["net_id"]: len(net["members"])
        for net in view_model["nets"]
    }
    marker_counts = {net_id: len(points) for net_id, points in markers.items()}
    if marker_counts != expected_counts:
        raise FunctionViewError(
            f"{output.name}: selected master markers differ: "
            f"expected={expected_counts}, actual={marker_counts}"
        )

    segments, components = source_wire_components(wires, junctions)
    retained_wire_indexes: set[int] = set()
    wire_nets: dict[int, str] = {}
    for component in components:
        represented = {
            net_id
            for net_id, points in markers.items()
            if any(
                point_on_segment(point, segments[index])
                for point in points
                for index in component
            )
        }
        if len(represented) > 1:
            touching = {
                net_id: sorted(
                    point
                    for point in points
                    if any(
                        point_on_segment(point, segments[index])
                        for index in component
                    )
                )
                for net_id, points in markers.items()
                if any(
                    point_on_segment(point, segments[index])
                    for point in points
                    for index in component
                )
            }
            raise FunctionViewError(
                f"{output.name}: master wire component touches selected nets "
                f"{sorted(represented)} at {touching}"
            )
        if represented:
            net_id = next(iter(represented))
            retained_wire_indexes.update(component)
            for index in component:
                wire_nets[index] = net_id

    retained_segments = [segments[index] for index in sorted(retained_wire_indexes)]
    selected_points = {
        net_id: points for net_id, points in markers.items()
    }
    retained_labels: set[int] = set()
    for index, block in enumerate(labels):
        label = sexpr.parse_label(block)
        if label.net_id not in selected_points:
            continue
        point = decimal_point(label.x_text, label.y_text)
        if point in selected_points[label.net_id] or any(
            point_on_segment(point, segments[wire_index])
            and wire_nets.get(wire_index) == label.net_id
            for wire_index in retained_wire_indexes
        ):
            retained_labels.add(index)

    retained_junctions: set[int] = set()
    for index, block in enumerate(junctions):
        point = parse_junction(block)
        if any(point_on_segment(point, segment) for segment in retained_segments):
            retained_junctions.add(index)

    keep_starts = {
        wires[index].start for index in retained_wire_indexes
    }
    keep_starts.update(labels[index].start for index in retained_labels)
    keep_starts.update(junctions[index].start for index in retained_junctions)
    removable = {"wire", "junction", "global_label", "no_connect"}
    for block in sorted(blocks, key=lambda item: item.start, reverse=True):
        if block.kind in removable and block.start not in keep_starts:
            replacement = (
                wire_as_context_polyline(block) if block.kind == "wire" else ""
            )
            source_text = source_text[:block.start] + replacement + source_text[block.end:]
    source_text, count = re.subn(
        r'\(title "[^"]*"\)',
        f'(title "{title}")',
        source_text,
        count=1,
    )
    if count != 1:
        raise FunctionViewError("master schematic lacks its unique title")
    # Removed connectivity objects leave their original indentation behind.
    # Strip that semantically empty whitespace here so checked generated
    # schematics remain reviewable and pass repository whitespace checks.
    source_text = "\n".join(line.rstrip() for line in source_text.splitlines()) + "\n"
    output.write_text(source_text, encoding="utf-8")


def expected_partitions(view_model: dict) -> Counter:
    return Counter(
        frozenset((member["component"], member["pin"]) for member in net["members"])
        for net in view_model["nets"]
    )


def exported_partitions(path: Path) -> tuple[Counter, set[str]]:
    root = ET.parse(path).getroot()
    partitions = Counter()
    for net in root.findall(".//nets/net"):
        members = frozenset(
            (node.attrib["ref"], node.attrib["pin"]) for node in net.findall("node")
        )
        if net.attrib.get("name", "").startswith("unconnected-("):
            continue
        partitions[members] += 1
    refs = {component.attrib["ref"] for component in root.findall(".//components/comp")}
    return partitions, refs


def normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(
        r"(<title>SVG Image created as [^<]+ date )[^<]+(</title>)",
        rf"\g<1>{FIXED_SVG_DATE} \g<2>",
        text,
        count=1,
    )
    if count != 1:
        raise FunctionViewError(f"{path.name}: SVG lacks its unique dated title")
    if 'id="explicit-white-background"' not in text:
        desc = re.search(r"(<desc>.*?</desc>\s*)", text, re.DOTALL)
        if desc is None:
            raise FunctionViewError(f"{path.name}: SVG lacks a desc insertion point")
        text = text[: desc.end()] + WHITE_BACKGROUND + text[desc.end() :]
    path.write_text(
        "\n".join(line.rstrip() for line in text.splitlines()) + "\n",
        encoding="utf-8",
    )


def export_and_validate(
    schematic: Path,
    view_model: dict,
    expected_refs: set[str],
) -> Path:
    xml_path = schematic.with_suffix(".xml")
    subprocess.run(
        [
            "kicad-cli",
            "sch",
            "export",
            "netlist",
            "--format",
            "kicadxml",
            "-o",
            str(xml_path),
            str(schematic),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    actual, refs = exported_partitions(xml_path)
    if actual != expected_partitions(view_model):
        raise FunctionViewError(f"{schematic.name}: exported endpoint partition differs")
    if refs != expected_refs:
        raise FunctionViewError(
            f"{schematic.name}: component context differs: "
            f"missing={sorted(expected_refs - refs)}, extra={sorted(refs - expected_refs)}"
        )
    subprocess.run(
        [
            "kicad-cli",
            "sch",
            "export",
            "svg",
            "--no-background-color",
            "-o",
            str(schematic.parent),
            str(schematic),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    svg_path = schematic.with_suffix(".svg")
    normalize_svg(svg_path)
    return svg_path


def generate_all(destination: Path) -> list[tuple[Path, Path]]:
    electrical = load_module("r02_function_view_generator", ELECTRICAL_GENERATOR)
    electrical.ensure_deterministic_python_hashes()
    projection = electrical.load_yaml(PROJECTION)
    model = electrical.load_model_validator().validate(MODEL)
    electrical.validate_projection(projection, model)
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    views = resolved_view_selections(manifest, model)
    components, mappings = build_complete_split_projection(model, projection)
    floorplan = extract_source_floorplan()
    expected_refs = {component["ref"] for component in components}
    if set(floorplan) != expected_refs:
        raise FunctionViewError(
            f"source placement mismatch: missing={sorted(expected_refs - set(floorplan))}, "
            f"extra={sorted(set(floorplan) - expected_refs)}"
        )
    outputs = []
    for view in views:
        stem = f"{view['order']:02d}_{view['prefix']}{view['descriptor']}"
        title = f"Light 2 harness r02 — {view['title']} — FUNCTION VIEW, NOT AUTHORITY"
        view_model = build_view_model(components, view)
        view_mapping = {
            "top_name": stem,
            "title": title,
            "components": copy.deepcopy(mappings),
        }
        circuit = electrical.build_circuit(
            view_model,
            view_mapping,
            PROJECTION.parent,
            force_label_stubs=True,
        )
        schematic = support.write_fixed_label_view(
            electrical,
            circuit,
            floorplan,
            destination,
            stem,
            title,
        )
        filter_master_schematic(schematic, schematic, view_model, title)
        validate_source_geometry(schematic)
        svg = export_and_validate(schematic, view_model, expected_refs)
        schematic.with_suffix(".xml").unlink()
        outputs.append((schematic, svg))
        print(f"PASS: {stem}")
    return outputs


def require_equal(expected: Path, generated: Path) -> None:
    if not expected.exists() or expected.read_bytes() != generated.read_bytes():
        raise FunctionViewError(f"stale or missing function view: {expected}")


def unexpected_artifacts(expected_names: set[str]) -> list[Path]:
    if not OUTPUT.exists():
        return []
    return sorted(
        path
        for path in OUTPUT.rglob("*")
        if path.is_file()
        and path.suffix in {".kicad_sch", ".svg"}
        and (path.parent != OUTPUT or path.name not in expected_names)
    )


def main() -> int:
    ensure_deterministic_process()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="replace checked function views after complete validation",
    )
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="light2-r02-function-views-") as scratch:
            # SKiDL writes an otherwise empty ``skidl.erc`` side effect in the
            # process working directory. Confine it to the disposable build
            # directory rather than littering the repository root.
            original_directory = Path.cwd()
            try:
                os.chdir(scratch)
                generated = generate_all(Path(scratch))
            finally:
                os.chdir(original_directory)
            expected_names = {
                source.name
                for schematic, svg in generated
                for source in (schematic, svg)
            }
            if args.write:
                OUTPUT.mkdir(parents=True, exist_ok=True)
                for schematic, svg in generated:
                    for source in (schematic, svg):
                        target = OUTPUT / source.name
                        shutil.copyfile(source, target)
                for stale in unexpected_artifacts(expected_names):
                    stale.unlink()
                for directory in sorted(
                    (path for path in OUTPUT.rglob("*") if path.is_dir()),
                    reverse=True,
                ):
                    try:
                        directory.rmdir()
                    except OSError:
                        pass
            else:
                for schematic, svg in generated:
                    require_equal(OUTPUT / schematic.name, schematic)
                    require_equal(OUTPUT / svg.name, svg)
                unexpected = unexpected_artifacts(expected_names)
                if unexpected:
                    raise FunctionViewError(
                        "unexpected stale function views: "
                        + ", ".join(str(path.relative_to(OUTPUT)) for path in unexpected)
                    )
    except (
        ET.ParseError,
        FunctionViewError,
        OSError,
        subprocess.CalledProcessError,
        ValueError,
        yaml.YAMLError,
    ) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    action = "generated and validated" if args.write else "validated"
    print(f"PASS: {action} 17 r02 function views")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
