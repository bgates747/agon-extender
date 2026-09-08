// PORT-014 fixed text admission/return bounds. Actual VDU parsing stays in retained EDP.
#pragma once
#include <cstddef>
#include <cstdint>
struct VisibleTextTransaction {
  static constexpr std::uint8_t request[] = {12, 31, 2, 2, 69, 77, 79, 83, 32, 84, 79, 32, 69, 68, 80, 58, 32, 85, 65, 82, 84, 32, 84, 69, 88, 84, 13, 10, 23, 0, 202, 23, 0, 128, 166};
  static constexpr std::uint8_t reply[] = {0x80, 1, 0xA6};
  std::uint8_t input[sizeof(request)]{}, output[3]{};
  std::size_t received{}, consumed{}, produced{};
  bool parsing{};
  const char *failure{};
  void fail(const char *why) { if (!failure) failure = why; parsing = false; }
  void receive(std::uint8_t b) {
    if (failure) return;
    if (received == sizeof(input)) { fail("extra request bytes"); return; }
    if (b != request[received]) { fail("wrong request bytes"); return; }
    input[received++] = b;
  }
  bool begin() {
    if (failure || received != sizeof(input) || consumed || parsing) return false;
    parsing = true; return true;
  }
  int available() const { return parsing && !failure ? int(received-consumed) : 0; }
  int peek() const { return available() ? input[consumed] : -1; }
  int read() { int b=peek(); if (b>=0) ++consumed; return b; }
  std::size_t write(std::uint8_t b) {
    if (failure) return 0;
    if (!parsing || produced==sizeof(output) || b!=reply[produced]) {
      fail("unexpected retained-parser output"); return 0;
    }
    output[produced++]=b; return 1;
  }
  bool finish() {
    if (!parsing || failure || consumed!=sizeof(input) || produced!=sizeof(output)) {
      fail("incomplete retained-parser transaction"); return false;
    }
    parsing=false; return true;
  }
};
