#!/usr/bin/env python3
"""Check actual presentation helpers, color/lane preservation and carrier policy."""
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='hdmi-mode3-aspect-') as directory:
    for indexed in (False,True):
        output=Path(directory)/('indexed' if indexed else 'rgb')
        flags=['-DAGON_EXTENDER_HDMI_AUTO','-DAGON_EXTENDER_HDMI_PPA_320']
        if indexed:flags.append('-DAGON_EXTENDER_INDEXED_PPA')
        subprocess.run(['g++','-std=c++17','-O1','-g',*flags,'-I'+str(ROOT/'vdp/video'),
                        str(HERE/'hdmi_mode3_aspect_test.cpp'),'-o',str(output)],check=True)
        subprocess.run([str(output)],check=True)
    output=Path(directory)/'existing-geometry'
    subprocess.run(['g++','-std=c++17','-O1','-DAGON_EXTENDER_HDMI_AUTO',
                    '-I'+str(ROOT/'vdp/video'),str(HERE/'hdmi_output_test.cpp'),'-o',str(output)],check=True)
    subprocess.run([str(output)],check=True)
print('PASS: mode3 repeated rows, both variants, cropped edges, guards, colors and existing geometry/ownership')
