#!/usr/bin/env python3
"""Analyze one PORT-008 r01 forward-only Sigrok capture.

This analyzer is intentionally narrower than the predecessor LA-03 analyzer.
It applies the committed forward-only procedure rather than the old
bidirectional fixed-frame experiment, while preserving exact sampled facts for
failed runs.  An observed absence of edges means only that no edge was sampled
at the capture rate; it is not proof that a shorter physical pulse did not
occur.

KNOWN EVIDENCE LIMIT: INTEGRITY-AUDIT-F014 established that this prototype
does not validate every procedure precondition, data value, or setup/hold
claim. It is preserved for the failed historical runs only and must not support
qualification or automated success until PORT-008 replaces or repairs it.
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile


CHUNK = re.compile(r"^logic-1-(\d+)$")
PROBE_MAP_IDENTITY = "la03-p4-probe-fixture-r01"
SIGNALS = {
    "parallel_d4": "D0",
    "parallel_d1": "D1",
    "parallel_d0": "D2",
    "valid_n": "D3",
    "rev_oe_n": "D4",
    "clock": "D5",
    "ready_n": "D6",
    "fwd_oe_n": "D7",
}


class CaptureError(ValueError):
    """The capture does not satisfy the analyzer's structural contract."""


def parse_sample_rate(raw: str) -> int:
    units = {"MHz": 1_000_000, "kHz": 1_000, "Hz": 1}
    fields = raw.split()
    if len(fields) == 1:
        return int(float(fields[0]))
    if len(fields) == 2 and fields[1] in units:
        return int(float(fields[0]) * units[fields[1]])
    raise CaptureError(f"unsupported sample rate {raw!r}")


def load_capture(path: Path) -> tuple[int, bytes, dict[str, int]]:
    with ZipFile(path) as archive:
        config = configparser.ConfigParser()
        config.read_string(archive.read("metadata").decode("utf-8"))
        device = config["device 1"]
        sample_rate = parse_sample_rate(device["samplerate"])
        probes = {
            device[f"probe{index}"].upper(): index - 1
            for index in range(1, int(device["total probes"]) + 1)
        }
        chunks = []
        for name in archive.namelist():
            match = CHUNK.fullmatch(name)
            if match:
                chunks.append((int(match.group(1)), name))
        if not chunks:
            raise CaptureError("capture contains no digital sample chunks")
        chunks.sort()
        samples = b"".join(archive.read(name) for _, name in chunks)
    return sample_rate, samples, probes


def waveform(samples: bytes, bit: int) -> list[int]:
    return [(sample >> bit) & 1 for sample in samples]


def edges(bits: list[int]) -> list[int]:
    return [
        index
        for index in range(1, len(bits))
        if bits[index] != bits[index - 1]
    ]


def transitions(bits: list[int], before: int, after: int) -> list[int]:
    return [
        index
        for index in range(1, len(bits))
        if bits[index - 1] == before and bits[index] == after
    ]


def spans(bits: list[int], value: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    start: int | None = None
    for index, current in enumerate(bits):
        if current == value and start is None:
            start = index
        elif current != value and start is not None:
            result.append((start, index))
            start = None
    if start is not None:
        result.append((start, len(bits)))
    return result


def span_records(
    values: list[tuple[int, int]], sample_rate: int
) -> list[dict[str, int | float]]:
    return [
        {
            "start_sample": start,
            "end_sample_exclusive": end,
            "samples": end - start,
            "duration_us": round((end - start) * 1_000_000 / sample_rate, 3),
        }
        for start, end in values
    ]


def analyze(capture: Path) -> dict[str, object]:
    sample_rate, samples, probes = load_capture(capture)
    missing = sorted(set(SIGNALS.values()) - probes.keys())
    if missing:
        raise CaptureError("capture lacks probes: " + ", ".join(missing))

    signals = {
        name: waveform(samples, probes[channel])
        for name, channel in SIGNALS.items()
    }
    valid_spans = spans(signals["valid_n"], 0)
    ready_spans = spans(signals["ready_n"], 0)
    fwd_spans = spans(signals["fwd_oe_n"], 0)
    rev_spans = spans(signals["rev_oe_n"], 0)
    overlap_bits = [
        int(fwd == 0 and rev == 0)
        for fwd, rev in zip(signals["fwd_oe_n"], signals["rev_oe_n"])
    ]
    overlap_spans = spans(overlap_bits, 1)
    falling_clock = transitions(signals["clock"], 1, 0)
    qualified_falling = [
        edge
        for edge in falling_clock
        if any(start <= edge < end for start, end in valid_spans)
    ]

    findings: list[dict[str, str]] = []
    if len(valid_spans) == 1 and valid_spans[0][0] > 0 and valid_spans[0][1] < len(samples):
        findings.append(
            {
                "severity": "info",
                "code": "COMPLETE_VALID_WINDOW_OBSERVED",
                "message": "One bounded active-low VALID_N window was sampled.",
            }
        )
    else:
        findings.append(
            {
                "severity": "error",
                "code": "VALID_WINDOW_INCOMPLETE",
                "message": "The capture does not contain exactly one bounded VALID_N window.",
            }
        )
    if len(qualified_falling) != 4:
        findings.append(
            {
                "severity": "error",
                "code": "GENERAL_POLL_CLOCK_EVIDENCE_MISSING",
                "message": (
                    "The four-byte preparation poll requires four sampled falling CLOCK "
                    f"edges while VALID_N is active; observed {len(qualified_falling)}. "
                    "This is an evidence failure, not proof that sub-sample pulses did not occur."
                ),
            }
        )
    if signals["ready_n"][-1] == 0:
        findings.append(
            {
                "severity": "error",
                "code": "READY_NOT_RELEASED",
                "message": "P4 READY_N remained asserted at the capture boundary.",
            }
        )
    if overlap_spans:
        findings.append(
            {
                "severity": "error",
                "code": "FORBIDDEN_DIRECTION_OVERLAP",
                "message": (
                    "FWD_OE_N and REV_OE_N were simultaneously active-low for "
                    f"{sum(end - start for start, end in overlap_spans)} sampled cycles."
                ),
            }
        )

    line_metrics = {
        name: {
            "probe": SIGNALS[name],
            "initial": bits[0],
            "final": bits[-1],
            "edge_count": len(edges(bits)),
        }
        for name, bits in signals.items()
    }
    return {
        "schema_version": 1,
        "analyzer": "port-008-forward-capture-v1",
        "capture": {
            "filename": capture.name,
            "sha256": hashlib.sha256(capture.read_bytes()).hexdigest(),
            "sample_rate_hz": sample_rate,
            "sample_count": len(samples),
            "duration_ms": round(len(samples) * 1_000 / sample_rate, 3),
        },
        "probe_map": {
            "identity": PROBE_MAP_IDENTITY,
            "signals": SIGNALS,
        },
        "result": "fail" if any(item["severity"] == "error" for item in findings) else "pass",
        "findings": findings,
        "metrics": {
            "lines": line_metrics,
            "valid_low_spans": span_records(valid_spans, sample_rate),
            "ready_low_spans": span_records(ready_spans, sample_rate),
            "fwd_oe_low_spans": span_records(fwd_spans, sample_rate),
            "rev_oe_low_spans": span_records(rev_spans, sample_rate),
            "direction_overlap_low_spans": span_records(overlap_spans, sample_rate),
            "clock_falling_edges": len(falling_clock),
            "clock_falling_edges_while_valid": len(qualified_falling),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = analyze(args.capture)
    except (CaptureError, KeyError, OSError) as error:
        parser.error(str(error))
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{report['result'].upper()}: samples={report['capture']['sample_count']} "
        f"rate={report['capture']['sample_rate_hz']}Hz findings={len(report['findings'])}"
    )
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
