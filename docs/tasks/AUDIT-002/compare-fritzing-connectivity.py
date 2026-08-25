#!/usr/bin/env python3
"""Compare extracted Fritzing connectivity with the AUDIT-002 circuit contract.

This task-local validator keeps design net names out of Fritzing's unstable
generated net IDs.  It resolves durable ``Instance.connector`` endpoint names,
checks each evidence-derived equivalence group, verifies required separation,
and rejects structural defects reported by the extractor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "expected-circuit.json"
CONNECTIVITY = ROOT / "generated" / "connectivity.json"
JSON_OUTPUT = ROOT / "generated" / "comparison.json"
MARKDOWN_OUTPUT = ROOT / "generated" / "comparison.md"


def endpoint_name(record: dict[str, object]) -> str:
    return f"{record['instance']}.{record['connector']}"


def compare() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text())
    actual = json.loads(CONNECTIVITY.read_text())

    endpoint_nets: dict[str, str] = {}
    non_board_members: dict[str, list[str]] = {}
    for net in actual["nets"]:
        net_id = net["net_id"]
        members: list[str] = []
        for endpoint in net["endpoints"]:
            name = endpoint_name(endpoint)
            if name in endpoint_nets:
                raise ValueError(f"duplicate extracted endpoint name: {name}")
            endpoint_nets[name] = net_id
            if endpoint["kind"] not in {"breadboard", "wire"}:
                members.append(name)
        non_board_members[net_id] = sorted(members)

    checks: list[dict[str, object]] = []

    def record(category: str, subject: str, passed: bool, detail: str) -> None:
        checks.append(
            {
                "category": category,
                "subject": subject,
                "passed": passed,
                "detail": detail,
            }
        )

    named_net_ids: dict[str, str | None] = {}
    for name, endpoints in manifest["named_nets"].items():
        missing = [endpoint for endpoint in endpoints if endpoint not in endpoint_nets]
        ids = sorted({endpoint_nets[endpoint] for endpoint in endpoints if endpoint in endpoint_nets})
        passed = not missing and len(ids) == 1
        named_net_ids[name] = ids[0] if passed else None
        detail_parts = []
        if missing:
            detail_parts.append("missing " + ", ".join(missing))
        if len(ids) != 1:
            detail_parts.append("resolved nets " + (", ".join(ids) or "none"))
        record(
            "named_net",
            name,
            passed,
            "; ".join(detail_parts) if detail_parts else f"all endpoints on {ids[0]}",
        )

    components = {item["title"]: item for item in actual["components"]}
    for name, expected in manifest["components"].items():
        item = components.get(name)
        passed = item is not None
        detail = "component absent"
        if item is not None:
            mismatches = []
            for field in ("kind", "value"):
                if field in expected and item.get(field) != expected[field]:
                    mismatches.append(
                        f"{field} expected {expected[field]!r}, found {item.get(field)!r}"
                    )
            passed = not mismatches
            detail = "; ".join(mismatches) if mismatches else "identity and value match"
        record("component", name, passed, detail)

    for left, right in manifest["different_net_pairs"]:
        left_id = named_net_ids.get(left)
        right_id = named_net_ids.get(right)
        passed = left_id is not None and right_id is not None and left_id != right_id
        record(
            "named_net_separation",
            f"{left} != {right}",
            passed,
            f"{left}={left_id or 'unresolved'}, {right}={right_id or 'unresolved'}",
        )

    for left, right in manifest["forbidden_same_net_endpoints"]:
        left_id = endpoint_nets.get(left)
        right_id = endpoint_nets.get(right)
        passed = left_id is not None and right_id is not None and left_id != right_id
        record(
            "endpoint_separation",
            f"{left} != {right}",
            passed,
            f"left={left_id or 'missing'}, right={right_id or 'missing'}",
        )

    for endpoint in manifest["isolated_endpoints"]:
        net_id = endpoint_nets.get(endpoint)
        members = non_board_members.get(net_id, []) if net_id else []
        passed = net_id is not None and members == [endpoint]
        record(
            "isolation",
            endpoint,
            passed,
            f"non-board members on {net_id or 'missing'}: {', '.join(members) or 'none'}",
        )

    findings = actual["findings"]
    for name, expected_count in manifest["structural_requirements"].items():
        actual_count = len(findings[name])
        record(
            "structure",
            name,
            actual_count == expected_count,
            f"expected {expected_count}, found {actual_count}",
        )

    failures = [item for item in checks if not item["passed"]]
    return {
        "schema_version": 1,
        "manifest": str(MANIFEST.relative_to(ROOT.parents[1])),
        "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "connectivity": str(CONNECTIVITY.relative_to(ROOT.parents[1])),
        "connectivity_input_sha256": actual["input_sha256"],
        "passed": not failures,
        "check_count": len(checks),
        "failure_count": len(failures),
        "checks": checks,
    }


def markdown(result: dict[str, object]) -> str:
    lines = [
        "# AUDIT-002 expected/actual circuit comparison",
        "",
        f"- Result: **{'PASS' if result['passed'] else 'FAIL'}**",
        f"- Checks: {result['check_count']}",
        f"- Failures: {result['failure_count']}",
        f"- Reviewed FZZ SHA-256: `{result['connectivity_input_sha256']}`",
        "",
        "## Checks",
        "",
        "| Result | Category | Subject | Detail |",
        "|---|---|---|---|",
    ]
    for item in result["checks"]:
        icon = "PASS" if item["passed"] else "FAIL"
        detail = str(item["detail"]).replace("|", "\\|")
        lines.append(
            f"| {icon} | `{item['category']}` | `{item['subject']}` | {detail} |"
        )
    lines.append("")
    return "\n".join(lines)


def outputs() -> dict[Path, bytes]:
    result = compare()
    return {
        JSON_OUTPUT: (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        MARKDOWN_OUTPUT: markdown(result).encode(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = outputs()
    if args.check:
        stale = [
            str(path)
            for path, data in expected.items()
            if not path.exists() or path.read_bytes() != data
        ]
        if stale:
            raise SystemExit("stale generated output: " + ", ".join(stale))
        if not json.loads(expected[JSON_OUTPUT])["passed"]:
            raise SystemExit("circuit comparison failed")
        return
    for path, data in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


if __name__ == "__main__":
    main()
