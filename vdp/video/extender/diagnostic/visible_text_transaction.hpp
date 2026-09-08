// Bounded text admission; actual VDU execution stays in retained EDP.
// No banner or count is compiled here. EMOS owns the flush/General Poll suffix.
#pragma once
#include <cstddef>
#include <cstdint>
struct VisibleTextTransaction {
  static constexpr std::size_t text_limit = 1024;
  static constexpr std::uint8_t suffix[] = {23, 0, 0xCA, 23, 0, 0x80};
  std::uint8_t input[text_limit + 7]{}, output[3]{};
  std::size_t received{}, consumed{}, produced{}, text_size{}, footer{};
  unsigned arguments{};
  std::uint8_t token{};
  bool parsing{}, complete{};
  const char *failure{};
  void fail(const char *why) { if (!failure) failure = why; parsing = false; }
  void receive(std::uint8_t b) {
    if (failure) return;
    if (complete || received == sizeof(input)) { fail("extra request bytes"); return; }
    if (footer) {
      if (footer < sizeof(suffix)) {
        if (b != suffix[footer++]) { fail("wrong completion suffix"); return; }
      } else {
        // A6 preserves old VDPTEXT; A7 identifies the SD sample API.
        if (b != 0xA6 && b != 0xA7) { fail("wrong completion token"); return; }
        token = b; complete = true;
      }
    } else if (!arguments && b == 23) {
      if (!text_size) { fail("empty text"); return; }
      footer = 1;
    } else {
      if (text_size == text_limit) { fail("text too long"); return; }
      if (arguments) --arguments;
      else if (b == 31) arguments = 2;
      else if (!((b >= 32 && b <= 126) || (b >= 8 && b <= 13) || b == 30)) {
        fail("unsupported text command"); return;
      }
      ++text_size;
    }
    input[received++] = b;
  }
  bool begin() {
    if (failure || !complete || consumed || parsing) return false;
    parsing = true; return true;
  }
  int available() const { return parsing && !failure ? int(received-consumed) : 0; }
  int peek() const { return available() ? input[consumed] : -1; }
  int read() { int b=peek(); if (b>=0) ++consumed; return b; }
  std::size_t write(std::uint8_t b) {
    if (failure) return 0;
    const std::uint8_t expected[] = {0x80, 1, token};
    if (!parsing || produced==sizeof(output) || b!=expected[produced]) {
      fail("unexpected retained-parser output"); return 0;
    }
    output[produced++]=b; return 1;
  }
  bool finish() {
    if (!parsing || failure || consumed!=received || produced!=sizeof(output)) {
      fail("incomplete retained-parser transaction"); return false;
    }
    parsing=false; return true;
  }
};
