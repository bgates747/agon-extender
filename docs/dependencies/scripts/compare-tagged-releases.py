#!/usr/bin/env python3
"""Compare two independently generated tagged-release dependency graphs.

Every changed source file is emitted once at its highest applicable attention
tier.  Lower-tier reason codes are preserved, so prioritization never becomes
an excuse to make unselected upstream changes disappear.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from dependency_model import artifact_hash, load_data, write_canonical


TARGET_PROFILE = "build-profile:extender:p4-default"
BOUNDARY_ROLES = {"build-metadata", "header", "license"}


def file_map(graph: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (node["owner"], node["properties"]["source.path"]): node
        for node in graph["nodes"]
        if node["kind"] == "file"
    }


def selection_map(graph: dict[str, Any], profile: str) -> dict[str, dict[str, Any]]:
    return {
        record["subject_id"]: record
        for record in graph["selection_records"]
        if record["build_profile_id"] == profile
    }


def connected_to_selected(graph: dict[str, Any], selected: set[str]) -> set[str]:
    connected = set(selected)
    for edge in graph["edges"]:
        if edge["from"] in selected:
            connected.add(edge["to"])
        if edge["to"] in selected:
            connected.add(edge["from"])
    # Symbols defined by files mediate most useful one-hop file relationships.
    for _ in range(2):
        for edge in graph["edges"]:
            if edge["from"] in connected:
                connected.add(edge["to"])
            if edge["to"] in connected:
                connected.add(edge["from"])
    return connected


def classify(
    key: tuple[str, str],
    old_node: dict[str, Any] | None,
    new_node: dict[str, Any] | None,
    old_selection: dict[str, dict[str, Any]],
    new_selection: dict[str, dict[str, Any]],
    connected: set[str],
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if old_node is None:
        reasons.append("new-file")
    if new_node is None:
        reasons.append("deleted-file")
    node = new_node or old_node
    assert node is not None
    role = node["properties"]["source.role"]
    if role in BOUNDARY_ROLES:
        reasons.append(f"boundary-role:{role}")
    old_status = old_selection.get(old_node["id"], {}).get("status") if old_node else None
    new_status = new_selection.get(new_node["id"], {}).get("status") if new_node else None
    if old_status != new_status:
        reasons.append(f"selection-status:{old_status or 'absent'}->{new_status or 'absent'}")
    if reasons:
        return "A", sorted(reasons)
    if "selected" in {old_status, new_status}:
        reasons.append("selected-target-closure")
        return "B", reasons
    if "excluded" in {old_status, new_status}:
        reasons.append("deliberately-excluded")
    if (old_node and old_node["id"] in connected) or (new_node and new_node["id"] in connected):
        reasons.append("connected-to-selected-closure")
    if reasons:
        return "C", sorted(reasons)
    return "D", ["isolated-unselected-content"]


def compare(old: dict[str, Any], new: dict[str, Any], profile: str) -> dict[str, Any]:
    old_files, new_files = file_map(old), file_map(new)
    old_selection, new_selection = selection_map(old, profile), selection_map(new, profile)
    selected = {
        subject_id
        for records in (old_selection, new_selection)
        for subject_id, record in records.items()
        if record["status"] == "selected"
    }
    connected = connected_to_selected(old, selected) | connected_to_selected(new, selected)
    changes = []
    for key in sorted(set(old_files) | set(new_files)):
        old_node, new_node = old_files.get(key), new_files.get(key)
        if old_node and new_node and old_node["properties"]["source.sha256"] == new_node["properties"]["source.sha256"]:
            old_status = old_selection.get(old_node["id"], {}).get("status")
            new_status = new_selection.get(new_node["id"], {}).get("status")
            if old_status == new_status:
                continue
        tier, reasons = classify(key, old_node, new_node, old_selection, new_selection, connected)
        changes.append(
            {
                "owner": key[0],
                "path": key[1],
                "change": "added" if old_node is None else "deleted" if new_node is None else "modified",
                "old_sha256": old_node["properties"]["source.sha256"] if old_node else None,
                "new_sha256": new_node["properties"]["source.sha256"] if new_node else None,
                "old_status": old_selection.get(old_node["id"], {}).get("status") if old_node else None,
                "new_status": new_selection.get(new_node["id"], {}).get("status") if new_node else None,
                "tier": tier,
                "reason_codes": reasons,
            }
        )
    changes.sort(key=lambda item: (item["tier"], item["owner"], item["path"]))
    deleted_by_hash = {
        item["old_sha256"]: item for item in changes if item["change"] == "deleted" and item["old_sha256"]
    }
    rename_candidates = []
    for item in changes:
        if item["change"] == "added" and item["new_sha256"] in deleted_by_hash:
            prior = deleted_by_hash[item["new_sha256"]]
            rename_candidates.append(
                {"owner": item["owner"], "old_path": prior["path"], "new_path": item["path"], "sha256": item["new_sha256"], "status": "hash-equal-candidate-not-identity-claim"}
            )
    counts = {tier: sum(item["tier"] == tier for item in changes) for tier in "ABCD"}
    return {
        "schema_version": "1.0.0",
        "artifact_kind": "merge_attention",
        "old_graph": {"id": old["id"], "sha256": artifact_hash(old)},
        "new_graph": {"id": new["id"], "sha256": artifact_hash(new)},
        "build_profile_id": profile,
        "changes": changes,
        "rename_candidates": rename_candidates,
        "summary": {"changed_file_count": len(changes), "tier_counts": counts},
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Tagged-release merge attention",
        "",
        f"Profile: `{data['build_profile_id']}`",
        "",
        f"Changed files: {data['summary']['changed_file_count']}",
        "",
        "| Tier | Owner | Path | Change | Reasons |",
        "|---|---|---|---|---|",
    ]
    for item in data["changes"]:
        lines.append(f"| {item['tier']} | {item['owner']} | `{item['path']}` | {item['change']} | {', '.join(item['reason_codes'])} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old_graph", type=Path)
    parser.add_argument("new_graph", type=Path)
    parser.add_argument("--profile", default=TARGET_PROFILE)
    parser.add_argument("--yaml", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    result = compare(load_data(args.old_graph), load_data(args.new_graph), args.profile)
    write_canonical(args.yaml, result)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(markdown(result), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
