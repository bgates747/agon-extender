#!/usr/bin/env python3
"""Validate the r02 BOM and generate its Markdown and flat CSV views."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
DEFAULT_BOM = ROOT / "bom.yaml"
DEFAULT_MODEL = ROOT / "connectivity.yaml"
DEFAULT_MARKDOWN = ROOT / "BOM.md"
DEFAULT_CSV = ROOT / "bom.csv"


class BomError(ValueError):
    """The maintained BOM is inconsistent or differs from the frozen model."""


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if not isinstance(document, dict):
        raise BomError(f"{path}: expected a YAML mapping")
    return document


def validate(bom: dict, model: dict) -> None:
    """Require exact BOM coverage and source-field agreement."""

    if bom.get("schema_version") != 1:
        raise BomError("unsupported BOM schema_version")
    metadata = bom.get("bom", {})
    source_design = metadata.get("source_design", {})
    model_id = model.get("model", {}).get("model_id")
    if source_design.get("exact") != model_id:
        raise BomError(
            f"BOM selects {source_design.get('exact')!r}, model is {model_id!r}"
        )
    if metadata.get("build_quantity") != 1:
        raise BomError("design BOM must describe exactly one circuit build")

    components = {component["ref"]: component for component in model["components"]}
    fitted_refs = {
        ref for ref, component in components.items() if component["kind"] != "connector"
    }
    connector_refs = {
        ref for ref, component in components.items() if component["kind"] == "connector"
    }

    line_ids: set[str] = set()
    covered_refs: set[str] = set()
    for line in bom.get("line_items", []):
        line_id = line.get("line_id")
        if not isinstance(line_id, str) or not line_id:
            raise BomError("every BOM line requires a nonempty line_id")
        if line_id in line_ids:
            raise BomError(f"duplicate line_id: {line_id}")
        line_ids.add(line_id)

        refs = line.get("refs")
        if not isinstance(refs, list) or not refs:
            raise BomError(f"{line_id}: refs must be a nonempty list")
        if line.get("quantity") != len(refs):
            raise BomError(
                f"{line_id}: quantity {line.get('quantity')} differs from {len(refs)} refs"
            )
        if line.get("uom") != "each":
            raise BomError(f"{line_id}: only per-item quantities are supported")

        source_match = line.get("source_match", {})
        for ref in refs:
            if ref not in components:
                raise BomError(f"{line_id}: unknown component ref {ref}")
            if ref in covered_refs:
                raise BomError(f"component ref appears on multiple BOM lines: {ref}")
            if ref in connector_refs:
                raise BomError(f"{line_id}: connector {ref} belongs in supplied_equipment")
            component = components[ref]
            for field, expected in source_match.items():
                actual = component.get(field)
                if actual != expected:
                    raise BomError(
                        f"{line_id}/{ref}: {field} is {actual!r}, expected {expected!r}"
                    )
            if line.get("value") != component.get("value"):
                raise BomError(
                    f"{line_id}/{ref}: BOM value differs from connectivity value"
                )
            covered_refs.add(ref)

    if covered_refs != fitted_refs:
        raise BomError(
            f"fitted coverage mismatch: missing={sorted(fitted_refs - covered_refs)}, "
            f"extra={sorted(covered_refs - fitted_refs)}"
        )

    equipment_ids: set[str] = set()
    represented_refs: set[str] = set()
    for equipment in bom.get("supplied_equipment", []):
        equipment_id = equipment.get("equipment_id")
        if not isinstance(equipment_id, str) or not equipment_id:
            raise BomError("every supplied-equipment line requires an equipment_id")
        if equipment_id in equipment_ids:
            raise BomError(f"duplicate equipment_id: {equipment_id}")
        equipment_ids.add(equipment_id)
        refs = equipment.get("represented_by_refs", [])
        for ref in refs:
            if ref not in connector_refs:
                raise BomError(f"{equipment_id}: {ref} is not a model connector")
            if ref in represented_refs:
                raise BomError(f"connector appears on multiple equipment lines: {ref}")
            represented_refs.add(ref)
    if represented_refs != connector_refs:
        raise BomError(
            f"interface coverage mismatch: missing={sorted(connector_refs - represented_refs)}, "
            f"extra={sorted(represented_refs - connector_refs)}"
        )


def markdown_view(bom: dict) -> str:
    metadata = bom["bom"]
    source = metadata["source_design"]
    approval = metadata["approval"]
    lines = [
        "<!-- Generated by generate_bom.py from bom.yaml; do not edit. -->",
        "# Light 2 harness r02 bill of materials",
        "",
        f"This BOM describes one `{source['exact']}` circuit build. Its lifecycle "
        f"status is **{metadata['status']}**. Electrical connectivity and nominal "
        "values remain authoritative in `connectivity.yaml`; this document is a "
        "checked procurement projection.",
        "",
        f"The {approval['approved_by']} froze this BOM under "
        f"`{approval['decision']}` at `{approval['approved_at'].isoformat()}`.",
        "",
        "## Fitted circuit components",
        "",
        "| Line ID | Qty | References | Part or value | Package / procurement constraint | Role |",
        "|---|---:|---|---|---|---|",
    ]
    for item in bom["line_items"]:
        part = item.get("manufacturer_part_number") or item["value"]
        constraint = f"{item['package']}; {item['procurement_spec']}"
        lines.append(
            f"| `{item['line_id']}` | {item['quantity']} | "
            f"`{', '.join(item['refs'])}` | `{part}` | {constraint} | {item['role']} |"
        )

    lines.extend(
        [
            "",
            f"**Fitted total:** {sum(item['quantity'] for item in bom['line_items'])} "
            "discrete components across "
            f"{len(bom['line_items'])} procurement lines.",
            "",
            "## Supplied equipment and modeled interfaces",
            "",
            "| Qty | Equipment | Model references | Disposition |",
            "|---:|---|---|---|",
        ]
    )
    for item in bom["supplied_equipment"]:
        lines.append(
            f"| {item['quantity']} | {item['product_name']} | "
            f"`{', '.join(item['represented_by_refs'])}` | {item['disposition']} |"
        )

    lines.extend(["", "## Exclusions", ""])
    lines.extend(f"{index}. {item}." for index, item in enumerate(metadata["exclusions"], 1))
    lines.extend(
        [
            "",
            "These physical-assembly items remain outside this design BOM until the "
            "r02 breadboard construction authority fixes their exact form and quantity.",
            "",
            "## Machine-readable sources",
            "",
            "1. `bom.yaml` is the maintained procurement input.",
            "2. `bom.csv` is a flat generated import view suitable for inventory or ERP mapping.",
            "3. `connectivity.yaml` is the frozen electrical authority.",
            "",
        ]
    )
    return "\n".join(lines)


def csv_view(bom: dict) -> str:
    stream = io.StringIO(newline="")
    fields = [
        "line_id",
        "quantity",
        "uom",
        "category",
        "references",
        "product_name",
        "manufacturer",
        "manufacturer_part_number",
        "value",
        "package",
        "procurement_spec",
        "role",
    ]
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for item in bom["line_items"]:
        writer.writerow(
            {
                field: (
                    ";".join(item["refs"])
                    if field == "references"
                    else item.get(field)
                )
                for field in fields
            }
        )
    return stream.getvalue()


def check_or_write(path: Path, expected: str, write: bool) -> None:
    if write:
        path.write_text(expected, encoding="utf-8")
        print(f"PASS: wrote {path}")
        return
    if not path.exists():
        raise BomError(f"generated output missing: {path}")
    if path.read_text(encoding="utf-8") != expected:
        raise BomError(f"generated output is stale: {path}")
    print(f"PASS: checked {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bom", type=Path, default=DEFAULT_BOM)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write generated Markdown and CSV instead of checking them",
    )
    args = parser.parse_args()
    try:
        bom = load_yaml(args.bom)
        model = load_yaml(args.model)
        validate(bom, model)
        check_or_write(args.markdown, markdown_view(bom), args.write)
        check_or_write(args.csv, csv_view(bom), args.write)
    except (BomError, OSError, yaml.YAMLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    fitted = sum(item["quantity"] for item in bom["line_items"])
    print(
        f"PASS: BOM covers {fitted} fitted components and all modeled interfaces"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
