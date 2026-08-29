#!/usr/bin/env python3
"""Validate the task-local placement-independent electrical model.

This validator intentionally knows nothing about schematic coordinates,
breadboard placement, PCB routing, or firmware. Cross-reference and terminal
accounting checks complement JSON Schema and prevent a visually plausible YAML
edit from silently changing or corrupting the electrical graph.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "schema" / "circuit.schema.json"


class ModelError(ValueError):
    """A structural or semantic electrical-model error."""


def natural_key(value: str) -> tuple[tuple[int, Any], ...]:
    """Return a deterministic natural-sort key for references and pins."""

    return tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in re.split(r"(\d+)", value)
        if part
    )


def endpoint_key(endpoint: dict[str, str]) -> tuple[Any, ...]:
    return natural_key(endpoint["component"]) + ((2, "@"),) + natural_key(endpoint["pin"])


def endpoint_label(endpoint: tuple[str, str]) -> str:
    return f"{endpoint[0]}.{endpoint[1]}"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if not isinstance(document, dict):
        raise ModelError(f"{path}: top-level YAML value must be a mapping")
    return document


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def require_unique(values: Iterable[str], label: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        rendered = ", ".join(sorted(duplicates, key=natural_key))
        raise ModelError(f"duplicate {label}: {rendered}")


def require_order(actual: list[Any], expected: list[Any], label: str) -> None:
    if actual != expected:
        raise ModelError(f"{label} are not in canonical natural order")


def validate_schema(document: dict[str, Any]) -> None:
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise ModelError(f"schema error at {location}: {error.message}")


def validate_semantics(document: dict[str, Any]) -> None:
    components = document["components"]
    component_refs = [component["ref"] for component in components]
    require_unique(component_refs, "component reference")
    require_order(component_refs, sorted(component_refs, key=natural_key), "components")

    terminals: set[tuple[str, str]] = set()
    for component in components:
        ref = component["ref"]
        pins = [terminal["pin"] for terminal in component["terminals"]]
        require_unique(pins, f"terminal pin in {ref}")
        require_order(pins, sorted(pins, key=natural_key), f"terminals in {ref}")

        orientation = component["orientation"]
        polarity_roles = [
            terminal.get("polarity_role") for terminal in component["terminals"]
        ]
        if orientation == "polarized" and not any(polarity_roles):
            raise ModelError(f"polarized component {ref} has no terminal polarity roles")
        if orientation != "polarized" and any(polarity_roles):
            raise ModelError(
                f"nonpolar/keyed component {ref} must not declare terminal polarity roles"
            )
        if orientation != "symmetric" and any(
            "interchangeable_group" in terminal for terminal in component["terminals"]
        ):
            raise ModelError(
                f"only symmetric component {ref} may declare interchangeable terminals"
            )

        terminals.update((ref, pin) for pin in pins)

    nets = document["nets"]
    net_ids = [net["net_id"] for net in nets]
    require_unique(net_ids, "net ID")
    require_order(net_ids, sorted(net_ids), "nets")

    assignments: dict[tuple[str, str], str] = {}
    for net in nets:
        members = net["members"]
        expected_members = sorted(members, key=endpoint_key)
        require_order(members, expected_members, f"members of net {net['net_id']}")

        endpoints = [(member["component"], member["pin"]) for member in members]
        labels = [endpoint_label(endpoint) for endpoint in endpoints]
        require_unique(labels, f"member in net {net['net_id']}")

        for endpoint in endpoints:
            if endpoint not in terminals:
                raise ModelError(
                    f"net {net['net_id']} references undeclared terminal "
                    f"{endpoint_label(endpoint)}"
                )
            if endpoint in assignments:
                raise ModelError(
                    f"terminal {endpoint_label(endpoint)} is assigned to both "
                    f"{assignments[endpoint]} and net {net['net_id']}"
                )
            assignments[endpoint] = f"net {net['net_id']}"

    unconnected = document["unconnected"]
    expected_unconnected = sorted(unconnected, key=endpoint_key)
    require_order(unconnected, expected_unconnected, "unconnected terminals")
    unconnected_endpoints = [
        (endpoint["component"], endpoint["pin"]) for endpoint in unconnected
    ]
    require_unique(
        [endpoint_label(endpoint) for endpoint in unconnected_endpoints],
        "intentional-unconnected terminal",
    )
    for endpoint in unconnected_endpoints:
        if endpoint not in terminals:
            raise ModelError(
                f"unconnected record references undeclared terminal {endpoint_label(endpoint)}"
            )
        if endpoint in assignments:
            raise ModelError(
                f"terminal {endpoint_label(endpoint)} is assigned to both "
                f"{assignments[endpoint]} and unconnected"
            )
        assignments[endpoint] = "unconnected"

    missing = sorted(terminals - assignments.keys(), key=lambda item: endpoint_key(
        {"component": item[0], "pin": item[1]}
    ))
    if missing:
        rendered = ", ".join(endpoint_label(endpoint) for endpoint in missing)
        raise ModelError(f"declared terminals are not accounted for: {rendered}")


def validate(path: Path) -> dict[str, Any]:
    document = load_yaml(path)
    validate_schema(document)
    validate_semantics(document)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an HW-001 placement-independent circuit model."
    )
    parser.add_argument("model", type=Path)
    args = parser.parse_args()

    try:
        document = validate(args.model)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ModelError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(
        "PASS: "
        f"{args.model} — {len(document['components'])} components, "
        f"{len(document['nets'])} nets, "
        f"{len(document['unconnected'])} intentional no-connects"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
