#!/usr/bin/env python3
"""Render deterministic Markdown and Graphviz projections of a graph slice."""

from __future__ import annotations

import argparse
import html
import subprocess
from collections import Counter
from pathlib import Path

from dependency_model import load_data


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def dot_quote(value: object) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def render_markdown(data: dict, output: Path) -> None:
    nodes = {node["id"]: node for node in data["nodes"]}
    counts = Counter(node["kind"] for node in data["nodes"])
    lines = [
        f"# {data['title']}",
        "",
        "Generated projection; the YAML dependency slice is authoritative.",
        "",
        "## Summary",
        "",
        f"- Nodes: {data['summary']['node_count']}",
        f"- Edges: {data['summary']['edge_count']}",
        f"- Explicit boundaries: {data['summary']['boundary_count']}",
        f"- Unresolved records: {data['summary']['unresolved_count']}",
        "- Node kinds: " + ", ".join(f"{kind}={count}" for kind, count in sorted(counts.items())),
        "",
        "## Nodes",
        "",
        "| Kind | ID | Label | Port disposition |",
        "|---|---|---|---|",
    ]
    for node in data["nodes"]:
        lines.append(
            "| "
            + " | ".join(
                markdown_escape(value)
                for value in (
                    node["kind"],
                    f"`{node['id']}`",
                    node["label"],
                    node.get("properties", {}).get("port.disposition", "—"),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Relationships",
            "",
            "| From | Relationship | To | Confidence |",
            "|---|---|---|---|",
        ]
    )
    for edge in data["edges"]:
        lines.append(
            "| "
            + " | ".join(
                markdown_escape(value)
                for value in (
                    nodes[edge["from"]]["label"],
                    edge["relation"],
                    nodes[edge["to"]]["label"],
                    edge["confidence"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "| From | Relationship | Omitted target | Stop rule |",
            "|---|---|---|---|",
        ]
    )
    for boundary in data["boundaries"]:
        lines.append(
            "| "
            + " | ".join(
                markdown_escape(value)
                for value in (
                    nodes[boundary["from"]]["label"],
                    boundary["relation"],
                    boundary["omitted_to"],
                    boundary["stop_rule_id"],
                )
            )
            + " |"
        )
    if data["unresolved"]:
        lines.extend(["", "## Unresolved", ""])
        for record in data["unresolved"]:
            lines.append(f"- `{record['id']}` — {record['description']}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def render_dot(data: dict, output: Path) -> None:
    kind_colors = {
        "command": "#b8e0a5",
        "dispatch": "#f5d98b",
        "function": "#add8e6",
        "method": "#add8e6",
        "state": "#e8b4d8",
        "subsystem": "#d7c4f2",
        "platform-api": "#f2b8b5",
        "physical-facility": "#f2b8b5",
    }
    lines = [
        "digraph dependency_slice {",
        "  rankdir=LR;",
        # An explicit white canvas keeps black relationship lines legible in
        # SVG viewers that otherwise inherit a dark editor/theme background.
        '  graph [fontname="DejaVu Sans", bgcolor="white"];',
        '  node [shape=box, style="rounded,filled", fontname="DejaVu Sans", fontsize=10];',
        '  edge [fontname="DejaVu Sans", fontsize=9];',
    ]
    for node in data["nodes"]:
        label = f"{node['label']}\\n[{node['kind']}]"
        color = kind_colors.get(node["kind"], "#eeeeee")
        lines.append(
            f"  {dot_quote(node['id'])} [label={dot_quote(label)}, fillcolor={dot_quote(color)}];"
        )
    for edge in data["edges"]:
        style = "solid" if edge["confidence"] == "confirmed" else "dashed"
        lines.append(
            f"  {dot_quote(edge['from'])} -> {dot_quote(edge['to'])} "
            f"[label={dot_quote(edge['relation'])}, style={dot_quote(style)}];"
        )
    lines.append("}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slice", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--dot", type=Path)
    parser.add_argument("--svg", type=Path)
    args = parser.parse_args()
    if not any((args.markdown, args.dot, args.svg)):
        parser.error("request at least one of --markdown, --dot, or --svg")
    data = load_data(args.slice)
    if data["artifact_kind"] != "dependency_slice":
        parser.error("input must be a dependency_slice")
    if args.markdown:
        render_markdown(data, args.markdown)
    dot_path = args.dot
    if args.svg and dot_path is None:
        dot_path = args.svg.with_suffix(".dot")
    if dot_path:
        render_dot(data, dot_path)
    if args.svg:
        subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(args.svg)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
