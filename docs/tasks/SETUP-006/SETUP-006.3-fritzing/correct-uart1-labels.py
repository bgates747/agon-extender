#!/usr/bin/env python3
"""Migrate current SETUP-006 wiring drafts to corrected Agon UART1 labels.

This bounded migration exists because CA-2026-08-25-001 found that the first
generated Agon header and label-bank parts attached UART1 alternate functions
to the wrong physical pins.  Fritzing embeds custom parts inside every sketch,
so correcting the canonical generator alone cannot repair existing `.fzz`
drafts.

The migration replaces only the four bundled Agon header/label-bank parts and
their same-length module-ID references.  It deliberately does not parse or
rewrite wire endpoints, connector IDs, geometry, or any other sketch content.
The deterministic `draft_v1` remains an output of `make-draft-v1.py`; this
script migrates its source and the Author's manually arranged `draft_v2`, then
validates all three current drafts with `--check`.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WIRING_ROOT = ROOT.parent / "SETUP-006.4-wiring-design"
CANONICAL = ROOT / "generated" / "light2-extender-breadboard-scaffold.fzz"
MIGRATION_TARGETS = (
    WIRING_ROOT / "light2-extender-breadboard-wiring-draft.fzz",
    WIRING_ROOT / "light2-extender-breadboard-wiring-draft_v2.fzz",
)
CHECK_TARGETS = (
    *MIGRATION_TARGETS,
    WIRING_ROOT / "light2-extender-breadboard-wiring-draft_v1.fzz",
)

OLD_SOURCE_SHA256 = (
    "9dbd85b7d971cb787df117a9ddc81e4bc05feaa53c2a7e5ae47e5af6db71c541"
)
OLD_V2_SHA256 = (
    "207a59b795b472db7881b68eadeb7a55464ab13a51690bfa1de8f1476e8564cb"
)
EXPECTED_OLD_HASHES = {
    MIGRATION_TARGETS[0]: OLD_SOURCE_SHA256,
    MIGRATION_TARGETS[1]: OLD_V2_SHA256,
}

MODULE_MIGRATIONS = {
    "agon-light2-even-16-contact-header-fritzing-r02":
        "agon-light2-even-16-contact-header-fritzing-r03",
    "agon-light2-odd-16-contact-header-fritzing-r02":
        "agon-light2-odd-16-contact-header-fritzing-r03",
    "agon-light2-even-pin-label-bank-fritzing-r02":
        "agon-light2-even-pin-label-bank-fritzing-r03",
    "agon-light2-odd-pin-label-bank-fritzing-r02":
        "agon-light2-odd-pin-label-bank-fritzing-r03",
}

CORRECT_LABELS = (
    b"17 PC0 / TXD1",
    b"18 PC1 / RXD1",
    b"19 PC2 / RTS1",
    b"20 PC3 / CTS1",
)
INCORRECT_LABELS = (
    b"13 PD4 / RTS1",
    b"14 PD5 / CTS1",
    b"17 PC0 / RXD1",
    b"19 PC2 / TXD1",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(path: Path) -> tuple[list[zipfile.ZipInfo], dict[str, bytes]]:
    with zipfile.ZipFile(path) as bundle:
        infos = bundle.infolist()
        return infos, {info.filename: bundle.read(info.filename) for info in infos}


def canonical_parts() -> dict[str, bytes]:
    _infos, files = archive(CANONICAL)
    required = {
        f"{prefix}.{module_id}.{suffix}"
        for module_id in MODULE_MIGRATIONS.values()
        for prefix, suffix in (("part", "fzp"), ("svg.breadboard", "svg"))
    }
    missing = required - files.keys()
    if missing:
        raise ValueError(f"canonical scaffold lacks corrected parts: {sorted(missing)}")
    return {name: files[name] for name in required}


def migrated_name(name: str) -> str:
    for old, new in MODULE_MIGRATIONS.items():
        name = name.replace(old, new)
    return name


def migrated_sketch(data: bytes) -> bytes:
    for old, new in MODULE_MIGRATIONS.items():
        old_bytes = old.encode()
        new_bytes = new.encode()
        if len(old_bytes) != len(new_bytes):
            raise AssertionError("module-ID migration must preserve byte length")
        data = data.replace(old_bytes, new_bytes)
    return data


def write_archive(
    path: Path,
    infos: list[zipfile.ZipInfo],
    files: dict[str, bytes],
    corrected_parts: dict[str, bytes],
) -> None:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as output:
        for original_info in infos:
            old_name = original_info.filename
            new_name = migrated_name(old_name)
            info = copy.copy(original_info)
            info.filename = new_name
            info.orig_filename = new_name
            if new_name in corrected_parts:
                data = corrected_parts[new_name]
            elif old_name.endswith(".fz"):
                data = migrated_sketch(files[old_name])
            else:
                data = files[old_name]
            output.writestr(info, data)
    path.write_bytes(stream.getvalue())


def validate(
    path: Path,
    require_current: bool,
    corrected_parts: dict[str, bytes] | None = None,
) -> None:
    _infos, files = archive(path)
    payload = b"\n".join(files.values())
    old_ids = [item.encode() for item in MODULE_MIGRATIONS]
    new_ids = [item.encode() for item in MODULE_MIGRATIONS.values()]
    if require_current:
        if any(item in payload for item in old_ids):
            raise ValueError(f"{path.name} still contains an r02 Agon part identity")
        if not all(item in payload for item in new_ids):
            raise ValueError(f"{path.name} lacks a corrected r03 Agon part identity")
        if any(item in payload for item in INCORRECT_LABELS):
            raise ValueError(f"{path.name} still contains an incorrect UART1 label")
        if not all(item in payload for item in CORRECT_LABELS):
            raise ValueError(f"{path.name} lacks a corrected UART1 label")
        if corrected_parts is not None:
            stale = [
                name
                for name, expected in corrected_parts.items()
                if files.get(name) != expected
            ]
            if stale:
                raise ValueError(
                    f"{path.name} has stale corrected Agon parts: {sorted(stale)}"
                )


def migrate(path: Path, corrected_parts: dict[str, bytes]) -> bool:
    infos, files = archive(path)
    payload = b"\n".join(files.values())
    has_old_identity = any(
        item.encode() in payload for item in MODULE_MIGRATIONS
    )
    has_stale_current_part = any(
        files.get(name) != data for name, data in corrected_parts.items()
    )
    if not has_old_identity and not has_stale_current_part:
        validate(path, require_current=True, corrected_parts=corrected_parts)
        return False
    if has_old_identity:
        expected = EXPECTED_OLD_HASHES[path]
        actual = sha256(path)
        if actual != expected:
            raise ValueError(
                f"refusing to migrate unexpected {path.name}: expected {expected}, "
                f"found {actual}"
            )
    write_archive(path, infos, files, corrected_parts)
    validate(path, require_current=True, corrected_parts=corrected_parts)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify all three current wiring drafts use corrected r03 parts",
    )
    args = parser.parse_args()
    parts = canonical_parts()
    if args.check:
        for path in CHECK_TARGETS:
            validate(path, require_current=True, corrected_parts=parts)
        return

    for path in MIGRATION_TARGETS:
        migrate(path, parts)


if __name__ == "__main__":
    main()
