"""Actual adapter and upstream ASCII converter; no hardware or second key map."""
from pathlib import Path
import re,subprocess,tempfile
from processed_keyboard_test import function
root=Path(__file__).resolve().parents[1];video=root/'vdp/video';vendor=root/'vdp/vendor/vdp-gl/src'
utils=(vendor/'fabutils.h').read_text();enum=utils.split('enum VirtualKey {',1)[1].split('};',1)[0]
constants='\n'.join(x for x in utils.splitlines() if x.startswith('#define ASCII_'))
adapter=(video/'extender/input/unavailable_input_adapter.hpp').read_text()
keyboard=adapter[adapter.index('class UnavailableKeyboard final'):adapter.index('class UnavailableMouse final')]
converter=function((vendor/'codepages.cpp').read_text(),'int virtualKeyToASCII(')
source='''#include <cassert>
#include <cstdio>
#include <cstdint>
#include "extender/input/processed_keyboard.hpp"
#define AGON_EXTENDER_PROCESSED_KEYBOARD 1
'''+constants+'\nnamespace fabgl { enum VirtualKey {'+enum+'''};
struct VirtualKeyItem { uint8_t ASCII{}; VirtualKey vk{}; bool down{};
 bool CTRL{},SHIFT{},LALT{},RALT{},CAPSLOCK{},NUMLOCK{},SCROLLLOCK{},GUI{}; uint8_t scancode[8]{}; };
struct VirtualKeyToASCII {VirtualKey vk;uint8_t ASCII;};
struct CodePage {uint16_t codepage; const VirtualKeyToASCII *convTable;};
'''+converter+'}\nuint8_t _keycode=0;\n'+keyboard+function(adapter,'inline bool getKeyboardKey(')+'''
int main() {
 using namespace fabgl; using namespace agon::extender::input;
 auto &fifo=processedKeyboard(); UnavailableKeyboard kb; VirtualKeyItem item{};
 auto query=[&](VirtualKey vk) {kb.injectVirtualKey(vk,kb.isVKDown(vk),false);if(!getKeyboardKey(&item)){fprintf(stderr,"missing vk=%u last=%u fault=%u ",unsigned(vk),unsigned(VK_LAST),fifo.queryFault());assert(false);}assert(item.vk==vk);};
 fifo.reset(); query(VK_a);assert(!item.down && item.ASCII=='a' && _keycode==0);
 assert(!getKeyboardKey(&item));
 assert(fifo.push({'a',0,VK_a,1,'a'}));assert(getKeyboardKey(&item));
 query(VK_a);assert(item.down && item.ASCII=='a' && _keycode=='a');
 assert(fifo.push({0,1,VK_LCTRL,1,0}));assert(getKeyboardKey(&item));
 query(VK_a);assert(item.down && item.CTRL && item.ASCII==1 && _keycode==1);
 assert(fifo.push({0,0,VK_LCTRL,0,0}));assert(getKeyboardKey(&item));
 assert(fifo.push({'a',0,VK_a,0,'a'}));assert(getKeyboardKey(&item));
 query(VK_a);assert(!item.down && item.ASCII=='a' && _keycode=='a');
 assert(fifo.push({11,0,VK_UP,1,0}));assert(getKeyboardKey(&item));
 query(VK_UP);assert(item.down && _keycode==11);
 fifo.reset();_keycode=77;
 // Every valid key and modifier byte uses the exact upstream conversion.
 for(unsigned mods=0;mods<256;++mods) {
  assert(fifo.push({77,uint8_t(mods),VK_a,0,0}));assert(getKeyboardKey(&item));
  for(unsigned vk=0;vk<=248;++vk) {
   query(VirtualKey(vk));auto expected=item;expected.down=true;
   assert(item.ASCII==uint8_t(virtualKeyToASCII(expected,nullptr)));
   assert(!item.down && _keycode==77);
  }
 }
 fifo.reset();kb.injectVirtualKey(VirtualKey(255),false,false);assert(fifo.size()==0);
 for(unsigned i=0;i<fifo.capacity;++i)kb.injectVirtualKey(VK_a,false,false);
 kb.injectVirtualKey(VK_a,false,false);assert(fifo.queryFault());
 fifo.reset();assert(!fifo.queryFault() && !fifo.isDown(VK_UP) && !fifo.modifiers());
 assert(fifo.push({'a',0,VK_a,1,'a'}));assert(getKeyboardKey(&item));
 kb.injectVirtualKey(VK_a,true,false);kb.injectVirtualKey(VK_ESCAPE,false,false);
 assert(getKeyboardKey(&item) && item.vk==VK_a && item.down);
 assert(getKeyboardKey(&item) && item.vk==VK_ESCAPE && !item.down);
 assert(!getKeyboardKey(&item));
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(source)
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(video),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: actual key-query adapter, upstream conversion, 256 modifier states, ordering, invalid key, overflow and reset')
