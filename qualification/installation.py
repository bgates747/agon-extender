#!/usr/bin/env python3
"""Verify retained installation bytes and source closure without contacting boards.

This adapts existing installation evidence; it never flashes, rebuilds firmware,
or treats a historical readback as fresh proof of the currently powered board.
Source archives may honestly contain an identified uncommitted patch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hardware_validation import atomic_json, sha256, utc_stamp


def checked_file(record: dict) -> Path:
    path = Path(record["path"]).resolve(strict=True)
    if not path.is_file() or sha256(path) != record["sha256"]:
        raise ValueError(f"retained evidence hash mismatch: {path}")
    return path


def file_record(path: Path) -> dict:
    return {"path": str(path.resolve(strict=True)), "sha256": sha256(path)}


def verify_source(source: dict, commit: str, build_id: str) -> dict:
    archive = checked_file(source["archive"])
    inventory_path = checked_file(source["inventory"])
    manifest = json.loads(checked_file(source["build_manifest"]).read_text())
    inventory = json.loads(inventory_path.read_text())
    if (manifest.get("source_commit", manifest.get("commit")) != commit or
            manifest.get("build_id") != build_id):
        raise ValueError("source manifest does not identify the installed build")
    dirty = manifest.get("source_dirty", manifest.get("dirty"))
    if type(dirty) is not bool:
        raise ValueError("source manifest must declare clean or dirty inputs")
    records = inventory.get("source_sha256")
    if records is None:
        entries = inventory["files"]
        records = {entry["path"]: entry["sha256"] for entry in entries}
        if len(records) != len(entries):
            raise ValueError("duplicate source inventory path")
    if not isinstance(records, dict) or not records:
        raise ValueError("empty source inventory")
    prefix = source.get("archive_prefix", "")
    observed = {}
    with tarfile.open(archive) as stream:
        for member in stream:
            name = member.name
            parts = PurePosixPath(name).parts
            if name.startswith("/") or ".." in parts:
                raise ValueError("unsafe source archive path")
            if member.isdir():
                continue
            if not member.isfile() or (prefix and not name.startswith(prefix)):
                raise ValueError("source archive has a link or unexpected prefix")
            relative = name[len(prefix):]
            if relative in observed:
                raise ValueError("duplicate source archive member")
            with stream.extractfile(member) as data:
                observed[relative] = hashlib.file_digest(data, "sha256").hexdigest()
    if observed != records:
        raise ValueError("source archive does not match the complete source inventory")
    if dirty:
        patch = checked_file(source["patch"])
        if (manifest.get("source_patch_sha256") != sha256(patch) or
                manifest.get("source_archive_sha256") != sha256(archive)):
            raise ValueError("archived-patch provenance does not match build inputs")
    else:
        artifacts = manifest.get("artifacts", [])
        for name, path in (("source.tar.gz", archive), ("source-inputs.json", inventory_path)):
            if not any(Path(item["path"]).name == name and item["sha256"] == sha256(path)
                       for item in artifacts):
                raise ValueError("clean build manifest does not bind its source archive/inventory")
    return {"kind": "archived-patch" if dirty else "clean-build-archive",
            "base_commit": commit, "dirty": dirty, "files_verified": len(records),
            "archive_sha256": sha256(archive), "inventory_sha256": sha256(inventory_path)}


def verify_spec(spec: dict) -> dict:
    if spec.get("schema") != 1 or spec.get("target") not in ("p4", "emos"):
        raise ValueError("installation specification must name p4 or emos under schema 1")
    target = spec["target"]
    commit, build_id = spec["component_commit"], spec["build_id"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not build_id:
        raise ValueError("full source commit and exact build identity required")
    artifact = checked_file(spec["artifact"])
    readback = checked_file(spec["readback"])
    artifact_bytes, installed = artifact.read_bytes(), readback.read_bytes()
    evidence = json.loads(checked_file(spec["installation_evidence"]).read_text())
    manifest = json.loads(checked_file(spec["source"]["build_manifest"]).read_text())
    if evidence.get("build_id") != build_id:
        raise ValueError("installation evidence identifies a different build")
    if target == "p4":
        offset = spec["flash_offset"]
        start, end = spec["written_sector_range"]
        before = checked_file(spec["preimage"]).read_bytes()
        if (type(offset) is not int or start != offset or start % 4096 or
                end != (offset + len(artifact_bytes) + 4095) // 4096 * 4096 or
                len(installed) != 16777216 or len(before) != len(installed) or
                installed[offset:offset + len(artifact_bytes)] != artifact_bytes or
                installed[:start] != before[:start] or installed[end:] != before[end:]):
            raise ValueError("P4 independent application/full-device preservation comparison failed")
        if (evidence.get("source_commit") != commit or not evidence.get("app_exact") or
                evidence.get("app_sha256") != sha256(artifact) or
                evidence.get("after_sha256") != sha256(readback) or
                evidence.get("written_sector_range") != [start, end] or
                not evidence.get("outside_written_sectors_unchanged")):
            raise ValueError("P4 retained installation evidence disagrees with bytes")
        if not any(item["sha256"] == sha256(artifact) and item["bytes"] == len(artifact_bytes)
                   for item in manifest.get("artifacts", [])):
            raise ValueError("P4 build manifest does not bind the accepted application")
    else:
        raw_bytes = manifest.get("raw_bytes", 0)
        raw = artifact_bytes[:raw_bytes]
        if (len(installed) != 131072 or not 0 < len(artifact_bytes) <= 131072 or
                installed != artifact_bytes.ljust(131072, b"\xff") or
                not 0 < raw_bytes <= len(artifact_bytes) or
                artifact_bytes[raw_bytes:] != b"\xff" * (len(artifact_bytes) - raw_bytes) or
                not evidence.get("entire_128KiB_ROM_exact") or
                evidence.get("padded_sha256") != sha256(readback) or
                manifest.get("raw_sha256") != hashlib.sha256(raw).hexdigest() or
                manifest.get("padded_sha256") != sha256(readback)):
            raise ValueError("EMOS complete ROM, padding or installed/build evidence mismatch")
    source = verify_source(spec["source"], commit, build_id)
    return {"schema": 2, "status": "verified", "target": target,
            "verification_scope": "retained-installation",
            "live_identity_required": True,
            "component_commit": commit, "build_id": build_id,
            "artifact_sha256": sha256(artifact), "artifact_bytes": len(artifact_bytes),
            "installed_readback_sha256": sha256(readback),
            "source": source, "specification": spec,
            "limits": "Historical installation proof; fresh bench identity and physical qualification remain required."}


def load_receipt(path: Path) -> dict:
    receipt = json.loads(path.read_text())
    if receipt.get("schema") != 2 or receipt.get("status") != "verified":
        raise ValueError("use an evidence-verified schema-2 installation receipt")
    observed = verify_spec(receipt["specification"])
    for key, value in observed.items():
        if receipt.get(key) != value:
            raise ValueError(f"installation receipt field changed or incomplete: {key}")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("output must be a fresh path")
    receipt = verify_spec(json.loads(args.spec.read_text()))
    receipt["verified_at"] = utc_stamp()
    atomic_json(args.output, receipt)
    print(f"Retained {receipt['target']} installation verified; no board was contacted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
