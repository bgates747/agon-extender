// Bounded keyboard qualification Stream, not a general VDU ingress grammar.
// Only complete locale/General Poll commands enter the retained parser. Its
// normal serializer writes replies and unsolicited keys into the same buffer;
// the sole process-task owner drains it before admitting another operation.
#pragma once
#include <Stream.h>
#include <cstring>
#include "../input/processed_keyboard.hpp"

inline constexpr agon::extender::input::ProcessedKey keyboardProbeEvents[] = {
  {'a',0,22,1,'a'}, {'a',0,22,0,'a'}, {0,2,117,1,0},
  {'B',2,49,1,'B'}, {'B',2,49,1,'B'}, {'B',2,49,1,'B'},
  {'B',2,49,0,'B'}, {0,0,117,0,0},
  {'7',0,9,1,'7'}, {'7',0,9,0,'7'}, {13,0,143,1,13}, {13,0,143,0,13}
};
class KeyboardProbeStream final : public Stream {
 public:
  uint8_t input[4]{}, output[128]{};
  size_t consumed{}, produced{};
  bool command_loaded{};
  const char *failure{};
  void fail(const char *why) { if (!failure) failure=why; }
  bool command(const uint8_t *bytes) {
    if (command_loaded || produced || bytes[0]!=23 || bytes[1]!=0 ||
        (bytes[2]!=0x81 && bytes[2]!=0x80)) {
      fail("unsupported or overlapping command"); return false;
    }
    std::memcpy(input,bytes,4); consumed=0; command_loaded=true; return true;
  }
  bool commandDone() {
    if (!command_loaded || consumed!=4) { fail("parser consumption"); return false; }
    command_loaded=false; return !failure;
  }
  int available() override { return command_loaded ? int(4-consumed) : 0; }
  int peek() override { return available() ? input[consumed] : -1; }
  int read() override { return available() ? input[consumed++] : -1; }
  void flush() override { fail("unsupported stream flush"); }
  size_t write(uint8_t byte) override {
    if (failure || produced==sizeof(output)) { fail("output capacity"); return 0; }
    output[produced++]=byte; return 1;
  }
  size_t write(const uint8_t *bytes,size_t length) override {
    size_t n=0; while (n<length && write(bytes[n])) ++n; return n;
  }
};
class VDUStreamProcessor;
KeyboardProbeStream *beginKeyboardQualification();
void runKeyboardQualification(VDUStreamProcessor *processor);
void rejectKeyboardDuplexChange();
inline void setVDPProtocolDuplex(bool) { rejectKeyboardDuplexChange(); }
