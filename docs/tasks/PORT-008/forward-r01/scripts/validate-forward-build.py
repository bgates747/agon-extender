#!/usr/bin/env python3
"""Extend the qualified Phase-F link audit for PORT-008 forward ingress.

The retained display/browser closure is still governed by PORT-003 Phase F.
This thin adapter deliberately reuses that validator and changes only the
environment-specific ingress requirements: the r01 ForwardParallelStream must
be linked, its pin/return diagnostic must be embedded, and the disconnected
Stream must be absent.  Keeping this delta explicit prevents a forked copy of
the large closure policy from drifting away from its authority.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
PHASE_F_VALIDATOR = (
    ROOT / "docs/tasks/PORT-003/phase-f/scripts/validate-phase-f-build.py"
)
ENVIRONMENT = "p4-forward-vdp"


def load_phase_f_validator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "port003_phase_f_build_validator", PHASE_F_VALIDATOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {PHASE_F_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rewrite_record(path: Path, *, artifact_kind: str) -> None:
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    record["artifact_kind"] = artifact_kind
    record["generated_by"] = (
        "docs/tasks/PORT-008/forward-r01/scripts/validate-forward-build.py"
    )
    record["derived_from_generator"] = (
        "docs/tasks/PORT-003/phase-f/scripts/validate-phase-f-build.py"
    )
    record["environment"] = ENVIRONMENT
    if artifact_kind.endswith("build_closure"):
        record["diagnostic_status"] = (
            "P4 compile/link evidence for retained VDP/browser plus r01 forward "
            "ingress; identity is proved only when expected fields are supplied; "
            "no deployment or physical-transfer claim"
        )
        record["build_invocation"] = (
            "scripts/vdp-pio.sh run -e p4-forward-vdp"
        )
    path.write_text(
        yaml.safe_dump(record, sort_keys=False, width=1000),
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=ROOT / f"vdp/.pio/build/{ENVIRONMENT}",
    )
    parser.add_argument(
        "--nm",
        type=Path,
        default=(
            ROOT
            / "vdp/.pio/packages/toolchain-riscv32-esp/bin/riscv32-esp-elf-nm"
        ),
    )
    parser.add_argument("--expected-source-identity")
    parser.add_argument("--expected-build-id")
    parser.add_argument("--expected-artifact-status")
    parser.add_argument("--closure-output", type=Path, required=True)
    parser.add_argument("--exclusions-output", type=Path, required=True)
    args = parser.parse_args()

    phase_f = load_phase_f_validator()
    phase_f.ENVIRONMENT = ENVIRONMENT
    phase_f.REQUIRED_SYMBOLS = dict(phase_f.REQUIRED_SYMBOLS)
    phase_f.REQUIRED_SYMBOLS.pop("deliberately disconnected ingress", None)
    phase_f.REQUIRED_SYMBOLS.update(
        {
            "r01 forward ingress setup": (
                "agon::extender::transport::ForwardParallelStream::begin()"
            ),
            "r01 forward ingress receiver": (
                "agon::extender::transport::ForwardParallelStream::receiverTask()"
            ),
            "discard-only return sink": (
                "agon::extender::transport::ForwardParallelStream::write(unsigned char)"
            ),
        }
    )
    phase_f.EXCLUDED_SYMBOL_FRAGMENTS = [
        *phase_f.EXCLUDED_SYMBOL_FRAGMENTS,
        "agon::extender::transport::DisconnectedStream",
    ]
    phase_f.REQUIRED_DIAGNOSTIC_STRING_FRAGMENTS = [
        *phase_f.REQUIRED_DIAGNOSTIC_STRING_FRAGMENTS,
        "r01 receiver started D=22,12,23,11,32,10,33,9 CLK=14",
        "VALID_N=13 READY_N=20 return=discard-only",
    ]

    delegated_argv = [
        str(PHASE_F_VALIDATOR),
        "--build-dir",
        str(args.build_dir),
        "--nm",
        str(args.nm),
        "--closure-output",
        str(args.closure_output),
        "--exclusions-output",
        str(args.exclusions_output),
    ]
    for option, value in (
        ("--expected-source-identity", args.expected_source_identity),
        ("--expected-build-id", args.expected_build_id),
        ("--expected-artifact-status", args.expected_artifact_status),
    ):
        if value is not None:
            delegated_argv.extend((option, value))

    original_argv = sys.argv
    try:
        sys.argv = delegated_argv
        result = phase_f.main()
    finally:
        sys.argv = original_argv

    rewrite_record(
        args.closure_output,
        artifact_kind="port_008_forward_build_closure",
    )
    rewrite_record(
        args.exclusions_output,
        artifact_kind="port_008_forward_link_exclusions",
    )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
