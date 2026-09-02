#!/usr/bin/env python3
"""Rejected historical validator for the r01 forward-ingress candidate.

Its implementation is retained to interpret old evidence, but it describes the
superseded ForwardParallelStream composition.  Invocation now fails before it
can validate or rewrite a record as though that composition were current.
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
RETIRED_MESSAGE = (
    "p4-forward-vdp is rejected and superseded; this historical validator "
    "cannot produce current build evidence"
)


def extract_function(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise ValueError(f"forward source lacks function {signature}")
    opening = source.find("{", start)
    if opening < 0:
        raise ValueError(f"forward source lacks body for {signature}")
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise ValueError(f"forward source has unterminated body for {signature}")


def require_ordered(source: str, fragments: tuple[str, ...], context: str) -> None:
    cursor = 0
    for fragment in fragments:
        position = source.find(fragment, cursor)
        if position < 0:
            raise ValueError(f"{context}: missing or misordered {fragment!r}")
        cursor = position + len(fragment)


def validate_direction_enable_source() -> None:
    source_path = (
        ROOT / "vdp/video/extender/transport/forward_parallel_stream.cpp"
    )
    source = source_path.read_text(encoding="utf-8")
    for fragment in (
        "kForwardEnablePin = GPIO_NUM_15",
        "kReverseEnablePin = GPIO_NUM_21",
    ):
        if fragment not in source:
            raise ValueError(f"forward direction ownership missing {fragment!r}")

    require_ordered(
        extract_function(source, "ForwardParallelStream::releaseDirections()"),
        (
            "gpio_set_level(kForwardEnablePin, 1)",
            "gpio_set_level(kReverseEnablePin, 1)",
        ),
        "fail-safe direction release",
    )
    require_ordered(
        extract_function(
            source, "ForwardParallelStream::selectForwardDirection()"
        ),
        (
            "gpio_set_level(kReverseEnablePin, 1)",
            "gpio_set_level(kForwardEnablePin, 0)",
        ),
        "break-before-make forward selection",
    )
    require_ordered(
        extract_function(source, "ForwardParallelStream::configureHardware()"),
        ("configureDirectionControl()", "parlio_rx_unit_config_t"),
        "direction control before PARLIO setup",
    )
    require_ordered(
        extract_function(source, "ForwardParallelStream::begin()"),
        ("configureHardware()", "selectForwardDirection()", "xTaskCreate("),
        "forward startup lifecycle",
    )
    receiver = extract_function(source, "ForwardParallelStream::receiverTask()")
    if receiver.count("releaseDirections()") < 2:
        raise ValueError(
            "receiver fatal paths must release direction enables before stopping"
        )


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
    sys.stderr.write(RETIRED_MESSAGE + "\n")
    return 2

    # Historical implementation below is intentionally unreachable.
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

    validate_direction_enable_source()

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
        "VALID_N=13 READY_N=20 FWD_OE_N=15:low REV_OE_N=21:high",
        "return=discard-only",
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
