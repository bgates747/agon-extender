#!/usr/bin/env python3
"""Validate PORT-003 evidence invariants that are material to Review Gate 1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))

from dependency_model import load_data  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def require_unique(values: list[object], message: str) -> None:
    require(len(values) == len(set(values)), message)


def main() -> int:
    evidence = load_data(ROOT / "docs/tasks/PORT-003/generated/display-evidence.yaml")
    summary = evidence["summary"]
    require(summary["candidate_count"] == 6, "expected six Work 1.d candidates")
    require(summary["unresolved_selection_count"] == 0, "source selection is unresolved")
    require(summary["platform_source_count"] == 5, "expected five pinned P4 headers")

    candidates = {item["id"]: item for item in evidence["candidates"]}
    require_unique([item["id"] for item in evidence["candidates"]], "duplicate candidate ID")
    require_unique(
        [(item["owner"], item["path"]) for item in evidence["sources"]],
        "duplicate direct source tuple",
    )
    require_unique(
        [(item["path"], item["line"], item["declaration"]) for item in evidence["abstract_contract"]],
        "duplicate abstract-contract tuple",
    )
    require_unique(
        [(item["owner"], item["path"], item["line"]) for item in evidence["architecture_hits"]],
        "duplicate architecture-hit tuple",
    )
    require_unique(
        [item["path"] for item in evidence["platform"]["sources"]],
        "duplicate P4 platform source",
    )
    require(candidates["display-vdp-screen-facade"]["summary"]["selected_files"] > 0, "screen facade not selected")
    require(candidates["display-vga-concrete-controller-family"]["summary"]["excluded_files"] > 0, "old VGA family not excluded")

    declarations = "\n".join(item["declaration"] for item in evidence["abstract_contract"])
    require("swapBuffers" in declarations, "abstract contract omits swapBuffers")
    require("readScreen" in declarations, "abstract contract omits readScreen")
    require("getColumns" not in declarations, "text-controller method leaked into bitmapped contract")

    capability_categories = {
        category
        for item in evidence["platform"]["capabilities"]
        for category in item["categories"]
    }
    required = {
        "frame-consumer-callback",
        "multiple-framebuffers",
        "psram-framebuffer",
        "refresh-on-demand",
        "dma2d-copy",
        "capability-allocation",
        "cache-maintenance",
        "logical-timer",
    }
    require(required <= capability_categories, "pinned P4 capability coverage is incomplete")
    print("PORT-003 evidence validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
