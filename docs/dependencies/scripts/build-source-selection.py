#!/usr/bin/env python3
"""Enrich the PORT-001 graph with exhaustive schema-2 source selection.

The PORT-001 graph is intentionally retained as a mechanical intermediate: it
captures symbols and relationships discovered before source selection became a
durable project concern. This generator inventories every immutable source
tree, verifies any declared repository-managed import byte-for-byte, removes
the obsolete per-node selection scalar, and adds normalized profile/subject
records driven by build evidence and accepted SETUP-004 dispositions. It does
not copy or alter source.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml

from dependency_model import (
    GENERATOR_VERSION,
    NODE_KINDS,
    RELATIONS,
    SCHEMA_VERSION,
    canonicalize_graph_collections,
    edge_id,
    evidence_id,
    hash_paths,
    load_data,
    merge_evidence_ids,
    sha256_file,
    source_span,
    typed_id,
    write_canonical,
)


OBSERVED_PROFILE = "build-profile:upstream:agon-vdp-v2.16.0-esp32"
TARGET_PROFILE = "build-profile:extender:p4-default"

NON_RUNTIME_ROLES = {"documentation", "license", "example", "test", "asset"}
CODE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".ino", ".s", ".S"}
HEADER_SUFFIXES = {".h", ".hh", ".hpp", ".hxx", ".inc"}

# Exact reviewed spans for the fused source used by PORT-002's proof.  These
# ranges are source-selection boundaries, not claims that an implementation
# guard already exists in upstream vdp-gl.
REGION_SPAN_OVERRIDES: dict[tuple[str, str], tuple[int, int]] = {
    ("storage-vdp-gl-filebrowser-api", "src/fabutils.cpp"): (676, 1406),
    ("storage-vdp-gl-filebrowser-api", "src/fabutils.h"): (773, 1152),
    ("storage-vdp-gl-esp32-mount-format-backends", "src/fabutils.cpp"): (1180, 1406),
    ("storage-vdp-gl-esp32-mount-format-backends", "src/fabutils.h"): (1033, 1123),
}

WHOLE_FILE_FALLOUT_KINDS = {
    "omit-unused-translation-unit",
    "omit-architecture-specific-source",
    "replace-fused-display-backend",
    "omit-physical-keyboard-engine",
    "omit-physical-mouse-engine",
    "omit-incompatible-physical-controller",
    "omit-independent-unreferenced-translation-unit",
}


def parse_owner_root(value: str) -> tuple[str, Path]:
    try:
        owner, raw_path = value.split("=", 1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected OWNER=PATH") from error
    root = Path(raw_path).resolve()
    if not root.is_dir():
        raise argparse.ArgumentTypeError(f"source root does not exist: {root}")
    return owner, root


def source_files(root: Path, commit: str | None) -> list[str]:
    """List immutable release content, excluding local build/cache material."""

    if commit:
        actual = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if actual != commit:
            raise ValueError(f"{root}: expected commit {commit}, found {actual}")
        output = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "--name-only", commit],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return sorted(line for line in output.splitlines() if line and (root / line).is_file())

    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(root).parts
        and "__pycache__" not in path.relative_to(root).parts
    )


def managed_repository_path(
    repository_root: Path, baseline_source: dict[str, Any], source_path: str
) -> Path | None:
    """Resolve one immutable source path to its reviewed managed import.

    Split imports such as agon-vdp must map every source file exactly once.
    Ambiguous or incomplete mappings are configuration errors, never a reason
    to silently downgrade provenance.
    """

    managed = baseline_source.get("managed_import")
    if not managed:
        return None
    matches: list[Path] = []
    for mapping in managed["mappings"]:
        prefix = mapping["source_prefix"]
        excluded = mapping.get("exclude_prefixes", [])
        if source_path.startswith(prefix) and not any(
            source_path.startswith(value) for value in excluded
        ):
            relative = source_path[len(prefix) :]
            matches.append(repository_root / mapping["repository_path"] / relative)
    if len(matches) != 1:
        raise ValueError(
            f"{baseline_source['owner']}:{source_path}: expected exactly one managed "
            f"import mapping, found {len(matches)}"
        )
    return matches[0]


def file_role(path: str) -> str:
    lower = path.lower()
    name = Path(path).name.lower()
    suffix = Path(path).suffix
    parts = {part.lower() for part in Path(path).parts}
    if name.startswith(("license", "copying", "notice")):
        return "license"
    if "test" in parts or "tests" in parts or name.startswith("test_"):
        return "test"
    if "example" in parts or "examples" in parts:
        return "example"
    if suffix in CODE_SUFFIXES:
        return "firmware-source"
    if suffix in HEADER_SUFFIXES:
        return "header"
    if name in {"readme", "readme.md", "code_of_conduct.md", "contributing.md"} or suffix.lower() in {".md", ".rst", ".txt"}:
        return "documentation"
    if name in {"platformio.ini", "cmakelists.txt", "component.mk", "library.json", "library.properties", "keywords.txt"} or suffix.lower() in {".json", ".yml", ".yaml", ".ini", ".toml"}:
        return "build-metadata"
    if suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", ".html", ".css", ".js"}:
        return "asset"
    return "other"


def owner_path(value: str) -> tuple[str, str] | None:
    if ":" not in value:
        return None
    owner, path = value.split(":", 1)
    return owner, path


def accepted_dispositions(evidence_dir: Path) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], dict[tuple[str, str, str], list[int]]]:
    by_file: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    entry_lines: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for path in sorted(evidence_dir.glob("work-1*.yaml")):
        data = load_data(path)
        for record in data.get("records", []):
            if record.get("author_review", {}).get("status") != "accepted":
                continue
            disposition = record.get("disposition")
            if disposition not in {"retain", "replace", "omit"}:
                continue
            normalized = {
                "id": record["id"],
                "work_item": data["work_item"],
                "disposition": disposition,
                "name": record["name"],
                "graph_node_ids": record.get("graph_node_ids", []),
                "fallout_kind": record.get("fallout_analysis", {}).get("kind"),
            }
            references: set[tuple[str, str]] = set()
            source_highlights: set[tuple[str, str]] = set()
            for value in record.get("source_highlights", []):
                parsed = owner_path(value)
                if parsed:
                    references.add(parsed)
                    source_highlights.add(parsed)
            implementation = record.get("implementation_highlights", {})
            selected_units: set[tuple[str, str]] = set()
            for key in ("selected_translation_units", "header_implementation"):
                for value in implementation.get(key, []):
                    parsed = owner_path(value)
                    if parsed:
                        references.add(parsed)
                        if key == "selected_translation_units":
                            selected_units.add(parsed)
            whole_file_paths: set[tuple[str, str]] = set()
            if normalized["fallout_kind"] in WHOLE_FILE_FALLOUT_KINDS:
                whole_file_paths.update(selected_units)
                inferred_headers = {
                    (owner, str(Path(path).with_suffix(".h")))
                    for owner, path in selected_units
                    if Path(path).suffix.lower() in {".c", ".cc", ".cpp", ".cxx"}
                }
                references.update(inferred_headers)
                whole_file_paths.update(inferred_headers)
                selected_stems = {
                    (owner, str(Path(path).with_suffix(""))) for owner, path in selected_units
                }
                whole_file_paths.update(
                    key
                    for key in references
                    if (key[0], str(Path(key[1]).with_suffix(""))) in selected_stems
                )
            elif normalized["fallout_kind"] == "omit-header-defined-subsystem":
                whole_file_paths.update(source_highlights)
            for key in references:
                by_file[key].append({**normalized, "whole_file": key in whole_file_paths})
            for value in record.get("agent_entry_points", []):
                parts = value.rsplit(":", 1)
                if len(parts) != 2 or not parts[1].isdigit():
                    continue
                parsed = owner_path(parts[0])
                if parsed:
                    entry_lines[(record["id"], parsed[0], parsed[1])].append(int(parts[1]))
    for records in by_file.values():
        records.sort(key=lambda item: (item["work_item"], item["id"]))
    return by_file, entry_lines


def direct_build_inputs(compile_commands_path: Path) -> set[tuple[str, str]]:
    records = json.loads(compile_commands_path.read_text(encoding="utf-8"))
    selected: set[tuple[str, str]] = set()
    markers = {"CRC": "/CRC/", "ESP32Time": "/ESP32Time/", "vdp-gl": "/vdp-gl/"}
    for record in records:
        path = record["file"].replace("\\", "/")
        for owner, marker in markers.items():
            if marker in path:
                selected.add((owner, path.split(marker, 1)[1]))
                break
        else:
            if path.startswith("video/"):
                selected.add(("agon-vdp", path))
    return selected


def declared_target_status(
    role: str,
    observed_status: str,
    file_dispositions: list[dict[str, Any]],
    is_new_upstream_file: bool,
) -> str:
    """Apply the fail-visible target default before generating causes."""

    if is_new_upstream_file and not file_dispositions:
        return "unresolved"
    if role in NON_RUNTIME_ROLES:
        return "not-applicable"
    if any(
        item["disposition"] in {"omit", "replace"} and item["whole_file"]
        for item in file_dispositions
    ):
        return "excluded"
    return observed_status


def add_artifact_evidence(
    evidence: list[dict[str, Any]], identifier: str, input_id: str, pointer: str, description: str
) -> str:
    evidence.append(
        {
            "id": identifier,
            "kind": "reviewed-analysis",
            "method": "reviewed",
            "description": description,
            "artifact_id": input_id,
            "record_pointer": pointer,
            "review": {
                "status": "accepted",
                "reviewed_on": "2026-08-22",
                "basis": "Accepted PORT-002 Review Gate 1 model and accepted SETUP-004 dispositions.",
            },
        }
    )
    return identifier


def cause(
    code: str,
    cause_class: str,
    effect: str,
    evidence_ids: Iterable[str],
    decision_refs: Iterable[str] = (),
) -> dict[str, Any]:
    return {
        "code": code,
        "class": cause_class,
        "effect": effect,
        "evidence_ids": sorted(set(evidence_ids)),
        "decision_refs": sorted(set(decision_refs)),
    }


def selection_record(
    profile_id: str,
    subject_id: str,
    status: str,
    causes: list[dict[str, Any]],
    *,
    dispositions: Iterable[dict[str, Any]] = (),
    entry_points: Iterable[str] = (),
    replacement_subject_id: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": typed_id("selection", profile_id, subject_id),
        "build_profile_id": profile_id,
        "subject_id": subject_id,
        "status": status,
        "causes": causes,
        "entry_point_ids": sorted(set(entry_points)),
        "disposition_refs": sorted(
            {f"{item['work_item']}:{item['id']}:{item['disposition']}" for item in dispositions}
        ),
    }
    if replacement_subject_id:
        record["replacement_subject_id"] = replacement_subject_id
    return record


def region_span_for(
    record: dict[str, Any], owner: str, path: str, root: Path, entry_lines: dict[tuple[str, str, str], list[int]]
) -> tuple[int, int, str]:
    override = REGION_SPAN_OVERRIDES.get((record["id"], path))
    if override:
        return override[0], override[1], "reviewed-exact-boundary"
    lines = entry_lines.get((record["id"], owner, path), [])
    if lines:
        return min(lines), max(lines), "reviewed-seam-anchor"
    return 1, min(1, len((root / path).read_bytes().splitlines())), "reviewed-file-anchor"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-graph", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=Path("docs/dependencies/reviewed/source-baselines.yaml"))
    parser.add_argument("--source-root", action="append", required=True, type=parse_owner_root)
    parser.add_argument("--setup-evidence", type=Path, default=Path("docs/tasks/SETUP-004/evidence"))
    parser.add_argument("--compile-commands", type=Path, default=Path("docs/tasks/SETUP-003/generated/compile-commands.json"))
    parser.add_argument(
        "--phase-a-evidence",
        type=Path,
        default=Path("docs/tasks/PORT-003/phase-a/evidence/build-closure.yaml"),
        help="observed PORT-003 Phase A application closure, when present",
    )
    parser.add_argument("--prior-graph", type=Path, help="previous official-tag graph; newly appearing files default to unresolved")
    parser.add_argument("--output", type=Path, default=Path("docs/dependencies/generated/code-graph.yaml"))
    args = parser.parse_args()

    repository_root = Path.cwd().resolve()
    base_path = args.base_graph.resolve()
    baseline_path = args.baseline.resolve()
    evidence_dir = args.setup_evidence.resolve()
    compile_commands_path = args.compile_commands.resolve()
    phase_a_path = args.phase_a_evidence.resolve()
    roots = dict(args.source_root)
    base = load_data(base_path)
    prior = load_data(args.prior_graph.resolve()) if args.prior_graph else None
    prior_files = (
        {
            (node["owner"], node["properties"]["source.path"])
            for node in prior["nodes"]
            if node["kind"] == "file"
        }
        if prior
        else set()
    )
    baseline = load_data(baseline_path)
    source_by_owner = {item["owner"]: item for item in baseline["sources"]}
    if sorted(roots) != sorted(source_by_owner):
        raise ValueError("source roots must exactly match reviewed baseline owners")

    dispositions, entry_lines = accepted_dispositions(evidence_dir)
    direct = direct_build_inputs(compile_commands_path)
    old_file_nodes = {
        (node["owner"], node.get("properties", {}).get("source.path")): node
        for node in base["nodes"]
        if node["kind"] == "file"
    }
    observed_selected = {
        key for key, node in old_file_nodes.items() if node.get("build_selection") == "selected"
    }

    inputs = [item for item in base["inputs"] if not item["id"].startswith("input:port-001:")]
    new_inputs = [
        {
            "id": "input:port-002:base-code-graph",
            "path": base_path.relative_to(repository_root).as_posix(),
            "role": "PORT-001 mechanical and reviewed relationship graph",
            "schema_version": base["schema_version"],
            "sha256": sha256_file(base_path),
        },
        {
            "id": "input:port-002:setup-004-evidence",
            "path": evidence_dir.relative_to(repository_root).as_posix(),
            "role": "accepted source disposition records",
            "schema_version": 1,
            "sha256": hash_paths(repository_root, [p.relative_to(repository_root).as_posix() for p in sorted(evidence_dir.glob("work-1*.yaml"))]),
        },
    ]
    inputs.extend(new_inputs)
    phase_a = load_data(phase_a_path) if phase_a_path.is_file() else None
    if phase_a:
        if not phase_a.get("summary", {}).get("closure_proved"):
            raise ValueError(f"{phase_a_path}: Phase A closure is not proved")
        inputs.append(
            {
                "id": "input:port-003:phase-a-build-closure",
                "path": phase_a_path.relative_to(repository_root).as_posix(),
                "role": "observed PORT-003 Phase A application compile/link closure",
                "schema_version": phase_a["schema_version"],
                "sha256": sha256_file(phase_a_path),
            }
        )
    if args.prior_graph:
        prior_path = args.prior_graph.resolve()
        inputs.append(
            {
                "id": "input:port-002:prior-tag-graph",
                "path": prior_path.relative_to(repository_root).as_posix(),
                "role": "previous official-tag graph for new-file detection",
                "schema_version": prior["schema_version"],
                "sha256": sha256_file(prior_path),
            }
        )
    input_ids = {item["id"] for item in inputs}
    compile_input_id = next(item["id"] for item in inputs if item["path"].endswith("compile-commands.json"))

    evidence = list(base["evidence"])
    observed_evidence = add_artifact_evidence(
        evidence,
        "evidence:build-profile:upstream-control",
        compile_input_id,
        "/",
        "Successful upstream ESP32 control-build compilation database and include closure.",
    )
    disposition_evidence = add_artifact_evidence(
        evidence,
        "evidence:reviewed:setup-004-dispositions",
        "input:port-002:setup-004-evidence",
        "/records",
        "Accepted SETUP-004 retain, replace, and omit dispositions.",
    )
    baseline_input_id = next(item["id"] for item in inputs if item["path"].endswith("source-baselines.yaml"))
    manifest_evidence: dict[str, str] = {}

    nodes = [dict(node) for node in base["nodes"] if node["kind"] != "file"]
    for node in nodes:
        node.pop("build_selection", None)
    edges = list(base["edges"])
    selection_records: list[dict[str, Any]] = []
    exhaustive_paths: dict[str, list[str]] = {}
    file_nodes: dict[tuple[str, str], dict[str, Any]] = {}

    sources = []
    base_sources = {item["owner"]: dict(item) for item in base["sources"]}
    for owner in sorted(source_by_owner):
        baseline_source = source_by_owner[owner]
        paths = source_files(roots[owner], baseline_source.get("commit"))
        managed_paths = {
            path: managed_repository_path(repository_root, baseline_source, path)
            for path in paths
        }
        managed_presence = baseline_source.get("managed_import", {}).get(
            "presence_class", "upstream-reference"
        )
        for path, repository_path in managed_paths.items():
            if repository_path is None:
                continue
            if not repository_path.is_file():
                raise FileNotFoundError(
                    f"{owner}:{path}: managed import is missing: {repository_path}"
                )
            source_hash = sha256_file(roots[owner] / path)
            managed_hash = sha256_file(repository_path)
            if managed_hash != source_hash:
                raise ValueError(
                    f"{owner}:{path}: managed import differs from immutable source "
                    f"({managed_hash} != {source_hash})"
                )
        exhaustive_paths[owner] = paths
        source = base_sources[owner]
        source["tree_sha256"] = hash_paths(roots[owner], paths)
        source["manifest_file_count"] = len(paths)
        source["presence_class"] = managed_presence
        sources.append(source)
        evidence_key = evidence_id("reviewed", owner, baseline_path.name, 1, "exhaustive-source-manifest")
        manifest_evidence[owner] = add_artifact_evidence(
            evidence,
            evidence_key,
            baseline_input_id,
            f"/sources/{owner}",
            f"Exhaustive immutable file manifest for {owner} {baseline_source['identity']}.",
        )

        for path in paths:
            key = (owner, path)
            node_id = typed_id("file", owner, path)
            previous = old_file_nodes.get(key)
            evidence_ids = merge_evidence_ids(previous.get("evidence_ids", []) if previous else [], [manifest_evidence[owner]])
            role = file_role(path)
            source_properties = {
                **(previous.get("properties", {}) if previous else {}),
                "source.path": path,
                "source.sha256": sha256_file(roots[owner] / path),
                "source.role": role,
                "source.presence_class": managed_presence,
                "source.identity": baseline_source["identity"],
            }
            if managed_paths[path] is not None:
                source_properties["source.repository_path"] = managed_paths[path].relative_to(
                    repository_root
                ).as_posix()
            node = {
                "id": node_id,
                "kind": "file",
                "owner": owner,
                "label": path,
                "locations": previous.get("locations", []) if previous else [],
                "evidence_ids": evidence_ids,
                "properties": source_properties,
            }
            file_nodes[key] = node
            nodes.append(node)

            file_dispositions = dispositions.get(key, [])
            observed_status = (
                "not-applicable"
                if role in NON_RUNTIME_ROLES
                else "selected" if key in observed_selected else "available-not-selected"
            )
            target_status = declared_target_status(
                role,
                observed_status,
                file_dispositions,
                prior is not None and key not in prior_files,
            )

            observed_causes: list[dict[str, Any]] = []
            if observed_status == "selected":
                code = "direct-build-input" if key in direct else "transitive-include"
                observed_causes.append(cause(code, "mechanical", "selects", [observed_evidence]))
            elif observed_status == "not-applicable":
                observed_causes.append(cause("non-runtime-upstream-content", "reviewed", "explains-presence", [manifest_evidence[owner]]))
            else:
                observed_causes.append(cause("build-rule-match", "mechanical", "does-not-select", [observed_evidence]))
            selection_records.append(selection_record(OBSERVED_PROFILE, node_id, observed_status, observed_causes))

            file_dispositions = dispositions.get(key, [])
            retain = [item for item in file_dispositions if item["disposition"] == "retain"]
            negative = [item for item in file_dispositions if item["disposition"] in {"omit", "replace"}]
            whole_negative = [item for item in negative if item["whole_file"]]
            region_negative = [item for item in negative if not item["whole_file"]]
            decision_refs = ["docs/decisions/ADR-0011-upstream-vdp-integration-and-project-structure.md"]
            decision_refs.extend(f"{item['work_item']}:{item['id']}" for item in file_dispositions)
            if target_status == "selected":
                target_causes = [cause("retained-compatibility-requirement", "reviewed", "selects", [disposition_evidence], decision_refs)]
                if not retain and observed_status == "selected":
                    target_causes.append(
                        cause(
                            "inherited-broad-build-selection",
                            "reviewed",
                            "selects",
                            [observed_evidence],
                            decision_refs,
                        )
                    )
            elif target_status == "excluded":
                target_causes = [cause("deliberate-exclusion", "reviewed", "excludes", [disposition_evidence], decision_refs)]
            elif target_status == "not-applicable":
                target_causes = [cause("non-runtime-upstream-content", "reviewed", "explains-presence", [manifest_evidence[owner]], decision_refs)]
            elif target_status == "unresolved":
                target_causes = [cause("unresolved-selection", "reviewed", "marks-unresolved", [manifest_evidence[owner]], decision_refs)]
            else:
                target_causes = [cause("build-rule-match", "mechanical", "does-not-select", [observed_evidence], decision_refs)]
            replacement_id = None
            if target_status == "excluded" and any(item["disposition"] == "replace" for item in whole_negative):
                replacement_id = "build-unit:extender:p4-port-adapters"
            entry_points = sorted({node_id for item in retain for node_id in item["graph_node_ids"]})
            governing_dispositions = whole_negative if target_status == "excluded" else file_dispositions
            selection_records.append(
                selection_record_value := selection_record(
                    TARGET_PROFILE,
                    node_id,
                    target_status,
                    target_causes,
                    dispositions=governing_dispositions,
                    entry_points=entry_points,
                    replacement_subject_id=replacement_id,
                )
            )
            if target_status != observed_status:
                selection_record_value["drift_from_status"] = observed_status
                selection_record_value["drift_disposition"] = "expected-port-selection"
            if target_status == "unresolved":
                selection_record_value["unresolved_reason"] = (
                    "File is new relative to the supplied prior official-tag graph and has no accepted selection disposition."
                )

            # Mixed dispositions require narrower target records; file-level
            # selection remains truthful while the seam is visibly excluded.
            if target_status == "selected" and region_negative:
                for disposition in region_negative:
                    start, end, boundary_status = region_span_for(disposition, owner, path, roots[owner], entry_lines)
                    span = source_span(source["id"], roots[owner], path, start, end)
                    region_evidence_id = evidence_id("reviewed", owner, path, start, disposition["id"])
                    evidence.append(
                        {
                            "id": region_evidence_id,
                            "kind": "reviewed-analysis",
                            "method": "reviewed",
                            "description": f"Reviewed source-selection seam for {disposition['name']}.",
                            "span": span,
                            "review": {
                                "status": "accepted",
                                "reviewed_on": "2026-08-22",
                                "basis": f"Accepted {disposition['work_item']} disposition {disposition['id']}.",
                            },
                        }
                    )
                    region_id = typed_id("source-region", owner, path, disposition["id"])
                    nodes.append(
                        {
                            "id": region_id,
                            "kind": "source-region",
                            "owner": owner,
                            "label": disposition["name"],
                            "locations": [span],
                            "evidence_ids": [region_evidence_id],
                            "properties": {
                                "region.parent_file_id": node_id,
                                "region.disposition": disposition["disposition"],
                                "region.boundary_status": boundary_status,
                                "region.candidate_id": disposition["id"],
                            },
                        }
                    )
                    edges.append(
                        {
                            "id": edge_id(node_id, "contains", region_id),
                            "from": node_id,
                            "to": region_id,
                            "relation": "contains",
                            "confidence": "confirmed",
                            "evidence_ids": [region_evidence_id],
                        }
                    )
                    replacement = "build-unit:extender:p4-port-adapters" if disposition["disposition"] == "replace" else None
                    selection_records.append(
                        selection_record(
                            TARGET_PROFILE,
                            region_id,
                            "excluded",
                            [cause("deliberate-exclusion", "reviewed", "excludes", [region_evidence_id, disposition_evidence], [f"{disposition['work_item']}:{disposition['id']}"])],
                            dispositions=[disposition],
                            replacement_subject_id=replacement,
                        )
                    )

    adapter_evidence_id = add_artifact_evidence(
        evidence,
        "evidence:reviewed:p4-port-adapter-boundary",
        "input:port-002:setup-004-evidence",
        "/records/*/disposition=replace",
        "Accepted replace dispositions require project-owned P4 adapter implementations.",
    )
    adapter_evidence_ids = [adapter_evidence_id]
    phase_a_evidence_id = None
    if phase_a:
        phase_a_evidence_id = "evidence:build-profile:port-003-phase-a"
        evidence.append(
            {
                "id": phase_a_evidence_id,
                "kind": "build-log",
                "method": "mechanical",
                "description": (
                    "Successful PORT-003 Phase A P4 diagnostic compile/link closure; "
                    "not hardware or rendering qualification."
                ),
                "artifact_id": "input:port-003:phase-a-build-closure",
                "record_pointer": "/application_translation_units",
            }
        )
        adapter_evidence_ids.append(phase_a_evidence_id)
    nodes.append(
        {
            "id": "build-unit:extender:p4-port-adapters",
            "kind": "build-unit",
            "owner": "extender",
            "label": "Project-owned P4 port adapters",
            "locations": [],
            "evidence_ids": adapter_evidence_ids,
            "properties": {
                "port.state": "phase-a-partial" if phase_a else "planned",
                "port.task": "PORT-003",
            },
        }
    )
    if phase_a and phase_a_evidence_id:
        project_units = [
            (
                "build-unit:extender:p4-display-contract-canary",
                "PORT-003 Phase A display contract canary",
                "video/extender/canary/display_contract_canary.cpp",
                "diagnostic-canary",
            ),
            (
                "build-unit:extender:p4-display-controller-contract",
                "P4 concrete display-controller contract skeleton",
                "video/extender/display/p4_display_controller.cpp",
                "contract-only",
            ),
            (
                "build-unit:extender:p4-vdp-gl-port-utility-closure",
                "P4 vdp-gl utility compatibility closure",
                "video/extender/port/fabutils_port.cpp",
                "phase-a-narrow-port",
            ),
        ]
        for unit_id, label, path, state in project_units:
            nodes.append(
                {
                    "id": unit_id,
                    "kind": "build-unit",
                    "owner": "extender",
                    "label": label,
                    "locations": [],
                    "evidence_ids": [phase_a_evidence_id],
                    "properties": {
                        "project.path": path,
                        "port.state": state,
                        "port.task": "PORT-003",
                    },
                }
            )
        phase_edges = [
            (
                "build-unit:extender:p4-display-contract-canary",
                "depends-on",
                "build-unit:extender:p4-display-controller-contract",
            ),
            (
                "build-unit:extender:p4-display-contract-canary",
                "depends-on",
                "build-unit:extender:p4-vdp-gl-port-utility-closure",
            ),
            (
                "build-unit:extender:p4-display-contract-canary",
                "depends-on",
                "file:vdp-gl:src/canvas.cpp",
            ),
            (
                "build-unit:extender:p4-display-contract-canary",
                "depends-on",
                "file:vdp-gl:src/displaycontroller.cpp",
            ),
            (
                "build-unit:extender:p4-display-controller-contract",
                "depends-on",
                "type:vdp-gl:fabgl::GenericBitmappedDisplayController",
            ),
            (
                "build-unit:extender:p4-vdp-gl-port-utility-closure",
                "depends-on",
                "file:vdp-gl:src/fabutils.cpp",
            ),
        ]
        for source_id, relation, target_id in phase_edges:
            edges.append(
                {
                    "id": edge_id(source_id, relation, target_id),
                    "from": source_id,
                    "to": target_id,
                    "relation": relation,
                    "confidence": "confirmed",
                    "evidence_ids": [phase_a_evidence_id],
                }
            )

    build_profiles = [
        {
            "id": OBSERVED_PROFILE,
            "label": "Official Agon VDP v2.16.0 ESP32 control build",
            "profile_kind": "observed-build",
            "target_board": "Espressif ESP32-PICO-D4 / upstream esp32dev environment",
            "platform": "upstream PlatformIO environment",
            "framework": "Arduino",
            "configuration": "agon-vdp v2.16.0 platformio.ini [env:esp32dev]",
            "source_ids": sorted(source["id"] for source in sources),
            "evidence_ids": [observed_evidence],
        },
        {
            "id": TARGET_PROFILE,
            "label": "Agon Extender ESP32-P4 default target",
            "profile_kind": "declared-target",
            "target_board": "Olimex ESP32-P4-DevKit",
            "platform": "pioarduino 55.03.311",
            "framework": "Arduino and ESP-IDF hybrid",
            "configuration": "declared source-selection target; firmware build not yet implemented",
            "source_ids": sorted(source["id"] for source in sources),
            "evidence_ids": [disposition_evidence],
            "drift_against_profile_id": OBSERVED_PROFILE,
        },
    ]

    generator_argv = [
        ".venv/bin/python",
        "docs/dependencies/scripts/build-source-selection.py",
        "--base-graph",
        "docs/dependencies/generated/base-code-graph.yaml",
        "--baseline",
        "docs/dependencies/reviewed/source-baselines.yaml",
        *sum((["--source-root", f"{owner}={source_by_owner[owner]['root_placeholder']}"] for owner in sorted(roots)), []),
    ]
    if args.prior_graph:
        generator_argv.extend(
            ["--prior-graph", args.prior_graph.resolve().relative_to(repository_root).as_posix()]
        )
    generator_argv.extend(["--output", "docs/dependencies/generated/code-graph.yaml"])

    output = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "code_graph",
        "id": "graph:agon-extender:vdp-source-selection-v2",
        "generator": {
            "name": "build-source-selection",
            "version": GENERATOR_VERSION,
            "path": "docs/dependencies/scripts/build-source-selection.py",
            "argv": generator_argv,
        },
        "sources": sources,
        "inputs": inputs,
        "tools": base["tools"],
        "vocabulary": {
            "node_kinds": NODE_KINDS,
            "relations": RELATIONS,
            "selection_statuses": ["selected", "excluded", "available-not-selected", "not-applicable", "unresolved"],
            "selection_causes": [
                "direct-build-input",
                "build-rule-match",
                "transitive-include",
                "header-defined-implementation",
                "generated-build-input",
                "retained-compatibility-requirement",
                "project-adapter",
                "inherited-broad-build-selection",
                "deliberate-exclusion",
                "non-runtime-upstream-content",
                "unresolved-selection",
            ],
        },
        "build_profiles": build_profiles,
        "evidence": evidence,
        "nodes": nodes,
        "edges": edges,
        "selection_records": selection_records,
        "unresolved": base.get("unresolved", []),
    }
    canonicalize_graph_collections(output)
    write_canonical(args.output.resolve(), output)
    print(
        f"wrote {len(nodes)} nodes, {len(edges)} edges, {len(selection_records)} selection records, "
        f"{sum(len(paths) for paths in exhaustive_paths.values())} manifest files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
