#include <cstdio>
#include "extender/input/browser_keyboard.hpp"
int main() {
 using K=agon::extender::input::BrowserKeyboard;
 for (unsigned pop_time : {100u,150u}) {
  K keyboard; agon::extender::input::ProcessedKey out{};
  keyboard.ready(true);
  const bool took=keyboard.take(42,100);
  const bool fresh=keyboard.heartbeat(42,150);
  keyboard.pop(out,pop_time);
  const bool alive=keyboard.heartbeat(42,151);
  std::printf("take(100)=%d; heartbeat(150)=%d; pop(%u); heartbeat(151)=%d\n",took,fresh,pop_time,alive);
  if(!took || !fresh || alive != (pop_time==150)) return 1;
 }
}
