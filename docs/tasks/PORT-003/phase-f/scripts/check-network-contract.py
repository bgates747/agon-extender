#!/usr/bin/env python3
"""Validate the frozen narrow PORT-006 browser-video contract."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    hardware = spec["hardware"]
    gpio_roles = {
        "mdc": hardware["mdc_gpio"],
        "mdio": hardware["mdio_gpio"],
        "reset": hardware["reset_gpio"],
        **hardware["rmii"],
    }
    numeric_gpios = [value for value in gpio_roles.values() if isinstance(value, int)]
    assert len(numeric_gpios) == len(set(numeric_gpios))
    assert hardware["phy_address"] == 1
    assert "ETH_PHY_IP101" in spec["startup_call"]

    lifecycle = spec["lifecycle"]
    transition_keys = set()
    for transition in lifecycle["transitions"]:
        assert transition["from"] in lifecycle["states"]
        assert transition["to"] in lifecycle["states"]
        key = (transition["from"], transition["event"])
        if key in transition_keys:
            raise ValueError(f"duplicate lifecycle transition: {key}")
        transition_keys.add(key)

    routes = spec["http"]["routes"]
    route_keys = [(route["method"], route["path"]) for route in routes]
    assert len(route_keys) == len(set(route_keys))
    assert ("GET", "/video") in route_keys
    assert spec["opaque_message_api"]["lease"]["maximum_segments"] == 2
    assert spec["opaque_message_api"]["lease"]["maximum_total_bytes"] == 32 + 2359296
    assert spec["http"]["websocket"]["video_clients"] == 1
    assert spec["http"]["websocket"]["credits_per_client"] == 1
    assert spec["security_boundary"]["internet_exposure"] == "prohibited and unclaimed"

    output = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_006_initial_contract_check",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/check-network-contract.py",
        "unique_ethernet_gpio_count": len(numeric_gpios),
        "lifecycle_transition_count": len(transition_keys),
        "http_route_count": len(route_keys),
        "maximum_opaque_message_bytes": spec["opaque_message_api"]["lease"]["maximum_total_bytes"],
        "result": "pass",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(output, sort_keys=False), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
