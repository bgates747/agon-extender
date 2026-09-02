#!/usr/bin/env python3
"""Validate the PORT-008 non-release target's compile/link closure.

This is a deliberately bounded gate.  It checks that one supplied PlatformIO
environment map presents the required production transport objects as direct
``LOAD`` inputs, that the separately supplied ELF exposes selected integration
symbols, and that the current ordinary source-selection manifests exclude the
qualification-only composition.  A GNU map ``LOAD`` record does not prove
that an input retained code in the ELF, and matching map/ELF basenames do not
prove the files came from one link.  This gate also cannot prove which object
defined an observed ELF symbol, release-object equivalence, source provenance,
target runtime behavior, or physical qualification.

SECURITY: source-selection manifests are parsed as UTF-8 JSON data only.  No
tool, hook, command, or script named by a manifest is executed.  The sole
external program invoked is the target ``nm`` executable supplied explicitly
on this command line; callers must trust that executable and the supplied
evidence files.  No shell is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
from typing import Any, Sequence


QUALIFICATION_ENVIRONMENT = "p4-port008-nonrelease-qualification"
QUALIFICATION_MANIFEST_NAME = (
    "p4-port008-nonrelease-qualification-source-selection.json"
)
ORDINARY_MANIFESTS = {
    "p4-browser-vdp": "p4-browser-vdp-source-selection.json",
    "p4-forward-vdp": "p4-forward-vdp-source-selection.json",
}
QUALIFICATION_DEFINITION = (
    "AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION=1"
)

REQUIRED_TRANSLATION_UNITS = (
    "video/extender/transport/p4_parallel_data_plane.cpp",
    "video/extender/transport/extender_vdp_stream.cpp",
    "video/extender/transport/p4_parallel_target.cpp",
    "video/extender/transport/p4_parallel_qualification.cpp",
)
FORBIDDEN_TRANSLATION_UNITS = (
    "video/extender/transport/forward_parallel_stream.cpp",
    "video/extender/transport/disconnected_stream.cpp",
)
QUALIFICATION_TRANSLATION_UNIT = (
    "video/extender/transport/p4_parallel_qualification.cpp"
)

REQUIRED_LINKED_SYMBOLS = (
    "VDUStreamProcessor::VDUStreamProcessor(Stream*)",
    (
        "agon::extender::transport::P4ParallelDataPlane::serviceOnce("
        "agon::extender::transport::ReceiveWaitPolicy)"
    ),
    (
        "agon::extender::transport::ExtenderVdpStream::write("
        "unsigned char const*, unsigned int)"
    ),
    (
        "agon::extender::transport::EspP4ParlioBackend::wait("
        "agon::extender::transport::ReceiveWaitPolicy, "
        "std::atomic<bool> const&)"
    ),
    (
        "agon::extender::transport::"
        "beginP4ParallelNonreleaseQualification()"
    ),
)

NM_TIMEOUT_SECONDS = 30
TIMEOUT_EXIT_STATUS = 124
MAP_LOAD_LINE = re.compile(r"^LOAD[ \t]+(.+?)[ \t]*$")
NM_DEFINED_LINE = re.compile(
    r"^[0-9A-Fa-f]+[ \t]+([A-Za-z?])[ \t]+(.+?)\s*$"
)


class ClosureError(ValueError):
    """One required closure condition was absent or contradictory."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def regular_file(path: Path, label: str) -> Path:
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ClosureError(f"{label} does not exist: {path}: {exc}") from exc
    if not resolved.is_file():
        raise ClosureError(f"{label} is not a regular file: {path}")
    return resolved


def regular_directory(path: Path, label: str) -> Path:
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ClosureError(f"{label} does not exist: {path}: {exc}") from exc
    if not resolved.is_dir():
        raise ClosureError(f"{label} is not a directory: {path}")
    return resolved


def contained_file(path: Path, root: Path, label: str) -> Path:
    resolved = regular_file(path, label)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ClosureError(
            f"{label} is outside the supplied environment build root: {path}"
        ) from exc
    return resolved


def load_json(path: Path, label: str) -> dict[str, Any]:
    path = regular_file(path, label)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ClosureError(
            f"{label} is not readable UTF-8 JSON: {path}: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise ClosureError(f"{label} must contain one JSON object")
    return document


def normalized_translation_units(
    document: dict[str, Any], field: str, label: str
) -> tuple[str, ...]:
    value = document.get(field)
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ClosureError(f"{label}.{field} must be a string array")
    if len(value) != len(set(value)):
        raise ClosureError(f"{label}.{field} contains a duplicate")
    for item in value:
        pure = PurePosixPath(item)
        if (
            pure.is_absolute()
            or not pure.parts
            or any(part in ("", ".", "..") for part in pure.parts)
            or "\\" in item
        ):
            raise ClosureError(
                f"{label}.{field} contains a non-normalized path: {item!r}"
            )
    return tuple(value)


def require_environment(
    document: dict[str, Any], expected: str, label: str
) -> None:
    observed = document.get("environment")
    if observed != expected:
        raise ClosureError(
            f"{label} environment mismatch: expected {expected!r}, "
            f"observed {observed!r}"
        )


def validate_source_selections(
    qualification_manifest: Path, environment: str
) -> tuple[Path, dict[str, str]]:
    qualification_path = regular_file(
        qualification_manifest, "qualification source-selection manifest"
    )
    if qualification_path.name != QUALIFICATION_MANIFEST_NAME:
        raise ClosureError(
            "qualification source-selection manifest must have the tracked "
            f"name {QUALIFICATION_MANIFEST_NAME!r}"
        )
    qualification = load_json(
        qualification_path, "qualification source-selection manifest"
    )
    require_environment(
        qualification, environment, "qualification source-selection manifest"
    )
    selected = set(
        normalized_translation_units(
            qualification,
            "project_translation_units",
            "qualification source-selection manifest",
        )
    )
    forbidden = set(
        normalized_translation_units(
            qualification,
            "forbidden_project_translation_units",
            "qualification source-selection manifest",
        )
    )
    missing = set(REQUIRED_TRANSLATION_UNITS) - selected
    if missing:
        raise ClosureError(
            "qualification source-selection manifest omits required "
            "translation units: " + ", ".join(sorted(missing))
        )
    selected_forbidden = set(FORBIDDEN_TRANSLATION_UNITS) & selected
    if selected_forbidden:
        raise ClosureError(
            "qualification source-selection manifest selects forbidden "
            "translation units: " + ", ".join(sorted(selected_forbidden))
        )
    unguarded = set(FORBIDDEN_TRANSLATION_UNITS) - forbidden
    if unguarded:
        raise ClosureError(
            "qualification source-selection manifest does not explicitly "
            "forbid: " + ", ".join(sorted(unguarded))
        )
    definitions = qualification.get("component_compile_definitions")
    if not isinstance(definitions, list) or any(
        not isinstance(item, str) for item in definitions
    ):
        raise ClosureError(
            "qualification source-selection manifest."
            "component_compile_definitions must be a string array"
        )
    if definitions.count(QUALIFICATION_DEFINITION) != 1:
        raise ClosureError(
            "qualification source-selection manifest must define exactly "
            f"one {QUALIFICATION_DEFINITION!r}"
        )

    ordinary_results: dict[str, str] = {}
    for ordinary_environment, filename in ORDINARY_MANIFESTS.items():
        ordinary_path = qualification_path.parent / filename
        ordinary = load_json(
            ordinary_path,
            f"{ordinary_environment} source-selection manifest",
        )
        require_environment(
            ordinary,
            ordinary_environment,
            f"{ordinary_environment} source-selection manifest",
        )
        ordinary_selected = set(
            normalized_translation_units(
                ordinary,
                "project_translation_units",
                f"{ordinary_environment} source-selection manifest",
            )
        )
        ordinary_forbidden = set(
            normalized_translation_units(
                ordinary,
                "forbidden_project_translation_units",
                f"{ordinary_environment} source-selection manifest",
            )
        )
        if QUALIFICATION_TRANSLATION_UNIT in ordinary_selected:
            raise ClosureError(
                f"{ordinary_environment} selects qualification-only "
                f"translation unit {QUALIFICATION_TRANSLATION_UNIT}"
            )
        if QUALIFICATION_TRANSLATION_UNIT not in ordinary_forbidden:
            raise ClosureError(
                f"{ordinary_environment} does not explicitly forbid "
                f"{QUALIFICATION_TRANSLATION_UNIT}"
            )
        ordinary_results[ordinary_environment] = sha256_file(ordinary_path)

    return qualification_path, ordinary_results


def object_path(translation_unit: str) -> str:
    if not translation_unit.endswith(".cpp"):
        raise ClosureError(
            f"unsupported production translation unit: {translation_unit}"
        )
    return translation_unit + ".o"


def normalize_map_token(value: str) -> str:
    normalized = posixpath.normpath(value)
    if normalized in ("", "."):
        raise ClosureError("link map contains an empty LOAD path")
    return normalized


def validate_map_direct_inputs(
    map_path: Path, build_root: Path, project_root: Path
) -> tuple[tuple[str, ...], dict[str, str]]:
    try:
        text = map_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ClosureError(
            f"link map is not readable UTF-8 text: {map_path}: {exc}"
        ) from exc
    loads = tuple(
        normalize_map_token(match.group(1))
        for line in text.splitlines()
        if (match := MAP_LOAD_LINE.fullmatch(line)) is not None
    )
    if not loads:
        raise ClosureError("link map contains no direct LOAD input lines")

    try:
        build_relative = build_root.relative_to(project_root).as_posix()
    except ValueError as exc:
        raise ClosureError(
            "environment build root must be inside the qualification "
            "manifest's project root"
        ) from exc

    accepted: list[str] = []
    object_hashes: dict[str, str] = {}
    for translation_unit in REQUIRED_TRANSLATION_UNITS:
        relative_object = object_path(translation_unit)
        resolved_object = contained_file(
            build_root / PurePosixPath(relative_object),
            build_root,
            f"required environment object {relative_object}",
        )
        expected_relative = normalize_map_token(
            posixpath.join(build_relative, relative_object)
        )
        expected_absolute = normalize_map_token(
            (build_root / PurePosixPath(relative_object)).as_posix()
        )
        suffix = "/" + relative_object
        candidates = [
            item
            for item in loads
            if item == relative_object or item.endswith(suffix)
        ]
        if len(candidates) != 1:
            raise ClosureError(
                f"link map must contain exactly one direct LOAD input for "
                f"{relative_object}; observed {len(candidates)}"
            )
        observed = candidates[0]
        if observed not in (expected_relative, expected_absolute):
            raise ClosureError(
                f"link map LOAD path for {relative_object} is outside the "
                f"supplied build root: {observed}"
            )
        accepted.append(observed)
        object_hashes[relative_object] = sha256_file(resolved_object)

    for translation_unit in FORBIDDEN_TRANSLATION_UNITS:
        relative_object = object_path(translation_unit)
        object_name = PurePosixPath(relative_object).name
        suffix = "/" + relative_object
        candidates = [
            item
            for item in loads
            if item == relative_object or item.endswith(suffix)
        ]
        if candidates:
            raise ClosureError(
                "link map contains forbidden direct LOAD input for "
                f"{relative_object}: {candidates[0]}"
            )
        # A project object can appear elsewhere in a linker map as an archive
        # member or in a discarded-section context.  Such a reference does not
        # prove retained code, but it violates this bounded exclusion check
        # even when a direct LOAD line is absent.
        object_reference = re.compile(
            rf"(?:^|[/\s(]){re.escape(object_name)}(?=$|[\s)])",
            re.MULTILINE,
        )
        if object_reference.search(text):
            raise ClosureError(
                "link map references forbidden prototype/disconnected "
                f"object {object_name}"
            )
    return tuple(accepted), object_hashes


def run_target_nm(nm_path: Path, elf_path: Path) -> str:
    command = [str(nm_path), "-C", "--defined-only", str(elf_path)]
    environment = os.environ.copy()
    environment["LC_ALL"] = "C"
    environment["LANG"] = "C"
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            timeout=NM_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ClosureError(
            f"explicitly supplied target nm timed out after "
            f"{NM_TIMEOUT_SECONDS} seconds"
        ) from exc
    except OSError as exc:
        raise ClosureError(
            f"explicitly supplied target nm could not run: {exc}"
        ) from exc
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ClosureError(
            f"explicitly supplied target nm exited {completed.returncode}"
            + (f": {stderr}" if stderr else "")
        )
    try:
        return completed.stdout.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ClosureError(
            "explicitly supplied target nm emitted non-UTF-8 output"
        ) from exc


def validate_linked_symbols(nm_path: Path, elf_path: Path) -> tuple[str, ...]:
    output = run_target_nm(nm_path, elf_path)
    definitions: dict[str, list[str]] = {}
    for line in output.splitlines():
        match = NM_DEFINED_LINE.fullmatch(line)
        if match is None:
            continue
        symbol_type, name = match.groups()
        definitions.setdefault(name, []).append(symbol_type)

    for required in REQUIRED_LINKED_SYMBOLS:
        types = definitions.get(required, [])
        if not any(symbol_type in "TtWw" for symbol_type in types):
            raise ClosureError(
                "target ELF lacks required linked code symbol: " + required
            )
    return REQUIRED_LINKED_SYMBOLS


def validate(
    *,
    environment: str,
    build_root: Path,
    map_path: Path,
    elf_path: Path,
    qualification_manifest: Path,
    nm_path: Path,
) -> dict[str, Any]:
    if environment != QUALIFICATION_ENVIRONMENT:
        raise ClosureError(
            f"this bounded validator accepts only "
            f"{QUALIFICATION_ENVIRONMENT!r}, not {environment!r}"
        )
    qualification_path, ordinary_hashes = validate_source_selections(
        qualification_manifest, environment
    )
    project_root = qualification_path.parent.parent.resolve(strict=True)
    resolved_build_root = regular_directory(
        build_root, "environment build root"
    )
    if resolved_build_root.name != environment:
        raise ClosureError(
            "environment build root basename does not match the supplied "
            f"environment: {resolved_build_root.name!r}"
        )
    resolved_map = contained_file(
        map_path, resolved_build_root, "environment link map"
    )
    resolved_elf = contained_file(
        elf_path, resolved_build_root, "environment ELF"
    )
    if resolved_map.stem != resolved_elf.stem:
        raise ClosureError(
            "environment map and ELF basenames do not identify one nominal "
            f"image: {resolved_map.name!r} versus {resolved_elf.name!r}"
        )
    resolved_nm = regular_file(nm_path, "explicitly supplied target nm")

    direct_load_inputs, object_hashes = validate_map_direct_inputs(
        resolved_map, resolved_build_root, project_root
    )
    linked_symbols = validate_linked_symbols(resolved_nm, resolved_elf)
    return {
        "evidence_class": (
            "nonrelease-manifest-direct-load-and-symbol-closure"
        ),
        "environment": environment,
        "bounded_nonrelease_closure_checks_passed": True,
        "checked_claims": [
            "qualification-manifest-selection",
            "map-direct-load-input-presence",
            "separately-supplied-elf-symbol-observation",
            "ordinary-manifest-qualification-exclusion",
        ],
        "required_direct_load_inputs_present": True,
        "required_elf_symbols_observed": True,
        "release_object_equivalence_proved": False,
        "required_symbol_origin_proved": False,
        "map_elf_pairing_proved": False,
        "source_provenance_proved": False,
        "runtime_or_physical_qualification_proved": False,
        "target_nm_trust_model": "explicitly-supplied-trusted-executable",
        "qualification_source_selection_sha256": sha256_file(
            qualification_path
        ),
        "ordinary_source_selection_sha256": ordinary_hashes,
        "link_map_sha256": sha256_file(resolved_map),
        "elf_sha256": sha256_file(resolved_elf),
        "target_nm_sha256": sha256_file(resolved_nm),
        "required_direct_load_inputs": list(direct_load_inputs),
        "required_object_sha256": object_hashes,
        "required_linked_symbols": list(linked_symbols),
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--environment", required=True)
    value.add_argument("--build-root", required=True, type=Path)
    value.add_argument("--map", required=True, dest="map_path", type=Path)
    value.add_argument("--elf", required=True, dest="elf_path", type=Path)
    value.add_argument(
        "--source-selection",
        required=True,
        dest="qualification_manifest",
        type=Path,
    )
    value.add_argument("--nm", required=True, dest="nm_path", type=Path)
    return value


def main(arguments: Sequence[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    try:
        report = validate(
            environment=args.environment,
            build_root=args.build_root,
            map_path=args.map_path,
            elf_path=args.elf_path,
            qualification_manifest=args.qualification_manifest,
            nm_path=args.nm_path,
        )
    except ClosureError as exc:
        sys.stderr.write(f"PORT-008 non-release closure: FAILED: {exc}\n")
        return TIMEOUT_EXIT_STATUS if "timed out" in str(exc) else 1
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
