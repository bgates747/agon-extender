"""Shared deterministic data helpers for durable dependency artifacts.

JSON Schema cannot enforce graph-wide referential integrity, tuple uniqueness,
canonical ordering, or source-span fingerprints.  The executable checks live
here so every generator and projection applies the same invariants.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

import yaml


SCHEMA_VERSION = "2.0.0"
LEGACY_SCHEMA_VERSION = "1.0.0"
GENERATOR_VERSION = "0.2.0"

NODE_KINDS = [
    "command",
    "dispatch",
    "function",
    "method",
    "type",
    "macro",
    "variable",
    "file",
    "source-region",
    "state",
    "callback",
    "task",
    "interrupt",
    "timer",
    "protocol-packet",
    "subsystem",
    "platform-api",
    "physical-facility",
    "resource",
    "build-unit",
    "test",
    "artifact",
]

RELATIONS = [
    "contains",
    "defines",
    "declares",
    "includes",
    "dispatches-to",
    "calls",
    "may-call",
    "reads",
    "writes",
    "owns",
    "resets",
    "configures",
    "constructs",
    "allocates",
    "creates-task",
    "invokes-callback",
    "sends-packet",
    "receives-packet",
    "depends-on",
    "requires-platform-api",
    "requires-hardware",
    "delegates-to",
    "affects",
]


class DependencyArtifactError(ValueError):
    """A dependency artifact violates a project-level graph invariant."""


SafeLoader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
SafeDumper = getattr(yaml, "CSafeDumper", yaml.SafeDumper)


class CanonicalDumper(SafeDumper):
    """Safe YAML dumper with aliases disabled for stable readable output."""

    def ignore_aliases(self, data: Any) -> bool:  # noqa: ANN401 - PyYAML hook
        return True


def load_data(path: Path) -> dict[str, Any]:
    """Load one JSON or YAML object."""

    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix == ".json" else yaml.load(text, Loader=SafeLoader)
    if not isinstance(data, dict):
        raise DependencyArtifactError(f"{path}: expected a top-level object")
    return data


def canonical_yaml(data: dict[str, Any]) -> str:
    """Serialize canonical tracked YAML without volatile timestamps."""

    return yaml.dump(
        data,
        Dumper=CanonicalDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=1000,
    )


def write_canonical(path: Path, data: dict[str, Any]) -> None:
    """Write canonical YAML, creating only the requested artifact directory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_yaml(data), encoding="utf-8", newline="\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_span(path: Path, start_line: int, end_line: int) -> str:
    """Hash exact source bytes for an inclusive one-based line span."""

    lines = path.read_bytes().splitlines(keepends=True)
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        raise DependencyArtifactError(
            f"{path}: invalid source span {start_line}-{end_line}; file has {len(lines)} lines"
        )
    return sha256_bytes(b"".join(lines[start_line - 1 : end_line]))


def source_span(
    source_id: str,
    source_root: Path,
    relative_path: str,
    start_line: int,
    end_line: int | None = None,
    symbol: str | None = None,
) -> dict[str, Any]:
    """Create a source span with stale-reference fingerprints."""

    end = start_line if end_line is None else end_line
    path = source_root / relative_path
    span: dict[str, Any] = {
        "source_id": source_id,
        "path": relative_path,
        "start_line": start_line,
        "end_line": end,
    }
    if symbol is not None:
        span["symbol"] = symbol
    span["file_sha256"] = sha256_file(path)
    span["span_sha256"] = sha256_span(path, start_line, end)
    return span


def id_component(value: object) -> str:
    """Encode a readable ID component without filesystem or whitespace ambiguity."""

    normalized = " ".join(str(value).strip().split())
    # Percent is safe because this function is also applied to already encoded
    # typed-ID tails while constructing readable edge IDs. Excluding it would
    # double-encode `%20` as `%2520` on every derived edge identity.
    return quote(normalized, safe="%-._~:/()[]<>@,+*=&")


def typed_id(kind: str, *components: object) -> str:
    return f"{kind}:" + ":".join(id_component(component) for component in components)


def edge_id(source_id: str, relation: str, target_id: str) -> str:
    """Return a compact deterministic edge ID while preserving its relation."""

    digest = sha256_bytes(f"{source_id}\0{relation}\0{target_id}".encode("utf-8"))[:16]
    source_tail = id_component(source_id.rsplit(":", 1)[-1])[:36]
    target_tail = id_component(target_id.rsplit(":", 1)[-1])[:36]
    return typed_id("edge", relation, f"{source_tail}-{target_tail}-{digest}")


def evidence_id(kind: str, owner: str, path: str, line: int, purpose: str) -> str:
    digest = sha256_bytes(f"{kind}\0{owner}\0{path}\0{line}\0{purpose}".encode("utf-8"))[:12]
    return typed_id("evidence", kind, owner, Path(path).name, line, digest)


def artifact_hash(data: dict[str, Any]) -> str:
    return sha256_bytes(canonical_yaml(data).encode("utf-8"))


def hash_paths(root: Path, relative_paths: Iterable[str]) -> str:
    """Hash a deterministic path/content manifest rather than local root names."""

    digest = hashlib.sha256()
    for relative_path in sorted(set(relative_paths)):
        encoded = relative_path.encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        content_hash = bytes.fromhex(sha256_file(root / relative_path))
        digest.update(content_hash)
    return digest.hexdigest()


def index_by_id(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in records}


def merge_evidence_ids(existing: list[str], additions: Iterable[str]) -> list[str]:
    return sorted(set(existing).union(additions))


def canonicalize_graph_collections(data: dict[str, Any]) -> None:
    """Sort collections whose order is part of the deterministic contract."""

    for key in (
        "sources",
        "inputs",
        "tools",
        "build_profiles",
        "evidence",
        "nodes",
        "edges",
        "selection_records",
        "unresolved",
    ):
        if key in data:
            data[key] = sorted(data[key], key=lambda item: item["id"])
    if "annotations" in data:
        data["annotations"] = sorted(
            data["annotations"],
            key=lambda item: (
                item["target_kind"],
                item["target_id"],
                item["namespace"],
                item["key"],
            ),
        )
    if "boundaries" in data:
        data["boundaries"] = sorted(
            data["boundaries"],
            key=lambda item: (item["from"], item["relation"], item["omitted_to"]),
        )
    if "groups" in data:
        data["groups"] = {
            key: sorted(set(values)) for key, values in sorted(data["groups"].items())
        }
