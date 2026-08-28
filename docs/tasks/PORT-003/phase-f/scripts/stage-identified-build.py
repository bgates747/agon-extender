#!/usr/bin/env python3
"""Stage one identified Phase F build with fail-closed provenance.

This script exists because PlatformIO's generic output names are not deployment
authority. It runs only against a clean committed worktree, verifies the
post-link closure and factory-image segments, copies every controlled output
under the full build ID, and writes the adjacent manifest required by the
project versioning policy. It never flashes hardware.
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
ENVIRONMENT = "p4-browser-vdp"
SOURCE_IDENTITY = "extender-vdp-v0.1.0"
ARTIFACT_STATUS = "candidate"
VARIANT = "olimex-p4-devkit"
BUILD_ID = re.compile(
    r"^extender-vdp-v0\.1\.0-b"
    r"(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})Z$"
)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True
    ).strip()


def sha256_file(path: Path) -> str:
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


def copy_record(
    source: Path,
    destination: Path,
    *,
    role: str,
    flash_offset: str | None = None,
) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(source)
    shutil.copyfile(source, destination)
    record: dict[str, Any] = {
        "role": role,
        "filename": destination.name,
        "size_bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
    }
    if flash_offset is not None:
        record["flash_offset"] = flash_offset
    return record


def require_factory_segment(
    factory: bytes, offset: int, expected: bytes, label: str
) -> None:
    observed = factory[offset : offset + len(expected)]
    if observed != expected:
        raise ValueError(
            f"factory image {label} segment at {offset:#x} differs from its "
            "standalone build output"
        )


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

    match = BUILD_ID.fullmatch(args.build_id)
    if match is None:
        parser.error("build ID does not match the approved extender-vdp-v0.1.0 form")
    created_at = (
        f"{match[1]}-{match[2]}-{match[3]}T"
        f"{match[4]}:{match[5]}:{match[6]}Z"
    )

    head = git("rev-parse", "HEAD")
    expected_commit = git("rev-parse", f"{args.commit}^{{commit}}")
    if head != expected_commit:
        raise ValueError(f"HEAD {head} differs from requested commit {expected_commit}")
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise ValueError("identified build staging requires a clean worktree")

    identity = json.loads(
        (ROOT / f"vdp/pio/{ENVIRONMENT}-identity.json").read_text(encoding="utf-8")
    )
    expected_identity = {
        "schema_version": 1,
        "artifact_id": "extender-vdp",
        "source_identity": SOURCE_IDENTITY,
        "status": ARTIFACT_STATUS,
        "variant": VARIANT,
    }
    if identity != expected_identity:
        raise ValueError(f"committed identity differs from approved record: {identity}")

    closure = load_yaml(args.closure)
    exclusions = load_yaml(args.exclusions)
    expected_checks = {
        "source_identity": SOURCE_IDENTITY,
        "build_id": args.build_id,
        "artifact_status": ARTIFACT_STATUS,
    }
    observed_checks = {
        name: record.get("expected")
        for name, record in closure.get("identity", {}).get("checks", {}).items()
    }
    if observed_checks != expected_checks:
        raise ValueError(f"closure identity differs: {observed_checks}")
    identity_proof = closure["identity"]
    if (
        identity_proof.get("identity_state") != "identified-deployable"
        or identity_proof.get("rejected_marker_present")
        or not identity_proof.get("deployable_identity_proved")
    ):
        raise ValueError("post-link evidence does not prove the identified image")
    if not closure.get("summary", {}).get("closure_proved"):
        raise ValueError("post-link closure is not proved")
    if not exclusions.get("summary", {}).get("exclusions_proved"):
        raise ValueError("post-link exclusions are not proved")

    build_dir = args.build_dir.resolve()
    application = build_dir / "firmware.bin"
    factory_path = build_dir / "firmware.factory.bin"
    bootloader = build_dir / "bootloader.bin"
    partitions = build_dir / "partitions.bin"
    elf = build_dir / "firmware.elf"
    linker_map = build_dir / "firmware.map"
    sdkconfig = build_dir / "config/sdkconfig.json"
    flash_args = build_dir / "flash_args"
    for required in (
        application,
        factory_path,
        bootloader,
        partitions,
        elf,
        linker_map,
        sdkconfig,
        flash_args,
    ):
        if not required.is_file():
            raise FileNotFoundError(required)

    if sha256_file(application) != closure["firmware"]["sha256"]:
        raise ValueError("application image differs from closure evidence")
    if sha256_file(factory_path) != closure["factory_firmware"]["sha256"]:
        raise ValueError("factory image differs from closure evidence")

    factory = factory_path.read_bytes()
    application_bytes = application.read_bytes()
    bootloader_bytes = bootloader.read_bytes()
    partitions_bytes = partitions.read_bytes()
    require_factory_segment(factory, 0x2000, bootloader_bytes, "bootloader")
    require_factory_segment(factory, 0x8000, partitions_bytes, "partition table")
    require_factory_segment(factory, 0x20000, application_bytes, "application")
    ota_data = factory[0xF000 : 0x11000]
    if len(ota_data) != 0x2000:
        raise ValueError("factory image does not contain the complete OTA-data segment")

    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite staged build: {output_dir}")
    output_dir.mkdir(parents=True)
    prefix = args.build_id
    outputs = [
        copy_record(
            application,
            output_dir / f"{prefix}.application.bin",
            role="application",
            flash_offset="0x20000",
        ),
        copy_record(
            factory_path,
            output_dir / f"{prefix}.factory.bin",
            role="factory-image",
            flash_offset="0x0",
        ),
        copy_record(
            bootloader,
            output_dir / f"{prefix}.bootloader.bin",
            role="bootloader",
            flash_offset="0x2000",
        ),
        copy_record(
            partitions,
            output_dir / f"{prefix}.partitions.bin",
            role="partition-table",
            flash_offset="0x8000",
        ),
    ]
    ota_path = output_dir / f"{prefix}.otadata.bin"
    ota_path.write_bytes(ota_data)
    outputs.append(
        {
            "role": "ota-data",
            "filename": ota_path.name,
            "flash_offset": "0xf000",
            "size_bytes": ota_path.stat().st_size,
            "sha256": sha256_file(ota_path),
        }
    )
    outputs.extend(
        [
            copy_record(elf, output_dir / f"{prefix}.elf", role="elf"),
            copy_record(linker_map, output_dir / f"{prefix}.map", role="linker-map"),
            copy_record(
                sdkconfig,
                output_dir / f"{prefix}.sdkconfig.json",
                role="sdkconfig",
            ),
            copy_record(
                flash_args,
                output_dir / f"{prefix}.flash-args.txt",
                role="flash-arguments",
            ),
            copy_record(
                args.closure,
                output_dir / f"{prefix}.build-closure.yaml",
                role="post-link-closure",
            ),
            copy_record(
                args.exclusions,
                output_dir / f"{prefix}.link-exclusions.yaml",
                role="post-link-exclusions",
            ),
        ]
    )

    manifest = {
        "schema_version": 1,
        "build": {
            "build_id": args.build_id,
            "artifact_id": "extender-vdp",
            "source_identity": SOURCE_IDENTITY,
            "variant": VARIANT,
            "created_at": created_at,
            "status": ARTIFACT_STATUS,
        },
        "provenance": {
            "repository": "agon-extender",
            "commit": head,
            "dirty": False,
            "source_date_epoch": int(git("show", "-s", "--format=%ct", head)),
            "toolchain": [
                {"name": "pioarduino", "version": "55.03.311"},
                {"name": "arduino-esp32", "version": "3.3.11"},
                {"name": "esp-idf", "version": "5.5.5"},
            ],
            "configuration": [
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
                },
            ],
        },
        "compatibility": {
            "provides": ["retained-vdp-p4-browser-video-candidate"],
            "requires": [
                "olimex-p4-devkit-profile-r03",
                "p4-ota-partition-layout-r01",
            ],
        },
        "outputs": outputs,
        "qualification": {
            "procedure": "p4-browser-video-qualification-r01",
            "state": "not-run",
            "hardware_authorized": False,
            "claim_boundary": (
                "identified P4-only candidate build; no target-runtime, Agon "
                "transport, return-UART, EMOS-routing, or hardware claim"
            ),
        },
        "notes": [
            "Factory segment equality was verified for bootloader, partition table, OTA data, and application.",
            "Hardware deployment remains forbidden until separate PORT-003 item 15 authorization.",
        ],
    }
    manifest_path = output_dir / f"{prefix}.manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
