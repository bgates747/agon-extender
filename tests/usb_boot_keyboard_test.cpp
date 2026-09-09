#include <cassert>
#include <cstdio>
#include <vector>
#include "extender/input/usb_boot_keyboard.hpp"
using K=agon::extender::input::UsbBootKeyboard;
int main() {
  K k; std::vector<K::Key> events;
  auto emit=[&](K::Key e){events.push_back(e);};
  auto report=[&](uint8_t mods,std::initializer_list<uint8_t> keys) {
    uint8_t data[8]={mods,0}; unsigned i=2;
    for (auto key:keys) data[i++]=key;
    return k.report(data,sizeof(data),emit);
  };
  assert(report(0,{4})==K::Result::accepted);
  assert(events.size()==1 && events[0].processed.ascii=='a');
  report(0,{4,4}); assert(events.size()==1); // duplicate/idle reports
  report(0,{5,4}); assert(events.size()==2);
  report(0,{4,5}); assert(events.size()==2); // slots are not key identities
  report(0,{}); assert(events.size()==4 && !events[2].processed.down && !events[3].processed.down);
  events.clear();
  report(2,{4}); // left shift + A in one report
  assert(events.size()==2 && events[0].usage==225 && events[1].processed.ascii=='A');
  report(0,{4}); // shift up first
  assert(events.size()==3 && !events.back().processed.down);
  report(0,{});
  assert(events.back().processed.ascii=='A' && !events.back().processed.down);
  events.clear();
  report(0x10,{6}); // right control + C
  assert(events.back().processed.ascii==3 && events.back().processed.modifiers==1);
  k.disconnect(emit);
  assert(events.size()==4 && events[2].usage==228 && !events[2].processed.down);
  assert(events.back().processed.ascii==3 && events.back().processed.modifiers==0);
  events.clear(); k.disconnect(emit); assert(events.empty());
  report(0,{57}); report(0,{}); report(0,{4});
  assert(events.back().processed.ascii=='A');
  report(0,{}); report(2,{4}); assert(events.back().processed.ascii=='a');
  k.disconnect(emit); events.clear();
  report(0,{4,5,6,7,8,9}); assert(events.size()==6);
  assert(report(0,{1,1,1,1,1,1})==K::Result::invalid);
  assert(events.size()==12);
  assert(report(0,{4})==K::Result::waiting_neutral && events.size()==12);
  assert(report(2,{})==K::Result::waiting_neutral);
  assert(report(0,{})==K::Result::rearmed);
  report(0,{4}); assert(events.size()==13);
  k.lostReport(emit); assert(events.size()==14);
  k.lostReport(emit); assert(events.size()==14); // one cleanup per held key
  assert(report(0,{4})==K::Result::waiting_neutral);
  report(0,{}); report(0,{4}); assert(events.size()==15);
  uint8_t short_report[7]{};
  assert(k.report(short_report,7,emit)==K::Result::invalid);
  assert(events.size()==16);
  k.disconnect(emit); events.clear();
  report(0,{80}); assert(!events[0].mapped && events[0].usage==80); // unmapped left arrow retained
  report(0,{}); assert(!events[1].processed.down && events[1].usage==80);
  events.clear(); report(0xff,{}); assert(events.size()==8);
  assert(events.back().processed.modifiers==143);
  k.disconnect(emit); assert(events.size()==16);
  for (unsigned i=8;i<16;++i) assert(!events[i].processed.down && events[i].processed.modifiers==0);
  puts("PASS: USB reports, modifier transitions, retained releases, rollover, loss recovery and unplug cleanup");
}
