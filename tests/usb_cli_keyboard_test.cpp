#include <cassert>
#include <cstdio>
#include <vector>
#include <array>
#include "extender/input/usb_cli_keyboard.hpp"
#include "extender/input/usb_key_queue.hpp"
using namespace agon::extender::input;
int main() {
  assert(!mapUsbCliKey(50,0,1).virtual_key);
  assert(mapUsbCliKey(50,0,0).keycode=='#');
  assert(!mapUsbCliKey(84,0,1).virtual_key); // Keypad is outside this increment.
  UsbCliKeyboard k;std::vector<ProcessedKey> events;
  auto emit=[&](ProcessedKey e){events.push_back(e);};
  std::array<uint8_t,8> report{};
  auto send=[&](uint32_t t){k.report(report.data(),report.size(),t,emit);};
  k.locale=1;send(0);k.admit();
  report[2]=42;send(1);
  assert(events.back().keycode==127 && events.back().ascii==8 && events.back().virtual_key==132);
  k.tick(500,emit);assert(events.size()==1);
  k.tick(501,emit);assert(events.size()==2 && events.back().down);
  k.tick(5000,emit);assert(events.size()==3); // No catch-up flood.
  report[2]=0;send(5001);assert(!events.back().down && events.back().keycode==127);
  auto n=events.size();k.tick(6000,emit);assert(events.size()==n);
  for(auto [usage,ascii,vk]:std::vector<std::array<int,3>>{{80,8,154},{79,21,156},{81,10,152},{82,11,150}}) {
    report[2]=usage;send(6001);assert(events.back().keycode==ascii && events.back().virtual_key==vk);
    report[2]=0;send(6002);
  }
  // UK and US differ at physical Shift+2. Release identity is retained even
  // after Shift goes up and the locale setting changes.
  k.locale=0;report[0]=2;report[2]=31;send(7000);assert(events.back().keycode=='"');
  report[0]=0;k.locale=1;send(7001);report[2]=0;send(7002);
  assert(events.back().keycode=='"' && !events.back().down);
  report[0]=2;report[2]=31;send(7100);assert(events.back().keycode=='@');
  k.disconnect(emit);assert(!events.back().down && events.back().keycode=='@');
  // New admission never replays the held key. Neutral permits a new press.
  report[0]=0;report[2]=4;send(8000);k.admissionBoundary();n=events.size();k.admit();
  send(8001);k.tick(9000,emit);assert(events.size()==n);
  report[2]=0;send(9001);report[2]=4;send(9002);assert(events.size()==n+1 && events.back().keycode=='a');
  k.lost(emit);assert(!events.back().down);n=events.size();send(9003);assert(events.size()==n);
  report[2]=0;send(9004);report[2]=4;send(9005);assert(events.size()==n+1);
  k.disconnect(emit);
  // Queue reserves cleanup capacity even when a key-up cannot be admitted.
  UsbKeyQueue q;ProcessedKey key{'a',0,22,1,'a'},out;
  for(unsigned i=0;i<48;++i) assert(q.push(key));
  key.down=0;assert(!q.push(key));assert(q.releaseAll());
  for(unsigned i=0;i<48;++i) {assert(q.pop(out));assert(out.down);}
  assert(q.pop(out) && !out.down && out.virtual_key==22);assert(q.empty());
  puts("USB CLI editing, UK/US mapping, repeat, admission, loss and queue cleanup pass");
}
