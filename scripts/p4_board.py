"""Validated compile-time board inputs for the native P4 builder.

Board files describe wiring, not software/source selection or transport
admission. Generated outputs are disposable and never an editable authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

BOARD_DIR = Path(__file__).resolve().parents[1] / "vdp/build/boards"
DEFAULT_BOARD = "p4-devkit"


def load_board(name: str, profile: str) -> tuple[dict, Path]:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise SystemExit("unsafe board name")
    path = BOARD_DIR / f"{name}.json"
    if not path.is_file():
        raise SystemExit(f"unknown board: {name}")
    board = json.loads(path.read_text())
    validate_board(board, name, profile)
    return board, path


def validate_board(board: dict, name: str, profile: str) -> None:
    def require(condition: bool, message: str) -> None:
        if not condition:
            raise SystemExit(f"board {name}: {message}")

    require(board.get("schema_version") == 1 and board.get("chip") == "esp32p4",
            "unsupported schema or chip")
    require(board.get("board") == name, "board identity differs from filename")
    require(bool(re.fullmatch(r"[a-z0-9-]+-r[0-9]+", board.get("identity", ""))),
            "missing revisioned identity")
    require(profile in board.get("supported_profiles", []),
            f"unsupported software profile: {profile}")
    require(board.get("display_output") == "browser-only", "unsupported display output")
    require((board.get("silicon_min"), board.get("silicon_max")) == (100, 199),
            "unreviewed silicon range")

    def gpio(value: object) -> bool:
        # P4 GPIO numbers 0-54 exist; flash and onboard connections are reserved
        # separately. Reject bool, which Python otherwise treats as integer.
        return type(value) is int and 0 <= value <= 54

    t = board["transport"]
    require(len(t["data"]) == 8 and len(t["isolation"]) in (0, 3),
            "expected eight lanes and zero or three isolation controls")
    pins = [*t["data"], t["clock"], t["valid"], t["ready"], *t["isolation"]]
    require(all(gpio(pin) for pin in pins), "invalid transport GPIO")
    require(len(pins) == len(set(pins)), "duplicate transport GPIO")
    require(all(gpio(pin) for pin in board["reserved_gpios"]), "invalid reserved GPIO")
    require(not set(pins).intersection(board["reserved_gpios"]),
            "transport touches reserved onboard GPIO")
    require(set(board["requires_disconnected_sensing"]).issubset(pins),
            "sensing condition does not refer to a transport GPIO")
    header = board["header"]
    if name == "p4-pc":
        # Physical Rev C EXT1 header is fixed. Validate it independently of the
        # desired logical assignment so edited metadata cannot invent a pad.
        actual = {"2": 7, "14": 8, "15": 9, "16": 10, "17": 11, "18": 12,
                  "19": 13, "20": 14, "32": 15, "33": 16, "36": 17, "46": 18,
                  "47": 19, "48": 20, "26": 4, "27": 6}
        require(header == {"name": "EXT1", "gpio_pins": actual, "ground_pin": 3},
                "header differs from reviewed Rev C pinout")
        require(set(pins).issubset(map(int, actual)), "transport GPIO absent from header")
        require(set(board["requires_disconnected_sensing"]) == set(pins).intersection({20, 32}),
                "missing optional sensing condition")
        require(not t["isolation"], "direct PC harness has no isolation controls")
    eth = board["ethernet"]
    require(eth["phy"] == "IP101" and type(eth["address"]) is int
            and 0 <= eth["address"] <= 31, "unsupported Ethernet PHY/address")
    require(all(gpio(eth[k]) for k in ("mdc", "mdio", "reset", "clock_input")),
            "invalid Ethernet GPIO")
    # Arduino's P4 EMAC clock selection is fixed to the external clock pad.
    require(eth["clock_input"] == 50, "unsupported P4 RMII clock pad")
    sd = board["sd"]
    require(all(gpio(sd[k]) for k in ("clk", "cmd", "d0", "d1", "d2", "d3")),
            "invalid SD GPIO")
    require(type(sd["ldo"]) is int and 1 <= sd["ldo"] <= 4, "invalid SD LDO")
    usb = board["usb"]
    require(usb["hub_reset"] is None or gpio(usb["hub_reset"]), "invalid hub reset GPIO")
    require(usb["peripheral_map"] == 0, "only the reviewed HS host selection is supported")
    for key in ("reset_assert_ms", "reset_recovery_ms"):
        require(type(usb[key]) is int and 0 <= usb[key] <= 1000, "invalid USB reset delay")
    peripheral_pins = [eth[k] for k in ("mdc", "mdio", "reset", "clock_input")]
    peripheral_pins += [sd[k] for k in ("clk", "cmd", "d0", "d1", "d2", "d3")]
    if usb["hub_reset"] is not None:
        peripheral_pins.append(usb["hub_reset"])
    require(len(peripheral_pins) == len(set(peripheral_pins)), "duplicate peripheral GPIO")
    require(not set(pins).intersection(peripheral_pins), "transport/peripheral GPIO conflict")
    overrides = board["sdkconfig_overrides"]
    require(set(overrides).issubset({"CONFIG_USB_HOST_HUBS_SUPPORTED", "CONFIG_USB_HOST_HUB_MULTI_LEVEL"}),
            "unreviewed SDK override")
    require(all(value in ("y", "n") for value in overrides.values()), "invalid SDK override")
    require(usb["hub_reset"] is None or overrides.get("CONFIG_USB_HOST_HUBS_SUPPORTED") == "y",
            "hub reset requires SDK hub support")


def render_header(board: dict) -> str:
    t, eth, sd, usb = (board[k] for k in ("transport", "ethernet", "sd", "usb"))
    fence = [*t["data"], t["clock"], t["valid"], t["ready"], *t["isolation"]]
    # Preserve the existing DevKit startup reset order as well as its pin set.
    if board["board"] == DEFAULT_BOARD:
        fence.sort()
    text = "// Generated from vdp/build/boards; do not edit.\n#pragma once\n#include <array>\n"
    text += "namespace agon::extender::board {\n"
    text += f'inline constexpr char kIdentity[] = "{board["identity"]}";\n'
    text += f"inline constexpr std::array<int, 8> kDataPins{{{', '.join(map(str, t['data']))}}};\n"
    text += f"inline constexpr std::array<int, {len(fence)}> kFencePins{{{', '.join(map(str, fence))}}};\n"
    values = {"UartRx": t["data"][0], "UartTx": t["data"][1],
              "UartCts": t["data"][2], "UartRts": t["data"][3],
              "Clock": t["clock"], "Valid": t["valid"], "Ready": t["ready"],
              "PhyAddress": eth["address"], "EthMdc": eth["mdc"],
              "EthMdio": eth["mdio"], "EthReset": eth["reset"],
              "SdLdo": sd["ldo"], "UsbHubReset": usb["hub_reset"] if usb["hub_reset"] is not None else -1,
              "UsbResetAssertMs": usb["reset_assert_ms"], "UsbResetRecoveryMs": usb["reset_recovery_ms"],
              "UsbPeripheralMap": usb["peripheral_map"]}
    values.update({"Sd" + k.capitalize(): sd[k] for k in ("clk", "cmd", "d0", "d1", "d2", "d3")})
    text += "".join(f"inline constexpr int k{key} = {value};\n" for key, value in values.items())
    text += "}\n"
    return text


def apply_sdk_overrides(config: str, overrides: dict[str, str]) -> str:
    keys = set(overrides)
    lines = [line for line in config.splitlines()
             if not any(line.startswith(key + "=") or line == f"# {key} is not set" for key in keys)]
    lines.extend(f"{key}={value}" if value != "n" else f"# {key} is not set"
                 for key, value in sorted(overrides.items()))
    return "\n".join(lines) + "\n"


def write_board_inputs(board: dict, path: Path, output: Path, generated: Path) -> dict:
    header = generated / "agon_extender_board_config.hpp"
    header.write_text(render_header(board))
    record = {"board": board["board"], "identity": board["identity"],
              "profile_path": str(path), "profile_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "header_sha256": hashlib.sha256(header.read_bytes()).hexdigest(),
              "configuration": board}
    (output / "board.json").write_text(json.dumps(record, indent=2) + "\n")
    return record
