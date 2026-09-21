#include "extender/display/mode_status.hpp"
#include <cassert>
#include <thread>
using namespace agon::extender::display;
int main() {
 ModeStatusStore store;
 ModeStatus value{};
 assert(!store.read(value));
 store.publish({8,320,240,64,60,false});
 assert(store.read(value) && value.mode==8 && value.colors==64 && !value.double_buffered);
 store.invalidate(); assert(!store.read(value));
 store.publish({140,320,200,16,70,true});
 assert(store.read(value) && value.refresh_hz==70 && value.double_buffered);
 // Reader may reject an in-progress publication, but must never combine modes.
 std::atomic<bool> done{false};
 std::thread writer([&]{for(unsigned n=1;n<100000;++n) {
   store.invalidate(); store.publish({n,n,n,n,n,bool(n&1)});
 } done=true;});
 while(!done.load()) if(store.read(value) && value.mode!=140) {
  assert(value.mode==value.width && value.width==value.height &&
         value.height==value.colors && value.colors==value.refresh_hz &&
         value.double_buffered==bool(value.mode&1));
 }
 writer.join();
}
