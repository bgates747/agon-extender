#!/usr/bin/env python3
"""Project schema-2 graph selection records into complete YAML and compact Markdown."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from dependency_model import artifact_hash, load_data, write_canonical


def build_projection(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = {node["id"]: node for node in graph["nodes"]}
    records_by_subject: dict[str, list[dict[str, Any]]] = {}
    for record in graph["selection_records"]:
        records_by_subject.setdefault(record["subject_id"], []).append(record)

    subjects = []
    for subject_id in sorted(records_by_subject):
        node = nodes[subject_id]
        subjects.append(
            {
                "id": subject_id,
                "kind": node["kind"],
                "owner": node["owner"],
                "path": node.get("properties", {}).get("source.path"),
                "parent_file_id": node.get("properties", {}).get("region.parent_file_id"),
                "role": node.get("properties", {}).get("source.role"),
                "presence_class": node.get("properties", {}).get("source.presence_class"),
                "sha256": node.get("properties", {}).get("source.sha256"),
                "locations": node.get("locations", []),
                "profiles": sorted(records_by_subject[subject_id], key=lambda item: item["build_profile_id"]),
            }
        )

    project_boundaries = [
        {
            "id": node["id"],
            "label": node["label"],
            "path": node.get("properties", {}).get("project.path"),
            "state": node.get("properties", {}).get("port.state"),
            "task": node.get("properties", {}).get("port.task"),
            "evidence_ids": node["evidence_ids"],
        }
        for node in graph["nodes"]
        if node["kind"] == "build-unit" and node["owner"] == "extender"
    ]

    return {
        "schema_version": "1.0.0",
        "artifact_kind": "source_selection_projection",
        "source_graph": {"id": graph["id"], "sha256": artifact_hash(graph)},
        "build_profiles": graph["build_profiles"],
        "subjects": subjects,
        "project_boundaries": sorted(project_boundaries, key=lambda item: item["id"]),
        "summary": {
            profile["id"]: dict(
                sorted(
                    Counter(
                        record["status"]
                        for record in graph["selection_records"]
                        if record["build_profile_id"] == profile["id"]
                    ).items()
                )
            )
            for profile in graph["build_profiles"]
        },
    }


def markdown(projection: dict[str, Any]) -> str:
    lines = [
        "# Source-selection guide",
        "",
        f"Canonical graph: `{projection['source_graph']['id']}`",
        "",
        "The YAML companion is exhaustive. This compact view lists target selections,",
        "exclusions, and source-region seams; available and non-runtime content remains",
        "queryable in the YAML projection.",
        "",
        "## Profile summary",
        "",
        "| Profile | Selected | Excluded | Available | Non-runtime | Unresolved |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for profile in projection["build_profiles"]:
        counts = projection["summary"][profile["id"]]
        lines.append(
            f"| `{profile['id']}` | {counts.get('selected', 0)} | {counts.get('excluded', 0)} | "
            f"{counts.get('available-not-selected', 0)} | {counts.get('not-applicable', 0)} | {counts.get('unresolved', 0)} |"
        )
    lines.extend(
        [
            "",
            "## P4 target closure and boundaries",
            "",
            "| Subject | Status | Why | Disposition |",
            "|---|---|---|---|",
        ]
    )
    for subject in projection["subjects"]:
        record = next(
            (item for item in subject["profiles"] if item["build_profile_id"] == "build-profile:extender:p4-default"),
            None,
        )
        if record is None or record["status"] not in {"selected", "excluded", "unresolved"}:
            continue
        causes = ", ".join(item["code"] for item in record["causes"])
        refs = ", ".join(record["disposition_refs"]) or "—"
        lines.append(f"| `{subject['id']}` | {record['status']} | {causes} | {refs} |")
    lines.extend(
        [
            "",
            "## Project-owned replacement boundaries",
            "",
            "| Build unit | State | Project path | Task |",
            "|---|---|---|---|",
        ]
    )
    for boundary in projection["project_boundaries"]:
        path = f"`{boundary['path']}`" if boundary["path"] else "—"
        task = f"`{boundary['task']}`" if boundary["task"] else "—"
        lines.append(
            f"| `{boundary['id']}` | {boundary['state'] or '—'} | {path} | {task} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", type=Path)
    parser.add_argument("--yaml", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    projection = build_projection(load_data(args.graph))
    write_canonical(args.yaml, projection)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(markdown(projection), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
