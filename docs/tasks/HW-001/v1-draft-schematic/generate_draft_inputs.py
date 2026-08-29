#!/usr/bin/env python3
"""Reproduce and check the frozen light2-harness-r02 electrical input.

This task-local generator exists because the design has 44 electrical
component instances and complete terminal accounting; KiCad projects the split
Agon connector as two symbols, producing 45 placed references. Keeping that
mechanical expansion in code
prevents transcription drift while the compact accepted topology remains in
HW-001 and ADR-0016. The generated YAML became the authoritative
``light2-harness-r02`` connectivity record only after explicit Author approval
on 2026-08-29. Normal use is ``--check``; ``--write-authority`` is deliberately
explicit because any electrical change requires a newly approved harness
revision rather than an in-place rewrite of r02.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = ROOT.parents[3]
MODEL_PATH = (
    REPOSITORY_ROOT
    / "hardware/designs/light2-harness-r02/connectivity.yaml"
)
PROJECTION_PATH = ROOT / "kicad-projection.yaml"
VALIDATOR_PATH = ROOT.parent / "electrical-model" / "validate.py"


def natural_key(value: str) -> tuple[tuple[int, Any], ...]:
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part.lower())
        for part in re.split(r"(\d+)", value)
        if part
    )


def terminal(
    pin: int | str,
    name: str,
    electrical_type: str,
    **extra: Any,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "pin": str(pin),
        "name": name,
        "electrical_type": electrical_type,
    }
    record.update(extra)
    return record


def resistor(ref: str, value: str, description: str) -> dict[str, Any]:
    return {
        "ref": ref,
        "kind": "resistor",
        "orientation": "symmetric",
        "terminal_scope": "complete",
        "value": value,
        "description": description,
        "terminals": [
            terminal(
                1,
                "A",
                "passive",
                interchangeable_group="resistor-ends",
            ),
            terminal(
                2,
                "B",
                "passive",
                interchangeable_group="resistor-ends",
            ),
        ],
    }


def capacitor(ref: str, value: str, description: str, domain: str) -> dict[str, Any]:
    return {
        "ref": ref,
        "kind": "capacitor",
        "orientation": "symmetric",
        "terminal_scope": "complete",
        "value": value,
        "description": description,
        "power_domain": domain,
        "terminals": [
            terminal(
                1,
                "A",
                "passive",
                interchangeable_group="capacitor-ends",
            ),
            terminal(
                2,
                "B",
                "passive",
                interchangeable_group="capacitor-ends",
            ),
        ],
    }


def connector(
    ref: str,
    value: str,
    count: int,
    names: dict[int, str],
    description: str,
) -> dict[str, Any]:
    return {
        "ref": ref,
        "kind": "connector",
        "orientation": "keyed",
        "terminal_scope": "complete",
        "value": value,
        "description": description,
        "terminals": [
            terminal(pin, names.get(pin, f"UNUSED_{pin}"), "passive")
            for pin in range(1, count + 1)
        ],
    }


def lvc244(ref: str, description: str) -> dict[str, Any]:
    names = {
        1: "1OE_N",
        2: "1A1",
        3: "2Y4",
        4: "1A2",
        5: "2Y3",
        6: "1A3",
        7: "2Y2",
        8: "1A4",
        9: "2Y1",
        10: "GND",
        11: "2A1",
        12: "1Y4",
        13: "2A2",
        14: "1Y3",
        15: "2A3",
        16: "1Y2",
        17: "2A4",
        18: "1Y1",
        19: "2OE_N",
        20: "VCC",
    }
    inputs = {1, 2, 4, 6, 8, 11, 13, 15, 17, 19}
    outputs = {3, 5, 7, 9, 12, 14, 16, 18}
    return {
        "ref": ref,
        "kind": "integrated-circuit",
        "orientation": "keyed",
        "terminal_scope": "complete",
        "part_number": "SN74LVC244AN",
        "value": "SN74LVC244AN",
        "description": description,
        "power_domain": "agon-domain",
        "terminals": [
            terminal(
                pin,
                names[pin],
                (
                    "power-input"
                    if pin in {10, 20}
                    else "input"
                    if pin in inputs
                    else "tri-state"
                    if pin in outputs
                    else "unspecified"
                ),
            )
            for pin in range(1, 21)
        ],
    }


def lv125(ref: str, description: str, domain: str) -> dict[str, Any]:
    names = {
        1: "1OE_N",
        2: "1A",
        3: "1Y",
        4: "2OE_N",
        5: "2A",
        6: "2Y",
        7: "GND",
        8: "3Y",
        9: "3A",
        10: "3OE_N",
        11: "4Y",
        12: "4A",
        13: "4OE_N",
        14: "VCC",
    }
    inputs = {1, 2, 4, 5, 9, 10, 12, 13}
    outputs = {3, 6, 8, 11}
    return {
        "ref": ref,
        "kind": "integrated-circuit",
        "orientation": "keyed",
        "terminal_scope": "complete",
        "part_number": "SN74LV125AN",
        "value": "SN74LV125AN",
        "description": description,
        "power_domain": domain,
        "terminals": [
            terminal(
                pin,
                names[pin],
                (
                    "power-input"
                    if pin in {7, 14}
                    else "input"
                    if pin in inputs
                    else "tri-state"
                    if pin in outputs
                    else "unspecified"
                ),
            )
            for pin in range(1, 15)
        ],
    }


def endpoint(ref: str, pin: int | str) -> dict[str, str]:
    return {"component": ref, "pin": str(pin)}


def generate_model() -> dict[str, Any]:
    components: list[dict[str, Any]] = []
    components.extend(
        [
            capacitor("C1", "100 nF", "U1 local bypass", "agon-domain"),
            capacitor("C2", "100 nF", "U2 local bypass", "agon-domain"),
            capacitor("C3", "100 nF", "U3 local bypass", "agon-domain"),
            capacitor("C4", "100 nF", "U4 local bypass", "p4-domain"),
            capacitor("C5", "1 uF", "Agon-domain local bulk", "agon-domain"),
            capacitor("C6", "1 uF", "P4-domain local bulk", "p4-domain"),
        ]
    )

    agon_names = {
        13: "PD4_READY_N",
        14: "PD5_CLOCK",
        16: "PD7_VALID_N",
        17: "PC0_TXD1_D0",
        18: "PC1_RXD1_D1",
        19: "PC2_RTS1_D2",
        20: "PC3_CTS1_D3",
        21: "PC4_D4",
        22: "PC5_D5",
        23: "PC6_D6",
        24: "PC7_D7",
        33: "GND",
        34: "AGON_3V3",
    }
    ext1_names = {
        1: "P4_3V3",
        2: "GND",
        10: "GPIO9_D7",
        11: "GPIO10_D5",
        12: "GPIO11_D3_UART_RTS",
        13: "GPIO12_D1_UART_TX",
        14: "GPIO13_VALID_N",
        15: "GPIO14_CLOCK",
        16: "GPIO15_UART_FWD_CTL_N",
        18: "GPIO17_PAR_FWD_CTL_N",
    }
    ext2_names = {
        1: "P4_5V_UNUSED",
        2: "GND",
        8: "GPIO33_D6",
        9: "GPIO32_D4",
        10: "GPIO23_D2_UART_CTS",
        11: "GPIO22_D0_UART_RX",
        12: "GPIO21_UART_RETURN_CTL_N",
        13: "GPIO20_READY_CTL_N",
        15: "GND",
        18: "GND",
    }
    components.extend(
        [
            connector(
                "J1",
                "Agon Light 2 GPIO 2x17",
                34,
                agon_names,
                "Agon Light 2 main GPIO header",
            ),
            connector(
                "J2",
                "Olimex P4 EXT1",
                20,
                ext1_names,
                "Olimex ESP32-P4-DevKit Rev D1 EXT1",
            ),
            connector(
                "J3",
                "Olimex P4 EXT2",
                20,
                ext2_names,
                "Olimex ESP32-P4-DevKit Rev D1 EXT2",
            ),
        ]
    )

    series_descriptions = [
        "D0/UART RX source-series candidate",
        "D1 source-series candidate",
        "D2/UART CTS source-series candidate",
        "D3 source-series candidate",
        "D4 source-series candidate",
        "D5 source-series candidate",
        "D6 source-series candidate",
        "D7 source-series candidate",
        "CLOCK source-series candidate",
        "VALID_N source-series candidate",
        "UART TX source-series candidate",
        "UART RTS source-series candidate",
        "READY_N source-series candidate",
    ]
    for number, description in enumerate(series_descriptions, start=1):
        components.append(resistor(f"R{number}", "220 ohm", description))

    pull_descriptions = {
        14: ("47 kohm", "GPIO22 D0/UART RX inactive pull-up"),
        15: ("47 kohm", "GPIO12 D1/UART TX inactive pull-up"),
        16: ("47 kohm", "GPIO23 D2/UART CTS inactive pull-up"),
        17: ("47 kohm", "GPIO11 D3/UART RTS inactive pull-up"),
        18: ("47 kohm", "GPIO32 D4 inactive pull-down"),
        19: ("47 kohm", "GPIO10 D5 inactive pull-down"),
        20: ("47 kohm", "GPIO33 D6 inactive pull-down"),
        21: ("47 kohm", "GPIO9 D7 inactive pull-down"),
        22: ("10 kohm", "GPIO14 CLOCK inactive pull-down"),
        23: ("10 kohm", "GPIO13 VALID_N inactive pull-up"),
        24: ("10 kohm", "Agon PD4 READY_N inactive pull-up"),
        25: ("10 kohm", "UART forward OE Agon-domain pull-up"),
        26: ("10 kohm", "Parallel forward OE Agon-domain pull-up"),
        27: ("10 kohm", "UART return OE Agon-domain pull-up"),
        28: ("10 kohm", "P4 GPIO15 U4 control pull-up"),
        29: ("10 kohm", "P4 GPIO17 U4 control pull-up"),
        30: ("10 kohm", "P4 GPIO21 U4 control pull-up"),
        31: ("10 kohm", "P4 GPIO20 U4 control pull-up"),
    }
    for number, (value, description) in pull_descriptions.items():
        components.append(resistor(f"R{number}", value, description))

    components.extend(
        [
            lvc244("U1", "Shared UART-forward and lower parallel/timing buffer"),
            lvc244("U2", "Upper parallel-data buffer"),
            lv125("U3", "Agon-powered UART return buffer", "agon-domain"),
            lv125("U4", "P4-powered low-only isolated controls", "p4-domain"),
        ]
    )
    components.sort(key=lambda component: natural_key(component["ref"]))

    nets: list[dict[str, Any]] = []

    def add_net(
        net_id: str,
        net_class: str,
        members: list[tuple[str, int | str]],
        description: str,
        power_domain: str | None | object = ...,
    ) -> None:
        record: dict[str, Any] = {
            "net_id": net_id,
            "class": net_class,
            "members": [endpoint(ref, pin) for ref, pin in members],
            "description": description,
        }
        if power_domain is not ...:
            record["power_domain"] = power_domain
        record["members"].sort(
            key=lambda member: (
                natural_key(member["component"]),
                natural_key(member["pin"]),
            )
        )
        nets.append(record)

    add_net(
        "agon-3v3",
        "power",
        [
            ("C1", 1), ("C2", 1), ("C3", 1), ("C5", 1), ("J1", 34),
            ("R24", 1), ("R25", 1), ("R26", 1), ("R27", 1),
            ("U1", 20), ("U2", 19), ("U2", 20), ("U3", 10),
            ("U3", 13), ("U3", 14),
        ],
        "Agon-sourced 3.3 V logic domain",
        "agon-domain",
    )
    add_net(
        "agon-pc0-d0-uart-tx",
        "signal",
        [("J1", 17), ("U1", 2)],
        "eZ80 PC0 source for D0 and UART1 TXD1",
    )
    add_net(
        "agon-pc1-d1-uart-rx",
        "signal",
        [("J1", 18), ("R11", 2), ("U1", 17)],
        "Shared eZ80 PC1 parallel D1 output or UART1 RXD1 input",
    )
    add_net(
        "agon-pc2-d2-uart-rts",
        "signal",
        [("J1", 19), ("U1", 4)],
        "eZ80 PC2 source for D2 and UART1 RTS1",
    )
    add_net(
        "agon-pc3-d3-uart-cts",
        "signal",
        [("J1", 20), ("R12", 2), ("U1", 15)],
        "Shared eZ80 PC3 parallel D3 output or UART1 CTS1 input",
    )
    for bit, pin, input_pin in ((4, 21, 2), (5, 22, 4), (6, 23, 6), (7, 24, 8)):
        add_net(
            f"agon-pc{bit}-d{bit}",
            "signal",
            [("J1", pin), ("U2", input_pin)],
            f"eZ80 PC{bit} parallel D{bit} source",
        )
    add_net(
        "agon-pd4-ready-n",
        "control",
        [("J1", 13), ("R13", 2), ("R24", 2)],
        "Active-low Extender-to-Agon parallel admission",
    )
    add_net(
        "agon-pd5-clock",
        "control",
        [("J1", 14), ("U1", 13)],
        "eZ80 parallel sampling clock source",
    )
    add_net(
        "agon-pd7-valid-n",
        "control",
        [("J1", 16), ("U1", 11)],
        "eZ80 active-low parallel record validity source",
    )

    ground_members: list[tuple[str, int]] = [
        ("C1", 2), ("C2", 2), ("C3", 2), ("C4", 2), ("C5", 2),
        ("C6", 2), ("J1", 33), ("J2", 2), ("J3", 2), ("J3", 15),
        ("J3", 18), ("R18", 2), ("R19", 2), ("R20", 2), ("R21", 2),
        ("R22", 2), ("U1", 6), ("U1", 8), ("U1", 10),
        ("U2", 10), ("U2", 11), ("U2", 13), ("U2", 15), ("U2", 17),
        ("U3", 7), ("U3", 9), ("U3", 12),
        ("U4", 2), ("U4", 5), ("U4", 7), ("U4", 9), ("U4", 12),
    ]
    add_net(
        "ground",
        "ground",
        ground_members,
        "Common signal return; positive supply rails remain separate",
        None,
    )

    add_net(
        "p4-3v3",
        "power",
        [
            ("C4", 1), ("C6", 1), ("J2", 1),
            ("R14", 1), ("R15", 1), ("R16", 1), ("R17", 1),
            ("R23", 1), ("R28", 1), ("R29", 1), ("R30", 1),
            ("R31", 1), ("U4", 14),
        ],
        "P4-sourced 3.3 V logic domain",
        "p4-domain",
    )

    forward_paths = [
        (1, "U1", 18, "p4-gpio22-d0-uart-rx", "J3", 11, "R14", 2),
        (2, "U1", 3, "p4-gpio12-d1-uart-tx", "J2", 13, "R15", 2),
        (3, "U1", 16, "p4-gpio23-d2-uart-cts", "J3", 10, "R16", 2),
        (4, "U1", 5, "p4-gpio11-d3-uart-rts", "J2", 12, "R17", 2),
        (5, "U2", 18, "p4-gpio32-d4", "J3", 9, "R18", 1),
        (6, "U2", 16, "p4-gpio10-d5", "J2", 11, "R19", 1),
        (7, "U2", 14, "p4-gpio33-d6", "J3", 8, "R20", 1),
        (8, "U2", 12, "p4-gpio9-d7", "J2", 10, "R21", 1),
        (9, "U1", 7, "p4-gpio14-clock", "J2", 15, "R22", 1),
        (10, "U1", 9, "p4-gpio13-valid-n", "J2", 14, "R23", 2),
    ]
    for resistor_number, driver, driver_pin, destination_net, connector_ref, connector_pin, pull_ref, pull_pin in forward_paths:
        add_net(
            f"{destination_net}-driver",
            "signal" if resistor_number <= 8 else "control",
            [(driver, driver_pin), (f"R{resistor_number}", 1)],
            f"Buffered source side of {destination_net}",
        )
        destination_members: list[tuple[str, int]] = [
            (f"R{resistor_number}", 2),
            (connector_ref, connector_pin),
            (pull_ref, pull_pin),
        ]
        if resistor_number == 2:
            destination_members.append(("U3", 2))
        if resistor_number == 4:
            destination_members.append(("U3", 5))
        add_net(
            destination_net,
            "signal" if resistor_number <= 8 else "control",
            destination_members,
            f"Protected P4 endpoint for {destination_net}",
        )

    add_net(
        "p4-uart-tx-driver",
        "signal",
        [("R11", 1), ("U3", 3)],
        "Buffered P4 UART2 TX source before series resistance",
    )
    add_net(
        "p4-uart-rts-driver",
        "control",
        [("R12", 1), ("U3", 6)],
        "Buffered P4 UART2 RTS source before series resistance",
    )
    add_net(
        "ready-n-driver",
        "control",
        [("R13", 1), ("U4", 11)],
        "Low-only READY_N source before series resistance",
    )

    add_net(
        "uart-forward-oe-n",
        "control",
        [("R25", 2), ("U1", 1), ("U4", 3)],
        "Agon-domain active-low enable for UART-forward U1 bank",
    )
    add_net(
        "parallel-forward-oe-n",
        "control",
        [("R26", 2), ("U1", 19), ("U2", 1), ("U4", 6)],
        "Agon-domain active-low enable for parallel-forward banks",
    )
    add_net(
        "uart-return-oe-n",
        "control",
        [("R27", 2), ("U3", 1), ("U3", 4), ("U4", 8)],
        "Agon-domain active-low enable for UART return drivers",
    )

    control_paths = [
        ("p4-gpio15-uart-forward-control-n", "J2", 16, "R28", "U4", 1),
        ("p4-gpio17-parallel-forward-control-n", "J2", 18, "R29", "U4", 4),
        ("p4-gpio20-ready-control-n", "J3", 13, "R31", "U4", 13),
        ("p4-gpio21-uart-return-control-n", "J3", 12, "R30", "U4", 10),
    ]
    for net_id, connector_ref, connector_pin, pull_ref, buffer_ref, buffer_pin in control_paths:
        add_net(
            net_id,
            "control",
            [(connector_ref, connector_pin), (pull_ref, 2), (buffer_ref, buffer_pin)],
            f"P4-domain pulled-up control {net_id}",
        )

    # The shared validator intentionally canonicalizes net IDs
    # lexicographically (unlike component and pin references, which use
    # natural order). Match that contract so regeneration stays byte-stable.
    nets.sort(key=lambda net: net["net_id"])

    connected = {
        (member["component"], member["pin"])
        for net in nets
        for member in net["members"]
    }
    unused_output_pins = {
        ("U1", "12"), ("U1", "14"),
        ("U2", "3"), ("U2", "5"), ("U2", "7"), ("U2", "9"),
        ("U3", "8"), ("U3", "11"),
    }
    unconnected: list[dict[str, str]] = []
    for component in components:
        for term in component["terminals"]:
            key = (component["ref"], term["pin"])
            if key in connected:
                continue
            if key in unused_output_pins:
                reason = "Disabled unused buffer output"
            elif component["kind"] == "connector":
                reason = "Header contact outside this bounded transport circuit"
            else:
                raise RuntimeError(f"unaccounted non-connector terminal {key}")
            unconnected.append(
                {"component": key[0], "pin": key[1], "reason": reason}
            )
    unconnected.sort(
        key=lambda item: (natural_key(item["component"]), natural_key(item["pin"]))
    )

    return {
        "schema_version": 1,
        "model": {
            "model_id": "light2-harness-r02",
            "title": "Light 2 common UART and forward-parallel transport r02",
            "status": "candidate",
            "authority": True,
            "scope": (
                "Authoritative placement-independent connectivity for the "
                "Agon Light 2 and Olimex ESP32-P4-DevKit Rev D1 controlled "
                "prototype transport."
            ),
            "source_refs": [
                "ADR-0016",
                "HW-001-D001",
                "HW-001-D002",
                "HW-001-D003",
                "HW-001-D004",
                "HW-001-D005",
                "HW-001-D006",
                "HW-001-D007",
                "HW-001-D008",
                "v1-uart-parallel-circuit-proposal.md",
            ],
            "notes": (
                "R1-R13 are frozen at 220 ohms for this candidate. The revision "
                "does not claim qualification of eZ80-only reset recovery, "
                "Legacy electrical absence, 1.152 Mbaud UART operation, or flow control."
            ),
        },
        "components": components,
        "nets": nets,
        "unconnected": unconnected,
    }


def generate_projection(model: dict[str, Any]) -> dict[str, Any]:
    mappings = []
    for component in model["components"]:
        ref = component["ref"]
        if ref.startswith("C"):
            library, symbol = "Device", "C"
        elif ref == "J1":
            library, symbol = "Connector_Generic", "Conn_02x17_Odd_Even"
        elif ref in {"J2", "J3"}:
            library, symbol = "Connector_Generic", "Conn_01x20"
        elif ref.startswith("R"):
            library, symbol = "Device", "R"
        elif ref in {"U1", "U2"}:
            library, symbol = "HW001_Draft", "SN74LVC244AN"
        elif ref in {"U3", "U4"}:
            library, symbol = "HW001_Draft", "SN74LV125AN"
        else:
            raise RuntimeError(f"no KiCad symbol mapping for {ref}")
        mappings.append({"ref": ref, "library": library, "symbol": symbol})
    return {
        "schema_version": 1,
        "source_model": "../../../../hardware/designs/light2-harness-r02/connectivity.yaml",
        "tool": "kicad7",
        "top_name": "v1-uart-parallel-model",
        "title": "Light 2 harness r02 UART and forward-parallel transport — CANDIDATE",
        "components": mappings,
    }


def validate_model(path: Path) -> None:
    spec = importlib.util.spec_from_file_location("hw001_validate", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator {VALIDATOR_PATH}")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    validator.validate(path)


def rendered(path: Path, header: str, document: dict[str, Any]) -> str:
    body = yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=100)
    return f"# {header}\n{body}"


def check_exact(path: Path, expected: str) -> None:
    if not path.exists():
        raise RuntimeError(f"missing generated input: {path}")
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        raise RuntimeError(
            f"{path} differs from the frozen deterministic definition; "
            "do not overwrite r02—review the change and assign a new revision"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        action="store_true",
        help="verify that the frozen authority and KiCad projection are exact",
    )
    mode.add_argument(
        "--write-authority",
        action="store_true",
        help="materialize the already approved r02 authority; never use to revise r02",
    )
    args = parser.parse_args()

    model = generate_model()
    projection = generate_projection(model)
    model_header = (
        "AUTHORITATIVE light2-harness-r02 connectivity; generated deterministically; "
        "electrical changes require a new revision."
    )
    projection_header = (
        "GENERATED KiCad projection; symbol/layout metadata is not electrical authority."
    )
    model_text = rendered(MODEL_PATH, model_header, model)
    projection_text = rendered(PROJECTION_PATH, projection_header, projection)

    if args.write_authority:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        MODEL_PATH.write_text(model_text, encoding="utf-8")
        PROJECTION_PATH.write_text(projection_text, encoding="utf-8")
    else:
        check_exact(MODEL_PATH, model_text)
        check_exact(PROJECTION_PATH, projection_text)

    validate_model(MODEL_PATH)
    print(
        f"PASS: {'materialized' if args.write_authority else 'checked'} "
        f"{MODEL_PATH} and {PROJECTION_PATH} "
        f"({len(model['components'])} components, {len(model['nets'])} nets, "
        f"{len(model['unconnected'])} intentional no-connects)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
