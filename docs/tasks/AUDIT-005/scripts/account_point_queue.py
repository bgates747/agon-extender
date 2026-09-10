#!/usr/bin/env python3
"""Offline W8 arithmetic and burst accounting for the accepted W7 decode.

This consumes existing evidence; it neither captures hardware nor measures P4
internals. Constants describe the pinned r03 point workload and r07 controller
sources cited in p4-queue-accounting.md. Queue occupancy remains a model.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def account(analysis_path, frames_path):
    analysis = json.loads(analysis_path.read_text())
    frames = json.loads(frames_path.read_text())["forward"]
    for flag in ("coverage_pass", "acquisition_pass", "independent_decode_matches"):
        if analysis.get(flag) is not True:
            raise ValueError(f"Accepted decode required: {flag}")
    rate = analysis["sample_rate_hz"]
    start = analysis["final_reply_end_seconds"] - analysis["payload_start_to_reply_seconds"]
    end = start + analysis["payload"]["wire_span_seconds"]
    # Boundaries reconstructed from the accepted analysis can round by less
    # than one sample; stop-bit end stays well beyond the last byte's start.
    payload = [f for f in frames if start - 0.5 / rate <= f["start"] / rate < end]
    block = bytes(v for x in range(8, 65, 8) for v in (25, 69, x, 0, 24, 0, 0, 0))
    if bytes(f["byte"] for f in payload) != block * 512:
        raise ValueError("Decoded payload differs from the exact r03 point workload")

    # All gaps exceeding 1 ms are reported, without selecting a favorable
    # subsection. This is a descriptive threshold, not an inferred P4 event.
    resumes = [i for i in range(1, len(payload))
               if (payload[i]["start"] - payload[i - 1]["end"]) / rate > 0.001]
    gaps = [(payload[i]["start"] - payload[i - 1]["end"]) / rate for i in resumes]
    intervals = [(payload[b]["start"] - payload[a]["start"]) / rate
                 for a, b in zip(resumes, resumes[1:])]
    byte_counts = Counter(b - a for a, b in zip(resumes, resumes[1:]))
    points = 4096
    primitives = points * 5
    capacity = 1024
    budget = 64
    period = 16667 / 1_000_000
    receive_bytes = 4096
    pending = receive_bytes / 8 * 5
    passes = {"total": (primitives - capacity) / budget,
              "send": (primitives - capacity - pending) / budget,
              "tail": pending / budget}
    predicted = {k: v * period for k, v in passes.items()}
    measured = {"total": analysis["payload_start_to_reply_seconds"],
                "send": analysis["payload"]["wire_span_seconds"]}
    measured["tail"] = measured["total"] - measured["send"]
    return {
        "evidence_class": "source model plus offline analysis of accepted W7 wire decode",
        "input_sha256": {"analysis.json": digest(analysis_path), "frames.json": digest(frames_path)},
        "payload_bytes": len(payload), "points": points, "nul_commands": points * 2,
        "payload_parser_calls": points * 3, "primitives_per_point": 5,
        "payload_primitives": primitives, "queue_capacity": capacity,
        "primitive_budget": budget, "period_microseconds": 16667,
        "nominal_receive_buffer_bytes": receive_bytes,
        "model_passes": passes, "model_seconds": predicted,
        "measured_seconds": measured,
        "measured_minus_model_seconds": {k: measured[k] - predicted[k] for k in passes},
        "wire_bursts": {
            "gap_threshold_seconds": 0.001, "gap_count": len(gaps),
            "gap_min_seconds": min(gaps), "gap_median_seconds": statistics.median(gaps),
            "gap_max_seconds": max(gaps),
            "resume_interval_count": len(intervals),
            "resume_interval_min_seconds": min(intervals),
            "resume_interval_mean_seconds": statistics.mean(intervals),
            "resume_interval_median_seconds": statistics.median(intervals),
            "resume_interval_max_seconds": max(intervals),
            "between_resume_byte_counts": dict(sorted(byte_counts.items())),
            "mean_bytes_between_resumes": statistics.mean(b - a for a, b in zip(resumes, resumes[1:])),
            "first_burst_bytes": resumes[0], "last_burst_bytes": len(payload) - resumes[-1],
            "first_resume_offset_seconds": payload[resumes[0]]["start"] / rate - start,
        },
        "limits": "No P4 occupancy or function duration was measured. Startup phase, finite FIFO/driver buffering, enqueue progress, direct flush and scheduling costs are not separately assigned. This models the original r07 budget; it predicts no exact time for the selected stock-drain correction.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis", type=Path)
    parser.add_argument("frames", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = account(args.analysis, args.frames)
    # Never replace earlier results silently.
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print("Point queue accounting complete; source model, not internal timing evidence.")


if __name__ == "__main__":
    main()
