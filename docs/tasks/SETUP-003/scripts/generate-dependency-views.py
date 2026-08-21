#!/usr/bin/env python3
"""Generate deterministic SETUP-003 Work 7 dependency views.

The file graph is resolved mechanically from Work 6 include records. Reviewed
subsystem and runtime relationships come only from the tracked Work 7 graph
model; Graphviz renders those edges but never infers or alters them.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import platform
from pathlib import Path, PurePosixPath
import re
import subprocess

import yaml


GENERATOR_VERSION = "1.0.0"
OWNER_ROOTS = {
    "agon-vdp": "video",
    "vdp-gl": "src",
    "CRC": "src",
    "ESP32Time": "",
}
OWNER_COLORS = {
    "agon-vdp": "#dceeff",
    "vdp-gl": "#ffe8cc",
    "ESP32Time": "#dff5e1",
    "CRC": "#f1e1ff",
}
RUNTIME_COLORS = {
    "startup-orchestration": "#dceeff",
    "primary-vdp-transport": "#dff5e1",
    "graphics-display": "#ffe8cc",
    "physical-ps2-input": "#f1e1ff",
    "terminal-mode": "#fff3bf",
    "audio": "#ffd8df",
    "firmware-updater": "#d9f3f0",
}


def dot_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def node_record(node: tuple[str, str]) -> dict[str, str]:
    return {"owner": node[0], "path": node[1]}


def known_files(
    symbols: dict[str, object], portability: dict[str, object], files: dict[str, object]
) -> tuple[set[tuple[str, str]], dict[tuple[str, str], int]]:
    nodes: set[tuple[str, str]] = set()
    maximum_lines: dict[tuple[str, str], int] = defaultdict(int)

    for record in symbols["symbols"]:
        key = (record["owner"], record["path"])
        nodes.add(key)
        maximum_lines[key] = max(maximum_lines[key], int(record["line"]))
    for section in (
        "includes",
        "conditional_directives",
        "platform_occurrences",
        "global_symbols",
        "protocol_symbol_candidates",
    ):
        for record in portability[section]:
            key = (record["owner"], record["path"])
            nodes.add(key)
            maximum_lines[key] = max(maximum_lines[key], int(record["line"]))
    for record in files["files"]:
        if record["path"].startswith("video/"):
            key = ("agon-vdp", record["path"])
            nodes.add(key)
            if record["lines"] is not None:
                maximum_lines[key] = int(record["lines"])
    return nodes, maximum_lines


def resolve_include(
    nodes: set[tuple[str, str]], owner: str, source: str, target: str
) -> tuple[str, str] | None:
    candidates = [str(PurePosixPath(source).parent / target), target]
    root = OWNER_ROOTS[owner]
    if root:
        candidates.append(f"{root}/{target}")
    for path in candidates:
        if (owner, path) in nodes:
            return owner, path

    owner_matches = sorted(
        node
        for node in nodes
        if node[0] == owner and (node[1] == target or node[1].endswith(f"/{target}"))
    )
    if len(owner_matches) == 1:
        return owner_matches[0]
    all_matches = sorted(
        node for node in nodes if node[1] == target or node[1].endswith(f"/{target}")
    )
    if len(all_matches) == 1:
        return all_matches[0]
    return None


def tarjan(
    nodes: set[tuple[str, str]], edges: set[tuple[tuple[str, str], tuple[str, str]]]
) -> list[list[tuple[str, str]]]:
    adjacency: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for source, target in edges:
        adjacency[source].append(target)
    for values in adjacency.values():
        values.sort()

    indices: dict[tuple[str, str], int] = {}
    lowlinks: dict[tuple[str, str], int] = {}
    stack: list[tuple[str, str]] = []
    on_stack: set[tuple[str, str]] = set()
    components: list[list[tuple[str, str]]] = []

    def visit(node: tuple[str, str]) -> None:
        indices[node] = lowlinks[node] = len(indices)
        stack.append(node)
        on_stack.add(node)
        for target in adjacency[node]:
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])
        if lowlinks[node] == indices[node]:
            component: list[tuple[str, str]] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            components.append(sorted(component))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return sorted(
        (component for component in components if len(component) > 1),
        key=lambda component: (-len(component), component),
    )


def validate_model(
    model: dict[str, object],
    portability: dict[str, object],
    control_build: dict[str, object],
    nodes: set[tuple[str, str]],
    maximum_lines: dict[tuple[str, str], int],
) -> None:
    for key in ("agon_vdp_commit", "vdp_gl_commit"):
        if model["source"].get(key) != portability["source"].get(key):
            raise ValueError(f"graph-model source does not match portability source: {key}")
    if model["source"]["agon_vdp_release"] != control_build["source"]["tag"]:
        raise ValueError("graph-model release does not match control-build release")
    if model["source"]["agon_vdp_commit"] != control_build["source"]["commit"]:
        raise ValueError("graph-model commit does not match control-build commit")
    if (
        model["source"]["vdp_gl_commit"]
        != control_build["resolved_libraries"]["vdp_gl"]["commit"]
    ):
        raise ValueError("graph-model vdp-gl commit does not match control-build dependency")

    subsystem_ids = {item["id"] for item in portability["reviewed_subsystems"]}
    runtime_ids = {item["id"] for item in model["runtime_nodes"]}
    if len(runtime_ids) != len(model["runtime_nodes"]):
        raise ValueError("duplicate runtime node ID")
    for node in model["runtime_nodes"]:
        if node["subsystem"] not in subsystem_ids:
            raise ValueError(f"unknown runtime-node subsystem: {node}")

    def validate_evidence(edge: dict[str, object]) -> None:
        evidence = edge["evidence"]
        key = (evidence["owner"], evidence["path"])
        if key not in nodes:
            raise ValueError(f"evidence file is not indexed: {evidence}")
        line = int(evidence["line"])
        if line < 1 or line > maximum_lines[key]:
            raise ValueError(f"evidence line is outside indexed extent: {evidence}")

    for edge in model["subsystem_edges"]:
        if edge["from"] not in subsystem_ids or edge["to"] not in subsystem_ids:
            raise ValueError(f"unknown subsystem edge endpoint: {edge}")
        validate_evidence(edge)
    for edge in model["runtime_edges"]:
        if edge["from"] not in runtime_ids or edge["to"] not in runtime_ids:
            raise ValueError(f"unknown runtime edge endpoint: {edge}")
        validate_evidence(edge)


def include_cycle_dot(
    components: list[list[tuple[str, str]]],
    edges: set[tuple[tuple[str, str], tuple[str, str]]],
    rankdir: str,
) -> str:
    members = {node for component in components for node in component}
    component_by_node = {
        node: index for index, component in enumerate(components) for node in component
    }
    node_ids = {node: f"n{index:03d}" for index, node in enumerate(sorted(members))}
    lines = [
        "digraph include_cycles {",
        f"  rankdir={rankdir};",
        '  graph [label="Direct source include cycles", labelloc=t, '
        'fontsize=18, bgcolor="white", pad=0.2];',
        '  node [shape=box, style="rounded,filled", fontname="DejaVu Sans", fontsize=10];',
        '  edge [color="#667085", arrowsize=0.7];',
    ]
    for index, component in enumerate(components, start=1):
        lines.append(f"  subgraph cluster_{index:02d} {{")
        lines.append(f'    label="SCC {index} · {len(component)} files";')
        lines.append('    color="#98a2b3"; style="rounded";')
        for node in component:
            label = f"{node[0]}\n{node[1]}"
            lines.append(
                f"    {node_ids[node]} [label={dot_quote(label)}, "
                f"fillcolor={dot_quote(OWNER_COLORS[node[0]])}];"
            )
        lines.append("  }")
    for source, target in sorted(edges):
        # Show only the edges that make each component cyclic. Cross-component
        # edges remain in dependency-views.yaml but obscure the cycle view.
        if (
            source in members
            and target in members
            and component_by_node[source] == component_by_node[target]
        ):
            lines.append(f"  {node_ids[source]} -> {node_ids[target]};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def subsystem_dot(
    subsystems: list[dict[str, object]], edges: list[dict[str, object]], rankdir: str
) -> str:
    statuses = {item["id"]: item["runtime_status"] for item in subsystems}
    lines = [
        "digraph subsystem_dependencies {",
        f"  rankdir={rankdir};",
        '  graph [label="Reviewed runtime subsystem dependencies", labelloc=t, '
        'fontsize=18, bgcolor="white", pad=0.25, nodesep=0.35, ranksep=0.65];',
        '  node [shape=box, style="rounded,filled", fontname="DejaVu Sans", '
        'fontsize=10, fillcolor="#eaf2ff"];',
        '  edge [fontname="DejaVu Sans", fontsize=8, color="#667085", '
        'fontcolor="#475467", arrowsize=0.7];',
    ]
    for subsystem in sorted(statuses):
        label = f"{subsystem}\n{statuses[subsystem]}"
        lines.append(f"  {dot_quote(subsystem)} [label={dot_quote(label)}];")
    for edge in sorted(
        edges, key=lambda item: (item["from"], item["to"], item["relation"])
    ):
        lines.append(
            f"  {dot_quote(edge['from'])} -> {dot_quote(edge['to'])} "
            f"[label={dot_quote(edge['relation'].replace('-', ' '))}];"
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def runtime_dot(
    nodes: list[dict[str, object]], edges: list[dict[str, object]], rankdir: str
) -> str:
    shapes = {
        "entry": "oval",
        "function": "box",
        "handler": "box",
        "task": "component",
        "interrupt": "hexagon",
        "command": "diamond",
        "timer-callback": "octagon",
    }
    by_subsystem: dict[str, list[dict[str, object]]] = defaultdict(list)
    for node in nodes:
        by_subsystem[node["subsystem"]].append(node)
    lines = [
        "digraph runtime_entries {",
        f"  rankdir={rankdir};",
        '  graph [label="Runtime entry, task, callback, and interrupt relationships", '
        'labelloc=t, fontsize=18, bgcolor="white", pad=0.25, nodesep=0.3, '
        'ranksep=0.55];',
        '  node [style="filled", fontname="DejaVu Sans", fontsize=9];',
        '  edge [fontname="DejaVu Sans", fontsize=8, color="#667085", '
        'fontcolor="#475467", arrowsize=0.7];',
    ]
    for index, subsystem in enumerate(sorted(by_subsystem), start=1):
        lines.append(f"  subgraph cluster_{index:02d} {{")
        lines.append(
            f"    label={dot_quote(subsystem)}; color=\"#98a2b3\"; "
            'style="rounded";'
        )
        for node in sorted(by_subsystem[subsystem], key=lambda item: item["id"]):
            lines.append(
                f"    {dot_quote(node['id'])} [label={dot_quote(node['label'])}, "
                f"shape={shapes[node['kind']]}, "
                f"fillcolor={dot_quote(RUNTIME_COLORS.get(subsystem, '#eef2f6'))}];"
            )
        lines.append("  }")
    for edge in sorted(
        edges, key=lambda item: (item["from"], item["to"], item["relation"])
    ):
        lines.append(
            f"  {dot_quote(edge['from'])} -> {dot_quote(edge['to'])} "
            f"[label={dot_quote(edge['relation'].replace('-', ' '))}];"
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def render(dot: str, dot_path: Path, svg_path: Path, graphviz: str) -> None:
    dot_path.write_text(dot, encoding="utf-8")
    subprocess.run([graphviz, "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--portability",
        type=Path,
        default=Path("docs/tasks/SETUP-003/generated/portability.yaml"),
    )
    parser.add_argument(
        "--symbols", type=Path, default=Path("docs/tasks/SETUP-003/generated/symbols.yaml")
    )
    parser.add_argument(
        "--files", type=Path, default=Path("docs/tasks/SETUP-003/generated/files.yaml")
    )
    parser.add_argument(
        "--includes", type=Path, default=Path("docs/tasks/SETUP-003/generated/includes.yaml")
    )
    parser.add_argument(
        "--control-build",
        type=Path,
        default=Path("docs/tasks/SETUP-003/generated/control-build.yaml"),
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("docs/tasks/SETUP-003/evidence/work-7-graph-model.yaml"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("docs/tasks/SETUP-003/generated")
    )
    parser.add_argument("--graphviz", default="dot")
    args = parser.parse_args()

    portability = yaml.safe_load(args.portability.read_text())
    symbols = yaml.safe_load(args.symbols.read_text())
    files = yaml.safe_load(args.files.read_text())
    includes = yaml.safe_load(args.includes.read_text())
    control_build = yaml.safe_load(args.control_build.read_text())
    model = yaml.safe_load(args.model.read_text())
    nodes, maximum_lines = known_files(symbols, portability, files)
    validate_model(model, portability, control_build, nodes, maximum_lines)

    edge_locations: dict[
        tuple[tuple[str, str], tuple[str, str]], list[dict[str, object]]
    ] = defaultdict(list)
    unresolved = Counter()
    unresolved_by_owner = Counter()
    for record in portability["includes"]:
        source = (record["owner"], record["path"])
        target = resolve_include(nodes, record["owner"], record["path"], record["target"])
        if target is None:
            unresolved[record["target"]] += 1
            unresolved_by_owner[record["owner"]] += 1
        elif target != source:
            edge_locations[(source, target)].append(
                {"line": int(record["line"]), "target": record["target"]}
            )
    edges = set(edge_locations)
    fan_in = Counter(target for _, target in edges)
    fan_out = Counter(source for source, _ in edges)
    components = tarjan(nodes, edges)

    def ranking(
        counter: Counter[tuple[str, str]], limit: int = 25
    ) -> list[dict[str, object]]:
        return [
            {**node_record(node), "count": count}
            for node, count in sorted(
                counter.items(), key=lambda item: (-item[1], item[0])
            )[:limit]
        ]

    graphviz_version = subprocess.run(
        [args.graphviz, "-V"], check=True, capture_output=True, text=True
    ).stderr.strip()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    include_edges = [
        {
            "from": node_record(source),
            "to": node_record(target),
            "locations": sorted(
                edge_locations[(source, target)],
                key=lambda item: (item["line"], item["target"]),
            ),
        }
        for source, target in sorted(edges)
    ]
    component_records = []
    for index, component in enumerate(components, start=1):
        member_set = set(component)
        component_records.append(
            {
                "id": f"scc-{index:02d}",
                "size": len(component),
                "internal_edges": sum(
                    source in member_set and target in member_set for source, target in edges
                ),
                "members": [node_record(node) for node in component],
            }
        )

    document = {
        "schema_version": 1,
        "generator": {
            "name": "generate-dependency-views",
            "version": GENERATOR_VERSION,
            "regeneration_command": (
                ".venv/bin/python "
                "docs/tasks/SETUP-003/scripts/generate-dependency-views.py"
            ),
        },
        "source": {
            "repository": control_build["source"]["repository"],
            "release_tag": control_build["source"]["tag"],
            "commit": control_build["source"]["commit"],
        },
        "resolved_dependencies": control_build["resolved_libraries"],
        "tools": {
            "python": platform.python_version(),
            "pyyaml": yaml.__version__,
            "graphviz": graphviz_version,
        },
        "method": {
            "file_edges": (
                "direct source include records resolved to indexed "
                "project/dependency files"
            ),
            "subsystem_edges": (
                "reviewed tracked graph model; source references validated "
                "against indexed file extents"
            ),
            "runtime_edges": (
                "reviewed tracked graph model; source references validated "
                "against indexed file extents"
            ),
            "compiler_closure_context": (
                "P4 compiler transitive closure; direct include tree is partial "
                "at its recorded fatal header"
            ),
        },
        "include_graph": {
            "indexed_nodes": len(nodes),
            "raw_include_records": len(portability["includes"]),
            "resolved_internal_edges": len(edges),
            "unresolved_external_or_ambiguous_records": sum(unresolved.values()),
            "unresolved_by_owner": dict(sorted(unresolved_by_owner.items())),
            "top_unresolved_targets": [
                {"target": target, "count": count}
                for target, count in sorted(
                    unresolved.items(), key=lambda item: (-item[1], item[0])
                )[:25]
            ],
            "compiler_dependency_closure_files": len(includes["dependency_closure"]),
            "compiler_include_tree_complete": not bool(includes["terminal_diagnostics"]),
            "fan_in_top": ranking(fan_in),
            "fan_out_top": ranking(fan_out),
            "strongly_connected_components": component_records,
            "edges": include_edges,
        },
        "subsystem_graph": {
            "nodes": [
                {"id": item["id"], "runtime_status": item["runtime_status"]}
                for item in portability["reviewed_subsystems"]
            ],
            "edges": model["subsystem_edges"],
        },
        "runtime_graph": {
            "nodes": model["runtime_nodes"],
            "edges": model["runtime_edges"],
        },
        "rendered_views": [
            "include-cycles.svg",
            "subsystem-dependencies.svg",
            "runtime-entry-points.svg",
        ],
    }
    (output / "dependency-views.yaml").write_text(
        "# Generated by docs/tasks/SETUP-003/scripts/generate-dependency-views.py; do not hand-edit.\n"
        + yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    render(
        include_cycle_dot(
            components,
            edges,
            model["presentation"]["include_cycle_rank_direction"],
        ),
        output / "include-cycles.dot",
        output / "include-cycles.svg",
        args.graphviz,
    )
    render(
        subsystem_dot(
            portability["reviewed_subsystems"],
            model["subsystem_edges"],
            model["presentation"]["subsystem_rank_direction"],
        ),
        output / "subsystem-dependencies.dot",
        output / "subsystem-dependencies.svg",
        args.graphviz,
    )
    render(
        runtime_dot(
            model["runtime_nodes"],
            model["runtime_edges"],
            model["presentation"]["runtime_rank_direction"],
        ),
        output / "runtime-entry-points.dot",
        output / "runtime-entry-points.svg",
        args.graphviz,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
