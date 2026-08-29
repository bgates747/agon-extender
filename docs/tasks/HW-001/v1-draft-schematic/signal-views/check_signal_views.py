#!/usr/bin/env python3
"""Validate generated HW-001 signal-atlas drawings."""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
KICAD_SEXPR = ROOT / "kicad_sexpr.py"
MODEL_PATH = ROOT.parents[4] / "hardware/designs/light2-harness-r02/connectivity.yaml"
DEFAULT_PLACEMENT = ROOT / "canonical-placement.yaml"
DEFAULT_VIEW_ZERO = ROOT / "generated/00-canonical-component-placement.kicad_sch"
DEFAULT_VIEW_ONE = ROOT / "generated/01-d0-uart-rx-lane.kicad_sch"
DEFAULT_VIEW_ONE_NETLIST = ROOT / "generated/01-d0-uart-rx-lane.xml"
DEFAULT_VIEW_TWO = ROOT / "generated/02-d1-uart-tx-lane.kicad_sch"
DEFAULT_VIEW_TWO_NETLIST = ROOT / "generated/02-d1-uart-tx-lane.xml"


class CheckError(ValueError):
    """A signal-atlas artifact violates its declared contract."""


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CheckError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check(placement_path: Path, schematic_path: Path) -> None:
    with placement_path.open(encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    components = document.get("components", {})
    if len(components) != 45:
        raise CheckError(f"canonical placement requires 45 projected components, got {len(components)}")
    for prefix, expected_count in (("U", 4), ("C", 6), ("R", 31)):
        refs = [ref for ref in components if ref.startswith(prefix)]
        if len(refs) != expected_count:
            raise CheckError(f"expected {expected_count} {prefix} references, got {len(refs)}")
        x_positions = [components[ref][0] for ref in refs]
        if len(x_positions) != len(set(x_positions)):
            raise CheckError(f"{prefix} components are not all horizontally staggered")

    sexpr = load_module("hw001_signal_check_sexpr", KICAD_SEXPR)
    text = schematic_path.read_text(encoding="utf-8")
    blocks = list(sexpr.immediate_blocks(text))
    forbidden = {"global_label", "wire", "junction", "no_connect"}
    present = sorted({block.kind for block in blocks} & forbidden)
    if present:
        raise CheckError(f"view 0 must be wire-free; found {present}")

    actual_refs = set()
    for block in blocks:
        if block.kind != "symbol":
            continue
        match = re.search(r'^\s*\(property "Reference" "([^"]+)"', block.text, re.MULTILINE)
        if match:
            actual_refs.add(match.group(1))
    if actual_refs != set(components):
        raise CheckError(
            f"view 0 component mismatch: missing={sorted(set(components) - actual_refs)}, "
            f"extra={sorted(actual_refs - set(components))}"
        )


def symbol_placements(text: str, sexpr) -> dict[str, tuple[float, float, float]]:
    """Return each root symbol's numeric KiCad ``at`` coordinates."""

    placements = {}
    for block in sexpr.immediate_blocks(text):
        if block.kind != "symbol":
            continue
        ref = re.search(
            r'^\s*\(property "Reference" "([^"]+)"', block.text, re.MULTILINE
        )
        at = re.match(r'^\(symbol\s+\(lib_id "[^"]+"\)\s+\(at ([^)]+)\)', block.text)
        if ref and at:
            values = tuple(float(value) for value in at.group(1).split())
            if len(values) != 3:
                raise CheckError(f"{ref.group(1)}: malformed symbol placement")
            placements[ref.group(1)] = values
    return placements


def canonical_endpoint(ref: str, pin: str) -> tuple[str, str]:
    if ref == "JO1":
        return "J1", str(2 * int(pin) - 1)
    if ref == "JE1":
        return "J1", str(2 * int(pin))
    return ref, pin


def check_signal_view(
    view_zero_path: Path,
    view_path: Path,
    netlist_path: Path,
    view_number: int,
    endpoints_by_net: dict[str, set[tuple[str, str]]],
    header_labels: dict[str, tuple[str, str]],
    segment_routes: dict[tuple[str, int], tuple[tuple[str, str], ...]] | None = None,
    literal: bool = True,
) -> None:
    generator = load_module("hw001_signal_generator_check", ROOT / "generate_signal_views.py")
    sexpr = load_module("hw001_signal_view_one_sexpr", KICAD_SEXPR)
    text = view_path.read_text(encoding="utf-8")
    blocks = list(sexpr.immediate_blocks(text))
    forbidden = {"junction", "no_connect"}
    if literal:
        forbidden.add("global_label")
    if any(block.kind in forbidden for block in blocks):
        raise CheckError(
            f"view {view_number} contains a forbidden label, junction, or no-connect"
        )
    wires = [block for block in blocks if block.kind == "wire"]
    if literal:
        expected_wire_count = sum(
            len(endpoints) - 1 for endpoints in endpoints_by_net.values()
        )
        expected_wire_count += sum(
            len(points) for points in (segment_routes or {}).values()
        )
        if len(wires) != expected_wire_count:
            raise CheckError(
                f"view {view_number} requires {expected_wire_count} wires, got {len(wires)}"
            )
        actual_labels = set(re.findall(r'^  \(text "([^"]+)"', text, re.MULTILINE))
        expected_labels = {label for _, label in header_labels.values()}
        if actual_labels != expected_labels:
            raise CheckError(
                f"view {view_number} active-header annotations differ from specification"
            )

    zero_placements = symbol_placements(view_zero_path.read_text(encoding="utf-8"), sexpr)
    one_placements = symbol_placements(text, sexpr)
    expected_refs = set(zero_placements) if literal else {
        ("JO1" if int(pin) % 2 else "JE1") if ref == "J1" else ref
        for endpoints in endpoints_by_net.values()
        for ref, pin in endpoints
    }
    if set(one_placements) != expected_refs:
        raise CheckError(
            f"view {view_number} component set differs: {sorted(one_placements)}"
        )
    offsets = []
    for ref, placement in one_placements.items():
        canonical = zero_placements.get(ref)
        if canonical is None or placement[2] != canonical[2]:
            raise CheckError(
                f"{ref}: view {view_number} changed its canonical orientation"
            )
        offsets.append(
            (placement[0] - canonical[0], placement[1] - canonical[1])
        )
    baseline = offsets[0]
    if any(
        abs(offset[0] - baseline[0]) > 0.011
        or abs(offset[1] - baseline[1]) > 0.011
        for offset in offsets[1:]
    ):
        raise CheckError(
            f"view {view_number} moved components relative to canonical placement"
        )

    expected = Counter(frozenset(endpoints) for endpoints in endpoints_by_net.values())
    root = ET.parse(netlist_path).getroot()
    nets = root.find("nets")
    if nets is None:
        raise CheckError(f"view {view_number} netlist has no nets element")
    actual = Counter()
    for net in nets.findall("net"):
        if net.get("name", "").startswith("unconnected-("):
            continue
        actual[
            frozenset(
                canonical_endpoint(node.get("ref", ""), node.get("pin", ""))
                for node in net.findall("node")
            )
        ] += 1
    if actual != expected:
        raise CheckError(
            f"view {view_number} endpoint partition differs from its exact projection; "
            f"missing={list((expected - actual).elements())!r}; "
            f"extra={list((actual - expected).elements())!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--placement", type=Path, default=DEFAULT_PLACEMENT)
    parser.add_argument("--view-zero", type=Path, default=DEFAULT_VIEW_ZERO)
    parser.add_argument("--view-one", type=Path, default=DEFAULT_VIEW_ONE)
    parser.add_argument(
        "--view-one-netlist", type=Path, default=DEFAULT_VIEW_ONE_NETLIST
    )
    parser.add_argument("--view-two", type=Path, default=DEFAULT_VIEW_TWO)
    parser.add_argument(
        "--view-two-netlist", type=Path, default=DEFAULT_VIEW_TWO_NETLIST
    )
    args = parser.parse_args()
    try:
        check(args.placement, args.view_zero)
        generator = load_module(
            "hw001_signal_generator_contract", ROOT / "generate_signal_views.py"
        )
        check_signal_view(
            args.view_zero,
            args.view_one,
            args.view_one_netlist,
            1,
            generator.VIEW_ONE_ENDPOINTS,
            generator.VIEW_ONE_HEADER_LABELS,
        )
        check_signal_view(
            args.view_zero,
            args.view_two,
            args.view_two_netlist,
            2,
            generator.VIEW_TWO_ENDPOINTS,
            generator.VIEW_TWO_HEADER_LABELS,
            generator.VIEW_TWO_SEGMENT_ROUTES,
        )
        with MODEL_PATH.open(encoding="utf-8") as stream:
            model = yaml.safe_load(stream)
        additional_specs = (
            *generator.ADDITIONAL_STATIC_SPECS,
            *generator.build_infrastructure_specs(model),
        )
        for spec in additional_specs:
            check_signal_view(
                args.view_zero,
                ROOT / "generated" / f"{spec['name']}.kicad_sch",
                ROOT / "generated" / f"{spec['name']}.xml",
                spec["number"],
                spec["endpoints"],
                spec["labels"],
                spec["routes"],
                spec["literal"],
            )

        represented = {
            endpoint
            for endpoints in (
                *generator.VIEW_ONE_ENDPOINTS.values(),
                *generator.VIEW_TWO_ENDPOINTS.values(),
                *(
                    endpoints
                    for spec in additional_specs
                    for endpoints in spec["endpoints"].values()
                ),
            )
            for endpoint in endpoints
        }
        canonical = {
            (member["component"], member["pin"])
            for net in model["nets"]
            for member in net["members"]
        }
        if represented != canonical:
            raise CheckError(
                "atlas connected-terminal coverage differs from canonical model; "
                f"missing={sorted(canonical - represented)!r}; "
                f"extra={sorted(represented - canonical)!r}"
            )
    except (OSError, ET.ParseError, CheckError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        "PASS: all 19 atlas views match their exact endpoint projections and "
        "collectively cover every canonical connected terminal"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
