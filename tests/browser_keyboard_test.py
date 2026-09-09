"""Host checks of session semantics and exact pinned FabGL virtual key values."""
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory() as temp:
        binary=Path(temp)/'keyboard'
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                        '-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),
                        str(ROOT/'tests/browser_keyboard_test.cpp'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
        enum=(ROOT/'vdp/vendor/vdp-gl/src/fabutils.h').read_text().split('enum VirtualKey {',1)[1].split('};',1)[0]
        enum=re.sub(r'/\*.*?\*/','',enum,flags=re.S)
        # Extract just the dependency's enum, without platform headers.
        (Path(temp)/'map.cpp').write_text('#include <cassert>\n#include "extender/input/browser_keyboard.hpp"\nenum VirtualKey {'+enum+'};\n'+'''
int main() {
 using K=agon::extender::input::BrowserKeyboard;
 assert(K::map({42,0,1}).virtual_key==VK_BACKSPACE);
 assert(K::map({40,0,1}).virtual_key==VK_RETURN);
 assert(K::map({41,0,1}).virtual_key==VK_ESCAPE);
 assert(K::map({57,16,1}).virtual_key==VK_CAPSLOCK);
 assert(K::map({49,0,1}).virtual_key==VK_BACKSLASH);
 assert(K::map({49,2,1}).virtual_key==VK_VERTICALBAR);
 assert(K::map({52,2,1}).virtual_key==VK_QUOTEDBL);
 assert(K::map({53,2,1}).virtual_key==VK_TILDE);
 assert(K::map({56,2,1}).virtual_key==VK_QUESTION);
 assert(K::map({30,2,1}).virtual_key==VK_EXCLAIM);
 assert(K::map({31,2,1}).virtual_key==VK_AT);
}
''')
        subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'vdp/video'),str(Path(temp)/'map.cpp'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
    print('PASS: pinned stock virtual keys')
if __name__=='__main__': main()
