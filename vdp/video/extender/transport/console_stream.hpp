// Adopted Stream for retained VDP parsing; one process task owns RX and TX.
#pragma once
#include <Stream.h>
#include <driver/uart.h>
#include <cstring>
#include "console_session.hpp"
#include "../input/processed_keyboard.hpp"
class ConsoleStream final : public Stream {
 public:
  agon::extender::transport::ConsoleSession session;
  uint8_t setup[4]{},output[8192]{};
  unsigned pos{4},read_pos{},count{};
  int cached{-1};
  const char *failure{};
  void fail(const char *why) { if (!failure) failure=why; }
  void feed(const uint8_t *p) { std::memcpy(setup,p,4);pos=0; }
  int available() override {
    if (pos<4) return 4-pos;
    size_t n=0;if(session.active()) uart_get_buffered_data_len(UART_NUM_1,&n);
    return int(n)+(cached>=0);
  }
  int read() override {
    if(pos<4) return setup[pos++];
    if(cached>=0) {int b=cached;cached=-1;return b;}
    uint8_t b;
    return session.active() && uart_read_bytes(UART_NUM_1,&b,1,0)==1 ? b : -1;
  }
  int peek() override { if(pos<4)return setup[pos];if(cached<0)cached=read();return cached; }
  void flush() override { /* Stream flush does not cancel pending UART bytes. */ }
  size_t write(uint8_t b) override {
    if(count==sizeof(output)) { fail("reply queue overflow");return 0; }
    output[(read_pos+count)%sizeof(output)]=b;++count;return 1;
  }
  size_t write(const uint8_t *p,size_t n) override {size_t i=0;while(i<n && write(p[i]))++i;return i;}
};
class VDUStreamProcessor;
ConsoleStream *beginConsole();
void runConsole(VDUStreamProcessor *);
void consoleControl(VDUStreamProcessor *, const uint8_t *p);
void consoleLayout(int region);
void consolePoll();
inline void setVDPProtocolDuplex(bool) { /* UART1 is full duplex for this composition. */ }
