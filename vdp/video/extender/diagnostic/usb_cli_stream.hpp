// Bounded native-USB CLI composition. Only complete stock locale/poll commands
// enter the retained parser; complete keyboard/reply frames share its serializer.
#pragma once
#include <Stream.h>
#include <cstring>
#include "../input/processed_keyboard.hpp"
class UsbCliStream final : public Stream {
 public:
  uint8_t input[4]{},output[128]{};
  size_t consumed{},produced{};
  bool loaded{};
  const char *failure{};
  void fail(const char *reason) { if (!failure) failure=reason; }
  bool command(const uint8_t *p) {
    if (loaded || produced || p[0]!=23 || p[1]!=0 || (p[2]!=0x81 && p[2]!=0x80)) {
      fail("unsupported command"); return false;
    }
    std::memcpy(input,p,4); consumed=0; loaded=true; return true;
  }
  bool commandDone() { if (consumed!=4) fail("incomplete parser consumption"); loaded=false; return !failure; }
  int available() override { return loaded ? int(4-consumed) : 0; }
  int peek() override { return available()?input[consumed]:-1; }
  int read() override { return available()?input[consumed++]:-1; }
  void flush() override { fail("unsupported flush"); }
  size_t write(uint8_t p) override {
    if (failure || produced==sizeof(output)) { fail("reply capacity"); return 0; }
    output[produced++]=p; return 1;
  }
  size_t write(const uint8_t *p,size_t n) override { size_t i=0; while(i<n && write(p[i])) ++i;return i; }
};
class VDUStreamProcessor;
UsbCliStream *beginKeyboardQualification();
void runKeyboardQualification(VDUStreamProcessor *processor);
void rejectKeyboardDuplexChange();
inline void setVDPProtocolDuplex(bool) { rejectKeyboardDuplexChange(); }
