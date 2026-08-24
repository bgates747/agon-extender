#!/usr/bin/env python3
"""Orchestrate deterministic qualification generation and validation."""

from __future__ import annotations

import argparse
import filecmp
import importlib.util
import tempfile
from pathlib import Path

from qualification_model import GENERATED, REVIEWED, build_matrix, dump_yaml, validate_matrix


def _renderer():
    path = Path(__file__).with_name("render-compatibility-views.py")
    spec = importlib.util.spec_from_file_location("qualification_renderer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load renderer {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render


def _generate(output: Path) -> None:
    matrix = build_matrix(REVIEWED)
    errors = validate_matrix(matrix)
    if errors:
        raise ValueError("\n".join(errors))
    output.mkdir(parents=True, exist_ok=True)
    (output / "compatibility-matrix.yaml").write_text(dump_yaml(matrix), encoding="utf-8")
    _renderer()(matrix, output)


def _files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        _generate(GENERATED)
        print(f"regenerated {len(_files(GENERATED))} files under {GENERATED}")
        return 0

    with tempfile.TemporaryDirectory(prefix="agon-extender-qualification-") as temporary:
        candidate = Path(temporary) / "generated"
        _generate(candidate)
        expected_files = _files(GENERATED)
        candidate_files = _files(candidate)
        if expected_files != candidate_files:
            raise SystemExit(f"generated file set differs: tracked={expected_files}, candidate={candidate_files}")
        differences = [path for path in expected_files if not filecmp.cmp(GENERATED / path, candidate / path, shallow=False)]
        if differences:
            raise SystemExit("generated files differ: " + ", ".join(str(path) for path in differences))
    print(f"deterministic check passed: {len(expected_files)} generated files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
