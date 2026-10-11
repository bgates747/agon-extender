#!/usr/bin/env python3
"""Render the existing DevKit header cells with documented external pulls.

Labels and conductor fills come from the retained original SVG, not a new
pin assignment. Control bias comes from light2-harness-r01/profile.yaml;
the retained data-lane pull-up value comes from light2-harness-r03/README.md.
The result is an intended-wiring reference, not as-built qualification.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
import yaml


ROOT = Path(__file__).resolve().parents[4]
LEGACY = ROOT / "hardware/designs/light2-harness-r01"
NS = {"s": "http://www.w3.org/2000/svg"}
COLORS = {
    "#111111": "Black", "#ffffff": "White", "#1976d2": "Blue",
    "#388e3c": "Green", "#808080": "Gray", "#7b1fa2": "Purple",
    "#fbc02d": "Yellow", "#f57c00": "Orange", "#d32f2f": "Red",
    "#6d4c41": "Brown",
}


def main():
    root = ET.parse(LEGACY / "legacy-evidence/wiring-diagram.svg").getroot()
    profile = yaml.safe_load((LEGACY / "profile.yaml").read_text())
    connections = {
        (f"p4-{s['p4_header'].lower()}", s["p4_header_pin"]): s
        for s in profile["signals"]
    }
    image = Image.new("RGB", (1600, 1580), "white")
    draw = ImageDraw.Draw(image)
    fontdir = Path("/usr/share/fonts/truetype/dejavu")

    def text(x, y, label, size=23, bold=False, fill="#15202b"):
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        draw.text((x, y), label, font=ImageFont.truetype(str(fontdir / name), size), fill=fill)

    text(40, 25, "Olimex ESP32-P4-DevKit Rev D1 — full header reference", 34, True)
    text(40, 82, "Component-side view • Ethernet at top • USB Serial/JTAG at bottom", 25, True)
    text(40, 124, "Both headers: pin 20 at Ethernet end; pin 1 at USB end. Harness colors, not probe colors.", 23)
    text(40, 160, "Existing header drawing with external pull annotations; intended wiring, not verified as-built positions.", 20)
    count = 0
    for ident, x, title in [("p4-ext1", 40, "EXT1 — board left"), ("p4-ext2", 820, "EXT2 — board right")]:
        text(x, 200, title, 27, True)
        group = root.find(f"s:g[@id='{ident}']", NS)
        children = list(group)
        for pin in range(20, 0, -1):
            cell = group.find(f"s:rect[@id='{ident}-pin{pin}']", NS)
            label = "".join(children[children.index(cell) + 1].itertext()).replace("\xa0", " ")
            assert label.split()[0] == str(pin)
            fill = cell.attrib["fill"]
            fg = "#111111" if fill in {"#ffffff", "#fbc02d", "#f57c00"} else "white"
            y = 246 + (20 - pin) * 54
            draw.rounded_rectangle((x, y, x + 740, y + 49), radius=4, fill=fill, outline="#59616a")
            signal = connections.get((ident, pin))
            text(x + 12, y + (1 if signal else 10), label, 22, True, fg)
            if signal:
                text(x + 624, y + 3, COLORS[fill], 21, True, fg)
                name = signal["name"]
                control = profile["electrical"]["control_bias"].get(name)
                if control:
                    direction = control["direction"]
                    value = control["resistance_ohm"] // 1000
                    rail = "Agon 3.3 V" if direction == "pull-up" else "common GND"
                    draw.rounded_rectangle((x - 3, y - 3, x + 743, y + 52), radius=5, outline="#dc7800", width=3)
                else:
                    # Existing eight data pulls; distinct from the 220-ohm series parts.
                    value, direction, rail = 15, "pull-up", "Agon 3.3 V"
                text(x + 12, y + 28, f"{value} kΩ {direction} → {rail}", 17, False, fg)
            count += 1
    assert count == 40 and len(connections) == 11
    text(40, 1340, "USB Serial/JTAG end — pin 1 is at the bottom of both headers", 25, True)
    text(40, 1390, "READY_N + VALID_N: 10 kΩ up to Agon 3.3 V.  CLOCK: 10 kΩ down to common GND.", 23, True)
    text(40, 1435, "Data D0–D7: one 15 kΩ pull-up per line to Agon 3.3 V.", 23, True)
    text(40, 1480, "Pull resistors are external. The separate 220 Ω data-series resistors are not pull resistors.", 21)
    text(40, 1520, "Use Agon's pull-up rail; do not connect it to the P4's 3.3 V or 5 V supply pins.", 21)
    image.save(ROOT / "docs/tasks/PORT-008/devkit-header-reference-r01.png")


if __name__ == "__main__":
    main()
