#!/usr/bin/env python3
"""Generate the PORT-008 physical header-placement and ribbon-color reference.

The historical output filename is retained because PORT-008 already refers to
it. This revision intentionally contains no wiring, passives, or probe markers.
Connector assignments are checked against the authoritative r02 connectivity
model; colors preserve the legacy ribbon-conductor convention.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import yaml


SCRIPT = Path(__file__).resolve()
REPOSITORY = SCRIPT.parents[5]
CONNECTIVITY = REPOSITORY / "hardware/designs/light2-harness-r02/connectivity.yaml"
OUTPUT = SCRIPT.parent.parent / "normal-forward-wiring-and-probes.svg"

AGON_LABELS = {
    1: "VBAT", 2: "+5V USB", 3: "GND", 4: "+5V", 5: "GND",
    6: "ESP39", 7: "ESP35", 8: "ESP27", 9: "ESP26", 10: "ESP36",
    11: "ESP37", 12: "ESP38", 13: "PD4 / READY_N", 14: "PD5 / CLOCK",
    15: "PD6", 16: "PD7 / VALID_N", 17: "PC0 / TXD1 / D0",
    18: "PC1 / RXD1 / D1", 19: "PC2 / RTS1 / D2",
    20: "PC3 / CTS1 / D3", 21: "PC4 / D4", 22: "PC5 / D5",
    23: "PC6 / D6", 24: "PC7 / D7", 25: "CS", 26: "PB5",
    27: "PB6", 28: "CLK", 29: "SDA", 30: "SCL", 31: "PB3",
    32: "PB7", 33: "GND", 34: "+3.3V",
}

P4_LABELS = {
    "J2": {
        1: "P4 3V3", 2: "GND", 3: "unused", 4: "unused", 5: "unused",
        6: "unused", 7: "unused", 8: "unused", 9: "unused",
        10: "GPIO9 / D7", 11: "GPIO10 / D5",
        12: "GPIO11 / D3 / UART RTS", 13: "GPIO12 / D1 / UART TX",
        14: "GPIO13 / VALID_N", 15: "GPIO14 / CLOCK",
        16: "GPIO15 / UART forward OE_N", 17: "unused",
        18: "GPIO17 / parallel forward OE_N", 19: "unused", 20: "unused",
    },
    "J3": {
        1: "P4 5V (unused)", 2: "GND", 3: "unused", 4: "unused",
        5: "unused", 6: "unused", 7: "unused", 8: "GPIO33 / D6",
        9: "GPIO32 / D4", 10: "GPIO23 / D2 / UART CTS",
        11: "GPIO22 / D0 / UART RX", 12: "GPIO21 / UART return OE_N",
        13: "GPIO20 / READY control_N", 14: "unused", 15: "GND",
        16: "unused", 17: "unused", 18: "GND", 19: "unused", 20: "unused",
    },
}

# Exact conductor colors retained from the legacy 16-way Agon ribbons.
ODD_COLORS = [
    "#d32f2f", "#808080", "#111111", "#ffffff", "#808080", "#7b1fa2",
    "#1976d2", "#388e3c", "#fbc02d", "#f57c00", "#d32f2f", "#6d4c41",
    "#111111", "#ffffff", "#808080", "#7b1fa2", "#111111",
]
EVEN_COLORS = [
    "#1976d2", "#388e3c", "#fbc02d", "#f57c00", "#d32f2f", "#6d4c41",
    "#111111", "#ffffff", "#808080", "#7b1fa2", "#1976d2", "#388e3c",
    "#fbc02d", "#f57c00", "#d32f2f", "#6d4c41", "#d32f2f",
]
P4_COLORS = {
    ("J2", 10): "#388e3c", ("J2", 11): "#1976d2",
    ("J2", 12): "#7b1fa2", ("J2", 13): "#808080",
    ("J2", 14): "#ffffff", ("J2", 15): "#111111",
    ("J3", 8): "#6d4c41", ("J3", 9): "#d32f2f",
    ("J3", 10): "#f57c00", ("J3", 11): "#fbc02d",
    ("J3", 13): "#1976d2",
}


def load_connectors() -> dict[str, dict[int, str]]:
    model = yaml.safe_load(CONNECTIVITY.read_text(encoding="utf-8"))
    result = {}
    for component in model["components"]:
        if component["ref"] in {"J1", "J2", "J3"}:
            result[component["ref"]] = {
                int(item["pin"]): item["name"] for item in component["terminals"]
            }
    if set(result) != {"J1", "J2", "J3"}:
        raise RuntimeError("connectivity model lacks J1/J2/J3")
    return result


def text_color(fill: str) -> str:
    dark = {"#111111", "#6d4c41", "#7b1fa2", "#1976d2", "#388e3c", "#d32f2f"}
    return "#ffffff" if fill in dark else "#111111"


def bank(title: str, subtitle: str, x: int, y: int, rows: list[tuple[str, str]]) -> str:
    width, height, gap = 500, 25, 3
    out = [
        f'<g aria-label="{escape(title)}">',
        f'<text x="{x}" y="{y - 28}" class="bank-title">{escape(title)}</text>',
        f'<text x="{x}" y="{y - 9}" class="bank-note">{escape(subtitle)}</text>',
    ]
    for index, (label, fill) in enumerate(rows):
        row_y = y + index * (height + gap)
        out.append(f'<rect x="{x}" y="{row_y}" width="{width}" height="{height}" rx="3" fill="{fill}" stroke="#333"/>')
        out.append(f'<text x="{x + 8}" y="{row_y + 17}" class="pin" fill="{text_color(fill)}">{escape(label)}</text>')
    out.append("</g>")
    return "\n".join(out)


def main() -> None:
    authority = load_connectors()
    assert set(authority["J1"]) == set(range(1, 35))
    assert set(authority["J2"]) == set(range(1, 21))
    assert set(authority["J3"]) == set(range(1, 21))

    j2_rows = [(f"J2.{pin:02d}  {P4_LABELS['J2'][pin]}", P4_COLORS.get(("J2", pin), "#ffffff")) for pin in range(1, 21)]
    j3_rows = [(f"J3.{pin:02d}  {P4_LABELS['J3'][pin]}", P4_COLORS.get(("J3", pin), "#ffffff")) for pin in range(1, 21)]

    odd_rows, even_rows = [], []
    for landing in range(1, 18):
        odd, even = 2 * landing - 1, 2 * landing
        odd_fill = "#ffffff" if authority["J1"][odd].startswith("UNUSED_") else ODD_COLORS[landing - 1]
        even_fill = "#ffffff" if authority["J1"][even].startswith("UNUSED_") else EVEN_COLORS[landing - 1]
        odd_rows.append((f"Agon {odd:02d}  ·  JO1.{landing:02d}  ·  {AGON_LABELS[odd]}", odd_fill))
        even_rows.append((f"Agon {even:02d}  ·  JE1.{landing:02d}  ·  {AGON_LABELS[even]}", even_fill))

    content = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="1260" viewBox="0 0 1140 1260">',
        '<!-- Generated by scripts/generate-normal-forward-wiring-and-probes.py. -->',
        '<rect width="1140" height="1260" fill="#ffffff"/>',
        '<style>.title{font:700 24px sans-serif}.note{font:14px sans-serif;fill:#333}.bank-title{font:700 18px sans-serif}.bank-note{font:italic 13px sans-serif;fill:#444}.pin{font:700 13px monospace}</style>',
        '<text x="570" y="36" text-anchor="middle" class="title">Physical header placement and canonical conductor colors</text>',
        '<text x="570" y="61" text-anchor="middle" class="note">Header positions and pin order show the physical breadboard landing orientation.</text>',
        bank("J3 — ESP32-P4 EXT2", "physical left", 45, 112, j3_rows),
        bank("J2 — ESP32-P4 EXT1", "physical right", 595, 112, j2_rows),
        bank("JO1 — Agon odd-pin landing header", "Agon pin · breadboard-header pin · signal", 45, 738, odd_rows),
        bank("JE1 — Agon even-pin landing header", "Agon pin · breadboard-header pin · signal", 595, 738, even_rows),
        '<text x="570" y="1235" text-anchor="middle" class="note">Colors identify canonical ribbon conductors; this drawing does not specify electrical connectivity.</text>',
        '</svg>\n',
    ]
    OUTPUT.write_text("\n".join(content), encoding="utf-8")
    print(OUTPUT.relative_to(REPOSITORY))


if __name__ == "__main__":
    main()
