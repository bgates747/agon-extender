"""Minimal root-level KiCad schematic S-expression helpers."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterator


class KiCadSexprError(ValueError):
    """A KiCad schematic S-expression cannot be parsed safely."""


@dataclass(frozen=True)
class Block:
    """One immediate child S-expression of the KiCad schematic root."""

    start: int
    end: int
    kind: str
    text: str


@dataclass(frozen=True)
class LabelEndpoint:
    """A global label and its exact KiCad attachment coordinate."""

    net_id: str
    x_text: str
    y_text: str

    @property
    def point(self) -> tuple[float, float]:
        return float(self.x_text), float(self.y_text)


def immediate_blocks(text: str) -> Iterator[Block]:
    """Yield root-child blocks while respecting quoted strings and escapes."""

    depth = 0
    child_start: int | None = None
    in_string = False
    escaped = False

    for index, character in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
            continue
        if character == "(":
            if depth == 1:
                child_start = index
            depth += 1
            continue
        if character != ")":
            continue
        depth -= 1
        if depth < 0:
            raise KiCadSexprError("unbalanced closing parenthesis")
        if depth == 1 and child_start is not None:
            block_text = text[child_start : index + 1]
            match = re.match(r"\(([^\s()]+)", block_text)
            if match is None:
                raise KiCadSexprError("cannot identify KiCad child block")
            yield Block(child_start, index + 1, match.group(1), block_text)
            child_start = None

    if in_string or depth != 0:
        raise KiCadSexprError("unterminated string or unbalanced schematic")


def parse_label(block: Block) -> LabelEndpoint:
    """Parse one root-level KiCad global label."""

    name_match = re.match(r'^\(global_label "([^"]+)"', block.text)
    at_match = re.search(
        r"\s+\(at\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s+"
        r"(-?(?:\d+(?:\.\d*)?|\.\d+))(?:\s+[^)]*)?\)",
        block.text,
    )
    if name_match is None or at_match is None:
        raise KiCadSexprError("malformed global_label block")
    return LabelEndpoint(name_match.group(1), at_match.group(1), at_match.group(2))


def symbol_reference(block: Block) -> str:
    """Return the reference property from one root-level symbol block."""

    match = re.search(
        r'^\s*\(property "Reference" "([^"]+)"', block.text, re.MULTILINE
    )
    if match is None:
        raise KiCadSexprError("symbol has no Reference property")
    return match.group(1)


def symbol_transform(block: Block) -> tuple[float, float, int, str | None]:
    """Return one root-level symbol's position, rotation, and mirror axis."""

    match = re.match(
        r'^\(symbol\s+\(lib_id "[^"]+"\)\s+'
        r'\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)\s+(0|90|180|270)\)'
        r'(?:\s+\(mirror\s+([xy])\))?',
        block.text,
    )
    if match is None:
        raise KiCadSexprError("unsupported symbol transform")
    x, y, angle, mirror = match.groups()
    return float(x), float(y), int(angle), mirror
