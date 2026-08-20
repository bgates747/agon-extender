#!/usr/bin/env python3
"""Validate tracked version registries and manifest templates.

This intentionally checks project policy that a generic YAML parser cannot:
artifact-name syntax, lifecycle values, identity schemes, duplicate names, and
the required top-level shape of each record type. It does not invent missing
values or treat templates' deliberate null placeholders as completed records.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
REVISION = re.compile(r"^r(?:0[1-9]|[1-9][0-9]+)$")
SEMANTIC_VERSION = re.compile(
    r"^v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$"
)
STATUSES = {
    "draft",
    "experimental",
    "candidate",
    "qualified",
    "released",
    "deprecated",
    "rejected",
}
SCHEMES = {"revision", "semantic_version"}


def fail(message: str) -> None:
    raise ValueError(message)


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = REPOSITORY_ROOT / relative_path
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        fail(f"{relative_path}: root must be a mapping")
    if value.get("schema_version") != 1:
        fail(f"{relative_path}: schema_version must be 1")
    return value


def require_mapping(record: dict[str, Any], key: str, path: str) -> None:
    if not isinstance(record.get(key), dict):
        fail(f"{path}: {key} must be a mapping")


def require_list(record: dict[str, Any], key: str, path: str) -> None:
    if not isinstance(record.get(key), list):
        fail(f"{path}: {key} must be a list")


def validate_artifacts() -> None:
    path = "docs/versions/artifacts.yaml"
    record = load_yaml(path)
    if not REVISION.fullmatch(str(record.get("registry_revision", ""))):
        fail(f"{path}: registry_revision must be r01 or greater")
    require_list(record, "artifacts", path)

    seen: set[str] = set()
    for index, artifact in enumerate(record["artifacts"]):
        label = f"{path}: artifacts[{index}]"
        if not isinstance(artifact, dict):
            fail(f"{label} must be a mapping")
        artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str) or not ARTIFACT_ID.fullmatch(artifact_id):
            fail(f"{label}: invalid artifact_id {artifact_id!r}")
        if artifact_id in seen:
            fail(f"{label}: duplicate artifact_id {artifact_id}")
        seen.add(artifact_id)

        scheme = artifact.get("identity_scheme")
        if scheme not in SCHEMES:
            fail(f"{label}: invalid identity_scheme {scheme!r}")
        if artifact.get("status") not in STATUSES:
            fail(f"{label}: invalid status {artifact.get('status')!r}")
        if not isinstance(artifact.get("variants"), list):
            fail(f"{label}: variants must be a list")

        identity = artifact.get("latest_identity")
        if identity is None:
            continue
        prefix = f"{artifact_id}-"
        if not isinstance(identity, str) or not identity.startswith(prefix):
            fail(f"{label}: latest_identity must begin with {prefix}")
        suffix = identity[len(prefix) :]
        pattern = REVISION if scheme == "revision" else SEMANTIC_VERSION
        if not pattern.fullmatch(suffix):
            fail(f"{label}: latest_identity does not match {scheme}")


def validate_templates() -> None:
    build_path = "docs/versions/build-manifest.template.yaml"
    build = load_yaml(build_path)
    require_mapping(build, "build", build_path)
    require_mapping(build, "provenance", build_path)
    require_mapping(build, "compatibility", build_path)
    require_list(build, "outputs", build_path)

    baseline_path = "docs/versions/baselines/TEMPLATE.yaml"
    baseline = load_yaml(baseline_path)
    require_mapping(baseline, "baseline", baseline_path)
    require_list(baseline, "artifacts", baseline_path)
    require_list(baseline, "external_dependencies", baseline_path)
    require_mapping(baseline, "compatibility", baseline_path)
    require_mapping(baseline, "qualification", baseline_path)

    run_path = "tests/runs/TEMPLATE/manifest.yaml"
    run = load_yaml(run_path)
    require_mapping(run, "run", run_path)
    require_mapping(run, "procedure", run_path)
    require_list(run, "artifacts_under_test", run_path)
    require_list(run, "base_hardware", run_path)
    require_mapping(run, "compatibility_checked", run_path)
    require_list(run, "evidence", run_path)


def validate_vdp_source_identity() -> None:
    path = "vdp/version.yaml"
    record = load_yaml(path)
    artifact_id = record.get("artifact_id")
    identity = record.get("identity")
    if not isinstance(artifact_id, str) or not ARTIFACT_ID.fullmatch(artifact_id):
        fail(f"{path}: invalid artifact_id {artifact_id!r}")
    if not isinstance(identity, str) or not identity.startswith(f"{artifact_id}-"):
        fail(f"{path}: identity must begin with {artifact_id}-")
    if not REVISION.fullmatch(identity[len(artifact_id) + 1 :]):
        fail(f"{path}: canary identity must end in a valid revision")
    if record.get("status") not in STATUSES:
        fail(f"{path}: invalid status {record.get('status')!r}")
    require_list(record, "configuration", path)
    require_mapping(record, "compatibility", path)


def main() -> int:
    try:
        validate_artifacts()
        validate_templates()
        validate_vdp_source_identity()
    except (OSError, yaml.YAMLError, ValueError) as error:
        print(f"version-record validation failed: {error}", file=sys.stderr)
        return 1
    print("version-record validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
