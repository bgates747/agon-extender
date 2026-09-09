#include <cassert>
#include <cstdio>
#include "extender/input/browser_keyboard.hpp"
using namespace agon::extender::input;
int main() {
  BrowserKeyboard k; ProcessedKey e;
  assert(!k.take(1,0)); k.ready(true); assert(k.take(1,0));
  assert(k.push(1,{4,0,1},1)); assert(k.pop(e,1)&&e.keycode=='a'&&e.virtual_key==22);
  // Key-up retains the key identity, even with Shift held after key-down.
  assert(k.push(1,{4,2,0},2)); assert(k.pop(e,2)&&!e.down&&e.virtual_key==22);
  assert(k.push(1,{225,2,1},3)); assert(k.pop(e,3)&&e.virtual_key==117);
  assert(k.push(1,{5,2,1},4)); assert(k.pop(e,4)&&e.keycode=='B'&&e.virtual_key==49);
  assert(k.push(1,{5,2,1},5)); assert(k.pop(e,5)&&e.keycode=='B');
  // Queued old input is discarded; modifier/key releases precede takeover.
  assert(k.push(1,{6,2,1},6)); assert(k.take(2,7));
  assert(!k.push(1,{7,0,1},8)); assert(k.push(2,{30,0,1},8));
  assert(k.pop(e,8)&&e.virtual_key==117&&!e.down&&!e.modifiers);
  assert(k.pop(e,8)&&e.virtual_key==49&&!e.down);
  assert(k.pop(e,8)&&e.keycode=='1'&&e.down);
  k.close(1); assert(!k.pop(e,9)); // stale socket close cannot revoke new owner
  assert(k.pop(e,2008)&&!e.down&&e.keycode=='1'); assert(!k.pop(e,2009));
  assert(!k.heartbeat(2,2009));
  assert(k.take(3,2010)); assert(k.push(3,{4,0,1},2010)); assert(k.pop(e,2010));
  for(unsigned i=0;i<64;++i) assert(k.push(3,{4,0,1},2011));
  assert(!k.push(3,{4,0,1},2011)); assert(k.pop(e,2011)&&!e.down); assert(!k.pop(e,2011));
  assert(k.take(4,2012)); assert(!k.push(4,{4,0,2},2012));
  assert(k.take(5,3000)); assert(!k.heartbeat(5,5000));
  assert(k.take(5,6000)); assert(!k.push(5,{4,0,1},8000));
  for(unsigned p=4;p<30;++p) {
    assert(BrowserKeyboard::map({uint8_t(p),0,1}).keycode=='a'+p-4);
    assert(BrowserKeyboard::map({uint8_t(p),2,1}).keycode=='A'+p-4);
    assert(BrowserKeyboard::map({uint8_t(p),16,1}).keycode=='A'+p-4);
    assert(BrowserKeyboard::map({uint8_t(p),18,1}).keycode=='a'+p-4);
  }
  assert(BrowserKeyboard::map({49,0,1}).keycode=='\\');
  assert(BrowserKeyboard::map({49,2,1}).keycode=='|');
  assert(BrowserKeyboard::map({52,2,1}).keycode=='"');
  assert(BrowserKeyboard::map({42,0,1}).keycode==8);
  puts("PASS: browser mapping, repeat, takeover ordering, release, expiry, malformed input and overflow");
}
