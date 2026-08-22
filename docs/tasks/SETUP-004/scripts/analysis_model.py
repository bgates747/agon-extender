"""Shared deterministic model helpers for SETUP-004 extraction scripts."""

from __future__ import annotations

from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

import yaml


SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".ino"}
DEFINITION_KINDS = {"function", "method", "macro", "type", "variable"}
REVERSE_RELATIONS = {
    "calls",
    "depends-on",
    "dispatches-to",
    "requires-hardware",
    "requires-platform-api",
}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_id(prefix: str, *values: Any) -> str:
    body = "\0".join(str(value) for value in values)
    return f"{prefix}:{hashlib.sha256(body.encode()).hexdigest()[:16]}"


def dump_yaml(path: Path, data: dict[str, Any], header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {header}\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def compile_patterns(patterns: Iterable[str], location: str) -> list[re.Pattern[str]]:
    compiled: list[re.Pattern[str]] = []
    for index, pattern in enumerate(patterns):
        try:
            compiled.append(re.compile(pattern))
        except re.error as error:
            raise ValueError(f"{location}[{index}]: invalid regex {pattern!r}: {error}") from error
    return compiled


def matches(patterns: Iterable[re.Pattern[str]], value: str) -> bool:
    return any(pattern.search(value) for pattern in patterns)


def source_key(owner: str, path: str) -> str:
    return f"{owner}:{path}"


def clean_cpp(text: str) -> str:
    """Mask C/C++ comments and literals while preserving offsets and newlines."""

    output = list(text)
    index = 0
    state = "code"
    quote_char = ""
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and next_char == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "line-comment"
                continue
            if char == "/" and next_char == "*":
                output[index] = output[index + 1] = " "
                index += 2
                state = "block-comment"
                continue
            if char in {'"', "'"}:
                quote_char = char
                output[index] = " "
                index += 1
                state = "literal"
                continue
        elif state == "line-comment":
            if char == "\n":
                state = "code"
            else:
                output[index] = " "
        elif state == "block-comment":
            if char == "*" and next_char == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "code"
                continue
            if char != "\n":
                output[index] = " "
        elif state == "literal":
            if char == "\\" and next_char:
                output[index] = " "
                if next_char != "\n":
                    output[index + 1] = " "
                index += 2
                continue
            if char == quote_char:
                output[index] = " "
                state = "code"
            elif char != "\n":
                output[index] = " "
        index += 1
    return "".join(output)


def canonical_source_roots(project_root: Path) -> dict[str, Path]:
    """Resolve the read-only canonical checkouts without recording host paths."""

    agon_root = project_root.parents[1] / "agon-vdp"
    library_root = agon_root / ".pio/libdeps/esp32dev"
    return {
        "agon-vdp": agon_root,
        "vdp-gl": library_root / "vdp-gl",
        "ESP32Time": library_root / "ESP32Time",
        "CRC": library_root / "CRC",
    }


def compilation_units(compile_commands: list[dict[str, Any]]) -> set[str]:
    result = {"agon-vdp:video/video.ino"}
    prefix = ".pio/libdeps/p4-work3/"
    for command in compile_commands:
        path = command["file"]
        if path.startswith(prefix):
            rest = path[len(prefix) :]
            owner, relative = rest.split("/", 1)
            result.add(source_key(owner, relative))
        else:
            result.add(source_key("agon-vdp", path))
    return result


class GraphIndex:
    def __init__(self, graph: dict[str, Any]) -> None:
        self.graph = graph
        self.nodes = {node["id"]: node for node in graph["nodes"]}
        self.evidence = {item["id"]: item for item in graph["evidence"]}
        self.edges = {edge["id"]: edge for edge in graph["edges"]}
        self.observed_selection = {
            record["subject_id"]: record["status"]
            for record in graph.get("selection_records", [])
            if record["build_profile_id"]
            == "build-profile:upstream:agon-vdp-v2.16.0-esp32"
        }
        self.in_edges: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.out_edges: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for edge in graph["edges"]:
            self.in_edges[edge["to"]].append(edge)
            self.out_edges[edge["from"]].append(edge)
        self.file_nodes: dict[str, str] = {}
        for node in graph["nodes"]:
            if node["kind"] != "file":
                continue
            path = node.get("properties", {}).get("source.path")
            if path:
                self.file_nodes[source_key(node["owner"], path)] = node["id"]

    def evidence_sources(self, evidence_ids: Iterable[str]) -> set[str]:
        result: set[str] = set()
        for evidence_id in evidence_ids:
            evidence = self.evidence.get(evidence_id, {})
            span = evidence.get("span")
            if span:
                source = self.source_owner(span["source_id"])
                result.add(source_key(source, span["path"]))
        return result

    def evidence_coordinates(self, evidence_ids: Iterable[str]) -> set[tuple[str, str, int]]:
        result: set[tuple[str, str, int]] = set()
        for evidence_id in evidence_ids:
            evidence = self.evidence.get(evidence_id, {})
            span = evidence.get("span")
            if span:
                result.add(
                    (
                        self.source_owner(span["source_id"]),
                        span["path"],
                        int(span["start_line"]),
                    )
                )
        return result

    def source_owner(self, source_id: str) -> str:
        for source in self.graph["sources"]:
            if source["id"] == source_id:
                return source["owner"]
        raise ValueError(f"unknown graph source ID: {source_id}")

    def reverse_reachable(self, seeds: Iterable[str], max_depth: int = 6) -> tuple[set[str], list[str]]:
        visited = set(seeds)
        edge_ids: set[str] = set()
        queue = deque((seed, 0) for seed in seeds)
        while queue:
            node_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self.in_edges.get(node_id, []):
                if edge["relation"] not in REVERSE_RELATIONS:
                    continue
                edge_ids.add(edge["id"])
                if edge["from"] not in visited:
                    visited.add(edge["from"])
                    queue.append((edge["from"], depth + 1))
        return visited, sorted(edge_ids)

    def source_participation(self, source: str, translation_units: set[str]) -> dict[str, Any]:
        owner, path = source.split(":", 1)
        suffix = Path(path).suffix.lower()
        file_node_id = self.file_nodes.get(source)
        if source in translation_units:
            return {"classification": "selected-translation-unit", "selected_by": [source]}
        if suffix not in SOURCE_SUFFIXES:
            return {"classification": "non-code-source", "selected_by": []}
        if suffix in {".h", ".hh", ".hpp"} and file_node_id:
            definitions = [
                edge["to"]
                for edge in self.out_edges.get(file_node_id, [])
                if edge["relation"] == "defines" and self.nodes[edge["to"]]["kind"] in DEFINITION_KINDS
            ]
            selected_by = self.including_translation_units(file_node_id, translation_units)
            classification = "header-defined-implementation" if definitions else "declaration-only-header"
            if not selected_by:
                classification += "-include-root-unresolved"
            return {
                "classification": classification,
                "selected_by": selected_by,
                "definition_node_ids": sorted(definitions),
            }
        node = self.nodes.get(file_node_id or "", {})
        return {
            "classification": self.observed_selection.get(
                node.get("id", ""), "source-participation-unresolved"
            ),
            "selected_by": [],
        }

    def including_translation_units(self, file_node_id: str, translation_units: set[str]) -> list[str]:
        reverse_includes: dict[str, list[str]] = defaultdict(list)
        for edge in self.edges.values():
            if edge["relation"] == "includes":
                reverse_includes[edge["to"]].append(edge["from"])
        visited = {file_node_id}
        queue = deque([file_node_id])
        roots: set[str] = set()
        while queue:
            current = queue.popleft()
            node = self.nodes[current]
            if node["kind"] == "file":
                for location in node.get("locations", []):
                    key = source_key(node["owner"], location["path"])
                    if key in translation_units:
                        roots.add(key)
            for parent in reverse_includes.get(current, []):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)
        return sorted(roots)


def project_paths(task_root: Path) -> dict[str, Path]:
    project_root = task_root.parents[2]
    return {
        "project_root": project_root,
        "graph": project_root / "docs/dependencies/generated/code-graph.yaml",
        "compile_commands": project_root / "docs/tasks/SETUP-003/generated/compile-commands.json",
        "includes": project_root / "docs/tasks/SETUP-003/generated/includes.yaml",
        "symbols": project_root / "docs/tasks/SETUP-003/generated/symbols.yaml",
        "portability": project_root / "docs/tasks/SETUP-003/generated/portability.yaml",
        "dependencies": project_root / "docs/tasks/SETUP-003/generated/dependency-views.yaml",
    }


def load_compile_commands(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON list")
    return data
