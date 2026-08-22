#!/usr/bin/env python3
"""Extract scoped SETUP-004 candidates and reproducible mechanical facts."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys
from typing import Any

import yaml

from analysis_model import (
    GraphIndex,
    canonical_source_roots,
    clean_cpp,
    compilation_units,
    compile_patterns,
    dump_yaml,
    load_compile_commands,
    load_yaml,
    matches,
    project_paths,
    sha256,
    source_key,
    stable_id,
)


GENERATOR_VERSION = "1.0.0"
CONNECTION_KINDS = {"task", "interrupt", "timer"}
VISIBLE_KINDS = {"command", "dispatch", "protocol-packet"}


def validate_sources(scope: dict[str, Any], graph: dict[str, Any], scope_path: Path) -> None:
    actual = {source["owner"]: source for source in graph["sources"]}
    for owner, expected in scope["sources"].items():
        source = actual.get(owner)
        if not source:
            raise ValueError(f"{scope_path}: source {owner!r} is absent from PORT-001 graph")
        if source["identity"] != expected["identity"] or source.get("commit") != expected.get("commit"):
            raise ValueError(f"{scope_path}: source identity mismatch for {owner}")


def build_rules(scope: dict[str, Any], section: str) -> list[dict[str, Any]]:
    rules = []
    for raw in scope.get(section, []):
        rule = dict(raw)
        for key in ("graph_node_patterns", "include_target_patterns", "occurrence_patterns"):
            rule[key] = compile_patterns(raw.get(key, []), f"{section}.{raw['id']}.{key}")
        rules.append(rule)
    return rules


def item_matches(rule: dict[str, Any], item: dict[str, Any]) -> bool:
    key = {
        "graph-node": "graph_node_patterns",
        "include": "include_target_patterns",
        "occurrence": "occurrence_patterns",
    }[item["kind"]]
    return matches(rule[key], item["match_value"])


def discover_items(
    scope: dict[str, Any],
    graph: dict[str, Any],
    portability: dict[str, Any],
    effective_sources: set[str],
) -> list[dict[str, Any]]:
    discovery = scope["discovery"]
    graph_patterns = compile_patterns(discovery["graph_node_patterns"], "discovery.graph_node_patterns")
    include_patterns = compile_patterns(discovery["include_target_patterns"], "discovery.include_target_patterns")
    occurrence_patterns = compile_patterns(discovery["occurrence_patterns"], "discovery.occurrence_patterns")
    graph_kinds = set(discovery["graph_node_kinds"])

    graph_files = {
        (node["owner"], location["path"]): location["file_sha256"]
        for node in graph["nodes"]
        if node["kind"] == "file"
        for location in node.get("locations", [])[:1]
        if source_key(node["owner"], location["path"]) in effective_sources
    }
    items: list[dict[str, Any]] = []
    for node in graph["nodes"]:
        if node["kind"] in graph_kinds and matches(graph_patterns, node["id"]):
            items.append(
                {
                    "id": f"graph-node:{node['id']}",
                    "kind": "graph-node",
                    "match_value": node["id"],
                    "graph_node_id": node["id"],
                    "label": node["label"],
                    "owner": node["owner"],
                    "evidence_ids": sorted(node.get("evidence_ids", [])),
                }
            )
    for node_id in discovery.get("explicit_graph_node_ids", []):
        node = next((item for item in graph["nodes"] if item["id"] == node_id), None)
        if node is None:
            raise ValueError(f"explicit graph node is absent: {node_id}")
        items.append(
            {
                "id": f"graph-node:{node['id']}",
                "kind": "graph-node",
                "match_value": node["id"],
                "graph_node_id": node["id"],
                "label": node["label"],
                "owner": node["owner"],
                "evidence_ids": sorted(node.get("evidence_ids", [])),
            }
        )
    for include in portability["includes"]:
        if (include["owner"], include["path"]) not in graph_files:
            continue
        if matches(include_patterns, include["target"]):
            items.append(
                {
                    "id": f"include:{include['owner']}:{include['path']}:{include['line']}:{include['target']}",
                    "kind": "include",
                    "match_value": include["target"],
                    "owner": include["owner"],
                    "path": include["path"],
                    "line": include["line"],
                    "target": include["target"],
                    "evidence_ids": [],
                }
            )
    occurrence_metadata: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    for occurrence in portability["platform_occurrences"]:
        occurrence_metadata[
            (occurrence["owner"], occurrence["path"], int(occurrence["line"]))
        ].add(occurrence["category"])

    project_root = Path(__file__).resolve().parents[4]
    source_roots = canonical_source_roots(project_root)
    occurrence_items: dict[str, dict[str, Any]] = {}
    for (owner, path), expected_hash in sorted(graph_files.items()):
        root = source_roots.get(owner)
        if root is None:
            raise ValueError(f"no canonical source root is configured for {owner}")
        source_path = root / path
        if not source_path.is_file():
            raise ValueError(f"immutable source file is absent: {owner}:{path}")
        actual_hash = sha256(source_path)
        if actual_hash != expected_hash:
            raise ValueError(f"immutable source hash mismatch: {owner}:{path}")
        raw_text = source_path.read_text(encoding="utf-8", errors="replace")
        cleaned_lines = clean_cpp(raw_text).splitlines()
        raw_lines = raw_text.splitlines()
        for line_number, (raw_line, cleaned_line) in enumerate(
            zip(raw_lines, cleaned_lines, strict=True), start=1
        ):
            for pattern_index, pattern in enumerate(occurrence_patterns):
                for match in pattern.finditer(cleaned_line):
                    occurrence_id = stable_id(
                        "occurrence",
                        owner,
                        path,
                        line_number,
                        pattern_index,
                        match.start(),
                        match.end(),
                    )
                    occurrence_items[occurrence_id] = {
                        "id": occurrence_id,
                        "kind": "occurrence",
                        "match_value": match.group(0),
                        "matched_text": match.group(0),
                        "owner": owner,
                        "path": path,
                        "line": line_number,
                        "text": raw_line.strip(),
                        "categories": sorted(
                            occurrence_metadata.get((owner, path, line_number), set())
                        ),
                        "origin": "comment-and-literal-stripped-source-scan",
                        "source_file_sha256": expected_hash,
                        "evidence_ids": [],
                    }
    items.extend(occurrence_items.values())
    unique_items = {item["id"]: item for item in items}
    if len(unique_items) != len(items):
        duplicates = len(items) - len(unique_items)
        raise ValueError(f"discovery produced {duplicates} duplicate item IDs")
    return sorted(unique_items.values(), key=lambda item: item["id"])


def candidate_source_roles(
    members: list[dict[str, Any]], index: GraphIndex
) -> dict[str, set[str]]:
    roles: dict[str, set[str]] = {
        "direct_scanned": set(),
        "graph_seed": set(),
        "inbound_consumers": set(),
    }
    for member in members:
        if member["kind"] in {"include", "occurrence"}:
            roles["direct_scanned"].add(source_key(member["owner"], member["path"]))
        if member["kind"] == "graph-node":
            node_id = member["graph_node_id"]
            node = index.nodes[node_id]
            for location in node.get("locations", []):
                roles["graph_seed"].add(source_key(node["owner"], location["path"]))
            roles["graph_seed"].update(index.evidence_sources(node.get("evidence_ids", [])))
            for edge in index.in_edges.get(node_id, []):
                caller = index.nodes[edge["from"]]
                for location in caller.get("locations", []):
                    roles["inbound_consumers"].add(
                        source_key(caller["owner"], location["path"])
                    )
                roles["inbound_consumers"].update(
                    index.evidence_sources(caller.get("evidence_ids", []))
                )
                roles["inbound_consumers"].update(
                    index.evidence_sources(edge.get("evidence_ids", []))
                )
    return roles


def mechanical_record(
    group: dict[str, Any],
    members: list[dict[str, Any]],
    index: GraphIndex,
    translation_units: set[str],
    effective_sources: set[str],
    boundary_nodes: dict[str, dict[str, str]],
) -> dict[str, Any]:
    graph_node_ids = sorted(member["graph_node_id"] for member in members if member["kind"] == "graph-node")
    evidence_ids = sorted({evidence for member in members for evidence in member.get("evidence_ids", [])})
    source_roles = candidate_source_roles(members, index)
    source_roles = {
        role: sorted(values & effective_sources) for role, values in source_roles.items()
    }
    direct_sources = set(source_roles["direct_scanned"])
    sources = sorted(
        direct_sources
        if direct_sources
        else set(source_roles["graph_seed"]) | set(source_roles["inbound_consumers"])
    )
    participation = [
        {"source": source, **index.source_participation(source, translation_units)} for source in sources
    ]
    reachable, traversal_edges = index.reverse_reachable(graph_node_ids)
    reachable_nodes = [index.nodes[node_id] for node_id in sorted(reachable)]
    candidate_coordinates = {
        (member["owner"], member["path"], int(member["line"]))
        for member in members
        if member["kind"] in {"include", "occurrence"}
    }
    for node in reachable_nodes:
        candidate_coordinates.update(index.evidence_coordinates(node.get("evidence_ids", [])))
    for edge_id in traversal_edges:
        candidate_coordinates.update(
            index.evidence_coordinates(index.edges[edge_id].get("evidence_ids", []))
        )

    connections: dict[str, list[str]] = {
        "startup": [],
        "tasks": [],
        "interrupts": [],
        "timers": [],
        "callbacks": [],
        "global_state": [],
    }
    connections["startup"] = sorted(
        node["id"]
        for node in reachable_nodes
        if node["id"] in {
            "function:agon-vdp:setup()",
            "function:agon-vdp:loop()",
            "function:agon-vdp:processLoop(void%20*%20parameter)",
            "function:agon-vdp-runtime:setup",
            "subsystem:agon-vdp:startup-orchestration",
        }
    )
    for node in reachable_nodes:
        if node["kind"] in CONNECTION_KINDS:
            connections[f"{node['kind']}s"].append(node["id"])
        for edge in index.out_edges.get(node["id"], []):
            target = index.nodes[edge["to"]]
            if edge["relation"] in {"reads", "writes"} and target["kind"] == "variable":
                connections["global_state"].append(target["id"])
            if "callback" in edge["relation"] or "callback" in target.get("label", "").lower():
                connections["callbacks"].append(target["id"])
            if target["kind"] in CONNECTION_KINDS:
                connections[f"{target['kind']}s"].append(target["id"])
    for node in index.nodes.values():
        if node["kind"] not in CONNECTION_KINDS:
            continue
        if index.evidence_coordinates(node.get("evidence_ids", [])) & candidate_coordinates:
            connections[f"{node['kind']}s"].append(node["id"])
    for key in connections:
        connections[key] = sorted(set(connections[key]))

    visible = sorted(node["id"] for node in reachable_nodes if node["kind"] in VISIBLE_KINDS)
    unresolved = sorted(
        item["id"]
        for item in index.graph["unresolved"]
        if item.get("subject_id") in reachable
        or bool(set(item.get("candidate_ids", [])) & reachable)
    )
    dependencies = {
        "graph_nodes": sorted(
            {
                node_id
                for node_id in graph_node_ids
                if index.nodes[node_id]["kind"] in {"platform-api", "physical-facility"}
            }
        ),
        "headers": sorted(
            {member["target"] for member in members if member["kind"] == "include"}
        ),
        "source_occurrences": sorted(
            {member["matched_text"] for member in members if member["kind"] == "occurrence"}
        ),
    }
    boundary_continuations: list[dict[str, str]] = []
    for node_id in sorted(reachable):
        for edge in index.out_edges.get(node_id, []):
            boundary = boundary_nodes.get(edge["to"])
            if boundary:
                boundary_continuations.append(
                    {
                        "edge_id": edge["id"],
                        "boundary_node_id": edge["to"],
                        **boundary,
                    }
                )
    boundary_continuations = sorted(
        {item["edge_id"]: item for item in boundary_continuations}.values(),
        key=lambda item: item["edge_id"],
    )
    source_owners = sorted({source.split(":", 1)[0] for source in sources})
    review_gaps = [
        "present physical owner requires reviewed product evidence",
        "provisional disposition and rationale require reviewed product judgment",
        "cross-candidate decision dependencies require reviewed stable task or ADR IDs",
    ]
    if unresolved:
        review_gaps.append("unresolved graph records intersect the mechanically reachable source set")
    if not visible:
        review_gaps.append("absence of visible behavior requires reviewed reverse-reachability confirmation")
    return {
        "id": group["id"],
        "name": group["name"],
        "owning_projects": source_owners,
        "source_files": sources,
        "source_roles": source_roles,
        "source_participation": participation,
        "direct_hardware_architecture_dependencies": dependencies,
        "connections": connections,
        "visible_graph_nodes": visible,
        "graph_node_ids": graph_node_ids,
        "evidence_ids": evidence_ids,
        "traversal_edge_ids": traversal_edges,
        "boundary_continuations": boundary_continuations,
        "unresolved_ids": unresolved,
        "review_gaps": review_gaps,
    }


def main() -> int:
    script_path = Path(__file__).resolve()
    task_root = script_path.parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-item", required=True)
    parser.add_argument("--task-root", type=Path, default=task_root)
    args = parser.parse_args()

    task_root = args.task_root.resolve()
    paths = project_paths(task_root)
    work_suffix = args.work_item.rsplit(".", 1)[-1]
    scope_path = task_root / "scope" / f"work-1{work_suffix}.yaml"
    if not scope_path.exists():
        raise ValueError(f"no scope manifest for {args.work_item}: {scope_path}")
    scope = load_yaml(scope_path)
    if scope.get("work_item") != args.work_item:
        raise ValueError(f"{scope_path}: work_item does not match {args.work_item}")

    graph = load_yaml(paths["graph"])
    portability = load_yaml(paths["portability"])
    validate_sources(scope, graph, scope_path)
    index = GraphIndex(graph)
    translation_units = compilation_units(load_compile_commands(paths["compile_commands"]))
    effective_sources = set(translation_units)
    for source in index.file_nodes:
        participation = index.source_participation(source, translation_units)
        if participation.get("selected_by"):
            effective_sources.add(source)
    groups = build_rules(scope, "candidate_groups")
    boundaries = build_rules(scope, "boundaries")
    items = discover_items(scope, graph, portability, effective_sources)

    assignments: dict[str, list[dict[str, Any]]] = defaultdict(list)
    exclusions: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    unclassified: list[dict[str, Any]] = []
    for item in items:
        candidate_matches = [rule for rule in groups if item_matches(rule, item)]
        boundary_matches = [rule for rule in boundaries if item_matches(rule, item)]
        matches_all = [("candidate", rule) for rule in candidate_matches] + [
            ("boundary", rule) for rule in boundary_matches
        ]
        if len(matches_all) > 1:
            ambiguous.append(
                {
                    "item_id": item["id"],
                    "matches": [f"{kind}:{rule['id']}" for kind, rule in matches_all],
                }
            )
        elif candidate_matches:
            assignments[candidate_matches[0]["id"]].append(item)
        elif boundary_matches:
            boundary = boundary_matches[0]
            exclusions.append(
                {
                    "item_id": item["id"],
                    "boundary_id": boundary["id"],
                    "owner": boundary["owner"],
                    "reason": boundary["reason"],
                }
            )
        else:
            unclassified.append(item)

    boundary_nodes = {
        exclusion["item_id"].removeprefix("graph-node:"): {
            "boundary_id": exclusion["boundary_id"],
            "owner": exclusion["owner"],
            "reason": exclusion["reason"],
        }
        for exclusion in exclusions
        if exclusion["item_id"].startswith("graph-node:")
    }

    candidate_records = []
    mechanical_records = []
    for group in groups:
        members = sorted(assignments[group["id"]], key=lambda item: item["id"])
        candidate_records.append(
            {
                "id": group["id"],
                "name": group["name"],
                "member_count": len(members),
                "members": members,
            }
        )
        mechanical_records.append(
            mechanical_record(
                group,
                members,
                index,
                translation_units,
                effective_sources,
                boundary_nodes,
            )
        )

    input_paths = [
        scope_path,
        paths["compile_commands"],
        paths["includes"],
        paths["symbols"],
        paths["portability"],
        paths["dependencies"],
        paths["graph"],
    ]
    inputs = [
        {"path": path.relative_to(paths["project_root"]).as_posix(), "sha256": sha256(path)}
        for path in input_paths
    ]
    metadata = {
        "schema_version": 1,
        "generator": {
            "name": "extract-work-item",
            "version": GENERATOR_VERSION,
            "path": script_path.relative_to(paths["project_root"]).as_posix(),
            "regeneration_command": f".venv/bin/python docs/tasks/SETUP-004/scripts/extract-work-item.py --work-item {args.work_item}",
        },
        "work_item": args.work_item,
        "inputs": inputs,
    }
    output_dir = task_root / "generated" / f"work-1{work_suffix}"
    dump_yaml(
        output_dir / "candidates.yaml",
        {
            **metadata,
            "artifact_kind": "setup_004_candidates",
            "counts": {
                "scoped_items": len(items),
                "assigned": sum(len(value) for value in assignments.values()),
                "excluded": len(exclusions),
                "ambiguous": len(ambiguous),
                "unclassified": len(unclassified),
            },
            "candidates": candidate_records,
            "exclusions": sorted(exclusions, key=lambda item: item["item_id"]),
            "ambiguous": ambiguous,
            "unclassified": unclassified,
        },
        "Generated by scripts/extract-work-item.py; do not hand-edit.",
    )
    dump_yaml(
        output_dir / "mechanical-facts.yaml",
        {
            **metadata,
            "artifact_kind": "setup_004_mechanical_facts",
            "candidates": mechanical_records,
        },
        "Generated by scripts/extract-work-item.py; do not hand-edit.",
    )
    print(
        f"extracted {len(items)} scoped items: "
        f"{sum(len(value) for value in assignments.values())} assigned, "
        f"{len(exclusions)} excluded, {len(ambiguous)} ambiguous, "
        f"{len(unclassified)} unclassified"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
