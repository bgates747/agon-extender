#!/usr/bin/env python3
"""Prove the PORT-003 Phase F P4 application and exclusion closure.

This validator distinguishes project-selected application code from the broad
component archives compiled by the pinned Arduino/ESP-IDF framework. A source
appearing in a framework build tree is not evidence that Extender selected or
linked that feature; the final ELF, linker map, and tracked allowlist are the
authorities checked here.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_bytes, sha256_file, write_canonical  # noqa: E402

ENVIRONMENT = "p4-browser-vdp"
REQUIRED_SYMBOLS = {
    "Arduino setup lifecycle": "setup()",
    "Arduino loop lifecycle": "loop()",
    "official process task": "processLoop(void*)",
    "official stream parser": "VDUStreamProcessor::processNext()",
    "official General Poll startup gate": "VDUStreamProcessor::sendGeneralPoll()",
    "official complete mode switch": "changeMode(unsigned char)",
    "official Teletext initialization": "agon_ttxt::init()",
    "project official-mode facade": "agon::extender::display::ScreenFacadeAdapter::configure(",
    "P4 timer/task adapter": "agon::extender::display::P4FrameService::start(",
    "project concrete controller": "vtable for agon::extender::display::P4DisplayController",
    "immutable snapshot producer": "agon::extender::display::PresentationSnapshotPool::tryBegin(",
    "immutable snapshot consumer": "agon::extender::display::PresentationSnapshotPool::tryAcquireLatest(",
    "EVF1 snapshot bridge": "agon::extender::web::BrowserVideoProvider::tryAcquireAfter(",
    "wired network owner": "agon::extender::network::WiredNetworkService::start()",
    "deliberately disconnected ingress": "agon::extender::transport::DisconnectedStream::available()",
    "P4 watchdog adapter": "agon::extender::port::disableRetainedVdpIdleWatchdogs()",
}
EXCLUDED_SYMBOL_FRAGMENTS = [
    "fabgl::VGA",
    "fabgl::CVBS",
    "fabgl::Scene",
    "fabgl::PS2",
    "fabgl::SoundGenerator",
    "fabgl::FileBrowser",
    "fabgl::Terminal",
    "YModem",
    "YMODEM",
    "agon::extender::transport::Parallel",
    "agon::extender::transport::Return",
    "agon::extender::transport::Uart",
]
EXCLUDED_STORAGE_SYMBOL_FRAGMENTS = [
    "fs::FS::",
    "fs::File::",
    "SDClass::",
    "SDFS::",
    "SPIFFSFS::",
    "LittleFSFS::",
]
WIFI_OPERATIONAL_SYMBOL_FRAGMENTS = [
    "WiFiSTAClass::begin(",
    "WiFiSTAClass::connect(",
    "WiFiAPClass::softAP(",
    "WiFiScanClass::scanNetworks(",
    "WiFiGenericClass::mode(",
    "WiFiGenericClass::enableSTA(",
    "WiFiGenericClass::enableAP(",
]
ALLOWED_WIFI_FRAMEWORK_RESIDUE = {
    "WiFi",
    "WiFiClass::~WiFiClass()",
    "WiFiGenericClass::WiFiGenericClass()",
    "_GLOBAL__sub_I__ZN9WiFiClass9printDiagER5Print",
}
REQUIRED_DIAGNOSTIC_STRING_FRAGMENTS = [
    "source_identity=%s",
    "build_id=%s",
    "artifact_status=%s",
    "enabled=%u alloc_fail=%u cadence=%u transition=%u",
    "state=%u clients=%u refused=%u credits=%u protocol=%u",
    "acquired=%u no_new=%u invalid=%u sent=%u failed=%u",
    "free_8bit=%u minimum_8bit=%u free_psram=%u minimum_psram=%u",
    "retained VDP IDLE watchdog subscriptions disabled",
    "retained VDP watchdog setup failed",
]
WATCHDOG_SOURCE_BOUNDARY = re.compile(
    r"#ifndef\s+VDP_USE_WDT\s+"
    r"#ifdef\s+AGON_EXTENDER_P4_BOOT\s+"
    r".*?disableRetainedVdpIdleWatchdogs\(\).*?"
    r"delay\(200\);\s+delay\(200\);\s+"
    r"#else\s+"
    r"disableCore0WDT\(\);\s+delay\(200\);.*?"
    r"disableCore1WDT\(\);\s+delay\(200\);\s+"
    r"#endif\s+#endif",
    re.DOTALL,
)


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def symbol_name(line: str) -> str:
    fields = line.strip().split(maxsplit=2)
    return fields[2] if len(fields) == 3 else line.strip()


def application_compile_records(path: Path) -> dict[str, dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    vdp_root = ROOT / "vdp"
    found: dict[str, dict[str, Any]] = {}
    for record in records:
        source = Path(record["file"]).resolve()
        try:
            candidate = source.relative_to(vdp_root).as_posix()
        except ValueError:
            continue
        if not candidate.startswith(("video/", "vendor/")):
            continue
        command = record.get("command")
        arguments = shlex.split(command) if command is not None else record["arguments"]
        standards = [arg for arg in arguments if arg.startswith("-std=")]
        found[candidate] = {
            "standards": standards,
            "effective_standard": standards[-1] if standards else None,
        }
    return found


def loaded_application_objects(map_text: str) -> list[str]:
    prefix = f".pio/build/{ENVIRONMENT}/"
    owned_prefixes = (
        prefix + "selected-vdp-gl/",
        prefix + "video/",
        prefix + "vendor/",
    )
    return sorted({
        line.strip().removeprefix("LOAD ").removeprefix(prefix)
        for line in map_text.splitlines()
        if line.strip().startswith("LOAD ")
        and line.strip().removeprefix("LOAD ").startswith(owned_prefixes)
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


def embedded_object(path: str) -> str:
    return Path(path).name + ".S.o"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build-dir", type=Path,
        default=ROOT / f"vdp/.pio/build/{ENVIRONMENT}",
    )
    parser.add_argument(
        "--nm", type=Path,
        default=ROOT / "vdp/.pio/packages/toolchain-riscv32-esp/bin/riscv32-esp-elf-nm",
    )
    parser.add_argument("--expected-source-identity")
    parser.add_argument("--expected-build-id")
    parser.add_argument("--expected-artifact-status")
    parser.add_argument(
        "--closure-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-f/evidence/build-closure.yaml",
        help="write build-closure evidence here",
    )
    parser.add_argument(
        "--exclusions-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-f/evidence/link-exclusions.yaml",
        help="write link-exclusion evidence here",
    )
    args = parser.parse_args()
    expected_identities = {
        "source_identity": args.expected_source_identity,
        "build_id": args.expected_build_id,
        "artifact_status": args.expected_artifact_status,
    }
    supplied_identity_fields = [
        name for name, value in expected_identities.items() if value is not None
    ]
    if supplied_identity_fields and len(supplied_identity_fields) != len(expected_identities):
        parser.error("all three expected identity fields must be supplied together")
    selection_path = ROOT / f"vdp/pio/{ENVIRONMENT}-source-selection.json"
    generated_cmake = ROOT / "vdp/video/CMakeLists.txt"
    build_dir = args.build_dir.resolve()
    compile_commands = build_dir / "compile_commands.json"
    map_path = build_dir / "firmware.map"
    elf_path = build_dir / "firmware.elf"
    binary_path = build_dir / "firmware.bin"
    factory_path = build_dir / "firmware.factory.bin"
    required_files = (
        selection_path, generated_cmake, compile_commands, map_path, elf_path,
        binary_path, factory_path, args.nm,
    )
    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(path)

    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection["environment"] != ENVIRONMENT:
        raise ValueError("source selection describes another environment")
    map_text = map_path.read_text(encoding="utf-8", errors="replace")
    symbols = subprocess.run(
        [str(args.nm), "-C", str(elf_path)], check=True, capture_output=True, text=True
    ).stdout
    image_strings = subprocess.run(
        ["strings", str(elf_path)], check=True, capture_output=True, text=True
    ).stdout.splitlines()
    undefined = subprocess.run(
        [str(args.nm), "-uC", str(elf_path)], check=True, capture_output=True, text=True
    ).stdout.splitlines()

    expected = expected_objects(selection)
    compile_records = application_compile_records(compile_commands)
    loaded = loaded_application_objects(map_text)
    expected_project = sorted(selection["project_translation_units"])
    expected_embedded = sorted(embedded_object(path) for path in selection["embedded_text_files"])
    loaded_embedded = sorted({
        line.strip().removeprefix("LOAD ").removeprefix(f".pio/build/{ENVIRONMENT}/")
        for line in map_text.splitlines()
        if line.strip().startswith(f"LOAD .pio/build/{ENVIRONMENT}/")
        and line.strip().removeprefix(f"LOAD .pio/build/{ENVIRONMENT}/") in expected_embedded
    })
    missing_objects = sorted(set(expected.values()) - set(loaded))
    unexpected_objects = sorted(set(loaded) - set(expected.values()))
    missing_compile = sorted(set(expected_project) - set(compile_records))
    unexpected_compile = sorted(set(compile_records) - set(expected_project))
    standard_mismatches = {
        source: compile_records[source]
        for source in expected_project
        if source in compile_records
        and compile_records[source]["effective_standard"] != "-std=gnu++17"
    }
    missing_embedded = sorted(set(expected_embedded) - set(loaded_embedded))
    unexpected_embedded = sorted(set(loaded_embedded) - set(expected_embedded))

    symbol_checks = [
        {"claim": claim, "symbol_fragment": fragment, "present": fragment in symbols}
        for claim, fragment in REQUIRED_SYMBOLS.items()
    ]
    embedded_symbol_checks = []
    for path in selection["embedded_text_files"]:
        stem = re.sub(r"[^A-Za-z0-9]", "_", Path(path).name)
        for endpoint in ("start", "end"):
            fragment = f"_binary_{stem}_{endpoint}"
            embedded_symbol_checks.append({
                "source": path,
                "endpoint": endpoint,
                "symbol_fragment": fragment,
                "present": fragment in symbols,
            })

    source_matches = {
        pattern: sorted(source for source in expected if fnmatch.fnmatch(source, pattern))
        for pattern in selection["excluded_source_families"]
    }
    symbol_matches = {
        fragment: sorted(
            line.strip() for line in symbols.splitlines() if fragment in line
        )
        for fragment in EXCLUDED_SYMBOL_FRAGMENTS
    }
    storage_symbol_matches = {
        fragment: sorted(
            line.strip() for line in symbols.splitlines() if fragment in line
        )
        for fragment in EXCLUDED_STORAGE_SYMBOL_FRAGMENTS
    }
    wifi_symbols = sorted({
        symbol_name(line) for line in symbols.splitlines() if "WiFi" in line
    })
    unexpected_wifi_residue = sorted(set(wifi_symbols) - ALLOWED_WIFI_FRAMEWORK_RESIDUE)
    missing_wifi_residue = sorted(ALLOWED_WIFI_FRAMEWORK_RESIDUE - set(wifi_symbols))
    wifi_operational_matches = {
        fragment: sorted(
            line.strip() for line in symbols.splitlines() if fragment in line
        )
        for fragment in WIFI_OPERATIONAL_SYMBOL_FRAGMENTS
    }
    selected_wifi_references = {}
    for source in expected_project:
        text = (ROOT / "vdp" / source).read_text(encoding="utf-8", errors="replace")
        if re.search(r"#\s*include\s*[<\"]WiFi|\bWiFi(?:STA|AP|Scan|Class)?\b", text):
            selected_wifi_references[source] = sorted(set(
                match.group(0) for match in re.finditer(
                    r"#\s*include\s*[<\"]WiFi[^>\"]*[>\"]|\bWiFi(?:STA|AP|Scan|Class)?\b",
                    text,
                )
            ))

    cmake_text = generated_cmake.read_text(encoding="utf-8")
    cmake_standard_pinned = (
        'target_compile_options(${COMPONENT_LIB} PRIVATE "-std=gnu++17")'
        in cmake_text
    )
    arduino_version_strings = sorted({
        line.strip() for line in image_strings
        if re.fullmatch(r"\d+\.\d+\.\d+", line.strip())
    })
    arduino_3_3_11_identified = "3.3.11" in arduino_version_strings
    diagnostic_string_checks = [
        {
            "fragment": fragment,
            "present": any(fragment in line for line in image_strings),
        }
        for fragment in REQUIRED_DIAGNOSTIC_STRING_FRAGMENTS
    ]
    video_source = (ROOT / "vdp/video/video.ino").read_text(encoding="utf-8")
    watchdog_source_boundary = {
        "p4_adapter_branch_present": bool(WATCHDOG_SOURCE_BOUNDARY.search(video_source)),
        "stock_core0_call_count": video_source.count("disableCore0WDT();"),
        "stock_core1_call_count": video_source.count("disableCore1WDT();"),
    }
    watchdog_source_boundary["proved"] = (
        watchdog_source_boundary["p4_adapter_branch_present"]
        and watchdog_source_boundary["stock_core0_call_count"] == 1
        and watchdog_source_boundary["stock_core1_call_count"] == 1
    )
    identity_checks = {
        name: {
            "expected": value,
            "present": value is not None and value in image_strings,
        }
        for name, value in expected_identities.items()
    }
    rejected_identity_marker_present = any(
        "UNVERSIONED-DO-NOT-DEPLOY" in line for line in image_strings
    )
    deployable_identity_required = bool(supplied_identity_fields)
    requested_identity_validation_ok = not deployable_identity_required or (
        all(check["present"] for check in identity_checks.values())
        and not rejected_identity_marker_present
    )
    deployable_identity_proved = deployable_identity_required and (
        all(check["present"] for check in identity_checks.values())
        and not rejected_identity_marker_present
    )
    closure_ok = not (
        missing_objects or unexpected_objects or missing_compile or unexpected_compile
        or standard_mismatches or missing_embedded or unexpected_embedded
        or any(not check["present"] for check in symbol_checks)
        or any(not check["present"] for check in embedded_symbol_checks)
        or not cmake_standard_pinned
        or not arduino_3_3_11_identified
        or any(not check["present"] for check in diagnostic_string_checks)
        or not watchdog_source_boundary["proved"]
        or not requested_identity_validation_ok
    )
    exclusions_ok = not (
        any(source_matches.values())
        or any(symbol_matches.values())
        or any(storage_symbol_matches.values())
        or any(wifi_operational_matches.values())
        or unexpected_wifi_residue
        or missing_wifi_residue
        or selected_wifi_references
    )

    inputs = {
        "source_selection": {
            "path": relative(selection_path), "sha256": sha256_file(selection_path),
        },
        "generated_application_cmake": {
            "path": relative(generated_cmake), "sha256": sha256_file(generated_cmake),
        },
        "compile_commands": {
            "path": relative(compile_commands), "sha256": sha256_file(compile_commands),
        },
        "linker_map": {"path": relative(map_path), "sha256": sha256_file(map_path)},
        "normalized_elf_symbols_sha256": sha256_bytes(symbols.encode()),
    }
    closure = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_build_closure",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/validate-phase-f-build.py",
        "diagnostic_status": "clean P4 compile/link evidence only; no deployment, VDU ingress, return transport, or hardware claim",
        "environment": ENVIRONMENT,
        "build_invocation": "scripts/vdp-pio.sh run -e p4-browser-vdp",
        "inputs": inputs,
        "firmware": {
            "path": relative(binary_path),
            "sha256": sha256_file(binary_path),
            "size_bytes": binary_path.stat().st_size,
        },
        "factory_firmware": {
            "path": relative(factory_path),
            "sha256": sha256_file(factory_path),
            "size_bytes": factory_path.stat().st_size,
        },
        "header_defined_official_implementation": [
            {"path": path, "sha256": sha256_file(ROOT / "vdp" / path)}
            for path in selection["header_defined_official_implementation"]
        ],
        "application_translation_units": [
            {
                "source": source,
                "object": expected[source],
                "object_loaded": expected[source] in loaded,
                **(
                    {"compiler": compile_records[source]}
                    if source in compile_records else {}
                ),
            }
            for source in sorted(expected)
        ],
        "embedded_assets": [
            {
                "source": source,
                "object": embedded_object(source),
                "object_loaded": embedded_object(source) in loaded_embedded,
            }
            for source in selection["embedded_text_files"]
        ],
        "required_elf_symbols": symbol_checks,
        "embedded_asset_symbols": embedded_symbol_checks,
        "diagnostic_strings": diagnostic_string_checks,
        "watchdog_source_boundary": watchdog_source_boundary,
        "identity": {
            "deployable_identity_required": deployable_identity_required,
            "checks": identity_checks,
            "rejected_marker_present": rejected_identity_marker_present,
            "identity_state": (
                "identified-deployable"
                if deployable_identity_proved
                else "unversioned-do-not-deploy"
            ),
            "requested_identity_validation_ok": requested_identity_validation_ok,
            "deployable_identity_proved": deployable_identity_proved,
        },
        "undefined_elf_symbols": sorted(line.strip() for line in undefined),
        "summary": {
            "selected_translation_unit_count": len(expected),
            "project_translation_unit_count": len(expected_project),
            "vendored_translation_unit_count": len(selection["vendored_translation_units"]),
            "embedded_asset_count": len(expected_embedded),
            "missing_objects": missing_objects,
            "unexpected_application_objects": unexpected_objects,
            "missing_project_compile_records": missing_compile,
            "unexpected_project_compile_records": unexpected_compile,
            "compiler_standard_mismatches": standard_mismatches,
            "missing_embedded_objects": missing_embedded,
            "unexpected_embedded_objects": unexpected_embedded,
            "generated_cmake_pins_cxx17": cmake_standard_pinned,
            "image_identifies_arduino_3_3_11": arduino_3_3_11_identified,
            "runtime_diagnostic_strings_present": all(
                check["present"] for check in diagnostic_string_checks
            ),
            "watchdog_source_boundary_proved": watchdog_source_boundary["proved"],
            "semantic_version_strings_in_image": arduino_version_strings,
            "closure_proved": closure_ok,
        },
    }
    exclusions = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_link_exclusions",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/validate-phase-f-build.py",
        "diagnostic_status": "project-selected application closure; broad framework archive compilation is recorded separately and is not an Extender feature claim",
        "environment": ENVIRONMENT,
        "source_pattern_matches": source_matches,
        "symbol_fragment_matches": symbol_matches,
        "storage_symbol_fragment_matches": storage_symbol_matches,
        "wifi": {
            "selected_project_source_references": selected_wifi_references,
            "operational_symbol_matches": wifi_operational_matches,
            "allowed_framework_residue": sorted(ALLOWED_WIFI_FRAMEWORK_RESIDUE),
            "observed_framework_residue": wifi_symbols,
            "missing_allowed_residue": missing_wifi_residue,
            "unexpected_residue": unexpected_wifi_residue,
            "classification": "Arduino Ethernet dependency packaging contributes an unused global WiFi object constructor/destructor; no project source selects Wi-Fi and no operational Wi-Fi API is linked",
        },
        "framework_boundary": {
            "classification": "Arduino/ESP-IDF and managed-component archives are dependencies, not project-selected application translation units",
            "application_object_prefixes": ["selected-vdp-gl/", "video/", "vendor/"],
            "absolute hardware-register symbols_are_not_storage_api_evidence": True,
        },
        "summary": {
            "source_match_count": sum(map(len, source_matches.values())),
            "symbol_match_count": sum(map(len, symbol_matches.values())),
            "storage_symbol_match_count": sum(map(len, storage_symbol_matches.values())),
            "wifi_operational_symbol_match_count": sum(map(len, wifi_operational_matches.values())),
            "exclusions_proved": exclusions_ok,
        },
    }
    write_canonical(args.closure_output, closure)
    write_canonical(args.exclusions_output, exclusions)
    if not closure_ok or not exclusions_ok:
        raise SystemExit("Phase F closure validation failed")
    print(
        f"proved {len(expected)} selected units, {len(expected_embedded)} assets, "
        f"{len(symbol_checks)} required symbols, C++17, and all exclusions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
