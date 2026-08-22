#!/usr/bin/env python3
"""Run bounded deterministic source-selection queries against the canonical graph."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
from typing import Any

from dependency_model import artifact_hash, load_data, write_canonical


def related_nodes(graph: dict[str, Any], seed: str, depth: int) -> set[str]:
    adjacency: dict[str, set[str]] = {}
    for edge in graph["edges"]:
        adjacency.setdefault(edge["from"], set()).add(edge["to"])
        adjacency.setdefault(edge["to"], set()).add(edge["from"])
    seen = {seed}
    queue = deque([(seed, 0)])
    while queue:
        node, current_depth = queue.popleft()
        if current_depth == depth:
            continue
        for neighbor in sorted(adjacency.get(node, set())):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, current_depth + 1))
    return seen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", type=Path)
    parser.add_argument("--owner")
    parser.add_argument("--path-contains")
    parser.add_argument("--profile")
    parser.add_argument("--status", action="append")
    parser.add_argument("--cause", action="append")
    parser.add_argument("--disposition-contains")
    parser.add_argument("--related-node", help="command, subsystem, packet, behavior, or any typed graph node")
    parser.add_argument("--merge-attention", type=Path, help="optional tagged-release comparison to restrict/query changed files")
    parser.add_argument("--tier", action="append", choices=list("ABCD"))
    parser.add_argument("--change", action="append", choices=["added", "deleted", "modified"])
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    graph = load_data(args.graph)
    merge = load_data(args.merge_attention) if args.merge_attention else None
    changed = (
        {(item["owner"], item["path"]): item for item in merge["changes"]}
        if merge
        else None
    )
    nodes = {node["id"]: node for node in graph["nodes"]}
    related = related_nodes(graph, args.related_node, args.depth) if args.related_node else None
    matches = []
    for record in graph["selection_records"]:
        node = nodes[record["subject_id"]]
        path = node.get("properties", {}).get("source.path", "")
        parent = node.get("properties", {}).get("region.parent_file_id")
        change_record = changed.get((node["owner"], path)) if changed is not None else None
        if changed is not None and change_record is None:
            continue
        if args.tier and change_record["tier"] not in args.tier:
            continue
        if args.change and change_record["change"] not in args.change:
            continue
        if args.owner and node["owner"] != args.owner:
            continue
        if args.path_contains and args.path_contains not in (path or node["label"]):
            continue
        if args.profile and record["build_profile_id"] != args.profile:
            continue
        if args.status and record["status"] not in args.status:
            continue
        codes = {cause["code"] for cause in record["causes"]}
        if args.cause and not set(args.cause).issubset(codes):
            continue
        if args.disposition_contains and not any(args.disposition_contains in ref for ref in record["disposition_refs"]):
            continue
        if related is not None and record["subject_id"] not in related and parent not in related and not set(record["entry_point_ids"]) & related:
            continue
        match = {"subject": node, "selection": record}
        if change_record is not None:
            match["tagged_release_change"] = change_record
        matches.append(match)
    matches.sort(key=lambda item: (item["selection"]["build_profile_id"], item["subject"]["id"]))
    omitted = max(0, len(matches) - args.limit)
    result = {
        "schema_version": "1.0.0",
        "artifact_kind": "dependency_query",
        "source_graph": {"id": graph["id"], "sha256": artifact_hash(graph)},
        "filters": {
            "owner": args.owner,
            "path_contains": args.path_contains,
            "profile": args.profile,
            "statuses": args.status or [],
            "causes": args.cause or [],
            "disposition_contains": args.disposition_contains,
            "related_node": args.related_node,
            "merge_attention": str(args.merge_attention) if args.merge_attention else None,
            "tiers": args.tier or [],
            "changes": args.change or [],
            "depth": args.depth,
            "limit": args.limit,
        },
        "matches": matches[: args.limit],
        "boundaries": [] if not omitted else [{"kind": "result-limit", "omitted_count": omitted}],
        "summary": {"matched_count": len(matches), "returned_count": min(len(matches), args.limit)},
    }
    write_canonical(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
