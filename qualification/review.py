#!/usr/bin/env python3
"""Bind the Author's manual observations to one complete physical run, offline.

Never manufacture observations or prefill passing reviews. The input document
must transcribe an actual Author review after the physical automated run.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hardware_validation import atomic_json, sha256, utc_stamp


def bind_review(summary: dict, review: dict) -> dict:
    if (summary.get("status") != "success" or summary.get("full_suite") is not True or
            summary.get("restoration", {}).get("status") != "verified" or
            summary.get("notification", {}).get("status") != "success" or
            set(summary.get("flashed", {})) != {"p4", "emos"} or
            not summary.get("physical_cases") or
            any(case.get("status") != "pass" for case in summary["physical_cases"]) or
            summary.get("check_counts", {}).get("pass") != summary.get("check_counts", {}).get("required") or
            summary.get("check_counts", {}).get("required", 0) < 1):
        raise ValueError("manual review requires a complete successful physical run with restored CLI/notification")
    if review.get("schema") != 1 or not review.get("author_statement", "").strip():
        raise ValueError("actual Author statement required")
    required = summary["manual_cases_required"]
    if set(review.get("cases", {})) != set(required):
        raise ValueError("manual review must account for every declared visual/loaded-asset case")
    for case in review["cases"].values():
        if case.get("status") != "pass" or not case.get("observations", "").strip():
            raise ValueError("manual case is failed, pending or has no actual observation")
    return {"schema": 1, "qualification_state": "qualified",
            "output_profile": summary["output_profile"], "installed_pair": summary["flashed"],
            "author_review": review, "limits": "Declared profile and cases only; no all-mode or performance claim."}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, type=Path)
    p.add_argument("--review", required=True, type=Path)
    a = p.parse_args()
    summary_path = a.run / "summary.json"
    target = a.run / "author-review.json"
    if target.exists() or target.is_symlink():
        p.error("review receipt already exists; preserve it")
    review = bind_review(json.loads(summary_path.read_text()), json.loads(a.review.read_text()))
    review.update(summary_sha256=sha256(summary_path), review_source_sha256=sha256(a.review),
                  recorded_at=utc_stamp())
    atomic_json(target, review)
    print("Author review bound to the complete run; production selection/tagging remains separate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
