#!/usr/bin/env python3
"""Import and verify the immutable PORT-003 Phase A source baselines.

This is initial-import machinery, not a source transformer. It copies bytes and
executable modes from the already reviewed immutable roots, maps official VDP
`video/` files into the upstream-shaped project tree, and refuses unexplained
files in dependency destinations. It must never be used to normalize, format,
or patch upstream source.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
DEPENDENCY_SCRIPTS = ROOT / "docs/dependencies/scripts"
sys.path.insert(0, str(DEPENDENCY_SCRIPTS))

from dependency_model import hash_paths, load_data, sha256_file, write_canonical  # noqa: E402


OWNER_DESTINATIONS = {
    "vdp-gl": ROOT / "vdp/vendor/vdp-gl",
    "ESP32Time": ROOT / "vdp/vendor/ESP32Time",
    "CRC": ROOT / "vdp/vendor/CRC",
}
OFFICIAL_METADATA_ROOT = ROOT / "vdp/vendor/agon-vdp-release"
OFFICIAL_VIDEO_ROOT = ROOT / "vdp/video"
ALLOWED_DEPENDENCY_ADMIN = {".git"}
GENERATED_OFFICIAL_VIDEO_FILES = {"CMakeLists.txt"}


def parse_root(value: str) -> tuple[str, Path]:
    try:
        owner, raw = value.split("=", 1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected OWNER=PATH") from error
    path = Path(raw).resolve()
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"source root is not a directory: {path}")
    return owner, path


def git_files(root: Path, commit: str) -> tuple[list[str], dict[str, int]]:
    actual = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual != commit:
        raise ValueError(f"{root}: expected commit {commit}, found {actual}")
    output = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", commit],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    files: list[str] = []
    modes: dict[str, int] = {}
    for line in output.splitlines():
        metadata, relative = line.split("\t", 1)
        mode, object_type, _object_hash = metadata.split()
        if object_type != "blob":
            raise ValueError(f"unsupported Git object in source release: {relative}")
        if not (root / relative).is_file():
            raise FileNotFoundError(root / relative)
        files.append(relative)
        modes[relative] = int(mode[-3:], 8)
    return sorted(files), modes


def registry_files(root: Path) -> tuple[list[str], dict[str, int]]:
    files = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and not ALLOWED_DEPENDENCY_ADMIN.intersection(path.relative_to(root).parts)
        and "__pycache__" not in path.relative_to(root).parts
    )
    modes = {
        relative: stat.S_IMODE((root / relative).stat().st_mode)
        for relative in files
    }
    return files, modes


def mapped_path(owner: str, relative: str) -> Path:
    if owner == "agon-vdp":
        if relative.startswith("video/"):
            return OFFICIAL_VIDEO_ROOT / relative.removeprefix("video/")
        return OFFICIAL_METADATA_ROOT / relative
    return OWNER_DESTINATIONS[owner] / relative


def atomic_copy(source: Path, destination: Path, mode: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.port-003-import.tmp")
    if temporary.exists():
        temporary.unlink()
    shutil.copyfile(source, temporary)
    os.chmod(temporary, mode)
    os.replace(temporary, destination)


def mapped_tree_hash(owner: str, source_files: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(source_files):
        encoded = relative.encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        digest.update(bytes.fromhex(sha256_file(mapped_path(owner, relative))))
    return digest.hexdigest()


def unexpected_dependency_files(owner: str, expected: set[str]) -> list[str]:
    root = OWNER_DESTINATIONS[owner]
    if not root.exists():
        return []
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root).as_posix() not in expected
    )


def unexpected_official_files(source_paths: list[str]) -> list[str]:
    expected_video = {
        path.removeprefix("video/")
        for path in source_paths
        if path.startswith("video/")
    }
    actual_video = {
        path.relative_to(OFFICIAL_VIDEO_ROOT).as_posix()
        for path in OFFICIAL_VIDEO_ROOT.rglob("*")
        if path.is_file()
        and "extender" not in path.relative_to(OFFICIAL_VIDEO_ROOT).parts
        and path.relative_to(OFFICIAL_VIDEO_ROOT).as_posix()
        not in GENERATED_OFFICIAL_VIDEO_FILES
    }
    expected_metadata = {
        path for path in source_paths if not path.startswith("video/")
    }
    actual_metadata = (
        {
            path.relative_to(OFFICIAL_METADATA_ROOT).as_posix()
            for path in OFFICIAL_METADATA_ROOT.rglob("*")
            if path.is_file()
        }
        if OFFICIAL_METADATA_ROOT.exists()
        else set()
    )
    unexpected_video = [f"video/{path}" for path in actual_video - expected_video]
    unexpected_metadata = [
        f"release/{path}" for path in actual_metadata - expected_metadata
    ]
    return sorted(unexpected_video + unexpected_metadata)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", action="append", required=True, type=parse_root)
    parser.add_argument("--apply", action="store_true", help="copy missing or differing bytes before verification")
    parser.add_argument(
        "--verify-index",
        action="store_true",
        help="also require every imported release path in the Git index",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-a/evidence/import-manifest.yaml",
    )
    args = parser.parse_args()

    roots = dict(args.source_root)
    graph = load_data(ROOT / "docs/dependencies/generated/code-graph.yaml")
    graph_sources = {record["owner"]: record for record in graph["sources"]}
    expected_owners = set(graph_sources)
    if set(roots) != expected_owners:
        raise ValueError(f"source roots must be exactly {sorted(expected_owners)}")

    records: list[dict[str, Any]] = []
    expected_index_paths: set[str] = set()
    for owner in sorted(roots):
        source = graph_sources[owner]
        source_root = roots[owner]
        if source["commit"]:
            paths, modes = git_files(source_root, source["commit"])
        else:
            paths, modes = registry_files(source_root)
        actual_source_hash = hash_paths(source_root, paths)
        if len(paths) != source["manifest_file_count"]:
            raise ValueError(
                f"{owner}: expected {source['manifest_file_count']} files, found {len(paths)}"
            )
        if actual_source_hash != source["tree_sha256"]:
            raise ValueError(
                f"{owner}: expected tree {source['tree_sha256']}, found {actual_source_hash}"
            )

        if owner == "agon-vdp":
            unexpected = unexpected_official_files(paths)
            if unexpected:
                raise ValueError(
                    f"{owner}: unexpected destination files: {unexpected[:10]}"
                )
        else:
            unexpected = unexpected_dependency_files(owner, set(paths))
            if unexpected:
                raise ValueError(f"{owner}: unexpected destination files: {unexpected[:10]}")

        changed = 0
        for relative in paths:
            source_path = source_root / relative
            destination = mapped_path(owner, relative)
            expected_index_paths.add(destination.relative_to(ROOT).as_posix())
            differs = not destination.is_file() or sha256_file(destination) != sha256_file(source_path)
            if differs:
                if not args.apply:
                    raise ValueError(f"{owner}: import differs or is missing: {relative}")
                atomic_copy(source_path, destination, modes[relative])
                changed += 1
            elif args.apply:
                os.chmod(destination, modes[relative])

        imported_hash = mapped_tree_hash(owner, paths)
        if imported_hash != source["tree_sha256"]:
            raise ValueError(f"{owner}: imported tree hash mismatch: {imported_hash}")
        executable = [relative for relative in paths if modes[relative] & 0o111]
        records.append(
            {
                "owner": owner,
                "source_id": source["id"],
                "identity": source["identity"],
                "commit": source["commit"],
                "expected_tree_sha256": source["tree_sha256"],
                "imported_tree_sha256": imported_hash,
                "file_count": len(paths),
                "files_written": changed,
                "executable_paths": executable,
                "mapping": (
                    {
                        "video/": "vdp/video/",
                        "other_release_content": "vdp/vendor/agon-vdp-release/",
                    }
                    if owner == "agon-vdp"
                    else {"source_root": f"vdp/vendor/{owner}/"}
                ),
                "local_modification_status": "none",
            }
        )

    if args.verify_index:
        tracked = set(
            subprocess.run(
                ["git", "-C", str(ROOT), "ls-files", "-z"],
                check=True,
                capture_output=True,
            ).stdout.decode().split("\0")
        )
        missing_from_index = sorted(expected_index_paths - tracked)
        if missing_from_index:
            raise ValueError(
                "reviewed import paths missing from Git index: "
                f"{missing_from_index[:10]}"
            )

    result = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_a_import_manifest",
        "generated_by": "docs/tasks/PORT-003/phase-a/scripts/import-baselines.py",
        "diagnostic_status": "source-import verification only",
        "sources": records,
        "summary": {
            "source_count": len(records),
            "file_count": sum(record["file_count"] for record in records),
            "files_written": sum(record["files_written"] for record in records),
            "all_tree_hashes_match": all(
                record["expected_tree_sha256"] == record["imported_tree_sha256"]
                for record in records
            ),
            "vendored_source_modifications": 0,
        },
    }
    write_canonical(args.output, result)
    print(
        f"verified {result['summary']['file_count']} files across "
        f"{result['summary']['source_count']} immutable baselines; "
        f"wrote {result['summary']['files_written']} files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
