#!/usr/bin/env python3
"""Generate bounded, deterministic dependency slices from a PORT-001 graph."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml

from dependency_model import (
    GENERATOR_VERSION,
    SCHEMA_VERSION,
    artifact_hash,
    canonicalize_graph_collections,
    index_by_id,
    load_data,
    sha256_file,
    typed_id,
    write_canonical,
)


def parse_stop(value: str) -> tuple[str, str]:
    try:
        kind, item = value.split("=", 1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected KIND=VALUE") from error
    if kind not in {"node-id", "node-kind", "relation", "subsystem"}:
        raise argparse.ArgumentTypeError(f"unsupported stop kind: {kind}")
    return kind, item


def boundary_reason(rule: dict[str, Any], direction: str) -> str:
    return f"Traversal stopped by {rule['id']} while following an {direction} relationship."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--seed", required=True, action="append")
    parser.add_argument(
        "--direction",
        action="append",
        choices=["outgoing", "incoming"],
        default=[],
    )
    parser.add_argument("--relation", action="append", default=[])
    parser.add_argument("--node-kind", action="append", default=[])
    parser.add_argument("--maximum-depth", type=int, default=4)
    parser.add_argument("--stop", action="append", default=[], type=parse_stop)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    graph = load_data(args.graph)
    if graph["artifact_kind"] != "code_graph":
        parser.error("--graph must name a code_graph artifact")
    nodes = index_by_id(graph["nodes"])
    edges = graph["edges"]
    missing_seeds = sorted(set(args.seed) - set(nodes))
    if missing_seeds:
        parser.error("seed nodes do not exist: " + ", ".join(missing_seeds))

    directions = args.direction or ["outgoing"]
    relations = set(args.relation or graph["vocabulary"]["relations"])
    node_kinds = set(args.node_kind or graph["vocabulary"]["node_kinds"])
    stop_rules = [
        {
            "id": typed_id("stop", kind, value),
            "kind": kind,
            "values": [value],
            "reason": f"Explicit {kind} traversal boundary for {value}.",
        }
        for kind, value in args.stop
    ]
    depth_rule = {
        "id": typed_id("stop", "depth", args.maximum_depth),
        "kind": "depth",
        "values": [args.maximum_depth],
        "reason": f"Maximum traversal depth is {args.maximum_depth}.",
    }
    stop_rules.append(depth_rule)
    relation_rule = {
        "id": typed_id("stop", "relation-filter"),
        "kind": "relation",
        "values": sorted(relations),
        "reason": "Relationship was excluded by the slice relation filter.",
    }
    node_kind_rule = {
        "id": typed_id("stop", "node-kind-filter"),
        "kind": "node-kind",
        "values": sorted(node_kinds),
        "reason": "Target node kind was excluded by the slice node-kind filter.",
    }
    stop_rules.extend([relation_rule, node_kind_rule])

    outgoing: dict[str, list[tuple[dict[str, Any], str]]] = defaultdict(list)
    incoming: dict[str, list[tuple[dict[str, Any], str]]] = defaultdict(list)
    for edge in edges:
        outgoing[edge["from"]].append((edge, edge["to"]))
        incoming[edge["to"]].append((edge, edge["from"]))
    for adjacency in (outgoing, incoming):
        for records in adjacency.values():
            records.sort(key=lambda item: item[0]["id"])

    selected = set(args.seed)
    queue = deque((seed, 0) for seed in sorted(args.seed))
    visited_depth = {seed: 0 for seed in args.seed}
    boundaries: dict[tuple[str, str, str], dict[str, Any]] = {}

    def explicit_stop(node_id: str, edge: dict[str, Any]) -> dict[str, Any] | None:
        for rule in stop_rules[:-3]:
            value = rule["values"][0]
            if rule["kind"] == "node-id" and node_id == value:
                return rule
            if rule["kind"] == "node-kind" and nodes[node_id]["kind"] == value:
                return rule
            if rule["kind"] == "relation" and edge["relation"] == value:
                return rule
            if rule["kind"] == "subsystem" and (
                node_id == value
                or nodes[node_id].get("properties", {}).get("review.runtime_id") == value
            ):
                return rule
        return None

    while queue:
        current, depth = queue.popleft()
        for direction in directions:
            adjacency = outgoing if direction == "outgoing" else incoming
            for edge, neighbor in adjacency.get(current, []):
                rule = None
                if edge["relation"] not in relations:
                    rule = relation_rule
                elif nodes[neighbor]["kind"] not in node_kinds:
                    rule = node_kind_rule
                else:
                    rule = explicit_stop(neighbor, edge)
                if rule is None and depth >= args.maximum_depth and neighbor not in selected:
                    rule = depth_rule
                if rule is not None:
                    key = (current, edge["relation"], neighbor)
                    boundaries[key] = {
                        "from": current,
                        "relation": edge["relation"],
                        "omitted_to": neighbor,
                        "stop_rule_id": rule["id"],
                        "reason": boundary_reason(rule, direction),
                        "continuation_slice": None,
                    }
                    continue
                if neighbor not in selected:
                    selected.add(neighbor)
                    visited_depth[neighbor] = depth + 1
                    queue.append((neighbor, depth + 1))

    selected_edges = [
        edge
        for edge in edges
        if edge["from"] in selected
        and edge["to"] in selected
        and edge["relation"] in relations
    ]
    evidence_ids = {
        evidence_id
        for node_id in selected
        for evidence_id in nodes[node_id]["evidence_ids"]
    }
    evidence_ids.update(
        evidence_id for edge in selected_edges for evidence_id in edge["evidence_ids"]
    )
    unresolved = []
    for record in graph.get("unresolved", []):
        subject_id = record.get("subject_id")
        description_mentions_node = subject_id is None and any(
            node_id in record["description"] for node_id in selected
        )
        if subject_id in selected or description_mentions_node:
            unresolved.append(record)
            evidence_ids.update(record["evidence_ids"])
    evidence = [
        record for record in graph["evidence"] if record["id"] in evidence_ids
    ]
    groups: dict[str, list[str]] = defaultdict(list)
    for node_id in selected:
        groups[nodes[node_id]["kind"]].append(node_id)

    repository_root = Path.cwd().resolve()
    graph_path = args.graph.resolve()
    generator_path = "docs/dependencies/scripts/slice-dependency-graph.py"
    output_relative = args.output.resolve().relative_to(repository_root).as_posix()
    argv = [
        ".venv/bin/python",
        generator_path,
        "--graph",
        graph_path.relative_to(repository_root).as_posix(),
    ]
    for seed in args.seed:
        argv.extend(["--seed", seed])
    for direction in directions:
        argv.extend(["--direction", direction])
    for relation in sorted(args.relation):
        argv.extend(["--relation", relation])
    for node_kind in sorted(args.node_kind):
        argv.extend(["--node-kind", node_kind])
    argv.extend(["--maximum-depth", str(args.maximum_depth)])
    for kind, value in args.stop:
        argv.extend(["--stop", f"{kind}={value}"])
    argv.extend(["--title", args.title, "--output", output_relative])

    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "dependency_slice",
        "id": typed_id("slice", graph["id"], "+".join(sorted(args.seed))),
        "generator": {
            "name": "slice-dependency-graph",
            "version": GENERATOR_VERSION,
            "path": generator_path,
            "argv": argv,
        },
        "sources": graph["sources"],
        "inputs": graph["inputs"]
        + [
            {
                "id": typed_id("input", "port-001", "code-graph"),
                "path": graph_path.relative_to(repository_root).as_posix(),
                "role": "canonical merged dependency graph",
                "schema_version": SCHEMA_VERSION,
                "sha256": sha256_file(graph_path),
            }
        ],
        "tools": graph["tools"],
        "source_graph": {
            "id": graph["id"],
            "path": graph_path.relative_to(repository_root).as_posix(),
            "schema_version": SCHEMA_VERSION,
            "sha256": artifact_hash(graph),
        },
        "title": args.title,
        "seed_nodes": sorted(args.seed),
        "policy": {
            "directions": directions,
            "relations": sorted(relations),
            "node_kinds": sorted(node_kinds),
            "maximum_depth": args.maximum_depth,
            "stop_rules": sorted(stop_rules, key=lambda item: item["id"]),
        },
        "evidence": evidence,
        "nodes": [nodes[node_id] for node_id in selected],
        "edges": selected_edges,
        "groups": dict(groups),
        "boundaries": list(boundaries.values()),
        "unresolved": unresolved,
        "summary": {
            "node_count": len(selected),
            "edge_count": len(selected_edges),
            "boundary_count": len(boundaries),
            "unresolved_count": len(unresolved),
        },
    }
    canonicalize_graph_collections(artifact)
    artifact["seed_nodes"] = sorted(artifact["seed_nodes"])
    write_canonical(args.output, artifact)
    print(
        f"wrote {len(selected)} nodes, {len(selected_edges)} edges, "
        f"{len(boundaries)} boundaries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
