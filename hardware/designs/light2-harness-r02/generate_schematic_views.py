#!/usr/bin/env python3
"""Generate and validate the maintained r02 human schematic projections.

The hand-laid-out KiCad schematic is a human-readable projection. Electrical
connectivity remains authoritative in ``connectivity.yaml``. This script
exports the schematic through KiCad, proves its exact connected and intentional
no-connect endpoint partitions, and emits deterministic XML and explicit-white
SVG review artifacts.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[2]
MODEL = ROOT / "connectivity.yaml"
SCHEMATIC = ROOT / "schematic.kicad_sch"
XML_OUTPUT = ROOT / "schematic.xml"
SVG_OUTPUT = ROOT / "schematic.svg"
MODEL_VALIDATOR = REPOSITORY / "docs/tasks/HW-001/electrical-model/validate.py"
FIXED_XML_DATE = "Sat Aug 30 00:00:00 2026"
FIXED_SVG_DATE = "2026/08/30 00:00:00"
WHITE_BACKGROUND = (
    '  <rect id="explicit-white-background" x="0" y="0" width="100%" '
    'height="100%" fill="#ffffff" stroke="none"/>\n'
)


class SchematicError(ValueError):
    """The maintained schematic or one of its exports is invalid."""


def load_validator():
    spec = importlib.util.spec_from_file_location("hw001_r02_validator", MODEL_VALIDATOR)
    if spec is None or spec.loader is None:
        raise SchematicError(f"cannot load electrical-model validator: {MODEL_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def projected_endpoint(component: str, pin: str) -> tuple[str, str]:
    """Map physical Agon J1 pins onto the drawing's split odd/even headers."""

    if component != "J1":
        return component, pin
    number = int(pin)
    return (
        "JO1" if number % 2 else "JE1",
        str((number + 1) // 2 if number % 2 else number // 2),
    )


def expected_topology(model: dict) -> tuple[Counter, frozenset[tuple[str, str]]]:
    partitions = Counter(
        frozenset(
            projected_endpoint(member["component"], member["pin"])
            for member in net["members"]
        )
        for net in model["nets"]
    )
    unconnected = frozenset(
        projected_endpoint(item["component"], item["pin"])
        for item in model["unconnected"]
    )
    return partitions, unconnected


def validate_net_label_presentation(model: dict) -> None:
    """Require labels only for power nets and keep them horizontal.

    Signal and control nets are literal wires.  Only ground and the two 3.3 V
    domains use labels.  KiCad may rotate labels along with moved symbols, so
    this presentation check complements electrical topology validation.
    """

    text = SCHEMATIC.read_text(encoding="utf-8")
    labels = re.findall(
        r'^\s*\(global_label\s+"([^"]+)"[^\n]*'
        r'\(at\s+-?[0-9.]+\s+-?[0-9.]+\s+(0|90|180|270)\)',
        text,
        re.MULTILINE,
    )
    power_nets = {"ground", "agon-3v3", "p4-3v3"}
    expected_count = sum(
        len(net["members"]) for net in model["nets"] if net["net_id"] in power_nets
    )
    if len(labels) != expected_count:
        raise SchematicError(
            f"canonical schematic has {len(labels)} endpoint labels; "
            f"expected {expected_count} power/ground labels"
        )
    unexpected = sorted({name for name, _ in labels} - power_nets)
    if unexpected:
        raise SchematicError(
            f"canonical schematic retains non-power net labels: {unexpected}"
        )
    vertical = sum(angle in {"90", "270"} for _, angle in labels)
    if vertical:
        raise SchematicError(
            f"canonical schematic has {vertical} vertically rotated net labels"
        )


def exported_topology(path: Path) -> tuple[Counter, frozenset[tuple[str, str]]]:
    root = ET.parse(path).getroot()
    partitions = Counter()
    unconnected = set()
    for net in root.findall(".//nets/net"):
        members = frozenset(
            (node.attrib["ref"], node.attrib["pin"])
            for node in net.findall("node")
        )
        name = net.attrib.get("name", "")
        if name.startswith("unconnected-(") and len(members) == 1:
            unconnected.update(members)
        else:
            partitions[members] += 1
    return partitions, frozenset(unconnected)


def compare_topology(model: dict, path: Path) -> None:
    expected_partitions, expected_unconnected = expected_topology(model)
    actual_partitions, actual_unconnected = exported_topology(path)
    if actual_partitions != expected_partitions:
        raise SchematicError("KiCad connected-net endpoint partition differs from r02")
    if actual_unconnected != expected_unconnected:
        raise SchematicError("KiCad intentional no-connect partition differs from r02")


def normalize_xml(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    source = SCHEMATIC.relative_to(REPOSITORY).as_posix()
    text, source_count = re.subn(
        r"(<design>\s*<source>)[^<]+(</source>)",
        rf"\g<1>{source}\g<2>",
        text,
        count=1,
    )
    text, date_count = re.subn(
        r"<date>[^<]+</date>",
        f"<date>{FIXED_XML_DATE}</date>",
        text,
        count=1,
    )
    if source_count != 1 or date_count != 1:
        raise SchematicError("KiCad XML export lacks its unique source or date field")
    path.write_text(text, encoding="utf-8")


def normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text, title_count = re.subn(
        r"(<title>SVG Image created as [^<]+ date )[^<]+(</title>)",
        rf"\g<1>{FIXED_SVG_DATE} \g<2>",
        text,
        count=1,
    )
    if title_count != 1:
        raise SchematicError("KiCad SVG export lacks its unique dated title")
    if 'id="explicit-white-background"' not in text:
        desc = re.search(r"(<desc>.*?</desc>\s*)", text, re.DOTALL)
        if desc is None:
            raise SchematicError("KiCad SVG export lacks a background insertion point")
        text = text[: desc.end()] + WHITE_BACKGROUND + text[desc.end() :]
    # KiCad 7 emits line-ending spaces throughout SVG output. They carry no
    # rendering information and make repository whitespace checks unusable.
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(text, encoding="utf-8")


def export_views(directory: Path) -> tuple[Path, Path]:
    xml_path = directory / "schematic.xml"
    svg_path = directory / "schematic.svg"
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
            str(SCHEMATIC),
        ],
        check=True,
    )
    subprocess.run(
        [
            "kicad-cli",
            "sch",
            "export",
            "svg",
            "--no-background-color",
            "-o",
            str(directory),
            str(SCHEMATIC),
        ],
        check=True,
    )
    normalize_xml(xml_path)
    normalize_svg(svg_path)
    return xml_path, svg_path


def require_current(expected: Path, actual: Path) -> None:
    if not expected.exists() or expected.read_bytes() != actual.read_bytes():
        raise SchematicError(f"stale or missing generated view: {expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="replace the checked XML and SVG projections after validation",
    )
    args = parser.parse_args()
    try:
        model = load_validator().validate(MODEL)
        validate_net_label_presentation(model)
        with tempfile.TemporaryDirectory(prefix="light2-harness-r02-schematic-") as scratch:
            xml_path, svg_path = export_views(Path(scratch))
            compare_topology(model, xml_path)
            if args.write:
                shutil.copyfile(xml_path, XML_OUTPUT)
                shutil.copyfile(svg_path, SVG_OUTPUT)
            else:
                require_current(XML_OUTPUT, xml_path)
                require_current(SVG_OUTPUT, svg_path)
    except (
        OSError,
        ET.ParseError,
        SchematicError,
        subprocess.CalledProcessError,
        ValueError,
    ) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    action = "generated and validated" if args.write else "validated"
    print(f"PASS: {action} r02 schematic XML and explicit-white SVG")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
