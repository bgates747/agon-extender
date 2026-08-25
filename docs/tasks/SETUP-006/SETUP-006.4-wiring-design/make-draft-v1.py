#!/usr/bin/env python3
"""Derive the first review copy from the Author's completed Fritzing draft.

This task-local script exists because Fritzing 1.0.1 cannot safely perform the
required custom-part identity migration or preserve all established wiring
while reversing the composite breadboard's row-coordinate vocabulary.

The source draft is treated as immutable evidence.  The derivative operation:

1. replaces the embedded P4 r04 part with the corrected r05 part;
2. advances the composite breadboard part to r05 while reversing A--J row
   connector identities and every corresponding sketch reference;
3. adds visible row letters matching the physical upside-down orientation; and
4. adds a bundled, movable SN74HC125N DIP-14 U1, rotated 180 degrees in this
   view, with pin 1 at the upper-right corner at upper-board F36; and
5. applies the evidence-proved AUDIT-002 controlled-power circuit corrections,
   including separate Agon pin 33/GND and pin 34/+3.3 V contacts.

U1's breadboard artwork is deliberately diagrammatic.  Its pin rows match the
accepted custom scaffold's two center-adjacent hole rows; it is not a package
mechanical drawing or PCB footprint.  This workaround is local to the wiring
diagram and must not be reused as manufacturing geometry.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "light2-extender-breadboard-wiring-draft.fzz"
OUTPUT = ROOT / "light2-extender-breadboard-wiring-draft_v1.fzz"
P4_PACKAGE = (
    ROOT.parent
    / "SETUP-006.3-fritzing"
    / "generated"
    / "agon-extender-olimex-esp32-p4-devkit-rev-d1-fritzing-r05.fzpz"
)

SOURCE_SHA256 = "df8b899c41b2b186af5c298a30e70178c5fad94f0430a14f7f100407172c3b54"

P4_R04 = "agon-extender-olimex-esp32-p4-devkit-rev-d1-fritzing-r04"
P4_R05 = "agon-extender-olimex-esp32-p4-devkit-rev-d1-fritzing-r05"
BOARD_R04 = "agon-extender-bb1460-two-rail-scaffold-fritzing-r04"
BOARD_R05 = "agon-extender-bb1460-two-rail-scaffold-fritzing-r05"
U1_MODULE = "agon-extender-sn74hc125n-dip14-fritzing-r01"
AGON_PIN33_MODULE = "agon-light2-pin33-ground-contact-fritzing-r01"
AGON_PIN34_MODULE = "agon-light2-pin34-3v3-contact-fritzing-r01"

ROW_REVERSE = dict(zip("ABCDEFGHIJ", "JIHGFEDCBA", strict=True))
BOARD_CONNECTOR_RE = re.compile(r"^(top|bottom)-([A-J])(\d+)$")
BOARD_NAME_RE = re.compile(r"(BB630 )([A-J])(\d+)")
BOARD_BUS_RE = re.compile(r"^(top|bottom)-([A-J])([A-J])-(\d+)$")

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def xml_bytes(root: ET.Element) -> bytes:
    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def archive_contents(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def deterministic_zip(files: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, (2026, 8, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    return stream.getvalue()


def map_board_connector(value: str) -> str:
    match = BOARD_CONNECTOR_RE.fullmatch(value)
    if not match:
        return value
    section, row, column = match.groups()
    return f"{section}-{ROW_REVERSE[row]}{column}"


def map_board_name(value: str | None) -> str | None:
    if value is None:
        return None
    return BOARD_NAME_RE.sub(
        lambda match: f"{match.group(1)}{ROW_REVERSE[match.group(2)]}{match.group(3)}",
        value,
    )


def migrate_board_fzp(source: bytes) -> bytes:
    root = ET.fromstring(source)
    root.set("moduleId", BOARD_R05)
    root.set("referenceFile", f"{BOARD_R05}.fzp")
    version = root.find("version")
    if version is not None:
        version.text = "3"
    title = root.find("title")
    if title is not None:
        title.text = "BB1460 two-rail scaffold — reversed physical row lettering"

    for layers in root.findall(".//layers"):
        image = layers.get("image")
        if image:
            layers.set("image", image.replace(BOARD_R04, BOARD_R05))

    for connector in root.findall("./connectors/connector"):
        old_id = connector.get("id", "")
        connector.set("id", map_board_connector(old_id))
        connector.set("name", map_board_name(connector.get("name")) or "")
        description = connector.find("description")
        if description is not None:
            description.text = map_board_name(description.text)
        for point in connector.findall(".//p"):
            svg_id = point.get("svgId")
            if svg_id and svg_id.endswith("pin"):
                point.set("svgId", f"{map_board_connector(svg_id[:-3])}pin")

    for bus in root.findall("./buses/bus"):
        bus_id = bus.get("id", "")
        match = BOARD_BUS_RE.fullmatch(bus_id)
        if match:
            section, first, last, column = match.groups()
            mapped = sorted((ROW_REVERSE[first], ROW_REVERSE[last]))
            bus.set("id", f"{section}-{mapped[0]}{mapped[1]}-{column}")
        for member in bus.findall("nodeMember"):
            member.set(
                "connectorId", map_board_connector(member.get("connectorId", ""))
            )
    return xml_bytes(root)


def migrate_board_svg(source: bytes) -> bytes:
    root = ET.fromstring(source)
    layer = root.find(f".//{{{SVG_NS}}}g[@id='breadboardbreadboard']")
    if layer is None:
        raise ValueError("composite breadboard SVG lacks breadboardbreadboard layer")

    # Capture physical row centers before changing IDs.  Lettering changes the
    # coordinate vocabulary only; no connector geometry is moved.
    row_y: dict[tuple[str, str], float] = {}
    for section in ("top", "bottom"):
        for row in "ABCDEFGHIJ":
            item = root.find(f".//*[@id='{section}-{row}1pin']")
            if item is None:
                raise ValueError(f"missing board connector {section}-{row}1pin")
            row_y[(section, row)] = float(item.get("cy", "nan"))

    for item in root.iter():
        item_id = item.get("id")
        if item_id and item_id.endswith("pin"):
            item.set("id", f"{map_board_connector(item_id[:-3])}pin")

    # BPS prints row letters on the physical breadboard.  Show the corrected
    # upside-down orientation at both ends without altering any hole or bus.
    for section in ("top", "bottom"):
        for old_row in "ABCDEFGHIJ":
            new_row = ROW_REVERSE[old_row]
            y = row_y[(section, old_row)] + 1.35
            for side, x in (("left", 4.2), ("right", 464.0)):
                text = ET.SubElement(
                    layer,
                    f"{{{SVG_NS}}}text",
                    {
                        "id": f"{section}-row-{new_row}-{side}-label",
                        "x": f"{x:g}",
                        "y": f"{y:g}",
                        "font-size": "3.8",
                        "font-weight": "bold",
                        "text-anchor": "middle",
                        "fill": "#555555",
                    },
                )
                text.text = new_row
    return xml_bytes(root)


def u1_svg() -> bytes:
    # The 0.7-inch longitudinal pitch is true to a DIP-14.  The transverse
    # rendering is compressed solely to seat the part on the accepted
    # diagrammatic scaffold's two center-adjacent connector rows.
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<svg xmlns="{SVG_NS}" width="0.7in" height="0.22in" viewBox="0 0 50.4 15.84">',
        '<g id="breadboard">',
        '<rect x="1.8" y="1.8" width="46.8" height="12.24" rx="1.4" fill="#303030" stroke="#151515" stroke-width="0.7"/>',
        '<path d="M 49.5,5.0 A 3.0,3.0 0 0 0 49.5,10.84" fill="none" stroke="#bdbdbd" stroke-width="0.8"/>',
        '<circle cx="46.3" cy="4.2" r="0.9" fill="#d8d8d8"/>',
        '<text x="25.2" y="7.0" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="3.8" fill="#f0f0f0">U1</text>',
        '<text x="25.2" y="11.1" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="3.35" fill="#f0f0f0">SN74HC125N</text>',
    ]
    for offset in range(7):
        x = 3.6 + offset * 7.2
        upper_pin = 7 - offset
        lower_pin = 8 + offset
        lines.extend(
            [
                f'<rect id="connector{upper_pin - 1}pin" x="{x - 1.35:g}" y="0" width="2.7" height="1.44" fill="#9a9a9a"/>',
                f'<rect id="connector{lower_pin - 1}pin" x="{x - 1.35:g}" y="14.4" width="2.7" height="1.44" fill="#9a9a9a"/>',
            ]
        )
    lines.append("</g></svg>")
    return ("\n".join(lines) + "\n").encode()


U1_PIN_NAMES = {
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


def u1_fzp() -> bytes:
    module = ET.Element(
        "module",
        {
            "moduleId": U1_MODULE,
            "referenceFile": f"{U1_MODULE}.fzp",
            "fritzingVersion": "1.0.1",
        },
    )
    ET.SubElement(module, "version").text = "1"
    ET.SubElement(module, "author").text = "Agon Extender Project"
    ET.SubElement(module, "title").text = "SN74HC125N quad tri-state buffer"
    ET.SubElement(module, "label").text = "U"
    tags = ET.SubElement(module, "tags")
    for tag in ("SN74HC125N", "74HC125", "DIP-14", "buffer", "tri-state"):
        ET.SubElement(tags, "tag").text = tag
    properties = ET.SubElement(module, "properties")
    for name, value in (
        ("family", "74HC125 quad tri-state buffer"),
        ("part number", "SN74HC125N"),
        ("package", "DIP-14 (diagrammatic breadboard view)"),
        ("pins", "14"),
    ):
        ET.SubElement(properties, "property", {"name": name}).text = value
    ET.SubElement(module, "taxonomy").text = "part.dip.14.pins.buffer"
    ET.SubElement(module, "description").text = (
        "Task-local wiring-diagram representation of the documented on-hand "
        "SN74HC125N U1. Transverse artwork is compressed to the accepted "
        "breadboard scaffold and is not package or PCB geometry."
    )
    views = ET.SubElement(module, "views")
    for view_name in ("iconView", "breadboardView", "schematicView", "pcbView"):
        view = ET.SubElement(views, view_name)
        layers = ET.SubElement(
            view,
            "layers",
            {"image": f"breadboard/{U1_MODULE}.svg"},
        )
        ET.SubElement(layers, "layer", {"layerId": "breadboard"})
    connectors = ET.SubElement(module, "connectors", {"ignoreTerminalPoints": "true"})
    for pin in range(1, 15):
        connector = ET.SubElement(
            connectors,
            "connector",
            {"id": f"connector{pin - 1}", "name": f"pin {pin} {U1_PIN_NAMES[pin]}", "type": "male"},
        )
        ET.SubElement(connector, "description").text = U1_PIN_NAMES[pin]
        connector_views = ET.SubElement(connector, "views")
        breadboard = ET.SubElement(connector_views, "breadboardView")
        ET.SubElement(
            breadboard,
            "p",
            {"layer": "breadboard", "svgId": f"connector{pin - 1}pin"},
        )
    return xml_bytes(module)


def single_contact_svg(connector_id: str, label: str, color: str) -> bytes:
    """Return a compact labeled flying-contact diagram part.

    Pins 33 and 34 do not belong to either 16-contact signal bank.  The wider
    artwork is intentional: one electrical contact sits at its right edge
    while the attached label extends into the free left margin.
    """
    foreground = "#ffffff" if color in {"#111111", "#d32f2f"} else "#111111"
    return (
        f'<?xml version="1.0" encoding="utf-8"?>\n'
        f'<svg xmlns="{SVG_NS}" width="0.45in" height="0.1in" viewBox="0 0 32.4 7.2">\n'
        '<g id="breadboard">\n'
        f'<rect x="0.2" y="0.1" width="32" height="7" rx="1" fill="{color}" stroke="#333333" stroke-width="0.6"/>\n'
        f'<text x="1.8" y="4.85" font-family="DejaVu Sans, sans-serif" font-size="4.0" font-weight="bold" fill="{foreground}">{label}</text>\n'
        f'<rect id="{connector_id}pin" x="27.45" y="1.05" width="5.1" height="5.1" rx="0.5" fill="{color}" stroke="#333333" stroke-width="0.55"/>\n'
        '</g></svg>\n'
    ).encode()


def single_contact_fzp(
    module_id: str, connector_id: str, title: str, description: str
) -> bytes:
    module = ET.Element(
        "module",
        {
            "moduleId": module_id,
            "referenceFile": f"{module_id}.fzp",
            "fritzingVersion": "1.0.1",
        },
    )
    ET.SubElement(module, "version").text = "1"
    ET.SubElement(module, "author").text = "Agon Extender Project"
    ET.SubElement(module, "title").text = title
    ET.SubElement(module, "label").text = title
    tags = ET.SubElement(module, "tags")
    for tag in ("Agon Light 2", "flying contact", "power", "custom"):
        ET.SubElement(tags, "tag").text = tag
    properties = ET.SubElement(module, "properties")
    ET.SubElement(properties, "property", {"name": "family"}).text = (
        "Agon Light 2 separate power contact"
    )
    ET.SubElement(module, "taxonomy").text = "connector.single.agon.power"
    ET.SubElement(module, "description").text = description
    views = ET.SubElement(module, "views")
    for view_name in ("iconView", "breadboardView", "schematicView", "pcbView"):
        view = ET.SubElement(views, view_name)
        layers = ET.SubElement(
            view, "layers", {"image": f"breadboard/{module_id}.svg"}
        )
        ET.SubElement(layers, "layer", {"layerId": "breadboard"})
    connectors = ET.SubElement(module, "connectors")
    connector = ET.SubElement(
        connectors,
        "connector",
        {"id": connector_id, "name": title, "type": "male"},
    )
    ET.SubElement(connector, "description").text = description
    connector_views = ET.SubElement(connector, "views")
    for view_name in ("breadboardView", "schematicView", "pcbView"):
        view = ET.SubElement(connector_views, view_name)
        ET.SubElement(
            view, "p", {"layer": "breadboard", "svgId": f"{connector_id}pin"}
        )
    return xml_bytes(module)


def connection(
    parent: ET.Element,
    connector_id: str,
    source_layer: str,
    target_id: str,
    target_index: str,
    target_layer: str,
) -> None:
    connector = ET.SubElement(
        parent,
        "connector",
        {"connectorId": connector_id, "layer": source_layer},
    )
    connects = ET.SubElement(connector, "connects")
    ET.SubElement(
        connects,
        "connect",
        {"connectorId": target_id, "modelIndex": target_index, "layer": target_layer},
    )


def migrate_sketch(source: bytes, board_svg_source: bytes) -> tuple[str, bytes, str]:
    root = ET.fromstring(source)
    instances = root.find("instances")
    if instances is None:
        raise ValueError("sketch has no instances")

    board = instances.find(f"instance[@moduleIdRef='{BOARD_R04}']")
    p4 = instances.find(f"instance[@moduleIdRef='{P4_R04}']")
    if board is None or p4 is None:
        raise ValueError("source draft does not contain expected r04 board and P4")

    board_index = board.get("modelIndex", "")
    p4.set("moduleIdRef", P4_R05)
    p4.set("path", f"part.{P4_R05}.fzp")
    board.set("moduleIdRef", BOARD_R05)
    board.set("path", f"part.{BOARD_R05}.fzp")

    original_geometry = {
        item.get("modelIndex", ""): ET.tostring(
            item.find("./views/breadboardView/geometry"), encoding="unicode"
        )
        for item in instances.findall("instance")
        if item.find("./views/breadboardView/geometry") is not None
    }

    # Remap both the board instance's own connector records and every inbound
    # reference to modelIndex 1.  This preserves the exact physical hole and
    # net while changing only its upside-down row name.
    for element in root.iter():
        connector_id = element.get("connectorId")
        if not connector_id:
            continue
        if element.tag == "connector":
            ancestor_is_board = element in board.findall(".//connector")
            if ancestor_is_board:
                element.set("connectorId", map_board_connector(connector_id))
        elif element.tag == "connect" and element.get("modelIndex") == board_index:
            element.set("connectorId", map_board_connector(connector_id))

    used_indices = [int(item.get("modelIndex", "0")) for item in instances.findall("instance")]
    u1_index = str(max(used_indices) + 1)

    # The reversed physical labels put the lower center-adjacent row at E and
    # the upper center-adjacent row at F. U1 is rotated 180 degrees in this
    # view: pin 1 is upper-right at F36 and the package spans columns 30--36.
    u1_board: dict[str, str] = {}
    for offset in range(7):
        u1_board[f"connector{offset}"] = f"top-F{36 - offset}"
        u1_board[f"connector{7 + offset}"] = f"top-E{30 + offset}"

    board_view = board.find("./views/breadboardView")
    if board_view is None:
        raise ValueError("board instance has no breadboard view")
    existing_board_connectors = {
        item.get("connectorId") for item in board_view.findall("./connectors/connector")
    }
    occupied = sorted(set(u1_board.values()) & existing_board_connectors)
    if occupied:
        raise ValueError(f"U1 target holes are already occupied: {', '.join(occupied)}")
    board_connectors = board_view.find("connectors")
    if board_connectors is None:
        board_connectors = ET.SubElement(board_view, "connectors")
    for u1_connector, board_connector in u1_board.items():
        connection(
            board_connectors,
            board_connector,
            "breadboardbreadboard",
            u1_connector,
            u1_index,
            "breadboard",
        )

    u1 = ET.SubElement(
        instances,
        "instance",
        {
            "moduleIdRef": U1_MODULE,
            "modelIndex": u1_index,
            "path": f"part.{U1_MODULE}.fzp",
        },
    )
    ET.SubElement(u1, "title").text = "U1"
    u1_views = ET.SubElement(u1, "views")
    u1_breadboard = ET.SubElement(u1_views, "breadboardView", {"layer": "breadboard"})
    ET.SubElement(
        u1_breadboard,
        "geometry",
        {"z": "5", "x": "274.5", "y": "53.1"},
    )
    u1_connectors = ET.SubElement(u1_breadboard, "connectors")
    for u1_connector, board_connector in u1_board.items():
        connection(
            u1_connectors,
            u1_connector,
            "breadboard",
            board_connector,
            board_index,
            "breadboardbreadboard",
        )
    for view_name, x in (("schematicView", "1500"), ("pcbView", "1600")):
        view = ET.SubElement(u1_views, view_name, {"layer": "breadboard"})
        ET.SubElement(view, "geometry", {"z": "5", "x": x, "y": "400"})

    def by_title(title: str) -> ET.Element:
        found = [item for item in instances.findall("instance") if item.findtext("title") == title]
        if len(found) != 1:
            raise ValueError(f"expected one sketch instance titled {title}, found {len(found)}")
        return found[0]

    def board_connectors_element() -> ET.Element:
        found = board.find("./views/breadboardView/connectors")
        if found is None:
            raise ValueError("board instance has no breadboard connectors")
        return found

    def remove_board_backlink(
        board_connector: str, target_index: str, target_connector: str
    ) -> None:
        container = board_connectors_element()
        item = next(
            (
                candidate
                for candidate in container.findall("connector")
                if candidate.get("connectorId") == board_connector
            ),
            None,
        )
        if item is None:
            raise ValueError(f"missing board backlink at {board_connector}")
        connects = item.find("connects")
        if connects is None:
            raise ValueError(f"board backlink {board_connector} has no targets")
        matches = [
            target
            for target in connects.findall("connect")
            if target.get("modelIndex") == target_index
            and target.get("connectorId") == target_connector
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected one backlink {board_connector} -> "
                f"{target_index}.{target_connector}, found {len(matches)}"
            )
        connects.remove(matches[0])
        if not connects.findall("connect"):
            container.remove(item)

    def add_board_backlink(
        board_connector: str,
        target_index: str,
        target_connector: str,
        target_layer: str,
    ) -> None:
        container = board_connectors_element()
        existing = next(
            (
                candidate
                for candidate in container.findall("connector")
                if candidate.get("connectorId") == board_connector
            ),
            None,
        )
        if existing is not None:
            raise ValueError(f"physical hole already occupied: {board_connector}")
        connection(
            container,
            board_connector,
            "breadboardbreadboard",
            target_connector,
            target_index,
            target_layer,
        )

    def retarget(
        title: str,
        connector_id: str,
        old_board_connector: str,
        new_board_connector: str,
        target_layer: str,
    ) -> None:
        instance = by_title(title)
        model_index = instance.get("modelIndex", "")
        changed = 0
        for target in instance.findall(
            f".//connector[@connectorId='{connector_id}']/connects/connect"
        ):
            if (
                target.get("modelIndex") == board_index
                and target.get("connectorId") == old_board_connector
            ):
                target.set("connectorId", new_board_connector)
                changed += 1
        if changed == 0:
            raise ValueError(
                f"missing {title}.{connector_id} target {old_board_connector}"
            )
        remove_board_backlink(old_board_connector, model_index, connector_id)
        add_board_backlink(
            new_board_connector, model_index, connector_id, target_layer
        )

    def attach_passive(title: str, connector_id: str, board_connector: str) -> None:
        instance = by_title(title)
        model_index = instance.get("modelIndex", "")
        connector = instance.find(
            f"./views/breadboardView/connectors/connector[@connectorId='{connector_id}']"
        )
        if connector is None:
            raise ValueError(f"missing passive endpoint {title}.{connector_id}")
        if connector.find("connects") is not None:
            raise ValueError(f"passive endpoint already attached: {title}.{connector_id}")
        connects = ET.SubElement(connector, "connects")
        ET.SubElement(
            connects,
            "connect",
            {
                "connectorId": board_connector,
                "modelIndex": board_index,
                "layer": "breadboardbreadboard",
            },
        )
        add_board_backlink(board_connector, model_index, connector_id, "breadboard")

    # AUDIT-002 found that the first U1 overlay had inherited geometrically
    # plausible but electrically incorrect endpoint choices from the manual
    # source draft.  These corrections reproduce the tracked predecessor U1
    # pin map; they are not a new circuit design.
    retarget("R7", "connector1", "top-G30", "top-G31", "breadboard")
    r7_leg = by_title("R7").find(
        "./views/breadboardView/connectors/connector[@connectorId='connector1']/leg"
    )
    assert r7_leg is not None
    r7_points = r7_leg.findall("point")
    r7_points[-1].set("x", "55.3095")

    retarget("Wire4", "connector1", "top-I31", "top-I13", "breadboardWire")
    wire4_geometry = by_title("Wire4").find("./views/breadboardView/geometry")
    assert wire4_geometry is not None
    wire4_geometry.set("x2", "-198")

    retarget(
        "Wire12",
        "connector0",
        "center-rail-blue37",
        "center-rail-red37",
        "breadboardWire",
    )
    wire12_geometry = by_title("Wire12").find("./views/breadboardView/geometry")
    assert wire12_geometry is not None
    wire12_geometry.set("y", "139.5")
    wire12_geometry.set("y2", "-31.5")

    # Wire17 previously shared the CLOCK pin's physical hole.  Move only its
    # breadboard end to an adjacent hole on the same five-hole CLOCK bus.
    retarget("Wire17", "connector1", "top-C15", "top-D15", "breadboardWire")
    wire17_geometry = by_title("Wire17").find("./views/breadboardView/geometry")
    assert wire17_geometry is not None
    wire17_geometry.set("y2", "-11.25")

    # These three vertical resistors were already drawn at their intended
    # locations, but their second leads were not recorded as landed.
    attach_passive("R8", "connector1", "top-rail-red33")
    attach_passive("R10", "connector1", "top-rail-red39")
    attach_passive("R12", "connector1", "top-A32")
    # R8/R10's manually drawn free leads stopped half a grid pitch short of
    # the upper red rail.  Extend only those lead segments to their now-
    # recorded holes; the resistor bodies and signal-side leads do not move.
    for title in ("R8", "R10"):
        leg = by_title(title).find(
            "./views/breadboardView/connectors/connector[@connectorId='connector1']/leg"
        )
        assert leg is not None
        leg.findall("point")[-1].set("x", "1.3095")

    board_svg = ET.fromstring(board_svg_source)
    board_geometry = board.find("./views/breadboardView/geometry")
    assert board_geometry is not None
    board_x = float(board_geometry.get("x", "0"))
    board_y = float(board_geometry.get("y", "0"))

    def board_scene_point(connector_id: str) -> tuple[float, float]:
        item = next(
            (
                candidate
                for candidate in board_svg.iter()
                if candidate.get("id") == f"{connector_id}pin"
            ),
            None,
        )
        if item is None:
            raise ValueError(f"board SVG lacks {connector_id}pin")
        return (
            board_x + float(item.get("cx", "nan")) * 1.25,
            board_y + float(item.get("cy", "nan")) * 1.25,
        )

    next_index = max(int(item.get("modelIndex", "0")) for item in instances.findall("instance")) + 1

    def add_contact(
        module_id: str,
        title: str,
        connector_id: str,
        board_connector: str,
    ) -> str:
        nonlocal next_index
        model_index = str(next_index)
        next_index += 1
        target_x, target_y = board_scene_point(board_connector)
        item = ET.SubElement(
            instances,
            "instance",
            {
                "moduleIdRef": module_id,
                "modelIndex": model_index,
                "path": f"part.{module_id}.fzp",
            },
        )
        ET.SubElement(item, "title").text = title
        views = ET.SubElement(item, "views")
        breadboard_view = ET.SubElement(views, "breadboardView", {"layer": "breadboard"})
        ET.SubElement(
            breadboard_view,
            "geometry",
            {
                "z": "6",
                "x": f"{target_x - 37.5:g}",
                "y": f"{target_y - 4.5:g}",
            },
        )
        connectors = ET.SubElement(breadboard_view, "connectors")
        connection(
            connectors,
            connector_id,
            "breadboard",
            board_connector,
            board_index,
            "breadboardbreadboard",
        )
        for view_name, x in (("schematicView", "1700"), ("pcbView", "1800")):
            view = ET.SubElement(views, view_name, {"layer": "breadboard"})
            ET.SubElement(view, "geometry", {"z": "6", "x": x, "y": "500"})
        add_board_backlink(board_connector, model_index, connector_id, "breadboard")
        return model_index

    add_contact(
        AGON_PIN34_MODULE,
        "AgonPin34ThreeV3_1",
        "agon-pin34",
        "top-J5",
    )
    add_contact(
        AGON_PIN33_MODULE,
        "AgonPin33Ground1",
        "agon-pin33",
        "bottom-A3",
    )

    def add_wire(title: str, first: str, second: str, color: str) -> None:
        nonlocal next_index
        model_index = str(next_index)
        next_index += 1
        first_x, first_y = board_scene_point(first)
        second_x, second_y = board_scene_point(second)
        item = ET.SubElement(
            instances,
            "instance",
            {
                "moduleIdRef": "WireModuleID",
                "modelIndex": model_index,
                "path": ":/resources/parts/core/wire.fzp",
            },
        )
        ET.SubElement(item, "title").text = title
        views = ET.SubElement(item, "views")
        view = ET.SubElement(views, "breadboardView", {"layer": "breadboardWire"})
        ET.SubElement(
            view,
            "geometry",
            {
                "z": "6",
                "x": f"{first_x:g}",
                "y": f"{first_y:g}",
                "x1": "0",
                "y1": "0",
                "x2": f"{second_x - first_x:g}",
                "y2": f"{second_y - first_y:g}",
                "wireFlags": "64",
            },
        )
        ET.SubElement(
            view,
            "wireExtras",
            {"mils": "22.2222", "color": color, "opacity": "1", "banded": "0"},
        )
        connectors = ET.SubElement(view, "connectors")
        connection(
            connectors,
            "connector0",
            "breadboardWire",
            first,
            board_index,
            "breadboardbreadboard",
        )
        connection(
            connectors,
            "connector1",
            "breadboardWire",
            second,
            board_index,
            "breadboardbreadboard",
        )
        add_board_backlink(first, model_index, "connector0", "breadboardWire")
        add_board_backlink(second, model_index, "connector1", "breadboardWire")

    # The Agon supplies only the logic reference rail.  The P4's positive
    # supply pins remain untouched; only the proved EXT1 pin 2 ground joins the
    # common signal ground.
    add_wire("Agon3V3Entry", "top-I5", "top-rail-red5", "#cc1414")
    add_wire(
        "Agon3V3RailBridge", "top-rail-red59", "center-rail-red59", "#cc1414"
    )
    add_wire("AgonGroundEntry", "bottom-B3", "center-rail-blue3", "#111111")
    add_wire(
        "GroundRailBridge", "top-rail-blue59", "center-rail-blue59", "#111111"
    )
    add_wire("P4SignalGround", "top-D2", "top-rail-blue2", "#111111")

    # Every original placement except the four explicitly corrected route
    # objects remains byte-identical at the breadboard-geometry level.
    changed_geometry = {"5846", "5852", "5907", "5920"}
    for model_index, expected in original_geometry.items():
        if model_index in changed_geometry:
            continue
        current = instances.find(
            f"instance[@modelIndex='{model_index}']/views/breadboardView/geometry"
        )
        assert current is not None
        if ET.tostring(current, encoding="unicode") != expected:
            raise ValueError(f"unrelated geometry changed for modelIndex {model_index}")

    sketch_name = root.get("title") or "light2-extender-breadboard-wiring-draft"
    root.set("title", "light2-extender-breadboard-wiring-draft_v1")
    return sketch_name, xml_bytes(root), u1_index


def validate(files: dict[str, bytes], sketch_file: str, u1_index: str) -> None:
    root = ET.fromstring(files[sketch_file])
    instances = root.find("instances")
    assert instances is not None
    assert instances.find(f"instance[@moduleIdRef='{P4_R04}']") is None
    assert instances.find(f"instance[@moduleIdRef='{BOARD_R04}']") is None
    assert instances.find(f"instance[@moduleIdRef='{P4_R05}']") is not None
    assert instances.find(f"instance[@moduleIdRef='{BOARD_R05}']") is not None
    u1 = instances.find(f"instance[@modelIndex='{u1_index}']")
    assert u1 is not None and u1.get("moduleIdRef") == U1_MODULE

    board_fzp = ET.fromstring(files[f"part.{BOARD_R05}.fzp"])
    board_ids = {item.get("id") for item in board_fzp.findall("./connectors/connector")}
    assert "top-E36" in board_ids and "top-F36" in board_ids
    board_svg = ET.fromstring(files[f"svg.breadboard.{BOARD_R05}.svg"])
    labels = {
        item.text
        for item in board_svg.findall(f".//{{{SVG_NS}}}text")
        if item.get("id", "").startswith(("top-row-", "bottom-row-"))
    }
    assert labels == set("ABCDEFGHIJ")

    p4_fzp = ET.fromstring(files[f"part.{P4_R05}.fzp"])
    p4_names = {
        item.get("id"): item.get("name") for item in p4_fzp.findall("./connectors/connector")
    }
    assert "GPIO16" in p4_names["ext1-pin17"]
    assert "GPIO17" in p4_names["ext1-pin18"]

    u1_fzp_root = ET.fromstring(files[f"part.{U1_MODULE}.fzp"])
    assert len(u1_fzp_root.findall("./connectors/connector")) == 14
    u1_connections = u1.findall("./views/breadboardView/connectors/connector")
    assert len(u1_connections) == 14
    by_id = {item.get("connectorId"): item for item in u1_connections}
    pin1_target = by_id["connector0"].find("./connects/connect")
    assert pin1_target is not None
    assert pin1_target.get("connectorId") == "top-F36"

    titles = {item.findtext("title"): item for item in instances.findall("instance")}
    assert titles["AgonPin34ThreeV3_1"].get("moduleIdRef") == AGON_PIN34_MODULE
    assert titles["AgonPin33Ground1"].get("moduleIdRef") == AGON_PIN33_MODULE

    board_view = instances.find(
        f"instance[@moduleIdRef='{BOARD_R05}']/views/breadboardView"
    )
    assert board_view is not None
    collisions = [
        item.get("connectorId", "")
        for item in board_view.findall("./connectors/connector")
        if len(item.findall("./connects/connect")) > 1
    ]
    assert not collisions, f"multiply occupied breadboard holes: {collisions}"

    expected_files = {
        f"part.{P4_R05}.fzp",
        f"svg.breadboard.{P4_R05}.svg",
        f"part.{BOARD_R05}.fzp",
        f"svg.breadboard.{BOARD_R05}.svg",
        f"part.{U1_MODULE}.fzp",
        f"svg.breadboard.{U1_MODULE}.svg",
        f"part.{AGON_PIN33_MODULE}.fzp",
        f"svg.breadboard.{AGON_PIN33_MODULE}.svg",
        f"part.{AGON_PIN34_MODULE}.fzp",
        f"svg.breadboard.{AGON_PIN34_MODULE}.svg",
    }
    assert expected_files <= set(files)
    assert not any(P4_R04 in name or BOARD_R04 in name for name in files)


def build() -> bytes:
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError(
            "completed source draft has changed; preserve it and review the new source "
            f"before deriving v1 (expected {SOURCE_SHA256}, found {source_hash})"
        )

    files = archive_contents(SOURCE)
    sketch_names = [name for name in files if name.endswith(".fz")]
    if len(sketch_names) != 1:
        raise ValueError(f"expected one .fz sketch, found {len(sketch_names)}")
    old_sketch = sketch_names[0]

    p4_files = archive_contents(P4_PACKAGE)
    p4_fzp_name = next(name for name in p4_files if name.endswith(".fzp"))
    p4_svg_name = next(name for name in p4_files if name.endswith(".svg"))

    board_fzp_old = f"part.{BOARD_R04}.fzp"
    board_svg_old = f"svg.breadboard.{BOARD_R04}.svg"
    board_fzp_new = f"part.{BOARD_R05}.fzp"
    board_svg_new = f"svg.breadboard.{BOARD_R05}.svg"

    files[board_fzp_new] = migrate_board_fzp(files.pop(board_fzp_old))
    files[board_svg_new] = migrate_board_svg(files.pop(board_svg_old))
    _old_title, sketch, u1_index = migrate_sketch(
        files.pop(old_sketch), files[board_svg_new]
    )
    sketch_file = "light2-extender-breadboard-wiring-draft_v1.fz"
    files[sketch_file] = sketch

    files.pop(f"part.{P4_R04}.fzp")
    files.pop(f"svg.breadboard.{P4_R04}.svg")
    files[f"part.{P4_R05}.fzp"] = p4_files[p4_fzp_name]
    files[f"svg.breadboard.{P4_R05}.svg"] = p4_files[p4_svg_name]
    files[f"part.{U1_MODULE}.fzp"] = u1_fzp()
    files[f"svg.breadboard.{U1_MODULE}.svg"] = u1_svg()
    files[f"part.{AGON_PIN33_MODULE}.fzp"] = single_contact_fzp(
        AGON_PIN33_MODULE,
        "agon-pin33",
        "Agon pin 33 GND",
        "Separate black ground lead from Agon Light 2 physical pin 33.",
    )
    files[f"svg.breadboard.{AGON_PIN33_MODULE}.svg"] = single_contact_svg(
        "agon-pin33", "33 GND", "#111111"
    )
    files[f"part.{AGON_PIN34_MODULE}.fzp"] = single_contact_fzp(
        AGON_PIN34_MODULE,
        "agon-pin34",
        "Agon pin 34 +3.3 V",
        "Separate red 3.3 V logic-reference lead from Agon Light 2 physical pin 34.",
    )
    files[f"svg.breadboard.{AGON_PIN34_MODULE}.svg"] = single_contact_svg(
        "agon-pin34", "34 +3V3", "#d32f2f"
    )

    validate(files, sketch_file, u1_index)
    return deterministic_zip(files)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the existing draft_v1 is the deterministic output",
    )
    args = parser.parse_args()
    built = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != built:
            raise SystemExit(f"stale or missing generated file: {OUTPUT}")
        return
    OUTPUT.write_bytes(built)


if __name__ == "__main__":
    main()
