#!/usr/bin/env python3
"""Generate the bounded PORT-003 display-boundary evidence projection.

This is task-local analysis machinery, not firmware. It deliberately consumes
the durable dependency graph and immutable upstream trees so PORT-003 can be
reviewed without creating a second hand-maintained source-selection authority.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
DEPENDENCY_SCRIPTS = REPOSITORY_ROOT / "docs/dependencies/scripts"
sys.path.insert(0, str(DEPENDENCY_SCRIPTS))

from dependency_model import artifact_hash, load_data, write_canonical  # noqa: E402


PROFILE = "build-profile:extender:p4-default"
DISPOSITION_PREFIX = "SETUP-004.1.d:"

SOURCE_ROOTS = {
    "agon-vdp": "source:agon-vdp:v2.16.0",
    "vdp-gl": "source:vdp-gl:all-the-plots",
}

PLATFORM_FILES = {
    "rgb-panel": "esp32p4/include/esp_lcd/rgb/include/esp_lcd_panel_rgb.h",
    "mipi-dsi": "esp32p4/include/esp_lcd/dsi/include/esp_lcd_mipi_dsi.h",
    "capability-heap": "esp32p4/include/heap/include/esp_heap_caps.h",
    "cache": "esp32p4/include/esp_mm/include/esp_cache.h",
    "timer": "esp32p4/include/esp_timer/include/esp_timer.h",
}

PLATFORM_PATTERNS = {
    "frame-consumer-callback": re.compile(r"\bon_(?:vsync|frame_buf_complete|color_trans_done)\b"),
    "multiple-framebuffers": re.compile(r"\b(?:num_fbs|double_fb)\b"),
    "psram-framebuffer": re.compile(r"\bfb_in_psram\b"),
    "bounce-buffer": re.compile(r"\b(?:bounce_buffer_size_px|on_bounce_empty)\b"),
    "refresh-on-demand": re.compile(r"\brefresh_on_demand\b"),
    "dma2d-copy": re.compile(r"\buse_dma2d\b"),
    "capability-allocation": re.compile(r"\b(?:heap_caps_\w*|MALLOC_CAP_(?:DMA|SPIRAM|INTERNAL))\b"),
    "cache-maintenance": re.compile(r"\besp_cache_\w*\b"),
    "logical-timer": re.compile(r"\besp_timer_(?:create|start_periodic|stop|delete)\b"),
}

ARCHITECTURE_PATTERNS = {
    "classic-esp32-i2s": re.compile(r"\b(?:I2S[01]|ETS_I2S\w*|i2s_(?:struct|reg))\b"),
    "classic-dma-descriptor": re.compile(r"\b(?:lldesc_t|DMABuffer\w*|MALLOC_CAP_DMA)\b"),
    "gpio-signal-routing": re.compile(r"\b(?:GPIO\w*|gpio_matrix\w*)\b"),
    "interrupt-or-isr": re.compile(r"\b(?:IRAM_ATTR|FromISR|intr_alloc\w*|Interrupt)\b"),
    "xtensa-coprocessor": re.compile(r"\b(?:xthal_\w*|xtensa\w*)\b", re.IGNORECASE),
    "core-affinity": re.compile(r"\b(?:xTaskCreatePinnedToCore|CoreUsage|CPUINTENSIVE_TASKS_CORE)\b"),
    "flash-cache-assumption": re.compile(r"\bspi_flash_cache_enabled\b"),
    "capability-heap": re.compile(r"\b(?:heap_caps_\w*|MALLOC_CAP_(?:INTERNAL|SPIRAM|8BIT|32BIT))\b"),
    "physical-frame-clock": re.compile(r"\b(?:VSync\w*|vsync\w*|frameCounter)\b"),
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def location_path(node: dict[str, Any]) -> str | None:
    for location in node.get("locations", []):
        if location.get("path"):
            return location["path"]
    return None


def candidates_from(record: dict[str, Any]) -> list[str]:
    candidates = {
        ref.split(":", 2)[1]
        for ref in record["disposition_refs"]
        if ref.startswith(DISPOSITION_PREFIX) and ref.count(":") >= 2
    }
    return sorted(candidates)


def source_path(owner: str, relative: str, roots: dict[str, Path]) -> Path:
    if owner not in roots:
        raise ValueError(f"no source root for {owner}")
    return roots[owner] / relative


def scan_architecture(
    files: list[dict[str, Any]], roots: dict[str, Path]
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for item in files:
        owner = item["owner"]
        relative = item["path"]
        path = source_path(owner, relative, roots)
        lines = path.read_text(errors="replace").splitlines()
        for line_number, line in enumerate(lines, 1):
            categories = [name for name, pattern in ARCHITECTURE_PATTERNS.items() if pattern.search(line)]
            if categories:
                findings.append(
                    {
                        "owner": owner,
                        "path": relative,
                        "line": line_number,
                        "categories": categories,
                        "text": line.strip(),
                    }
                )
    return sorted(findings, key=lambda item: (item["owner"], item["path"], item["line"]))


def extract_pure_virtuals(path: Path, owner: str, relative: str) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        stripped = line.strip()
        in_selected_contract = 805 <= line_number <= 868 or 897 <= line_number <= 1230
        if in_selected_contract and stripped.startswith("virtual ") and stripped.endswith("= 0;"):
            contracts.append(
                {
                    "owner": owner,
                    "path": relative,
                    "line": line_number,
                    "declaration": stripped,
                }
            )
    return contracts


def scan_platform(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sources: list[dict[str, Any]] = []
    capabilities: list[dict[str, Any]] = []
    for facility, relative in sorted(PLATFORM_FILES.items()):
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        sources.append(
            {
                "facility": facility,
                "path": relative,
                "sha256": file_sha256(path),
            }
        )
        for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            categories = [name for name, pattern in PLATFORM_PATTERNS.items() if pattern.search(line)]
            if categories:
                capabilities.append(
                    {
                        "facility": facility,
                        "path": relative,
                        "line": line_number,
                        "categories": categories,
                        "text": line.strip(),
                    }
                )
    return sources, sorted(capabilities, key=lambda item: (item["path"], item["line"]))


def bounded_related_files(
    graph: dict[str, Any], seeds: set[str], selected: dict[str, dict[str, Any]], maximum_depth: int
) -> list[dict[str, Any]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        adjacency[edge["from"]].add(edge["to"])
        adjacency[edge["to"]].add(edge["from"])
    nodes = {node["id"]: node for node in graph["nodes"]}
    queue = deque((seed, 0) for seed in sorted(seeds))
    distances = {seed: 0 for seed in seeds}
    while queue:
        current, distance = queue.popleft()
        if distance >= maximum_depth:
            continue
        for neighbor in sorted(adjacency.get(current, ())):
            if neighbor not in distances:
                distances[neighbor] = distance + 1
                queue.append((neighbor, distance + 1))
    result = []
    for subject_id, record in selected.items():
        if subject_id not in distances:
            continue
        node = nodes[subject_id]
        if node["kind"] != "file":
            continue
        result.append(
            {
                "subject_id": subject_id,
                "owner": node["owner"],
                "path": node.get("properties", {}).get("source.path", node["label"]),
                "distance": distances[subject_id],
                "status": record["status"],
                "causes": [cause["code"] for cause in record["causes"]],
            }
        )
    return sorted(result, key=lambda item: (item["distance"], item["owner"], item["path"]))


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# PORT-003 display evidence",
        "",
        "Generated by `scripts/generate-display-evidence.py`; do not edit by hand.",
        "",
        f"Canonical graph: `{data['source_graph']['id']}` (`{data['source_graph']['sha256']}`)",
        "",
        "## Work 1.d source decisions",
        "",
        "| Candidate | Selected | Excluded | Regions |",
        "|---|---:|---:|---:|",
    ]
    for candidate in data["candidates"]:
        lines.append(
            f"| `{candidate['id']}` | {candidate['summary']['selected_files']} | "
            f"{candidate['summary']['excluded_files']} | {candidate['summary']['source_regions']} |"
        )
    lines.extend(
        [
            "",
            "## Abstract controller contract",
            "",
            "| Source | Line | Declaration |",
            "|---|---:|---|",
        ]
    )
    for contract in data["abstract_contract"]:
        declaration = contract["declaration"].replace("|", "\\|")
        lines.append(f"| `{contract['path']}` | {contract['line']} | `{declaration}` |")
    lines.extend(
        [
            "",
            "## Architecture-assumption counts",
            "",
            "| Category | Hits |",
            "|---|---:|",
        ]
    )
    for name, count in data["summary"]["architecture_hits_by_category"].items():
        lines.append(f"| `{name}` | {count} |")
    lines.extend(
        [
            "",
            "## Pinned P4 platform headers",
            "",
            f"Platform source: `{data['platform']['source_id']}`",
            "",
            "| Facility | Path | SHA-256 |",
            "|---|---|---|",
        ]
    )
    for source in data["platform"]["sources"]:
        lines.append(f"| `{source['facility']}` | `{source['path']}` | `{source['sha256']}` |")
    lines.extend(
        [
            "",
            f"Matched platform declarations: {data['summary']['platform_capability_count']}.",
            "",
            "The YAML companion retains every bounded hit, source fingerprint, disposition, symbol, and closure record.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--agon-vdp-root", type=Path, required=True)
    parser.add_argument("--vdp-gl-root", type=Path, required=True)
    parser.add_argument("--p4-framework-root", type=Path, required=True)
    parser.add_argument("--yaml", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    roots = {"agon-vdp": args.agon_vdp_root, "vdp-gl": args.vdp_gl_root}
    graph = load_data(args.graph)
    nodes = {node["id"]: node for node in graph["nodes"]}
    selections = {
        record["subject_id"]: record
        for record in graph["selection_records"]
        if record["build_profile_id"] == PROFILE
    }

    candidate_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    direct_file_ids: set[str] = set()
    direct_files: dict[tuple[str, str], dict[str, Any]] = {}
    for record in selections.values():
        candidates_for_record = candidates_from(record)
        if not candidates_for_record:
            continue
        node = nodes[record["subject_id"]]
        item = {
            "subject_id": node["id"],
            "kind": node["kind"],
            "owner": node["owner"],
            "path": node.get("properties", {}).get("source.path", location_path(node)),
            "label": node["label"],
            "status": record["status"],
            "causes": [cause["code"] for cause in record["causes"]],
            "disposition_refs": record["disposition_refs"],
        }
        for candidate in candidates_for_record:
            candidate_records[candidate].append(item)
        if node["kind"] == "file":
            direct_file_ids.add(node["id"])
            direct_files[(item["owner"], item["path"])] = item

    sources = []
    for (owner, relative), item in sorted(direct_files.items()):
        path = source_path(owner, relative, roots)
        if not path.is_file():
            raise FileNotFoundError(path)
        expected = nodes[item["subject_id"]].get("properties", {}).get("source.sha256")
        actual = file_sha256(path)
        if expected and expected != actual:
            raise ValueError(f"source fingerprint mismatch: {owner}:{relative}")
        sources.append(
            {
                "owner": owner,
                "source_id": SOURCE_ROOTS[owner],
                "path": relative,
                "sha256": actual,
                "status": item["status"],
            }
        )

    symbols = []
    for node in graph["nodes"]:
        if node["kind"] not in {"function", "method", "type", "variable"}:
            continue
        locations = [
            location
            for location in node.get("locations", [])
            if f"file:{node['owner']}:{location.get('path')}" in direct_file_ids
        ]
        if locations:
            symbols.append(
                {
                    "id": node["id"],
                    "kind": node["kind"],
                    "owner": node["owner"],
                    "label": node["label"],
                    "locations": locations,
                }
            )
    symbols.sort(key=lambda item: item["id"])

    candidates = []
    for candidate, records in sorted(candidate_records.items()):
        records.sort(key=lambda item: item["subject_id"])
        candidates.append(
            {
                "id": candidate,
                "records": records,
                "summary": {
                    "selected_files": sum(item["kind"] == "file" and item["status"] == "selected" for item in records),
                    "excluded_files": sum(item["kind"] == "file" and item["status"] == "excluded" for item in records),
                    "source_regions": sum(item["kind"] == "source-region" for item in records),
                },
            }
        )

    contract_path = roots["vdp-gl"] / "src/displaycontroller.h"
    abstract_contract = extract_pure_virtuals(contract_path, "vdp-gl", "src/displaycontroller.h")
    architecture_hits = scan_architecture(sources, roots)
    category_counts = {
        category: sum(category in hit["categories"] for hit in architecture_hits)
        for category in sorted(ARCHITECTURE_PATTERNS)
    }
    related_files = bounded_related_files(graph, direct_file_ids, selections, maximum_depth=3)
    platform_sources, platform_capabilities = scan_platform(args.p4_framework_root)

    data = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_display_evidence",
        "generated_by": "docs/tasks/PORT-003/scripts/generate-display-evidence.py",
        "source_graph": {"id": graph["id"], "sha256": artifact_hash(graph)},
        "build_profile": PROFILE,
        "source_roots": [
            {"owner": owner, "source_id": SOURCE_ROOTS[owner], "placeholder": f"${{{owner.upper().replace('-', '_')}_SOURCE}}"}
            for owner in sorted(SOURCE_ROOTS)
        ],
        "candidates": candidates,
        "sources": sources,
        "abstract_contract": abstract_contract,
        "symbols": symbols,
        "architecture_hits": architecture_hits,
        "bounded_related_files": related_files,
        "platform": {
            "source_id": "platform:pioarduino:55.03.311:esp-idf-5.5.5:esp32p4",
            "placeholder": "${PIOARDUINO_LIBS_ROOT}",
            "sources": platform_sources,
            "capabilities": platform_capabilities,
        },
        "summary": {
            "candidate_count": len(candidates),
            "direct_file_count": len(sources),
            "symbol_count": len(symbols),
            "abstract_contract_count": len(abstract_contract),
            "architecture_hit_count": len(architecture_hits),
            "architecture_hits_by_category": category_counts,
            "bounded_related_file_count": len(related_files),
            "platform_source_count": len(platform_sources),
            "platform_capability_count": len(platform_capabilities),
            "unresolved_selection_count": sum(item["status"] == "unresolved" for item in selections.values()),
        },
    }
    write_canonical(args.yaml, data)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(render_markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
