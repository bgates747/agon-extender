#!/usr/bin/env python3
"""Check the maintained r03 drawing against its model and export review views.

Adapted from r02's export/check workflow. This draft reuses the existing
electrical-model schema validator; it does not generate schematic geometry.
Header units use actual physical pin numbers, without r02's JO1/JE1 remapping.
Export dates are normalized to the drawing date, not presented as test times.
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
SCHEMATIC = ROOT / "schematic.kicad_sch"
VALIDATOR = REPOSITORY / "docs/tasks/HW-001/electrical-model/validate.py"
OUTPUTS = ("schematic.xml", "schematic.svg", "schematic.pdf")


def load_model() -> dict:
    spec = importlib.util.spec_from_file_location("electrical_model", VALIDATOR)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load model validator: {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(ROOT / "connectivity.yaml")


def check_netlist(model: dict, path: Path) -> None:
    root = ET.parse(path).getroot()
    expected_values = {c["ref"]: c["value"] for c in model["components"]}
    parts = root.findall("./components/comp")
    actual_values = {c.get("ref"): c.findtext("value") for c in parts}
    if actual_values != expected_values or len(parts) != len(expected_values):
        raise ValueError("KiCad component references/values differ from the model")
    expected_nets = Counter(
        frozenset((p["component"], p["pin"]) for p in net["members"])
        for net in model["nets"]
    )
    expected_nc = frozenset(
        (p["component"], p["pin"]) for p in model["unconnected"]
    )
    actual_nets = Counter()
    actual_nc = set()
    for net in root.findall("./nets/net"):
        members = frozenset((p.get("ref"), p.get("pin")) for p in net.findall("node"))
        if net.get("name", "").startswith("unconnected-(") and len(members) == 1:
            actual_nc.update(members)
        else:
            actual_nets[members] += 1
    if actual_nets != expected_nets:
        raise ValueError("KiCad connected-net endpoint partition differs from the model")
    if actual_nc != expected_nc:
        raise ValueError("KiCad intentional no-connect partition differs from the model")


def normalize_exports(directory: Path) -> None:
    xml_path = directory / OUTPUTS[0]
    xml = xml_path.read_text()
    xml, sources = re.subn(
        r"(<design>\s*<source>)[^<]+(</source>)",
        rf"\g<1>{SCHEMATIC.relative_to(REPOSITORY).as_posix()}\g<2>",
        xml, count=1,
    )
    xml, dates = re.subn(
        r"<date>[^<]+</date>", "<date>Mon Sep 7 00:00:00 2026</date>", xml, count=1,
    )
    if (sources, dates) != (1, 1):
        raise ValueError("unexpected KiCad XML metadata")
    # Project-library provenance must not disclose a machine-local checkout.
    xml = xml.replace(str(REPOSITORY) + "/", "")
    xml_path.write_text(xml)

    svg_path = directory / OUTPUTS[1]
    svg, titles = re.subn(
        r"(<title>SVG Image created as [^<]+ date )[^<]+(</title>)",
        r"\g<1>2026/09/07 00:00:00 \g<2>", svg_path.read_text(), count=1,
    )
    desc = re.search(r"<desc>.*?</desc>\s*", svg, re.DOTALL)
    if titles != 1 or desc is None:
        raise ValueError("unexpected KiCad SVG metadata")
    background = (
        '<rect id="explicit-white-background" x="0" y="0" width="100%" '
        'height="100%" fill="#ffffff" stroke="none"/>\n'
    )
    svg = svg[:desc.end()] + background + svg[desc.end():]
    svg_path.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n")

    pdf_path = directory / OUTPUTS[2]
    pdf = pdf_path.read_bytes()
    # KiCad 7 writes a fixed-width creation-date field. Replace only its 14
    # digits, retaining every byte offset in the PDF cross-reference table.
    normalized, dates = re.subn(
        rb"/CreationDate \(D:\d{14}\)",
        b"/CreationDate (D:20260907000000)", pdf,
    )
    if dates != 1 or len(normalized) != len(pdf):
        raise ValueError("unexpected KiCad PDF creation-date format")
    pdf_path.write_bytes(normalized)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="refresh checked XML/SVG/PDF")
    args = parser.parse_args()
    try:
        model = load_model()
        with tempfile.TemporaryDirectory(prefix="light2-harness-r03-") as scratch:
            directory = Path(scratch)
            subprocess.run([
                "kicad-cli", "sch", "export", "netlist", "--format", "kicadxml",
                "-o", str(directory / OUTPUTS[0]), str(SCHEMATIC),
            ], check=True)
            check_netlist(model, directory / OUTPUTS[0])
            for kind in ("svg", "pdf"):
                target = directory if kind == "svg" else directory / OUTPUTS[2]
                subprocess.run([
                    "kicad-cli", "sch", "export", kind, "--exclude-drawing-sheet",
                    "--no-background-color", "-o", str(target), str(SCHEMATIC),
                ], check=True)
            normalize_exports(directory)
            for name in OUTPUTS:
                source, destination = directory / name, ROOT / name
                if args.write:
                    shutil.copyfile(source, destination)
                elif not destination.exists() or source.read_bytes() != destination.read_bytes():
                    raise ValueError(f"stale or missing export: {destination}")
    except (OSError, ValueError, ET.ParseError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: r03 values, topology, all no-connects, and XML/SVG/PDF exports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
