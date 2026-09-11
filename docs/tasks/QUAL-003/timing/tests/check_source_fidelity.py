"""Prove that disabling diagnostic hooks recovers the accepted renderer tokens."""
from pathlib import Path
import re,subprocess
ROOT=Path(__file__).resolve().parents[5]
def tokens(text):
    text=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
    return re.findall(r'[A-Za-z_][A-Za-z_0-9]*|0x[0-9a-fA-F]+|\d+|[^\s]',text)
def uninstrument(text):
    out=[];inside=False;keep=True
    for line in text.splitlines():
        if line.strip()=='#ifdef AGON_GRAPHICS_TIMING':
            assert not inside;inside=True;keep=False;continue
        if inside and line.strip()=='#else':keep=True;continue
        if inside and line.strip()=='#endif':inside=False;keep=True;continue
        if not keep:continue
        if 'AGON_GRAPHICS_SCOPE(' in line:continue
        out.append(line)
    assert not inside
    return '\n'.join(out)
for name in ['vdp/vendor/vdp-gl/src/displaycontroller.cpp','vdp/vendor/vdp-gl/src/displaycontroller.h',
             'vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp','vdp/video/vdu_sys.h']:
    base=subprocess.check_output(['git','show','f0dc271:'+name],cwd=ROOT,text=True)
    assert tokens(base)==tokens(uninstrument((ROOT/name).read_text())),name
    print('Uninstrumented tokens unchanged:',name)
