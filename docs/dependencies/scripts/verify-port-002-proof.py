#!/usr/bin/env python3
"""Verify and record the six accepted PORT-002 source-selection proof cases."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from dependency_model import artifact_hash, load_data, write_canonical


OBSERVED = "build-profile:upstream:agon-vdp-v2.16.0-esp32"
TARGET = "build-profile:extender:p4-default"


def case_result(name: str, subjects: list[str], assertions: list[tuple[bool, str]], records: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    failed = [message for passed, message in assertions if not passed]
    return {
        "id": name,
        "status": "pass" if not failed else "fail",
        "subjects": subjects,
        "assertions": [message for _, message in assertions],
        "failures": failed,
        "selection_records": [records[(profile, subject)]["id"] for subject in subjects for profile in (OBSERVED, TARGET) if (profile, subject) in records],
    }


def build_report(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = {node["id"]: node for node in graph["nodes"]}
    records = {(item["build_profile_id"], item["subject_id"]): item for item in graph["selection_records"]}

    ds = "file:vdp-gl:src/devdrivers/DS3231.cpp"
    fab = "file:vdp-gl:src/fabutils.cpp"
    browser = "source-region:vdp-gl:src/fabutils.cpp:storage-vdp-gl-filebrowser-api"
    storage = "source-region:vdp-gl:src/fabutils.cpp:storage-vdp-gl-esp32-mount-format-backends"
    vga = "file:vdp-gl:src/dispdrivers/vga8controller.cpp"
    header = "file:agon-vdp:video/vdu.h"
    library = "file:ESP32Time:ESP32Time.cpp"
    license_file = "file:vdp-gl:LICENSE"

    cases = [
        case_result(
            "proof-1-ds3231-whole-file-exclusion",
            [ds],
            [
                (ds in nodes, "DS3231 exists in the exhaustive upstream manifest"),
                (records[(OBSERVED, ds)]["status"] == "selected", "upstream control build selects DS3231"),
                (records[(TARGET, ds)]["status"] == "excluded", "P4 target deliberately excludes DS3231"),
            ],
            records,
        ),
        case_result(
            "proof-2-fused-fabutils-regions",
            [fab, browser, storage],
            [
                (records[(TARGET, fab)]["status"] == "selected", "fabutils.cpp remains selected"),
                (records[(TARGET, browser)]["status"] == "excluded", "FileBrowser region is excluded"),
                (records[(TARGET, storage)]["status"] == "excluded", "classic ESP32 storage region is excluded"),
                (nodes[browser]["properties"]["region.boundary_status"] == "reviewed-exact-boundary", "FileBrowser carries an exact fingerprinted boundary"),
            ],
            records,
        ),
        case_result(
            "proof-3-vga-replacement-boundary",
            [vga],
            [
                (records[(OBSERVED, vga)]["status"] == "selected", "upstream control build selects concrete VGA source"),
                (records[(TARGET, vga)]["status"] == "excluded", "P4 target excludes concrete VGA source"),
                (records[(TARGET, vga)].get("replacement_subject_id") == "build-unit:extender:p4-port-adapters", "replacement points to the planned project adapter boundary"),
            ],
            records,
        ),
        case_result(
            "proof-4-header-defined-official-vdp",
            [header],
            [
                (records[(OBSERVED, header)]["status"] == "selected", "official implementation header is selected upstream"),
                (any(cause["code"] == "transitive-include" for cause in records[(OBSERVED, header)]["causes"]), "selection is mechanically represented as transitive include"),
                (records[(TARGET, header)]["status"] == "selected", "P4 compatibility target retains the header"),
            ],
            records,
        ),
        case_result(
            "proof-5-pinned-release-library",
            [library],
            [
                (nodes[library]["properties"]["source.identity"] == "2.0.6", "ESP32Time exact release identity is recorded"),
                (records[(OBSERVED, library)]["status"] == "selected", "upstream build selects the release source"),
                (records[(TARGET, library)]["status"] == "selected", "P4 target retains the release source"),
            ],
            records,
        ),
        case_result(
            "proof-6-license-visible-non-runtime",
            [license_file],
            [
                (nodes[license_file]["properties"]["source.role"] == "license", "license is classified explicitly"),
                (records[(TARGET, license_file)]["status"] == "not-applicable", "license is not a firmware build candidate"),
                (any(cause["code"] == "non-runtime-upstream-content" for cause in records[(TARGET, license_file)]["causes"]), "license remains merge-visible non-runtime content"),
            ],
            records,
        ),
    ]
    return {
        "schema_version": "1.0.0",
        "artifact_kind": "port_002_proof",
        "source_graph": {"id": graph["id"], "sha256": artifact_hash(graph)},
        "cases": cases,
        "summary": {"passed": sum(case["status"] == "pass" for case in cases), "failed": sum(case["status"] == "fail" for case in cases)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(load_data(args.graph))
    write_canonical(args.output, report)
    for case in report["cases"]:
        print(f"{case['status'].upper()}: {case['id']}")
    return 1 if report["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
