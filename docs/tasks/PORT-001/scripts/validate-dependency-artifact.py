#!/usr/bin/env python3
"""Validate PORT-001 dependency artifacts beyond their JSON Schema contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from dependency_model import (
    DependencyArtifactError,
    canonical_yaml,
    hash_paths,
    load_data,
    sha256_file,
    sha256_span,
)


def parse_mapping(value: str) -> tuple[str, Path]:
    try:
        key, raw_path = value.split("=", 1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected ID=PATH") from error
    return key, Path(raw_path).resolve()


def duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def check_sorted(records: list[dict[str, Any]], key: str, label: str) -> None:
    values = [record[key] for record in records]
    if values != sorted(values):
        raise DependencyArtifactError(f"{label} is not sorted by {key}")


def validate_references(
    data: dict[str, Any],
    base_graph: dict[str, Any] | None,
    source_roots: dict[str, Path],
    check_canonical: bool,
    verify_files: bool,
    original_text: str,
) -> None:
    kind = data["artifact_kind"]
    collections = [key for key in ("sources", "inputs", "tools", "evidence", "nodes", "edges", "unresolved") if key in data]
    for key in collections:
        ids = [record["id"] for record in data[key]]
        duplicates = duplicate_values(ids)
        if duplicates:
            raise DependencyArtifactError(f"duplicate {key} IDs: {', '.join(duplicates)}")
        check_sorted(data[key], "id", key)

    all_ids: list[str] = []
    for key in collections:
        all_ids.extend(record["id"] for record in data[key])
    duplicate_global_ids = duplicate_values(all_ids)
    if duplicate_global_ids:
        raise DependencyArtifactError(
            "IDs reused across collections: " + ", ".join(duplicate_global_ids)
        )

    base_nodes = {node["id"] for node in (base_graph or {}).get("nodes", [])}
    base_edges = {edge["id"] for edge in (base_graph or {}).get("edges", [])}
    local_nodes = {node["id"] for node in data.get("nodes", [])}
    local_edges = {edge["id"] for edge in data.get("edges", [])}
    available_nodes = local_nodes | base_nodes
    available_edges = local_edges | base_edges
    evidence_ids = {record["id"] for record in data.get("evidence", [])}
    source_ids = {record["id"] for record in data.get("sources", [])}
    input_ids = {record["id"] for record in data.get("inputs", [])}

    if verify_files:
        for input_record in data.get("inputs", []):
            input_path = Path(input_record["path"])
            if not input_path.is_file():
                raise DependencyArtifactError(
                    f"{input_record['id']}: input artifact is missing: {input_record['path']}"
                )
            if sha256_file(input_path) != input_record["sha256"]:
                raise DependencyArtifactError(
                    f"{input_record['id']}: stale input artifact fingerprint"
                )

        graph_reference = data.get("target_graph") or data.get("source_graph")
        if graph_reference:
            graph_path = Path(graph_reference["path"])
            if not graph_path.is_file():
                raise DependencyArtifactError(
                    f"referenced graph is missing: {graph_reference['path']}"
                )
            if sha256_file(graph_path) != graph_reference["sha256"]:
                raise DependencyArtifactError("referenced graph fingerprint is stale")

    edge_tuples: set[tuple[str, str, str]] = set()
    for edge in data.get("edges", []):
        edge_tuple = (edge["from"], edge["relation"], edge["to"])
        if edge_tuple in edge_tuples:
            raise DependencyArtifactError(f"duplicate edge tuple: {edge_tuple}")
        edge_tuples.add(edge_tuple)
        if edge["from"] not in available_nodes or edge["to"] not in available_nodes:
            raise DependencyArtifactError(f"dangling edge endpoints: {edge['id']}")
        missing = sorted(set(edge["evidence_ids"]) - evidence_ids)
        if missing:
            raise DependencyArtifactError(f"{edge['id']}: missing evidence {missing}")

    for node in data.get("nodes", []):
        expected_prefix = node["kind"] + ":"
        if not node["id"].startswith(expected_prefix):
            raise DependencyArtifactError(
                f"{node['id']}: ID prefix does not agree with kind {node['kind']}"
            )
        missing = sorted(set(node["evidence_ids"]) - evidence_ids)
        if missing:
            raise DependencyArtifactError(f"{node['id']}: missing evidence {missing}")

    for evidence in data.get("evidence", []):
        span = evidence.get("span")
        if span:
            if span["source_id"] not in source_ids:
                raise DependencyArtifactError(
                    f"{evidence['id']}: unknown source {span['source_id']}"
                )
            if span["start_line"] > span["end_line"]:
                raise DependencyArtifactError(f"{evidence['id']}: reversed source span")
            root = source_roots.get(span["source_id"])
            if root is not None:
                path = root / span["path"]
                if sha256_file(path) != span["file_sha256"]:
                    raise DependencyArtifactError(f"{evidence['id']}: stale file fingerprint")
                if sha256_span(path, span["start_line"], span["end_line"]) != span["span_sha256"]:
                    raise DependencyArtifactError(f"{evidence['id']}: stale span fingerprint")
        artifact_id = evidence.get("artifact_id")
        if artifact_id is not None and artifact_id not in input_ids:
            raise DependencyArtifactError(
                f"{evidence['id']}: unknown input artifact {artifact_id}"
            )

    if source_roots and kind == "code_graph":
        source_by_owner = {record["owner"]: record for record in data["sources"]}
        file_paths_by_owner: dict[str, set[str]] = {
            owner: set() for owner in source_by_owner
        }
        for node in data.get("nodes", []):
            if node["kind"] == "file" and node["owner"] in file_paths_by_owner:
                file_paths_by_owner[node["owner"]].add(node["properties"]["source.path"])
        roots_by_owner = {
            source["owner"]: source_roots[source["id"]]
            for source in data["sources"]
            if source["id"] in source_roots
        }
        for owner, root in roots_by_owner.items():
            expected = source_by_owner[owner].get("tree_sha256")
            if expected and hash_paths(root, file_paths_by_owner[owner]) != expected:
                raise DependencyArtifactError(
                    f"{source_by_owner[owner]['id']}: source tree fingerprint mismatch"
                )

    if kind == "graph_overlay":
        for annotation in data["annotations"]:
            targets = available_nodes if annotation["target_kind"] == "node" else available_edges
            if annotation["target_id"] not in targets:
                raise DependencyArtifactError(
                    f"annotation target does not resolve: {annotation['target_id']}"
                )
            missing = sorted(set(annotation["evidence_ids"]) - evidence_ids)
            if missing:
                raise DependencyArtifactError(
                    f"annotation {annotation['target_id']}: missing evidence {missing}"
                )

    if kind == "dependency_slice":
        missing_seeds = sorted(set(data["seed_nodes"]) - local_nodes)
        if missing_seeds:
            raise DependencyArtifactError(f"missing seed nodes: {missing_seeds}")
        for group, members in data["groups"].items():
            missing = sorted(set(members) - local_nodes)
            if missing:
                raise DependencyArtifactError(f"group {group}: missing nodes {missing}")
        stop_rules = {rule["id"] for rule in data["policy"]["stop_rules"]}
        for boundary in data["boundaries"]:
            if boundary["from"] not in local_nodes:
                raise DependencyArtifactError(f"boundary source missing: {boundary['from']}")
            if boundary["omitted_to"] in local_nodes:
                raise DependencyArtifactError(
                    f"boundary target was not omitted: {boundary['omitted_to']}"
                )
            if boundary["stop_rule_id"] not in stop_rules:
                raise DependencyArtifactError(
                    f"boundary stop rule missing: {boundary['stop_rule_id']}"
                )
        expected_summary = {
            "node_count": len(data["nodes"]),
            "edge_count": len(data["edges"]),
            "boundary_count": len(data["boundaries"]),
            "unresolved_count": len(data["unresolved"]),
        }
        if data["summary"] != expected_summary:
            raise DependencyArtifactError(
                f"slice summary mismatch: expected {expected_summary}, got {data['summary']}"
            )

    if check_canonical and original_text != canonical_yaml(data):
        raise DependencyArtifactError("artifact is not in canonical YAML form")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("docs/tasks/PORT-001/schema/dependency-artifacts.schema.json"),
    )
    parser.add_argument("--base-graph", type=Path)
    parser.add_argument("--source-root", action="append", default=[], type=parse_mapping)
    parser.add_argument("--canonical", action="store_true")
    parser.add_argument("--verify-files", action="store_true")
    args = parser.parse_args()

    artifact = load_data(args.artifact)
    schema = load_data(args.schema)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(
            schema, format_checker=Draft202012Validator.FORMAT_CHECKER
        ).iter_errors(artifact),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        for error in errors:
            location = "/".join(str(part) for part in error.absolute_path) or "<root>"
            print(f"{args.artifact}:{location}: {error.message}", file=sys.stderr)
        return 1

    base_graph = load_data(args.base_graph) if args.base_graph else None
    source_roots = dict(args.source_root)
    try:
        validate_references(
            artifact,
            base_graph,
            source_roots,
            args.canonical,
            args.verify_files,
            args.artifact.read_text(encoding="utf-8"),
        )
    except (DependencyArtifactError, OSError) as error:
        print(f"{args.artifact}: {error}", file=sys.stderr)
        return 1

    print(f"validated {artifact['artifact_kind']} {artifact['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
