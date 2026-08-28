#!/usr/bin/env python3
"""Validate the independent EVF1 layout and browser/server credit models."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def transition(model: dict[str, object], state: str, event: str) -> tuple[str, str]:
    matches = [
        item for item in model["transitions"]
        if item["from"] == state and item["event"] == event
    ]
    if len(matches) != 1:
        raise ValueError(f"{state} + {event}: expected one transition, found {len(matches)}")
    return matches[0]["to"], matches[0]["action"]


def run_events(model: dict[str, object], events: list[str]) -> tuple[str, list[str]]:
    state = model["initial"]
    actions = []
    for event in events:
        state, action = transition(model, state, event)
        actions.append(action)
    return state, actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    wire = spec["wire"]
    fields = wire["fields"]
    occupied: set[int] = set()
    for field in fields:
        field_bytes = set(range(field["offset"], field["offset"] + field["size"]))
        if occupied & field_bytes:
            raise ValueError(f"overlapping EVF1 field: {field['name']}")
        occupied |= field_bytes
    assert occupied == set(range(wire["header_bytes"]))
    assert wire["flags"]["emitted_mask"] & ~wire["flags"]["known_mask"] == 0
    assert wire["flags"]["emitted_mask"] & wire["flags"]["required_mask"] == wire["flags"]["required_mask"]
    limits = wire["limits"]
    assert limits["maximum_width"] * 3 * limits["maximum_height"] == limits["maximum_payload_bytes"]

    scenario_results = []
    for scenario in spec["scenarios"]:
        result: dict[str, object] = {"id": scenario["id"]}
        if "server_events" in scenario:
            state, actions = run_events(spec["server_credit"], scenario["server_events"])
            assert state == scenario["expected_server_state"]
            result["server_state"] = state
            result["server_actions"] = actions
            if scenario.get("expected_release"):
                assert any("release lease" in action for action in actions)
        if "browser_events" in scenario:
            state, actions = run_events(spec["browser_credit"], scenario["browser_events"])
            assert state == scenario["expected_browser_state"]
            result["browser_state"] = state
            result["browser_actions"] = actions
            if scenario.get("expected_additional_credit") is False:
                assert sum("send one frame request" in action for action in actions) == 1
        scenario_results.append(result)

    output = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_evf1_contract_check",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/check-evf1-contract.py",
        "oracle_independence": "no production source, JavaScript, header, or binary imported",
        "header_bytes_covered": len(occupied),
        "scenario_results": scenario_results,
        "result": "pass",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(output, sort_keys=False), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
