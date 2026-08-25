#!/usr/bin/env python3
"""Extract electrical connectivity from a bundled Fritzing breadboard sketch.

This task-local extractor exists because visual inspection cannot distinguish a
wire that merely touches a hole from one Fritzing records as connected.  It
resolves reciprocal sketch links, bundled-part buses, and ideal wire continuity
into deterministic net identities while keeping resistors, capacitors, and IC
pins as component boundaries.

The output is audit evidence, not an electrical simulator.  In particular, it
does not model powered logic behavior inside U1 or infer connections from SVG
overlap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = (
    ROOT.parent
    / "SETUP-006"
    / "SETUP-006.4-wiring-design"
    / "light2-extender-breadboard-wiring-draft_v1.fzz"
)
GENERATED = ROOT / "generated"
JSON_OUTPUT = GENERATED / "connectivity.json"
MARKDOWN_OUTPUT = GENERATED / "connectivity.md"


Endpoint = tuple[str, str]


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[Endpoint, Endpoint] = {}

    def add(self, item: Endpoint) -> None:
        self.parent.setdefault(item, item)

    def find(self, item: Endpoint) -> Endpoint:
        self.add(item)
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: Endpoint, right: Endpoint) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            self.parent[right_root] = left_root
        else:
            self.parent[left_root] = right_root


@dataclass(frozen=True)
class Instance:
    model_index: str
    module_id: str
    title: str
    properties: dict[str, str]
    element: ET.Element


def read_archive(path: Path) -> tuple[dict[str, bytes], str, ET.Element]:
    with zipfile.ZipFile(path) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    sketches = [name for name in files if name.endswith(".fz")]
    if len(sketches) != 1:
        raise ValueError(f"expected one Fritzing sketch, found {len(sketches)}")
    sketch_name = sketches[0]
    return files, sketch_name, ET.fromstring(files[sketch_name])


def parse_instances(root: ET.Element) -> dict[str, Instance]:
    result: dict[str, Instance] = {}
    for element in root.findall("./instances/instance"):
        model_index = element.get("modelIndex", "")
        if not model_index or model_index in result:
            raise ValueError(f"missing or duplicate model index {model_index!r}")
        properties = {
            item.get("name", ""): item.get("value", "")
            for item in element.findall("./property")
        }
        result[model_index] = Instance(
            model_index=model_index,
            module_id=element.get("moduleIdRef", ""),
            title=element.findtext("title") or f"instance-{model_index}",
            properties=properties,
            element=element,
        )
    return result


def connector_elements(instance: Instance) -> list[ET.Element]:
    view = instance.element.find("./views/breadboardView")
    if view is None:
        return []
    return view.findall("./connectors/connector")


def direct_links(
    instances: dict[str, Instance],
) -> tuple[set[tuple[Endpoint, Endpoint]], list[dict[str, object]]]:
    links: set[tuple[Endpoint, Endpoint]] = set()
    raw: dict[tuple[Endpoint, Endpoint], int] = defaultdict(int)
    for instance in instances.values():
        for connector in connector_elements(instance):
            source = (instance.model_index, connector.get("connectorId", ""))
            for target in connector.findall("./connects/connect"):
                destination = (
                    target.get("modelIndex", ""),
                    target.get("connectorId", ""),
                )
                pair = tuple(sorted((source, destination)))
                links.add(pair)
                raw[(source, destination)] += 1

    reciprocity: list[dict[str, object]] = []
    for left, right in sorted(links):
        reciprocity.append(
            {
                "left": list(left),
                "right": list(right),
                "left_to_right": raw[(left, right)] > 0,
                "right_to_left": raw[(right, left)] > 0,
            }
        )
    return links, reciprocity


def bundled_connectors(files: dict[str, bytes], module_id: str) -> set[str] | None:
    name = f"part.{module_id}.fzp"
    if name not in files:
        return None
    root = ET.fromstring(files[name])
    return {item.get("id", "") for item in root.findall("./connectors/connector")}


def add_bundled_buses(
    files: dict[str, bytes], instances: dict[str, Instance], union: UnionFind
) -> list[dict[str, object]]:
    buses: list[dict[str, object]] = []
    for instance in instances.values():
        name = f"part.{instance.module_id}.fzp"
        if name not in files:
            continue
        root = ET.fromstring(files[name])
        for bus in root.findall("./buses/bus"):
            members = [
                (instance.model_index, member.get("connectorId", ""))
                for member in bus.findall("nodeMember")
            ]
            for member in members:
                union.add(member)
            for member in members[1:]:
                union.union(members[0], member)
            buses.append(
                {
                    "model_index": instance.model_index,
                    "instance": instance.title,
                    "bus_id": bus.get("id", ""),
                    "members": [list(member) for member in members],
                }
            )
    return buses


def part_endpoint_ids(instance: Instance, files: dict[str, bytes]) -> set[str]:
    bundled = bundled_connectors(files, instance.module_id)
    if bundled is not None:
        return bundled
    ids = {item.get("connectorId", "") for item in connector_elements(instance)}
    # Stock two-terminal passives can have a visually unconnected lead omitted
    # from the sketch's connector list.  Preserve that lead as a dangling
    # endpoint instead of silently dropping it from the audit.
    if instance.module_id in {
        "ResistorModuleID",
        "100milCeramicCapacitorModuleID",
        "WireModuleID",
    }:
        ids.update(("connector0", "connector1"))
    return ids


def component_kind(module_id: str) -> str:
    if module_id == "WireModuleID":
        return "wire"
    if module_id == "ResistorModuleID":
        return "resistor"
    if module_id == "100milCeramicCapacitorModuleID":
        return "capacitor"
    if "sn74hc125n" in module_id.lower() or "sn74lv125" in module_id.lower():
        return "logic_ic"
    if "header" in module_id.lower():
        return "connector"
    if "devkit" in module_id.lower():
        return "board"
    if "bb1460" in module_id.lower():
        return "breadboard"
    return "other"


def endpoint_record(endpoint: Endpoint, instances: dict[str, Instance]) -> dict[str, str]:
    instance = instances[endpoint[0]]
    return {
        "model_index": endpoint[0],
        "instance": instance.title,
        "module_id": instance.module_id,
        "kind": component_kind(instance.module_id),
        "connector": endpoint[1],
    }


def value_for(instance: Instance) -> str | None:
    if instance.module_id == "ResistorModuleID":
        return instance.properties.get("resistance")
    if instance.module_id == "100milCeramicCapacitorModuleID":
        return instance.properties.get("capacitance")
    return None


def wire_color(instance: Instance) -> str | None:
    item = instance.element.find("./views/breadboardView/wireExtras")
    return item.get("color") if item is not None else None


def build(path: Path) -> tuple[dict[str, object], str]:
    files, sketch_name, root = read_archive(path)
    instances = parse_instances(root)
    union = UnionFind()

    for instance in instances.values():
        for connector_id in part_endpoint_ids(instance, files):
            union.add((instance.model_index, connector_id))

    links, reciprocity = direct_links(instances)
    for left, right in links:
        if left[0] not in instances or right[0] not in instances:
            raise ValueError(f"connection references missing instance: {left} <-> {right}")
        union.union(left, right)

    buses = add_bundled_buses(files, instances, union)

    # A Fritzing wire is an ideal conductor between its two endpoints. Passive
    # components and IC pins deliberately remain boundaries.
    for instance in instances.values():
        if instance.module_id == "WireModuleID":
            union.union(
                (instance.model_index, "connector0"),
                (instance.model_index, "connector1"),
            )

    groups: dict[Endpoint, list[Endpoint]] = defaultdict(list)
    for endpoint in union.parent:
        groups[union.find(endpoint)].append(endpoint)
    ordered_groups = sorted(
        (sorted(members) for members in groups.values()), key=lambda members: members
    )
    net_by_endpoint: dict[Endpoint, str] = {}
    nets: list[dict[str, object]] = []
    for number, members in enumerate(ordered_groups, start=1):
        net_id = f"N{number:03d}"
        for endpoint in members:
            net_by_endpoint[endpoint] = net_id
        nets.append(
            {
                "net_id": net_id,
                "endpoints": [endpoint_record(item, instances) for item in members],
            }
        )

    components: list[dict[str, object]] = []
    for instance in sorted(instances.values(), key=lambda item: int(item.model_index)):
        kind = component_kind(instance.module_id)
        if kind not in {"resistor", "capacitor", "logic_ic", "wire"}:
            continue
        endpoint_ids = sorted(part_endpoint_ids(instance, files))
        components.append(
            {
                "model_index": instance.model_index,
                "title": instance.title,
                "module_id": instance.module_id,
                "kind": kind,
                "value": value_for(instance),
                "color": wire_color(instance),
                "pins": [
                    {
                        "connector": connector_id,
                        "net_id": net_by_endpoint[(instance.model_index, connector_id)],
                        "direct_connection_count": sum(
                            1
                            for pair in links
                            if (instance.model_index, connector_id) in pair
                        ),
                    }
                    for connector_id in endpoint_ids
                ],
            }
        )

    collisions: list[dict[str, object]] = []
    for instance in instances.values():
        if component_kind(instance.module_id) != "breadboard":
            continue
        for connector in connector_elements(instance):
            targets = connector.findall("./connects/connect")
            if len(targets) > 1:
                collisions.append(
                    {
                        "board": instance.title,
                        "connector": connector.get("connectorId", ""),
                        "targets": [
                            {
                                "model_index": target.get("modelIndex", ""),
                                "connector": target.get("connectorId", ""),
                            }
                            for target in targets
                        ],
                    }
                )

    nonreciprocal = [
        item
        for item in reciprocity
        if not item["left_to_right"] or not item["right_to_left"]
    ]
    dangling_passive_pins = [
        {
            "component": component["title"],
            "model_index": component["model_index"],
            "connector": pin["connector"],
            "net_id": pin["net_id"],
        }
        for component in components
        if component["kind"] in {"resistor", "capacitor"}
        for pin in component["pins"]
        if pin["direct_connection_count"] == 0
    ]

    result: dict[str, object] = {
        "schema_version": 1,
        "input": str(path.relative_to(ROOT.parents[1])),
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sketch_file": sketch_name,
        "instance_count": len(instances),
        "net_count": len(nets),
        "instances": [
            {
                "model_index": item.model_index,
                "title": item.title,
                "module_id": item.module_id,
                "kind": component_kind(item.module_id),
                "properties": item.properties,
            }
            for item in sorted(instances.values(), key=lambda item: int(item.model_index))
        ],
        "nets": nets,
        "components": components,
        "buses": buses,
        "direct_connections": reciprocity,
        "findings": {
            "nonreciprocal_connections": nonreciprocal,
            "occupied_hole_collisions": collisions,
            "dangling_passive_pins": dangling_passive_pins,
        },
    }
    return result, markdown(result)


def pin_map(component: dict[str, object]) -> str:
    pins = component["pins"]
    assert isinstance(pins, list)
    return ", ".join(f"{pin['connector']}={pin['net_id']}" for pin in pins)


def markdown(result: dict[str, object]) -> str:
    findings = result["findings"]
    assert isinstance(findings, dict)
    lines = [
        "# AUDIT-002 extracted Fritzing connectivity",
        "",
        f"- Input: `{result['input']}`",
        f"- SHA-256: `{result['input_sha256']}`",
        f"- Instances: {result['instance_count']}",
        f"- Conductive nets: {result['net_count']}",
        "",
        "## Components",
        "",
        "| Component | Kind | Value/color | Endpoint nets |",
        "|---|---|---|---|",
    ]
    for component in result["components"]:
        assert isinstance(component, dict)
        value = component["value"] or component["color"] or "--"
        lines.append(
            f"| `{component['title']}` | {component['kind']} | `{value}` | {pin_map(component)} |"
        )

    lines.extend(["", "## Structural findings", ""])
    lines.append(
        f"1. Nonreciprocal direct connections: {len(findings['nonreciprocal_connections'])}."
    )
    lines.append(
        f"2. Multiply occupied breadboard holes: {len(findings['occupied_hole_collisions'])}."
    )
    dangling = findings["dangling_passive_pins"]
    lines.append(f"3. Passive pins with no direct placement/connection: {len(dangling)}.")
    for item in dangling:
        lines.append(
            f"   - `{item['component']}.{item['connector']}` on `{item['net_id']}`."
        )
    lines.extend(
        [
            "",
            "The extracted net IDs are deterministic within this exact input. They are audit",
            "labels, not design net names and not stable interface identifiers.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(result: dict[str, object], report: str) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    MARKDOWN_OUTPUT.write_text(report)


def expected_outputs(result: dict[str, object], report: str) -> dict[Path, bytes]:
    return {
        JSON_OUTPUT: (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        MARKDOWN_OUTPUT: report.encode(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = build(args.input.resolve())
    outputs = expected_outputs(result, report)
    if args.check:
        stale = [str(path) for path, data in outputs.items() if not path.exists() or path.read_bytes() != data]
        if stale:
            raise SystemExit("stale generated output: " + ", ".join(stale))
        return
    write_outputs(result, report)


if __name__ == "__main__":
    main()
