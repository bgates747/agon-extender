#!/usr/bin/env python3
"""Validate the durable hardware object authority.

JSON Schema owns record shape. This validator owns collection-wide invariants:
deterministic order, canonical-name uniqueness, alias hygiene, containment
references and cycles, and links to the versioned artifact registry.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
OBJECTS_PATH = REPOSITORY_ROOT / "hardware/objects/objects.yaml"
SCHEMA_PATH = REPOSITORY_ROOT / "hardware/objects/schema.json"
ARTIFACTS_PATH = REPOSITORY_ROOT / "docs/versions/artifacts.yaml"


def fail(message: str) -> None:
    raise ValueError(message)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        fail(f"{path.relative_to(REPOSITORY_ROOT)}: root must be a mapping")
    return value


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        fail("hardware/objects/schema.json: root must be an object")
    Draft202012Validator.check_schema(value)
    return value


def format_schema_path(error: Any) -> str:
    path = "hardware/objects/objects.yaml"
    if error.absolute_path:
        path += ":" + "".join(f"[{part!r}]" for part in error.absolute_path)
    return path


def validate_schema(record: dict[str, Any], schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(record),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        fail(f"{format_schema_path(error)}: {error.message}")


def validate_unique_and_ordered(objects: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    object_ids = [item["object_id"] for item in objects]
    if object_ids != sorted(object_ids):
        for index, (actual, expected) in enumerate(zip(object_ids, sorted(object_ids))):
            if actual != expected:
                fail(
                    "hardware/objects/objects.yaml: objects must be sorted by "
                    f"object_id; index {index} has {actual!r}, expected {expected!r}"
                )

    by_id: dict[str, dict[str, Any]] = {}
    labels: dict[str, str] = {}
    for item in objects:
        object_id = item["object_id"]
        if object_id in by_id:
            fail(f"hardware/objects/objects.yaml: duplicate object_id {object_id!r}")
        by_id[object_id] = item

        folded_label = item["label"].casefold()
        if folded_label in labels:
            fail(
                "hardware/objects/objects.yaml: duplicate label "
                f"{item['label']!r} on {labels[folded_label]!r} and {object_id!r}"
            )
        labels[folded_label] = object_id

        seen_aliases: set[str] = set()
        for alias in item["aliases"]:
            folded_alias = alias.casefold()
            if folded_alias in seen_aliases:
                fail(
                    f"hardware/objects/objects.yaml: {object_id!r} has "
                    f"case-insensitive duplicate alias {alias!r}"
                )
            if folded_alias in {object_id.casefold(), folded_label}:
                fail(
                    f"hardware/objects/objects.yaml: {object_id!r} alias "
                    f"{alias!r} duplicates its canonical identity or label"
                )
            seen_aliases.add(folded_alias)
    return by_id


def validate_containment(by_id: dict[str, dict[str, Any]]) -> None:
    for object_id, item in by_id.items():
        parent = item["parent_object_id"]
        if parent is None:
            continue
        if parent == object_id:
            fail(f"hardware/objects/objects.yaml: {object_id!r} contains itself")
        if parent not in by_id:
            fail(
                f"hardware/objects/objects.yaml: {object_id!r} references "
                f"unknown parent_object_id {parent!r}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(object_id: str, path: list[str]) -> None:
        if object_id in visiting:
            cycle_start = path.index(object_id)
            cycle = path[cycle_start:] + [object_id]
            fail(
                "hardware/objects/objects.yaml: containment cycle: "
                + " -> ".join(cycle)
            )
        if object_id in visited:
            return
        visiting.add(object_id)
        parent = by_id[object_id]["parent_object_id"]
        if parent is not None:
            visit(parent, path + [object_id])
        visiting.remove(object_id)
        visited.add(object_id)

    for object_id in by_id:
        visit(object_id, [])


def validate_artifact_references(objects: list[dict[str, Any]]) -> None:
    registry = load_yaml(ARTIFACTS_PATH)
    artifact_records = registry.get("artifacts")
    if not isinstance(artifact_records, list):
        fail("docs/versions/artifacts.yaml: artifacts must be a list")
    artifact_ids = {
        item.get("artifact_id")
        for item in artifact_records
        if isinstance(item, dict) and isinstance(item.get("artifact_id"), str)
    }

    for item in objects:
        object_id = item["object_id"]
        references = item["related_artifact_ids"]
        if references != sorted(references):
            fail(
                f"hardware/objects/objects.yaml: {object_id!r} "
                "related_artifact_ids must be sorted"
            )
        for artifact_id in references:
            if artifact_id not in artifact_ids:
                fail(
                    f"hardware/objects/objects.yaml: {object_id!r} references "
                    f"unknown artifact_id {artifact_id!r}"
                )


def validate_authority_identity(record: dict[str, Any]) -> None:
    registry = load_yaml(ARTIFACTS_PATH)
    artifact_records = registry.get("artifacts")
    if not isinstance(artifact_records, list):
        fail("docs/versions/artifacts.yaml: artifacts must be a list")

    artifact_id = record["artifact_id"]
    matches = [
        item
        for item in artifact_records
        if isinstance(item, dict) and item.get("artifact_id") == artifact_id
    ]
    if len(matches) != 1:
        fail(
            "docs/versions/artifacts.yaml: expected exactly one record for "
            f"{artifact_id!r}, found {len(matches)}"
        )
    artifact = matches[0]
    if artifact.get("identity_scheme") != "revision":
        fail(
            f"docs/versions/artifacts.yaml: {artifact_id!r} must use the "
            "revision identity scheme"
        )
    if artifact.get("latest_identity") != record["identity"]:
        fail(
            f"hardware/objects/objects.yaml: identity {record['identity']!r} "
            "does not match the artifact registry latest_identity"
        )
    if artifact.get("status") != record["status"]:
        fail(
            f"hardware/objects/objects.yaml: status {record['status']!r} "
            "does not match the artifact registry status"
        )


def main() -> int:
    try:
        record = load_yaml(OBJECTS_PATH)
        schema = load_schema()
        validate_schema(record, schema)
        objects = record["objects"]
        validate_authority_identity(record)
        by_id = validate_unique_and_ordered(objects)
        validate_containment(by_id)
        validate_artifact_references(objects)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ValueError) as error:
        print(f"hardware-object validation failed: {error}", file=sys.stderr)
        return 1
    print(f"hardware-object validation passed ({len(objects)} objects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
