#!/usr/bin/env python3
"""Shared deterministic model and validators for QUAL-001.

This file exists so every generator, renderer, check, and test applies one set
of ordering and semantic rules. Keep policy here synchronized with the reviewed
schema and docs/qualification/README.md.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
QUALIFICATION = ROOT / "docs" / "qualification"
REVIEWED = QUALIFICATION / "reviewed"
GENERATED = QUALIFICATION / "generated"
SCHEMA = QUALIFICATION / "schema" / "compatibility-matrix.schema.json"
VDU_INVENTORY = ROOT / "docs" / "tasks" / "SETUP-004" / "VDU-inventory.md"
DEPENDENCY_GRAPH = ROOT / "docs" / "dependencies" / "generated" / "code-graph.yaml"

COLLECTION_FILES = {
    "sources": "sources.yaml",
    "modes": "modes.yaml",
    "interfaces": "interfaces.yaml",
    "capabilities": "capabilities.yaml",
    "qualification_domains": "qualification-domains.yaml",
    "mode_expectations": "mode-expectations.yaml",
    "obligations": "obligations.yaml",
    "evidence": "evidence.yaml",
    "evidence_links": "evidence-links.yaml",
}

SECTION_RULES = {
    "Base VDU commands": ("base-vdu", None),
    "Direct VDU 23 commands": ("direct-vdu-23", "interface:agon-vdp:vdu-23"),
    "System commands — VDU 23, 0": ("system", "interface:agon-vdp:vdu-23"),
    "Mouse commands — VDU 23, 0, &89": ("mouse", "interface:agon-vdp:vdu-23-0-x89"),
    "Audio commands — VDU 23, 0, &85": ("audio", "interface:agon-vdp:vdu-23-0-x85"),
    "Bitmap and sprite commands — VDU 23, 27": ("bitmap-sprite", "interface:agon-vdp:vdu-23-27"),
    "Font commands — VDU 23, 0, &95": ("font", "interface:agon-vdp:vdu-23-0-x95"),
    "Context commands — VDU 23, 0, &C8": ("context", "interface:agon-vdp:vdu-23-0-xc8"),
    "Copper commands — VDU 23, 0, &C4": ("copper", "interface:agon-vdp:vdu-23-0-xc4"),
    "Tile commands — VDU 23, 0, &C2": ("tile", "interface:agon-vdp:vdu-23-0-xc2"),
    "Buffered commands — VDU 23, 0, &A0, bufferId;": ("buffered", "interface:agon-vdp:vdu-23-0-xa0"),
    "PLOT families — VDU 25, mode, x; y;": ("plot", "interface:agon-vdp:vdu-25"),
}

SYMBOL_DISPOSITIONS = {
    "✅": "supported",
    "🟡": "accepted-noop",
    "🔀": "mode-dependent",
    "⛔": "unsupported",
    "❓": "unresolved",
}

SUPERSEDED_MATRIX_NOTICE = """# SUPERSEDED REVIEW GATE 2 CANDIDATE DATA.
# The embedded three-mode cross product is not current architecture or command-
# scope authority. See ADR-0014, SETUP-005, SETUP-004/VDU-inventory.md, and
# QUAL-001-RG2-02R.
"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(data: Any) -> str:
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=1000,
    )


def dump_generated_matrix_yaml(data: Any) -> str:
    """Serialize the retained candidate matrix with its mandatory warning."""

    return SUPERSEDED_MATRIX_NOTICE + dump_yaml(data)


def _slug(value: str) -> str:
    value = value.lower().replace("&", "x")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def _atom(value: str) -> str | None:
    value = value.strip().rstrip(";")
    if re.fullmatch(r"\d+", value):
        return value
    if re.fullmatch(r"&[0-9A-Fa-f]+", value):
        return "x" + value[1:].lower()
    if re.fullmatch(r"\d+[–-]\d+", value):
        return value.replace("–", "-")
    if re.fullmatch(r"&[0-9A-Fa-f]+[–-]&[0-9A-Fa-f]+", value):
        left, right = re.split(r"[–-]", value)
        return f"x{left[1:].lower()}-x{right[1:].lower()}"
    return None


def _candidate_interface_id(selector: str, category: str, parent_id: str | None) -> str:
    if selector.startswith("bytes "):
        atoms = re.findall(r"\d+(?:[–-]\d+)?", selector)
        return "interface:agon-vdp:character-data-" + "-".join(a.replace("–", "-") for a in atoms)

    if selector.startswith("VDU "):
        tokens = [item.strip() for item in selector.split(",")]
        first = re.fullmatch(r"VDU\s+(\d+)", tokens[0])
        if not first:
            raise ValueError(f"cannot derive VDU identity from {selector!r}")
        atoms = ["vdu", first.group(1)]
        for token in tokens[1:]:
            parsed = _atom(token)
            if parsed is None:
                break
            atoms.append(parsed)
        return "interface:agon-vdp:" + "-".join(atoms)

    if category == "plot":
        atoms = [_atom(item) for item in re.findall(r"&[0-9A-Fa-f]+[–-]&[0-9A-Fa-f]+", selector)]
        return "interface:agon-vdp:vdu-25-mode-" + "-".join(item for item in atoms if item)

    if selector.startswith("..., ") and parent_id:
        tokens = [item.strip() for item in selector[5:].split(",")]
        command_atom = next((_atom(token) for token in tokens if _atom(token) is not None), None)
        if command_atom is None:
            raise ValueError(f"cannot derive child identity from {selector!r}")
        return parent_id + "-" + command_atom

    raise ValueError(f"cannot derive interface identity from {selector!r}")


def parse_vdu_inventory(path: Path = VDU_INVENTORY) -> list[dict[str, Any]]:
    """Import every marked inventory line without interpreting its prose."""

    records: list[dict[str, Any]] = []
    category_order: dict[str, int] = defaultdict(int)
    section: str | None = None
    line_pattern = re.compile(r"^- (✅|🟡|🔀|⛔|❓) `([^`]+)` — (.+)$")

    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if raw.startswith("## "):
            section = raw[3:]
            continue
        match = line_pattern.match(raw)
        if not match:
            continue
        if section not in SECTION_RULES:
            raise ValueError(f"line {line_number}: marked entry under unknown section {section!r}")
        symbol, selector, title = match.groups()
        if title.endswith("."):
            title = title[:-1]
        category, parent_id = SECTION_RULES[section]
        record = {
            "id": _candidate_interface_id(selector, category, parent_id),
            "selector": selector,
            "title": title,
            "category": category,
            "display_order": category_order[category],
            "disposition": SYMBOL_DISPOSITIONS[symbol],
        }
        category_order[category] += 1
        if parent_id:
            record["parent_interface_id"] = parent_id
        record["source_refs"] = ["source:setup-004:vdu-inventory"]
        records.append(record)

    candidate_counts = Counter(record["id"] for record in records)
    for record in records:
        if candidate_counts[record["id"]] > 1:
            record["id"] += "-" + _slug(record["title"])

    ids = {record["id"] for record in records}
    for record in records:
        parent = record.get("parent_interface_id")
        if parent and parent not in ids:
            raise ValueError(f"{record['id']}: parent {parent} is absent from imported inventory")
    if len(records) != 211:
        raise ValueError(f"expected 211 accepted inventory entries, imported {len(records)}")
    if len(ids) != len(records):
        duplicates = [item for item, count in Counter(record["id"] for record in records).items() if count > 1]
        raise ValueError(f"duplicate imported interface IDs: {duplicates}")
    return records


def load_reviewed(reviewed: Path = REVIEWED) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    collections: dict[str, list[dict[str, Any]]] = {}
    digests: dict[str, str] = {}
    for collection, filename in COLLECTION_FILES.items():
        path = reviewed / filename
        raw = path.read_bytes()
        document = yaml.safe_load(raw)
        expected_kind = "qualification_" + collection
        if set(document) != {"schema_version", "artifact_kind", collection}:
            raise ValueError(f"{path}: expected only schema_version, artifact_kind, and {collection}")
        if document["schema_version"] != "1.0.0" or document["artifact_kind"] != expected_kind:
            raise ValueError(f"{path}: unexpected schema or artifact identity")
        if not isinstance(document[collection], list):
            raise ValueError(f"{path}: {collection} must be a list")
        collections[collection] = document[collection]
        digests[f"reviewed/{filename}"] = sha256_bytes(raw)
    return collections, dict(sorted(digests.items()))


def build_matrix(reviewed: Path = REVIEWED) -> dict[str, Any]:
    collections, digests = load_reviewed(reviewed)
    matrix: dict[str, Any] = {
        "schema_version": "1.0.0",
        "artifact_kind": "compatibility_qualification_matrix",
        "id": "matrix:extender:compatibility",
        "generated": {
            "generator": "docs/qualification/scripts/build-compatibility-matrix.py",
            "input_sha256": digests,
        },
    }
    for name in COLLECTION_FILES:
        matrix[name] = sorted(collections[name], key=lambda record: record["id"])
    return matrix


def _known_record_ids(matrix: dict[str, Any]) -> dict[str, set[str]]:
    return {name: {record["id"] for record in matrix[name]} for name in COLLECTION_FILES}


def _repository_reference_exists(reference: str) -> bool:
    task_stems = {path.stem for path in (ROOT / "docs" / "tasks").glob("*.md")}
    decision_stems = {path.name.split("-", 2)[0] + "-" + path.name.split("-", 2)[1] for path in (ROOT / "docs" / "decisions").glob("ADR-*.md")}
    return any(reference == stem or reference.startswith(stem + "-") for stem in task_stems | decision_stems)


def _dependency_ids() -> set[str]:
    ids: set[str] = set()
    if not DEPENDENCY_GRAPH.exists():
        return ids
    pattern = re.compile(r"^- id: (\S+)$")
    with DEPENDENCY_GRAPH.open(encoding="utf-8") as stream:
        for line in stream:
            match = pattern.match(line.rstrip("\n"))
            if match:
                ids.add(match.group(1))
    return ids


def _all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _all_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_strings(child)


def validate_matrix(matrix: dict[str, Any], *, verify_inventory: bool = True) -> list[str]:
    errors: list[str] = []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    for error in sorted(Draft202012Validator(schema).iter_errors(matrix), key=lambda item: list(item.path)):
        location = ".".join(str(item) for item in error.path) or "<root>"
        errors.append(f"schema {location}: {error.message}")
    if errors:
        return errors

    ids_by_collection = _known_record_ids(matrix)
    all_ids = [record["id"] for name in COLLECTION_FILES for record in matrix[name]]
    for item, count in Counter(all_ids).items():
        if count > 1:
            errors.append(f"duplicate global ID: {item}")

    interface_ids = ids_by_collection["interfaces"]
    mode_ids = ids_by_collection["modes"]
    source_ids = ids_by_collection["sources"]
    subject_ids = {
        "interface": interface_ids,
        "capability": ids_by_collection["capabilities"],
        "domain": ids_by_collection["qualification_domains"],
    }

    tuples = [(item["interface_id"], item["mode_id"]) for item in matrix["mode_expectations"]]
    for item, count in Counter(tuples).items():
        if count > 1:
            errors.append(f"duplicate mode expectation tuple: {item}")
    expected_tuples = {(interface, mode) for interface in interface_ids for mode in mode_ids}
    missing_tuples = expected_tuples - set(tuples)
    extra_tuples = set(tuples) - expected_tuples
    if missing_tuples:
        errors.append(f"missing {len(missing_tuples)} interface/mode expectations")
    if extra_tuples:
        errors.append(f"invalid interface/mode expectations: {sorted(extra_tuples)}")

    for interface in matrix["interfaces"]:
        parent = interface.get("parent_interface_id")
        if parent and parent not in interface_ids:
            errors.append(f"{interface['id']}: dangling parent {parent}")
        for source in interface["source_refs"]:
            if source not in source_ids:
                errors.append(f"{interface['id']}: dangling source {source}")
    display_tuples = [(item["category"], item["display_order"]) for item in matrix["interfaces"]]
    for item, count in Counter(display_tuples).items():
        if count > 1:
            errors.append(f"duplicate interface display tuple: {item}")

    for collection in ("capabilities", "qualification_domains"):
        for record in matrix[collection]:
            for source in record["source_refs"]:
                if source not in source_ids:
                    errors.append(f"{record['id']}: dangling source {source}")

    for expectation in matrix["mode_expectations"]:
        if expectation["interface_id"] not in interface_ids:
            errors.append(f"{expectation['id']}: dangling interface")
        if expectation["mode_id"] not in mode_ids:
            errors.append(f"{expectation['id']}: dangling mode")
        if expectation["expectation"] == "unresolved" and not expectation["blocker_refs"]:
            errors.append(f"{expectation['id']}: unresolved expectation requires blocker_refs")

    dependency_ids = _dependency_ids()
    obligations = {record["id"]: record for record in matrix["obligations"]}
    for obligation in matrix["obligations"]:
        kind = obligation["subject_kind"]
        if obligation["subject_id"] not in subject_ids[kind]:
            errors.append(f"{obligation['id']}: dangling {kind} subject {obligation['subject_id']}")
        secondary = obligation["scope"] == "secondary-capability"
        if secondary != (kind == "capability"):
            errors.append(f"{obligation['id']}: scope and subject_kind disagree")
        if any(mode not in mode_ids for mode in obligation["mode_ids"]):
            errors.append(f"{obligation['id']}: dangling mode reference")
        if obligation["qualification_state"] == "blocked" and not obligation["blocker_refs"]:
            errors.append(f"{obligation['id']}: blocked state requires blocker_refs")
        if obligation["qualification_state"] == "qualified" and not obligation.get("qualification_basis"):
            errors.append(f"{obligation['id']}: qualified state requires qualification_basis")
        for source in obligation["source_refs"]:
            if source not in source_ids:
                errors.append(f"{obligation['id']}: dangling source {source}")
        for node in obligation["dependency_node_ids"]:
            if node not in dependency_ids:
                errors.append(f"{obligation['id']}: dangling dependency node {node}")
        for reference in obligation["owner_task_ids"] + obligation["requirement_refs"] + obligation["blocker_refs"]:
            if not _repository_reference_exists(reference):
                errors.append(f"{obligation['id']}: dangling repository reference {reference}")

    evidence = {record["id"]: record for record in matrix["evidence"]}
    link_tuples: list[tuple[str, str]] = []
    links_by_obligation: dict[str, list[dict[str, Any]]] = {}
    for link in matrix["evidence_links"]:
        link_tuples.append((link["obligation_id"], link["evidence_id"]))
        if link["obligation_id"] not in obligations:
            errors.append(f"{link['id']}: dangling obligation")
            continue
        if link["evidence_id"] not in evidence:
            errors.append(f"{link['id']}: dangling evidence")
            continue
        links_by_obligation.setdefault(link["obligation_id"], []).append(link)
        if obligations[link["obligation_id"]]["scope"] != evidence[link["evidence_id"]]["scope"]:
            errors.append(f"{link['id']}: evidence scope cannot satisfy obligation scope")
    for item, count in Counter(link_tuples).items():
        if count > 1:
            errors.append(f"duplicate obligation/evidence tuple: {item}")
    for obligation in matrix["obligations"]:
        if obligation["qualification_state"] != "qualified":
            continue
        supporting = [
            link for link in links_by_obligation.get(obligation["id"], [])
            if link["relationship"] == "supports"
            and evidence[link["evidence_id"]]["lifecycle"] == "accepted"
        ]
        if not supporting:
            errors.append(f"{obligation['id']}: qualified state lacks accepted supporting evidence")

    for source in matrix["sources"]:
        reference = source["ref"]
        if "://" not in reference and not (ROOT / reference).exists():
            errors.append(f"{source['id']}: missing repository path {reference}")

    sensitive = re.compile(r"(?:/home/|/Users/|\b(?:\d{1,3}\.){3}\d{1,3}\b|BEGIN [A-Z ]*PRIVATE KEY|password\s*[:=])", re.I)
    for value in _all_strings(matrix):
        if sensitive.search(value):
            errors.append("matrix contains a machine-local path, network address, or credential-like value")
            break

    if verify_inventory:
        imported = parse_vdu_inventory()
        if matrix["interfaces"] != sorted(imported, key=lambda record: record["id"]):
            errors.append("reviewed interfaces differ from the exact accepted SETUP-004 VDU inventory import")
    return errors
