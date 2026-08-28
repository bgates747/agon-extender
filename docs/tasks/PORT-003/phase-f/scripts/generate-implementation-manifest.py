#!/usr/bin/env python3
"""Generate the deterministic PORT-003 Phase F implementation manifest.

The manifest joins already-generated, independently validated authorities. It
does not infer qualification from a successful build. Candidate identity and
procedure approval remain distinct from the later identified build and the
separately authorized hardware run.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]

CONTRACT_PATHS = [
    "docs/tasks/PORT-003/phase-f/contracts.md",
    "docs/tasks/PORT-003/phase-f/boot-closure.yaml",
    "docs/tasks/PORT-003/phase-f/network-service-contract.yaml",
    "docs/tasks/PORT-003/phase-f/fixtures/snapshot-pool-model.yaml",
    "docs/tasks/PORT-003/phase-f/fixtures/evf1-contract.yaml",
    "docs/tasks/PORT-003/phase-f/fixtures/independent-fixtures.yaml",
    "docs/tasks/PORT-003/phase-f/fixtures/visible-vdu-command-expected.svg",
    "docs/tasks/PORT-003/phase-f/compatibility-delta.md",
    "docs/procedures/p4-browser-video-qualification-r01.md",
]

EVIDENCE_PATHS = [
    "docs/tasks/PORT-003/phase-f/evidence/source-provenance.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/source-provenance.md",
    "docs/tasks/PORT-003/phase-f/evidence/snapshot-model-check.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/evf1-contract-check.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/network-contract-check.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/independent-fixtures-check.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/browser-test-results.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/host-regression-results.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/build-closure.yaml",
    "docs/tasks/PORT-003/phase-f/evidence/link-exclusions.yaml",
]

DEPENDENCY_PATHS = [
    "docs/dependencies/reviewed/source-baselines.yaml",
    "docs/dependencies/generated/code-graph.yaml",
    "docs/dependencies/generated/source-selection.yaml",
    "docs/dependencies/generated/source-selection.md",
    "docs/dependencies/generated/port-002-proof.yaml",
]


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def fingerprint(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def require_passed_evidence() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    closure = load_yaml(ROOT / "docs/tasks/PORT-003/phase-f/evidence/build-closure.yaml")
    exclusions = load_yaml(ROOT / "docs/tasks/PORT-003/phase-f/evidence/link-exclusions.yaml")
    regressions = load_yaml(ROOT / "docs/tasks/PORT-003/phase-f/evidence/host-regression-results.yaml")
    if not closure.get("summary", {}).get("closure_proved"):
        raise ValueError("Phase F build closure is not proved")
    if not exclusions.get("summary", {}).get("exclusions_proved"):
        raise ValueError("Phase F exclusions are not proved")
    summary = regressions.get("summary", {})
    if summary.get("failed") != 0 or summary.get("passed", 0) < 1:
        raise ValueError("Phase F host regression gate is not passing")
    return closure, exclusions, regressions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-f/implementation-manifest.yaml",
    )
    args = parser.parse_args()

    closure, exclusions, regressions = require_passed_evidence()
    provenance = load_yaml(
        ROOT / "docs/tasks/PORT-003/phase-f/evidence/source-provenance.yaml"
    )
    selection_path = "vdp/pio/p4-browser-vdp-source-selection.json"
    import json

    selection = json.loads((ROOT / selection_path).read_text(encoding="utf-8"))
    if selection.get("environment") != "p4-browser-vdp":
        raise ValueError("source selection describes another environment")

    project_authority = next(
        item for item in provenance["authorities"]
        if item["repository"] == "agon-extender"
    )
    source_groups: dict[str, list[dict[str, Any]]] = {}
    for record in provenance["records"]:
        if record["repository"] != "agon-extender":
            continue
        source_groups.setdefault(record["group"], []).append(
            {
                "path": record["path"],
                "bytes": record["bytes"],
                "sha256": record["sha256"],
            }
        )
    source_groups = {
        group: sorted(records, key=lambda item: item["path"])
        for group, records in sorted(source_groups.items())
    }

    baseline = load_yaml(ROOT / "docs/dependencies/reviewed/source-baselines.yaml")
    agon_vdp = next(item for item in baseline["sources"] if item["owner"] == "agon-vdp")
    patched = []
    for item in agon_vdp["managed_import"]["patched_paths"]:
        repository_path = f"vdp/{item['path']}"
        patched.append(
            {
                "path": repository_path,
                "upstream_path": item["path"],
                "decision_ref": item["decision_ref"],
                "repository_sha256": sha256_file(ROOT / repository_path),
            }
        )

    document = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_implementation_manifest",
        "status": "candidate-freeze",
        "authority": "docs/tasks/PORT-003.md#phase-f--browser-video-handoff-and-bootable-port",
        "phase_contract": (
            "bootable retained VDP with immutable RGB888 browser handoff and "
            "direct P4 wired service; no VDU ingress, return transport, or hardware claim"
        ),
        "source_state": {
            "ref": project_authority["ref"],
            "base_commit": project_authority["base_commit"],
            "state": project_authority["state"],
            "candidate_commit": None,
        },
        "identity": {
            "source_identity": "extender-vdp-v0.1.0",
            "build_id": None,
            "artifact_status": "candidate",
            "procedure_identity": "p4-browser-video-qualification-r01",
            "candidate_inputs_approved": True,
            "identified_build_pending": True,
            "hardware_authorization_required": True,
            "deployment_allowed": False,
        },
        "source_baselines": [
            {
                "owner": item["owner"],
                "identity": item["identity"],
                "commit": item.get("commit"),
            }
            for item in baseline["sources"]
        ],
        "source_selection": {
            "path": selection_path,
            "sha256": sha256_file(ROOT / selection_path),
            "environment": selection["environment"],
            "project_translation_units": selection["project_translation_units"],
            "vendored_translation_units": selection["vendored_translation_units"],
            "embedded_text_files": selection["embedded_text_files"],
            "header_defined_official_implementation": selection[
                "header_defined_official_implementation"
            ],
        },
        "bounded_sources": source_groups,
        "patched_vendor_files": sorted(patched, key=lambda item: item["path"]),
        "contracts_and_fixtures": [fingerprint(path) for path in CONTRACT_PATHS],
        "generated_evidence": [fingerprint(path) for path in EVIDENCE_PATHS],
        "dependency_artifacts": [fingerprint(path) for path in DEPENDENCY_PATHS],
        "predeployment_build": {
            "environment": closure["environment"],
            "identity_state": closure["identity"]["identity_state"],
            "rejected_identity_marker_present": closure["identity"][
                "rejected_marker_present"
            ],
            "firmware": closure["firmware"],
            "factory_firmware": closure["factory_firmware"],
            "selected_translation_unit_count": closure["summary"][
                "selected_translation_unit_count"
            ],
            "embedded_asset_count": len(closure["embedded_assets"]),
            "host_regression_passed": regressions["summary"]["passed"],
            "host_regression_failed": regressions["summary"]["failed"],
            "exclusions_proved": exclusions["summary"]["exclusions_proved"],
            "deploy": "forbidden-until-identified-committed-rebuild-and-author-approval",
        },
        "deferred_owners": {
            "PORT-008": ["parallel VDU ingress", "return UART", "EMOS command fixture"],
            "PORT-004": ["audio scheduler", "network audio sink"],
            "PORT-005": ["processed input source"],
            "PORT-006": ["services beyond the narrow browser-video foundation"],
            "PORT-007": ["P4 microSD storage"],
            "MODE-001": ["runtime operating-mode transitions"],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(document, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
