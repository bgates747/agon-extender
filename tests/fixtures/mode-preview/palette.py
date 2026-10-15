"""Quantize to Agon's mode defaults using nearest RGB, without dithering.

Palette entries come from agon_palette.h (RRGGBB). Offline RGB matching avoids coloured HSV fringes on neutral text edges.
No dithering: every raster pixel is an exact member of the selected palette.
"""
from pathlib import Path
import re
from PIL import Image

def default_palette(repo, colours):
    source=(Path(repo)/'vdp/video/agon_palette.h').read_text()
    body=re.search(r'defaultPalette'+f'{colours:02X}'+r'\[[^]]+\]\s*=\s*\{(.*?)\}',source,re.S).group(1)
    body=re.sub(r'//[^\n]*','',body)
    values=[int(v,16) for v in re.findall(r'0x[0-9A-Fa-f]+',body)]
    assert len(values)==colours
    return [(((n>>4)&3)*85,((n>>2)&3)*85,(n&3)*85) for n in values]

def quantize(image,palette):
    # Match original RGB samples directly. Native HSV matching turns neutral
    # antialiasing into coloured fringes; offline RGB distance preserves clarity.
    # Palette order breaks equal-distance ties deterministically. No dithering.
    lookup={}
    def mapped(rgb):
        if rgb not in lookup:
            lookup[rgb]=min(palette,key=lambda p:sum((a-b)**2 for a,b in zip(rgb,p)))
        return lookup[rgb]
    pixels=[mapped(rgb) for rgb in image.get_flattened_data()]
    result=Image.new('RGB',image.size);result.putdata(pixels)
    assert set(result.get_flattened_data())<=set(palette)
    return result
