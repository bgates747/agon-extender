#!/usr/bin/env python3
"""Compare a KiCad XML netlist projection with its authoritative YAML model."""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class ComparisonError(ValueError):
    """The KiCad projection does not match the YAML electrical authority."""


def load_model_validator():
    spec = importlib.util.spec_from_file_location("hw001_model_validator", ROOT / "validate.py")
    if spec is None or spec.loader is None:
        raise ComparisonError("cannot load HW-001 electrical-model validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def endpoint(member: dict[str, str]) -> tuple[str, str]:
    return member["component"], member["pin"]


def expected_nets(model: dict) -> dict[str, frozenset[tuple[str, str]]]:
    return {
        net["net_id"]: frozenset(endpoint(member) for member in net["members"])
        for net in model["nets"]
    }


def expected_unconnected(model: dict) -> frozenset[tuple[str, str]]:
    return frozenset(endpoint(member) for member in model["unconnected"])


def actual_nets(path: Path) -> dict[str, frozenset[tuple[str, str]]]:
    root = ET.parse(path).getroot()
    nets_element = root.find("nets")
    if nets_element is None:
        raise ComparisonError(f"{path}: missing XML nets element")
    result: dict[str, frozenset[tuple[str, str]]] = {}
    for net in nets_element.findall("net"):
        name = net.get("name")
        if not name:
            raise ComparisonError(f"{path}: net without a name")
        members = frozenset(
            (node.get("ref", ""), node.get("pin", ""))
            for node in net.findall("node")
        )
        if name in result:
            raise ComparisonError(f"{path}: duplicate XML net name {name}")
        result[name] = members
    return result


def compare(
    model_path: Path,
    netlist_path: Path,
    *,
    ignore_net_names: bool = False,
) -> None:
    validator = load_model_validator()
    model = validator.validate(model_path)
    expected = expected_nets(model)
    actual = actual_nets(netlist_path)
    declared_unconnected = expected_unconnected(model)

    # KiCad's XML exporter emits each deliberately no-connect-marked pin as a
    # synthetic one-pin `unconnected-(...-Pad...)` net. Match those endpoints
    # to the authority explicitly, then remove only those exact synthetic nets
    # before comparing the named connected nets.
    actual_unconnected: set[tuple[str, str]] = set()
    connected_actual = {}
    for name, members in actual.items():
        if name.startswith("unconnected-(") and len(members) == 1:
            actual_unconnected.update(members)
        else:
            connected_actual[name] = members

    if declared_unconnected != frozenset(actual_unconnected):
        raise ComparisonError(
            "KiCad no-connect mismatch: "
            f"expected={sorted(declared_unconnected)}, "
            f"actual={sorted(actual_unconnected)}"
        )

    if ignore_net_names:
        expected_partitions = Counter(expected.values())
        actual_partitions = Counter(connected_actual.values())
        if expected_partitions == actual_partitions:
            return
        raise ComparisonError(
            "KiCad topology mismatch with net names ignored: "
            f"expected={sorted(sorted(members) for members in expected_partitions.elements())}, "
            f"actual={sorted(sorted(members) for members in actual_partitions.elements())}"
        )

    if expected == connected_actual:
        return

    messages = []
    for net_id in sorted(set(expected) | set(connected_actual)):
        if expected.get(net_id) != connected_actual.get(net_id):
            messages.append(
                f"{net_id}: expected={sorted(expected.get(net_id, []))}, "
                f"actual={sorted(connected_actual.get(net_id, []))}"
            )
    raise ComparisonError("KiCad netlist mismatch: " + "; ".join(messages))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare a KiCad XML netlist against an HW-001 YAML model."
    )
    parser.add_argument("model", type=Path)
    parser.add_argument("netlist", type=Path)
    parser.add_argument(
        "--ignore-net-names",
        action="store_true",
        help=(
            "compare exact endpoint partitions while allowing KiCad-generated "
            "net names"
        ),
    )
    args = parser.parse_args()
    try:
        compare(
            args.model,
            args.netlist,
            ignore_net_names=args.ignore_net_names,
        )
    except (OSError, ET.ParseError, ComparisonError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    qualifier = (
        "exactly matches the endpoint topology of"
        if args.ignore_net_names
        else "exactly matches"
    )
    print(f"PASS: {args.netlist} {qualifier} {args.model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
