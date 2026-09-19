"""Execute native CLI acquisition policy with sanitizer-backed host boundaries."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    exe=Path(temp)/'usb-cli'
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                    '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/usb_cli_keyboard_test.cpp'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
    enum=(ROOT/'vdp/vendor/vdp-gl/src/fabutils.h').read_text().split('enum VirtualKey {',1)[1].split('};',1)[0]
    enum=re.sub(r'/\*.*?\*/','',enum,flags=re.S)
    check=Path(temp)/'keys.cpp'
    check.write_text('#include <cassert>\n#include "extender/input/usb_cli_keyboard.hpp"\nenum VirtualKey {'+enum+'};\n'+'''
int main() {
 using agon::extender::input::mapUsbCliKey;
 assert(mapUsbCliKey(32,2,0).virtual_key==VK_POUND);
 assert(mapUsbCliKey(71,0,1).virtual_key==VK_SCROLLLOCK);
 assert(mapUsbCliKey(83,0,1).virtual_key==VK_NUMLOCK);
 assert(mapUsbCliKey(84,0,1).virtual_key==VK_KP_DIVIDE);
 assert(mapUsbCliKey(88,0,1).virtual_key==VK_KP_ENTER);
 assert(mapUsbCliKey(89,32,1).virtual_key==VK_KP_1);
 assert(mapUsbCliKey(89,34,1).virtual_key==VK_KP_END);
 assert(mapUsbCliKey(99,0,1).virtual_key==VK_KP_DELETE);
 assert(mapUsbCliKey(58,0,1).virtual_key==VK_F1);
 assert(mapUsbCliKey(69,0,1).virtual_key==VK_F12);
 const int expected[]={VK_INSERT,VK_HOME,VK_PAGEUP,VK_DELETE,VK_END,VK_PAGEDOWN,VK_RIGHT,VK_LEFT,VK_DOWN,VK_UP};
 for(unsigned i=0;i<10;++i) assert(mapUsbCliKey(73+i,0,1).virtual_key==expected[i]);
}
''')
    subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'vdp/video'),str(check),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
