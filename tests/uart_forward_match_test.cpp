#include "uart_forward_match.hpp"
#include <cassert>
#include <cstdint>

int main() {
  constexpr uint8_t message[] = {0x00, 0x55, 0xAA, 0xFF};
  using State = UartForwardMatch::State;
  UartForwardMatch exact(message, 4, 0);
  exact.feed(message, 2, 100);
  exact.feed(message + 2, 2, 101);
  exact.poll(300); assert(exact.state() == State::receiving);
  exact.poll(301); assert(exact.state() == State::pass);
  exact.feed(message, 1, 302); assert(exact.state() == State::fail);
  assert(exact.count() == 5);

  UartForwardMatch bad(message, 4, 0);
  bad.feed(message + 1, 1, 100);
  bad.feed(message, 4, 200); bad.poll(500);
  assert(bad.state() == State::fail); // no substring resynchronisation

  UartForwardMatch short_frame(message, 4, 0);
  short_frame.feed(message, 3, 1); short_frame.poll(3001);
  assert(short_frame.state() == State::fail);
  short_frame.feed(message + 3, 1, 3002);
  assert(short_frame.state() == State::fail);

  UartForwardMatch absent(message, 4, 0);
  absent.poll(179999); assert(absent.state() == State::waiting);
  absent.feed(message, 4, 180000); absent.poll(180200);
  assert(absent.state() == State::fail);

  UartForwardMatch error(message, 4, 0);
  error.feed(message, 4, 10); error.error("parity"); error.poll(210);
  assert(error.state() == State::fail);

  UartForwardMatch late_error(message, 4, 0);
  late_error.feed(message, 4, 10); late_error.poll(210);
  late_error.error("overflow"); assert(late_error.state() == State::fail);

  UartForwardMatch overlong(message, 4, 0);
  uint8_t noise[100] = {};
  overlong.feed(noise, sizeof(noise), 1);
  assert(overlong.state() == State::fail && overlong.count() == 100);
  assert(overlong.stored() == 64);

  UartForwardMatch wrap(message, 4, UINT32_MAX - 100);
  wrap.feed(message, 4, UINT32_MAX - 50); wrap.poll(149);
  assert(wrap.state() == State::pass);
}
