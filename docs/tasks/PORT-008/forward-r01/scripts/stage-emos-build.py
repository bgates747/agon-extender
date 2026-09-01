#!/usr/bin/env python3
"""Stage one clean, identified PORT-008 EMOS and fixture package.

The generic MOS port and EMOS repository own compilation and linked-image
checks. This task-local stager adds the candidate authority, clean-source,
identity, fixed-fixture, and immutable-output checks required before physical
deployment. It copies files only into a new ignored directory and never writes
an SD card or communicates with bench hardware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
CANDIDATE = ROOT / "docs/tasks/PORT-008/forward-r01/candidate.yaml"
SOURCE_IDENTITY = "agon-emos-v0.1.0"
ARTIFACT_STATUS = "candidate"
PROFILE = "port/port008-forward.mk"
BUILD_ID = re.compile(
    rf"^{re.escape(SOURCE_IDENTITY)}-b(\d{{4}})-(\d{{2}})-(\d{{2}})-"
    r"(\d{2})-(\d{2})-(\d{2})Z$"
)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_clean_commit(root: Path, expected: str, label: str) -> str:
    head = git(root, "rev-parse", "HEAD")
    resolved = git(root, "rev-parse", f"{expected}^{{commit}}")
    if head != resolved:
        raise ValueError(f"{label} HEAD {head} differs from candidate {resolved}")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError(f"{label} worktree is dirty")
    return head


def copy_output(source: Path, destination: Path, role: str) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(source)
    shutil.copyfile(source, destination)
    return {
        "role": role,
        "filename": destination.name,
        "media_type": "application/octet-stream",
        "size_bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--extender-commit", required=True)
    parser.add_argument("--emos-root", required=True, type=Path)
    parser.add_argument("--mos-agondev-root", required=True, type=Path)
    parser.add_argument("--mos-worktree", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    match = BUILD_ID.fullmatch(args.build_id)
    if match is None:
        parser.error(f"build ID must use {SOURCE_IDENTITY}-b<UTC timestamp>")
    created_at = (
        f"{match[1]}-{match[2]}-{match[3]}T"
        f"{match[4]}:{match[5]}:{match[6]}Z"
    )

    candidate = yaml.safe_load(CANDIDATE.read_text(encoding="utf-8"))
    if not isinstance(candidate, dict):
        raise ValueError(f"{CANDIDATE}: expected YAML mapping")
    authorities = candidate["source_authority"]

    extender_head = require_clean_commit(
        ROOT, args.extender_commit, "agon-extender"
    )
    emos_root = args.emos_root.resolve()
    mos_root = args.mos_agondev_root.resolve()
    emos_head = require_clean_commit(
        emos_root, authorities["agon_emos"]["commit"], "agon-emos"
    )
    mos_head = require_clean_commit(
        mos_root, authorities["mos_agondev"]["commit"], "mos-agondev"
    )
    if authorities["agon_emos"].get("profile") != PROFILE:
        raise ValueError("candidate does not select the PORT-008 EMOS profile")

    prepared_root = args.mos_worktree.resolve()
    prepared = json.loads(
        (prepared_root / ".mos-agondev-worktree.json").read_text(encoding="utf-8")
    )
    if prepared.get("source") != {"head": emos_head, "tracked_dirty": False}:
        raise ValueError("prepared MOS tree is not derived from clean candidate EMOS")

    mos_bin = mos_root / "projects/mos-port/bin/MOS.bin"
    identity_bytes = mos_bin.read_bytes()
    for required in (
        SOURCE_IDENTITY.encode(),
        args.build_id.encode(),
        ARTIFACT_STATUS.encode(),
    ):
        if required not in identity_bytes:
            raise ValueError(f"MOS image lacks identity field {required!r}")
    if b"UNVERSIONED-DO-NOT-DEPLOY" in identity_bytes:
        raise ValueError("MOS image still contains the rejected identity marker")

    fixture_record = candidate["fixture"]
    fixture_bin = emos_root / "projects/port008-forward/build/P8VDU.BIN"
    if fixture_bin.stat().st_size != fixture_record["output_bytes"]:
        raise ValueError("fixture size differs from candidate")
    if sha256_file(fixture_bin) != fixture_record["output_sha256"]:
        raise ValueError("fixture hash differs from candidate")

    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite staged package: {output_dir}")
    output_dir.mkdir(parents=True)

    outputs = [
        copy_output(
            mos_root / f"projects/mos-port/bin/MOS.{suffix}",
            output_dir / f"{args.build_id}.{suffix.lower()}",
            role,
        )
        for suffix, role in (
            ("bin", "firmware-binary"),
            ("elf", "linked-elf"),
            ("hex", "intel-hex"),
            ("map", "linker-map"),
        )
    ]
    fixture_output = output_dir / fixture_record["output_filename"]
    fixture = copy_output(fixture_bin, fixture_output, "cold-boot-fixture")

    source_epoch = int(git(emos_root, "show", "-s", "--format=%ct", emos_head))
    manifest = {
        "schema_version": 1,
        "build": {
            "build_id": args.build_id,
            "artifact_id": "agon-emos",
            "source_identity": SOURCE_IDENTITY,
            "variant": "port008-forward",
            "created_at": created_at,
            "status": ARTIFACT_STATUS,
        },
        "provenance": {
            "repository": "agon-emos",
            "commit": emos_head,
            "dirty": False,
            "source_date_epoch": source_epoch,
            "toolchain": [
                {"name": "mos-agondev", "commit": mos_head},
            ],
            "configuration": [
                {"artifact_id": "agon-emos-profile", "identity": PROFILE},
                {"artifact_id": "light2-harness", "identity": "light2-harness-r01"},
                {
                    "artifact_id": "port-008-forward-qualification",
                    "identity": "port-008-forward-qualification-r01",
                },
            ],
            "prepared_source": {
                "commit": prepared["source"]["head"],
                "dirty": prepared["source"]["tracked_dirty"],
                "file_count": len(prepared["files"]),
            },
            "candidate_repository": {
                "repository": "agon-extender",
                "commit": extender_head,
            },
        },
        "compatibility": {
            "provides": ["fixed-purpose-forward-parallel-vdu-routing"],
            "requires": [
                "light2-harness-r01",
                "extender-vdp-v0.2.0",
                "agon-transport-fixture-r01",
            ],
        },
        "outputs": outputs,
        "qualification": {
            "procedure": "port-008-forward-qualification-r01",
            "state": "not-run",
            "hardware_authorized": False,
            "claim_boundary": (
                "identified fixed-purpose EMOS forward candidate; no physical "
                "transfer, reverse UART, sysvar, r02/V1, or broad compatibility claim"
            ),
        },
        "notes": [
            "The repository-root product-linked UART divisor guard passed before staging.",
            "The fixed-purpose profile contains no reverse transport.",
        ],
    }
    manifest_path = output_dir / f"{args.build_id}.manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )

    fixture_manifest = {
        "schema_version": 1,
        "artifact": {
            "artifact_id": "agon-transport-fixture",
            "identity": "agon-transport-fixture-r01",
            "variant": "light2",
            "status": "candidate",
        },
        "provenance": {
            "repository": "agon-emos",
            "commit": emos_head,
            "dirty": False,
            "source": "projects/port008-forward/fixture.json",
        },
        "output": fixture,
        "vdu_payload": {
            "size_bytes": fixture_record["vdu_payload_bytes"],
            "sha256": fixture_record["vdu_payload_sha256"],
        },
        "expected_rgb888": {
            "size_bytes": fixture_record["expected_rgb888_bytes"],
            "sha256": fixture_record["expected_rgb888_sha256"],
        },
    }
    fixture_manifest_path = output_dir / "agon-transport-fixture-r01.manifest.yaml"
    fixture_manifest_path.write_text(
        yaml.safe_dump(fixture_manifest, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )

    print(manifest_path)
    print(fixture_manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
