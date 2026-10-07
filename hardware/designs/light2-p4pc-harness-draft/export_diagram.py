#!/usr/bin/env python3
"""Render the PC pin map using the legacy diagram's banks, labels and colours.

The native board JSON remains the pin-allocation authority. This diagram is a
candidate construction aid, not an independently editable connectivity model.
It preserves the historical SVG and derives its complete Agon labels from it.
"""
from pathlib import Path
import hashlib
import json
import re
from html import escape
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "hardware/designs/light2-harness-r01/legacy-evidence/wiring-diagram.svg"
PROFILE = ROOT / "vdp/build/boards/p4-pc.json"
NS = {"s": "http://www.w3.org/2000/svg"}
board = json.loads(PROFILE.read_text())
legacy = ET.parse(SOURCE).getroot()
agon = {}
for text in legacy.findall(".//s:text", NS):
    label = "".join(text.itertext()).strip()
    match = re.fullmatch(r"(\d+)\s+(.+)", label)
    if match and (label.endswith("VBAT") or "PC" in label or "PD" in label
                  or "ESP" in label or label.endswith(("PB3", "PB5", "PB6", "PB7", "SCL", "SDA", "CS", "CLK"))):
        # Agon appears first in the legacy SVG. Later DevKit labels reuse pin
        # numbers and must not overwrite those physical Agon contacts.
        agon.setdefault(int(match[1]), match[2])
agon.update({2: "+5 V USB", 3: "GND", 4: "+5 V", 5: "GND", 33: "GND", 34: "+3.3 V"})
assert set(agon) == set(range(1, 35)), "all 34 Agon contacts must be labelled"
pc = {1: "+3.3 V", 2: "+5 V", 3: "GND", 4: "GPIO26 / USB1 N",
      5: "ESP_EN", 6: "GPIO27 / USB1 P", 7: "GPIO2 / User LED", 8: "GPIO14",
      9: "GPIO15", 10: "GPIO16", 11: "GPIO17", 12: "GPIO18", 13: "GPIO19",
      14: "GPIO20 / BAT_SENSE", 15: "GPIO32 / EXT_PWR_SEN", 16: "GPIO33",
      17: "GPIO36", 18: "GPIO46", 19: "GPIO47 / Spare", 20: "GPIO48 / Spare"}
t = board["transport"]
mapping = {17 + i: board["header"]["gpio_pins"][str(gpio)] for i, gpio in enumerate(t["data"])}
mapping.update({13: board["header"]["gpio_pins"][str(t["ready"])],
                14: board["header"]["gpio_pins"][str(t["clock"])],
                16: board["header"]["gpio_pins"][str(t["valid"])], 33: 3})
net = {17 + i: f"D{i}" for i in range(8)}
net.update({13: "READY_N", 14: "CLOCK", 16: "VALID_N", 33: "GND"})
colour = {"D0": "#fbc02d", "D1": "#808080", "D2": "#f57c00", "D3": "#7b1fa2",
          "D4": "#d32f2f", "D5": "#1976d2", "D6": "#6d4c41", "D7": "#388e3c",
          "READY_N": "#1976d2", "CLOCK": "#111111", "VALID_N": "#ffffff", "GND": "#111111"}
reverse = {destination: source for source, destination in mapping.items()}
parts = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1540" viewBox="0 0 1800 1540" font-family="DejaVu Sans, sans-serif">',
         '<title>Agon Light 2 to Olimex P4-PC Rev C — complete headers and straight-across wiring</title>',
         '<desc>Unversioned P4-PC wiring review draft. Derived from the legacy wiring diagram and native p4-pc board profile. All 34 Agon and 20 PC contacts shown. No sniffer markers or series resistors.</desc>',
         '<rect width="1800" height="1540" fill="white"/>']


def text(x, y, value, size=16, fill="#20242b", anchor="start", bold=False):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}">{escape(value)}</text>')


def rect(x, y, w, h, fill="#f5f6f8", stroke="#c2c8d0", **attrs):
    attributes = " ".join(f'{k.replace("_", "-")}="{escape(str(v))}"' for k, v in attrs.items())
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" {attributes}/>')


def path(d, stroke, width=3, **attrs):
    attributes = " ".join(f'{k.replace("_", "-")}="{escape(str(v))}"' for k, v in attrs.items())
    parts.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" {attributes}/>')


text(40, 40, "Agon Light 2 → Olimex ESP32-P4-PC Rev C", 28, bold=True)
text(40, 69, "Wiring review draft · Unversioned · Native build selection: p4-pc", 16, "#56606e")
text(40, 99, "Board-side views: look down onto the connector pins. Pin 1 is outlined; wiring-side socket views are mirrored.", 17)

# Physical paired-row views show every contact without stretching one bank or
# falsely representing two banks as two separate physical connectors.
text(60, 145, "Complete Agon GPIO header — 2 × 17", 20, bold=True)
text(60, 169, "Rotate the official horizontal pinout 90° counterclockwise; no mirror.", 14, "#56606e")
text(945, 145, "Complete P4-PC EXT1 header — 2 × 10", 20, bold=True)
text(945, 169, "Component side: LAN / HDMI end above; USB-A end below.", 14, "#56606e")
text(310, 194, "Pin 1 / VBAT end", 14, anchor="middle", bold=True)
text(1248, 194, "↑ LAN / HDMI", 14, anchor="middle", bold=True)


def overview(labels, count, x, start, pitch, is_pc=False):
    for pin in range(1, count + 1):
        col = (pin - 1) % 2
        row = (pin - 1) // 2
        xx, yy = x + col * 255, start + row * pitch
        active = pin in reverse if is_pc else pin in mapping
        rect(xx, yy, 245, pitch - 2, "#e9f3ff" if active else "#f5f6f8",
             "#111111" if pin == 1 else "#c2c8d0", stroke_width=3 if pin == 1 else 1,
             id=f'{"pc" if is_pc else "agon"}-overview-pin{pin}')
        label = labels[pin]
        if is_pc and active:
            label = label.split(" / ")[0]
            if net[reverse[pin]] != "GND":
                label += " / " + net[reverse[pin]]
        text(xx + 8, yy + pitch - 7, f"{pin:2d}  {label}", 13, bold=active or pin == 1)


overview(agon, 34, 60, 207, 21)
overview(pc, 20, 945, 207, 30, True)
text(310, 587, "Pin 33 GND / pin 34 +3.3 V end", 14, anchor="middle", bold=True)
text(1248, 529, "↓ Four USB-A keyboard ports", 14, anchor="middle", bold=True)
text(945, 556, "Odd pins on the left; even pins on the right.", 15)
text(945, 579, "The square pin-1 pad is the +3.3 V contact.", 15)

path("M 40 611 H 1760", "#c2c8d0", 1)
text(40, 645, "Breadboard wiring — same bank separation and wire colours as the original SVG", 21, bold=True)
text(40, 671, "Below, each header row is separated and reversed (high pin numbers at top) to keep the data wires straight.", 16, "#56606e")


def bank(odd, x):
    title = "Odd-numbered contacts" if odd else "Even-numbered contacts"
    text(x, 712, title, 20, bold=True)
    text(x, 739, "Agon GPIO", 16, bold=True)
    text(x + 420, 739, "P4-PC EXT1", 16, bold=True)
    first, pitch = 756, 29
    a_pins = list(range(33 if odd else 34, 0, -2))
    p_pins = list(range(19 if odd else 20, 0, -2))
    a_y = {pin: first + i * pitch for i, pin in enumerate(a_pins)}
    p_y = {pin: first + 4 * pitch + i * pitch for i, pin in enumerate(p_pins)}
    for pin in a_pins:
        active = pin in mapping
        fill = colour[net[pin]] if active else "#f5f6f8"
        ink = "white" if active and net[pin] not in ("D0", "D2", "VALID_N") else "#20242b"
        rect(x, a_y[pin], 235, 24, fill, "#555555" if active else "#c2c8d0", id=f'agon-bank-pin{pin}')
        text(x + 8, a_y[pin] + 17, f"{pin:2d}  {agon[pin]}", 14, ink, bold=active)
    for pin in p_pins:
        active = pin in reverse
        fill = colour[net[reverse[pin]]] if active else "#f5f6f8"
        ink = "white" if active and net[reverse[pin]] not in ("D0", "D2", "VALID_N") else "#20242b"
        label = pc[pin]
        if active:
            label = label.split(" / ")[0]
            if net[reverse[pin]] != "GND":
                label += " / " + net[reverse[pin]]
        rect(x + 420, p_y[pin], 255, 24, fill, "#555555" if active else "#c2c8d0", id=f'pc-bank-pin{pin}')
        text(x + 428, p_y[pin] + 17, f"{pin:2d}  {label}", 13, ink, bold=active)
    for source, destination in mapping.items():
        if source not in a_y:
            continue
        sy, dy = a_y[source] + 12, p_y[destination] + 12
        name = net[source]
        if name == "GND":
            # Route ground outside both columns, without crossing signal wires.
            d = f"M {x} {sy} H 20 V 1260 H 900 V 1058"
            path(d, "#111111", 3, id="wire-ground", data_agon_pin=source, data_pc_pin=destination, data_net=name)
            path(f"M {x+675} {dy} H 850 V 1260", "#111111", 3, id="wire-pc-ground")
            rect(848, 1258, 4, 4, "#111111", "#111111")
            text(x + 300, 1250, "Common ground: Agon 33 → PC EXT1-3", 14, anchor="middle", bold=True)
            continue
        d = f"M {x+235} {sy} H {x+355} V {dy} H {x+420}" if sy != dy else f"M {x+235} {sy} H {x+420}"
        if name == "VALID_N":
            path(d, "#555555", 5)
        path(d, colour[name], 3, id=f"wire-{name.lower()}", data_agon_pin=source, data_pc_pin=destination, data_net=name)
        text(x + 327, min(sy, dy) - 6, f"{source} → {destination} · {name}", 11, "#374151", anchor="middle")
        resistance = 15000 if name.startswith("D") else 10000
        rail = "GND" if name == "CLOCK" else "AGON_3V3"
        # Pulls attach to the Agon contact, not to the PC board's power pins.
        # Keep resistor values explicit: data 15k, inherited handshake bias 10k.
        path(f"M {x} {sy} H {x-20}", colour[name] if name != "VALID_N" else "#555555", 2)
        rect(x-80, sy-8, 60, 16, "#fffaf0", "#8d6e63",
             id=f"pull-{name.lower()}", data_agon_pin=source,
             data_resistance_ohm=resistance, data_rail=rail)
        text(x-50, sy+4, "15 kΩ" if resistance == 15000 else "10 kΩ", 11, anchor="middle", bold=True)
        rail_x = 900 if rail == "GND" else x-120
        d = f"M {x-80} {sy} H {rail_x}"
        if rail == "GND":
            # White crossover gap: CLOCK ground is not joined to the red rail.
            path(d, "white", 7)
        path(d, "#111111" if rail == "GND" else "#d32f2f", 2)
        rect(rail_x-2, sy-2, 4, 4, "#111111" if rail == "GND" else "#d32f2f",
             "#111111" if rail == "GND" else "#d32f2f")
    text(x + 420, 1222, "↑ High-numbered end; pin 1/2 end ↓", 12, "#56606e")


# Shared Agon positive rail, fed only by Agon pin 34. PC power pins stay open.
path("M 1060 768 H 940 V 690 H 40 V 1108", "#d32f2f", 3, id="agon-power-feed", data_agon_pin=34)
path("M 940 768 V 1108", "#d32f2f", 3)
text(545, 686, "Agon +3.3 V — from pin 34", 14, "#b71c1c", anchor="middle", bold=True)
text(40, 815, "+3.3 V", 12, "#b71c1c")
text(940, 815, "+3.3 V", 12, "#b71c1c")
text(900, 1145, "GND", 12, bold=True)
bank(True, 160)
bank(False, 1060)
path("M 885 699 V 1283", "#dce0e6", 1)
path("M 40 1294 H 1760", "#c2c8d0", 1)
text(40, 1328, "Pulls and spare contacts", 20, bold=True)
text(40, 1358, "Eight data pull-ups: 15 kΩ each to Agon pin 34 (+3.3 V). READY_N and VALID_N: 10 kΩ pull-ups to that same rail.", 17)
text(40, 1386, "CLOCK: 10 kΩ pull-down to common ground. Handshake values follow the original drawing; data values follow the later harness.", 16)
text(40, 1414, "P4-PC EXT1-19 / GPIO47 and EXT1-20 / GPIO48 remain spare. GPIO20/32 sensing links must remain disconnected.", 16)
text(40, 1442, "Connect the common ground only; do not join the independently powered Agon and P4-PC positive supply rails.", 16)
text(40, 1473, "READY_N has one jog because Agon pin 15 is unused. No series resistors or sniffer circles. A square dot marks a rail junction.", 16)
text(40, 1510, "Pin authority: vdp/build/boards/p4-pc.json · Physical reference: Olimex Rev C schematic and top silkscreen · 2026-10-04", 13, "#56606e")
parts.append("</svg>")
target = HERE / "wiring-diagram.svg"
target.write_text("\n".join(parts) + "\n")
print(f"Wrote {target.relative_to(ROOT)}")
print("Legacy source SHA256:", hashlib.sha256(SOURCE.read_bytes()).hexdigest())
