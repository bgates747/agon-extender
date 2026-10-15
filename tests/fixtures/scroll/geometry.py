"""Resolution-independent circular scrolling, using public VDU commands.

The bitmap is immutable. A clipped plot restores the row/column just scrolled
out, at the opposing edge. PLOT is required: the direct bitmap-draw command does
not install the current graphics clipping rectangle.
"""
from dataclasses import dataclass
import struct


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self):
        return self.x + self.width - 1

    @property
    def bottom(self):
        return self.y + self.height - 1


DIRECTIONS = {"up": 3, "down": 2, "left": 1, "right": 0}


def cases(width, height, margin):
    if not (0 < width <= 32767 and 0 < height <= 32767
            and 0 <= margin < min(width, height) / 2):
        raise ValueError("Invalid screen dimensions or partial-region margin")
    full = Rect(0, 0, width, height)
    result = []
    for partial in (False, True):
        for direction in DIRECTIONS:
            region = full
            if partial:
                region = (Rect(margin, 0, width - 2 * margin, height)
                          if direction in ("up", "down") else
                          Rect(0, margin, width, height - 2 * margin))
            result.append((f'{"partial" if partial else "full"}-{direction}',
                           direction, partial, region))
    return result


def viewport(rect):
    # Pixel coordinates, top-left origin. VDU24 orders bottom before top.
    return bytes([24]) + struct.pack('<HHHH', rect.x, rect.bottom,
                                    rect.right, rect.y)


def bitmap(x, y):
    return bytes([25, 0xED]) + struct.pack('<hh', x, y)


def wrap(region, direction, step):
    """Return the destination clipping strip and full-pattern plot offset.

    step starts at zero. Its source is the boundary row/column BEFORE this
    update, so a whole-region cycle returns the original image exactly.
    """
    if step < 0:
        raise ValueError("Negative step")
    if direction == "up":
        source = region.y + step % region.height
        return Rect(region.x, region.bottom, region.width, 1), (0, region.bottom-source)
    if direction == "down":
        source = region.bottom - step % region.height
        return Rect(region.x, region.y, region.width, 1), (0, region.y-source)
    if direction == "left":
        source = region.x + step % region.width
        return Rect(region.right, region.y, 1, region.height), (region.right-source, 0)
    if direction == "right":
        source = region.right - step % region.width
        return Rect(region.x, region.y, 1, region.height), (region.x-source, 0)
    raise ValueError("Unknown direction")


def update(region, direction, partial, step):
    strip, offset = wrap(region, direction, step)
    return (viewport(region) + bytes([23, 7, 2 if partial else 1,
                                    DIRECTIONS[direction], 1])
            + viewport(strip) + bitmap(*offset))
