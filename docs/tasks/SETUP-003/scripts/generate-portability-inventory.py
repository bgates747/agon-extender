#!/usr/bin/env python3
"""Generate reviewed portability/ownership evidence for SETUP-003 Work 6.

The extractor combines broad mechanical candidates with a bounded, manually
reviewed subsystem relationship file. It validates every reviewed source
reference and declared source-wide search before emitting the combined output.
It deliberately makes no retain/replace/stub/omit/defer disposition.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess

import yaml


EXPECTED_RELEASE_COMMIT = "c7ac293d2aa81ddfa693390549bcd909069c8fc3"
EXPECTED_VDP_GL_COMMIT = "ac2dd5986daf496c43ae8e7fe41836274aec54a0"
GENERATOR_VERSION = "1.1.0"

SOURCE_AREAS = (
    ("agon-vdp", "video"),
    ("vdp-gl", ".pio/libdeps/p4-work3/vdp-gl/src"),
    ("ESP32Time", ".pio/libdeps/p4-work3/ESP32Time"),
    ("CRC", ".pio/libdeps/p4-work3/CRC/src"),
)

TEXT_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".ino"}

RULES = {
    "task_lifecycle": re.compile(
        r"\b(?:xTaskCreate(?:PinnedToCore)?|vTaskDelete|vTaskDelay|TaskHandle_t|"
        r"xTaskGetCurrentTaskHandle)\b"
    ),
    "synchronization": re.compile(
        r"\b(?:SemaphoreHandle_t|QueueHandle_t|xSemaphore\w+|xQueue\w+|"
        r"std::(?:mutex|recursive_mutex|lock_guard|unique_lock))\b"
    ),
    "interrupt_callback": re.compile(
        r"\b(?:attachInterrupt|detachInterrupt|esp_intr_alloc|intr_handle_t|"
        r"IRAM_ATTR|ISR|callback|Callback)\b"
    ),
    "stream_transport": re.compile(
        r"\b(?:Stream|HardwareSerial|Serial[0-9]*|UART|uart_\w+)\b"
    ),
    "psram_memory": re.compile(
        r"\b(?:ps_malloc|ps_calloc|ps_realloc|heap_caps_\w+|MALLOC_CAP_\w+|"
        r"psram_allocator|BOARD_HAS_PSRAM)\b"
    ),
    "gpio_adc": re.compile(
        r"\b(?:gpio_\w+|GPIO_NUM_\w+|pinMode|digitalRead|digitalWrite|"
        r"adc[12]?_\w+|analogRead|analogWrite)\b"
    ),
    "bus_timer_ulp": re.compile(
        r"\b(?:i2c_\w+|spi_\w+|I2C|SPI|Wire|timer_\w+|esp_timer_\w+|"
        r"ulp_\w+|ULP)\b"
    ),
    "network_update_storage": re.compile(
        r"\b(?:WiFi|Network|HTTP\w*|Update|ArduinoOTA|OTA|FS|File|SD|SPIFFS|"
        r"LittleFS|NVS|Preferences)\b"
    ),
    "audio_video_input": re.compile(
        r"\b(?:SoundGenerator|VGA\w*|CVBS\w*|Canvas|DisplayController|"
        r"PS2\w*|Keyboard|Mouse|Audio\w*)\b"
    ),
    "framework_platform": re.compile(
        r"\b(?:FreeRTOS|ESP32|ESP_IDF|ESP_PLATFORM|Arduino|fabgl)\b"
    ),
}

PROTOCOL_NAME = re.compile(
    r"(?:VDP|VDU|PACKET|COMMAND|CMD|KEY|MOUSE|AUDIO|VIDEO|MODE|STATUS|BUFFER)",
    re.IGNORECASE,
)


def scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def normalized_path(owner: str, relative: Path) -> str:
    path = relative.as_posix()
    if owner == "agon-vdp":
        return f"video/{path}"
    if owner in {"vdp-gl", "CRC"}:
        return f"src/{path}"
    return path


def source_files(source: Path) -> list[tuple[str, Path, str]]:
    records: list[tuple[str, Path, str]] = []
    for owner, area in SOURCE_AREAS:
        root = source / area
        candidates = [root] if root.is_file() else root.rglob("*")
        for path in candidates:
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                records.append((owner, path, normalized_path(owner, path.relative_to(root))))
    return sorted(records, key=lambda item: (item[0], item[2]))


def source_index(source: Path) -> dict[tuple[str, str], list[str]]:
    return {
        (owner, display_path): file_path.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
        for owner, file_path, display_path in source_files(source)
    }


def validate_review(
    review: dict[str, object], indexed_source: dict[tuple[str, str], list[str]]
) -> dict[str, int]:
    reference_count = 0

    def visit(value: object) -> None:
        nonlocal reference_count
        if isinstance(value, dict):
            if {"owner", "path", "line"}.issubset(value):
                key = (str(value["owner"]), str(value["path"]))
                if key not in indexed_source:
                    raise ValueError(f"review reference does not resolve: {key}")
                line = int(value["line"])
                if line < 1 or line > len(indexed_source[key]):
                    raise ValueError(f"review reference line does not resolve: {key}:{line}")
                reference_count += 1
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(review.get("subsystems", []))

    search_count = 0
    for check in review.get("validated_searches", []):
        owner = str(check["owner"])
        pattern = str(check["literal"])
        actual: list[dict[str, object]] = []
        for (candidate_owner, path), source_lines in indexed_source.items():
            if candidate_owner != owner:
                continue
            for line_number, line in enumerate(source_lines, start=1):
                if pattern in line:
                    actual.append({"path": path, "line": line_number})
        expected = check.get("expected_locations", [])
        if actual != expected:
            raise ValueError(
                f"review search {check['id']} changed: expected {expected}, found {actual}"
            )
        search_count += 1

    return {
        "reviewed_subsystems": len(review.get("subsystems", [])),
        "reviewed_source_references": reference_count,
        "validated_source_searches": search_count,
    }


def occurrence(owner: str, path: str, line: int, text: str, category: str) -> dict[str, object]:
    return {
        "category": category,
        "owner": owner,
        "path": path,
        "line": line,
        "text": text.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument(
        "--symbols",
        type=Path,
        default=Path("docs/tasks/SETUP-003/generated/symbols.yaml"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/tasks/SETUP-003/generated/portability.yaml"),
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path(
            "docs/tasks/SETUP-003/evidence/work-6-reviewed-subsystems.yaml"
        ),
    )
    args = parser.parse_args()
    source = args.source.resolve()
    symbols_path = args.symbols.resolve()
    output = args.output.resolve()
    review_path = args.review.resolve()

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True, capture_output=True, check=True
    ).stdout.strip()
    if commit != EXPECTED_RELEASE_COMMIT:
        parser.error(f"source is {commit}, expected {EXPECTED_RELEASE_COMMIT}")
    vdp_gl = source / ".pio/libdeps/p4-work3/vdp-gl"
    vdp_gl_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=vdp_gl, text=True, capture_output=True, check=True
    ).stdout.strip()
    if vdp_gl_commit != EXPECTED_VDP_GL_COMMIT:
        parser.error(f"vdp-gl is {vdp_gl_commit}, expected {EXPECTED_VDP_GL_COMMIT}")

    symbol_document = yaml.safe_load(symbols_path.read_text(encoding="utf-8"))
    review_document = yaml.safe_load(review_path.read_text(encoding="utf-8"))
    review_validation = validate_review(review_document, source_index(source))
    source_symbols = symbol_document["symbols"]
    global_symbols = [
        {
            key: symbol[key]
            for key in ("owner", "name", "path", "line", "kind", "typeref", "file", "properties", "role")
            if key in symbol
        }
        for symbol in source_symbols
        if symbol["kind"] in {"variable", "externvar"} and "scope" not in symbol
    ]

    occurrences: list[dict[str, object]] = []
    conditions: list[dict[str, object]] = []
    includes: list[dict[str, object]] = []
    include_pattern = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]')
    condition_pattern = re.compile(r"^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)$")
    for owner, file_path, display_path in source_files(source):
        text = file_path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            include = include_pattern.match(line)
            if include:
                includes.append(
                    {
                        "owner": owner,
                        "path": display_path,
                        "line": line_number,
                        "target": include.group(1),
                    }
                )
            condition = condition_pattern.match(line)
            if condition:
                conditions.append(
                    {
                        "owner": owner,
                        "path": display_path,
                        "line": line_number,
                        "directive": condition.group(1),
                        "expression": condition.group(2).strip(),
                    }
                )
            if not stripped or stripped.startswith("//"):
                continue
            for category, pattern in RULES.items():
                if pattern.search(line):
                    occurrences.append(
                        occurrence(owner, display_path, line_number, stripped, category)
                    )

    protocol_symbols = [
        {
            key: symbol[key]
            for key in ("owner", "name", "path", "line", "kind", "scope", "role")
            if key in symbol
        }
        for symbol in source_symbols
        if symbol["owner"] == "agon-vdp"
        and symbol["kind"] in {"macro", "enum", "enumerator", "variable", "externvar"}
        and PROTOCOL_NAME.search(symbol["name"])
    ]

    for records in (global_symbols, occurrences, conditions, includes, protocol_symbols):
        records.sort(
            key=lambda item: (
                str(item.get("owner", "")), str(item.get("path", "")),
                int(item.get("line", 0)), str(item.get("category", "")),
                str(item.get("name", "")),
            )
        )
    counts = Counter(item["category"] for item in occurrences)

    lines = [
        "# Generated by docs/tasks/SETUP-003/scripts/generate-portability-inventory.py; do not hand-edit.",
        "schema_version: 1",
        "generator:",
        "  name: generate-portability-inventory",
        f"  version: {scalar(GENERATOR_VERSION)}",
        "  regeneration_command: >-",
        "    .venv/bin/python docs/tasks/SETUP-003/scripts/generate-portability-inventory.py",
        "    --source <official-agon-vdp-checkout>",
        "source:",
        f"  agon_vdp_commit: {scalar(commit)}",
        f"  vdp_gl_commit: {scalar(vdp_gl_commit)}",
        f"symbol_index_total: {symbol_document['total_symbols']}",
        "interpretation_status: source-validated-relationships-without-dispositions",
        "limitations:",
        "  - Text matches are candidates, not proven ownership or call relationships.",
        "  - Conditional branches are recorded without evaluating the active build configuration.",
        "  - Protocol-related symbols are selected by name and require source validation.",
        "  - No retain, replace, stub, omit, or defer disposition is inferred.",
        "review_validation:",
        f"  reviewed_subsystems: {review_validation['reviewed_subsystems']}",
        f"  reviewed_source_references: {review_validation['reviewed_source_references']}",
        f"  validated_source_searches: {review_validation['validated_source_searches']}",
        "counts:",
        f"  global_symbols: {len(global_symbols)}",
        f"  includes: {len(includes)}",
        f"  conditional_directives: {len(conditions)}",
        f"  protocol_symbol_candidates: {len(protocol_symbols)}",
        "  occurrences_by_category:",
    ]
    lines.extend(f"    {key}: {counts[key]}" for key in sorted(counts))

    def append_records(name: str, records: list[dict[str, object]]) -> None:
        lines.append(f"{name}:")
        for record in records:
            first = True
            for key, value in record.items():
                prefix = "  - " if first else "    "
                lines.append(f"{prefix}{key}: {scalar(value)}")
                first = False

    append_records("global_symbols", global_symbols)
    append_records("includes", includes)
    append_records("conditional_directives", conditions)
    append_records("platform_occurrences", occurrences)
    append_records("protocol_symbol_candidates", protocol_symbols)
    lines.append("reviewed_subsystems:")
    reviewed_yaml = yaml.safe_dump(
        review_document["subsystems"],
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip()
    lines.extend(f"  {line}" for line in reviewed_yaml.splitlines())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
