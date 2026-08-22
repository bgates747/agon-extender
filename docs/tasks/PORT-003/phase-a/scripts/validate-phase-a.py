#!/usr/bin/env python3
"""Prove the PORT-003 Phase A application and link closure.

The hybrid framework compiles a large pinned platform closure. This validator
scopes its claim to project and vendored VDP application sources, then proves
their actual map-file loads and required ELF symbols. It does not mistake an
ESP-IDF or Arduino framework unit with a similar generic name for an excluded
vdp-gl physical controller.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))

from dependency_model import sha256_bytes, sha256_file, write_canonical  # noqa: E402


REQUIRED_SYMBOLS = {
    "project controller factory":
        "agon::extender::display::makeP4DisplayControllerContractCanary()",
    "project concrete controller vtable":
        "vtable for agon::extender::display::P4DisplayControllerContractCanary",
    "vendored Canvas constructor":
        "fabgl::Canvas::Canvas(fabgl::BitmappedDisplayController*)",
    "vendored common controller constructor":
        "fabgl::BitmappedDisplayController::BitmappedDisplayController()",
    "vendored common controller primitive executor":
        "fabgl::BitmappedDisplayController::execPrimitive(",
    "vendored generic controller vtable":
        "vtable for fabgl::GenericBitmappedDisplayController",
}

EXCLUDED_SYMBOL_PREFIXES = [
    "fabgl::VGA",
    "fabgl::CVBS",
    "fabgl::Scene",
    "fabgl::PS2",
    "fabgl::SoundGenerator",
    "fabgl::FileBrowser",
]


def repository_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def project_compile_sources(compile_commands: Path) -> list[str]:
    records = json.loads(compile_commands.read_text(encoding="utf-8"))
    result = []
    vdp_root = ROOT / "vdp"
    for record in records:
        path = Path(record["file"]).resolve()
        try:
            relative = path.relative_to(vdp_root).as_posix()
        except ValueError:
            continue
        if relative.startswith(("video/", "vendor/vdp-gl/")):
            result.append(relative)
    return sorted(set(result))


def loaded_application_objects(map_text: str) -> list[str]:
    build_prefix = ".pio/build/p4-display-contract-canary/"
    result = []
    for line in map_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("LOAD "):
            continue
        path = stripped.removeprefix("LOAD ")
        if path.startswith(build_prefix + "selected-vdp-gl/") or path.startswith(
            build_prefix + "video/"
        ):
            result.append(path.removeprefix(build_prefix))
    return sorted(set(result))


def expected_objects(selection: dict[str, Any]) -> dict[str, str]:
    result = {}
    for source in selection["project_translation_units"]:
        result[source] = f"{source}.o"
    for source in selection["vendored_translation_units"]:
        result[source] = f"selected-vdp-gl/{Path(source).stem}.o"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=ROOT / "vdp/.pio/build/p4-display-contract-canary",
    )
    parser.add_argument("--nm", type=Path, required=True)
    parser.add_argument(
        "--closure-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-a/evidence/build-closure.yaml",
    )
    parser.add_argument(
        "--exclusions-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-a/evidence/link-exclusions.yaml",
    )
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    selection_path = ROOT / "vdp/pio/source-selection.json"
    compile_commands = build_dir / "compile_commands.json"
    map_path = build_dir / "firmware.map"
    elf_path = build_dir / "firmware.elf"
    for path in (selection_path, compile_commands, map_path, elf_path, args.nm):
        if not path.is_file():
            raise FileNotFoundError(path)

    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    map_text = map_path.read_text(encoding="utf-8", errors="replace")
    symbols = subprocess.run(
        [str(args.nm), "-C", str(elf_path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    undefined = subprocess.run(
        [str(args.nm), "-uC", str(elf_path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    compiled_project = project_compile_sources(compile_commands)
    expected = expected_objects(selection)
    loaded = loaded_application_objects(map_text)
    missing_objects = sorted(set(expected.values()) - set(loaded))
    unexpected_objects = sorted(set(loaded) - set(expected.values()))
    expected_project = sorted(selection["project_translation_units"])
    missing_project = sorted(set(expected_project) - set(compiled_project))
    unexpected_project = sorted(set(compiled_project) - set(expected_project))

    symbol_checks = [
        {
            "claim": claim,
            "symbol_fragment": fragment,
            "present": fragment in symbols,
        }
        for claim, fragment in REQUIRED_SYMBOLS.items()
    ]
    exclusion_source_matches = {
        pattern: sorted(
            source
            for source in expected
            if fnmatch.fnmatch(source, pattern)
        )
        for pattern in selection["excluded_source_families"]
    }
    exclusion_symbol_matches = {
        prefix: sorted(line.strip() for line in symbols.splitlines() if prefix in line)
        for prefix in EXCLUDED_SYMBOL_PREFIXES
    }

    closure_ok = not (
        missing_objects
        or unexpected_objects
        or missing_project
        or unexpected_project
        or any(not record["present"] for record in symbol_checks)
    )
    exclusions_ok = not any(exclusion_source_matches.values()) and not any(
        exclusion_symbol_matches.values()
    )

    common_inputs = {
        "source_selection": {
            "path": repository_path(selection_path),
            "sha256": sha256_file(selection_path),
        },
        "compile_commands": {
            "path": repository_path(compile_commands),
            "sha256": sha256_file(compile_commands),
        },
        "linker_map": {
            "path": repository_path(map_path),
            "sha256": sha256_file(map_path),
        },
        "normalized_elf_symbols_sha256": sha256_bytes(
            symbols.encode("utf-8")
        ),
    }
    closure = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_a_build_closure",
        "generated_by": "docs/tasks/PORT-003/phase-a/scripts/validate-phase-a.py",
        "diagnostic_status": "compile/link evidence only; not hardware qualification",
        "environment": selection["environment"],
        "build_invocation":
            ".venv/bin/pio run --project-dir vdp -e p4-display-contract-canary",
        "inputs": common_inputs,
        "application_translation_units": [
            {
                "source": source,
                "object": expected[source],
                "object_loaded": expected[source] in loaded,
            }
            for source in sorted(expected)
        ],
        "required_elf_symbols": symbol_checks,
        "undefined_elf_symbols": sorted(line.strip() for line in undefined),
        "summary": {
            "selected_translation_unit_count": len(expected),
            "project_translation_unit_count": len(expected_project),
            "vendored_translation_unit_count": len(selection["vendored_translation_units"]),
            "missing_objects": missing_objects,
            "unexpected_application_objects": unexpected_objects,
            "missing_project_compile_records": missing_project,
            "unexpected_project_compile_records": unexpected_project,
            "closure_proved": closure_ok,
        },
    }
    exclusions = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_a_link_exclusions",
        "generated_by": "docs/tasks/PORT-003/phase-a/scripts/validate-phase-a.py",
        "diagnostic_status": "VDP application closure only; framework components are out of scope",
        "environment": selection["environment"],
        "source_pattern_matches": exclusion_source_matches,
        "symbol_prefix_matches": exclusion_symbol_matches,
        "summary": {
            "excluded_source_pattern_count": len(exclusion_source_matches),
            "excluded_symbol_prefix_count": len(exclusion_symbol_matches),
            "source_match_count": sum(map(len, exclusion_source_matches.values())),
            "symbol_match_count": sum(map(len, exclusion_symbol_matches.values())),
            "exclusions_proved": exclusions_ok,
        },
    }
    write_canonical(args.closure_output, closure)
    write_canonical(args.exclusions_output, exclusions)
    if not closure_ok or not exclusions_ok:
        raise SystemExit("Phase A closure validation failed")
    print(
        f"proved {len(expected)} application translation units, "
        f"{sum(record['present'] for record in symbol_checks)} required symbols, "
        "and zero excluded VDP units/symbols"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
