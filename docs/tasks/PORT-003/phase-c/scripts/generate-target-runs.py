#!/usr/bin/env python3
"""Generate the Phase C target-run index from authoritative run manifests."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import load_data, sha256_file, write_canonical  # noqa: E402


OBSERVATION_FIELDS = {
    "normal_elapsed_ticks": "elapsed_ticks",
    "independently_polled_notice_samples": "polled_notice_samples",
    "maximum_poll_interval_us": "maximum_poll_interval_us",
    "injected_tick_distinct_edges": "injected_edge_delta",
    "rollover_final_counter": "rollover_final_counter",
    "bounded_unconsumed_drops": "unconsumed_drops",
    "restart_cycles": "restart_cycles",
    "final_result": "final_result",
}


def indexed_run(path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    observations = {
        item["requirement"]: item.get("observed")
        for item in manifest.get("observations", [])
    }
    selected = {
        output: observations[source]
        for source, output in OBSERVATION_FIELDS.items()
        if source in observations
    }
    initial_heap = observations.get("initial_free_heap_bytes")
    final_heap = observations.get("final_free_heap_bytes")
    if isinstance(initial_heap, int) and isinstance(final_heap, int):
        selected["heap_delta_bytes"] = final_heap - initial_heap
    return {
        "run_id": manifest["run"]["run_id"],
        "manifest": path.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha256_file(path),
        "candidate_identity": manifest["artifacts_under_test"][0]["identity"],
        "qualification_procedure": manifest["procedure"]["identity"],
        "source_commit": manifest["source"]["commit"],
        "outcome": manifest["run"]["outcome"],
        "procedure_deviation_count": len(manifest["procedure"].get("deviations", [])),
        "observations": selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-c/evidence/target-runs.yaml",
    )
    args = parser.parse_args()
    runs = []
    for path in sorted((ROOT / "tests/runs").glob("PORT-003-*/manifest.yaml")):
        manifest = load_data(path)
        if manifest.get("procedure", {}).get("artifact_id") != "p4-frame-service-qualification":
            continue
        runs.append(indexed_run(path, manifest))
    write_canonical(
        args.output.resolve(),
        {
            "schema_version": "1.0.0",
            "artifact_kind": "port_003_phase_c_target_runs",
            "generated_by": "docs/tasks/PORT-003/phase-c/scripts/generate-target-runs.py",
            "runs": runs,
        },
    )
    print(f"indexed {len(runs)} Phase C target run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
