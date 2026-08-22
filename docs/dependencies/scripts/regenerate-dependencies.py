#!/usr/bin/env python3
"""Regenerate and validate the durable dependency artifacts in one command."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from dependency_model import sha256_file


TRACKED_OUTPUTS = [
    Path("docs/dependencies/generated/code-graph.yaml"),
    Path("docs/dependencies/generated/source-selection.yaml"),
    Path("docs/dependencies/generated/source-selection.md"),
    Path("docs/dependencies/generated/port-002-proof.yaml"),
    Path("docs/dependencies/generated/commands/vdu-22.yaml"),
    Path("docs/dependencies/generated/commands/vdu-22.md"),
    Path("docs/dependencies/generated/diagrams/vdu-22.dot"),
    Path("docs/dependencies/generated/diagrams/vdu-22.svg"),
]


def run(*arguments: str) -> None:
    subprocess.run([sys.executable, *arguments], check=True)


def pipeline(source_roots: list[str], prior_graph: str | None = None) -> None:
    root_args = sum((["--source-root", value] for value in source_roots), [])
    prior_args = ["--prior-graph", prior_graph] if prior_graph else []
    run(
        "docs/dependencies/scripts/build-code-graph.py",
        "--setup-root", "docs/tasks/SETUP-003",
        "--baseline", "docs/dependencies/reviewed/source-baselines.yaml",
        *root_args,
        "--reviewed-claims", "docs/dependencies/reviewed/claims.yaml",
        "--output-dir", "docs/dependencies/generated",
    )
    run(
        "docs/dependencies/scripts/build-source-selection.py",
        "--base-graph", "docs/dependencies/generated/base-code-graph.yaml",
        "--baseline", "docs/dependencies/reviewed/source-baselines.yaml",
        *root_args,
        *prior_args,
        "--output", "docs/dependencies/generated/code-graph.yaml",
    )
    run(
        "docs/dependencies/scripts/project-source-selection.py",
        "docs/dependencies/generated/code-graph.yaml",
        "--yaml", "docs/dependencies/generated/source-selection.yaml",
        "--markdown", "docs/dependencies/generated/source-selection.md",
    )
    run(
        "docs/dependencies/scripts/verify-port-002-proof.py",
        "docs/dependencies/generated/code-graph.yaml",
        "--output", "docs/dependencies/generated/port-002-proof.yaml",
    )
    run(
        "docs/dependencies/scripts/slice-dependency-graph.py",
        "--graph", "docs/dependencies/generated/code-graph.yaml",
        "--seed", "command:agon-vdp:vdu-22",
        "--direction", "outgoing",
        *sum((["--relation", value] for value in ["allocates", "calls", "configures", "depends-on", "dispatches-to", "invokes-callback", "reads", "requires-hardware", "requires-platform-api", "sends-packet", "writes"]), []),
        "--maximum-depth", "4",
        "--title", "VDU 22 screen-mode selection — proof dependency slice",
        "--output", "docs/dependencies/generated/commands/vdu-22.yaml",
    )
    run(
        "docs/dependencies/scripts/render-dependency-slice.py",
        "docs/dependencies/generated/commands/vdu-22.yaml",
        "--markdown", "docs/dependencies/generated/commands/vdu-22.md",
        "--dot", "docs/dependencies/generated/diagrams/vdu-22.dot",
        "--svg", "docs/dependencies/generated/diagrams/vdu-22.svg",
    )
    run(
        "docs/dependencies/scripts/validate-dependency-artifact.py",
        "docs/dependencies/generated/code-graph.yaml", "--canonical",
    )
    run(
        "docs/dependencies/scripts/validate-dependency-artifact.py",
        "docs/dependencies/generated/commands/vdu-22.yaml", "--canonical",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", action="append", required=True)
    parser.add_argument("--check-deterministic", action="store_true")
    parser.add_argument("--prior-graph", help="previous official-tag schema-2 graph")
    args = parser.parse_args()
    pipeline(args.source_root, args.prior_graph)
    if args.check_deterministic:
        first = {path: sha256_file(path) for path in TRACKED_OUTPUTS}
        pipeline(args.source_root, args.prior_graph)
        second = {path: sha256_file(path) for path in TRACKED_OUTPUTS}
        changed = [str(path) for path in TRACKED_OUTPUTS if first[path] != second[path]]
        if changed:
            raise SystemExit("non-deterministic outputs: " + ", ".join(changed))
        print("deterministic regeneration: byte-identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
