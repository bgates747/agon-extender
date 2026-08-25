#!/usr/bin/env python3
"""Generate the SETUP-006.3 Fritzing wiring-diagram scaffold.

This file exists because hand-aligning detachable breadboard sections in
Fritzing 1.0.1 proved unreliable.  It deliberately owns all 0.1-inch grid
coordinates, custom-part connectors, breadboard buses, and P4 placement.

The output establishes placement and connection points for a wiring diagram.
Only the explicitly rendered Agon header banks are assigned; do not infer
other signal wiring, electrical safety, or qualification.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"

SVG_DPI = 72.0
SCENE_DPI = 90.0
PITCH = 7.2  # 0.1 inch at Fritzing's conventional 72 SVG units/inch.
SCENE_PITCH = 9.0  # 0.1 inch in Fritzing sketch geometry coordinates.
COLUMNS = 63
FIRST_HOLE_X = 10.8

MODULE_HEIGHT = 97.2
MODULE_OVERLAP = 7.2
RAIL_BODY_HEIGHT = 25.2
RAIL_EDGE_OVERLAP = MODULE_OVERLAP / 2.0

# The physical assembly uses both BB100R strips supplied with the BB1460 kit:
# one at the top edge and one between the two BB630 terminal areas. Each rail
# overlaps its neighboring snap edge by half a grid interval.
TOP_RAIL_Y = 0.0
TOP_MODULE_Y = TOP_RAIL_Y + RAIL_BODY_HEIGHT - RAIL_EDGE_OVERLAP
CENTER_RAIL_Y = TOP_MODULE_Y + MODULE_HEIGHT - RAIL_EDGE_OVERLAP
BOTTOM_MODULE_Y = CENTER_RAIL_Y + RAIL_BODY_HEIGHT - RAIL_EDGE_OVERLAP
ASSEMBLY_HEIGHT = BOTTOM_MODULE_Y + MODULE_HEIGHT

MODULE_ROW_Y = {
    letter: 12.6 + index * PITCH + (PITCH if index >= 5 else 0.0)
    for index, letter in enumerate("ABCDEFGHIJ")
}
TOP_ROW_Y = {
    letter: TOP_MODULE_Y + y for letter, y in MODULE_ROW_Y.items()
}
BOTTOM_ROW_Y = {
    letter: BOTTOM_MODULE_Y + y for letter, y in MODULE_ROW_Y.items()
}

# The facing five-hole groups are F:J on the upper BB630 and A:E on the lower
# BB630.  Each P4 header occupies their middle row, leaving two holes outward
# and two inward.  The custom composite absorbs the one-grid overlap required
# to keep the P4's exact 1.0-inch header spacing on-grid.
EXT1_BOARD_ROW = "H"
EXT2_BOARD_ROW = "C"
EXT1_Y = TOP_ROW_Y[EXT1_BOARD_ROW]
EXT2_Y = BOTTOM_ROW_Y[EXT2_BOARD_ROW]

# A BB100R's two contact rows occupy the center of its 0.35-inch body. The
# red and blue legends sit outside those rows; they do not pass through holes.
RAIL_HOLE_Y_OFFSETS = (9.0, 16.2)
RAIL_LEGEND_Y_OFFSETS = (4.5, 20.7)
RAIL_LOCATIONS = {
    "top": TOP_RAIL_Y,
    "center": CENTER_RAIL_Y,
}
# This landscape drawing keeps Agon columns increasing left-to-right. Rather
# than rotate the established wiring layout, both distribution strips place
# the blue/GND rail above the red/hot rail.
RAIL_ROWS = ("blue", "red")
RAIL_LEGEND_COLORS = {
    "blue": "#306bc9",
    "red": "#d93434",
}
RAIL_COLUMNS = tuple(column for column in range(1, 61) if column % 6)

BOARD_WIDTH = 468.0  # 6.5 inches in SVG units.
# Keep stable diagram margins on 0.1-inch dimensions.  GUI evidence later
# established that connector phase, rather than canvas-center phase, controls
# the observed first-movement snap; these dimensions are not relied upon as a
# snapping workaround.
BOARD_VIEW_WIDTH = 6.6 * SVG_DPI
BOARD_VIEW_HEIGHT = 3.4 * SVG_DPI

# Official Olimex Rev D1 PCB facts extracted from the maintained KiCad source.
P4_BOARD_LENGTH = 72.0 / 25.4 * SVG_DPI
P4_BOARD_WIDTH = 30.0 / 25.4 * SVG_DPI
P4_HEADER_SEPARATION = 25.4 / 25.4 * SVG_DPI
P4_HEADER_EDGE_INSET = (30.0 - 25.4) / 2.0 / 25.4 * SVG_DPI
P4_PIN1_END_INSET = 11.6 / 25.4 * SVG_DPI

# These connector positions deliberately share the breadboard holes' 0.05-inch
# phase relative to Fritzing's 0.1-inch grid.  The resulting part origin is on
# the grid, so moving the complete P4 with Align to Grid enabled preserves all
# header-to-hole alignment.  This padding is a Fritzing integration constraint,
# not an Olimex board dimension.
P4_PIN1_X = 0.65 * SVG_DPI
P4_EXT1_Y = 0.175 * SVG_DPI
P4_EXT2_Y = P4_EXT1_Y + P4_HEADER_SEPARATION
P4_BODY_X = P4_PIN1_X - P4_PIN1_END_INSET
# Breadboard view is a wiring diagram, not a mechanical footprint.  Crop the
# rendered PCB body to the header centerlines so sockets immediately outside
# both headers remain visible and easy to wire.  The physical 30 mm board width
# remains recorded above and in the task evidence; it must not be inferred from
# this deliberately diagrammatic silhouette.
P4_BODY_Y = P4_EXT1_Y
P4_BODY_HEIGHT = P4_HEADER_SEPARATION
P4_VIEW_WIDTH = 3.2 * SVG_DPI
P4_VIEW_HEIGHT = 1.4 * SVG_DPI
P4_BODY_CENTER_Y = P4_BODY_Y + P4_BODY_HEIGHT / 2.0

P4_SVG_X = FIRST_HOLE_X - P4_PIN1_X
P4_SVG_Y = EXT1_Y - P4_EXT1_Y

# Fritzing 1.0.1 moves both parts by this exact translation on their first
# interactive grid-aligned movement.  The translation puts the BB1460 terminal
# centers and matching P4 header centers directly on 0.1-inch grid lines.
# Generate that canonical post-snap state instead of making the GUI discover it.
GRID_PHASE_X = 0.05 * SCENE_DPI
GRID_PHASE_Y = 0.025 * SCENE_DPI
BOARD_SCENE_X = GRID_PHASE_X
BOARD_SCENE_Y = GRID_PHASE_Y - TOP_MODULE_Y / SVG_DPI * SCENE_DPI
P4_SCENE_X = BOARD_SCENE_X + P4_SVG_X / SVG_DPI * SCENE_DPI
P4_SCENE_Y = BOARD_SCENE_Y + P4_SVG_Y / SVG_DPI * SCENE_DPI

# The two 1x16 Agon harness connectors deliberately exclude physical header
# pins 33 and 34.  Their separate power wiring is outside this drawing stage.
# Do not expand either header to 17 positions: that would misrepresent the
# actual harness.
#
# In this landscape view, the even bank is above EXT1 and the odd bank below
# EXT2.  Rotating the diagram counterclockwise to the canonical portrait view
# puts the low pin numbers at the top, so pins descend from left to right here.
AGON_EVEN_START_COLUMN = 6
AGON_ODD_START_COLUMN = 4
AGON_EVEN_BOARD_ROW = "A"
AGON_ODD_BOARD_ROW = "J"
AGON_HEADER_PIN_X = 0.05 * SVG_DPI
AGON_HEADER_PIN_Y = 0.05 * SVG_DPI
AGON_HEADER_VIEW_WIDTH = 1.6 * SVG_DPI
AGON_HEADER_VIEW_HEIGHT = 0.1 * SVG_DPI

AGON_PIN_DATA = {
    "even": (
        (2, "+5V USB", "#1976d2", "#ffffff"),
        (4, "+5V", "#388e3c", "#ffffff"),
        (6, "ESP39", "#fbc02d", "#111111"),
        (8, "ESP27", "#f57c00", "#111111"),
        (10, "ESP36", "#d32f2f", "#ffffff"),
        (12, "ESP38", "#6d4c41", "#ffffff"),
        (14, "PD5 / CTS1", "#111111", "#ffffff"),
        (16, "PD7", "#ffffff", "#111111"),
        (18, "PC1", "#808080", "#ffffff"),
        (20, "PC3", "#7b1fa2", "#ffffff"),
        (22, "PC5", "#1976d2", "#ffffff"),
        (24, "PC7", "#388e3c", "#ffffff"),
        (26, "PB5", "#fbc02d", "#111111"),
        (28, "CLK", "#f57c00", "#111111"),
        (30, "SCL", "#d32f2f", "#ffffff"),
        (32, "MOSI", "#6d4c41", "#ffffff"),
    ),
    "odd": (
        (1, "VBAT", "#d32f2f", "#ffffff"),
        (3, "GND", "#808080", "#ffffff"),
        (5, "GND", "#111111", "#ffffff"),
        (7, "ESP35", "#ffffff", "#111111"),
        (9, "ESP26", "#808080", "#ffffff"),
        (11, "ESP37", "#7b1fa2", "#ffffff"),
        (13, "PD4 / RTS1", "#1976d2", "#ffffff"),
        (15, "PD6", "#388e3c", "#ffffff"),
        (17, "PC0 / RXD1", "#fbc02d", "#111111"),
        (19, "PC2 / TXD1", "#f57c00", "#111111"),
        (21, "PC4", "#d32f2f", "#ffffff"),
        (23, "PC6", "#6d4c41", "#ffffff"),
        (25, "CS", "#111111", "#ffffff"),
        (27, "MISO", "#ffffff", "#111111"),
        (29, "SDA", "#808080", "#ffffff"),
        (31, "SCK", "#7b1fa2", "#ffffff"),
    ),
}

BOARD_MODULE_ID = "agon-extender-bb1460-two-rail-scaffold-fritzing-r04"
P4_MODULE_ID = "agon-extender-olimex-esp32-p4-devkit-rev-d1-fritzing-r04"
AGON_HEADER_MODULE_IDS = {
    "even": "agon-light2-even-16-contact-header-fritzing-r02",
    "odd": "agon-light2-odd-16-contact-header-fritzing-r02",
}
AGON_LABEL_CELL_WIDTH = 0.5 * SVG_DPI
AGON_LABEL_BANK_LENGTH = 16 * PITCH
AGON_LABEL_BANK_MODULE_IDS = {
    "odd": "agon-light2-odd-pin-label-bank-fritzing-r02",
    "even": "agon-light2-even-pin-label-bank-fritzing-r02",
}
AGON_LABEL_BANK_SCENE_X = {
    "odd": BOARD_SCENE_X
    + (
        FIRST_HOLE_X
        + (AGON_ODD_START_COLUMN - 1) * PITCH
        - AGON_HEADER_PIN_X
    )
    / SVG_DPI
    * SCENE_DPI,
    "even": BOARD_SCENE_X
    + (
        FIRST_HOLE_X
        + (AGON_EVEN_START_COLUMN - 1) * PITCH
        - AGON_HEADER_PIN_X
    )
    / SVG_DPI
    * SCENE_DPI,
}
AGON_LABEL_BANK_SCENE_Y = {
    # Preserve the Author's accepted _usermod separation from the matching
    # header while reducing each label's physical depth to 0.5 inch. The even
    # bank moves outward by the added top rail's effective snapped width.
    "even": -76.5,
    "odd": 274.5,
}
SKETCH_BASENAME = "light2-extender-breadboard-scaffold"
P4_PACKAGE_BASENAME = P4_MODULE_ID
BOARD_PACKAGE_BASENAME = BOARD_MODULE_ID


def fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def xml_bytes(element: ET.Element) -> bytes:
    ET.indent(element, space="  ")
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)


def svg_header(width: float, height: float) -> list[str]:
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{fmt(width / SVG_DPI)}in" height="{fmt(height / SVG_DPI)}in" '
        f'viewBox="0 0 {fmt(width)} {fmt(height)}">'
    ]


def hole_svg(connector_id: str, x: float, y: float) -> str:
    return (
        f'<circle id="{connector_id}pin" cx="{fmt(x)}" cy="{fmt(y)}" '
        'r="1.85" fill="#202020" stroke="#7a7a7a" stroke-width="0.55"/>'
    )


def terminal_connector_id(section: str, row: str, column: int) -> str:
    return f"{section}-{row}{column}"


def rail_connector_id(location: str, row: str, column: int) -> str:
    return f"{location}-rail-{row}{column}"


def board_svg() -> bytes:
    lines = svg_header(BOARD_VIEW_WIDTH, BOARD_VIEW_HEIGHT)
    lines.append('<g id="breadboardbreadboard">')

    for y in (TOP_MODULE_Y, BOTTOM_MODULE_Y):
        lines.extend(
            [
                f'<rect x="0.5" y="{fmt(y + 0.5)}" width="467" height="96.2" '
                'rx="4" fill="#f7f7f3" stroke="#b8b8b0" stroke-width="1"/>',
                f'<rect x="4" y="{fmt(y + 45)}" width="460" height="7.2" '
                'fill="#e8e8e2"/>',
            ]
        )

    # Both BB100R strips retain their observed 0.35-inch width. Their contact
    # rows are centered, with polarity-color legends straddling the holes.
    for rail_top in RAIL_LOCATIONS.values():
        lines.append(
            f'<rect x="0.5" y="{fmt(rail_top)}" width="467" '
            f'height="{fmt(RAIL_BODY_HEIGHT)}" rx="3" fill="#fafaf6" '
            'stroke="#abab9f" stroke-width="1.2"/>'
        )
        for row, y_offset in zip(RAIL_ROWS, RAIL_LEGEND_Y_OFFSETS):
            lines.append(
                f'<line x1="8" y1="{fmt(rail_top + y_offset)}" '
                f'x2="460" y2="{fmt(rail_top + y_offset)}" '
                f'stroke="{RAIL_LEGEND_COLORS[row]}" stroke-width="1.4"/>'
            )

    for column in range(1, COLUMNS + 1):
        x = FIRST_HOLE_X + (column - 1) * PITCH
        if column == 1 or column % 5 == 0:
            for label_y in (
                TOP_MODULE_Y + 6.7,
                TOP_MODULE_Y + 49.9,
                BOTTOM_MODULE_Y + 49.9,
                ASSEMBLY_HEIGHT - 3.2,
            ):
                lines.append(
                    f'<text x="{fmt(x)}" y="{fmt(label_y)}" font-size="3.8" '
                    f'text-anchor="middle" fill="#555">{column}</text>'
                )

        for section, rows in (("top", TOP_ROW_Y), ("bottom", BOTTOM_ROW_Y)):
            for row, y in rows.items():
                lines.append(hole_svg(terminal_connector_id(section, row, column), x, y))

    for location, rail_top in RAIL_LOCATIONS.items():
        for row, y_offset in zip(RAIL_ROWS, RAIL_HOLE_Y_OFFSETS):
            for column in RAIL_COLUMNS:
                x = FIRST_HOLE_X + (column - 1) * PITCH
                lines.append(
                    hole_svg(
                        rail_connector_id(location, row, column),
                        x,
                        rail_top + y_offset,
                    )
                )

    lines.append("</g></svg>")
    return ("\n".join(lines) + "\n").encode()


def add_part_views(module: ET.Element, image_name: str, layer: str) -> None:
    views = ET.SubElement(module, "views")
    for view_name in ("iconView", "breadboardView", "schematicView", "pcbView"):
        view = ET.SubElement(views, view_name)
        layers = ET.SubElement(view, "layers", {"image": f"breadboard/{image_name}"})
        ET.SubElement(layers, "layer", {"layerId": layer})


def add_connector(
    connectors: ET.Element,
    connector_id: str,
    name: str,
    connector_type: str,
    layer: str,
) -> None:
    connector = ET.SubElement(
        connectors,
        "connector",
        {"id": connector_id, "name": name, "type": connector_type},
    )
    ET.SubElement(connector, "description").text = name
    views = ET.SubElement(connector, "views")
    for view_name in ("breadboardView", "schematicView", "pcbView"):
        view = ET.SubElement(views, view_name)
        ET.SubElement(
            view,
            "p",
            {"layer": layer, "svgId": f"{connector_id}pin"},
        )
    ET.SubElement(connector, "erc", {"ignore": "always"})


def board_fzp() -> bytes:
    module = ET.Element(
        "module",
        {
            "moduleId": BOARD_MODULE_ID,
            "referenceFile": f"{BOARD_MODULE_ID}.fzp",
            "fritzingVersion": "1.0.1",
        },
    )
    ET.SubElement(module, "version").text = "2"
    ET.SubElement(module, "author").text = "Agon Extender Project"
    ET.SubElement(module, "title").text = "BB1460 two-rail scaffold"
    ET.SubElement(module, "label").text = "Breadboard"
    tags = ET.SubElement(module, "tags")
    for tag in ("breadboard", "BB1460", "BB630", "BB100R", "custom"):
        ET.SubElement(tags, "tag").text = tag
    properties = ET.SubElement(module, "properties")
    ET.SubElement(properties, "property", {"name": "family"}).text = "Breadboard"
    ET.SubElement(properties, "property", {"name": "size"}).text = "BB1460 custom"
    ET.SubElement(module, "taxonomy").text = "prototyping.breadboard.custom.bb1460"
    ET.SubElement(module, "description").text = (
        "Mechanical scaffold: two BB630 terminal areas with top and center "
        "BB100R strips; generated for SETUP-006.3 and not an electrical design."
    )
    image_name = f"{BOARD_MODULE_ID}.svg"
    add_part_views(module, image_name, "breadboardbreadboard")

    connectors = ET.SubElement(module, "connectors", {"ignoreTerminalPoints": "true"})
    for section in ("top", "bottom"):
        for column in range(1, COLUMNS + 1):
            for row in "ABCDEFGHIJ":
                connector_id = terminal_connector_id(section, row, column)
                add_connector(
                    connectors,
                    connector_id,
                    f"{section.title()} BB630 {row}{column}",
                    "female",
                    "breadboardbreadboard",
                )
    for location in RAIL_LOCATIONS:
        for row in RAIL_ROWS:
            for column in RAIL_COLUMNS:
                connector_id = rail_connector_id(location, row, column)
                add_connector(
                    connectors,
                    connector_id,
                    f"{location.title()} BB100R {row} rail, position {column}",
                    "female",
                    "breadboardbreadboard",
                )

    buses = ET.SubElement(module, "buses")
    for section in ("top", "bottom"):
        for column in range(1, COLUMNS + 1):
            for row_group in ("ABCDE", "FGHIJ"):
                bus = ET.SubElement(
                    buses,
                    "bus",
                    {"id": f"{section}-{row_group[0]}{row_group[-1]}-{column}"},
                )
                for row in row_group:
                    ET.SubElement(
                        bus,
                        "nodeMember",
                        {"connectorId": terminal_connector_id(section, row, column)},
                    )
    for location in RAIL_LOCATIONS:
        for row in RAIL_ROWS:
            bus = ET.SubElement(
                buses,
                "bus",
                {"id": f"{location}-rail-{row}"},
            )
            for column in RAIL_COLUMNS:
                ET.SubElement(
                    bus,
                    "nodeMember",
                    {"connectorId": rail_connector_id(location, row, column)},
                )
    return xml_bytes(module)


P4_PIN_NAMES = {
    "EXT1": (
        "+3.3V", "GND", "GPIO2 / USER_LED", "GPIO3 / SD_DET",
        "GPIO4 / SPI_SCK", "GPIO5 / SPI_CS", "GPIO6", "GPIO7 / I2C_SDA",
        "GPIO8 / I2C_SCL", "GPIO9", "GPIO10", "GPIO11", "GPIO12",
        "GPIO13", "GPIO14", "GPIO15", "GPIO17", "GPIO16", "GPIO18", "GPIO19",
    ),
    "EXT2": (
        "+5V", "GND", "GPIO54 / SPI_RX", "GPIO53 / SPI_TX", "GPIO48",
        "GPIO47", "GPIO46", "GPIO33", "GPIO32", "GPIO23", "GPIO22",
        "GPIO21", "GPIO20", "ESP_EN", "GND", "GPIO27 / USB1P1_1P",
        "GPIO26 / USB1P1_1N", "GND", "USB_DP", "USB_DN",
    ),
}


def p4_connector_id(header: str, pin: int) -> str:
    return f"{header.lower()}-pin{pin}"


def p4_svg() -> bytes:
    lines = svg_header(P4_VIEW_WIDTH, P4_VIEW_HEIGHT)
    lines.append('<g id="breadboard">')
    lines.extend(
        [
            f'<rect x="{fmt(P4_BODY_X)}" y="{fmt(P4_BODY_Y)}" '
            f'width="{fmt(P4_BOARD_LENGTH)}" height="{fmt(P4_BODY_HEIGHT)}" '
            'rx="3" fill="#c5222a" '
            'stroke="#7e1118" stroke-width="1"/>',
            f'<rect x="0.5" y="{fmt(P4_BODY_CENTER_Y - 8)}" width="{fmt(P4_BODY_X + 18)}" '
            'height="16" rx="2" fill="#b7b9bc" stroke="#62666a"/>',
            f'<text x="{fmt(P4_BODY_X + 18)}" '
            f'y="{fmt(P4_BODY_CENTER_Y)}" '
            'font-size="4.2" font-weight="bold" text-anchor="middle" '
            'dominant-baseline="middle" fill="#fff" '
            f'transform="rotate(90 {fmt(P4_BODY_X + 18)} '
            f'{fmt(P4_BODY_CENTER_Y)})">OLIMEX P4 D1</text>',
            f'<rect x="{fmt(P4_BODY_X + P4_BOARD_LENGTH - 25)}" '
            f'y="{fmt(P4_BODY_CENTER_Y - 22.5)}" width="29" '
            'height="45" rx="2" fill="#adadad" stroke="#505050"/>',
            f'<text x="{fmt(P4_BODY_X + P4_BOARD_LENGTH - 10.5)}" '
            f'y="{fmt(P4_BODY_CENTER_Y + 2)}" '
            'font-size="5" text-anchor="middle" fill="#222" '
            'transform="rotate(90 '
            f'{fmt(P4_BODY_X + P4_BOARD_LENGTH - 10.5)} '
            f'{fmt(P4_BODY_CENTER_Y + 2)})">ETHERNET</text>',
            '<text x="5" y="18" font-size="4.5" fill="#222">USB</text>',
            f'<text x="1.5" y="{fmt(P4_VIEW_HEIGHT - 5)}" font-size="3.8" '
            'fill="#333">pin 1 / column 1 end</text>',
        ]
    )
    for header, y in (("EXT1", P4_EXT1_Y), ("EXT2", P4_EXT2_Y)):
        lines.append(
            f'<rect x="{fmt(P4_PIN1_X - 3.4)}" y="{fmt(y - 3.4)}" '
            f'width="{fmt(19 * PITCH + 6.8)}" height="6.8" '
            'fill="#272727" stroke="#111" stroke-width="0.5"/>'
        )
        for pin in range(1, 21):
            x = P4_PIN1_X + (pin - 1) * PITCH
            connector_id = p4_connector_id(header, pin)
            lines.append(
                f'<rect id="{connector_id}pin" x="{fmt(x - 1.65)}" '
                f'y="{fmt(y - 1.65)}" width="3.3" height="3.3" '
                'fill="#d4b04c" stroke="#684f14" stroke-width="0.45"/>'
            )
            signal = P4_PIN_NAMES[header][pin - 1]
            label_y = y + (5.2 if header == "EXT1" else -5.2)
            text_anchor = "start" if header == "EXT1" else "end"
            lines.append(
                f'<text x="{fmt(x)}" y="{fmt(label_y)}" '
                f'font-size="2.65" text-anchor="{text_anchor}" '
                'fill="#fff" '
                f'transform="rotate(90 {fmt(x)} {fmt(label_y)})">'
                f'{pin} {signal}</text>'
            )
        header_label_x = P4_BODY_X + 7
        header_label_y = y + (7.5 if header == "EXT1" else -4.8)
        lines.append(
            f'<text x="{fmt(header_label_x)}" y="{fmt(header_label_y)}" '
            f'font-size="3.5" font-weight="bold" text-anchor="middle" '
            f'fill="#fff">{header}</text>'
        )
    lines.append("</g></svg>")
    return ("\n".join(lines) + "\n").encode()


def p4_fzp() -> bytes:
    module = ET.Element(
        "module",
        {
            "moduleId": P4_MODULE_ID,
            "referenceFile": f"{P4_MODULE_ID}.fzp",
            "fritzingVersion": "1.0.1",
        },
    )
    ET.SubElement(module, "version").text = "4"
    ET.SubElement(module, "author").text = "Agon Extender Project"
    ET.SubElement(module, "title").text = "Olimex ESP32-P4-DevKit Rev D1"
    ET.SubElement(module, "label").text = "EDP"
    tags = ET.SubElement(module, "tags")
    for tag in ("Olimex", "ESP32-P4", "DevKit", "custom"):
        ET.SubElement(tags, "tag").text = tag
    properties = ET.SubElement(module, "properties")
    ET.SubElement(properties, "property", {"name": "family"}).text = "ESP32-P4 DevKit"
    ET.SubElement(properties, "property", {"name": "revision"}).text = "D1"
    ET.SubElement(module, "taxonomy").text = "microcontroller.esp32-p4.olimex-devkit"
    ET.SubElement(module, "description").text = (
        "Diagrammatic Rev D1 breadboard representation generated from official "
        "Olimex EXT1/EXT2 geometry for SETUP-006.3; the rendered body is "
        "deliberately cropped to expose adjacent breadboard sockets."
    )
    image_name = f"{P4_MODULE_ID}.svg"
    # `breadboardbreadboard` is Fritzing's special always-underneath layer and
    # is reserved for the breadboard itself.  The P4 must be a normal
    # `breadboard` part so it renders above the sockets into which it is fitted.
    add_part_views(module, image_name, "breadboard")
    connectors = ET.SubElement(module, "connectors")
    for header in ("EXT1", "EXT2"):
        for pin, signal in enumerate(P4_PIN_NAMES[header], start=1):
            add_connector(
                connectors,
                p4_connector_id(header, pin),
                f"{header} pin {pin} — {signal}",
                "male",
                "breadboard",
            )
    return xml_bytes(module)


def agon_header_pin_sequence(bank: str) -> tuple[tuple[int, str, str, str], ...]:
    """Return left-to-right pin order for the landscape wiring diagram."""
    return tuple(reversed(AGON_PIN_DATA[bank]))


def agon_header_connector_id(bank: str, pin: int) -> str:
    return f"agon-{bank}-pin{pin}"


def agon_header_pin_y(bank: str) -> float:
    return AGON_HEADER_PIN_Y


def agon_header_start_column(bank: str) -> int:
    return AGON_EVEN_START_COLUMN if bank == "even" else AGON_ODD_START_COLUMN


def agon_header_board_row(bank: str) -> tuple[str, str]:
    if bank == "even":
        return "top", AGON_EVEN_BOARD_ROW
    return "bottom", AGON_ODD_BOARD_ROW


def agon_header_svg_position(bank: str) -> tuple[float, float]:
    section, row = agon_header_board_row(bank)
    rows = TOP_ROW_Y if section == "top" else BOTTOM_ROW_Y
    first_board_x = FIRST_HOLE_X + (agon_header_start_column(bank) - 1) * PITCH
    return first_board_x - AGON_HEADER_PIN_X, rows[row] - agon_header_pin_y(bank)


def agon_header_scene_position(bank: str) -> tuple[float, float]:
    x, y = agon_header_svg_position(bank)
    return (
        BOARD_SCENE_X + x / SVG_DPI * SCENE_DPI,
        BOARD_SCENE_Y + y / SVG_DPI * SCENE_DPI,
    )


def agon_header_svg(bank: str) -> bytes:
    """Render one compact, label-free Agon harness contact block."""
    pin_y = agon_header_pin_y(bank)
    lines = svg_header(AGON_HEADER_VIEW_WIDTH, AGON_HEADER_VIEW_HEIGHT)
    lines.append('<g id="breadboard">')
    lines.append(
        f'<rect x="0.2" y="{fmt(pin_y - 3.5)}" '
        f'width="{fmt(15 * PITCH + 7)}" height="7" rx="1" '
        'fill="#252525" stroke="#080808" stroke-width="0.6"/>'
    )
    for index, (pin, _signal, fill, _text_color) in enumerate(
        agon_header_pin_sequence(bank)
    ):
        x = AGON_HEADER_PIN_X + index * PITCH
        connector_id = agon_header_connector_id(bank, pin)
        lines.append(
            f'<rect id="{connector_id}pin" x="{fmt(x - 2.55)}" '
            f'y="{fmt(pin_y - 2.55)}" width="5.1" height="5.1" rx="0.5" '
            f'fill="{fill}" stroke="#333" stroke-width="0.55"/>'
        )
    lines.append("</g></svg>")
    return ("\n".join(lines) + "\n").encode()


def agon_header_fzp(bank: str) -> bytes:
    module_id = AGON_HEADER_MODULE_IDS[bank]
    module = ET.Element(
        "module",
        {
            "moduleId": module_id,
            "referenceFile": f"{module_id}.fzp",
            "fritzingVersion": "1.0.1",
        },
    )
    ET.SubElement(module, "version").text = "2"
    ET.SubElement(module, "author").text = "Agon Extender Project"
    ET.SubElement(module, "title").text = f"Agon Light 2 {bank} 16-contact header"
    ET.SubElement(module, "label").text = f"AGON-{bank.upper()}"
    tags = ET.SubElement(module, "tags")
    for tag in ("Agon Light 2", "header", "1x16", bank, "custom"):
        ET.SubElement(tags, "tag").text = tag
    properties = ET.SubElement(module, "properties")
    ET.SubElement(properties, "property", {"name": "family"}).text = (
        "Agon Light 2 harness header"
    )
    ET.SubElement(properties, "property", {"name": "positions"}).text = "16"
    ET.SubElement(module, "taxonomy").text = f"connector.header.1x16.agon.{bank}"
    ET.SubElement(module, "description").text = (
        f"Label-free Agon Light 2 {bank} 16-contact harness bank. Physical "
        "pins 33 and 34 are intentionally excluded; their separate wiring is "
        "not drawn. Labels are separate movable diagram objects."
    )
    image_name = f"{module_id}.svg"
    add_part_views(module, image_name, "breadboard")
    connectors = ET.SubElement(module, "connectors")
    for pin, signal, _fill, _text_color in agon_header_pin_sequence(bank):
        add_connector(
            connectors,
            agon_header_connector_id(bank, pin),
            f"Agon pin {pin} — {signal}",
            "male",
            "breadboard",
        )
    return xml_bytes(module)


def agon_label_bank_svg(bank: str) -> bytes:
    """Render one independently movable 16-label bank on 0.1-inch pitch."""
    lines = svg_header(AGON_LABEL_BANK_LENGTH, AGON_LABEL_CELL_WIDTH)
    lines.append('<g id="breadboard">')
    # Rotate the original legacy-style vertical bank clockwise into its normal
    # horizontal breadboard orientation.  Baking this transform into the SVG
    # avoids Fritzing's unstable interactive rotation and snap calculations.
    lines.append(
        f'<g transform="matrix(0 1 -1 0 {fmt(AGON_LABEL_BANK_LENGTH)} 0)">'
    )
    for row, (pin, name, fill, text_color) in enumerate(AGON_PIN_DATA[bank]):
        y = row * PITCH
        lines.extend(
            [
                f'<rect x="0.2" y="{fmt(y + 0.2)}" '
                f'width="{fmt(AGON_LABEL_CELL_WIDTH - 0.4)}" '
                f'height="{fmt(PITCH - 0.4)}" rx="1" fill="{fill}" '
                'stroke="#333333" stroke-width="0.55"/>',
                # Fritzing 1.0.1 mangles adjacent tspans in custom SVGs.
                # Keep each complete label in one plain text node.
                f'<text x="2.3" y="{fmt(y + 5.1)}" '
                'font-family="DejaVu Sans, sans-serif" font-size="4" '
                f'text-anchor="start" fill="{text_color}">{pin} {name}</text>',
            ]
        )
    lines.append('</g>')
    # Fritzing 1.0.1 mis-resolves connector-free bundled custom parts and may
    # render the preceding part's artwork instead.  This invisible, unconnected
    # placement anchor exists solely to satisfy that inherited loader behavior.
    lines.append(
        '<circle id="connector0pin" cx="3.6" cy="3.6" r="0.01" '
        'fill="none" stroke="none"/>'
    )
    lines.append('</g></svg>')
    return ("\n".join(lines) + "\n").encode()


def agon_label_bank_fzp(bank: str) -> bytes:
    module_id = AGON_LABEL_BANK_MODULE_IDS[bank]
    module = ET.Element(
        "module",
        {
            "moduleId": module_id,
            "referenceFile": f"{module_id}.fzp",
            "fritzingVersion": "1.0.1",
        },
    )
    ET.SubElement(module, "version").text = "2"
    ET.SubElement(module, "author").text = "Agon Extender Project"
    ET.SubElement(module, "title").text = f"Agon Light 2 {bank} pin-label bank"
    ET.SubElement(module, "label").text = f"AGON {bank.upper()} PIN LABELS"
    tags = ET.SubElement(module, "tags")
    for tag in ("Agon Light 2", "pin label", "movable", "custom"):
        ET.SubElement(tags, "tag").text = tag
    properties = ET.SubElement(module, "properties")
    ET.SubElement(properties, "property", {"name": "family"}).text = (
        "Agon Light 2 movable pin-label bank"
    )
    ET.SubElement(module, "taxonomy").text = "annotation.pin-label.agon-light2"
    ET.SubElement(module, "description").text = (
        f"One independently movable, color-coded {bank} bank containing "
        "exactly 16 represented Agon Light 2 pin labels on 0.1-inch row pitch; "
        "contains no Extender-specific functional mappings."
    )
    image_name = f"{module_id}.svg"
    add_part_views(module, image_name, "breadboard")
    connectors = ET.SubElement(module, "connectors")
    add_connector(
        connectors,
        "connector0",
        "Non-electrical Fritzing placement anchor",
        "male",
        "breadboard",
    )
    return xml_bytes(module)


def add_sketch_connector_connections(
    view: ET.Element,
    connections: dict[str, tuple[str, str, str]],
    connector_layer: str,
) -> None:
    connectors = ET.SubElement(view, "connectors")
    for connector_id, (peer_id, peer_model, peer_layer) in sorted(connections.items()):
        connector = ET.SubElement(
            connectors,
            "connector",
            {"connectorId": connector_id, "layer": connector_layer},
        )
        ET.SubElement(connector, "geometry", {"x": "0", "y": "0"})
        connects = ET.SubElement(connector, "connects")
        ET.SubElement(
            connects,
            "connect",
            {
                "connectorId": peer_id,
                "modelIndex": peer_model,
                "layer": peer_layer,
            },
        )


def sketch_fz() -> bytes:
    module = ET.Element("module", {"fritzingVersion": "1.0.1", "icon": ".png"})
    ET.SubElement(module, "project_properties")
    views = ET.SubElement(module, "views")
    ET.SubElement(
        views,
        "view",
        {
            "name": "breadboardView",
            "backgroundColor": "#ffffff",
            "gridSize": "0.1in",
            "showGrid": "1",
            "alignToGrid": "1",
            "viewFromBelow": "0",
        },
    )
    for name, grid in (("schematicView", "0.1in"), ("pcbView", "0.05in")):
        ET.SubElement(
            views,
            "view",
            {
                "name": name,
                "backgroundColor": "#ffffff",
                "gridSize": grid,
                "showGrid": "1",
                "alignToGrid": "1",
                "viewFromBelow": "0",
            },
        )

    instances = ET.SubElement(module, "instances")
    board_instance = ET.SubElement(
        instances,
        "instance",
        {
            "moduleIdRef": BOARD_MODULE_ID,
            "modelIndex": "1",
            "path": f"part.{BOARD_MODULE_ID}.fzp",
        },
    )
    ET.SubElement(board_instance, "title").text = "BB1460TwoRail1"
    board_views = ET.SubElement(board_instance, "views")
    board_breadboard = ET.SubElement(
        board_views,
        "breadboardView",
        {"layer": "breadboardbreadboard"},
    )
    ET.SubElement(
        board_breadboard,
        "geometry",
        {"z": "1", "x": fmt(BOARD_SCENE_X), "y": fmt(BOARD_SCENE_Y)},
    )

    board_connections: dict[str, tuple[str, str, str]] = {}
    p4_connections: dict[str, tuple[str, str, str]] = {}
    agon_header_connections: dict[str, dict[str, tuple[str, str, str]]] = {
        "even": {},
        "odd": {},
    }
    for header, section, row in (
        ("EXT1", "top", EXT1_BOARD_ROW),
        ("EXT2", "bottom", EXT2_BOARD_ROW),
    ):
        for pin in range(1, 21):
            board_id = terminal_connector_id(section, row, pin)
            p4_id = p4_connector_id(header, pin)
            board_connections[board_id] = (p4_id, "2", "breadboard")
            p4_connections[p4_id] = (board_id, "1", "breadboardbreadboard")

    for bank, model_index in (("even", "3"), ("odd", "4")):
        section, row = agon_header_board_row(bank)
        for offset, (pin, _signal, _fill, _text_color) in enumerate(
            agon_header_pin_sequence(bank)
        ):
            column = agon_header_start_column(bank) + offset
            board_id = terminal_connector_id(section, row, column)
            header_id = agon_header_connector_id(bank, pin)
            board_connections[board_id] = (header_id, model_index, "breadboard")
            agon_header_connections[bank][header_id] = (
                board_id,
                "1",
                "breadboardbreadboard",
            )

    add_sketch_connector_connections(
        board_breadboard, board_connections, "breadboardbreadboard"
    )
    for view_name, x in (("schematicView", "0"), ("pcbView", "0")):
        view = ET.SubElement(board_views, view_name, {"layer": "breadboardbreadboard"})
        ET.SubElement(view, "geometry", {"z": "1", "x": x, "y": "400"})

    p4_instance = ET.SubElement(
        instances,
        "instance",
        {
            "moduleIdRef": P4_MODULE_ID,
            "modelIndex": "2",
            "path": f"part.{P4_MODULE_ID}.fzp",
        },
    )
    ET.SubElement(p4_instance, "title").text = "P4DevKit1"
    p4_views = ET.SubElement(p4_instance, "views")
    p4_breadboard = ET.SubElement(
        p4_views,
        "breadboardView",
        {"layer": "breadboard"},
    )
    ET.SubElement(
        p4_breadboard,
        "geometry",
        {"z": "2", "x": fmt(P4_SCENE_X), "y": fmt(P4_SCENE_Y)},
    )
    add_sketch_connector_connections(p4_breadboard, p4_connections, "breadboard")
    for view_name in ("schematicView", "pcbView"):
        view = ET.SubElement(p4_views, view_name, {"layer": "breadboard"})
        ET.SubElement(view, "geometry", {"z": "2", "x": "250", "y": "400"})

    for bank, model_index, z in (("even", "3", "3"), ("odd", "4", "3")):
        module_id = AGON_HEADER_MODULE_IDS[bank]
        header_instance = ET.SubElement(
            instances,
            "instance",
            {
                "moduleIdRef": module_id,
                "modelIndex": model_index,
                "path": f"part.{module_id}.fzp",
            },
        )
        ET.SubElement(header_instance, "title").text = f"Agon{bank.title()}Header1"
        header_views = ET.SubElement(header_instance, "views")
        header_breadboard = ET.SubElement(
            header_views,
            "breadboardView",
            {"layer": "breadboard"},
        )
        scene_x, scene_y = agon_header_scene_position(bank)
        ET.SubElement(
            header_breadboard,
            "geometry",
            {"z": z, "x": fmt(scene_x), "y": fmt(scene_y)},
        )
        add_sketch_connector_connections(
            header_breadboard,
            agon_header_connections[bank],
            "breadboard",
        )
        for view_name in ("schematicView", "pcbView"):
            view = ET.SubElement(header_views, view_name, {"layer": "breadboard"})
            ET.SubElement(view, "geometry", {"z": z, "x": "500", "y": "400"})

    for bank, model_index in (("odd", "5"), ("even", "6")):
        module_id = AGON_LABEL_BANK_MODULE_IDS[bank]
        label_instance = ET.SubElement(
            instances,
            "instance",
            {
                "moduleIdRef": module_id,
                "modelIndex": model_index,
                "path": f"part.{module_id}.fzp",
            },
        )
        ET.SubElement(label_instance, "title").text = (
            f"Agon{bank.title()}PinLabelBank1"
        )
        label_views = ET.SubElement(label_instance, "views")
        breadboard = ET.SubElement(
            label_views,
            "breadboardView",
            {"layer": "breadboard"},
        )
        ET.SubElement(
            breadboard,
            "geometry",
            {
                "z": "4",
                "x": fmt(AGON_LABEL_BANK_SCENE_X[bank]),
                "y": fmt(AGON_LABEL_BANK_SCENE_Y[bank]),
            },
        )
        for view_name in ("schematicView", "pcbView"):
            view = ET.SubElement(label_views, view_name, {"layer": "breadboard"})
            ET.SubElement(
                view,
                "geometry",
                {"z": "4", "x": str(600 + int(model_index) * 100), "y": "400"},
            )

    return xml_bytes(module)


def preview_svg(
    board: bytes,
    p4: bytes,
    agon_headers: dict[str, bytes],
    agon_label_banks: dict[str, bytes],
) -> bytes:
    board_root = ET.fromstring(board)
    p4_root = ET.fromstring(p4)
    header_roots = {
        bank: ET.fromstring(image) for bank, image in agon_headers.items()
    }
    label_roots = {
        bank: ET.fromstring(image) for bank, image in agon_label_banks.items()
    }
    margin = 70
    right_margin = 70
    width = BOARD_WIDTH + margin + right_margin
    height = ASSEMBLY_HEIGHT + 2 * margin
    root = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": f"{fmt(width / SVG_DPI)}in",
            "height": f"{fmt(height / SVG_DPI)}in",
            "viewBox": f"0 0 {fmt(width)} {fmt(height)}",
        },
    )
    ET.SubElement(root, "rect", {"width": "100%", "height": "100%", "fill": "#ffffff"})
    title = ET.SubElement(
        root,
        "text",
        {"x": "40", "y": "18", "font-size": "8", "font-weight": "bold", "fill": "#222"},
    )
    title.text = "SETUP-006.3 — partial harness wiring diagram"
    board_group = ET.SubElement(
        root, "g", {"transform": f"translate({margin} {margin})"}
    )
    for child in list(board_root):
        board_group.append(child)
    p4_group = ET.SubElement(
        root,
        "g",
        {
            "transform":
                f"translate({fmt(margin + P4_SVG_X)} {fmt(margin + P4_SVG_Y)})"
        },
    )
    for child in list(p4_root):
        p4_group.append(child)

    for bank, header_root in header_roots.items():
        x, y = agon_header_svg_position(bank)
        group = ET.SubElement(
            root,
            "g",
            {"transform": f"translate({fmt(margin + x)} {fmt(margin + y)})"},
        )
        for child in list(header_root):
            group.append(child)

    for bank, label_root in label_roots.items():
        label_x = (
            margin
            + (AGON_LABEL_BANK_SCENE_X[bank] - BOARD_SCENE_X)
            / SCENE_DPI
            * SVG_DPI
        )
        label_y = (
            margin
            + (AGON_LABEL_BANK_SCENE_Y[bank] - BOARD_SCENE_Y)
            / SCENE_DPI
            * SVG_DPI
        )
        label_group = ET.SubElement(
            root,
            "g",
            {"transform": f"translate({fmt(label_x)} {fmt(label_y)})"},
        )
        for child in list(label_root):
            label_group.append(child)

    return xml_bytes(root)


def build_files() -> dict[str, bytes]:
    board_image = board_svg()
    p4_image = p4_svg()
    header_images = {bank: agon_header_svg(bank) for bank in ("even", "odd")}
    label_bank_images = {
        bank: agon_label_bank_svg(bank) for bank in ("odd", "even")
    }
    files = {
        f"{SKETCH_BASENAME}.fz": sketch_fz(),
        f"part.{BOARD_MODULE_ID}.fzp": board_fzp(),
        f"part.{P4_MODULE_ID}.fzp": p4_fzp(),
        f"svg.breadboard.{BOARD_MODULE_ID}.svg": board_image,
        f"svg.breadboard.{P4_MODULE_ID}.svg": p4_image,
    }
    for bank in ("even", "odd"):
        module_id = AGON_HEADER_MODULE_IDS[bank]
        files[f"part.{module_id}.fzp"] = agon_header_fzp(bank)
        files[f"svg.breadboard.{module_id}.svg"] = header_images[bank]
    for bank in ("odd", "even"):
        module_id = AGON_LABEL_BANK_MODULE_IDS[bank]
        files[f"part.{module_id}.fzp"] = agon_label_bank_fzp(bank)
        files[f"svg.breadboard.{module_id}.svg"] = label_bank_images[bank]
    files[f"{SKETCH_BASENAME}.svg"] = preview_svg(
        board_image, p4_image, header_images, label_bank_images
    )
    return files


def zip_bytes(files: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(name for name in files if not name.endswith(".svg") or name.startswith("svg.")):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    return stream.getvalue()


def p4_package_bytes(files: dict[str, bytes]) -> bytes:
    """Return a deterministic Fritzing bundled-part archive for My Parts."""
    members = {
        f"part.{P4_MODULE_ID}.fzp": files[f"part.{P4_MODULE_ID}.fzp"],
        f"svg.breadboard.{P4_MODULE_ID}.svg": files[
            f"svg.breadboard.{P4_MODULE_ID}.svg"
        ],
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(
        stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, members[name])
    return stream.getvalue()


def board_package_bytes(files: dict[str, bytes]) -> bytes:
    """Return the accepted composite breadboard as a deterministic part."""
    members = {
        f"part.{BOARD_MODULE_ID}.fzp": files[f"part.{BOARD_MODULE_ID}.fzp"],
        f"svg.breadboard.{BOARD_MODULE_ID}.svg": files[
            f"svg.breadboard.{BOARD_MODULE_ID}.svg"
        ],
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(
        stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, members[name])
    return stream.getvalue()


def validate(
    files: dict[str, bytes],
    archive_bytes: bytes,
    p4_archive_bytes: bytes,
    board_archive_bytes: bytes,
) -> None:
    for name, data in files.items():
        if name.endswith((".fz", ".fzp", ".svg")):
            ET.fromstring(data)

    board_root = ET.fromstring(files[f"part.{BOARD_MODULE_ID}.fzp"])
    p4_root = ET.fromstring(files[f"part.{P4_MODULE_ID}.fzp"])
    header_roots = {
        bank: ET.fromstring(files[f"part.{AGON_HEADER_MODULE_IDS[bank]}.fzp"])
        for bank in ("even", "odd")
    }
    board_connectors = board_root.findall("./connectors/connector")
    p4_connectors = p4_root.findall("./connectors/connector")
    header_connectors = {
        bank: root.findall("./connectors/connector")
        for bank, root in header_roots.items()
    }
    expected_board_connectors = (
        2 * COLUMNS * 10
        + len(RAIL_LOCATIONS) * len(RAIL_ROWS) * len(RAIL_COLUMNS)
    )
    assert len(board_connectors) == expected_board_connectors
    assert expected_board_connectors == 1460
    assert len(p4_connectors) == 40
    assert all(len(connectors) == 16 for connectors in header_connectors.values())
    assert len({item.attrib["id"] for item in board_connectors}) == len(board_connectors)
    assert len({item.attrib["id"] for item in p4_connectors}) == len(p4_connectors)
    for bank, connectors in header_connectors.items():
        connector_ids = {item.attrib["id"] for item in connectors}
        expected_ids = {
            agon_header_connector_id(bank, pin)
            for pin, _signal, _fill, _text_color in AGON_PIN_DATA[bank]
        }
        assert connector_ids == expected_ids
        # Pins 33 and 34 are never contacts in either 1x16 harness connector.
        assert all("pin33" not in item and "pin34" not in item for item in connector_ids)
        expected_names = {
            agon_header_connector_id(bank, pin): f"Agon pin {pin} — {name}"
            for pin, name, _fill, _text_color in AGON_PIN_DATA[bank]
        }
        assert {
            item.attrib["id"]: item.attrib["name"] for item in connectors
        } == expected_names
        header_image = ET.fromstring(
            files[f"svg.breadboard.{AGON_HEADER_MODULE_IDS[bank]}.svg"]
        )
        assert all(not item.tag.endswith("text") for item in header_image.iter())

    board_image = ET.fromstring(files[f"svg.breadboard.{BOARD_MODULE_ID}.svg"])
    board_text = [
        item for item in board_image.iter() if item.tag.endswith("text")
    ]
    assert all("CENTER GROOVE" not in (item.text or "") for item in board_text)
    expected_index_columns = {1, *range(5, 61, 5)}
    expected_index_y = {
        TOP_MODULE_Y + 6.7,
        TOP_MODULE_Y + 49.9,
        BOTTOM_MODULE_Y + 49.9,
        ASSEMBLY_HEIGHT - 3.2,
    }
    index_text = [
        item for item in board_text if (item.text or "").isdigit()
    ]
    assert len(index_text) == len(expected_index_columns) * len(expected_index_y)
    assert {int(item.text or "0") for item in index_text} == expected_index_columns
    assert {
        round(float(item.attrib["y"]), 3) for item in index_text
    } == {round(value, 3) for value in expected_index_y}

    rail_legends = [
        item for item in board_image.iter() if item.tag.endswith("line")
    ]
    assert len(rail_legends) == len(RAIL_LOCATIONS) * len(RAIL_ROWS)
    for rail_top in RAIL_LOCATIONS.values():
        for row, y_offset in zip(RAIL_ROWS, RAIL_LEGEND_Y_OFFSETS):
            matches = [
                item
                for item in rail_legends
                if abs(float(item.attrib["y1"]) - (rail_top + y_offset)) < 0.001
            ]
            assert len(matches) == 1
            assert matches[0].attrib["stroke"] == RAIL_LEGEND_COLORS[row]

    rail_holes = {
        item.attrib["id"]: (float(item.attrib["cx"]), float(item.attrib["cy"]))
        for item in board_image.iter()
        if item.tag.endswith("circle")
        and item.attrib.get("id", "").startswith(("top-rail-", "center-rail-"))
    }
    assert len(rail_holes) == 200
    for location, rail_top in RAIL_LOCATIONS.items():
        for row, y_offset in zip(RAIL_ROWS, RAIL_HOLE_Y_OFFSETS):
            for column in RAIL_COLUMNS:
                connector_id = rail_connector_id(location, row, column)
                _x, y = rail_holes[f"{connector_id}pin"]
                assert abs(y - (rail_top + y_offset)) < 0.001
        rail_center = rail_top + RAIL_BODY_HEIGHT / 2.0
        assert abs(
            sum(rail_top + offset for offset in RAIL_HOLE_Y_OFFSETS) / 2.0
            - rail_center
        ) < 0.001
        assert rail_top + RAIL_LEGEND_Y_OFFSETS[0] < rail_top + RAIL_HOLE_Y_OFFSETS[0]
        assert rail_top + RAIL_LEGEND_Y_OFFSETS[1] > rail_top + RAIL_HOLE_Y_OFFSETS[1]

    all_pin_data = {
        pin: (name, fill, text_color)
        for bank in ("odd", "even")
        for pin, name, fill, text_color in AGON_PIN_DATA[bank]
    }
    assert set(all_pin_data) == set(range(1, 33))
    for bank in ("odd", "even"):
        module_id = AGON_LABEL_BANK_MODULE_IDS[bank]
        label_part = ET.fromstring(files[f"part.{module_id}.fzp"])
        label_connectors = label_part.findall("./connectors/connector")
        assert len(label_connectors) == 1
        assert label_connectors[0].attrib == {
            "id": "connector0",
            "name": "Non-electrical Fritzing placement anchor",
            "type": "male",
        }
        label_image = ET.fromstring(files[f"svg.breadboard.{module_id}.svg"])
        assert label_image.attrib["width"] == "1.6in"
        assert label_image.attrib["height"] == "0.5in"
        texts = [item for item in label_image.iter() if item.tag.endswith("text")]
        rectangles = [
            item for item in label_image.iter() if item.tag.endswith("rect")
        ]
        anchor_pins = [
            item
            for item in label_image.iter()
            if item.attrib.get("id") == "connector0pin"
        ]
        assert len(anchor_pins) == 1
        assert anchor_pins[0].attrib["fill"] == "none"
        assert anchor_pins[0].attrib["stroke"] == "none"
        transforms = [
            item.attrib["transform"]
            for item in label_image.iter()
            if "transform" in item.attrib
        ]
        assert transforms == ["matrix(0 1 -1 0 115.2 0)"]
        expected_labels = [
            (pin, name, fill)
            for pin, name, fill, _text_color in AGON_PIN_DATA[bank]
        ]
        assert len(texts) == len(rectangles) == len(expected_labels) == 16
        for text_item, rectangle, (pin, name, fill) in zip(
            texts, rectangles, expected_labels
        ):
            assert text_item.attrib["text-anchor"] == "start"
            assert list(text_item) == []
            assert text_item.text == f"{pin} {name}"
            assert rectangle.attrib["fill"] == fill
        for first, second in zip(rectangles, rectangles[1:]):
            assert (
                abs(float(second.attrib["y"]) - float(first.attrib["y"]) - PITCH)
                < 0.001
            )
        header_scene_x, _header_scene_y = agon_header_scene_position(bank)
        assert abs(AGON_LABEL_BANK_SCENE_X[bank] - header_scene_x) < 0.001
        anchor_scene_x = (
            AGON_LABEL_BANK_SCENE_X[bank] + 3.6 / SVG_DPI * SCENE_DPI
        )
        anchor_scene_y = (
            AGON_LABEL_BANK_SCENE_Y[bank] + 3.6 / SVG_DPI * SCENE_DPI
        )
        for coordinate in (anchor_scene_x, anchor_scene_y):
            assert (
                abs(coordinate / SCENE_PITCH - round(coordinate / SCENE_PITCH))
                < 0.001
            )
    assert abs(PITCH / SVG_DPI - 0.1) < 0.001

    immutable_mux_names = {
        13: "PD4 / RTS1",
        14: "PD5 / CTS1",
        17: "PC0 / RXD1",
        19: "PC2 / TXD1",
    }
    for pin, expected_name in immutable_mux_names.items():
        assert all_pin_data[pin][0] == expected_name
    forbidden_extender_mappings = ("READY_N", "VALID_N", " / D", "CLOCK")
    assert all(
        not any(mapping in name for mapping in forbidden_extender_mappings)
        for name, _fill, _text_color in all_pin_data.values()
    )
    assert abs(EXT2_Y - EXT1_Y - P4_HEADER_SEPARATION) < 0.001
    assert abs(P4_SVG_X + P4_PIN1_X - FIRST_HOLE_X) < 0.001
    assert abs(P4_SVG_Y + P4_EXT1_Y - EXT1_Y) < 0.001
    assert abs(P4_SVG_Y + P4_EXT2_Y - EXT2_Y) < 0.001
    board_first_hole_scene_x = BOARD_SCENE_X + FIRST_HOLE_X / SVG_DPI * SCENE_DPI
    board_first_hole_scene_y = (
        BOARD_SCENE_Y + TOP_ROW_Y["A"] / SVG_DPI * SCENE_DPI
    )
    p4_first_pin_scene_x = P4_SCENE_X + P4_PIN1_X / SVG_DPI * SCENE_DPI
    p4_first_pin_scene_y = P4_SCENE_Y + P4_EXT1_Y / SVG_DPI * SCENE_DPI
    for coordinate in (
        board_first_hole_scene_x,
        board_first_hole_scene_y,
        p4_first_pin_scene_x,
        p4_first_pin_scene_y,
    ):
        assert abs(coordinate / SCENE_PITCH - round(coordinate / SCENE_PITCH)) < 0.001
    assert abs(board_first_hole_scene_x - p4_first_pin_scene_x) < 0.001

    for bank in ("even", "odd"):
        section, row = agon_header_board_row(bank)
        rows = TOP_ROW_Y if section == "top" else BOTTOM_ROW_Y
        column = agon_header_start_column(bank)
        board_x = (
            BOARD_SCENE_X
            + (FIRST_HOLE_X + (column - 1) * PITCH) / SVG_DPI * SCENE_DPI
        )
        board_y = BOARD_SCENE_Y + rows[row] / SVG_DPI * SCENE_DPI
        header_x, header_y = agon_header_scene_position(bank)
        pin_x = header_x + AGON_HEADER_PIN_X / SVG_DPI * SCENE_DPI
        pin_y = header_y + agon_header_pin_y(bank) / SVG_DPI * SCENE_DPI
        assert abs(board_x - pin_x) < 0.001
        assert abs(board_y - pin_y) < 0.001
        for coordinate in (pin_x, pin_y):
            assert abs(coordinate / SCENE_PITCH - round(coordinate / SCENE_PITCH)) < 0.001

    sketch_root = ET.fromstring(files[f"{SKETCH_BASENAME}.fz"])
    instances = sketch_root.findall("./instances/instance")
    assert len(instances) == 6
    label_titles = {
        instance.findtext("title", default="")
        for instance in instances
        if instance.attrib.get("moduleIdRef") in AGON_LABEL_BANK_MODULE_IDS.values()
    }
    assert label_titles == {"AgonOddPinLabelBank1", "AgonEvenPinLabelBank1"}
    board_scene_width = BOARD_VIEW_WIDTH / SVG_DPI * SCENE_DPI
    board_scene_height = BOARD_VIEW_HEIGHT / SVG_DPI * SCENE_DPI
    assert abs(
        (board_scene_width / 2.0) / SCENE_PITCH
        - round((board_scene_width / 2.0) / SCENE_PITCH)
    ) < 0.001
    assert abs(
        (board_scene_height / 2.0) / SCENE_PITCH
        - round((board_scene_height / 2.0) / SCENE_PITCH)
    ) < 0.001
    p4_scene_width = P4_VIEW_WIDTH / SVG_DPI * SCENE_DPI
    p4_scene_height = P4_VIEW_HEIGHT / SVG_DPI * SCENE_DPI
    # Canvas centers need not be on the grid. Fritzing's observed placement
    # authority is the connector center selected internally by the application.
    assert p4_scene_width > 0
    assert p4_scene_height > 0

    expected_archive = {
        f"{SKETCH_BASENAME}.fz",
        f"part.{BOARD_MODULE_ID}.fzp",
        f"part.{P4_MODULE_ID}.fzp",
        f"svg.breadboard.{BOARD_MODULE_ID}.svg",
        f"svg.breadboard.{P4_MODULE_ID}.svg",
    }
    for bank in ("even", "odd"):
        module_id = AGON_HEADER_MODULE_IDS[bank]
        expected_archive.add(f"part.{module_id}.fzp")
        expected_archive.add(f"svg.breadboard.{module_id}.svg")
    for module_id in AGON_LABEL_BANK_MODULE_IDS.values():
        expected_archive.add(f"part.{module_id}.fzp")
        expected_archive.add(f"svg.breadboard.{module_id}.svg")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        assert set(archive.namelist()) == expected_archive
        for name in expected_archive:
            if name.endswith((".fz", ".fzp", ".svg")):
                ET.fromstring(archive.read(name))

    expected_p4_archive = {
        f"part.{P4_MODULE_ID}.fzp",
        f"svg.breadboard.{P4_MODULE_ID}.svg",
    }
    with zipfile.ZipFile(io.BytesIO(p4_archive_bytes)) as archive:
        assert set(archive.namelist()) == expected_p4_archive
        for name in expected_p4_archive:
            ET.fromstring(archive.read(name))

    expected_board_archive = {
        f"part.{BOARD_MODULE_ID}.fzp",
        f"svg.breadboard.{BOARD_MODULE_ID}.svg",
    }
    with zipfile.ZipFile(io.BytesIO(board_archive_bytes)) as archive:
        assert set(archive.namelist()) == expected_board_archive
        for name in expected_board_archive:
            ET.fromstring(archive.read(name))


def checksum_manifest(
    archive_bytes: bytes,
    p4_archive_bytes: bytes,
    board_archive_bytes: bytes,
) -> bytes:
    return (
        f"{hashlib.sha256(archive_bytes).hexdigest()}  {SKETCH_BASENAME}.fzz\n"
        f"{hashlib.sha256(p4_archive_bytes).hexdigest()}  "
        f"{P4_PACKAGE_BASENAME}.fzpz\n"
        f"{hashlib.sha256(board_archive_bytes).hexdigest()}  "
        f"{BOARD_PACKAGE_BASENAME}.fzpz\n"
    ).encode()


def write_outputs(
    files: dict[str, bytes],
    archive_bytes: bytes,
    p4_archive_bytes: bytes,
    board_archive_bytes: bytes,
    output: Path,
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{SKETCH_BASENAME}.fzz").write_bytes(archive_bytes)
    (output / f"{P4_PACKAGE_BASENAME}.fzpz").write_bytes(p4_archive_bytes)
    (output / f"{BOARD_PACKAGE_BASENAME}.fzpz").write_bytes(board_archive_bytes)
    (output / f"{SKETCH_BASENAME}.svg").write_bytes(files[f"{SKETCH_BASENAME}.svg"])
    (output / "SHA256SUMS").write_bytes(
        checksum_manifest(archive_bytes, p4_archive_bytes, board_archive_bytes)
    )


def check_committed(
    files: dict[str, bytes],
    archive_bytes: bytes,
    p4_archive_bytes: bytes,
    board_archive_bytes: bytes,
) -> None:
    expected = {
        f"{SKETCH_BASENAME}.fzz": archive_bytes,
        f"{P4_PACKAGE_BASENAME}.fzpz": p4_archive_bytes,
        f"{BOARD_PACKAGE_BASENAME}.fzpz": board_archive_bytes,
        f"{SKETCH_BASENAME}.svg": files[f"{SKETCH_BASENAME}.svg"],
        "SHA256SUMS": checksum_manifest(
            archive_bytes,
            p4_archive_bytes,
            board_archive_bytes,
        ),
    }
    for name, data in expected.items():
        path = GENERATED / name
        if not path.exists() or path.read_bytes() != data:
            raise SystemExit(f"generated output is stale or missing: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate sources and confirm committed generated outputs are current",
    )
    args = parser.parse_args()

    files = build_files()
    archive_bytes = zip_bytes(files)
    p4_archive_bytes = p4_package_bytes(files)
    board_archive_bytes = board_package_bytes(files)
    validate(files, archive_bytes, p4_archive_bytes, board_archive_bytes)
    if args.check:
        check_committed(
            files,
            archive_bytes,
            p4_archive_bytes,
            board_archive_bytes,
        )
        print("SETUP-006.3 Fritzing scaffold: PASS (deterministic outputs current)")
        return

    write_outputs(
        files,
        archive_bytes,
        p4_archive_bytes,
        board_archive_bytes,
        GENERATED,
    )
    print(f"wrote {GENERATED / (SKETCH_BASENAME + '.fzz')}")
    print(f"wrote {GENERATED / (P4_PACKAGE_BASENAME + '.fzpz')}")
    print(f"wrote {GENERATED / (BOARD_PACKAGE_BASENAME + '.fzpz')}")
    print(f"wrote {GENERATED / (SKETCH_BASENAME + '.svg')}")


if __name__ == "__main__":
    main()
