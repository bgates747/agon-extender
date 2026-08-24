#!/usr/bin/env python3
"""Prove the PORT-003 Phase D P4 application and link closure."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_bytes, sha256_file, write_canonical  # noqa: E402


REQUIRED_SYMBOLS = {
    "P4 timer/task adapter": "agon::extender::display::P4FrameService::start(",
    "logical frame state machine": "agon::extender::display::LogicalFrameService::servicePending()",
    "logical plane exchange": "agon::extender::display::PlaneStorage::swapPlanes()",
    "palette allocation": "agon::extender::display::PaletteState::createPalette(",
    "Copper signal-list update": "agon::extender::display::PaletteState::updateSignalList(",
    "pure base compositor": "agon::extender::display::PresentationCompositor::composeBase(",
    "quiescent controller composition": "agon::extender::display::P4DisplayController::composeVisibleRegionQuiescent(",
    "retained Canvas submission": "fabgl::Canvas::noOp()",
    "retained common primitive executor": "fabgl::BitmappedDisplayController::execPrimitive(",
}
EXCLUDED_SYMBOL_PREFIXES = [
    "fabgl::VGA", "fabgl::CVBS", "fabgl::Scene", "fabgl::PS2",
    "fabgl::SoundGenerator", "fabgl::FileBrowser",
]


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def compiled_application_sources(path: Path) -> list[str]:
    records = json.loads(path.read_text(encoding="utf-8"))
    vdp_root = ROOT / "vdp"
    found = set()
    for record in records:
        source = Path(record["file"]).resolve()
        try:
            candidate = source.relative_to(vdp_root).as_posix()
        except ValueError:
            continue
        if candidate.startswith(("video/", "vendor/vdp-gl/")):
            found.add(candidate)
    return sorted(found)


def loaded_application_objects(map_text: str, environment: str) -> list[str]:
    prefix = f".pio/build/{environment}/"
    return sorted({
        line.strip().removeprefix("LOAD ").removeprefix(prefix)
        for line in map_text.splitlines()
        if line.strip().startswith("LOAD ")
        and line.strip().removeprefix("LOAD ").startswith(
            (prefix + "selected-vdp-gl/", prefix + "video/")
        )
    })


def expected_objects(selection: dict[str, Any]) -> dict[str, str]:
    result = {
        source: f"{source}.o" for source in selection["project_translation_units"]
    }
    result.update({
        source: f"selected-vdp-gl/{Path(source).stem}.o"
        for source in selection["vendored_translation_units"]
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build-dir", type=Path,
        default=ROOT / "vdp/.pio/build/p4-presentation",
    )
    parser.add_argument("--nm", type=Path, required=True)
    parser.add_argument(
        "--closure-output", type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-d/evidence/build-closure.yaml",
    )
    parser.add_argument(
        "--exclusions-output", type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-d/evidence/link-exclusions.yaml",
    )
    args = parser.parse_args()

    selection_path = ROOT / "vdp/pio/p4-presentation-source-selection.json"
    build_dir = args.build_dir.resolve()
    compile_commands = build_dir / "compile_commands.json"
    map_path = build_dir / "firmware.map"
    elf_path = build_dir / "firmware.elf"
    binary_path = build_dir / "firmware.bin"
    for path in (selection_path, compile_commands, map_path, elf_path,
                 binary_path, args.nm):
        if not path.is_file():
            raise FileNotFoundError(path)

    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection["environment"] != "p4-presentation":
        raise ValueError("source selection is not the Phase D environment")
    map_text = map_path.read_text(encoding="utf-8", errors="replace")
    symbols = subprocess.run(
        [str(args.nm), "-C", str(elf_path)], check=True,
        capture_output=True, text=True,
    ).stdout
    undefined = subprocess.run(
        [str(args.nm), "-uC", str(elf_path)], check=True,
        capture_output=True, text=True,
    ).stdout.splitlines()

    expected = expected_objects(selection)
    compiled = compiled_application_sources(compile_commands)
    loaded = loaded_application_objects(map_text, selection["environment"])
    expected_project = sorted(selection["project_translation_units"])
    missing_objects = sorted(set(expected.values()) - set(loaded))
    unexpected_objects = sorted(set(loaded) - set(expected.values()))
    missing_compile = sorted(set(expected_project) - set(compiled))
    unexpected_compile = sorted(set(compiled) - set(expected_project))
    symbol_checks = [
        {"claim": claim, "symbol_fragment": fragment, "present": fragment in symbols}
        for claim, fragment in REQUIRED_SYMBOLS.items()
    ]
    source_matches = {
        pattern: sorted(source for source in expected if fnmatch.fnmatch(source, pattern))
        for pattern in selection["excluded_source_families"]
    }
    symbol_matches = {
        prefix: sorted(line.strip() for line in symbols.splitlines() if prefix in line)
        for prefix in EXCLUDED_SYMBOL_PREFIXES
    }
    closure_ok = not (
        missing_objects or unexpected_objects or missing_compile or unexpected_compile
        or any(not check["present"] for check in symbol_checks)
    )
    exclusions_ok = not any(source_matches.values()) and not any(symbol_matches.values())
    inputs = {
        "source_selection": {
            "path": relative(selection_path), "sha256": sha256_file(selection_path),
        },
        "compile_commands": {
            "path": relative(compile_commands), "sha256": sha256_file(compile_commands),
        },
        "linker_map": {"path": relative(map_path), "sha256": sha256_file(map_path)},
        "normalized_elf_symbols_sha256": sha256_bytes(symbols.encode()),
    }
    closure = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_d_build_closure",
        "generated_by": "docs/tasks/PORT-003/phase-d/scripts/validate-phase-d.py",
        "diagnostic_status": (
            "clean P4 compile/link evidence only; not deployment, artifact identity, "
            "physical qualification, or output-sink qualification"
        ),
        "environment": selection["environment"],
        "build_invocation": ".venv/bin/pio run -d vdp -e p4-presentation",
        "inputs": inputs,
        "firmware": {
            "path": relative(binary_path),
            "sha256": sha256_file(binary_path),
            "size_bytes": binary_path.stat().st_size,
        },
        "application_translation_units": [
            {"source": source, "object": expected[source],
             "object_loaded": expected[source] in loaded}
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
            "missing_project_compile_records": missing_compile,
            "unexpected_project_compile_records": unexpected_compile,
            "closure_proved": closure_ok,
        },
    }
    exclusions = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_d_link_exclusions",
        "generated_by": "docs/tasks/PORT-003/phase-d/scripts/validate-phase-d.py",
        "diagnostic_status": "VDP application closure only; framework components are out of scope",
        "environment": selection["environment"],
        "source_pattern_matches": source_matches,
        "symbol_prefix_matches": symbol_matches,
        "summary": {
            "source_match_count": sum(map(len, source_matches.values())),
            "symbol_match_count": sum(map(len, symbol_matches.values())),
            "exclusions_proved": exclusions_ok,
        },
    }
    write_canonical(args.closure_output.resolve(), closure)
    write_canonical(args.exclusions_output.resolve(), exclusions)
    if not closure_ok or not exclusions_ok:
        raise SystemExit("Phase D closure validation failed")
    print(
        f"proved {len(expected)} selected units, {len(symbol_checks)} required "
        "symbols, and zero exclusions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
