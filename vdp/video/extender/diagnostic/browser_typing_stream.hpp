// Whole safe VDU units enter the retained parser. This qualification ingress
// deliberately rejects graphics/mode changes and incomplete commands.
#pragma once
#include <Stream.h>
#include <cstring>
#include "../input/browser_keyboard.hpp"
class BrowserTypingStream final : public Stream {
 public:
  uint8_t input[4]{}, output[128]{};
  unsigned size{}, consumed{}, produced{};
  const char *failure{};
  void fail(const char *why) { if (!failure) failure=why; }
  bool command(const uint8_t *p,unsigned n) {
    if (available()||produced||n>4) { fail("overlapping command"); return false; }
    std::memcpy(input,p,n); consumed=0; size=n; return true;
  }
  int available() override { return size-consumed; }
  int peek() override { return available()?input[consumed]:-1; }
  int read() override { return available()?input[consumed++]:-1; }
  void flush() override { fail("unexpected stream flush"); }
  size_t write(uint8_t b) override {
    if (produced==sizeof(output)) { fail("TX capacity"); return 0; }
    output[produced++]=b; return 1;
  }
  size_t write(const uint8_t *p,size_t n) override { size_t i=0; while(i<n&&write(p[i]))++i; return i; }
};
class VDUStreamProcessor;
BrowserTypingStream *beginBrowserTyping();
void runBrowserTyping(VDUStreamProcessor *processor);
void rejectBrowserTypingDuplex();
inline void setVDPProtocolDuplex(bool) { rejectBrowserTypingDuplex(); }
