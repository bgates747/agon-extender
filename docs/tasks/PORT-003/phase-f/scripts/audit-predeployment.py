#!/usr/bin/env python3
"""Fail-closed PORT-003 Phase F candidate-freeze audit.

The audit describes the deliberately uncommitted candidate input set and
validates its generated authorities after the Author has approved the source
identity and procedure. It never assigns a build ID, qualification result, or
deployment authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
DEFAULT_OUTPUT = ROOT / "docs/tasks/PORT-003/phase-f/evidence/predeployment-audit.yaml"
ALLOWED_CHANGED_PREFIXES = (
    "docs/dependencies/",
    "docs/procedures/",
    "docs/tasks/PORT-003/phase-b/",
    "docs/tasks/PORT-003/phase-c/",
    "docs/tasks/PORT-003/phase-d/",
    "docs/tasks/PORT-003/phase-e/",
    "docs/tasks/PORT-003/phase-f/",
    "vdp/pio/",
    "vdp/video/",
)
ALLOWED_CHANGED_EXACT = {
    "TODO.md",
    "docs/development/2026-08-27.md",
    "docs/development/2026-08-28.md",
    "docs/tasks/PORT-003.md",
    "docs/tasks/PORT-006.md",
    "docs/versions/artifacts.yaml",
    "scripts/vdp-pio.sh",
    "vdp/platformio.ini",
    "vdp/sdkconfig.defaults",
}
SENSITIVE_PATTERNS = {
    "absolute home path": re.compile("/" "home/"),
    "private IPv4 literal": re.compile(
        r"(?<![0-9])(?:10\.[0-9]{1,3}(?:\.[0-9]{1,3}){2}|"
        r"192\.168\.[0-9]{1,3}\.[0-9]{1,3}|"
        r"172\.(?:1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3})(?![0-9])"
    ),
    "bench USB identity": re.compile(
        "E8:F6" ":0A:E2:E1:60", re.IGNORECASE
    ),
}
LOCAL_LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_yaml(relative: str) -> dict[str, Any]:
    value = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative}: expected a YAML mapping")
    return value


def changed_paths(output: Path) -> list[dict[str, str]]:
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
    )
    fields = raw.decode("utf-8").split("\0")
    records: list[dict[str, str]] = []
    index = 0
    output_relative = output.resolve().relative_to(ROOT).as_posix()
    while index < len(fields) and fields[index]:
        entry = fields[index]
        status = entry[:2]
        path = entry[3:]
        if "R" in status or "C" in status:
            raise ValueError("rename/copy status is outside this bounded audit")
        index += 1
        if path == output_relative:
            continue
        records.append({"status": status, "path": path})
    return sorted(records, key=lambda item: item["path"])


def validate_links(paths: list[Path]) -> list[dict[str, str]]:
    checked: list[dict[str, str]] = []
    for path in paths:
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for match in LOCAL_LINK.finditer(text):
            target = match.group(1).strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            location = target.split("#", 1)[0]
            if not location:
                continue
            candidate = (path.parent / location).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError as error:
                raise ValueError(f"{path.relative_to(ROOT)}: link escapes project: {target}") from error
            if not candidate.exists():
                raise FileNotFoundError(
                    f"{path.relative_to(ROOT)}: missing local link target {target}"
                )
            checked.append(
                {
                    "document": path.relative_to(ROOT).as_posix(),
                    "target": target,
                }
            )
    return checked


def validate_manifest_fingerprints(manifest: dict[str, Any]) -> int:
    count = 0
    for section in (
        "contracts_and_fixtures", "generated_evidence", "dependency_artifacts"
    ):
        for record in manifest[section]:
            path = ROOT / record["path"]
            if path.stat().st_size != record["bytes"]:
                raise ValueError(f"manifest byte count mismatch: {record['path']}")
            if sha256_file(path) != record["sha256"]:
                raise ValueError(f"manifest hash mismatch: {record['path']}")
            count += 1
    return count


def validate_provenance(provenance: dict[str, Any]) -> int:
    count = 0
    for record in provenance["records"]:
        if record["repository"] != "agon-extender":
            continue
        path = ROOT / record["path"]
        if path.stat().st_size != record["bytes"]:
            raise ValueError(f"provenance byte count mismatch: {record['path']}")
        if sha256_file(path) != record["sha256"]:
            raise ValueError(f"provenance hash mismatch: {record['path']}")
        count += 1
    return count


def validate_patched_vendor_files(
    upstream_root: Path,
) -> tuple[int, list[str], list[str]]:
    baseline = load_yaml("docs/dependencies/reviewed/source-baselines.yaml")
    agon_vdp = next(item for item in baseline["sources"] if item["owner"] == "agon-vdp")
    declared = sorted(item["path"] for item in agon_vdp["managed_import"]["patched_paths"])
    observed = sorted(
        path.removeprefix("vdp/")
        for path in run("git", "diff", "--name-only", "--", "vdp/video").stdout.splitlines()
        if path.startswith("vdp/video/") and "/extender/" not in path
    )
    undeclared = sorted(set(observed) - set(declared))
    if undeclared:
        raise ValueError(
            f"current upstream-shaped changes are undeclared: {undeclared}"
        )
    for relative in declared:
        project = ROOT / "vdp" / relative
        upstream = upstream_root / relative
        if not project.is_file() or not upstream.is_file():
            raise FileNotFoundError(f"missing patched pair: {relative}")
        if project.read_bytes() == upstream.read_bytes():
            raise ValueError(f"declared patched path is byte-identical upstream: {relative}")
    return len(declared), declared, observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-vdp-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()

    records = changed_paths(output)
    if not records:
        raise ValueError("predeployment audit expected an uncommitted candidate")
    staged = [item for item in records if item["status"][0] not in (" ", "?")]
    if staged:
        raise ValueError(f"predeployment files are unexpectedly staged: {staged}")
    unexpected = [
        item["path"] for item in records
        if item["path"] not in ALLOWED_CHANGED_EXACT
        and not item["path"].startswith(ALLOWED_CHANGED_PREFIXES)
    ]
    if unexpected:
        raise ValueError(f"changed paths escape Phase F boundary: {unexpected}")

    paths = [ROOT / item["path"] for item in records]
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"candidate path is not a regular file: {path.relative_to(ROOT)}")
        data = path.read_bytes()
        if b"\0" in data:
            raise ValueError(f"unexpected binary candidate file: {path.relative_to(ROOT)}")
        text = data.decode("utf-8")
        if re.search(r"^(?:<<<<<<<|=======|>>>>>>>)", text, re.MULTILINE):
            raise ValueError(f"conflict marker in {path.relative_to(ROOT)}")
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                raise ValueError(f"{label} in tracked candidate: {path.relative_to(ROOT)}")

    yaml_count = 0
    json_count = 0
    for path in paths:
        if path.suffix.lower() in (".yaml", ".yml"):
            yaml.safe_load(path.read_text(encoding="utf-8"))
            yaml_count += 1
        elif path.suffix.lower() == ".json":
            json.loads(path.read_text(encoding="utf-8"))
            json_count += 1

    link_records = validate_links(paths)
    run("git", "diff", "--check")
    run("bash", "-n", "scripts/vdp-pio.sh")
    python_paths = [str(path) for path in paths if path.suffix == ".py"]
    if python_paths:
        run(str(ROOT / ".venv/bin/python"), "-m", "py_compile", *python_paths)

    selection = json.loads(
        (ROOT / "vdp/pio/p4-browser-vdp-source-selection.json").read_text(encoding="utf-8")
    )
    closure = load_yaml("docs/tasks/PORT-003/phase-f/evidence/build-closure.yaml")
    exclusions = load_yaml("docs/tasks/PORT-003/phase-f/evidence/link-exclusions.yaml")
    regressions = load_yaml("docs/tasks/PORT-003/phase-f/evidence/host-regression-results.yaml")
    provenance = load_yaml("docs/tasks/PORT-003/phase-f/evidence/source-provenance.yaml")
    manifest = load_yaml("docs/tasks/PORT-003/phase-f/implementation-manifest.yaml")
    dependency_proof = load_yaml("docs/dependencies/generated/port-002-proof.yaml")
    registry = load_yaml("docs/versions/artifacts.yaml")
    identity_record = json.loads(
        (ROOT / "vdp/pio/p4-browser-vdp-identity.json").read_text(encoding="utf-8")
    )

    selected = sorted(
        selection["project_translation_units"] + selection["vendored_translation_units"]
    )
    closure_selected = sorted(item["source"] for item in closure["application_translation_units"])
    if selected != closure_selected:
        raise ValueError("source selection and linked closure disagree")
    if selection["embedded_text_files"] != [
        item["source"] for item in closure["embedded_assets"]
    ]:
        raise ValueError("embedded source selection and linked closure disagree")
    if not closure["summary"]["closure_proved"]:
        raise ValueError("build closure is not proved")
    identity = closure["identity"]
    if identity["identity_state"] != "unversioned-do-not-deploy":
        raise ValueError("predeployment build unexpectedly has a deployable identity")
    if not identity["rejected_marker_present"] or identity["deployable_identity_proved"]:
        raise ValueError("predeployment identity fail-safe is not proved")
    if not exclusions["summary"]["exclusions_proved"]:
        raise ValueError("link exclusions are not proved")
    if regressions["summary"] != {"passed": 17, "failed": 0}:
        raise ValueError(f"unexpected host regression summary: {regressions['summary']}")
    if dependency_proof["summary"] != {"passed": 6, "failed": 0}:
        raise ValueError("dependency proof is not passing")

    project_authority = next(
        item for item in provenance["authorities"] if item["repository"] == "agon-extender"
    )
    if project_authority["ref"] != "working-tree" or project_authority["state"] != "modified":
        raise ValueError("predeployment provenance must describe the working tree honestly")
    if manifest["status"] != "candidate-freeze":
        raise ValueError("implementation manifest has the wrong review state")
    if manifest["identity"] != {
        "source_identity": "extender-vdp-v0.1.1",
        "build_id": None,
        "artifact_status": "candidate",
        "procedure_identity": "p4-browser-video-qualification-r01",
        "candidate_inputs_approved": True,
        "identified_build_pending": True,
        "hardware_authorization_required": True,
        "deployment_allowed": False,
    }:
        raise ValueError("implementation manifest lost the approved candidate controls")
    if manifest["predeployment_build"]["identity_state"] != "unversioned-do-not-deploy":
        raise ValueError("implementation manifest lost the rejected build marker")
    if identity_record != {
        "schema_version": 1,
        "artifact_id": "extender-vdp",
        "source_identity": "extender-vdp-v0.1.1",
        "status": "candidate",
        "variant": "olimex-p4-devkit",
    }:
        raise ValueError("committed build identity differs from the approved candidate")
    if registry.get("registry_revision") != "r13":
        raise ValueError("artifact registry is not approved revision r13")
    registry_by_id = {
        item["artifact_id"]: item for item in registry.get("artifacts", [])
    }
    for artifact_id, identity_value in (
        ("extender-vdp", "extender-vdp-v0.1.1"),
        (
            "p4-browser-video-qualification",
            "p4-browser-video-qualification-r01",
        ),
    ):
        record = registry_by_id.get(artifact_id, {})
        if (
            record.get("latest_identity") != identity_value
            or record.get("status") != "candidate"
        ):
            raise ValueError(f"registry lost candidate control {identity_value}")

    compatibility = (ROOT / "docs/tasks/PORT-003/phase-f/compatibility-delta.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "It adds no VDU command byte",
        "Required P4 and boot adaptations",
        "New output behavior outside the VDU wire contract",
        "Deliberate Phase F nonclaims",
    ):
        if phrase not in compatibility:
            raise ValueError(f"compatibility delta omits required boundary: {phrase}")
    procedure = (
        ROOT / "docs/procedures/p4-browser-video-qualification-r01.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "Status: Candidate — execution requires separate PORT-003 item 15 authorization",
        "extender-vdp-v0.1.1",
        "Registry revision: `r13`",
        "p4-browser-video-qualification-r01",
        "The Agon is physically disconnected",
        "must separately approve",
    ):
        if phrase not in procedure:
            raise ValueError(f"candidate procedure omits required gate: {phrase}")

    manifest_fingerprints = validate_manifest_fingerprints(manifest)
    provenance_fingerprints = validate_provenance(provenance)
    patched_count, patched_paths, currently_changed_patched_paths = validate_patched_vendor_files(
        args.upstream_vdp_root.resolve()
    )

    document = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_predeployment_audit",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/audit-predeployment.py",
        "status": "pass",
        "claim_boundary": (
            "approved identity and procedure with uncommitted candidate inputs; no "
            "committed candidate, identified build, target runtime, or hardware claim"
        ),
        "source_state": {
            "base_commit": run("git", "rev-parse", "HEAD").stdout.strip(),
            "worktree": "modified",
            "index": "clean",
            "deployment_allowed": False,
        },
        "changed_files": [
            {
                **record,
                "bytes": (ROOT / record["path"]).stat().st_size,
                "sha256": sha256_file(ROOT / record["path"]),
            }
            for record in records
        ],
        "validation": {
            "changed_file_count": len(records),
            "yaml_documents_parsed": yaml_count,
            "json_documents_parsed": json_count,
            "local_markdown_links_resolved": len(link_records),
            "python_files_compiled": len(python_paths),
            "shell_scripts_parsed": 1,
            "manifest_fingerprints_verified": manifest_fingerprints,
            "project_provenance_fingerprints_verified": provenance_fingerprints,
            "patched_upstream_files_verified": patched_count,
            "source_selection_matches_linked_closure": True,
            "embedded_assets_match_linked_closure": True,
            "host_regression_gates_passed": regressions["summary"]["passed"],
            "dependency_proofs_passed": dependency_proof["summary"]["passed"],
            "link_exclusions_proved": True,
            "compatibility_boundary_present": True,
            "identity_fail_safe_present": True,
            "approved_candidate_identity_frozen": True,
            "artifact_registry_revision": "r13",
            "candidate_procedure_remains_separately_gated": True,
            "private_machine_values_absent": True,
            "git_diff_check_passed": True,
        },
        "patched_upstream_paths": patched_paths,
        "currently_changed_patched_upstream_paths": currently_changed_patched_paths,
        "local_links": link_records,
        "result": "pass",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.safe_dump(document, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"Phase F predeployment audit passed: {len(records)} files, "
        f"{regressions['summary']['passed']} host gates, {patched_count} vendor patches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
