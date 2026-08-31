#!/usr/bin/env python3
"""Stage one clean, identified PORT-008 P4 forward candidate.

PORT-003 owns the factory-image consistency and provenance implementation.
This adapter selects the forward environment and replaces the Phase-F-only
claim with the narrower PORT-008 candidate configuration.  It never flashes
hardware.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
PHASE_F_STAGER = (
    ROOT / "docs/tasks/PORT-003/phase-f/scripts/stage-identified-build.py"
)
ENVIRONMENT = "p4-forward-vdp"


def load_phase_f_stager() -> Any:
    spec = importlib.util.spec_from_file_location(
        "port003_phase_f_build_stager", PHASE_F_STAGER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {PHASE_F_STAGER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=ROOT / f"vdp/.pio/build/{ENVIRONMENT}",
    )
    parser.add_argument("--closure", type=Path, required=True)
    parser.add_argument("--exclusions", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    phase_f = load_phase_f_stager()
    phase_f.ENVIRONMENT = ENVIRONMENT
    delegated_argv = [
        str(PHASE_F_STAGER),
        "--build-id",
        args.build_id,
        "--commit",
        args.commit,
        "--build-dir",
        str(args.build_dir),
        "--closure",
        str(args.closure),
        "--exclusions",
        str(args.exclusions),
        "--output-dir",
        str(args.output_dir),
    ]
    original_argv = sys.argv
    try:
        sys.argv = delegated_argv
        result = phase_f.main()
    finally:
        sys.argv = original_argv

    manifest_path = args.output_dir.resolve() / f"{args.build_id}.manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{manifest_path}: expected YAML mapping")
    manifest["generated_by"] = (
        "docs/tasks/PORT-008/forward-r01/scripts/stage-forward-build.py"
    )
    manifest["derived_from_generator"] = (
        "docs/tasks/PORT-003/phase-f/scripts/stage-identified-build.py"
    )
    manifest["provenance"]["configuration"] = [
        {
            "artifact_id": "olimex-p4-devkit-profile",
            "identity": "olimex-p4-devkit-profile-r03",
        },
        {
            "artifact_id": "p4-ota-partition-layout",
            "identity": "p4-ota-partition-layout-r01",
        },
        {
            "artifact_id": "p4-browser-video-qualification",
            "identity": "p4-browser-video-qualification-r01",
            "role": "retained display/browser prerequisite",
        },
        {
            "artifact_id": "light2-harness",
            "identity": "light2-harness-r01",
        },
        {
            "artifact_id": "port-008-forward-qualification",
            "identity": "port-008-forward-qualification-r01",
        },
    ]
    manifest["compatibility"] = {
        "provides": [
            "retained-vdp-p4-browser-video-candidate",
            "light2-r01-forward-parallel-ingress-candidate",
            "discard-only-return-sink",
        ],
        "requires": [
            "olimex-p4-devkit-profile-r03",
            "p4-ota-partition-layout-r01",
            "light2-harness-r01",
        ],
    }
    manifest["qualification"] = {
        "procedure": "port-008-forward-qualification-r01",
        "state": "not-run",
        "hardware_authorized": False,
        "claim_boundary": (
            "identified P4 candidate with retained browser video and r01 "
            "forward ingress; no deployment, physical transfer, return UART, "
            "sysvar, r02/V1, or broad compatibility claim"
        ),
    }
    manifest["notes"] = [
        "Factory segment equality was verified for bootloader, partition table, OTA data, and application.",
        "The PORT-008 validator extended the retained Phase-F closure with the selected ForwardParallelStream and discard-only return requirements.",
        "Physical deployment remains forbidden until the Author separately authorizes the reviewed PORT-008 procedure.",
    ]
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )
    print(manifest_path)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
