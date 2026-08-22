#!/usr/bin/env python3
"""Build deterministic PORT-001 graphs from accepted SETUP-003 evidence.

The lexical analyzer deliberately does not claim to be a C++ parser. It strips
comments and literals, bounds function bodies with balanced braces, and emits
only unique-name call/state relationships. Ambiguous candidates remain explicit
`unresolved` records. This limitation is provenance, not an implementation
detail: replacing it later with Clang evidence must not silently upgrade old
claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml

from dependency_model import (
    GENERATOR_VERSION,
    LEGACY_SCHEMA_VERSION,
    NODE_KINDS,
    RELATIONS,
    canonicalize_graph_collections,
    edge_id,
    evidence_id,
    hash_paths,
    id_component,
    load_data,
    merge_evidence_ids,
    sha256_file,
    source_span,
    typed_id,
    write_canonical,
)


SOURCE_METADATA: dict[str, dict[str, Any]] = {}
EXPECTED_COMMITS: dict[str, str] = {}

SYMBOL_KIND = {
    "class": "type",
    "enum": "type",
    "enumerator": "variable",
    "externvar": "variable",
    "function": "function",
    "macro": "macro",
    "member": "variable",
    "namespace": "type",
    "prototype": "function",
    "struct": "type",
    "typedef": "type",
    "union": "type",
    "variable": "variable",
}

RUNTIME_KIND = {
    "command": "command",
    "entry": "function",
    "function": "function",
    "handler": "function",
    "interrupt": "interrupt",
    "task": "task",
    "timer-callback": "timer",
}

RUNTIME_RELATION = {
    "activates-output": "configures",
    "allocates-interrupt": "configures",
    "calls": "calls",
    "calls-once": "calls",
    "changes-state": "affects",
    "creates-task": "creates-task",
    "creates-timer": "configures",
    "dispatches": "dispatches-to",
    "dispatches-byte": "dispatches-to",
    "loops": "calls",
    "polls": "calls",
}

SUBSYSTEM_RELATION = {
    "allocates-through": "allocates",
    "connects-to": "depends-on",
    "creates-task-and-isr": "depends-on",
    "creates-tasks-and-isr": "depends-on",
    "defaults-to-keyboard": "depends-on",
    "emits-input-packets": "depends-on",
    "polls-for-abort": "depends-on",
    "quiesces": "affects",
    "receives-image-over": "depends-on",
    "renders-through": "depends-on",
    "returns-packets-over": "depends-on",
    "reuses-packet-channel": "depends-on",
    "starts": "configures",
    "stores-samples-in": "depends-on",
    "stores-transfer-files-in": "depends-on",
    "uses-cursor-and-positioner": "depends-on",
}

CONTROL_WORDS = {
    "alignas",
    "alignof",
    "catch",
    "decltype",
    "delete",
    "do",
    "for",
    "if",
    "new",
    "noexcept",
    "requires",
    "return",
    "sizeof",
    "static_assert",
    "switch",
    "throw",
    "typeid",
    "while",
}

PLATFORM_CALL_PREFIXES = (
    "esp_",
    "gpio_",
    "heap_caps_",
    "psram",
    "rtc_",
    "uart_",
    "vTask",
    "xQueue",
    "xSemaphore",
    "xTask",
)

PLATFORM_CALL_NAMES = {
    "delay",
    "digitalRead",
    "digitalWrite",
    "millis",
    "pinMode",
}


def parse_owner_root(value: str) -> tuple[str, Path]:
    try:
        owner, raw_path = value.split("=", 1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected OWNER=PATH") from error
    root = Path(raw_path).resolve()
    if not root.is_dir():
        raise argparse.ArgumentTypeError(f"source root does not exist: {root}")
    return owner, root


def configure_source_metadata(baseline: dict[str, Any]) -> None:
    SOURCE_METADATA.clear()
    EXPECTED_COMMITS.clear()
    for source in baseline["sources"]:
        owner = source["owner"]
        if owner in SOURCE_METADATA:
            raise ValueError(f"duplicate source owner in baseline: {owner}")
        SOURCE_METADATA[owner] = {
            key: source[key]
            for key in (
                "repository",
                "identity_kind",
                "identity",
                "root_placeholder",
            )
        }
        if source.get("commit"):
            EXPECTED_COMMITS[owner] = source["commit"]


def git_commit(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def source_id(owner: str) -> str:
    return typed_id("source", owner, SOURCE_METADATA[owner]["identity"])


def normalize_signature(signature: str | None) -> str:
    return "" if not signature else " ".join(signature.split())


def symbol_kind(record: dict[str, Any]) -> str:
    kind = SYMBOL_KIND[record["kind"]]
    if kind == "function" and record.get("scopeKind") in {"class", "struct", "union"}:
        return "method"
    return kind


def symbol_qualified_name(record: dict[str, Any]) -> str:
    scope = record.get("scope")
    return f"{scope}::{record['name']}" if scope else record["name"]


def symbol_node_id(record: dict[str, Any]) -> str:
    kind = symbol_kind(record)
    qualified_name = symbol_qualified_name(record)
    signature = normalize_signature(record.get("signature")) if kind in {"function", "method", "macro"} else ""
    identity = qualified_name + signature
    if kind == "macro":
        definition = record.get("macrodef", "")
        variant = hashlib.sha256(definition.encode("utf-8")).hexdigest()[:12]
        identity += f"@{record['path']}#variant-{variant}"
    elif record.get("file") is True:
        identity += f"@{record['path']}"
    return typed_id(kind, record["owner"], identity)


def file_node_id(owner: str, path: str) -> str:
    return typed_id("file", owner, path)


def clean_cpp(text: str) -> str:
    """Replace comments and literals with spaces while preserving newlines."""

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


def line_offsets(text: str) -> list[int]:
    offsets = [0]
    offsets.extend(match.end() for match in re.finditer("\n", text))
    return offsets


def find_function_body(cleaned: str, offsets: list[int], start_line: int) -> tuple[int, int, str] | None:
    start_offset = offsets[start_line - 1]
    search_end = min(len(cleaned), start_offset + 32768)
    opening = -1
    for index in range(start_offset, search_end):
        if cleaned[index] == ";":
            return None
        if cleaned[index] == "{":
            opening = index
            break
    if opening < 0:
        return None
    depth = 0
    for index in range(opening, len(cleaned)):
        if cleaned[index] == "{":
            depth += 1
        elif cleaned[index] == "}":
            depth -= 1
            if depth == 0:
                end_line = cleaned.count("\n", 0, index) + 1
                return opening, index + 1, cleaned[opening + 1 : index]
    return None


def classify_write(body: str, start: int, end: int) -> bool:
    before = body[max(0, start - 4) : start]
    after = body[end : min(len(body), end + 8)]
    return bool(
        re.match(r"\s*(?:\+\+|--|[+\-*/%&|^]?=(?!=))", after)
        or re.search(r"(?:\+\+|--)\s*$", before)
    )


def is_member_access(text: str, name_start: int) -> bool:
    return bool(re.search(r"(?:\.|->|::)\s*$", text[max(0, name_start - 8) : name_start]))


def resolve_unqualified_call(
    caller: dict[str, Any],
    candidates: list[str],
    definition_metadata: dict[str, dict[str, Any]],
) -> list[str]:
    """Resolve only scope-safe unqualified calls; never guess receiver types."""

    owner = caller["owner"]
    scope = caller.get("scope")
    if scope:
        scoped = [
            candidate
            for candidate in candidates
            if definition_metadata[candidate]["owner"] == owner
            and definition_metadata[candidate].get("scope") == scope
        ]
        if len(scoped) == 1:
            return scoped
    free_same_owner = [
        candidate
        for candidate in candidates
        if definition_metadata[candidate]["owner"] == owner
        and not definition_metadata[candidate].get("scope")
    ]
    if len(free_same_owner) == 1:
        return free_same_owner
    # Do not cross an ownership boundary by bare name. Calls into a dependency
    # require qualified/compiler evidence or a reviewed edge; otherwise a
    # coincidentally unique project function can be selected incorrectly.
    return []


class GraphStore:
    def __init__(self) -> None:
        self.evidence: dict[str, dict[str, Any]] = {}
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.unresolved: dict[str, dict[str, Any]] = {}

    def add_evidence(self, record: dict[str, Any]) -> str:
        existing = self.evidence.get(record["id"])
        if existing is not None and existing != record:
            raise ValueError(f"evidence ID collision: {record['id']}")
        self.evidence[record["id"]] = record
        return record["id"]

    def add_node(self, record: dict[str, Any]) -> str:
        existing = self.nodes.get(record["id"])
        if existing is None:
            self.nodes[record["id"]] = record
            return record["id"]
        if (existing["kind"], existing["owner"], existing["label"]) != (
            record["kind"],
            record["owner"],
            record["label"],
        ):
            raise ValueError(f"node ID collision: {record['id']}")
        existing["evidence_ids"] = merge_evidence_ids(existing["evidence_ids"], record["evidence_ids"])
        locations = {json.dumps(item, sort_keys=True): item for item in existing.get("locations", [])}
        locations.update({json.dumps(item, sort_keys=True): item for item in record.get("locations", [])})
        existing["locations"] = [locations[key] for key in sorted(locations)]
        existing.setdefault("properties", {}).update(record.get("properties", {}))
        if existing["build_selection"] != "selected" and record["build_selection"] == "selected":
            existing["build_selection"] = "selected"
        return record["id"]

    def add_edge(
        self,
        source: str,
        relation: str,
        target: str,
        confidence: str,
        evidence_ids: Iterable[str],
        rationale: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> str:
        key = (source, relation, target)
        existing = self.edges.get(key)
        if existing is not None:
            existing["evidence_ids"] = merge_evidence_ids(existing["evidence_ids"], evidence_ids)
            if properties:
                existing.setdefault("properties", {}).update(properties)
            return existing["id"]
        record: dict[str, Any] = {
            "id": edge_id(source, relation, target),
            "from": source,
            "to": target,
            "relation": relation,
            "confidence": confidence,
        }
        if rationale:
            record["rationale"] = rationale
        record["evidence_ids"] = sorted(set(evidence_ids))
        if properties:
            record["properties"] = properties
        self.edges[key] = record
        return record["id"]


def input_record(path: Path, repository_root: Path, role: str) -> dict[str, Any]:
    relative = path.relative_to(repository_root).as_posix()
    return {
        "id": typed_id("input", "setup-003", path.stem),
        "path": relative,
        "role": role,
        "schema_version": 1,
        "sha256": sha256_file(path),
    }


def selected_source_paths(compile_commands: list[dict[str, Any]]) -> set[tuple[str, str]]:
    selected: set[tuple[str, str]] = set()
    markers = {
        "CRC": "/CRC/",
        "ESP32Time": "/ESP32Time/",
        "vdp-gl": "/vdp-gl/",
    }
    for entry in compile_commands:
        path = entry["file"].replace("\\", "/")
        matched = False
        for owner, marker in markers.items():
            if marker in path:
                selected.add((owner, path.split(marker, 1)[1]))
                matched = True
                break
        if not matched and path.startswith("video/"):
            selected.add(("agon-vdp", path))
    return selected


def source_file_line_count(path: Path) -> int:
    lines = path.read_bytes().splitlines()
    return max(1, len(lines))


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced source braces while extracting VDU dispatch")


def parse_case_value(expression: str) -> tuple[str, str] | None:
    expression = " ".join(expression.split())
    range_match = re.fullmatch(r"(0x[0-9A-Fa-f]+|\d+)\s*\.\.\.\s*(0x[0-9A-Fa-f]+|\d+)", expression)
    if range_match:
        start = int(range_match.group(1), 0)
        end = int(range_match.group(2), 0)
        return f"vdu-{start}-{end}", f"VDU bytes {start}–{end}"
    if re.fullmatch(r"0x[0-9A-Fa-f]+|\d+", expression):
        value = int(expression, 0)
        return f"vdu-{value}", f"VDU {value}"
    return None


def add_base_vdu_dispatch(
    store: GraphStore,
    roots: dict[str, Path],
    definitions_by_name: dict[str, list[str]],
    definition_metadata: dict[str, dict[str, Any]],
) -> None:
    """Extract the outer base-VDU switch as explicit command dispatch data.

    This source-specific extractor is intentionally narrow. It recognizes only
    literal singleton and GNU range `case` labels in the final `switch(c)` of
    `VDUStreamProcessor::vdu`; extended VDU 23 families require later reviewed
    dispatch specifications rather than brittle recursive switch guessing.
    """

    owner = "agon-vdp"
    path = "video/vdu.h"
    source = (roots[owner] / path).read_text(encoding="utf-8", errors="replace")
    cleaned = clean_cpp(source)
    switches = list(re.finditer(r"\bswitch\s*\(\s*c\s*\)\s*\{", cleaned))
    if not switches:
        raise ValueError("video/vdu.h: outer switch(c) not found")
    switch_match = switches[-1]
    opening = cleaned.find("{", switch_match.start())
    closing = matching_brace(cleaned, opening)
    switch_body = cleaned[opening + 1 : closing]
    cases = list(re.finditer(r"\bcase\s+([^:]+):", switch_body))
    for index, case_match in enumerate(cases):
        parsed = parse_case_value(case_match.group(1))
        if parsed is None:
            continue
        command_identity, command_label = parsed
        case_start = opening + 1 + case_match.start()
        case_line = cleaned.count("\n", 0, case_start) + 1
        section_start = case_match.end()
        section_end = cases[index + 1].start() if index + 1 < len(cases) else len(switch_body)
        section = switch_body[section_start:section_end]
        command_id = typed_id("command", "agon-vdp", command_identity)
        dispatch_id = typed_id("dispatch", "agon-vdp", f"VDUStreamProcessor::vdu:{command_identity}")
        evidence = make_source_evidence(
            store,
            roots,
            owner,
            path,
            case_line,
            f"base-vdu-case-{command_identity}",
            f"Literal base VDU dispatch case for {command_label}.",
            symbol="VDUStreamProcessor::vdu",
        )
        store.add_node(
            {
                "id": command_id,
                "kind": "command",
                "owner": owner,
                "label": command_label,
                "build_selection": "selected",
                "locations": [store.evidence[evidence]["span"]],
                "evidence_ids": [evidence],
                "properties": {"protocol.family": "base-vdu"},
            }
        )
        store.add_node(
            {
                "id": dispatch_id,
                "kind": "dispatch",
                "owner": owner,
                "label": f"VDUStreamProcessor::vdu case {command_label}",
                "build_selection": "selected",
                "locations": [store.evidence[evidence]["span"]],
                "evidence_ids": [evidence],
                "properties": {"protocol.family": "base-vdu"},
            }
        )
        store.add_edge(command_id, "dispatches-to", dispatch_id, "confirmed", [evidence])

        for call_match in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", section):
            name = call_match.group(1)
            if name in CONTROL_WORDS:
                continue
            candidates = sorted(set(definitions_by_name.get(name, [])))
            caller = {"owner": owner, "scope": "VDUStreamProcessor"}
            resolved = (
                []
                if is_member_access(section, call_match.start())
                else resolve_unqualified_call(caller, candidates, definition_metadata)
            )
            if len(resolved) != 1:
                continue
            call_line = case_line + section.count("\n", 0, call_match.start())
            call_evidence = make_source_evidence(
                store,
                roots,
                owner,
                path,
                call_line,
                f"base-vdu-dispatch-{command_identity}-{name}",
                f"Unique indexed call {name}() in the {command_label} dispatch case.",
                symbol="VDUStreamProcessor::vdu",
            )
            store.add_edge(
                dispatch_id,
                "dispatches-to",
                resolved[0],
                "strong",
                [call_evidence],
                "The bounded dispatch case contains this call and exactly one indexed definition matches by name; overload resolution was not compiler-derived.",
                {"extraction.method": "bounded-switch-lexical"},
            )


def make_source_evidence(
    store: GraphStore,
    roots: dict[str, Path],
    owner: str,
    path: str,
    line: int,
    purpose: str,
    description: str,
    *,
    end_line: int | None = None,
    symbol: str | None = None,
    method: str = "mechanical",
) -> str:
    identifier = evidence_id("source", owner, path, line, purpose)
    record: dict[str, Any] = {
        "id": identifier,
        "kind": "source-span" if method == "mechanical" else "reviewed-analysis",
        "method": method,
        "description": description,
        "span": source_span(
            source_id(owner), roots[owner], path, line, end_line, symbol
        ),
    }
    if method == "reviewed":
        record["review"] = {
            "status": "accepted",
            "reviewed_on": "2026-08-21",
            "basis": "Imported from source-validated SETUP-003 reviewed evidence.",
        }
    return store.add_evidence(record)


def build_sources(roots: dict[str, Path], paths_by_owner: dict[str, set[str]]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for owner in sorted(SOURCE_METADATA):
        metadata = SOURCE_METADATA[owner]
        commit = git_commit(roots[owner]) if owner in EXPECTED_COMMITS else None
        if owner in EXPECTED_COMMITS and commit != EXPECTED_COMMITS[owner]:
            raise ValueError(
                f"{owner}: expected {EXPECTED_COMMITS[owner]}, found {commit}"
            )
        sources.append(
            {
                "id": source_id(owner),
                "owner": owner,
                "repository": metadata["repository"],
                "identity_kind": metadata["identity_kind"],
                "identity": metadata["identity"],
                "commit": commit,
                "tree_sha256": hash_paths(roots[owner], paths_by_owner[owner]),
                "root_placeholder": metadata["root_placeholder"],
            }
        )
    return sources


def add_mechanical_graph(
    store: GraphStore,
    roots: dict[str, Path],
    symbols: dict[str, Any],
    dependency_views: dict[str, Any],
    portability: dict[str, Any],
    compile_commands: list[dict[str, Any]],
) -> None:
    selected = selected_source_paths(compile_commands)
    for edge in dependency_views["include_graph"]["edges"]:
        selected.add((edge["from"]["owner"], edge["from"]["path"]))
        selected.add((edge["to"]["owner"], edge["to"]["path"]))

    all_files = {(record["owner"], record["path"]) for record in symbols["symbols"]}
    for include_edge in dependency_views["include_graph"]["edges"]:
        all_files.add((include_edge["from"]["owner"], include_edge["from"]["path"]))
        all_files.add((include_edge["to"]["owner"], include_edge["to"]["path"]))
    all_files = sorted(all_files)
    for owner, path in all_files:
        last_line = source_file_line_count(roots[owner] / path)
        evidence = make_source_evidence(
            store,
            roots,
            owner,
            path,
            1,
            "file",
            "Source file indexed by SETUP-003.",
            end_line=last_line,
        )
        store.add_node(
            {
                "id": file_node_id(owner, path),
                "kind": "file",
                "owner": owner,
                "label": path,
                "build_selection": "selected" if (owner, path) in selected else "available-not-selected",
                "locations": [store.evidence[evidence]["span"]],
                "evidence_ids": [evidence],
                "properties": {"source.path": path},
            }
        )

    definitions_by_name: dict[str, list[str]] = defaultdict(list)
    definition_metadata: dict[str, dict[str, Any]] = {}
    definition_records: list[tuple[dict[str, Any], str]] = []
    variable_nodes_by_name: dict[str, list[str]] = defaultdict(list)
    symbol_nodes: dict[tuple[str, str, int, str], str] = {}

    for record in symbols["symbols"]:
        kind = symbol_kind(record)
        node_id = symbol_node_id(record)
        qualified_name = symbol_qualified_name(record)
        role = record.get("role", "declaration")
        evidence = make_source_evidence(
            store,
            roots,
            record["owner"],
            record["path"],
            int(record["line"]),
            f"symbol-{role}-{node_id}",
            f"Ctags {role} for {qualified_name}.",
            symbol=qualified_name,
        )
        properties = {
            "source.ctags_kind": record["kind"],
            "source.role": role,
        }
        if record.get("typeref"):
            properties["source.typeref"] = record["typeref"]
        node: dict[str, Any] = {
            "id": node_id,
            "kind": kind,
            "owner": record["owner"],
            "label": qualified_name
            + (
                normalize_signature(record.get("signature"))
                if kind in {"function", "method", "macro"}
                else ""
            ),
            "build_selection": "selected" if (record["owner"], record["path"]) in selected else "available-not-selected",
            "qualified_name": qualified_name,
            "locations": [store.evidence[evidence]["span"]],
            "evidence_ids": [evidence],
            "properties": properties,
        }
        store.add_node(node)
        relation = "defines" if role == "definition" else "declares"
        store.add_edge(
            file_node_id(record["owner"], record["path"]),
            relation,
            node_id,
            "confirmed",
            [evidence],
        )
        symbol_nodes[(record["owner"], record["path"], int(record["line"]), record["name"])] = node_id
        if role == "definition" and kind in {"function", "method"}:
            definitions_by_name[record["name"]].append(node_id)
            definition_metadata[node_id] = record
            definition_records.append((record, node_id))
        if role == "definition" and kind == "variable":
            variable_nodes_by_name[record["name"]].append(node_id)

    add_base_vdu_dispatch(store, roots, definitions_by_name, definition_metadata)

    for include_edge in dependency_views["include_graph"]["edges"]:
        source = include_edge["from"]
        target = include_edge["to"]
        evidence_ids = []
        for location in include_edge["locations"]:
            evidence_ids.append(
                make_source_evidence(
                    store,
                    roots,
                    source["owner"],
                    source["path"],
                    int(location["line"]),
                    f"include-{target['owner']}-{target['path']}",
                    f"Resolved include of {target['owner']}:{target['path']}.",
                )
            )
        store.add_edge(
            file_node_id(source["owner"], source["path"]),
            "includes",
            file_node_id(target["owner"], target["path"]),
            "confirmed",
            evidence_ids,
        )

    globals_from_inventory = {
        (record["owner"], record["path"], int(record["line"]), record["name"])
        for record in portability["global_symbols"]
    }
    global_name_nodes: dict[str, list[str]] = defaultdict(list)
    for key in globals_from_inventory:
        node_id = symbol_nodes.get(key)
        if node_id:
            global_name_nodes[key[3]].append(node_id)

    source_cache: dict[tuple[str, str], tuple[str, str, list[int]]] = {}
    call_pattern = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
    global_pattern = (
        re.compile(r"\b(" + "|".join(sorted(map(re.escape, global_name_nodes), key=len, reverse=True)) + r")\b")
        if global_name_nodes
        else None
    )
    unresolved_seen: set[tuple[str, str, str]] = set()

    for record, caller_id in definition_records:
        cache_key = (record["owner"], record["path"])
        if cache_key not in source_cache:
            text = (roots[record["owner"]] / record["path"]).read_text(
                encoding="utf-8", errors="replace"
            )
            source_cache[cache_key] = (text, clean_cpp(text), line_offsets(text))
        text, cleaned, offsets = source_cache[cache_key]
        body_result = find_function_body(cleaned, offsets, int(record["line"]))
        if body_result is None:
            continue
        opening, closing, body = body_result
        body_start_line = cleaned.count("\n", 0, opening) + 1
        body_end_line = cleaned.count("\n", 0, closing) + 1

        for match in call_pattern.finditer(body):
            name = match.group(1)
            if name in CONTROL_WORDS:
                continue
            line = body_start_line + body.count("\n", 0, match.start())
            candidates = sorted(set(definitions_by_name.get(name, [])))
            member_access = is_member_access(body, match.start())
            resolved = (
                []
                if member_access
                else resolve_unqualified_call(record, candidates, definition_metadata)
            )
            evidence = make_source_evidence(
                store,
                roots,
                record["owner"],
                record["path"],
                line,
                f"call-{caller_id}-{name}",
                f"Token-aware lexical call candidate {name}() in {symbol_qualified_name(record)}.",
                symbol=symbol_qualified_name(record),
            )
            if len(resolved) == 1:
                store.add_edge(
                    caller_id,
                    "calls",
                    resolved[0],
                    "strong",
                    [evidence],
                    "A comment/literal-stripped function body contains this call and exactly one indexed definition matches by name; C++ overload and dynamic-dispatch semantics were not compiler-resolved.",
                    {"extraction.method": "token-aware-lexical"},
                )
            elif candidates:
                unresolved_key = (caller_id, "call", name)
                if unresolved_key not in unresolved_seen:
                    unresolved_seen.add(unresolved_key)
                    unresolved_id = typed_id("unresolved", "call", caller_id, name)
                    store.unresolved[unresolved_id] = {
                        "id": unresolved_id,
                        "kind": "symbol",
                        "description": f"Call {name}() from {caller_id} cannot be resolved safely from lexical context.",
                        "subject_id": caller_id,
                        "candidate_ids": candidates,
                        "evidence_ids": [evidence],
                    }
            elif not member_access and (name.startswith(PLATFORM_CALL_PREFIXES) or name in PLATFORM_CALL_NAMES):
                platform_id = typed_id("platform-api", "external", name)
                store.add_node(
                    {
                        "id": platform_id,
                        "kind": "platform-api",
                        "owner": "external",
                        "label": f"{name}()",
                        "build_selection": "external",
                        "qualified_name": name,
                        "locations": [],
                        "evidence_ids": [evidence],
                        "properties": {"extraction.method": "platform-name-pattern"},
                    }
                )
                store.add_edge(
                    caller_id,
                    "requires-platform-api",
                    platform_id,
                    "strong",
                    [evidence],
                    "The call matches an explicit platform API naming rule; framework overload resolution was not performed.",
                    {"extraction.method": "platform-name-pattern"},
                )

        if global_pattern:
            for match in global_pattern.finditer(body):
                name = match.group(1)
                if is_member_access(body, match.start()):
                    continue
                candidates = sorted(set(global_name_nodes[name]))
                owner_candidates = [candidate for candidate in candidates if candidate.split(":", 2)[1] == id_component(record["owner"])]
                resolved = owner_candidates if len(owner_candidates) == 1 else candidates
                line = body_start_line + body.count("\n", 0, match.start())
                evidence = make_source_evidence(
                    store,
                    roots,
                    record["owner"],
                    record["path"],
                    line,
                    f"state-{caller_id}-{name}",
                    f"Token-aware lexical reference to indexed global/static state {name}.",
                    symbol=symbol_qualified_name(record),
                )
                if len(resolved) == 1:
                    relation = "writes" if classify_write(body, match.start(), match.end()) else "reads"
                    store.add_edge(
                        caller_id,
                        relation,
                        resolved[0],
                        "strong",
                        [evidence],
                        "The token resolves to one indexed global/static definition; read/write classification is lexical and does not model aliasing.",
                        {"extraction.method": "token-aware-lexical"},
                    )
                elif len(resolved) > 1:
                    unresolved_key = (caller_id, "state", name)
                    if unresolved_key not in unresolved_seen:
                        unresolved_seen.add(unresolved_key)
                        unresolved_id = typed_id("unresolved", "state", caller_id, name)
                        store.unresolved[unresolved_id] = {
                            "id": unresolved_id,
                            "kind": "symbol",
                            "description": f"State reference {name} from {caller_id} has multiple indexed definitions.",
                            "subject_id": caller_id,
                            "candidate_ids": resolved,
                            "evidence_ids": [evidence],
                        }


def reviewed_artifact_evidence(
    store: GraphStore,
    input_id: str,
    pointer: str,
    purpose: str,
    description: str,
) -> str:
    identifier = typed_id("evidence", "reviewed", purpose)
    return store.add_evidence(
        {
            "id": identifier,
            "kind": "reviewed-analysis",
            "method": "reviewed",
            "description": description,
            "artifact_id": input_id,
            "record_pointer": pointer,
            "review": {
                "status": "accepted",
                "reviewed_on": "2026-08-21",
                "basis": "Imported from source-validated SETUP-003 reviewed evidence.",
            },
        }
    )


def is_physical_facility(label: str) -> bool:
    return bool(
        re.search(
            r"\b(?:DAC|DMA|GPIO|I2S\d|pins?|PS/2|RTC GPIO|registers?|UART\d|ULP|VGA)\b",
            label,
            re.IGNORECASE,
        )
    )


def add_reviewed_overlay(
    store: GraphStore,
    roots: dict[str, Path],
    portability: dict[str, Any],
    dependency_views: dict[str, Any],
    portability_input_id: str,
) -> None:
    subsystem_nodes: dict[str, str] = {}
    runtime_nodes: dict[str, str] = {}

    for index, subsystem in enumerate(portability["reviewed_subsystems"]):
        pointer = f"reviewed_subsystems/{index}"
        subsystem_id = typed_id("subsystem", "agon-vdp", subsystem["id"])
        subsystem_nodes[subsystem["id"]] = subsystem_id
        evidence_ids = []
        for evidence_index, evidence in enumerate(subsystem["evidence"]):
            evidence_ids.append(
                make_source_evidence(
                    store,
                    roots,
                    evidence["owner"],
                    evidence["path"],
                    int(evidence["line"]),
                    f"subsystem-{subsystem['id']}-{evidence_index}",
                    evidence["fact"],
                    method="reviewed",
                )
            )
        store.add_node(
            {
                "id": subsystem_id,
                "kind": "subsystem",
                "owner": "agon-vdp",
                "label": subsystem["id"].replace("-", " ").title(),
                "build_selection": "selected",
                "locations": [],
                "evidence_ids": evidence_ids,
                "properties": {
                    "review.runtime_status": subsystem["runtime_status"],
                    "review.portability_boundary": subsystem["portability_boundary"],
                },
            }
        )
        for facility_index, facility in enumerate(subsystem["direct_facilities"]):
            kind = "physical-facility" if is_physical_facility(facility) else "platform-api"
            facility_id = typed_id(kind, "reviewed", facility.lower())
            facility_evidence = reviewed_artifact_evidence(
                store,
                portability_input_id,
                f"{pointer}/direct_facilities/{facility_index}",
                f"facility-{subsystem['id']}-{facility_index}",
                f"Reviewed direct facility for subsystem {subsystem['id']}: {facility}",
            )
            store.add_node(
                {
                    "id": facility_id,
                    "kind": kind,
                    "owner": "external",
                    "label": facility,
                    "build_selection": "external",
                    "locations": [],
                    "evidence_ids": [facility_evidence],
                    "properties": {"review.source": "SETUP-003-portability"},
                }
            )
            store.add_edge(
                subsystem_id,
                "requires-hardware" if kind == "physical-facility" else "requires-platform-api",
                facility_id,
                "confirmed",
                [facility_evidence],
                properties={"review.source": "SETUP-003-portability"},
            )

    runtime_graph = dependency_views["runtime_graph"]
    incident_evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in runtime_graph["edges"]:
        incident_evidence[edge["from"]].append(edge["evidence"])
        incident_evidence[edge["to"]].append(edge["evidence"])
    for runtime in runtime_graph["nodes"]:
        kind = RUNTIME_KIND[runtime["kind"]]
        runtime_id = typed_id(kind, "agon-vdp-runtime", runtime["id"])
        runtime_nodes[runtime["id"]] = runtime_id
        evidence_ids = []
        unique_evidence = {
            (item["owner"], item["path"], int(item["line"])): item
            for item in incident_evidence[runtime["id"]]
        }
        for evidence_index, evidence in enumerate(unique_evidence.values()):
            evidence_ids.append(
                make_source_evidence(
                    store,
                    roots,
                    evidence["owner"],
                    evidence["path"],
                    int(evidence["line"]),
                    f"runtime-{runtime['id']}-{evidence_index}",
                    f"Reviewed runtime relationship evidence for {runtime['label']}.",
                    method="reviewed",
                )
            )
        if not evidence_ids:
            subsystem = next(
                item for item in portability["reviewed_subsystems"] if item["id"] == runtime["subsystem"]
            )
            evidence = subsystem["evidence"][0]
            evidence_ids.append(
                make_source_evidence(
                    store,
                    roots,
                    evidence["owner"],
                    evidence["path"],
                    int(evidence["line"]),
                    f"runtime-{runtime['id']}-fallback",
                    f"Subsystem evidence for runtime node {runtime['label']}.",
                    method="reviewed",
                )
            )
        store.add_node(
            {
                "id": runtime_id,
                "kind": kind,
                "owner": "agon-vdp",
                "label": runtime["label"],
                "build_selection": "selected",
                "locations": [],
                "evidence_ids": evidence_ids,
                "properties": {
                    "review.runtime_kind": runtime["kind"],
                    "review.runtime_id": runtime["id"],
                },
            }
        )
        store.add_edge(
            subsystem_nodes[runtime["subsystem"]],
            "owns",
            runtime_id,
            "confirmed",
            evidence_ids,
            properties={"review.source": "SETUP-003-runtime-graph"},
        )

    for edge in dependency_views["subsystem_graph"]["edges"]:
        evidence = edge["evidence"]
        evidence_id_value = make_source_evidence(
            store,
            roots,
            evidence["owner"],
            evidence["path"],
            int(evidence["line"]),
            f"subsystem-edge-{edge['from']}-{edge['relation']}-{edge['to']}",
            f"Reviewed subsystem relationship: {edge['from']} {edge['relation']} {edge['to']}.",
            method="reviewed",
        )
        store.add_edge(
            subsystem_nodes[edge["from"]],
            SUBSYSTEM_RELATION.get(edge["relation"], "depends-on"),
            subsystem_nodes[edge["to"]],
            "confirmed",
            [evidence_id_value],
            properties={
                "review.original_relation": edge["relation"],
                "review.source": "SETUP-003-subsystem-graph",
            },
        )

    for edge in runtime_graph["edges"]:
        evidence = edge["evidence"]
        evidence_id_value = make_source_evidence(
            store,
            roots,
            evidence["owner"],
            evidence["path"],
            int(evidence["line"]),
            f"runtime-edge-{edge['from']}-{edge['relation']}-{edge['to']}",
            f"Reviewed runtime relationship: {edge['from']} {edge['relation']} {edge['to']}.",
            method="reviewed",
        )
        store.add_edge(
            runtime_nodes[edge["from"]],
            RUNTIME_RELATION.get(edge["relation"], "affects"),
            runtime_nodes[edge["to"]],
            "confirmed",
            [evidence_id_value],
            properties={
                "review.original_relation": edge["relation"],
                "review.source": "SETUP-003-runtime-graph",
            },
        )


def add_project_reviewed_claims(
    store: GraphStore,
    roots: dict[str, Path],
    claims: dict[str, Any],
    claims_input_id: str,
) -> list[dict[str, Any]]:
    """Normalize manually reviewed PORT-001 claims into the formal overlay."""

    for index, node in enumerate(claims.get("nodes", [])):
        evidence = node["evidence"]
        evidence_id_value = make_source_evidence(
            store,
            roots,
            evidence["owner"],
            evidence["path"],
            int(evidence["line"]),
            f"project-claim-node-{index}-{node['id']}",
            evidence["fact"],
            method="reviewed",
        )
        store.add_node(
            {
                "id": node["id"],
                "kind": node["kind"],
                "owner": node["owner"],
                "label": node["label"],
                "build_selection": node["build_selection"],
                "locations": [store.evidence[evidence_id_value]["span"]],
                "evidence_ids": [evidence_id_value],
                "properties": {"review.source": "PORT-001-claims"},
            }
        )

    for index, edge in enumerate(claims.get("edges", [])):
        evidence = edge["evidence"]
        evidence_id_value = make_source_evidence(
            store,
            roots,
            evidence["owner"],
            evidence["path"],
            int(evidence["line"]),
            f"project-claim-edge-{index}-{edge['from']}-{edge['relation']}-{edge['to']}",
            evidence["fact"],
            method="reviewed",
        )
        store.add_edge(
            edge["from"],
            edge["relation"],
            edge["to"],
            edge["confidence"],
            [evidence_id_value],
            edge.get("rationale"),
            {"review.source": "PORT-001-claims"},
        )

    annotations: list[dict[str, Any]] = []
    for index, annotation in enumerate(claims.get("annotations", [])):
        evidence_id_value = reviewed_artifact_evidence(
            store,
            claims_input_id,
            f"annotations/{index}",
            f"project-claim-annotation-{index}-{annotation['target_id']}",
            annotation["basis"],
        )
        annotations.append(
            {
                "target_kind": annotation["target_kind"],
                "target_id": annotation["target_id"],
                "namespace": annotation["namespace"],
                "key": annotation["key"],
                "value": annotation["value"],
                "status": annotation["status"],
                "decision_ref": annotation.get("decision_ref"),
                "evidence_ids": [evidence_id_value],
            }
        )
    return annotations


def artifact_from_store(
    identifier: str,
    generator_name: str,
    generator_path: str,
    generator_argv: list[str],
    sources: list[dict[str, Any]],
    inputs: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    store: GraphStore,
) -> dict[str, Any]:
    artifact = {
        "schema_version": LEGACY_SCHEMA_VERSION,
        "artifact_kind": "code_graph",
        "id": identifier,
        "generator": {
            "name": generator_name,
            "version": GENERATOR_VERSION,
            "path": generator_path,
            "argv": generator_argv,
        },
        "sources": sources,
        "inputs": inputs,
        "tools": tools,
        "vocabulary": {"node_kinds": NODE_KINDS, "relations": RELATIONS},
        "evidence": list(store.evidence.values()),
        "nodes": list(store.nodes.values()),
        "edges": list(store.edges.values()),
        "unresolved": list(store.unresolved.values()),
    }
    canonicalize_graph_collections(artifact)
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--setup-root", type=Path, default=Path("docs/tasks/SETUP-003")
    )
    parser.add_argument("--source-root", action="append", required=True, type=parse_owner_root)
    parser.add_argument(
        "--reviewed-claims",
        type=Path,
        default=Path("docs/dependencies/reviewed/claims.yaml"),
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("docs/dependencies/reviewed/source-baselines.yaml"),
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("docs/dependencies/generated")
    )
    args = parser.parse_args()

    repository_root = Path.cwd().resolve()
    setup_root = args.setup_root.resolve()
    baseline_path = args.baseline.resolve()
    baseline = load_data(baseline_path)
    configure_source_metadata(baseline)
    roots = dict(args.source_root)
    missing_roots = sorted(set(SOURCE_METADATA) - set(roots))
    if missing_roots:
        parser.error(f"missing source roots: {', '.join(missing_roots)}")

    artifact_paths = {
        "symbols": setup_root / "generated/symbols.yaml",
        "dependency_views": setup_root / "generated/dependency-views.yaml",
        "portability": setup_root / "generated/portability.yaml",
        "compile_commands": setup_root / "generated/compile-commands.json",
    }
    symbols = load_data(artifact_paths["symbols"])
    dependency_views = load_data(artifact_paths["dependency_views"])
    portability = load_data(artifact_paths["portability"])
    compile_commands = json.loads(artifact_paths["compile_commands"].read_text(encoding="utf-8"))
    reviewed_claims_path = args.reviewed_claims.resolve()
    reviewed_claims = load_data(reviewed_claims_path)

    paths_by_owner: dict[str, set[str]] = {owner: set() for owner in SOURCE_METADATA}
    for record in symbols["symbols"]:
        paths_by_owner[record["owner"]].add(record["path"])
    for include_edge in dependency_views["include_graph"]["edges"]:
        paths_by_owner[include_edge["from"]["owner"]].add(include_edge["from"]["path"])
        paths_by_owner[include_edge["to"]["owner"]].add(include_edge["to"]["path"])
    for subsystem in portability["reviewed_subsystems"]:
        for evidence in subsystem["evidence"]:
            paths_by_owner[evidence["owner"]].add(evidence["path"])
    for claim in reviewed_claims.get("nodes", []) + reviewed_claims.get("edges", []):
        evidence = claim["evidence"]
        paths_by_owner[evidence["owner"]].add(evidence["path"])
    sources = build_sources(roots, paths_by_owner)

    mechanical_inputs = [
        input_record(baseline_path, repository_root, "reviewed immutable source baseline"),
        input_record(artifact_paths["compile_commands"], repository_root, "selected build translation units"),
        input_record(artifact_paths["dependency_views"], repository_root, "resolved includes and reviewed graph evidence"),
        input_record(artifact_paths["portability"], repository_root, "global state and reviewed subsystem evidence"),
        input_record(artifact_paths["symbols"], repository_root, "Ctags symbol index"),
    ]
    claims_input = input_record(
        reviewed_claims_path, repository_root, "manually reviewed PORT-001 semantic claims"
    )
    reviewed_inputs = mechanical_inputs + [claims_input]
    tools = [
        {"id": typed_id("tool", "python"), "name": "Python", "version": sys.version.split()[0]},
        {"id": typed_id("tool", "pyyaml"), "name": "PyYAML", "version": yaml.__version__},
        {
            "id": typed_id("tool", "ctags"),
            "name": "Universal Ctags",
            "version": symbols["tool"].splitlines()[0],
        },
    ]
    generator_path = "docs/dependencies/scripts/build-code-graph.py"
    generator_argv = [
        ".venv/bin/python",
        generator_path,
        "--setup-root",
        "docs/tasks/SETUP-003",
        "--baseline",
        "docs/dependencies/reviewed/source-baselines.yaml",
    ]
    for owner in SOURCE_METADATA:
        generator_argv.extend(
            ["--source-root", f"{owner}={SOURCE_METADATA[owner]['root_placeholder']}"]
        )
    generator_argv.extend(["--output-dir", "docs/dependencies/generated"])
    generator_argv.extend(
        ["--reviewed-claims", "docs/dependencies/reviewed/claims.yaml"]
    )

    mechanical_store = GraphStore()
    add_mechanical_graph(
        mechanical_store,
        roots,
        symbols,
        dependency_views,
        portability,
        compile_commands,
    )
    mechanical = artifact_from_store(
        typed_id("graph", "agon-vdp", SOURCE_METADATA["agon-vdp"]["identity"], "mechanical"),
        "build-code-graph",
        generator_path,
        generator_argv,
        sources,
        mechanical_inputs,
        tools,
        mechanical_store,
    )

    output_dir = args.output_dir.resolve()
    mechanical_path = output_dir / "mechanical-graph.yaml"
    write_canonical(mechanical_path, mechanical)
    mechanical_digest = sha256_file(mechanical_path)

    reviewed_store = GraphStore()
    portability_input_id = next(
        item["id"] for item in mechanical_inputs if item["path"].endswith("portability.yaml")
    )
    add_reviewed_overlay(
        reviewed_store,
        roots,
        portability,
        dependency_views,
        portability_input_id,
    )
    annotations = add_project_reviewed_claims(
        reviewed_store,
        roots,
        reviewed_claims,
        claims_input["id"],
    )
    overlay = {
        "schema_version": LEGACY_SCHEMA_VERSION,
        "artifact_kind": "graph_overlay",
        "id": typed_id("overlay", "setup-003", "reviewed-semantics"),
        "generator": {
            "name": "build-reviewed-overlay",
            "version": GENERATOR_VERSION,
            "path": generator_path,
            "argv": generator_argv,
        },
        "sources": sources,
        "inputs": reviewed_inputs,
        "tools": tools,
        "target_graph": {
            "id": mechanical["id"],
            "path": mechanical_path.relative_to(repository_root).as_posix(),
            "schema_version": LEGACY_SCHEMA_VERSION,
            "sha256": mechanical_digest,
        },
        "evidence": list(reviewed_store.evidence.values()),
        "nodes": list(reviewed_store.nodes.values()),
        "edges": list(reviewed_store.edges.values()),
        "annotations": annotations,
    }
    canonicalize_graph_collections(overlay)
    overlay_path = output_dir / "reviewed-overlay.yaml"
    write_canonical(overlay_path, overlay)
    overlay_digest = sha256_file(overlay_path)

    merged_store = mechanical_store
    for evidence in reviewed_store.evidence.values():
        merged_store.add_evidence(evidence)
    for node in reviewed_store.nodes.values():
        merged_store.add_node(node)
    for edge in reviewed_store.edges.values():
        merged_store.add_edge(
            edge["from"],
            edge["relation"],
            edge["to"],
            edge["confidence"],
            edge["evidence_ids"],
            edge.get("rationale"),
            edge.get("properties"),
        )
    for annotation in annotations:
        target_collection = (
            merged_store.nodes if annotation["target_kind"] == "node" else {
                edge["id"]: edge for edge in merged_store.edges.values()
            }
        )
        target = target_collection[annotation["target_id"]]
        target.setdefault("properties", {})[
            f"{annotation['namespace']}.{annotation['key']}"
        ] = annotation["value"]
        target["evidence_ids"] = merge_evidence_ids(
            target["evidence_ids"], annotation["evidence_ids"]
        )
    merged_inputs = reviewed_inputs + [
        {
            "id": typed_id("input", "port-001", "mechanical-graph"),
            "path": mechanical_path.relative_to(repository_root).as_posix(),
            "role": "mechanically generated base graph",
            "schema_version": LEGACY_SCHEMA_VERSION,
            "sha256": mechanical_digest,
        },
        {
            "id": typed_id("input", "port-001", "reviewed-overlay"),
            "path": overlay_path.relative_to(repository_root).as_posix(),
            "role": "normalized accepted SETUP-003 semantic overlay",
            "schema_version": LEGACY_SCHEMA_VERSION,
            "sha256": overlay_digest,
        },
    ]
    merged = artifact_from_store(
        typed_id("graph", "agon-vdp", SOURCE_METADATA["agon-vdp"]["identity"], "merged"),
        "build-code-graph",
        generator_path,
        generator_argv,
        sources,
        merged_inputs,
        tools,
        merged_store,
    )
    # This is the mechanically/reviewed PORT-001 graph before exhaustive
    # source-selection enrichment.  It is an ignored build intermediate, not
    # the schema-2 canonical graph published by build-source-selection.py.
    write_canonical(output_dir / "base-code-graph.yaml", merged)

    print(
        f"wrote {len(merged['nodes'])} nodes, {len(merged['edges'])} edges, "
        f"{len(merged['unresolved'])} unresolved records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
