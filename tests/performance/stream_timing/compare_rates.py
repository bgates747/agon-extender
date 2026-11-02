#!/usr/bin/env python3
"""Four-arm ordinary UART1/parallel comparison; reads retained evidence only.

Reuse the original row and complete-buffer validators. This tool cannot build,
flash, reset, invoke a test or infer physical results from instruction counts.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import statistics
import time

from analyze import read_rows, validate_dumps
from payloads import HEADER_BYTES, LENGTHS

ARMS = {"U0": "excom", "P0": "exext", "U1": "excom", "P1": "exext"}
ENDPOINTS = ("submit_prt", "wire_prt", "receipt_prt", "reply_prt")
TICKS_PER_SECOND = 72000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combine(paths):
    records = [row for path in paths for row in csv.DictReader(path.read_text().splitlines())]
    if not records:
        raise ValueError("empty CSV evidence")
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=records[0])
    writer.writeheader()
    writer.writerows(records)
    return out.getvalue()


def load_campaign(path):
    config = json.loads(path.read_text())
    if config.get("schema") != 1 or set(config.get("arms", {})) != set(ARMS):
        raise ValueError("expected schema 1 and exactly U0/P0/U1/P1")
    if config.get("direction") != "ez80-to-p4" or config.get("parallel_format") != 4:
        raise ValueError("only the declared forward format4 comparison is supported")
    loaded = {}
    seen = set()
    for name, route in ARMS.items():
        arm = config["arms"][name]
        if arm.get("route") != route:
            raise ValueError("incorrect arm route: " + name)
        for field in ("emos_sha256", "fixture_sha256", "p4_sha256", "environment_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", arm.get(field, "")):
                raise ValueError("missing artifact/config identity: " + name + "/" + field)
        paths = {}
        hashes = {}
        for field in ("results", "captures"):
            if not arm.get(field):
                raise ValueError("missing evidence: " + name + "/" + field)
            paths[field] = [(path.parent / item).resolve() for item in arm[field]]
            for item in paths[field]:
                if item in seen:
                    raise ValueError("evidence file reused across inputs: " + item.name)
                seen.add(item)
                hashes[str(item.relative_to(path.parent.resolve()))
                       if item.is_relative_to(path.parent.resolve()) else item.name] = sha(item)
        rows = read_rows(combine(paths["results"]), route)
        integrity = validate_dumps("\n".join(p.read_text(errors="replace") for p in paths["captures"]), rows)
        loaded[name] = {"identity": {k: arm[k] for k in
                        ("route", "emos_sha256", "fixture_sha256", "p4_sha256", "environment_sha256")},
                        "rows": rows, "integrity": integrity, "evidence_sha256": hashes}
    for field in ("p4_sha256", "environment_sha256"):
        if len({a["identity"][field] for a in loaded.values()}) != 1:
            raise ValueError("comparison changed " + field)
    for first, second in (("U0", "P0"), ("U1", "P1")):
        for field in ("emos_sha256", "fixture_sha256"):
            if loaded[first]["identity"][field] != loaded[second]["identity"][field]:
                raise ValueError("routes do not share the exact image/fixture: " + field)
    if loaded["U0"]["identity"]["emos_sha256"] == loaded["U1"]["identity"]["emos_sha256"]:
        raise ValueError("baseline and optimized EMOS images are identical")
    return loaded


def change(candidate, baseline):
    if baseline <= 0:
        raise ValueError("baseline below timer resolution")
    return 100 * (candidate / baseline - 1)


def summarize(arms):
    result = []
    for length in LENGTHS:
        variants = {}
        for name, arm in arms.items():
            samples = [r for r in arm["rows"] if r["wire_bytes"] == length and r["repeat"] != 0]
            if len(samples) != 5:
                raise ValueError("five measured samples required")
            metrics = {}
            for endpoint in ENDPOINTS:
                ticks = [r[endpoint] for r in samples]
                metrics[endpoint] = dict(median_ticks=statistics.median(ticks),
                    min_ticks=min(ticks), max_ticks=max(ticks),
                    median_ms=statistics.median(ticks) * 1000 / TICKS_PER_SECOND,
                    min_ms=min(ticks) * 1000 / TICKS_PER_SECOND,
                    max_ms=max(ticks) * 1000 / TICKS_PER_SECOND)
            drain = [r["wire_prt"] for r in samples]
            for field, count in (("stream_bytes_per_second", length),
                                 ("upload_bytes_per_second", length - HEADER_BYTES)):
                rates = [count * TICKS_PER_SECOND / ticks for ticks in drain]
                metrics[field] = dict(median=statistics.median(rates), min=min(rates), max=max(rates))
            variants[name] = metrics
        comparison = {
            "P1_vs_P0_drain_time_percent": change(variants["P1"]["wire_prt"]["median_ticks"], variants["P0"]["wire_prt"]["median_ticks"]),
            "P1_vs_P0_stream_rate_percent": change(variants["P1"]["stream_bytes_per_second"]["median"], variants["P0"]["stream_bytes_per_second"]["median"]),
            "P1_over_U1_stream_rate": variants["P1"]["stream_bytes_per_second"]["median"] / variants["U1"]["stream_bytes_per_second"]["median"],
            "U1_vs_U0_drain_time_percent": change(variants["U1"]["wire_prt"]["median_ticks"], variants["U0"]["wire_prt"]["median_ticks"]),
        }
        result.append(dict(wire_bytes=length, upload_bytes=length - HEADER_BYTES,
                           variants=variants, comparison=comparison))
    return sorted(result, key=lambda r: (r["variants"]["P0"]["wire_prt"]["median_ticks"],
                                         r["wire_bytes"]), reverse=True)


def markdown(rows):
    lines = ["# Matched transfer-rate comparison", "",
        "Forward ordinary VDU buffer SET on one P4: U0/P0 use baseline EMOS, U1/P1 optimized EMOS; U means UART1 and P parallel. "
        "Largest baseline parallel drain time first. Five measured samples per cell; warm-up retained but excluded.", "",
        "Rates use measured sender drain, including waits and earlier handovers. Stream bytes include the 11-byte header; useful upload bytes exclude it. "
        "Percentages are 100 × (candidate / baseline − 1). Each cell is median [min, max].", ""]
    for key, title in (("stream_bytes_per_second", "Command-stream bytes/s"),
                       ("upload_bytes_per_second", "Useful upload bytes/s")):
        lines += ["## " + title, "", "| Stream bytes | U0 | P0 | U1 | P1 |", "|---:|---:|---:|---:|---:|"]
        for row in rows:
            cells = [row["variants"][arm][key] for arm in ARMS]
            lines.append("| " + str(row["wire_bytes"]) + " | " + " | ".join(
                f"{c['median']:.0f} [{c['min']:.0f}, {c['max']:.0f}]" for c in cells) + " |")
        lines.append("")
    lines += ["## Rate and elapsed-time differences", "",
        "| Stream bytes | P1/P0 drain time change | P1/P0 stream rate change | P1/U1 stream rate | U1/U0 drain time change |",
        "|---:|---:|---:|---:|---:|"]
    for row in rows:
        c = row["comparison"]
        lines.append(f"| {row['wire_bytes']} | {c['P1_vs_P0_drain_time_percent']:+.2f}% | {c['P1_vs_P0_stream_rate_percent']:+.2f}% | {c['P1_over_U1_stream_rate']:.3f}× | {c['U1_vs_U0_drain_time_percent']:+.2f}% |")
    for key, title in (("submit_prt", "Application submission, ms"),
                       ("wire_prt", "Sender drain, ms"),
                       ("receipt_prt", "Local parallel completion, ms"),
                       ("reply_prt", "Ordered processing and reply, ms")):
        lines += ["", "## " + title, "", "| Stream bytes | U0 | P0 | U1 | P1 |", "|---:|---:|---:|---:|---:|"]
        for row in rows:
            cells = []
            for arm in ARMS:
                c = row["variants"][arm][key]
                cells.append("—" if key == "receipt_prt" and arm.startswith("U") else
                             f"{c['median_ms']:.3f} [{c['min_ms']:.3f}, {c['max_ms']:.3f}]")
            lines.append("| " + str(row["wire_bytes"]) + " | " + " | ".join(cells) + " |")
    lines += ["", "PRT1 is nominally 72,000 counts/s (13.8889 µs/count), without independent oscillator calibration. "
        "Drain is observed in software; interrupts and observation delay remain included. "
        "Parallel local completion is physical cleanup/UART return, with no software receipt. "
        "The ordered fence adds a seven-byte query and six-byte reverse reply; it does not prove rendering or HDMI presentation. "
        "These uploads do not measure reverse bulk rate, autonomous transmission or useful CPU headroom.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be fresh")
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    arms = load_campaign(args.campaign)
    rows = summarize(arms)
    args.output.mkdir(parents=True)
    result = dict(schema=1, direction="ez80-to-p4", timer_counts_per_second=TICKS_PER_SECOND,
                  header_bytes=HEADER_BYTES, arms=arms, comparison=rows,
                  campaign_sha256=sha(args.campaign), started_utc=started,
                  ended_utc=datetime.now(timezone.utc).isoformat(),
                  analysis_elapsed_host_seconds=time.monotonic() - clock)
    (args.output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (args.output / "RESULTS.md").write_text(markdown(rows))
    print("Validated 96 rows and complete receiver-buffer proofs; " + str(args.output / "RESULTS.md"))


if __name__ == "__main__":
    main()
