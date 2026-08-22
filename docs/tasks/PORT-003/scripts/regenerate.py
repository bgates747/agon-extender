#!/usr/bin/env python3
"""Regenerate and validate the complete PORT-003 Review Gate 1 evidence set."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TASK_ROOT = ROOT / "docs/tasks/PORT-003"
GENERATED = TASK_ROOT / "generated"
TRACKED_OUTPUTS = [
    GENERATED / "display-evidence.yaml",
    GENERATED / "display-evidence.md",
    GENERATED / "display-mode-slice.yaml",
    GENERATED / "display-mode-slice.md",
    GENERATED / "display-mode-slice.dot",
    GENERATED / "display-mode-slice.svg",
    GENERATED / "controller-contract-slice.yaml",
    GENERATED / "controller-contract-slice.md",
    GENERATED / "controller-contract-slice.dot",
    GENERATED / "controller-contract-slice.svg",
]


def run(*arguments: str) -> None:
    subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipeline(agon_vdp: Path, vdp_gl: Path, p4_framework: Path) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    run(
        "docs/tasks/PORT-003/scripts/generate-display-evidence.py",
        "--graph", "docs/dependencies/generated/code-graph.yaml",
        "--agon-vdp-root", str(agon_vdp),
        "--vdp-gl-root", str(vdp_gl),
        "--p4-framework-root", str(p4_framework),
        "--yaml", "docs/tasks/PORT-003/generated/display-evidence.yaml",
        "--markdown", "docs/tasks/PORT-003/generated/display-evidence.md",
    )
    common_relations = [
        "allocates", "calls", "configures", "defines", "depends-on", "dispatches-to",
        "includes",
        "invokes-callback", "reads", "requires-hardware",
        "requires-platform-api", "writes",
    ]
    relation_args = sum((["--relation", relation] for relation in common_relations), [])
    slices = [
        (
            "command:agon-vdp:vdu-22", "outgoing", "4",
            "PORT-003 display-mode boundary", "display-mode-slice",
        ),
        (
            "type:vdp-gl:fabgl::BitmappedDisplayController", "incoming", "2",
            "PORT-003 bitmapped-controller consumers", "controller-contract-slice",
        ),
    ]
    for seed, direction, depth, title, stem in slices:
        yaml_path = f"docs/tasks/PORT-003/generated/{stem}.yaml"
        run(
            "docs/dependencies/scripts/slice-dependency-graph.py",
            "--graph", "docs/dependencies/generated/code-graph.yaml",
            "--seed", seed,
            "--direction", direction,
            *relation_args,
            "--maximum-depth", depth,
            "--title", title,
            "--output", yaml_path,
        )
        run(
            "docs/dependencies/scripts/render-dependency-slice.py",
            yaml_path,
            "--markdown", f"docs/tasks/PORT-003/generated/{stem}.md",
            "--dot", f"docs/tasks/PORT-003/generated/{stem}.dot",
            "--svg", f"docs/tasks/PORT-003/generated/{stem}.svg",
        )
        run("docs/dependencies/scripts/validate-dependency-artifact.py", yaml_path, "--canonical")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agon-vdp-root", type=Path, required=True)
    parser.add_argument("--vdp-gl-root", type=Path, required=True)
    parser.add_argument("--p4-framework-root", type=Path, required=True)
    parser.add_argument("--check-deterministic", action="store_true")
    args = parser.parse_args()
    pipeline(args.agon_vdp_root, args.vdp_gl_root, args.p4_framework_root)
    run("docs/tasks/PORT-003/scripts/validate-display-evidence.py")
    if args.check_deterministic:
        first = {path: digest(path) for path in TRACKED_OUTPUTS}
        pipeline(args.agon_vdp_root, args.vdp_gl_root, args.p4_framework_root)
        run("docs/tasks/PORT-003/scripts/validate-display-evidence.py")
        second = {path: digest(path) for path in TRACKED_OUTPUTS}
        changed = [str(path.relative_to(ROOT)) for path in TRACKED_OUTPUTS if first[path] != second[path]]
        if changed:
            raise SystemExit("non-deterministic PORT-003 evidence: " + ", ".join(changed))
        print("PORT-003 evidence regeneration: byte-identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
