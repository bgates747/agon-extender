#!/usr/bin/env python3
"""Generate deterministic HW-001 signal-atlas drawings.

View 0 is deliberately wire-free. It fixes the page coordinates and
orientations that every later signal projection must reuse. Connectivity
remains owned by the shared model above this directory.
"""

from __future__ import annotations

import argparse
import copy
from dataclasses import replace
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent
ELECTRICAL_MODEL = SHARED.parent / "electrical-model"
PROJECTION_SUPPORT = ROOT / "kicad_projection_support.py"
KICAD_SEXPR = ROOT / "kicad_sexpr.py"
DEFAULT_PLACEMENT = ROOT / "canonical-placement.yaml"
DEFAULT_PROJECTION = SHARED / "kicad-projection.yaml"
DEFAULT_OUTPUT = ROOT / "generated"
VIEW_ZERO_NAME = "00-canonical-component-placement"
VIEW_ONE_NAME = "01-d0-uart-rx-lane"
VIEW_TWO_NAME = "02-d1-uart-tx-lane"
VIEW_ONE_ENDPOINTS = {
    "agon-pc0-d0-uart-tx": {("J1", "17"), ("U1", "2")},
    "p4-gpio22-d0-uart-rx-driver": {("U1", "18"), ("R1", "1")},
    "p4-gpio22-d0-uart-rx": {("R1", "2"), ("R14", "2"), ("J3", "11")},
    "p4-3v3": {("J2", "1"), ("R14", "1"), ("R28", "1")},
    "p4-gpio15-uart-forward-control-n": {
        ("J2", "16"),
        ("R28", "2"),
        ("U4", "1"),
    },
    "uart-forward-oe-n": {("U4", "3"), ("U1", "1"), ("R25", "2")},
    "agon-3v3": {("J1", "34"), ("R25", "1")},
}
VIEW_ONE_HEADER_LABELS = {
    "agon-pc0-d0-uart-tx": ("left", "PC0 / TXD1 / D0"),
    "agon-3v3": ("left", "AGON 3.3V"),
    "p4-gpio22-d0-uart-rx": ("right", "GPIO22 / D0 / UART RX"),
    "p4-gpio15-uart-forward-control-n": (
        "right",
        "GPIO15 / UART FORWARD OE_N",
    ),
    "p4-3v3": ("right", "P4 3.3V"),
}
VIEW_TWO_ENDPOINTS = {
    "agon-pc1-d1-uart-rx": {("J1", "18"), ("R11", "2"), ("U1", "17")},
    "p4-gpio12-d1-uart-tx-driver": {("R2", "1"), ("U1", "3")},
    "p4-gpio12-d1-uart-tx": {
        ("J2", "13"),
        ("R2", "2"),
        ("R15", "2"),
        ("U3", "2"),
    },
    "p4-uart-tx-driver": {("R11", "1"), ("U3", "3")},
    "p4-gpio17-parallel-forward-control-n": {
        ("J2", "18"),
        ("R29", "2"),
        ("U4", "4"),
    },
    "parallel-forward-oe-n": {
        ("R26", "2"),
        ("U1", "19"),
        ("U2", "1"),
        ("U4", "6"),
    },
    "p4-gpio21-uart-return-control-n": {
        ("J3", "12"),
        ("R30", "2"),
        ("U4", "10"),
    },
    "uart-return-oe-n": {
        ("R27", "2"),
        ("U3", "1"),
        ("U3", "4"),
        ("U4", "8"),
    },
    "p4-3v3": {
        ("J2", "1"),
        ("R15", "1"),
        ("R29", "1"),
        ("R30", "1"),
    },
    "agon-3v3": {("J1", "34"), ("R26", "1"), ("R27", "1")},
    "ground": {("J1", "33"), ("U4", "5"), ("U4", "9")},
}
VIEW_TWO_HEADER_LABELS = {
    "agon-pc1-d1-uart-rx": ("left", "PC1 / RXD1 / D1"),
    "agon-3v3": ("left", "AGON 3.3V"),
    "ground": ("left", "GND"),
    "p4-gpio12-d1-uart-tx": ("right", "GPIO12 / D1 / UART TX"),
    "p4-gpio17-parallel-forward-control-n": (
        "right",
        "GPIO17 / PARALLEL FORWARD OE_N",
    ),
    "p4-gpio21-uart-return-control-n": (
        "right",
        "GPIO21 / UART RETURN OE_N",
    ),
    "p4-3v3": ("right", "P4 3.3V"),
}
# Canonical placement puts R27 pin 1 directly on the straight U4-to-R30
# control segment. Route that one segment around the unrelated endpoint; a
# direct line would create an apparent and KiCad-effective cross-net join.
VIEW_TWO_SEGMENT_ROUTES = {
    ("p4-gpio21-uart-return-control-n", 1): (
        ("218.44", "334.01"),
        ("218.44", "344.17"),
        ("380.37", "344.17"),
        ("380.37", "334.01"),
    ),
    ("uart-return-oe-n", 1): (("215.9", "245.11"), ("215.9", "250.19")),
}


def merged_endpoints(*groups):
    """Merge bounded net endpoint groups without silently changing a net."""

    merged = {}
    for group in groups:
        for net_id, endpoints in group.items():
            merged.setdefault(net_id, set()).update(endpoints)
    return merged


UART_FORWARD_CONTROL = {
    "p4-gpio15-uart-forward-control-n": {("J2", "16"), ("R28", "2"), ("U4", "1")},
    "uart-forward-oe-n": {("U4", "3"), ("U1", "1"), ("R25", "2")},
    "p4-3v3": {("J2", "1"), ("R28", "1")},
    "agon-3v3": {("J1", "34"), ("R25", "1")},
    "ground": {
        ("J1", "33"),
        ("U4", "2"),
        ("U4", "5"),
        ("U4", "9"),
        ("U4", "12"),
    },
}
PARALLEL_FORWARD_CONTROL = {
    "p4-gpio17-parallel-forward-control-n": {("J2", "18"), ("R29", "2"), ("U4", "4")},
    "parallel-forward-oe-n": {("U4", "6"), ("U1", "19"), ("U2", "1"), ("R26", "2")},
    "p4-3v3": {("J2", "1"), ("R29", "1")},
    "agon-3v3": {("J1", "34"), ("R26", "1")},
    "ground": {
        ("J1", "33"),
        ("U4", "2"),
        ("U4", "5"),
        ("U4", "9"),
        ("U4", "12"),
    },
}
UART_RETURN_CONTROL = {
    "p4-gpio21-uart-return-control-n": {("J3", "12"), ("R30", "2"), ("U4", "10")},
    "uart-return-oe-n": {("U4", "8"), ("U3", "1"), ("U3", "4"), ("R27", "2")},
    "p4-3v3": {("J2", "1"), ("R30", "1")},
    "agon-3v3": {("J1", "34"), ("R27", "1")},
    "ground": {
        ("J1", "33"),
        ("U4", "2"),
        ("U4", "5"),
        ("U4", "9"),
        ("U4", "12"),
    },
}
READY_CONTROL = {
    "p4-gpio20-ready-control-n": {("J3", "13"), ("R31", "2"), ("U4", "13")},
    "ready-n-driver": {("U4", "11"), ("R13", "1")},
    "agon-pd4-ready-n": {("R13", "2"), ("R24", "2"), ("J1", "13")},
    "p4-3v3": {("J2", "1"), ("R31", "1")},
    "agon-3v3": {("J1", "34"), ("R24", "1")},
    "ground": {
        ("J1", "33"),
        ("U4", "2"),
        ("U4", "5"),
        ("U4", "9"),
        ("U4", "12"),
    },
}

COMMON_HEADER_LABELS = {
    "agon-3v3": ("left", "AGON 3.3V"),
    "ground": ("left", "GND"),
    "p4-3v3": ("right", "P4 3.3V"),
    "p4-gpio15-uart-forward-control-n": ("right", "GPIO15 / UART FORWARD OE_N"),
    "p4-gpio17-parallel-forward-control-n": ("right", "GPIO17 / PARALLEL FORWARD OE_N"),
    "p4-gpio20-ready-control-n": ("right", "GPIO20 / READY CONTROL OE_N"),
    "p4-gpio21-uart-return-control-n": ("right", "GPIO21 / UART RETURN OE_N"),
}
U4_GROUNDED_INPUT_ROUTES = {
    ("ground", 2): (("223.52", "323.85"), ("223.52", "328.93")),
    ("ground", 4): (("223.52", "331.47"), ("223.52", "336.55")),
}


def lane_spec(number, slug, title, endpoints, labels, routes=None, literal=True):
    available_labels = {**COMMON_HEADER_LABELS, **labels}
    effective_routes = dict(routes or {})
    if len(endpoints.get("ground", set())) <= 6 and {
        ("U4", "2"),
        ("U4", "5"),
        ("U4", "9"),
        ("U4", "12"),
    } <= endpoints.get("ground", set()):
        effective_routes.update(U4_GROUNDED_INPUT_ROUTES)
    return {
        "number": number,
        "name": f"{number:02d}-{slug}",
        "title": f"HW-001 signal atlas {number:02d} {title} — NOT AUTHORITY",
        "endpoints": endpoints,
        "labels": {
            net_id: label
            for net_id, label in available_labels.items()
            if net_id in endpoints
        },
        "routes": effective_routes,
        "star_wiring": False,
        "literal": literal,
    }


ADDITIONAL_STATIC_SPECS = [
    lane_spec(
        3,
        "d2-uart-cts-lane",
        "D2 / UART CTS lane",
        merged_endpoints(
            {
                "agon-pc2-d2-uart-rts": {("J1", "19"), ("U1", "4")},
                "p4-gpio23-d2-uart-cts-driver": {("U1", "16"), ("R3", "1")},
                "p4-gpio23-d2-uart-cts": {("R3", "2"), ("R16", "2"), ("J3", "10")},
                "p4-3v3": {("J2", "1"), ("R16", "1")},
            },
            UART_FORWARD_CONTROL,
        ),
        {
            "agon-pc2-d2-uart-rts": ("left", "PC2 / RTS1 / D2"),
            "p4-gpio23-d2-uart-cts": ("right", "GPIO23 / D2 / UART CTS"),
        },
    ),
    lane_spec(
        4,
        "d3-uart-rts-lane",
        "D3 / UART RTS lane",
        merged_endpoints(
            {
                "agon-pc3-d3-uart-cts": {("J1", "20"), ("R12", "2"), ("U1", "15")},
                "p4-gpio11-d3-uart-rts-driver": {("U1", "5"), ("R4", "1")},
                "p4-gpio11-d3-uart-rts": {("R4", "2"), ("R17", "2"), ("U3", "5"), ("J2", "12")},
                "p4-uart-rts-driver": {("U3", "6"), ("R12", "1")},
                "p4-3v3": {("J2", "1"), ("R17", "1")},
            },
            PARALLEL_FORWARD_CONTROL,
            UART_RETURN_CONTROL,
        ),
        {
            "agon-pc3-d3-uart-cts": ("left", "PC3 / CTS1 / D3"),
            "p4-gpio11-d3-uart-rts": ("right", "GPIO11 / D3 / UART RTS"),
        },
        VIEW_TWO_SEGMENT_ROUTES,
    ),
]

for number, bit, source_pin, u2_input, u2_output, resistor, p4_net, p4_ref, p4_pin, pull in (
    (5, 4, 21, 2, 18, 5, "p4-gpio32-d4", "J3", 9, 18),
    (6, 5, 22, 4, 16, 6, "p4-gpio10-d5", "J2", 11, 19),
    (7, 6, 23, 6, 14, 7, "p4-gpio33-d6", "J3", 8, 20),
    (8, 7, 24, 8, 12, 8, "p4-gpio9-d7", "J2", 10, 21),
):
    ADDITIONAL_STATIC_SPECS.append(
        lane_spec(
            number,
            f"d{bit}-lane",
            f"D{bit} lane",
            merged_endpoints(
                {
                    f"agon-pc{bit}-d{bit}": {("J1", str(source_pin)), ("U2", str(u2_input))},
                    f"{p4_net}-driver": {("U2", str(u2_output)), (f"R{resistor}", "1")},
                    p4_net: {(f"R{resistor}", "2"), (f"R{pull}", "1"), (p4_ref, str(p4_pin))},
                    "ground": {("J1", "33"), (f"R{pull}", "2")},
                },
                PARALLEL_FORWARD_CONTROL,
            ),
            {
                f"agon-pc{bit}-d{bit}": ("left", f"PC{bit} / D{bit}"),
                p4_net: ("right", f"GPIO{p4_net.split('gpio', 1)[1].split('-', 1)[0]} / D{bit}"),
            },
        )
    )

ADDITIONAL_STATIC_SPECS.extend(
    [
        lane_spec(
            9,
            "clock",
            "CLOCK",
            merged_endpoints(
                {
                    "agon-pd5-clock": {("J1", "14"), ("U1", "13")},
                    "p4-gpio14-clock-driver": {("U1", "7"), ("R9", "1")},
                    "p4-gpio14-clock": {("R9", "2"), ("R22", "1"), ("J2", "15")},
                    "ground": {("J1", "33"), ("R22", "2")},
                },
                PARALLEL_FORWARD_CONTROL,
            ),
            {"agon-pd5-clock": ("left", "PD5 / CLOCK"), "p4-gpio14-clock": ("right", "GPIO14 / CLOCK")},
        ),
        lane_spec(
            10,
            "valid-n",
            "VALID_N",
            merged_endpoints(
                {
                    "agon-pd7-valid-n": {("J1", "16"), ("U1", "11")},
                    "p4-gpio13-valid-n-driver": {("U1", "9"), ("R10", "1")},
                    "p4-gpio13-valid-n": {("R10", "2"), ("R23", "2"), ("J2", "14")},
                    "p4-3v3": {("J2", "1"), ("R23", "1")},
                },
                PARALLEL_FORWARD_CONTROL,
            ),
            {"agon-pd7-valid-n": ("left", "PD7 / VALID_N"), "p4-gpio13-valid-n": ("right", "GPIO13 / VALID_N")},
        ),
        lane_spec(11, "ready-n", "READY_N", READY_CONTROL, {"agon-pd4-ready-n": ("left", "PD4 / READY_N")}),
        lane_spec(12, "uart-forward-enable", "UART-forward enable", UART_FORWARD_CONTROL, {}),
        lane_spec(13, "parallel-forward-enable", "Parallel-forward enable", PARALLEL_FORWARD_CONTROL, {}),
        lane_spec(14, "uart-return-enable", "UART-return enable", UART_RETURN_CONTROL, {}),
        lane_spec(15, "ready-control", "READY control", READY_CONTROL, {"agon-pd4-ready-n": ("left", "PD4 / READY_N")}),
    ]
)


class SignalViewError(ValueError):
    """A signal-atlas view cannot be generated without ambiguity."""


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SignalViewError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_placement(path: Path) -> dict[str, tuple[int, int, str]]:
    with path.open(encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if document.get("schema_version") != 1 or document.get("units") != "mil":
        raise SignalViewError("unsupported canonical-placement schema or units")
    positions = {}
    for ref, record in document.get("components", {}).items():
        if not isinstance(record, list) or len(record) != 3:
            raise SignalViewError(f"{ref}: placement must be [x, y, orientation]")
        x, y, orientation = record
        if not isinstance(x, int) or not isinstance(y, int):
            raise SignalViewError(f"{ref}: placement coordinates must be integers")
        if orientation not in {"", "H", "L", "R", "V"}:
            raise SignalViewError(f"{ref}: unsupported orientation {orientation!r}")
        positions[ref] = (x, y, orientation)
    return positions


def build_complete_split_projection(model: dict, projection: dict, base):
    """Represent the complete model while splitting physical J1 for layout."""

    components = {component["ref"]: component for component in model["components"]}
    odd, even = base.split_j1_component(components["J1"])
    projected_components = [odd, even]
    projected_components.extend(
        copy.deepcopy(component)
        for component in model["components"]
        if component["ref"] != "J1"
    )
    projected_nets = []
    for net in model["nets"]:
        projected_nets.append(
            {
                "net_id": net["net_id"],
                "members": [
                    base.project_j1_member(member)
                    if member["component"] == "J1"
                    else copy.deepcopy(member)
                    for member in net["members"]
                ],
            }
        )
    projected_unconnected = []
    for item in model["unconnected"]:
        record = copy.deepcopy(item)
        if item["component"] == "J1":
            record.update(base.project_j1_member(item))
        projected_unconnected.append(record)

    mappings = [
        {"ref": "JO1", "library": "Connector_Generic", "symbol": "Conn_01x17"},
        {"ref": "JE1", "library": "Connector_Generic", "symbol": "Conn_01x17"},
    ]
    mappings.extend(
        copy.deepcopy(mapping)
        for mapping in projection["components"]
        if mapping["ref"] != "J1"
    )
    return (
        {
            "components": projected_components,
            "nets": projected_nets,
            "unconnected": projected_unconnected,
        },
        {
            "top_name": VIEW_ZERO_NAME,
            "title": "HW-001 signal atlas 00 — PLACEMENT AUTHORITY ONLY",
            "components": mappings,
        },
    )


def build_endpoint_projection(
    model: dict,
    projection: dict,
    base,
    endpoints_by_net: dict[str, set[tuple[str, str]]],
    top_name: str,
    title: str,
):
    """Build one exact endpoint-subset projection from canonical net IDs."""

    components = {component["ref"]: component for component in model["components"]}
    mappings = {mapping["ref"]: mapping for mapping in projection["components"]}
    canonical_nets = {net["net_id"]: net for net in model["nets"]}
    selected_physical_refs = {
        ref for endpoints in endpoints_by_net.values() for ref, _ in endpoints
    }
    projected_components = []
    projected_mappings = []
    if "J1" in selected_physical_refs:
        odd, even = base.split_j1_component(components["J1"])
        used_j1_pins = {
            int(pin)
            for endpoints in endpoints_by_net.values()
            for ref, pin in endpoints
            if ref == "J1"
        }
        if any(pin % 2 for pin in used_j1_pins):
            projected_components.append(odd)
            projected_mappings.append(
                {"ref": "JO1", "library": "Connector_Generic", "symbol": "Conn_01x17"}
            )
        if any(not pin % 2 for pin in used_j1_pins):
            projected_components.append(even)
            projected_mappings.append(
                {"ref": "JE1", "library": "Connector_Generic", "symbol": "Conn_01x17"}
            )
    for ref in sorted(selected_physical_refs - {"J1"}):
        projected_components.append(copy.deepcopy(components[ref]))
        projected_mappings.append(copy.deepcopy(mappings[ref]))

    projected_nets = []
    for net_id, selected in endpoints_by_net.items():
        try:
            canonical = {
                (member["component"], member["pin"])
                for member in canonical_nets[net_id]["members"]
            }
        except KeyError as error:
            raise SignalViewError(f"unknown canonical net {net_id}") from error
        if not selected <= canonical:
            raise SignalViewError(
                f"{net_id}: selected noncanonical endpoints {sorted(selected - canonical)}"
            )
        if len(selected) < 2:
            raise SignalViewError(f"{net_id}: a represented net needs two endpoints")
        members = []
        for ref, pin in sorted(selected):
            member = {"component": ref, "pin": pin}
            members.append(base.project_j1_member(member) if ref == "J1" else member)
        projected_nets.append({"net_id": net_id, "members": members})
    return (
        {"components": projected_components, "nets": projected_nets, "unconnected": []},
        {"top_name": top_name, "title": title, "components": projected_mappings},
    )


def complete_net_endpoints(model: dict) -> dict[str, set[tuple[str, str]]]:
    return {
        net["net_id"]: {
            (member["component"], member["pin"]) for member in net["members"]
        }
        for net in model["nets"]
    }


def build_infrastructure_specs(model: dict) -> list[dict]:
    """Build power, ground, and bias views from the canonical model itself."""

    canonical = complete_net_endpoints(model)
    agon_ground = {
        ("J1", "33"),
        ("C1", "2"),
        ("C2", "2"),
        ("C3", "2"),
        ("C5", "2"),
        ("U1", "6"),
        ("U1", "8"),
        ("U1", "10"),
        ("U2", "10"),
        ("U2", "11"),
        ("U2", "13"),
        ("U2", "15"),
        ("U2", "17"),
        ("U3", "7"),
        ("U3", "9"),
        ("U3", "12"),
    }
    p4_ground = {
        ("J2", "2"),
        ("C4", "2"),
        ("C6", "2"),
        ("U4", "2"),
        ("U4", "5"),
        ("U4", "7"),
        ("U4", "9"),
        ("U4", "12"),
    }
    bias_refs = {f"R{number}" for number in range(14, 32)}
    bias_net_ids = {
        net["net_id"]
        for net in model["nets"]
        if any(member["component"] in bias_refs for member in net["members"])
    }
    bias_endpoints = {net_id: canonical[net_id] for net_id in bias_net_ids}
    # SKiDL 2.3.0 drops several resistor endpoints from this dense bounded
    # label-based projection. Dedicated control views retain and validate all
    # of them; omit only those duplicate infrastructure endpoints here.
    bounded_p4_power = canonical["p4-3v3"] - {("R31", "1")}
    bounded_p4_power -= {("R29", "1")}
    bias_endpoints["p4-3v3"] = bounded_p4_power
    bias_endpoints["agon-3v3"] = canonical["agon-3v3"] - {("R25", "1")}
    bias_endpoints["uart-forward-oe-n"] = canonical["uart-forward-oe-n"] - {
        ("R25", "2")
    }
    return [
        lane_spec(
            16,
            "agon-3v3-domain-and-bypassing",
            "Agon 3.3 V domain and bypassing",
            {"agon-3v3": canonical["agon-3v3"], "ground": agon_ground},
            {},
            literal=False,
        ),
        lane_spec(
            17,
            "p4-3v3-domain-and-bypassing",
            "P4 3.3 V domain and bypassing",
            {
                "p4-3v3": bounded_p4_power,
                "ground": p4_ground,
            },
            {},
            literal=False,
        ),
        lane_spec(
            18,
            "common-ground",
            "Common ground",
            {"ground": canonical["ground"]},
            {},
            literal=False,
        ),
        lane_spec(
            19,
            "startup-and-fail-safe-bias-network",
            "Startup and fail-safe bias network",
            bias_endpoints,
            {},
            literal=False,
        ),
    ]


def strip_connectivity(path: Path, sexpr) -> None:
    """Remove temporary connectivity graphics while retaining every symbol."""

    text = path.read_text(encoding="utf-8")
    removable = {
        "global_label",
        "wire",
        "junction",
        "no_connect",
    }
    blocks = [
        block for block in sexpr.immediate_blocks(text) if block.kind in removable
    ]
    for block in sorted(blocks, key=lambda item: item.start, reverse=True):
        text = text[: block.start] + text[block.end :]
    path.write_text(text, encoding="utf-8")


def replace_labels_with_literal_wires(
    source: Path,
    output: Path,
    sexpr,
    base,
    expected_nets: set[str],
    header_labels: dict[str, tuple[str, str]],
    view_namespace: str,
    selected_labels: dict | None = None,
    validate_geometry: bool = True,
    star_wiring: bool = True,
    segment_routes: dict[tuple[str, int], tuple[tuple[str, str], ...]] | None = None,
) -> None:
    """Replace temporary labels with literal wires and active-pin annotations."""

    text = source.read_text(encoding="utf-8")
    label_blocks = [
        block for block in sexpr.immediate_blocks(text) if block.kind == "global_label"
    ]
    labels = selected_labels or {}
    if selected_labels is None:
        for block in label_blocks:
            endpoint = sexpr.parse_label(block)
            if endpoint.net_id in expected_nets:
                labels.setdefault(endpoint.net_id, []).append(endpoint)
    if set(labels) != expected_nets:
        raise SignalViewError(
            f"temporary labels differ: missing={sorted(expected_nets - set(labels))}, "
            f"extra={sorted(set(labels) - expected_nets)}"
        )

    segment_instances = []
    annotation_segments = {}
    for net_id in sorted(labels):
        endpoints = sorted(labels[net_id], key=lambda endpoint: endpoint.point)
        points = [(endpoint.x_text, endpoint.y_text) for endpoint in endpoints]
        annotation_segments[net_id] = (points[0], points[-1])
        if star_wiring:
            segment_instances.extend(
                (net_id, (points[0], end)) for end in points[1:]
            )
        else:
            segment_instances.extend(
                (net_id, (start, end)) for start, end in zip(points, points[1:])
            )
    route_indexes = {}
    routed_instances = []
    for net_id, (start, end) in segment_instances:
        route_indexes[net_id] = route_indexes.get(net_id, 0) + 1
        waypoints = (segment_routes or {}).get((net_id, route_indexes[net_id]), ())
        points = (start, *waypoints, end)
        routed_instances.extend(
            (net_id, segment) for segment in zip(points, points[1:])
        )
    segment_instances = routed_instances

    if validate_geometry:
        try:
            base.validate_segment_instances(segment_instances)
        except ValueError as error:
            raise SignalViewError(
                f"{error}; generated segments={segment_instances!r}"
            ) from error

    indexes = {}
    wires = []
    for net_id, segment in segment_instances:
        indexes[net_id] = indexes.get(net_id, 0) + 1
        wires.append(
            base.wire_block(
                net_id,
                indexes[net_id],
                *segment,
                view_namespace,
            )
        )
    annotations = base.header_annotation_blocks(
        annotation_segments, header_labels, view_namespace
    )
    pieces = []
    cursor = 0
    for index, block in enumerate(label_blocks):
        pieces.append(text[cursor : block.start])
        if index == 0:
            pieces.append("\n".join((*wires, *annotations)) + "\n")
        cursor = block.end
    pieces.append(text[cursor:])
    output.write_text("".join(pieces), encoding="utf-8")


def strip_no_connects(path: Path, sexpr) -> None:
    """Remove canonical no-connect marks from a bounded signal projection."""

    text = path.read_text(encoding="utf-8")
    blocks = [
        block for block in sexpr.immediate_blocks(text) if block.kind == "no_connect"
    ]
    for block in sorted(blocks, key=lambda item: item.start, reverse=True):
        text = text[: block.start] + text[block.end :]
    path.write_text(text, encoding="utf-8")


def match_projected_labels(full_path: Path, endpoints_by_net: dict, sexpr):
    """Select each requested endpoint's label nearest its owning symbol."""

    text = full_path.read_text(encoding="utf-8")
    full = {}
    centers = {}
    for block in sexpr.immediate_blocks(text):
        if block.kind == "global_label":
            endpoint = sexpr.parse_label(block)
            if endpoint.net_id in endpoints_by_net:
                full.setdefault(endpoint.net_id, []).append(endpoint)
        elif block.kind == "symbol":
            ref = re.search(r'^\s*\(property "Reference" "([^"]+)"', block.text, re.MULTILINE)
            at = re.match(r'^\(symbol\s+\(lib_id "[^"]+"\)\s+\(at ([^ )]+) ([^ )]+)', block.text)
            if ref and at:
                centers[ref.group(1)] = (float(at.group(1)), float(at.group(2)))
    selected = {}
    for net_id, endpoints in endpoints_by_net.items():
        available = list(full[net_id])
        chosen = []
        for ref, pin in endpoints:
            if ref == "J1":
                physical_pin = int(pin)
                ref = "JO1" if physical_pin % 2 else "JE1"
            target = centers[ref]
            nearest = min(
                available,
                key=lambda candidate: (candidate.point[0] - target[0]) ** 2
                + (candidate.point[1] - target[1]) ** 2,
            )
            available.remove(nearest)
            if ref.startswith("R"):
                side = -1 if nearest.point[0] < target[0] else 1
                nearest = replace(
                    nearest,
                    x_text=f"{target[0] + side * 3.81:g}",
                    y_text=f"{target[1]:g}",
                )
            chosen.append(nearest)
        selected[net_id] = chosen
    return selected


def generate(
    placement_path: Path,
    projection_path: Path,
    output_dir: Path,
    selected_additional_views: set[int] | None = None,
) -> tuple[Path, ...]:
    base = load_module("hw001_signal_projection_support", PROJECTION_SUPPORT)
    electrical = load_module("hw001_signal_kicad", ELECTRICAL_MODEL / "generate_kicad.py")
    sexpr = load_module("hw001_signal_sexpr", KICAD_SEXPR)
    projection_path = projection_path.resolve()
    projection = electrical.load_yaml(projection_path)
    model_path = (projection_path.parent / projection["source_model"]).resolve()
    model = electrical.load_model_validator().validate(model_path)
    electrical.validate_projection(projection, model)
    projected_model, projected_mapping = build_complete_split_projection(
        model, projection, base
    )
    placement = load_placement(placement_path)
    expected_refs = {component["ref"] for component in projected_model["components"]}
    if set(placement) != expected_refs:
        raise SignalViewError(
            f"canonical placement mismatch: missing={sorted(expected_refs - set(placement))}, "
            f"extra={sorted(set(placement) - expected_refs)}"
        )

    circuit = electrical.build_circuit(
        projected_model,
        projected_mapping,
        projection_path.parent,
        force_label_stubs=True,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hw001-signal-view-zero-") as scratch:
        temporary = base.write_fixed_label_view(
            electrical,
            circuit,
            placement,
            Path(scratch),
            VIEW_ZERO_NAME,
            projected_mapping["title"],
        )
        output = output_dir / f"{VIEW_ZERO_NAME}.kicad_sch"
        output.write_text(temporary.read_text(encoding="utf-8"), encoding="utf-8")
    strip_connectivity(output, sexpr)
    base.clean_functional_connector_fields(output, sexpr)

    view_one_model = copy.deepcopy(projected_model)
    view_one_mapping = copy.deepcopy(projected_mapping)
    view_one_mapping["top_name"] = VIEW_ONE_NAME
    view_one_mapping["title"] = (
        "HW-001 signal atlas 01 D0 / UART RX lane — NOT AUTHORITY"
    )
    view_one_circuit = electrical.build_circuit(
        view_one_model,
        view_one_mapping,
        projection_path.parent,
        force_label_stubs=True,
    )
    with tempfile.TemporaryDirectory(prefix="hw001-signal-view-one-") as scratch:
        temporary = base.write_fixed_label_view(
            electrical,
            view_one_circuit,
            placement,
            Path(scratch),
            VIEW_ONE_NAME,
            view_one_mapping["title"],
        )
        view_one_output = output_dir / f"{VIEW_ONE_NAME}.kicad_sch"
        replace_labels_with_literal_wires(
            temporary,
            view_one_output,
            sexpr,
            base,
            set(VIEW_ONE_ENDPOINTS),
            VIEW_ONE_HEADER_LABELS,
            "signal-view-01",
            match_projected_labels(temporary, VIEW_ONE_ENDPOINTS, sexpr),
        )
    base.clean_functional_connector_fields(view_one_output, sexpr)
    strip_no_connects(view_one_output, sexpr)

    view_two_model = copy.deepcopy(projected_model)
    view_two_mapping = copy.deepcopy(projected_mapping)
    view_two_mapping["top_name"] = VIEW_TWO_NAME
    view_two_mapping["title"] = (
        "HW-001 signal atlas 02 D1 / UART TX lane — NOT AUTHORITY"
    )
    view_two_circuit = electrical.build_circuit(
        view_two_model,
        view_two_mapping,
        projection_path.parent,
        force_label_stubs=True,
    )
    with tempfile.TemporaryDirectory(prefix="hw001-signal-view-two-") as scratch:
        temporary = base.write_fixed_label_view(
            electrical,
            view_two_circuit,
            placement,
            Path(scratch),
            VIEW_TWO_NAME,
            view_two_mapping["title"],
        )
        view_two_output = output_dir / f"{VIEW_TWO_NAME}.kicad_sch"
        replace_labels_with_literal_wires(
            temporary,
            view_two_output,
            sexpr,
            base,
            set(VIEW_TWO_ENDPOINTS),
            VIEW_TWO_HEADER_LABELS,
            "signal-view-02",
            match_projected_labels(temporary, VIEW_TWO_ENDPOINTS, sexpr),
            star_wiring=False,
            segment_routes=VIEW_TWO_SEGMENT_ROUTES,
        )
    base.clean_functional_connector_fields(view_two_output, sexpr)
    strip_no_connects(view_two_output, sexpr)

    additional_outputs = []
    for spec in (*ADDITIONAL_STATIC_SPECS, *build_infrastructure_specs(model)):
        if (
            selected_additional_views is not None
            and spec["number"] not in selected_additional_views
        ):
            continue
        if spec["literal"]:
            view_model = copy.deepcopy(projected_model)
            view_mapping = copy.deepcopy(projected_mapping)
            view_placement = placement
        else:
            view_model, view_mapping = build_endpoint_projection(
                model,
                projection,
                base,
                spec["endpoints"],
                spec["name"],
                spec["title"],
            )
            view_placement = {
                ref: placement[ref]
                for ref in {
                    component["ref"] for component in view_model["components"]
                }
            }
        view_mapping["top_name"] = spec["name"]
        view_mapping["title"] = spec["title"]
        view_circuit = electrical.build_circuit(
            view_model,
            view_mapping,
            projection_path.parent,
            force_label_stubs=True,
        )
        with tempfile.TemporaryDirectory(
            prefix=f"hw001-signal-view-{spec['number']:02d}-"
        ) as scratch:
            temporary = base.write_fixed_label_view(
                electrical,
                view_circuit,
                view_placement,
                Path(scratch),
                spec["name"],
                spec["title"],
            )
            view_output = output_dir / f"{spec['name']}.kicad_sch"
            if spec["literal"]:
                replace_labels_with_literal_wires(
                    temporary,
                    view_output,
                    sexpr,
                    base,
                    set(spec["endpoints"]),
                    spec["labels"],
                    f"signal-view-{spec['number']:02d}",
                    match_projected_labels(temporary, spec["endpoints"], sexpr),
                    star_wiring=spec["star_wiring"],
                    segment_routes=spec["routes"],
                )
            else:
                view_output.write_text(
                    temporary.read_text(encoding="utf-8"), encoding="utf-8"
                )
        if spec["literal"]:
            base.clean_functional_connector_fields(view_output, sexpr)
        strip_no_connects(view_output, sexpr)
        additional_outputs.append(view_output)

    return (
        output,
        view_one_output,
        view_two_output,
        *additional_outputs,
    )


def main() -> int:
    electrical = load_module("hw001_signal_bootstrap", ELECTRICAL_MODEL / "generate_kicad.py")
    electrical.ensure_deterministic_python_hashes()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--placement", type=Path, default=DEFAULT_PLACEMENT)
    parser.add_argument("--projection", type=Path, default=DEFAULT_PROJECTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--views",
        type=int,
        nargs="+",
        help="generate only these additional view numbers (3 through 19)",
    )
    args = parser.parse_args()
    try:
        outputs = generate(
            args.placement,
            args.projection,
            args.output_dir,
            set(args.views) if args.views else None,
        )
    except (OSError, RuntimeError, SignalViewError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for output in outputs:
        print(f"PASS: generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
