#!/usr/bin/env python3
"""Analyze logic captures for the REV-02a / LA-02 / LA-03 passes.

This script parses a Sigrok `.sr` zip capture and emits deterministic transition
metrics so the REV-02a fault source can be inferred without manual waveform
inspection.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import zipfile
from pathlib import Path

CHUNK = re.compile(r"^logic-1-(\d+)$")


PROFILE_MAPS = {
    "REV-02A": {
        "pc0": "D1",
        "pc1": "D6",
        "ready": "D2",
        "clock": "D7",
        "valid": "D5",
    },
    "LA-02": {
        "fwd_oe_n": "D0",
        "rev_oe_n": "D1",
        "u1_1a": "D2",
        "u1_1y": "D3",
        "u1_2y": "D4",
        "u1_2a": "D5",
        "u1_4y": "D7",
        "u1_4a": "D6",
    },
    "LA-03": {
        "gpio12": "D1",
        "gpio22": "D2",
        "gpio15": "D7",
        "gpio21": "D4",
        "ready": "D6",
        "clock": "D5",
        "valid": "D3",
        "gpio32": "D0",
    },
}


def parse_wire_map(values: list[str]) -> dict[str, str]:
    wire_map = {}
    for item in values:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"invalid --wire mapping '{item}', expected NAME=Dn"
            )
        key, value = item.split("=", 1)
        if not value.startswith("D"):
            raise argparse.ArgumentTypeError(
                f"invalid probe '{value}' in '{item}', expected format D0..D7"
            )
        wire_map[key] = value.upper()
    return wire_map


def load_capture(path: Path) -> tuple[int, bytes, dict[str, int]]:
    with zipfile.ZipFile(path) as z:
        metadata = z.read("metadata").decode()
        cfg = configparser.ConfigParser()
        cfg.read_string(metadata)
        dev = cfg["device 1"]
        samplerate_raw = dev.get("samplerate", "0")
        if samplerate_raw.endswith(" MHz"):
            samplerate = int(float(samplerate_raw[:-4]) * 1_000_000)
        elif samplerate_raw.endswith(" kHz"):
            samplerate = int(float(samplerate_raw[:-4]) * 1_000)
        elif samplerate_raw.endswith(" Hz"):
            samplerate = int(float(samplerate_raw[:-3]))
        else:
            samplerate = int(float(samplerate_raw))
        probes = {
            dev[f"probe{idx}"].upper(): idx - 1
            for idx in range(1, int(dev["total probes"]) + 1)
        }
        chunks = [
            (int(m.group(1)), n)
            for n in z.namelist()
            if (m := CHUNK.fullmatch(n))
        ]
        chunks.sort(key=lambda item: item[0])
        samples = b"".join(z.read(n) for _, n in chunks)
        return samplerate, samples, probes


def waveform(samples: bytes, bit: int) -> list[int]:
    shift = bit
    return [((b >> shift) & 1) for b in samples]


def transitions(bits: list[int], a: int, b: int) -> list[int]:
    return [i for i in range(1, len(bits)) if bits[i - 1] == a and bits[i] == b]


def edge_count(bits: list[int]) -> int:
    return sum(1 for a, b in zip(bits, bits[1:]) if a != b)


def epoch_count(bits: list[int], on_value: int) -> int:
    edges = transitions(bits, 1 - on_value, on_value)
    return len(edges)


def run_lengths(bits: list[int], value: int) -> list[int]:
    lengths = []
    started = None
    for i, v in enumerate(bits):
        if v == value and started is None:
            started = i
        if started is not None and v != value:
            lengths.append(i - started)
            started = None
    if started is not None:
        lengths.append(len(bits) - started)
    return lengths


def active_spans(bits: list[int], value: int) -> list[tuple[int, int]]:
    """Return half-open spans where a sampled line has the requested value."""
    spans: list[tuple[int, int]] = []
    start = None
    for index, current in enumerate(bits):
        if current == value and start is None:
            start = index
        elif current != value and start is not None:
            spans.append((start, index))
            start = None
    if start is not None:
        spans.append((start, len(bits)))
    return spans


def low_overlap(a: list[int], b: list[int]) -> tuple[int, int]:
    overlap = [1 if x == 0 and y == 0 else 0 for x, y in zip(a, b)]
    total = sum(overlap)
    spans = run_lengths(overlap, 1)
    longest = max(spans or [0])
    return total, longest


def transitions_within(bits: list[int], enable: list[int], enable_state: int) -> int:
    t = transitions(bits, 0, 1) + transitions(bits, 1, 0)
    inside = 0
    for i in t:
        if enable[i] == enable_state:
            inside += 1
    return inside


def analyze_la01(
    signals: dict[str, list[int]], strict: bool
) -> tuple[str, list[str], list[str], dict]:
    pc0 = signals["pc0"]
    pc1 = signals["pc1"]
    ready = signals["ready"]
    clock = signals["clock"]
    valid = signals["valid"]

    pc_edges = edge_count(pc0) + edge_count(pc1)
    ready_edges = edge_count(ready)
    valid_edges = edge_count(valid)
    clock_edges = edge_count(clock)
    falling = transitions(clock, 1, 0)
    valid_spans = active_spans(valid, 0)
    qualified_by_epoch = [
        sum(1 for edge in falling if start <= edge < end)
        for start, end in valid_spans
    ]
    qualified_edges = [edge for edge in falling if valid[edge] == 0]

    errors: list[str] = []
    warnings: list[str] = []

    if pc_edges == 0:
        errors.append("PC0/PC1 did not carry the forward canary")
    if valid_spans and (valid_spans[0][0] == 0 or valid_spans[-1][1] == len(valid)):
        errors.append("VALID_N epoch is truncated by the capture boundary")
    if len(valid_spans) != 1:
        errors.append(
            f"expected one active-low VALID_N epoch, observed {len(valid_spans)}"
        )
    if qualified_by_epoch != [1024]:
        errors.append(
            "expected 1024 falling CLOCK edges in the canary epoch, observed "
            f"{qualified_by_epoch}"
        )
    if not qualified_edges or any(ready[edge] != 0 for edge in qualified_edges):
        errors.append("READY_N was not asserted throughout every qualified canary edge")
    if ready_edges < 2 or 0 not in ready:
        errors.append("READY_N did not show a complete admission/release cycle")
    if not ready or ready[-1] != 1:
        errors.append("READY_N was not released at capture end")
    if not valid or valid[-1] != 1:
        errors.append("VALID_N was not inactive at capture end")
    if clock_edges < 2048:
        errors.append(
            f"CLOCK has only {clock_edges} transitions; canary framing is incomplete"
        )

    result = "FAIL" if errors else "PASS"

    return result, errors, warnings, {
        "pc_edges": pc_edges,
        "ready_edges": ready_edges,
        "valid_edges": valid_edges,
        "clock_edges": clock_edges,
        "valid_falling_clocks": len(qualified_edges),
        "valid_epoch_falling_clocks": qualified_by_epoch,
        "valid_epochs": len(valid_spans),
        "ready_rising": epoch_count(ready, 1),
        "ready_falling": epoch_count(ready, 0),
        "valid_rising": epoch_count(valid, 1),
        "valid_falling": epoch_count(valid, 0),
        "clock_rising": epoch_count(clock, 1),
        "clock_falling": epoch_count(clock, 0),
    }


def analyze_la02(
    signals: dict[str, list[int]], strict: bool
) -> tuple[str, list[str], list[str], dict]:
    fwd = signals["fwd_oe_n"]
    rev = signals["rev_oe_n"]

    fwd_edges = edge_count(fwd)
    rev_edges = edge_count(rev)
    both_low_total, both_low_longest = low_overlap(fwd, rev)

    overlap_errors = []
    if both_low_total > 0:
        overlap_errors.append(
            f"FWD_OE_N and REV_OE_N overlap low for {both_low_total} samples "
            f"(max run {both_low_longest})"
        )

    errors: list[str] = []
    warnings: list[str] = []
    if fwd_edges == 0:
        errors.append("FWD_OE_N showed no transitions")
    if rev_edges == 0:
        errors.append("REV_OE_N showed no transitions")
    if overlap_errors:
        (warnings if not strict else errors).extend(overlap_errors)

    for signal_name in ("u1_1a", "u1_1y", "u1_2a", "u1_2y", "u1_4y", "u1_4a"):
        if signal_name in signals and edge_count(signals[signal_name]) == 0:
            warnings.append(f"{signal_name} showed no transitions")

    result = "PASS"
    if strict and (warnings or errors):
        result = "FAIL"
    elif errors:
        result = "FAIL"
    elif warnings:
        result = "WARN"

    return result, errors, warnings, {
        "fwd_oe_n_edges": fwd_edges,
        "rev_oe_n_edges": rev_edges,
        "both_own_low_samples": both_low_total,
        "both_own_low_longest_run": both_low_longest,
        "signal_edges": {name: edge_count(signals[name]) for name in signals},
    }


def analyze_la03(
    signals: dict[str, list[int]], strict: bool, sample_rate_hz: int | None = None
) -> tuple[str, list[str], list[str], dict]:
    g12 = signals["gpio12"]
    g22 = signals["gpio22"]
    fwd = signals["gpio15"]
    rev = signals["gpio21"]
    ready = signals["ready"]
    clock = signals["clock"]
    valid = signals["valid"]

    both_low_total, both_low_longest = low_overlap(fwd, rev)
    g12_edges = edge_count(g12)
    g22_edges = edge_count(g22)
    rev_edges = transitions_within(g12, rev, 0) + transitions_within(g22, rev, 0)
    fwd_edges = transitions_within(g12, fwd, 0) + transitions_within(g22, fwd, 0)
    readiness = edge_count(ready)
    valid_edges = edge_count(valid)
    clock_edges = edge_count(clock)

    fwd_off = transitions(fwd, 0, 1)
    fwd_on = transitions(fwd, 1, 0)
    rev_on = transitions(rev, 1, 0)
    rev_off = transitions(rev, 0, 1)
    fwd_to_rev_samples = [
        edge - max(prior for prior in fwd_off if prior <= edge)
        for edge in rev_on
        if any(prior <= edge for prior in fwd_off)
    ]
    rev_to_fwd_samples = [
        min(later for later in fwd_on if later >= edge) - edge
        for edge in rev_off
        if any(later >= edge for later in fwd_on)
    ]

    def samples_to_us(values: list[int]) -> list[float]:
        if not sample_rate_hz:
            return []
        return [round(value * 1_000_000 / sample_rate_hz, 3) for value in values]

    fwd_to_rev_us = samples_to_us(fwd_to_rev_samples)
    rev_to_fwd_us = samples_to_us(rev_to_fwd_samples)

    errors: list[str] = []
    warnings: list[str] = []

    if g12_edges == 0 and g22_edges == 0:
        errors.append("No reverse-path GPIO12/GPIO22 transitions observed")
    if g12_edges == 0:
        warnings.append("GPIO12 showed no transitions")
    if g22_edges == 0:
        warnings.append("GPIO22 showed no transitions")
    if both_low_total > 0:
        (warnings if not strict else errors).append(
            f"FWD_OE_N and REV_OE_N overlap low for {both_low_total} samples "
            f"(max run {both_low_longest})"
        )
    if readiness == 0 and not strict:
        warnings.append("READY_N did not change")
    elif readiness == 0:
        errors.append("READY_N did not change")
    if (rev_edges + fwd_edges) == 0 and not strict:
        warnings.append(
            "No GPIO12/GPIO22 transitions aligned with an owned direction window"
        )
    elif (rev_edges + fwd_edges) == 0:
        errors.append("No GPIO12/GPIO22 transitions aligned with ownership windows")
    if sample_rate_hz:
        if len(fwd_to_rev_us) != len(rev_on):
            errors.append("Not every reverse-enable edge follows a forward release")
        if len(rev_to_fwd_us) != len(rev_off):
            errors.append(
                "Not every reverse release is followed by forward reacquisition"
            )
        if any(gap < 10 for gap in fwd_to_rev_us):
            errors.append("Forward-to-reverse break is shorter than 10 us")
        if any(gap < 10 for gap in rev_to_fwd_us):
            errors.append("Reverse-to-forward break is shorter than 10 us")

    result = "PASS"
    if strict and (warnings or errors):
        result = "FAIL"
    elif errors:
        result = "FAIL"
    elif warnings:
        result = "WARN"

    return result, errors, warnings, {
        "gpio12_edges": g12_edges,
        "gpio22_edges": g22_edges,
        "uart_edges_in_rev_window": rev_edges,
        "uart_edges_in_fwd_window": fwd_edges,
        "fwd_oe_n_edges": edge_count(fwd),
        "rev_oe_n_edges": edge_count(rev),
        "both_own_low_samples": both_low_total,
        "both_own_low_longest_run": both_low_longest,
        "ready_edges": readiness,
        "clock_edges": clock_edges,
        "valid_edges": valid_edges,
        "fwd_off_to_rev_on_us": fwd_to_rev_us,
        "rev_off_to_fwd_on_us": rev_to_fwd_us,
    }


ANALYZERS = {
    "REV-02A": analyze_la01,
    "LA-02": analyze_la02,
    "LA-03": analyze_la03,
}


def build_signals(
    samples: bytes, probes: dict[str, int], mapping: dict[str, str]
) -> dict[str, list[int]]:
    resolved = {}
    for name, probe in mapping.items():
        if probe not in probes:
            raise KeyError(f"capture has no '{probe}' probe for '{name}'")
        resolved[name] = waveform(samples, probes[probe])
    return resolved


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("capture", type=Path, help="path to logic.sr")
    ap.add_argument(
        "--profile",
        default="REV-02A",
        choices=sorted(ANALYZERS),
        help="capture profile to evaluate",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as failures",
    )
    ap.add_argument(
        "--wire",
        action="append",
        default=[],
        type=str,
        help="optional override mapping in form name=Dn, e.g. pc0=D0",
    )
    ap.add_argument("--output", type=Path, required=True, help="report output path")
    ap.add_argument(
        "--expected-samples",
        type=int,
        help="fail if the capture does not contain exactly this many samples",
    )
    ap.add_argument(
        "--verdict",
        type=Path,
        help="REV-02a result.txt proving the trace came from the R workflow",
    )
    args = ap.parse_args()

    profile = args.profile
    mapping = PROFILE_MAPS[profile].copy()
    mapping.update(parse_wire_map(args.wire))

    samplerate, samples, probes = load_capture(args.capture)
    signals = build_signals(samples, probes, mapping)
    if profile == "LA-03":
        result, errors, warnings, metrics = ANALYZERS[profile](
            signals, args.strict, samplerate
        )
    else:
        result, errors, warnings, metrics = ANALYZERS[profile](signals, args.strict)
    if args.expected_samples is not None and len(samples) != args.expected_samples:
        errors.append(
            f"capture contains {len(samples)} samples, expected "
            f"{args.expected_samples}"
        )
        result = "FAIL"

    verdict_status = None
    if profile == "REV-02A":
        if args.verdict is None:
            errors.append(
                "REV-02a requires --verdict result.txt to prove R workflow completion"
            )
        elif not args.verdict.is_file():
            errors.append(f"REV-02a verdict does not exist: {args.verdict}")
        else:
            verdict_lines = dict(
                line.split("=", 1)
                for line in args.verdict.read_text().splitlines()
                if "=" in line
            )
            verdict_status = verdict_lines.get("status")
            if verdict_status != "PASS":
                errors.append(f"REV-02a verdict is {verdict_status!r}, expected 'PASS'")
            if verdict_lines.get("forward_pass") != "1":
                errors.append("REV-02a verdict lacks the forward canary proof")
            if verdict_lines.get("reverse_bytes") != "1024":
                errors.append("REV-02a verdict lacks the full 1024-byte reverse echo")
        result = "FAIL" if errors else "PASS"

    report = {
        "profile": profile,
        "result": result,
        "strict": args.strict,
        "sample_rate_hz": samplerate,
        "sample_count": len(samples),
        "sample_mapping": mapping,
        "errors": errors,
        "warnings": warnings,
        "rev02a_verdict": verdict_status,
        "metrics": metrics,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"{result}: {profile} "
        f"samples={len(samples)} rate={samplerate}hz "
        f"errors={len(errors)} warnings={len(warnings)}"
    )
    if errors:
        for message in errors:
            print(f"ERR: {message}")
    if warnings:
        for message in warnings:
            print(f"WARN: {message}")
    return 0 if result in ("PASS", "WARN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
