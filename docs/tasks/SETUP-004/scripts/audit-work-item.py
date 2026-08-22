#!/usr/bin/env python3
"""Audit SETUP-004 extraction coverage and reviewed-record completeness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import yaml

from analysis_model import dump_yaml, load_yaml, project_paths, sha256


GENERATOR_VERSION = "1.1.0"
REQUIRED_MECHANICAL_FIELDS = {
    "owning_projects",
    "source_files",
    "source_roles",
    "source_participation",
    "direct_hardware_architecture_dependencies",
    "connections",
    "visible_graph_nodes",
    "boundary_continuations",
    "unresolved_ids",
    "review_gaps",
}
REQUIRED_REVIEWED_FIELDS = {
    "source_highlights",
    "implementation_highlights",
    "facilities",
    "activation",
    "connections",
    "visible_behavior",
    "target_compatibility",
    "physical_owner_class",
    "physical_owner",
    "author_review",
    "disposition",
    "rationale",
    "omission_fallout",
    "dependencies",
    "dependency_effects",
    "evidence_ids",
    "graph_node_ids",
    "agent_entry_points",
}
OWNER_CLASSES = {"Agon main board", "onboard VDP", "Extender", "shared", "none"}
REVIEW_STATUSES = {"pending", "accepted"}
DEPENDENCY_EFFECTS = {
    "blocks-disposition",
    "blocks-implementation",
    "requires-later-qualification",
}
CONNECTION_FIELDS = {"startup", "tasks", "interrupts", "timers", "callbacks", "global_state"}
FALLOUT_FIELDS = {"kind", "first_failure", "selected_consumers", "severance", "residual_risk"}


def load_reviewed(
    task_root: Path, work_item: str
) -> tuple[dict[str, dict[str, Any]], list[tuple[Path, dict[str, Any]]]]:
    result: dict[str, dict[str, Any]] = {}
    documents: list[tuple[Path, dict[str, Any]]] = []
    suffix = work_item.rsplit(".", 1)[-1]
    for path in sorted((task_root / "evidence").glob(f"work-1{suffix}-*.yaml")):
        document = load_yaml(path)
        if document.get("work_item") != work_item:
            raise ValueError(f"{path}: work_item mismatch")
        for record in document.get("records", []):
            if record["id"] in result:
                raise ValueError(f"duplicate reviewed candidate {record['id']}")
            result[record["id"]] = record
        documents.append((path, document))
    return result, documents


def package_root(package: str, version: str) -> Path:
    packages = Path.home() / ".platformio/packages"
    if package == "arduino-esp32":
        matches = []
        for candidate in packages.glob("framework-arduinoespressif32*"):
            manifest = candidate / "package.json"
            if not manifest.is_file():
                continue
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if data.get("name") == "framework-arduinoespressif32" and data.get("version") == version:
                matches.append(candidate)
        if len(matches) != 1:
            raise ValueError(
                f"expected one installed Arduino-ESP32 {version} package, found {len(matches)}"
            )
        return matches[0]
    if package == "esp-idf-libs-esp32p4":
        root = packages / "framework-arduinoespressif32-libs/esp32p4"
        manifest = root.parent / "package.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if not str(data.get("version", "")).startswith(version):
            raise ValueError(f"installed ESP-IDF library package does not match {version}")
        return root
    raise ValueError(f"unknown target evidence package: {package}")


def validate_target_evidence(documents: list[tuple[Path, dict[str, Any]]]) -> set[str]:
    seen: set[str] = set()
    roots: dict[tuple[str, str], Path] = {}
    for path, document in documents:
        target = document.get("target_framework", {})
        for item in target.get("source_evidence", []):
            evidence_id = item.get("id")
            if not isinstance(evidence_id, str) or not evidence_id.startswith("target:"):
                raise ValueError(f"{path}: invalid target source evidence ID")
            if evidence_id in seen:
                raise ValueError(f"{path}: duplicate target source evidence ID {evidence_id}")
            seen.add(evidence_id)
            key = (item["package"], str(item["version"]))
            root = roots.setdefault(key, package_root(*key))
            source_path = root / item["path"]
            if not source_path.is_file():
                raise ValueError(f"{path}: target evidence source is absent: {evidence_id}")
            if sha256(source_path) != item["sha256"]:
                raise ValueError(f"{path}: target evidence source hash mismatch: {evidence_id}")
    return seen


def main() -> int:
    script_path = Path(__file__).resolve()
    task_root = script_path.parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-item", required=True)
    parser.add_argument("--task-root", type=Path, default=task_root)
    args = parser.parse_args()

    task_root = args.task_root.resolve()
    paths = project_paths(task_root)
    suffix = args.work_item.rsplit(".", 1)[-1]
    output_dir = task_root / "generated" / f"work-1{suffix}"
    candidates_path = output_dir / "candidates.yaml"
    mechanical_path = output_dir / "mechanical-facts.yaml"
    candidates = load_yaml(candidates_path)
    mechanical = load_yaml(mechanical_path)
    if candidates.get("work_item") != args.work_item or mechanical.get("work_item") != args.work_item:
        raise ValueError("generated artifact work_item mismatch")

    reviewed, reviewed_documents = load_reviewed(task_root, args.work_item)
    target_evidence_ids = validate_target_evidence(reviewed_documents)
    graph = load_yaml(paths["graph"])
    graph_evidence_ids = {item["id"] for item in graph["evidence"]}
    graph_node_ids = {item["id"] for item in graph["nodes"]}
    mechanical_by_id = {record["id"]: record for record in mechanical["candidates"]}
    candidate_ids = {record["id"] for record in candidates["candidates"]}
    errors: list[str] = []
    warnings: list[str] = []

    if candidates["ambiguous"]:
        errors.append(f"{len(candidates['ambiguous'])} scoped items have ambiguous ownership")
    if candidates["unclassified"]:
        errors.append(f"{len(candidates['unclassified'])} scoped items are unclassified")
    if set(mechanical_by_id) != candidate_ids:
        errors.append("candidate and mechanical candidate ID sets differ")
    empty_candidates = sorted(
        record["id"] for record in candidates["candidates"] if not record["member_count"]
    )
    if empty_candidates:
        errors.append(f"candidate groups have no members: {empty_candidates}")

    missing_reviews = sorted(candidate_ids - set(reviewed))
    extra_reviews = sorted(set(reviewed) - candidate_ids)
    if missing_reviews:
        errors.append(f"missing reviewed records: {missing_reviews}")
    if extra_reviews:
        errors.append(f"reviewed records absent from scope: {extra_reviews}")

    candidate_audits = []
    for candidate_id in sorted(candidate_ids):
        mechanical_record = mechanical_by_id[candidate_id]
        missing_mechanical = sorted(REQUIRED_MECHANICAL_FIELDS - set(mechanical_record))
        reviewed_record = reviewed.get(candidate_id)
        missing_reviewed = (
            sorted(REQUIRED_REVIEWED_FIELDS - set(reviewed_record)) if reviewed_record else sorted(REQUIRED_REVIEWED_FIELDS)
        )
        if missing_mechanical:
            errors.append(f"{candidate_id}: missing mechanical fields {missing_mechanical}")
        if reviewed_record and missing_reviewed:
            errors.append(f"{candidate_id}: missing reviewed fields {missing_reviewed}")

        if reviewed_record:
            if reviewed_record.get("physical_owner_class") not in OWNER_CLASSES:
                errors.append(f"{candidate_id}: invalid physical_owner_class")
            author_review = reviewed_record.get("author_review", {})
            review_status = author_review.get("status") if isinstance(author_review, dict) else None
            if review_status not in REVIEW_STATUSES:
                errors.append(f"{candidate_id}: invalid author_review status")
            if review_status == "accepted" and not author_review.get("decision_date"):
                errors.append(f"{candidate_id}: accepted author_review requires decision_date")
            connections = reviewed_record.get("connections", {})
            if not isinstance(connections, dict) or set(connections) != CONNECTION_FIELDS:
                errors.append(f"{candidate_id}: reviewed connections must contain {sorted(CONNECTION_FIELDS)}")
            dependencies = reviewed_record.get("dependencies", [])
            effects = reviewed_record.get("dependency_effects", [])
            effect_ids = [item.get("id") for item in effects if isinstance(item, dict)]
            if sorted(effect_ids) != sorted(dependencies):
                errors.append(f"{candidate_id}: dependency_effects must cover dependencies exactly")
            for item in effects:
                if not isinstance(item, dict) or item.get("effect") not in DEPENDENCY_EFFECTS:
                    errors.append(f"{candidate_id}: invalid dependency effect {item!r}")
            compatibility = reviewed_record.get("target_compatibility", {})
            if not isinstance(compatibility, dict) or not compatibility.get("status") or not compatibility.get("finding"):
                errors.append(f"{candidate_id}: incomplete target_compatibility")
            unknown_target = sorted(
                evidence
                for evidence in compatibility.get("evidence", [])
                if evidence.startswith("target:") and evidence not in target_evidence_ids
            )
            if unknown_target:
                errors.append(f"{candidate_id}: unknown target evidence IDs {unknown_target}")
            unknown_evidence = sorted(set(reviewed_record.get("evidence_ids", [])) - graph_evidence_ids)
            unknown_nodes = sorted(set(reviewed_record.get("graph_node_ids", [])) - graph_node_ids)
            if unknown_evidence:
                errors.append(f"{candidate_id}: unknown PORT-001 evidence IDs {unknown_evidence}")
            if unknown_nodes:
                errors.append(f"{candidate_id}: unknown PORT-001 graph node IDs {unknown_nodes}")

        dependencies = mechanical_record.get("direct_hardware_architecture_dependencies")
        if not isinstance(dependencies, dict) or set(dependencies) != {
            "graph_nodes", "headers", "source_occurrences"
        }:
            errors.append(f"{candidate_id}: malformed mechanical direct dependencies")
        mechanical_connections = mechanical_record.get("connections", {})
        if not isinstance(mechanical_connections, dict) or set(mechanical_connections) != CONNECTION_FIELDS:
            errors.append(f"{candidate_id}: malformed mechanical connections")

        fallout_status = "not-applicable"
        if reviewed_record and reviewed_record.get("disposition") in {"omit", "replace", "stub"}:
            fallout = reviewed_record.get("fallout_analysis")
            fallout_status = (
                "present"
                if isinstance(fallout, dict) and FALLOUT_FIELDS <= set(fallout)
                else "missing"
            )
            if fallout_status == "missing":
                errors.append(f"{candidate_id}: disposition requires fallout analysis")
        if not mechanical_record["source_files"]:
            warnings.append(f"{candidate_id}: no mechanically located source files; reviewed evidence must explain")
        candidate_audits.append(
            {
                "id": candidate_id,
                "mechanical_fields_complete": not missing_mechanical,
                "reviewed_record_present": reviewed_record is not None,
                "reviewed_fields_complete": reviewed_record is not None and not missing_reviewed,
                "fallout_status": fallout_status,
                "mechanical_unresolved_count": len(mechanical_record["unresolved_ids"]),
                "mechanical_review_gap_count": len(mechanical_record["review_gaps"]),
                "mechanical_boundary_continuation_count": len(
                    mechanical_record["boundary_continuations"]
                ),
            }
        )

    status = "pass-ready-for-author-review" if not errors else "fail"
    coverage = {
        "schema_version": 1,
        "artifact_kind": "setup_004_coverage_audit",
        "generator": {
            "name": "audit-work-item",
            "version": GENERATOR_VERSION,
            "path": script_path.relative_to(paths["project_root"]).as_posix(),
            "regeneration_command": f".venv/bin/python docs/tasks/SETUP-004/scripts/audit-work-item.py --work-item {args.work_item}",
        },
        "work_item": args.work_item,
        "inputs": [
            {
                "path": candidates_path.relative_to(paths["project_root"]).as_posix(),
                "sha256": sha256(candidates_path),
            },
            {
                "path": mechanical_path.relative_to(paths["project_root"]).as_posix(),
                "sha256": sha256(mechanical_path),
            },
            {
                "path": paths["graph"].relative_to(paths["project_root"]).as_posix(),
                "sha256": sha256(paths["graph"]),
            },
            *[
                {
                    "path": path.relative_to(paths["project_root"]).as_posix(),
                    "sha256": sha256(path),
                }
                for path, _document in reviewed_documents
            ],
        ],
        "status": status,
        "counts": {
            **candidates["counts"],
            "candidate_count": len(candidate_ids),
            "reviewed_candidate_count": len(set(reviewed) & candidate_ids),
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        "candidate_audits": candidate_audits,
        "errors": errors,
        "warnings": warnings,
    }
    dump_yaml(
        output_dir / "coverage.yaml",
        coverage,
        "Generated by scripts/audit-work-item.py; do not hand-edit.",
    )
    print(f"coverage {status}: {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
