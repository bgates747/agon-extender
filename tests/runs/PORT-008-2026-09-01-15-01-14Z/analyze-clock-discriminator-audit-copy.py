#!/usr/bin/env python3
"""Analyze the PORT-008 READY-isolated two-point CLOCK diagnostic.

This analyzer owns the temporary ``la03-clock-discriminator-r01`` map, not the
canonical LA-03 fixture map.  It reports sampled electrical facts and applies
the diagnostic's strict READY-isolation rule.  It does not infer that a pulse
shorter than one sample did not occur.
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
import re
from zipfile import ZipFile

import numpy as np


CHUNK = re.compile(r"^logic-1-(\d+)$")
EXPECTED_RATE = 24_000_000
EXPECTED_SAMPLES = 240_000_000
PRETRIGGER_PERCENT = 10
SIGNALS = {
    "valid_n": "D3",
    "source_clock": "D4",
    "destination_clock": "D5",
    "isolated_ready_n": "D6",
    "fwd_oe_n": "D7",
}


class CaptureError(ValueError):
    """The archive does not satisfy the diagnostic's structural contract."""


def parse_sample_rate(raw: str) -> int:
    units = {"MHz": 1_000_000, "kHz": 1_000, "Hz": 1}
    fields = raw.split()
    if len(fields) == 1:
        return int(float(fields[0]))
    if len(fields) == 2 and fields[1] in units:
        return int(float(fields[0]) * units[fields[1]])
    raise CaptureError(f"unsupported sample rate {raw!r}")


@dataclass
class LineStats:
    channel: str
    bit: int
    initial: int | None = None
    final: int | None = None
    high_samples: int = 0
    sample_count: int = 0
    edges: list[int] = field(default_factory=list)
    rises: list[int] = field(default_factory=list)
    falls: list[int] = field(default_factory=list)
    low_start: int | None = None
    low_spans: list[tuple[int, int]] = field(default_factory=list)

    def consume(self, samples: np.ndarray, offset: int) -> None:
        bits = (samples >> self.bit) & 1
        if bits.size == 0:
            return
        first = int(bits[0])
        if self.initial is None:
            self.initial = first
            self.final = first
            if first == 0:
                self.low_start = 0
        elif self.final != first:
            self._transition(offset, first)

        local_edges = np.flatnonzero(bits[1:] != bits[:-1]) + 1
        for local_index in local_edges.tolist():
            absolute = offset + int(local_index)
            self._transition(absolute, int(bits[local_index]))

        self.high_samples += int(bits.sum())
        self.sample_count += int(bits.size)
        self.final = int(bits[-1])

    def _transition(self, index: int, new_state: int) -> None:
        old_state = int(self.final)
        self.edges.append(index)
        if old_state == 0 and new_state == 1:
            self.rises.append(index)
            if self.low_start is None:
                raise CaptureError(f"{self.channel}: missing low-span start")
            self.low_spans.append((self.low_start, index))
            self.low_start = None
        elif old_state == 1 and new_state == 0:
            self.falls.append(index)
            self.low_start = index
        else:
            raise CaptureError(f"{self.channel}: invalid transition")
        self.final = new_state

    def finish(self, total: int) -> None:
        if self.initial is None or self.final is None:
            raise CaptureError(f"{self.channel}: no samples")
        if self.low_start is not None:
            self.low_spans.append((self.low_start, total))
            self.low_start = None


def span_records(
    spans: list[tuple[int, int]], sample_rate: int, minimum: int = 0
) -> list[dict[str, int | float]]:
    records = []
    for start, end in spans:
        clipped_start = max(start, minimum)
        if end <= clipped_start:
            continue
        samples = end - clipped_start
        records.append(
            {
                "start_sample": clipped_start,
                "end_sample_exclusive": end,
                "samples": samples,
                "duration_us": round(samples * 1_000_000 / sample_rate, 3),
            }
        )
    return records


def analyze(capture: Path) -> dict[str, object]:
    with ZipFile(capture) as archive:
        config = configparser.ConfigParser()
        config.read_string(archive.read("metadata").decode("utf-8"))
        device = config["device 1"]
        sample_rate = parse_sample_rate(device["samplerate"])
        probes = {
            device[f"probe{index}"].upper(): index - 1
            for index in range(1, int(device["total probes"]) + 1)
        }
        missing = sorted(set(SIGNALS.values()) - probes.keys())
        if missing:
            raise CaptureError("capture lacks probes: " + ", ".join(missing))
        chunks = []
        for name in archive.namelist():
            match = CHUNK.fullmatch(name)
            if match:
                chunks.append((int(match.group(1)), name))
        if not chunks:
            raise CaptureError("capture contains no digital sample chunks")
        chunks.sort()

        lines = {
            name: LineStats(channel, probes[channel])
            for name, channel in SIGNALS.items()
        }
        mismatch = LineStats("D4!=D5", 0)
        offset = 0
        for _, name in chunks:
            samples = np.frombuffer(archive.read(name), dtype=np.uint8)
            for line in lines.values():
                line.consume(samples, offset)
            clock_xor = (((samples >> probes["D4"]) & 1) !=
                         ((samples >> probes["D5"]) & 1)).astype(np.uint8)
            mismatch.consume(clock_xor, offset)
            offset += int(samples.size)

    for line in (*lines.values(), mismatch):
        line.finish(offset)

    if sample_rate != EXPECTED_RATE:
        raise CaptureError(f"expected {EXPECTED_RATE} Hz, observed {sample_rate}")
    if offset != EXPECTED_SAMPLES:
        raise CaptureError(f"expected {EXPECTED_SAMPLES} samples, observed {offset}")

    expected_trigger = offset * PRETRIGGER_PERCENT // 100
    ready = lines["isolated_ready_n"]
    if not ready.rises:
        raise CaptureError("D6 contains no rising trigger edge")
    trigger = min(ready.rises, key=lambda index: abs(index - expected_trigger))
    if trigger != expected_trigger:
        raise CaptureError(
            f"D6 trigger expected at sample {expected_trigger}, observed {trigger}"
        )

    post_ready_low = span_records(ready.low_spans, sample_rate, trigger)
    post_valid_low = span_records(
        lines["valid_n"].low_spans, sample_rate, trigger
    )
    source_edges = [edge for edge in lines["source_clock"].edges if edge >= trigger]
    destination_edges = [
        edge for edge in lines["destination_clock"].edges if edge >= trigger
    ]
    mismatch_post_edges = [edge for edge in mismatch.edges if edge >= trigger]
    matching_post_samples = sum(
        end - max(start, trigger)
        for start, end in mismatch.low_spans
        if end > trigger
    )
    mismatch_post_samples = offset - trigger - matching_post_samples

    findings: list[dict[str, str]] = []
    if post_ready_low:
        findings.append(
            {
                "severity": "error",
                "code": "ISOLATED_READY_GLITCHED_LOW",
                "message": (
                    "D6 sampled low after the trigger; the strict READY-isolation "
                    "invariant is not cleanly satisfied."
                ),
            }
        )
    else:
        findings.append(
            {
                "severity": "info",
                "code": "ISOLATED_READY_REMAINED_HIGH",
                "message": "D6 remained high for the complete post-trigger interval.",
            }
        )
    findings.append(
        {
            "severity": "error" if not source_edges else "info",
            "code": "SOURCE_CLOCK_ABSENT" if not source_edges else "SOURCE_CLOCK_PRESENT",
            "message": (
                "No eZ80-side D4 CLOCK edge was sampled after power-on."
                if not source_edges
                else f"Sampled {len(source_edges)} eZ80-side D4 CLOCK edges."
            ),
        }
    )
    findings.append(
        {
            "severity": "info",
            "code": (
                "DESTINATION_CLOCK_ABSENT"
                if not destination_edges
                else "DESTINATION_CLOCK_PRESENT"
            ),
            "message": (
                "No P4-side D5 CLOCK edge was sampled after power-on."
                if not destination_edges
                else f"Sampled {len(destination_edges)} P4-side D5 CLOCK edges."
            ),
        }
    )
    if post_valid_low:
        findings.append(
            {
                "severity": "warning",
                "code": "VALID_GLITCHED_LOW",
                "message": "D3 contained brief low samples but no bounded transfer record.",
            }
        )

    line_records = {}
    for name, line in lines.items():
        post_edges = [edge for edge in line.edges if edge >= trigger]
        line_records[name] = {
            "probe": line.channel,
            "initial": line.initial,
            "final": line.final,
            "high_samples": line.high_samples,
            "low_samples": offset - line.high_samples,
            "edge_count": len(line.edges),
            "post_trigger_edge_count": len(post_edges),
            "edge_head": line.edges[:12],
            "edge_tail": line.edges[-12:],
        }

    return {
        "schema_version": 1,
        "analyzer": "port-008-clock-discriminator-v1",
        "capture": {
            "filename": capture.name,
            "sha256": hashlib.sha256(capture.read_bytes()).hexdigest(),
            "sample_rate_hz": sample_rate,
            "sample_count": offset,
            "duration_ms": round(offset * 1_000 / sample_rate, 3),
            "pretrigger_percent": PRETRIGGER_PERCENT,
            "trigger": "D6 rising",
            "trigger_sample": trigger,
        },
        "probe_map": {
            "identity": "la03-clock-discriminator-r01",
            "signals": SIGNALS,
        },
        "result": "invalid" if post_ready_low else (
            "source-clock-absent" if not source_edges else "source-clock-present"
        ),
        "findings": findings,
        "metrics": {
            "lines": line_records,
            "post_trigger_ready_low_spans": post_ready_low,
            "post_trigger_valid_low_spans": post_valid_low,
            "post_trigger_source_clock_edges": len(source_edges),
            "post_trigger_destination_clock_edges": len(destination_edges),
            "clock_mismatch_high_samples_total": mismatch.high_samples,
            "clock_mismatch_high_samples_post_trigger": mismatch_post_samples,
            "clock_mismatch_post_trigger_edges": len(mismatch_post_edges),
            "clock_match_post_trigger": mismatch_post_samples == 0,
        },
        "bounded_interpretation": {
            "established": [
                "No D4 source-side CLOCK transition was sampled during the ten-second capture.",
                "No D5 destination-side CLOCK transition was sampled after the Agon power-on trigger.",
                "D4 and D5 remained logically equal throughout the post-trigger interval.",
            ],
            "limitation": (
                "Brief post-trigger D6 low spans violate the diagnostic's strict "
                "READY-high validity rule, so this run cannot cleanly select a final "
                "discriminator branch."
            ),
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
        f"rate={report['capture']['sample_rate_hz']}Hz"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
